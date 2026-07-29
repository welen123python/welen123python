import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url

    async def fetch_html(self, url: str) -> str:
        """
        Asynchronously fetches HTML page content with robust error handling.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/115.0.0.0 Safari/537.36"
                    )
                }
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Error fetching {url} for bookmaker {self.name}: {str(e)}")
            return ""

    @abstractmethod
    async def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrapes odds and returns a standardized list of match details.
        Expected format:
        [
            {
                "home_team": str,
                "away_team": str,
                "sport": str,
                "event_date": datetime (optional),
                "markets": {
                    "1X2": {
                        "Home": float,
                        "Draw": float,
                        "Away": float
                    },
                    ...
                }
            }
        ]
        """
        pass
