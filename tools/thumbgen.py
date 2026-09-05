#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ulashish kartalari uchun 16:9 rasm generatori.

Dizayn Claude Design'da tayyorlangan ("Marvel Video Covers"). U HTML/CSS
da yozilgani uchun bu skript ham uni HTML sifatida chizadi va Chrome
bilan suratga oladi — Pillow'da qayta chizsak, aslidan chetlashardi.

Manba — bitta 2:3 poster (img/<id>.jpg). Natija — img/wide/<id>.jpg,
aniq 1280x720.

Ishlatish:
    python3 tools/thumbgen.py                 # posteri bor hamma film
    python3 tools/thumbgen.py im1 av4         # faqat ko'rsatilganlar
    python3 tools/thumbgen.py --force         # mavjudlarini qayta yasaydi
    python3 tools/thumbgen.py --keep-html     # oraliq HTML ni saqlaydi
"""

import os
import sys
import base64
import argparse
import subprocess
import tempfile

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]

W, H = 1280, 720
CHANNEL = "MARVEL_KOLLEKSIYA"

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

FONT_FACES = [
    ("Bebas Neue", 400, "BebasNeue-latin.woff2"),
    ("Bebas Neue", 400, "BebasNeue-latin-ext.woff2"),
    ("IBM Plex Mono", 600, "IBMPlexMono-600-latin.woff2"),
    ("IBM Plex Mono", 600, "IBMPlexMono-600-latin-ext.woff2"),
]


def find_chrome():
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    return None


def data_uri(path, mime):
    with open(path, "rb") as f:
        return "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode())


def font_css():
    out = []
    for family, weight, fname in FONT_FACES:
        path = os.path.join(FONT_DIR, fname)
        if not os.path.exists(path):
            continue
        out.append(
            "@font-face{font-family:'%s';font-style:normal;font-weight:%d;"
            "font-display:block;src:url('%s') format('woff2');}"
            % (family, weight, data_uri(path, "font/woff2")))
    return "\n".join(out)


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
%(fonts)s
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#15151a}
</style></head><body>

<div id="cover" style="position:relative;width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#24242a;font-family:'Bebas Neue',Impact,sans-serif">

  <!-- Fon: posterning o'zi, xiralashtirilgan va qoraytirilgan -->
  <div style="position:absolute;inset:-60px;filter:blur(38px) saturate(1) brightness(0.66)">
    <div style="position:absolute;inset:0;background:#2a2730 center/cover no-repeat;background-image:url('%(poster)s')"></div>
  </div>

  <!-- Yumshoq yorug'lik: chapdan o'ngga qorayadi -->
  <div style="position:absolute;inset:0;background:radial-gradient(90%% 120%% at 22%% 50%%, rgba(255,255,255,0.14) 0%%, rgba(12,12,16,0.6) 72%%)"></div>

  <!-- Poster ostidagi siljigan oq blok -->
  <div style="position:absolute;left:108px;top:114px;width:340px;height:510px;background:#f4f4f2"></div>
  <div style="position:absolute;left:90px;top:100px;width:340px;height:510px;background:#2a2730 center/cover no-repeat;background-image:url('%(poster)s')"></div>

  <!-- Yil, nom, chiziq.
       Maydon posterning aynan balandligida (100..610) — shunda matnning
       markazi poster markazi bilan bir xil bo'ladi. Avval maydon 0..556
       edi va matn ko'zga 77px yuqorida turardi. -->
  <div id="l-text" style="position:absolute;left:544px;top:100px;bottom:110px;right:72px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start">
    <div style="font-family:'IBM Plex Mono',monospace;font-weight:600;font-size:30px;letter-spacing:6px;color:#15151a;background:#f4f4f2;padding:12px 20px 10px;margin-bottom:26px">%(year)s</div>
    <div id="title" style="font-size:96px;line-height:0.86;letter-spacing:2px;color:#f5f5f3;text-transform:uppercase">%(title)s</div>
    <div style="width:100%%;height:5px;background:#f4f4f2;margin-top:30px"></div>
  </div>

  <!-- Kanal tasmasi -->
  <div style="position:absolute;left:544px;top:566px;right:72px;display:flex;align-items:center;gap:14px">
    <div style="display:flex;align-items:baseline;font-family:'IBM Plex Mono',monospace;font-weight:600;line-height:1">
      <div style="font-size:36px;color:rgba(244,244,242,0.65)">@</div>
      <div style="font-size:36px;color:#f4f4f2;letter-spacing:4px;text-transform:uppercase">%(channel)s</div>
    </div>
    <div style="flex:1;height:3px;background:rgba(244,244,242,0.5)"></div>
  </div>
</div>

<script>
// Uzun nomlar kadrdan chiqmasin: sig'guncha kichraytiramiz.
// Dizaynda nom qo'lda ikki qatorga bo'lingan edi, bizda 38 xil nom bor.
(function () {
  var box = document.getElementById('l-text');
  var title = document.getElementById('title');
  var size = 96;
  function overflows() {
    return title.scrollWidth > title.clientWidth + 1 ||
           box.scrollHeight > box.clientHeight + 1;
  }
  while (size > 40 && overflows()) {
    size -= 2;
    title.style.fontSize = size + 'px';
  }
  document.documentElement.setAttribute('data-ready', '1');
})();
</script>
</body></html>
"""


def build_html(poster_path, title, year, channel=CHANNEL):
    return PAGE % {
        "W": W, "H": H,
        "fonts": font_css(),
        "poster": data_uri(poster_path, "image/jpeg"),
        "title": esc(title),
        "year": esc(str(year)),
        "channel": esc(channel),
    }


def shoot(chrome, html_path, png_path):
    cmd = [
        chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", "--default-background-color=00000000",
        "--virtual-time-budget=4000",
        "--screenshot=" + png_path,
        "--window-size=%d,%d" % (W, H),
        "file://" + html_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if not os.path.exists(png_path):
        raise RuntimeError("Chrome surat yasamadi:\n" + res.stderr[-600:])


def to_jpeg(png_path, out_path, quality=88):
    from PIL import Image
    im = Image.open(png_path).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    folder = os.path.dirname(out_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    im.save(out_path, "JPEG", quality=quality, optimize=True)


def build(poster_path, out_path, title, year, chrome=None, keep_html=False,
          channel=CHANNEL):
    chrome = chrome or find_chrome()
    if not chrome:
        raise SystemExit("Chrome topilmadi. Uni o'rnating yoki CHROME_PATHS ga yo'l qo'shing.")

    tmp = tempfile.mkdtemp(prefix="thumbgen_")
    html_path = os.path.join(tmp, "page.html")
    png_path = os.path.join(tmp, "shot.png")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html(poster_path, title, year, channel))

    shoot(chrome, html_path, png_path)
    to_jpeg(png_path, out_path)

    if keep_html:
        print("     HTML: %s" % html_path)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="film id lari (bo'sh = hammasi)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--keep-html", action="store_true")
    ap.add_argument("--channel", default=CHANNEL)
    args = ap.parse_args()

    base = os.path.dirname(HERE)
    img_dir = os.path.join(base, "img")
    out_dir = os.path.join(img_dir, "wide")

    sys.path.insert(0, os.path.join(os.path.dirname(base), "MarvelCollectionBot"))
    import catalog

    chrome = find_chrome()
    if not chrome:
        raise SystemExit("Chrome topilmadi — u bo'lmasa rasm chizilmaydi.")

    wanted = args.ids or [i for i, _ in catalog.ordered()]
    made = skipped = missing = 0

    for mid in wanted:
        movie = catalog.MOVIES_DB.get(mid)
        if not movie:
            print("  ? noma'lum id: %s" % mid)
            continue
        src = os.path.join(img_dir, mid + ".jpg")
        if not os.path.exists(src):
            missing += 1
            continue
        dst = os.path.join(out_dir, mid + ".jpg")
        if os.path.exists(dst) and not args.force:
            skipped += 1
            continue
        build(src, dst, movie["title"], movie["year"], chrome=chrome,
              keep_html=args.keep_html, channel=args.channel)
        made += 1
        print("  ✅ %s  —  %s" % (mid, movie["title"]))

    print("\nYasaldi: %d | O'tkazildi: %d | Poster yo'q: %d" % (made, skipped, missing))
    if missing:
        print("Poster kutilmoqda: img/<id>.jpg (2:3)")


if __name__ == "__main__":
    main()
