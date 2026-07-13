import pytest
from app.scraper.bookmakers.bet365 import Bet365Scraper
from app.scraper.bookmakers.betano import BetanoScraper
from app.scraper.bookmakers.betfair import BetfairScraper
from app.scraper.bookmakers.pinnacle import PinnacleScraper
from app.scraper.bookmakers.one_xbet import OneXBetScraper
from app.scraper.bookmakers.sportingbet import SportingbetScraper
from app.scraper.engine import ScraperEngine

@pytest.mark.asyncio
async def test_bet365_scraper():
    scraper = Bet365Scraper()
    results = await scraper.scrape()
    assert len(results) > 0
    match = results[0]
    assert "Real Madrid" in match["home_team"] or "Barcelona" in match["home_team"]
    assert match["markets"]["1X2"]["Home"] == 2.10

@pytest.mark.asyncio
async def test_betano_scraper():
    scraper = BetanoScraper()
    results = await scraper.scrape()
    assert len(results) > 0
    assert results[0]["markets"]["1X2"]["Draw"] == 3.50

@pytest.mark.asyncio
async def test_betfair_scraper():
    scraper = BetfairScraper()
    results = await scraper.scrape()
    assert len(results) > 0
    assert results[0]["markets"]["1X2"]["Away"] == 3.15

@pytest.mark.asyncio
async def test_pinnacle_scraper():
    scraper = PinnacleScraper()
    results = await scraper.scrape()
    assert len(results) > 0
    assert results[0]["markets"]["1X2"]["Home"] == 2.20

@pytest.mark.asyncio
async def test_one_xbet_scraper():
    scraper = OneXBetScraper()
    results = await scraper.scrape()
    assert len(results) > 0
    assert results[0]["markets"]["1X2"]["Draw"] == 3.45

@pytest.mark.asyncio
async def test_sportingbet_scraper():
    scraper = SportingbetScraper()
    results = await scraper.scrape()
    assert len(results) > 0
    assert results[0]["markets"]["1X2"]["Away"] == 3.12

@pytest.mark.asyncio
async def test_scraper_engine_simulation():
    engine = ScraperEngine()
    simulated_data = engine.generate_simulated_data()
    assert len(simulated_data) > 0

    # We should have 6 bookmakers represented
    bookmakers_found = set(item["bookmaker"] for item in simulated_data)
    assert len(bookmakers_found) == 6
