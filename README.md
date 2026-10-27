# Lending Profitability and Risk Simulator

[![Open the live Streamlit app](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://rishabb-lending-simulator.streamlit.app/)
[![Checks](https://github.com/rishabbshankar226/Lending-Profitability-Risk-Simulator/actions/workflows/checks.yml/badge.svg?branch=main)](https://github.com/rishabbshankar226/Lending-Profitability-Risk-Simulator/actions/workflows/checks.yml)

**[Open the live app: rishabb-lending-simulator.streamlit.app](https://rishabb-lending-simulator.streamlit.app/)**

The app is public and needs no sign-in or upload. The Streamlit Community Cloud
host sleeps when idle, so the first load can take several seconds. It opens on
the base case: Conservative, $48,133 full-runoff operating result, 0.84% net
principal loss and $147,450 lowest month-end cash. These match the
[policy table](#cli-and-input-contracts) below. On the hosted build, **More capital · $1.25m**
makes Balanced the recommendation ($294,468 operating result, $53,857 lowest
month-end cash); **Higher defaults · 2×** loads a stress case.

> **Which build is hosted.** On October 26, 2026 the live app was still serving
> the earlier `feature/lending-simulator` build, not `main`. Its Conservative
> base run is `5a88f7bef3fa93d4`; `main` produces `438a13c9e03c52a9`, and run IDs
> include the model version. The displayed base-case figures match, but the
> interface differs (the hosted *Strategy comparison* tab is *Policies* on
> `main`). Moving the host to `main` is a separate release action; see the
> [hosted deployment notes](docs/deployment.md).

**Start here:** [Two-minute reviewer guide](docs/reviewer-guide.md) ·
[Business memo](docs/business-memo.md) ·
[90-second captioned tour](docs/tour/README.md) (earlier hosted build)

![Finance workbench overview on main](docs/screenshots/workbench/desktop-1440-overview.png)

*The finance workbench on `main`, captured in Chromium at workbench revision
`ba68ea3`, before the model 0.1.1 numerical audit. The headline figures are unchanged.*

A deterministic expected-value model for a lender retaining 12-month installment
loans. It compares three approval policies under credit-loss, collateral,
facility and month-end cash constraints. Python calculates the financial results;
a Streamlit workspace reviews applied scenarios, stress cases and exports.

The application uses 10,000 fictional applications and illustrative risk/cost
assumptions. It has no borrower scoring or historical calibration. Results are
conditional projections, not evidence of actual lender performance.

## What the app does

- **Overview, Policies, Cohorts, Funding & stress, Methodology:** five views over
  one applied scenario, with profit, cash and loss margins first. Edits stay
  draft until an explicit **Run scenario**; invalid input keeps the last valid result.
- **Policy comparison:** Conservative, Balanced and Aggressive are ranked by
  full-runoff operating profit among policies that meet the loss cap and cash
  floor. A pinned baseline shows deltas against a later run.
- **Stress and capital cases:** one-click examples, a 20-case default/funding
  grid, cohort cutoffs and exact capital-gap figures.
- **Exports:** CSV package with manifest, audit workbook and Markdown decision
  brief, each generated only when requested; the same runs reproduce through the CLI.

## Current state

`main` at `2d7ddbb` (October 16, 2026) is model version `0.1.1`. It includes the
finance-workbench interface ([PR #4](https://github.com/rishabbshankar226/Lending-Profitability-Risk-Simulator/pull/4))
and the numerical, input-boundary and installed-package audit
([PR #6](https://github.com/rishabbshankar226/Lending-Profitability-Risk-Simulator/pull/6)).
[CI run 38916063015](https://github.com/rishabbshankar226/Lending-Profitability-Risk-Simulator/actions/runs/38916063015)
passed on that commit: dependency consistency, Ruff, strict mypy, 200 tests,
compilation and the base-case CLI export, then real-Chromium checks (10 acceptance,
2 export-resilience and 3 accessibility/zoom journeys, plus 2 reference captures).
The [audit ledger](docs/AUDIT_2026-10-15.md) records revision-specific results and
the [approved development-tooling record](docs/DEVELOPMENT_TOOLING_APPROVAL.md).
The hosted app has not been switched to this revision.

## Architecture

| Module | Responsibility |
| --- | --- |
| `data.py`, `data/` | Validated immutable synthetic demand, isolated seeded generation and content identity |
| `analytics.py`, `queries/` | Private SQLite aggregation of integer cents and demand-weighted cohorts |
| `numeric.py` | Fresh Decimal contexts, finite arithmetic traps and cancellation precision budgets |
| `types.py`, `model.py` | Assumptions, cohort repayment/default/recovery schedules, funding, cash and reconciliations |
| `decisions.py` | Eligibility, exact profit ranking, tie resolution and deterministic stress cases |
| `json_input.py`, `cli.py` | Bounded exact configuration intake and reproducible local scenario exports |
| `presentation.py`, `exports.py` | Report adapters, exact CSV packages and workbook snapshots/benchmarks |
| `ui/`, `app.py` | Draft/apply state, isolated visitor sessions, charts and deferred exports |
| `typings/` | Source-checked declarations for consumed XlsxWriter APIs and documented dynamic boundaries |

The synthetic generator uses a fresh `random.Random(seed)` instance. Changing
scenarios does not resample outcomes or mutate global random state. This model
has no Monte Carlo paths, correlation matrices, VaR or expected-shortfall
estimator. Monte Carlo standard errors and confidence intervals are therefore
not quantities produced by this deterministic engine. Uncertainty in its
illustrative PD/recovery assumptions requires empirical evidence that is absent.

## Financial methodology

Originations occur at month-end, followed by 12 scheduled payment months.
Defaults occur before each payment. Recoveries arrive after their configured
lag. The common horizon is `24 + 12 + recovery_lag` months, including month zero;
the default lag gives 39 monthly rows through December 2029.

- Monthly contractual payment is `P*r/(1-(1+r)^(-12))`, with annual nominal rate
  divided by 12. Zero interest uses `P/12`. The last payment clears residual principal.
- Monthly conditional hazard is `h = 1-(1-PD)^(1/12)`. Stressed lifetime PD is
  capped at one. PD/rate bounds, nonnegative exposure and positive integer helper
  terms are validated before arithmetic.
- Expected ultimate loss attributable to a month’s defaults is
  `opening performing EAD * h * LGD`, where `LGD = 1-recovery_rate`. Calendar-month
  expense differs when recovery cash arrives later. Amortizing exposure and survivor weighting matter;
  lifetime loss is not initial principal multiplied by lifetime PD without them.
- Debt is the smaller of the facility cap and advance rate times ending
  performing principal. Funding interest uses opening debt; debt reductions
  require cash repayment.
- Contribution includes interest and merchant fees less net credit loss,
  funding, servicing and acquisition. Operating profit subtracts platform costs
  throughout the common horizon. Principal repayments are not revenue, and a
  charge-off is not a second cash payment.
- Eligibility requires funded loans, passed financial checks, net loss at or
  below its cap and minimum month-end cash at or above its floor. Eligible
  policies rank by unrounded full-runoff profit, then loss, cash and fixed policy
  order. Losses and breakeven do not produce a profitable recommendation.

Fresh 96-digit Decimal contexts use HALF_EVEN and explicit DivisionByZero,
InvalidOperation, Overflow and Underflow traps. Ambient rounding, precision and
traps do not affect calculations. Rate/hazard cancellation uses additional
guard precision, bounded at 4,096 digits; unsupported arithmetic fails explicitly.
No currency quantization occurs inside the financial engine. Loan, debt, cash,
cohort, equity and runoff checks use an absolute USD `1e-16` tolerance.

Count validation uses count units: a precision-derived allowance of at most
one ULP per aggregated count term. A zero denominator cannot fund loans, and
approval ratios remain in `[0,1]` after negligible aggregation roundoff.
Financial loss/cash eligibility comparisons use no threshold epsilon.

Model version `0.1.1` identifies the corrected numerical semantics. Run IDs
include the version, dataset, policy, assumptions and cohorts. The input/output
field shapes and CLI options are retained. Old exported files remain unchanged;
reproducing an old run exactly requires its original model revision. Passing an
old input manifest to this release evaluates those inputs under this release.

## Setup

Prerequisites: Python 3.12 and a working local SQLite library. The committed
constraints record the verified Python 3.12 Linux dependency resolution used
for CI. They are not a certification of every operating system or interpreter.

From the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip check
python -m streamlit run app.py --server.address 127.0.0.1
```

Open the localhost address printed by Streamlit. No credential, external API
or upload is required for the bundled fictional data. Each browser session
keeps its own draft and applied assumptions. Results change only after an
explicit successful Run. Invalid drafts retain the previous accepted result.

Runtime-only installation uses `requirements.txt`. Browser checks use
`requirements-browser.txt`; all three have exact resolved constraints. The
existing build dependency is pinned in `pyproject.toml`. Approved development
tools are included in the development/browser environments. Runtime-only
installations do not require the checkers or typing stubs.

## CLI and input contracts

```bash
python -m lending_simulator.cli --output artifacts/base-case
```

The built wheel contains its default dataset and resources, so the CLI also
runs outside the checkout after installation. The Streamlit entrypoint remains
a source-checkout workflow. The command writes each policy's exact CSV ZIP and workbook, plus
`comparison.json` and `workbook-spec.json`. The CSV package includes exact
Decimal strings, units and the selected manifest. Chart numbers and workbook
numeric cells use display precision; they are not an exact financial transport.
Workbook portfolio sheets are saved snapshots; isolated amortization/default
benchmarks contain live formulas.

A complete custom configuration example:

```bash
cat > /tmp/lending-assumptions.json <<'JSON'
{"initial_cash":"1250000","default_stress":"1","funding_rate":"0.08"}
JSON
python -m lending_simulator.cli --assumptions /tmp/lending-assumptions.json --output artifacts/capital
```

Configuration files accept an assumptions object or a downloaded manifest with
an `assumptions` object. Financial values may be decimal strings; original JSON
numeric tokens are decoded directly to Decimal. Unknown assumption fields,
boolean money, non-finite values, duplicate JSON keys and invalid root shapes
are rejected. Files are bounded at 1,000,000 actual bytes and 128 container levels.
Failures return exit code 2 with a readable error; failed reconciliations return
1; successful computations return 0.

A custom application CSV uses exactly `application_id,month,risk_band,principal_cents`.
IDs must be unique/nonblank, months must be integers 0–23, bands must be
low/medium/high and principal must be positive integer cents, at most $1 million
per application. Quoted IDs, blank lines, CRLF and an empty header-only dataset
are supported. Unknown/extra/missing cells and malformed quoting are rejected.

The default decision uses $500,000 starting cash and a $2 million facility:

| Policy | Approval | Operating profit through runoff | Net loss | Minimum cash | Eligible |
| --- | ---: | ---: | ---: | ---: | --- |
| Conservative | 45% | $48,133 | 0.84% | $147,450 | Yes |
| Balanced | 80% | $294,468 | 1.58% | ($696,143) | No: cash floor |
| Aggressive | 100% | $396,446 | 2.29% | ($1,485,855) | No: cash floor |

These rounded display values accompany the current exact
[base-case reference](docs/base-case.json). The policy settings are illustrative.

## Verification

With the environment active:

```bash
python -m pip check
python -m ruff check lending_simulator app.py tests typings
python -m mypy --strict lending_simulator app.py
python -m pytest
python -m compileall -q app.py lending_simulator
python -m lending_simulator.cli --output artifacts/base-case
python -m pip wheel --no-deps --wheel-dir artifacts/wheels .
```

For the existing real-browser checks:

```bash
python -m pip install -r requirements-browser.txt
python -m playwright install --with-deps chromium
python -m scripts.browser_acceptance --output artifacts/browser-acceptance
python -m scripts.browser_export_resilience --output artifacts/export-resilience
python -m scripts.browser_accessibility --output artifacts/accessibility
```

The browser programs own temporary loopback servers and isolated Chromium
sessions. Their checks cover actual rendering, keyboard/reflow, state,
downloads, server-generation failures and native zoom. AppTest and HTTP startup
checks do not substitute for real browser execution.

[The audit ledger](docs/AUDIT_2026-10-15.md) records severity, baseline file/line
evidence, exact remediation and executed results. Mypy checks all application
modules with strict mode and forbids explicit application `Any` declarations.
[Boundary declarations](typings/README.md) document third-party typing limits
and the runtime coverage that complements them. The
[tooling approval record](docs/DEVELOPMENT_TOOLING_APPROVAL.md) names exact
versions and resolved additions. No check is claimed to pass until executed.

## Model and operating governance

[Model specification](docs/model-spec.md) documents timing and accounting.
[Model risk documentation](docs/MODEL_RISK.md) separates software verification,
independent empirical validation and institutional governance.
[Source fitness](docs/source-fitness.md) explains why historical sources remain
contextual. Earlier validation reports, screenshots and example workbooks are
historical evidence for their identified revisions, rather than validation of
this changed calculation version.

The model excludes prepayment, delinquency stages, taxes, loan sales, price
response, intramonth liquidity and GAAP/CECL provision timing. Negative cash is
an unfunded diagnostic path, not invented financing. Institutional policy
approval, appropriate deployment access/TLS/host controls and independent
validation are prerequisites for real lending use. The audit does not certify
credit prediction accuracy or regulatory compliance.
