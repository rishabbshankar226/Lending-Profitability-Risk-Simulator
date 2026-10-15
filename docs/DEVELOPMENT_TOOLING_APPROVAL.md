# Development-tooling approval record

Target: `rishabbshankar226/Lending-Profitability-Risk-Simulator` only.

The user's scope lock states: **"STOP and ask for human approval before deleting
directories, adding any new third-party dependency, or making breaking schema/API
changes."** The concrete proposal below was presented before installation.
The user approved it with "continue" on October 15, 2026. Only the four named
direct development packages and their five resolved additions were installed
and added. The package installation report is retained with the review evidence.

## Approved addition

These exact development-only dependencies are in `requirements-dev.txt` and the
`dev` optional group, with resolved additions pinned in development/browser
constraints. Source annotations are repaired and CI requires Ruff/strict mypy.
Runtime dependencies and the existing financial output field shapes stay as
currently implemented. This approval does not include a merge, deployment,
directory deletion or another repository.

| Direct development package | Exact version | Purpose |
| --- | --- | --- |
| mypy | 2.4.0 | Required project-wide strict static analysis |
| ruff | 0.17.0 | Reproducible linting using the verified checker version |
| pandas-stubs | 2.2.3.250527 | Typing aligned with the existing pandas 2.2.3 boundary |
| plotly-stubs | 0.1.4 | Type coverage for the existing untyped chart dependency |

The approved resolution adds five transitive packages:

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
report. The post-approval full compiler run passes all 22 application files.
XlsxWriter's consumed API has explicit first-party declarations checked against
the installed 3.2.9 source; no additional third-party stub was installed.
The current 59-version runtime/browser/build/development set returned zero
matched advisories in an OSV query retained with the review export.
That point-in-time lookup does not establish absence of undisclosed defects.

## Source repairs and verification

The baseline full strict-mypy command reported 280 errors in 17 source files.
The numerical checkpoint reported 278, including missing source annotations,
unparameterized containers, dynamic boundary values and missing pandas/Plotly/
XlsxWriter type coverage. Installing the tools exposed 285 errors before source
repairs. The final local strict run reports zero issues in all 22 source files.
Existing financial/state assertions are unchanged; all 200 tests pass locally,
including six added reporting regressions. Installation alone was not completion.

The earlier limited checks from an existing checker installation are historical
evidence. Verification now uses this repository's approved environment. CI
requires dependency consistency, Ruff and full strict mypy before tests.
The [audit ledger](AUDIT_2026-10-15.md) records exact final CI/browser evidence;
the [typing boundary record](../typings/README.md) states static-analysis limits.

## Approved acceptance criteria

- Add only the named direct packages and their exact resolved dependencies.
- Run `python -m mypy --strict lending_simulator app.py` with no application Any
  declarations, and finish the annotations/runtime narrowing exposed by it.
- Keep third-party boundary limitations explicit; do not hide application errors
  with blanket import or type-check suppression.
- Add required lint/type steps to CI and rerun unit/property, AppTest, HTTP,
  package/export and real-browser checks for the resulting implementation.
- Update the audit/result record and deliver the complete final patch before
  seeking approval to advance to the variance-analysis repository.
