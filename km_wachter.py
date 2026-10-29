# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Modernised 2025.

SERVICE_INTERVAL_KM: int = 15000
WARN_AT_PERCENT: int = 80


def wear_percent(km_since_service: float, interval: int) -> float:
    """Return how much of the service interval has been consumed, as a percentage."""
    return (km_since_service / interval) * 100


def needs_service(car: dict) -> bool:
    """Return True if the car has consumed 80 % or more of its service interval.

    A missing last_service_km reading is treated as unknown, not as zero,
    so the car is not falsely flagged.
    """
    if "last_service_km" not in car:
        return False
    km_since = car["odometer"] - car["last_service_km"]
    return wear_percent(km_since, SERVICE_INTERVAL_KM) >= WARN_AT_PERCENT


def check_fleet(fleet: list[dict]) -> list[str]:
    """Flag every car that is due for service and return their IDs."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
