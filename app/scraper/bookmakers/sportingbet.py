from typing import List, Dict, Any
from bs4 import BeautifulSoup
from app.scraper.base import BaseScraper, logger

class SportingbetScraper(BaseScraper):
    def __init__(self):
        super().__init__("Sportingbet", "https://www.sportingbet.com")

    async def scrape(self) -> List[Dict[str, Any]]:
        html_sample = """
        <div class="sportingbet-event" data-sport="Soccer">
          <div class="event-title">Real Madrid vs Barcelona</div>
          <div class="odds-row">
            <span class="odd-button" data-o="Home">2.18</span>
            <span class="odd-button" data-o="Draw">3.30</span>
            <span class="odd-button" data-o="Away">3.12</span>
          </div>
        </div>
        """
        try:
            soup = BeautifulSoup(html_sample, "html.parser")
            events = []
            for event in soup.find_all("div", class_="sportingbet-event"):
                title = event.find("div", class_="event-title").text.strip()
                home, away = [t.strip() for t in title.split("vs")]
                sport = event.get("data-sport", "Soccer")

                home_odds = float(event.find("span", {"data-o": "Home"}).text)
                draw_odds = float(event.find("span", {"data-o": "Draw"}).text)
                away_odds = float(event.find("span", {"data-o": "Away"}).text)

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
            logger.error(f"Error parsing in SportingbetScraper: {str(e)}")
            return []
