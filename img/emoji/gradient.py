"""Ikonkaga Marvel rangida gradient beradi.

Shakl generatsiya qilingan rasmdan niqob sifatida olinadi, rang esa
kod bilan aniq beriladi — model rang ohangini (hue) buzib yuborardi.
"""
import colorsys
from PIL import Image

MARVEL = (0xED, 0x1D, 0x24)          # asosiy Marvel qizili


def lighter(rgb, lightness):
    """Ayni hue va to'yinganlikda, faqat yorqinligi boshqa rang."""
    h, _, s = colorsys.rgb_to_hls(*[c / 255 for c in rgb])
    r, g, b = colorsys.hls_to_rgb(h, lightness, s)
    return (round(r * 255), round(g * 255), round(b * 255))


CUT = 40          # shundan past qiymat — fon
FULL = 110        # shundan yuqori qiymat — shaklning to'la ichi


def mask_from(path, size=100):
    """Qora fonli rasmdan shakl niqobi.

    Alfa eng yorqin kanaldan olinadi: shakl qizil bo'lgani uchun
    yorqinlik bo'yicha olinsa ichi yarim-shaffof bo'lib qolardi.
    CUT..FULL oralig'i faqat chekka silliqligi uchun qoldiriladi.
    """
    im = Image.open(path).convert("RGB").resize((size, size), Image.LANCZOS)
    r, g, b = im.split()
    top = Image.new("L", im.size)
    tp, rp, gp, bp = top.load(), r.load(), g.load(), b.load()
    for y in range(size):
        for x in range(size):
            v = max(rp[x, y], gp[x, y], bp[x, y])
            if v <= CUT:
                tp[x, y] = 0
            elif v >= FULL:
                tp[x, y] = 255
            else:
                tp[x, y] = round((v - CUT) * 255 / (FULL - CUT))
    return top


def paint(mask, top, bottom):
    """Niqobni gradient bilan bo'yaydi.

    Gradient butun kadr bo'ylab emas, shaklning haqiqiy balandligi
    bo'ylab cho'ziladi — aks holda ikonkaga gradientning faqat bir
    bo'lagi tushib, rang to'liq ko'rinmaydi.
    """
    size = mask.size[0]
    box = mask.getbbox() or (0, 0, size, size)
    y0, y1 = box[1], max(box[3] - 1, box[1] + 1)

    out = Image.new("RGBA", mask.size)
    px, mp = out.load(), mask.load()
    for y in range(size):
        t = min(1.0, max(0.0, (y - y0) / (y1 - y0)))
        col = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        for x in range(size):
            a = mp[x, y]
            px[x, y] = col + (a,) if a else (0, 0, 0, 0)
    return out
