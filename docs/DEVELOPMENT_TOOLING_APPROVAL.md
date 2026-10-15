# Development-tooling approval required

Target: `rishabbshankar226/Lending-Profitability-Risk-Simulator` only.

The user's scope lock states: **"STOP and ask for human approval before deleting
directories, adding any new third-party dependency, or making breaking schema/API
changes."** The packages below are new to this repository, so they have not been
installed in its verification environment or added to its active requirements.
The numerical fixes and complete reviewable patches are already prepared.

## Concrete requested addition

Add these exact development-only dependencies to `requirements-dev.txt` and the
`dev` optional group, pin the resolved additions in the development/browser
constraints, finish source annotations, and enforce Ruff/strict mypy in CI.
Runtime dependencies and the existing financial output field shapes stay as
currently implemented. This approval does not include a merge, deployment,
directory deletion or another repository.

| Direct development package | Exact version | Purpose |
| --- | --- | --- |
| mypy | 2.4.0 | Required project-wide strict static analysis |
| ruff | 0.17.0 | Reproducible linting using the verified checker version |
| pandas-stubs | 2.2.3.250527 | Typing aligned with the existing pandas 2.2.3 boundary |
| plotly-stubs | 0.1.4 | Type coverage for the existing untyped chart dependency |

The read-only pip resolution proposes five additional transitive packages:

| Transitive addition | Exact version |
| --- | --- |
| ast_serialize | 0.13.0 |
| librt | 0.16.0 |
| mypy_extensions | 1.1.0 |
| pathspec | 1.1.1 |
| types-pytz | 2026.5.0.20261006 |

PyPI package metadata and a Python 3.12 pip `--dry-run --report` resolved these
versions on October 15, 2026. No existing runtime package upgrade was proposed.
The review export includes the complete metadata, wheel hashes and resolution
report. Availability is verified; type compatibility still needs the actual
post-approval compiler run and source repairs. XlsxWriter's untyped boundary
also needs explicit application typing; no nonexistent stub package is proposed.

## Why completion needs this step

The baseline full strict-mypy command reported 280 errors in 17 source files.
The numerical checkpoint still reports 278, including missing source annotations,
unparameterized containers, dynamic boundary values and missing pandas/Plotly/
XlsxWriter type coverage. Installing tools alone will not fix those source errors.
The proposed next step includes repairing them without replacing the existing
architecture or weakening financial/state assertions.

An already available checker installation was used read-only: the new numeric
and JSON intake modules pass strict mypy, and application/test lint passes.
Those limited results are not represented as a passing full-project type check.
The current CI workflow retains its existing tests; it does not yet enforce the
missing project-wide type gate. The PR remains a draft until that work is complete.

## Acceptance after approval

- Add only the named direct packages and their exact resolved dependencies.
- Run `python -m mypy --strict lending_simulator app.py` with no application Any
  declarations, and finish the annotations/runtime narrowing exposed by it.
- Keep third-party boundary limitations explicit; do not hide application errors
  with blanket import or type-check suppression.
- Add required lint/type steps to CI and rerun unit/property, AppTest, HTTP,
  package/export and real-browser checks for the resulting implementation.
- Update the audit/result record and deliver the complete final patch before
  seeking approval to advance to the variance-analysis repository.
