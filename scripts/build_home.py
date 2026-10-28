"""Build the publick.org homepage, and a page for each state with many towns.

"Find your town" lists every town under towns/, grouped by state, each state
the same way: its name, how many towns, and its towns' names in columns, each
linking the town's site. A list of names stays short enough to read and to
search with the browser's find however many towns a state has; the page has
no scripts (its Content-Security-Policy allows none). When a state has
STATE_PAGE_AT towns or more, it also gets its own page (publick.org/<state>/,
from home/state.html), with a card for each town and its meetings this week,
linked under the state's list. Once the network has INDEX_AT towns or more,
the homepage lists only the states, each with how many towns and a link to its
page, and every state has a page. Only live towns are named: a town appears
once it has a folder.

The counts at the top (towns, boards followed, meetings in the next 7 days)
come from each town's data/run.json, written by its daily run, never from its
meeting files, so the build stays quick at any size. Until every town's run
record has them, only the number of towns is shown. Each town's card on a
state's page says the same of the town: its meetings this week, from its run
record, when it has any.

The open data page, publick.org/data/ (from home/data.html), lists each live
town's export, /data/meetings.json, and its Data page, both built by the engine
with the town's site.

Everything else on the pages is home/index.html and home/state.html as
written; the generated parts go between their <!-- towns:... --> markers.

It also writes the network's sitemap, publick.org/sitemap.xml: an index of
this site's own (sitemap-home.xml) and every live town's (the engine's
build_site.py writes each), so submitting it once in Search Console, to the
publick.org domain property that covers every town's subdomain, covers every
town, and a new town is in it from its first build. robots.txt names it. The
status page, which build_status.py adds, is kept out of search results, so out
of the sitemap.

    PYTHONPATH=../publick-engine python scripts/build_home.py --out _home    # the pages to publish
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path

# Each town's config as the engine reads it, over the network's shared settings (defaults/network.toml,
# defaults/states/<st>.toml): the engine is on PYTHONPATH, as for building a town.
from pipeline.config import read_config

ROOT = Path(__file__).resolve().parent.parent
# A state with this many live towns gets its own page.
STATE_PAGE_AT = 10
# A network with this many live towns lists only its states on the homepage, and every state gets its page.
INDEX_AT = 150
# Days of coming meetings counted at the top of the homepage.
COMING_DAYS = 7
SITE = "https://publick.org"


def live_towns(root: Path) -> list[dict]:
    towns = []
    for folder in sorted((root / "towns").iterdir()):
        configs = list((folder / "config").glob("*.toml")) if folder.is_dir() else []
        if len(configs) != 1:
            continue
        config = read_config(configs[0], root)
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


def coming(town: dict, today: date) -> int | None:
    """A town's meetings in the next COMING_DAYS days, from its run record; None without one."""
    if not town["activity"]:
        return None
    last = (today + timedelta(days=COMING_DAYS - 1)).isoformat()
    return sum(n for day, n in town["activity"]["meetings_by_date"].items() if today.isoformat() <= day <= last)


def glance_html(towns: list[dict], today: date) -> str:
    """The network at a glance: its towns, and, once every town's run record has them, the
    boards it follows and its meetings in the next COMING_DAYS days."""
    items = [("towns", len(towns), "town", "towns")]
    if towns and all(t["activity"] for t in towns):
        coming_total = sum(coming(t, today) for t in towns)
        boards = sum(t["activity"]["boards"] for t in towns)
        items += [("boards", boards, "board or committee followed", "boards and committees followed"),
                  ("meetings", coming_total, f"public meeting in the next {COMING_DAYS} days",
                   f"public meetings in the next {COMING_DAYS} days")]
    lis = "".join(f'\n          <li><strong>{n:,}</strong> {one if n == 1 else many}</li>' for _, n, one, many in items)
    return f'\n        <ul class="glance" aria-label="The network today">{lis}\n        </ul>'


def card_news(town: dict, today: date) -> str:
    """What a town's card says of it: its meetings this week (as its own home page counts them, the
    next COMING_DAYS days), when it has any."""
    if n := coming(town, today):
        return f'<span class="news">{plural(n, "meeting this week", "meetings this week")}</span>'
    return ""


def town_cards(towns: list[dict], indent: str, today: date) -> str:
    items = "".join(
        f'\n{indent}  <li><a href="{escape(t["url"])}"><span class="name">{escape(t["town"])}</span>'
        f'<span class="domain">{escape(t["domain"])}</span>{card_news(t, today)}</a></li>' for t in towns)
    return f'\n{indent}<ul class="town-cards">{items}\n{indent}</ul>'


def town_list(towns: list[dict], indent: str) -> str:
    """A state's towns on the homepage: each one's name, linking its site."""
    items = "".join(f'\n{indent}  <li><a href="{escape(t["url"])}">{escape(t["town"])}</a></li>' for t in towns)
    return f'\n{indent}<ul class="town-list">{items}\n{indent}</ul>'


def has_page(towns_in_state: int, network_towns: int) -> bool:
    return towns_in_state >= STATE_PAGE_AT or network_towns >= INDEX_AT


def state_index(towns: list[dict]) -> str:
    """A large network's homepage: each state, how many towns, and a link to its page."""
    items = "".join(f'\n          <li><a href="{abbr}/"><span class="name">{escape(state)}</span> '
                    f'<span class="count">{plural(len(ts), "town", "towns")}</span></a></li>'
                    for state, abbr, ts in by_state(towns))
    return f'\n        <ul class="state-index">{items}\n        </ul>'


def states_html(towns: list[dict]) -> str:
    """Every state the same way: its name and how many towns, its towns' names, and, for a state with
    its own page, a link to it."""
    if len(towns) >= INDEX_AT:
        return state_index(towns)
    parts = []
    for state, abbr, ts in by_state(towns):
        count = plural(len(ts), "town", "towns")
        more = (f'\n          <p class="state-more"><a href="{abbr}/">Every {escape(state)} town, '
                f'with its meetings this week</a></p>' if has_page(len(ts), len(towns)) else "")
        parts.append(f'\n        <section class="state" aria-labelledby="state-{abbr}">\n'
                     f'          <h3 id="state-{abbr}">{escape(state)} <span class="count">{count}</span></h3>'
                     f'{town_list(ts, "          ")}{more}\n'
                     f'        </section>')
    return "".join(parts)


def data_html(towns: list[dict]) -> str:
    """The open data page's table: each town's Data page (named for the town) and its export, the
    engine's /data/meetings.json."""
    rows = "".join(
        f'\n          <tr><th scope="row"><a href="{escape(t["url"])}/data/">{escape(t["town"])}, {escape(t["state_abbr"].upper())}</a></th>'
        f'<td><a href="{escape(t["url"])}/data/meetings.json">meetings.json</a></td></tr>' for t in towns)
    return ('\n      <div class="table-scroll" role="region" aria-labelledby="data-caption" tabindex="0">'
            '\n        <table>\n          <caption id="data-caption">Each town\'s file</caption>'
            '\n          <thead><tr><th scope="col">Town and its Data page</th><th scope="col">Download</th></tr></thead>'
            f'\n          <tbody>{rows}\n          </tbody>\n        </table>\n      </div>')


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


def state_pages(template: str, root: Path, today: date | None = None) -> dict[str, str]:
    """The page for each state with STATE_PAGE_AT towns or more, or for every state once the network has
    INDEX_AT towns, by its folder (its abbreviation)."""
    today = today or datetime.now(timezone.utc).date()
    pages = {}
    live = live_towns(root)
    for state, abbr, ts in by_state(live):
        if not has_page(len(ts), len(live)):
            continue
        page = template.replace("{state}", escape(state)).replace("{abbr}", abbr)
        page = page.replace("{count}", plural(len(ts), "town", "towns"))
        pages[abbr] = fill(page, "state", town_cards(ts, "        ", today), "home/state.html")
    return pages


def sitemap_index(towns: list[dict]) -> str:
    """The network's sitemap: this site's own, then each live town's."""
    entries = [f"  <sitemap><loc>{loc}</loc></sitemap>"
               for loc in [f"{SITE}/sitemap-home.xml", *(f"{t['url']}/sitemap.xml" for t in towns)]]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(entries) + "\n</sitemapindex>\n")


def sitemap(states: list[str], today: date) -> str:
    """This site's pages: the homepage, which changes with each day's counts, and each state's page,
    which changes only when a town is added: it has no date, as the day it last changed isn't known."""
    entries = [f"  <url><loc>{SITE}/</loc><lastmod>{today.isoformat()}</lastmod></url>"]
    entries += [f"  <url><loc>{SITE}/{abbr}/</loc></url>" for abbr in sorted(states)]
    entries.append(f"  <url><loc>{SITE}/data/</loc></url>")
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
    shutil.copytree(source, out, ignore=shutil.ignore_patterns("state.html", "data.html"))
    (out / "index.html").write_text(render((source / "index.html").read_text(encoding="utf-8"), args.root),
                                    encoding="utf-8")
    states = state_pages((source / "state.html").read_text(encoding="utf-8"), args.root)
    for abbr, page in states.items():
        (out / abbr).mkdir(parents=True, exist_ok=True)
        (out / abbr / "index.html").write_text(page, encoding="utf-8")
    (out / "data").mkdir(parents=True, exist_ok=True)
    (out / "data" / "index.html").write_text(
        fill((source / "data.html").read_text(encoding="utf-8"), "data", data_html(live_towns(args.root)), "home/data.html"),
        encoding="utf-8")
    (out / "sitemap-home.xml").write_text(sitemap(list(states), datetime.now(timezone.utc).date()), encoding="utf-8")
    (out / "sitemap.xml").write_text(sitemap_index(live_towns(args.root)), encoding="utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print(f"Wrote {out / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
