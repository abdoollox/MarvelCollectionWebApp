#!/usr/bin/env python3
"""Inline ro'yxati uchun kichik posterlar: img/*.jpg -> img/small/*.jpg (200x300).

Telegram inline natijalar ro'yxatidagi thumbnail'ni faqat kichik fayl bo'lsa
yuklab oladi. Katta 600x900 poster (~170 KB) o'rniga shu yerdagi ~15 KB
nusxa ishlatiladi.
"""
import glob
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "img")
OUT = os.path.join(SRC, "small")
W, H = 200, 300


def main():
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for path in sorted(glob.glob(os.path.join(SRC, "*.jpg"))):
        img = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
        img.save(os.path.join(OUT, os.path.basename(path)), "JPEG",
                 quality=80, optimize=True)
        n += 1
    print("Tayyor: %d ta kichik poster -> %s" % (n, OUT))


if __name__ == "__main__":
    main()
