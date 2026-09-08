#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WebApp'dagi katalog ma'lumotlarini catalog.py dan yasaydi.

Ilgari MOVIES va NOT_READY ro'yxatlari index.html da qo'lda yozilardi —
ya'ni bir xil ma'lumot ikki joyda turardi. 64 ta yozuv bilan bu xatoga
olib boradi (Temir odam / Halk chalkashligi shundan chiqqan edi).

Endi yagona manba — botning catalog.py fayli.

Ishlatish:
    python3 tools/webappdata.py            # index.html ni yangilaydi
    python3 tools/webappdata.py --korish   # faqat ko'rsatadi
"""

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BOT = os.path.join(os.path.dirname(ROOT), "MarvelCollectionBot")
sys.path.insert(0, BOT)

import catalog

INDEX = os.path.join(ROOT, "index.html")

# catalog dagi turlar -> WebApp dagi qisqa belgi
KIND = {"film": None, "series": "s", "animation": "a", "special": "m"}


def movies_block():
    rows = []
    prev_phase = None
    for mid, m in catalog.ordered():
        if prev_phase is not None and m["phase"] != prev_phase:
            rows.append("")
        prev_phase = m["phase"]
        kind = KIND.get(m["kind"])
        extra = ', k:"%s"' % kind if kind else ""
        rows.append('    { id:"%s",%s n:%d,%s p:%d, y:%d, uz:"%s"%s },' % (
            mid, " " * max(1, 14 - len(mid)),
            m["order"], " " * max(1, 4 - len(str(m["order"]))),
            m["phase"], m["year"], m["title"].replace('"', '\\"'), extra))
    rows[-1] = rows[-1].rstrip(",")
    return "  var MOVIES = [\n" + "\n".join(rows) + "\n  ];"


def not_ready_block():
    rows = []
    prev_phase = None
    line = []
    for mid, m in catalog.ordered():
        if catalog.is_ready(m):
            continue
        if m["phase"] != prev_phase:
            if line:
                rows.append("    " + " ".join(line))
                line = []
            rows.append("    // %d-faza" % m["phase"])
            prev_phase = m["phase"]
        line.append("%s: true," % mid)
        if len(line) == 4:
            rows.append("    " + " ".join(line))
            line = []
    if line:
        rows.append("    " + " ".join(line))
    body = "\n".join(rows).rstrip(",")
    total = len(catalog.MOVIES_DB)
    ready = catalog.ready_count()
    head = ("  // Hali kanalga yuklanganlar: %d / %d.\n"
            "  // BU BLOK QO'LDA YOZILMAYDI — tools/webappdata.py yasaydi.\n"
            % (ready, total))
    return head + "  var NOT_READY = {\n" + body + "\n  };"


def replace(src, start_re, end_marker, block):
    m = re.search(start_re, src)
    if not m:
        raise SystemExit("boshlanish topilmadi: %s" % start_re)
    end = src.index(end_marker, m.end())
    return src[:m.start()] + block + src[end + len(end_marker):]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--korish", action="store_true")
    args = ap.parse_args()

    movies = movies_block()
    not_ready = not_ready_block()

    if args.korish:
        print(movies[:400] + "\n...\n")
        print(not_ready)
        return

    src = open(INDEX, encoding="utf-8").read()
    src = replace(src, r"  var MOVIES = \[", "\n  ];", movies)
    src = replace(src, r"  // Hali kanalga yuklan.*?\n(  //.*?\n)*  var NOT_READY = \{",
                  "\n  };", not_ready)
    open(INDEX, "w", encoding="utf-8").write(src)
    print("index.html yangilandi: %d yozuv, %d tayyor"
          % (len(catalog.MOVIES_DB), catalog.ready_count()))


if __name__ == "__main__":
    main()
