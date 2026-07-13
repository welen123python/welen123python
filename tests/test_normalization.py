from app.services.normalization import NormalizationService

def test_clean_name():
    assert NormalizationService.clean_name("Real Madrid CF") == "real madrid"
    assert NormalizationService.clean_name("Barcelona FC") == "barcelona"
    assert NormalizationService.clean_name("Atletico Madrid") == "atletico madrid"
    assert NormalizationService.clean_name("  Sporting CP  ") == "sporting cp"

def test_match_names():
    assert NormalizationService.match_names("Real Madrid CF", "Real Madrid") is True
    assert NormalizationService.match_names("FC Barcelona", "Barcelona FC") is True
    assert NormalizationService.match_names("Bayern Munich", "Bayern München") is True
    assert NormalizationService.match_names("Manchester United", "Manchester City") is False

def test_match_events():
    event_a = {"home_team": "Real Madrid CF", "away_team": "FC Barcelona", "sport": "Soccer"}
    event_b = {"home_team": "Real Madrid", "away_team": "Barcelona", "sport": "Soccer"}
    assert NormalizationService.match_events(event_a, event_b) is True

    # Different sports should not match
    event_c = {"home_team": "Real Madrid", "away_team": "Barcelona", "sport": "Basketball"}
    assert NormalizationService.match_events(event_a, event_c) is False
