# Data

Collected daily by the network's workflow (`.github/workflows/network.yml` in
this repository). Records are never deleted; changes over time are kept in
each record and in git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting since July 2026, and those on the calendar: board, date, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen, including amended agendas | The town's [meetings calendar](https://www.wallingfordct.gov/events/meetings/) and [Minutes & Agendas page](https://www.wallingfordct.gov/minutes-and-agendas/) (public records) |
| `meetings/status.json` | When the town website was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes (PDF) | Each agenda (upcoming meetings) and set of minutes as the town posted it, kept in the network's documents bucket at `files.publick.org/wallingford-ct/` rather than in git. Agendas with backup are linked, not kept | Town of Wallingford (public records) |
| `housing/housing.json` | New homes permitted by year (Census estimates: the town reports no months), home value, rent, and rent burden with margins of error, and the housing stock | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/06000US0917078740/) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for Wallingford town, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
