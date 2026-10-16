# Adding a town

From an empty folder to a published site, in the network repository
(publick-org/publick.org). Written from adding Beverly, and used since for
Lawrence, Burlington, and the towns in publick.org #58; each step names where
the answer comes from, so a town the engine already reads takes an afternoon,
not weeks.

## Start with the helper

From this repository, with the engine checked out next to it:

```
PYTHONPATH=../publick-engine python -m pipeline.new_town <Town> <state> <city website URL>
```

It does steps 1 to 6 as far as public sources answer them, and marks the
rest for a person (the engine's `pipeline/new_town.py`):

- **Step 1:** whether the city's site is CivicPlus (Agenda Center, Archive
  Center, and its calendars, by name) or has a CivicClerk portal; two or
  three minutes files, and whether they're scans; SeeClickFix's places named
  for the town. It stops at a browser check, and at a meeting platform the
  engine doesn't read, and says so.
- **Steps 2 and 3:** the BLS series and the Census place in any state; in
  Massachusetts also the DLS name and DOR code, the DESE district, and the
  MassGIS ward file. Other states' own codes and wards are marked.
- **Step 4:** a skeleton only. A person fills in the officials from official
  pages.
- **Step 5:** the config, from the closest live town (the same meeting
  platform and state), with the colors from the city's stylesheet. No
  `[digest]`: that's step 8.
- **Step 6:** in a copy, so `data/` stays empty: a build with no data, four
  weeks of meetings fetched (`--full` for everything from `since`), a second
  build, the site checks, and `pipeline.listings`. Then the share image.

It writes `towns/<town>-<state>/` (the config, `data/static/` with the ward
file, the share image) and `new-town-<town>-<state>.md`, a report of what it
found, where each answer came from, and what's left. Everything left is a
`# To fill in:` comment in the config: work through them with the steps
below, deleting each as it's done. The town's site checks fail while any is
left. Then publish (step 7).

## 1. What the city uses

- [ ] **Meetings.** Open the city's website. A CivicPlus site (a "Powered by
      CivicPlus" footer) has an Agenda Center (`/AgendaCenter`, Malden and
      Beverly), a calendar with an Archive Center (`/Archive.aspx`,
      Gloucester), or both. Otherwise look for a CivicClerk portal
      (`<city>.portal.civicclerk.com`: Manchester, Burlington), a DotNetNuke
      calendar (Manchester), or a meetings calendar with one documents page
      for every board (Wallingford). Anything else (Govstack, Drupal, the
      Rhode Island Secretary of State's portal) needs a new reader in the
      engine first: stop here and make that its own piece of work. A reader is written once and works for every town on the
      same software.
- [ ] **Can the site be read automatically?** Fetch a listing page with
      `curl` and a User-Agent naming Publick. A site that answers with a
      browser check ("Just a moment…") blocks automated reading: ask the
      town to allow Publick's crawler. Never work around the check.
- [ ] **School Committee meetings.** Often posted somewhere else: the school
      district's website (Beverly, Malden, Wallingford) or public Google Drive
      folders (Gloucester), or in the city's Agenda Center with everything
      else. The engine reads Agenda Centers, Drive folders laid out one per
      committee, a Finalsite district's board posts, a district's calendar
      feed, a page of a board's dates, and a page that links each meeting's
      agenda and minutes (`[page_meetings]`: Methuen, Waltham, Nashua). Not
      yet: BoardDocs, Diligent
      Community, nested Drive folders; leave the board out and say so in the
      pull request.
- [ ] **Minutes.** Download two or three. A scanned PDF (no text to select)
      is transcribed by the model, which costs money every month; note how
      many pages a year that would be. Minutes as Word files aren't read.
- [ ] **311.** Search SeeClickFix for the city
      (`seeclickfix.com/api/v2/places?search=<City>`; the place may need its
      state, like `<city>_ma`). Many issues the city
      acknowledged means it uses SeeClickFix; a handful nobody answered means
      it doesn't. Cities on other systems (QAlert, Beverly's MyBeverly) have no
      public data: leave 311 out.
- [ ] **Building permits.** Only Gloucester's Data Hub file is read today.

## 2. The state's and the country's codes

For Massachusetts, below. For another state, start from a town's config in
that state (README, "Adding a town") and the state package's docstring in the
engine (`pipeline/states/<state>/__init__.py`), which lists its keys; the
Census and BLS steps are the same everywhere, with the state's own FIPS code.

- [ ] **DLS name and DOR code** (`[finance]`): in any file in the network
      repository's `states/ma/dls/`, the town's row ("DOR Code": "030",
      "Municipality": "Beverly").
- [ ] **DESE district** (`[schools]`):
      `educationtocareer.data.mass.gov/resource/n2xa-p822.json` with
      `$query=SELECT dist_code, dist_name WHERE dist_name like '%<Town>%'
      GROUP BY dist_code, dist_name`. Usually the DOR code followed by 0000.
- [ ] **Census place** (`[housing]`): the BLS area code below contains it
      (`CT25` + the 5-digit place FIPS). `census_geo` is `16000US25` + the
      place FIPS; `bps_place` is the place FIPS.
- [ ] **BLS series** (`[labor]`): `download.bls.gov/pub/time.series/la/la.area`
      (send a User-Agent with a contact address). The city's line is
      `CT25xxxxx000000`; the series is `LAU` + that + `03`.
- [ ] **Subsidized Housing Inventory**: `shi_name` as the state's PDF writes
      the town.

## 3. Wards

In Massachusetts, from MassGIS (below). Elsewhere, the city's own GIS
(Burlington), or the state's (NH GRANIT for Manchester, RIGIS for South
Kingstown's precincts). A town without wards, its seats all elected
townwide, uses its voting precincts for 311 (`areas = "precincts"`) and
shows no ward map; a town with neither (Bangor) has no 311 section yet.

- [ ] **Ward and precinct file**, for 311 and the Officials page: MassGIS
      Wards and Precincts (2022),
      `arcgisserver.digital.mass.gov/arcgisserver/rest/services/AGOL/WardsPrecincts2022/MapServer/0/query`
      with `where=TOWN='<TOWN>'`, `outFields=WARD,PRECINCT,WP_DISTRICT,POP_2020`,
      `outSR=4326`, `f=geojson`. Rename the properties to `ward`, `precinct`,
      `district`, `population_2020`, round coordinates to 6 places, and save
      it as `data/static/<town>-precincts-2022.geojson` with `name` and
      `source` set as in Malden's.

## 4. Elected officials

- [ ] **Mayor, council, school committee** from the city's and the school
      district's own pages, confirmed against the last municipal election's
      official results and the newest minutes listing members present. Never
      from news sites or memory.
- [ ] **Seats**: a ward seat gets `ward`; a citywide seat doesn't. A seat
      elected by a group of wards (Beverly's School Committee districts) gets
      `wards = [1, 2, 3]`.
- [ ] **Terms**: from the charter, or the city's page restating it. Leave
      `term_ends` out when no official source gives it.
- [ ] **Contact**: city- and school-issued email addresses only, and the
      mayor's office phone. Not the personal phones and home addresses some
      cities publish. Check each address as the page shows it: links can
      point to an old domain or a personal account, and printed lists can
      have typos. When two official pages disagree (a member's name, an
      address), use the body's own newest page or minutes.
- [ ] **Officers**: use the body's own titles (President or Chair).
- [ ] **Next election** (`[officials] next_election`): the date of the
      town's next regular municipal election, from the city's election
      calendar or its charter. A vacancy filled by a special election is
      said in the body's `note` until then.

## 5. The config

- [ ] Copy the config of a town with the same meeting system and state
      (Malden for an Agenda Center in Massachusetts), and change: `[site]`
      (name, domain `<town>-<state>.publick.org`, `contact_email`,
      `user_agent`), `[town]`, `[analytics] prefix`, `[storage] prefix`, the
      tables above, and `[freshness]` (drop 311 if the town has none).
      What every town shares, or every town in the state, isn't in a
      town's config: it's in `defaults/network.toml` and
      `defaults/states/<st>.toml` (README, "Adding a town"), picked by
      `[town] state_abbr`. Leave it out, or set the town's own value where
      it differs.
- [ ] **Colors** (`[site.colors]`): the most-used colors in the city
      website's stylesheet; each must reach 4.5:1 on white.
- [ ] **City calendar** (`[meetings.civicplus]`, for a CivicPlus city): the
      calendar read month by month, with `calendars` naming the city's
      calendar of public meetings ("City Meetings"), even when the Agenda
      Center has the agendas: an Agenda Center lists a meeting only once its
      agenda is posted. A meeting in both is shown once.
- [ ] **Board names** (`[meetings.aliases]`): only names the engine doesn't
      fix itself (it already turns "Health, Board of" round, and matches a
      calendar's "Open Space and Recreation Committee" or "Malden Cultural
      Council" to the Agenda Center's "Open Space & Recreation Committee" or
      "Cultural Council"). `python -m pipeline.listings` lists the meetings
      shown as one and why; a calendar meeting next to an Agenda Center one
      of the same day, not put together, needs an alias.
- [ ] **School board**: where the district lists its meetings, so they're
      shown before their agendas: its calendar feed (`[ical_meetings]`), a
      page of the year's dates (`[schedule_meetings]`, or `schedule_url` in
      `[finalsite_meetings]` or `[drive_meetings]`).
- [ ] **City or town** needs nothing: the first run records the Census
      Bureau's word for the place (`data/place.json`), and the site says "the
      city" or "the town" to match. Set `[town] kind` only to override it.
- [ ] **Council committees** (`[meetings.agenda_center.committees]`): list
      each committee by a phrase in its agenda titles. When titles name two
      ("Public Services/Committee of the Whole"), leave the shared one out so
      the committee's own name decides. A board name ending in "Meeting"
      makes titles read "… Meeting Meeting".
- [ ] **Sections**: only what the town has. No 311 section without 311 data.
- [ ] **Glossary**: the network's and the state's terms (`[terms]` in
      `defaults/`) are in every town's glossary already. Add a
      `[[glossary]]` entry, with its `definition`, only for a term of the
      town's own (its own offices and ordinances), or one it uses in another
      sense than the state's. A term every town in the state would need goes
      in the state's file instead, with its Spanish.
- [ ] **Spanish**: every town launches in English and Spanish (`[site]
      languages` in `defaults/network.toml`). Nothing else to do: the first
      runs draft the town's own text (tagline, boards, seats) and translate
      its summaries, each checked without AI and reviewed by a second AI
      model; anything that fails is shown in English. No person checks the
      Spanish, and the site says so. Role titles in Spanish use the generic
      form ("Vicepresidente"), since the holder changes.

## 6. Check before merging

- [ ] Build locally with the engine on `PYTHONPATH` and `PUBLICK_TOWN_DIR`
      set to the town's folder, with an empty `data/` (it must build), then
      after `python -m pipeline.fetch_meetings`: every board listed under its
      usual name, committees under their own boards, no errors.
- [ ] `python -m pytest ../publick-engine/site_checks` on the build.
- [ ] Read the first summaries of the main board's meetings before
      announcing the site. Each summary is also checked against its
      document's own text (the engine's `pipeline/factcheck.py`): `python -m
      pipeline.factcheck` with `PUBLICK_TOWN_DIR` set lists anything not found.

## 7. Publish

- [ ] Pull request adding `towns/<town>-<state>/` (config, empty `data/`
      with the ward file in `data/static/`, share image). Its run builds and
      checks the town.
- [ ] Merge, then **Actions → Network → Run workflow** for the town, fetching.
      No DNS change; the homepage lists the town under its state by itself.
      A run collects up to 60 minutes; run it again until none are waiting.
      Its older documents get a small share of the summary budget each run;
      to summarize its first months in a day, set **catch_up** (dollars, e.g.
      3) on a manual run. Only meetings from `[summaries] since` on are
      summarized: set it to the first of the month about three months before
      launch, so the town's history doesn't take the month's budget (older
      meetings keep their records and documents). The month's budget and the town's own limit per
      run still apply.
- [ ] Nothing for email: a catch-all rule in Cloudflare's Email Routing
      forwards every `@publick.org` address, the site's `contact_email`
      among them.
- [ ] Add the town to the README's "Keeping officials current" election
      dates if they differ.

## 8. A week after launch

- [ ] **Weekly digest by email**, once the town has a full week of
      meetings to send: add an empty `[digest]` table to its config (the
      signup's settings are in `defaults/network.toml`), and add
      `<town>-<state>.publick.org` to
      `DIGEST_TOWNS` in `wrangler.scheduler.toml`. Once that's merged, run
      **Actions → Worker**: it also makes the town's Buttondown tag,
      `<town>-<state>-en`.
