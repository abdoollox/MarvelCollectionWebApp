#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ulashish kartalari uchun 16:9 thumbnail generatori.

Manba — bitta vertikal poster (img/<id>.jpg). Natija — img/wide/<id>.jpg.
Ya'ni har film uchun faqat BITTA rasm yuklash kifoya, qolganini skript qiladi.

Ishlatish:
    python3 tools/thumbgen.py                  # hammasini yasaydi
    python3 tools/thumbgen.py im1 av4          # faqat ko'rsatilganlarni
    python3 tools/thumbgen.py --style diagonal # boshqa uslubda
    python3 tools/thumbgen.py --force          # mavjudlarini ham qayta yasaydi
"""

import os
import sys
import argparse

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720

RED = (237, 29, 36)
DARK = (10, 12, 17)
WHITE = (255, 255, 255)

FONT_HEAVY = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

BRAND = "MARVEL KOLLEKSIYA"


# ----------------------------------------------------------------- yordamchi

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def _wrap(draw, text, font, max_w):
    """Matnni so'zlar bo'yicha qatorlarga bo'ladi (sig'ish kafolatlanmaydi)."""
    lines, cur = [], ""
    for word in text.split():
        probe = (cur + " " + word).strip()
        if not cur or text_size(draw, probe, font)[0] <= max_w:
            cur = probe
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, path, max_w, max_lines=2, start=64, low=22):
    """Matn kenglikka HAQIQATAN sig'adigan o'lchamni topadi.

    Avvalgi variant bitta uzun so'z sig'masa ham uni qo'shib yuborardi va
    matn kadrdan chiqib ketardi. Endi har o'lcham uchun barcha qatorlar
    tekshiriladi.
    """
    for size in range(start, low - 1, -2):
        font = load_font(path, size)
        lines = _wrap(draw, text, font, max_w)
        if len(lines) <= max_lines and all(
                text_size(draw, ln, font)[0] <= max_w for ln in lines):
            return lines, font
    font = load_font(path, low)
    return _wrap(draw, text, font, max_w)[:max_lines], font


def fit_one(draw, text, path, max_w, start=22, low=12):
    """Bitta qatorli matn uchun sig'adigan o'lcham."""
    for size in range(start, low - 1, -1):
        font = load_font(path, size)
        if text_size(draw, text, font)[0] <= max_w:
            return font
    return load_font(path, low)


def backdrop(poster):
    """Xiralashtirilgan, qoraytirilgan fon — posterning o'zidan."""
    src = poster.copy().convert("RGB")
    ratio = max(W / src.width, H / src.height)
    src = src.resize((int(src.width * ratio * 1.15), int(src.height * ratio * 1.15)),
                     Image.LANCZOS)
    left = (src.width - W) // 2
    top = (src.height - H) // 2
    src = src.crop((left, top, left + W, top + H))
    src = src.filter(ImageFilter.GaussianBlur(28))
    dark = Image.new("RGB", (W, H), DARK)
    return Image.blend(src, dark, 0.62)


def cover(poster, box_w, box_h):
    """Rasmni berilgan o'lchamga to'ldirib kesadi."""
    src = poster.copy().convert("RGB")
    ratio = max(box_w / src.width, box_h / src.height)
    src = src.resize((max(1, int(src.width * ratio)), max(1, int(src.height * ratio))),
                     Image.LANCZOS)
    left = (src.width - box_w) // 2
    top = int((src.height - box_h) * 0.35)   # yuzlar odatda yuqorida
    return src.crop((left, top, left + box_w, top + box_h))


# ----------------------------------------------------------------- uslublar

def style_arc(poster, title, meta):
    """1-uslub: chapda doira yoyi bilan kesilgan poster, o'ngda matn."""
    img = backdrop(poster)

    # Yoy to'liq balandlikni qoplashi uchun radius H/2 dan katta bo'lishi
    # kerak — shunda tepa va past chetlari kadrda kesiladi.
    cx, r = 400, 385
    right = cx + r                       # yoyning eng o'ng nuqtasi

    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rectangle([0, 0, cx, H], fill=255)
    md.ellipse([cx - r, H // 2 - r, cx + r, H // 2 + r], fill=255)

    panel = cover(poster, right, H)
    img.paste(panel, (0, 0), mask.crop((0, 0, panel.width, panel.height)))

    d = ImageDraw.Draw(img)
    d.arc([cx - r, H // 2 - r, cx + r, H // 2 + r], start=-90, end=90,
          fill=RED, width=9)

    x0 = right + 55
    avail = W - x0 - 55

    lines, font = fit_lines(d, title.upper(), FONT_HEAVY, avail, max_lines=3, start=56)
    line_h = text_size(d, "AJ", font)[1] + 20
    y = H // 2 - (line_h * len(lines)) // 2 - 42

    for line in lines:
        w, _ = text_size(d, line, font)
        d.rectangle([x0 - 14, y - 12, x0 + w + 14, y + line_h - 6], fill=RED)
        d.text((x0, y - 2), line, font=font, fill=WHITE)
        y += line_h + 6

    mf = fit_one(d, meta, FONT_BOLD, avail, start=22)
    d.text((x0, y + 12), meta, font=mf, fill=(212, 216, 224))

    bf = fit_one(d, BRAND, FONT_HEAVY, avail - 28, start=19)
    bw, bh = text_size(d, BRAND, bf)
    by = H - 72
    d.rectangle([x0 - 14, by - 11, x0 + bw + 14, by + bh + 13], fill=WHITE)
    d.text((x0, by), BRAND, font=bf, fill=DARK)

    return img


def style_diagonal(poster, title, meta):
    """2-uslub: diagonal kesim, chapda poster, o'ngda matn."""
    img = backdrop(poster)

    top_x, bottom_x = 620, 430

    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.polygon([(0, 0), (top_x, 0), (bottom_x, H), (0, H)], fill=255)

    panel = cover(poster, top_x, H)
    img.paste(panel, (0, 0), mask.crop((0, 0, panel.width, panel.height)))

    d = ImageDraw.Draw(img)
    d.line([(top_x, 0), (bottom_x, H)], fill=RED, width=9)

    x0 = top_x + 70
    avail = W - x0 - 55

    lines, font = fit_lines(d, title.upper(), FONT_HEAVY, avail, max_lines=3, start=58)
    line_h = text_size(d, "AJ", font)[1] + 16
    y = H // 2 - (line_h * len(lines)) // 2 - 34

    for line in lines:
        d.text((x0, y), line, font=font, fill=WHITE)
        y += line_h

    d.rectangle([x0, y + 18, x0 + 84, y + 26], fill=RED)

    mf = fit_one(d, meta, FONT_BOLD, avail, start=23)
    d.text((x0, y + 46), meta, font=mf, fill=(208, 212, 222))

    bf = fit_one(d, BRAND, FONT_HEAVY, avail, start=19)
    d.text((x0, H - 60), BRAND, font=bf, fill=RED)

    return img


def style_frame(poster, title, meta):
    """3-uslub: chapda poster kartasi, atrofida xira fon."""
    img = backdrop(poster)

    card_h = 530
    card_w = int(card_h * 2 / 3)
    cx0, cy0 = 80, (H - card_h) // 2

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle([cx0 + 12, cy0 + 16, cx0 + card_w + 12, cy0 + card_h + 16],
                 fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")

    card = cover(poster, card_w, card_h)
    img.paste(card, (cx0, cy0))

    d = ImageDraw.Draw(img)
    d.rectangle([cx0, cy0, cx0 + card_w, cy0 + card_h], outline=RED, width=5)

    x0 = cx0 + card_w + 60
    avail = W - x0 - 60

    lines, font = fit_lines(d, title.upper(), FONT_HEAVY, avail, max_lines=3, start=62)
    line_h = text_size(d, "AJ", font)[1] + 18
    y = cy0 + 96

    d.rectangle([x0, y - 32, x0 + 76, y - 24], fill=RED)
    for line in lines:
        d.text((x0, y), line, font=font, fill=WHITE)
        y += line_h

    mf = fit_one(d, meta, FONT_BOLD, avail, start=24)
    d.text((x0, y + 42), meta, font=mf, fill=(208, 212, 222))

    bf = fit_one(d, BRAND, FONT_HEAVY, avail - 28, start=20)
    bw, bh = text_size(d, BRAND, bf)
    by = cy0 + card_h - 34
    d.rectangle([x0 - 13, by - 11, x0 + bw + 13, by + bh + 13], fill=RED)
    d.text((x0, by), BRAND, font=bf, fill=WHITE)

    return img


STYLES = {"arc": style_arc, "diagonal": style_diagonal, "frame": style_frame}


# ----------------------------------------------------------------- ishga tushirish

def build(poster_path, out_path, title, meta, style):
    poster = Image.open(poster_path).convert("RGB")
    img = STYLES[style](poster, title, meta)
    folder = os.path.dirname(out_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    img.save(out_path, "JPEG", quality=88, optimize=True)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="film id lari (bo'sh = hammasi)")
    ap.add_argument("--style", default="arc", choices=sorted(STYLES))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base, "img")
    out_dir = os.path.join(img_dir, "wide")

    sys.path.insert(0, os.path.join(os.path.dirname(base), "MarvelCollectionBot"))
    import catalog

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
        meta = "%d  •  %s" % (movie["year"], catalog.PHASES.get(movie["phase"], ""))
        build(src, dst, movie["title"], meta, args.style)
        made += 1
        print("  ✅ %s" % os.path.relpath(dst, base))

    print("\nYasaldi: %d | O'tkazildi: %d | Poster yo'q: %d" % (made, skipped, missing))


if __name__ == "__main__":
    main()
