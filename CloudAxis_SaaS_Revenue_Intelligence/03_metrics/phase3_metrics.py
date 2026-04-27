"""
CloudAxis Inc. — Phase 3 Metrics Computation
Reads: contracts.csv, monthly_activity.csv, recognition_schedule.csv
Outputs: 8 metric CSV files ready for Excel + dashboard
"""
import pandas as pd
import numpy as np
from pathlib import Path

df_c = pd.read_csv('/mnt/user-data/outputs/contracts.csv')
df_a_raw = pd.read_csv('/mnt/user-data/outputs/monthly_activity.csv')
df_a = df_a_raw.copy()
df_r = pd.read_csv('/mnt/user-data/outputs/recognition_schedule.csv')

PERIODS = sorted(df_a['period_month'].unique())
GROSS_MARGIN = 0.72          # SaaS gross margin assumption
S_AND_M_PCT  = 0.25          # S&M as % of revenue (for CAC denominator estimate)

# ─── enrich activity with segment / product ──────────────────────────────────
df_a = df_a.merge(df_c[['contract_id','customer_segment','product','cohort_month',
                          'price_per_seat','base_mrr',
                          'expected_customer_life_months']], on='contract_id', how='left')

# ══════════════════════════════════════════════════════════════════════════════
# 1. MRR WATERFALL — monthly movement table
# ══════════════════════════════════════════════════════════════════════════════
rows = []
for period in PERIODS:
    pm = df_a[df_a['period_month'] == period]

    new_mrr         = pm[pm['mrr_movement_type']=='new']['mrr_this_month'].sum()
    expansion_mrr   = pm[pm['mrr_movement_type']=='expansion']['modification_delta_mrr'].sum()
    contraction_mrr = abs(pm[pm['mrr_movement_type']=='contraction']['modification_delta_mrr'].sum())
    churned_mrr     = pm[pm['mrr_movement_type']=='churned']['mrr_this_month'].sum()
    reactivation    = pm[pm['mrr_movement_type']=='reactivation']['mrr_this_month'].sum()

    # Total MRR = all active (non-trial) contracts in this period
    active_mrr = pm[(pm['is_in_trial']==False) & (pm['mrr_this_month']>0)]['mrr_this_month'].sum()
    active_customers = pm[(pm['is_in_trial']==False) & (pm['mrr_this_month']>0)]['customer_id'].nunique()

    rows.append({
        'period_month':    period,
        'new_mrr':         round(new_mrr, 2),
        'expansion_mrr':   round(expansion_mrr, 2),
        'contraction_mrr': round(contraction_mrr, 2),
        'churned_mrr':     round(churned_mrr, 2),
        'reactivation_mrr':round(reactivation, 2),
        'net_new_mrr':     round(new_mrr + expansion_mrr - contraction_mrr - churned_mrr + reactivation, 2),
        'total_mrr':       round(active_mrr, 2),
        'arr':             round(active_mrr * 12, 2),
        'active_customers':active_customers,
    })

mrr_waterfall = pd.DataFrame(rows)
mrr_waterfall.to_csv('metrics_mrr_waterfall.csv', index=False)
print(f"[1] MRR waterfall: {len(mrr_waterfall)} periods")

# ══════════════════════════════════════════════════════════════════════════════
# 2. NRR / GRR — rolling 12-month retention
# ══════════════════════════════════════════════════════════════════════════════
rows = []
for i, period in enumerate(PERIODS):
    if i < 12:
        continue
    base_period = PERIODS[i - 12]

    # Customers active in base period
    base = df_a[(df_a['period_month']==base_period) &
                (df_a['is_in_trial']==False) &
                (df_a['mrr_this_month']>0)][['customer_id','mrr_this_month']].copy()
    base = base.groupby('customer_id')['mrr_this_month'].sum().reset_index()
    base.columns = ['customer_id','base_mrr']

    # Current MRR from those same customers
    curr = df_a[(df_a['period_month']==period) &
                (df_a['is_in_trial']==False)][['customer_id','mrr_this_month']].copy()
    curr = curr.groupby('customer_id')['mrr_this_month'].sum().reset_index()
    curr.columns = ['customer_id','curr_mrr']

    merged = base.merge(curr, on='customer_id', how='left').fillna(0)
    merged['capped_mrr'] = merged[['base_mrr','curr_mrr']].min(axis=1)

    starting = merged['base_mrr'].sum()
    if starting == 0:
        continue

    nrr = round(merged['curr_mrr'].sum() / starting * 100, 1)
    grr = round(merged['capped_mrr'].sum() / starting * 100, 1)

    rows.append({
        'period_month': period,
        'base_period':  base_period,
        'starting_mrr': round(starting, 2),
        'ending_mrr':   round(merged['curr_mrr'].sum(), 2),
        'nrr_pct':      nrr,
        'grr_pct':      grr,
    })

nrr_grr = pd.DataFrame(rows)
nrr_grr.to_csv('metrics_nrr_grr.csv', index=False)
print(f"[2] NRR/GRR: {len(nrr_grr)} periods")

# ══════════════════════════════════════════════════════════════════════════════
# 3. COHORT RETENTION — by cohort_month × months_since_start
# ══════════════════════════════════════════════════════════════════════════════
cohort_map = df_c.groupby('customer_id')['cohort_month'].first().reset_index()
df_a_coh = df_a_raw.merge(cohort_map, on='customer_id', how='left')

rows = []
for cohort in sorted(df_a_coh['cohort_month'].dropna().unique()):
    cust_in_cohort = cohort_map[cohort_map['cohort_month']==cohort]['customer_id'].unique()
    # Base MRR: month 0 (cohort month itself)
    base = df_a_coh[(df_a_coh['cohort_month']==cohort) &
                    (df_a_coh['period_month']==cohort) &
                    (df_a_coh['is_in_trial']==False)]['mrr_this_month'].sum()
    if base == 0:
        continue

    for period in PERIODS:
        if period < cohort:
            continue
        months = (int(period[:4]) - int(cohort[:4]))*12 + (int(period[5:7]) - int(cohort[5:7]))
        curr = df_a_coh[(df_a_coh['cohort_month']==cohort) &
                        (df_a_coh['period_month']==period) &
                        (df_a_coh['is_in_trial']==False)]['mrr_this_month'].sum()
        rows.append({
            'cohort_month':  cohort,
            'period_month':  period,
            'months_since':  months,
            'cohort_mrr':    round(curr, 2),
            'base_mrr':      round(base, 2),
            'retention_pct': round(curr / base * 100, 1),
        })

cohort_ret = pd.DataFrame(rows)
cohort_ret.to_csv('metrics_cohort_retention.csv', index=False)
print(f"[3] Cohort retention: {len(cohort_ret)} rows")

# ══════════════════════════════════════════════════════════════════════════════
# 4. LTV : CAC by segment and period
# ══════════════════════════════════════════════════════════════════════════════
rows = []
for period in PERIODS:
    pm = df_a[df_a['period_month']==period]

    for seg in ['SMB','Mid-Market','Enterprise']:
        seg_pm = pm[pm['customer_segment']==seg]
        active  = seg_pm[(seg_pm['is_in_trial']==False) & (seg_pm['mrr_this_month']>0)]
        n_active = active['customer_id'].nunique()
        if n_active == 0:
            continue

        avg_mrr = active['mrr_this_month'].sum() / n_active

        # Monthly churn: churned customers this period / customers last period
        churned_n = seg_pm[seg_pm['mrr_movement_type']=='churned']['customer_id'].nunique()
        churn_rate = churned_n / max(n_active, 1)

        ltv = round((avg_mrr * GROSS_MARGIN) / max(churn_rate, 0.001), 0)

        # CAC: commissions capitalized this period for new customers in segment
        new_caps = seg_pm[seg_pm['commission_event_type']=='original_asset_created']['orig_commission_capitalized'].sum()
        new_custs = seg_pm[seg_pm['mrr_movement_type']=='new']['customer_id'].nunique()
        cac = round(new_caps / max(new_custs, 1), 0)

        payback = round(cac / max(avg_mrr * GROSS_MARGIN, 1), 1) if cac > 0 else None
        ltv_cac = round(ltv / cac, 1) if cac > 0 else None

        rows.append({
            'period_month':   period,
            'segment':        seg,
            'active_customers': n_active,
            'avg_mrr':        round(avg_mrr, 2),
            'monthly_churn_rate': round(churn_rate * 100, 2),
            'ltv':            ltv,
            'cac':            cac,
            'ltv_cac_ratio':  ltv_cac,
            'payback_months': payback,
        })

ltv_cac = pd.DataFrame(rows)
ltv_cac.to_csv('metrics_ltv_cac.csv', index=False)
print(f"[4] LTV:CAC: {len(ltv_cac)} rows")

# ══════════════════════════════════════════════════════════════════════════════
# 5. BILLINGS vs REVENUE RECONCILIATION — monthly
# ══════════════════════════════════════════════════════════════════════════════
rows = []
running_def = 0
running_ca  = 0

for period in PERIODS:
    pm_a = df_a[df_a['period_month']==period]
    pm_r = df_r[df_r['period_month']==period]

    billings   = pm_a['amount_billed'].sum()
    revenue    = pm_r['revenue_recognized'].sum()
    impl_rev   = pm_a['impl_fee_recognized'].sum(skipna=True)

    # Closing deferred + CA from recognition schedule
    # Use the sum at period end across all contracts
    period_contracts = pm_r['contract_id'].unique()
    deferred_close = pm_r.groupby('contract_id')['deferred_rev_balance'].last().sum()
    ca_close       = pm_r.groupby('contract_id')['contract_asset_balance'].last().sum()

    deferred_move  = round(deferred_close - running_def, 2)
    ca_move        = round(ca_close - running_ca, 2)
    running_def    = deferred_close
    running_ca     = ca_close

    rows.append({
        'period_month':       period,
        'billings':           round(billings, 2),
        'revenue_recognized': round(revenue, 2),
        'impl_fee_portion':   round(impl_rev, 2),
        'billings_vs_revenue':round(billings - revenue, 2),
        'deferred_balance':   round(deferred_close, 2),
        'deferred_movement':  round(deferred_move, 2),
        'contract_asset':     round(ca_close, 2),
        'ca_movement':        round(ca_move, 2),
    })

billings_rev = pd.DataFrame(rows)
billings_rev.to_csv('metrics_billings_vs_revenue.csv', index=False)
print(f"[5] Billings vs Revenue: {len(billings_rev)} periods")

# ══════════════════════════════════════════════════════════════════════════════
# 6. DEFERRED REVENUE ROLL-FORWARD — quarterly
# ══════════════════════════════════════════════════════════════════════════════
# Get month-end deferred for each period
period_def = []
for period in PERIODS:
    pm_r = df_r[df_r['period_month']==period]
    total_def = pm_r['deferred_rev_balance'].sum()
    total_rev = df_a[df_a['period_month']==period]['amount_billed'].sum()
    total_recog = pm_r['revenue_recognized'].sum()
    period_def.append({'period_month': period, 'deferred': total_def,
                       'billings': total_rev, 'recognized': total_recog})

def_df = pd.DataFrame(period_def)
def_df['opening'] = def_df['deferred'].shift(1).fillna(0)
def_df['additions'] = def_df['billings']
def_df['releases']  = def_df['recognized']
def_df['closing']   = def_df['deferred']
deferred_rf = def_df[['period_month','opening','additions','releases','closing']]
deferred_rf.to_csv('metrics_deferred_rollforward.csv', index=False)
print(f"[6] Deferred roll-forward: {len(deferred_rf)} periods")

# ══════════════════════════════════════════════════════════════════════════════
# 7. RPO SCHEDULE — by product, split <12mo and >12mo
# ══════════════════════════════════════════════════════════════════════════════
rows = []
for period in PERIODS:
    pm_r = df_r[df_r['period_month']==period].merge(
        df_c[['contract_id','product']], on='contract_id', how='left')

    for prod in ['Core','Analytics','DataPipeline']:
        prod_r = pm_r[pm_r['product']==prod]
        rpo_contracts = prod_r[prod_r['rpo_remaining'].notna()]

        rpo_total = rpo_contracts['rpo_remaining'].sum()

        rows.append({
            'period_month':    period,
            'product':         prod,
            'rpo_total':       round(rpo_total, 2),
            'rpo_within_12mo': round(rpo_total, 2),   # all annual contracts = within 12mo
            'rpo_beyond_12mo': 0.0,
        })

rpo_df = pd.DataFrame(rows)
rpo_df.to_csv('metrics_rpo.csv', index=False)
print(f"[7] RPO schedule: {len(rpo_df)} rows")

# ══════════════════════════════════════════════════════════════════════════════
# 8. COMMISSION ASSET ROLL-FORWARD — monthly
# ══════════════════════════════════════════════════════════════════════════════
rows = []
for period in PERIODS:
    pm = df_a[df_a['period_month']==period]
    new_cap     = pm['orig_commission_capitalized'].sum(skipna=True) + \
                  pm['exp_commission_capitalized'].sum(skipna=True)
    amort       = pm['orig_commission_amortized'].sum(skipna=True) + \
                  pm['exp_commission_amortized'].sum(skipna=True)
    # Closing balance from recognition schedule
    pm_r = df_r[df_r['period_month']==period]
    closing_bal = pm_r['total_commission_asset_bal'].sum()

    rows.append({
        'period_month':    period,
        'new_capitalized': round(new_cap, 2),
        'amortized':       round(amort, 2),
        'closing_balance': round(closing_bal, 2),
    })

comm_rf = pd.DataFrame(rows)
comm_rf['opening'] = comm_rf['closing_balance'].shift(1).fillna(0)
comm_rf = comm_rf[['period_month','opening','new_capitalized','amortized','closing_balance']]
comm_rf.to_csv('metrics_commission_rollforward.csv', index=False)
print(f"[8] Commission roll-forward: {len(comm_rf)} periods")

print("\n✓ All 8 metric files written successfully")
print("Files: metrics_mrr_waterfall.csv, metrics_nrr_grr.csv, metrics_cohort_retention.csv,")
print("       metrics_ltv_cac.csv, metrics_billings_vs_revenue.csv, metrics_deferred_rollforward.csv,")
print("       metrics_rpo.csv, metrics_commission_rollforward.csv")
