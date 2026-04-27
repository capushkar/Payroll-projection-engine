# I Built a Full ASC 606 Reporting Stack With AI. Here's What That Really Took.

*By Pushkar Agrawal | Revenue Recognition · SaaS Finance · AI in Accounting*
*Part 1 of 2 — Quick read (~6 minutes) · Full methodology in Part 2*

---

## The Setup

I built a complete ASC 606 revenue recognition stack for a fictional SaaS company — 50 customers, 61 contracts, 948 monthly transactions — covering every edge case I could engineer: seat additions, tier upgrades, tier downgrades, early terminations, bundle contracts, implementation fees, usage-based overages, free trials, renewals, product switches.

Then I produced the full output you'd expect from a finance team: a validated recognition schedule, 8 SaaS metrics, a 9-tab Excel model, an interactive dashboard, and an 8-page disclosure package formatted as a 10-K financial statement footnote.

I used AI extensively throughout. And I want to be honest about what that actually meant — not the polished version, but the real version.

---

## What AI Is Good At — and What It Doesn't Know

AI has been trained on vast amounts of accounting literature, SEC filings, technical standards, and SaaS financial models. When you ask it to write an ASC 606 recognition engine or build a deferred revenue roll-forward, it draws on patterns from thousands of real examples. That's genuinely powerful.

But here's what AI doesn't know: *your* situation.

It doesn't know whether your company's auditors prefer a conservative or aggressive interpretation of the modification guidance. It doesn't know whether a 6% annual churn floor is reasonable for your customer segment or whether it should be 3% or 12%. It doesn't know if your company prices bundle contracts at a premium or a discount to standalone. It doesn't know your materiality threshold. It doesn't know your renewal history. It doesn't know how your sales team actually structures deals.

This gap — between what AI knows from global training data and what's correct for your specific case — is where most of the work actually lived.

---

## The Part Nobody Talks About: Validation

Here's what the timeline actually looked like on this project.

AI wrote code quickly. The recognition engine, the metrics layer, the Excel model, the dashboard — fast. But then the real work started.

The first LTV:CAC output showed ratios of 200–255x. AI didn't flag this as a problem. It was mathematically correct given the inputs. But it was wrong for *this* dataset — because it was using a spot monthly churn rate, and in a 50-customer model, most months have zero churn events, giving a near-zero rate and an astronomical LTV. Fixing this required understanding *why* the number was wrong, deciding that trailing 12-month average churn with a floor was the right methodology, and rebuilding the calculation. That diagnostic process took longer than the original build.

The deferred revenue roll-forward in the first disclosure draft showed "total billings" versus "total revenue recognised" as the two movement columns. Arithmetically, these don't tie — because monthly billing is recognised immediately and never touches the deferred balance. A real 10-K uses additions to deferred versus releases from deferred. AI didn't catch this. I did, after checking every quarter's arithmetic and tracing why none of them tied.

The commission roll-forward was missing a write-off line. When a contract terminates early, ASC 340-40-35-1 requires immediate expensing of the unamortised commission balance. The engine implemented this correctly — but the disclosure didn't show it as a separate movement, which meant the table didn't tie. Again: the tool built the right mechanism but didn't know the disclosure needed to reflect it.

There were also 12 logical validation checks I designed and ran against the recognition schedule: no negative balances, no simultaneous deferred revenue and contract asset, commission asset never increasing outside capitalisation events, zero catch-up adjustments on all modifications. Several of these failed on initial runs. Diagnosing each failure — distinguishing a real bug from a false positive in the check logic — required knowing what the output *should* look like, not just running the code.

**This is the part that took the most time, and the part AI cannot do for you.** AI runs the calculation. It doesn't know if the result is right for your organisation, your auditors, your industry, your contract structure.

---

## The Judgements That Still Required a Professional

Beyond validation, there were decisions that required accounting expertise — and that AI would have gotten wrong without direction:

**Modification treatment.** When a customer upgrades mid-contract, you choose between prospective treatment (new separate performance obligation for the increment) and cumulative catch-up (retroactive adjustment to reflect the new price from day one). Most SaaS companies use prospective. That's a policy decision with a material impact on revenue timing. I made it. AI executed it.

**Material right assessment.** Renewal options must be assessed under ASC 606-10-55-42 — do they give the customer a price advantage they wouldn't otherwise receive? If yes, they're a separate performance obligation. In this model, renewals are at market rates, so no material right. Getting this wrong would have created phantom deferred revenue across every renewal contract.

**RPO exclusions.** Month-to-month contracts, DataPipeline variable overages — both excluded from Remaining Performance Obligations. Different practical expedients apply to each. AI knows the standard exists. I decided which expedients apply to which contracts.

**Commission rate and amortisation life.** The model uses 10–15% commission on full contract value, amortised over expected customer life by segment (18/24/36 months). These numbers don't come from ASC 340-40 — they come from the business. AI doesn't know what your sales team gets paid or how long your customers actually stay.

---

## What This Means

AI compressed what would have been months of execution into days. That's real and significant. A Big 4 engagement on a project of this scope — dedicated manager, two seniors, staff associate, 8–12 weeks — costs more than most Series A SaaS companies can justify for an internal finance project.

One accounting professional with the right tools can now produce comparable output in a fraction of the time.

But the output is only as good as the professional governing it. AI that gets the modification treatment wrong will get it wrong 948 times, consistently, at scale. The floor of acceptable work has risen. The ceiling for what one person can produce has risen faster.

The skill that matters now isn't knowing how to write the code. It's knowing whether the output is right.

---

*Part 2 covers the full technical methodology: the recognition engine architecture, all 12 validation checks, specific bugs found and fixed, disclosure decisions, and an open invitation for peer review.*

*Full code and output files available on GitHub. [Link]*

*Pushkar Agrawal is an accounting professional with 6–7 years of experience in financial reporting, revenue recognition, and audit coordination.*
*Tools used: Python (pandas, reportlab, openpyxl), Claude (Anthropic), Excel*
