# Runbook

What to do when something needs a person: each morning's checks, what each
alert means, and how to fix or roll back. The README says how the network
works; this says what to do.

Times are UTC. Eastern is UTC−4 in summer, UTC−5 in winter.

## Who has access

| Service | What it holds | Owners |
|---|---|---|
| GitHub, `publick-org` | Both repositories, their secrets, Actions | NasTber |
| Cloudflare | `publick.org` DNS, both Workers, the R2 buckets (`publick-sites`, `publick-documents`), email routing | NasTber |
| Anthropic | The API key, its spending and rate limits | NasTber |
| GoatCounter | The `publick` page-view site | NasTber |
| Buttondown | The weekly digest's email: its readers, and sending from `hello@digest.publick.org` (DNS records on `digest.publick.org`) | NasTber |

## Each morning

| When | What | Started by |
|---|---|---|
| 08:20 | The engine's release: everything merged to the engine's `main` since the last release, if its tests passed | The scheduler Worker (GitHub's schedule is a late backup) |
| 08:40 | `engine.yml`: a pull request moving `engine-version` to that release, checked on every page of every town, merged if all pass | The scheduler Worker |
| 09:05 to 14:05, hourly | `network.yml` daily runs: each start takes the towns that are due | The scheduler Worker; GitHub's 12:17 is a backup |
| Sundays, 5:30 PM Eastern | Each town in `DIGEST_TOWNS` (`wrangler.scheduler.toml`) emailed its weekly digest; a failure opens **The weekly digest didn't send** | The scheduler Worker, checking hourly on Sundays and Mondays (UTC) |

So anything merged to the engine's `main` before 08:20 goes to every town
that morning, if every town passes on it. Merge engine changes after the
morning's engine pull request has merged (about 09:15) to give them a day on
`main` before they ship. Anything merged to this repository is live at once:
a push run publishes the towns it touches (every town for `engine-version`
or a workflow change), and a workflow change applies to the next run.

**Check, in this order:**

1. **The engine pull request** (titled "Engine vX.Y.Z"): merged by itself, or
   still open with a failed run. The workflow's failure emails the owner.
2. **[publick.org/status/](https://publick.org/status/)**: every town
   "Up to date" after the last daily start, about 14:30.
3. **The "Towns need attention" issue** (label `towns behind`): open means a
   town has had no good update in 30 hours, a figure source keeps failing, or
   a state's statewide fetch failed three times in a row. Each new town
   behind gets a comment, which emails.
4. **The month's spending**: the plan job of a daily run prints the budget
   (`pipeline.network budget`), or add up `towns/*/data/summary-costs.json`
   for the month.

## When something's wrong

### The engine pull request failed

The towns stay on the engine they have; nothing's broken for readers.

1. Open the failed pull request's run (`network.yml`, event
   `pull_request`) and find the town and check that failed.
2. If the engine is at fault, fix it in the engine with a pull request. The
   next morning's release and engine pull request take the fix; to move
   today, run the engine's **Actions → Release → Run workflow**, then this
   repository's **Actions → Engine → Run workflow**.
3. If the failure is a site's (a city's page changed, a document went
   missing) and not the engine's, fix that town's config, or merge the
   engine pull request by hand once you're sure the failure isn't the
   engine's.
4. If the engine pull request didn't open at all, check that
   `ENGINE_PR_TOKEN` hasn't expired (the workflow's log says so).

### A town is behind

From the issue, then the town's last fetching run:

- **One source failing** (311, a calendar, a state figure): the rest of the
  site is current, and the status page says which data is behind. A city
  that changed its website needs a config or reader change; a source that
  refuses requests for a day usually recovers on its own.
- **The whole town failing to build or pass its checks**: the site keeps
  its last good build. Find the failing check in the run, fix the config or
  the engine, and run **Actions → Network → Run workflow** for that town.
- **SeeClickFix refusing** (three 403s in a row stop the 311 step): wait a
  day before running again by hand; it limits by address.

### The daily runs stopped

The scheduler opens **The network's daily runs have stopped** (label
`network stopped`) after 30 hours without a finished run.

1. Start one by hand: **Actions → Network → Run workflow** with **daily**
   ticked.
2. If that works, the scheduler isn't starting runs: check
   `SCHEDULER_GITHUB_TOKEN` (it expires about 2027-10-01) and the Worker's
   logs in Cloudflare (**Workers & Pages → publick-scheduler → Logs**). To
   redeploy it, run **Actions → Worker**.
3. If the run itself fails before any town, read its plan job: usually a
   workflow change or GitHub itself.

### Pausing the daily runs

To stop every run for a while (a source that must not be asked again, a
broken engine you can't roll back yet): **Actions → Network → ⋯ → Disable
workflow**. The scheduler's starts then fail harmlessly, the sites keep
their last builds, and after 30 hours the scheduler opens "The network's
daily runs have stopped", as expected. **Enable workflow** turns it back on; the next start
takes every town that's due.

### A site is broken, or shows something wrong

Roll the town back to its previous build, then fix forward. With the sites
bucket's keys set, from a checkout of the engine:

```sh
python -m pipeline.deploy rollback --domain <town>-<state>.publick.org                 # the build before
python -m pipeline.deploy rollback --domain <town>-<state>.publick.org --build <build>
```

Builds beyond the newest ten are deleted daily, so a rollback reaches back
about ten publishes. To take every town back to an older engine, set
`engine-version` to the earlier release and merge; the push run publishes
every town on it.

### Many more readers than usual

A news story or a shared link can bring more readers in an hour than a
usual week. The sites are static and the Worker keeps their files in
Cloudflare's cache, so the one limit that bites is Cloudflare's plan:

1. **Workers & Pages → publick-sites → Metrics**: requests, errors, and
   CPU time. On the free plan, past 100,000 requests a day every site gets
   Cloudflare's error 1027 until midnight UTC: move the account to Workers
   Paid (**Workers & Pages → Plans**), which takes effect at once.
2. **R2 → publick-sites → Metrics**: reads should stay low while the Worker's
   cache is working. A climb in reads with the requests means it isn't.
3. If one town's signup form is being abused (the Worker's logs say "over
   the rate limit" many times), turn that town's `[digest] signup` off and
   merge; the form is gone on the next build.
4. GoatCounter counts page views on its own limits; missed counts don't
   affect the sites.

### A reader reports an error

The "Report an error" buttons go to each town's `contact_email`.

- **A meeting listed wrong by the city** (an old schedule, a wrong time):
  a `[[meetings.corrections]]` entry in the town's config, with the reason,
  a link to the evidence and the date checked (the README's "Checking
  meetings by hand"). It can go up in English.
- **A summary that's wrong**: read the document first. If the city's
  document says it (a typo in the minutes), the summary is right to copy
  it. If the summary is wrong, there's no switch yet to hold back one
  summary: roll the town back if the harm is serious, and fix it in the
  engine (a fact-check rule, or a prompt change with its version raised).
  A switch for this is a gap to close.
- **An official listed wrong**: fix the town's `[officials]` table and its
  `checked` date, from the city's own pages.

Record what was wrong and what changed in the pull request that fixes it.

### The budget runs out

When the month's budget is spent, towns stop making summaries and
translations until the next month; everything else keeps running. New
documents go first, so upcoming agendas are the last to stop.

- The budget is `SUMMARY_BUDGET` in `network.yml` ($80 a month), and a
  single month's can be set in `SUMMARY_BUDGET_MONTH` (`2026-12=100`).
  Changing it is a pull request to this repository; it applies to the next
  run.
- Check the Anthropic console's spending against the ledgers once a month:
  the console is the bill, and the ledgers are recounted from what the
  engine saved.
- A new town's history is summarized only from `[summaries] since`, about
  three months before launch, so a launch doesn't take the month.

## Releasing by hand

- **An urgent engine fix:** merge it, run the engine's **Actions → Release →
  Run workflow**, then **Actions → Engine → Run workflow** here. The engine
  pull request still checks every town before it merges.
- **The Workers:** **Actions → Worker** deploys both from the engine at
  `engine-version`. It never runs on its own, because the sites Worker's
  routes decide which hostnames it answers: a mistake there takes every site
  down. Deploy it after a release that changes `worker/`, and look at a
  town's site and `publick.org/status/` right after.

## Secrets and when they expire

Set in this repository's **Settings → Secrets and variables → Actions**; the
README's "Setup, once" says what each holds.

| Secret | Expires | If it lapses |
|---|---|---|
| `SCHEDULER_GITHUB_TOKEN` | About 2027-10-01 (made 2026-09-30, 366 days) | Runs fall back to GitHub's late schedule; the release and engine pull request start hours late. Replace it, then run **Actions → Worker** |
| `ENGINE_PR_TOKEN` | When it was set to | The engine stops moving; `engine.yml` fails and emails |
| `ANTHROPIC_API_KEY` | When revoked | No new summaries or translations; sites keep the ones they have |
| `CLOUDFLARE_API_TOKEN` | When it was set to | **Actions → Worker** can't deploy; the running Workers keep working |
| `SITES_*`, `STORAGE_*` | When revoked | Nothing publishes, or documents aren't stored; sites keep their last builds |
| `BLS_API_KEY` | When revoked | Unemployment figures fall behind |
| `BUTTONDOWN_SUBSCRIBE_KEY` | When revoked | The digest's signup form says it didn't go through. Make a new key in Buttondown (**API → Keys**: subscribers read and write, sending disabled), then run **Actions → Worker** |
| `BUTTONDOWN_SEND_KEY` | When revoked | The weekly digest isn't sent, and the scheduler opens an issue. Make a new key (emails read and write, sending enabled), then run **Actions → Worker** |

Put each expiry date in a calendar when the token is made.

## By hand, on a schedule

- **The meetings audit**, about weekly while towns are added: each town's
  upcoming meetings against the city's own sites (README, "Checking meetings
  by hand").
- **Officials**, after each municipal election and whenever a seat changes
  (README, "Keeping officials current", which lists each town's dates). The
  next is November 3, 2026, for Bangor, Lewiston, and South Kingstown.
- **New Hampshire's yearly figures**, when the status page shows them behind
  (README, "New Hampshire's yearly figures"). Vermont's, Maine's, and Rhode
  Island's are saved into the engine once a year too (the engine README's
  States section); Rhode Island's are downloaded by hand in a browser.
- **A new town's email routing rule**, in Cloudflare's dashboard, when the
  town is added (`ADDING-A-TOWN.md`).
