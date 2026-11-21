# GPU xizmatlari: Reranker va Chatterbox (o'zbekcha TTS)

**Kim uchun:** bu ikki xizmatni o'z loyihasiga (masalan LexSim backend'iga) ulaydigan dasturchi.
**Holat sanasi:** 2026-11-21. Barcha raqamlar shu sanada o'lchangan.
**Qisqacha:** ikkala model ham **GPU kompyuterda** ishlaydi (Windows, NVIDIA RTX 3050 8 GB, LAN IP `192.168.88.43`).
- **Reranker** serverga (`einvestment@192.168.88.110`) ulangan va hozir ishlayapti.
- **Chatterbox** hozircha faqat shu kompyuterning o'zidan yoki vaqtinchalik ochiq havola orqali ishlaydi. Serverdan barqaror ulanish **hali qilinmagan** (6-bo'lim).

---

## 1. Umumiy sxema

```
                SERVER (192.168.88.110, GPU yo'q)                         GPU KOMPYUTER (192.168.88.43, RTX 3050)
 ┌──────────────────────────────────────────────────┐            ┌───────────────────────────────────────────┐
 │ loyiha backend'i                                  │            │                                           │
 │   │ POST /search                                  │            │                                           │
 │   ▼                                               │            │                                           │
 │ lexsim-api (systemd, 127.0.0.1:8090)              │            │                                           │
 │   ├─ bge-m3 so'rov embedding (CPU)                │            │                                           │
 │   ├─ PostgreSQL + pgvector (127.0.0.1:5432)       │            │                                           │
 │   └─ reranker → 127.0.0.1:8091 ═══ teskari SSH tunnel ═══════► rerank_server.py 127.0.0.1:8091 (GPU)    │
 └──────────────────────────────────────────────────┘            │                                           │
                                                                  │ app_uaz_gpu.py (Chatterbox) 0.0.0.0:7102  │
   brauzer / test ─── https://...trycloudflare.com (vaqtinchalik) ─► (Gradio UI + API)                       │
                                                                  └───────────────────────────────────────────┘
```

Videokarta xotirasi: TTS, STT va reranker uchalasi birga **~6.8 / 8 GB** band qiladi.

---

## 2. Reranker

### 2.1 Nima va nima uchun kerak
- **Model:** `BAAI/bge-reranker-v2-m3`. Ko'p tilli **cross-encoder**, 568M parametr. GPU'da fp16 rejimida ishlaydi, matnning birinchi 512 tokenini o'qiydi.
- **Qidiruvdagi o'rni.** RAG qidiruvi ikki bosqichli:
  1. **Vektor qidiruv (`bge-m3`) — tez.** Savolga ma'nosi yaqin 30 ta bo'lakni topadi.
  2. **Reranker — sekin, lekin aniq.** Har bir nomzodni savol bilan **birga** o'qib, 0 dan 1 gacha baho beradi. Eng yaxshi 5 tasi qoladi.
- **Foydasi (45 savol, LexSim sinov to'plami):**
  - rerankersiz: Recall@5 **0.878**
  - reranker bilan: **0.967**
- **Nega GPU kompyuterda.** Server protsessorida (E5-2690 v4, AVX-512 yo'q) bitta savolga **10–19 s** ketadi, bu 2.5 s byudjetga sig'maydi. GPU'da esa ~0.5 s.

### 2.2 Joylashuv

| Narsa | Qayerda |
|---|---|
| Xizmat kodi | `D:\lexsim\tools\rerank_server.py` (faqat `127.0.0.1:8091`) |
| Python muhiti | `D:\lexsim\venv` (torch 2.6 cu124 `C:\sayro_local\venv` dan `.pth` orqali olinadi) |
| Tunnel | `D:\lexsim\tunnel.ps1`, SSH kalit `C:\Users\ali20\.ssh\lexsim_tunnel` |
| Avtostart | Task Scheduler vazifasi **"LexSim reranker"** → `D:\lexsim\autostart.ps1` (Windows'ga **kirilganda**) |
| Maxfiy kalit | kompyuterda `C:\Users\ali20\.lexsim_rerank_key`, serverda `~/.lexsim.env` → `LEXSIM_RERANK_KEY` (kalitning o'zi bu hujjatga yozilmagan) |
| Loglar (kompyuter) | `D:\lexsim\autostart.log`, `tunnel.log`, `rerank.err` |

### 2.3 Tavsiya etilgan ulanish: `lexsim-api` orqali

Loyiha reranker'ga **to'g'ridan-to'g'ri murojaat qilmasligi kerak**. Server ichida `lexsim-api` chaqiriladi: qidiruv, filtr, reranker va zaxira rejimining hammasi uning ichida.

**So'rov** (server ichidan; xizmat faqat `127.0.0.1`da ochiq):
```bash
curl -s -X POST http://127.0.0.1:8090/search -H 'Content-Type: application/json' \
  -d '{"q": "Penya juda katta, sud kamaytira oladimi?", "case_type": "IPK", "k": 5}'
```
- `q` — savol. Lotin, kirill va rus tili qabul qilinadi, birinchi 2000 belgi ishlatiladi.
- `case_type` — `"IPK"`, `"FPK"` yoki `null`.
- `k` — natijalar soni, 1–10.

**Javob:**
```json
{
  "confident": true,
  "reranked": true,
  "results": [
    {"norm_id": "FK-326", "chunk_id": "FK-326", "title": "Neustoykani kamaytirish",
     "lex_url": "https://lex.uz/docs/111181#-155297", "score": 0.977, "via": "search"}
  ],
  "related": ["OXS163-p11", "FK-327"],
  "ms": 870
}
```

| Maydon | Ma'nosi | Loyiha nima qilishi kerak |
|---|---|---|
| `reranked` | `true` — GPU reranker ishladi. `false` — kompyuter o'chiq yoki javob bermadi, natijalar faqat vektor tartibida | `false` bo'lsa natija biroz kamroq aniq (Recall ~0.88). Log'ga yozish yetarli |
| `confident` | `false` — eng yaxshi natijaning bahosi 0.3 dan past | Bunda **"manba topilmadi — mentor tekshirsin"** deb javob bering, o'zingizdan javob to'qimang. Bu faqat `reranked=true` bo'lganda baholanadi |
| `score` | Reranker bahosi, 0–1 | `reranked=false` bo'lsa `null` |
| `via` | `"exact"` — matnda aniq havola bor edi ("FK 326-modda"); `"search"` — qidiruv natijasi | — |
| `related` | Bog'liq moddalar va Plenum bandlari (`refs`) | Qo'shimcha kontekst sifatida berish mumkin |

**Holatni tekshirish:**
```bash
curl -s http://127.0.0.1:8090/health
# {"ok": true, "rows": 2423, "model": "BAAI/bge-m3", "reranker": "remote", "remote_reranker_ok": true, "rerank_n": 30}
```
`remote_reranker_ok: false` — GPU kompyuter hozir ulanmagan.

### 2.4 To'g'ridan-to'g'ri reranker (faqat boshqa maqsad uchun kerak bo'lsa)
Serverda `127.0.0.1:8091`, kalit bilan:
```bash
set -a; . ~/.lexsim.env; set +a
curl -s -X POST http://127.0.0.1:8091/rerank -H "X-Key: $LEXSIM_RERANK_KEY" -H 'Content-Type: application/json' \
  -d '{"query": "savol", "texts": ["1-matn", "2-matn"]}'
# {"scores": [0.91, 0.02], "ms": 40}
```
- Bitta so'rovda ko'pi bilan **50 ta matn**, so'rov hajmi ≤ 2 MB.
- Kalitsiz so'rov → `401`.
- So'rovlar navbat bilan bajariladi: GPU bitta.

### 2.5 O'lchangan raqamlar (server + GPU reranker, 45 savol)

| | Recall@5 | Bazadagi qidiruv (p50) | Jami javob (p50) |
|---|---|---|---|
| GPU reranker ishlayapti | **0.967** | 18 ms | **0.87 s** |
| Zaxira (kompyuter o'chiq) | 0.878 | ~20 ms | 2.8–5.5 s* |

\* Zaxira rejimida server avval reranker'ni kutadi: `LEXSIM_RERANK_TIMEOUT`, standart 5 s. Bu vaqtni `~/.lexsim.env` da kamaytirsa bo'ladi.

**Eslatma:** sinov to'plamini (45 savol) Claude tuzgan, mentorniki emas. Mentorning 50 savoli bilan qayta o'lchash kerak.

### 2.6 Ishonchlilik
- **Tunnel uzilsa,** 10 s da o'zi qayta ulanadi.
- **Kompyuter keskin o'chsa,** server o'lik sessiyani ≤ 90 s da yopadi. Bu `/etc/ssh/sshd_config.d/60-clientalive.conf` faylidagi keepalive sozlamasi orqali ishlaydi. Sinovda tunnel 11 s da o'zi tiklandi.
- **Reranker jarayoni yiqilsa,** `autostart.ps1` uni 15 s da qayta ishga tushiradi.
- **Tunnel kaliti** serverda `command="/bin/false",restrict,port-forwarding,permitlisten="127.0.0.1:8091"` bilan cheklangan: u bilan faqat shu bitta portni ochish mumkin, buyruq bajarib bo'lmaydi.

---

## 3. Chatterbox (o'zbekcha TTS)

### 3.1 Nima va qanday ishlaydi
- **Model:** `UAzimov/Uzbek-tts-chatterbox`. Bu Resemble AI **Chatterbox Standard** modeliga (~500M, Llama asosli T3 + S3Gen) qo'shilgan o'zbekcha LoRA adapter.
- Kod `gokhaneraslan/chatterbox-finetuning` repo'sidan olingan. Litsenziya: MIT.
- **Ishlash bosqichlari:**
  1. **Ovoz namunasi (conditioning).** Namuna audiodan ovoz xususiyatlari olinadi: speaker embedding va namunaning ovoz tokenlari. Buni **bir marta** qilib, `.pt` faylga saqlaymiz.
  2. **T3 — matndan ovoz tokenlari.** Avtoregressiv: tokenlar birma-bir hisoblanadi. **Vaqtning asosiy qismi shu bosqichda ketadi.**
  3. **S3Gen — tokenlardan 24 kHz audio.** Audioga ko'rinmas **Perth watermark** (suv belgisi) qo'shiladi.
- **Matn:** lotin yozuvida. Apostroflar (`ʻ`, `’` va h.k.) avtomatik `'` ga keltiriladi, raqamlar so'zga aylantiriladi (`uz_normalize`).

### 3.2 Joylashuv

| Narsa | Qayerda |
|---|---|
| Ilova | `D:\voice_local\app_uaz_gpu.py` (Gradio 5.50, port **7102**) |
| Python muhiti | `D:\voice_local\venv` (torch 2.6 cu124 `.pth` orqali) |
| Model | `D:\voice_local\chatterbox-finetuning\pretrained_models` (base) + `D:\voice_local\uazimov` (adapter) |
| Saqlangan ovozlar | `D:\voice_local\voices\<nom>.pt` (bitta ovoz ~70 KB) |
| Loglar | `D:\voice_local\uaz.log`, `uaz.err` |

Model ilova ochilganda **oldindan yuklanadi** (~31 s). Shuning uchun birinchi so'rov kutmaydi.

### 3.3 Ishlatish tartibi
1. **Bir marta:** `/clone` — namuna (5–10 s, toza ovoz) va nom → ovoz klonlanadi va `voices/<nom>.pt` ga saqlanadi. **~4.3 s.**
2. **Kerak bo'lganda:** `/use_voice` — saqlangan ovozni tanlash (**~0.02 s**). `"Standart ovoz"` — model ichidagi standart ovoz.
3. **Har safar:** `/speak` — matn → audio. Klonlash qaytadan qilinmaydi.

### 3.4 API (Gradio)
Endpoint'lar: `/clone (ref_audio, name)`, `/use_voice (name)`, `/speak (text)` → `(audio, info)`.

**Python (`pip install gradio_client`):**
```python
from gradio_client import Client, handle_file

c = Client("http://localhost:7102")            # shu kompyuterdan; tashqaridan — 6-bo'limga qarang
c.predict(handle_file("namuna.wav"), "mening_ovozim", api_name="/clone")   # bir marta
c.predict("mening_ovozim", api_name="/use_voice")
wav_path, info = c.predict("Assalomu alaykum! Ertaga soat o'nda uchrashamiz.", api_name="/speak")
print(wav_path, info)   # vaqtinchalik .wav fayl yo'li; info: "6.4 s hisoblash, 3.0 s ovoz, RTF=2.09 (CUDA)"
```

**HTTP (ikki qadamli Gradio protokoli):**
```bash
# 1) so'rov -> event_id
curl -s -X POST http://localhost:7102/gradio_api/call/speak -H 'Content-Type: application/json' \
  -d '{"data": ["Assalomu alaykum!"]}'
# {"event_id": "abc..."}
# 2) natija (SSE). Oxirgi "data:" qatorida [ {"url": ".../audio.wav", ...}, "info" ]
curl -s -N http://localhost:7102/gradio_api/call/speak/abc...
```
Fayl yuborish (`/clone` uchun): avval `POST /gradio_api/upload -F files=@namuna.wav` qilinadi, keyin qaytgan yo'l `{"path": "...", "meta": {"_type": "gradio.FileData"}}` ko'rinishida beriladi.

### 3.5 O'lchangan raqamlar (RTX 3050)

| Amal | Vaqt |
|---|---|
| Ilova ishga tushishi (model yuklash) | ~31 s, bir marta |
| Klonlash (`/clone`) | 4.3 s, ovoz uchun bir marta |
| Saqlangan ovozni yuklash (`/use_voice`) | 0.02 s |
| Gapirish: 3.0–3.2 s audio (`/speak`) | **6.4–7.2 s** (RTF ≈ 2.1–2.2) |

Solishtirish uchun shu model **server protsessorida**: ~20–25 s/gap (iliq holatda, taxminiy). Serverdagi **MMS** esa ~0.7–1 s, lekin ovozi sun'iyroq.

### 3.6 Cheklovlar (loyihaga ulashdan oldin bilish kerak)
- **Real-time emas.** Bitta gap uchun audioning o'zidan ~2 baravar uzoq kutiladi. Jonli suhbat uchun matnni gaplarga bo'lib, birinchi gap tayyor bo'lishi bilan eshittirish kerak.
- **Faol ovoz hammaga bitta.** `/use_voice` butun ilova uchun ovozni almashtiradi, ya'ni ikki foydalanuvchi bir vaqtda turli ovoz so'rasa bir-biriga xalaqit beradi. Ko'p foydalanuvchili tizimda har `/speak`dan oldin `/use_voice` chaqiring yoki bitta ovozda qoling.
- **So'rovlar navbat bilan bajariladi** (bitta GPU). Bir vaqtda kelgan so'rovlar navbatda kutadi.
- **Avtostart yo'q.** Kompyuter qayta yonsa, ilovani qo'lda ishga tushirish kerak (5-bo'lim).
- **Watermark.** Har bir audioda Perth suv belgisi bor. U eshitilmaydi, lekin sun'iy ovoz ekanini aniqlashga imkon beradi.

---

## 4. "Loyihamni ulasam, ishlaydimi?"

| Loyiha qayerda ishlaydi | Reranker (RAG qidiruvi) | Chatterbox |
|---|---|---|
| **Serverda** (192.168.88.110) | ✅ **Ishlaydi.** `http://127.0.0.1:8090/search`. Kompyuter o'chiq bo'lsa ham javob beradi (`reranked=false`) | ⚠️ **Hozir barqaror emas.** Serverdan 7102 ga LAN orqali ulanib bo'lmaydi (sinovda brandmauer blokladi). Faqat vaqtinchalik Cloudflare havolasi bor. Yechim — 6-bo'lim |
| **Shu GPU kompyuterning o'zida** | ✅ Serverdagi API'ga murojaat qilish kerak. Kompyuterning lokal bazasi (`D:\lexsim`, port 5433) faqat sinov uchun | ✅ **Ishlaydi.** `http://localhost:7102` |
| **Boshqa joyda** (internet, boshqa kompyuter) | ❌ `lexsim-api` tashqariga ochilmagan. Ochish kerak bo'lsa: nginx + kalit + TLS (qilinmagan) | ⚠️ Faqat vaqtinchalik `*.trycloudflare.com` havolasi orqali: u **parolsiz va ochiq**, qayta ishga tushganda o'zgaradi. Ishlab chiqarish uchun yaramaydi |

**Ikkala xizmat ham ishlashi uchun shartlar:**
1. GPU kompyuter **yoqilgan va unga kirilgan** bo'lishi kerak. Avtostart Windows'ga kirganda ishlaydi, login ekranida emas.
2. Uyqu rejimi va gibernatsiya xizmatlarni to'xtatadi. Doimiy ishlashi kerak bo'lsa, Windows quvvat sozlamalarida uyquni o'chiring.
3. Videokartani TTS, STT va reranker birga ishlatadi. Uchchalasi sig'adi (~6.8/8 GB), lekin yana model qo'shishga joy deyarli yo'q.

---

## 5. Boshqaruv buyruqlari

**GPU kompyuter (PowerShell):**
```powershell
# Reranker + tunnel (avtostart vazifasi qo'lda ishga tushiriladi)
Start-ScheduledTask -TaskName "LexSim reranker"
# Chatterbox (avtostartsiz)
$env:HF_HUB_OFFLINE="1"
Start-Process D:\voice_local\venv\Scripts\python.exe -ArgumentList D:\voice_local\app_uaz_gpu.py `
  -RedirectStandardOutput D:\voice_local\uaz.log -RedirectStandardError D:\voice_local\uaz.err -WindowStyle Hidden
# Holat
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
Get-Content D:\lexsim\tunnel.log -Tail 5
```

**Server:**
```bash
sudo systemctl status lexsim-api          # qidiruv API
sudo systemctl restart lexsim-api
tail -f ~/lexsim/logs/api.log
curl -s http://127.0.0.1:8090/health      # remote_reranker_ok = GPU ulanganmi
sudo ss -ltnp | grep 8091                 # tunnel ochiqmi (sudo'siz PID ko'rinmaydi)
```

---

## 6. Hali qilinmagan ishlar (tavsiya)

1. **Chatterbox'ni serverga barqaror ulash.** Hozirgi Gradio o'rniga oddiy HTTP endpoint (`POST /tts {text, voice} → wav`) qilish va uni reranker kabi teskari SSH tunnel orqali serverga ochish (masalan `127.0.0.1:8092`). Shunda server loyihasi TTS'ga xuddi `/search` kabi murojaat qiladi. Kompyuter o'chiq bo'lsa, zaxira sifatida serverdagi **MMS** (`aidemo-mms`, port 7008, tez lekin sun'iyroq ovoz) ishlatiladi.
2. **Chatterbox avtostarti.** Reranker'dagi kabi Task Scheduler orqali.
3. **Ochiq Cloudflare havolasini yopish.** 7102 uchun quick tunnel parolsiz. Sinovlar tugagach uni to'xtatish kerak.
4. **Mentorning 50 savoli bilan RAG'ni qayta o'lchash** va `confident` chegarasini (0.3) sozlash.
