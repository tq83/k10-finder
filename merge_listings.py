#!/usr/bin/env python3
"""Merge a batch of newly found K10 listings into listings.json.

Usage:
  python3 merge_listings.py new.json                 # merge a batch (see UPDATE.md for format)
  python3 merge_listings.py new.json --remove URL    # also drop listings that are gone/sold elsewhere
  python3 merge_listings.py --sold URL=PRICE         # move a listing into comps as sold today
  python3 merge_listings.py --dry-run new.json       # show what would change, write nothing

Rules:
  * Dedupe by normalized URL (scheme/host lowercased, query/fragment and trailing slash dropped).
  * Existing listing  -> updates price/bid, auctionEnd, mileage, redFlags, etc. with any non-empty
                         fields from the batch; keeps its id and firstSeen.
  * New listing       -> gets the next id (k10-NN) and firstSeen = now (Arizona time) unless given.
  * Auctions whose auctionEnd is more than 2 hours in the past are moved out of `listings`
    into `removed` (reason "auction ended"). The 2h grace keeps a just-ended lot visible briefly.
  * --remove / --sold also move listings into `removed`; --sold adds a comp too.
  * `updated` is set to now. Comps in the batch are appended, deduped by URL (or year+trim+date).
  * imageUrl is always kept equal to imageUrls[0].
"""
import json, sys, argparse, pathlib, re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

AZ = timezone(timedelta(hours=-7))  # Arizona: MST all year, no DST
HERE = pathlib.Path(__file__).resolve().parent
DB = HERE / "listings.json"
GRACE = timedelta(hours=2)

def now_iso(): return datetime.now(AZ).replace(microsecond=0).isoformat()
def norm(u):
    if not u: return ""
    p = urlsplit(u.strip())
    return f"{p.netloc.lower().removeprefix('www.')}{p.path.rstrip('/')}".lower()
def parse(ts):
    try:
        d = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=AZ)
    except Exception: return None

DEFAULTS = dict(year=None, make="Chevrolet", model="K10", trim="", engine="", transmission="", price=None,
                priceType="ask", auctionEnd=None, mileage=None, mileageNote="", location="", state="",
                lat=None, lng=None, source="", url="", imageUrl=None, imageUrls=[], condition=[],
                redFlags="", notes="", valueRating="fair", firstSeen=None)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", nargs="?")
    ap.add_argument("--remove", nargs="*", default=[], metavar="URL")
    ap.add_argument("--sold", nargs="*", default=[], metavar="URL=PRICE")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    db = json.loads(DB.read_text())
    db.setdefault("listings", []); db.setdefault("comps", []); db.setdefault("removed", [])
    now, stamp = datetime.now(AZ), now_iso()
    by_url = {norm(l["url"]): l for l in db["listings"]}
    nums = [int(m.group(1)) for l in db["listings"] + db["removed"] if (m := re.match(r"k10-(\d+)$", str(l.get("id", ""))))]
    nxt = max(nums, default=0) + 1
    added, updated, removed = [], [], []

    batch = {}
    if a.batch:
        batch = json.loads(pathlib.Path(a.batch).read_text())
        if isinstance(batch, list): batch = {"listings": batch}
    for nl in batch.get("listings", []):
        if not nl.get("url"): print("skip (no url):", nl.get("trim") or nl, file=sys.stderr); continue
        k = norm(nl["url"])
        if k in by_url:
            cur = by_url[k]
            changed = [f for f, v in nl.items() if f not in ("id", "firstSeen", "url") and v not in (None, "", []) and cur.get(f) != v]
            for f in changed: cur[f] = nl[f]
            if changed: updated.append((cur["id"], changed))
        else:
            l = {**DEFAULTS, **{f: v for f, v in nl.items() if v is not None}}
            l["id"] = nl.get("id") or f"k10-{nxt:02d}"; nxt += 1
            l["firstSeen"] = nl.get("firstSeen") or stamp
            db["listings"].append(l); by_url[k] = l; added.append(l["id"])

    def drop(l, reason):
        db["listings"].remove(l); by_url.pop(norm(l["url"]), None)
        db["removed"].append({"id": l["id"], "year": l.get("year"), "make": l.get("make"), "model": l.get("model"),
                              "trim": l.get("trim"), "lastPrice": l.get("price"), "url": l["url"],
                              "reason": reason, "removedAt": stamp})
        removed.append((l["id"], reason))

    for u in a.remove:
        l = by_url.get(norm(u))
        if l: drop(l, "removed (gone/sold elsewhere)")
        else: print("not found:", u, file=sys.stderr)
    for s in a.sold:
        u, _, p = s.rpartition("=")
        l = by_url.get(norm(u))
        if not l: print("not found:", u, file=sys.stderr); continue
        db["comps"].append({"year": l.get("year"), "trim": " ".join(x for x in [l.get("model"), l.get("trim")] if x),
                            "soldPrice": int(float(p.replace(",", "").replace("$", ""))), "soldDate": now.date().isoformat(),
                            "mileage": l.get("mileage"), "mileageNote": l.get("mileageNote", ""), "source": l.get("source"), "url": l["url"]})
        drop(l, f"sold ${p}")
    for l in list(db["listings"]):
        e = parse(l.get("auctionEnd")) if l.get("priceType") == "bid" else None
        if e and now - e > GRACE: drop(l, "auction ended")

    ck = lambda c: norm(c.get("url")) or f"{c.get('year')}|{c.get('trim')}|{c.get('soldDate')}"
    have = {ck(c) for c in db["comps"]}
    for c in batch.get("comps", []):
        if ck(c) not in have: db["comps"].append(c); have.add(ck(c))

    for l in db["listings"]:
        imgs = [u for u in (l.get("imageUrls") or []) if u] or ([l["imageUrl"]] if l.get("imageUrl") else [])
        l["imageUrls"] = imgs[:10]; l["imageUrl"] = imgs[0] if imgs else None
    db["updated"] = stamp
    db["removed"] = db["removed"][-200:]

    print(f"added {len(added)}: {', '.join(added) or '-'}")
    print(f"updated {len(updated)}: {', '.join(f'{i}({",".join(f)})' for i, f in updated) or '-'}")
    print(f"removed {len(removed)}: {', '.join(f'{i} [{r}]' for i, r in removed) or '-'}")
    print(f"now {len(db['listings'])} active listings, {len(db['comps'])} comps")
    if a.dry_run: print("dry run: nothing written"); return
    DB.write_text(json.dumps(db, indent=2, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
