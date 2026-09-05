# MarvelCollectionWebApp

Marvel kolleksiyasining Telegram WebApp interfeysi.

Bitta `index.html` fayl — framework yo'q, build yo'q, npm yo'q.
GitHub Pages'ga push qilinsa, deploy tugadi.

## Serverga murojaat qilmaydi

Bu ilova hech qanday API'ga so'rov yubormaydi. Ko'rilgan filmlar
belgisi ikki joyda saqlanadi:

1. `localStorage` — sinxron o'qiladi, ekran kutmaydi
2. `tg.CloudStorage` — Telegramning o'z xotirasi, foydalanuvchining barcha
   qurilmalarida o'zi sinxronlanadi (1200 ms timeout bilan — bulut
   kechiksa ilova baribir ochiladi)

Statistikani bot yig'adi, WebApp emas.

## Deploy

GitHub'ga push qiling, so'ng: **Settings → Pages → Branch: `main` / root**.

Manzil: `https://<username>.github.io/MarvelCollectionWebApp/`
Shu manzilni `MarvelCollectionBot/.env` dagi `WEBAPP_URL` ga yozing.

## Rasmlar

Ikki xil rasm ishlatiladi:

| Papka | Nisbat | Qayerda |
|---|---|---|
| `img/<id>.jpg` | **2:3** vertikal | Shu WebApp katalogidagi kartalar |
| `img/wide/<id>.jpg` | **16:9** gorizontal | Botdan ulashilgan karta |

Masalan `img/im1.jpg` va `img/wide/im1.jpg`.

**Ikkinchisini qo'lda yasash shart emas** — `tools/thumbgen.py` uni
posterdan avtomatik chizadi (Claude Design'dagi "Marvel Video Covers"
dizayni bo'yicha, Chrome orqali):

```bash
python3 tools/thumbgen.py
```

Rasm yo'q bo'lsa hech narsa buzilmaydi: kartada film raqami ko'rinadi,
ulashilgan karta esa matn ko'rinishida chiqadi.

To'liq ro'yxat va o'lchamlar: [img/README.md](img/README.md)

## Nishonlar

Profil sahifasi 16 ta nishondan iborat. Hammasi **belgilangan filmlar
to'plamidan hisoblanadi** — server ham, qo'shimcha ma'lumot ham kerak emas.

Nishonlar uch bo'limga bo'lingan, har birida o'z hisobi bor:

| Bo'lim | Soni | Misol |
|---|---|---|
| Sagalar | 2 | 🧭 Cheksizlik sagasi — 23 film |
| Fazalar | 5 | ⚔️ Buyuk urush — 3-Faza to'liq |
| Qahramonlar | 9 | ⚡ Momaqaldiroq xudosi — Tor 1-4 |

Bo'lim shartning shaklidan avtomatik aniqlanadi (`saga` → Sagalar,
`phase` → Fazalar, qolgani → Qahramonlar). Shartga tushmaydigan nishon
qo'shilsa, unga `group:"hero"` kabi qiymat yozib qo'yiladi.

6-Faza uchun nishon **ataylab yo'q**: unda hozir bitta film bor, ya'ni
nishon bir bosishda ochilardi. Faza to'lganda qo'shiladi.

### Nishon qo'shish

`BADGES` massiviga qator qo'shing. Shart uch xil bo'lishi mumkin:

```js
{ id:"thor", icon:"⚡", tier:"rare", name:"Momaqaldiroq xudosi",
  desc:"Tor yo'lining hammasi", films:["thor1","thor2","thor3","thor4"] }

{ id:"phase1", icon:"🌱", tier:"common", name:"Tashabbus",
  desc:"1-Faza to'liq ko'rildi", phase:1 }          // butun faza

{ id:"infinity", icon:"🧭", tier:"legend", name:"Cheksizlik sagasi",
  desc:"1-3 fazalarning hammasi", saga:"infinity" } // butun saga
```

`tier` faqat rangga ta'sir qiladi: `common` (kulrang-ko'k), `rare`
(qizil), `epic` (binafsha), `legend` (oltin + yorqinlik).

### Yetib bo'lmaydigan nishonlar

Nishon uchun kerakli filmlardan biri `NOT_READY` da bo'lsa, uni erishib
bo'lmaydi. Bunday nishon katagida **⏳** belgisi chiqadi, varag'ida esa
izoh: *"kerakli filmlardan ba'zilari hali kolleksiyaga qo'shilmagan"*.

Bu yashirilmaydi — aks holda odam `3/4` ni ko'rib, aybni o'zidan
qidiradi. Film qo'shilishi bilan nishon o'zi ochiladi.

### Nishon = tavsiya

Nishon bosilganda pastdan varaq chiqadi va **yetishmayotgan filmlar**
ro'yxati ko'rinadi. Har biri bosiladi va to'g'ridan botga olib boradi.
Ya'ni nishonlar tizimi bir vaqtning o'zida tavsiya dvijoki.

### Yangi nishon ochilganda

Katalog tepasida oltin tasma chiqadi va haptik zarba beriladi. Buning
uchun `marvel_badges_seen` kaliti ishlatiladi — unda allaqachon
nishonlangan nishonlar ro'yxati turadi.

Ilova **birinchi marta** ochilganda tabrik chiqmaydi — mavjud nishonlar
jimgina eslab qolinadi. Aks holda eski foydalanuvchiga o'nta tabrik
birdan chiqib ketardi.

Belgi olib tashlansa nishon ham yo'qoladi va qayta erishilganda tabrik
yana chiqadi.

## Sozlamalar

`index.html` ichidagi JS boshida:

```js
var BOT = "marvelkinobot";   // @ siz — .env dagi BOT_USERNAME bilan bir xil
```

`MOVIES` massivi — filmlar ro'yxati. `MarvelCollectionBot/catalog.py` bilan
**`id` orqali** bog'langan.

`NOT_READY` — hali kanalga yuklanmagan filmlar. Hozirgi holat:
Cheksizlik sagasi (23 film) tayyor, Multikoinot sagasi (14 film) yo'q.

```js
var NOT_READY = { bw: true, shangchi: true, /* ... */ ff4: true };
```

Bunday kartalarda "TEZ ORADA" yozuvi chiqadi va ular bosilmaydi.

**Bu ro'yxat `catalog.py` bilan mos turishi kerak:** u yerda
`message_id = 0` bo'lgan film shu yerda ham `true` bo'lsin. Aks holda
karta bosiladi, lekin bot "tez orada" deb javob beradi.

Film qo'shilganda uni ikkala joydan ham olib tashlang.

## Yangi til

`LANGS` massiviga ikkinchi til qo'shilishi bilan til tanlash ekrani
o'zi paydo bo'ladi (bitta til bo'lganda u ortiqcha, shuning uchun
o'tkazib yuboriladi). Har film uchun `MOVIES` ichiga `ru: "..."`
kabi nom qo'shiladi va posterlar `img/<id>_<til>.jpg` ga o'tadi.
