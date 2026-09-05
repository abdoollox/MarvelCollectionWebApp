#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IMDb reytinglarini rasmiy manbadan oladi.

Ikki bosqich:
  1. IMDb qidiruvidan har film uchun tconst (tt...) topiladi
  2. IMDb ochiq ma'lumot to'plamidan (title.ratings.tsv.gz) reyting olinadi

Reyting vaqt o'tishi bilan o'zgaradi, shuning uchun qo'lda yozilmaydi —
istalgan vaqt shu skript bilan yangilanadi.

Ishlatish:
    python3 tools/imdb_fetch.py            # topganini ko'rsatadi
    python3 tools/imdb_fetch.py --apply    # catalog.py ga yozadi
"""

import io
import os
import re
import sys
import gzip
import json
import time
import argparse
import urllib.parse
import urllib.request

from import_posters import EN     # id -> (inglizcha nom, yil)

SUGGEST = "https://v3.sg.media-imdb.com/suggestion/x/%s.json"
RATINGS = "https://datasets.imdbws.com/title.ratings.tsv.gz"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def find_tconst(title, year):
    """IMDb qidiruvidan film identifikatorini topadi."""
    q = urllib.parse.quote(title.lower())
    try:
        data = json.loads(fetch(SUGGEST % q).decode("utf-8"))
    except Exception as e:
        return None, "so'rov xatosi: %s" % e

    cands = [d for d in data.get("d", []) if str(d.get("id", "")).startswith("tt")]
    if not cands:
        return None, "natija yo'q"

    # Yil aniq mos kelgani ustun; keyin bir yil farq; keyin birinchisi
    for tol in (0, 1):
        for d in cands:
            if d.get("qid") in ("movie", "tvMovie") and abs((d.get("y") or 0) - year) <= tol:
                return d["id"], d.get("l", "")
    return cands[0]["id"], cands[0].get("l", "") + " (yil mos kelmadi)"


def load_ratings(cache):
    """Reytinglar jadvalini yuklaydi (bir marta yuklab, keshlaydi)."""
    if not os.path.exists(cache):
        print("IMDb reytinglar to'plami yuklanmoqda (~8 MB)...")
        raw = fetch(RATINGS, timeout=180)
        with open(cache, "wb") as f:
            f.write(raw)
    out = {}
    with gzip.open(cache, "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            tconst, rating, votes = line.rstrip("\n").split("\t")
            out[tconst] = (float(rating), int(votes))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    base = os.path.dirname(here)
    cache = os.path.join(here, ".imdb_ratings.tsv.gz")

    sys.path.insert(0, os.path.join(os.path.dirname(base), "MarvelCollectionBot"))
    import catalog

    print("Identifikatorlar qidirilmoqda (%d ta film)...\n" % len(EN))
    ids = {}
    for mid, (title, year) in EN.items():
        tconst, note = find_tconst(title, year)
        ids[mid] = (tconst, note)
        time.sleep(0.35)          # IMDb ni bosmaymiz

    ratings = load_ratings(cache)
    print()

    result, problems = {}, []
    for mid, movie in catalog.ordered():
        tconst, note = ids.get(mid, (None, "topilmadi"))
        if not tconst:
            problems.append((mid, note))
            print("  ❌ %-9s %-36s %s" % (mid, movie["title"][:36], note))
            continue
        pair = ratings.get(tconst)
        if not pair:
            problems.append((mid, "reyting yo'q (%s)" % tconst))
            print("  ⚠️  %-9s %-36s %s — reyting yo'q" % (mid, movie["title"][:36], tconst))
            continue
        rating, votes = pair
        result[mid] = rating
        print("  ✅ %-9s %-36s %s  %.1f  (%s ovoz)  ← %s"
              % (mid, movie["title"][:36], tconst, rating, format(votes, ","), note))

    print("\nTopildi: %d / %d" % (len(result), len(EN)))

    if not args.apply:
        print("\n(Ko'rish rejimi. Yozish uchun: --apply)")
        return

    path = os.path.join(os.path.dirname(base), "MarvelCollectionBot", "catalog.py")
    src = io.open(path, encoding="utf-8").read()

    lines = ["# IMDb reytinglari. Qo'lda yozilmaydi — tools/imdb_fetch.py yangilaydi.",
             "# Manba: IMDb rasmiy ochiq to'plami (title.ratings.tsv.gz).",
             'IMDB_UPDATED = "%s"' % time.strftime("%Y-%m-%d"),
             "IMDB = {"]
    for mid, _ in catalog.ordered():
        if mid in result:
            lines.append('    "%s": %.1f,' % (mid, result[mid]))
    lines.append("}")
    lines.append("")
    lines.append("")
    lines.append("def imdb(movie_id):")
    lines.append('    """Filmning IMDb reytingi yoki None."""')
    lines.append("    return IMDB.get(movie_id)")
    block = "\n".join(lines)

    marker = "def ordered():"
    if "IMDB = {" in src:
        src = re.sub(r"# IMDb reytinglari.*?return IMDB\.get\(movie_id\)\n",
                     block + "\n", src, flags=re.S)
    else:
        src = src.replace(marker, block + "\n\n" + marker)
    io.open(path, "w", encoding="utf-8").write(src)
    print("\n✅ catalog.py yangilandi (%d ta reyting)" % len(result))


if __name__ == "__main__":
    main()
