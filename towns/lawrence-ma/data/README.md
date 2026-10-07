# Data

Collected daily by the network's workflow (`.github/workflows/network.yml` in
this repository). Records are never deleted; changes over time are kept in
each record and in git history.

| Path | Contents | Source and license |
|---|---|---|
| `meetings/meetings.json` | One record per public meeting since January 2026: board, date, status (cancelled, removed), links to its agenda and minutes, and every change since it was first seen, including revised agendas | The city's [Agenda Center](https://www.cityoflawrence.com/AgendaCenter) (public records) |
| `meetings/status.json` | When the Agenda Center was last checked, for the site and the stale-data alert | Derived |
| Agendas and minutes (PDF) | Each agenda (upcoming meetings) and set of minutes as the city posted it, kept in the network's documents bucket at `files.publick.org/lawrence-ma/` rather than in git | City of Lawrence Agenda Center (public records) |
| `summaries/`, `summaries/es/` | AI-written summaries of agendas and minutes, and their Spanish translations, each checked against its document and labeled as AI-generated on the site | Publick, from the documents above |
| `finance/tax_bill.json` | Average single-family tax bill, recent fiscal years | [Mass. Division of Local Services, Municipal Databank](https://dls-gw.dor.state.ma.us/reports/rdPage.aspx?rdReport=AverageSingleTaxBill.SingleFamTaxBill_wRange) (public record) |
| `finance/budget.json` | General fund spending by function, revenue by source, levy and levy limit, free cash, stabilization fund, bond ratings, and spending per resident with the state median | [Mass. Division of Local Services, Municipal Databank](https://dls-gw.dor.state.ma.us/reports/rdPage.aspx?rdReport=ScheduleA.GenFund_MAIN) (public record) |
| `housing/housing.json` | New homes permitted by year; home value, rent, and rent burden with margins of error; Subsidized Housing Inventory share; residential parcels by type | [Census Building Permits Survey](https://www.census.gov/construction/bps/), [American Community Survey via Census Reporter](https://censusreporter.org), [EOHLC Subsidized Housing Inventory](https://www.mass.gov/info-details/subsidized-housing-inventory-shi), [Mass. DLS](https://dls-gw.dor.state.ma.us/reports/rdPage.aspx?rdReport=PropertyTaxInformation.LA4.Parcel_counts_vals) (public records) |
| `schools/schools.json` | Graduation rate, chronic absenteeism, and MCAS results (grades 3–8) for Lawrence Public Schools and the state, by year | [DESE, Education-to-Career data hub](https://educationtocareer.data.mass.gov) |
| `labor/unemployment.json` | Monthly unemployment rate for Lawrence city, with the statewide rate | [BLS Local Area Unemployment Statistics](https://www.bls.gov/lau/) (public domain) |
| `static/lawrence-precincts-2022.geojson` | The 6 wards (A to F) and 24 precincts, with 2020 population (89,143 in all) | [MassGIS, Wards and Precincts (2022)](https://gis.data.mass.gov/maps/aec5130790814ace94438d3bcf23cf9a) |

What Publick makes here (the summaries and translations, and figures it
calculates) is under CC BY 4.0, with credit; the repository's `LICENSE` says
how, and what keeps its own terms.
