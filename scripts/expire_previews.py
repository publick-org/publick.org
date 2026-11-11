"""Take down the previews of towns' sites that are older than a week.

The Preview workflow (.github/workflows/preview.yml) publishes a preview of a
town's site at preview-<town>.publick.org, in the sites bucket beside the
towns' own sites. Nothing else removes one, so this does, once a day: a
preview last published more than DAYS days ago stops being served, and its
manifests are deleted. Its files are deleted by the daily prune, like any
build's no site uses (the engine's pipeline/deploy.py).

A site is deleted only when both are true:

- its address is preview-<name>.publick.org;
- its live build's robots.txt is the one a preview is built with (the
  engine's build_site --preview), which no town's own site has.

So a town whose own address began with "preview-" would be left alone, and so
is anything under sites/ this doesn't recognize. It lists the bucket by the
"sites/preview-" prefix: its work grows with the previews, not the towns.

    SITES_ENDPOINT=... SITES_BUCKET=... SITES_ACCESS_KEY_ID=... SITES_SECRET_ACCESS_KEY=... \\
        python scripts/expire_previews.py [--days 7] [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

DAYS = 7
PREFIX = "sites/preview-"
PREVIEW_HOST = re.compile(r"preview-[a-z0-9]([a-z0-9-]*[a-z0-9])?\.publick\.org")
# A preview's robots.txt, by its content: files are stored under the SHA-256 of what they hold.
PREVIEW_ROBOTS = hashlib.sha256(b"User-agent: *\nDisallow: /\n").hexdigest()


def list_objects(client, bucket: str, prefix: str) -> list[dict]:
    return [o for page in client.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix)
            for o in page.get("Contents", [])]


def is_preview(client, bucket: str, host: str) -> bool:
    """Whether the site live at this address was built as a preview: by its robots.txt."""
    body = client.get_object(Bucket=bucket, Key=f"sites/{host}/current.json")["Body"].read()
    manifest = json.loads(body)
    return manifest.get("files", {}).get("robots.txt", {}).get("blob") == PREVIEW_ROBOTS


def expire(client, bucket: str, days: int = DAYS, now: datetime | None = None, dry_run: bool = False) -> dict:
    """Delete each preview last published more than `days` days ago. Returns the addresses deleted, kept, and
    skipped (with why)."""
    now = now or datetime.now(timezone.utc)
    sites: dict[str, list[dict]] = {}
    for o in list_objects(client, bucket, PREFIX):
        sites.setdefault(o["Key"].split("/")[1], []).append(o)
    result: dict = {"deleted": [], "kept": [], "skipped": {}}
    for host, objects in sorted(sites.items()):
        live = next((o for o in objects if o["Key"] == f"sites/{host}/current.json"), None)
        if not PREVIEW_HOST.fullmatch(host):
            result["skipped"][host] = "not a preview's address"
        elif live is None:
            result["skipped"][host] = "no live build"
        elif now - live["LastModified"] <= timedelta(days=days):
            result["kept"].append(host)
        elif not is_preview(client, bucket, host):
            result["skipped"][host] = "its robots.txt isn't a preview's"
        else:
            if not dry_run:
                # The live manifest first, so the preview stops being served even if a later deletion fails.
                client.delete_object(Bucket=bucket, Key=live["Key"])
                rest = [o["Key"] for o in objects if o["Key"] != live["Key"]]
                for i in range(0, len(rest), 1000):
                    response = client.delete_objects(Bucket=bucket, Delete={
                        "Objects": [{"Key": k} for k in rest[i:i + 1000]], "Quiet": True})
                    if response.get("Errors"):
                        raise SystemExit(f"::error::{len(response['Errors'])} deletions failed under sites/{host}/, "
                                         f"e.g. {response['Errors'][0].get('Key')}")
            result["deleted"].append(host)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--days", type=int, default=DAYS, help="how long a preview stays up after it's published")
    parser.add_argument("--dry-run", action="store_true", help="say what would be deleted, and delete nothing")
    args = parser.parse_args()
    if args.days < 1:
        parser.error("--days must be at least 1")
    import boto3
    client = boto3.client("s3", endpoint_url=os.environ["SITES_ENDPOINT"], region_name="auto",
                          aws_access_key_id=os.environ["SITES_ACCESS_KEY_ID"],
                          aws_secret_access_key=os.environ["SITES_SECRET_ACCESS_KEY"])
    result = expire(client, os.environ["SITES_BUCKET"], days=args.days, dry_run=args.dry_run)
    for host in result["deleted"]:
        print(f"{'Would delete' if args.dry_run else 'Deleted'} {host}: last published more than {args.days} days ago.")
    for host in result["kept"]:
        print(f"Kept {host}.")
    for host, why in result["skipped"].items():
        print(f"::warning::Left sites/{host}/ alone: {why}.")
    if not (result["deleted"] or result["kept"] or result["skipped"]):
        print("No previews.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
