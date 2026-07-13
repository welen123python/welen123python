from typing import List, Dict, Any
from bs4 import BeautifulSoup
from app.scraper.base import BaseScraper, logger

class PinnacleScraper(BaseScraper):
    def __init__(self):
        super().__init__("Pinnacle", "https://www.pinnacle.com")

    async def scrape(self) -> List[Dict[str, Any]]:
        html_sample = """
        <div class="pinnacle-event" data-sport="Soccer">
          <span class="teams">Real Madrid - Barcelona FC</span>
          <div class="odds">
            <span class="home-price">2.20</span>
            <span class="draw-price">3.60</span>
            <span class="away-price">3.30</span>
          </div>
        </div>
        """
        try:
            soup = BeautifulSoup(html_sample, "html.parser")
            events = []
            for ev in soup.find_all("div", class_="pinnacle-event"):
                teams_text = ev.find("span", class_="teams").text.strip()
                home, away = [t.strip() for t in teams_text.split("-")]
                sport = ev.get("data-sport", "Soccer")

                home_odds = float(ev.find("span", class_="home-price").text)
                draw_odds = float(ev.find("span", class_="draw-price").text)
                away_odds = float(ev.find("span", class_="away-price").text)

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
            logger.error(f"Error parsing in PinnacleScraper: {str(e)}")
            return []
