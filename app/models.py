from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # admin, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Bookmaker(Base):
    __tablename__ = "bookmakers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    odds = relationship("Odd", back_populates="bookmaker")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    home_team = Column(String, index=True, nullable=False)
    away_team = Column(String, index=True, nullable=False)
    sport = Column(String, default="Soccer", index=True)
    event_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    odds = relationship("Odd", back_populates="event", cascade="all, delete-orphan")
    surebets = relationship("Surebet", back_populates="event", cascade="all, delete-orphan")

class Odd(Base):
    __tablename__ = "odds"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    bookmaker_id = Column(Integer, ForeignKey("bookmakers.id"), nullable=False)
    market_type = Column(String, nullable=False)  # e.g., "1X2", "Over_Under"
    outcome_name = Column(String, nullable=False)  # e.g., "Home", "Away", "Draw", "Over 2.5", "Under 2.5"
    odds_value = Column(Float, nullable=False)  # The decimal odds value
    scraped_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="odds")
    bookmaker = relationship("Bookmaker", back_populates="odds")

class Surebet(Base):
    __tablename__ = "surebets"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    market_type = Column(String, nullable=False)  # "1X2", "Home_Away", "Over_Under"
    outcomes = Column(JSON, nullable=False)  # Stores details of the surebet options (outcome_name, odds, bookmaker, required stake)
    arbitrage_percentage = Column(Float, nullable=False)  # Sum of 1/Odds
    roi = Column(Float, nullable=False)  # (1 / arb_pct) - 1
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="surebets")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
