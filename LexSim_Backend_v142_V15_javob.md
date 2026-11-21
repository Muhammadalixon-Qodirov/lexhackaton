# Backend v1.4.2 — BACKEND_TASKS_V15 ga javob

**Kimga:** frontend jamoasi.
**Sana:** 2026-11-21.
**Server:** `https://lex-api.e-investment.uz/api/v1`.

```bash
curl -s https://lex-api.e-investment.uz/api/v1/health
```

Javobda `"version": "1.4.2"` bo'lishi kerak. Yangi `features`:
- `turn-emotion`, `turn-gesture`, `turn-reactions` — gap ohangi, imo-ishora va tinglovchilar munosabati;
- `reprimand-ladder` — kuchayib boradigan tanbeh;
- `voice-palette-alias` — palitra nomlari (`judge_m2` va hokazo) qabul qilinadi;
- `tts-cache-free` — keshdan qaytgan TTS limitga sanalmaydi.

**Kontrakt.** Siz yuborgan yangi `contracts.schema.json` backendga qo'yildi. Sizning `Turn.gesture`, `Turn.reactions` va `Emotion`/`Gesture` enum'laringiz bo'yicha kontrakt testi yashil. Barcha testlar: 41/41.

Bu hujjat [LexSim_Backend_v141_Vazifalar_javob.md](LexSim_Backend_v141_Vazifalar_javob.md) ning davomi.

---

## Avval: siz ko'rgan ovoz muammolarining asosiy sababi

**GPU kompyuter tarmoqdan uzilgan** (o'chgan yoki uxlab qolgan). Klonlangan ovoz, tez STT va reranker shu kompyuterda ishlaydi. Server bunga to'g'ri munosabat bildirgan, zaxira yo'lga o'tgan:
- STT CPU'da: Kotib, sekin, 2,6 s audio ~16 s;
- yangi gaplar MMS ovozida;
- ma'no baholash kalit so'zlar bo'yicha.

Kompyuterni qayta yoqish loyiha egasining ishi. U yonishi bilan hammasi o'zi GPU'ga qaytadi.

Hozirgi holat:
```
GET /voice/status → {"tts":"server","stt":"cpu","sttEngine":"kotib",
                     "gpu":{"chatterbox":false,"stt":false,"rerank":false}}
```

---

## 1. Ovoz — tuzatildi

| # | Muammo | Holat |
|---|---|---|
| 1.1 | `/voice/status` → `stt: null` | ✅ Endi haqiqiy holat qaytadi: `"gpu"`, `"cpu"` yoki `null` (hech biri ishlamasa). `sttEngine` — aynan ishlayotgan dvigatel. Yangi `gpu` obyekti: GPU portlari har 10 s da haqiqatan tekshiriladi. Holat hali tekshirilmagan bo'lsa, `null`. |
| 1.2 | STT GPU'da emas | ✅ Kod to'g'ri ishlayapti: GPU o'chiq bo'lgani uchun CPU zaxirasi ishladi. GPU qaytsa, so'rov o'zi GPU'ga ketadi. Mezon ≤ 2,5 s; GPU bilan oxirgi o'lchov ~4 s (tunnel sababli), qisqartirish ustida ishlayman. |
| 1.3 | TTS 429 | ✅ **Keshdan qaytgan gap limitga sanalmaydi.** Bitta talaba keshdagi gapga 120 marta so'rov yubordi — 120/120 `200`. Yangi render uchun limit talaba boshiga **90/daq**. **`Retry-After` har bir 429 da yuboriladi:** joy bo'shashigacha qolgan soniyalar. |
| 1.4 | "Ish yo'li"dagi 2 ta gap | ✅ / ⏳ Yangi `lines.json` qo'yildi va `(sekin)` olib tashlandi. Gaplar GPU kompyuter qaytgach klonlangan ovozda yoziladi. |
| 1.5 | GPU qaytgach klon ovozda qayta yozish | ✅ Avtomatik render endi **har 10 daqiqada** ishlaydi. GPU o'chiq bo'lsa, kutadi; qaytishi bilan klonlangan ovozda yo'q doimiy gaplarni va talabaga MMS'da berilgan gaplarni o'zi yozadi. Holatini `/health` → `voice.autoPrerender` va `voice.coverage` da ko'rasiz. |

**Hozir:** `coverage` 301 tadan 267 ta tayyor. Yangi tanbeh va zal gaplari GPU qaytishini kutyapti.

## 2. Ovozlar palitrasi

| Band | Holat |
|---|---|
| 2.1 Palitra (3 sudya, 2 kotib, 4 vakil, 3 taraf, 2 guvoh) | ⏳ Har bir ovoz uchun egasining roziligi bilan yozilgan namuna kerak, ayniqsa ayol ovozlari. Loyiha egasi yig'yapti. |
| 2.1 Palitra nomlari | ✅ `POST /voice/tts` endi `judge_m2`, `lawyer_f1`, `secretary_f1` kabi nomlarni (`[a-z][a-z0-9_]{1,23}`) **qabul qiladi**. Palitra klonlanguncha har bir nom jins belgisi (`_m`/`_f`) bo'yicha mavjud ovozga yo'naltiriladi. **Ayol nomiga erkak ovozi tushmaydi.** Jins belgisi yo'q noma'lum nom 422 qaytaradi. |
| 2.2 `scene.voices` | ⏳ Ssenariy paketlari bilan birga beriladi. Hozir bitta ish bor va uning ovozlari sizdagi xaritaga mos. |
| 2.3 Ovozda emotsiya | ✅ / ⏳ `emotion` maydoni qabul qilinadi va xato bermaydi. Hozir doim neytral keshdagi ovoz qaytadi, emotsiya kutishga sabab bo'lmaydi. Emotsiya variantlarini render qilish GPU qaytgach va palitradan keyin. |

**Nomlar xaritasi (vaqtincha):**

| Kirish | Qaysi ovozga |
|---|---|
| `judge_m*` | `elder_m` |
| boshqa `*_m*` | `male` |
| `lawyer_f*`, `opponent_f*`, `witness_f*`, `expert_f*` | `female_alt` |
| boshqa `*_f*` (`secretary_f1`, `clerk_f1`, …) | `female` |

## 3. Mimika va imo-ishora — har bir `npcTurn` da ✅

Har bir `npcTurn` da ma'noga mos `emotion` bor, kerakli joyda `gesture` ham bor. Ovoz ohangi, yuz va harakat bitta jadvaldan olinadi va bir-biriga zid kelmaydi.

| Vaziyat | `emotion` | `gesture` |
|---|---|---|
| Sudya majlisni ochadi, tushuntiradi, «Oʻtiring» | `calm` | — |
| Vakolat tasdiqlandi | `calm` | `nod` |
| Sudya aniqlashtirishni so'raydi, vakolatni qayta so'raydi | `uncertain` | `lean-in` |
| Sudya e'tirozni qabul qiladi | `calm` | `nod` |
| Sudya iltimosnoma yoki e'tirozni rad etadi | `neutral` | `shake-head` |
| Ogohlantirish (bosqich, rol, tekshirilmagan dalil) | `impatient` | `shake-head` |
| Haqorat, pora | `upset` | `shake-head` |
| Tanbeh zinapoyasi | 7-bo'limga qarang | |
| Raqib odatdagi javob yoki e'tiroz beradi | `calm` | `lean-in` (savolga javobda) |
| Raqib noqulay faktni tan oladi («uch oy foydalanganmiz») | `uncertain` | `sigh` |
| Raqib tekshirilmagan holatga e'tiroz bildiradi | `upset` | `shake-head` |
| Raqib gapni bo'ladi (`advanced`) | `upset` | `lean-in` |
| Kotib | `neutral` | — |

- Sudyaning sabri (`meters.patience`) tugab borayotgan bo'lsa, oddiy gapda ham yuzi `impatient` yoki `upset` bo'ladi.
- Mumkin bo'lgan qiymatlar sizning sxemangizdagi bilan bir xil.

## 7. Zal "tirik" bo'lsin

### 7.2. Kuchayib boradigan tanbeh ✅

O'tirgan holda murojaat qilish va «Hurmatli sud» demaslik uchun har birining **o'z hisoblagichi** bor. Hisoblagich sessiya davomida saqlanadi. Har bosqichda 2 xil gap bor, tasodifiy tanlanadi va so'zma-so'z takrorlanmaydi.

| Necha marta | Sudya (o'tirib gapirish) | `emotion` / `gesture` | Ball |
|---|---|---|---|
| 1 | «…sudga oʻrningizdan turib murojaat qiling.» yoki «…tik turib murojaat qilinadi.» | `calm` / — | beginner: **0** (`decisions` da `info`, «eslatma, ball ayirilmadi»); intermediate: −1; advanced: −2 |
| 2 | «Sizga ikkinchi marta eslatyapman: sudga tik turib murojaat qilinadi.» yoki variant | `impatient` / `shake-head` | −2 |
| 3 | «Sud majlisi tartibiga rioya qilmayapsiz. Ogohlantirish bayonnomaga kiritiladi.» yoki variant | `upset` / `shake-head` | −5, `bad` |
| 4+ (`advanced`) | «…sud qonunda nazarda tutilgan choralarni qo'llashi mumkin.» yoki «bu oxirgi ogohlantirish…» | `upset` / `shake-head` | −5 va etika mezoni pasayadi |

- «Hurmatli sud» demaslik ham xuddi shu zinapoya bo'yicha ishlaydi, gaplari o'ziga xos.
- Bir gapda ikkala xato bo'lsa, sudya **bitta** tanbeh aytadi (o'tirish ustun), lekin ikkalasi ham hisoblanadi.
- Har bir tanbehda munosabat: mijoz `uncertain`, kotib `neutral`.
- **Choralar uchun modda aytilmaydi.** Mentor bazadan tasdiqlagach qo'shiladi. Birinchi ikki bosqichda IPK 167 ko'rsatiladi: u allaqachon tasdiqlangan.
- Qolgan xatolar (gap bo'lish, raqibga to'g'ridan-to'g'ri murojaat, mavzudan chetga chiqish) keyingi bosqichda shu zinapoyaga ulanadi. Ularni tanish uchun aniq signal kerak, masalan gap bo'lish uchun «sudya gapirayotgan payt» belgisi. Sizdan shu signalni yuborish so'raladi.

### 7.3. `reactions` ✅

| Gap | `reactions` |
|---|---|
| Sud talabaning iltimosnomasini yoki e'tirozini rad etdi | `opponent: reassured`, `principal: upset` |
| Sud talabaning e'tirozini qabul qildi | `opponent: upset`, `principal: reassured` |
| Raqib noqulay faktni tan oldi | `principal: reassured`, `judge: calm` |
| Talaba kuchli dalil keltirdi (lahza 4/4) | sudyaning keyingi gapida `opponent: uncertain`; raqibning keyingi gapi `lean-in` bilan |
| Sudya tanbehladi yoki ogohlantirdi | `principal: uncertain`, `secretary: neutral` |
| Vakolat tasdiqlanmadi, kelishuvga yaqin | `principal: upset` / `reassured` |
| Raqib gapni bo'ldi, sudya to'xtatdi | `opponent: uncertain` |

- Har gapda ≤ 5 ta munosabat bo'ladi.
- So'zlovchining o'zi munosabatlar ichida kelmaydi.

### 7.4. Kichik lahzalar

| # | Holat |
|---|---|
| 1. Maslahatxona va qaror | ✅ Avvaldan bor edi: maslahatxonaga ketishda va qaytishda hamma turadi (`scene.everyoneStands: true`), qaror tik turib tinglanadi, keyin «Oʻtiring». |
| 2. Guvoh | ⏳ Hozirgi ishda guvoh yo'q. Javobgarlikni tushuntirish moddasini mentor bazadan qo'yadi, guvoh bor ssenariy bilan birga. |
| 3. Raqib gapirganda talaba tik tursa | ⏳ Buning uchun «hozir kim gapiryapti» signali kerak. Hozir `standing` faqat talaba sudga murojaat qilganda tekshiriladi. |
| 4. Kotib: «Bayonnomaga kiritildi.» | ✅ Faqat sudning iltimosnoma bo'yicha ajrimidan keyin aytiladi (`secretary`, `neutral`) |
| 5. Juda uzun monolog | ✅ 120 so'zdan ko'p bo'lsa, sudya muloyim to'xtatadi: «Qisqaroq, mohiyatini ayting.» yoki variant (`calm` / `lean-in`). Keyin gap odatdagidek baholanadi. 90 soniyalik chegara frontend tomonda: audio davomiyligi bizga kelmaydi. |
| 6. Raqib gapni bo'ladi | ✅ `advanced`, tushuntirish yoki dalillar bosqichida, uzun gapdan keyin, **sessiyada ko'pi bilan 1 marta**: raqib «Eʼtiroz, hurmatli sud!», sudya «Javobgar vakili, navbatingiz kelganda gapirasiz. Davom eting.» |

## 4. 10 ta ssenariy: yuridik va mantiqiy tekshiruv

- 4.1-bandga qo'shilaman: iqtisodiy sudda faqat tadbirkorlar orasidagi nizo ko'riladi, «yuk tashish» mavzusi ham to'g'ri tanlangan.
- Linterga (`scenario_pkg.py validate`) qo'shiladigan tekshiruvlar: sanalar ketma-ketligi, summalarni qayta hisoblash (asosiy qarz + penya, stavka × kun × summa) va `scene.papers` dagi har bir hujjat `evidence[]` ga mosligi. Mentorning birinchi yangi paketi bilan birga qilinadi, chunki sana va summalar maydonlari o'sha paketda aniqlanadi.
- 4.5-banddagi tekshiruv varaqasi `SCENARIO_FORMAT.md` ga qo'shiladi.

## 5. `POST /records` va `/teacher/records`

⏳ Qila olaman, lekin bu talabaning shaxsiy ma'lumoti (ovozi). Loyiha egasi quyidagilarni tasdiqlashi kerak:
- saqlash muddati, taklif — 180 kun;
- shifrlash kaliti qayerda saqlanadi;
- o'chirish so'rovi qanday beriladi.

Tasdiq kelgach endpoint'lar va kontrakt maydonlari alohida hujjatda beriladi.

---

## Sizdan kerak

1. `voice-coverage.mjs` va `live.mjs` ni **GPU kompyuter qaytgach** qayta ishga tushiring. Shungacha `case` va `court` da bir nechta `miss` bo'lishi kutilgan: yangi gaplar hali klonlangan ovozda yozilmagan.
2. `npcTurn.gesture` va `reactions` endi keladi. Yuzlar haqiqatan o'zgarayotganini o'yinchida tekshiring.
3. Gap bo'lishni va raqib gapirayotganda tik turishni tanish uchun «kim gapiryapti / audio tugadimi» signali kerak. Uni qanday yuborishingiz qulay, ayting.
