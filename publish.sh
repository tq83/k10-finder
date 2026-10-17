#!/usr/bin/env bash
# Publish K10 Finder: validate data, refresh the inline copy, commit, push, and wait for the live site.
# Usage: ./publish.sh ["commit message"]
set -euo pipefail
cd "$(dirname "$0")"
SITE="${K10_SITE_URL:-https://k10-finder.onrender.com}"
MSG="${1:-Update listings $(TZ=America/Phoenix date '+%Y-%m-%d %H:%M MST')}"

python3 -m json.tool listings.json >/dev/null || { echo "listings.json is not valid JSON" >&2; exit 1; }
python3 sync_inline.py
WANT=$(python3 -c 'import json;print(json.load(open("listings.json"))["updated"])')

git add -A
if git diff --cached --quiet; then echo "Nothing changed; not publishing."; exit 0; fi
git commit -q -m "$MSG"
git push -q origin main
echo "Pushed $(git rev-parse --short HEAD). Render auto-deploys on push; waiting for $SITE ..."

for i in $(seq 1 40); do   # up to ~10 minutes
  GOT=$(curl -fsS -m 20 "$SITE/listings.json?ts=$(date +%s)" 2>/dev/null | python3 -c 'import json,sys;print(json.load(sys.stdin).get("updated",""))' 2>/dev/null || true)
  if [ "$GOT" = "$WANT" ]; then
    N=$(curl -fsS -m 20 "$SITE/listings.json?ts=$(date +%s)" | python3 -c 'import json,sys;print(len(json.load(sys.stdin)["listings"]))')
    echo "LIVE: $SITE is serving updated=$WANT with $N listings."; exit 0
  fi
  sleep 15
done
echo "Pushed, but $SITE still isn't serving updated=$WANT after ~10 min. Check deploys (Render MCP list_deploys for the k10-finder service), or trigger_deploy." >&2
exit 2
