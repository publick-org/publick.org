# Data

Collected by the site's daily run. Records are never deleted; changes over time are kept in each record and in
git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting: board, date, time, place, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen | The town's [meeting portal](https://hamdenct.portal.civicclerk.com); [Hamden Public Schools](https://www.hamden.org/boe-meeting-agendas-minutes) (public records) |
| `meetings/page_status.json`, `meetings/recordings_status.json`, `meetings/status.json` | When each meetings source was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes | Each agenda and set of minutes as the town posted it, kept in the documents bucket at `files.publick.org/hamden-ct/` rather than in git | The meeting sources above (public records) |
| `meetings/recordings.json` | Meetings' recordings, each matched to its meeting, and how far each got toward a summary | CivicClerk (public records); transcribed by Hamden Publick |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes, and their Spanish translations, each checked against its document and labeled as AI-generated on the site | Hamden Publick, from the documents above |
| `strings/` | Machine-drafted translations of the town's own text (board and category names, section summaries), until its config gives its own | Hamden Publick |
| `311/requests.json`, `311/scorecard.json` | One record per public 311 request (category, location, area, status, and when it was submitted, acknowledged, closed or reopened; no descriptions, photos or reporter details), and the figures the 311 pages show, kept in the documents bucket at `files.publick.org/hamden-ct/data/311/` rather than in git | [SeeClickFix](https://seeclickfix.com), [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/) |
| `311/status.json`, `311/sync.json` | When 311 was last read, and how far its reading has got | Derived |
| `finance/tax_bill.json` | Average single-family tax bill, calculated from the state's mill rates and the statewide Parcel and CAMA file | [Connecticut Office of Policy and Management, on data.ct.gov](https://data.ct.gov/d/emyx-j53e) (public records) |
| `finance/budget.json` | Mill rate, tax levy, grand list, adopted budget, and the audited Municipal Fiscal Indicators, with property tax per resident and the state median | Connecticut Office of Policy and Management, on [data.ct.gov](https://data.ct.gov) (public records) |
| `schools/schools.json` | Graduation rate, chronic absenteeism, state test results (Smarter Balanced), and spending per pupil for the district and the state, by year | [Connecticut State Department of Education, EdSight](https://public-edsight.ct.gov) (public records) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/06000US0917035650/) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for the town, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `place.json` | The Census Bureau's word for the place ("town"), for the site's wording | [Census TIGERweb](https://tigerweb.geo.census.gov) (public domain) |
| `meetings/identities.json`, `run.json`, `checks.json` | Each meeting's identity and page address, the last daily run's record, the checks' results, and the summaries' bookkeeping | Derived |

What Hamden Publick makes here (the summaries and translations, and figures it calculates) is under
the license in the repository's `LICENSE`; each source keeps its own terms.

<!-- Written by the engine's pipeline/data_readme.py from the town's config and data folder. -->
