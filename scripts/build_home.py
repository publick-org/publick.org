"""Build the publick.org homepage, and a page for each state with many towns.

"Find your town" lists every town under towns/, grouped by state. When a state
has STATE_PAGE_AT towns or more, it gets its own page (publick.org/<state>/,
from home/state.html) and the homepage links to it instead, so the homepage
stays short however many towns the network has. Only live towns are named:
a town appears once it has a folder.

The counts at the top (towns, boards followed, meetings in the next 7 days)
come from each town's data/run.json, written by its daily run, never from its
meeting files, so the build stays quick at any size. Until every town's run
record has them, only the number of towns is shown.

Everything else on the pages is home/index.html and home/state.html as
written; the generated parts go between their <!-- towns:... --> markers.

It also writes the sitemap of these pages, and a robots.txt naming it. Each
town's site has its own (the engine's build_site.py). The status page, which
build_status.py adds, is kept out of search results, so out of the sitemap.

    python scripts/build_home.py --out _home    # the pages to publish
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tomllib
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# A state with this many live towns gets its own page.
STATE_PAGE_AT = 10
# Days of coming meetings counted at the top of the homepage.
COMING_DAYS = 7
SITE = "https://publick.org"


def live_towns(root: Path) -> list[dict]:
    towns = []
    for folder in sorted((root / "towns").iterdir()):
        configs = list((folder / "config").glob("*.toml")) if folder.is_dir() else []
        if len(configs) != 1:
            continue
        config = tomllib.loads(configs[0].read_text(encoding="utf-8"))
        site, town = config["site"], config["town"]
        record = folder / "data" / "run.json"
        activity = json.loads(record.read_text(encoding="utf-8")).get("activity") if record.exists() else None
        towns.append({"name": site["name"], "domain": site["domain"], "url": f"https://{site['domain']}",
                      "town": town["name"], "state": town["state"], "state_abbr": town["state_abbr"].lower(),
                      "activity": activity})
    return sorted(towns, key=lambda t: (t["state"], t["town"]))


def by_state(towns: list[dict]) -> list[tuple[str, str, list[dict]]]:
    """(state, its abbreviation, its towns), states in alphabetical order."""
    states: dict[str, list[dict]] = {}
    for t in towns:
        states.setdefault(t["state"], []).append(t)
    return [(state, ts[0]["state_abbr"], ts) for state, ts in sorted(states.items())]


def plural(n: int, one: str, many: str) -> str:
    return f"{n:,} {one if n == 1 else many}"


def glance_html(towns: list[dict], today: date) -> str:
    """The network at a glance: its towns, and, once every town's run record has them, the
    boards it follows and its meetings in the next COMING_DAYS days."""
    items = [("towns", len(towns), "town", "towns")]
    if towns and all(t["activity"] for t in towns):
        last = (today + timedelta(days=COMING_DAYS - 1)).isoformat()
        coming = sum(n for t in towns for day, n in t["activity"]["meetings_by_date"].items()
                     if today.isoformat() <= day <= last)
        boards = sum(t["activity"]["boards"] for t in towns)
        items += [("boards", boards, "board or committee followed", "boards and committees followed"),
                  ("meetings", coming, f"public meeting in the next {COMING_DAYS} days",
                   f"public meetings in the next {COMING_DAYS} days")]
    lis = "".join(f'\n          <li><strong>{n:,}</strong> {one if n == 1 else many}</li>' for _, n, one, many in items)
    return f'\n        <ul class="glance" aria-label="The network today">{lis}\n        </ul>'


def town_cards(towns: list[dict], indent: str) -> str:
    items = "".join(
        f'\n{indent}  <li><a href="{escape(t["url"])}"><span class="name">{escape(t["town"])}</span>'
        f'<span class="domain">{escape(t["domain"])}</span></a></li>' for t in towns)
    return f'\n{indent}<ul class="town-cards">{items}\n{indent}</ul>'


def states_html(towns: list[dict]) -> str:
    parts = []
    for state, abbr, ts in by_state(towns):
        count = plural(len(ts), "town", "towns")
        if len(ts) >= STATE_PAGE_AT:
            parts.append(f'\n        <p class="state-link"><a href="{abbr}/"><span class="name">{escape(state)}</span>'
                         f'<span class="count">{count}</span></a></p>')
            continue
        parts.append(f'\n        <section class="state" aria-labelledby="state-{abbr}">\n'
                     f'          <h3 id="state-{abbr}">{escape(state)} <span class="count">{count}</span></h3>'
                     f'{town_cards(ts, "          ")}\n'
                     f'        </section>')
    return "".join(parts)


def fill(page: str, name: str, block: str, source: str) -> str:
    pattern = re.compile(rf"(<!-- towns:{name} -->).*?(<!-- /towns:{name} -->)", re.S)
    if not pattern.search(page):
        raise SystemExit(f"{source} has no <!-- towns:{name} --> ... <!-- /towns:{name} --> markers")
    return pattern.sub(lambda m: m.group(1) + block + "\n        " + m.group(2), page)


def render(page: str, root: Path, today: date | None = None) -> str:
    today = today or datetime.now(timezone.utc).date()
    live = live_towns(root)
    block = glance_html(live, today) + states_html(live)
    return fill(page, "live", block, "home/index.html")


def state_pages(template: str, root: Path) -> dict[str, str]:
    """The page for each state with STATE_PAGE_AT towns or more, by its folder (its abbreviation)."""
    pages = {}
    for state, abbr, ts in by_state(live_towns(root)):
        if len(ts) < STATE_PAGE_AT:
            continue
        page = template.replace("{state}", escape(state)).replace("{abbr}", abbr)
        page = page.replace("{count}", plural(len(ts), "town", "towns"))
        pages[abbr] = fill(page, "state", town_cards(ts, "        "), "home/state.html")
    return pages


def sitemap(states: list[str], today: date) -> str:
    """The homepage, which changes with each day's counts, and each state's page, which changes only
    when a town is added: it has no date, as the day it last changed isn't known."""
    entries = [f"  <url><loc>{SITE}/</loc><lastmod>{today.isoformat()}</lastmod></url>"]
    entries += [f"  <url><loc>{SITE}/{abbr}/</loc></url>" for abbr in sorted(states)]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(entries) + "\n</urlset>\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True, help="folder to write the pages to")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    source = args.root / "home"
    out = args.out if args.out.is_absolute() else args.root / args.out
    if out.resolve() == source.resolve():
        raise SystemExit("--out must be a new folder, not home/: the pages are built from home/'s templates")
    shutil.rmtree(out, ignore_errors=True)
    shutil.copytree(source, out, ignore=shutil.ignore_patterns("state.html"))
    (out / "index.html").write_text(render((source / "index.html").read_text(encoding="utf-8"), args.root),
                                    encoding="utf-8")
    states = state_pages((source / "state.html").read_text(encoding="utf-8"), args.root)
    for abbr, page in states.items():
        (out / abbr).mkdir(parents=True, exist_ok=True)
        (out / abbr / "index.html").write_text(page, encoding="utf-8")
    (out / "sitemap.xml").write_text(sitemap(list(states), datetime.now(timezone.utc).date()), encoding="utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print(f"Wrote {out / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
