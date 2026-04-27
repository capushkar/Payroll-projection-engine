# CloudAxis Inc. — SaaS Revenue Intelligence Stack

**Author:** Pushkar Agrawal, CA · Finance Transformation Lead  
**Standard:** US GAAP · ASC 606 · ASC 340-40  
**Dataset:** Synthetic · 50 customers · 61 contracts · 24 months (Jan 2023 – Dec 2024)  
**Status:** Peer-reviewed · All validation checks passing

---

## What this is

A complete, production-grade ASC 606 revenue recognition and SaaS metrics stack — built entirely from first principles on a synthetic 50-customer dataset designed to cover every material edge case in a SaaS business.

The project demonstrates that one accounting professional with the right tools can produce output that previously required a dedicated team — and shows exactly where AI was used for execution and where professional judgement was required.

---

## What was built

| Deliverable | Description |
|---|---|
| Recognition engine | 8-step ASC 606 loop · 12 named validation checks · all passing |
| SaaS metrics | MRR waterfall · NRR/GRR · Cohort retention · LTV:CAC · Billings vs revenue |
| Excel model | 10-tab workbook · charts · colour-coded · revenue disaggregation |
| Interactive dashboard | 5-page HTML · all data embedded · no install needed |
| ASC 606 disclosure | 10-page PDF formatted as 10-K financial statement footnote |
| Data dictionary | Complete column reference for all 3 source files and 8 metric outputs |
| Pipeline diagram | 4-layer data flow: generation → engine → metrics → outputs |

---

## Run order

Each script reads from the previous step's output. Run in sequence:

```bash
# Step 1 — Generate the dataset
python 01_data_generation/generate_cloudaxis_50.py

# Step 2 — Run the recognition engine (reads contracts.csv + monthly_activity.csv)
python 02_recognition_engine/recognition_engine_fixed.py

# Step 3a — Compute metrics (reads all 3 source files)
python 03_metrics/phase3_metrics.py

# Step 3b — Build disclosure inputs (reads recognition_schedule.csv)
python 03_metrics/build_disclosure_inputs.py

# Step 4 — Build the PDF disclosure package
python 05_disclosure/build_disclosure_pdf.py

# Step 5 — Build the LinkedIn carousel
python 05_disclosure/build_carousel_v2.py
```

The Excel model (`04_outputs/`) and dashboard (`04_outputs/`) are pre-built from the final engine run. Open them directly in Excel / any browser.

---

## Folder structure

```
01_data_generation/
    generate_cloudaxis_50.py      Source: generates all data
    contracts.csv                 61 contracts · 34 columns
    monthly_activity.csv          948 rows · 25 columns

02_recognition_engine/
    recognition_engine_fixed.py   ASC 606 engine · 8-step loop
    recognition_schedule.csv      948 rows · 12 columns · engine output

03_metrics/
    phase3_metrics.py             Computes all 8 metric tables
    build_disclosure_inputs.py    Derives disclosure CSVs from engine output
    outputs/
        metrics_mrr_waterfall.csv
        metrics_nrr_grr.csv
        metrics_cohort_retention.csv
        metrics_ltv_cac.csv
        metrics_billings_vs_revenue.csv
        metrics_deferred_rollforward.csv
        metrics_rpo.csv
        metrics_commission_rollforward.csv
        note_2_disaggregation.csv
        note_3_deferred_rollforward.csv
        note_4_rpo.csv
        note_5_commission_rollforward.csv

04_outputs/
    CloudAxis_Revenue_Intelligence.xlsx   10-tab Excel model
    CloudAxis_Dashboard.html              Interactive dashboard (open in browser)
    CloudAxis_Pipeline_Flow.html          Data flow diagram
    CloudAxis_Data_Dictionary.docx        Full column reference

05_disclosure/
    build_disclosure_pdf.py        PDF builder script
    build_carousel_v2.py           LinkedIn carousel builder
    CloudAxis_ASC606_Disclosure.pdf    10-page 10-K footnote · final
    linkedin_carousel_v2.pdf           6-slide LinkedIn carousel · final

06_content/
    financeforge_part1.md          Blog post Part 1 (quick read, broad audience)
    financeforge_part2.md          Blog post Part 2 (methodology · peer review)
    linkedin_post1_final.txt       LinkedIn post for project launch
    linkedin_post2_final.txt       LinkedIn post (publish months later)
    linkedin_poster_v2.html        Static poster image (open in Chrome, screenshot)
```

---

## Dataset design

The 50-customer dataset was engineered to simultaneously cover every material edge case:

**Products:** Core (per-seat annual), Analytics (flat-rate), DataPipeline (usage-based + overage)  
**Payment terms:** Annual upfront, annual quarterly, monthly  
**Segments:** SMB (10% commission), Mid-Market (12%), Enterprise (15%)  
**Modifications:** Seat additions, tier upgrades, tier downgrades, product switches  
**Terminations:** Early with penalty, early with refund, early no penalty  
**Special features:** Bundle contracts (SSP allocation), implementation fees (not distinct), free trials, renewals, churned-at-renewal

---

## Key accounting policy decisions

All modifications are **prospective** (ASC 606-10-25-12). Upgrades and downgrades update MRR from the modification date forward — no cumulative catch-up.

Implementation fees are **not distinct** (ASC 606-10-25-19, both prongs). Combined with the subscription and recognised ratably over the contract term.

Renewal options are **not material rights** (ASC 606-10-55-42). Renewals are priced at prevailing market rates with no contractual discount.

DataPipeline variable overages are **excluded from RPO** per the right-to-invoice practical expedient (ASC 606-10-50-14).

Month-to-month contracts are **excluded from RPO**. No enforceable right to future payment.

Commission assets are **written off immediately** on contract termination, churn, or product switch (ASC 340-40-35-1). The engine explicitly zeroes balances in the exit period.

Churn contract assets are **reversed in the exit period**. Unbilled receivables are uncollectable when the customer does not renew; revenue is reversed up to the current period amount.

---

## Validation

The recognition engine runs 12 named validation checks on every execution:

| # | Check | Standard |
|---|---|---|
| 01 | No negative revenue rows | ASC 606 para 56 |
| 02 | No negative deferred revenue | Contract liability ≥ 0 |
| 03 | No negative contract asset | Asset ≥ 0 |
| 04 | Deferred + CA never both positive (per contract) | Mutually exclusive |
| 05 | Commission asset never increases outside capitalisation | ASC 340-40-35-1 |
| 06 | No catch-up adjustments (all modifications prospective) | ASC 606-10-25-12 |
| 07 | Trial period revenue = zero | ASC 606-10-55-42 |
| 08 | Terminated contracts: zero residual balances | ASC 606 exit accounting |
| 09 | Churn contracts: zero residual contract asset | S11 — uncollectable CA |
| 10 | Product switch contracts: zero residual balances | Switch derecognition |
| 11 | Bundle SSP allocation within $1 tolerance | ASC 606-10-32-31 |
| 12 | Deferred roll-forward ties (all 8 quarters) | C1 — balance movement |

**All 12 pass on the current engine and dataset.**

---

## Disclosure package highlights

The 10-page PDF (`05_disclosure/CloudAxis_ASC606_Disclosure.pdf`) is formatted as a 10-K financial statement footnote and covers:

- **Note 1:** Revenue recognition policy — five-step model, all three products, modification treatment, implementation fees (two-prong distinctness), material rights assessment, practical expedients
- **Note 2:** Revenue disaggregation — 4 dimensions (product, segment, billing arrangement, geography) · FY 2024 $2,317,039 · FY 2023 $1,225,893
- **Note 3:** Deferred revenue roll-forward (balance-movement format — all 8 quarters tie)
- **Note 3B:** Contract asset roll-forward (all 8 quarters tie)
- **Note 4:** Remaining performance obligations — $447,719 at Dec 31 2024 · 100% within 12 months
- **Note 5:** Commission asset roll-forward — ASC 340-40 · write-offs disclosed · honest rounding footnote
- **Note 6:** Key accounting assumptions — every judgement cited to ASC paragraph

---

## What AI did / what required professional judgement

**AI executed:** Python recognition engine, Excel model, HTML dashboard, PDF disclosure, this README.

**Professional judgement required for every one of these:**
- Whether tier upgrades and downgrades use prospective or cumulative catch-up treatment
- Whether renewal options constitute material rights under ASC 606-10-55-42
- Which contracts belong in RPO and which practical expedients apply
- The churn rate methodology for LTV (spot rate gives 200× — completely misleading)
- Whether the contract asset on churned contracts should reverse revenue or go to bad debt
- Diagnosing and fixing 4 engine bugs that AI did not flag

An AI that gets the modification treatment wrong will get it wrong 948 times. Consistently. Without flagging it. The validation log in `06_content/financeforge_part2.md` documents every bug found and fixed.

---

## Dependencies

```bash
pip install pandas numpy openpyxl reportlab pypdf
```

Python 3.10+. No other dependencies.

---

## Peer review

This project has been through two rounds of independent technical review. All critical and significant findings have been addressed. The full validation log and open peer review invitation are in `06_content/financeforge_part2.md`.

Specific questions for peer reviewers:
1. Is the prospective treatment for all modification types (including annual upfront downgrades) the right policy choice?
2. Is a 6% annual churn floor defensible for the LTV calculation, and how would you establish it for different company profiles?
3. Does the RPO disclosure meet the spirit of ASC 606-10-50-13 through 50-16?
4. Is the commission rate on full TCV (rather than first-year ACV) consistent with your firm's practice?

---

*Pushkar Agrawal · CA · Finance Transformation Lead · financeforge.com*
