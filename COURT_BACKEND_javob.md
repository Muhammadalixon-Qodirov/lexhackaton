# COURT_BACKEND.md ga javob — backend v1.2

**Kimga:** frontend jamoasi.
**Sana:** 2026-11-21.
**Server:** `http://192.168.88.110:8100/api/v1` — `GET /health` → `"version": "1.2.0"`.
**Holat:** P0 to'liq bajarildi, P1 asosan bajarildi. P2 (`/cases`) keyingi bosqichda. Batafsil — quyida.

Adapterdagi 1–4-bandlar (`durationMinutes`, `briefing`, `options`, event filtri) endi kerak emas, backend o'zi to'g'ri shaklda beradi. `rmt_` prefiksi va noma'lum eventlarni tashlash himoya sifatida qolsin.

---

## 1. Qabul ro'yxati (§8.2)

| # | Talab | Holat | Izoh |
|---|---|---|---|
| 1 | §3.1 snapshot: `durationMinutes` satr, `briefing` obyekt, `options: []` | ✅ | Adaptersiz o'tishi kerak. Bizdagi Python tekshiruvi o'tdi; sizning `check.ts` ni ham ishga tushiring |
| 2 | §3.2 bitta turn = bitta so'zlovchi, `role` + `emotion` | ✅ | Prefikslar yo'q. `role`: `judge`, `secretary`, `opponent`. Sahna izohlari `speaker: "system"` |
| 3 | §3.3 `roomId: "court-economic"` | ✅ | |
| 4 | §3.4 imlo ʻ / ʼ | ✅ | Serverdan chiqadigan **barcha** JSON matnlari (talaba gapi ham) javobdan oldin normallashtiriladi. Avtomatik test: `/[A-Za-z]['’‘][A-Za-z]/` topilmaydi |
| 5 | §3.5 manbalar faqat lex.uz, FK 326/578 tasdiqlangan | ✅ | 2-bo'lim |
| 6 | Idempotentlik (3 marta bir xil `clientTurnId`) | ✅ | 202 javobi ham aynan qaytadi |
| 7 | Egalik — boshqa cookie → 403 | ✅ | |
| 8 | `events?after=N` uzluksiz `sequence` | ✅ | |
| 9 | §4.1 LLM'li turn 15 s'dan ortiq bloklamaydi | ✅ | Variant **A** (async 202), 3-bo'lim |
| 10 | §4.2 `report.decisions`, `better`, `article` | ✅ | Ma'no bo'yicha baholash (GPU reranker) ham qo'shildi — 6-bo'lim |
| 11 | §4.3 maslahat −5 va `report.hints` | ✅ | |
| 12 | §4.4 `/voice/tts` MP3 (4 ovoz), `/voice/stt` | ✅ | Bitta asl ovozdan hosil qilingan — 4-bo'lim |
| 13 | Ikkala rol, yaxshi va yomon yo'l | ✅ | Yaxshi yo'l — 95/100 `excellent` (bitta maslahat −5). Yomon yo'l — 0 `failed` (pora) yoki `poor` |

**Tekshirish:** `python3 tools/backend_sinov.py` — ikkala rol, kontrakt tekshiruvlari (§8.2 dagi 1–4, 6–8, 10, 11) bilan.

---

## 2. Huquqiy manbalar (§3.5, §6)

**FK 326 va FK 578 — tasdiqlandi.** RAG bazasidagi lex.uz matni (2026-11-20 da olingan):

- **FK 326 «Neustoykani kamaytirish»** — https://lex.uz/docs/111181#-155297
  > «Agar toʻlanishi lozim boʻlgan neustoyka kreditorning majburiyatini buzish oqibatlariga nomutanosibligi koʻrinib tursa, sud neustoykani kamaytirishga haqli. Bunda qarzdor majburiyatni qay darajada bajarganligi, majburiyatda ishtirok etayotgan taraflarning mulkiy ahvoli, shuningdek kreditorning manfaatlari eʼtiborga olinishi kerak…»
- **FK 578 «Bino yoki inshootni topshirish»** — https://lex.uz/docs/180550#-186372
  > «Bino yoki inshootni ijaraga beruvchi tomonidan topshirish va ijaraga oluvchi tomonidan qabul qilib olish taraflar imzolaydigan topshirish dalolatnomasi yoki topshirishga doir boshqa hujjat boʻyicha amalga oshiriladi…»

**Penya bo'yicha isbot yuki.** FK 326 ning o'zida yozilmagan, uni Plenum qarori (OXS163, 4-band) bilan mentor tasdiqlashi kerak. Hisobotda bu haqda alohida da'vo qilinmaydi.

**`Source` maydonlari:**
- `officialUrl` — faqat `https://lex.uz/docs/...`;
- `articleNumber` — masalan `"IPK 62-modda"`;
- `effectiveAt` — lex.uz izohidagi oxirgi tahrir sanasi, masalan `"2021-04-21"`; tahrir bo'lmasa maydon yo'q;
- `verifiedAt: null` — mentor tasdiqlagach to'ldiriladi.

**Sudyaning har bir qadami IPK'ga bog'langan.** Har bir sudya va kotib turnida `articles: [{id, label, url}]` qo'shimcha maydoni bor:

| Qadam | Modda |
|---|---|
| «Sud kirib kelmoqda», «Oʻtiring», «Hurmatli sud!», tik turish | IPK 167 |
| Majlisni ochish, ishni e'lon qilish, vakolat | IPK 165, IPK 62 |
| Sud tarkibi, rad qilish huquqi | IPK 165, 20, 21 |
| Rad qilish arizasini hal qilish | IPK 22, 23 |
| Huquqlarni tushuntirish | IPK 165 |
| Iltimosnomalar | IPK 169 |
| Yozma dalillarni o'qib eshittirish | IPK 168 |
| Qo'shimcha materiallar, muzokaralar | IPK 173 |
| Maslahatxona | IPK 175 |
| Hal qiluv qarori «Oʻzbekiston Respublikasi nomidan» | IPK 186, 179 |
| Qonuniy kuchga kirish | IPK 192 |

Hamma raqamlar RAG bazasida bor. Mentor tasdig'i hali yo'q.

**Sud nomi:** «Namuna tumanlararo iqtisodiy sudi» (ochilish so'zi va `briefing.workplace`).

---

## 3. Async turn (§4.1, variant A)

- **LLM kerak bo'lmagan gap** (protsedura, RAG): odatdagidek **200**. Javob <300 ms, RAG bilan ~1,5 s.
- **Raqib LLM javobi kerak bo'lgan gap:**
  1. `POST /turns` darhol **202** qaytaradi: `events: [dialogue.userTurn, session.status{status:"in-progress"}]`, snapshot'da `pending: true`.
  2. Javob tayyor bo'lgach, `GET /sessions/{id}/events?after=N` qolgan eventlarni beradi va snapshot'da `pending: false` bo'ladi. 1,5 s oraliqda so'rang.
- **`pending` paytida** `turns`, `finish` va `documents` so'rovlariga `409 turn_pending` («Raqib advokat javob tayyorlamoqda. Biroz kuting.») qaytadi.
- **LLM kerakligini qanday bilamiz:** server shu gapni sessiya nusxasida quruq yurgizib ko'radi. Bu bir zumda bajariladi.
- **`engine` qiymati rost:** oxirgi raqib gapi LLM'dan bo'lsa `"llm"`, LLM javob bermagan yoki tekshiruvdan o'tmagan bo'lsa `"scripted"`.
- **Demo rejimi:** LLM'ni kuzatuv panelidan (`/monitor`) bir tugma bilan o'chirsa bo'ladi. Hammasi shablon bilan, 200 bilan va tez ishlaydi.

---

## 4. Ovoz (§4.4)

```
POST /api/v1/voice/tts   {"text": "…", "voice": "elder_m" | "male" | "female" | "female_alt"}   text ≤ 600
  → 200 audio/mpeg (MP3, 24 kHz, mono, 64 kbit/s), to'g'ri Content-Length, Cache-Control: private, max-age=86400
  → 404 voice_unavailable | 422 validation_failed | 502 voice_failed | 504 voice_timeout
POST /api/v1/voice/stt   (audio/wav yoki webm/ogg — ffmpeg o'zi 16 kHz mono'ga aylantiradi, ≤ 3 MB, 30 s gacha)
  → 200 {"text": "…", "engine", "audioSeconds", "ms"}     matn ʻ/ʼ bilan, sud atamalari tuzatilgan (penya, ishonchnoma …)
GET  /api/v1/voice/status → {"tts": "server" | null, "stt": "server" | null, "voices": [...], ...}
```

**Ovozlar.** Serverda **bitta** jonli o'zbek ovozi bor: MMS-TTS, erkak. Qolgan uchtasi undan balandlik va tezlikni o'zgartirib hosil qilingan:

| Ovoz | Kim | Nima o'zgartirilgan |
|---|---|---|
| `elder_m` | sudya | balandlik ×0,86, tezlik ×0,92 |
| `male` | erkak taraf yoki guvoh | asl ovoz |
| `female` | kotib | balandlik ×1,32 |
| `female_alt` | raqib vakili (ayol) | balandlik ×1,42, tezlik ×1,04 |

Ayol ovozlari sun'iyroq eshitiladi. Haqiqiy ayol ovozi uchun Chatterbox (7002) bor, lekin u bir gapga ~70 s sarflaydi.

**Tezlik:**
- sudya va kotib shablonlari hamda raqib namunalari server ishga tushganda oldindan tayyorlanadi, keshdan **<0,3 s** keladi;
- yangi gap ~2–7 s oladi (server CPU yuklanishiga bog'liq).

**Maxfiylik:**
- STT uchun yuborilgan audio Gradio diskidan darhol o'chiriladi, backend uni saqlamaydi;
- TTS keshida faqat NPC gaplari bor, talaba ovozi u yerga tushmaydi.

---

## 5. Sahna va tik turish (§4.5)

- **`scene`:** turnlarda qisman (`Partial<CourtScene>`), snapshot'da to'liq holat (`scene`, qo'shimcha maydon).
- **Ochilish ketma-ketligi:**
  1. kotib: «Sud kirib kelmoqda…» — `everyoneStands: true, judgeIn: false`;
  2. system: «Sudya zalga kirdi.» — `judgeIn: true`;
  3. sudya: «Oʻtiring.» — `everyoneStands: false`;
  4. sudya: ochilish so'zi;
  5. kotib: hisobot;
  6. sudya: vakolat so'raydi.
- **Qaror:**
  1. sudya: maslahatxonaga;
  2. system: `judgeIn: false`;
  3. kotib: «Sud kirib kelmoqda…» — `everyoneStands: true`;
  4. system: `judgeIn: true`;
  5. sudya: xulosa qismi;
  6. sudya: «Oʻtiring. Sud majlisi yopiq…» — `everyoneStands: false`.
- **`stand` / `sit`:** `InteractionRequest.action` sifatida qabul qilinadi. Yana `inspect-phone` ham qabul qilinadi, u hech narsa qilmaydi.
  - Talaba `sit` holatida gapirsa, sudya birinchi marta «…, sudga tik turib murojaat qiling.» deydi (IPK 167).
  - Har safar `communication` mezonidan ball tushadi va `decisions` ga yoziladi.
  - Klient hech qachon `stand`/`sit` yubormasa, qoida o'chiq: eski klientlar jarimasiz ishlaydi.

---

## 6. Hisobot (§4.2, §4.3)

- **`decisions[]`.** Har bir talaba gapi uchun `{at, prompt, chose, tone, points, why, better, article}`.
  - Bitta gapda bir nechta kuzatuv bo'lsa (masalan, murojaatsiz va o'tirib), har biri alohida yoziladi.
  - `article` faqat bazada tasdiqlangan modda, masalan `"IPK 167-modda"`.
- **`hints`** — olingan maslahatlar soni. **`reflect`** — mulohaza savoli (rolga qarab).
- **Maslahat narxi.** Har bir `GET /hint` shu bosqich uchun **bir marta −5 ball** hisoblanadi va `decisions` ga `tone: "info"` bilan tushadi.
  - Ballsiz oldindan yuklash kerak bo'lsa: `GET /hint?preview=1`.
  - `assessment` rejimida `409 hints_disabled`.
- **Etika.** Pora, bosim yoki yolg'on ko'rsatuvga undash bo'lsa: `zeroedByEthics: true`, ball 0, natija `failed`, sudya ogohlantiradi.
- **Ma'no bo'yicha baholash (§4.2 tavsiyasi).** Talaba gapi har bir muhim lahzaning namunaviy to'g'ri va noto'g'ri gaplari bilan GPU reranker (`bge-reranker-v2-m3`) orqali solishtiriladi. Bitta tekshiruv 30–440 ms oladi.
  - Moslik ≥ 0,5 → daraja 3. To'liq 4-daraja uchun modda raqamini aytish baribir kerak.
  - Ish materiallariga zid da'vo (masalan, "hisob-fakturalar soxta") aniqlanadi va etika ballidan tushadi.
  - Kalit so'z yordamchi signal bo'lib qoldi.
  - Natija: to'g'ri fikrni boshqa so'zlar bilan aytgan talaba **86/100** oldi. Oldin u past ball olardi.
  - Hisobotdagi `decisions[].semantic` da moslik bahosi ko'rinadi. Namunalarni mentor [backend/semantic.json](backend/semantic.json) da tahrirlaydi.
  - GPU kompyuter o'chiq bo'lsa, faqat kalit so'z bo'yicha baholanadi.

---

## 7. Hali qilinmagan ishlar

| Ish | Nega | Qachon |
|---|---|---|
| **P2 — `/cases` "Ish yo'li"** (`kind: "lease"`, bosqichlar `l-consult` → `l-hearing`) | Katta alohida dvigatel: tugunlar, variantlar va tayyor papka. `engine.ts` va `ishga-tiklash.ts` ni o'qib, Python'da takrorlash kerak | Keyingi bosqich. Birinchi navbatda faqat `l-hearing` — hozirgi sud majlisi variantli rejimda va erkin matn bilan |
| Chatterbox (GPU) tabiiy ovozlari | Backend tayyor, GPU kompyuterdan tunnel kerak ([Chatterbox_Serverga_Ulash.md](Chatterbox_Serverga_Ulash.md)) | GPU kompyuter egasi tunnelni ochgach |
| `verifiedAt` to'ldirish | Mentor tasdig'i kerak | Mentor ko'rib chiqqach |
| LLM < 15 s | Serverda GPU yo'q, Qwen3.6-35B CPU'da birinchi tokengacha 45–70 s. Kichik model (Qwen 7B/4B) o'zbek tilida yomonroq | 10-bo'lim, 2-savol |

---

## 8. Qo'shimcha maydonlar (Zod ularni e'tiborsiz qoldiradi)

| Joy | Maydon |
|---|---|
| Snapshot | `pending: boolean`, `scene: CourtScene`, `standing: boolean \| null` |
| Turn | `role`, `scene`, `articles: [{id, label, url}]` |
| `dialogue.npcTurn.payload` | `revealedFactIds` |
| Assessment | `decisions`, `hints`, `reflect` |
| `/health` | `version`, `queue_depth`, `llm.last_ms`, `rag_db` |

`protocol` = **1** bo'lib qoldi, buzuvchi o'zgarish yo'q.

---

## 9. Ish tartibi bo'yicha

- **Kuzatuv paneli:** `http://192.168.88.110:8100/monitor`, admin token bilan.
  - Ko'rinadi: har bir so'rov vaqti qismlarga bo'lingan holda (LLM, RAG, TTS, STT, dvigatel), xizmatlar holati, CPU.
  - Kalitlar: LLM, RAG, TTS va STT modelini almashtirish.
- **Proxy bo'yicha:** `rewrites` tavsiyasi bekor qilindi, faqat sizning adapteringiz orqali.
- **Sizdan kerak:** Playwright QA natijasi va `check.ts` chiqishi. Biror maydon o'tmasa, Zod xabarini yuboring.

---

## 10. Ochiq savollarga javob

1. **TTS (7008) qaysi model?**
   - Meta **MMS-TTS** (VITS), o'zbekcha, bitta erkak ovozi. Lotin matnni kirillga o'girib gapiradi.
   - Login so'ragani — Gradio UI'ning o'zi. Endi undan foydalanmang, `/api/v1/voice/tts` ni ishlating.
   - Kechikish: yangi gap 2–7 s, keshdan <0,3 s. Qolgan 3 ovoz — 4-bo'lim.
   - Ikkinchi model: **Chatterbox** (7002), tabiiyroq, lekin ~70 s/gap. Faqat oldindan yozib olish uchun.
2. **Qwen'ni 15 s gacha tushirish:**
   - Hozirgi CPU serverda real emas.
   - Variantlar: (a) GPU'li server; (b) tashqi API (Claude yoki boshqa) — 1–3 s; (c) kichikroq model — o'zbekcha sifati pasayadi.
   - **Demo uchun tavsiya:** async rejim yoqilgan holda LLM ishlayversin; hakamlar oldida sekin bo'lsa, panelda LLM'ni o'chiring (`engine: "scripted"`).
3. **`stand` / `sit` qabul qilinadimi?** Ha, allaqachon qabul qilinadi (5-bo'lim).
4. **§5 qachon?** Keyingi bosqich. Birinchi prototip — `l-hearing`. Uning uchun `CaseSnapshot` dagi `options` (3 foydali + 1 ishonarli xato) matnlarini mentor bilan kelishib olish kerak.
5. **Hakaton joyida server qanday ishlaydi?** Server `192.168.88.110`, faqat lokal tarmoqda. Ikki yo'l:
   - (a) **Tailscale yoki WireGuard** yopiq tunnel — tavsiya. Server va demo noutbukka o'rnatiladi, port ochilmaydi.
   - (b) Backend demo noutbukda ishga tushiriladi. Lekin RAG bazasi (PostgreSQL + bge-m3) va ovoz modellari serverda, noutbukka ko'chirish og'ir.

   Qaror server egasida.
