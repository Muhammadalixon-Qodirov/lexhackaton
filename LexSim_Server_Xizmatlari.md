# LexSim — serverdagi AI xizmatlari (frontend uchun)

**Kimga:** frontend jamoasi.
**Holat:** 2026-11-20 da tekshirilgan. Xizmatlar ishlab turibdi, quyidagi tezliklar o'lchangan.
**Server:** `192.168.88.110` — faqat lokal tarmoqda. Cloudflare tunnellari o'chirilgan, internetdan kirib bo'lmaydi.

> **Yangilanish:** ovozni endi backend orqali chaqiring: `POST /api/v1/voice/tts` va `/api/v1/voice/stt` ([LexSim_Backend_v1_Frontend.md](LexSim_Backend_v1_Frontend.md), 3.2-bo'lim). Bu hujjat Gradio xizmatlarining o'zi haqida — ma'lumot uchun.
>
> Bu xizmatlar **sinov uchun**. Asosiy suhbat (sudya, raqib) keyinroq backend servisi orqali keladi — [LexSim_Backend_Spec.md](LexSim_Backend_Spec.md) kontrakti o'zgarmaydi. Hozir ulardan ovoz va subtitrni sinab ko'rish, sahnani "jonlantirish" uchun foydalaning.

---

## 1. Qisqacha

| Port | Xizmat | Nima qiladi | O'lchangan tezlik | Tavsiya |
|---|---|---|---|---|
| **7008** | TTS — MMS | O'zbekcha matnni ovozga aylantiradi | 4,7 s ovoz **1,8 s** da tayyor | ✅ Jonli ishlatsa bo'ladi |
| 7002 | TTS — Chatterbox (UAzimov) | Tabiiyroq o'zbekcha ovoz | 3,2 s ovoz **70 s** da tayyor | ❌ Jonli emas, faqat oldindan yozib olish uchun |
| 7003 | STT — NavAI (whisper-medium) | O'zbekcha nutqni matnga aylantiradi | 4,7 s ovoz **18 s** da | ⚠️ Aniq, lekin sekin |
| 7009 | STT — Kotib | O'zbekcha nutqni matnga aylantiradi | 4,7 s ovoz **25 s** da | ⚠️ Aniq, lekin sekin |
| 8000 | LLM — Qwen3.6-35B (colibri) | OpenAI uslubidagi chat API | Qisqa promptda birinchi token **30 s** | ❌ Jonli suhbat uchun emas, faqat tajriba |

Sinovda ikkala STT ham gapni to'g'ri tanidi: *"hurmatli sud iltimosnomani qanoatlantirishingizni so'rayman"*.

**Amaliy xulosa:**
- **NPC ovozi:** MMS (7008) bilan har bir `dialogue.npcTurn` matnini ovozga aylantirib, subtitr bilan birga qo'yish mumkin.
- **Talaba ovozi (STT):** hozircha eksperimental. Matn kiritish asosiy bo'lib qolsin, mikrofon — qo'shimcha tugma, "matnga aylantirilmoqda..." holati bilan.

---

## 2. Ovoz xizmatlarini chaqirish (Gradio 6 API)

Barcha ovoz xizmatlari Gradio 6 ilovasi. API sxemasi: `http://192.168.88.110:<port>/gradio_api/info`.

| Port | Endpoint | Kirish | Chiqish |
|---|---|---|---|
| 7008 | `/synth` | `text` (string), `auto_cyr` (bool, `true` — lotinni kirillga o'giradi, model kirillda yaxshiroq gapiradi) | `[audio_fayl, ma'lumot_matni]` |
| 7002 | `/synth` | `text` (string) | `[audio_fayl, ma'lumot_matni]` |
| 7003, 7009 | `/transcribe` | `audio_path` (yuklangan fayl) | `[matn, ma'lumot_matni]` |

### 2.1 Qanday ishlaydi (HTTP)

**TTS (matn → ovoz):**
1. `POST http://192.168.88.110:7008/gradio_api/call/synth` — tana `{"data": ["Matn", true]}` → javob `{"event_id": "..."}`.
2. `GET http://192.168.88.110:7008/gradio_api/call/synth/<event_id>` — SSE oqim. Oxirgi `data:` qatorida `[{"url": ".../gradio_api/file=/tmp/gradio/.../audio.wav", ...}, "ma'lumot"]`.
3. `url` dan WAV faylni olib, ijro etasiz.

**STT (ovoz → matn):**
1. `POST http://192.168.88.110:7003/gradio_api/upload` (multipart, maydon nomi `files`) → `["/tmp/gradio/.../a.wav"]`.
2. `POST .../gradio_api/call/transcribe` — tana `{"data": [{"path": "<1-qadamdagi yo'l>", "meta": {"_type": "gradio.FileData"}}]}` → `event_id`.
3. `GET .../gradio_api/call/transcribe/<event_id>` — oxirgi `data:` qatorida `["tanilgan matn", "ma'lumot"]`.

**Ehtiyot bo'ling:** ma'lumot matnida yangi qator belgisi bor. JSON'ni qattiq rejimda parse qilsangiz xato beradi. Python'da `json.loads(..., strict=False)`, JS'da `JSON.parse` muammosiz ishlaydi.

### 2.2 JavaScript (`@gradio/client`)

```ts
import { Client, handle_file } from "@gradio/client";

// TTS
const tts = await Client.connect("http://192.168.88.110:7008");
const r = await tts.predict("/synth", { text: "Sud majlisi ochiq deb e'lon qilinadi.", auto_cyr: true });
const audioUrl = (r.data as any[])[0].url;   // <audio src={audioUrl}>

// STT
const stt = await Client.connect("http://192.168.88.110:7003");
const s = await stt.predict("/transcribe", { audio_path: handle_file(blob) });
const text = (s.data as any[])[0];
```

**Tavsiya — brauzerdan to'g'ridan-to'g'ri emas, Next.js API route orqali chaqiring** (`/api/voice/tts`, `/api/voice/stt`). Shunda:
- CORS muammosi bo'lmaydi;
- server IP'si brauzerga chiqmaydi;
- keyinroq backend servisiga o'tish oson bo'ladi (LexSim spetsifikatsiyasi, 8-bo'limdagi "Ovoz" bandi).

### 2.3 Audio formati
- **TTS** WAV qaytaradi.
- **STT** uchun WAV yuborgan ma'qul: 16 kHz, mono. Brauzerdagi `MediaRecorder` odatda `webm/ogg` beradi. Serverda ffmpeg bor-yo'qligi tekshirilmagan, shuning uchun yuborishdan oldin WAV'ga aylantiring yoki avval bitta `webm` bilan sinab ko'ring.
- **Uzunlik:** STT sekin bo'lgani uchun talaba replikasini 10–15 soniya bilan cheklang.

### 2.4 Python bilan sinov
Tayyor skript — [tools/server_sinov.py](tools/server_sinov.py). Matnni ikkala TTS bilan ovozga aylantiradi, keyin ikkala STT bilan qayta matnga aylantiradi va har bir qadamning vaqtini chiqaradi:

```bash
python3 tools/server_sinov.py 192.168.88.110
```

---

## 3. LLM (Qwen3.6, port 8000) — faqat tajriba uchun

OpenAI uslubidagi API:

```
POST http://192.168.88.110:8000/v1/chat/completions
Authorization: Bearer <COLI_API_KEY>
Content-Type: application/json

{"model": "qwen3.6-colibri", "stream": true, "max_tokens": 150,
 "messages": [{"role": "system", "content": "Sen iqtisodiy sud sudyasisan..."},
              {"role": "user", "content": "..."}]}
```

- **API kalitini** server administratoridan oling (serverdagi `~/.colibri.env`). Kalit **faqat server tomonda** saqlansin — brauzer kodiga yozilmasin.
- **O'lchangan natija:** qisqa promptda birinchi token 30 s, RAG bilan (~2100 token) 163 s, keyin ~7 token/s. Javob sifati ham past: rolni bajarmadi, o'zbekchasida xatolar bor.
- **Xulosa:** sahna va UI'ni sinash uchun ishlatsa bo'ladi. Haqiqiy sudya va raqib rollari keyinroq backend servisi orqali kuchli model bilan keladi. Hozircha namuna backend'dagi skriptli personaj qolsin.

---

## 4. Sahnaga qanday ulash (taklif)

| Qadam | Nima | Xizmat |
|---|---|---|
| 1 | `dialogue.npcTurn` keldi → subtitr ko'rsatiladi | — |
| 2 | Shu matn ovozga aylantiriladi va og'iz animatsiyasi audio uzunligiga moslanadi | TTS 7008 |
| 3 | Talaba mikrofonni bosib gapiradi → matnga aylantiriladi → tasdiqlash uchun kiritish maydoniga qo'yiladi → `POST /turns` | STT 7003 (eksperimental) |

**Rollarga ovoz:** hozir jonli ishlaydigan bitta tez ovoz bor (MMS). Sudya va raqib bir xil eshitilmasligi uchun:
- tezlik yoki balandlikni brauzerda o'zgartiring (`playbackRate`, WebAudio);
- yoki doimiy iboralarni ("Sud majlisi ochiq deb e'lon qilinadi" va boshqa shablonlar) Chatterbox bilan **oldindan** yozib, fayl sifatida saqlang — 70 s/ibora bo'lsa ham bir marta ishlanadi.

---

## 5. Qoidalar

- **Portlarni internetga chiqarmang** (Cloudflare, ngrok va boshqalar). Xizmatlarda parol yo'q.
- `ai_demo/bin/launch_one.sh` skripti ilova bilan birga Cloudflare tunnelini ham ochadi — uni ishlatmang. Xizmatlar systemd orqali boshqariladi.
- **Server yuklanishi:** Chatterbox va STT protsessorni ko'p yeydi. Bir vaqtda ko'p so'rov yubormang. Sinovda navbat bilan chaqiring.
- **Muammo bo'lsa:** server administratoriga xizmat nomini ayting (`aidemo-stt`, `aidemo-mms`, `aidemo-kotib`, `aidemo-uaz`, `colibri-qwen36`).
