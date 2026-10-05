# Data

Collected daily by the network's workflow (`.github/workflows/network.yml` in
this repository). Records are never deleted; changes over time are kept in
each record and in git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting on the city calendar, and per meeting since January 2026 with minutes in the Archive Center: board, date, time, place, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen, including revised agendas | The city's [calendar](https://www.lewistonmaine.gov/Calendar.aspx) and [Archive Center](https://www.lewistonmaine.gov/Archive.aspx) (public records) |
| `meetings/status.json` | When the city calendar was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes (PDF) | Each agenda (upcoming meetings) and set of minutes as the city posted it, kept in the network's documents bucket at `files.publick.org/lewiston-me/` rather than in git | City of Lewiston Archive Center (public records) |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes, and their Spanish translations, labeled as AI-generated on the site | Publick, from the documents above |
| `finance/budget.json` | Tax rate by tax year with the median of Maine's municipalities, the property tax commitment, taxable valuation and certified ratio, and property tax per resident with the state median | [Maine Revenue Services, Municipal Valuation Return Statistical Summary](https://www.maine.gov/revenue/taxes/property-tax/municipal-services/valuation-return-statistical-summary); [U.S. Census Bureau population estimates](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html) (public records) |
| `finance/tax_bill.json` | Average single-family tax bill by tax year, calculated by Publick: the average assessed value of Lewiston's single-family homes (land use 101) times the tax rate | Maine Revenue Services (above) and the [Maine GeoLibrary's parcel table](https://www.arcgis.com/home/item.html?id=346131b710a645ffb624f448a9cba6d4) (public records) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error; the housing stock | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org/profiles/16000US2338740/) (public records) |
| `schools/schools.json` | Graduation rate, chronic absenteeism, state test results, and spending per pupil for Lewiston Public Schools and the state, by year | [Maine Department of Education, ESSA Dashboard](https://www.maine.gov/doe/dashboard) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for Lewiston city, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `static/lewiston-wards-2020.geojson` | The 7 wards drawn after the 2020 Census, with 2020 population (the sum of the census blocks inside each ward; 37,121 in all) | [City of Lewiston GIS, Wards - City Council](https://maps2.lewistonmaine.gov/arcgis/rest/services/Public/Wards_council/MapServer/0); population from the [U.S. Census Bureau](https://www.census.gov) (public domain) |

The School Committee posts its agendas and minutes in public Google Drive
folders, linked from the [school department's School Committee
page](https://www.lewistonpublicschools.org/en-US/school-committee-bc9f3846),
one folder per meeting. The engine doesn't read that layout yet; once it does,
those meetings appear in `meetings/meetings.json` too.
