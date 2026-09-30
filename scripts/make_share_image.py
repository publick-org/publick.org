"""Draw publick.org's share image: the card a link to the homepage shows on
Substack, social media, or in a message.

A 1200 x 630 PNG of the homepage's masthead (its icon, name, and line), in
its own fonts and colors, written to home/share/publick.png. It also updates
the image's ?v= in home/index.html, so sites that cache a card by its image
address pick up the new one. Each town's site has its own card (the engine's
pipeline/make_share_image.py). Run this again after changing the masthead.
Needs Playwright (the engine's requirements-dev.txt).

    python scripts/make_share_image.py
"""

from __future__ import annotations

import base64
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = ROOT / "home"
IMAGE = HOME / "share" / "publick.png"
IMAGE_URL = "https://publick.org/share/publick.png"


def data_url(path: Path, mime: str) -> str:
    # Inline, because a page set from a string can't load local files.
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def share_html() -> str:
    """The masthead, in home/css/site.css's colors, with what each town's site covers."""
    fonts = HOME / "fonts"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: "Public Sans"; font-weight: 400; src: url("{data_url(fonts / "public-sans-400.woff2", "font/woff2")}"); }}
@font-face {{ font-family: "Source Serif 4"; font-weight: 700; src: url("{data_url(fonts / "source-serif-4-700.woff2", "font/woff2")}"); }}
html, body {{ margin: 0; width: 1200px; height: 630px; }}
body {{ font-family: "Public Sans", sans-serif; background: #faf7f0; color: #1c1a17; box-sizing: border-box;
  display: flex; flex-direction: column; justify-content: center; padding: 0 96px; }}
.brand {{ display: flex; align-items: center; gap: 40px; }}
.mark {{ width: 150px; height: 150px; }}
.name {{ font-family: "Source Serif 4", serif; font-weight: 700; font-size: 120px; letter-spacing: -0.01em; line-height: 1; }}
.line {{ margin: 32px 0 0; font-size: 44px; }}
.rule {{ margin: 44px 0 0; border-top: 2px solid #2c4a63; border-bottom: 8px double #2c4a63; height: 6px; }}
.covers {{ margin: 36px 0 0; font-size: 34px; line-height: 1.35; color: #5c574f; }}
</style></head><body>
<div class="brand"><img class="mark" src="{data_url(HOME / "favicon.svg", "image/svg+xml")}" alt=""><div class="name">Publick</div></div>
<p class="line">Your town's public record, every day.</p>
<div class="rule"></div>
<p class="covers">Meetings · 311 · Schools · Budget · Housing · Your street</p>
</body></html>"""


def main() -> None:
    from playwright.sync_api import sync_playwright

    IMAGE.parent.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        page.set_content(share_html())
        page.evaluate("document.fonts.ready")
        page.screenshot(path=IMAGE)
        browser.close()
    version = hashlib.sha256(IMAGE.read_bytes()).hexdigest()[:10]
    index = HOME / "index.html"
    page, count = re.subn(rf'{re.escape(IMAGE_URL)}(\?v=[0-9a-f]*)?"', f'{IMAGE_URL}?v={version}"', index.read_text(encoding="utf-8"))
    if not count:
        raise SystemExit(f"home/index.html has no og:image of {IMAGE_URL}")
    index.write_text(page, encoding="utf-8")
    print(f"Wrote {IMAGE.relative_to(ROOT)} (v={version})")


if __name__ == "__main__":
    main()
