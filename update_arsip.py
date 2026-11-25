#!/usr/bin/env python3
"""Gabungkan history result.json ke arsip.json (kumulatif, tidak pernah dibuang).
Jalankan SETELAH result.json diperbarui. Aman dijalankan berulang kali."""
import json, os, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "result.json"
DST = sys.argv[2] if len(sys.argv) > 2 else "arsip.json"

def load(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default

src = load(SRC, {})
arsip = load(DST, {})
baru = 0
for kode, m in src.items():
    if not isinstance(m, dict):
        continue
    a = arsip.setdefault(kode, {"name": m.get("name", kode), "data": {}})
    a["name"] = m.get("name", a.get("name", kode))
    d = a["data"]
    rows = list(m.get("history") or [])
    for x in rows:                       # history: {date, result}
        tgl, res = x.get("date"), str(x.get("result", "")).strip()
        if not tgl or not res.isdigit():
            continue
        if d.get(tgl) != res:
            if tgl not in d:
                baru += 1
            d[tgl] = res                 # tanggal sama tapi beda isi -> pakai yang terbaru
    a["data"] = dict(sorted(d.items()))  # urut tanggal lama -> baru

with open(DST, "w", encoding="utf-8") as f:
    json.dump(arsip, f, ensure_ascii=False, separators=(",", ":"))
print(f"arsip: {sum(len(v['data']) for v in arsip.values())} result, {baru} baru")
