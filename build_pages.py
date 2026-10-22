#!/usr/bin/env python3
"""Bangun halaman statis tiap post (p/N.html) + sitemap.xml dari GitHub Issues, supaya bisa diindeks Google."""
import os, json, html, re, urllib.request, glob

REPO = os.environ["REPO"]                      # "scenangka/MASTER"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER, NAME = REPO.split("/")
SITE = f"https://{OWNER}.github.io/{NAME}"
BLOCKED = []                                   # username yg disembunyikan (samakan dgn info.html)
HIDE_LABEL = "hidden"
LABEL = ""                                     # samakan dgn info.html

def api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               **({"Authorization": "Bearer " + TOKEN} if TOKEN else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

issues, page = [], 1
while True:
    q = f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=100&page={page}" + (f"&labels={LABEL}" if LABEL else "")
    batch = api(q)
    issues += batch
    if len(batch) < 100: break
    page += 1

bl = [b.lower() for b in BLOCKED]
posts = [i for i in issues if "pull_request" not in i
         and i["user"]["login"].lower() not in bl
         and not any(l["name"] == HIDE_LABEL for l in i["labels"])]

E = html.escape
TPL = """<!doctype html>
<html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · WB.PREDICTION</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}"><meta property="og:url" content="{url}">
<style>
body{{margin:0;background:#07130d;color:#eaf5ee;font:16px/1.6 system-ui,sans-serif}}
.w{{max-width:760px;margin:0 auto;padding:18px 14px}}
a{{color:#3ddc84}}h1{{line-height:1.25}}
.m{{color:#8fb09c;font-size:.85rem}}
pre{{background:#0a1810;border:1px solid #1c3d2b;border-radius:10px;padding:14px;overflow:auto;white-space:pre-wrap;font:14px/1.5 ui-monospace,Menlo,Consolas,monospace}}
.b{{display:inline-block;background:#3ddc84;color:#04140b;padding:9px 16px;border-radius:8px;font-weight:700;text-decoration:none;margin:6px 6px 0 0}}
</style></head><body><div class="w">
<a href="{home}">← WB.PREDICTION</a>
<h1>{title}</h1>
<div class="m">{labels}oleh {user} · {date}</div>
<pre>{body}</pre>
<a class="b" href="{home}#/{num}">💬 Lihat &amp; komentar</a><a class="b" href="{home}">Semua postingan</a>
</div></body></html>
"""

os.makedirs("p", exist_ok=True)
keep = set()
for i in posts:
    n = i["number"]
    body = (i.get("body") or "").strip()
    body = re.sub(r"^```[a-z]*\n|\n```$", "", body)          # buang pagar kode
    desc = re.sub(r"\s+", " ", re.sub(r"[─=\-]{3,}", " ", body)).strip()[:155]
    labels = "".join(f"[{E(l['name'])}] " for l in i["labels"])
    out = TPL.format(title=E(i["title"]), desc=E(desc), url=f"{SITE}/p/{n}.html", home=f"{SITE}/info.html",
                     labels=labels, user=E(i["user"]["login"]), date=i["created_at"][:10], body=E(body), num=n)
    with open(f"p/{n}.html", "w", encoding="utf-8") as f: f.write(out)
    keep.add(f"p/{n}.html")

for old in glob.glob("p/*.html"):                            # hapus halaman post yg sudah dihapus/disembunyikan
    if old not in keep: os.remove(old)

urls = [f"{SITE}/info.html"] + [f"{SITE}/p/{i['number']}.html" for i in posts]
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"<url><loc>{E(u)}</loc></url>\n" for u in urls) + "</urlset>\n")
print(f"{len(posts)} post -> p/*.html + sitemap.xml")
