"""The towns whose weekly digest the scheduler Worker emails: its DIGEST_TOWNS.

A town's digest is on when its config has a [digest] table: the engine then
shows the signup form on its /digest/ page (pipeline/digest.py signup), with the
settings defaults/network.toml fills in. The list is every such town's hostname
([site] domain), read with the engine's own config reader, so a town whose form
is shown is sent its issues, and one without isn't. It's written nowhere by
hand: .github/workflows/worker.yml passes it to the scheduler when it deploys it,
and makes each town's Buttondown tag from it.

--check fails when the list and the configs could disagree: a town with a
[digest] table whose signup is off (or one without the table whose signup is
on), or a DIGEST_TOWNS of its own in wrangler.scheduler.toml, which the deploy
would override. The network workflow runs it on every pull request.

    PYTHONPATH=../publick-engine python scripts/digest_towns.py            # the hostnames, comma-separated
    PYTHONPATH=../publick-engine python scripts/digest_towns.py --check    # exits 1 on a disagreement
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

# The town configs are read with the engine's config reader, and their layers in defaults/: the engine is on
# PYTHONPATH, as for building a town. Standard library only, so it runs without the engine's packages.
from pipeline import digest
from pipeline.network import TOWNS, town_config, town_dirs

ROOT = Path(__file__).resolve().parent.parent
SCHEDULER_CONFIG = "wrangler.scheduler.toml"


def own_table(root: Path, name: str) -> bool:
    """Whether the town's own config file (not its layers) has a [digest] table."""
    path = next((root / TOWNS / name / "config").glob("*.toml"))
    with path.open("rb") as f:
        return "digest" in tomllib.load(f)


def towns(root: Path) -> list[tuple[str, str, bool]]:
    """Each town's folder, hostname, and whether its digest is on (the engine shows its signup form)."""
    rows = []
    for name in town_dirs(root):
        config = town_config(root, name)
        rows.append((name, config["site"]["domain"].lower(), digest.signup(config) is not None))
    return rows


def digest_hosts(rows: list[tuple[str, str, bool]]) -> list[str]:
    """The hostnames of the towns whose digest is on (rows, from towns()), sorted."""
    return sorted(host for _, host, on in rows if on)


def problems(root: Path, rows: list[tuple[str, str, bool]]) -> list[str]:
    """Why the list could disagree with the towns' configs (rows, from towns()); empty when it can't."""
    found = []
    for name, host, on in rows:
        table = own_table(root, name)
        if table and not on:
            found.append(f"towns/{name} has a [digest] table, but its signup is off, so {host} isn't in the list: "
                         "leave the table out to turn the digest off.")
        elif on and not table:
            found.append(f"towns/{name} has no [digest] table, but its signup is on, so {host} is in the list.")
    hosts = [host for _, host, on in rows if on]
    found += [f"{host} is the domain of more than one town with a digest." for host in sorted(set(hosts))
              if hosts.count(host) > 1]
    scheduler = root / SCHEDULER_CONFIG
    if scheduler.is_file():
        with scheduler.open("rb") as f:
            if "DIGEST_TOWNS" in tomllib.load(f).get("vars", {}):
                found.append(f"{SCHEDULER_CONFIG} sets DIGEST_TOWNS. It's made from the towns' configs when the "
                             "scheduler is deployed (scripts/digest_towns.py), which replaces it: take it out.")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="the network repository (default: this one)")
    parser.add_argument("--check", action="store_true", help="check the list can't disagree with the configs")
    args = parser.parse_args()
    rows = towns(args.root)
    if args.check:
        found = problems(args.root, rows)
        for problem in found:
            print(f"::error::{problem}")
        if not found:
            print(f"The digest's {len(digest_hosts(rows))} towns agree with the towns' configs.")
        return 1 if found else 0
    print(",".join(digest_hosts(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
