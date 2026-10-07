# Data

Collected daily by the network's workflow (`.github/workflows/network.yml` in
this repository). Records are never deleted; changes over time are kept in
each record and in git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting since January 2026, and those on the city calendar: board, date, time, place, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen, including revised agendas | The city's [Agenda Center](https://www.bangormaine.gov/AgendaCenter) and [calendar](https://www.bangormaine.gov/Calendar.aspx) (public records) |
| `meetings/status.json` | When the Agenda Center and the calendar were last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes (PDF) | Each agenda (upcoming meetings) and set of minutes as the city posted it, kept in the network's documents bucket at `files.publick.org/bangor-me/` rather than in git. Minutes posted as Word documents are linked, not kept | City of Bangor Agenda Center (public records) |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes from July 2026 on, and their Spanish translations, labeled as AI-generated on the site | Publick, from the documents above |
| `schools/schools.json` | Graduation rate, chronic absenteeism, state test results, and spending per pupil for Bangor Public Schools and the state, by year | [Maine Department of Education, ESSA Dashboard](https://www.maine.gov/doe/dashboard), through the engine's yearly extract (`pipeline/states/me/`) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error, and the housing stock | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/16000US2302795/) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for Bangor city, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |

Bangor has no wards or precincts (every voter votes at one polling place, and
every seat is elected at-large), so there is no ward file in `static/`. The
city's 311 requests (SeeClickFix) and its tax rate and property tax (Maine
Revenue Services) will appear under `311/` and `finance/` once the engine can
show them for Bangor (see `config/bangor.toml`).
