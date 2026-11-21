# LexSim_Frontend_v3_Javob.md ga javob — backend v1.3.1

**Kimga:** frontend jamoasi.
**Sana:** 2026-11-21.
**Server:** `http://192.168.88.110:8100/api/v1`. `GET /health` → `"version": "1.3.1"`.

| | Holat |
|---|---|
| B1 `/health` versiya + `features` | ✅ |
| B2 LLM tezligi | ✅ tayyor javoblar banki bilan hal qilindi (beginner va intermediate'da LLM yo'q) |
| B3 variantlar | ✅ qayta yozildi: 1 to'g'ri, 2 deyarli to'g'ri, 1 qo'pol xato. `tone`/`article` — tanlangandan keyin (izohga qarang) |
| B4 STT | 🟡 qisman: 15 s oyna, `confidence: null`. ≤ 3 s faqat GPU STT bilan |
| B5 kalitli API | ✅ |
| B6 `X-Duration-Ms`, so'z vaqtlari | ✅ (so'z vaqtlari taxminiy) |
| Ilovalar (`contracts.schema.json`, `lines.json`) | ❗ bizga yetib kelmadi. Faqat hujjatning o'zi keldi, iltimos qayta yuboring |

---

## B1. `/health`

```json
{"ok": true, "protocol": 1, "version": "1.3.1",
 "features": ["levels", "reveal-options", "silence", "nlu", "store", "xapi", "prerender",
              "reply-bank", "voice-key", "tts-duration"], "queue_depth": 0, ...}
```

## B2. Tezlik — raqibning tayyor javoblar banki

- **Raqib endi LLM'ni kutmaydi.** U [backend/replies.json](backend/replies.json) bankidan gapiradi: 5 ta lahza, 25 ta variant. Har bir variant talabaning muayyan dalilliga javob beradi.
- **Tanlov:** GPU reranker talaba gapiga eng mos variantni tanlaydi. Topilmasa, umumiy javob aytiladi.
- **O'lchov:** to'liq sud majlisi, ikkala rol bo'yicha. **Har bir `turn` ≤ 4,6 s, odatda 0–1,5 s.** Sizning mezoningiz p50 ≤ 8 s, p95 ≤ 20 s edi.
- **LLM** faqat `advanced` darajada va mos variant topilmaganda chaqiriladi, o'shanda `202` va async. Sizning 4-variantingiz shu.
- **`/nlu/match` p95:** 136–336 ms (mezon ≤ 400 ms).
- **SSE:** hozir shart emas, chunki LLM kamdan-kam ishlaydi. Polling yetadi. LLM runtime tezlashtirilganda (server egasining qarori) SSE qo'shiladi.

## B3. Variantlar

- **Tarkib** ([backend/options.json](backend/options.json)), har bir bosqichda (13 ta to'plam):
  - **1 ta to'g'ri**;
  - **2 ta deyarli to'g'ri**: noto'g'ri modda (masalan, FK 544 o'rniga FK 333), noto'g'ri tartib (rad qilish ish oxirida, penya iltimosnomasi dalillardan oldin) yoki talabdan voz kechish ("faqat bir oy uchun qarz");
  - **1 ta qo'pol xato**: pora va'dasi, "sudya bilan oldindan gaplashganmiz", o'zboshimchalik tahdidi, noqonuniy dalil, raqibni zaldan chiqarish talabi.
- **Uzunliklar:** bosqich ichida ±20%. To'g'ri variant eng uzuni emas: u bosqichga qarab 1-, 2-, 3- yoki 4-o'rinda turadi. Buni unit test tekshiradi.
- **Tartib** `seed` bo'yicha aralashtiriladi.
- **`tone` va `article` — tanlangandan keyin.** Siz ularni har bir variantga qo'shishni so'radingiz. Lekin `COURT_BACKEND.md` §1.3 da "variantlarning qiymati hech qachon oshkor qilinmaydi" qoidasi bor: `tone` klientga oldindan borsa, to'g'ri javob DevTools'da ko'rinib qoladi. Shuning uchun:
  - `snapshot.options[]` → faqat `{id, text, kind}`;
  - tanlangandan keyin `snapshot.feedback` → `{tone, message, article, optionId}`, bunda `message` — mentor yozgan aniq sabab;
  - hisobotda `decisions[]` → `optionId`, `optionTone`, `why`, `article` va `better` (shu bosqichning to'g'ri varianti).

  Agar sizga `tone` boshqa sabab bilan oldindan kerak bo'lsa (masalan, mentor rejimi), yozing — alohida bayroq bilan qo'shamiz.
- **Ball:** qo'pol xato variantlari dvigatelda qoidabuzarlik sifatida qayd etiladi. Pora → `zeroedByEthics`, noqonuniy dalil va tahdid → `ethics` ballidan tushadi.

**Sinov:**

| Variant | `feedback` |
|---|---|
| `v-1` | `{tone: "good", message: "Toʻgʻri tanlov.", article: "IPK 62-modda"}` |
| `r-3` | `{tone: "bad", message: "Rad qilish ishni mazmunan koʻrish boshlangunga qadar bildiriladi, oxirida emas.", article: "IPK 22-modda"}` |

## B4. STT

- ✅ **Tanish oynasi 15 s:** ortig'i kesiladi.
- ✅ **Javobda `confidence: null`.** Kotib modeli ishonch bahosini bermaydi. `null` bo'lsa, o'z tekshiruvingizni qo'llang.
- ❌ **"5 s audio ≤ 3 s" serverning CPU'sida bajarilmaydi.**
  - Kotib 5 s audioni 18 s da taniydi. LLM bilan CPU talashganda 37 s.
  - Yangi model (`faster-whisper small int8`) o'rnatish uchun server egasining ruxsati kerak. Uning ham CPU'da tezligi ~4–6 s bo'ladi.
- **Haqiqiy yechim — GPU kompyuterdagi STT.** U yerda STT modeli allaqachon ishlaydi (GPU xotirasidagi 6,8/8 GB ning bir qismi). Uni reranker va Chatterbox kabi tunnel orqali serverga ochish kerak, masalan `127.0.0.1:8093`. Shunda 5 s audio ~1 s da tanilishi kutiladi va whisper `confidence` ham beradi.
  - Buni GPU kompyuter egasi bilan kelishamiz. Backend tomoni bir kunlik ish.

## B5. Kalitli API

- **401/403** body bilan `{error:{code,message}}`, ~50 ms (o'lchandi: 53 ms).
- **`/store/cases` hajm limiti: 512 KB.** Siz 256 KB kutgansiz, ya'ni zaxira bor. Undan oshsa → `413 payload_too_large`.
- **`/xapi/statements`** → `200 {"stored": n, "ids": [...]}`. `id` bo'yicha idempotent: takror yuborilgan statement qayta yozilmaydi, `stored: 0`.
- **Rate limit** `X-LexSim-Owner` bo'yicha, IP bo'yicha emas: NLU 600/daq, store 600/daq, TTS 300/daq, STT 120/daq.
- **`X-LexSim-Owner`** `[A-Za-z0-9_-]{8,64}` bo'lishi kerak. Ism kabi qiymat → `422`. Sarlavha logga yozilmaydi: logda faqat yo'l va status qoladi.

## B6. Ovoz va vizemalar

`POST /voice/tts` javobida:

```
X-Duration-Ms: 3216                       # MP3 kadrlaridan aniq hisoblanadi (ffprobe bilan bir xil)
X-Word-Timings: [[161,441],[465,1026],…]  # har so'z [startMs, endMs]
X-Word-Timings-Source: estimate           # taxminiy: davomiylik harf soniga mutanosib
```

MMS va Chatterbox so'z chegarasini bermaydi, shuning uchun so'z vaqtlari taxminiy. RMS bilan birga ishlating.

## Ovoz ro'yxati (`lines.json`) va kesh

- **Fayl kelmadi.** Ikki yo'l:
  - (a) faylni yuboring, men render qilaman;
  - (b) kalit `.env.local` ga qo'yilgach, o'zingiz `POST /voice/prerender {items: lines, engine: "chatterbox_gpu"}` yuboring, keyin `GET /voice/prerender/{jobId}` bilan holatini kuzating. 97 ta gap Chatterbox GPU'da ~15 daqiqa oladi.
- **Kesh** shu matn va shu `voice` bilan kelgan so'rovga keshdan **~5–60 ms** da javob beradi.
  - Ichki kesh kaliti boshqacha hisoblanadi, lekin bir xil `{text, voice}` har doim bir xil kalitni beradi.
  - Siz yuborgan `ʻ`/`ʼ` matnda o'zgarmaydi. Faqat MMS modeliga uzatishda `'` ga keltiriladi, chunki uning lotin→kirill o'girgichi shuni kutadi.
- **Allaqachon render qilingan:** sud zalining 61 ta qat'iy gapi (sudya, kotib, raqib banki), Chatterbox GPU ovozida.
- **Rollar uchun haqiqiy ovozlar** hali klonlanmagan: namunalar va rozilik kerak. Hozircha bitta standart ovoz va balandlik filtri ishlatiladi.

## Testlar

- **Unit:** 14 ta yashil. Ular qamrab oladi: imlo, `llm_check`, NLU, `case_state`, xAPI va idempotentligi, variantlar (1+3, uzunlik ±20%, `tone` oshkor emas), so'z vaqtlari, raqib banki matnlari.
- **Integratsiya:** `tools/backend_sinov.py` ikkala rol bo'yicha o'tdi: kontrakt, 403, idempotentlik, sequence, imlo, manbalar.
- **`contracts.schema.json`** kelgach, CI'da javoblarni shu sxemaga qarshi tekshirish qo'shiladi.
