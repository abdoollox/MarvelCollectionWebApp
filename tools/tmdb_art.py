#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TMDB dan gorizontal artwork va film logotiplarini yuklaydi.

Nega kerak: thumbnail videoning nisbatida yasaladi (ko'pincha 2.4:1).
Bunday keng kadrda tik poster kichrayib qoladi. Gorizontal backdrop esa
kadrni to'ldiradi va kesilishga chidamli.

TMDB'da har film uchun:
  - backdrops — 16:9 kadrlar (matnsizini afzal ko'ramiz)
  - logos     — filmning shaffof PNG logotipi

Natija:
  img/art/<id>.jpg    backdrop (1280 kenglikda)
  img/logos/<id>.png  logotip

Kalit .env faylida: TMDB_KEY=...

Ishlatish:
    python3 tools/tmdb_art.py            # faqat ko'rsatadi
    python3 tools/tmdb_art.py --apply
    python3 tools/tmdb_art.py --apply im1 loki1
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BOT = os.path.join(os.path.dirname(ROOT), "MarvelCollectionBot")
sys.path.insert(0, BOT)
sys.path.insert(0, HERE)

import catalog
from import_posters import EN, SERIES_FILES

API = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p"
ART_DIR = os.path.join(ROOT, "img", "art")
LOGO_DIR = os.path.join(ROOT, "img", "logos")
MAP_FILE = os.path.join(HERE, "tmdb_map.json")


def load_key():
    path = os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        sys.exit("XATO: .env yo'q. .env.namuna dan nusxa oling va kalitni qo'ying.")
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("TMDB_KEY=") and len(line) > 9:
            return line.split("=", 1)[1].strip()
    sys.exit("XATO: .env da TMDB_KEY bo'sh.")


def api(key, path, **params):
    params["api_key"] = key
    url = "%s%s?%s" % (API, path, urllib.parse.urlencode(params))
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                return json.load(r)
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return None


def pick_backdrop(images):
    """Eng mos backdrop: avval matnsiz (til yo'q), keyin ovoz bo'yicha."""
    shots = images.get("backdrops") or []
    if not shots:
        return None
    clean = [s for s in shots if not s.get("iso_639_1")]
    pool = clean or shots
    pool.sort(key=lambda s: (s.get("vote_average", 0), s.get("width", 0)),
              reverse=True)
    return pool[0]["file_path"]


def pick_logo(images):
    """Inglizcha PNG logotip."""
    logos = [l for l in (images.get("logos") or [])
             if (l.get("file_path") or "").lower().endswith(".png")]
    if not logos:
        logos = images.get("logos") or []
    if not logos:
        return None
    en = [l for l in logos if l.get("iso_639_1") == "en"]
    pool = en or logos
    pool.sort(key=lambda l: (l.get("vote_average", 0), l.get("width", 0)),
              reverse=True)
    return pool[0]["file_path"]


def download(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())
    return os.path.getsize(dest)


# TMDB dagi nomi fayl nomidan farq qiladigan yozuvlar
NAME_FIX = {
    "punisher": "The Punisher: One Last Kill",
}


def targets():
    """Har yozuv uchun: (id, qidiruv nomi, yil, serialmi)."""
    out = []
    for mid, movie in catalog.ordered():
        if catalog.is_series(movie):
            stem = SERIES_FILES.get(mid, "")
            name = stem.split(" (")[0] if stem else movie["title"]
            name = NAME_FIX.get(mid, name)
            out.append((mid, name, movie["year"], True))
        else:
            en = EN.get(mid)
            out.append((mid, en[0] if en else movie["title"],
                        en[1] if en else movie["year"], False))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    key = load_key()
    cache = {}
    if os.path.exists(MAP_FILE):
        cache = json.load(open(MAP_FILE, encoding="utf-8"))

    found = missing = 0
    for mid, name, year, is_tv in targets():
        if args.ids and mid not in args.ids:
            continue

        hit = cache.get(mid)
        if not hit:
            # Maxsus taqdimotlar TMDB'da ba'zan film, ba'zan serial
            # sifatida turadi — ikkalasini ham sinaymiz.
            kinds = ["tv", "movie"] if is_tv else ["movie", "tv"]
            items = []
            for kind in kinds:
                params = {"query": name}
                if kind == "movie":
                    params["year"] = year
                res = api(key, "/search/%s" % kind, **params)
                items = (res or {}).get("results") or []
                if not items and kind == "movie":
                    # yilsiz qayta urinamiz
                    res = api(key, "/search/movie", query=name)
                    items = (res or {}).get("results") or []
                if items:
                    break
            if not items:
                print("  ❌ %-13s %s — TMDB da topilmadi" % (mid, name[:34]))
                missing += 1
                continue
            hit = {"kind": kind, "tmdb_id": items[0]["id"],
                   "tmdb_name": items[0].get("title") or items[0].get("name")}
            cache[mid] = hit

        images = api(key, "/%s/%d/images" % (hit["kind"], hit["tmdb_id"]),
                     include_image_language="en,null")
        if not images:
            print("  ❌ %-13s rasmlar olinmadi" % mid)
            missing += 1
            continue

        back = pick_backdrop(images)
        logo = pick_logo(images)
        print("  %s %-13s %-34s backdrop:%s logo:%s" % (
            "✅" if back else "⚠️ ", mid, hit["tmdb_name"][:34],
            "bor" if back else "yo'q", "bor" if logo else "yo'q"))

        if args.apply:
            if back:
                download(IMG + "/w1280" + back,
                         os.path.join(ART_DIR, mid + ".jpg"))
            if logo:
                download(IMG + "/w500" + logo,
                         os.path.join(LOGO_DIR, mid + ".png"))
        found += 1 if back else 0
        time.sleep(0.12)

    json.dump(cache, open(MAP_FILE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\nBackdrop topildi: %d | muammo: %d" % (found, missing))
    if not args.apply:
        print("(Ko'rish rejimi. Yuklash uchun: --apply)")


if __name__ == "__main__":
    main()
