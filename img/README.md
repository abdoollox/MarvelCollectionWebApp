# Rasmlar

**Siz faqat posterni yuklaysiz.** 16:9 karta undan avtomatik yasaladi.

| | Papka | Nisbat | Kim yaratadi |
|---|---|---|---|
| Poster | `img/<id>.jpg` | **2:3** | Siz |
| Karta | `img/wide/<id>.jpg` | **16:9** | `tools/thumbgen.py` |

Poster qo'yganingizdan keyin:

```bash
python3 tools/thumbgen.py
```

Skript Claude Design'da tayyorlangan dizaynni Chrome bilan chizadi —
xira fon, siljigan oq blok, yil belgisi, nom va kanal tasmasi.
Uzun nomlar avtomatik kichrayadi va ikki qatorga bo'linadi.

**Poster talablari:**

- JPG, 2:3 nisbat (masalan 500x750 yoki 600x900)
- 60-150 KB
- Nom kichik harflarda, film id siga aniq mos

Poster yo'q bo'lsa hech narsa buzilmaydi: WebApp kartada film raqami
ko'rsatadi, botdan ulashilgan karta esa matn ko'rinishida chiqadi.

## Birinchi navbatda — kanalga yuklangan 23 ta film

| # | Poster fayli | Film |
|---|---|---|
| 1 | `img/im1.jpg` | Temir odam (2008) |
| 2 | `img/hulk.jpg` | Aql bovar qilmas Halk (2008) |
| 3 | `img/im2.jpg` | Temir odam 2 (2010) |
| 4 | `img/thor1.jpg` | Tor (2011) |
| 5 | `img/ca1.jpg` | Kapitan Amerika: Birinchi qasoskor (2011) |
| 6 | `img/av1.jpg` | Qasoskorlar (2012) |
| 7 | `img/im3.jpg` | Temir odam 3 (2013) |
| 8 | `img/thor2.jpg` | Tor: Qorong'u olam (2013) |
| 9 | `img/ca2.jpg` | Kapitan Amerika: Qish askari (2014) |
| 10 | `img/gotg1.jpg` | Galaktika qo'riqchilari (2014) |
| 11 | `img/av2.jpg` | Qasoskorlar: Ultron davri (2015) |
| 12 | `img/antman1.jpg` | Chumoli-odam (2015) |
| 13 | `img/ca3.jpg` | Kapitan Amerika: Fuqarolar urushi (2016) |
| 14 | `img/ds1.jpg` | Doktor Streyndj (2016) |
| 15 | `img/gotg2.jpg` | Galaktika qo'riqchilari 2 (2017) |
| 16 | `img/sm1.jpg` | O'rgimchak-odam: Uyga qaytish (2017) |
| 17 | `img/thor3.jpg` | Tor: Ragnaryok (2017) |
| 18 | `img/bp1.jpg` | Qora Panter (2018) |
| 19 | `img/av3.jpg` | Qasoskorlar: Cheksizlik urushi (2018) |
| 20 | `img/antman2.jpg` | Chumoli-odam va Ari (2018) |
| 21 | `img/cm1.jpg` | Kapitan Marvel (2019) |
| 22 | `img/av4.jpg` | Qasoskorlar: Final (2019) |
| 23 | `img/sm2.jpg` | O'rgimchak-odam: Uydan uzoqda (2019) |

## Keyinroq — hali yuklanmagan 15 ta film

| # | Poster fayli | Film |
|---|---|---|
| 24 | `img/bw.jpg` | Qora Beva (2021) |
| 25 | `img/shangchi.jpg` | Shang-Chi va o'n uzuk afsonasi (2021) |
| 26 | `img/eternals.jpg` | Abadiylar (2021) |
| 27 | `img/sm3.jpg` | O'rgimchak-odam: Uyga yo'l yo'q (2021) |
| 28 | `img/ds2.jpg` | Doktor Streyndj: Telbalik multikoinoti (2022) |
| 29 | `img/thor4.jpg` | Tor: Sevgi va momaqaldiroq (2022) |
| 30 | `img/bp2.jpg` | Qora Panter: Vakanda abadiy (2022) |
| 31 | `img/antman3.jpg` | Chumoli-odam va Ari: Kvantomaniya (2023) |
| 32 | `img/gotg3.jpg` | Galaktika qo'riqchilari 3 (2023) |
| 33 | `img/marvels.jpg` | Marvellar (2023) |
| 34 | `img/dpw.jpg` | Dedpul va Volverin (2024) |
| 35 | `img/ca4.jpg` | Kapitan Amerika: Yangi dunyo (2025) |
| 36 | `img/tbolts.jpg` | Momaqaldiroqlar* (2025) |
| 37 | `img/ff4.jpg` | Fantastik to'rtlik: Birinchi qadamlar (2025) |
| 38 | `img/sm4.jpg` | O'rgimchak-odam: Yangi kun (2026) |
