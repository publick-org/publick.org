# Data

Collected by the site's daily run. Records are never deleted; changes over time are kept in each record and in
git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting: board, date, time, place, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen | The city's [calendar](https://www.southburlingtonvt.gov/calendar.aspx) and [Agenda Center](https://www.southburlingtonvt.gov/AgendaCenter); [South Burlington School District](https://www.sbschools.net/page/school-board) (public records) |
| `meetings/page_status.json`, `meetings/recordings_status.json`, `meetings/status.json` | When each meetings source was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes | Each agenda and set of minutes as the city posted it, kept in the documents bucket at `files.publick.org/south-burlington-vt/` rather than in git | The meeting sources above (public records) |
| `meetings/recordings.json` | Meetings' recordings, each matched to its meeting, and how far each got toward a summary | The Internet Archive and YouTube (public records); transcribed by South Burlington Publick |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes, and their Spanish translations, each checked against its document and labeled as AI-generated on the site | South Burlington Publick, from the documents above |
| `strings/` | Machine-drafted translations of the town's own text (board and category names, section summaries), until its config gives its own | South Burlington Publick |
| `finance/tax_bill.json` | Average homestead tax bill by tax year, calculated from the state's tax rates and the homestead values in the statewide parcel data | [Vermont Department of Taxes, PVR Annual Report](https://tax.vermont.gov/pvr-annual-report), [VCGI statewide parcel data](https://geodata.vermont.gov/datasets/vt-data-statewide-standardized-parcel-data-parcel-polygons) (public records) |
| `finance/budget.json` | Tax rates (homestead and nonhomestead education, municipal) with the median of Vermont's towns, what the property tax raised by part, the grand list, and property tax per resident with the state median | [Vermont Department of Taxes, PVR Annual Report](https://tax.vermont.gov/pvr-annual-report); [Census population estimates](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html) (public records) |
| `schools/schools.json` | Graduation rate, chronic absenteeism, and state test results (VTCAP) for the district and the state, by year, and the district's budget and education spending per pupil | Vermont Agency of Education: [Vermont Education Dashboard data on data.vermont.gov](https://data.vermont.gov), [per pupil spending report](https://education.vermont.gov/accountability-data/financial-reports/per-pupil-spending) (public records) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/16000US5066175/) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for the city, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `place.json` | The Census Bureau's word for the place ("city"), for the site's wording | [Census TIGERweb](https://tigerweb.geo.census.gov) (public domain) |
| `meetings/identities.json`, `run.json`, `checks.json`, `summary-batch.json` | Each meeting's identity and page address, the last daily run's record, the checks' results, and the summaries' bookkeeping | Derived |

What South Burlington Publick makes here (the summaries and translations, and figures it calculates) is under
the license in the repository's `LICENSE`; each source keeps its own terms.

<!-- Written by the engine's pipeline/data_readme.py from the town's config and data folder. -->
