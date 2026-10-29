import csv, statistics

rows = []
with open('fleet_history.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append({
            'car_id': row['car_id'],
            'odometer_km': float(row['odometer_km']),
            'km_since_service': float(row['km_since_service']),
            'avg_daily_km': float(row['avg_daily_km']),
            'load_factor': float(row['load_factor']),
            'age_years': float(row['age_years']),
            'broke_down': int(row['broke_down']),
        })

broken = [r for r in rows if r['broke_down'] == 1]
fine   = [r for r in rows if r['broke_down'] == 0]

print(f'Total rows: {len(rows)}')
print(f'Broke down: {len(broken)}')
print(f'Did not:    {len(fine)}')
print()

features = ['odometer_km', 'km_since_service', 'avg_daily_km', 'load_factor', 'age_years']

for feat in features:
    bv = sorted([r[feat] for r in broken])
    fv = sorted([r[feat] for r in fine])
    b_mean   = statistics.mean(bv)
    f_mean   = statistics.mean(fv)
    b_median = statistics.median(bv)
    f_median = statistics.median(fv)
    abs_diff_mean   = b_mean - f_mean
    abs_diff_median = b_median - f_median
    pct_diff_mean   = ((b_mean - f_mean) / f_mean * 100) if f_mean != 0 else float('inf')
    print(f'--- {feat} ---')
    print(f'  Broken  mean={b_mean:>10.2f}  median={b_median:>10.2f}  min={min(bv):>8.2f}  max={max(bv):>8.2f}')
    print(f'  Fine    mean={f_mean:>10.2f}  median={f_median:>10.2f}  min={min(fv):>8.2f}  max={max(fv):>8.2f}')
    print(f'  Abs diff mean={abs_diff_mean:>+.2f}  ({pct_diff_mean:>+.1f}%)   Abs diff median={abs_diff_median:>+.2f}')
    print()

# Distribution of load_factor for broken vs fine
print('=== load_factor distribution (broken) ===')
lf_broken = sorted([r['load_factor'] for r in broken])
print(lf_broken)

print()
print('=== load_factor distribution (fine) ===')
lf_fine = sorted([r['load_factor'] for r in fine])
print(lf_fine)

# How many broken have load_factor >= 0.60?
print()
high_lf_broken = [r for r in broken if r['load_factor'] >= 0.60]
high_lf_fine   = [r for r in fine   if r['load_factor'] >= 0.60]
print(f'load_factor >= 0.60: broken={len(high_lf_broken)}/{len(broken)} ({100*len(high_lf_broken)/len(broken):.1f}%),  fine={len(high_lf_fine)}/{len(fine)} ({100*len(high_lf_fine)/len(fine):.1f}%)')

high_lf_broken2 = [r for r in broken if r['load_factor'] >= 0.70]
high_lf_fine2   = [r for r in fine   if r['load_factor'] >= 0.70]
print(f'load_factor >= 0.70: broken={len(high_lf_broken2)}/{len(broken)} ({100*len(high_lf_broken2)/len(broken):.1f}%),  fine={len(high_lf_fine2)}/{len(fine)} ({100*len(high_lf_fine2)/len(fine):.1f}%)')

# km_since_service >= 10000?
print()
high_kss_broken = [r for r in broken if r['km_since_service'] >= 10000]
high_kss_fine   = [r for r in fine   if r['km_since_service'] >= 10000]
print(f'km_since_service >= 10000: broken={len(high_kss_broken)}/{len(broken)} ({100*len(high_kss_broken)/len(broken):.1f}%),  fine={len(high_kss_fine)}/{len(fine)} ({100*len(high_kss_fine)/len(fine):.1f}%)')

# Show all broken cars sorted by load_factor
print()
print('=== BROKEN-DOWN CARS (sorted by load_factor desc) ===')
for r in sorted(broken, key=lambda x: x['load_factor'], reverse=True):
    print(f"{r['car_id']}  odo={r['odometer_km']:>7.0f}  kss={r['km_since_service']:>6.0f}  adkm={r['avg_daily_km']:>3.0f}  lf={r['load_factor']:.2f}  age={r['age_years']:>2.0f}")

# avg_daily_km >= 150?
print()
high_adkm_broken = [r for r in broken if r['avg_daily_km'] >= 150]
high_adkm_fine   = [r for r in fine   if r['avg_daily_km'] >= 150]
print(f'avg_daily_km >= 150: broken={len(high_adkm_broken)}/{len(broken)} ({100*len(high_adkm_broken)/len(broken):.1f}%),  fine={len(high_adkm_fine)}/{len(fine)} ({100*len(high_adkm_fine)/len(fine):.1f}%)')
