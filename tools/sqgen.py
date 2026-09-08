#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inline ro'yxati uchun kvadrat ikonkalar: img/art/*.jpg -> img/sq/*.jpg.

Nega kvadrat: Telegram InlineQueryResultArticle dagi rasmni kvadrat
qilib kesib ko'rsatadi. 16:9 thumbnail'ni to'g'ridan-to'g'ri berib
bo'lmaydi — pastidagi nom butunlay kesilib ketadi. Tik poster ham
yaramaydi: undagi yozuvlar chetda qolib qirqiladi.

Shuning uchun aynan shu backdrop'ning markazidan kvadrat kesib olamiz —
qahramonlar markazda turadi, ro'yxat esa thumbnail'lar bilan bir
oilaga o'xshaydi.
"""
import glob
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "img", "art")
OUT = os.path.join(ROOT, "img", "sq")
SIZE = 320


def square(img):
    """Markazdan kvadrat kesadi."""
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def main():
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for path in sorted(glob.glob(os.path.join(SRC, "*.jpg"))):
        img = Image.open(path).convert("RGB")
        img = square(img).resize((SIZE, SIZE), Image.LANCZOS)
        img.save(os.path.join(OUT, os.path.basename(path)), "JPEG",
                 quality=82, optimize=True)
        n += 1
    print("Tayyor: %d ta kvadrat ikonka -> %s" % (n, OUT))


if __name__ == "__main__":
    main()
