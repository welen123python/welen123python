from typing import List, Dict, Any
from bs4 import BeautifulSoup
from app.scraper.base import BaseScraper, logger

class BetanoScraper(BaseScraper):
    def __init__(self):
        super().__init__("Betano", "https://www.betano.com")

    async def scrape(self) -> List[Dict[str, Any]]:
        html_sample = """
        <div class="events-container">
          <div class="event-card" data-sport="Soccer">
            <span class="home-team">Real Madrid CF</span>
            <span class="away-team">Barcelona FC</span>
            <div class="market-odds">
              <span class="odd" data-type="1">2.15</span>
              <span class="odd" data-type="X">3.50</span>
              <span class="odd" data-type="2">3.10</span>
            </div>
          </div>
        </div>
        """
        try:
            soup = BeautifulSoup(html_sample, "html.parser")
            events = []
            for card in soup.find_all("div", class_="event-card"):
                home = card.find("span", class_="home-team").text.strip()
                away = card.find("span", class_="away-team").text.strip()
                sport = card.get("data-sport", "Soccer")

                home_odds = float(card.find("span", {"data-type": "1"}).text)
                draw_odds = float(card.find("span", {"data-type": "X"}).text)
                away_odds = float(card.find("span", {"data-type": "2"}).text)

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
            logger.error(f"Error parsing in BetanoScraper: {str(e)}")
            return []
