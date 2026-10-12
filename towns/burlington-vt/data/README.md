# Data

Collected daily by the network's workflow (`.github/workflows/network.yml` in
this repository). Records are never deleted; changes over time are kept in
each record and in git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting since April 2026: board, title, date, time, place, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen, including revised agendas | The city's [CivicClerk portal](https://burlingtonvt.portal.civicclerk.com) (public records) |
| `meetings/status.json` | When the portal was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes (PDF) | Each agenda (upcoming meetings) and set of minutes as the city posted it, kept in the network's documents bucket at `files.publick.org/burlington-vt/` rather than in git | City of Burlington CivicClerk portal (public records) |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes, and their Spanish translations, each checked against its document and labeled as AI-generated on the site | Publick, from the documents above |
| `311/requests.json` | One record per public SeeClickFix request in the city's own request types ("Burlington, VT"): category, location, ward, council district, status, and submitted/acknowledged/closed/reopened times. No descriptions, photos, or reporter details | [SeeClickFix](https://seeclickfix.com), [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/) |
| `311/scorecard.json` | Metrics shown on the 311 page, recomputed daily | Derived from `311/requests.json`; same license |
| `finance/tax_bill.json` | Average homestead tax bill by tax year, calculated by Publick from the state's tax rates and the homestead values in the statewide parcel data | [Vermont Department of Taxes, PVR Annual Report](https://tax.vermont.gov/pvr-annual-report), [VCGI statewide parcel data](https://geodata.vermont.gov/datasets/vt-data-statewide-standardized-parcel-data-parcel-polygons) (public records) |
| `finance/budget.json` | Tax rates (homestead and nonhomestead education, municipal) with the median of Vermont's towns, what the property tax raised by part, the grand list, and property tax per resident with the state median | [Vermont Department of Taxes, PVR Annual Report](https://tax.vermont.gov/pvr-annual-report); [Census population estimates](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html) (public records) |
| `schools/schools.json` | Graduation rate, chronic absenteeism, and state test results (VTCAP) for Burlington School District and the state, by year, and the district's budget and education spending per pupil | Vermont Agency of Education: [Vermont Education Dashboard data on data.vermont.gov](https://data.vermont.gov), [per pupil spending report](https://education.vermont.gov/accountability-data/financial-reports/per-pupil-spending) (public records) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org) (public records) |
| `labor/unemployment.json` | Monthly unemployment rate for Burlington city, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `static/burlington-wards-2024.geojson` | The 8 wards in effect since March 2024 (the city's 2022 redistricting, in the charter since 2023), each with its council district (East: Wards 1 and 8; Central: 2 and 3; South: 5 and 6; North: 4 and 7) and 2020 census population: the sum of the census blocks inside each ward, 44,743 in all, the city's 2020 count. The redistricting cut a few blocks between wards, most of them on and near the UVM campus; those blocks' people are divided by the share of the block's area in each ward, so Wards 1, 6, and 8 are estimates (Ward 6's most of all) | [City of Burlington GIS, City Wards 2024](https://maps.burlingtonvt.gov/arcgis/rest/services/City_Wards_2024/MapServer/0); population from the [U.S. Census Bureau](https://www.census.gov), 2020 census blocks through [TIGERweb](https://tigerweb.geo.census.gov) (public domain) |

Data derived from SeeClickFix is shared under the same CC BY-NC-SA 3.0 license,
with attribution to seeclickfix.com.

The ward file's coordinates are rounded to 6 decimal places. Its population is
Publick's sum, not the city's: the GIS layer's own population field (`total`)
adds up to 40,299, not the city's 44,743, and looks left over from a draft of
the plan, so it isn't used.

What Publick makes here (the summaries and translations, and figures it
calculates) is under CC BY 4.0, with credit; the repository's `LICENSE` says
how, and what keeps its own terms.
