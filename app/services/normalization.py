from difflib import SequenceMatcher
import re

class NormalizationService:
    @staticmethod
    def clean_name(name: str) -> str:
        """
        Cleans and standardizes names by converting to lowercase, removing common suffixes,
        accents, and special characters.
        """
        if not name:
            return ""
        name = name.lower().strip()

        # Replace non-alphanumeric chars with spaces
        name = re.sub(r"[^\w\s]", " ", name)

        # Suffixes/prefixes to strip
        suffixes = [
            r"\bcf\b", r"\bfc\b", r"\bclub de fútbol\b", r"\bclub de futbol\b",
            r"\bclube\b", r"\bas\b", r"\bus\b", r"\bac\b"
        ]
        for pattern in suffixes:
            name = re.sub(pattern, "", name)

        # Collapse multi-spaces
        name = " ".join(name.split())
        return name

    @classmethod
    def match_names(cls, name_a: str, name_b: str, threshold: float = 0.80) -> bool:
        """
        Returns True if the team names are highly likely to refer to the same team.
        """
        clean_a = cls.clean_name(name_a)
        clean_b = cls.clean_name(name_b)

        if clean_a == clean_b:
            return True

        # Hard check to differentiate City / United / Women etc.
        critical_keywords = ["united", "city", "women", "u21", "u23", "u19", "b", "reserves"]
        for kw in critical_keywords:
            if (kw in clean_a) != (kw in clean_b):
                return False

        # Fallback to string similarity ratio
        ratio = SequenceMatcher(None, clean_a, clean_b).ratio()
        return ratio >= threshold

    @classmethod
    def match_events(cls, event_a: dict, event_b: dict) -> bool:
        """
        Determines if two event dictionaries represent the same sporting match.
        """
        # Ensure identical sports
        if event_a.get("sport", "").lower() != event_b.get("sport", "").lower():
            return False

        home_a = event_a.get("home_team", "")
        away_a = event_a.get("away_team", "")
        home_b = event_b.get("home_team", "")
        away_b = event_b.get("away_team", "")

        # Check direct home-home and away-away matching
        if cls.match_names(home_a, home_b) and cls.match_names(away_a, away_b):
            return True

        # Check reversed if there's any swap
        if cls.match_names(home_a, away_b) and cls.match_names(away_a, home_b):
            return True

        return False
