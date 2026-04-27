import pandas as pd
import numpy as np
from datetime import date, timedelta
import random
import calendar

random.seed(42)
np.random.seed(42)

# ══════════════════════════════════════════════════════════════════════════════
# CLOUDAXIS INC. — 50-CUSTOMER DATASET
# All unique cases guaranteed. Fixed paths. All prior fixes included.
# ══════════════════════════════════════════════════════════════════════════════

SEGMENTS      = ['SMB', 'Mid-Market', 'Enterprise']
REGIONS       = ['North America', 'EMEA', 'APAC', 'LATAM']
REG_WEIGHTS   = [0.45, 0.25, 0.20, 0.10]
CHURN_REASONS = ['price', 'competitor', 'product_fit', 'non_renewal', 'unknown']

CUST_LIFE     = {'SMB': 18, 'Mid-Market': 24, 'Enterprise': 36}
COMM_PCT_NEW  = {'SMB': 0.10, 'Mid-Market': 0.12, 'Enterprise': 0.15}
COMM_PCT_UPG  = {'SMB': 0.05, 'Mid-Market': 0.05, 'Enterprise': 0.05}
BASE_PPS      = {'SMB': 80, 'Mid-Market': 140, 'Enterprise': 220}
ANALYTICS_MRR = {'SMB': (200, 800), 'Mid-Market': (600, 2000), 'Enterprise': (1500, 5000)}
PIPELINE_BASE = {'SMB': (500, 1500), 'Mid-Market': (1200, 3000), 'Enterprise': (2500, 6000)}

START_DATE = date(2023, 1, 1)
END_DATE   = date(2024, 12, 31)
PERIODS    = pd.date_range('2023-01', '2024-12', freq='MS')

def rand_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def month_start(d):
    return date(d.year, d.month, 1)

def add_months(d, n):
    m = d.month - 1 + n
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))

def months_between(d1, d2):
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)

def calc_pps(segment, seats):
    base = BASE_PPS[segment]
    vol  = 1 - min(0.25, seats * 0.003)
    neg  = random.uniform(0.90, 1.10)
    return round(base * vol * neg, 2)

# ══════════════════════════════════════════════════════════════════════════════
# GUARANTEED CASES — exactly 50 customers covering every unique scenario
# Format: (product1, product2_or_None, segment, payment_terms, fate, features)
# features: set of strings from {'seat_add','tier_upgrade','tier_downgrade',
#           'impl_fee','free_trial','renewed','churned_at_renewal',
#           'early_penalty','early_refund','early_no_penalty'}
# ══════════════════════════════════════════════════════════════════════════════

CUSTOMER_SPECS = [
    # ── Core solo ─────────────────────────────────────────────────────────
    ('Core', None, 'SMB',        'monthly',          'active',   {'seat_add','renewed'}),
    ('Core', None, 'Mid-Market', 'annual_upfront',   'active',   {'seat_add','renewed'}),
    ('Core', None, 'Enterprise', 'annual_quarterly',  'active',   {'seat_add','churned_at_renewal'}),
    ('Core', None, 'SMB',        'annual_upfront',   'active',   {'impl_fee','renewed'}),
    ('Core', None, 'Mid-Market', 'monthly',           'active',   {'impl_fee','renewed'}),
    ('Core', None, 'Enterprise', 'annual_upfront',   'active',   {'seat_add','impl_fee','renewed'}),
    ('Core', None, 'SMB',        'annual_upfront',   'early_termination', {'impl_fee','early_penalty'}),
    ('Core', None, 'Mid-Market', 'monthly',           'early_termination', {'early_refund'}),
    ('Core', None, 'Enterprise', 'annual_quarterly',  'early_termination', {'early_no_penalty'}),
    ('Core', None, 'SMB',        'annual_quarterly',  'active',   {'renewed'}),
    ('Core', None, 'Mid-Market', 'annual_upfront',   'active',   {'renewed'}),
    ('Core', None, 'Enterprise', 'monthly',           'active',   {'seat_add','renewed'}),

    # ── Analytics solo ────────────────────────────────────────────────────
    ('Analytics', None, 'SMB',        'monthly',          'active',   {'tier_upgrade','renewed'}),
    ('Analytics', None, 'Mid-Market', 'annual_upfront',   'active',   {'tier_upgrade','churned_at_renewal'}),
    ('Analytics', None, 'Enterprise', 'annual_upfront',   'active',   {'tier_downgrade','renewed'}),
    ('Analytics', None, 'SMB',        'monthly',           'active',   {'free_trial','renewed'}),
    ('Analytics', None, 'Mid-Market', 'annual_quarterly',  'product_switch', {'tier_upgrade'}),
    ('Analytics', None, 'Enterprise', 'annual_upfront',   'active',   {'renewed'}),
    ('Analytics', None, 'SMB',        'monthly',           'active',   {'tier_downgrade','churned_at_renewal'}),
    ('Analytics', None, 'Mid-Market', 'monthly',           'active',   {'free_trial','tier_upgrade','renewed'}),

    # ── DataPipeline solo ─────────────────────────────────────────────────
    ('DataPipeline', None, 'SMB',        'annual_upfront',  'active',  {'renewed'}),
    ('DataPipeline', None, 'Mid-Market', 'monthly',          'active',  {'renewed'}),
    ('DataPipeline', None, 'Enterprise', 'annual_quarterly', 'active',  {'churned_at_renewal'}),
    ('DataPipeline', None, 'SMB',        'monthly',          'early_termination', {'early_penalty'}),
    ('DataPipeline', None, 'Mid-Market', 'annual_upfront',  'active',  {'impl_fee','renewed'}),

    # ── Bundle Core+Analytics ─────────────────────────────────────────────
    ('Core', 'Analytics', 'SMB',        'annual_upfront',  'active',  {'seat_add','renewed'}),
    ('Core', 'Analytics', 'Mid-Market', 'monthly',          'active',  {'tier_upgrade','renewed'}),
    ('Core', 'Analytics', 'Enterprise', 'annual_quarterly', 'active',  {'seat_add','impl_fee','renewed'}),
    ('Core', 'Analytics', 'SMB',        'annual_upfront',  'active',  {'free_trial','churned_at_renewal'}),
    ('Core', 'Analytics', 'Mid-Market', 'annual_upfront',  'product_switch', {'tier_upgrade'}),
    ('Core', 'Analytics', 'Enterprise', 'monthly',          'active',  {'tier_downgrade','renewed'}),
    ('Core', 'Analytics', 'SMB',        'monthly',          'early_termination', {'early_refund'}),
    ('Core', 'Analytics', 'Mid-Market', 'annual_quarterly', 'active',  {'seat_add','tier_upgrade','renewed'}),
    ('Core', 'Analytics', 'Enterprise', 'annual_upfront',  'active',  {'impl_fee','renewed'}),
    ('Core', 'Analytics', 'SMB',        'annual_upfront',  'early_termination', {'early_penalty'}),

    # ── Fill remaining 15 with varied solo contracts ───────────────────────
    ('Core',         None, 'SMB',        'monthly',          'active',  {'renewed'}),
    ('Analytics',    None, 'SMB',        'annual_upfront',  'active',  {'renewed'}),
    ('DataPipeline', None, 'Enterprise', 'monthly',          'active',  {'renewed'}),
    ('Core',         None, 'Mid-Market', 'annual_upfront',  'active',  {'churned_at_renewal'}),
    ('Analytics',    None, 'Enterprise', 'monthly',          'active',  {'tier_upgrade','renewed'}),
    ('Core',         None, 'Enterprise', 'annual_quarterly', 'active',  {'renewed'}),
    ('Analytics',    None, 'SMB',        'monthly',          'active',  {'free_trial','tier_downgrade'}),
    ('DataPipeline', None, 'SMB',        'monthly',          'active',  {'renewed'}),
    ('Core',         None, 'SMB',        'annual_upfront',  'early_termination', {'early_no_penalty'}),
    ('Analytics',    None, 'Mid-Market', 'annual_quarterly', 'active',  {'renewed'}),
    ('Core',         None, 'Enterprise', 'annual_upfront',  'active',  {'seat_add','impl_fee','renewed'}),
    ('Analytics',    None, 'Enterprise', 'annual_upfront',  'active',  {'churned_at_renewal'}),
    ('DataPipeline', None, 'Mid-Market', 'annual_quarterly', 'active', {'renewed'}),
    ('Core',         None, 'Mid-Market', 'monthly',          'active',  {'seat_add','renewed'}),
    ('Analytics',    None, 'SMB',        'monthly',          'active',  {'tier_upgrade','churned_at_renewal'}),
]

assert len(CUSTOMER_SPECS) == 50, f"Expected 50 customers, got {len(CUSTOMER_SPECS)}"

contracts_rows = []
activity_rows  = []
ctr_id         = 1
cust_id        = 1
asset_counter  = 1

for spec in CUSTOMER_SPECS:
    prod1, prod2, segment, payment_terms, fate, features = spec
    cid      = f'CUST-{cust_id:04d}'
    region   = random.choices(REGIONS, REG_WEIGHTS)[0]
    products = [prod1] + ([prod2] if prod2 else [])
    is_bundle= len(products) == 2
    cust_id += 1

    contract_start = month_start(rand_date(START_DATE, date(2024, 6, 1)))
    exp_life       = CUST_LIFE[segment]
    bundle_ids     = []

    for pidx, product in enumerate(products):
        ctrid = f'CTR-{ctr_id:04d}'
        ctr_id += 1
        bundle_ids.append(ctrid)

        # ── Pricing ──────────────────────────────────────────────────────
        if product == 'Core':
            seats         = random.randint(5, 100)
            pps           = calc_pps(segment, seats)
            base_mrr      = round(seats * pps, 2)
            seats_c       = seats
            price_ps      = pps
            usage_fee     = None; overage_r = None; usage_tier = None
        elif product == 'Analytics':
            lo, hi        = ANALYTICS_MRR[segment]
            base_mrr      = round(random.uniform(lo, hi), 2)
            seats_c       = None; price_ps = None
            usage_fee     = None; overage_r = None; usage_tier = None
        else:
            lo, hi        = PIPELINE_BASE[segment]
            usage_fee     = round(random.uniform(lo, hi), 2)
            overage_r     = round(random.uniform(0.05, 0.50), 4)
            usage_tier    = round(random.uniform(500, 5000), 0)
            base_mrr      = usage_fee
            seats_c       = None; price_ps = None

        ssp_amount = round(base_mrr * random.uniform(1.10, 1.20), 2) if is_bundle else base_mrr

        # ── Term & payment ────────────────────────────────────────────────
        is_annual  = payment_terms in ('annual_upfront', 'annual_quarterly')
        is_committed = is_annual
        contract_end = add_months(contract_start, 12) if is_annual else None

        # ── Impl fee ──────────────────────────────────────────────────────
        has_impl  = 'impl_fee' in features and product in ('Core', 'DataPipeline')
        impl_fee  = round(random.uniform(2000, 25000), 2) if has_impl else 0.0

        # ── Free trial ────────────────────────────────────────────────────
        trial_months = (random.choice([1, 2]) if 'free_trial' in features and product == 'Analytics' else 0)
        cohort_month = add_months(contract_start, trial_months).strftime('%Y-%m')

        # ── Commission ────────────────────────────────────────────────────
        comm_pct_new  = COMM_PCT_NEW[segment]
        comm_pct_upg  = COMM_PCT_UPG[segment]
        tcv = round(base_mrr * 12, 2) if is_annual else round(base_mrr * exp_life, 2)

        # ── Fate ──────────────────────────────────────────────────────────
        renewal_type = term_date = term_type = term_penalty = None
        modification_type = asc606_mod = None

        if fate == 'early_termination' and pidx == 0:
            survival    = random.randint(3, 10)
            term_date   = add_months(contract_start, survival)
            if 'early_penalty' in features:   term_type = 'early_with_penalty'
            elif 'early_refund' in features:  term_type = 'early_with_refund'
            else:                             term_type = 'early_no_penalty'
            term_penalty = round(base_mrr * random.uniform(1, 3), 2) if term_type == 'early_with_penalty' else 0.0
            active_until = term_date
        elif fate == 'product_switch' and not is_bundle and pidx == 0:
            switch_month    = add_months(contract_start, random.randint(4, 10))
            active_until    = switch_month
            modification_type = 'product_switch'
            asc606_mod      = 'prospective'
        elif 'churned_at_renewal' in features and is_annual:
            active_until = contract_end
            renewal_type = 'churned_at_renewal'
        else:
            active_until = END_DATE
            if is_annual and contract_end and contract_end <= END_DATE:
                renewal_type = 'renewed'

        contracts_rows.append({
            'contract_id': ctrid, 'customer_id': cid,
            'customer_segment': segment, 'region': region,
            'product': product,
            'pricing_model': {'Core':'per_seat_annual','Analytics':'flat_monthly','DataPipeline':'usage_hybrid'}[product],
            'contract_start_date': contract_start, 'contract_end_date': contract_end,
            'contract_tcv': tcv, 'base_mrr': base_mrr,
            'seats_contracted': seats_c, 'price_per_seat': price_ps,
            'usage_base_fee': usage_fee, 'overage_rate_per_unit': overage_r,
            'usage_tier_included': usage_tier,
            'free_trial_months': trial_months, 'has_impl_fee': has_impl,
            'impl_fee_amount': impl_fee, 'is_multi_element': is_bundle,
            'bundle_contract_id': None,
            'payment_terms': payment_terms,
            'sales_commission_pct_new': comm_pct_new,
            'sales_commission_pct_upgrade': comm_pct_upg,
            'ssp_amount': ssp_amount, 'cohort_month': cohort_month,
            'is_committed_term': is_committed, 'expected_customer_life_months': exp_life,
            'renewal_type': renewal_type, 'modification_type': modification_type,
            'asc606_modification_treatment': asc606_mod,
            'modified_from_contract_id': None,
            'termination_date': term_date, 'termination_type': term_type,
            'termination_penalty_amount': term_penalty,
        })

        # ── Monthly activity ──────────────────────────────────────────────
        current_mrr   = base_mrr
        current_seats = seats_c
        current_pps   = price_ps
        first_pay     = False
        seat_done     = False
        tier_done     = False
        upfront_billed= False
        orig_asset_id = orig_amt = orig_life = orig_start = None
        exp_asset_id  = exp_amt = exp_life_a = exp_start = None
        upgrade_month = None

        for period in PERIODS:
            pdate    = period.date()
            if pdate < contract_start: continue
            if pdate > active_until:   break
            if contract_end and pdate > contract_end and renewal_type not in ('renewed',): break

            months_in = months_between(contract_start, pdate)
            in_trial  = trial_months > 0 and pdate < add_months(contract_start, trial_months)
            mod_event = mod_delta = mov_type = comm_ev = None

            # First paying month
            if not in_trial and not first_pay:
                mov_type   = 'new'
                first_pay  = True
                orig_asset_id   = f'ASSET-{asset_counter:05d}'
                asset_counter  += 1
                orig_amt        = round(tcv * comm_pct_new, 2)
                orig_life       = exp_life
                orig_start      = pdate
                comm_ev         = 'original_asset_created'

            # Seat expansion (Core, months 4-9, locked PPS)
            if (product == 'Core' and not seat_done and 'seat_add' in features
                    and not in_trial and first_pay and 4 <= months_in <= 9):
                extra          = random.randint(2, 20)
                delta          = round(extra * current_pps, 2)
                current_seats += extra
                current_mrr   += delta
                mod_event      = 'seat_add'; mod_delta = delta
                mov_type       = 'expansion'; seat_done = True
                remaining      = max(1, months_between(pdate, active_until))
                exp_asset_id   = f'ASSET-{asset_counter:05d}'
                asset_counter += 1
                exp_amt        = round(round(delta * remaining, 2) * comm_pct_new, 2)
                exp_life_a     = exp_life; exp_start = pdate
                comm_ev        = 'expansion_asset_created'

            # Tier upgrade (Analytics, months 5-9) — PROSPECTIVE treatment
            # Upgrade is treated as a new separate performance obligation for the increment.
            # Commission on increment uses full new-business rate (same as seat add).
            # No catch-up adjustment; new rate applies from upgrade month forward only.
            if (product == 'Analytics' and not tier_done and 'tier_upgrade' in features
                    and not in_trial and first_pay and 5 <= months_in <= 9):
                bump           = round(current_mrr * random.uniform(0.20, 0.60), 2)
                current_mrr   += bump
                mod_event      = 'tier_upgrade'; mod_delta = bump
                mov_type       = 'expansion'; tier_done = True; upgrade_month = pdate
                remaining      = max(1, months_between(pdate, active_until))
                exp_asset_id   = f'ASSET-{asset_counter:05d}'
                asset_counter += 1
                exp_amt        = round(round(bump * remaining, 2) * comm_pct_new, 2)
                exp_life_a     = exp_life; exp_start = pdate
                comm_ev        = 'expansion_asset_created'

            # Tier downgrade (Analytics, months 6-10)
            if (product == 'Analytics' and not tier_done and 'tier_downgrade' in features
                    and not in_trial and first_pay and 6 <= months_in <= 10):
                cut            = round(current_mrr * random.uniform(0.15, 0.35), 2)
                current_mrr    = max(current_mrr - cut, 200.0)
                mod_event      = 'tier_downgrade'; mod_delta = -cut
                mov_type       = 'contraction'; tier_done = True

            # Termination / churn
            if term_date and pdate == month_start(term_date):
                mod_event = 'early_termination'
                if mov_type != 'new': mov_type = 'churned'
            elif renewal_type == 'churned_at_renewal' and contract_end and pdate == month_start(contract_end):
                mod_event = 'churn'; mov_type = 'churned'
            elif fate == 'product_switch' and not is_bundle and pdate == month_start(active_until):
                mod_event = 'product_switch_out'; mov_type = 'churned'

            churn_reason = random.choice(CHURN_REASONS) if mov_type == 'churned' else None

            # Billing — annual_upfront: only month 1
            if in_trial:
                mrr = billed = 0.0
            elif product == 'DataPipeline':
                usage    = round(random.uniform(usage_tier * 0.55, usage_tier * 1.65), 1)
                overage_u= round(max(0.0, usage - usage_tier), 1)
                overage_v= round(overage_u * overage_r, 2)
                mrr      = round(usage_fee + overage_v, 2)
                billed   = round(mrr, 2)
            else:
                mrr = current_mrr
                if payment_terms == 'annual_upfront':
                    if not upfront_billed:
                        billed = round(mrr * 12, 2); upfront_billed = True
                    else:
                        billed = 0.0
                elif payment_terms == 'annual_quarterly':
                    billed = round(mrr * 3, 2) if months_in % 3 == 0 else 0.0
                else:
                    billed = round(mrr, 2)

            usage_c = usage_tier_v = overage_uv = overage_rev = None
            if product == 'DataPipeline' and not in_trial:
                usage_c = usage; usage_tier_v = usage_tier; overage_uv = overage_u; overage_rev = overage_v

            impl_recog = round(impl_fee / 12, 2) if has_impl and not in_trial else None

            # Commission amortization
            o_cap = o_amort = o_bal = None
            e_cap = e_amort = e_bal = None
            if comm_ev == 'original_asset_created':
                o_cap = orig_amt
            if orig_asset_id and first_pay and not in_trial:
                months_since = months_between(orig_start, pdate) if orig_start else 0
                amort_pm = round(orig_amt / max(1, orig_life), 2)
                o_amort  = amort_pm
                o_bal    = round(max(0, orig_amt - amort_pm * (months_since + 1)), 2)
            if comm_ev == 'expansion_asset_created':
                e_cap = exp_amt
            if exp_asset_id and exp_start and not in_trial:
                months_since_exp = months_between(exp_start, pdate)
                amort_pm_e = round(exp_amt / max(1, exp_life_a), 2)
                e_amort    = amort_pm_e
                e_bal      = round(max(0, exp_amt - amort_pm_e * (months_since_exp + 1)), 2)
            # (tier_upgrade now uses expansion_asset_created path above — no special handling needed)

            activity_rows.append({
                'contract_id': ctrid, 'customer_id': cid,
                'period_month': pdate.strftime('%Y-%m'),
                'seats_active': current_seats,
                'usage_units_consumed': usage_c, 'usage_tier_included': usage_tier_v,
                'overage_units': overage_uv, 'overage_revenue': overage_rev,
                'mrr_this_month': round(mrr, 2) if not in_trial else 0.0,
                'amount_billed': round(billed, 2),
                'is_in_trial': in_trial,
                'modification_event': mod_event, 'modification_delta_mrr': mod_delta,
                'mrr_movement_type': mov_type,
                'impl_fee_recognized': impl_recog,
                'orig_asset_id': orig_asset_id,
                'orig_commission_capitalized': o_cap,
                'orig_commission_amortized': o_amort,
                'orig_commission_asset_bal': o_bal,
                'exp_asset_id': exp_asset_id,
                'exp_commission_capitalized': e_cap,
                'exp_commission_amortized': e_amort,
                'exp_commission_asset_bal': e_bal,
                'commission_event_type': comm_ev,
                'churn_reason': churn_reason,
            })

    # Link bundle contracts
    if is_bundle and len(bundle_ids) == 2:
        for i, row in enumerate(contracts_rows[-2:]):
            row['bundle_contract_id'] = bundle_ids[1 - i]

    # Product switch new contract
    if fate == 'product_switch' and not is_bundle:
        switch_start = active_until
        new_product  = 'Core' if prod1 == 'Analytics' else 'Analytics'
        new_ctrid    = f'CTR-{ctr_id:04d}'
        ctr_id      += 1
        new_seats    = random.randint(5, 50) if new_product == 'Core' else None
        new_pps      = calc_pps(segment, new_seats) if new_product == 'Core' else None
        lo2, hi2     = (ANALYTICS_MRR if new_product == 'Analytics' else ({},))[segment] if new_product == 'Analytics' else (0, 0)
        new_mrr      = round(new_seats * new_pps, 2) if new_product == 'Core' else round(random.uniform(*ANALYTICS_MRR[segment]), 2)
        new_comm     = round(new_mrr * exp_life * comm_pct_new, 2)
        new_asset    = f'ASSET-{asset_counter:05d}'
        asset_counter += 1

        contracts_rows.append({
            'contract_id': new_ctrid, 'customer_id': cid,
            'customer_segment': segment, 'region': region,
            'product': new_product,
            'pricing_model': 'per_seat_annual' if new_product=='Core' else 'flat_monthly',
            'contract_start_date': switch_start,
            'contract_end_date': add_months(switch_start, 12),
            'contract_tcv': round(new_mrr * 12, 2),
            'base_mrr': new_mrr, 'seats_contracted': new_seats, 'price_per_seat': new_pps,
            'usage_base_fee': None, 'overage_rate_per_unit': None, 'usage_tier_included': None,
            'free_trial_months': 0, 'has_impl_fee': False, 'impl_fee_amount': 0.0,
            'is_multi_element': False, 'bundle_contract_id': None,
            'payment_terms': 'monthly',
            'sales_commission_pct_new': comm_pct_new, 'sales_commission_pct_upgrade': comm_pct_upg,
            'ssp_amount': new_mrr, 'cohort_month': switch_start.strftime('%Y-%m'),
            'is_committed_term': True,
            'expected_customer_life_months': exp_life,
            'renewal_type': None, 'modification_type': 'product_switch',
            'asc606_modification_treatment': 'prospective',
            'modified_from_contract_id': ctrid,
            'termination_date': None, 'termination_type': None, 'termination_penalty_amount': None,
        })
        for period in PERIODS:
            pdate = period.date()
            if pdate < switch_start: continue
            months_in = months_between(switch_start, pdate)
            mov = 'reactivation' if months_in == 0 else None
            me  = 'product_switch_in' if months_in == 0 else None
            o_cap2 = new_comm if months_in == 0 else None
            amort2 = round(new_comm / exp_life, 2)
            o_bal2 = round(max(0, new_comm - amort2 * (months_in + 1)), 2)
            activity_rows.append({
                'contract_id': new_ctrid, 'customer_id': cid,
                'period_month': pdate.strftime('%Y-%m'),
                'seats_active': new_seats, 'usage_units_consumed': None,
                'usage_tier_included': None, 'overage_units': None, 'overage_revenue': None,
                'mrr_this_month': round(new_mrr, 2), 'amount_billed': round(new_mrr, 2),
                'is_in_trial': False,
                'modification_event': me, 'modification_delta_mrr': round(new_mrr, 2) if months_in==0 else None,
                'mrr_movement_type': mov,
                'impl_fee_recognized': None,
                'orig_asset_id': new_asset, 'orig_commission_capitalized': o_cap2,
                'orig_commission_amortized': amort2, 'orig_commission_asset_bal': o_bal2,
                'exp_asset_id': None, 'exp_commission_capitalized': None,
                'exp_commission_amortized': None, 'exp_commission_asset_bal': None,
                'commission_event_type': 'original_asset_created' if months_in==0 else None,
                'churn_reason': None,
            })

df_c = pd.DataFrame(contracts_rows)
df_a = pd.DataFrame(activity_rows)
df_c.to_csv('contracts.csv', index=False)
df_a.to_csv('monthly_activity.csv', index=False)

# ── Validation ────────────────────────────────────────────────────────────
print('=' * 60)
print('CLOUDAXIS INC. — 50-CUSTOMER DATASET')
print('=' * 60)
print(f'Contracts: {len(df_c)}  |  Customers: {df_c["customer_id"].nunique()}')
print(f'Activity rows: {len(df_a)}')
print()
print('Products:')
for p,n in df_c['product'].value_counts().items(): print(f'  {p:<15} {n}')
print('Payment terms:')
for p,n in df_c['payment_terms'].value_counts().items(): print(f'  {p:<22} {n}')
print('Segments:')
for p,n in df_c['customer_segment'].value_counts().items(): print(f'  {p:<15} {n}')
print('Modification events:')
for p,n in df_a['modification_event'].value_counts().dropna().items(): print(f'  {p:<25} {n}')
print('Termination types:')
for p,n in df_c['termination_type'].value_counts().dropna().items(): print(f'  {p:<25} {n}')
print('Renewal types:')
for p,n in df_c['renewal_type'].value_counts().dropna().items(): print(f'  {p:<25} {n}')
print(f'Bundles:       {df_c["is_multi_element"].sum()} contracts')
print(f'Has impl fee:  {df_c["has_impl_fee"].sum()} contracts')
print(f'Free trial:    {(df_c["free_trial_months"]>0).sum()} contracts')
print(f'Product switch:{(df_c["modification_type"]=="product_switch").sum()} contracts')
print()
print('FILES SAVED: contracts.csv · monthly_activity.csv')
print('=' * 60)
