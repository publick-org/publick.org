# publick.org

The Publick network: the publick.org homepage and every town's site, run
from this one repository with the [Publick engine](https://github.com/publick-org/publick-engine)
at the version in `engine-version`.

```
engine-version                The engine release every town runs, e.g. v1.3.0
home/                         The publick.org homepage; its town lists are filled in by scripts/build_home.py
home/upcoming.toml            Towns shown under "Coming next" on the homepage
towns/<town>-<state>/         One folder per town, laid out as a town repository is:
  config/<town>.toml            everything town-specific
  data/                         collected data, committed by the daily run
  site/static/                  files that replace or add to the engine's (the share image)
wrangler.toml                 The Worker that serves every site from the sites bucket
scripts/import-town.sh        Copies a town's own repository into towns/
scripts/build_home.py         Writes the homepage's "Live now" and "Coming next" lists
scripts/build_status.py       Writes the network status page, publick.org/status/
.github/workflows/network.yml The daily runs, and builds on push and pull request
.github/workflows/worker.yml  Deploys the Worker (by hand)
```

## How it runs

Every site is built into the sites bucket (Cloudflare R2) and served by one
Worker, which picks the site by hostname: `gloucester-ma.publick.org` is
`towns/gloucester-ma`, and `publick.org` is `home/`. See the engine's
`pipeline/deploy.py` and `worker/index.js`.

- **Daily**, in four runs from 09:17 to 12:17 UTC: each town belongs to one run, by a
  stable hash of its folder name. A run fetches each of its towns' new data,
  builds and checks the site, publishes it if the checks pass, and commits the
  data. Towns run in batches of four per job, up to ten jobs at a time. Daily
  runs give the accessibility checks a sample of each town's pages (every
  hand-written page, and the first and largest of each kind of record page);
  every other run checks every page.
- **On push to `main`:** rebuilds and publishes the towns the push touched (every
  town when `engine-version` or a workflow changed), and the homepage if `home/`,
  `scripts/` or a town's config changed. Data isn't fetched.
- **On a pull request:** builds and checks the towns it touches. Nothing is published.
- **By hand** (**Actions → Network → Run workflow**): any towns, with or without
  fetching; with no towns named, every town and the homepage.

Each run ends with one table of every town it ran, and fails once if any town
failed or has stale data, so GitHub sends one email per run.

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
after 30 hours with no daily run.

## Adding a town

Add `towns/<town>-<state>/` with its `config/<town>.toml` (start from the
engine's `tests/fixtures/town/config/gloucester.toml` and its README), an
empty `data/`, and optionally `site/static/share/<town>.png`. Set
`[site] domain` to `<town>-<state>.publick.org` and `network_url` to
`https://publick.org`, which links the network's name in every page footer.
Merge, then run the workflow for the town by hand to fetch its data. No DNS
change is needed, and the homepage lists the town as live (and drops it from
`home/upcoming.toml`'s "Coming next") on its own.

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

Then turn off GitHub Pages for this repository (**Settings → Pages**), and
run **Actions → Worker**.
