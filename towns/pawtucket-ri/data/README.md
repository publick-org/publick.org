# Data

Collected by the site's daily run. Records are never deleted; changes over time are kept in each record and in
git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting: board, date, time, place, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen | [Rhode Island Open Meetings portal](https://opengov.sos.ri.gov/OpenMeetingsPublic/OpenMeetingDashboard?subtopmenuId=201) (public records) |
| `meetings/opengov_status.json`, `meetings/recordings_status.json`, `meetings/status.json` | When each meetings source was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes | Each agenda and set of minutes as the city posted it, kept in the documents bucket at `files.publick.org/pawtucket-ri/` rather than in git | The meeting sources above (public records) |
| `meetings/recordings.json` | Meetings' recordings, each matched to its meeting, and how far each got toward a summary | YouTube (public records); transcribed by Pawtucket Publick |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes, and their Spanish translations, each checked against its document and labeled as AI-generated on the site | Pawtucket Publick, from the documents above |
| `strings/` | Machine-drafted translations of the town's own text (board and category names, section summaries), until its config gives its own | Pawtucket Publick |
| `311/requests.json`, `311/scorecard.json` | One record per public 311 request (category, location, area, status, and when it was submitted, acknowledged, closed or reopened; no descriptions, photos or reporter details), and the figures the 311 pages show, kept in the documents bucket at `files.publick.org/pawtucket-ri/data/311/` rather than in git | [SeeClickFix](https://seeclickfix.com), [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/) |
| `311/status.json`, `311/sync.json` | When 311 was last read, and how far its reading has got | Derived |
| `finance/budget.json` | Tax rates by class of property, the tax levy and net assessed value by class, and property tax per resident, with the state's median | [Rhode Island Division of Municipal Finance](https://municipalfinance.ri.gov/) statewide tables; [Census population estimates](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html) (public records) |
| `schools/schools.json` | Graduation rate, chronic absenteeism, RICAS results (grades 3-8), and spending per pupil for the district and the state, by year | [Rhode Island Department of Education, report card data files and assessment data portal](https://reportcard.ride.ri.gov/DataFiles) (public records) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/16000US4454640/) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for the city, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `static/pawtucket-precincts-2022.geojson` | District boundaries, with 2020 census population | [RIGIS (2022)](https://www.arcgis.com/home/item.html?id=9104ca2e5e9b4cdb9985e8935ef2514d); population from the [U.S. Census Bureau](https://www.census.gov) (public domain) |
| `addresses.json` | House number ranges by street, each with its ward, for the Officials page's address lookup | [Census TIGER/Line address ranges](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) (public domain) |
| `place.json` | The Census Bureau's word for the place ("city"), for the site's wording | [Census TIGERweb](https://tigerweb.geo.census.gov) (public domain) |
| `meetings/identities.json`, `run.json`, `checks.json` | Each meeting's identity and page address, the last daily run's record, the checks' results, and the summaries' bookkeeping | Derived |

What Pawtucket Publick makes here (the summaries and translations, and figures it calculates) is under
the license in the repository's `LICENSE`; each source keeps its own terms.

<!-- Written by the engine's pipeline/data_readme.py from the town's config and data folder. -->
