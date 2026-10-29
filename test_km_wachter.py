# test_km_wachter.py
from km_wachter import needs_service, wear_percent, SERVICE_INTERVAL_KM, WARN_AT_PERCENT


def test_almost_due_car_is_flagged():
    # A car at 14,900 of its 15,000 km window is about 99% worn and MUST be flagged.
    assert needs_service({"id": "VOS-4471", "odometer": 14900, "last_service_km": 0}) is True


def test_missing_reading_is_not_treated_as_zero():
    # A car with NO last-service reading must not be treated as fully worn.
    assert needs_service({"id": "VOS-7788", "odometer": 92000}) is False


def test_wear_percent_uses_floating_point():
    # 14,900 km of a 15,000 km interval is 99.33…%, not 0% (integer division would give 0).
    pct = wear_percent(14900, SERVICE_INTERVAL_KM)
    assert 99.0 < pct < 100.0


def test_wear_percent_exactly_at_interval():
    # Exactly one full interval = 100 %.
    assert wear_percent(15000, SERVICE_INTERVAL_KM) == 100.0


def test_warn_threshold_is_80_percent():
    # The threshold constant must remain at 80 — do not change this.
    assert WARN_AT_PERCENT == 80


def test_car_just_below_threshold_is_not_flagged():
    # 11,999 km of 15,000 km = 79.99% — just under 80%, must NOT be flagged.
    assert needs_service({"id": "VOS-TEST", "odometer": 11999, "last_service_km": 0}) is False


def test_car_exactly_at_threshold_is_flagged():
    # 12,000 km of 15,000 km = exactly 80% — must be flagged.
    assert needs_service({"id": "VOS-TEST", "odometer": 12000, "last_service_km": 0}) is True
