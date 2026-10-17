#!/usr/bin/env bash
# Publish K10 Finder: validate data, refresh the inline copy, commit, push, deploy, verify live.
#   ./publish.sh ["commit message"]   full publish
#   ./publish.sh --wait               only wait/verify that the live site matches local files
# Exit: 0 live (or nothing to do) | 1 bad JSON | 2 pushed+deployed but not live after ~10 min
#       3 pushed, but no deploy started: call Render MCP trigger_deploy(serviceId=srv-db9fuhqjnfac73c5i370),
#         then run ./publish.sh --wait
set -euo pipefail
cd "$(dirname "$0")"
SITE="${K10_SITE_URL:-https://k10-finder.onrender.com}"
# Optional Render deploy hook (Render dashboard > k10-finder > Settings > Deploy Hook). Keep it out of git.
[ -f "$HOME/.k10-finder.env" ] && . "$HOME/.k10-finder.env"
HOOK="${RENDER_DEPLOY_HOOK_URL:-}"

is_live() {
  local a b
  a=$(curl -fsS -m 20 "$SITE/listings.json" 2>/dev/null | sha256sum | cut -d' ' -f1)
  # Check the plain URLs (no cache-buster): that is what a phone gets from the CDN edge cache.
  b=$(curl -fsS -m 20 "$SITE/" 2>/dev/null | sha256sum | cut -d' ' -f1)
  [ "$a" = "$(sha256sum listings.json | cut -d' ' -f1)" ] && [ "$b" = "$(sha256sum index.html | cut -d' ' -f1)" ]
}
report_live() {
  local n upd
  n=$(curl -fsS -m 20 "$SITE/listings.json?ts=$(date +%s)" | python3 -c 'import json,sys;d=json.load(sys.stdin);print(len(d["listings"]),d["updated"])')
  echo "LIVE: $SITE serving ${n% *} listings, updated ${n#* }"
}
wait_live() {  # $1 = tries (15s apart)
  for _ in $(seq 1 "$1"); do is_live && { report_live; return 0; }; sleep 15; done; return 1
}

if [ "${1:-}" = "--wait" ]; then wait_live 40 && exit 0; echo "Not live after ~10 min." >&2; exit 2; fi

MSG="${1:-Update listings $(TZ=America/Phoenix date '+%Y-%m-%d %H:%M MST')}"
python3 -m json.tool listings.json >/dev/null || { echo "listings.json is not valid JSON" >&2; exit 1; }
# Save photos from expiring hosts (Facebook, Craigslist) into photos/ and repoint imageUrls. Never blocks a publish.
python3 fetch_photos.py || echo "WARNING: fetch_photos.py failed; publishing with existing photo links" >&2
python3 -m json.tool listings.json >/dev/null || { echo "listings.json is not valid JSON after fetch_photos" >&2; exit 1; }
python3 sync_inline.py

git add -A
if git diff --cached --quiet; then
  if is_live; then echo "Nothing changed; live site already current."; exit 0; fi
  echo "No new commit, but live site differs from local files; deploying latest commit."
else
  git commit -q -m "$MSG"
fi
git push -q origin main
echo "Pushed $(git rev-parse --short HEAD)."

if [ -n "$HOOK" ]; then
  curl -fsS -m 30 -X POST "$HOOK" >/dev/null && echo "Deploy hook triggered."
  wait_live 40 && exit 0
  echo "Not live after ~10 min. Check Render list_deploys for srv-db9fuhqjnfac73c5i370." >&2; exit 2
fi

# No hook: auto-deploy may pick the push up (if the Render GitHub app has access to the repo).
if wait_live 8; then exit 0; fi
echo "DEPLOY_NEEDED: pushed but Render hasn't deployed it. Call Render MCP trigger_deploy(serviceId=\"srv-db9fuhqjnfac73c5i370\"), then run ./publish.sh --wait" >&2
exit 3
