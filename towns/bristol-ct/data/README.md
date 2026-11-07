# Data

Collected by the site's daily run. Records are never deleted; changes over time are kept in each record and in
git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting: board, date, time, place, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen | The city's [meeting portal](https://bristolct.portal.civicclerk.com); [Bristol Public Schools](https://www.bristol.k12.ct.us/boe-meeting-minutes), also on [meetings.boardbook.org](https://meetings.boardbook.org/Public/Organization/2447) (public records) |
| `meetings/boardbook_status.json`, `meetings/page_status.json`, `meetings/recordings_status.json`, `meetings/status.json` | When each meetings source was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes | Each agenda and set of minutes as the city posted it, kept in the documents bucket at `files.publick.org/bristol-ct/` rather than in git | The meeting sources above (public records) |
| `meetings/recordings.json` | Meetings' recordings, each matched to its meeting, and how far each got toward a summary | CivicClerk and YouTube (public records); transcribed by Bristol Publick |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes, and their Spanish translations, each checked against its document and labeled as AI-generated on the site | Bristol Publick, from the documents above |
| `strings/` | Machine-drafted translations of the town's own text (board and category names, section summaries), until its config gives its own | Bristol Publick |
| `finance/tax_bill.json` | Average single-family tax bill, calculated from the state's mill rates and the statewide Parcel and CAMA file | [Connecticut Office of Policy and Management, on data.ct.gov](https://data.ct.gov/d/emyx-j53e) (public records) |
| `finance/budget.json` | Mill rate, tax levy, grand list, adopted budget, and the audited Municipal Fiscal Indicators, with property tax per resident and the state median | Connecticut Office of Policy and Management, on [data.ct.gov](https://data.ct.gov) (public records) |
| `schools/schools.json` | Graduation rate, chronic absenteeism, state test results (Smarter Balanced), and spending per pupil for the district and the state, by year | [Connecticut State Department of Education, EdSight](https://public-edsight.ct.gov) (public records) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/16000US0908420/) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for the city, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `static/bristol-council-districts-2022.geojson` | District boundaries, with 2020 census population | [The City of Bristol (2022)](https://server1.mapxpress.net/arcgis/rest/services/Bristol/Active/MapServer/39); population from the [U.S. Census Bureau](https://www.census.gov) (public domain) |
| `addresses.json` | House number ranges by street, each with its ward, for the Officials page's address lookup | [Census TIGER/Line address ranges](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) (public domain) |
| `place.json` | The Census Bureau's word for the place ("city"), for the site's wording | [Census TIGERweb](https://tigerweb.geo.census.gov) (public domain) |
| `meetings/identities.json`, `run.json`, `checks.json`, `summary-batch.json` | Each meeting's identity and page address, the last daily run's record, the checks' results, and the summaries' bookkeeping | Derived |

What Bristol Publick makes here (the summaries and translations, and figures it calculates) is under
the license in the repository's `LICENSE`; each source keeps its own terms.

<!-- Written by the engine's pipeline/data_readme.py from the town's config and data folder. -->
