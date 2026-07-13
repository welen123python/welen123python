from typing import List, Dict, Any
from bs4 import BeautifulSoup
from app.scraper.base import BaseScraper, logger

class BetfairScraper(BaseScraper):
    def __init__(self):
        super().__init__("Betfair", "https://www.betfair.com")

    async def scrape(self) -> List[Dict[str, Any]]:
        html_sample = """
        <table class="market-table">
          <tr class="runner-row" data-sport="Soccer">
            <td class="match-name">Real Madrid v Barcelona</td>
            <td class="back-cell" data-runner="Home">2.08</td>
            <td class="back-cell" data-runner="Draw">3.35</td>
            <td class="back-cell" data-runner="Away">3.15</td>
          </tr>
        </table>
        """
        try:
            soup = BeautifulSoup(html_sample, "html.parser")
            events = []
            for row in soup.find_all("tr", class_="runner-row"):
                teams_text = row.find("td", class_="match-name").text.strip()
                home, away = [t.strip() for t in teams_text.split("v")]
                sport = row.get("data-sport", "Soccer")

                home_odds = float(row.find("td", {"data-runner": "Home"}).text)
                draw_odds = float(row.find("td", {"data-runner": "Draw"}).text)
                away_odds = float(row.find("td", {"data-runner": "Away"}).text)

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
            logger.error(f"Error parsing in BetfairScraper: {str(e)}")
            return []
