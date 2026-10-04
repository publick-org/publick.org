# publick.org

The Publick network: the publick.org homepage and every town's site, run
from this one repository with the [Publick engine](https://github.com/publick-org/publick-engine)
at the version in `engine-version`.

```
LICENSE                       What may be reused and how: CC BY 4.0 for what Publick makes, the credit line,
                              and what keeps its own terms (311, public records); the code is MIT
LICENSE-CC-BY-4.0.txt         The CC BY 4.0 legal text
engine-version                The engine release every town runs, e.g. v1.30.0; moved each morning by engine.yml
ADDING-A-TOWN.md              The checklist for adding a town, from an empty folder to its first published site
RUNBOOK.md                    What to do when something needs a person: each morning's checks, alerts, rollback
home/                         The publick.org homepage (index.html) and the page for a state with many towns
                              (state.html); their town lists are filled in by scripts/build_home.py
towns/<town>-<state>/         One folder per town, laid out as a town repository is:
  config/<town>.toml            everything town-specific
  data/                         collected data, committed by the daily run, with run.json (its last
                                daily run) and summary-costs.json (its AI summaries' cost, by month)
  site/static/                  files that replace or add to the engine's (the share image)
states/ma/                    Statewide sources, fetched once for every town: Massachusetts's DLS reports
wrangler.toml                 The Worker that serves every site from the sites bucket
wrangler.scheduler.toml       The Worker that starts the daily runs on time
scripts/import-town.sh        Copies a town's own repository into towns/
scripts/build_home.py         Writes the homepage's town lists, by state, with the network's counts (from each
                              town's data/run.json), and a page for each state with 10 or more towns; and the
                              homepage's sitemap.xml and robots.txt
scripts/build_status.py       Writes the network status page, publick.org/status/
scripts/make_share_image.py   Draws home/share/publick.png, the homepage's card on Substack and social media
.github/workflows/network.yml The daily runs, and builds on push and pull request
.github/workflows/worker.yml  Deploys both Workers (by hand)
```

## How it runs

Every site is built into the sites bucket (Cloudflare R2) and served by one
Worker, which picks the site by hostname: `gloucester-ma.publick.org` is
`towns/gloucester-ma`, and `publick.org` is `home/`. See the engine's
`pipeline/deploy.py` and `worker/index.js`.

- **Daily**, started every hour from 09:05 to 14:05 UTC by the
  `publick-scheduler` Worker (`wrangler.scheduler.toml`), with one GitHub
  schedule (12:17 UTC) as a backup, since GitHub starts those late or not at
  all. Each start takes the towns that are due (their last daily run
  finished more than `DUE_HOURS`, 18, ago), oldest first; a start with nothing
  due does nothing, and the next start makes up a missed one.
  - The statewide job fetches the sources a state's towns share, once for all
    of them, into `states/`: Massachusetts's DLS reports, only when a report
    isn't saved or is over a week old.
  - Each town then fetches its own new data, is built and checked, published
    if the checks pass, and its data committed. Towns run in batches of four
    per job, up to ten jobs at a time. Daily runs give the accessibility checks
    a sample of each town's pages (every hand-written page, and the first and
    largest of each kind of record page); every other run checks every page.
  - AI summaries and translations share one budget, `SUMMARY_BUDGET` ($80 a
    month, decided 2026-10-03; a month can have its own in `SUMMARY_BUDGET_MONTH`): each run gives each of its towns a share of what's left, new
    documents first.
- **On push to `main`:** rebuilds and publishes the towns the push touched (every
  town when `engine-version` or a workflow changed), records that in their run
  records, and rebuilds the homepage and status page. Data isn't fetched.
- **The engine, once a day, by itself** (`engine.yml`, 08:40 UTC): the
  scheduler Worker starts the engine's release at 08:20 and this at 08:40
  (GitHub's own schedules for both are a late backup). After the release, it opens a pull request moving `engine-version` to
  it, waits for that pull request's run to build and check every page of
  every town, and merges it if every town passes; the merge publishes them.
  If a town fails, the pull request stays open, the towns stay where they
  are, and the failed workflow emails the owner. So the towns take at most
  one new engine a day, and only one that passed on all of them. For an
  urgent fix, release the engine now (its **Actions → Release → Run
  workflow**) and run **Actions → Engine**.
- **On a pull request:** builds and checks the towns it touches. Nothing is published.
- **By hand** (**Actions → Network → Run workflow**): tick **daily** for a daily
  run, as the scheduler starts; or any towns, with or without fetching; with no
  towns named, every town and the homepage.

## Alerts

A daily run doesn't fail when a town does; its data is still committed. Instead,
one GitHub issue, **Towns need attention** (label `towns behind`, assigned to
`ALERT_ASSIGNEE` in `network.yml`), is opened when a town has had no good
update (published, with fresh data) for 30 hours, or a figure source's checks
keep failing, or a state's statewide checks have failed three times in a row.
Each daily run updates it and closes it when every town is caught up. An edit
sends no email, so the run also comments with the towns newly behind (from
`python -m pipeline.network behind --new-since`); a town already listed, or
one that's caught up, sends nothing. If the daily runs stop altogether, the scheduler opens
**The network's daily runs have stopped** (label `network stopped`) after 30
hours, and closes it when a run finishes. A pull request's run still fails when
a town does, so a broken site can't be merged.

## Status page

[publick.org/status/](https://publick.org/status/) is public, for the
towns' readers: whether each site's data is up to date, when each data source
(its config's `[freshness]` table) last updated, and which data a failed or
missed update affects, in plain words. It leaves out the run's internals
(commands, errors, timings), which stay in the run's summary on GitHub Actions
and its email. Each run that fetches a town's data writes the result to the
town's `data/run.json`, committed with the data; after the run's towns finish,
the homepage is rebuilt from `main` with the status page
(`scripts/build_status.py`) and published. A site shows "some data delayed"
when a step of its last run failed or a source is behind, and "not updated"
after 30 hours with no daily run. It never shows what running the network
costs or how much data it keeps.

## Adding a town

The step-by-step checklist, from finding what the city uses to the first
published site, is [ADDING-A-TOWN.md](ADDING-A-TOWN.md). In short:

Add `towns/<town>-<state>/` with its `config/<town>.toml` (start from the
engine's `tests/fixtures/town/config/gloucester.toml` and its README), an
empty `data/`, and optionally `site/static/share/<town>.png`. Set
`[site] domain` to `<town>-<state>.publick.org` and `network_url` to
`https://publick.org`, which links the network's name in every page footer.
Add an `[analytics]` table with `goatcounter = "publick"` and `prefix` set to
the town's folder, so its page views count on the network's GoatCounter site.
Merge, then run the workflow for the town by hand to fetch its data (set
`catch_up` to a few dollars to summarize its first months' documents in that
run, within the month's budget). No DNS
change is needed: the homepage lists the town under its state on its own, and gives the state its own page once it has 10
towns.

The town's tax, budget, and school figures come from its state, through the
engine's package for that state (the engine README's States section): its
`[finance]` and `[schools]` tables take that state's keys. Start from a town in
the same state: Gloucester or Malden for Massachusetts, Manchester for New
Hampshire. A town in a state the engine has no package for leaves those tables
and the budget and schools sections out; it still gets meetings, 311,
unemployment, and housing. List each source in its `[freshness]` table, so the
status page shows it.

Add the `officials` section and an `[officials]` table (the engine README's
config table): the mayor, the council, and the school committee, from official
city and school websites, with `checked` set to the day you checked them. Use
only city- or school-issued email addresses and the mayor's office phone, not
personal numbers the city may also publish. Give a member a `ward` only if
the seat is elected by that ward, and `wards` if it's elected by several (a
district of wards, as on Beverly's School Committee).

## Keeping officials current

Each town's `[officials]` table is kept by hand. Check every town's members
against the city and school websites after each municipal election (the next
for Beverly, Gloucester, Lawrence, Malden, Manchester, and Wallingford is November
2027; new terms start in January 2028), and whenever a seat changes between elections (a resignation,
an appointment to fill a vacancy, new council or committee officers). Update
the members and `checked` in one pull request.

## Checking meetings by hand

About once a week while towns are added, compare each town's upcoming
meetings with its city's own calendar, Agenda Center or portal, and school
district site (decided 2026-10-02: this stays by hand). With the engine on
`PYTHONPATH` and `PUBLICK_TOWN_DIR` set to the town's folder:

- `python -m pipeline.listings` lists the meetings shown as one and why. A
  calendar meeting beside an Agenda Center one of the same board and day
  that isn't put together means the two name the board differently: add the
  calendar's name to `[meetings.aliases]`.
- A meeting the city posted after the morning's run comes in on the next.
- Where the city's own listing is wrong (an entry left over from a board's
  old schedule, a typo in a time), add a `[[meetings.corrections]]` entry
  with the reason, a link to the evidence and the date checked. It can go
  up in English: the next run drafts its Spanish, and a translation in
  `[strings.es]` is used instead when there is one. Manchester's Arts Commission entry for
  November 9, 2026 is the first. The engine's README says what each field
  does; a correction comes down by itself when the city changes the listing.

## New Hampshire's yearly figures

New Hampshire's tax rates and school figures come from statewide files the
engine saves once a year, because the state's websites refuse automated
requests. When the status page shows "New Hampshire state figures (yearly)" as
behind for a New Hampshire town, download the new files in a browser and run
the engine's `python -m pipeline.states.nh.extract` (the engine README, New
Hampshire's yearly figures) and merge that to the engine. The next morning's
release and engine move (`engine.yml`) take it to every New Hampshire town.

## Moving a town in from its own repository

1. Turn off the town repository's schedule (**Actions → Update and deploy → Disable workflow**).
2. `scripts/import-town.sh <town>-<state>` to copy its latest config, data, and
   static files into `towns/`, then commit and merge.
3. Delete the town's `CNAME` record in Cloudflare DNS, so the wildcard record sends it to the Worker.
4. Once the site is up from here, remove the custom domain from the old
   repository's Pages settings and archive the repository.

## Rolling back

With the sites bucket's keys set (below), from a checkout of the engine:

```sh
python -m pipeline.deploy rollback --domain gloucester-ma.publick.org                  # the build before
python -m pipeline.deploy rollback --domain gloucester-ma.publick.org --build <build>
```

To go back to an older engine for every town, set `engine-version` to the
earlier release and merge.

## Setup, once

In the Cloudflare account that holds `publick.org`:

1. **R2 → Create bucket** `publick-sites`, with no public address.
2. **R2 → Manage API tokens → Create Account API token** with *Object Read & Write*
   on `publick-sites` only.
3. **My Profile → API Tokens → Create Token** from the *Edit Cloudflare Workers*
   template, limited to this account and the `publick.org` zone, for deploying the Worker.
4. **DNS:** proxied (orange cloud) `AAAA` records for `*` and for `@`, both to
   `100::`. The address is never reached; the Worker answers first. Remove the
   GitHub Pages `A` records for `@`, and each town's `CNAME` as it moves.
5. **Workers Routes:** any other hostname under `publick.org` that must not
   reach the Worker needs a route with **no Worker**, such as
   `files.publick.org/*` (the documents bucket).

In this repository's **Settings → Secrets and variables → Actions**:

| Secret | What |
|---|---|
| `SITES_ENDPOINT` | `https://<account id>.r2.cloudflarestorage.com` |
| `SITES_BUCKET` | `publick-sites` |
| `SITES_ACCESS_KEY_ID`, `SITES_SECRET_ACCESS_KEY` | The R2 token from step 2 |
| `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` | The token from step 3, and the account ID |
| `ANTHROPIC_API_KEY`, `BLS_API_KEY`, `STORAGE_ACCESS_KEY_ID`, `STORAGE_SECRET_ACCESS_KEY` | As for a town repository (engine README, Secrets) |
| `ENGINE_PR_TOKEN` | For `engine.yml`, which moves the engine each day: a fine-grained personal access token with resource owner `publick-org`, this repository only, and **Contents** and **Pull requests** read and write. Required: what the workflow's own token pushes, opens, or merges starts no other workflow, so the pull request wouldn't be checked and the merge wouldn't publish. It expires; replace it before it does (until then the engine doesn't move, and the workflow's failure emails the owner) |
| `SCHEDULER_GITHUB_TOKEN` | For the scheduler Worker: a fine-grained personal access token with resource owner `publick-org`, for this repository with **Actions** and **Issues** read and write, and for `publick-engine` with **Actions** read and write (widened 2026-10-03, so the scheduler can start the engine's release). It expires (the current one, made 2026-09-30, about 2027-10-01); replace it (then run **Actions → Worker**) before it does. Until then, runs fall back to GitHub's own schedule |

The scheduler's Cron Triggers also need the Cloudflare account to have a
`workers.dev` subdomain: opening **Workers & Pages** in the dashboard once
creates it. The Workers don't use it; both have `workers_dev = false`.

Then turn off GitHub Pages for this repository (**Settings → Pages**), and
run **Actions → Worker**.
