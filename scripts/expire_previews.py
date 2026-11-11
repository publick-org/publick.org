"""Take down the previews of towns' sites that are older than a week.

The Preview workflow (.github/workflows/preview.yml) publishes a preview of a
town's site at preview-<town>.publick.org, in the sites bucket beside the
towns' own sites. Nothing else removes one, so this does, once a day: a
preview last published more than DAYS days ago stops being served, and its
manifests are deleted. Its files are deleted by the daily prune, like any
build's no site uses (the engine's pipeline/deploy.py).

A site is deleted only when both are true:

- its address is preview-<name>.publick.org;
- its live build's robots.txt (its newest build's, when a deletion was cut
  short and left no live one) is the one a preview is built with (the
  engine's build_site --preview), which no town's own site has.

So a town whose own address began with "preview-" would be left alone, and so
is anything under sites/ this doesn't recognize: only a site's own manifests
(current.json, builds/<build>.json) are ever deleted. It lists the bucket by
the "sites/preview-" prefix: its work grows with the previews, not the towns.

Each site is listed again just before it is judged, so one published again
while this runs is kept. One site's failure (a manifest that can't be read, a
deletion refused) doesn't stop the others: each is reported as it happens,
and the run fails at the end if any did.

--check-site DIR is for the Preview workflow, before it publishes: it fails
unless DIR was built as a preview, by the same test, so that nothing is
published at a preview's address that this would later refuse to take down.

    SITES_ENDPOINT=... SITES_BUCKET=... SITES_ACCESS_KEY_ID=... SITES_SECRET_ACCESS_KEY=... \\
        python scripts/expire_previews.py [--days 7] [--dry-run]
    python scripts/expire_previews.py --check-site _site
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DAYS = 7
PREFIX = "sites/preview-"
PREVIEW_HOST = re.compile(r"preview-[a-z0-9]([a-z0-9-]*[a-z0-9])?\.publick\.org")
# A site's own manifests, the only objects this deletes.
MANIFEST = re.compile(r"sites/[^/]+/(current\.json|builds/[^/]+\.json)")
# A preview's robots.txt, by its content: files are stored under the SHA-256 of what they hold.
PREVIEW_ROBOTS = hashlib.sha256(b"User-agent: *\nDisallow: /\n").hexdigest()


def list_objects(client, bucket: str, prefix: str) -> list[dict]:
    return [o for page in client.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix)
            for o in page.get("Contents", [])]


def built_as_preview(manifest) -> bool:
    """Whether a build's manifest lists a preview's robots.txt. Anything that isn't a manifest isn't one."""
    files = manifest.get("files") if isinstance(manifest, dict) else None
    robots = files.get("robots.txt") if isinstance(files, dict) else None
    return isinstance(robots, dict) and robots.get("blob") == PREVIEW_ROBOTS


def expire_site(client, bucket: str, host: str, days: int, now: datetime, dry_run: bool = False) -> tuple[str, str]:
    """Judge one preview, from a listing made now, and delete it if it's due. Returns "deleted", "kept" or
    "skipped", and why. Raises when a manifest can't be read or a deletion fails."""
    objects = list_objects(client, bucket, f"sites/{host}/")
    manifests = [o for o in objects if MANIFEST.fullmatch(o["Key"])]
    others = len(objects) - len(manifests)
    left = f"; {others} other objects under it left alone" if others else ""
    if not manifests:
        return "skipped", "no builds" + left
    newest = max(manifests, key=lambda o: o["LastModified"])
    if now - newest["LastModified"] <= timedelta(days=days):
        return "kept", f"last published {newest['LastModified']:%Y-%m-%d}"
    # The live build says what the site is; with none (a deletion cut short), its newest build does.
    live = next((o for o in manifests if o["Key"] == f"sites/{host}/current.json"), None)
    judged = live or newest
    manifest = json.loads(client.get_object(Bucket=bucket, Key=judged["Key"])["Body"].read())
    if not built_as_preview(manifest):
        return "skipped", "its robots.txt isn't a preview's"
    if not dry_run:
        # The live manifest first, so the preview stops being served even if a later deletion fails; the next
        # run finishes one cut short.
        if live:
            client.delete_object(Bucket=bucket, Key=live["Key"])
        rest = [o["Key"] for o in manifests if o is not live]
        for i in range(0, len(rest), 1000):
            response = client.delete_objects(Bucket=bucket, Delete={
                "Objects": [{"Key": k} for k in rest[i:i + 1000]], "Quiet": True})
            if response.get("Errors"):
                raise RuntimeError(f"{len(response['Errors'])} deletions failed, e.g. {response['Errors'][0].get('Key')}")
    return "deleted", f"last published {newest['LastModified']:%Y-%m-%d}" + left


def expire(client, bucket: str, days: int = DAYS, now: datetime | None = None, dry_run: bool = False,
           say=print) -> dict:
    """Delete each preview last published more than `days` days ago, saying what happens to each as it
    happens. Returns the addresses deleted, kept, skipped (with why), and failed (with the error)."""
    now = now or datetime.now(timezone.utc)
    hosts = sorted({o["Key"].split("/")[1] for o in list_objects(client, bucket, PREFIX) if o["Key"].count("/") >= 2})
    result: dict = {"deleted": [], "kept": [], "skipped": {}, "failed": {}}
    for host in hosts:
        if not PREVIEW_HOST.fullmatch(host):
            outcome, why = "skipped", "not a preview's address"
        else:
            try:
                outcome, why = expire_site(client, bucket, host, days, now, dry_run)
            except Exception as e:  # noqa: BLE001 (one site's failure, whatever it is, doesn't stop the others)
                outcome, why = "failed", f"{type(e).__name__}: {e}"
        if outcome == "deleted":
            result["deleted"].append(host)
            say(f"{'Would delete' if dry_run else 'Deleted'} {host} ({why}).")
        elif outcome == "kept":
            result["kept"].append(host)
            say(f"Kept {host} ({why}).")
        elif outcome == "skipped":
            result["skipped"][host] = why
            say(f"::warning::Left sites/{host}/ alone: {why}.")
        else:
            result["failed"][host] = why
            say(f"::error::sites/{host}/: {why}")
    return result


def check_site(site_dir: Path) -> bool:
    """Whether a built site is a preview, by the test expire() uses: its robots.txt."""
    robots = site_dir / "robots.txt"
    return robots.is_file() and hashlib.sha256(robots.read_bytes()).hexdigest() == PREVIEW_ROBOTS


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--days", type=int, default=DAYS, help="how long a preview stays up after it's published")
    parser.add_argument("--dry-run", action="store_true", help="say what would be deleted, and delete nothing")
    parser.add_argument("--check-site", type=Path, metavar="DIR", help="only check that the site built in DIR is a "
                        "preview, as this would recognize one; needs no keys")
    args = parser.parse_args()
    if args.check_site:
        if check_site(args.check_site):
            print(f"{args.check_site} was built as a preview.")
            return 0
        print(f"::error::{args.check_site} wasn't built as a preview (its robots.txt isn't a preview's): it isn't "
              "published at a preview's address, where nothing would take it down.")
        return 1
    if args.days < 1:
        parser.error("--days must be at least 1")
    import boto3
    client = boto3.client("s3", endpoint_url=os.environ["SITES_ENDPOINT"], region_name="auto",
                          aws_access_key_id=os.environ["SITES_ACCESS_KEY_ID"],
                          aws_secret_access_key=os.environ["SITES_SECRET_ACCESS_KEY"])
    result = expire(client, os.environ["SITES_BUCKET"], days=args.days, dry_run=args.dry_run)
    if not any(result.values()):
        print("No previews.")
    return 1 if result["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
