# Data

Collected by the site's daily run. Records are never deleted; changes over time are kept in each record and in
git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting: board, date, time, place, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen | The city's [meeting portal](https://springfieldma.portal.civicclerk.com); [Springfield Public Schools](https://www.springfieldpublicschools.com/school_committee/school_committee_meeting-_minutes_archive) (public records) |
| `meetings/recordings_status.json`, `meetings/sharpschool_status.json`, `meetings/status.json` | When each meetings source was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes | Each agenda and set of minutes as the city posted it, kept in the documents bucket at `files.publick.org/springfield-ma/` rather than in git | The meeting sources above (public records) |
| `meetings/recordings.json` | Meetings' recordings, each matched to its meeting, and how far each got toward a summary | YouTube (public records); transcribed by Springfield Publick |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes, and their Spanish translations, each checked against its document and labeled as AI-generated on the site | Springfield Publick, from the documents above |
| `strings/` | Machine-drafted translations of the town's own text (board and category names, section summaries), until its config gives its own | Springfield Publick |
| `finance/tax_bill.json` | Average single-family tax bill, by fiscal year | [Mass. Division of Local Services, Municipal Databank](https://dls-gw.dor.state.ma.us/reports/rdPage.aspx?rdReport=AverageSingleTaxBill.SingleFamTaxBill_wRange) (public records) |
| `finance/budget.json` | General fund spending by function, revenue by source, levy and levy limit, free cash, stabilization fund, bond ratings, and spending per resident with the state median | [Mass. Division of Local Services, Municipal Databank](https://dls-gw.dor.state.ma.us/reports/rdPage.aspx?rdReport=ScheduleA.GenFund_MAIN) (public records) |
| `schools/schools.json` | Graduation rate, chronic absenteeism, and MCAS results for the district and the state, by year | [DESE, Education-to-Career data hub](https://educationtocareer.data.mass.gov) (public records) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error; the Subsidized Housing Inventory's share | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/16000US2567000/), [EOHLC Subsidized Housing Inventory](https://www.mass.gov/info-details/subsidized-housing-inventory-shi) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for the city, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `static/springfield-precincts-2022.geojson` | Ward boundaries, with 2020 census population | [MassGIS (2022)](https://gis.data.mass.gov/maps/aec5130790814ace94438d3bcf23cf9a); population from the [U.S. Census Bureau](https://www.census.gov) (public domain) |
| `addresses.json` | House number ranges by street, each with its ward, for the Officials page's address lookup | [Census TIGER/Line address ranges](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) (public domain) |
| `place.json` | The Census Bureau's word for the place ("city"), for the site's wording | [Census TIGERweb](https://tigerweb.geo.census.gov) (public domain) |
| `meetings/identities.json`, `run.json`, `checks.json` | Each meeting's identity and page address, the last daily run's record, the checks' results, and the summaries' bookkeeping | Derived |

What Springfield Publick makes here (the summaries and translations, and figures it calculates) is under
the license in the repository's `LICENSE`; each source keeps its own terms.

<!-- Written by the engine's pipeline/data_readme.py from the town's config and data folder. -->
