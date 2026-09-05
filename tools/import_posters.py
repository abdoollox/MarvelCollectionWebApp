#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Yig'ilgan posterlarni katalogga moslab qo'yadi.

Fayl nomlari ingliz tilida bo'ladi ("Iron Man (2008).jpg"), katalog esa
o'zbekcha. Shuning uchun bu yerda id -> inglizcha nom jadvali turadi va
mosligi nom + yil bo'yicha topiladi.

Fayl 2:3 emas bo'lsa markazidan kesiladi.

Ishlatish:
    python3 tools/import_posters.py <papka>            # faqat ko'rsatadi
    python3 tools/import_posters.py <papka> --apply    # img/ ga yozadi
"""

import os
import re
import sys
import argparse

from PIL import Image

# Katalog id -> (inglizcha nom, yil). Fayl nomlari shu bo'yicha topiladi.
EN = {
    "im1":      ("Iron Man", 2008),
    "hulk":     ("The Incredible Hulk", 2008),
    "im2":      ("Iron Man 2", 2010),
    "thor1":    ("Thor", 2011),
    "ca1":      ("Captain America The First Avenger", 2011),
    "av1":      ("The Avengers", 2012),
    "im3":      ("Iron Man 3", 2013),
    "thor2":    ("Thor The Dark World", 2013),
    "ca2":      ("Captain America The Winter Soldier", 2014),
    "gotg1":    ("Guardians of the Galaxy", 2014),
    "av2":      ("Avengers Age of Ultron", 2015),
    "antman1":  ("Ant-Man", 2015),
    "ca3":      ("Captain America Civil War", 2016),
    "ds1":      ("Doctor Strange", 2016),
    "gotg2":    ("Guardians of the Galaxy Vol. 2", 2017),
    "sm1":      ("Spider-Man Homecoming", 2017),
    "thor3":    ("Thor Ragnarok", 2017),
    "bp1":      ("Black Panther", 2018),
    "av3":      ("Avengers Infinity War", 2018),
    "antman2":  ("Ant-Man and the Wasp", 2018),
    "cm1":      ("Captain Marvel", 2019),
    "av4":      ("Avengers Endgame", 2019),
    "sm2":      ("Spider-Man Far From Home", 2019),
    "bw":       ("Black Widow", 2021),
    "shangchi": ("Shang-Chi and the Legend of the Ten Rings", 2021),
    "eternals": ("Eternals", 2021),
    "sm3":      ("Spider-Man No Way Home", 2021),
    "ds2":      ("Doctor Strange in the Multiverse of Madness", 2022),
    "thor4":    ("Thor Love and Thunder", 2022),
    "bp2":      ("Black Panther Wakanda Forever", 2022),
    "antman3":  ("Ant-Man and the Wasp Quantumania", 2023),
    "gotg3":    ("Guardians of the Galaxy Vol. 3", 2023),
    "marvels":  ("The Marvels", 2023),
    "dpw":      ("Deadpool Wolverine", 2024),
    "ca4":      ("Captain America Brave New World", 2025),
    "tbolts":   ("Thunderbolts", 2025),
    "ff4":      ("The Fantastic Four First Steps", 2025),
    "sm4":      ("Spider-Man Brand New Day", 2026),
}

# Serial, to'plam va boshqa keraksiz fayllar
SKIP = re.compile(r"(season|collection|marvel cinematic universe\.)", re.I)

TARGET_W, TARGET_H = 600, 900          # 2:3


# Ba'zi fayllarda son so'z bilan, ba'zilarida raqam bilan yoziladi
# ("Fantastic Four" / "Fantastic 4"). Taqqoslashdan oldin bittasiga keltiramiz.
NUMBERS = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5"}


def norm(text):
    """Taqqoslash uchun: kichik harf, faqat harf va raqam."""
    text = text.lower()
    for word, digit in NUMBERS.items():
        text = re.sub(r"\b%s\b" % word, digit, text)
    text = re.sub(r"\b(the|a|an|of|and|vol)\b", " ", text)
    return re.sub(r"[^a-z0-9]+", "", text)


def year_of(name):
    m = re.search(r"\((\d{4})\)", name)
    return int(m.group(1)) if m else None


def scan(folder):
    out = []
    for entry in sorted(os.listdir(folder)):
        path = os.path.join(folder, entry)
        if not os.path.isfile(path) or entry.startswith("."):
            continue
        if not entry.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue
        if SKIP.search(entry):
            continue
        stem = os.path.splitext(entry)[0]
        out.append({
            "file": entry,
            "path": path,
            "year": year_of(stem),
            "key": norm(re.sub(r"\(\d{4}\)", "", stem)),
        })
    return out


def match(files):
    """Har film uchun mos faylni topadi."""
    found, missing = {}, []
    for mid, (title, year) in EN.items():
        key = norm(title)
        hit = next((f for f in files if f["key"] == key and f["year"] == year), None)
        if not hit:
            hit = next((f for f in files if f["key"] == key), None)
        if hit:
            found[mid] = hit
        else:
            missing.append(mid)
    return found, missing


def to_poster(src, dst):
    """2:3 ga kesib, JPG qilib saqlaydi."""
    im = Image.open(src).convert("RGB")
    ratio = max(TARGET_W / im.width, TARGET_H / im.height)
    im = im.resize((max(1, round(im.width * ratio)), max(1, round(im.height * ratio))),
                   Image.LANCZOS)
    left = (im.width - TARGET_W) // 2
    top = (im.height - TARGET_H) // 2
    im = im.crop((left, top, left + TARGET_W, top + TARGET_H))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, "JPEG", quality=88, optimize=True)
    return os.path.getsize(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base, "img")

    sys.path.insert(0, os.path.join(os.path.dirname(base), "MarvelCollectionBot"))
    import catalog

    files = scan(args.folder)
    found, missing = match(files)
    used = {f["file"] for f in found.values()}

    print("Papkada mos keladigan fayllar: %d ta" % len(files))
    print("Topildi: %d / %d\n" % (len(found), len(EN)))

    for mid, movie in catalog.ordered():
        hit = found.get(mid)
        mark = "✅" if hit else "❌"
        print("  %s %-9s %-38s %s" % (mark, mid, movie["title"][:38],
                                      hit["file"] if hit else "— topilmadi —"))

    if missing:
        print("\nTopilmaganlar: %s" % ", ".join(missing))

    leftover = [f["file"] for f in files if f["file"] not in used]
    if leftover:
        print("\nIshlatilmagan fayllar (%d ta):" % len(leftover))
        for f in leftover[:15]:
            print("   ", f)
        if len(leftover) > 15:
            print("    ... yana %d ta" % (len(leftover) - 15))

    if not args.apply:
        print("\n(Ko'rish rejimi. Yozish uchun: --apply)")
        return

    print()
    total = 0
    for mid, hit in found.items():
        dst = os.path.join(img_dir, mid + ".jpg")
        size = to_poster(hit["path"], dst)
        total += size
        print("  ✅ img/%s.jpg  %5.0f KB" % (mid, size / 1024))
    print("\nJami: %d ta poster, %.1f MB" % (len(found), total / 1024 / 1024))


if __name__ == "__main__":
    main()
