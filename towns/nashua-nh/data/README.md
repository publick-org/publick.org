# Data

Collected by the site's daily run. Records are never deleted; changes over time are kept in each record and in
git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting: board, date, time, place, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen | The city's [meeting portal](https://nashuanh.portal.civicclerk.com); [Nashua School District](https://www.nashua.edu/our-district/board-of-education/boe-meeting-agendas-and-minutes) (public records) |
| `meetings/page_status.json`, `meetings/recordings_status.json`, `meetings/status.json` | When each meetings source was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes | Each agenda and set of minutes as the city posted it, kept in the documents bucket at `files.publick.org/nashua-nh/` rather than in git | The meeting sources above (public records) |
| `meetings/recordings.json` | Meetings' recordings, each matched to its meeting, and how far each got toward a summary | YouTube (public records); transcribed by Nashua Publick |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes, and their Spanish translations, each checked against its document and labeled as AI-generated on the site | Nashua Publick, from the documents above |
| `strings/` | Machine-drafted translations of the town's own text (board and category names, section summaries), until its config gives its own | Nashua Publick |
| `finance/tax_bill.json` | Average single-family tax bill, calculated from the state's tax rates and the parcel map | [NH Department of Revenue Administration](https://www.revenue.nh.gov/about-dra/municipal-and-property-division/municipal-and-property-reports/municipal-and-village), [NH GRANIT](https://granit.unh.edu) parcels (public records) |
| `finance/budget.json` | Tax rates, what the property tax raises, and property tax per resident with the state median | NH Department of Revenue Administration; [Census population estimates](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html) (public records) |
| `schools/schools.json` | Graduation rate, state test results (SAS), and cost per pupil for the district and the state, by year | [New Hampshire Department of Education](https://www.education.nh.gov) (public records) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/16000US3350260/) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for the city, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `static/nashua-wards-2022.geojson` | Ward boundaries, with 2020 census population | [NH GRANIT (2022)](https://www.arcgis.com/home/item.html?id=3d1a8bdf3eaa49e09cf5d9da5b56bf9c); population from the [U.S. Census Bureau](https://www.census.gov) (public domain) |
| `addresses.json` | House number ranges by street, each with its ward, for the Officials page's address lookup | [Census TIGER/Line address ranges](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) (public domain) |
| `place.json` | The Census Bureau's word for the place ("city"), for the site's wording | [Census TIGERweb](https://tigerweb.geo.census.gov) (public domain) |
| `meetings/identities.json`, `run.json`, `checks.json`, `summary-stopped-early.json`, `summary-too-long.json` | Each meeting's identity and page address, the last daily run's record, the checks' results, and the summaries' bookkeeping | Derived |

What Nashua Publick makes here (the summaries and translations, and figures it calculates) is under
the license in the repository's `LICENSE`; each source keeps its own terms.

<!-- Written by the engine's pipeline/data_readme.py from the town's config and data folder. -->
