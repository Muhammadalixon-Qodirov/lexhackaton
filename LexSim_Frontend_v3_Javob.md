# LexSim — Frontend javobi: backend v1.3 qabul qilindi

**Kimga:** LexSim court backend jamoasi (AI dasturchi va uning agenti)
**Kimdan:** LexSim frontend (`lexsim-web`, Next.js 16)
**Sana:** 2026-11-21
**Asos:** sizning `LexSim_Backend_AI_javob.md` (v1.3) va oldingi hujjatlar:
- `LexSim_Frontend_v2_Backend_Moslash.md`;
- `LexSim_Backend_AI_Toliq_Topshiriq.md`.

---

## 0. Qisqacha

| | Holat |
|---|---|
| v1.3 darajalar (beginner / intermediate / advanced) | ✅ Qabul qilindi, frontendga ulandi, jonli tekshirildi |
| `reveal-options`, `silence`, `inputMode`, `stt`, `hint` | ✅ Ulandi |
| Kalitli API (`/nlu/match`, `/store/cases`, `/xapi/statements`, `/voice/*`) | 🟡 Kod tayyor. Kalit `.env.local`ga qo'yilgach jonli tekshiriladi |
| Siz so'ragan `contracts.schema.json` | ✅ Ilova qilindi |
| Siz so'ragan ovoz ro'yxati (`/voice/prerender` uchun) | ✅ Ilova qilindi: 97 ta gap |
| Ochiq muammolar | §4 da, ustuvorlik bo'yicha |

---

## 1. Biz tekshirgan narsalar (kalitsiz, cookie sessiya orqali)

Server manzili: `http://192.168.88.110:8100/api/v1`.

| Tekshiruv | Natija |
|---|---|
| `POST /sessions {scenarioId, mode, level:"beginner"}` | 4 ta variant chiqdi; har javobdan keyin `feedback` va modda keldi ✅ |
| `level:"intermediate"` | Variantlar dastlab yo'q; `interactions {action:"reveal-options"}` ularni ochadi, `optionsRevealed:true` ✅ |
| `level:"advanced"` | `optionId` yuborilsa **422** ✅; `/hint` chaqirilsa **409** ✅; variant ham, maslahat ham yo'q ✅ |
| `turns {text, inputMode:"voice", stt:{confidence}}` | Qabul qilinadi ✅ |
| `GET /health` | ⚠️ `version: "1.2.0"` qaytaryapti (§4, B1) |

Avtomatik QA (Playwright) to'liq o'tdi:
- `economic.mjs` — Iqtisodiy sud: beginner variantlar, advanced'da variant ham, maslahat ham yo'q;
- `levels.mjs`;
- `case.mjs`;
- `theft.mjs`;
- `dismiss.mjs`.

---

## 2. Frontend sizning API'ni qanday ishlatadi (aniq shartnoma)

> Muhim: brauzer hech qachon serveringizga to'g'ridan-to'g'ri murojaat qilmaydi. Barcha chaqiruvlar Next.js serveri orqali o'tadi. Kalit faqat serverda turadi.

### 2.1. Ikki xil autentifikatsiya

1. **Sessiya (cookie):** `/sessions/**`, `/scenarios`, `/health`. Har bir talaba (owner) uchun alohida cookie jar saqlanadi.
2. **Kalitli (server-server):** quyidagi ikki header bilan:
   ```
   X-LexSim-Key:   <LEXSIM_REMOTE_KEY>
   X-LexSim-Owner: <studentHash>   // sha256("lexsim:v1:" + ownerToken).hex.slice(0,32)
   ```
   `studentHash` qaytarib bo'lmaydigan, barqaror identifikator. Ism, email va cookie **hech qachon** yuborilmaydi. Iltimos, `X-LexSim-Owner` ni faqat shu ko'rinishda saqlang va loglang.

### 2.2. Ishlatiladigan endpointlar va timeoutlar

| Endpoint | Qayerda | Timeout | Izoh |
|---|---|---|---|
| `GET /health`, `GET /scenarios` | Hub kartasi | 4 s | Server o'lik bo'lsa, karta yashirinadi |
| `POST /sessions` | Iqtisodiy sud | qisqa | `level` yuboriladi |
| `GET /sessions/{id}` | | qisqa | |
| `POST /sessions/{id}/turns` | | **180 s** | Sizda LLM 60–110 s; biz async 202 + `/events` ni ham qo'llaymiz |
| `GET /sessions/{id}/events?after=n` | | qisqa | Polling |
| `POST /sessions/{id}/interactions` | | qisqa | `stand`, `sit`, `reveal-options`, `silence`, … |
| `POST /sessions/{id}/documents` | | qisqa | |
| `POST /sessions/{id}/finish` | | 65 s | |
| `GET /sessions/{id}/report`, `POST …/appeal` | Hisobot | qisqa | |
| `GET /sessions/{id}/hint[?preview=1]` | | qisqa | `preview` — ballsiz ko'rish; haqiqiy hint −5 |
| `POST /nlu/match` 🔑 | "Ish yo'li" | **4 s** | §2.3 |
| `GET/PUT /store/cases/{id}` 🔑 | "Ish yo'li" | 8 s | §2.4 |
| `POST /xapi/statements` 🔑 | "Ish yo'li" | 8 s | §2.5 |
| `GET /voice/status` | Barcha xonalar | 3 s | |
| `POST /voice/tts` 🔑/cookie | | 20 s | `{text, voice}` |
| `POST /voice/stt` 🔑/cookie | | 40 s | `audio/wav` 16 kHz mono |

🔑 — kalitli chaqiruv.

**Degradatsiya qoidasi:** kalitli chaqiruvlarning har qandayi xato bersa yoki timeout bo'lsa, frontend o'zining lokal mantig'i bilan davom etadi. Talaba hech qachon xato ekranini ko'rmaydi. Shuning uchun **tez va aniq status kodlari** biz uchun sekin "to'g'ri" javobdan muhimroq.

### 2.3. `/nlu/match` — "Ish yo'li" ishlarida o'z so'zi bilan javob

Biz yuboradigan so'rov:
```json
{
  "utterance": "Hurmatli sud, da'vogar 9–10-oktabr kunlari kasal bo'lgan…",
  "inputMode": "text",
  "stt": { "confidence": 0.82 },
  "context": { "case": "labour", "stage": "hearing", "node": "h-open", "prompt": "Sudya: Da'vo talabingizni bayon qiling." },
  "candidates": [ { "id": "claim", "text": "…", "tone": "good" }, { "id": "env", "text": "…", "tone": "bad" } ],
  "rubric": { "mustAddress": true, "forbidden": ["pora", "tanish", "konvert", "pul beraman", "kelishib qo'yamiz"] }
}
```

`stt` maydoni faqat ovozli javobda yuboriladi.

Biz kutadigan javob (o'qiladigan maydonlar):
```json
{ "match": { "id": "claim", "score": 0.91 } | null,
  "clarify": "Qaysi kunlar haqida gapiryapsiz?" | null,
  "quality": { "ethics": "ok" | "violation" } }
```
- `quality.ethics = "violation"` bo'lsa, biz xonadagi tuzoq variantni tanlaymiz yoki jarima beramiz.
- `match = null` bo'lsa, `clarify` matni talabaga ko'rsatiladi.
- **Kandidatlar har doim qisqa ro'yxat** (1–4 ta). Ularni ochiq to'plamdan qidirmang.

### 2.4. `/store/cases` — ishni saqlash (optimistik versiya)

```
PUT /store/cases/{caseId}
{ "owner": "<studentHash>", "kind": "labour"|"theft"|"index", "state": {…}, "version": <oxirgi ko'rgan versiya> }
→ 200 { "version": n+1 }   |   409 { "version": <joriy> }
```
- 409 kelsa, biz joriy versiyani olib bir marta qayta yozamiz. Xotiradagi engine haqiqat manbai hisoblanadi.
- Har bir talaba va ish turi uchun alohida indeks hujjat yuritiladi: `idx-<hash24>-<kind>` → `{ caseId }`. Server qayta ishga tushsa, ish shu indeks orqali tiklanadi.
- `state` — bizning ichki JSON'imiz (Set'lar `{"__set":[…]}` ko'rinishida). Uni **o'qimang va o'zgartirmang**, faqat saqlang.
- Hajmi odatda 5–40 KB.

### 2.5. `/xapi/statements`

Xona tugaganda bir marta `{ statements: [...] }` yuboriladi. Har bir qaror uchun bitta `answered` (yoki `hinted`) statement, oxirida bitta `completed` statement:
- `actor.account.name = studentHash`;
- `homePage = https://lexsim.uz`;
- kengaytmalar `https://lexsim.uz/xapi/{tone,article,better,seconds,hints,cohort}` nomlari bilan.

Takroriy yuborishga qarshi himoyamiz bor. Shunday bo'lsa ham, iltimos, server tomonda `id` bo'yicha idempotent bo'ling.

---

## 3. Siz so'ragan fayllar (ilova)

### 3.1. `contracts.schema.json`
- Fayl: `lexsim-web/docs/contracts.schema.json` (bu hujjat yonida nusxasi ham bor).
- Ichida 46 ta sxema, JSON Schema draft 2020-12, `$defs` ostida, `io: input` rejimida (so'rov yuborish nuqtai nazaridan).
- Asosiylari: `Snapshot`, `Turn`, `TurnRequest`, `Interaction`, `CreateSession`, `Assessment`, `Hint`, `Level`, `InputMode`, `CourtScene`, `RemoteStatus` va "Ish yo'li" (`Case*`) sxemalari.
- Qayta yaratish: `node tools/contracts/export.mjs`.
- **Iltimos:** CI'da javoblaringizni shu sxemalarga qarshi tekshiring. Ayniqsa `Snapshot` va `Turn` muhim. Bizda normalizer bor, lekin u faqat zaxira uchun.

### 3.2. Ovoz ro'yxati — `lines.json`
- Fayl: `lexsim-web/tools/voice/lines.json`. Generator: `node tools/voice/lines.mjs`.
- **97 ta takrorlanmas gap.** Siz ~300 ta deb taxmin qilgandingiz, lekin ikkala ishdagi barcha qat'iy gaplar shuncha. Shartga bog'liq gaplar barcha variantlari bilan olingan.

| Ovoz | Soni | Kimlar |
|---|---|---|
| `elder_m` | 37 | sudya, podpolkovnik |
| `male` | 36 | da'vogar, guvoh, navbatchi, tergovchi |
| `female` | 20 | devonxona, kotib, arizachi |
| `female_alt` | 4 | javobgar vakili |

Format:
```json
{ "voice": "male", "text": "Assalomu alaykum. Meni ishdan bo'shatishdi…", "speaker": "client", "case": "labour", "stage": "consult" }
```

**So'rov:**
- `POST /voice/tts {text, voice}` aynan shu matn bilan kelganda, **keshdan darhol (< 150 ms)** bering.
- Kesh kaliti: `sha256(voice + "|" + NFC(text))`.
- Matnni normalizatsiya qilmang. Bizda `ʻ` (U+02BB) va `ʼ` (U+02BC) ishlatiladi, ular apostrof bilan almashtirilmasin.

---

## 4. Ochiq muammolar (ustuvorlik bo'yicha)

### 🔴 B1. `/health` versiyasi noto'g'ri
`GET /health` hali ham `"version": "1.2.0"` qaytaryapti.
**Qabul mezoni:** `"1.3.x"` qaytsin va `features: ["levels","reveal-options","silence","nlu","store","xapi","prerender"]` massivi bo'lsin. Frontend imkoniyatlarni shu orqali yoqadi.

### 🔴 B2. LLM tezligi (eng katta muammo)
Bir `turn` 60–110 s davom etyapti. Talaba uchun 10 s dan ortig'i "buzildi" deb qabul qilinadi. Hozir buni kutish chipi yashirib turibdi, lekin bu yechim emas.

Bu server egasining qarori talab qilinadigan masala. Variantlar:
1. `security-agent` / `ai_demo` jarayonlarini LexSim sessiyalari paytida to'xtatish yoki ularga resurs limiti qo'yish (resurs talashuvi bartaraf etiladi).
2. Faqat AVX2 bo'lgan CPU'da 35B-A3B o'rniga kichikroq model (7–8B Q4) ishlatish: tezkor replikalar uchun kichik model, yakuniy baholash uchun katta model.
3. Javobni token-streaming (SSE) bilan berish. Shunda birinchi so'z 2–3 s da ko'rinadi, frontend esa `/events` orqali qisman matnni ko'rsata oladi.
4. Beginner va intermediate'da LLM'ni umuman chaqirmaslik: variant tanlanganda tayyor ssenariy javobi qaytsin.

**Qabul mezoni:** `turn` p50 ≤ 8 s, p95 ≤ 20 s; `/nlu/match` p95 ≤ 400 ms.

### 🟠 B3. Beginner variantlari deyarli bir xil
Hozir 4 ta variantdan 3 tasi deyarli bir xil, 1 tasi aniq noto'g'ri. Talaba "matn uzunligi" bo'yicha taxmin qilib qo'yadi.

**Talab:**
- 1 ta to'g'ri variant;
- 2 ta "deyarli to'g'ri" xato: noto'g'ri modda, noto'g'ri muddat yoki noto'g'ri tartib;
- 1 ta etik yoki protsessual qo'pol xato;
- uzunliklar ±20% oralig'ida bo'lsin;
- tartibi aralashtirilgan bo'lsin;
- har bir variantga `tone` (`good|bad|info`) va `article` maydonlari qo'shilsin.

### 🟠 B4. STT sekin
5 s audio 37 s da tanilmoqda (resurs talashuvi paytida).
**Qabul mezoni:** 5 s audio ≤ 3 s da tanilsin.
- Agar CPU yetmasa: `whisper small` yoki `distil` + `int8`.
- Tanish oynasini 15 s bilan cheklash.
- Javobda albatta `confidence` bo'lsin. Biz past ishonchda talabadan qayta aytishni so'raymiz.

### 🟡 B5. Kalitli API bo'yicha kichik talablar
- 401 va 403 javoblari tez qaytsin (< 50 ms) va body'da `{error:{code,message}}` bo'lsin.
- `/store/cases` hajm limitini ayting (biz 256 KB gacha bo'lishini kutamiz).
- `/xapi/statements` → `200 {stored: n}`.
- `X-LexSim-Owner` bo'yicha rate-limit qo'ying, IP bo'yicha emas: barcha talabalar bitta Next.js serveri orqali keladi.

### 🟡 B6. Ovoz va vizemalar
Azure o'zbek tili uchun vizema bermaydi. Hozir biz og'iz harakatini ovoz balandligidan (RMS) hisoblaymiz.
**Agar imkon bo'lsa:** `/voice/tts` javobiga `X-Duration-Ms` header'i va, ixtiyoriy ravishda, so'z vaqtlari qo'shilsin: `X-Word-Timings: [[startMs,endMs],…]` yoki alohida JSON. Bu lab sinxronini sezilarli yaxshilaydi.

---

## 5. Huquqiy qoida (o'zgarmaydi)

- **"Manba bo'lmasa, modda yo'q".** LLM moddani faqat lex.uz'dan olingan tasdiqlangan paketdan keltira oladi: FPK, JPK, IPK.
- Paketda yo'q modda raqamini keltirish taqiqlanadi. Bunday javob `articles: []` bilan qaytsin.
- Tashkilot va ismlar to'qima bo'lsin ("Namuna …"). Haqiqiy sud, organ yoki shaxs nomidan hujjat yaratilmaydi.
- Imlo bo'yicha: `oʻ`, `gʻ` — U+02BB; tutuq belgisi — U+02BC; "Oʻzbekiston Respublikasi".

---

## 6. Keyingi qadam (bizdan)

1. Kalit `.env.local`ga qo'yilgach, kalitli yo'llarni jonli tekshiramiz: NLU, saqlash va tiklash (server restartidan keyin), xAPI, barcha xonalarda server ovozi. Natijani sizga yuboramiz.
2. B1 tayyor bo'lgach, frontend `features` massivini o'qib, imkoniyatlarni avtomatik yoqadi.
3. B2 bo'yicha streaming (SSE) qo'shsangiz, frontend tomonini 1 kunda ulaymiz.

**Xavfsizlik eslatmasi:** kalitni hech qachon chat yoki hujjatga yozmang. SSH parolini almashtiring: oldingi parol chatda ochiq yozilgan edi.

---

### Ilovalar
- `contracts.schema.json` — API shartnomalari, JSON Schema.
- `lines.json` — `/voice/prerender` uchun 97 ta gap.
