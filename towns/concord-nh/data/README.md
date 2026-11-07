# Data

Collected by the site's daily run. Records are never deleted; changes over time are kept in each record and in
git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting: board, date, time, place, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen | The city's [calendar](https://www.concordnh.gov/calendar.aspx), [Archive Center](https://www.concordnh.gov/Archive.aspx) and [meeting portal](https://concordnh.legistar.com/Calendar.aspx); [Concord School District](https://www.sau8.org/board-of-education-2026-agendas-min) (public records) |
| `meetings/page_status.json`, `meetings/recordings_status.json`, `meetings/status.json` | When each meetings source was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes | Each agenda and set of minutes as the city posted it, kept in the documents bucket at `files.publick.org/concord-nh/` rather than in git | The meeting sources above (public records) |
| `meetings/recordings.json` | Meetings' recordings, each matched to its meeting, and how far each got toward a summary | TelVue and YouTube (public records); transcribed by Concord Publick |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes, and their Spanish translations, each checked against its document and labeled as AI-generated on the site | Concord Publick, from the documents above |
| `strings/` | Machine-drafted translations of the town's own text (board and category names, section summaries), until its config gives its own | Concord Publick |
| `311/requests.json`, `311/scorecard.json` | One record per public 311 request (category, location, area, status, and when it was submitted, acknowledged, closed or reopened; no descriptions, photos or reporter details), and the figures the 311 pages show, kept in the documents bucket at `files.publick.org/concord-nh/data/311/` rather than in git | [SeeClickFix](https://seeclickfix.com), [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/) |
| `311/status.json`, `311/sync.json` | When 311 was last read, and how far its reading has got | Derived |
| `finance/tax_bill.json` | Average single-family tax bill, calculated from the state's tax rates and the parcel map | [NH Department of Revenue Administration](https://www.revenue.nh.gov/about-dra/municipal-and-property-division/municipal-and-property-reports/municipal-and-village), [NH GRANIT](https://granit.unh.edu) parcels (public records) |
| `finance/budget.json` | Tax rates, what the property tax raises, and property tax per resident with the state median | NH Department of Revenue Administration; [Census population estimates](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html) (public records) |
| `schools/schools.json` | Graduation rate, state test results (SAS), and cost per pupil for the district and the state, by year | [New Hampshire Department of Education](https://www.education.nh.gov) (public records) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/16000US3314200/) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for the city, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `static/concord-wards-2022.geojson` | Ward boundaries, with 2020 census population | [NH GRANIT (2022)](https://www.arcgis.com/home/item.html?id=3d1a8bdf3eaa49e09cf5d9da5b56bf9c); population from the [U.S. Census Bureau](https://www.census.gov) (public domain) |
| `addresses.json` | House number ranges by street, each with its ward, for the Officials page's address lookup | [Census TIGER/Line address ranges](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) (public domain) |
| `place.json` | The Census Bureau's word for the place ("city"), for the site's wording | [Census TIGERweb](https://tigerweb.geo.census.gov) (public domain) |
| `meetings/identities.json`, `run.json`, `checks.json` | Each meeting's identity and page address, the last daily run's record, the checks' results, and the summaries' bookkeeping | Derived |

What Concord Publick makes here (the summaries and translations, and figures it calculates) is under
the license in the repository's `LICENSE`; each source keeps its own terms.

<!-- Written by the engine's pipeline/data_readme.py from the town's config and data folder. -->
