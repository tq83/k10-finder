# Updating the live K10 Finder

- **Live site:** https://k10-finder.onrender.com (Render free static site `k10-finder`, service id `srv-db9fuhqjnfac73c5i370`, workspace "My Workspace" `tea-db5i8dbbc2fs73906igg`)
- **Repo:** https://github.com/tq83/k10-finder (public, branch `main`). The local clone is `/workspace/k10-dashboard`.
- **Deploys:** there is no build step; the repo root is served as-is, and a deploy takes about 10 seconds. **Pushing alone does not deploy yet**, because Render's GitHub app isn't connected to this repo (it is cloned as a public URL), so Render never hears about the push. Until that is fixed, a run must trigger the deploy itself:
  - **Agent run (works now):** after `publish.sh` exits **3**, call Render MCP `trigger_deploy` with `{"serviceId":"srv-db9fuhqjnfac73c5i370"}` (it deploys the newest commit on `main`), then run `./publish.sh --wait`.
  - **Fully scripted (optional):** put `RENDER_DEPLOY_HOOK_URL=...` (from Render dashboard → k10-finder → Settings → Deploy Hook) in `~/.k10-finder.env`. `publish.sh` then deploys by itself.
  - **Real auto-deploy (optional):** give Render's GitHub app access to `tq83/k10-finder` (GitHub → Settings → Applications → Render → Configure → add repo). After that, a push deploys on its own and `publish.sh` exits 0.

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

# 3. Publish (validates JSON, saves expiring photos locally via fetch_photos.py, runs sync_inline.py, commits, pushes, waits until the live site serves the new files):
./publish.sh "Alert run $(TZ=America/Phoenix date '+%b %-d %-I%p')"
rm -f new.json
```

`publish.sh` exit codes:
- **0**: live, or nothing changed. Live means the site's `listings.json` and `index.html` byte-match the local files.
- **1**: bad JSON.
- **2**: deployed but not live after about 10 minutes. Check Render MCP `list_deploys(serviceId="srv-db9fuhqjnfac73c5i370", limit=1)` and `list_logs`.
- **3**: pushed, but nothing deployed. Call `trigger_deploy(serviceId="srv-db9fuhqjnfac73c5i370")`, then `./publish.sh --wait`.

If a run is interrupted after the push, rerunning `./publish.sh` is safe. It sees no new commit, notices the live site differs, and goes back through the deploy step.

## Photos from expiring sources (automatic)
Image links from Facebook Marketplace (fbcdn) are signed and stop working within about a day, and Craigslist images disappear when the ad comes down. `publish.sh` therefore runs **`fetch_photos.py`** before every publish:
- Every fbcdn / Craigslist photo URL is downloaded, resized to at most 1200 px wide, saved as JPEG quality 78 at `photos/<listing-id>/<hash>.jpg`, and `imageUrls` is changed to that relative path. Rerunning is safe. Craigslist photos are fetched at 1200x900 when available.
- A photo that has already expired (403) is dropped. If a Facebook or Craigslist listing is left with no photos, the script re-reads the listing page. For Facebook that is the public link-preview `og:image`, usually **only 1 photo**. For Craigslist it is the full gallery. If that also fails, the card shows the placeholder.
- Folders for listings no longer in `listings` are deleted, which keeps the repo small (about 150 KB per photo).
- `merge_listings.py` never replaces locally saved photos with fresh remote links.
- **For the alert run:** collect the Facebook photo URLs and publish in the **same run**, because the links can expire before the next run. Other hosts (BaT, ClassicCars.com, dealer CDNs) stay hotlinked.
- To run it by hand: `python3 fetch_photos.py [--dry-run]`.

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
- Pushing uses the box's `gh` login (account `tq83`) through a credential helper set in this repo only (`credential.https://github.com.helper = !gh auth git-credential`). If a push fails with an auth error, `gh auth status` will show it; Tarry would need to log in again.
