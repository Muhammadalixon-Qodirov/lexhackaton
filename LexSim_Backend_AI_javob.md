# LexSim_Backend_AI_Toliq_Topshiriq.md ga javob — backend v1.3

**Kimga:** frontend jamoasi.
**Sana:** 2026-11-21.
**Server:** `http://192.168.88.110:8100/api/v1`.
**Qisqacha:** backend'ning o'z doirasidagi ishlar bajarildi:
- `/nlu/match`;
- `X-LexSim-Key` va oldindan render;
- darajalar;
- `case_state`, xAPI va o'qituvchi API;
- `/metrics`, zaxira, unit testlar.

**LLM tezligi (§3) hali hal qilinmagan.** U butun serverga tegishli qarorlarni talab qiladi, ular server egasida (3-bo'lim).

---

## 1. Bajarildi

### D3 — `/nlu/match` (§4) ✅

- **Kontrakt §4.1 dagidek:** `match`, `alternatives`, `quality` (`address`, `factsCited`/`factsMissing`, `articles[].valid`, `ethics`, `politeness`), `clarify`, `ms`. Qo'shimcha maydonlar: `engine` (`reranker` | `lexical`), `reason` (`ambiguous`, `low_score`, `low_stt`, `no_match`, `ethics`) va `thresholds`.
- **Qanday ishlaydi:** faqat GPU reranker (`bge-reranker-v2-m3`) va qoidalar, LLM ishlatilmaydi. Har bir nomzodning `text` va `examples` matnlari bitta so'rovda baholanadi.
- **Tezlik:** 136–336 ms (talab p95 ≤ 800 ms).
- **Xavfsizlik qoidasi.** Eng yuqori ikki nomzod bir-biriga yaqin bo'lsa va biri `good`, ikkinchisi `bad` bo'lsa, taxmin qilinmaydi: `clarify` qaytadi. `bad` niyatni `good` deb tasniflash eng xavfli xato, shuning uchun shunday qilingan.
- **Faktlar.** `rubric.mustCiteFacts` faqat ID'lar ro'yxati. Tekshirish uchun **`rubric.facts`** ham yuboring:
  - `{"sick": "Daʼvogar kasal boʻlgan, varaqasi bor"}` — reranker ma'no bo'yicha tekshiradi;
  - yoki `{"notified": ["xabardor", "ogohlantir"]}` — kalit so'zlar bo'yicha.
- **STT ishonchi past bo'lsa** (`stt.confidence < 0.6`): `match: null`, `reason: "low_stt"`, `clarify: "Iltimos, fikringizni aniqroq takrorlang."`.
- **Reranker o'chiq bo'lsa** leksik moslikka o'tadi (`engine: "lexical"`). U sekinroq (~2 s) va ehtiyotkor: shubhali holda `clarify` qaytaradi.
- **Ostonalar** reranker shkalasida: `match ≥ 0.6`, `clarify ≥ 0.25`. Sizning 0,75/0,5 qiymatlaringiz cosine shkalasi uchun. **Kalibrlash to'plami** (`eval/nlu_<case>.jsonl`, §4.3) mentor tayyorlagach, ostonalarni o'sha bo'yicha sozlayman va top-1 / `bad`→`good` hisobotini beraman.

**Sinov (2026-11-21, reranker bilan):**

| Talaba gapi | Natija |
|---|---|
| «hurmatli sud men mijozim kasal bo'lganini va varaqasi borligini aytmoqchiman» (ovoz, 0,82) | `explain` 0,98, `factsCited: [sick]`, `factsMissing: [notified]` |
| «Hurmatli sud, arizada hammasi bor…» | `thin` (`bad`) 0,999 |
| «bugun havo yaxshi» | `match: null`, `no_match` |
| «…tanishim bor, pora beraman» | `ethics: "violation"` |

### D4 — server-to-server kalit va oldindan render (§5.1, §5.2) ✅

- **Kalit.** Har bir so'rovga `X-LexSim-Key: <kalit>` va `X-LexSim-Owner: <studentHash>` sarlavhalari qo'shiladi.
  - Kalit serverda: `cat ~/lexsim/backend/.lexsim_key`. Server egasidan oling va faqat Next serverida saqlang.
  - Kalit bilan `/voice/tts` va `/voice/stt` cookie'siz ishlaydi.
  - Limitlar `X-LexSim-Owner` bo'yicha hisoblanadi: TTS 300/daq, STT 120/daq.
- **Oldindan render:**
  - `POST /voice/prerender {items: [{text, voice}], engine?}` → `202 {jobId}`. Bitta so'rovda 1000 tagacha gap.
  - `GET /voice/prerender/{jobId}` → `{done, total, failed[], finished}`.
  - Keyin `/voice/tts` keshdan **~5 ms** da qaytadi (o'lchandi).
- **~300 gaplik ro'yxat** (`tools/voice/lines.mjs`) tayyor bo'lsa, render qilib beraman.
- **Haqiqiy ayol ovozi (§5.3).** Chatterbox GPU orqali bo'ladi:
  - backend tayyor;
  - serverdagi tunnel ruxsati qo'shildi;
  - GPU kompyuter tomoni qoldi: [Chatterbox_Serverga_Ulash.md](Chatterbox_Serverga_Ulash.md).

  Ulangach, oldindan render shu ovozda qilinadi.

### D5 — darajalar (§2) ✅ (iqtisodiy sud sessiyalari uchun)

- **Yaratish:** `POST /sessions {scenarioId, mode, level}`. `level` sukut bo'yicha `beginner`.
- **Snapshot maydonlari:** `level`, `inputModes`, `options`, `optionsRevealed`, `silenceSec`, `hintsAllowed`, `feedback`.

| | beginner | intermediate | advanced |
|---|---|---|---|
| `options` | har bosqichda 4 ta: 3 foydali + 1 ishonarli xato, tartibi `seed` bo'yicha aralashtirilgan | `[]`. `interactions {action:"reveal-options"}` → ochiladi, **−10**, bosqich uchun bir marta | `[]`. `optionId` → `422 options_disabled` |
| `inputModes` | option, text, voice | text, voice (+option ochilgach) | voice, text |
| Maslahat | −5 | −5 | `409 hints_disabled` |
| `feedback` | har javobdan keyin `{tone, message, article}` | faqat jiddiy xatoda | `null`, faqat hisobotda |
| Jimlik | — | `interactions {action:"silence"}` → sudya eslatadi | sudya «javob bering» deydi, `communication` dan ball tushadi |
| Sudya | murojaat ogohlantirishi bir marta | bir marta | har safar |
| Raqib (LLM) | yumshoq, namunaga yaqin | standart | qattiq: eng zaif joyga e'tiroz |

- **Variant qiymati oshkor qilinmaydi.** Klientga faqat `{id, text, kind}` boradi. Unit test buni tekshiradi.
  - Xato variant tanlansa: lahza darajasi cheklanadi, `decisions` ga sabab yoziladi, `feedback` beriladi.
  - Variantlar [backend/options.json](backend/options.json) da, mentor tahrirlaydi.
- **Turn:** `{optionId? | text?, inputMode, stt?: {confidence, durationMs}}`.
  - `inputMode` har bir user turnda va `decisions[].inputMode` da saqlanadi. Hisobotda: `report.inputModes: {option, text, voice}`.
  - Ovoz bilan `confidence < 0.6` bo'lsa: sudya «Iltimos, fikringizni aniqroq takrorlang» deydi, ball ayirilmaydi, bosqich o'zgarmaydi.
  - Og'zaki nutqda «Hurmatli sud» tekshiruvi yumshoqroq: gapning boshida «hurmat…», «sud» yoki «muhtaram» bo'lsa yetadi.
- **Jimlik vaqtini klient o'lchaydi.** Server vaqtni bilmaydi, shuning uchun `silenceSec` o'tganda `action:"silence"` yuboring.
- **"Ish yo'li" (`/cases`) uchun darajalar** P2 bilan birga keladi, chunki dvigatel hozir sizda. `/nlu/match` ni o'z dvigatelingizda shu qoidalar bilan ishlatishingiz mumkin.

### D7 — saqlash, xAPI, o'qituvchi (§7.1, §7.2) ✅

**Ish holati (`case_state`).** `X-LexSim-Key` bilan, SQLite'da, kunlik zaxira bilan:

```
PUT /api/v1/store/cases/{id}  {owner, kind, state, version}
  → 200 {id, version: n+1}
  → 409 version_conflict {version: <joriy>}   — boshqa joyda o'zgargan
  → 403                                         — boshqa owner
GET /api/v1/store/cases/{id}  → {id, owner, kind, state, version, updatedAt} | 404
```

- Yangi ish uchun `version: 0` yuboring. Holat hajmi 512 KB gacha.

**xAPI va o'qituvchi:**

```
POST /api/v1/xapi/statements            {statements: [...]} yoki massiv, 200 tagacha       (X-LexSim-Key)
GET  /api/v1/teacher/cohorts/{id}/summary   → har talaba: cases, avgScore, errors, hints, timeSec
GET  /api/v1/teacher/cohorts/{id}/hotspots  → eng ko'p xato qilingan lahzalar, moddalari bilan
```

- **Statement shakli:**
  - `actor.account.name = studentHash`. Ism yoki `mbox` bo'lsa → 422: maxfiylik uchun shaxsiy ma'lumot serverga tushmaydi;
  - guruh: `context.extensions["…/cohort"]`;
  - xato: `result.success:false` yoki `result.extensions["…/tone"]:"bad"`;
  - modda: `…/article`;
  - maslahat: `verb …/hinted` yoki `…/hint`;
  - vaqt: `result.duration` (ISO 8601).
- **O'qituvchi endpointlari** hozircha `X-LexSim-Key` yoki admin token bilan. O'qituvchi login P2'da.

### D8 — qisman ✅

- **Testlar:** 12 ta unit test (`backend/tests/test_core.py`), hammasi yashil. Ular qamrab oladi:
  - imlo, `llm_check`;
  - NLU: moslik, noaniqlik, STT, etika, leksik zaxira;
  - `case_state` versiyalari, xAPI va o'qituvchi;
  - variantlar to'plami va maxfiyligi.

  Integratsiya sinovi `tools/backend_sinov.py` ham qayta o'tkazildi.
- **`/metrics`** (Prometheus): har bir qism uchun p50/p95/avg/max (LLM, RAG, rerank, TTS, STT, dvigatel, saqlash), hodisalar hisoblagichi, navbat, xizmatlar holati, CPU. Kirish faqat lokal yoki token bilan.
- **Zaxira:** `sessions.db` (sessiyalar, `case_state`, xAPI) kuniga bir marta `backend/backups/` ga nusxalanadi, 14 kun saqlanadi.
- **Kontent kod tashqarisiga chiqarildi:** LLM tekshiruvidagi ruxsat etilgan raqamlar endi `scenarios.json → numbers` da. Variantlar `options.json`, ma'no namunalari `semantic.json`, rollar `roles.json` da.
- **Yangi kod alohida modullarda:** `nlu.py`, `store.py`, `voice.py`, `monitor.py`.

### D6 — gibrid: tayyor javoblar + LLM (§3.4) ✅ (qo'shimcha, 2026-11-21)

LLM tezligi hal bo'lguncha raqib **oldindan tayyorlangan javoblar bankidan** gapiradi ([backend/replies.json](backend/replies.json)):
- **Bank:** 5 ta raqib lahzasi, 25 ta variant. Har bir variant talabaning muayyan dalilliga javob beradi: dalolatnoma yo'q, FK 541, "fakturalar soxta", moliyaviy ahvol, "penyani bekor qiling" va hokazo.
- **Tanlov:** talaba gapi variantlarning namunalari bilan GPU reranker orqali solishtiriladi. Moslik ≥ 0,5 bo'lsa shu javob aytiladi, bo'lmasa umumiy javob.
- **Bir sessiyada** bitta variant ikki marta aytilmaydi.
- **LLM** faqat `advanced` darajada va mos variant topilmaganda chaqiriladi, o'shanda `202` va async. Boshqa darajalarda LLM chaqirilmaydi.
- **Natija:** to'liq sud majlisi (ikkala rol) **har bir javob ≤ 4,6 s** bilan o'tdi, ko'pi 0–1,5 s. Oldin raqib javobi 60–110 s edi. `engine: "scripted"`.
- **Tekshiruv:** barcha bank matnlari `llm_check` dan o'tadi. Unit test bitta noto'g'ri iborani topdi, u tuzatildi.

**Chatterbox GPU** ulandi (`127.0.0.1:8092`). GPU kompyuter egasi tunnel, avtostart va uyquni sozladi, ochiq havolani yopdi.
- Jonli yangi gap: ~10 s. Shuning uchun jonli TTS **MMS** da qoladi.
- **Qat'iy gaplar** (sudya, kotib, raqib banki — 61 ta) Chatterbox GPU'da **oldindan render** qilinmoqda. `/voice/tts` ular uchun avtomatik Chatterbox versiyasini beradi, keshdan.
- Rollar uchun ovozlar hali klonlanmagan: namunalar va rozilik kerak. Hozircha "Standart ovoz" + balandlik filtri ishlatiladi. Klonlangach qayta render qilinadi.

---

## 2. Hali qilinmagan (backend doirasida)

| Ish | Holat |
|---|---|
| FastAPI'ga o'tish va to'liq modullarga bo'lish (§6.1–6.2) | Kontrakt o'zgarmasdan, bosqichma-bosqich. Avval LLM masalasi hal bo'lsin, chunki SSE uchun ham kerak |
| JSON Schema bo'yicha CI (§6.4) | Sizdan `contracts.schema.json` kutyapman |
| Yuklama testi, 30 talaba (§6.5, §11) | LLM runtime aniq bo'lgach. Hozirgi LLM bilan ma'nosi yo'q |
| `/cases` dvigateli backend'da (P2) | Keyingi bosqich |
| LLM-hakam (§4.4) | LLM tezlashgach |

---

## 3. LLM tezligi (§3, D1/D2/D6) — server egasining qarori kerak

**Tekshirilgan faktlar (faqat o'qish):**
- **Model:** `qwen3_5_moe_text`. Gibrid: `linear_attention` + `full_attention`, 256 ekspert, har tokenda 8 tasi faol, diskda 22 GB.
- **CPU:** 2 × Xeon E5-2690 v4 (Broadwell), 28 fizik yadro, 2 ta NUMA tugun. **Faqat AVX2**: AVX-512 va AMX yo'q.
  - `llama.cpp` bu CPU'da ishlaydi, lekin sizning 15 token/s va 1,5 s TTFT taxminlaringiz AVX-512'li zamonaviy CPU uchun.
  - Bu CPU'da A3B-sinf model Q4 bilan taxminan 8–15 token/s kutiladi. TTFT ~400 tokenli promptda prompt-kesh bilan 1–3 s, keshsiz 5–10 s. Haqiqiy qiymatni faqat benchmark ko'rsatadi.
- **Bo'sh paytdagi yuklanish 24–27.** Sizning auditingiz tasdiqlandi: LLM bo'sh turganda ham ~22 yadroni band qiladi.

**Bunga bog'liq ikkita muammo topib, tuzatdim:**
- `lexsim-rag` dublikat xizmati 178 marta yiqilib, qayta yonib, CPU yegan edi — o'chirildi.
- Chatterbox ishlamay qolganda backend endi avtomatik MMS'ga o'tadi.

**Nega bajarilmadi:** `llama.cpp` ni yig'ish va 18 GB GGUF model yuklab olishni boshlamoqchi bo'ldim. Bu umumiy serverda yangi dastur o'rnatish bo'lgani uchun avtomatik ruxsat tizimi to'xtatdi. Bunday ish server egasining aniq roziligi bilan qilinishi kerak. Quyidagilarning hammasi ham server egasining qarori:
1. `security-agent` va `ai_demo` ni ko'chirish yoki CPU kvotasi bilan cheklash (§3.1, §8.2).
2. `colibri` ni to'xtatish yoki u bilan yonma-yon `llama-server` ni ishga tushirish. LLM porti `0.0.0.0:8000` dan `127.0.0.1` ga o'tsa, LAN'dagi boshqa mijozlar uziladi (§8.3).
3. LexSim uchun alohida yadrolar (`CPUAffinity`), `mlock`, `vm.swappiness`.

**Server egasi rozi bo'lsa, taklif qilinadigan reja:**
1. `~/llm/` ga `llama.cpp` ni `GGML_NATIVE`, AVX2 bilan yig'ish.
2. Qwen3.6 (`qwen3_5_moe`) qo'llanishini tekshirish. Qo'llanmasa, Qwen3-30B-A3B-Instruct-2507 Q4_K_M GGUF olinadi.
3. `127.0.0.1:8001` da `llama-server` ishga tushiriladi: `colibri` ga tegmasdan, bitta NUMA tuguniga bog'langan holda.
4. §11 benchmark: `colibri` va `llama.cpp` yonma-yon, boshqa ishlar ishlayotgan va to'xtatilgan holatda.
5. Natija yaxshi bo'lsa:
   - backend 8001 ga o'tadi;
   - SSE `/stream` va jumla-jumla TTS qo'shiladi;
   - gibrid tayyor variantlar qo'shiladi (§3.4). Ular uchun NLU allaqachon tayyor.

---

## 4. §10 savollariga javob

1. **`security-agent` va `ai_demo`** — qaror server egasida (3-bo'lim). Ular LexSim bilan bitta CPU va LLM navbatini bo'lishyapti, bu ham tasdiqlandi.
2. **`llama.cpp` + Qwen3.6:**
   - Model `qwen3_5_moe_text`, gibrid. Qo'llanishi `llama.cpp` ning joriy versiyasida tekshirilishi kerak.
   - Zaxira: Qwen3-30B-A3B-Instruct-2507.
   - O'zbekcha baholash to'plami (§3.5) hali yo'q, benchmark bilan birga tuziladi.
3. **Ayol ovozi:** fine-tune uchun yozuv yo'q. Reja — Chatterbox GPU bilan oldindan render: backend tayyor, GPU kompyuter tomoni qoldi. Rollar uchun 5–10 s namunalar va ovoz egalarining roziligi kerak.
4. **Kotib STT WER:** o'lchanmagan. 4,8 s sinov gapida 1 ta so'z xato bo'ldi (penya → «pingyani»). Tuzatish lug'ati qo'shildi. WER uchun 50–100 ta yozib olingan huquqiy gap kerak.
   - Kotib `confidence` qaytarmaydi. Shuning uchun `stt.confidence` ni hozircha klient beradi. Masalan, brauzer Web Speech bo'lsa uning bahosi, bo'lmasa maydon yuborilmaydi.
   - Tezlik 5 s audio uchun 37 s. Sabab — LLM bilan CPU raqobati: LLM'siz 18 s edi.
5. **`case_state`:** ✅ hozir ochiq (1-bo'lim, D7). Postgres o'rniga SQLite'da, chunki RAG Postgres'i boshqa xizmatga tegishli. Kunlik zaxira bor. Interfeys bir xil, kerak bo'lsa keyin Postgres'ga ko'chiriladi.

---

## 5. Xavfsizlik (§8)

| Talab | Holat |
|---|---|
| SSH paroli — almashtirish, faqat kalit bilan kirish | ❗ **Server egasi qilishi kerak.** Bu sessiyada bir necha marta eslatildi |
| LLM porti faqat lokal | Server egasi qarori (3-bo'lim, 2-band) |
| `/monitor` — token bilan | ✅ admin token, `.admin_token` (600). Panel LAN'dan ochiladi, tokensiz ma'lumot bermaydi |
| `/metrics`, `/store`, `/xapi`, `/nlu`, `/teacher` | ✅ faqat kalit yoki token bilan (`/metrics` lokal ham ochiq) |
| Zaxira | ✅ kunlik, 14 kun. Tiklash sinovi: `sqlite3 backups/sessions-YYYYMMDD.db ".tables"` |
| Talaba ovozi | ✅ diskda qolmaydi. xAPI'da ism yoki email qabul qilinmaydi |
