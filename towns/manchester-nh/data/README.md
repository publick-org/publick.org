# Data

Collected daily by the workflow in `.github/workflows/deploy.yml`. Records are
never deleted; changes over time are kept in each record and in git history.

| Path | Contents | Source and license |
|---|---|---|
| `311/requests.json` | One record per public SeeClickFix request in the City of Manchester DPW request types: category, location, ward, status, and submitted/acknowledged/closed/reopened times. No descriptions, photos, or reporter details | [SeeClickFix](https://seeclickfix.com), [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/) |
| `311/scorecard.json` | Metrics shown on the 311 page, recomputed daily | Derived from `311/requests.json`; same license |
| `static/manchester-wards-2022.geojson` | The 12 wards as of the city's 2021 redistricting, with 2020 census population (the sum of the census blocks inside each ward; 115,644 in all, each ward within 20 people of the city's redistricting report) | [NH GRANIT, Political Districts (Voting Wards), 2022](https://www.arcgis.com/home/item.html?id=3d1a8bdf3eaa49e09cf5d9da5b56bf9c); population from the [U.S. Census Bureau](https://www.census.gov) (public domain) |
| `meetings/meetings.json` | One record per public meeting since January 2026: board, title, date, time, place, status (cancelled, removed from the calendar), a link to its agenda where the city posts it, and every change since it was first seen | The city's [CivicClerk portal](https://manchesternh.portal.civicclerk.com) (Board of Mayor and Aldermen, its committees, the City Clerk's boards) and [city calendar](https://www.manchesternh.gov/Government/City-Calendars) (other boards and commissions); public records |
| `meetings/status.json` | When each calendar was last checked, for the site and the stale-data alert | Derived |
| `labor/unemployment.json` | Monthly unemployment rate for Manchester city, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org) (public records) |

Data derived from SeeClickFix is shared under the same CC BY-NC-SA 3.0 license,
with attribution to seeclickfix.com.

As more Manchester sources are added (agendas and minutes, budget, schools),
their files appear here under `meetings/`, `summaries/`, `finance/`, and `schools/`.
