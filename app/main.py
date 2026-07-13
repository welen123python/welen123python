import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.database import engine, Base, get_db
from app.models import User, Bookmaker, Event, Odd, Surebet, Notification
from app.auth import get_password_hash, verify_password, create_access_token
from app.services.analyzer import SurebetAnalyzer
from app.services.orchestrator import run_extraction_and_analysis_cycle
from app.services.notifier import manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.main")

# Background scheduler setup
scheduler = BackgroundScheduler()

def scheduled_cycle_job():
    """Wrapper to run async extraction inside background synchronous thread scheduler."""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(run_extraction_and_analysis_cycle(use_simulation=True))
    except RuntimeError:
        # No running event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(run_extraction_and_analysis_cycle(use_simulation=True))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")

    # Seed Bookmakers
    db = next(get_db())
    for name in settings.BOOKMAKERS:
        existing = db.query(Bookmaker).filter(Bookmaker.name == name).first()
        if not existing:
            db.add(Bookmaker(name=name, is_active=True))
    db.commit()
    db.close()

    # Trigger immediate cycle run on start to populate DB
    scheduled_cycle_job()

    # Start automated background scheduling
    scheduler.add_job(
        scheduled_cycle_job,
        'interval',
        seconds=settings.SCRAPING_INTERVAL_SECONDS,
        id='surebet_scraping_job'
    )
    scheduler.start()
    logger.info(f"Background scheduler started with interval of {settings.SCRAPING_INTERVAL_SECONDS} seconds.")

    yield

    # Shutdown scheduler
    scheduler.shutdown()
    logger.info("Background scheduler shutdown.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Template and static mounting
import os
os.makedirs("app/static", exist_ok=True)
os.makedirs("app/templates", exist_ok=True)

# Write a simple CSS file to static
with open("app/static/style.css", "w") as f:
    f.write("/* Custom styles */")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# ------------------ REST ENDPOINTS ------------------

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request, db: Session = Depends(get_db)):
    """Serves the main interactive dashboard."""
    surebets = db.query(Surebet).join(Event).all()
    notifications = db.query(Notification).order_by(Notification.created_at.desc()).limit(10).all()
    bookmakers = db.query(Bookmaker).all()

    # Structure surebets for UI
    ui_surebets = []
    for sb in surebets:
        ui_surebets.append({
            "id": sb.id,
            "home_team": sb.event.home_team,
            "away_team": sb.event.away_team,
            "sport": sb.event.sport,
            "market_type": sb.market_type,
            "arbitrage_percentage": sb.arbitrage_percentage,
            "roi": sb.roi,
            "outcomes": sb.outcomes
        })

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "surebets": ui_surebets,
            "notifications": notifications,
            "bookmakers": bookmakers,
            "default_investment": settings.DEFAULT_INVESTMENT
        }
    )

@app.post("/api/v1/auth/register")
def register_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pwd = get_password_hash(password)
    user = User(username=username, hashed_password=hashed_pwd)
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/api/v1/auth/login")
def login_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_access_token(subject=user.username)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/v1/surebets")
def list_surebets(db: Session = Depends(get_db)):
    surebets = db.query(Surebet).all()
    return surebets

@app.post("/api/v1/calculate")
def calculate_arbitrage_stakes(total_investment: float, odds: List[float], arb_pct: float):
    """
    Computes optimal stakes dynamically for a custom investment or list of odds.
    """
    stakes = SurebetAnalyzer.calculate_stakes(total_investment, odds, arb_pct)
    return {
        "stakes": stakes,
        "total": sum(stakes)
    }

@app.get("/api/v1/notifications")
def get_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).order_by(Notification.created_at.desc()).limit(20).all()


# ------------------ WEBSOCKET LIVE NOTIFICATIONS ------------------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep-alive or handle client messages if any
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
