from app.services.analyzer import SurebetAnalyzer

def test_calculate_arbitrage_2way_no_surebet():
    # Arb percent = 1/1.90 + 1/1.90 = 0.5263 + 0.5263 = 1.0526 (>= 1.0, no surebet)
    arb_pct, roi = SurebetAnalyzer.calculate_arbitrage_2way(1.90, 1.90)
    assert arb_pct >= 1.0
    assert roi == 0.0

def test_calculate_arbitrage_2way_with_surebet():
    # Arb percent = 1/2.10 + 1/2.15 = 0.4761 + 0.4651 = 0.9413 (< 1.0, surebet exists!)
    arb_pct, roi = SurebetAnalyzer.calculate_arbitrage_2way(2.10, 2.15)
    assert arb_pct < 1.0
    assert roi > 0.0
    assert round(roi * 100, 2) == 6.24

def test_calculate_arbitrage_3way_no_surebet():
    # Arb percent = 1/2.10 + 1/3.20 + 1/3.00 = 0.476 + 0.3125 + 0.333 = 1.12 (> 1.0, no surebet)
    arb_pct, roi = SurebetAnalyzer.calculate_arbitrage_3way(2.10, 3.20, 3.0)
    assert arb_pct >= 1.0
    assert roi == 0.0

def test_calculate_arbitrage_3way_with_surebet():
    # Arb percent = 1/3.20 + 1/3.60 + 1/3.40 = 0.3125 + 0.2778 + 0.2941 = 0.8844 (< 1.0, surebet!)
    arb_pct, roi = SurebetAnalyzer.calculate_arbitrage_3way(3.20, 3.60, 3.40)
    assert arb_pct < 1.0
    assert roi > 0.0
    assert round(roi * 100, 2) == 13.07

def test_calculate_stakes():
    # Total = 1000, odds = [2.10, 2.15], arb_pct = 0.9413
    stakes = SurebetAnalyzer.calculate_stakes(1000.0, [2.10, 2.15], 0.9413067552)
    assert sum(stakes) == 1000.0
    assert stakes[0] == 505.88
    assert stakes[1] == 494.12
