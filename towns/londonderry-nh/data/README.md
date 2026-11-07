# Data

Collected by the site's daily run. Records are never deleted; changes over time are kept in each record and in
git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting: board, date, time, place, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen | The town's [calendar](https://www.londonderrynh.gov/calendar.aspx) and [Agenda Center](https://www.londonderrynh.gov/AgendaCenter) (public records) |
| `meetings/recordings_status.json`, `meetings/status.json` | When each meetings source was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes | Each agenda and set of minutes as the town posted it, kept in the documents bucket at `files.publick.org/londonderry-nh/` rather than in git | The meeting sources above (public records) |
| `meetings/recordings.json` | Meetings' recordings, each matched to its meeting, and how far each got toward a summary | YouTube (public records); transcribed by Londonderry Publick |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes, and their Spanish translations, each checked against its document and labeled as AI-generated on the site | Londonderry Publick, from the documents above |
| `strings/` | Machine-drafted translations of the town's own text (board and category names, section summaries), until its config gives its own | Londonderry Publick |
| `finance/tax_bill.json` | Average single-family tax bill, calculated from the state's tax rates and the parcel map | [NH Department of Revenue Administration](https://www.revenue.nh.gov/about-dra/municipal-and-property-division/municipal-and-property-reports/municipal-and-village), [NH GRANIT](https://granit.unh.edu) parcels (public records) |
| `finance/budget.json` | Tax rates, what the property tax raises, and property tax per resident with the state median | NH Department of Revenue Administration; [Census population estimates](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html) (public records) |
| `schools/schools.json` | Graduation rate, state test results (SAS), and cost per pupil for the district and the state, by year | [New Hampshire Department of Education](https://www.education.nh.gov) (public records) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/06000US3301543220/) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for the town, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `place.json` | The Census Bureau's word for the place ("town"), for the site's wording | [Census TIGERweb](https://tigerweb.geo.census.gov) (public domain) |
| `meetings/identities.json`, `run.json`, `checks.json` | Each meeting's identity and page address, the last daily run's record, the checks' results, and the summaries' bookkeeping | Derived |

What Londonderry Publick makes here (the summaries and translations, and figures it calculates) is under
the license in the repository's `LICENSE`; each source keeps its own terms.

<!-- Written by the engine's pipeline/data_readme.py from the town's config and data folder. -->
