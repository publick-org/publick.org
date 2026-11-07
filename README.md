# publick.org

The Publick network: the publick.org homepage and every town's site, run
from this one repository with the [Publick engine](https://github.com/publick-org/publick-engine)
at the version in `engine-version`.

```
LICENSE                       What may be reused and how: CC BY 4.0 for what Publick makes, the credit line,
                              and what keeps its own terms (311, public records); the code is MIT
LICENSE-CC-BY-4.0.txt         The CC BY 4.0 legal text
engine-version                The engine release every town runs, an exact tag; moved each morning by engine.yml
ADDING-A-TOWN.md              The checklist for adding a town, from an empty folder to its first published site
home/                         The publick.org homepage (index.html) and the page for a state with many towns
                              (state.html); their town lists are filled in by scripts/build_home.py
towns/<town>-<state>/         One folder per town, laid out as a town repository is:
  config/<town>.toml            everything town-specific, over the settings in defaults/
  data/                         collected data, committed by the daily run, with run.json (its last
                                daily run); a 311 town's requests and scorecard are kept in the documents
                                bucket instead (below), and what its AI summaries cost
                                in the private store (below), never in git
  site/static/                  files that replace or add to the engine's (the share image)
defaults/network.toml         The settings every town shares ([summaries] model and prices, the documents bucket,
                              GoatCounter, 311 and digest settings), under each town's own config (below)
defaults/states/<st>.toml     The settings every town in a state shares (its name, Census and BLS codes, the
                              glossary of its civic terms and laws, in each language)
states/ma/                    Statewide sources, fetched once for every town: Massachusetts's DLS reports (other
                              states' figures are saved in the engine, or fetched by each town)
wrangler.toml                 The Worker that serves every site from the sites bucket
wrangler.scheduler.toml       The Worker that starts the daily runs on time, and checks every site loads, hourly
scripts/import-town.sh        Copies a town's own repository into towns/ (how the first three towns moved in)
scripts/build_home.py         Writes the homepage's town lists, by state (each state's towns' names, linking their
                              sites), with the network's counts (from each town's data/run.json), and a page for each
                              state with 10 or more towns, with each town's meetings this week (the homepage names 8
                              of its towns and a last item, "+ 4 more", leads to the page; from 150 towns, the
                              homepage lists only the states, and every state has a page); and the
                              network's sitemap.xml (an index of the homepage's and
                              every town's sitemaps) and robots.txt
scripts/build_status.py       Writes the network status page, publick.org/status/
scripts/make_share_image.py   Draws home/share/publick.png, the homepage's card on Substack and social media
.github/workflows/network.yml The daily runs, and builds on push and pull request
.github/workflows/engine.yml  Moves engine-version to each new engine release once the towns pass on it
.github/workflows/add-town.yml Adds a town, by hand: the engine's helper and a draft pull request with its report, then,
                              once that's merged, the town's first fetching runs (ADDING-A-TOWN.md)
.github/workflows/evaluate.yml Runs the engine's minutes or translation prompt against the real model before a prompt change
                              ships, or the minutes as a batch at each effort, to measure the Batches API (by hand)
.github/workflows/worker.yml  Deploys the Workers: the scheduler by itself when engine-version moves to an engine whose
                              scheduler changed, or wrangler.scheduler.toml changes; the sites Worker only by hand (an
                              engine whose sites Worker changed opens an issue asking for it)
```

## How it runs

Every site is built into the sites bucket (Cloudflare R2) and served by one
Worker, which picks the site by hostname: `gloucester-ma.publick.org` is
`towns/gloucester-ma`, and `publick.org` is `home/`. See the engine's
`pipeline/deploy.py` and `worker/index.js`.

- **Daily**, started every hour from 09:05 to 14:05 UTC by the
  `publick-scheduler` Worker (`wrangler.scheduler.toml`), with one GitHub
  schedule (12:17 UTC) as a backup, since GitHub starts those late or not at
  all. Each start takes the towns that are due (their last fetching run,
  daily or by hand, finished more than `DUE_HOURS`, 18, ago), oldest first; a start with nothing
  due does nothing, and the next start makes up a missed one.
  - The statewide job fetches the sources a state's towns share, once for all
    of them, into `states/`: Massachusetts's DLS reports, only when a report
    isn't saved or is over a week old.
  - Each town then fetches its own new data, is built and checked, published
    if the checks pass, and its data committed as soon as it's done. Towns run
    in batches of four per job (more, past `MAX_JOBS`, 100 jobs), up to ten jobs at a time, the slow ones spread
    over the jobs by how long each took last time. Daily runs, runs by hand
    that fetch, and pushes to `main` give the accessibility checks a sample of
    each town's pages (every hand-written page, and the first and largest of
    each kind of record page); pull requests and rebuilds by hand without
    fetching check every page.
  - AI summaries and translations share one monthly budget, the secret
    `SUMMARY_BUDGET` (a month can have its own in the secret `SUMMARY_BUDGET_MONTH`):
    each run gives each of its towns a share of what's left, new documents first.
    What each town spends is kept in the private store, a bucket nothing serves
    (the engine's docs/storage.md, Cost records), not in git; the run's `budget` job reads
    it, and prints how much of the budget is used and each town's share as
    fractions, never as amounts, since the run logs are public. A manual run's
    `catch_up` is a percent of the month's budget.
  - A run that fetches sends each town's summaries as one batch, at half the
    price, and publishes the town without them. After each of the job's
    towns, the earlier towns' batches that have ended are collected and those
    towns published again (commit "Add summaries for <town>"); once the job's
    towns are done, it waits for the rest, sends one at a time whatever a batch
    didn't make or hadn't finished half an hour after it was sent, and
    publishes those towns again. A batch a job couldn't collect is collected by
    the town's next run. Pull requests and rebuilds send none.
- **311 data** (since engine v1.51.0, publick-engine#115 and #121):
  a 311 town's `data/311/requests.json` and `scorecard.json`, most of what
  the repository grew by, are kept in the documents bucket under
  `<town>-<state>/data/311/`, read from its public address by any build and
  saved back by the daily run; git keeps `311/status.json`. The daily run of
  2026-10-13 saved every 311 town's there, and `.gitignore` has kept them
  out of git since (their history stays). A new 311 town's first run saves
  its files to the bucket from whatever its pull request committed, such as
  a backfill (`fetch_311 --backfill`), and the bucket's copy wins after that.
- **On push to `main`:** rebuilds and publishes the towns the push touched (every
  town when `engine-version` or a workflow changed), records that in their run
  records, and rebuilds the homepage and status page. Data isn't fetched.
- **The engine, once a day, by itself** (`engine.yml`, 08:40 UTC): the
  scheduler Worker starts the engine's release at 08:20 and this at 08:40
  (GitHub's own schedules for both are a late backup). After the release, it opens a pull request moving `engine-version` to
  it, waits for that pull request's run to build and check every town (every
  page of the canaries, the fewest towns with every kind of town between them,
  and a sample of the rest), and merges it if every town passes; the merge
  publishes them. A run that fails has its failed jobs run once more. If a few
  towns still fail (at most one in 20, and at least one), it merges anyway and
  holds them back: each keeps the site it has, and an issue (label
  `engine held back`) names them. If more fail, or anything but a town, the
  pull request stays open, the towns stay where they are, and the failed
  workflow emails the owner. So the towns take at most one new engine a day,
  and only one that passed on nearly all of them. For an
  urgent fix, release the engine now (its **Actions → Release → Run
  workflow**) and run **Actions → Engine**.
- **On a pull request:** builds and checks the towns it touches. Nothing is published.
- **The weekly digest**, each Sunday at 7 AM in the town's time, from the
  issue each town's Saturday run builds (its Sunday run, if Saturday's
  didn't publish): the scheduler Worker emails each town in its `DIGEST_TOWNS`
  (`wrangler.scheduler.toml`) its newest issue through Buttondown, to that
  town's readers alone. The signup form on a town's `/digest/` page (its
  config's `[digest] signup`) posts to the sites Worker, which passes the
  address on to Buttondown, within the `SIGNUP_LIMITER` rate limit
  (`wrangler.toml`). A new town joins a full week after its launch, not at
  launch (ADDING-A-TOWN.md, step 8): its `[digest]` table, its place in
  `DIGEST_TOWNS`, then **Actions → Worker**, which makes its Buttondown tag. A run makes two requests for each town and two more. See the engine's docs/site.md,
  Weekly digest.
- **By hand** (**Actions → Network → Run workflow**): tick **daily** for a daily
  run, as the scheduler starts; or any towns, with or without fetching; with no
  towns named, every town and the homepage.

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
published site, is [ADDING-A-TOWN.md](ADDING-A-TOWN.md). It starts with the
engine's helper, `python -m pipeline.new_town <Town> <state> <city website
URL>`, which writes the town's folder with everything left for a person
marked `# To fill in:`. In short:

Add `towns/<town>-<state>/` with its `config/<town>.toml` (start from the
engine's `tests/fixtures/town/config/gloucester.toml` and its docs/configuration.md), an
empty `data/`, and optionally `site/static/share/<town>.png`. Set
`[site] domain` to `<town>-<state>.publick.org` and `[town] state_abbr` to
the state's code. Add an `[analytics]` table with `prefix` set to the town's
folder, so its page views count apart on the network's GoatCounter site, and a
`[storage]` table with `prefix` set to the town's folder too (it defaults to
the config file's name). Its
`contact_email`, `<town>-<state>@publick.org`, needs no rule of its own: the
catch-all rule in Cloudflare Email Routing forwards it.
Merge, then run the workflow for the town by hand to fetch its data (set
`catch_up` to a few percent of the month's budget to summarize its first
months' documents in that run, within the town's share). No DNS
change is needed: the homepage lists the town under its state on its own, and links the state's own page, with
a card for each town, once the state has 10 towns.

What every town shares is in `defaults/network.toml`, and what every town in
a state shares in `defaults/states/<st>.toml`: the footer's network name and
link, the GoatCounter site, the documents bucket, the summaries' model and
prices, the 311 and digest settings, the state's name and codes, and the
glossary. A town's config leaves them out and takes them from there; a value
it sets itself wins. A table there fills in the town's table of the same name
only when the town has it (an empty `[digest]` turns the signup on).

The glossary is `[terms]`: the civic terms that read the same everywhere in
`defaults/network.toml` (consent agenda, variance, town meeting, warrant
article), and each state's laws and words in its file (Massachusetts's free
cash and Order of Conditions, New Hampshire's non-public session), the
state's winning. Each term has a column for each language, its wording there
and its definition; another language is another column. Every town gets them
all: its glossary page, the definitions on its meeting pages, and the words
its translator is given and checked against (the engine's
`pipeline/glossary.py`). A town's own `[[glossary]]` entries are only what
means something of its own there (Nashua's ordinance numbers, Gloucester's
Retirement Board warrant), and win over a term of the same name. The engine's `pipeline/config.py`
checks both files (its docs/network.md, "Settings shared by a network's towns"), and

```
PYTHONPATH=../publick-engine PUBLICK_TOWN_DIR=towns/<town>-<state> python -m pipeline.config show
```

prints a town's config with the file each value came from. A change to
`defaults/network.toml` rebuilds every town, and one to a state's file that
state's towns.

The town's tax, budget, and school figures come from its state, through the
engine's package for that state (the engine's docs/states.md): its
`[finance]` and `[schools]` tables take that state's keys. Every New England
state has a package. Start from a town in the same state: Gloucester or Malden
for Massachusetts, Manchester for New Hampshire, Wallingford for Connecticut,
Burlington for Vermont, Lewiston or Bangor for Maine, South Kingstown for
Rhode Island; Lowell for a Massachusetts city whose Agenda Center has every
board and no calendar; Nashua for a New Hampshire city on CivicClerk. Portland
for a city whose areas are council districts (`[town] areas`), and Methuen,
Waltham, or Nashua for a school board whose district posts its agendas and
minutes on one page of links (`[page_meetings]`). A town in a state the engine has
no package for leaves those tables and the budget and schools sections out; it
still gets meetings, 311, unemployment, and housing. List each source in its `[freshness]` table, so the
status page shows it.

Add the `officials` section and an `[officials]` table (the engine's
docs/configuration.md): the mayor, the council, and the school committee, from official
city and school websites, with `checked` set to the day you checked them. Use
only city- or school-issued email addresses and the mayor's office phone, not
personal numbers the city may also publish. Give a member a `ward` only if
the seat is elected by that ward, and `wards` if it's elected by several (a
district of wards, as on Beverly's School Committee).
