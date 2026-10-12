# Data

Collected daily by the network's workflow (`.github/workflows/network.yml` in
this repository). Records are never deleted; changes over time are kept in
each record and in git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting since July 2026, and those on the calendar: board, date, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen, including amended agendas | The town's [meetings calendar](https://www.wallingfordct.gov/events/meetings/) and [Minutes & Agendas page](https://www.wallingfordct.gov/minutes-and-agendas/); the Board of Education's from [Wallingford Public Schools](https://www.wallingford.k12.ct.us/board-of-education/board-of-education-meetings) (public records) |
| `meetings/status.json`, `meetings/finalsite_status.json` | When the town website and the Board of Education's page were last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes (PDF) | Each agenda (upcoming meetings) and set of minutes as the town posted it, kept in the network's documents bucket at `files.publick.org/wallingford-ct/` rather than in git. Agendas with backup are linked, not kept | Town of Wallingford (public records) |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes, and their Spanish translations, each checked against its document and labeled as AI-generated on the site | Publick, from the documents above |
| `finance/tax_bill.json` | Average single-family tax bill, calculated by Publick from the state's mill rates and the statewide Parcel and CAMA file | [Connecticut Office of Policy and Management, on data.ct.gov](https://data.ct.gov/d/emyx-j53e) (public records) |
| `finance/budget.json` | Mill rate, tax levy, grand list, adopted budget, and the audited Municipal Fiscal Indicators, with property tax per resident and the state median | Connecticut Office of Policy and Management, on [data.ct.gov](https://data.ct.gov) (public records) |
| `schools/schools.json` | Graduation rate, chronic absenteeism, state test results (Smarter Balanced), and spending per pupil for Wallingford Public Schools and the state, by year | [Connecticut State Department of Education, EdSight](https://public-edsight.ct.gov) (public records) |
| `housing/housing.json` | New homes permitted by year (Census estimates: the town reports no months), home value, rent, and rent burden with margins of error, and the housing stock | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/06000US0917078740/) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for Wallingford town, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |

What Publick makes here (the summaries and translations, and figures it
calculates) is under CC BY 4.0, with credit; the repository's `LICENSE` says
how, and what keeps its own terms.
