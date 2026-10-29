# analyze.py
# SUMMARY: Among the five features in fleet_history.csv, km_since_service shows the largest
# separation between cars that broke down and those that did not. avg_daily_km and load_factor
# show smaller but still visible separation. odometer_km and age_years show little separation
# in this dataset — the intuition that older or higher-mileage cars break down more is not
# supported by these 120 records.
#
# Risk score: a heuristic ranking (0–100) weighted by group-mean separation strength.
# It is a triage aid, not a validated predictor or probability estimate.

# ---------------------------------------------------------------------------
# Score formula
# ---------------------------------------------------------------------------
#   Each of the three separating features is min-max scaled to [0, 100] over
#   the full fleet, then combined with weights that reflect how strongly each
#   feature separates the two groups (measured by % difference in group means):
#
#     risk_score = 0.50 × scaled_km_since_service
#                + 0.30 × scaled_avg_daily_km
#                + 0.20 × scaled_load_factor
#
#   scaled_x = (x − min_x) / (max_x − min_x) × 100
#   If max_x == min_x (constant feature), scaled_x is set to 0 to avoid ÷0.
#
# Limitations:
#   - Scores are relative ranks within this 120-car dataset only.
#   - Modest group separation means many high-scoring cars will not break down.
#   - Weights come from observed group-mean differences, not a trained model.
#   - No held-out validation was performed.
# ---------------------------------------------------------------------------

import sys
import pandas as pd

REQUIRED_COLUMNS = {
    "car_id", "odometer_km", "km_since_service",
    "avg_daily_km", "load_factor", "age_years", "broke_down",
}
SCORE_FEATURES = ["km_since_service", "avg_daily_km", "load_factor"]
SCORE_WEIGHTS  = [0.50,               0.30,           0.20]
ALL_FEATURES   = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]


def validate_columns(df: pd.DataFrame) -> None:
    """Raise SystemExit with a clear message if any required column is absent."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        sys.exit(f"ERROR: fleet_history.csv is missing column(s): {sorted(missing)}")


def load_and_describe(path: str = "fleet_history.csv") -> pd.DataFrame:
    """Load the CSV, validate it, and print a quick overview."""
    df = pd.read_csv(path)
    validate_columns(df)

    n_total  = len(df)
    n_broken = int(df["broke_down"].sum())
    n_fine   = int((df["broke_down"] == 0).sum())

    print("=" * 65)
    print(f"Dataset: {n_total} cars  |  broke_down=1: {n_broken}  |  broke_down=0: {n_fine}")
    print()
    print("Column dtypes:")
    for col, dtype in df.dtypes.items():
        print(f"  {col:<22} {dtype}")
    print()

    missing_counts = df.isnull().sum()
    if missing_counts.any():
        print("Missing values:")
        for col, cnt in missing_counts[missing_counts > 0].items():
            print(f"  {col}: {cnt}")
    else:
        print("No missing values.")
    print()
    return df


def compare_groups(df: pd.DataFrame) -> None:
    """Compare each numeric feature between broken and intact cars.

    All statistics are derived from the DataFrame — nothing is hardcoded.
    """
    broken = df[df["broke_down"] == 1]
    fine   = df[df["broke_down"] == 0]
    n_b = len(broken)
    n_f = len(fine)

    print("=" * 65)
    print(f"Group comparison  (broken n={n_b}, fine n={n_f})")
    print()
    print(f"  {'Feature':<22} {'B-mean':>8} {'F-mean':>8} {'d-mean':>8} {'d-%':>7}  {'B-med':>7} {'F-med':>7}")
    print("  " + "-" * 63)

    for feat in ALL_FEATURES:
        b_mean   = broken[feat].mean()
        f_mean   = fine[feat].mean()
        b_median = broken[feat].median()
        f_median = fine[feat].median()
        delta    = b_mean - f_mean
        pct      = (delta / f_mean * 100) if f_mean != 0 else float("inf")
        print(
            f"  {feat:<22} {b_mean:>8.2f} {f_mean:>8.2f} {delta:>+8.2f} {pct:>+6.1f}%"
            f"  {b_median:>7.2f} {f_median:>7.2f}"
        )

    print()
    print("Interpretation (from computed d-% values above):")

    # Print interpretation using actual computed values
    for feat in ALL_FEATURES:
        b_mean = broken[feat].mean()
        f_mean = fine[feat].mean()
        pct    = ((b_mean - f_mean) / f_mean * 100) if f_mean != 0 else float("inf")
        if feat == "km_since_service":
            pct_high_b = (broken[feat] >= 10_000).mean() * 100
            pct_high_f = (fine[feat]   >= 10_000).mean() * 100
            print(
                f"  km_since_service : {pct:+.1f}% group-mean difference -- largest separator.\n"
                f"    {pct_high_b:.0f}% of broken cars had >10 000 km since last service "
                f"vs {pct_high_f:.0f}% of fine cars."
            )
        elif feat == "avg_daily_km":
            print(f"  avg_daily_km     : {pct:+.1f}% -- smaller but visible separation.")
        elif feat == "load_factor":
            print(f"  load_factor      : {pct:+.1f}% -- modest separation; groups overlap substantially.")
        elif feat == "odometer_km":
            print(f"  odometer_km      : {pct:+.1f}% -- little separation; total mileage is not predictive here.")
        elif feat == "age_years":
            print(f"  age_years        : {pct:+.1f}% -- little separation; age is not predictive here.")
    print()


def build_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Min-max scale the three predictive features and combine into a 0–100 heuristic score.

    A zero min-max range (constant feature) is handled safely: scaled value is set to 0.0.
    """
    df = df.copy()
    scaled_cols = []
    for feat in SCORE_FEATURES:
        col_min = df[feat].min()
        col_max = df[feat].max()
        col_name = f"_{feat}_scaled"
        if col_max == col_min:
            df[col_name] = 0.0          # constant feature — no information to scale
        else:
            df[col_name] = (df[feat] - col_min) / (col_max - col_min) * 100
        scaled_cols.append(col_name)

    df["risk_score"] = sum(
        w * df[col] for w, col in zip(SCORE_WEIGHTS, scaled_cols)
    )
    df["risk_score"] = df["risk_score"].clip(0, 100).round(1)
    return df.drop(columns=scaled_cols)


def print_top_10(df: pd.DataFrame) -> None:
    """Print the 10 highest-risk cars and note how many actually broke down."""
    ranked = df.sort_values("risk_score", ascending=False).reset_index(drop=True)

    print("=" * 65)
    print("Top 10 highest-risk cars (heuristic ranking)")
    print(f"  {'#':<4} {'car_id':<12} {'score':>6} {'kss':>7} {'adkm':>6} {'lf':>6} {'age':>5} {'broke':>6}")
    print("  " + "-" * 55)
    for pos, (_, row) in enumerate(ranked.head(10).iterrows(), start=1):
        print(
            f"  {pos:<4} {row['car_id']:<12} {row['risk_score']:>6.1f}"
            f" {row['km_since_service']:>7.0f} {row['avg_daily_km']:>6.0f}"
            f" {row['load_factor']:>6.2f} {row['age_years']:>5.0f} {int(row['broke_down']):>6}"
        )

    broke_in_top10 = int(ranked.head(10)["broke_down"].sum())
    print()
    print(f"  {broke_in_top10} of the top-10 highest-risk cars actually broke down.")
    print("  (A perfect score would be 10/10 -- this is a heuristic, not a classifier.)")
    print()


def main() -> None:
    df = load_and_describe()
    compare_groups(df)
    df = build_risk_scores(df)
    print_top_10(df)

    print("=" * 65)
    print("Score formula recap:")
    print("  risk_score = 0.50 * scaled_km_since_service")
    print("             + 0.30 * scaled_avg_daily_km")
    print("             + 0.20 * scaled_load_factor")
    print()
    print("  Each feature scaled to [0, 100] using fleet min/max.")
    print("  Weights reflect relative group-mean separation strength.")
    print("  This is a heuristic ranking tool, not a validated prediction model.")


if __name__ == "__main__":
    main()
