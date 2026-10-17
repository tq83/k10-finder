# K10 Finder dashboard

A single-page dashboard for Tarry's K10 hunt: square body 4x4s, $20k–$50k, buyer in Phoenix, AZ.

```
k10-dashboard/
├── index.html      the app (HTML, CSS and JS in one file, plus an inline copy of the data)
├── listings.json   the data (source of truth)
├── sync_inline.py  copies listings.json into index.html's inline fallback
├── preview*.png    headless screenshots (desktop, lightbox, mobile)
└── README.md
```

## Opening it
- **Double-click `index.html`.** Browsers block `fetch()` on `file://`, so the page reads the inline copy of the data embedded in the HTML. The header shows "from inline copy".
- **Or serve the folder** (`python3 -m http.server 8000` in this folder, then open http://localhost:8000). The page then loads `listings.json` live and the header shows "from listings.json". If that fails, it uses the inline copy.

Chart.js, Leaflet and Google Fonts load from CDNs. Offline, the chart and map panels show a short notice, fonts fall back to system fonts, and the cards, filters, lightbox and comps table still work. Map tiles are Esri Dark Gray Canvas, which needs no API key.

## Updating the data
1. Edit `listings.json` (schema below). Set `updated` to the time of the check as an ISO time with an offset, for example `2026-10-17T08:00:00-07:00`.
2. Run `python3 sync_inline.py`. **This step is required**, or the double-click version will keep showing old data. The script checks the JSON and rewrites the block between `<!--K10-DATA-START-->` and `<!--K10-DATA-END-->` in `index.html`.
3. Reload the page.

### Listing fields
| field | notes |
|---|---|
| `id` | unique and stable, e.g. `k10-13` |
| `year`, `make`, `model`, `trim` | the title is built from year + make + model, and trim goes underneath |
| `engine`, `transmission` | free text |
| `price` | number. Current bid for auctions, asking price otherwise |
| `priceType` | `"bid"` (auction; labeled "Current bid · not final") or `"ask"` (buy-now) |
| `auctionEnd` | ISO time with offset, or `null`. Drives the countdown and the "Ending soonest" stat |
| `mileage` | number, or **`null` when not trustworthy** (TMU, exempt, placeholder). Listings with `null` are left off the price-vs-mileage chart |
| `mileageNote` | shown under the mileage, e.g. "216 on replacement odometer (TMU)" |
| `location`, `state` | `state` is the 2-letter code. The "Arizona only" toggle uses `state === "AZ"` |
| `lat`, `lng` | map pin and distance from Phoenix. Use the state's center if only the state is known |
| `source` | e.g. `Bring a Trailer` (shown as "BaT"), `Cars & Bids`, `Hemmings`, `eBay`, `Craigslist`, `Facebook Marketplace`, `ClassicCars.com`, `Classic Car Deals` |
| `url` | target of the "View listing" button |
| `imageUrls` | array of photo URLs (up to ~10). Powers the card carousel and the lightbox |
| `imageUrl` | first photo, kept for compatibility. Used only if `imageUrls` is empty |
| `condition` | array of chips. Words like *rust* or *title* show red, *original* / *one owner* / *rust-free* show green, and *LS* / *swap* / *lift* show gold |
| `redFlags` | text shown in the red callout, or `""` |
| `notes` | short free text |
| `valueRating` | `"great"`, `"fair"` or `"pricey"` (text like "Great Deal" also works) |
| `firstSeen` | ISO time. Listings newer than the first batch and found within 24h of `updated` get a **NEW** badge |

### Comp fields
`year, trim, soldPrice, soldDate (YYYY-MM-DD), mileage (number or null), mileageNote (optional), source, url`

## Photos
- Photos are hotlinked from the listing sites (BaT, ClassicCars.com, totalwebmanager.com for Classic Car Deals, and Craigslist) with `referrerpolicy="no-referrer"`. A photo that fails to load is replaced by a styled placeholder.
- Craigslist photos expire when the ad is deleted, and that is expected.

## Features
- **Header stats:** active listings, median asking price (buy-now only), cheapest ask, and the auction ending soonest, with a live countdown.
- **Left sidebar filters:** search, auction or buy-now, AZ only, ending within 48 hrs, hide title issues, price, year, max mileage, value rating and source. Sort by best value, ending soonest, price, year, mileage, distance from Phoenix, or newest found.
- **Cards:** swipe or arrow-key photo carousel with dots and a photo count. Clicking a photo opens a full-screen lightbox with arrows, ←/→/Esc keys, swipe, thumbnails, and the title, price and "View listing" button.
- **Right column:** price-vs-mileage scatter (circles are asks, triangles are current bids, diamonds are sold comps). Clicking a point jumps to its card. The Southwest map has a Phoenix marker and a Southwest/All toggle.
- **Sold comps table** with median and range.
- All times show in Arizona time (MST, no daylight saving).

## Hosting
Live at **https://k10-finder.onrender.com** (Render free static site, auto-deploys from https://github.com/tq83/k10-finder). See **UPDATE.md** for the alert-run update path (`merge_listings.py` → `publish.sh`).
