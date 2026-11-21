# LexSim — Backend spetsifikatsiyasi (v1)

> **Kimga:** backend / AI dasturchi.
> **Kimdan:** frontend (3D) jamoasi.
> **Sana:** 2026-11-20 · **Protokol versiyasi:** `1`
> **Holat:** frontend tayyor va shu kontrakt bo‘yicha ishlaydi. Hozircha unga Next.js ichidagi **namuna backend** javob beradi (qoidaga asoslangan, LLM yo‘q). Vazifangiz — xuddi shu kontraktni haqiqiy servis sifatida qurish: LLM personaj, AI-ekspert, Lex.uz RAG, ma’lumotlar bazasi.

---

## 0. Qisqacha

- Frontend faqat **`/api/v1/*`** ga murojaat qiladi va har bir javobni Zod sxemasi bilan tekshiradi. Sxemaga mos kelmagan javob UI’da xato sifatida ko‘rsatiladi va sahnaga yetib bormaydi.
- **Server hamma narsani hal qiladi:** yashirin faktlar, sabr/ishonch, ball, manbalar. Frontend faqat ko‘rsatadi.
- Barcha kontrakt bitta faylda: `lexsim-web/src/contracts/index.ts` (Zod). Pydantic modellarni shundan yozing yoki JSON Schema generatsiya qiling.
- Ishlaydigan namuna (executable spec): `lexsim-web/src/server/` — ssenariy, intent, personaj, sessiya FSM, baholovchi. Xatti-harakatda ikkilansangiz, shu kod va uning testlari (`npm test`) javob beradi.

### Kim nima qiladi

| Frontend (biz) | Backend (siz) |
|---|---|
| 3D sahna, kamera, fizika, animatsiya | Sessiya holati va ssenariy dvigateli |
| Suhbat oynasi, hujjat formasi, hisobot sahifasi | **Personaj agenti (LLM)** |
| Emotion/gesture’ni aktyorlikka aylantirish | **Intent klassifikatori** (qaysi savol berildi) |
| Ovoz effektlari (protsedural) | **AI-ekspert / baholovchi** |
| 2D fallback | **Lex.uz bilim bazasi (RAG)** |
| | Ssenariylar banki, progress, auth, saqlash |
| | Xavfsizlik, rate limit, maxfiylik |

---

## 1. Ulanish

### 1.1. Manzil va proxy

Frontend so‘rovlarni **nisbiy yo‘lga** yuboradi: `fetch('/api/v1/...', { credentials: 'same-origin' })`.

Tavsiya: servisingiz alohida domen/portda ishlaydi, Next.js esa `/api/v1/:path*` ni unga **rewrite (proxy)** qiladi. Shunda cookie first-party bo‘lib qoladi va CORS kerak bo‘lmaydi. Bizga servis manzilini ayting — rewrite’ni biz qo‘shamiz va namuna backendni o‘chiramiz.

Agar proxy imkonsiz bo‘lsa: CORS `Access-Control-Allow-Credentials: true`, aniq origin (wildcard emas), cookie `SameSite=None; Secure`. Bu holatda frontendda ham `credentials: 'include'` ga o‘zgartiramiz — oldindan kelishib oling.

### 1.2. Sessiya egasi (hozirgi auth)

Hozir login yo‘q. Egalik **HttpOnly cookie** bilan:

- Cookie nomi: `lexsim_owner`
- `POST /v1/sessions` da cookie bo‘lmasa yarating: tasodifiy ≥ 24 bayt (base64url), `HttpOnly`, `SameSite=Lax`, prod’da `Secure`, `Path=/`, `Max-Age=30 kun`.
- Har bir `/sessions/{id}/*` so‘rovida sessiyaning `owner_token` i cookie bilan **constant-time** solishtiriladi. Mos kelmasa `403 forbidden`.

Keyinchalik haqiqiy auth (talaba/o‘qituvchi/admin) qo‘shilganda shu tekshiruv `user_id` egaligi bilan almashadi. Frontend kodida hech narsa o‘zgarmaydi, chunki u cookie’ni o‘qimaydi.

---

## 2. Umumiy qoidalar

### 2.1. Format

- So‘rov va javob: `application/json`, UTF-8.
- Barcha javoblarda `Cache-Control: no-store`.
- So‘rov tanasi maksimal **16 KB** (`413 payload_too_large`).
- Vaqt: ISO 8601 UTC string (`2026-11-20T09:24:12.000Z`).

### 2.2. Xato konverti

Har bir xato **aynan shu shaklda**:

```json
{ "error": { "code": "session_not_active", "message": "Sessiya faol emas" } }
```

> ⚠️ `message` **foydalanuvchiga to‘g‘ridan-to‘g‘ri ko‘rsatiladi** (toast). Shuning uchun u o‘zbek tilida, tushunarli va texnik tafsilotsiz bo‘lishi kerak. Stack trace, SQL yoki ichki ma’lumot hech qachon chiqmasin.

| HTTP | `code` | Qachon |
|---|---|---|
| 400 | `invalid_json` | Tana JSON emas |
| 403 | `forbidden` | Sessiya boshqa egaga tegishli |
| 404 | `scenario_not_found` | Bunday ssenariy yo‘q |
| 404 | `session_not_found` | Sessiya yo‘q yoki muddati o‘tgan |
| 409 | `session_not_active` | Status `in-progress` emas |
| 409 | `dialogue_not_started` | Suhbat boshlanmasdan `turns` yuborildi |
| 409 | `document_locked` | Hujjat allaqachon yuborilgan |
| 409 | `report_not_ready` | Hisobot hali yo‘q |
| 413 | `payload_too_large` | Tana > 16 KB |
| 422 | `validation_failed` | Sxemaga mos emas |
| 422 | `service_required` | `submit: true`, lekin `service: null` |
| 429 | `rate_limited` | Limitdan oshdi |
| 500 | `internal` | Kutilmagan xato (`message`: "Ichki xatolik") |
| 504 | `llm_timeout` | **Yangi.** LLM javob bermadi (§2.5) |

### 2.3. Idempotentlik — majburiy

Har bir **o‘zgartiruvchi** so‘rovda klient generatsiya qilgan ID bor: `clientTurnId` yoki `clientActionId` (8–64 belgi, odatda UUID).

- Bir xil ID bilan qayta kelgan so‘rov **birinchi javobning aynan o‘zini** qaytaradi. Hech narsa qayta bajarilmaydi, yangi event chiqmaydi.
- Frontend tarmoq uzilsa **bir marta avtomatik qayta yuboradi**, aynan shu ID bilan. Demak birinchi so‘rov hali LLM’da ishlayotgan paytda ikkinchisi kelishi mumkin. Bu holatda ikkinchisi **birinchisi tugashini kutib, o‘sha natijani** qaytarishi kerak (in-flight dedup). Ikkita LLM chaqiruv yoki ikkita replika — xato.
- Saqlash: `(session_id, client_id) → response` jadvali, sessiya umri davomida.

### 2.4. Ketma-ketlik

- Bir sessiya ichidagi mutatsiyalar **ketma-ket** bajariladi (sessiya darajasida lock: Postgres advisory lock, `SELECT … FOR UPDATE` yoki navbat).
- Har bir holat o‘zgarishi — event. Event `sequence` sessiya ichida **monoton o‘suvchi, bo‘shliqsiz** butun son (1, 2, 3 …).
- `snapshot.sequence` = shu paytgacha chiqarilgan oxirgi event raqami.
- Frontend `snapshot.sequence` joriydan kichik bo‘lgan javobni **eskirgan deb tashlab yuboradi**.

### 2.5. Kechikish (LLM uchun muhim)

Frontend replika yuborgach javobni kutadi va "Rustam aka o‘ylamoqda…" ko‘rsatadi.

| Ko‘rsatkich | Maqsad |
|---|---|
| `POST /turns` p50 | ≤ 2.5 s |
| `POST /turns` p95 | ≤ 6 s |
| Qattiq chegara | 20 s → `504 llm_timeout`, holat o‘zgarmaydi |
| `POST /finish` (baholash) | ≤ 30 s; undan uzoq bo‘lsa §4.7 dagi asinxron variant |

`504` da sessiya holati **o‘zgarmasligi** kerak (user replikasi ham yozilmaydi), shunda talaba xuddi shu matnni qayta yubora oladi. Frontend timeout va "qayta urinish" tugmasini o‘z tomonida qo‘shadi.

### 2.6. Rate limit (hozirgi qiymatlar, o‘zgartirish mumkin)

| Endpoint | Kalit | Limit / daqiqa |
|---|---|---|
| `POST /sessions` | egasi | 20 |
| `POST /turns` | sessiya | 30 |
| `POST /interactions` | sessiya | 60 |
| `POST /documents` | sessiya | 60 |
| `POST /appeal` | sessiya | 5 |

---

## 3. Endpointlar

Baza: `/api/v1`. Mutatsiya endpointlari **har doim** bir xil shakldagi javob qaytaradi:

```ts
MutationResponse = { events: SimEvent[]; snapshot: Snapshot }
```

`events` — **shu so‘rov natijasida** chiqqan eventlar (tartib bilan). `snapshot` — undan keyingi to‘liq holat.

| Method | Yo‘l | Tana | Javob |
|---|---|---|---|
| POST | `/sessions` | `{ scenarioId, mode?, seed? }` | `{ snapshot }` |
| GET | `/sessions/{id}` | — | `{ snapshot }` |
| POST | `/sessions/{id}/interactions` | `{ clientActionId, action }` | `MutationResponse` |
| POST | `/sessions/{id}/turns` | `{ clientTurnId, text }` | `MutationResponse` |
| POST | `/sessions/{id}/documents` | `{ clientActionId, draft, submit }` | `MutationResponse` |
| POST | `/sessions/{id}/finish` | `{ clientActionId }` | `MutationResponse` |
| GET | `/sessions/{id}/events?after=N` | — | `{ events, snapshot }` |
| GET | `/sessions/{id}/report` | — | `{ report }` |
| POST | `/sessions/{id}/appeal` | `{ reason }` | `{ report }` |

### 3.1. `POST /sessions`

```json
{ "scenarioId": "dxm-yoqolgan-staj", "mode": "tutorial" }
```

- `mode`: `"tutorial"` (sabr/ishonch ko‘rinadi) yoki `"assessment"` (yashirin). Default `tutorial`.
- `seed` (ixtiyoriy, int): ssenariy tasodifiyligini qayta tiklash uchun. Berilmasa o‘zingiz tanlang va **saqlang** (o‘qituvchi replay uchun kerak).
- Yangi sessiya `status: "briefing"`, `turns: []`, `sequence: 0` bilan qaytadi.

### 3.2. `POST /sessions/{id}/interactions`

`action` qiymatlari:

| `action` | Frontend qachon yuboradi | Server nima qiladi |
|---|---|---|
| `start` | Brifingdagi "Ishni boshlash" | `briefing → in-progress`, `startedAt` yoziladi, `session.status` event. Status allaqachon boshqa bo‘lsa — hech narsa qilmaydi (xato emas). |
| `sit-at-desk` | Talaba stolga o‘tirganda (3D’da `E`, 2D’da avtomatik) | `reach-desk` objective bajariladi. **Agar `turns` bo‘sh bo‘lsa** — fuqaroning **ochilish replikasi** NPC turn sifatida qo‘shiladi. Qayta chaqirilsa ochilish replikasi takrorlanmaydi. |
| `enter-room`, `open-terminal` | Hozir yuborilmaydi (zaxira) | Qabul qiling, `in-progress` bo‘lsa bo‘sh `events` bilan javob bering. |

> Frontend `turns.length > 0` bo‘lsa "suhbat boshlangan" deb hisoblaydi va sahifa yangilanganda talabani to‘g‘ridan-to‘g‘ri stolga o‘tqazadi. Shuning uchun ochilish replikasi faqat `sit-at-desk` da qo‘shilishi muhim.

### 3.3. `POST /sessions/{id}/turns` — asosiy endpoint

```json
{ "clientTurnId": "4f1c…", "text": "Qaysi yillarda va qayerda ishlagansiz?" }
```

- `text`: trim qilingan, 1–800 belgi.
- Shartlar: `status = in-progress` (aks holda `409 session_not_active`), `turns` bo‘sh emas (aks holda `409 dialogue_not_started`).
- Bitta so‘rovda chiqadigan eventlarning odatiy tartibi:

```
dialogue.userTurn            ← talaba replikasi (server tasdiqlagan)
[scene.objectState …]        ← masalan, telefon / konvert
dialogue.npcTurn             ← fuqaro javobi (+ revealedFactIds)
npc.emotion                  ← har bir NPC replikasidan keyin
npc.gesture                  ← gesture "none" bo‘lmasa
[objective.updated]          ← masalan "clarify"
[dialogue.npcTurn …]         ← qo‘shimcha: pora taklifi yoki navbat bosimi (system)
[session.status evaluating → report-ready]   ← sabr 0 yoki pora qabul qilinsa
```

Bitta turn’da fuqaro **bir nechta** replika aytishi mumkin (javob + pora taklifi). Frontend hammasini ketma-ket ko‘rsatadi.

Javob namunasi:

```json
{
  "events": [
    { "eventId": "evt_…", "sequence": 5, "sessionId": "sim_…", "timestamp": "…",
      "type": "dialogue.userTurn",
      "payload": { "turn": { "id": "t_3", "index": 2, "speaker": "user", "text": "Qaysi yillarda va qayerda ishlagansiz?", "at": "…" } } },
    { "eventId": "evt_…", "sequence": 6, "sessionId": "sim_…", "timestamp": "…",
      "type": "dialogue.npcTurn",
      "payload": { "turn": { "id": "t_4", "index": 3, "speaker": "npc", "text": "To‘qson birinchi yildan to‘qson sakkizgacha kolxozda ishlaganman…", "at": "…", "emotion": "calm" },
                   "revealedFactIds": ["work-period-1991-1998"] } },
    { "eventId": "evt_…", "sequence": 7, "sessionId": "sim_…", "timestamp": "…",
      "type": "npc.emotion", "payload": { "npcId": "rustam-aka", "emotion": "calm", "intensity": 0.5 } },
    { "eventId": "evt_…", "sequence": 8, "sessionId": "sim_…", "timestamp": "…",
      "type": "npc.gesture", "payload": { "npcId": "rustam-aka", "clip": "sigh" } }
  ],
  "snapshot": { "...": "§5.1" }
}
```

### 3.4. `POST /sessions/{id}/documents`

```json
{ "clientActionId": "…", "submit": false, "draft": { "service": "archive-reference", "applicantName": "…", "periodFrom": "1991", "periodTo": "1998", "employer": "…", "evidence": ["passport"], "nextStep": "…", "notify": "sms" } }
```

- `submit: false` — **qoralama**. Frontend forma yopilganda avtomatik yuboradi; yozilgan matn yo‘qolmasligi kerak.
- `submit: true` — yakuniy. `service` bo‘sh bo‘lsa `422 service_required`. Muvaffaqiyatda `documentSubmitted = true`, `document` objective bajariladi; shundan keyin har qanday yozish `409 document_locked`.

### 3.5. `POST /sessions/{id}/finish`

Talaba "Qabulni yakunlash" ni tasdiqlaganda. `in-progress` bo‘lsa: baholash → `session.status: evaluating` → `finish` objective → `session.status: report-ready`. Allaqachon `report-ready` bo‘lsa — bo‘sh `events` bilan joriy holat (xato emas).

Frontend `report-ready` ni ko‘rgach yakun oynasini (`snapshot.outcome`) ochadi, keyin `/report` ga o‘tadi.

### 3.6. `GET /sessions/{id}/events?after=N`

Uzilgandan keyin tiklash uchun: `sequence > N` bo‘lgan eventlar va joriy snapshot. Hozir frontend sahifa ochilganda `GET /sessions/{id}` dan foydalanadi. Bu endpoint ham ishlab tursin — SSE/WebSocket qo‘shilganda kerak bo‘ladi.

### 3.7. `GET /report` va `POST /appeal`

- `report` — `Assessment` (§5.4). `report-ready` gacha `409 report_not_ready`.
- `appeal`: `{ "reason": "10–1500 belgi" }` → `report.appeal = { at, reason }`, `reviewStatus = "needs-mentor"`, o‘qituvchi navbatiga tushadi. Yangilangan `report` qaytadi.

---

## 4. Ssenariy dvigateli va AI

### 4.1. Arxitektura: LLM nimani hal qiladi, nimani hal qilmaydi

```
talaba matni
   │
   ▼
┌─────────────────────┐   yopiq teglar to‘plami (§4.3)
│ Intent klassifikator│──────────────────────────────┐
│  (LLM, structured)  │                              │
└─────────────────────┘                              ▼
                                       ┌──────────────────────────────┐
                                       │ Ssenariy dvigateli           │
                                       │ DETERMINISTIK KOD, LLM EMAS  │
                                       │ • fakt ochish qoidalari      │
                                       │ • sabr / ishonch             │
                                       │ • pora, navbat bosimi        │
                                       │ • objectives, yakun          │
                                       │ • "beat" tanlash             │
                                       └──────────────┬───────────────┘
                                                      │ cheklangan kontekst
                                                      ▼
                                       ┌──────────────────────────────┐
                                       │ Personaj agenti (LLM)        │
                                       │ faqat replika matni +        │
                                       │ gesture (enum ichidan)       │
                                       └──────────────────────────────┘
```

**Asosiy qoida:** LLM hech qachon qaysi fakt ochilishini, sabr/ishonchni yoki ballni o‘zi hal qilmaydi. Bu loyiha konsepsiyasidagi "personaj javobni aytib qo‘ymasligi" va "baholashni tekshirsa bo‘ladigan qilish" talabining texnik ifodasi.

Namunada ikkala LLM o‘rnida qoidalar turibdi:
- `src/server/engine/intent.ts` → `RuleIntentClassifier` (regex, lotin + kirill)
- `src/server/engine/character.ts` → `ScriptedCharacterAgent` (tayyor replikalar)

Interfeyslar (`IntentClassifier`, `CharacterAgent`) aynan siz almashtiradigan joylar.

### 4.2. Ssenariy ma’lumoti

Ssenariy shabloni loyiha hujjatidagi YAML (`LexSim_Loyiha.md` §6.1). Namunadagi to‘liq misol: `src/server/scenarios/dxm-yoqolgan-staj.ts`. Har bir ssenariyda kerakli maydonlar:

| Maydon | Ma’nosi | Klientga boradimi |
|---|---|---|
| `public` (id, title, role, level, durationMinutes, roomId, briefing, npc{id,name,age}, disclaimer) | Brifing va UI | **Ha** (`snapshot.scenario`) |
| `initial.patience / trust` | 0–100 | Faqat tutorial’da raqam sifatida |
| `openingLine` | Ochilish replikasi | Ha, `sit-at-desk` da |
| `facts[]`: id, summary, unlockedBy (tag), minTrust, lines[], gesture | Yashirin faktlar | **Faqat ochilgandan keyin**, faqat `summary` |
| `correctService`, `expectedEvidence[]` | Hujjat bahosi | **Yo‘q** |
| `bribe` (earliestTurn, latestTurn, line, pushLine) | Etik sinov | Faqat sodir bo‘lganda replika sifatida |
| `queuePressure` (probability, turn, line) | Murakkablashtiruvchi | Faqat sodir bo‘lganda (`system` turn) |
| `idealPath[]` | Baholash | **Yo‘q** (faqat hisobotda) |
| `sources` | Huquqiy manbalar | Faqat hisobotda |
| `mentorApproved` | Mentor tasdig‘i | — |

`roomId` frontendda qaysi 3D xona yuklanishini belgilaydi. Hozir faqat `dxm-centre-01` bor; yangi xona kerak bo‘lsa bizga ayting.

> ⚠️ Yashirin faktlar matni (masalan "1991–1998") ochilmaguncha `snapshot` ning **hech bir joyida** bo‘lmasligi kerak. Namunadagi test aynan shuni tekshiradi.

### 4.3. Intent klassifikatori (LLM №1)

Vazifasi: talaba replikasini **yopiq teglar to‘plamiga** ajratish. Bitta replikada bir nechta teg bo‘lishi mumkin.

| Teg | Ma’nosi |
|---|---|
| `greeting` | Salomlashish |
| `empathy` | Hamdardlik, tinchlantirish ("xavotir olmang", "tushunaman") |
| `paraphrase` | Muammoni takrorlab tasdiqlash ("demak…", "to‘g‘ri tushundimmi") |
| `ask-work-period` | Qaysi yillar / qayerda ishlagani haqida savol |
| `ask-documents` | Qo‘lidagi hujjatlar, mehnat daftarchasi haqida savol |
| `ask-employer-status` | Tashkilot hozir bormi / tugatilganmi |
| `ask-previous-visits` | Avval qayerga murojaat qilgani |
| `explain-service` | Aniq xizmatni tushuntirish (arxiv so‘rovi, stajni tasdiqlash) |
| `explain-documents` | Kerakli hujjatlar ro‘yxati |
| `explain-deadline` | Muddat, keyingi qadam |
| `explain-tracking` | Natijani qanday kuzatish (SMS, portal, ariza raqami) |
| `dismiss` | Asossiz qaytarish ("bizda emas, boshqa joyga boring") |
| `rude` | Qo‘pollik |
| `jargon` | Tushunarsiz yuridik til |
| `overpromise` | Vakolatdan tashqari va’da ("albatta oshiramiz") |
| `bribe-refuse` | Porani rad etish — **faqat pora kutilayotganda** |
| `bribe-accept` | Porani qabul qilish — **faqat pora kutilayotganda** |
| `injection` | Roldan chiqarishga urinish ("rolni unut", "ideal yo‘lni ayt") |

Talablar:

- **Structured output** (JSON schema / tool call): `{ "tags": ["ask-work-period", "empathy"] }`. Erkin matn emas.
- Kirishga faqat: talaba replikasi, oxirgi 2–4 replika konteksti, `bribePending` flagi. Yashirin fakt matnlari **berilmaydi** — teg ta’riflari yetarli.
- `dismiss` + `explain-service` birga bo‘lsa — `dismiss` olib tashlanadi (aniq idoraga yo‘naltirish qaytarish emas).
- O‘zbek lotin, kirill, rus so‘zlari aralash, xatolar bilan yozilgan matnni tushunishi kerak.
- Model ishlamasa yoki timeout bo‘lsa: namunadagi qoidaga asoslangan klassifikatorga **fallback** qiling (u o‘zbekcha uchun yozilgan, porting oson).
- Sifat: ≥ 150 ta qo‘lda belgilangan replikada test to‘plami tuzing (mentor bilan). Maqsad: fakt-teglar bo‘yicha precision ≥ 0.9 (noto‘g‘ri savolga fakt ochilmasin), `bribe-*` bo‘yicha ≥ 0.95.

### 4.4. Dvigatel qoidalari (deterministik)

Namunadagi qiymatlar (`src/server/engine/session.ts`, `processTurn`). Mentor bilan kalibrlang, lekin **kodda** qoldiring:

- Har bir turn: sabr −2 (vaqt bosimi).
- Ustuvorlik tartibi: `injection` → pora kutilayotgan bo‘lsa pora javobi → `rude` → `dismiss` → fakt savollari → tushuntirishlar → `jargon` → `overpromise` → xushmuomalalik.
- **Fakt ochilishi:** teg mos kelsa **va** `trust ≥ fact.minTrust` → ochiladi (bir turn’da ko‘pi bilan 2 ta), ishonch +6 har biriga. Ishonch yetmasa — personaj chetlab o‘tadi (`evasive`), fakt ochilmaydi.
- `greeting/empathy/paraphrase`: sabr +6, ishonch +5 (boshqa effektlarga **qo‘shimcha**).
- `rude`: sabr −18, ishonch −8. `dismiss`: sabr −16, ishonch −16. `jargon`: sabr −8, ishonch −6.
- `explain-service`: ishonch +10, sabr +5. `explain-deadline`: ishonch +12. Boshqa tushuntirishlar: +8.
- Qiymatlar 0–100 oralig‘ida qisiladi.
- **Pora:** seed bo‘yicha `earliestTurn..latestTurn` oralig‘idagi turn’da, talaba qo‘pol/rad etuvchi bo‘lmagan paytda taklif qilinadi → `envelope` obyekti `active`. Holatlar: `offered → refused | accepted | pushed → ambiguous`. Qabul qilinsa sessiya **darhol** `report-ready` bilan tugaydi, ball 0.
- **Navbat bosimi:** seed bo‘yicha (70%), 4-turn’dan keyin bir marta `system` turn, sabr −5.
- **Sabr 0:** fuqaro "ketish" replikasini aytadi (gesture `stand`) → sessiya tugaydi, natija `poor`.
- **Emotion:** sabr < 25 → `upset`; < 45 → `impatient`; ishonch ≥ 72 → `reassured`; ≥ 55 → `calm`; aks holda `neutral`. Ayrim beat’lar vaqtincha `confused` / `uncertain` beradi.
- **Objectives** (id’lar frontendda belgilangan, o‘zgartirmang): `reach-desk` (o‘tirganda), `clarify` (≥ 2 fakt ochilganda), `document` (hujjat yuborilganda), `finish` (yakunda).

Barcha tasodifiylik **seed’langan PRNG** dan bo‘lsin — sessiyani qayta tiklash va o‘qituvchi replay uchun.

### 4.5. Personaj agenti (LLM №2)

Dvigatel "beat" ni tanlaydi, LLM esa shu beat’ni o‘z so‘zlari bilan aytadi.

Beat ro‘yxati: `reveal`, `evasive`, `already-told`, `warm`, `service-explained`, `steps-explained`, `jargon`, `overpromise`, `rude`, `dismissed`, `injection`, `bribe-refused`, `bribe-accepted`, `bribe-dropped`, `leaving`, `fallback`. Pora taklifi va `pushLine` — ssenariydagi tayyor matn (LLM emas).

**LLMga beriladigan kontekst (faqat shu):**

- Persona kartochkasi: ism, yosh, xarakter, nutq uslubi ("oddiy so‘zlashuv, ba’zan rus so‘zlari").
- Ochiq shikoyat (`openingLine` ma’nosi).
- **Allaqachon ochilgan** faktlar + shu turn’da ochilganlar (ularni aytishi **shart**).
- Joriy beat, emotion, sabr/ishonch (so‘z bilan: "juda asabiy", "ishona boshladi").
- Oxirgi 6–8 replika.

**Berilmaydi:** yopiq faktlar, ideal yo‘l, rubrika, ball, to‘g‘ri xizmat nomi, huquqiy javob.

**Chiqish (structured):**

```json
{ "text": "…", "gesture": "sigh" }
```

- `text`: o‘zbek tili, 1–3 gap, ≤ 350 belgi (subtitr va og‘iz animatsiyasi uzunlikka bog‘liq).
- `gesture`: faqat `GestureSchema` enum (§5.3). Boshqa qiymat kelsa → `none`.

**Qo‘riqchi (guardrail) — LLM javobidan keyin tekshiring:**

- Javobda yopiq fakt mazmuni bo‘lsa (kalit so‘zlar / embedding o‘xshashligi) → rad etib, namunadagi tayyor replikaga tushing.
- Personaj huquqiy maslahat bermaydi, modda keltirmaydi, roldan chiqmaydi, "men AI" demaydi.
- Bo‘sh, juda uzun yoki boshqa tilda javob → tayyor replika.
- Har qanday LLM xatosida sessiya buzilmasligi kerak: `ScriptedCharacterAgent` — doimiy zaxira.

`snapshot.engine` maydoni: LLM javob bergan bo‘lsa `"llm"`, zaxira replika ishlatilgan bo‘lsa `"scripted"`. Frontend `scripted` holatida "Ssenariyli demo personaj" belgisini ko‘rsatadi — demoda halollik uchun muhim.

### 4.6. AI-ekspert / baholovchi (LLM №3 + RAG)

Hozirgi namuna (`src/server/engine/evaluator.ts`) to‘liq deterministik. Uni **asos** sifatida saqlang: ballning katta qismi dvigatel yig‘gan dalillardan (qaysi teg qaysi turn’da, qaysi fakt ochilgan, pora holati, hujjat maydonlari) hisoblanadi. LLM esa:

1. Har bir xato/kuchli tomon uchun izoh va iqtibos tanlaydi.
2. "Qanday aytish kerak edi" ni yozadi.
3. Har bir huquqiy da’vo uchun Lex.uz RAG’dan manba topadi.

Rubrika (100 ball, o‘zgarmas):

| `id` | Nomi | Max |
|---|---|---|
| `legal` | Huquqiy to‘g‘rilik | 30 |
| `facts` | Faktlarni aniqlash | 15 |
| `procedure` | Tartib-taomil | 15 |
| `communication` | Muomala va empatiya | 15 |
| `ethics` | Etika va korrupsiyaga qarshi | 15 |
| `document` | Hujjat sifati | 10 |

Majburiy qoidalar:

- **Pora qabul qilinsa** yoki ataylab noto‘g‘ri yo‘naltirilsa: `scoreTotal = 0`, `zeroedByEthics = true`, `outcome.id = "failed"`.
- **"Manba bo‘lmasa, modda yo‘q":** `articleNumber` va `effectiveAt` faqat RAG manbani topgan **va** mentor tasdiqlagan bo‘lsa to‘ldiriladi. Aks holda faqat hujjat nomi, `verifiedAt: null`. Frontend `verifiedAt: null` ni "mentor tekshirsin" belgisi bilan ko‘rsatadi.
- `officialUrl` — **faqat `https://lex.uz/...` yoki `https://www.lex.uz/...`**. Frontend boshqa hostlarni havola sifatida ko‘rsatmaydi.
- **Ikki mustaqil baholash** (turli seed/temperature yoki turli model). Ball farqi > 10 bo‘lsa → `reviewStatus: "needs-mentor"`.
- `reviewStatus`: mentor tasdiqlamaguncha `"needs-mentor"` (yoki `"auto"`); faqat mentor `"mentor-approved"` qiladi.
- Ball **faqat serverda** hisoblanadi; klientdan kelgan hech qanday ball/fakt qabul qilinmaydi.
- `feedback`: ko‘pi bilan 3 ta `strength`, 3 ta `error`, 1 ta `mentor-review`.
- `supportingTurnIds` / `relatedTurnIds` — mavjud `turns[].id` lar (frontend ularni "N-replika" deb ko‘rsatadi).

### 4.7. Uzoq baholash

Baholash 30 s dan oshsa: `finish` darhol `session.status: evaluating` qaytarsin, `GET /report` esa tayyor bo‘lguncha `409 report_not_ready`. Bu variantni tanlasangiz **oldindan ayting** — frontendga polling va "baholanmoqda" ekranini qo‘shamiz (hozir `finish` javobida `report-ready` kutiladi).

### 4.8. Lex.uz bilim bazasi (RAG)

Loyiha hujjatidagi reja (`LexSim_Loyiha.md` §11.2):

- Hujjatlarning **amaldagi tahriri**, modda (kerak bo‘lsa qism) darajasida bo‘laklash.
- Har bir bo‘lak metadata: hujjat nomi, modda raqami, tahrir sanasi, havola (`lex.uz`), yuklangan sana.
- PostgreSQL + pgvector; o‘zbekcha uchun hybrid qidiruv (BM25 + vektor) tavsiya etiladi.
- 30+ test savolda qidiruv sifatini o‘lchash.
- Tahrir o‘zgarsa qayta indekslash; eski tahrirni o‘chirmasdan `valid_to` bilan belgilash (eski hisobotlarni tushuntirish uchun).
- Topilmasa — "mentor tekshirsin". Hech qachon model xotirasidan modda keltirmaslik.

---

## 5. Ma’lumot sxemalari

Manba: `lexsim-web/src/contracts/index.ts`. Quyida qisqacha.

### 5.1. Snapshot

```ts
Snapshot = {
  protocol: 1;
  sessionId: string;
  sequence: number;                 // oxirgi event raqami
  status: 'briefing' | 'in-progress' | 'evaluating' | 'report-ready' | 'aborted';
  mode: 'tutorial' | 'assessment';
  engine: 'scripted' | 'llm';
  scenario: ScenarioPublic;         // §4.2 "public"
  meters: { patience: number; trust: number } | null;  // assessment’da null
  npc: { emotion: Emotion; intensity: number /*0..1*/ };
  turns: Turn[];
  facts: { id: string; text: string; unlockedAtTurn: number }[];  // faqat ochilganlar
  factsTotal: number;
  objectives: { id: string; label: string; done: boolean }[];
  objects: Record<string, 'active' | 'disabled' | 'open' | 'closed'>;
  document: DocumentDraft;
  documentSubmitted: boolean;
  outcome: { id: 'excellent'|'average'|'poor'|'failed'; title: string; description: string } | null;
  startedAt: string | null;
}

Turn = { id: string; index: number; speaker: 'user' | 'npc' | 'system'; text: string; at: string; emotion?: Emotion }
```

- `turns[].id` sessiya ichida noyob va barqaror (hisobot ularga havola qiladi).
- `speaker: 'system'` — vaziyat tavsifi (navbatdagi odam eshikni taqillatdi). Frontend uni boshqacha ko‘rsatadi va taqillash ovozini chaladi.
- `objects` kalitlari 3D sahnaga bog‘langan: `envelope` (`active` → stolda konvert paydo bo‘ladi), `phone`. Yangi obyekt kerak bo‘lsa — bizga ayting.
- `outcome` — sessiya tugagach to‘ldiriladi.

### 5.2. DocumentDraft

```ts
DocumentDraft = {
  service: 'archive-reference' | 'pension-recalculation' | 'refer-elsewhere' | 'written-complaint' | null;
  applicantName: string;   // ≤ 120
  periodFrom: string;      // ≤ 10
  periodTo: string;        // ≤ 10
  employer: string;        // ≤ 200
  evidence: ('passport' | 'workbook-photos' | 'employer-details' | 'pension-decision' | 'witness-statement')[]; // ≤ 8
  nextStep: string;        // ≤ 1200
  notify: 'sms' | 'written' | 'none';
}
```

Bu enumlar hozir "Yo‘qolgan staj" uchun. Har bir ssenariy o‘z xizmatlar/hujjatlar ro‘yxatiga ega bo‘lishi kerak bo‘lsa — formani ssenariydan dinamik qilib qurish uchun kontraktni birga kengaytiramiz (§8).

### 5.3. Allow-list enumlar

```
Emotion  = neutral | impatient | upset | confused | uncertain | calm | reassured
Gesture  = none | nod | shake-head | sigh | lean-in | check-watch | show-phone
         | offer-envelope | withdraw-envelope | stand
```

Bu ro‘yxatdan tashqari qiymat yuborilsa, frontend butun javobni rad etadi. LLM chiqishini doim shu enumlarga map qiling.

### 5.4. Event turlari

| `type` | `payload` | Frontend nima qiladi |
|---|---|---|
| `dialogue.userTurn` | `{ turn }` | Vaqtinchalik ko‘rsatilgan replikani server tasdiqlagani bilan almashtiradi |
| `dialogue.npcTurn` | `{ turn, revealedFactIds }` | Subtitr yoziladi, og‘iz matn uzunligicha harakatlanadi; `system` bo‘lsa taqillash ovozi |
| `npc.emotion` | `{ npcId, emotion, intensity }` | Yuz/gavda holati (amalda `snapshot.npc` dan o‘qiladi) |
| `npc.gesture` | `{ npcId, clip }` | Bir martalik animatsiya |
| `scene.objectState` | `{ objectId, state }` | 3D obyekt (konvert va h.k.) |
| `objective.updated` | `{ objectiveId, done }` | Vazifalar ro‘yxati + ovozli signal |
| `session.status` | `{ status }` | `report-ready` → yakun oynasi |

Har bir event: `{ eventId, sequence, sessionId, timestamp, type, payload }`. `eventId` global noyob.

### 5.5. Assessment (hisobot)

```ts
Assessment = {
  sessionId; scenarioId; rubricVersion: string;
  scoreTotal: number /*0..100 int*/; zeroedByEthics: boolean;
  outcome: Outcome;
  criteria: { id: CriterionId; label; score; max; explanation; supportingTurnIds: string[] }[]; // 6 ta, §4.6 tartibida
  feedback: { kind: 'strength'|'error'|'mentor-review'; title; message; quote?; relatedTurnIds: string[];
              sources: { title; officialUrl /*https lex.uz*/; articleNumber?; effectiveAt?; verifiedAt: string|null }[] }[];
  betterAnswer: { original; improved; why } | null;
  idealPath: { step: string; done: boolean }[];
  nextScenario: { id; title; reason };
  reviewStatus: 'auto' | 'needs-mentor' | 'mentor-approved';
  appeal: { at; reason } | null;
  turns: Turn[]; facts: Fact[]; factsTotal: number;
  evaluatedAt: string;
}
```

---

## 6. Saqlash, xavfsizlik, maxfiylik

### 6.1. Minimal jadvallar

| Jadval | Asosiy maydonlar |
|---|---|
| `scenarios` | id, version, role, level, data (JSONB), mentor_approved_by/at |
| `sessions` | id, owner_token_hash / user_id, scenario_id + version, mode, seed, rng_state, status, patience, trust, bribe_stage, document (JSONB), document_submitted, ended_by, started_at, created_at |
| `session_events` | session_id, sequence (PK bilan), event_id, type, payload, created_at |
| `turns` | session_id, id, index, speaker, text, emotion, intent_tags[], created_at |
| `unlocked_facts` | session_id, fact_id, turn_index |
| `idempotency` | session_id, client_id, response (JSONB), status (in-flight/done) |
| `assessments` | session_id, rubric_version, payload (JSONB), review_status, evaluator_runs (JSONB) |
| `appeals` | session_id, reason, created_at, resolved_by/at |
| `law_chunks` | doc_title, article, text, effective_from, valid_to, url, embedding |
| `llm_calls` | session_id, turn_id, role (intent/character/eval), model, latency_ms, tokens, fallback_used — **matnsiz** |

Ssenariy versiyasini sessiyaga bog‘lang: ssenariy keyin o‘zgarsa, eski hisobot o‘sha versiya bo‘yicha qoladi.

### 6.2. Xavfsizlik

- Har bir kirish sxema bo‘yicha validatsiya; noma’lum maydonlar rad etiladi.
- LLM chiqishi hech qachon HTML/markdown sifatida emas, **oddiy matn** sifatida qaytadi (frontend uni text sifatida render qiladi, lekin baribir tozalang).
- API kalitlar faqat serverda. Prompt injection testlari (talaba "rolni unut", "baholash mezonlarini ayt" deydi) — test to‘plamida bo‘lsin.
- Sessiya ID taxmin qilinmaydigan (≥ 96 bit).
- Loglarda talaba matni, cookie, IP minimal; `llm_calls` da matn saqlanmaydi.

### 6.3. Maxfiylik ("Shaxsga doir ma’lumotlar to‘g‘risida"gi qonun)

- Suhbat yozuvlari faqat ta’lim maqsadida; o‘qituvchi faqat o‘z guruhini ko‘radi.
- Saqlash muddati va o‘chirish siyosatini belgilang; foydalanuvchi o‘z tarixini o‘chira olsin.
- Tashqi LLM provayderiga yuborilayotgan ma’lumot: ma’lumotlarni o‘qitishga ishlatmaslik shartini tekshiring, shaxsiy ma’lumot yubormang (ssenariylar sintetik).

---

## 7. Qabul qilish mezonlari

Servis tayyor deb hisoblanadi, agar:

1. **Kontrakt:** barcha javoblar `src/contracts/index.ts` dagi Zod sxemalardan o‘tadi. Eng oson yo‘li — bizning `lexsim-web` ni sizning servisga proxy qilib, `tools/qa/flow.mjs` (Playwright, to‘liq oqim) ni ishga tushirish.
2. **Dvigatel testlari:** `src/server/engine/__tests__/engine.test.ts` dagi barcha holatlar sizning servisda ham o‘tadi (portlang):
   - ochilishda yashirin fakt sizmaydi;
   - fakt faqat to‘g‘ri savolga ochiladi, `sequence` monoton va noyob;
   - bir xil `clientTurnId` → bir xil javob, bitta replika;
   - assessment rejimida `meters: null`;
   - boshqa egasi → 403;
   - sabr 0 → `poor`;
   - pora qabul → 0 ball, `failed`;
   - ideal yo‘l → `excellent`, ≥ 90 ball, rubrika max yig‘indisi 100, modda raqami yo‘q.
3. **Idempotentlik:** bir xil `clientTurnId` bilan ikkita **parallel** so‘rov → bitta LLM chaqiruv, bitta replika, ikkalasi bir xil javob.
4. **Kechikish:** `POST /turns` p95 ≤ 6 s (o‘zbekcha 20+ test dialogda o‘lchangan).
5. **LLM uzilishi:** model o‘chirilganda ham sessiya oxirigacha o‘tadi (`engine: "scripted"`).
6. **Etika:** 20+ dialog, mentor tekshiruvi — personaj yashirin faktni oldindan aytmaydi, huquqiy maslahat bermaydi, roldan chiqmaydi.
7. **Manbalar:** hisobotda tasdiqlanmagan modda raqami yo‘q; barcha havolalar `https://lex.uz`.

---

## 8. Keyingi bosqichlar (kontrakt hozircha yo‘q — birga kelishamiz)

| Mavzu | Taklif | Frontend tomonda |
|---|---|---|
| Streaming javob | `POST /turns` → SSE (`text/event-stream`): `npc.delta` (matn bo‘laklari) va oxirida to‘liq `MutationResponse` | Subtitr va og‘iz animatsiyasi bo‘laklab |
| Ovoz | `POST /v1/voice/session` → ephemeral token (WebRTC); STT/TTS sizda | Mikrofon ruxsati, yozuv indikatori, viseme |
| Auth | Talaba / o‘qituvchi / admin; cookie sessiya | Login sahifalari |
| Ssenariy katalogi | `GET /v1/scenarios` (faqat public qismi) | Hub hozir qo‘lda yozilgan ro‘yxatdan |
| Dinamik hujjat formasi | Ssenariy o‘z `services[]`, `evidence[]`, maydonlarini beradi | Forma shundan quriladi |
| O‘qituvchi paneli | Guruh statistikasi, tipik xatolar, e’tirozlar navbati, replay | Alohida sahifalar |
| Telegram-bot (fuqaro rejimi) | Xuddi shu dvigatel, boshqa kanal | — (frontend ishtirok etmaydi) |
| Advokat va fuqaro rollari | Yangi ssenariylar + `roomId` | Yangi 3D xonalar |

---

## 9. Javob berishingiz kerak bo‘lgan savollar

1. Servis manzili va tili (FastAPI deb faraz qilyapmiz) — proxy’ni qachon ulaymiz?
2. LLM modeli(lar) — o‘zbekcha dialogda 3 ta modelni solishtirish natijasi?
3. Baholash sinxronmi (≤ 30 s) yoki asinxronmi (§4.7)?
4. Streaming (SSE) MVP’da bo‘ladimi?
5. Hujjat formasi ssenariyga bog‘liq bo‘ladimi (§5.2)?
6. Rate limit va saqlash muddatlari bo‘yicha qarorlar.

Savollar bo‘lsa — frontend jamoasiga murojaat qiling. Kontraktni o‘zgartirish kerak bo‘lsa, `src/contracts/index.ts` ga PR orqali taklif qiling va `PROTOCOL_VERSION` ni oshiring.
