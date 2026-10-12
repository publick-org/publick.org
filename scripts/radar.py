"""Find local conversations a Publick site could answer, for a person to reply to.

Reads each town's subreddits (new posts and new comments, from Reddit's public
RSS), the wider subreddits it is talked about in (only posts that name the
town), and Bluesky's public search, and keeps what asks about something a
town's site covers: an agenda or a vote, a pothole, the tax rate, the
schools, rents, who the councilor is. Each match is listed with the page that
answers it, a question first, for a person to read and, where a link would
really help, reply to by hand. It posts nothing.

Where to look is in scripts/radar.toml; what each town's site covers is its
config's [[sections]].

    python scripts/radar.py --days 2 --out radar.md
    python scripts/radar.py --days 30 --cache .radar-cache --out radar.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from hashlib import sha1
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER_AGENT = "Mozilla/5.0 (compatible; publick-radar/0.1; +https://publick.org)"
ATOM = "{http://www.w3.org/2005/Atom}"
BLUESKY = "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts"

# What each section answers, as the words people use when they ask about it.
# Only words that mean the city: "rent", "budget" or "high school" alone match
# rental ads, car repair and comedy nights far more often than a civic question.
TOPICS = {
    "meetings": [
        "city council",
        "town council",
        "council meeting",
        "school committee",
        "school board",
        "planning board",
        "zoning board",
        "zba",
        "board of aldermen",
        "aldermen",
        "select board",
        "selectboard",
        "conservation commission",
        "agenda",
        "public hearing",
        "public comment",
        "council voted",
        "council vote",
        "ordinance",
    ],
    "311": [
        "pothole",
        "potholes",
        "streetlight",
        "street light",
        "trash pickup",
        "missed trash",
        "plowed",
        "graffiti",
        "311",
        "seeclickfix",
        "who do i call",
        "report it to the city",
        "dpw",
    ],
    "budget": [
        "city budget",
        "town budget",
        "school budget",
        "tax rate",
        "property tax",
        "property taxes",
        "tax bill",
        "override",
        "free cash",
        "mill rate",
        "taxes went up",
        "taxes are going up",
    ],
    "schools": [
        "superintendent",
        "mcas",
        "test scores",
        "graduation rate",
        "school district",
        "public schools",
        "teachers contract",
        "teacher contract",
        "enrollment",
    ],
    "housing": [
        "affordable housing",
        "housing crisis",
        "housing production",
        "zoning",
        "adu",
        "adus",
        "building permit",
        "rezoning",
        "inclusionary",
        "homeless shelter",
    ],
    "officials": [
        "mayor",
        "councilor",
        "councillor",
        "alderman",
        "who represents",
        "city election",
        "municipal election",
        "candidate forum",
        "candidates for",
        "running for council",
        "running for mayor",
        "ward councilor",
    ],
}

QUESTION = re.compile(
    r"\?|\b(anyone know|does anyone|has anyone|where can i|how do i|who do i|is there a|"
    r"what'?s going on|what is going on|what happened|any idea|any info|curious if|wondering)\b",
    re.I,
)
# Accounts that post forecasts, job listings and the like, never a question.
BOT_HANDLE = re.compile(r"bot|4cast|jobs|educativ|weather|brid\.gy", re.I)


@dataclass
class Town:
    slug: str
    name: str
    names: list[str]
    state: str
    domain: str
    sections: dict[str, str]
    subreddits: list[str]
    shared: list[str]
    hints: list[str]


@dataclass
class Item:
    town: str
    source: str
    kind: str
    url: str
    when: datetime
    author: str
    title: str
    text: str
    sections: list[str] = field(default_factory=list)
    words: list[str] = field(default_factory=list)
    question: bool = False
    mentions_publick: bool = False
    replies: int = 0

    @property
    def score(self) -> int:
        local = self.source.startswith("r/") and self.kind != "shared"
        return 2 * len(self.sections) + 3 * self.question + local + min(self.replies, 3)

    def key(self) -> str:
        """The thread: a Reddit comment's post, so a busy thread is listed once."""
        url = self.url.split("?")[0].rstrip("/")
        if "reddit.com" in url:
            url = "/".join(url.split("/")[:8])
        return url


def load_towns(config: Path) -> list[Town]:
    radar = tomllib.loads(config.read_text())["towns"]
    towns = []
    for slug, where in radar.items():
        (path,) = (ROOT / "towns" / slug / "config").glob("*.toml")
        cfg = tomllib.loads(path.read_text())
        town = cfg["town"]
        towns.append(
            Town(
                slug=slug,
                name=town["name"],
                names=where.get("names", [town["name"]]),
                state=town["state_abbr"],
                domain=cfg["site"]["domain"],
                sections={
                    s["slug"]: s["title"]
                    for s in cfg["sections"]
                    if s["slug"] in TOPICS and s.get("status", "live") == "live"
                },
                subreddits=where.get("subreddits", []),
                shared=where.get("shared", []),
                hints=where.get("hints", []),
            )
        )
    return towns


class Fetcher:
    """GETs with a polite pace for Reddit, which allows unauthenticated readers few requests, and an optional cache."""

    def __init__(self, cache: Path | None):
        self.cache = cache
        self.last_reddit = 0.0
        if cache:
            cache.mkdir(parents=True, exist_ok=True)

    def get(self, url: str) -> bytes | None:
        if self.cache:
            hit = self.cache / sha1(url.encode()).hexdigest()
            if hit.exists():
                return hit.read_bytes()
        reddit = "reddit.com" in url
        for attempt in range(4):
            if reddit:
                time.sleep(max(0.0, 7 - (time.monotonic() - self.last_reddit)))
                self.last_reddit = time.monotonic()
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    body = response.read()
                    break
            except urllib.error.HTTPError as error:
                if error.code == 429 and attempt < 3:
                    wait = float(
                        error.headers.get("x-ratelimit-reset")
                        or error.headers.get("retry-after")
                        or 30
                    )
                    print(f"  rate limited, waiting {wait:.0f}s", file=sys.stderr)
                    time.sleep(wait + 1)
                    continue
                print(f"  {error.code} for {url}", file=sys.stderr)
                return None
            except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
                if attempt < 3:
                    time.sleep(2 ** (attempt + 1))
                    continue
                print(f"  failed {url}: {error}", file=sys.stderr)
                return None
        else:
            return None
        if self.cache:
            hit.write_bytes(body)
        return body


def plain(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", unescape(html or ""))
    text = re.sub(r"submitted by\s+/u/\S+.*$", "", text, flags=re.S)
    text = re.sub(r"\[link\]|\[comments\]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def reddit_feed(fetcher: Fetcher, sub: str, comments: bool) -> list[dict]:
    path = "comments/" if comments else "new/"
    body = fetcher.get(f"https://www.reddit.com/r/{sub}/{path}.rss?limit=100")
    if not body:
        return []
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return []
    entries = []
    for entry in root.iter(f"{ATOM}entry"):
        link = entry.find(f"{ATOM}link")
        when = entry.findtext(f"{ATOM}published") or entry.findtext(f"{ATOM}updated")
        entries.append(
            {
                "url": link.get("href") if link is not None else "",
                "when": datetime.fromisoformat(when),
                "author": (
                    entry.findtext(f"{ATOM}author/{ATOM}name") or ""
                ).removeprefix("/u/"),
                # A comment's title is "/u/someone on <the post's title>".
                "title": re.sub(
                    r"^/u/\S+ on ", "", entry.findtext(f"{ATOM}title") or ""
                ),
                "text": plain(entry.findtext(f"{ATOM}content") or ""),
            }
        )
    return entries


def bluesky(fetcher: Fetcher, query: str, since: datetime) -> list[dict]:
    params = urllib.parse.urlencode(
        {
            "q": query,
            "sort": "latest",
            "limit": 100,
            "since": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    )
    body = fetcher.get(f"{BLUESKY}?{params}")
    if not body:
        return []
    posts = []
    for post in json.loads(body).get("posts", []):
        handle = post["author"]["handle"]
        if BOT_HANDLE.search(handle):
            continue
        rkey = post["uri"].rsplit("/", 1)[-1]
        posts.append(
            {
                "url": f"https://bsky.app/profile/{handle}/post/{rkey}",
                "when": datetime.fromisoformat(
                    post["record"]["createdAt"].replace("Z", "+00:00")
                ),
                "author": handle,
                "title": "",
                "text": post["record"].get("text", ""),
            }
        )
    return posts


def has_word(text: str, word: str) -> bool:
    flags = 0 if word.isupper() else re.I
    return re.search(rf"(?<![\w/]){re.escape(word)}(?!\w)", text, flags) is not None


def classify(item: Item, town: Town) -> Item:
    text = f"{item.title} {item.text}"
    for section in town.sections:
        hits = [w for w in TOPICS[section] if has_word(text, w)]
        if hits:
            item.sections.append(section)
            item.words.extend(hits)
    item.question = bool(QUESTION.search(text))
    item.mentions_publick = "publick" in text.lower()
    return item


def collect(towns: list[Town], fetcher: Fetcher, since: datetime) -> list[Item]:
    items: dict[str, Item] = {}
    feeds: dict[tuple[str, bool], list[dict]] = {}

    def feed(sub: str, comments: bool) -> list[dict]:
        if (sub, comments) not in feeds:
            print(f"  r/{sub}{' comments' if comments else ''}", file=sys.stderr)
            feeds[sub, comments] = reddit_feed(fetcher, sub, comments)
        return feeds[sub, comments]

    def add(town: Town, source: str, kind: str, entry: dict) -> None:
        if entry["when"] < since:
            return
        item = classify(Item(town.slug, source, kind, **entry), town)
        if not (item.sections or item.mentions_publick):
            return
        seen = items.setdefault(f"{town.slug} {item.key()}", item)
        if seen is not item:
            seen.replies += 1
            seen.question |= item.question
            seen.mentions_publick |= item.mentions_publick
            for section in item.sections:
                if section not in seen.sections:
                    seen.sections.append(section)
            seen.words.extend(w for w in item.words if w not in seen.words)

    for town in towns:
        print(town.slug, file=sys.stderr)
        for sub in town.subreddits:
            for comments in (False, True):
                for entry in feed(sub, comments):
                    add(town, f"r/{sub}", "comment" if comments else "post", entry)
        for sub in town.shared:
            for entry in feed(sub, False):
                if any(
                    has_word(f"{entry['title']} {entry['text']}", n) for n in town.names
                ):
                    add(town, f"r/{sub}", "shared", entry)
        queries = [
            f"{n} {w}"
            for n in town.names[:1]
            for w in ("council", "school", "budget", town.state)
        ]
        queries += town.names[1:]
        for query in queries:
            for entry in bluesky(fetcher, query, since):
                text = entry["text"]
                if any(has_word(text, n) for n in town.names) and any(
                    has_word(text, h) for h in town.hints
                ):
                    add(town, "Bluesky", "post", entry)
    return sorted(items.values(), key=lambda i: (i.town, -i.score, -i.when.timestamp()))


def report(towns: list[Town], items: list[Item], since: datetime, days: int) -> str:
    now = datetime.now(timezone.utc)
    lines = [
        f"# Publick radar: {now:%Y-%m-%d}",
        "",
        f"Conversations since {since:%Y-%m-%d} ({days} days) that a town's site could answer. "
        "A question is marked ❓. Read each before replying; reply only where the page really helps.",
        "",
        "| Town | Matches | Questions | Already linking Publick |",
        "|---|---|---|---|",
    ]
    by_town = {t.slug: [i for i in items if i.town == t.slug] for t in towns}
    for town in towns:
        found = by_town[town.slug]
        lines.append(
            f"| {town.name}, {town.state} | {len(found)} | {sum(i.question for i in found)} | "
            f"{sum(i.mentions_publick for i in found)} |"
        )
    for town in towns:
        found = by_town[town.slug]
        lines += ["", f"## {town.name}, {town.state}", ""]
        if not found:
            lines.append("Nothing found.")
            continue
        for item in found:
            pages = ", ".join(
                f"[{town.sections[s]}](https://{town.domain}/{s}/)"
                for s in item.sections
            )
            headline = item.title or item.text
            excerpt = item.text if item.title else ""
            flags = ("❓ " if item.question else "") + (
                "**links Publick** " if item.mentions_publick else ""
            )
            lines.append(f"- {flags}**[{headline[:140]}]({item.url})**  ")
            more = (
                f", and {item.replies} more matching comments" if item.replies else ""
            )
            lines.append(
                f"  {item.source} {item.kind}, {item.when:%b %d}, by {item.author}{more} · score {item.score}  "
            )
            if excerpt:
                lines.append(
                    f"  > {excerpt[:280]}{'…' if len(excerpt) > 280 else ''}  "
                )
            if pages:
                lines.append(
                    f"  → {pages} (matched: {', '.join(dict.fromkeys(item.words))})"
                )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--days", type=int, default=2, help="how far back to look")
    parser.add_argument("--town", action="append", help="only this town (repeatable)")
    parser.add_argument("--config", type=Path, default=ROOT / "scripts" / "radar.toml")
    parser.add_argument(
        "--cache",
        type=Path,
        help="keep fetched feeds here, to rerun without refetching",
    )
    parser.add_argument(
        "--out", type=Path, help="write the report here (default: print it)"
    )
    parser.add_argument("--json", type=Path, help="also write the matches as JSON")
    args = parser.parse_args()

    towns = [t for t in load_towns(args.config) if not args.town or t.slug in args.town]
    since = datetime.now(timezone.utc) - timedelta(days=args.days)
    items = collect(towns, Fetcher(args.cache), since)
    text = report(towns, items, since, args.days)
    if args.out:
        args.out.write_text(text)
        print(f"{len(items)} matches written to {args.out}", file=sys.stderr)
    else:
        print(text)
    if args.json:
        args.json.write_text(
            json.dumps(
                [
                    {**i.__dict__, "when": i.when.isoformat(), "score": i.score}
                    for i in items
                ],
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
