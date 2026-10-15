# Model risk and validation record

## Supported use and model basis

This software compares conditional cash/profit outcomes for a fictional lender
retaining a fixed 12-month product. It is a deterministic expected-value model,
not a borrower classifier or an empirical default forecast. Its base data,
pricing, probabilities, recoveries, costs and policy limits are illustrative.
No historical fitting, calibration, held-out backtest or causal policy study
has been performed. The existing [source-fitness decision](source-fitness.md)
remains contextual only.

The seeded generator fixes a fictional application population. Each call owns
its `random.Random` instance; scenario changes reweight those same rows without
sampling default paths. Threads and caller Decimal state do not change a
scenario's results. Growth changes vintage weights and may change aggregate
weighted band proportions; band labels, supplied PDs and prices stay fixed.

## Quantitative invariants

Base and effective lifetime PD lie in [0, 1]. Recovery lies in [0, 1], giving
LGD = 1 - recovery. Performing exposure is nonnegative. At a payment month,
conditional hazard times opening performing exposure gives expected gross
charge-off. Ultimate expected loss associated with those defaults is
`EAD * hazard * LGD`. Receipt of recovery cash is delayed; the model's calendar
month net credit expense is charge-offs less recoveries received that month,
so it need not equal ultimate loss assigned to the same default month.

Survivor weighting and amortization determine lifetime exposure. Initial
principal times lifetime PD times LGD is not the portfolio loss formula for
an amortizing loan. With zero recovery lag the per-month EL identity is checked
directly. With a lag, full runoff must receive the recovery fraction of total
gross charge-offs. Loan, debt, cash, cohort and simplified equity identities
must reconcile and all loans/debt run off. No source field is a claim of
GAAP/CECL allowance measurement.

Inputs have finite domains and runtime validation. Zero rates/probabilities
have explicit branches; invalid probabilities, exposures and helper terms
fail before arithmetic. Guard precision prevents tiny positive rates/PDs from
vanishing in subtraction. Fresh 96-digit contexts and traps isolate rounding
and failures; cancellation work is capped at 4,096 digits. Count roundoff has
count units and cannot admit funding against zero applications or produce an
approval ratio above one. Cash/loss policy comparisons use unrounded values.

## Verification evidence and limits

The original 144 tests passed before the audit. Added regressions reproduced
30 domain/precision/intake failures, five report/context failures, two invalid
count-denominator acceptances and one approval-bound failure. Their repaired
paths are covered by 49 new tests, including 48 fixed-seed generated portfolios,
independent numerical references, financial identities and threaded execution.
The numerical implementation checkpoint has 193 passing unit/AppTest/HTTP
cases in CI. A subsequent installed-wheel regression adds packaging coverage;
the full follow-up passes 194 tests locally. No follow-up CI run was queued,
so the earlier CI/browser passes do not verify the packaging repair. The
[audit ledger](AUDIT_2026-10-15.md) records exact commands, revisions and evidence.

These tests establish supported implementation behavior. They do not establish
PD/recovery accuracy, sensitivity to real population shifts, actual liquidity,
forecast confidence bands or economic profitability. No Monte Carlo paths or
correlation matrices exist in this implementation; sampling errors, VaR and
expected shortfall are not outputs. Adding such methods would be a separate
model specification, rather than an inferred repair to this deterministic model.

## Governance crosswalk

The requested SR 11-7 framework is treated as a historical development/validation/
governance crosswalk. The agencies' April 17, 2026
[SR 26-2 letter](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm)
supersedes SR 11-7; this primary page was checked October 15, 2026. It describes
a risk-based approach tailored to the institution. This repository does not
claim supervisory approval or determine an institution's legal obligations.

| Area | Present evidence | Required institutional decision |
| --- | --- | --- |
| Development and implementation | Source equations, explicit timing, exact inputs, pinned dependencies, numerical budgets and deterministic tests | Approve intended use, material assumptions, limits and change control |
| Independent validation | Synthetic reference/property regressions; no independent empirical validation | Obtain appropriate data/rights and qualified independent challenge before actual lending use |
| Governance and monitoring | Versioned source/data/inputs, run identity, retained exports and explicit failures | Assign owners, approvals, monitoring, overrides, incident response and retirement/revalidation triggers |

Model version 0.1.1 changes numerical semantics and run IDs. Old exports are not
rewritten; exact old-run reproduction requires the old release. Current CLI
runs evaluate supplied inputs with the current model version and dependencies.
Retain source revision, dependency constraints and inputs with any institutional
review. The full strict-typing release gate remains open under the user's
[new-dependency approval condition](DEVELOPMENT_TOOLING_APPROVAL.md).
