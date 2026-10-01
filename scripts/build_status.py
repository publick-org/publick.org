"""Build the network status page, publick.org/status/: every town's last daily run and data sources.

Each daily run that fetches a town's data writes its result to the town's
data/run.json (the engine's pipeline/network.py), and commits it with the
data: when the run finished, which steps failed, and each data source's
freshness (the engine's pipeline/freshness.py). This page puts every town's
record side by side, so a broken source shows here the morning it breaks,
not only in the run's email.

The page is public, for the towns' readers: it says which data on a site may
be out of date, in plain words, and leaves the run's internals (commands,
errors, timings) to the run's summary on GitHub Actions. A site has "some data
delayed" when a daily step of its last run failed or a source is behind, and
is "not updated" when it has had no daily run for LATE_HOURS. Figures that are
published monthly or yearly (FIGURE_STEPS) are behind only when newer figures
should have been published by now; a failed check of one isn't shown here, since
the site still has the latest figures (the engine reports repeated failures to
the maintainer).

It never shows what running the network costs or how much data it keeps:
those are for the maintainer, not the towns' readers.

The page's last-daily-run meta tag is when the most recent town's daily run
finished; the publick-scheduler Worker reads it to tell when the network's
runs have stopped altogether.

    python scripts/build_status.py --out _home
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
RUN_RECORD = Path("data") / "run.json"
# Each town runs once a day; a record older than this means its run didn't happen or didn't finish.
LATE_HOURS = 30
# The page's own times are in the network's time zone; each town's, in its own.
NETWORK_TZ = ZoneInfo("America/New_York")

LABELS = {"ok": "Up to date", "attention": "Some data delayed", "late": "Not updated", "none": "Not started"}

# What each step of the daily update brings to a town's site, in a reader's words. A step not named
# here is internal; its failure is reported only as part of the update not finishing.
STEP_DATA = {
    "Fetch meetings": "meeting calendar",
    "Fetch minutes": "meeting minutes",
    "Fetch School Committee documents": "School Committee agendas and minutes",
    "Summarize agendas": "agenda and minutes summaries",
    "Fetch tax bill": "tax bill figures",
    "Fetch unemployment": "unemployment rate",
    "Fetch school figures": "school figures",
    "Fetch budget figures": "budget figures",
    "Fetch housing figures": "housing figures",
    "Fetch building permits": "building permits",
    "Fetch 311 requests": "311 requests",
    "Compute 311 scorecard": "311 figures",
}
# Steps that fetch figures published monthly or yearly. The engine judges these by the period their data
# covers, so a failed check isn't news for readers unless the figures fall behind (a source row says so).
FIGURE_STEPS = {"Fetch tax bill", "Fetch unemployment", "Fetch school figures", "Fetch budget figures",
                "Fetch housing figures"}
# Steps that put the day's build on the site. If one fails, the site keeps the version before.
PUBLISH_STEPS = ("Build site", "Check site", "Publish site")


def when(stamp: str | None, tz: ZoneInfo) -> str:
    """'Sep 29, 2026, 5:40 a.m. EDT', or a dash for no time."""
    if not stamp:
        return "–"
    t = datetime.fromisoformat(stamp).astimezone(tz)
    hour = t.strftime("%I").lstrip("0")
    return f"{t:%b} {t.day}, {t.year}, {hour}:{t:%M} {'a.m.' if t.hour < 12 else 'p.m.'} {t:%Z}"


def load_towns(root: Path) -> list[dict]:
    towns = []
    for folder in sorted((root / "towns").iterdir()):
        configs = list((folder / "config").glob("*.toml")) if folder.is_dir() else []
        if len(configs) != 1:
            continue
        config = tomllib.loads(configs[0].read_text(encoding="utf-8"))
        record_path = folder / RUN_RECORD
        towns.append({"folder": folder.name, "name": config["site"]["name"],
                      "url": f"https://{config['site']['domain']}", "domain": config["site"]["domain"],
                      "place": f"{config['town']['name']}, {config['town']['state']}",
                      "tz": ZoneInfo(config["site"].get("timezone", "America/New_York")),
                      "record": json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else None})
    return towns


def last_run(record: dict) -> str:
    return record.get("finished_at") or record["started_at"]


def issues(record: dict, tz: ZoneInfo) -> list[str]:
    """What a reader of the town's site should know about its last update, in plain words.

    This page is public: it names the data affected, never the run's internals (commands, errors,
    timings). Those are in the run's summary on GitHub Actions.
    """
    found = []
    fetch_steps = (record.get("update") or {}).get("steps", [])
    failed = [s["name"] for s in fetch_steps if not s["ok"] and s["name"] not in FIGURE_STEPS]
    for name in failed:
        if name in STEP_DATA:
            found.append(f"The {STEP_DATA[name]} couldn't be checked for changes in the latest daily update.")
    internal = any(name not in STEP_DATA for name in failed) or (
        not fetch_steps and any(s["name"] == "Fetch new data" and not s["ok"] for s in record.get("steps", [])))
    if internal:
        found.append("Part of the latest update didn't finish.")
    if any(s["name"] in PUBLISH_STEPS and not s["ok"] for s in record.get("steps", [])):
        found.append("The latest update couldn't be put on the site, so it shows the version from before.")
    for r in record.get("sources") or []:
        if not r["stale"]:
            continue
        if "waiting_count" in r:
            n = r["waiting_count"]
            found.append(f"{n} agenda{'s' if n != 1 else ''} or minutes {'are' if n != 1 else 'is'} "
                         f"waiting for a summary.")
        elif r.get("behind") and r["behind"] != "no data yet":
            found.append(f"{r['label']}: {r['behind']}.")
        elif r["updated_at"]:
            found.append(f"{r['label']}: last updated {when(r['updated_at'], tz)}, later than expected.")
        else:
            found.append(f"{r['label']}: no data yet.")
    if record.get("stale") and not record.get("sources"):
        found.append("Some data is older than expected.")
    return found


def status(town: dict, now: datetime) -> str:
    record = town["record"]
    if record is None:
        return "none"
    if (now - datetime.fromisoformat(last_run(record))).total_seconds() > LATE_HOURS * 3600:
        return "late"
    return "attention" if issues(record, town["tz"]) else "ok"


def badge(state: str, text: str | None = None) -> str:
    return f'<span class="badge badge-{state}">{text or LABELS[state]}</span>'


def table(caption_id: str, caption: str, head: list[str], rows: list[list[str]]) -> str:
    """A table in a scrolling region of its own, so a wide one never widens the page on a phone."""
    ths = "".join(f'<th scope="col">{h}</th>' for h in head)
    body = "".join("<tr>" + f'<th scope="row">{r[0]}</th>' + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>"
                   for r in rows)
    return (f'<div class="table-scroll" role="region" aria-labelledby="{caption_id}" tabindex="0">\n'
            f'<table>\n<caption id="{caption_id}">{caption}</caption>\n'
            f'<thead><tr>{ths}</tr></thead>\n<tbody>{body}</tbody>\n</table>\n</div>')


def notes(t: dict, state: str) -> list[str]:
    record = t["record"]
    if record is None:
        return ["Daily updates haven't started for this site yet."]
    found = issues(record, t["tz"])
    if state == "late":
        found = [f"No update since {when(last_run(record), t['tz'])}. The site still works, with the data it "
                 "had then.", *found]
    return found


def summary_table(towns: list[dict], states: dict) -> str:
    rows = []
    for t in towns:
        found = notes(t, states[t["folder"]]) if states[t["folder"]] != "ok" else []
        note = ('<ul class="plain">' + "".join(f"<li>{escape(n)}</li>" for n in found) + "</ul>") if found else "–"
        rows.append([f'<a href="#{t["folder"]}">{escape(t["name"])}</a>', badge(states[t["folder"]]),
                     when(t["record"] and last_run(t["record"]), t["tz"]), note])
    return table("towns-caption", "Every site", ["Site", "Status", "Last updated", "Notes"], rows)


def town_section(t: dict, state: str) -> str:
    record, folder = t["record"], t["folder"]
    parts = [f'<section class="town-status town-status-{state}" id="{folder}" aria-labelledby="{folder}-heading">',
             f'<h2 id="{folder}-heading">{escape(t["name"])} {badge(state)}</h2>',
             f'<p class="town-place">{escape(t["place"])} · <a href="{escape(t["url"])}">{escape(t["domain"])}</a></p>']
    if record is not None:
        parts.append(f"<p>Last updated {when(last_run(record), t['tz'])}.</p>")
    found = notes(t, state)
    if state == "none":
        parts.append(f"<p>{escape(found[0])}</p>")
    elif found:
        items = "".join(f"<li>{escape(n)}</li>" for n in found)
        parts.append(f'<ul class="problems" aria-label="Notes on {escape(t["name"])}">{items}</ul>')

    if record and record.get("sources"):
        rows = []
        for r in record["sources"]:
            if "waiting_count" in r:
                result = badge("attention" if r["stale"] else "ok",
                               f"{r['waiting_count']} waiting" if r["waiting_count"] else "None waiting")
            else:
                result = badge("attention", "Delayed") if r["stale"] else badge("ok")
            if r.get("max_days"):
                expected = f"Every {r['max_days']} day{'s' if r['max_days'] != 1 else ''}"
            else:
                expected = escape(r.get("next") or "–")
            rows.append([escape(r["label"]), result, escape(r.get("latest") or "–"), when(r["updated_at"], t["tz"]),
                         expected])
        parts.append(table(f"{folder}-sources", f"Data on {escape(t['name'])}",
                           ["Data", "Status", "Latest", "Last checked", "Next expected"], rows))
    parts.append("</section>")
    return "\n".join(parts)


def render(towns: list[dict], now: datetime) -> str:
    states = {t["folder"]: status(t, now) for t in towns}
    counts = {s: sum(1 for v in states.values() if v == s) for s in LABELS}
    tally = ", ".join(f"{counts[s]} {LABELS[s].lower()}" for s in LABELS if counts[s])
    headline = (f"{len(towns)} site{'s' if len(towns) != 1 else ''}: {tally}." if towns else "No sites yet.")
    sections = "\n\n".join(town_section(t, states[t["folder"]]) for t in towns)
    # Run records are written only by runs that fetch: the daily runs, and manual ones.
    finished = [datetime.fromisoformat(last_run(t["record"])) for t in towns if t["record"]]
    last_daily = max(finished).astimezone(timezone.utc).isoformat(timespec="seconds") if finished else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Network status: Publick</title>
  <meta name="description" content="Whether each Publick site's data is up to date.">
  <meta name="robots" content="noindex">
  <meta name="last-daily-run" content="{last_daily}">
  <link rel="canonical" href="https://publick.org/status/">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'none'; style-src 'self'; img-src 'self' data:; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'">
  <meta name="color-scheme" content="light">
  <meta name="theme-color" content="#faf7f0">
  <link rel="preload" href="../fonts/public-sans-400.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="../fonts/source-serif-4-700.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="icon" href="../favicon-32.png" type="image/png" sizes="32x32">
  <link rel="apple-touch-icon" href="../apple-touch-icon.png">
  <link rel="stylesheet" href="../css/site.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to main content</a>

  <header class="site-header">
    <div class="wrap">
      <div class="masthead">
        <p class="brand"><a href="../"><img src="../favicon.svg" alt="" width="44" height="44"> Publick</a></p>
        <p class="masthead-line">Your town's public record, every day.</p>
      </div>
    </div>
  </header>

  <main id="main" tabindex="-1">
    <div class="wrap">
      <h1 class="page-title">Network status</h1>
      <p class="lede">Whether each Publick site's data is up to date. {headline}</p>
      <p>Each site collects its town's meetings and requests once a day, early in the morning, and checks for new figures that are published monthly or yearly (tax bills, budgets, school results, unemployment) weekly or monthly. When a daily source stops updating, a day's update doesn't finish, or new figures are later than usual, it shows here, and the site keeps showing the last data it had.</p>
      <p class="small">This page was last updated {when(now.isoformat(), NETWORK_TZ)}. Seen something out of date that isn't listed? Write to <a href="mailto:hello@publick.org">hello@publick.org</a>.</p>

      {summary_table(towns, states)}

{sections}

    </div>
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <p class="footer-brand">Publick</p>
      <ul class="footer-links">
        <li><a href="../">publick.org</a></li>
        <li><a href="mailto:hello@publick.org">hello@publick.org</a></li>
        <li><a href="https://github.com/publick-org">Source code on GitHub</a></li>
      </ul>
    </div>
  </footer>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True, help="the homepage's built folder; the page goes in status/")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--now", type=datetime.fromisoformat, help="the time to report as now (for testing)")
    args = parser.parse_args()
    out = (args.out if args.out.is_absolute() else args.root / args.out) / "status"
    now = args.now or datetime.now(timezone.utc)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(render(load_towns(args.root), now), encoding="utf-8")
    print(f"Wrote {out / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
