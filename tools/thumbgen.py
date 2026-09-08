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
LOGO_H = 72          # logotip balandligi (px)

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

LOGO = os.path.join(os.path.dirname(HERE), "img", "logo.png")

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


# Dizayn 1280x720 uchun chizilgan. Boshqa nisbatda ham to'g'ri
# ko'rinishi uchun barcha o'lchamlar balandlikka nisbatan qayta
# hisoblanadi (k = H / 720). Kenglik ortsa — matn maydoni kengayadi.
BASE_H = 720

PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
%(fonts)s
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#15151a}
</style></head><body>

<div id="cover" style="position:relative;width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#24242a;font-family:'Bebas Neue',Impact,sans-serif">

  <!-- Fon: posterning o'zi, xiralashtirilgan va qoraytirilgan -->
  <div style="position:absolute;inset:-%(blur_pad)dpx;filter:blur(%(blur)dpx) saturate(1) brightness(0.66)">
    <div style="position:absolute;inset:0;background:#2a2730 center/cover no-repeat;background-image:url('%(poster)s')"></div>
  </div>

  <!-- Yumshoq yorug'lik: chapdan o'ngga qorayadi -->
  <div style="position:absolute;inset:0;background:radial-gradient(90%% 120%% at 22%% 50%%, rgba(255,255,255,0.14) 0%%, rgba(12,12,16,0.6) 72%%)"></div>

  <!-- Poster ostidagi siljigan oq blok -->
  <div style="position:absolute;left:%(pl2)dpx;top:%(pt2)dpx;width:%(pw)dpx;height:%(ph)dpx;background:#f4f4f2"></div>
  <div style="position:absolute;left:%(pl)dpx;top:%(pt)dpx;width:%(pw)dpx;height:%(ph)dpx;background:#2a2730 center/cover no-repeat;background-image:url('%(poster)s')"></div>

  <!-- Yil, nom, chiziq. Maydon posterning aynan balandligida —
       shunda matnning markazi poster markazi bilan bir xil bo'ladi. -->
  <div id="l-text" style="position:absolute;left:%(tx)dpx;top:%(pt)dpx;bottom:%(tb)dpx;right:%(tr)dpx;display:flex;flex-direction:column;justify-content:center;align-items:flex-start">
    <div style="font-family:'IBM Plex Mono',monospace;font-weight:600;font-size:%(fy)dpx;letter-spacing:%(ly)dpx;color:#15151a;background:#f4f4f2;padding:%(yp1)dpx %(yp2)dpx %(yp3)dpx;margin-bottom:%(ym)dpx">%(year)s</div>
    <div id="title" style="font-size:%(ft)dpx;line-height:0.86;letter-spacing:2px;color:#f5f5f3;text-transform:uppercase">%(title)s</div>
    <div style="width:100%%;height:%(lh)dpx;background:#f4f4f2;margin-top:%(lm)dpx"></div>
  </div>

  <!-- Kanal belgisi. Markazi qat'iy nuqtada turadi. -->
  <div style="position:absolute;left:%(tx)dpx;top:%(by)dpx;right:%(tr)dpx;transform:translateY(-50%%);display:flex;align-items:center">
    %(brand)s
  </div>
</div>

<script>
// Uzun nomlar kadrdan chiqmasin: sig'guncha kichraytiramiz.
(function () {
  var box = document.getElementById('l-text');
  var title = document.getElementById('title');
  var size = %(ft)d;
  function overflows() {
    return title.scrollWidth > title.clientWidth + 1 ||
           box.scrollHeight > box.clientHeight + 1;
  }
  while (size > %(ft_min)d && overflows()) {
    size -= 2;
    title.style.fontSize = size + 'px';
  }
  document.documentElement.setAttribute('data-ready', '1');
})();
</script>
</body></html>
"""


def brand_block(channel, logo_h=None):
    """Kanal belgisi: logotip bo'lsa rasm, bo'lmasa eski matnli variant."""
    if os.path.exists(LOGO):
        return ('<img src="%s" style="height:%dpx;width:auto;display:block" '
                'alt="%s">' % (data_uri(LOGO, "image/png"),
                               logo_h or LOGO_H, esc(channel)))
    return ('<div style="display:flex;align-items:baseline;'
            'font-family:\'IBM Plex Mono\',monospace;font-weight:600;line-height:1">'
            '<div style="font-size:36px;color:rgba(244,244,242,0.65)">@</div>'
            '<div style="font-size:36px;color:#f4f4f2;letter-spacing:4px;'
            'text-transform:uppercase">%s</div></div>' % esc(channel))


def layout(size):
    """Dizayn o'lchamlarini kadr balandligiga moslaydi."""
    w, h = size
    k = h / float(BASE_H)

    def p(v):
        return int(round(v * k))

    d = {
        "W": w, "H": h,
        "blur_pad": p(60), "blur": p(38),
        "pl": p(90), "pt": p(100), "pl2": p(108), "pt2": p(114),
        "pw": p(340), "ph": p(510),
        "tx": p(544), "tb": p(110), "tr": p(72),
        "fy": p(30), "ly": p(6),
        "yp1": p(12), "yp2": p(20), "yp3": p(10), "ym": p(26),
        "ft": p(96), "ft_min": p(40),
        "lh": max(2, p(5)), "lm": p(30),
        "by": p(584),
    }

    # Kadr 16:9 dan kengroq bo'lsa (kino formati 2.4:1 kabi), balandlik
    # bo'yicha kichraytirilgan elementlar juda mayda bo'lib qoladi va
    # o'ng tomonda bo'sh joy ortib ketadi. Shuning uchun ularni biroz
    # kattalashtiramiz va vertikal markazga tekislaymiz.
    wide = (w / float(h)) / (1280 / float(BASE_H))
    if wide > 1.05:
        boost = min(1.25, 1 + (wide - 1) * 0.45)
        for key in ("pw", "ph", "ft", "fy", "yp1", "yp2", "yp3", "ym", "lm"):
            d[key] = int(round(d[key] * boost))
        d["pt"] = int(round((h - d["ph"]) / 2))
        d["pt2"] = d["pt"] + p(14)
        d["by"] = int(round(h * 0.80))
        d["tb"] = int(round(h * 0.20))

    return d


def build_html(poster_path, title, year, channel=CHANNEL, logo_h=None,
               size=None):
    size = size or (W, H)
    data = layout(size)
    data.update({
        "fonts": font_css(),
        "poster": data_uri(poster_path, "image/jpeg"),
        "title": esc(title),
        "year": esc(str(year)),
        "brand": brand_block(channel, logo_h or int(round(
            LOGO_H * size[1] / float(BASE_H)))),
    })
    return PAGE % data


def shoot(chrome, html_path, png_path, size=None):
    w, h = size or (W, H)
    cmd = [
        chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", "--default-background-color=00000000",
        "--virtual-time-budget=4000",
        "--screenshot=" + png_path,
        "--window-size=%d,%d" % (w, h),
        "file://" + html_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if not os.path.exists(png_path):
        raise RuntimeError("Chrome surat yasamadi:\n" + res.stderr[-600:])


def to_jpeg(png_path, out_path, quality=88, size=None):
    from PIL import Image
    target = size or (W, H)
    im = Image.open(png_path).convert("RGB")
    if im.size != target:
        im = im.resize(target, Image.LANCZOS)
    folder = os.path.dirname(out_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    im.save(out_path, "JPEG", quality=quality, optimize=True)


def build(poster_path, out_path, title, year, chrome=None, keep_html=False,
          channel=CHANNEL, logo_h=None, size=None):
    chrome = chrome or find_chrome()
    if not chrome:
        raise SystemExit("Chrome topilmadi. Uni o'rnating yoki CHROME_PATHS ga yo'l qo'shing.")

    tmp = tempfile.mkdtemp(prefix="thumbgen_")
    html_path = os.path.join(tmp, "page.html")
    png_path = os.path.join(tmp, "shot.png")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html(poster_path, title, year, channel, logo_h, size))

    shoot(chrome, html_path, png_path, size)
    to_jpeg(png_path, out_path, size=size)

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
