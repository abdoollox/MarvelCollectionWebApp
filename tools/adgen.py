#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bot reklamasi uchun 16:9 karta.

Foydalanuvchi "Do'stlarni taklif qilish" tugmasini bosganda tarqatiladigan
karta. Uslub film kartalari bilan bir xil (tools/thumbgen.py) — o'sha
generatorning yordamchilaridan foydalanadi.

Natija: img/promo.jpg (1280x720).

Ishlatish:
    python3 tools/adgen.py
    python3 tools/adgen.py --posters im1 av4 dpw
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import thumbgen as tg

W, H = tg.W, tg.H
IMG = os.path.join(ROOT, "img")
OUT = os.path.join(IMG, "promo.jpg")

# Chapdagi uch poster: eng tanish uchtasi
FRONT = ["av4", "im1", "dpw"]
# Fondagi to'r
TILES = ["im1", "av1", "gotg1", "bp1", "ca3", "dr1",
         "th3", "av4", "sm1", "dpw", "cm1", "antman1"]

HEAD = "BARCHA MARVEL FILMLARI"
SUB = "BIR JOYDA · O'ZBEK TILIDA · REKLAMASIZ"


def poster(movie_id):
    path = os.path.join(IMG, movie_id + ".jpg")
    return path if os.path.exists(path) else None


def tile_grid(ids):
    """Fon uchun posterlar to'ri."""
    cells = []
    for mid in ids:
        p = poster(mid)
        if not p:
            continue
        cells.append(
            '<div style="flex:1 0 16.66%%;height:50%%;background:#2a2730 '
            'center/cover no-repeat;background-image:url(\'%s\')"></div>'
            % tg.data_uri(p, "image/jpeg"))
    return "".join(cells)


def stack(ids):
    """Chapdagi bir-birining ustiga qo'yilgan posterlar."""
    # (chapga siljish, tepaga siljish, burilish, kenglik)
    # Birinchi poster kadrga to'liq sig'sin — chapdan 44px joy qoldiriladi,
    # oxirgisi esa matn boshlanadigan 600px dan oshmasligi kerak.
    layout = [(44, 176, -8, 232), (146, 146, -2, 260), (252, 112, 8, 288)]
    out = []
    for (left, top, rot, w), mid in zip(layout, ids):
        p = poster(mid)
        if not p:
            continue
        h = int(w * 1.5)
        out.append(
            '<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;'
            'height:%dpx;transform:rotate(%ddeg);box-shadow:0 18px 40px '
            'rgba(0,0,0,.55);border:3px solid #f4f4f2;background:#2a2730 '
            'center/cover no-repeat;background-image:url(\'%s\')"></div>'
            % (left, top, w, h, rot, tg.data_uri(p, "image/jpeg")))
    return "".join(out)


PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
%(fonts)s
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#15151a}
</style></head><body>

<div style="position:relative;width:%(W)dpx;height:%(H)dpx;overflow:hidden;
            background:#24242a;font-family:'Bebas Neue',Impact,sans-serif">

  <!-- Fon: posterlar to'ri, xiralashtirilgan -->
  <div style="position:absolute;inset:-70px;display:flex;flex-wrap:wrap;
              filter:blur(42px) brightness(0.5) saturate(1.1)">%(tiles)s</div>

  <!-- Yumshoq yorug'lik -->
  <div style="position:absolute;inset:0;background:radial-gradient(
       85%% 115%% at 24%% 50%%, rgba(255,255,255,0.13) 0%%, rgba(10,10,14,0.72) 70%%)"></div>

  <!-- Chapda posterlar -->
  %(stack)s

  <!-- O'ngda matn -->
  <div style="position:absolute;left:600px;top:96px;bottom:96px;right:70px;
              display:flex;flex-direction:column;justify-content:center;
              align-items:flex-start">
    <img src="%(logo)s" style="height:%(logo_h)dpx;width:auto;display:block;
         margin-bottom:34px" alt="Marvel Kolleksiya">
    <div style="font-size:76px;line-height:0.88;letter-spacing:2px;
                color:#f5f5f3;text-transform:uppercase">%(head)s</div>
    <div style="width:100%%;height:5px;background:#f4f4f2;margin:28px 0 22px"></div>
    <div style="font-family:'IBM Plex Mono',monospace;font-weight:600;
                font-size:21px;letter-spacing:3px;color:#d8d8d4">%(sub)s</div>
  </div>
</div>
</body></html>
"""


def build_html(head, sub, front, tiles, logo_h):
    return PAGE % {
        "W": W, "H": H,
        "fonts": tg.font_css(),
        "tiles": tile_grid(tiles),
        "stack": stack(front),
        "logo": tg.data_uri(tg.LOGO, "image/png"),
        "logo_h": logo_h,
        "head": tg.esc(head),
        "sub": tg.esc(sub),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--posters", nargs="*", default=FRONT)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--head", default=HEAD)
    ap.add_argument("--sub", default=SUB)
    ap.add_argument("--logo-h", type=int, default=96)
    ap.add_argument("--keep-html", action="store_true")
    args = ap.parse_args()

    chrome = tg.find_chrome()
    if not chrome:
        raise SystemExit("Chrome topilmadi.")

    import tempfile
    tmp = tempfile.mkdtemp(prefix="adgen_")
    html_path = os.path.join(tmp, "page.html")
    png_path = os.path.join(tmp, "shot.png")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html(args.head, args.sub, args.posters, TILES, args.logo_h))

    tg.shoot(chrome, html_path, png_path)
    tg.to_jpeg(png_path, args.out)
    print("Tayyor: %s (%d bayt)" % (args.out, os.path.getsize(args.out)))
    if args.keep_html:
        print("HTML:", html_path)


if __name__ == "__main__":
    main()
