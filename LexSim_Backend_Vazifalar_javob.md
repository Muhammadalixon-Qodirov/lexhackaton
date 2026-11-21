# Backend v1.4.5 — `LexSim_Backend_Vazifalar.md` ga javob

**Kimga:** frontend jamoasi.
**Sana:** 2026-11-21.
**Server:** `https://lex-api.e-investment.uz/api/v1`.

**O'rnatish vaqti.** v1.4.5 bugun **22:05** da avtomatik o'rnatiladi (7-ish). Siz so'raganingizdek, kunduzi qayta ishga tushirilmaydi.
- Kod tayyor va serverdagi alohida portda (8199) to'liq sinovdan o'tdi.
- O'rnatishdan oldin 46 ta test yana o'tkaziladi. Birortasi o'tmasa, o'rnatilmaydi.
- Xizmat javob bermasa, eski versiya o'zi qaytariladi.

**Tekshirish.** 22:05 dan keyin: `/health` → `"version": "1.4.5"`. Yangi `features`:
- `stt-confidence`, `stt-timings` — STT ishonchi va bosqichlar vaqti;
- `unclear-reask` — tushunarsiz javobga qayta so'rash;
- `turn-audio` — `npcTurn.audio`;
- `gpu-alert` — GPU o'chganda xabar.

**Kontrakt:** `contracts.schema.json` o'zgarmagan. Kontrakt testi yashil, barcha testlar 46/46.

---

## 1. STT kanali uzilmasin

| Tekshiruv | Natija |
|---|---|
| Bizning tunnel (110 → 185, RAG, GPU va MMS portlari) | systemd xizmati: `Restart=always`, `RestartSec=5`, `ServerAliveInterval=15`, `ExitOnForwardFailure=yes`. Bu `autossh` bilan bir xil ishlaydi. |
| **Qabul: tunnel uzilsa** | ✅ Sessiyani server tomondan o'ldirdim: **8,9 s** da 8/8 port qayta ochildi, RAG 200. Keyingi monitor tekshiruvida (≤ 10 s) `/voice/status` → `"stt":"gpu"`. Jami ~20 s, mezon ≤ 30 s. |
| GPU kompyuter tomoni (kompyuter → 110 tunneli, uxlash rejimi, BIOS) | ⏳ Loyiha egasining kompyuterida. Unga yo'riqnoma berildi: uxlash rejimini o'chirish, tarmoq kartasining quvvat tejashini o'chirish, simli tarmoq, tunnel avtomatik qayta ulanishi. Bugun kompyuter 2 marta uzildi, hozir yoniq. |
| GPU o'chganda xabar | ✅ Kod tayyor: GPU qismlari 2 daqiqadan ko'p o'chiq bo'lsa, bir marta xabar keladi, qaytganda yana xabar keladi. ⏳ Qaysi kanalga yuborishni loyiha egasi beradi (Telegram bot tokeni va chat). Shungacha xabar server logiga yoziladi. |

## 2. STT tezligi ≤ 2,5 s

**Qabul (GPU yoniq, server ichida, 6 s lik 16 kHz WAV, 10 marta):** **p50 1,79 s, p95 2,40 s** ✅.

Bu o'lchov v1.4.4 da olingan. v1.4.5 da qo'shilganlar:
- **`ffmpeg` siz yo'l.** 16 kHz mono 16-bit WAV kelsa (siz shunday yuboryapsiz), formatni o'zgartirish umuman bo'lmaydi.
- **Bosqichlar vaqti.** Har bir javobda va server logida bosqichlar vaqti bor:
  ```json
  "timings": {"convert": 0, "upload": 310, "model": 1250, "total": 1600}
  ```
- **`/health.voice.stt`** — p50 va p95 qiymatlari (3-ish).

Siz o'lchagan ~4 s ning sababi: o'sha paytda GPU o'chiq bo'lgan yoki vaqtga Netlify'dan serverimizgacha bo'lgan yo'l ham qo'shilgan. Dastlabki 20 ta so'rovni `timings` bilan solishtirsangiz, vaqt qayerga ketganini ko'ramiz.

Model GPU'da doim yuklangan turadi. Birinchi so'rov ham sekin bo'lmaydi: o'lchovning eng kichik vaqti 1,53 s.

## 3. STT ishonchi

`POST /voice/stt` javobi endi:
```json
{"text": "…", "confidence": 0.86, "lowConfidence": false, "engine": "gpu",
 "audioSeconds": 5.1, "ms": 1680, "timings": {...}}
```

**`confidence` qanday hisoblanadi** (model ishonch qiymatini bermaydi, shuning uchun o'zimiz baholaymiz):
- 70 % — so'zlarning ish lug'atida bo'lishi: ssenariy, gaplar, variantlar, moddalar;
- 15 % — so'zlar takrorlanmasligi;
- 15 % — audio uzunligiga nisbatan so'zlar soni.

**`lowConfidence` = `confidence < 0,5`.**

Qabul:
- «koʻtni tozalash kerak koʻtni» → **< 0,5**, `lowConfidence: true` ✅;
- «Hurmatli sud, ishonchnomani taqdim etaman, vakolatim tasdiqlangan» → **≥ 0,7** ✅.

**`turns` da** `stt.confidence < 0,5` kelsa (chegara 0,6 dan 0,5 ga tushirildi):
- sudya «Iltimos, fikringizni aniqroq takrorlang…» deydi (`uncertain` / `lean-in`);
- bosqich o'zgarmaydi;
- ball ayirilmaydi, `decisions[]` da `info` yoziladi.

**`/health.voice.stt`:**
```json
"stt": {"engine": "gpu", "p50Ms": 1790, "p95Ms": 2400, "samples24h": 120,
        "cpuFallbacks24h": 3, "lowConfidence24h": 5}
```

## 4. Yangi `lines.json` (115 gap) ✅

- `backend/voice_lines.json` ga qo'yildi va bugun ertalab **qayta ishga tushirishsiz** serverga chiqdi.
- Avtomatik render yangi 18 ta "qayta so'rash" gapini klonlangan ovozda yozyapti. Bu ish GPU yoniq paytda bir necha soat oladi, chunki u PREZIDENT ovozidan voz kechilgandan keyingi umumiy qayta yozish bilan birga ketyapti (pastga qarang).
- **Qabul:** `voice-coverage.mjs` ni bugun kechqurun yoki ertaga ishga tushiring.

## 5. Sud zalida qayta so'rash ✅ (v1.4.5)

| Talaba | Sud |
|---|---|
| bo'sh gap yoki faqat «Hurmatli sud» | qayta so'raydi |
| ≤ 2 so'z va mazmunsiz («ha», «xo'p») | qayta so'raydi. Istisno: «ha/yoʻq/tushunarli/bildirmaymiz» rad, huquqlar, iltimosnomalar va qo'shimcha materiallar bosqichlarida to'g'ri javob hisoblanadi |
| ish lug'atiga umuman tegmaydigan gap («koʻtni tozalash kerak») | qayta so'raydi |

**Sudya gaplari:** quyidagi 3 variant navbat bilan aytiladi, hammasi prerender ro'yxatida:
- «Daʼvogar vakili, fikringizni aniqroq bayon qiling.»
- «Sud sizni tushunmadi. Qisqa va aniq ayting.»
- «Iltimos, savolga mazmunan javob bering.»

Har bir qayta so'rashda: `emotion: "uncertain"`, `gesture: "lean-in"`, bosqich o'zgarmaydi, ball ayirilmaydi, `decisions[]` → `info`. Bunday gapga o'tirish yoki «Hurmatli sud» tanbehi ham berilmaydi.

**Qabul (alohida portda, jonli):**
```
turn {text:"ha"}                                 → «Daʼvogar vakili, fikringizni aniqroq bayon qiling.» uncertain/lean-in, info
turn {text:"Hurmatli sud, koʻtni tozalash kerak…"} → «Sud sizni tushunmadi. Qisqa va aniq ayting.»        uncertain/lean-in, info
turn {text:"Hurmatli sud, ishonchnomani taqdim etaman."} → «Vakolat tekshirildi.» — odatdagidek davom etadi
```

To'liq oqim ham (ikkala rol, lug'at yoqilgan) avvalgidek 95/100 bo'ldi. To'g'ri javoblar adashib «tushunarsiz» deb topilmadi.

## 6. `npcTurn.audio` ✅ (v1.4.5)

```json
"audio": {"id": "a7f3…c91-1795232101", "url": "/api/v1/voice/cache/a7f3…c91-1795232101.mp3",
          "durationMs": 2928, "voice": "elder_m"}
```

- **Ovoz rolga qarab tanlanadi:** `judge` → `elder_m`, `secretary` → `female`, `opponent` → `female_alt`, qolganlar → `male`. Bu sizning xaritangiz bilan bir xil. Siz `scene.voices` bo'yicha boshqa ovoz tanlasangiz, `audio` ni e'tiborsiz qoldirib, odatdagidek `POST /voice/tts` qiling.
- **`url`:** cookie yoki `X-LexSim-Key` bilan ochiladi. Javob sarlavhasi: `Cache-Control: private, max-age=31536000, immutable`.
- **`id` oxirida fayl vaqti bor.** Ovoz qayta yozilsa (masalan, klon almashsa), URL ham o'zgaradi va eski kesh ishlatilmaydi.
- **Gap keshda bo'lmasa,** `audio` maydoni bo'lmaydi.

**Qabul (alohida portda):** sud zalining ochilish gaplarida **5/5** gapda `audio` bor, `GET` → 200, 23 KB, 2928 ms.

## 7. Kichik ishlar

- **Qayta ishga tushirish:** ✅ 22:05 ga rejalashtirildi. Bundan keyin ham faqat 22:00 dan keyin.
- **v1.5:** sarlavhasiz `GET /store` → 422. Keyingi kechki yangilanishda qo'shiladi.
- **Guvoh:** ⏳ guvohli birinchi ssenariy bilan birga.

---

## Bugungi boshqa o'zgarish: `male` ovozi almashtirildi

Loyiha egasining so'rovi bilan `PREZIDENT.ogg` dan olingan klon (`male`: mijoz, guvoh, navbatchi, tergovchi) hamma joydan **o'chirildi**.

- `male` endi vaqtincha BETOFIQ klonida, pastroq ohangda ishlaydi.
- Shu rollarning gaplari qayta yozilmoqda. Tugaguncha ular MMS ovozida chiqadi.

**Sizdan:** brauzer keshida eski `male` audiosi qolgan bo'lsa, uni tozalang. `npcTurn.audio` bilan bu muammo bo'lmaydi, chunki u URL'ni o'zi yangilaydi.
