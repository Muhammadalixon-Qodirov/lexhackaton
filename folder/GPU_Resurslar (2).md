# Mavjud GPU resurslari: Reranker va o'zbekcha TTS (Chatterbox)

**Kim uchun:** shu resurslardan foydalanadigan AI agent yoki dasturchi.
**Holat:** ✅ hammasi ishlayapti (tekshirilgan: 2026-11-21).
**Qayerda hisoblanadi:** GPU kompyuterda (Windows, NVIDIA RTX 3050 8 GB). Sizning kodingiz modelni o'zi yuklamaydi, faqat quyidagi manzillarga so'rov yuboradi.

| Resurs | Nima qiladi | Qayerdan chaqiriladi | Tezlik |
|---|---|---|---|
| **LexSim qidiruv + Reranker** | O'zbek qonunlari (FK, IPK, FPK + 7 ta Plenum qarori) bo'yicha RAG qidiruvi; GPU reranker bilan | **Server ichidan:** `http://127.0.0.1:8090` (server: `einvestment@192.168.88.110`) | ~0.9 s / so'rov |
| **Reranker (alohida)** | Istalgan matnlar ro'yxatini savolga mosligi bo'yicha baholaydi (0–1) — o'z RAG'ingiz uchun | **Server ichidan:** `http://127.0.0.1:8091/rerank` (kalit bilan) | ~0.1–0.5 s / so'rov |
| **Chatterbox TTS** | O'zbekcha matn → tabiiy ovoz; ovozni bir marta klonlab saqlash mumkin | **Server ichidan:** `http://127.0.0.1:8092` (GPU kompyuterning o'zida: `http://localhost:7102`) | ~6.5–10 s / gap (3 s audio) |

---

## 1. LexSim qidiruv (reranker bilan)

### Qidiruv
```bash
curl -s -X POST http://127.0.0.1:8090/search -H 'Content-Type: application/json' \
  -d '{"q": "Penya juda katta, sud kamaytira oladimi?", "case_type": "IPK", "k": 5}'
```
- `q` — savol (lotin, kirill yoki ruscha; imlo xatosi bo'lsa ham bo'ladi), ≤ 2000 belgi.
- `case_type` — `"IPK"` (iqtisodiy ish), `"FPK"` (fuqarolik ishi) yoki `null`.
- `k` — natijalar soni, 1–10 (standart 5).

### Javob
```json
{
  "confident": true,
  "reranked": true,
  "results": [
    {"norm_id": "FK-326", "chunk_id": "FK-326", "title": "Neustoykani kamaytirish",
     "lex_url": "https://lex.uz/docs/111181#-155297", "score": 0.977, "via": "search"},
    {"norm_id": "OXS163-p4", "chunk_id": "OXS163-p4", "title": "... — 4-band",
     "lex_url": "https://lex.uz/docs/-1636810#-1636822", "score": 0.837, "via": "search"}
  ],
  "related": ["OXS163-p11", "FK-327"],
  "ms": 870
}
```

### Javobni qanday ishlatish
- **`results`** — eng mos 5 ta manba. Modelga matn bilan birga **`norm_id`** larni bering. Javobda faqat shu ID'larga iqtibos keltirilsin. `lex_url` — manbaning lex.uz'dagi havolasi.
- **`confident: false`** — bazada mos manba topilmadi (masalan jinoyat yoki mehnat ishi; bazada faqat FK, IPK, FPK va P0 Plenumlar bor). Bu holda **"Manba topilmadi — mentor tekshirsin"** deb javob bering va o'zingizdan modda to'qimang.
- **`reranked: false`** — GPU kompyuter hozir o'chiq. Natija baribir keladi, lekin biroz kamroq aniq bo'ladi. Ishni davom ettiring, xato emas.
- **`related`** — bog'liq moddalar va Plenum bandlari. Qo'shimcha kontekst uchun.
- **`via: "exact"`** — savolda aniq havola bor edi ("FK 326-modda", "ФКнинг 326-моддаси"), o'sha modda birinchi qo'yilgan.

### Holatni tekshirish
```bash
curl -s http://127.0.0.1:8090/health
# "remote_reranker_ok": true  -> GPU reranker ulangan
```

### Sifat (45 ta sinov savoli)
Recall@5 = **0.967** (GPU reranker bilan), **0.878** (GPU o'chiq bo'lsa).

---

## 2. Reranker — alohida ishlatish

**Model:** `BAAI/bge-reranker-v2-m3` — ko'p tilli (o'zbek, rus, ingliz…) cross-encoder, GPU'da. Savol va har bir matnni **birga** o'qib, mosligini baholaydi. Vektor qidiruvdan keyin eng yaxshi nomzodlarni tanlash uchun ishlatiladi (LexSim qidiruvi ichida ham aynan shu model ishlaydi).

**Qachon kerak:** sizda o'z ma'lumotlaringiz bo'yicha qidiruv bor (masalan backend'dagi stsenariylar, hujjatlar) va topilgan 10–50 ta nomzoddan eng moslarini tanlash kerak. LexSim qonunlari uchun buni qilmang — 1-bo'limdagi `/search` allaqachon reranker bilan ishlaydi.

### So'rov (server ichidan)
Kalit serverdagi `~/.lexsim.env` faylida (`LEXSIM_RERANK_KEY`). Uni o'qing, lekin log'ga yoki javobga chiqarmang.
```bash
set -a; . ~/.lexsim.env; set +a
curl -s -X POST http://127.0.0.1:8091/rerank \
  -H "X-Key: $LEXSIM_RERANK_KEY" -H 'Content-Type: application/json' \
  -d '{"query": "Penya juda katta, sud kamaytira oladimi?",
       "texts": ["FK 326-modda. Neustoykani kamaytirish. ...", "FK 734-modda. Qarz shartnomasi bo‘yicha foizlar.", "Bugun havo juda yaxshi."]}'
# {"scores": [0.021, 0.000016, 0.000016], "ms": 271}
```

```python
import json, os, urllib.request

def rerank(query: str, texts: list[str]) -> list[float] | None:
    """Baholar texts tartibida; GPU kompyuter javob bermasa None (o'z tartibingiz bilan davom eting)."""
    req = urllib.request.Request(
        "http://127.0.0.1:8091/rerank", method="POST",
        data=json.dumps({"query": query, "texts": texts}).encode(),
        headers={"Content-Type": "application/json", "X-Key": os.environ["LEXSIM_RERANK_KEY"]})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())["scores"]
    except Exception:
        return None

scores = rerank(savol, nomzodlar)
eng_yaxshi = [t for _, t in sorted(zip(scores, nomzodlar), reverse=True)][:5] if scores else nomzodlar[:5]
```

### Qoidalar
- Bitta so'rovda **≤ 50 ta matn**, so'rov hajmi ≤ 2 MB; har matnning taxminan birinchi **512 tokeni** (~1500–2000 belgi) hisobga olinadi.
- **Baholarning nisbiy tartibiga** qarang — mutlaq qiymat matn uzunligiga bog'liq (yuqoridagi misolda to'g'ri matn 0.021, lekin baribir boshqalardan ~1000 marta yuqori). To'liq modda matnlarida mos manba odatda **> 0.3** oladi.
- **Kalitsiz so'rov → 401.** GPU kompyuter o'chiq bo'lsa ulanish xatosi keladi — `timeout` qo'ying (5 s) va reranker'siz davom eting (`None` holati).
- Holat: `curl -s -H "X-Key: $LEXSIM_RERANK_KEY" http://127.0.0.1:8091/health` → `{"ok": true, "device": "cuda", "gpu": "NVIDIA GeForce RTX 3050"}`.

---

## 3. Chatterbox — o'zbekcha TTS

**Manzil:** server ichidan `http://127.0.0.1:8092` — GPU kompyuterdagi Chatterbox'ga teskari SSH tunnel (faqat `127.0.0.1`, internetga ham, LAN'ga ham ochiq emas). Avvalgi ommaviy `trycloudflare` havolasi **2026-11-21 da yopildi** (parolsiz edi).

### Ishlash tartibi
1. **Bir marta:** ovozni klonlash — `/clone`. 5–10 soniyalik toza namuna va nom beriladi. Ovoz serverda saqlanadi. Bu qadam ~4 s oladi.
2. **Kerak bo'lsa:** saqlangan ovozni tanlash — `/use_voice`. `"Standart ovoz"` — model ichidagi tayyor ovoz.
3. **Har safar:** gapirtirish — `/speak`. Matn beriladi, `.wav` audio qaytadi. Klonlash qaytadan qilinmaydi.

### Python (eng oson yo'l)
```python
# pip install gradio_client
from gradio_client import Client, handle_file

c = Client("http://127.0.0.1:8092")   # server ichidan

# bir marta: ovozni klonlab saqlash
c.predict(handle_file("namuna.wav"), "mening_ovozim", api_name="/clone")

# ovozni tanlash (yoki "Standart ovoz")
c.predict("mening_ovozim", api_name="/use_voice")

# gapirtirish
wav_path, info = c.predict("Assalomu alaykum! Ertaga soat o'nda uchrashamiz.", api_name="/speak")
print(wav_path)   # tayyor .wav fayl (24 kHz)
print(info)       # masalan: "6.4 s hisoblash, 3.0 s ovoz, RTF=2.09 (CUDA)"
```

### HTTP (Gradio protokoli, ikki qadam)
```bash
B=http://127.0.0.1:8092
# 1) so'rov yuborish -> event_id
curl -s -X POST $B/gradio_api/call/speak -H 'Content-Type: application/json' -d '{"data": ["Assalomu alaykum!"]}'
# 2) natijani olish: oxirgi "data:" qatorida [{"url": ".../audio.wav", ...}, "info"]
curl -s -N $B/gradio_api/call/speak/<event_id>
```

### Matn qoidalari
- Matnni **o'zbek lotin** yozuvida bering. Apostroflar (`oʻ`, `o'`, `o’`) avtomatik to'g'rilanadi.
- Raqamlar ("soat 10") avtomatik so'zga aylantiriladi.
- Uzun matnni **gaplarga bo'lib** yuboring. Bitta gap ~6–7 s ichida tayyor bo'ladi. Birinchisini eshittira turib, keyingisini so'rang.

---

## 4. Foydalanish qoidalari

1. **Chatterbox ham, reranker ham bir vaqtda bitta so'rovni bajaradi** (GPU bitta). Bir nechta so'rov kelsa, ular navbatda kutadi. Reranker'ga bir vaqtda ko'p so'rov yubormang — LexSim `/search` ham shu GPU'dan foydalanadi.
2. **Tanlangan ovoz hammaga umumiy.** `/use_voice` ilovaning butun ovozini almashtiradi. Bir nechta ovoz bilan ishlasangiz, har bir `/speak` dan oldin `/use_voice` ni chaqiring.
3. **Chatterbox manzili doimiy:** `http://127.0.0.1:8092` (server ichidan). Ilova va tunnel avtostart qilingan — Windows vazifalari har daqiqada tekshiradi, yo'q bo'lsa yoqadi. Ilova qayta ishga tushsa model ~30–150 s yuklanadi — shu vaqt ichida 8092 javob bermasligi mumkin; MMS'ga zaxira bilan ishlang. Javobdagi fayl `url` lari ham `http://127.0.0.1:8092/gradio_api/file=...` ko'rinishida keladi — shu manzildan yuklab oling.
4. **Bu xizmatlarni qayta ishga tushirmang va ularning sozlamalariga tegmang.** Bularga GPU kompyuterdagi reranker va tunnel, serverdagi `lexsim-api` systemd xizmati va 8090/8091 portlari kiradi. Ularni egasi boshqaradi. Muammo bo'lsa, `/health` natijasi bilan xabar bering.
5. Har bir audioda ko'rinmas suv belgisi (Perth watermark) bor. Audio sun'iy ovoz ekani shu orqali aniqlanishi mumkin.
