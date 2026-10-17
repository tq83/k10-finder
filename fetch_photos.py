#!/usr/bin/env python3
"""Save photos from sources whose image links expire into the repo, and point imageUrls at the local copies.

  python3 fetch_photos.py            # run before publishing (publish.sh does this automatically)
  python3 fetch_photos.py --dry-run

* Volatile hosts: Facebook CDN (fbcdn.net / fbsbx.com) and Craigslist (images.craigslist.org).
  Other hosts (BaT, ClassicCars.com, dealer CDNs) are stable and stay hotlinked.
* Each volatile photo is downloaded, resized to max 1200px wide, re-encoded as JPEG q78 (progressive)
  and saved as photos/<listing-id>/<hash>.jpg. The hash comes from the source URL minus its query
  string, so reruns are idempotent. imageUrls is rewritten to the relative path.
* Craigslist: tries the 1200x900 version of each image first, then falls back to the original size.
* A photo that can't be downloaded (e.g. an expired fbcdn link -> 403) is dropped. If a Facebook or
  Craigslist listing ends up with no photos, the script re-reads the listing page for fresh links
  (Facebook: the public link-preview og:image, normally 1 photo; Craigslist: the full gallery).
  If that also fails, the listing keeps an empty array and the page shows its placeholder.
* photos/<id>/ folders for listings no longer in `listings` are deleted to keep the repo small.
"""
import json, re, sys, io, html, hashlib, shutil, pathlib, urllib.request, urllib.error
from urllib.parse import urlsplit
from PIL import Image, ImageOps

HERE = pathlib.Path(__file__).resolve().parent
DB, PHOTOS = HERE / "listings.json", HERE / "photos"
MAXW, QUALITY, MAXN = 1200, 78, 10
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"
FB_PREVIEW_UA = "facebookexternalhit/1.1"   # Facebook serves public link-preview metadata (og:image) to this agent
VOLATILE = re.compile(r"(^|\.)(fbcdn\.net|fbsbx\.com|craigslist\.org)$", re.I)
DRY = "--dry-run" in sys.argv

def host(u): return urlsplit(u).netloc.lower()
def volatile(u): return u.startswith("http") and bool(VOLATILE.search(host(u)))
def local(u): return bool(u) and not re.match(r"^[a-z]+:", u)

def get(url, ua=UA, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def save(url, dest):
    cands = [url]
    if "craigslist.org" in host(url):
        big = re.sub(r"_\d+x\d+(c)?\.jpg", "_1200x900.jpg", url)
        if big != url: cands.insert(0, big)
    for c in cands:
        try:
            im = Image.open(io.BytesIO(get(c)))
            im = ImageOps.exif_transpose(im).convert("RGB")
            if im.width > MAXW: im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
            if not DRY:
                dest.parent.mkdir(parents=True, exist_ok=True)
                im.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
            return True
        except Exception as e:
            err = e
    print(f"    failed: {url[:90]}... ({err})")
    return False

def fresh_urls(l):
    """Re-read the listing page for current photo links."""
    u = l.get("url", "")
    try:
        if "facebook.com" in host(u):
            s = get(u, FB_PREVIEW_UA).decode("utf-8", "replace")
            return [html.unescape(x) for x in re.findall(r'property="og:image" content="([^"]+)"', s) or
                    re.findall(r'og:image" content="([^"]+)"', s)][:MAXN]
        if "craigslist.org" in host(u):
            s = get(u).decode("utf-8", "replace")
            m = re.search(r"var imgList = (\[.*?\]);", s)
            ids = [x["imgid"].split(":")[-1] for x in json.loads(m.group(1))] if m else \
                  list(dict.fromkeys(re.findall(r"images\.craigslist\.org/([0-9A-Za-z_]+?)_(?:50x50c|600x450)", s)))
            return [f"https://images.craigslist.org/{i}_600x450.jpg" for i in ids][:MAXN]
    except Exception as e:
        print(f"    page refetch failed: {e}")
    return []

def localize(l, urls):
    out = []
    for u in urls:
        if not volatile(u): out.append(u); continue
        name = hashlib.sha1(u.split("?")[0].encode()).hexdigest()[:12] + ".jpg"
        rel = f"photos/{l['id']}/{name}"
        if (HERE / rel).exists() or save(u, HERE / rel): out.append(rel)
    return out

def main():
    db = json.loads(DB.read_text())
    changed = 0
    for l in db.get("listings", []):
        urls = [u for u in (l.get("imageUrls") or []) if u] or ([l["imageUrl"]] if l.get("imageUrl") else [])
        # keep local files only if they still exist on disk
        urls = [u for u in urls if not local(u) or (HERE / u).exists()]
        needs = any(volatile(u) for u in urls)
        vol_src = any(k in host(l.get("url", "")) for k in ("facebook.com", "craigslist.org"))
        if not needs and not (vol_src and not urls): continue
        print(f"{l['id']} ({l.get('source')}): {sum(volatile(u) for u in urls)} volatile photo(s)")
        new = localize(l, urls)
        if not new and vol_src:
            print("  no usable photos; re-reading listing page")
            new = localize(l, fresh_urls(l))
        new = new[:MAXN]
        print(f"  -> {len(new)} photo(s) {'(placeholder)' if not new else ''}")
        if new != l.get("imageUrls"):
            l["imageUrls"], l["imageUrl"] = new, (new[0] if new else None); changed += 1
    # prune folders of listings that are no longer active
    active = {str(l["id"]) for l in db.get("listings", [])}
    if PHOTOS.exists():
        for d in PHOTOS.iterdir():
            if d.is_dir() and d.name not in active:
                print(f"pruning photos/{d.name} (listing no longer active)")
                if not DRY: shutil.rmtree(d)
    if changed and not DRY:
        DB.write_text(json.dumps(db, indent=2, ensure_ascii=False) + "\n")
    print(f"done: {changed} listing(s) updated{' (dry run)' if DRY else ''}")

if __name__ == "__main__":
    main()
