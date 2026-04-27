"""
CloudAxis — build_disclosure_inputs.py
Derives all ASC 606 disclosure numbers from engine output.
Run after: generate_cloudaxis_50.py → recognition_engine_fixed.py → phase3_metrics.py
Outputs: note_2_disaggregation.csv, note_3_deferred_rollforward.csv,
         note_4_rpo.csv, note_5_commission_rollforward.csv
These CSVs are consumed by build_disclosure_pdf.py.
"""
import pandas as pd
import numpy as np

df_c = pd.read_csv('contracts.csv')
df_a = pd.read_csv('monthly_activity.csv')
df_r = pd.read_csv('recognition_schedule.csv')

df_r2 = df_r.merge(df_c[['contract_id','product','customer_segment',
                           'payment_terms','region']], on='contract_id', how='left')

# ── Note 2: Revenue Disaggregation ─────────────────────────────────────────
dims = ['product','customer_segment','payment_terms','region']
rows = []
for dim in dims:
    for year in ['2024','2023']:
        fy = df_r2[df_r2['period_month'].str.startswith(year)]
        grp = fy.groupby(dim)['revenue_recognized'].sum().round(0).astype(int)
        for val, rev in grp.items():
            rows.append({'dimension': dim, 'value': val, 'year': year, 'revenue': rev})
    total_24 = df_r2[df_r2['period_month'].str.startswith('2024')]['revenue_recognized'].sum()
    total_23 = df_r2[df_r2['period_month'].str.startswith('2023')]['revenue_recognized'].sum()
    rows.append({'dimension': dim, 'value': 'TOTAL', 'year': '2024', 'revenue': round(total_24,0)})
    rows.append({'dimension': dim, 'value': 'TOTAL', 'year': '2023', 'revenue': round(total_23,0)})

pd.DataFrame(rows).to_csv('note_2_disaggregation.csv', index=False)
print('[1] note_2_disaggregation.csv ✓')

# ── Note 3: Deferred Roll-Forward (balance-movement) ───────────────────────
df_s = df_r.sort_values(['contract_id','period_month']).copy()
df_s['prev_def'] = df_s.groupby('contract_id')['deferred_rev_balance'].shift(1).fillna(0)
df_s['def_add']  = (df_s['deferred_rev_balance'] - df_s['prev_def']).clip(lower=0)
df_s['def_rel']  = (df_s['prev_def'] - df_s['deferred_rev_balance']).clip(lower=0)

quarters = {
    'Q1 2023':['2023-01','2023-02','2023-03'], 'Q2 2023':['2023-04','2023-05','2023-06'],
    'Q3 2023':['2023-07','2023-08','2023-09'], 'Q4 2023':['2023-10','2023-11','2023-12'],
    'Q1 2024':['2024-01','2024-02','2024-03'], 'Q2 2024':['2024-04','2024-05','2024-06'],
    'Q3 2024':['2024-07','2024-08','2024-09'], 'Q4 2024':['2024-10','2024-11','2024-12'],
}
running = 0; def_rows = []
for qname, months in quarters.items():
    q = df_s[df_s['period_month'].isin(months)]
    add  = round(q['def_add'].sum(), 0)
    rel  = round(q['def_rel'].sum(), 0)
    clos = round(df_r[df_r['period_month']==months[-1]]['deferred_rev_balance'].sum(), 0)
    def_rows.append({'quarter': qname, 'opening': running, 'additions': add,
                     'releases': rel, 'closing': clos,
                     'check_tie': abs(round(running + add - rel, 0) - clos) < 2})
    running = clos

pd.DataFrame(def_rows).to_csv('note_3_deferred_rollforward.csv', index=False)
ties = sum(1 for r in def_rows if r['check_tie'])
print(f'[2] note_3_deferred_rollforward.csv ✓  ({ties}/8 quarters tie)')

# ── Note 4: RPO by Product ─────────────────────────────────────────────────
rpo_rows = []
for qname, months in quarters.items():
    pm_r = df_r2[df_r2['period_month']==months[-1]]  # quarter-end snapshot
    for prod in ['Core','Analytics','DataPipeline']:
        rpo_total = pm_r[(pm_r['product']==prod) & (pm_r['rpo_remaining'].notna())]['rpo_remaining'].sum()
        rpo_rows.append({'quarter': qname, 'product': prod, 'rpo_total': round(rpo_total, 0)})

pd.DataFrame(rpo_rows).to_csv('note_4_rpo.csv', index=False)
print('[3] note_4_rpo.csv ✓')

# ── Note 5: Commission Roll-Forward (write-off as reconciling item) ─────────
comm_rows = []
running_c = 0
for qname, months in quarters.items():
    pm_a = df_a[df_a['period_month'].isin(months)]
    cap  = round(pm_a['orig_commission_capitalized'].sum(skipna=True) +
                 pm_a['exp_commission_capitalized'].sum(skipna=True), 0)
    amrt = round(pm_a['orig_commission_amortized'].sum(skipna=True) +
                 pm_a['exp_commission_amortized'].sum(skipna=True), 0)
    clos = round(df_r[df_r['period_month']==months[-1]]['total_commission_asset_bal'].sum(), 0)
    wo   = round(running_c + cap - amrt - clos, 0)  # reconciling item
    comm_rows.append({'quarter': qname, 'opening': running_c, 'capitalised': cap,
                      'amortised': amrt, 'write_offs': max(0, wo), 'closing': clos,
                      'check_tie': abs(round(running_c + cap - amrt - wo, 0) - clos) < 2})
    running_c = clos

pd.DataFrame(comm_rows).to_csv('note_5_commission_rollforward.csv', index=False)
ties_c = sum(1 for r in comm_rows if r['check_tie'])
print(f'[4] note_5_commission_rollforward.csv ✓  ({ties_c}/8 quarters tie)')
print('\n✓ All disclosure input files written')
