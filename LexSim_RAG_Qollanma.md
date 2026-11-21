# LexSim — RAG qo'llanmasi: Lex.uz'dan nima olinadi va qanday RAG qilinadi

**Kim uchun:** RAG'ni 8 GB GPU'li kompyuterda quradigan dasturchi.
**Natija:** PostgreSQL'dagi `law_chunks` jadvali — moddalar va Plenum bandlari embedding'lari bilan. Sudya agenti va baholovchi shu jadvaldan qidiradi.
**Bog'liq hujjatlar:** [LexSim_AI_Reja.md](LexSim_AI_Reja.md) (2-bo'lim), [LexSim_Backend_Spec.md](LexSim_Backend_Spec.md) (4.8 va 6.1-bo'limlar).

---

## 0. Qisqacha

1. **Qonun matnlari allaqachon olingan.** [data/lex](data/lex) papkasini o'sha kompyuterga ko'chiring: 4 ta kodeks, 1955 ta modda.
2. **Plenum qarorlarini** bitta buyruq bilan oling (1.2-bo'lim).
3. **Normallashtirish, bo'laklash, embedding:** `BAAI/bge-m3` modeli GPU'da, fp16 rejimida.
4. **Bazaga yozish:** PostgreSQL + pgvector + pg_trgm.
5. **Qidiruv:** aniq modda havolasi + vektor + trigram, keyin reranker.
6. **O'lchash:** mentorning 50 ta savoli bo'yicha Recall@5 ≥ 0,9.

---

## 1. Lex.uz'dan nima olinadi

Hamma narsa o'zbekcha lotin yozuvida olinadi (`?lang=4`). Skript: [tools/lex_extract.py](tools/lex_extract.py).

### 1.1 Kodekslar

| Ustuvorlik | Kod | Hujjat | lex.uz ID | Holati |
|---|---|---|---|---|
| P0 | FK1 | Fuqarolik kodeksi, 1-qism (majburiyatlar, neustoyka) | `111181` | ✅ olingan, 376 modda |
| P0 | FK2 | Fuqarolik kodeksi, 2-qism (ijara, qarz va boshqa shartnomalar) | `180550` | ✅ olingan, 803 modda |
| P0 | IPK | Iqtisodiy protsessual kodeks | `3523891` | ✅ olingan, 346 modda |
| P0 | FPK | Fuqarolik protsessual kodeksi | `3517334` | ✅ olingan, 430 modda |
| P1 | JPK | Jinoyat-protsessual kodeksi | `111463` | `python3 tools/lex_extract.py JPK=111463` |
| P1 | MJtK, MSIYuK | Ma'muriy javobgarlik kodeksi, Ma'muriy sud ishlarini yuritish kodeksi | ID'sini lex.uz qidiruvidan toping | keyinroq |

**Muhim:** FK1 va FK2'ning moddalari `FK-...` deb bitta prefiksda saqlanadi, chunki moddalar raqami ikki qismda davom etadi (masalan, `FK-326` 1-qismda, `FK-544` 2-qismda).

### 1.2 Plenum qarorlari

Ro'yxat kodekslardagi "LexUZ sharhi"da necha marta keltirilganiga qarab tuzildi:

| Ustuvorlik | Kod (o'zimiz bergan) | Qaror | lex.uz ID | Qaysi ishlar uchun |
|---|---|---|---|---|
| P0 | `OXS234` | Oliy xo'jalik sudi, 234-son (2011): mulk ijarasi shartnomasi | `-2004613` | IPK (namuna keysimiz) |
| P0 | `OXS163` | Oliy xo'jalik sudi, 163-son (2007): majburiyatni bajarmaganlik uchun mulkiy javobgarlik (neustoyka) | `-1636810` | IPK |
| P0 | `OXS283` | Oliy xo'jalik sudi, 283-son (2015): protsessual muddatlar | `-2712887` | IPK |
| P0 | `OXS204` | Oliy xo'jalik sudi, 204-son (2009): kelishuv bitimi | `-2026218` | IPK |
| P0 | `OS14` | Oliy sud, 14-son (2018): birinchi instansiya sudi FPK normalarini qo'llashi | `-3761338` | FPK |
| P0 | `OS19` | Oliy sud, 19-son (2019): birinchi instansiya sudining ajrimlari | `-4597589` | FPK |
| P0 | `OS12` | Oliy sud, 12-son (2019): sudning hal qiluv qarori | `-4396483` | FPK |
| P1 | `OS26` | Oliy sud, 26-son (2018): ishni sud muhokamasiga tayyorlash | `-3897686` | FPK |
| P1 | `OS37` | Oliy sud, 37-son (2024): sud xarajatlarini undirish | `-7305182` | FPK |
| P1 | `OXS196` | Oliy xo'jalik sudi, 196-son (2009): sud hujjatlarini ijro etish | `-1617964` | IPK |
| P1 | `OXS261` | Oliy xo'jalik sudi, 261-son (2014): ekspertiza | `-2453491` | IPK |
| P1 | `OXS270` | Oliy xo'jalik sudi, 270-son (2014): videokonferensaloqa rejimidagi majlis | `-2534033` | IPK |

Buyruq (P0 qarorlari, so'rovlar orasida 3 soniya pauza bilan):

```bash
python3 tools/lex_extract.py --plenum --out data/lex/plenum \
  OXS234=-2004613 OXS163=-1636810 OXS283=-2712887 OXS204=-2026218 \
  OS14=-3761338 OS19=-4597589 OS12=-4396483
```

**Har bir Plenum bandida `refs_codes` bor** — band tayangan moddalar ro'yxati (masalan, `OXS234-p3` → `FK-537`). Bu qidiruvda bog'liq moddalarni qo'shish uchun ham, keyinchalik embedder'ni o'qitish uchun tayyor juftliklar sifatida ham kerak (5.3-bo'lim).

**Mentor tekshirishi kerak:** har bir Plenum qarori hali amaldami? Oliy xo'jalik sudi 2017-yilda Oliy sudga birlashtirilgan. Uning ayrim qarorlari kuchini yo'qotgan yoki yangisi bilan almashtirilgan bo'lishi mumkin. lex.uz sahifasida holatini tekshiring.

### 1.3 Olinmaydigan narsalar
- **Lex.uz'ning hammasi.** Bazada 165 mingdan ortiq hujjat bor — idoraviy va mahalliy hujjatlar shovqin beradi.
- **Eski tahrirlar.** Skript faqat amaldagi matnni oladi. Eski tahrir faqat qonun o'zgarganda `valid_to` bilan saqlanadi (7-bo'lim).
- **Sud qarorlari (public.sud.uz)** — bu alohida qatlam (P1), alohida jadvalga yoziladi.

### 1.4 Lex.uz'dan olishda odob
- Skript har so'rovdan keyin 3 soniya kutadi va sahifani keshda saqlaydi (`data/lex/_cache`). Qayta ishlashda serverga qayta murojaat qilinmaydi.
- Ommaviy yuklab olishga ruxsatni LexAI jamoasidan so'rang: @lexai_support_bot yoki @huquqiyaxborot.

---

## 2. Kompyuterni tayyorlash (8 GB GPU)

```bash
# Python 3.10+ va CUDA'li PyTorch (CUDA versiyasiga mosini pytorch.org'dan oling)
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install sentence-transformers psycopg[binary] numpy tqdm

# PostgreSQL 16 + pgvector (shu kompyuterda yoki serverda)
# Ubuntu: sudo apt install postgresql-16 postgresql-16-pgvector
```

GPU xotirasi:

| Model | fp16'da xotira | 8 GB'ga sig'adimi |
|---|---|---|
| `BAAI/bge-m3` (568M) | ~1,1 GB + hisoblash | ✅ |
| `BAAI/bge-reranker-v2-m3` | ~1,1 GB | ✅ (embedding bilan birga ham) |
| `Qwen/Qwen3-Embedding-0.6B` | ~1,2 GB | ✅ |
| `Qwen/Qwen3-Embedding-4B` | ~8 GB | ❌ sig'maydi |

---

## 3. Normallashtirish va bo'laklash

### 3.1 Normallashtirish
Matnning o'zi (`text_latn`) **o'zgarmaydi** — foydalanuvchiga va iqtiboslarga shu ko'rsatiladi. Qidiruv uchun alohida `search_text` maydoni tayyorlanadi:
- **Apostroflar:** lex.uz lotin matnida `oʻ`, `gʻ` (U+02BB) va tutuq `ʼ` (U+02BC) ishlatiladi. Talaba esa `o'`, `o‘`, `o’` yozadi. `'`, `‘`, `’`, `` ` ``, `ʻ`, `ʼ` — hammasini bitta `'` belgisiga keltiring.
- **Kichik harf** va bo'sh joylarni tozalash.
- **Kirill yozuvidagi so'rov** (`Ҳурматли суд...`) → lotinga o'giriladi (qoidaviy transliteratsiya, model kerak emas).
- **Muhim:** so'rov ham xuddi shu funksiyadan o'tadi.

### 3.2 Bo'laklash
- **Kodekslar:** bitta modda — bitta bo'lak.
- **Uzun modda** (matni ~2000 belgidan uzun): xatboshilari bo'yicha ~1500 belgili bo'laklarga bo'linadi. Har bo'lak boshiga sarlavha qo'shiladi. `chunk_id` `FK-326#2` ko'rinishida, `norm_id` esa bir xil qoladi (`FK-326`).
- **Plenum:** bitta band — bitta bo'lak (`OXS234-p3`).
- **Embedding'ga beriladigan matn** sarlavha bilan boshlanadi, shunda qidiruv aniqroq bo'ladi:

```
FK 326-modda. Neustoykani kamaytirish
Agar toʻlanishi lozim boʻlgan neustoyka ...
```

### 3.3 Ish turlari (`case_types`)
Bu maydon fuqarolik ishida IPK yoki iqtisodiy sud Plenumi chiqib qolmasligi uchun kerak:

| Manba | `case_types` |
|---|---|
| FK | `{IPK,FPK}` |
| IPK | `{IPK}` |
| FPK | `{FPK}` |
| `OXS...` Plenumlari | `{IPK}` |
| `OS...` Plenumlari | `{FPK}` |

---

## 4. Embedding va bazaga yozish

### 4.1 Jadval

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE law_chunks (
  chunk_id        text PRIMARY KEY,       -- FK-326, FK-326#2, OXS234-p3
  norm_id         text NOT NULL,          -- iqtibos shu bilan: FK-326
  doc_type        text NOT NULL,          -- code | plenum
  code            text NOT NULL,          -- FK, IPK, FPK, OXS234 ...
  article_no      text,
  punkt           text,
  title           text,
  chapter         text,
  text_latn       text NOT NULL,          -- asl matn (ko'rsatish uchun)
  search_text     text NOT NULL,          -- normallashtirilgan (qidiruv uchun)
  lexuz_comment   text,
  refs            text[],                 -- bog'liq moddalar: {FK-537, FK-324}
  amendments      text[],
  case_types      text[] NOT NULL,
  lex_url         text NOT NULL,          -- faqat https://lex.uz/...
  doc_id          text,
  doc_title       text,
  valid_from      date,
  valid_to        date,                   -- NULL = amalda
  fetched_at      date,
  content_hash    text NOT NULL,          -- sha256(text_latn)
  embedding       vector(1024),
  embedding_model text
);
CREATE INDEX ON law_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON law_chunks USING gin (search_text gin_trgm_ops);
CREATE INDEX ON law_chunks (norm_id);
```

### 4.2 Embedding (GPU)

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3", device="cuda")
model.half()                      # fp16 — 8 GB GPU uchun
model.max_seq_length = 1024       # uzun moddalar bo'laklangani uchun yetadi

vecs = model.encode(texts, batch_size=16, normalize_embeddings=True,
                    show_progress_bar=True)
```

- 2 mingga yaqin bo'lak 8 GB GPU'da bir necha daqiqada hisoblanadi.
- `CUDA out of memory` xatosi chiqsa, `batch_size` ni 8 ga tushiring.
- Har qatorga `embedding_model = 'BAAI/bge-m3'` yoziladi.
- **Qoida:** so'rovlar ham **aynan shu model** bilan vektorga aylantirilishi shart.

---

## 5. Embedding modelini tanlash

### 5.1 `jamiyat_fikri` loyihangizdagi o'lchov

`jamiyat_fikri/.claude/skills/jonli-sinov/embedding-sinov/natijalar/2026-09-18/JADVAL.md` dagi natijalar (Hit@1, %):

| Model | Lotin | Kirill | Rus | Protsessorda so'rov |
|---|---|---|---|---|
| **bge-m3** | **97** | **100** | **100** | 331 ms |
| multilingual-e5-base (`query:` qo'shimchasi bilan) | 86–90 | 90 | 93 | 71 ms |
| LaBSE | 88 | 87,5 | 96,7 | 79 ms |
| multilingual-e5-small | 84 | 87,5 | 93 | 20 ms |
| granite-embedding-311m | 49 | 62,5 | 57 | 103 ms |

**Xulosa:** o'sha yerdagi tanlov — `bge-m3` — bu yerga ham mos. U o'zbek lotin, kirill va rus so'rovlarida eng aniq natija bergan, GPU'da esa sekinlik muammo emas.

**Lekin ehtiyot bo'ling:** o'sha sinov Telegram xabarlarida o'tkazilgan, huquqiy matnda emas. Natija o'tmaydi deb hisoblang va qayta o'lchang (6-bo'lim).

### 5.2 Solishtirish uchun nomzodlar

| Model | Nega | Holati |
|---|---|---|
| `BAAI/bge-m3` | Asosiy tanlov, sizning sinovingizda eng yaxshisi | ✅ ochiq, MIT litsenziyasi |
| `metricailab/UTE-1` | Aynan o'zbek huquqiy matni uchun o'qitilgan. EMNLP 2026 maqolasiga ko'ra eng yaxshi 5 tada 91,6% | ❓ maqolada chiqarilgan deyilgan, lekin men tekshirganimda Hugging Face sahifasi ochiq emas edi |
| `Qwen/Qwen3-Embedding-0.6B` | Yangi ko'p tilli model, 8 GB'ga sig'adi | sinab ko'rish kerak |
| LaBSE | — | ❌ ishlatmang: aniqligi past |

**Tanlash tartibi:** uchala nomzodni mentorning 50 ta savolida o'lchang. Recall@5 eng yuqori chiqqanini oling. Teng bo'lsa, `bge-m3` qoladi.

### 5.3 Embedder'ni fine-tune qilish (faqat kerak bo'lsa)
Agar reranker bilan ham Recall@5 < 0,9 bo'lsa, embedder'ni o'qitish mumkin. 8 GB GPU'da `bge-m3` uchun LoRA yoki kichik batch ishlaydi.

Tayyor o'quv juftliklari bor:
- Plenum bandi → u tayangan modda (`refs_codes`);
- LexUZ sharhidagi bog'liq moddalar (`refs`);
- mentor savollari.

Bu juftliklarni sinov to'plamiga aralashtirmang.

---

## 6. Qidiruv zanjiri va o'lchov

### 6.1 Qidiruv
1. **Normallashtirish** (3.1).
2. **Aniq havola.** Matnda "FK 326-modda", "IPKning 118-moddasi" yoki "ФКнинг 326-моддаси" bo'lsa, regex bilan `norm_id` topiladi va to'g'ridan-to'g'ri olinadi.
3. **Filtr:** `valid_to IS NULL AND :case_type = ANY(case_types)`.
4. **Gibrid qidiruv:** vektor bo'yicha eng yaxshi 30 ta va trigram bo'yicha eng yaxshi 30 ta, RRF bilan birlashtiriladi:

```sql
WITH v AS (
  SELECT chunk_id, row_number() OVER (ORDER BY embedding <=> :qvec) AS r
  FROM law_chunks
  WHERE valid_to IS NULL AND :case_type = ANY(case_types)
  ORDER BY embedding <=> :qvec LIMIT 30),
t AS (
  SELECT chunk_id, row_number() OVER (ORDER BY word_similarity(:q, search_text) DESC) AS r
  FROM law_chunks
  WHERE valid_to IS NULL AND :case_type = ANY(case_types) AND :q <% search_text
  ORDER BY word_similarity(:q, search_text) DESC LIMIT 30)
SELECT chunk_id, SUM(1.0 / (60 + r)) AS score
FROM (SELECT * FROM v UNION ALL SELECT * FROM t) x
GROUP BY chunk_id ORDER BY score DESC LIMIT 30;
```

5. **Reranker:** `BAAI/bge-reranker-v2-m3` eng yaxshi 30 tani qayta tartiblaydi → eng yaxshi 5–8 ta qoladi.
6. **Bog'liq moddalar:** `refs` dagi moddalar ham qo'shiladi (masalan, Plenum bandi → u tayangan FK moddasi).
7. **Modelga ID'lar bilan beriladi.** Model faqat shu ID'larni keltira oladi, kod buni tekshiradi.

### 6.2 O'lchov
- Mentor 50 ta savol yozadi va har biriga to'g'ri `norm_id` larni belgilaydi. Masalan: "Ijarachi kechiktirgan to'lov uchun penya juda katta, sud kamaytira oladimi?" → `FK-326`, `OXS163-p...`.
- Talaba yozadigan uslubda bo'lsin: lotin, kirill, ruscha aralash, imlo xatolari bilan.
- O'lchanadi: Recall@5 ≥ 0,9; qidiruv kechikishi ≤ 200 ms (embedding'siz).
- UTE-1 mualliflarining 178 ta savolli benchmarki ochiq bo'lsa, uni ham ishga tushiring.

### 6.3 Dastlabki sinov natijasi (2026-11-20, embedding'siz, faqat so'z qidiruvi)

12 ta savol bo'yicha oddiy BM25 qidiruvi: Recall@5 = **8/12**. Topilmagan 4 ta holat — aynan shu qo'llanmadagi qadamlar hal qiladigan muammolar:

| Savol | Nega topilmadi | Yechim |
|---|---|---|
| "Penya juda katta, sud kamaytira oladimi?" → `FK-326` | Talaba "penya" deydi, qonunda esa "neustoyka" | Sinonimlar lug'ati va embedding |
| "Iltimosnomani sud qanday hal qiladi?" → `IPK-169` | So'zlar juda umumiy, boshqa moddalar oldinga chiqdi | Embedding, `case_types` filtri, reranker |
| "Уменьшение неустойки судом" (ruscha) | Bazada faqat o'zbekcha matn bor | `bge-m3` tillararo ishlaydi (`jamiyat_fikri`dagi sinovda rus tili 100%) |
| "Ҳурматли суд, неустойкани камайтириш..." (kirill) | Kirill yozuvi lotinga o'girilmagan | So'rovni lotinga o'girish (3.1-bo'lim) |

Yana bitta tuzoq chiqdi: lex.uz sarlavhalarida `Daʼvo` (U+02BC belgisi) yozilgan, oddiy `da'vo` bilan qidiruv uni topmadi. Apostroflarni normallashtirish (3.1-bo'lim) shart.

**Sinonimlar lug'ati (boshlang'ich, mentor to'ldiradi).** So'rovga qonundagi atama qo'shiladi:

| Talaba yozadi | Qonundagi atama |
|---|---|
| penya, jarima (shartnoma bo'yicha) | neustoyka |
| arenda, ijara puli | ijara haqi, mol-mulkdan foydalanganlik uchun haq |
| shtraf | jarima, neustoyka |
| xodataystvo, so'rov | iltimosnoma |
| otvod | rad qilish |
| istets / otvetchik | da'vogar / javobgar |
| raspiska | tilxat |
| qarzni qaytarmayapti | qarz shartnomasi, qarz oluvchining majburiyati |

**Qamrov chegarasi:** bazada faqat FK, IPK, FPK va P0 Plenumlari bor. Masalan, mehnat yoki jinoyat ishi bo'yicha savolga RAG to'g'ri modda topa olmaydi. Bunday holatda tizim "manba topilmadi — mentor tekshirsin" deb javob berishi kerak, o'ylab topmasligi kerak.

---

## 7. Yangilash (qayta boshidan qilinmaydi)

| Holat | Nima qilinadi |
|---|---|
| Yangi hujjat | Ajratiladi va faqat yangi bo'laklar uchun embedding hisoblanib qo'shiladi |
| Modda o'zgardi (`content_hash` boshqacha) | Eski qatorga `valid_to` qo'yiladi, yangisi qo'shiladi |
| O'zgarish yo'q | Hech narsa qilinmaydi |
| Embedding modeli almashdi | Hamma embedding'lar qayta hisoblanadi — bir necha daqiqa |

---

## 8. Serverga o'tkazish

- **Jadvalni ko'chirish:** `pg_dump -t law_chunks lexsim > law_chunks.sql`, keyin serverda `psql lexsim < law_chunks.sql`.
- **So'rov embedding'i** serverda protsessorda hisoblanadi. `bge-m3` bilan bu taxminan 0,3 soniya (`jamiyat_fikri` o'lchovi bo'yicha). Javob uchun 2,5 soniyalik byudjetga sig'adi.
- **Muqobil:** GPU kompyuterda kichik embedding xizmati. Lekin u demo paytida o'chib qolsa, qidiruv to'xtaydi — server varianti ishonchliroq.

---

## 9. Tayyorlik ro'yxati

- [ ] `data/lex` (4 kodeks) ko'chirildi, P0 Plenum qarorlari olindi
- [ ] Mentor Plenum qarorlari hali amalda ekanini tasdiqladi
- [ ] Normallashtirish funksiyasi bitta va hujjatlar ham, so'rovlar ham undan o'tadi
- [ ] Uzun moddalar bo'laklandi, sarlavha har bo'lakda bor
- [ ] `law_chunks` jadvali va indekslar yaratildi
- [ ] Embedding hisoblandi (`embedding_model` yozilgan)
- [ ] 50 ta savol bo'yicha Recall@5 o'lchandi: bge-m3 / UTE-1 / Qwen3-0.6B
- [ ] Aniq havola (regex) va `case_types` filtri ishlaydi
- [ ] Jadval serverga ko'chirildi, serverda so'rov ishlaydi
