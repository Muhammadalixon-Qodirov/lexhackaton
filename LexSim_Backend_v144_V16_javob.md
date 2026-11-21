# Backend v1.4.4 — BACKEND_TASKS_V16 ga javob

**Kimga:** frontend jamoasi.
**Sana:** 2026-11-21.
**Server:** `https://lex-api.e-investment.uz/api/v1`.

**Versiya.** `/health` → `"version": "1.4.4"`. Yangi `features`:
- `turn-presence`, `interaction-context` — `presence` va `context` signallari ishlatiladi;
- `store-any-kind`, `store-ttl`, `store-owner-404` — ombor (B9).

**Testlar:** 44/44 yashil, `contracts.schema.json` (`presence`, `context`) bo'yicha kontrakt testi ham.

**Kalit.** `LEXSIM_REMOTE_KEY` Netlify'ga qo'yildi va ishlayapti. 08:13 dan boshlab sizdan kalitli so'rovlar kelyapti:
- `voice/tts` → 200;
- `store/cases` `PUT` → 200, "Ish yo'li" ishi va indeksi 5-versiyagacha yangilandi.

---

## 🔴 Hozirgi ishlar

### B1. Tik turish holati noma'lum ✅

`sit-at-desk` dan keyin `standing` `null` bo'lsa, endi `false` bo'ladi (talaba o'z joyida o'tiradi).

Jonli tekshiruv: `start → sit-at-desk → turn` («Hurmatli sud, ishonchnomani…», `stand`/`sit` siz) birinchi gapdayoq tanbeh beradi: «…sudga oʻrningizdan turib murojaat qiling.» (`calm`).

Zalga kirishda yuborayotgan `sit` ingiz zarar qilmaydi.

### B2. Signallar ✅

| Signal | Natija |
|---|---|
| `presence.standing` | Javob paytidagi holat. Oxirgi `stand`/`sit` dan **ustun**. |
| `presence.spokenSeconds > 90` | Sudya: «Qisqaroq, mohiyatini ayting.» yoki variant (`calm` / `lean-in`). Matn 120 so'zdan uzun bo'lsa ham shunday. |
| `context.during.role` = `opponent`, `witness` yoki `expert` + `stand` | Sudya: «Oʻtirishingiz mumkin.» yoki variant (`calm` / `nod`). **Ballsiz.** Har 3 marta tik turishda bir marta aytiladi. Jonli tekshiruv: 200, gap keldi. |
| `presence.heardTurnId` ≠ oxirgi NPC gapi | Siz so'raganingizdek **faqat log**: `presence_heard_mismatch` hisoblagichi va server logida sessiya id. Talabaga tanbeh berilmaydi. |

`presence` va `context` ichida noto'g'ri maydon kelsa, e'tiborga olinmaydi.

### B9. Serverless uchun ombor ✅

| # | Talab | Holat |
|---|---|---|
| 1 | Har qanday `kind` | ✅ `[\w.-]{1,40}`: `case`, `index`, `dxm-session`, `hearing` va boshqalar |
| 2 | Hajm | ✅ 512 KB chegarasi o'zgarmadi |
| 3 | Tezlik ≥ 120/daq | ✅ Talaba (`X-LexSim-Owner`) boshiga **600/daq** |
| 4 | Saqlash muddati | ✅ `dxm-session`, `hearing` — **7 kun**; qolgan turlar (`case`, `index` …) — **180 kun**. Muddat oxirgi yozuvdan hisoblanadi. Muddati o'tgan hujjat `GET` da 404 qaytaradi, har soatda o'chiriladi. 180 kunni E6 bo'yicha qaror chiqqach o'zgartirsa bo'ladi. |
| 5 | Boshqa talabaga 404 | ✅ `GET` ham, `PUT` ham **404** `case_not_found` qaytaradi: mavjudligi bilinmaydi. Avval 403 edi. |

**Egasi qayerdan olinadi:** `X-LexSim-Owner` sarlavhasidan. `PUT` da sarlavha bo'lmasa, `body.owner` ishlatiladi.

**`GET` da `X-LexSim-Owner` bo'lishi kerak.** Hozir siz uni yuboryapsiz: logda sarlavhasiz `GET` bitta ham yo'q.
- Sarlavha bo'lmasa, hozircha eski tartibda o'qiladi va logga yoziladi.
- **v1.5 dan** sarlavhasiz `GET` → 422.

**Qabul tekshiruvi (jonli, kalit bilan):**
```
PUT  /store/cases/dxm-test-1  {kind:"dxm-session", state:{step:1}, version:0}  (owner A) → 200 {version:1}
GET  /store/cases/dxm-test-1                                             (owner A) → 200, o'sha holat
GET  /store/cases/dxm-test-1                                             (owner B) → 404
PUT  /store/cases/dxm-test-1                                             (owner B) → 404
```

### B3. STT tezligi ⏳

GPU kompyuter hali ham o'chiq. Hozir `/voice/status` → `"stt":"cpu"`. GPU qaytgach, tunnel qadamlarini qisqartiraman.

---

## 🟢 Kichik ishlar

| # | Holat |
|---|---|
| B8 `npcTurn.audio` | Keyingi versiyada |
| B10 Guvoh | Guvoh bor ssenariy bilan birga |
| B11 Qayta ishga tushirish | Qabul qilindi: yangilanishlarni talabalar ishlamaydigan vaqtda qo'yaman. Qayta ishga tushirish ~4 s davom etadi. Shu vaqtda 502 bo'lsa, 2 s kutib bir marta qayta urining. Sessiyalar SQLite'da saqlanadi va yo'qolmaydi. |

Loyiha egasiga bog'liq ishlar (B4–B7) `LexSim_HOLAT.md` dagi navbat bo'yicha.
