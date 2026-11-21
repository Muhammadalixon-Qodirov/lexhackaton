# Backend v1.4.1 — BACKEND_TASKS_V14 ga javob

**Kimga:** frontend jamoasi.
**Sana:** 2026-11-21.
**Server:** `https://lex-api.e-investment.uz/api/v1`.

```bash
curl -s https://lex-api.e-investment.uz/api/v1/health
```

Javobda `"version": "1.4.1"` bo'lishi kerak. Yangi `features`: `cors`, `turn-engine`, `auto-prerender`, `scenario-package`, `voice-health`.

**Kontrakt.** `protocol: 1` buzilmadi, faqat yangi maydonlar qo'shildi. Testlar: 36/36 yashil. Ular ichida `contracts.schema.json` bo'yicha kontrakt testi bor.

Bu hujjat [LexSim_Backend_v141_javob.md](LexSim_Backend_v141_javob.md) o'rnini bosadi.

---

## Muhim: sizning P0 natijalaringiz eski holatda olingan

Siz `voice-coverage.mjs` ni men ikkita narsani tuzatishimdan **oldin** ishga tushirgansiz. Muammo modellarda yoki keshning yo'qolganida emas edi. Ikkita sabab bor edi:
1. Yangi serverda `ffmpeg` yo'q edi. Shuning uchun keshda yo'q har qanday TTS va **har qanday** STT `FileNotFoundError` bilan tushardi. ✅ O'rnatildi.
2. Eski serverdagi TTS keshi hali ko'chirilmagan edi. ✅ Ko'chirildi.

Hozirgi holat (server ichida hisoblangan, yangi ovoz yaratilmagan):
- eski `lines.json` dagi 97 ta gapning **97 tasi** keshda bor;
- sud zali va "Ish yo'li"dagi barcha doimiy gaplar: **277 tadan 260 tasi** klonlangan ovozda tayyor;
- qolgan 17 tasini avtomatik render yozyapti.

`voice-coverage.mjs` ni qayta ishga tushiring.

---

## P0 — ovoz

| # | Holat | Tafsilot |
|---|---|---|
| P0-1 STT | ✅ ishlaydi | `/voice/status` → `"stt":"server"`, `sttEngine:"gpu"`. GPU o'chsa, CPU zaxira ishlaydi. ⚠️ Mezoningiz ≤ 2,5 s, hozir **~4 s**: 4 s audio → 4,2 s. Sabab: GPU kompyuter boshqa tarmoqda, har STT so'rovida bir nechta tunnel qadami bor. Qisqartirish ustida ishlayman. |
| P0-2.1 Keshni ko'chirish | ✅ | Keshda 531 fayl bor |
| P0-2.2 Yangilangan `lines.json` | ⏳ **sizdan** | Fayl bizga yetib kelmadi, ilova bo'lmagan. Uni `backend/voice_lines.json` sifatida qo'yamiz, server qayta ishga tushganda o'zi render qiladi. |
| P0-2.3 Jonli sud gaplari va variantlari | ✅ / ⏳ | 64 ta jonli sud gapi tayyor. Yangi variantlar (savolga qaytish, «keyingi bosqichda», «o'ylash» gaplari) avtomatik render qilinmoqda. |
| P0-2.4 Keshda yo'q gap | ✅ 200 | Endi doim audio qaytadi. ⚠️ Lekin **~4 s** (mezon ≤ 2,5 s) va MMS ovozida. Keshda yo'q gaplar kam, chunki doimiy gaplarning hammasi oldindan yoziladi. |
| P0-2.5 Yangi gap avtomatik prerender | ✅ yangi | Server ishga tushganda tizimning barcha doimiy gaplarini yig'adi va klonlangan ovozda yo'qlarini fonda render qiladi. Ro'yxatda sudya shablonlari, variantlar, javoblar banki, raqib gaplari va sizning `lines.json` bor. |
| P0-3 Kalit | ⏳ | Loyiha egasi shaxsan beradi |
| P0-4 Ayol ovozi | ⏳ | Namunalar kutilmoqda |

## P1 — sud mantig'i

| # | Holat | Nima qilindi |
|---|---|---|
| P1-1 `points: null` | ✅ | `decisions[].points` endi har doim butun son. Test qo'shildi. |
| P1-2 Savol ochiq turganda e'tiroz | ✅ | Raddiya bosqichida (sudya «…munosabatingiz?» deb so'ragan joyda) ikki holat bor: (1) mazmunsiz e'tiroz — sud qaror chiqaradi: «qabul qildi» yoki «rad etildi», bosqich o'zgarmaydi; (2) mazmunli raddiya («…chunki javobgar foydalangan va fakturalarni imzolagan») — bosqich javobi, majlis davom etadi. «Hurmatli sud, eʼtiroz bildiraman.» ham taniladi va rad etiladi. |
| P1-3 Erta bosqichdagi harakat | ✅ | Sudya: «Savollar … bosqichida beriladi» yoki «Iltimosnomalar … tushuntirilgach beriladi». Keyin o'z savolini qaytaradi. Bosqich o'zgarmaydi, feedback `info`: «Bu harakat keyingi bosqichda qilinadi: …». «Iltimosnomalaringiz bormi?» bosqichida keyinga qoldirish iltimosnomasi ko'rib chiqiladi (IPK 171). |
| P1-4 Vakolat feedback'i | ✅ | `bad`: «Sudya vakolatni tasdiqlovchi hujjatni so'radi: avval ishonchnomani taqdim eting (IPK 62-modda).» |
| P1-5 `beginner` da 6–11 s | ✅ | Siz to'g'ri topdingiz: raqib javobining bir yo'lida daraja tekshirilmas edi va `beginner` da ham LLM chaqirilardi. Endi LLM **faqat** `advanced` da chaqiriladi. |
| P1-6 Bir xil gap takrorlanadi | ✅ | Har bosqichda 2–3 variant, navbat bilan aytiladi. Hammasi prerender ro'yxatida. |

## P2

- **502** xizmat qayta ishga tushgan paytga to'g'ri kelgan (3–5 s). Sessiyalar SQLite'da saqlanadi va yo'qolmaydi. 502 bo'lsa, 2 soniyadan keyin bir marta qayta urining.
- **`/health` → `voice`** (yangi):
  ```json
  "voice": {"tts":"mms","stt":"gpu","cacheFiles":470,
            "gpu":{"chatterbox":true,"stt":true,"rerank":true},
            "coverage":{"canonical":277,"ready":260},
            "servedFromCache":0.96,"servedTotal":125,
            "autoPrerender":{"jobId":"pr_auto_…","done":5,"total":17,"finished":false}}
  ```
  - `gpu.*: false` — shu qism oxirgi 30 s ichida javob bermagan, zaxira yo'l ishlayapti.
  - `servedFromCache` — talabaga berilgan ovozlarning keshdan kelgan ulushi. Maqsad ≥ 0,9. Shu ko'rsatkich `/monitor` panelida ham bor.
- **STT `confidence`** hali `null`.

---

## Asosiy yangi vazifa (~10 ta ssenariy): nima qilindi, nima qoldi

### Qilindi ✅

| Sizning bandingiz | API / fayl |
|---|---|
| §6 `GET /scenarios` | Har bir ssenariyda `court`, `difficulty`, `tags[]`, `summary` |
| §6 `seed` | `POST /sessions` `seed` qabul qiladi. Bo'lmasa server o'zi yaratadi. `snapshot.seed` da qaytadi |
| §6 `npcTurn.engine` | Har bir `turn` da `engine`: `"bank"` (tayyor javob), `"llm"` (model yozgan), `"script"` (sudya yoki kotibning kanonik gapi). `llm` bo'lsa `grounding: {"articleIds": [...]}` |
| §5.4 Kutishni yashirish | Model ishlaganda (`202`) javobda **darhol** sudyaning qisqa gapi keladi: «Tushunarli.», «Sud sizni eshitdi.», «Bir lahza.». Ko'pi bilan har 3 navbatda bir marta. Hammasi oldindan yozilgan. |
| §5 qabul mezoni ≥ 90 % keshdan | `/health.voice.servedFromCache` va `/monitor` |
| §1 Ssenariy paketi | Format: `backend/SCENARIO_FORMAT.md`. Ijara ishi paketga eksport qilindi: `backend/scenarios/sud-ijara.json` (barcha bloklar) |
| §7 `validate_scenario` | `python scenario_pkg.py validate scenarios/*.json`. Tekshiradi: moddalar normalar bazasida bormi, har bir fakt dalil yoki bosqichga bog'langanmi, har bir bosqichga yetib borish mumkinmi, `yakun` bormi, qarorda `default` bormi, o'zgaruvchilar e'lon qilinganmi, `secret` boshqa rolga oshkor bo'lmaganmi, gaplar render qilinganmi. Ijara ishi: 0 xato, 6 ogohlantirish. |

### Qoldi ⏳ va nimaga bog'liq

| Nima | Nimaga bog'liq |
|---|---|
| 9 ta yangi ssenariy | **Huquqiy mazmun**: faktlar, dalillar, moddalar, qaror funksiyasi. Ularni mentor yoki huquqshunos yozib tasdiqlashi kerak. Biz modda o'ylab topmaymiz. Format va tekshiruvchi tayyor. |
| Dvigatel paketni bevosita o'qishi | Birinchi yangi paket kelgach. Hozir ijara ishi eski fayllardan o'qiladi, paket ulardan eksport qilinadi va farq yo'q. |
| `outcome.decision.rules`: qarorni talabaning ishi belgilashi | Hozir ijara ishida qaror matni qat'iy («qisman qanoatlantiriladi»), ball esa talabaning ishiga bog'liq. Qaror qoidalarini mentor yozadi. |
| §5.5 Jonli javob p95 ≤ 3 s | Rasmiy tez API kaliti (Gemini Flash yoki Groq). Hozirgi vaqtinchalik model 7–20 s, faqat `advanced` da va faqat bankda mos javob bo'lmaganda. |
| §5.3 O'rtacha ishonchda «qisqa bo'lak + tayyor javob» | Tez API'dan keyin |
| §5.5 Jonli gap klonlangan ovozda, birinchi audio ≤ 1,5 s | Chatterbox hozir 1 s audioga ~2,5 s sarflaydi. Bunga GPU yoki gap-gap oqimi kerak. Hozir keshda yo'q gap MMS bilan chiqadi. |
| §8 Oltin transkriptlar va hujum to'plami | Ssenariylar bilan birga. Ijara ishi uchun `tests/` da 36 ta test bor. |
| `npcTurn.audio = {id, durationMs}` | Keyingi versiyada qo'shiladi |

---

## Sizdan kerak

1. **Yangilangan `lines.json`.** Fayl ilova bo'lmagan, qayta yuboring.
2. `voice-coverage.mjs`, `live.mjs` va `economic.mjs` ni qayta ishga tushirib, natijani yuboring. Kutilgan natija:
   - `voice-coverage` — `FAIL 0`, bir nechta gap `miss` bo'lishi mumkin, avtomatik render tugaguncha;
   - `live` — 8/8.
3. `npcTurn.engine` ni log qiling. `servedFromCache` ni sessiya oxirida ko'rsatish foydali.
