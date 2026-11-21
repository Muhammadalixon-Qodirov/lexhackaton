# LexSim backend v1 — frontendni ulash

**Kimga:** frontend jamoasi.
**Holat:** 2026-11-20 da serverda ishga tushirildi va ikkala rol bo'yicha boshidan oxirigacha sinovdan o'tdi.
**Kontrakt:** [LexSim_Backend_Spec.md](LexSim_Backend_Spec.md) bilan bir xil: `/api/v1/*`, `{events, snapshot}`, cookie `lexsim_owner`, xato `{error:{code,message}}`. Frontend kodini deyarli o'zgartirish shart emas. Faqat proxy va `scenarioId` kerak.

> **Yangilanish (v1.2, 2026-11-21):** frontend v2 talablari ([COURT_BACKEND.md](COURT_BACKEND.md)) bajarildi — javob va o'zgarishlar ro'yxati: [COURT_BACKEND_javob.md](COURT_BACKEND_javob.md). Muhim o'zgarishlar:
> - 2-bo'limdagi `rewrites` tavsiyasi **bekor**: frontend o'z adapteri orqali ulanadi;
> - 3.2-bo'limdagi ovoz endi MP3 va 4 ta ovoz bilan ishlaydi;
> - LLM kerak bo'lgan gaplarga `/turns` **202** qaytaradi.

---

## 1. Qisqacha

| Nima | Qiymat |
|---|---|
| Manzil | `http://192.168.88.110:8100/api/v1` (faqat lokal tarmoq, internetga ochilmagan) |
| Tekshirish | `curl http://192.168.88.110:8100/api/v1/health` |
| Ssenariylar | `sud-ijara-davogar` (talaba — da'vogar vakili), `sud-ijara-javobgar` (talaba — javobgar vakili) |
| Ssenariylar ro'yxati | `GET /api/v1/scenarios` (qo'shimcha endpoint, spec'da yo'q) |
| NPC | Sudya (`npcId: "sudya"`). Raqib advokat va kotib ham `npc` turn sifatida keladi, matn boshida `Da'vogar vakili:` / `Javobgar vakili:` / `Kotib:` bo'ladi |
| Dvigatel | `engine: "llm"` — sudya protsedurani kod bo'yicha yuritadi, **raqib advokat gaplarini serverdagi LLM (Qwen3.6) talabaning gapiga moslab yozadi**, Lex.uz RAG moddani tekshiradi va hisobotga manba beradi |
| Tezlik | Protsedura gaplariga javob darhol (<0,1 s). RAG ishlaydigan gaplarda **8–11 s**. Raqib LLM bilan javob beradigan gaplarda **60–90 s** (sessiya davomida 2–3 marta). "Sud o'ylamoqda..." holati va kamida **180 s** kutish vaqti kerak — 2.1-bo'limga qarang |

---

## 2. Ulash (Next.js proxy)

`next.config.js`:

```js
module.exports = {
  async rewrites() {
    return [{ source: "/api/v1/:path*", destination: "http://192.168.88.110:8100/api/v1/:path*" }];
  },
};
```

- `fetch('/api/v1/...', { credentials: 'same-origin' })` o'zgarmaydi. Cookie first-party bo'lib qoladi, CORS kerak emas.
- Namuna (mock) backendni o'chiring yoki env orqali almashtiring.
- Cookie hozir `Secure` siz yuboriladi, chunki sinov `http` da ishlaydi. HTTPS'ga o'tganda serverda `LEXSIM_SECURE_COOKIE=1` qo'yiladi.

### 2.1. Uzoq javoblar (LLM) — muhim

Next.js rewrite proxy'si sukut bo'yicha **30 soniyada** uziladi, LLM javobi esa 60–90 s. Shuning uchun:

```js
module.exports = {
  experimental: { proxyTimeout: 180000 },   // 3 daqiqa
  async rewrites() { /* yuqoridagi kabi */ },
};
```

- Frontend'dagi `fetch` uchun timeout yoki `AbortController` bo'lsa, `/turns` uchun kamida 180 s qiling.
- Spec'dagi 20 s chegarasi (`504 llm_timeout`) LLM bilan sinov paytida qo'llanmaydi. Backend LLM'ni 150 s kutadi, javob kelmasa raqib shablon gapini aytadi. Javob har doim keladi, faqat kech.
- Kutish paytida "Raqib advokat javob tayyorlamoqda..." yozuvi ko'rsatilsa yaxshi. Kiritish maydonini bloklang: bir sessiyada so'rovlar navbat bilan ishlanadi.
- Agar timeout ichida javob kelmay qolsa, xuddi shu `clientTurnId` bilan qayta yuboring — backend takrorlamaydi, birinchi javobni qaytaradi.

---

## 3. Oqim (sud majlisi)

```
POST /sessions {scenarioId:"sud-ijara-javobgar", mode:"tutorial"}   → status "briefing"
POST /sessions/{id}/interactions {action:"start", clientActionId}  → status "in-progress"
POST /sessions/{id}/interactions {action:"sit-at-desk", ...}       → kotib + sudyaning ochilish so'zi, reach-desk ✓
POST /sessions/{id}/turns {text, clientTurnId}  × 8–10 marta       → sudya / raqib replikalari
POST /sessions/{id}/finish {clientActionId}                        → "evaluating" → "report-ready"
GET  /sessions/{id}/report                                         → baholash
```

Sud bosqichlari server tomonda (frontend bilishi shart emas):

1. Vakolatni tasdiqlash
2. Rad qilish
3. Huquqlar
4. Iltimosnomalar
5. Tushuntirishlar
6. Dalillar
7. Penya iltimosnomasi
8. Qo'shimcha materiallar
9. Sud muzokaralari
10. Hal qiluv qarori e'lon qilinadi

Qaror e'lon qilingach, har bir gapga "Sud majlisi yopilgan. Yakunlash tugmasini bosing." deb javob keladi. Shu payt **Yakunlash** tugmasini ko'rsating.

### 3.1. Maslahatchi (yangi endpoint, spec'da yo'q)

`GET /api/v1/sessions/{id}/hint` — joriy bosqichda talaba nima qilishi kerakligini qaytaradi. Faqat `tutorial` rejimida ishlaydi, `assessment` da `409 hints_disabled`.

```json
{"hint": {"stage": "ishtirokchilar", "title": "Vakolatni tasdiqlash",
  "todo": "Sudya vakolatingizni so'radi. Ishonchnomani taqdim eting ...",
  "example": "Hurmatli sud, javobgar vakili sifatida ishtirok etyapman, ...",
  "commonMistake": "«Hurmatli sud» demasdan gapirish ...",
  "sources": [{"title": "Iqtisodiy protsessual kodeksi — ...", "officialUrl": "https://lex.uz/...", "verifiedAt": null}]}}
```

UI taklifi: kiritish maydoni yonida «💡 Nima deyishim kerak?» tugmasi.
- Bosilganda `todo` va `commonMistake` ko'rsatiladi.
- `example` uchun «Namunani qo'yish» tugmasi bo'lsin: matnni kiritish maydoniga qo'yadi, avtomatik yubormaydi.
- Talaba tugmani **bosganda** `GET /hint?open=1` chaqiring. Bu foydalanish hisobotga yoziladi: 3 martadan ko'p bo'lsa, `procedure` darajasi 3 bilan cheklanadi va izohda soni ko'rsatiladi.
- Oldindan yuklab qo'yish yoki bosqich o'zgarganda yangilash uchun `?open=1` siz chaqiring — u hisoblanmaydi.

Rollar va kim nima gapirishi: [data/sud/rollar.md](data/sud/rollar.md).

### 3.2. Ovoz (TTS va STT) — backend orqali

Gradio xizmatlarini (7008, 7003...) brauzerdan to'g'ridan-to'g'ri chaqirmang. Backend endpointlari xuddi shu proxy orqali ishlaydi: cookie, CORS va audio formatini backend hal qiladi, har bir chaqiruv vaqti kuzatuv panelida ko'rinadi. Ikkala endpoint ham `lexsim_owner` cookie talab qiladi, ya'ni avval sessiya ochilgan bo'lishi kerak.

**TTS** — NPC gapini ovozga aylantirish:

```ts
const r = await fetch("/api/v1/voice/tts", {method: "POST", credentials: "same-origin",
  headers: {"Content-Type": "application/json"}, body: JSON.stringify({text: turn.text})});
const url = URL.createObjectURL(await r.blob());          // audio/wav
new Audio(url).play();
```

- `turn.text` ni o'zgartirmasdan yuboring. «Kotib:», «Javobgar vakili:» kabi belgilarni backend o'zi olib tashlaydi.
- Ovoz modeli kuzatuv panelida tanlanadi (MMS yoki Chatterbox). Majburlash uchun `{"text": ..., "engine": "mms"}`.
- Sudya va raqibning shablon gaplari server ishga tushganda oldindan ovozlashtiriladi, ular **darhol** keladi (`X-TTS-Cache: hit`). Yangi gaplar MMS bilan ~2 s, Chatterbox bilan ~70 s.

**STT** — talaba nutqini matnga aylantirish:

```ts
// MediaRecorder bergan blob (webm/ogg) to'g'ridan-to'g'ri yuboriladi — WAV'ga aylantirish shart emas
const r = await fetch("/api/v1/voice/stt", {method: "POST", credentials: "same-origin",
  headers: {"Content-Type": blob.type}, body: blob});
const {text} = await r.json();       // kiritish maydoniga qo'ying, talaba tekshirib yuboradi
```

- Audio 3 MB va 30 s gacha (ortig'i kesiladi). Tavsiya: 10–15 s.
- Standart model — **Kotib**: sinovda NavAI'dan tezroq (37 s / 51 s) va aniqroq chiqdi. `?engine=navai` bilan majburlash mumkin, aks holda paneldagi tanlov ishlatiladi.
- Javob 15–25 s keladi. "Matnga aylantirilmoqda..." holatini ko'rsating, `proxyTimeout` (2.1-bo'lim) yetarli.

**Ovoz xatolari:**

| Status | Kod | Ma'nosi |
|---|---|---|
| 403 | `forbidden` | Sessiya ochilmagan |
| 422 | `voice_failed` | Audio formati yoki matn noto'g'ri |
| 502 | `voice_failed` | Model xato qaytardi |
| 504 | `voice_timeout` | Model javob bermadi |
| 429 | `rate_limited` | TTS 60/daq, STT 20/daq |

Xato bo'lsa, faqat subtitr ko'rsating — ovoz majburiy emas.

**Muhim qoida:** talaba har gapni «Hurmatli sud» deb boshlashi kerak, aks holda sudya ogohlantiradi va ball tushadi. Brifingda bu yozilgan. UI'da ham kiritish maydoni ustida eslatma bo'lsa yaxshi.

### Sinov uchun yaxshi javoblar (javobgar vakili)

1. Hurmatli sud, javobgar vakiliman, ishonchnomamni taqdim etaman.
2. Hurmatli sud, rad bildirmayman.
3. Hurmatli sud, tushunarli.
4. Hurmatli sud, iltimosnomam yo'q.
5. Hurmatli sud, obyekt topshirish dalolatnomasi bilan topshirilmagan, FK 578-modda talab qilgan hujjat yo'q.
6. Hurmatli sud, FK 326-moddaga asosan penyani kamaytirishni so'rab iltimosnoma beraman: penya nomutanosib, mijoz uch oy foydalangan va moliyaviy ahvoli og'ir.
7. Hurmatli sud, qo'shimcha materiallar yo'q.
8. Hurmatli sud! Tekshirilgan shartnoma va hisob-fakturalar asosida FK 326-moddaga ko'ra penyani kamaytirishni so'rayman.

Natija: 100/100 A'lo. Murojaatsiz, qisqa yoki soxta moddali javoblar bilan 20–30 ball, `poor`.

---

## 4. Snapshot'da nima keladi

| Maydon | Sud ssenariysida |
|---|---|
| `scenario` | `public` qismi: title, role, level `"beginner"`, durationMinutes 25, roomId `"dxm-centre-01"`, briefing, npc `{id:"sudya", name:"Sudya", age:52}`, disclaimer |
| `meters` | tutorial: `{patience, trust}` (70/50 dan boshlanadi), assessment: `null` |
| `npc.emotion` | Spec'dagi 7 ta enum. Ogohlantirishlarda `impatient`/`upset`, yaxshi javoblarda `calm`/`reassured` |
| `npc.gesture` | `nod`, `shake-head`, `stand` (sud tark etilganda) |
| `facts` | 4 ta (`factsTotal: 4`), faqat ochilganlari: F1 vakolat, F2 hujjatlar o'qildi, F3 dalolatnoma yo'q, F4 penya masalasi |
| `objectives` | `reach-desk`, `clarify` (2+ fakt ochilganda), `document` (hujjat yuborilsa), `finish` |
| `objects` | `{envelope:"disabled", phone:"disabled"}` |

**roomId:** hozir 3D sahnada faqat `dxm-centre-01` borligi uchun shu qo'yildi. Sud zali xonasi tayyor bo'lsa nomini ayting — [backend/scenarios.json](backend/scenarios.json) da almashtiramiz.

**Hujjat formasi (`/documents`):** forma DXM ssenariysi uchun (pensiya xizmatlari enumi). Sud uchun mos emas. v1 da tavsiya: sud ssenariylarida hujjat panelini yashiring. `document` objective bajarilmasa ham yakunlash ishlaydi. Agar ko'rsatmoqchi bo'lsangiz, `nextStep` maydoniga iltimosnoma matnini yozish mumkin (40+ belgi bo'lsa `document` mezoni kamida 3/4).

---

## 5. Hisobot (`GET /report`)

Spec'dagi `Assessment`:
- `rubricVersion: "court-v1"`.
- 6 ta mezon — `legal` 30, `facts` 15, `procedure` 15, `communication` 15, `ethics` 15, `document` 10 — label'lari sudga moslangan.
- `feedback`: ≤3 strength, ≤3 error, 1 mentor-review ("Haqiqiy sud qanday hal qilgan").
- `sources`: faqat `https://lex.uz/...`, `verifiedAt: null`.
- `betterAnswer` — eng zaif muhim lahza uchun "qanday aytish kerak edi".
- `idealPath` — `done` belgilari bilan.
- `nextScenario` — qarama-qarshi rol.
- `reviewStatus: "needs-mentor"`.

Baholash v1 da **deterministik**: kalit so'zlar, modda raqamlari va qoidalar bo'yicha, LLM ishlatilmaydi. Sinash uchun yetarli, lekin aqlli emas — talaba to'g'ri gapni boshqa so'zlar bilan aytsa, ball past chiqishi mumkin.

---

## 6. Xatolar

Spec bo'yicha:

| Status | Kodlar |
|---|---|
| 400 | `invalid_json` |
| 403 | `forbidden` (boshqa cookie) |
| 404 | `session_not_found`, `scenario_not_found` |
| 409 | `session_not_active`, `dialogue_not_started`, `document_locked`, `report_not_ready` |
| 413 | `payload_too_large` |
| 422 | `validation_failed`, `service_required` |
| 429 | `rate_limited` |
| 500 | `internal` |

`message` o'zbekcha, foydalanuvchiga ko'rsatsa bo'ladi. Bir xil `clientTurnId` bilan qayta yuborilsa, birinchi javobning aynan o'zi qaytadi (idempotent). `sequence` uzluksiz o'sadi. `GET /sessions/{id}/events?after=N` ishlaydi.

**`504 llm_timeout` hozir chiqmaydi:** RAG 15 s da javob bermasa, sudya baribir protsedura bo'yicha davom etadi.

---

## 7. Sinab ko'rish

```bash
# Serverni tekshirish
curl http://192.168.88.110:8100/api/v1/health

# To'liq oqim, ikkala rol (Python 3, kutubxona kerak emas)
python3 tools/backend_sinov.py
python3 tools/backend_sinov.py http://192.168.88.110:8100 sud-ijara-javobgar
```

Skript ([tools/backend_sinov.py](tools/backend_sinov.py)) har bir gapni, sudya javobini, vaqtni va oxirida ballarni chiqaradi. 403, idempotentlik va sequence'ni ham tekshiradi.

**Zod bilan mos kelmasa:** frontend javobni rad etsa, qaysi maydon va qaysi xato ekanini yuboring (Zod xabari + endpoint). Eng ehtimolli joylar:
- `scenario.level` qiymati (`"beginner"`);
- `roomId`;
- `turn.emotion` (faqat npc turn'larda bor);
- report'dagi `appeal: null`.

Ular [backend/scenarios.json](backend/scenarios.json) yoki serverda tez tuzatiladi.

---

## 8. v1 cheklovlari (bilib qo'ying)

- **Bitta ish, ikkita rol.** Sudya gaplari shablon. Ssenariy erkin suhbat emas, chiziqli: har gapdan keyin keyingi bosqichga o'tadi.
- **LLM faqat raqib advokat uchun.** U talaba gapiga javob qaytaradi: e'tiroz, penya iltimosnomasiga munosabat, yakuniy nutq. LLM javobi tekshiriladi: lotin yozuvi, yangi raqam yoki modda yo'qligi, faktni inkor etmasligi, qarorni oshkor qilmasligi. O'tmasa, shablon gap aytiladi. Serverdagi Qwen sekin (bir javob ~60 s). Kuchliroq model ulansa, sudya ham jonli bo'ladi, kontrakt o'zgarmaydi.
- **Baholash LLM'siz.** Ball kalit so'z va qoidalar bo'yicha hisoblanadi.
- **Ovoz.** 3.2-bo'lim. Hozir jonli ishlaydigan bitta tez ovoz bor (MMS). Kotib, sudya va raqibni turn boshidagi prefiks bo'yicha ajrating va brauzerda har biriga turli tezlik bering (`audio.playbackRate`).
- **Bir vaqtda ko'p foydalanuvchi.** RAG va LLM so'rovlari navbat bilan ishlanadi. LLM bilan bir vaqtda **1–2 kishi** sinasin. Ko'proq bo'lsa, javob bir necha daqiqaga cho'ziladi yoki shablon gap chiqadi.
- **Saqlash.** Sessiyalar serverda SQLite faylida saqlanadi. Xizmat qayta ishga tushsa ham yo'qolmaydi.

---

## 9. Server tomoni (administrator uchun)

| Xizmat | Port | Fayl |
|---|---|---|
| `lexsim-backend` | 0.0.0.0:8100 | `~/lexsim/backend/lexsim_server.py`, `scenarios.json`, `sessions.db` |
| `lexsim-rag` | 127.0.0.1:8090 (faqat ichki) | `~/lexsim/tools/api.py` (bge-m3 + reranker, PostgreSQL) |

| `colibri-qwen36` | 192.168.88.110:8000 | LLM (raqib replikalari). Backend unga `~/.colibri.env` dagi kalit bilan ulanadi |

```bash
systemctl status lexsim-backend lexsim-rag colibri-qwen36
journalctl -u lexsim-backend -f            # "LLM 62000 ms OK: ..." yoki "shablon (sabab)" qatorlari
curl -s http://192.168.88.110:8100/api/v1/health   # "llm": {enabled, calls, ok, fallback, last_ms}
sudo systemctl restart lexsim-backend      # scenarios.json o'zgargach
```

### 9.1. Kuzatuv paneli (tizim egalari uchun)

**Manzil:** `http://192.168.88.110:8100/monitor`. Admin token kerak, uni serverdan oling: `cat ~/lexsim/backend/.admin_token`.

| Panelda | Nima ko'rinadi |
|---|---|
| Vaqt qayerga ketyapti | Umumiy vaqtning necha foizi LLM, RAG, dvigatel va saqlashga ketgani; o'rtacha, p50, p95 va eng uzun |
| Hozir bajarilayotgan | Qaysi so'rov qaysi qismda va necha soniyadan beri kutyapti (jonli) |
| Bosqichlar | Sud bosqichlaridan qaysi biri eng sekin |
| Xizmatlar | RAG, LLM, TTS, STT tirikmi va javob vaqti |
| Jarayonlar | Server CPU va RAM'ini qaysi model yeyapti (jonli) |
| Tavsiyalar | Sekin joy uchun nima bilan almashtirish mumkin |
| Sozlamalar | LLM va RAG'ni o'chirish yoki yoqish, LLM kutish vaqti — darhol qo'llanadi, qayta ishga tushirish shart emas |

Panel har 2 soniyada yangilanadi. Talaba matni ko'rsatilmaydi, faqat vaqtlar.

**Admin API** (`X-Admin-Token` sarlavhasi bilan):
- `GET /api/v1/admin/stats` — statistika;
- `POST /api/v1/admin/settings` — tana `{"llm": true, "rag": true, "llm_timeout": 150}`.

**LLM'ni o'chirish yoki yoqish:** eng osoni — kuzatuv panelidagi kalit. Panelda qilingan sozlama `settings.json` ga yoziladi va `llm.conf` dan ustun turadi. Doimiy o'zgartirish uchun: `/etc/systemd/system/lexsim-backend.service.d/llm.conf` faylida `LEXSIM_LLM=1` ni `0` ga o'zgartiring, keyin `sudo systemctl daemon-reload && sudo systemctl restart lexsim-backend`. O'chiq bo'lsa, hammasi shablon bilan tez ishlaydi va `engine` qiymati `"scripted"` bo'ladi.

Portlarni internetga chiqarmang (Cloudflare yoki ngrok yo'q).
