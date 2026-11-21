# LexSim backend v1.4.0 — yangiliklar va frontendga ta'siri

**Kimga:** frontend jamoasi (`lexsim-web`).
**Sana:** 2026-11-21.
**Server:** `https://lex-api.e-investment.uz/api/v1` (2026-11-21 dan, HTTPS, `lexsim_owner` cookie endi `Secure`). Eski lokal manzil `http://192.168.88.110:8100/api/v1` vaqtincha ishlab turibdi, lekin sessiyalar ikki serverda alohida saqlanadi, shuning uchun hammasini yangi manzilga o'tkazing. Tekshirish: `GET /health` → `"version": "1.4.0"`, `features` ichida `"live-procedure"`.
**Kontrakt:** `protocol: 1` o'zgarmadi. Yangi narsalar mavjud maydonlar orqali yoki qo'shimcha maydon sifatida keladi. `contracts.schema.json` bo'yicha test o'tadi.

Oldingi hujjatlar:
- [LexSim_Backend_v3_javob.md](LexSim_Backend_v3_javob.md);
- [LexSim_Backend_v132_javob.md](LexSim_Backend_v132_javob.md);
- [LexSim_Backend_v14_jonli_sud.md](LexSim_Backend_v14_jonli_sud.md).

Bu hujjat ularning ustidan oxirgi o'zgarishlarni jamlaydi.

---

## 0. Qisqacha

| # | Nima o'zgardi | Frontendda nima qilish kerak |
|---|---|---|
| 1 | **Jonli sud:** sudya talabaga qarab yo'lni o'zgartiradi (aniqlashtirish, savol, iltimosnoma, e'tiroz, kelishuv) | Hech narsa. Yangi gaplar odatdagi `dialogue.npcTurn` bilan keladi. Faqat bosqich har gapda o'zgarmasligini hisobga oling (2-bo'lim) |
| 2 | **Haqiqiy ovozlar:** sudya, kotib, raqib va taraf klonlangan tabiiy ovozda, oldindan yozilgan | `voice` ni rolga qarab yuboring (3-bo'lim) |
| 3 | **STT GPU'da:** 5 s audio ~1–2 s da taniladi | Hech narsa. `confidence` hali `null` |
| 4 | **Tezlik:** talaba gapirib bo'lgach, javob ovozining birinchi so'zigacha ~1,5–4 s | Ovoz uchun alohida kutish holati shart emas, matn bir zumda keladi |
| 5 | GPU o'chsa, kutmasdan zaxira yo'lga o'tadi | Hech narsa |

---

## 1. Talabaning bir gapiga javob qanday yig'iladi

```
Talaba (matn yoki ovoz)
  │  ovoz bo'lsa: POST /voice/stt  ─────────────── 1,3–2,4 s (GPU Kotib)
  ▼
POST /sessions/{id}/turns {text, inputMode, ...}
  │  1) qoidalar: «Hurmatli sud», tik turish, pora, haqorat, modda bormi ─ ~5 ms
  │  2) harakatni aniqlash: savol / iltimosnoma / e'tiroz / kelishuv / oddiy javob
  │  3) javob zaifmi → sudya aniqlashtiradi (bosqich o'zgarmaydi)
  │  4) bosqich ishlovchisi + ma'no bahosi (GPU reranker) + qonun qidiruvi ── 0,1–1,3 s
  │  5) raqib javobi: 57 ta tayyor javobdan eng mosi (reranker tanlaydi)
  ▼
{events, snapshot} ─── npcTurn'lar (role: judge / secretary / opponent / system)
  │
  ▼  har bir npcTurn uchun: POST /voice/tts {text, voice} ─ oldindan yozilgan bo'lsa 0,01 s
Ovoz + subtitr
```

**Real o'lchov** (2026-11-21, haqiqiy zanjir: audio → STT → turn → TTS):

| Talaba gapi (audio) | STT | Backend | 1-javob ovozi | **1-so'zgacha** |
|---|---|---|---|---|
| E'tiroz, 6,8 s | 2,4 s | 1,3 s | 0,01 s | **3,7 s** |
| Penya iltimosnomasi, 7,2 s | 1,8 s | 1,3 s | 2,6 s* | 5,6 s* |
| "Qo'shimcha materiallarimiz yo'q", 3,7 s | 1,3 s | 0,1 s | 0,01 s | **1,4 s** |

\* Shu gap keshda yo'q edi. Hozir yangi sud gaplari ham render qilinmoqda (3.2-bo'lim). Tugagach, bu qator ham ~3 s bo'ladi.

**LLM (Qwen)** endi faqat `advanced` darajada, bankda mos javob topilmaganda chaqiriladi. Faqat shunda `202` va `/events` polling kerak bo'ladi, 60–110 s. Boshqa hollarda `/turns` doim `200`.

---

## 2. Jonli sud: frontend nimani ko'radi

Bosqich endi **har gapda oldinga o'tmaydi.** Talaba quyidagilarni qila oladi va sud javob beradi:

| Talaba nima deydi (misol) | Sud javobi (`npcTurn`) | Bosqich |
|---|---|---|
| Chala javob: «Hurmatli sud, javobgar qarzdor.» | Sudya, `role: judge`: «…talabingizni aniqlashtiring: qaysi shartnoma, qancha summa, qaysi asos?» | o'zgarmaydi |
| «…javobgar vakilidan so'ramoqchiman: obyektdan qancha muddat foydalandingiz?» | Sudya: «So'z … beriladi», keyin raqib (`opponent`) javob beradi, ba'zan fakt ochiladi (`revealedFactIds`), keyin sudya savolni qaytaradi | o'zgarmaydi |
| «…guvohni chaqirishni so'rab iltimosnoma beraman…» | Sudya raqib fikrini so'raydi → raqib → sudya ajrimi (IPK 169) | o'zgarmaydi |
| «…ishni keyinga qoldirishni so'rayman» | Sudya: rad, IPK 171 | o'zgarmaydi |
| «…gapiga e'tiroz bildiraman, chunki…» | «Sud e'tirozni qabul qildi» yoki «E'tiroz rad etildi…» | o'zgarmaydi |
| «…kelishuv bitimi tuzishni taklif qilamiz» | Raqib shartini aytadi → sud: yozma bitim kerak (IPK 131–132) | o'zgarmaydi |
| Penya iltimosnomasi erta | «Bayonnomaga kiritildi, dalillardan keyin hal qilinadi». Dalillar bosqichida avtomatik eshitiladi | oldinga |

**Raqib moslashadi:**
- penya so'ralmasa, penya bahsi bo'lmaydi;
- tekshirilmagan holatga raqib e'tiroz bildiradi;
- bir xil vaziyatda turli javoblar beradi.

**Xatoning oqibati:** `advanced` darajada vakolat tasdiqlanmasa, vakil majlisga qo'yilmaydi. Sessiya `report-ready` holatiga o'tadi, natija `poor`.

**UI uchun tavsiya:**
- "Bosqich o'zgardi" belgisini `turns` soniga emas, sudyaning yangi bosqich gapiga qarab ko'rsating.
- Talabaga "Raqibga savol bering", "Iltimosnoma bering", "E'tiroz bildiring" kabi **maslahat chiplari** foydali. Backend ularni matndan o'zi taniydi, alohida endpoint shart emas.

**Hisobot va feedback:**
- har bir harakat `decisions[]` ga alohida yoziladi (`tone`, `why`, `article`, `inputMode`, `optionId`);
- beginner darajada `feedback` darhol keladi. Masalan: «Raqibga ishga oid savol berildi — u faktni tasdiqladi.» yoki «E'tiroz rad etildi: …».

---

## 3. Ovoz

### 3.1. Rollar va ovozlar

Barcha ovozlar Chatterbox GPU'da klonlangan. Egalarining roziligi bor, namunalar: [ovoz_namunalar/](ovoz_namunalar/).

| `npcTurn.role` (yoki "Ish yo'li" xonasidagi so'zlovchi) | `voice` | Ovoz |
|---|---|---|
| `judge`, podpolkovnik | `elder_m` | sudya |
| `secretary`, devonxona, arizachi | `female` | kotib (hozircha erkak ovozi) |
| `opponent`, javobgar vakili | `female_alt` | raqib advokat (hozircha erkak ovozi) |
| da'vogar, guvoh, navbatchi, tergovchi | `male` | taraf yoki guvoh |
| `speaker: "system"` | — | ovozlashtirmang, faqat sahna izohi |

Ayol rollari hozircha erkak ovozida. Ayol ovozi namunalari kelgach almashtiriladi, sizdan hech narsa talab qilinmaydi.

### 3.2. Oldindan yozilgan gaplar

| To'plam | Soni | Holat |
|---|---|---|
| Sud zali: sudya shablonlari, kotib, raqib banki (57) | 88 | ✅ tayyor |
| Sizning `lines.json` (Ish yo'li xonalari) | 97 | ✅ tayyor |
| Jonli sud gaplari: aniqlashtirish, ajrimlar, savollarga javoblar, rol nomli shablonlar | 64 | ⏳ render qilinmoqda (~30 daqiqa) |

**Natija:** `POST /voice/tts {text, voice}` shu matnlar uchun **0,003–0,01 s** da qaytadi, javob sarlavhasida `X-TTS-Cache: hit` bo'ladi. Matnni o'zgartirmasdan yuboring: `npcTurn.text` ni aynan o'zini. `ʻ`/`ʼ` muammo emas.

Keshda yo'q gap (masalan, `advanced` dagi LLM javobi) tez MMS ovozi bilan ~1–2,5 s da chiqadi. U boshqa ovozda eshitiladi, bu kutilgan holat.

### 3.3. Lab-sinxron

Har bir TTS javobida:
```
X-Duration-Ms: 3216
X-Word-Timings: [[161,441],[465,1026],…]     # taxminiy, harf soniga mutanosib
X-Word-Timings-Source: estimate
```

### 3.4. STT

- `POST /voice/stt` (wav, webm yoki ogg) endi sukut bo'yicha **GPU Kotib**: 5 s audio ~1–2 s. GPU o'chiq bo'lsa, avtomatik CPU Kotib ishlaydi, sekinroq: 18–37 s.
- Javob: `{"text", "confidence": null, "engine": "gpu", "audioSeconds", "ms"}`.
- **`confidence` hali `null`.** Server STT'da `turns.stt` maydonini yubormang (siz shunday qilyapsiz).
- Sud atamalari tuzatiladi: «pinga» → «penya», «ishonch noma» → «ishonchnoma» va hokazo. Lekin STT ba'zi so'zlarni hali xato taniydi. Tushunish asosan ma'no bo'yicha ishlagani uchun javob odatda baribir to'g'ri chiqadi.

---

## 4. Ishonchlilik: GPU o'chsa

Reranker, STT va Chatterbox alohida GPU kompyuterda turadi. U javob bermasa:

| Qism | Nima bo'ladi | Talaba nimani sezadi |
|---|---|---|
| Reranker | 30 s davomida chaqirilmaydi. Kalit so'zlar bilan baholash, raqib umumiy javob beradi | javoblar umumiyroq |
| STT | CPU Kotib ishlaydi | ovoz tanish sekinroq |
| TTS | oldindan yozilgan gaplar keshdan (GPU kerak emas), yangilari MMS bilan | deyarli sezmaydi |

Kutib qolish yo'q: o'chiq xizmat 30 s davomida umuman chaqirilmaydi.

`GET /voice/status` va kuzatuv paneli (`/monitor`, admin uchun) holatni ko'rsatadi.

---

## 5. Sizdan kerak

1. **`LEXSIM_REMOTE_KEY`** ni Next serverining `.env.local` fayliga qo'ying. Kalitni server egasi beradi. Kalitli yo'llarni jonli tekshiring: `/nlu/match`, `/store/cases`, `/xapi/statements` va har xonada `/voice/tts`.
2. **TTS'da `voice` ni rolga qarab** yuboring (3.1-jadval).
3. **Jonli sud** bo'yicha Playwright QA'ga yangi yo'llarni qo'shing:
   - zaif javob → aniqlashtirish;
   - raqibga savol;
   - asossiz va asosli e'tiroz;
   - guvoh iltimosnomasi;
   - kelishuv taklifi;
   - `advanced` + vakolatsiz.
4. Mos kelmagan maydon bo'lsa, Zod xatosini yuboring.

---

## 6. Ma'lum cheklovlar

- **Bitta ish, ikki rol.** Ikkinchi ish (kontent va mentor) keyingi bosqichda.
- **`advanced` dagi LLM** hali 60–110 s. Rasmiy API'ga o'tish (Groq yoki Gemini) server egasining qarorida, u holda 1–3 s bo'ladi.
- **`verifiedAt`** — moddalarni mentor hali tasdiqlamagan.
- **STT `confidence`** yo'q.
- **Server tarmog'i:** `192.168.88.110` faqat lokal tarmoqda. Demo joyi uchun ulanish usuli (Tailscale) hal qilinishi kerak.

---

## 7. Tez tekshirish

```bash
curl -s https://lex-api.e-investment.uz/api/v1/health | python3 -m json.tool | head -20   # version 1.4.0
python3 tools/backend_sinov.py https://lex-api.e-investment.uz   # ikkala rol, to'liq oqim
```
