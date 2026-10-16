# XlsxWriter boundary declarations

These first-party declarations cover the XlsxWriter 3.2.9 methods consumed by
`lending_simulator/exports.py`. They are static signatures, not runtime
implementations or substitutes for workbook execution. The installed package
has incomplete annotations and no PEP 561 marker.

Signatures were checked against the pinned installed source on October 15,
2026, including its A1-cell overload decorators. Only the forms called by this
application are declared. Workbook options and format/validation dictionaries
remain `Mapping[str, object]`; the declaration does not claim to validate every
XlsxWriter option name. Actual workbook generation, ZIP contents, formulas,
cached values and exports are exercised by the existing tests and browser
download checks. Recheck this boundary before changing XlsxWriter's pin.

## Other dynamic boundaries

The application declares no `Any` types; mypy's strict mode and
`disallow_any_explicit` enforce this. Typed dictionaries describe existing run
manifests, assumption overrides, stress cases, workbook specifications and UI
callbacks. Narrowing casts are confined to validated input maps, application-
owned session state, bundled evidence and the known numeric/display columns
returned by pandas. They do not turn untrusted arithmetic into trusted results.

The pinned Plotly stubs restrict some supported date/categorical coordinates
and two-dimensional hover/text arrays. Those charts use Plotly's documented
property-dictionary constructors; Plotly's actual property validators remain
enabled, with no type-ignore or import suppression. Static checking does not
validate every dictionary property. AppTest and real-browser suites exercise
the resulting figures, labels, hover data and applied-case marker.

Primary references checked October 15, 2026:

- [Heatmap constructor and property dictionaries](https://plotly.com/python-api-reference/generated/plotly.graph_objects.Heatmap.html)
- [Date coordinates and shape properties](https://plotly.com/python/reference/layout/shapes/)
