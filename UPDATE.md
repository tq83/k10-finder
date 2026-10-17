# Updating the live K10 Finder

- **Live site:** https://k10-finder.onrender.com (Render free static site `k10-finder`, service id `srv-db9fuhqjnfac73c5i370`, workspace "My Workspace" `tea-db5i8dbbc2fs73906igg`)
- **Repo:** https://github.com/tq83/k10-finder (public, branch `main`). The local clone is `/workspace/k10-dashboard`.
- **Deploys:** Render auto-deploys every push to `main`. There is no build step; the repo root is served as-is. A deploy is usually live within about a minute.

## What each alert run does (non-interactive)

```bash
cd /workspace/k10-dashboard
git pull -q --rebase origin main            # in case anything changed elsewhere

# 1. Write ONLY the new or changed trucks from this run to a batch file (gitignored name):
#    /workspace/k10-dashboard/new.json  ->  {"listings":[...], "comps":[...]}   (comps optional)
#    Each listing uses the listings.json schema (see README.md). url is required and is the dedupe key.
#    Leave out id and firstSeen; the script assigns them.

# 2. Merge (preview first if you like):
python3 merge_listings.py new.json --dry-run
python3 merge_listings.py new.json \
    --remove <url-of-listing-that-is-gone> ... \
    --sold   <url>=<final price> ...           # optional: moves it into comps as sold today

# 3. Publish (validates JSON, runs sync_inline.py, commits, pushes, waits until the live site serves the new files):
./publish.sh "Alert run $(TZ=America/Phoenix date '+%b %-d %-I%p')"
rm -f new.json
```

`publish.sh` exit codes: **0** = live (or nothing changed), **1** = bad JSON, **2** = pushed but not live after about 10 minutes. On 2, check the deploy with Render MCP `list_deploys(serviceId="srv-db9fuhqjnfac73c5i370", limit=1)`. If no deploy started, run `trigger_deploy(serviceId="srv-db9fuhqjnfac73c5i370")`.

## How merge_listings.py treats the data
| Situation | Result |
|---|---|
| URL already in `listings` (compared ignoring `www.`, query string and trailing slash) | Non-empty fields from the batch overwrite the old ones, e.g. a new bid `price` or an updated `auctionEnd`. `id`, `firstSeen` and `url` are kept. |
| New URL | Gets the next `k10-NN` id and `firstSeen` = now (Arizona time). The page shows a **NEW** badge for 24 hours. |
| Auction whose `auctionEnd` was more than 2 hours ago | Moved automatically from `listings` to `removed` with reason "auction ended". If you know the hammer price, use `--sold url=price` instead so it becomes a comp. |
| `--remove URL` | Moved to `removed` (a buy-now ad that sold or was taken down). |
| `--sold URL=PRICE` | Added to `comps` with today's date and moved to `removed`. |
| Batch comps | Appended to `comps`, deduped by URL. |
| Always | `updated` is set to now, and `imageUrl` is set to `imageUrls[0]`. |

The `removed` array keeps the last 200 entries as history. The page ignores it, but it stops a dropped listing from coming back silently. If a later run finds a removed URL live again (for example a relist), it is added as a new listing.

## Checks before publishing
- Prices: `priceType: "bid"` for auctions (the page labels these "Current bid · not final") and `"ask"` for buy-now.
- Set `mileage: null` when the odometer can't be trusted (TMU, exempt, placeholder) and explain why in `mileageNote`.
- Give `lat`/`lng` for the city, or the state's center if only the state is known. `state` is a 2-letter code (the AZ-only filter uses it).
- Up to 10 `imageUrls` taken from the listing page. If none can be fetched, leave the array empty and the page shows a placeholder.
- `valueRating`: `great` / `fair` / `pricey` vs the comps.

## Manual / emergency
- Edit `listings.json` by hand, then run `./publish.sh`. It always runs `sync_inline.py`.
- Roll back with `git revert HEAD && git push`, which Render redeploys.
- Pushing uses the box's `gh` login (account `tq83`). If a push fails with an auth error, `gh auth status` will show it; Tarry would need to log in again.
