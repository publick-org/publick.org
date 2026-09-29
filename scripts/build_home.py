"""Build the publick.org homepage with its town lists up to date.

"Live now" lists every town under towns/: its site's name and address, its
place, and its sections, from its config. "Coming next" lists the towns in
home/upcoming.toml that don't have a folder yet, so a town moves from one list
to the other when it is added. Everything else on the page is home/index.html
as written; the lists go between its <!-- towns:live --> and <!-- towns:next -->
markers.

    python scripts/build_home.py --out _home    # the page to publish
    python scripts/build_home.py --out home     # refresh the committed page
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tomllib
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKERS = ("live", "next")


def live_towns(root: Path) -> list[dict]:
    towns = []
    for folder in sorted((root / "towns").iterdir()):
        configs = list((folder / "config").glob("*.toml")) if folder.is_dir() else []
        if len(configs) != 1:
            continue
        config = tomllib.loads(configs[0].read_text(encoding="utf-8"))
        site, town = config["site"], config["town"]
        titles = [s.get("title", s["slug"]) for s in config.get("sections", []) if s["slug"] != "about"]
        towns.append({"name": site["name"], "url": f"https://{site['domain']}", "town": town["name"],
                      "state": town["state"], "sections": titles})
    return sorted(towns, key=lambda t: (t["town"], t["state"]))


def upcoming_towns(root: Path, live: list[dict]) -> list[dict]:
    path = root / "home" / "upcoming.toml"
    listed = tomllib.loads(path.read_text(encoding="utf-8")).get("town", []) if path.exists() else []
    here = {(t["town"].lower(), t["state"].lower()) for t in live}
    return [t for t in listed if (t["name"].lower(), t["state"].lower()) not in here]


def sections_line(titles: list[str]) -> str:
    """['Meetings', '311 Requests', 'City budget'] -> 'Meetings, 311 requests and city budget, updated daily.'"""
    words = titles[:1] + [t.lower() for t in titles[1:]]
    if not words:
        return "Updated daily."
    joined = words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]
    return f"{joined}, updated daily."


def live_html(towns: list[dict]) -> str:
    items = "".join(
        f'\n          <li class="town">\n'
        f'            <h3><a href="{escape(t["url"])}">{escape(t["name"])}</a></h3>\n'
        f'            <p class="town-place">{escape(t["town"])}, {escape(t["state"])}</p>\n'
        f'            <p>{escape(sections_line(t["sections"]))}</p>\n'
        f'          </li>' for t in towns)
    return f'\n        <ul class="towns">{items}\n        </ul>\n        '


def next_html(towns: list[dict]) -> str:
    if not towns:
        return "\n      "
    items = "".join(
        f'\n          <li class="town town-next">\n'
        f'            <h3>{escape(t["name"])}, {escape(t["state"])}</h3>\n'
        f'            <p>{escape(t.get("note", "In the works."))}</p>\n'
        f'          </li>' for t in towns)
    return (f'\n      <section aria-labelledby="next-heading">\n'
            f'        <h2 id="next-heading">Coming next</h2>\n'
            f'        <ul class="towns">{items}\n        </ul>\n'
            f'      </section>\n      ')


def render(page: str, root: Path) -> str:
    live = live_towns(root)
    blocks = {"live": live_html(live), "next": next_html(upcoming_towns(root, live))}
    for name in MARKERS:
        pattern = re.compile(rf"(<!-- towns:{name} -->).*?(<!-- /towns:{name} -->)", re.S)
        if not pattern.search(page):
            raise SystemExit(f"home/index.html has no <!-- towns:{name} --> ... <!-- /towns:{name} --> markers")
        page = pattern.sub(lambda m: m.group(1) + blocks[name] + m.group(2), page)
    return page


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True, help="folder to write the page to")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    source = args.root / "home"
    out = args.out if args.out.is_absolute() else args.root / args.out
    page = render((source / "index.html").read_text(encoding="utf-8"), args.root)
    if out.resolve() != source.resolve():
        shutil.rmtree(out, ignore_errors=True)
        shutil.copytree(source, out, ignore=shutil.ignore_patterns("upcoming.toml"))
    (out / "index.html").write_text(page, encoding="utf-8")
    print(f"Wrote {out / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
