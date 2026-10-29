# What I checked, and what the agent got wrong

## What the agent got wrong

The agent did not make logical errors, but it did expose two things I had to catch and verify
myself before accepting the work.

**First: the missing-reading behavior.**
When a car has no `last_service_km` entry, the original code defaulted to zero — treating the
car as though it had been serviced at the factory start. I had to confirm that the fix (returning
`False` immediately on a missing key rather than computing a wear percentage from 0) was the
right call, not just a convenient one. It is correct because a missing reading is genuinely
unknown: we cannot infer anything about wear from it, so flagging it would produce false alarms
across the whole un-recorded portion of the fleet.

**Second: the km-to-miles constant.**
`fleet_utils.py` had `MILES_PER_KM = 1.609`. That is the km-per-mile ratio, not miles-per-km.
The correct value is 0.621371. The agent caught this during the helper-module sweep — but I
verified it independently by checking that 100 km * 0.621371 = 62.1 miles (correct) and that
100 km * 1.609 = 160.9 miles (clearly wrong — that is longer than the input in km, which is
impossible). The `verify.py` acceptance check confirms: 100 km must read as 61.0–63.5 miles.

## What I checked before I accepted its work

**Wear bug:** I checked that `wear_percent(14900, 15000)` now returns 99.33 (not 0) by reading
the formula — `(14900 / 15000) * 100` — and by running `python verify.py`, which reports
"a car at 14,900 of 15,000 km reports 99.3%".

**80% threshold unchanged:** `verify.py` checks `SERVICE_INTERVAL_KM == 15000` and
`WARN_AT_PERCENT == 80` explicitly. Both pass. I also read `km_wachter.py` directly to confirm
neither constant was touched.

**Missing-reading fix:** `test_missing_reading_is_not_treated_as_zero` passes, and
`test_summary_does_not_crash_on_missing_reading` passes. `verify.py` reports "a car with no
last-service reading is handled". I also traced the code path: `needs_service()` now returns
`False` on the first line if `last_service_km` is not in the dict.

**Average wear fix:** `verify.py` reports "average wear reads 59.67 (should be about 59.67)".
The original used `//` (integer division), which truncated 59.67 to 59. The fix uses `/`.

**Miles fix:** `verify.py` reports "100 km reads as 62.1 miles". I confirmed the constant
is now 0.621371 in `fleet_utils.py`.

**Test count:** `verify.py` confirms `test_fleet_report.py` holds 2 test functions.
`pytest` reports 9 passed, 0 failed.

## What the data actually said

I ran `python analyze.py` on all 120 cars in `fleet_history.csv` (26 broke down, 94 did not).

**km_since_service** was the strongest separator. Cars that broke down had an average of
11 678 km since their last service, versus 7 261 km for cars that did not — a +60.8% difference
in group means. More concretely, 81% of the broken cars had more than 10 000 km since their last
service, compared to 33% of the fine cars. This is the feature that drives the risk score most.

**avg_daily_km** showed a +21.5% difference (160 vs 131 km/day average). The broken group drove
harder on average, but the overlap between groups is large — many fine cars also have high daily
mileage, so this feature alone is not a reliable predictor.

**load_factor** showed +18.8% difference (0.60 vs 0.51 mean). Some separation exists but the
distributions overlap substantially; a high load factor alone does not reliably indicate a
breakdown.

**The two "obvious" features were flat.** `odometer_km` differed by only +0.3% between groups
(53 448 vs 53 302 km mean — essentially the same). `age_years` differed by -0.2% (5.88 vs 5.89
— identical medians of 5 years in both groups). The common intuition that older or
higher-mileage cars break down more is not supported by this particular dataset.

The risk score uses 0.50 * scaled_km_since_service + 0.30 * scaled_avg_daily_km +
0.20 * scaled_load_factor. It is a heuristic ranking, not a validated model: 8 of the top-10
highest-risk cars in the dataset actually broke down, which is better than chance but not a
reliable prediction.
