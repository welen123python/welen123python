from typing import List, Dict, Any
from bs4 import BeautifulSoup
from app.scraper.base import BaseScraper, logger

class OneXBetScraper(BaseScraper):
    def __init__(self):
        super().__init__("1xBet", "https://www.1xbet.com")

    async def scrape(self) -> List[Dict[str, Any]]:
        html_sample = """
        <div class="xbet-game" data-sport="Soccer">
          <div class="team-names">Real Madrid CF vs Barcelona FC</div>
          <div class="bets">
            <div class="coef" data-outcome="W1">2.12</div>
            <div class="coef" data-outcome="X">3.45</div>
            <div class="coef" data-outcome="W2">3.25</div>
          </div>
        </div>
        """
        try:
            soup = BeautifulSoup(html_sample, "html.parser")
            events = []
            for game in soup.find_all("div", class_="xbet-game"):
                teams_text = game.find("div", class_="team-names").text.strip()
                home, away = [t.strip() for t in teams_text.split("vs")]
                sport = game.get("data-sport", "Soccer")

                home_odds = float(game.find("div", {"data-outcome": "W1"}).text)
                draw_odds = float(game.find("div", {"data-outcome": "X"}).text)
                away_odds = float(game.find("div", {"data-outcome": "W2"}).text)

                events.append({
                    "home_team": home,
                    "away_team": away,
                    "sport": sport,
                    "markets": {
                        "1X2": {
                            "Home": home_odds,
                            "Draw": draw_odds,
                            "Away": away_odds
                        }
                    }
                })
            return events
        except Exception as e:
            logger.error(f"Error parsing in OneXBetScraper: {str(e)}")
            return []
