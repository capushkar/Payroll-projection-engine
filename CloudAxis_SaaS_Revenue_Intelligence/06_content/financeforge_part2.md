# ASC 606 Revenue Recognition at Scale With AI: Full Methodology, Validation Log, and Open Peer Review

*By Pushkar Agrawal | Revenue Recognition · SaaS Finance · AI in Accounting*
*Part 2 of 2 — Deep methodology (~25 minutes) · Quick summary in Part 1*

---

## Purpose of This Document

This piece serves two audiences.

The first is the accounting professional who read Part 1 and wants to understand whether the methodology is actually sound — the decisions made, the bugs found, the checks passed, the places where the output required correction. Think of it as an open working paper, written in the spirit of peer review.

The second is anyone thinking about how AI tools can be responsibly applied to complex professional work in accounting and finance, specifically in the context of organisations — small and mid-sized businesses — that cannot access the level of expertise that large enterprises take for granted. If a Controller at a 40-person SaaS company can produce disclosure-quality ASC 606 reporting independently using these tools, that has real implications for how financial reporting quality distributes across the economy.

This document is written with both in mind. Comments and challenges are welcome.

---

## The Dataset: Design Principles

The fictional company is CloudAxis Inc. — a B2B SaaS business with three products:

- **Core**: per-seat subscription, annual contracts
- **Analytics**: flat-rate subscription, annual or monthly
- **DataPipeline**: usage-based (base fee plus overage), committed annual term but monthly billing

The 50-customer dataset was engineered to simultaneously cover every material edge case under ASC 606. This was intentional. A dataset of routine contracts would be easy to validate but would not test the recognition engine under stress. The design principles were:

**Complete scenario coverage.** Every modification type in a single dataset: seat additions (prospective — distinct new seats), tier upgrades (prospective — new PO for the increment), tier downgrades (prospective — reduced rate forward), product switches (old contract derecognised, new contract initiated), early terminations with penalty, with refund, and without penalty. Every payment structure: annual upfront, annual quarterly, monthly. Every special feature: implementation fees (not distinct, ratable), free trials (no revenue, no commission amortisation), bundle contracts (SSP allocation), renewals, churned-at-renewal.

**Deliberate stress on the accounting identity.** Having annual upfront contracts alongside usage-based monthly contracts in the same dataset means the recognition engine must handle both cases without a generalised billing guard — the rule "after month 1, bill = 0" that applies to Core and Analytics must explicitly exclude DataPipeline, whose billing reflects actual monthly usage. This was a real bug in the first version.

**Sufficient volume for pattern validation.** 948 monthly activity rows across 61 contracts (50 customers; bundle customers each contribute two contracts — one per product line — plus one product-switch pair; solo customers contribute one each) provides enough volume to detect systematic errors versus one-off anomalies.

---

## The Recognition Engine: Architecture

The engine (`recognition_engine_fixed.py`) runs an 8-step calculation loop for each contract for each month in the 24-month window. The steps are:

**Step 1 — Trial period guard.** If the contract month falls within the free trial window (calculated from contract start plus trial months), revenue recognition is zero. Commission amortisation also pauses during trial.

**Step 2 — Commission asset creation.** On the first paying month, the original commission asset is capitalised (commission rate × TCV × amortisation period factor). On expansion events (seat additions, tier upgrades), an incremental expansion asset is created using the same commission rate applied to the incremental TCV for the remaining committed term.

**Step 3 — Modification treatment.** All modifications — upgrades, downgrades, seat additions — are treated prospectively. The current MRR is updated to reflect the modification. No cumulative catch-up is computed. This is a deliberate policy decision (documented below) not a default.

**Step 4 — Revenue recognition.** For Core and Analytics: ratable recognition at the allocated monthly rate. For DataPipeline: base fee plus actual overage, multiplied by the SSP allocation ratio for bundle contracts. For implementation fees: monthly amount (total fee / contract term months) included in the recognition figure and contributing to contract asset when billed separately.

**Step 5 — Termination flush.** On the termination month, all balances — deferred revenue, contract asset — are zeroed. The treatment depends on termination type: penalty contracts recognise the penalty as additional revenue; refund contracts recognise a credit against revenue; no-penalty contracts flush the remaining deferred to current-period revenue (service no longer owed).

**Note on mutual exclusivity.** The validation check (check [04] in the engine) confirms that deferred revenue and contract asset are never simultaneously positive *at the individual contract level per period* — which is the requirement under ASC 606. At the entity level, both balances appearing positive simultaneously is normal and expected: different contracts sit in different billing positions at any given month-end. The `Billings vs Revenue` Excel tab shows both entity-level balances positive in 19 of 24 months — this is correct, not a violation.

**Step 6 — Deferred revenue and contract asset calculation.** The net position formula: `deferred = max(0, cumulative_allocated_billed - cumulative_recognised)`. `contract_asset = max(0, cumulative_recognised - cumulative_allocated_billed)`. The mutual exclusivity constraint (both cannot be positive simultaneously) is enforced in the calculation.

**Step 7 — RPO calculation.** `RPO = current_MRR × months_remaining`. Exclusions: month-to-month contracts (no enforceable right to future payment), DataPipeline variable overages (ASC 606-10-50-14 practical expedient), contracts in churn or termination status. Renewal months are added to the term for renewed contracts.

**Step 8 — Commission amortisation.** Original asset: amortised straight-line over expected customer life from capitalisation date. Expansion asset: amortised over remaining expected life from expansion date. On early termination: full remaining balance written off to expense (ASC 340-40-35-1).

---

## Policy Decisions: What Was Decided and Why

These are accounting judgements — choices between permissible alternatives — that required deliberate decision-making. AI executed each after the decision was made. None of these were defaults.

### Modification treatment: always prospective

ASC 606-10-25-12 permits prospective treatment when a modification adds goods or services that are distinct and priced at standalone selling price. ASC 606-10-25-13 requires cumulative catch-up when the modification changes the transaction price for already-delivered goods.

For tier upgrades, the initial build used cumulative catch-up for annual upfront contracts (where cash was already received at the lower rate) and prospective for monthly contracts. This was later changed to always prospective for both upgrades and downgrades across all contract types.

**Rationale:** Most SaaS companies treat upgrades as new separate performance obligations for the increment. The prospective approach is cleaner operationally and more consistent with how the commercial transaction actually works — the customer is buying additional capability from a specific date, not repricing their prior access. Importantly, being consistent across contract types avoids the complexity of bifurcating modification treatment based on payment structure.

**Impact:** Removing cumulative catch-up reduced total recognised revenue by approximately $300K over the 24-month window compared to the mixed approach. This is the correct direction — the earlier treatment was inflating revenue by pulling forward catch-up adjustments.

### Renewal options: not a material right

Under ASC 606-10-55-42, a customer option to renew at a discounted price represents a material right — a separate performance obligation that requires allocation of transaction price to the option. If the renewal option provides a price or terms the customer wouldn't otherwise receive, it must be deferred.

In this model, all renewals are priced at prevailing market rates — the same price offered to new customers at renewal time. No discount, no locked-in pricing advantage.

**Decision:** Renewal options are not material rights. No separate performance obligation. No allocation at contract inception. Renewal-period revenue recognised only after the renewal contract is executed.

**What this means for RPO:** Renewal contracts in progress at the reporting date are not included in RPO until signed. This is consistent with most SaaS companies' disclosure practice.

### LTV churn methodology: trailing 12-month with 6% floor

The first version used spot monthly churn rate. In a 50-customer model where terminations are lumpy (1–2 per quarter), most months have a zero churn rate. A zero monthly churn rate makes the LTV formula (gross profit / monthly churn) mathematically infinite, before hitting whatever floor is applied.

**Decision:** Use trailing 12-month MRR-weighted churn rate. Apply a 6% annual floor (0.5% monthly) as a minimum. Cap LTV at 5 years of gross profit as a conservative analytical convention. Long-horizon LTV calculations are sensitive to assumed retention; capping at 5 years prevents compounding optimistic assumptions about customer behaviour that are not supported by observed data. This is independent of the ASC 340-40 amortisation period for capitalised commissions, which is governed separately by expected customer life as disclosed in Note 5.

**Result:** Average LTV:CAC shifted from 200–255× (spot rate) to 12× median (trailing with floor and cap). By segment — SMB: 29× average (27× median) / 3-month payback; Mid-Market: 12× average (9× median) / 7 months; Enterprise: 14× average (8× median) / 10 months. Wide variance within each segment reflects small sample sizes (11–12 observations per segment) — a few outlier quarters drive the mean above the median in all three.

**Note for reviewers:** The 6% annual floor is a judgement call. For a company with historically lower churn (Enterprise-heavy, sticky product), 3–4% might be more appropriate. For SMB-heavy with high early churn, 8–10% might be correct. This number should come from actual customer data, not a model assumption.

One important limitation to disclose: in this synthetic 50-customer dataset, 28 of 35 segment-period LTV observations (80%) sit exactly at the 0.5% monthly floor. This means the published LTV outputs primarily reflect the floor assumption rather than observed customer behaviour. A larger dataset — or a real company with hundreds of customers and steady churn — would activate the floor less frequently and produce LTV figures more responsive to actual data. Readers should weight the LTV outputs accordingly.

### Commission rate: full TCV at signing

The model capitalises commissions on the full contract value at signing. Rates: SMB 10%, Mid-Market 12%, Enterprise 15%. Expansion commissions use the same rates on the incremental committed value.

**Note:** Many SaaS companies pay commissions on first-year ACV only, not full TCV. If that were the policy here, capitalised amounts would be ~50% lower and the commission asset closing balance would be approximately $100K rather than $207K. The disclosure documents the actual policy assumption in Note 6. Any reviewer applying this model to a real company should adjust this assumption to match actual compensation policy.

---

## Validation Log: Bugs Found and Fixed

This section documents every material error identified during validation, the root cause, and the fix applied. This is the honest record.

### Bug 1: Annual upfront billing guard applied to DataPipeline

**Symptom:** DataPipeline contracts with annual upfront payment terms showed a growing contract asset over time, even though they were billed monthly.

**Root cause:** The annual upfront billing guard — which correctly zeroes out months 2–12 billing for Core and Analytics (which bill everything in month 1) — was applied unconditionally to all contracts with annual upfront payment terms. DataPipeline, whose payment terms describe the commitment structure rather than billing cadence, should always bill monthly based on actual usage.

**Fix:** Added a product check (`product != 'DataPipeline'`) to the billing guard. DataPipeline monthly billing now passes through correctly.

**Impact:** Two contracts affected. Contract asset reduced from $47K to $3K on the affected contracts (the remaining $3K is legitimate — implementation fee earned but not yet invoiced).

### Bug 2: Commission asset increasing on tier upgrades (initial version)

**Symptom:** The validation check "commission asset never increases between periods outside of capitalisation events" was flagging failures.

**Root cause:** The initial upgrade treatment used a not-commensurate modification approach, which recalculated the original asset's remaining life and amortisation rate at the upgrade date. The snapshot logic had an error: `remaining_life = exp_life + 6` (adding 6 months) rather than `exp_life - elapsed_months`. This caused the per-period amortisation to drop, allowing the balance to grow temporarily.

**Fix:** Changed upgrade treatment to fully prospective. Original asset unaffected. New expansion asset created for the increment. No life adjustment, no snapshot. Validation check now passes for all 61 contracts.

### Bug 3: Deferred roll-forward format wrong

**Symptom:** The Note 3 quarterly roll-forward table showed Opening + Billings − Revenue = Closing. None of the 8 quarters tied.

**Root cause:** "Total billings" includes monthly billing that is recognised in the same period — it never creates deferred revenue. Monthly billing flows directly into revenue without touching the liability. The correct roll-forward shows additions to deferred (net increase in balance from advance billing) versus releases from deferred (prior balance recognised). These are balance-sheet movements, not income statement flows.

**Fix:** Recomputed additions and releases from period-over-period balance changes at the contract level. `addition = max(0, deferred[t] − deferred[t−1])`. `release = max(0, deferred[t−1] − deferred[t])`. All 8 quarters now tie to the penny.

**What this means:** This is a common mistake in deferred revenue disclosures. The gross billings vs revenue presentation *looks* right but only ties if 100% of billing goes to deferred — which is only true for pure advance-billing businesses. Most SaaS companies have a mix.

### Bug 4: Commission roll-forward missing write-off line

**Symptom:** Opening + Capitalised − Amortised ≠ Closing for several quarters.

**Root cause:** Early terminations require immediate write-off of the unamortised commission balance (ASC 340-40-35-1). The engine implemented this correctly — balances were zeroed on termination. But the disclosure showed only capitalisation and amortisation, omitting write-offs as a separate movement. The arithmetic didn't tie for quarters with terminations.

**Fix:** Added a write-off column. FY 2023: $13,001. FY 2024: $46,853 (concentrated in Q1–Q3 as multiple contracts terminated or churned with outstanding commission balances). All 8 quarters now tie by construction (write-off is the reconciling item O + Cap − Amort − Close = WO) — disclosed as a footnote.

### S12. Cohort sizes and interpretation

The cohort heatmap displays percentage retention but not the number of customers in each cohort at M+0. With 50 customers distributed across 17 cohort months, individual cohorts contain 1–7 customers (median: 2). Single-customer events drive step-function changes — a 2-customer cohort losing one customer shows as 50% retention loss in a single month.

The Excel model and dashboard now display an "n" column alongside the heatmap, with cohorts of n<3 flagged in red and n<5 in amber. This allows readers to weight the retention signals appropriately.

> *"Cohort sizes in this synthetic dataset range from 1 to 7 customers, making cohort retention curves highly sensitive to single-customer events. In a production setting with cohorts of 50+ customers, retention curves are smoother and more reliable as a leading indicator of product health."*

### False positives: validation checks that were wrong

Three of the initial validation check failures turned out to be errors in the *check logic*, not the engine:

- **Annual upfront deferred drop ≠ MRR:** For contracts with implementation fees, the monthly deferred decrease equals recognised revenue (MRR + impl_fee/12), not just MRR. Check was too narrow.
- **Quarterly deferred oscillation failure:** For a bundle contract with implementation fee, the deferred balance after quarterly billing equals allocated_billed − monthly_recognition, not 2×monthly_revenue. Check was oversimplified.
- **Monthly contracts in RPO:** A product-switch-in contract with monthly billing terms but a committed end date correctly appears in RPO. Exclusion rule needed to be "monthly AND NOT committed_term", not "monthly".

Distinguishing real bugs from check logic errors requires knowing what the correct answer should be. This is the analytical work that validation actually involves.

---

## Where Professional Judgement Appeared Beyond Policy Decisions

Several outputs required evaluation that goes beyond knowing the accounting standard.

**Materiality of the $3,954 rounding adjustment.** Is this material? On a $207,428 commission asset, it's 1.9%. For a real company, materiality depends on quantitative thresholds (typically 5% of a relevant line item) but also qualitative factors. I disclosed it as a footnote rather than correcting via a forced adjustment, which is the right call for a model but would require more analysis in a real audit.

**The LTV:CAC results for Enterprise.** Even after applying trailing churn, Enterprise shows LTV:CAC ratios of 300× in periods with no churn events (floor-only churn). This looks unrealistic. The right response is not to hide it but to note in methodology that with 3–4 Enterprise customers, churn is inherently lumpy and the floor-based calculation will produce high ratios in no-churn quarters. A real analyst would complement this with cohort-based churn analysis using a longer lookback.

**The Q2 2023 deferred addition spike.** Additions to deferred spike to $435,738 in Q2 2023 because many annual upfront contracts were signed in that quarter. This reflects the dataset's loading pattern (not representative of an organic business ramp). A reviewer reading this without context would ask whether there was a one-time sales event. The correct disclosure includes a narrative explaining the pattern.

**Geography disaggregation.** The dataset has four regions: North America (58% of revenue), EMEA (20%), APAC (19%), LATAM (4%). ASC 606-10-50-5 requires disaggregation that depicts how revenue differs in nature, amount, timing, and uncertainty. Whether geography meets that test for this company is a judgement. It's included because it's a standard dimension for SaaS companies with international customers.

---

## Invitation for Peer Review

This project is intended as a working demonstration, not a finished product. If you are an accounting professional, a Big 4 technical reviewer, a CFO, or a Controller with ASC 606 experience, I would genuinely welcome challenges to any of the decisions documented here.

Specifically, I'm interested in feedback on:

1. Whether the prospective treatment for all modification types is the right policy choice, or whether there are scenarios in this dataset where cumulative catch-up would be more appropriate
2. Whether the commission rate on full TCV is reasonable as a portfolio assumption, and how you would adjust it for ACV-based compensation structures
3. Whether the 6% annual churn floor is defensible, and how you would establish a more principled floor for different company profiles
4. Whether the RPO disclosure meets the spirit of ASC 606-10-50-13 through 50-16, or whether additional disaggregation or explanation is needed

Comments on LinkedIn or via direct message. GitHub repository with full code will be linked below.

---

## Why This Matters for Smaller Organisations

The standard interpretation of ASC 606 compliance is that it requires a team — an internal technical accounting group, external auditors, possibly a Big 4 advisory engagement. That is the reality for public companies and larger private companies.

For a Series A SaaS company with 40 employees and a two-person finance team, that resource doesn't exist. The Controller is also the AP manager and the financial reporting lead. Revenue recognition is treated as a best-effort exercise rather than a rigorous one.

The demonstration here is that a single accounting professional, using AI as an execution tool and applying their own technical judgement for the decisions that matter, can produce output at a quality level that was previously inaccessible without a team. Not perfectly — the validation log above documents the errors found. But at a level that would support external audit, investor reporting, or board-level financial disclosure.

This is a meaningful change for how financial reporting quality distributes across the economy. The barrier has historically been access to specialised human capital, not the underlying accounting knowledge. AI lowers that barrier substantially while shifting the requirement from "can you build this" to "can you govern it."

---

*Pushkar Agrawal is an accounting professional with 6–7 years of experience in financial reporting, ASC 606 revenue recognition, and audit coordination. Currently Finance Lead at Resonant Energy LLC.*

*Tools: Python (pandas, reportlab, openpyxl), Claude (Anthropic), Excel*
*Full project files: GitHub [link]*
*Part 1 — Quick read: [link]*
