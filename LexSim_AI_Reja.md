# LexSim — AI reja: nima RAG, nima fine-tune, qaysi ma'lumot va qaysi model

**Mas'ul:** AI va backend dasturchi.
**Asos:** [LexSim_Backend_Spec.md](LexSim_Backend_Spec.md) (kontrakt), mentor sxemasi (protsessual kodekslar va manbalar), xalqaro tadqiqot — [reports/Xalqaro AI sud simulyatorlari.md](reports/Xalqaro%20AI%20sud%20simulyatorlari.md).
**Ustuvorlik:** **P0** — hakaton; **P1** — pilot; **P2** — keyinroq.

---

## 0. Qisqa javoblar

| Savol | Javob |
|---|---|
| Nimani RAG qilaman? | Lex.uz'dan **tanlangan** qonunlar: tanlangan ish turining protsessual kodeksi, FK'ning kerakli boblari, Plenum qarorlari (P0). Sud qarorlari (public.sud.uz) — P1. Lex.uz'ning hammasini birdaniga emas. |
| Nimani fine-tune qilaman? | Hakatonda — **hech narsani**. Keyinroq navbat bilan: 1) talaba harakatini aniqlovchi kichik model, 2) qarordan keys ajratuvchi, 3) sud uslubidagi matn, 4) eng oxirida rol agentlari. |
| Qaysi ma'lumotlarni ishlataman? | Lex.uz kodekslari va Plenum qarorlari; public.sud.uz qarorlari; mentor yozgan bosqichlar jadvali va ssenariylar; AI yaratib mentor tuzatgan namunaviy majlislar; belgilangan talaba replikalari. |
| Qaysi modellar kerak? | **Matn** — asosiy, API orqali kuchli model. **Embedding va reranker** — RAG uchun, serverda. **Vision** — faqat ma'lumot tayyorlashda (skrinshotdan matn olish), ishlash paytida kerak emas. **Audio** — ixtiyoriy ovozli rejim (P1/P2). |

---

## 1. Nima qayerda turadi

Eng muhim qaror shu jadvalda. Har bir bilim yoki vazifa o'ziga mos joyda turishi kerak.

| Bilim yoki vazifa | Qayerda | Nega |
|---|---|---|
| Qonun moddalari (protsessual va moddiy) | **RAG** | Qonun o'zgaradi; har gapda manba (modda ID) kerak |
| Plenum qarorlari | **RAG** | Sudlar normani qanday qo'llashi — ajrim va baholashning asosi |
| Sud amaliyoti (public.sud.uz qarorlari) | **RAG (P1)** va ssenariy manbai | O'xshash ishlar, "haqiqiy sud qanday hal qilgan" |
| Majlis bosqichlari, navbat, ruxsat etilgan harakatlar | **Kod (holatlar mashinasi)** | Tartib hech qachon buzilmasligi kerak |
| Kim nimani biladi (rollar chegarasi) | **Kod (kontekst yig'ish)** | Masalan, raqib talabaning eslatmalarini ko'rmaydi |
| Keys faktlari, dalillar, yashirin ma'lumot | **Ssenariy fayli** (to'g'ridan-to'g'ri kontekstga) | Bitta ish uchun kichik va aniq; qidirish shart emas |
| Muhim lahzalardagi to'g'ri ajrim | **Ssenariy skripti (mentor yozadi)** | To'g'rilik kafolatlanadi |
| Sud tili, rollar xulqi | **Prompt va 3–5 misol** (keyinroq fine-tune) | Uslub masalasi |
| Talaba gapining turi (iltimosnoma, e'tiroz...) | **AI, JSON chiqish** (keyinroq fine-tune qilingan kichik model) | Tor vazifa |
| Ball | **Kod (formula)** va AI mezon darajalari | Tekshiriladigan va barqaror bo'lishi kerak |

**Talabaning har bir gapi qanday ishlanadi:**

```
Talaba gapi
 1. Normallashtirish: apostroflar, kirill → lotin            KOD
 2. Harakat turi: iltimosnoma / e'tiroz / dalil / savol ...   AI → JSON
 3. Tartib: hozirgi bosqichda ruxsat bormi, navbat kimda?      KOD (holatlar mashinasi)
 4. Qonun: ish turi bo'yicha filtr, tegishli moddalar          RAG
 5. Ajrim (kerak bo'lsa): qaror va asos (norm_id)              AI → JSON, keyin KOD tekshiradi
 6. Nutq: sudya, raqib yoki guvoh gapiradi                     AI → {text, gesture}
 7. Log: teglar, ochilgan ma'lumot, manbalar                   KOD
```

---

## 2. RAG: aniq nimani qo'shish

### 2.1 Qatlamlar

| Qatlam | Manba | Tarkibi | Ustuvorlik | Kim ishlatadi |
|---|---|---|---|---|
| A. Protsessual kodeks | Lex.uz | Tanlangan ish turi kodeksi: IPK yoki FPK. Keyinroq MJtK, MSIYuK, JPK | P0 | Sudya agenti (ajrim asosi), baholovchi; mentor bosqichlar jadvalini shundan yozadi |
| B. Moddiy huquq | Lex.uz | FK'ning keysga kerakli boblari: majburiyatlar, ijara, qarz, neustoyka | P0 | Raqib, sudya, baholovchi |
| C. Plenum qarorlari | Lex.uz | Oliy sud Plenumi va amaldagi sobiq Oliy xo'jalik sudi Plenumi qarorlari (ish turiga oid) | P0 (2–5 tasi), P1 (hammasi) | Sudya, baholovchi |
| D. Sud amaliyoti | public.sud.uz | Anonimlashtirilgan qarorlar, bo'limlarga bo'lingan | P1 | Baholovchi ("haqiqiy sud"), sudya (o'xshash ish) |
| E. O'quv materiali | library.tsul.uz | Darsliklar, hujjat namunalari | P2 (ruxsat bilan) | Talabaga izoh |

P0 hajmi taxminan 200–500 bo'lak. Hakaton uchun shu yetarli.

**Birinchi ish turi:** topgan namunangiz ("sud keys" — ijara qarzi va penya) iqtisodiy sud qarori, ya'ni IPK. Mentor esa fuqarolik (FPK) ustunini batafsil chizgan. Bittasini mentor bilan tanlang — ikkalasining tuzilishi o'xshash.

### 2.2 RAG'ga qo'shilmaydigan narsalar
- **Lex.uz'ning hammasi birdaniga** (idoraviy va mahalliy hujjatlar) — shovqin ko'payadi.
- **Bekor qilingan tahrirlar** faol qidiruvga qo'shilmaydi. Ular arxivda `valid_to` sanasi bilan turadi.
- **Keys faktlari** — ular ssenariy faylida turadi.
- **Rubrika va namunaviy javob** — ular baholovchiga to'g'ridan-to'g'ri beriladi, rollarga hech qachon berilmaydi.
- **Talabalar ma'lumotlari.**

### 2.3 Bo'laklash va metadata

**Qonun moddalari:** bitta bo'lak — bitta modda. Uzun modda qismlarga bo'linadi, lekin modda sarlavhasi har bo'lakda qoladi.

| Maydon | Misol | Izoh |
|---|---|---|
| `norm_id` | `FK-326`, `IPK-118` | Iqtiboslar shu ID bilan |
| `code`, `article_no`, `part_no` | `FK`, `326`, `1` | |
| `title`, `chapter`, `section` | modda sarlavhasi, bob, bo'lim | |
| `text_cyrl` | asl matn | Lex.uz'da ko'pincha kirillda |
| `text_latn` | lotinga o'girilgan va normallashtirilgan | Qidiruv shu maydonda |
| `edition_date`, `valid_from`, `valid_to` | | Faqat amaldagi tahrir faol |
| `lex_url` | `https://lex.uz/docs/...` | Hisobotda faqat lex.uz havolasi (LexSim spetsifikatsiyasi, 4.6-bo'lim) |
| `case_types` | `["IPK", "FPK"]` | Qaysi ish turlarida qidiriladi |
| `refs` | `["IPK-72"]` | Ichki havolalar ("ushbu Kodeksning ...-moddasi") |

**Plenum qarorlari:** band (punkt) bo'yicha bo'linadi. Metadata: `plenum_id`, `punkt`, `date`, `court` (Oliy sud yoki Oliy xo'jalik sudi), `status`.

**Sud qarorlari:** quyidagi bo'limlarga bo'linadi:
- `kirish`
- `aniqladi`
- `asoslash`
- `qaror_qiladi`

Metadata: `case_no`, `court_type` (IPK, FPK...), `category` (ijara, qarz...), `outcome` (to'liq, qisman yoki rad), `norms_cited`, `date`.

### 2.4 Qidiruv zanjiri
1. **Normallashtirish:** apostroflar, kirill → lotin.
2. **Aniq raqam bo'yicha topish.** Matnda "FK 326-modda" yoki "ФКнинг 326-моддаси" bo'lsa, modda regex bilan to'g'ridan-to'g'ri olinadi. SimCourt ham shunday qiladi.
3. **Filtr:** `case_types` joriy ish turini o'z ichiga oladi va `valid_to` bo'sh.
4. **Gibrid qidiruv:** BM25/trigram va embedding birga → eng yaxshi 30–50 ta.
5. **Reranker (P1)** → eng yaxshi 5–8 ta.
6. **Havolalarni ochish:** `refs` dagi moddalar ham qo'shiladi.
7. **Modelga ID'lar bilan beriladi.** Model faqat berilgan ID'larni keltiradi, kod buni tekshiradi. Topilmasa — "mentor tekshirsin" (LexSim spetsifikatsiyasi, 4.8-bo'lim).

1–6-qadamlar uchun kechikish maqsadi: ≤ 200 ms.

### 2.5 O'zbek tiliga xos ishlov
- **Yozuv:** Lex.uz matnlari ko'pincha kirillda. Asl matn ham, lotin varianti ham saqlanadi. Qidiruv lotin variantda.
- **Qo'shimchalar:** "da'vogarning", "da'vogarga" kabi shakllarni oddiy BM25 bitta so'z deb bilmaydi. Yechim: `pg_trgm` (trigram) yoki yengil stemming. Embedding bu muammoni yumshatadi.
- **Apostroflar:** `o'`, `o‘`, `oʻ`, `o’` — hammasi bitta shaklga keltiriladi.
- **Ruscha atamalar (P1):** talaba ruscha yozsa ham topilsin. Lex.uz'dagi ruscha matnni qo'shimcha maydon sifatida indekslash mumkin.

### 2.6 Sifat o'lchovi
Mentor 50 ta savol yozadi va har biri uchun to'g'ri moddalarni belgilaydi. Shu to'plamda Recall@5 ≥ 0,9 bo'lishi kerak. Har o'zgarishdan keyin qayta o'lchanadi.

---

## 3. Ma'lumotlar

### 3.1 Ro'yxat

| # | Ma'lumot | Manba | Nima uchun | Ishlov | Ustuvorlik |
|---|---|---|---|---|---|
| 1 | Protsessual kodekslar | Lex.uz | RAG A; bosqichlar jadvali | Modda bo'yicha bo'lish | P0 |
| 2 | FK va boshqa moddiy kodekslar | Lex.uz | RAG B | Modda bo'yicha bo'lish | P0 |
| 3 | Plenum qarorlari | Lex.uz | RAG C | Band bo'yicha bo'lish | P0/P1 |
| 4 | Sud qarorlari (minglab) | public.sud.uz | Ssenariylar, RAG D, sud tili misollari, baholash etaloni, statistika | 3.2 dagi zanjir | P0: 3–5 tasi; P1: ommaviy |
| 5 | Bosqichlar jadvali | Mentor va kodeks | Holatlar mashinasi | Jadval yoki JSON | P0 |
| 6 | Ssenariy fayllari | Qarorlar asosida, mentor bilan | Sessiya konteksti | LexSim spetsifikatsiyasi 4.2-bo'limdagi shakl | P0: 1–2 ta |
| 7 | Sud tili iboralari | Qarorlar va mentor | Promptlar | Ro'yxat | P0 |
| 8 | Namunaviy majlis dialoglari | AI yaratadi, mentor tuzatadi | Promptdagi misollar, sinov | Chat formati | P0: 3–5 ta; P1: yuzlab |
| 9 | Belgilangan talaba replikalari | Jamoa va mentor | Harakat aniqlagichni sinash, keyinroq fine-tune | CSV yoki JSON | P0: 150+; P1: minglab |
| 10 | Sud o'yinlari (moot court) yozuvlari | TDYU sud o'yinlari jamoasi | Haqiqiy dialog namunalari | Ovoz → matn → anonimlashtirish | P1 (rozilik bilan) |
| 11 | Pilot dialoglari | O'z platformangiz | Eng sifatli o'quv va sinov ma'lumoti | Anonimlashtirish, rozilik | P1 |
| 12 | Darsliklar, shablonlar | library.tsul.uz | Izohlar, hujjat namunalari | Ruxsat bilan | P2 |

**Harakat teglari (9-band uchun):** LexSim spetsifikatsiyasining 4.3-bo'limidagi uslubda:
- `motion` — iltimosnoma
- `objection` — e'tiroz
- `recusal` — rad etish
- `present-evidence` — dalil taqdim etish
- `question-witness` — guvohga savol
- `statement` — bayon
- `closing-argument` — muzokaradagi nutq
- `rebuttal` — replika
- `improper-address` — sudga noto'g'ri murojaat
- `off-procedure` — bosqichdan tashqari harakat
- `injection` — rolni buzishga urinish

Ro'yxatni mentor bilan yakunlang.

### 3.2 Sud qarorlarini qayta ishlash zanjiri
1. **Yig'ish:** matn sifatida (HTML yoki PDF matni). Skrinshot bo'lsa — OCR (4.3-bo'lim).
2. **Normallashtirish:** kirill → lotin (asl matn ham saqlanadi), bo'sh joylar, apostroflar.
3. **Bo'limlarga ajratish:** "АНИҚЛАДИ" va "ҚАРОР ҚИЛАДИ" sarlavhalari bo'yicha regex.
4. **Metadata (regex bilan):**
   - ish raqami (masalan, "4-1001-2320/53831"), sud nomi, sana;
   - keltirilgan moddalar ("ФКнинг 8, 324, 326-моддалари", "ИПКнинг 118-моддаси");
   - natija ("қисман қаноатлантирилсин", "рад қилинсин").
5. **Anonimlashtirish:**
   - Tomonlar allaqachon yulduzcha bilan yopilgan, lekin sudya, kotib, vakillar va ayrim tadbirkorlarning ismi ochiq.
   - Ular rollar bilan almashtiriladi: regex (JShShIR, telefon, pasport), keyin AI o'tadi, oxirida inson tekshiradi.
6. **Saqlash:** `court_decisions` jadvali va bo'limlar bo'laklari (RAG D).
7. **Ssenariy fabrikasi (P1):** AI (Batch) qarordan keys faylini chiqaradi, mentor tasdiqlaydi.

### 3.3 Mentor yozadigan narsalar
- Tanlangan ish turi uchun majlis bosqichlari, har bosqichda kim nima qila olishi va mumkin bo'lgan ajrimlar.
- Ssenariydagi muhim lahzalar va ularning to'g'ri yechimi.
- RAG uchun 50 ta sinov savoli va to'g'ri moddalar.
- Belgilangan replikalarni tekshirish.
- Sud tili iboralari.

### 3.4 Huquqiy shartlar
- **Lex.uz va public.sud.uz:** foydalanish shartlarini tekshiring. Yuklab olishni sekinlashtiring (rate limit).
- **Shaxsiy ma'lumotlar:** "Shaxsga doir ma'lumotlar to'g'risida"gi qonunning 27-1-moddasi, 2026-yildagi o'zgartirishlar bilan.
- **library.tsul.uz:** mualliflik huquqi — faqat ruxsat bilan.
- **Pilot dialoglari:** talabalarning roziligi kerak.
- **AI provayderi:** ma'lumotlarni o'qitishga ishlatmaslik shartini tekshiring. Ssenariylar sintetik va anonim bo'lsin.

---

## 4. Modellar

### 4.1 Matn modellari (ishlash paytida)

| Vazifa | Model | Sozlama | Qayerda | Ustuvorlik |
|---|---|---|---|---|
| Rollar: sudya, raqib, guvoh (LexSim spetsifikatsiyasi, 4.5) | Claude Opus 5.5 (`claude-opus-5-5`) | effort `low`, streaming, JSON `{text, gesture}` | API | P0 |
| Sudya ajrimini tanlash | Opus 5.5 | effort `medium`, JSON (qaror va asos `norm_id`), kod tekshiradi | API | P0 |
| Talaba harakatini aniqlash (LexSim spetsifikatsiyasi, 4.3) | Opus 5.5 | effort `low`, JSON `{tags}`; zaxira — qoida asosidagi klassifikator | API va server | P0 |
| Baholovchi (LexSim spetsifikatsiyasi, 4.6) | Opus 5.5 | effort `high`, JSON, ikki marta mustaqil | API | P0 |
| Qarordan keys chiqarish, namunaviy majlis yaratish | Opus 5.5 | Batch API (arzonroq, asinxron) | API | P0 (oz), P1 (ommaviy) |
| Anonimlashtirishda ismlarni topish | Opus 5.5 va regex | Batch API | API | P1 |

Eslatmalar ([2-ai-qismi.md](2-ai-qismi.md), 4-bo'lim):
- `temperature` parametri yo'q. Barqarorlik JSON sxema, aniq ko'rsatmalar va ikki marta baholash bilan ta'minlanadi.
- O'zgarmas qism (rol, ssenariy, moddalar) keshlanadi.
- Kechikish yoki narx muammo bo'lsa, Sonnet 5.5 yoki Haiku 5.5 ni bir xil 20 ta o'zbekcha dialogda sinab ko'ring. LexSim spetsifikatsiyasining 9-bo'limidagi 2-savol aynan shu. Almashtirish — jamoa qarori.

### 4.2 Embedding va reranker (RAG uchun, serverda)

| Vazifa | Tavsiya (ochiq, lokal) | Muqobil | Izoh |
|---|---|---|---|
| Embedding | `BAAI/bge-m3` (ko'p tilli, 8192 tokengacha, protsessorda ishlaydi) | `Qwen3-Embedding-0.6B`, `intfloat/multilingual-e5-large`, yoki API orqali embedding | O'zbekchadagi sifatini 50 ta savol bilan solishtiring |
| Reranker (P1) | `BAAI/bge-reranker-v2-m3` | Qwen3-Reranker | Eng yaxshi 30 tani qayta tartiblaydi; protsessorda ham ishlaydi |
| So'z bo'yicha qidiruv | PostgreSQL FTS (`simple` sozlamasi) va `pg_trgm` | OpenSearch | Bu model emas, algoritm |

### 4.3 Vision kerakmi?
- **Ishlash paytida kerak emas.** Talaba matn yozadi, 3D sahna frontend'da.
- **Faqat ma'lumot tayyorlashda** — skrinshot yoki skan qilingan qarorlarni matnga aylantirish (OCR) uchun:
  - Tesseract (`uzb_cyrl`, `uzb`, `rus` tillari) — bepul, serverda ishlaydi.
  - Raqam va jadvallarni qayta tekshirish uchun Claude rasm o'qishi — faqat qiyin holatlarda.
- **Eng yaxshi yo'l** — saytdan matnni to'g'ridan-to'g'ri olish. Shunda vision umuman kerak bo'lmaydi. OCR summalarni buzishi mumkin, keysda esa raqam hal qiluvchi.
- **P2:** talaba yuklagan hujjat rasmini o'qish (masalan, dalil fotosurati).

### 4.4 Audio kerakmi?
- **Hakatonda shart emas** — matn rejimi yetadi.
- **Ovozli rejim (P1/P2)** sud zalida "jonli" his beradi, lekin o'zbekcha nutqni tanish (STT) va ovozlashtirish (TTS) sifati xavfli. LexSim spetsifikatsiyasining 8-bo'limidagi "Ovoz" bandi shu.

  | Vazifa | Variantlar |
  |---|---|
  | STT (nutq → matn) | Whisper — ochiq, o'zbekchani qo'llaydi, GPU'da tez. Bulut: Azure Speech yoki Google Speech-to-Text (`uz-UZ`) |
  | TTS (matn → nutq) | Azure'ning o'zbekcha neyron ovozlari. Meta MMS — ochiq, sifatini sinang |

  Har rolga alohida ovoz bo'lsin: sudya, raqib, guvoh.
- **Ma'lumot tayyorlashda:** sud o'yinlari yozuvlarini Whisper bilan oflayn matnga aylantiring. Serverda sekin bo'lsa ham bo'ladi.
- **Sinov:** atamalari ko'p 20 ta yuridik jumla. O'lchanadi: STT xatolik darajasi (WER) va TTS qanchalik tabiiy eshitilishi.

### 4.5 Serveringizda nima ishlaydi (128 GB RAM, 1 TB SSD)

| GPU'siz ham ishlaydi | GPU'siz ishlamaydi |
|---|---|
| PostgreSQL + pgvector, FTS, `pg_trgm` | Real vaqtda katta LLM — javob ≤ 2,5 s talabi bajarilmaydi |
| bge-m3 embedding: indekslash bir marta, so'rovlar tez | Fine-tuning |
| Reranker (eng yaxshi 30 ta) | Real vaqtda Whisper large |
| Tesseract OCR, transliteratsiya, regex | |
| Backend, holatlar mashinasi, skriptli zaxira personaj (LexSim spetsifikatsiyasi, 4.5) | |
| Whisper oflayn (sekin) | |

**Disk:** 1 TB yetadi. Lex.uz'ning tanlangan qismi va o'n minglab qarorlar matni bir necha GB, vektorlar ham bir necha GB.

**GPU bo'lsa:** 7–32B ochiq modellarni tez ishlatish va fine-tune qilish mumkin (5-bo'lim).

---

## 5. Fine-tuning

### 5.1 Fine-tune qilinmaydigan narsalar
- **Qonun bilimi** → RAG. Qonun o'zgaradi, iqtibos tekshirilishi kerak.
- **Bosqichlar tartibi** → kod.
- **Ball** → formula.
- **Keys faktlari** → ssenariy fayli.

### 5.2 Nomzodlar (bajarish tartibida)

| # | Nima | Nega | Ma'lumot | Asos model | Qachon |
|---|---|---|---|---|---|
| 1 | Talaba harakatini aniqlovchi | Tez, arzon, lokal. Tor vazifani kichik model yaxshi o'rganadi | 2–5 ming belgilangan replika (lotin, kirill, rus aralash) | XLM-RoBERTa yoki 1–4B ochiq LLM | Pilotdan keyin |
| 2 | Qarordan keys ajratuvchi | Minglab qarorni arzon qayta ishlash | 1–2 ming juftlik (qaror → JSON). AI ajratadi, mentor tekshiradi | 7–8B ochiq LLM, QLoRA | Pilotdan keyin |
| 3 | Sud uslubidagi matn (qaror loyihasi, sudya iboralari) | Real qarorlarni insonlar yozgan — uslub sifatli | Anonimlashtirilgan minglab qaror | 7–14B ochiq LLM | Keyinroq |
| 4 | Rol agentlari (dialog) | Faqat lokal ishlash majburiy bo'lsa | 1000+ tekshirilgan majlis dialogi | 14–32B ochiq LLM | Eng oxirida |

### 5.3 Shartlar
- **GPU kerak.** Taxminan: QLoRA bilan 7–14B model 24 GB VRAM'li GPU'da, 30B atrofidagi model 48 GB'li GPU'da o'qitiladi. GPU'ni bulutdan ijaraga olsa ham bo'ladi.
- **Avval asos modellarni solishtiring.** O'zbekcha qobiliyatini [UzLiB](https://github.com/tahrirchi/uzlib) benchmarki va o'z 20 ta dialogingiz bilan tekshiring. O'zbekcha modellar (masalan, MustaqiLLM/MilliyLM ~5B) til uchun yaxshi, lekin tor vazifalar uchun.
- **Sinov to'plami alohida** — o'qitishda ishlatilmagan, yangi keyslardan bo'lsin.
- **API bilan solishtirish.** Fine-tune qilingan model kuchli API modeldan yomon bo'lsa, uni ishlatmang.
- **Shartlar:** kuchli model yaratgan javoblarni o'z modelingizni o'qitishga ishlatishdan oldin provayder shartlarini tekshiring. Real sud qarorlarida bunday cheklov yo'q, lekin sayt shartlari va anonimlik baribir qoladi.

### 5.4 Ma'lumot formati (misollar)

Talaba harakatini aniqlovchi uchun:

```json
{"messages": [
  {"role": "system", "content": "Talaba gapini protsessual harakat turlariga ajrat. Faqat JSON qaytar."},
  {"role": "user", "content": "Bosqich: dalillar. Gap: \"Hurmatli sud, bank ko'chirmasini ish materiallariga qo'shishni so'rayman.\""},
  {"role": "assistant", "content": "{\"tags\": [\"motion\", \"present-evidence\"]}"}
]}
```

Sudya ajrimi uchun (kirishda RAG moddalari ham beriladi):

```json
{"messages": [
  {"role": "system", "content": "Sen iqtisodiy sud sudyasisan. Faqat berilgan moddalarga tayan."},
  {"role": "user", "content": "Bosqich: dalillar. Raqib e'tirozi: \"Obyekt dalolatnoma bilan topshirilmagan.\" Talaba javobi: \"Hisob-fakturalar foydalanilganini tasdiqlaydi.\" Moddalar: [FK-544: ...], [IPK-...: ...]"},
  {"role": "assistant", "content": "{\"decision\": \"overruled\", \"basis\": [\"FK-544\"], \"say\": \"E'tiroz rad etiladi. Ish materiallaridagi hisob-fakturalar obyektdan foydalanilganini tasdiqlaydi.\"}"}
]}
```

Moddalar va ajrimlarning huquqiy mazmunini mentor tekshiradi.

---

## 6. Ish tartibi

### P0 — hakaton
1. **Ish turini tanlang** (mentor bilan): IPK yoki FPK.
2. **Bosqichlar jadvali** — mentor bilan, keyin u holatlar mashinasiga aylanadi.
3. **RAG P0:** A, B va C qatlamlari (200–500 bo'lak) → PostgreSQL + pgvector + FTS, bge-m3 embedding.
4. **RAG sinovi:** mentor yozgan 50 ta savol, Recall@5 o'lchanadi.
5. **Bitta ssenariy:** "sud keys" qaroridan (ijara qarzi va penya) keys fayli: rollar, har rolning maxfiy ma'lumoti, muhim lahzalar.
6. **Promptlar:** sudya, raqib (va guvoh); 3–5 namunaviy dialog; sud iboralari.
7. **Harakat teglari** va sinov uchun 150 ta belgilangan replika.
8. **Ajrim JSON sxemasi va kod tekshiruvi:** modda ID bormi, bu bosqichda bunday ajrim mumkinmi.
9. **Red-team:** sudyani "sindirishga" 10–20 ta urinish — u talabaga yon bosmasligini tekshirish.
10. **Ulash va o'lchash:** LexSim kontraktiga ulash, kechikishni o'lchash.

### P1 — pilot
- Qarorlarni ommaviy yig'ish va qayta ishlash (3.2-bo'lim), RAG D qatlami.
- Ssenariy fabrikasi (Batch API) va mentor tasdig'i.
- Reranker, ruscha matn maydoni.
- Embedding modellarini va LLM modellarini solishtirish.
- Ovozli rejimni sinash.
- Pilot dialoglarini yig'ish (rozilik bilan).

### P2 — keyinroq
- Fine-tuning, 5.2-bo'limdagi tartibda.
- Boshqa ish turlari: MJtK, MSIYuK, JPK.
- library.tsul.uz materiallari (ruxsat bilan).
- Talaba yuklagan hujjatlarni o'qish (vision).

---

## 7. Qabul mezonlari

| O'lchov | Maqsad |
|---|---|
| RAG Recall@5 (50 ta savol) | ≥ 0,9 |
| Iqtiboslar faqat berilgan moddalardan | 100% |
| Qidiruv kechikishi | ≤ 200 ms |
| Harakat aniqlash precision | ≥ 0,9 (LexSim spetsifikatsiyasi, 4.3) |
| `POST /turns` kechikishi | p50 ≤ 2,5 s, p95 ≤ 6 s (LexSim spetsifikatsiyasi, 2.5) |
| Sudyaning tartib buzilishiga munosabati (red-team) | Kamida 80% holatda to'g'ri e'tiroz yoki ogohlantirish |
| Ajrim asoslarining to'g'riligi (mentor tekshiradi) | ≥ 90% |
| Baholovchi va mentor mosligi | QWK ≥ 0,7 |

---

## 8. Xalqaro tajribadan olingan qoidalar

Batafsil — [tadqiqot hisobotida](reports/Xalqaro%20AI%20sud%20simulyatorlari.md).

- **Jarayonni kod, so'zni LLM boshqaradi** (SimCourt, moot-court-ai-lite, ChatCourt).
- **Modda raqam bo'yicha aniq topiladi va har qidiruvdan keyin tekshiriladi** (SimCourt, LawThinker).
- **Har rolning konteksti alohida** va har navbatda qayta yig'iladi — guvoh keys fayliga zid gapirmaydi.
- **AI sudya talabaga yon bosishga moyil.** Princeton tadqiqotida u tartib buzilishiga 40 foizdan kam holatda e'tiroz bildirgan — oldindan sinang.
- **Baholovchi alohida** va natijani emas, xulqni baholaydi.

---

## 9. Ochiq savollar

1. Serverda GPU bormi? Bo'lsa, qaysi modeli va xotirasi qancha?
2. Birinchi ish turi qaysi: IPK yoki FPK?
3. Lex.uz'dan ommaviy yuklash mumkinmi? Rasmiy ochiq ma'lumot, API yoki LexAI bilan hamkorlik bormi?
4. public.sud.uz'dan foydalanish shartlari qanday? Qarorlarni matn sifatida olsa bo'ladimi?
5. library.tsul.uz'dan foydalanishga kim ruxsat beradi?
6. API'ni O'zbekistondan ishlatish va to'lov qilish imkoniyati tekshirildimi?
