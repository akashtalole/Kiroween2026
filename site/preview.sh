#!/usr/bin/env bash
# Assemble the site into an output directory by copying site/ and the markdown docs.
# Usage: bash site/preview.sh [outdir]   (default: _site) then: python3 -m http.server -d _site 8000
set -euo pipefail
OUT="${1:-_site}"
rm -rf "$OUT"
mkdir -p "$OUT/content/docs"
cp -r site/. "$OUT/"
rm -f "$OUT/preview.sh" "$OUT/README.md"
cp docs/*.md "$OUT/content/docs/"
cp PLAN.md "$OUT/content/docs/PLAN.md"
echo "Site assembled in $OUT"
