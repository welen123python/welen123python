import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Event, Bookmaker, Odd, Surebet, Notification
from app.scraper.engine import ScraperEngine
from app.services.analyzer import SurebetAnalyzer
from app.services.notifier import manager

logger = logging.getLogger("app.orchestrator")

async def run_extraction_and_analysis_cycle(use_simulation: bool = True):
    """
    Orchestrates a full extraction and analysis cycle:
    1. Scrapes odds from the 6 bookmakers (or simulates them).
    2. Stores events and odds in the database.
    3. Runs the surebet identification algorithm.
    4. Records new surebets and broadcasts real-time notifications.
    """
    logger.info("Starting automated surebet extraction and analysis cycle...")
    db: Session = SessionLocal()
    try:
        # Step 1: Extract data
        engine = ScraperEngine()
        scraped_data = await engine.run_all(use_simulation=use_simulation)
        logger.info(f"Successfully collected {len(scraped_data)} odd entries from bookmakers.")

        # Step 2: Ensure bookmakers exist in DB
        bookmaker_cache = {}
        for item in scraped_data:
            b_name = item["bookmaker"]
            if b_name not in bookmaker_cache:
                bm = db.query(Bookmaker).filter(Bookmaker.name == b_name).first()
                if not bm:
                    bm = Bookmaker(name=b_name, is_active=True)
                    db.add(bm)
                    db.commit()
                    db.refresh(bm)
                bookmaker_cache[b_name] = bm.id

        # To keep the database light, we'll clear older odds (e.g., older than 1 hour)
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        db.query(Odd).filter(Odd.scraped_at < cutoff_time).delete()
        db.commit()

        # Step 3: Populate database with new events and odds
        for item in scraped_data:
            home = item["home_team"]
            away = item["away_team"]
            sport = item.get("sport", "Soccer")
            event_date = item.get("event_date")
            b_name = item["bookmaker"]
            b_id = bookmaker_cache[b_name]

            # Find or create event
            event = db.query(Event).filter(
                Event.home_team == home,
                Event.away_team == away,
                Event.sport == sport
            ).first()

            if not event:
                event = Event(
                    home_team=home,
                    away_team=away,
                    sport=sport,
                    event_date=event_date or datetime.utcnow() + timedelta(days=2)
                )
                db.add(event)
                db.commit()
                db.refresh(event)

            # Store odds
            for market_type, outcomes in item.get("markets", {}).items():
                for outcome_name, odd_value in outcomes.items():
                    # Create or update Odd
                    existing_odd = db.query(Odd).filter(
                        Odd.event_id == event.id,
                        Odd.bookmaker_id == b_id,
                        Odd.market_type == market_type,
                        Odd.outcome_name == outcome_name
                    ).first()

                    if existing_odd:
                        existing_odd.odds_value = odd_value
                        existing_odd.scraped_at = datetime.utcnow()
                    else:
                        new_odd = Odd(
                            event_id=event.id,
                            bookmaker_id=b_id,
                            market_type=market_type,
                            outcome_name=outcome_name,
                            odds_value=odd_value,
                            scraped_at=datetime.utcnow()
                        )
                        db.add(new_odd)

        db.commit()

        # Step 4: Run Identification analysis
        surebets = SurebetAnalyzer.analyze(scraped_data)
        logger.info(f"Analyzed markets and identified {len(surebets)} surebets.")

        # Clear existing active surebets before inserting new ones to keep feed fresh
        db.query(Surebet).delete()
        db.commit()

        # Step 5: Save identified surebets and broadcast real-time notifications
        for sb in surebets:
            # Find the corresponding event in DB
            event = db.query(Event).filter(
                Event.home_team == sb["home_team"],
                Event.away_team == sb["away_team"]
            ).first()

            if not event:
                continue

            new_surebet = Surebet(
                event_id=event.id,
                market_type=sb["market_type"],
                outcomes=sb["outcomes"],
                arbitrage_percentage=sb["arbitrage_percentage"],
                roi=sb["roi"]
            )
            db.add(new_surebet)
            db.commit()
            db.refresh(new_surebet)

            # Build alert message
            msg = (
                f"🚨 ARBITRAGE DETECTED (ROI {sb['roi']}%): "
                f"{sb['home_team']} vs {sb['away_team']} on market '{sb['market_type']}'. "
                f"Net profit for $1000 is ${sb['net_profit']}!"
            )

            # Create persistent database notification
            notif = Notification(message=msg, is_read=False)
            db.add(notif)
            db.commit()

            # Broadcast alert to WebSockets in real-time
            alert_payload = {
                "id": new_surebet.id,
                "event": f"{sb['home_team']} vs {sb['away_team']}",
                "sport": sb["sport"],
                "market_type": sb["market_type"],
                "arbitrage_percentage": sb["arbitrage_percentage"],
                "roi": sb["roi"],
                "net_profit": sb["net_profit"],
                "outcomes": sb["outcomes"],
                "message": msg,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
            await manager.broadcast(alert_payload)

    except Exception as e:
        logger.error(f"Error in extraction and analysis cycle: {str(e)}", exc_info=True)
    finally:
        db.close()
