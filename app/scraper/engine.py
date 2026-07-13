import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.scraper.bookmakers.bet365 import Bet365Scraper
from app.scraper.bookmakers.betano import BetanoScraper
from app.scraper.bookmakers.betfair import BetfairScraper
from app.scraper.bookmakers.pinnacle import PinnacleScraper
from app.scraper.bookmakers.one_xbet import OneXBetScraper
from app.scraper.bookmakers.sportingbet import SportingbetScraper
from app.scraper.base import logger

class ScraperEngine:
    def __init__(self):
        self.scrapers = [
            Bet365Scraper(),
            BetanoScraper(),
            BetfairScraper(),
            PinnacleScraper(),
            OneXBetScraper(),
            SportingbetScraper()
        ]

    async def run_all(self, use_simulation: bool = True) -> List[Dict[str, Any]]:
        """
        Runs all scrapers. If use_simulation is True, it returns realistic simulated data
        which dynamically includes high-probability arbitrage opportunities (surebets)
        across multiple bookmakers to enable demonstration/testing of the analysis module.
        """
        if not use_simulation:
            # Run the actual beautifulsoup scrapers in parallel
            tasks = [scraper.scrape() for scraper in self.scrapers]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            combined_data = []
            for scraper, result in zip(self.scrapers, results):
                if isinstance(result, Exception):
                    logger.error(f"Scraper {scraper.name} failed with error: {str(result)}")
                elif result:
                    for event in result:
                        event["bookmaker"] = scraper.name
                        combined_data.append(event)
            return combined_data

        # Return rich, highly dynamic simulated odds structure
        return self.generate_simulated_data()

    def generate_simulated_data(self) -> List[Dict[str, Any]]:
        """
        Generates simulated odds from 6 bookmakers with standard variations
        and injects some profitable 2-way and 3-way surebet opportunities.
        """
        bookmakers = [s.name for s in self.scrapers]
        simulated_results = []

        # We will define a few matches
        matches = [
            {"home": "Real Madrid", "away": "Barcelona", "sport": "Soccer"},
            {"home": "Manchester City", "away": "Liverpool", "sport": "Soccer"},
            {"home": "Carlos Alcaraz", "away": "Jannik Sinner", "sport": "Tennis"},
            {"home": "Los Angeles Lakers", "away": "Boston Celtics", "sport": "Basketball"},
            {"home": "Bayern Munich", "away": "Paris Saint-Germain", "sport": "Soccer"},
        ]

        now = datetime.utcnow()

        for i, match in enumerate(matches):
            event_date = now + timedelta(days=random.randint(1, 5))

            if match["sport"] == "Soccer":
                # Generate 1X2 outcomes (3-way)
                # Let's inject a surebet for "Real Madrid vs Barcelona"
                if match["home"] == "Real Madrid":
                    # We want to force a 3-way surebet
                    # To do this, we need 1/O1 + 1/O2 + 1/O3 < 1.0
                    # Let's say:
                    # Bookmaker A (Bet365) has W1 = 3.20 (so 1/3.20 = 0.3125)
                    # Bookmaker B (Pinnacle) has X = 3.60 (so 1/3.60 = 0.2777)
                    # Bookmaker C (Betano) has W2 = 3.40 (so 1/3.40 = 0.2941)
                    # Total Implied Prob = 0.3125 + 0.2777 + 0.2941 = 0.8843 (ROI ~ 13%)
                    for b in bookmakers:
                        if b == "Bet365":
                            h, d, a = 3.20, 2.90, 2.50
                        elif b == "Pinnacle":
                            h, d, a = 2.10, 3.60, 2.80
                        elif b == "Betano":
                            h, d, a = 2.05, 3.10, 3.40
                        else:
                            h, d, a = 2.15, 3.20, 2.90

                        simulated_results.append({
                            "home_team": match["home"],
                            "away_team": match["away"],
                            "sport": match["sport"],
                            "event_date": event_date,
                            "bookmaker": b,
                            "markets": {
                                "1X2": {
                                    "Home": h,
                                    "Draw": d,
                                    "Away": a
                                }
                            }
                        })
                else:
                    # Normal match with slight differences (no guaranteed surebet)
                    base_h, base_d, base_a = 2.10, 3.30, 3.10
                    for b in bookmakers:
                        # Slight random noise
                        h = round(base_h + random.uniform(-0.15, 0.15), 2)
                        d = round(base_d + random.uniform(-0.15, 0.15), 2)
                        a = round(base_a + random.uniform(-0.15, 0.15), 2)
                        simulated_results.append({
                            "home_team": match["home"],
                            "away_team": match["away"],
                            "sport": match["sport"],
                            "event_date": event_date,
                            "bookmaker": b,
                            "markets": {
                                "1X2": {
                                    "Home": h,
                                    "Draw": d,
                                    "Away": a
                                }
                            }
                        })

            elif match["sport"] == "Tennis":
                # Generate Home/Away outcomes (2-way)
                # Let's inject a surebet for "Carlos Alcaraz vs Jannik Sinner"
                # Bookmaker D (Betfair) has Player 1 = 2.15
                # Bookmaker E (1xBet) has Player 2 = 2.10
                # Implied prob = 1/2.15 + 1/2.10 = 0.4651 + 0.4761 = 0.9412 (ROI ~ 6.2%)
                for b in bookmakers:
                    if b == "Betfair":
                        p1, p2 = 2.15, 1.70
                    elif b == "1xBet":
                        p1, p2 = 1.65, 2.10
                    else:
                        p1, p2 = 1.85, 1.95

                    simulated_results.append({
                        "home_team": match["home"],
                        "away_team": match["away"],
                        "sport": match["sport"],
                        "event_date": event_date,
                        "bookmaker": b,
                        "markets": {
                            "Home_Away": {
                                "Home": p1,
                                "Away": p2
                            }
                        }
                    })

            elif match["sport"] == "Basketball":
                # Normal match, 2-way Over/Under market
                # Let's inject an Over/Under surebet:
                # Bookmaker F (Sportingbet) has Over = 2.05
                # Bookmaker A (Bet365) has Under = 2.08
                # Implied prob = 1/2.05 + 1/2.08 = 0.4878 + 0.4807 = 0.9685 (ROI ~ 3.2%)
                for b in bookmakers:
                    if b == "Sportingbet":
                        over, under = 2.05, 1.80
                    elif b == "Bet365":
                        over, under = 1.75, 2.08
                    else:
                        over, under = 1.90, 1.90

                    simulated_results.append({
                        "home_team": match["home"],
                        "away_team": match["away"],
                        "sport": match["sport"],
                        "event_date": event_date,
                        "bookmaker": b,
                        "markets": {
                            "Over_Under_215.5": {
                                "Over": over,
                                "Under": under
                            }
                        }
                    })

        return simulated_results
