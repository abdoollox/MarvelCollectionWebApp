#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Video uchun 16:9 thumbnail — gorizontal artwork asosida.

Nega poster emas: kadr keng bo'lgani uchun tik poster kichrayib qoladi.
Backdrop esa kadrni to'ldiradi.

Nega 16:9 da qoladi: Telegram kompyuterda thumbnail'ni videoning
nisbatiga (ko'pincha 2.4:1) siqib, tepa/pastdan ~13% ini kesadi.
Agar biz o'zimiz kessak — HAMMA kesilganini ko'radi. 16:9 da qoldirsak
telefonda to'liq ko'rinadi, kompyuterda esa faqat chekka fon yo'qoladi.
Shuning uchun barcha element MARKAZIY XAVFSIZ ZONADA turadi.

    img/art/<id>.jpg + img/logos/<id>.png  ->  img/wide/<id>.jpg

Ishlatish:
    python3 tools/artgen.py                 # hammasi
    python3 tools/artgen.py im1 loki1
    python3 tools/artgen.py --zona          # kesilish chegarasini chizadi
"""

import argparse
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BOT = os.path.join(os.path.dirname(ROOT), "MarvelCollectionBot")
sys.path.insert(0, BOT)
sys.path.insert(0, HERE)

import catalog
import thumbgen as tg

W, H = 1280, 720
ART = os.path.join(ROOT, "img", "art")
LOGOS = os.path.join(ROOT, "img", "logos")
OUT = os.path.join(ROOT, "img", "wide")
BRAND = os.path.join(ROOT, "img", "logo.png")

# 16:9 rasm 2.4:1 oynaga siqilganda balandlikning 74% i qoladi —
# tepadan va pastdan 12.96% dan kesiladi.
#
# Xavfsiz zonani aynan shu miqdorga teng qilib bo'lmaydi: unda matn
# kesilgandan keyin kadr chekkasiga yopishib qoladi. Shuning uchun
# ustiga ~5% havo qo'shamiz — kesilganda ham, to'liq holatda ham
# yozuv erkin turadi.
CROP = 0.1296
SAFE = CROP + 0.05

# --- A uslubi: faqat artwork va brend belgisi
PAGE_A = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
%(fonts)s
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#0a0c11}
</style></head><body>
<div style="position:relative;width:%(W)dpx;height:%(H)dpx;overflow:hidden">
  <div style="position:absolute;inset:0;background:#12151d center/cover no-repeat;
              background-image:url('%(art)s')"></div>
  <div style="position:absolute;inset:0;background:linear-gradient(
       to top, rgba(6,7,10,0.88) 0%%, rgba(6,7,10,0.35) 20%%,
       rgba(6,7,10,0) 42%%)"></div>
  <div style="position:absolute;left:0;right:0;bottom:%(safe)dpx;
              display:flex;justify-content:center">%(brand)s</div>
  %(zona)s
</div>
</body></html>
"""

# --- B uslubi: pastda bir xil chiziq — barcha kartani birlashtiradi
PAGE_B = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
%(fonts)s
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#0a0c11}
</style></head><body>
<div style="position:relative;width:%(W)dpx;height:%(H)dpx;overflow:hidden;
            font-family:'Bebas Neue',Impact,sans-serif">

  <div style="position:absolute;inset:0;background:#12151d center/cover no-repeat;
              background-image:url('%(art)s')"></div>
  <div style="position:absolute;inset:0;background:linear-gradient(
       to top, rgba(6,7,10,0.94) 0%%, rgba(6,7,10,0.70) 24%%,
       rgba(6,7,10,0.10) 52%%, rgba(6,7,10,0) 70%%)"></div>

  <!-- Pastki chiziq: hamma thumbnail'da bir xil -->
  <div style="position:absolute;left:%(pad)dpx;right:%(pad)dpx;bottom:%(safe)dpx;
              display:flex;align-items:flex-end;justify-content:space-between;gap:32px">
    <div style="flex:1;min-width:0">
      <div style="width:%(bar)dpx;height:%(barh)dpx;background:#ED1D24;
                  margin-bottom:%(barm)dpx"></div>
      <div id="title" style="font-size:%(ft)dpx;line-height:0.88;letter-spacing:2px;
                  color:#f5f5f3;text-transform:uppercase;
                  text-shadow:0 4px 16px rgba(0,0,0,.85)">%(title)s</div>
    </div>
    %(brand)s
  </div>
  %(zona)s
</div>
<script>
(function () {
  var t = document.getElementById('title');
  if (!t) { document.documentElement.setAttribute('data-ready','1'); return; }
  var size = %(ft)d;
  while (size > 34 && (t.scrollWidth > t.clientWidth + 1 || t.scrollHeight > %(tmax)d)) {
    size -= 2;
    t.style.fontSize = size + 'px';
  }
  document.documentElement.setAttribute('data-ready', '1');
})();
</script>
</body></html>
"""


def brand_block(height=44):
    if not os.path.exists(BRAND):
        return "<div></div>"
    return ('<img src="%s" style="height:%dpx;width:auto;display:block;flex:none;'
            'filter:drop-shadow(0 4px 14px rgba(0,0,0,.7))">'
            % (tg.data_uri(BRAND, "image/png"), height))


def build_html(movie_id, title, year, zona=False, uslub="b"):
    safe = int(H * SAFE)
    band = ('<div style="position:absolute;left:0;right:0;top:0;height:%dpx;'
            'background:rgba(255,40,40,.30);border-bottom:2px solid #ff3030"></div>'
            '<div style="position:absolute;left:0;right:0;bottom:0;height:%dpx;'
            'background:rgba(255,40,40,.30);border-top:2px solid #ff3030"></div>'
            % (safe, safe)) if zona else ""

    common = {
        "W": W, "H": H,
        "fonts": tg.font_css(),
        "art": tg.data_uri(os.path.join(ART, movie_id + ".jpg"), "image/jpeg"),
        "brand": brand_block(56 if uslub == "a" else 44),
        "safe": safe, "pad": 58, "zona": band,
    }
    if uslub == "a":
        return PAGE_A % common

    common.update({
        "title": tg.esc(title),
        "ft": 74, "tmax": 150,
        "bar": 74, "barh": 6, "barm": 18,
    })
    return PAGE_B % common


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--zona", action="store_true")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--uslub", default="b", choices=["a", "b"],
                    help="a = faqat artwork + brend, b = pastki chiziqli")
    args = ap.parse_args()

    chrome = tg.find_chrome()
    if not chrome:
        raise SystemExit("Chrome topilmadi.")
    os.makedirs(args.out, exist_ok=True)

    tmp = tempfile.mkdtemp(prefix="artgen_")
    html_path = os.path.join(tmp, "page.html")
    png_path = os.path.join(tmp, "shot.png")

    done = skipped = 0
    for mid, movie in catalog.ordered():
        if args.ids and mid not in args.ids:
            continue
        if not os.path.exists(os.path.join(ART, mid + ".jpg")):
            print("  ⚠️  %-13s artwork yo'q" % mid)
            skipped += 1
            continue
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(build_html(mid, movie["title"], movie["year"],
                               args.zona, args.uslub))
        tg.shoot(chrome, html_path, png_path, (W, H))
        tg.to_jpeg(png_path, os.path.join(args.out, mid + ".jpg"), size=(W, H))
        print("  ✅ %-13s %s" % (mid, movie["title"][:38]))
        done += 1

    print("\nYasaldi: %d | o'tkazildi: %d" % (done, skipped))


if __name__ == "__main__":
    main()
