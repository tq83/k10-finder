#!/usr/bin/env python3
"""Copy listings.json into index.html's inline fallback block (so the page works when opened as a file)."""
import json, re, pathlib
here = pathlib.Path(__file__).resolve().parent
data = json.loads((here / "listings.json").read_text())          # validates JSON
blob = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
src = here / "index.html"
html = src.read_text() if src.exists() else (here / "template.html").read_text()
block = f'<!--K10-DATA-START-->\n<script id="k10-data" type="application/json">{blob}</script>\n<!--K10-DATA-END-->'
new, n = re.subn(r"<!--K10-DATA-START-->.*?<!--K10-DATA-END-->", lambda m: block, html, flags=re.S)
if n != 1: raise SystemExit("data markers not found in index.html")
src.write_text(new)
print(f"index.html updated: {len(data.get('listings', []))} listings, {len(data.get('comps', []))} comps")
