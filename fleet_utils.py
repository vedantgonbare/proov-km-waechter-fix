# fleet_utils.py
# Conversion and formatting helpers for Vossberg Mobility fleet reports.
# Modernised 2025: removed dead code (parse_service_date, chunk_list, is_due).

MILES_PER_KM: float = 0.621371    # was 1.609 (inverted — that is km-per-mile, not miles-per-km)


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles. Used by the nightly UK partner report."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a number as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list[float]) -> float:
    """Return the arithmetic mean of a list, or 0.0 for an empty list."""
    if not values:
        return 0.0
    return sum(values) / len(values)
