#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nishon rasmlarini ilova uchun tayyorlaydi.

Kirish: img/badges/_raw_<id>.png (kvadrat, to'q fonli generatsiya).
Chiqish: img/badges/<id>.png — 512x512, aylana bo'ylab kesilgan,
fon shaffof.

Ishlatish:
    python3 tools/badgegen.py            # _raw_*.png larning hammasi
    python3 tools/badgegen.py ironman    # faqat ko'rsatilgani
"""

import glob
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(os.path.dirname(HERE), "img", "badges")
SIZE = 256          # ilovada 52px da ko'rinadi; 3x ekranga ham yetarli
PAD = 0.035          # emblema kadrga deyarli to'la joylashgan
SUPER = 4            # maskani shu marta kattaroq chizib, keyin kichraytiramiz


def circle_mask(size, pad=PAD, super_scale=SUPER):
    """Chekkasi silliq aylana maskasi."""
    big = size * super_scale
    mask = Image.new("L", (big, big), 0)
    edge = int(big * pad)
    ImageDraw.Draw(mask).ellipse([edge, edge, big - edge, big - edge], fill=255)
    return mask.resize((size, size), Image.LANCZOS)


def build(raw_path, out_path):
    img = Image.open(raw_path).convert("RGBA").resize((SIZE, SIZE), Image.LANCZOS)
    img.putalpha(circle_mask(SIZE))
    img.save(out_path, "PNG", optimize=True)
    return os.path.getsize(out_path)


def main():
    wanted = sys.argv[1:]
    files = sorted(glob.glob(os.path.join(DIR, "_raw_*.png")))
    done = 0
    for path in files:
        badge_id = os.path.basename(path)[len("_raw_"):-len(".png")]
        if wanted and badge_id not in wanted:
            continue
        size = build(path, os.path.join(DIR, badge_id + ".png"))
        print("  %-12s %6.1f KB" % (badge_id, size / 1024))
        done += 1
    print("Tayyor: %d ta nishon" % done)


if __name__ == "__main__":
    main()
