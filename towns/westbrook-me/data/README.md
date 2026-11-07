# Data

Collected by the site's daily run. Records are never deleted; changes over time are kept in each record and in
git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting: board, date, time, place, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen | The city's [calendar](https://www.westbrookmaine.gov/calendar.aspx) and [Agenda Center](https://www.westbrookmaine.gov/AgendaCenter); [Westbrook School Department](https://www.westbrookschools.org/o/wsd/page/westbrook-school-committee) (public records) |
| `meetings/page_status.json`, `meetings/status.json` | When each meetings source was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes | Each agenda and set of minutes as the city posted it, kept in the documents bucket at `files.publick.org/westbrook-me/` rather than in git | The meeting sources above (public records) |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes, and their Spanish translations, each checked against its document and labeled as AI-generated on the site | Westbrook Publick, from the documents above |
| `strings/` | Machine-drafted translations of the town's own text (board and category names, section summaries), until its config gives its own | Westbrook Publick |
| `finance/budget.json` | Tax rate by tax year with the median of Maine's municipalities, the property tax commitment, taxable valuation and certified ratio, and property tax per resident with the state median | [Maine Revenue Services, Municipal Valuation Return Statistical Summary](https://www.maine.gov/revenue/taxes/property-tax/municipal-services/valuation-return-statistical-summary); [Census population estimates](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html) (public records) |
| `schools/schools.json` | Graduation rate, chronic absenteeism, state test results, and spending per pupil for the district and the state, by year | [Maine Department of Education, ESSA Dashboard](https://www.maine.gov/doe/dashboard) (public records) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/16000US2382105/) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for the city, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `static/westbrook-wards-2025.geojson` | Ward boundaries, with 2020 census population | [The City of Westbrook (2025)](https://services5.arcgis.com/Cxl8RQ4PEBjdRbtW/arcgis/rest/services/Voting/FeatureServer/177); population from the [U.S. Census Bureau](https://www.census.gov) (public domain) |
| `addresses.json` | House number ranges by street, each with its ward, for the Officials page's address lookup | [Census TIGER/Line address ranges](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) (public domain) |
| `place.json` | The Census Bureau's word for the place ("city"), for the site's wording | [Census TIGERweb](https://tigerweb.geo.census.gov) (public domain) |
| `meetings/identities.json`, `run.json`, `checks.json` | Each meeting's identity and page address, the last daily run's record, the checks' results, and the summaries' bookkeeping | Derived |

What Westbrook Publick makes here (the summaries and translations, and figures it calculates) is under
the license in the repository's `LICENSE`; each source keeps its own terms.

<!-- Written by the engine's pipeline/data_readme.py from the town's config and data folder. -->
