from typing import List, Dict, Any, Tuple
from app.services.normalization import NormalizationService
from app.config import settings

class SurebetAnalyzer:
    @staticmethod
    def calculate_arbitrage_2way(odd1: float, odd2: float) -> Tuple[float, float]:
        """
        Calculates arbitrage percentage and ROI for a 2-way market.
        Returns (arbitrage_percentage, ROI)
        """
        if odd1 <= 0 or odd2 <= 0:
            return 1.0, 0.0
        arb_pct = (1.0 / odd1) + (1.0 / odd2)
        roi = (1.0 / arb_pct) - 1.0 if arb_pct < 1.0 else 0.0
        return arb_pct, roi

    @staticmethod
    def calculate_arbitrage_3way(odd1: float, odd2: float, odd3: float) -> Tuple[float, float]:
        """
        Calculates arbitrage percentage and ROI for a 3-way market.
        Returns (arbitrage_percentage, ROI)
        """
        if odd1 <= 0 or odd2 <= 0 or odd3 <= 0:
            return 1.0, 0.0
        arb_pct = (1.0 / odd1) + (1.0 / odd2) + (1.0 / odd3)
        roi = (1.0 / arb_pct) - 1.0 if arb_pct < 1.0 else 0.0
        return arb_pct, roi

    @staticmethod
    def calculate_stakes(total_investment: float, odds_list: List[float], arb_pct: float) -> List[float]:
        """
        Calculates optimal individual stakes for a list of odds to secure equal profit.
        """
        if arb_pct >= 1.0 or arb_pct <= 0:
            # If not an arbitrage, distribute equally as a fallback
            return [round(total_investment / len(odds_list), 2) for _ in odds_list]

        stakes = []
        for odd in odds_list:
            stake = total_investment / (odd * arb_pct)
            stakes.append(round(stake, 2))

        # Adjust rounding errors slightly to sum to total_investment
        diff = round(total_investment - sum(stakes), 2)
        if diff != 0 and len(stakes) > 0:
            stakes[0] = round(stakes[0] + diff, 2)

        return stakes

    @classmethod
    def group_scraped_data(cls, scraped_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Groups raw odds data from different bookmakers into canonical events.
        """
        canonical_events: List[Dict[str, Any]] = []

        for item in scraped_data:
            home = item.get("home_team")
            away = item.get("away_team")
            sport = item.get("sport", "Soccer")
            bookmaker = item.get("bookmaker")
            markets = item.get("markets", {})

            if not home or not away or not bookmaker:
                continue

            # Check if this event matches any existing canonical event
            found_event = None
            for ce in canonical_events:
                if NormalizationService.match_events(ce, item):
                    found_event = ce
                    break

            if found_event is None:
                # Create a new canonical event
                found_event = {
                    "home_team": home,
                    "away_team": away,
                    "sport": sport,
                    "bookmakers_odds": {}
                }
                canonical_events.append(found_event)

            # Store the odds of this bookmaker
            found_event["bookmakers_odds"][bookmaker] = markets

        return canonical_events

    @classmethod
    def analyze(cls, scraped_data: List[Dict[str, Any]], total_investment: float = None) -> List[Dict[str, Any]]:
        """
        Analyzes the grouped events and returns a list of identified surebets.
        """
        if total_investment is None:
            total_investment = settings.DEFAULT_INVESTMENT

        grouped_events = cls.group_scraped_data(scraped_data)
        surebets_found = []

        for ce in grouped_events:
            # Gather all market types present across all bookmakers for this event
            all_market_types = set()
            for b_name, markets in ce["bookmakers_odds"].items():
                all_market_types.update(markets.keys())

            for market_type in all_market_types:
                # We need to find the best odds for each outcome of this market
                # Let's support 2-way and 3-way markets dynamically.
                # First, collect all outcomes for this market across all bookmakers
                outcome_to_best_odd = {}  # outcome_name -> {"odd": float, "bookmaker": str}

                for b_name, markets in ce["bookmakers_odds"].items():
                    market_odds = markets.get(market_type, {})
                    for outcome, odd_val in market_odds.items():
                        if not odd_val:
                            continue
                        try:
                            odd_val = float(odd_val)
                        except ValueError:
                            continue

                        if outcome not in outcome_to_best_odd or odd_val > outcome_to_best_odd[outcome]["odd"]:
                            outcome_to_best_odd[outcome] = {
                                "odd": odd_val,
                                "bookmaker": b_name
                            }

                # We require all standard outcomes of the market to be present to compute surebets
                # For 1X2 market, we need Home, Draw, Away
                # For 2-way market (like Home_Away, Over_Under, etc.), we need 2 outcomes (e.g. Home & Away, Over & Under)
                outcomes_keys = list(outcome_to_best_odd.keys())

                # Check 3-way market (usually 1X2)
                if len(outcomes_keys) == 3 and any(k in ["Home", "Draw", "Away"] for k in outcomes_keys):
                    # Standardize order: Home, Draw, Away
                    ordered_outcomes = ["Home", "Draw", "Away"]
                    if all(o in outcome_to_best_odd for o in ordered_outcomes):
                        o1 = outcome_to_best_odd["Home"]
                        o2 = outcome_to_best_odd["Draw"]
                        o3 = outcome_to_best_odd["Away"]

                        arb_pct, roi = cls.calculate_arbitrage_3way(o1["odd"], o2["odd"], o3["odd"])
                        if arb_pct < 1.0:
                            odds_list = [o1["odd"], o2["odd"], o3["odd"]]
                            stakes = cls.calculate_stakes(total_investment, odds_list, arb_pct)

                            surebets_found.append({
                                "home_team": ce["home_team"],
                                "away_team": ce["away_team"],
                                "sport": ce["sport"],
                                "market_type": market_type,
                                "arbitrage_percentage": round(arb_pct * 100, 2),
                                "roi": round(roi * 100, 2),
                                "payout": round(total_investment * (1.0 / arb_pct), 2),
                                "net_profit": round((total_investment * (1.0 / arb_pct)) - total_investment, 2),
                                "outcomes": [
                                    {"outcome_name": "Home", "odd": o1["odd"], "bookmaker": o1["bookmaker"], "stake": stakes[0], "pct": round((stakes[0]/total_investment)*100, 2)},
                                    {"outcome_name": "Draw", "odd": o2["odd"], "bookmaker": o2["bookmaker"], "stake": stakes[1], "pct": round((stakes[1]/total_investment)*100, 2)},
                                    {"outcome_name": "Away", "odd": o3["odd"], "bookmaker": o3["bookmaker"], "stake": stakes[2], "pct": round((stakes[2]/total_investment)*100, 2)}
                                ]
                            })

                # Check 2-way markets (Home_Away, Over_Under, etc.)
                elif len(outcomes_keys) == 2:
                    # Let's say outcomes are outcome1 and outcome2
                    k1, k2 = outcomes_keys[0], outcomes_keys[1]
                    o1 = outcome_to_best_odd[k1]
                    o2 = outcome_to_best_odd[k2]

                    arb_pct, roi = cls.calculate_arbitrage_2way(o1["odd"], o2["odd"])
                    if arb_pct < 1.0:
                        odds_list = [o1["odd"], o2["odd"]]
                        stakes = cls.calculate_stakes(total_investment, odds_list, arb_pct)

                        surebets_found.append({
                            "home_team": ce["home_team"],
                            "away_team": ce["away_team"],
                            "sport": ce["sport"],
                            "market_type": market_type,
                            "arbitrage_percentage": round(arb_pct * 100, 2),
                            "roi": round(roi * 100, 2),
                            "payout": round(total_investment * (1.0 / arb_pct), 2),
                            "net_profit": round((total_investment * (1.0 / arb_pct)) - total_investment, 2),
                            "outcomes": [
                                {"outcome_name": k1, "odd": o1["odd"], "bookmaker": o1["bookmaker"], "stake": stakes[0], "pct": round((stakes[0]/total_investment)*100, 2)},
                                {"outcome_name": k2, "odd": o2["odd"], "bookmaker": o2["bookmaker"], "stake": stakes[1], "pct": round((stakes[1]/total_investment)*100, 2)}
                            ]
                        })

        return surebets_found
