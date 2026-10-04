# Data

Collected daily by the network's workflow (`.github/workflows/network.yml` in
this repository). Records are never deleted; changes over time are kept in
each record and in git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting since January 2026, and those already scheduled: board, date, time, place, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen | The town's [CivicClerk portal](https://southkingstownri.portal.civicclerk.com) (Town Council and the town's boards and commissions); public records |
| `meetings/status.json` | When the portal was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes (PDF) | Each agenda (upcoming meetings) and set of minutes as the town posted it, kept in the network's documents bucket at `files.publick.org/south-kingstown-ri/` rather than in git. Agenda packets are linked, not kept | Town of South Kingstown (public records) |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes from July 2026 on, and their Spanish translations, labeled as AI-generated on the site | Publick, from the documents above |
| `311/requests.json` | One record per public SeeClickFix request to the Town of South Kingstown: category, location, voting precinct, status, and submitted/acknowledged/closed/reopened times. No descriptions, photos, or reporter details | [SeeClickFix](https://seeclickfix.com), [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/) |
| `311/scorecard.json` | Metrics shown on the 311 page, recomputed daily | Derived from `311/requests.json`; same license |
| `static/south-kingstown-precincts-2022.geojson` | The town's 11 voting precincts (3201 to 3211) as drawn in the 2021-2022 redistricting, with 2020 census population (the sum of the census blocks whose internal point is inside each precinct; 31,931 in all, the town's 2020 count). The town has no wards | [RIGIS, Voting Precincts (2022)](https://www.arcgis.com/home/item.html?id=9104ca2e5e9b4cdb9985e8935ef2514d) (from each town's Board of Canvassers and the Department of State); population from the [U.S. Census Bureau](https://www.census.gov) (public domain) |
| `finance/budget.json` | Tax rates by class of property, the tax levy and net assessed value by class, and property tax per resident, with the state's median | [Rhode Island Division of Municipal Finance](https://municipalfinance.ri.gov/) statewide tables (public records); per resident calculated by Publick with Census population estimates |
| `schools/schools.json` | Graduation rate, chronic absenteeism, RICAS results (grades 3-8), and spending per pupil for South Kingstown Public Schools and the state, by year | [Rhode Island Department of Education, report card data files and assessment data portal](https://reportcard.ride.ri.gov/DataFiles) |
| `housing/housing.json` | New homes permitted by year, home value, rent, and rent burden with margins of error, and the housing stock | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/06000US4400967460/) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for South Kingstown town, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `place.json` | The Census Bureau's word for the place ("town"), for the site's wording | [Census TIGERweb](https://tigerweb.geo.census.gov) (public domain) |

Data derived from SeeClickFix is shared under the same CC BY-NC-SA 3.0 license,
with attribution to seeclickfix.com.

The School Committee's meetings aren't collected: it posts them on BoardDocs
and the Secretary of State's Open Meetings portal, which Publick doesn't read.
