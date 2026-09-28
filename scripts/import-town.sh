#!/usr/bin/env bash
# Copy a town's repository into towns/<folder>/: its config/, data/, and
# site/ (its own static files). Replaces what's there, so it can be run again
# to take the latest data just before the town's own repository is retired.
# Usage: scripts/import-town.sh <folder> [<owner>/<repo>]
#   e.g. scripts/import-town.sh gloucester-ma   (repository publick-org/gloucester-ma)
set -euo pipefail
folder="$1"
repo="${2:-publick-org/$folder}"
root="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
git clone --quiet --depth 1 "https://github.com/$repo" "$tmp/town"
if [ "$(find "$tmp/town/config" -name '*.toml' | wc -l)" -ne 1 ]; then
  echo "$repo should have exactly one config/*.toml" >&2
  exit 1
fi
dest="$root/towns/$folder"
mkdir -p "$dest"
for part in config data site; do
  rm -rf "${dest:?}/$part"
  if [ -d "$tmp/town/$part" ]; then
    cp -R "$tmp/town/$part" "$dest/$part"
  fi
done
echo "Copied $repo at $(git -C "$tmp/town" rev-parse --short HEAD) into towns/$folder."
