# LexLevel — 3-guruh: Ichki logika (Backend, ball hisoblash, nazorat)

**Mas'ul:** server, ma'lumotlar bazasi, ball hisoblash va nazorat bo'yicha jamoa a'zosi.
**Maqsad:** tizimning "miyasi": keyslarni saqlash, sessiyalarni boshqarish, AI'ni chaqirish, ballni to'g'ri hisoblash, halollikni nazorat qilish va sertifikat berish. **Sertifikatga bo'lgan ishonch shu qismga bog'liq** — loyihaning eng muhim joyi.

Qo'shni fayllar: [1-vizual.md](1-vizual.md), [2-ai-qismi.md](2-ai-qismi.md).

**Hali yechimi yo'q savollar:** 15-bo'lim (butun loyiha uchun eng og'ir savollar ham shu yerda).

---

## 0. Loyiha bir qarashda

LexLevel — yuridik talabalar uchun virtual amaliyot. Talaba 4 modulda ishlaydi:

| Modul | Kod | Talaba nima qiladi |
|---|---|---|
| Mijoz | `mijoz` | AI mijoz bilan suhbatlashib, faktlarni aniqlaydi |
| Hujjat | `hujjat` | Da'vo arizasi, shartnoma yoki xulosa yozadi |
| Sud zali | `sud` | AI sudya va AI raqib advokat bilan sud jarayonida qatnashadi |
| Tahlil | `tahlil` | Keysni tahlil qiladi, Lex.uz'dan norma topib qo'llaydi |

Har modul baholanadi va IELTS kabi 1–9 band oladi. 4 modulning o'rtachasi sertifikatga yoziladi. Rejimlar: `practice` (mashq) va `exam` (imtihon).

## 1. Kim nima qiladi (uchala faylda bir xil)

| Funksiya | 1. Vizual | 2. AI | 3. Logika |
|---|---|---|---|
| Keys (vaziyat) | Ochiq qismini ko'rsatadi | Rol promptlarida ishlatadi | Saqlaydi, versiyalaydi, kimga nima ko'rinishini boshqaradi |
| Mijoz suhbati | Chat oynasi | Mijoz roli, fakt aniqlagich | Sessiya, ochilgan faktlar, vaqt |
| Sud zali | Sud zali ekrani | Sudya va raqib advokat | Bosqichlar, navbat, e'tiroz qachon bo'lishi |
| Hujjat yozish | Muharrir, avtosaqlash | Baholashning AI qismi | Saqlash, avtomatik tekshiruvlar |
| Baholash | Natija sahifasi | Mezon darajasi, dalil, izoh | Ball, band, cheklovlar, ekspert nazorati |
| Halollik nazorati | Hodisalarni yuboradi (paste, tab) | Og'zaki savollar (P1) | Qoidalar, bayroqlar, audit |
| Sertifikat | Sertifikat va tekshirish sahifasi | — | ID, imzo, muddat, holat |
| Ish beruvchi | Panel ekranlari | — | Qidiruv, rozilik, takliflar |

Ustuvorlik: **P0** — hakaton demosi uchun shart; **P1** — vaqt qolsa; **P2** — hakatondan keyin.

## 2. Arxitektura

```
Brauzer (Next.js) ──HTTP/SSE──> Backend (FastAPI) ──> PostgreSQL
                                     │
                                     ├──> AI moduli (ai/) ──> Claude API
                                     └──> Fon vazifalari (baholash navbati)
```

- **Backend:** Python + FastAPI. AI kutubxonalari bilan ishlash oson, AI moduli bilan bitta kodda turadi.
- **Baza:** PostgreSQL (hakatonda SQLite ham bo'ladi). P1: norma qidiruvi uchun pgvector.
- **Fon vazifalari:** baholash 10–30 soniya oladi, shuning uchun u so'rov ichida emas, fon vazifasida bajariladi (FastAPI BackgroundTasks, RQ yoki Celery).
- Barcha vaqtlar UTC'da va server vaqti bo'yicha.

## 3. Keys (real muammo) qayerdan olinadi

### 3.1 Manbalar
1. **Lex.uz "Sud amaliyoti" va "Sud qarorlari" bo'limlari** — real ishlar, anonimlashtirib ishlatiladi.
2. **Oliy sud Plenumi qarorlari** — tipik nizolar va sudlarning yondashuvi; rubrika uchun etalon.
3. **Amaliyotchi yuristlar** (advokat, yuriskonsult, notarius) — tipik murojaatlar, shaxsiy ma'lumotlarsiz.
4. **OTM yuridik klinikalari** — anonim murojaatlar (kelishuv asosida).
5. **Darsliklardagi kazuslar va sud o'yinlari (moot court) materiallari.**
6. **Ish beruvchilar** — o'z keyslari (P2, brendli keys).

### 3.2 Keys hayot sikli

| Holat | Kim | Nima bo'ladi |
|---|---|---|
| `draft` | Huquqshunos | Manbadan vaziyat yoziladi |
| `structured` | AI + huquqshunos | Keys JSON shakliga keltiriladi |
| `expert_review` | 1–2 ekspert | Huquqiy to'g'rilik, rubrika va kritik xatolar tekshiriladi |
| `pilot` | 5–10 talaba | Qiyinlik, vaqt va qaysi faktlar topilmayotgani o'lchanadi |
| `approved` | — | Mashq va imtihonda ishlatiladi |
| `needs_update` | Tizim | Keys tayangan qonun o'zgardi — imtihondan olinadi |
| `retired` | — | Eskirgan yoki uni juda ko'p talaba ko'rgan |

### 3.3 Anonimlashtirish qoidalari
- Olib tashlanadi yoki almashtiriladi: F.I.Sh., JShShIR, pasport, telefon, manzil, tashkilot nomi, ish raqami, sudya va advokat ismlari.
- Sanalar bir xil miqdorga suriladi va **oraliqlar saqlanadi**. Da'vo muddati sanalar orasidagi farqqa bog'liq; oraliq buzilsa, keys mantiqi ham buziladi.
- Summalarni bir xil koeffitsientga ko'paytirsa bo'ladi, hisob-kitob mantiqi saqlanadi.
- Har anonim keysni inson qayta tekshiradi.

### 3.4 Qonun o'zgarishini kuzatish
Keys tayangan har bir normani `norm_id`, Lex.uz havolasi va tahrir sanasi bilan saqlaydi. Haftada bir marta tekshiriladi: hujjat yangilangan bo'lsa, keys `needs_update` holatiga o'tadi va imtihondan olinadi.

### 3.5 Variantlar (imtihon uchun)
Asosiy keys shablon bo'ladi: ism, summa, sana va ayrim faktlar (masalan, "qisman qaytarilgan: ha/yo'q") parametr qilinadi. Variant shu tartibda tayyorlanadi:
1. Generator variant yasaydi.
2. Logika hisob-kitob va muddatlarni avtomatik tekshiradi.
3. Ekspert namunalarni ko'rib chiqadi.
4. Variant `approved` holatiga o'tadi.

Imtihonda talabaga u oldin ko'rmagan variant tushadi.

**Hakaton uchun:** bitta asosiy keys ("Qarz qaytarilmadi"). Uni jamoadagi huquqshunos yozadi, iloji bo'lsa amaliyotchi yurist ko'rib chiqadi. Qo'shimcha 1–2 variant.

### 3.6 Keys JSON (namuna)

Huquqiy mazmuni namuna uchun berilgan — uni jamoadagi huquqshunos to'ldiradi va tekshiradi.

```json
{
  "id": "qarz-001",
  "version": 1,
  "status": "approved",
  "title": "Qarz qaytarilmadi",
  "area": "fuqarolik",
  "difficulty": 2,
  "source": {"type": "court_decision", "note": "lex.uz sud qarorlari asosida, anonim"},
  "brief": "Rahbardan xat: mijoz do'stiga qarz bergan, qarz qaytarilmayapti. Suhbat o'tkazing va da'vo arizasini tayyorlang.",
  "attachments": [{"name": "tilxat.jpg", "visible": true}],
  "client": {
    "name": "Rustam Aliyev", "age": 45, "job": "tadbirkor",
    "mood": "asabiy, gapni chalg'itadi",
    "opening": "Assalomu alaykum. Do'stimga pul bergandim, endi qaytarmayapti..."
  },
  "facts_public": [
    "Mijoz do'stiga 10 mln so'm qarz bergan",
    "Qarzdor qo'ng'iroqlarga javob bermayapti"
  ],
  "facts_hidden": [
    {"id": "F1", "text": "Qarz 2023-yil 10-martda berilgan", "trigger": "qarz qachon berilgani yoki sanasi haqida so'rasa", "weight": 3, "critical": true},
    {"id": "F2", "text": "Tilxatda sana ko'rsatilmagan", "trigger": "tilxat yoki hujjatda nima yozilgani haqida so'rasa", "weight": 2, "critical": false},
    {"id": "F3", "text": "Qarzning 2 mln so'mi qaytarilgan", "trigger": "qarz qisman qaytarilganmi deb so'rasa", "weight": 3, "critical": true},
    {"id": "F4", "text": "Pul bank kartasi orqali o'tkazilgan", "trigger": "pul qanday berilgani haqida so'rasa", "weight": 2, "critical": false}
  ],
  "issues": ["qarz shartnomasi va uning isboti", "da'vo muddati", "qisman qaytarilgan summa", "dalillar"],
  "norms": ["FK-...", "FPK-..."],
  "modules": {
    "mijoz": {"time_limit_min": 15, "rubric_id": "rub-mijoz-v1"},
    "hujjat": {
      "task": "Sudga da'vo arizasini tayyorlang",
      "time_limit_min": 60,
      "rubric_id": "rub-hujjat-v1",
      "required_sections": ["sud nomi", "da'vogar", "javobgar", "holatlar bayoni", "talab", "dalillar ro'yxati", "ilovalar", "sana va imzo"],
      "expected_amount": 8000000
    },
    "sud": {
      "time_limit_min": 20,
      "rubric_id": "rub-sud-v1",
      "judge_questions": ["Qarz berilganini qanday dalil bilan tasdiqlaysiz?", "Qarzning bir qismi qaytarilganmi?"],
      "objections": [
        {"id": "O1", "trigger": "talaba tilxatni dalil sifatida taqdim etsa", "text": "Tilxatda sana ko'rsatilmagan", "good_answer": "bank o'tkazmasi ko'chirmasi kabi muqobil dalilni ko'rsatish"}
      ],
      "opponent_position": "Javobgar qarzni tan oladi, lekin 2 mln so'm qaytarilganini va muddat o'tganini aytadi"
    },
    "tahlil": {
      "rubric_id": "rub-tahlil-v1",
      "questions": ["Da'vo muddati o'tganmi? Asoslang."],
      "expected_norm_ids": ["FK-..."]
    }
  },
  "reference": {
    "key_points": ["Qarz 10 mln, 2 mln qaytarilgan, demak talab 8 mln", "Bank o'tkazmasi qarz berilganini tasdiqlaydi", "Da'vo muddati hisoblanishi kerak"],
    "critical_errors": [{"id": "E1", "text": "Da'vo muddati umuman tekshirilmagan", "cap_band": 5.0}]
  },
  "real_outcome": "Sud da'voni qisman qanoatlantirgan: 8 mln so'm undirilgan (namuna).",
  "variant_params": {"amount": [8000000, 10000000, 15000000], "client_name": ["Rustam Aliyev", "Botir Karimov"]}
}
```

**Kimga nima ko'rinadi:** talaba endpointlari faqat `id`, `title`, `brief`, `attachments` (faqat `visible: true`), `client.name/age/job`, `facts_public`, modul topshirig'i va vaqt limitlarini qaytaradi. Qolgan hamma narsa faqat serverda turadi. `real_outcome` faqat topshirilgandan keyin natija bilan beriladi.

## 4. Sessiya va holat boshqaruvi

### 4.1 Sessiya hayoti
`created` → `active` → `submitted` → `graded` → `final`. Muddat tugasa, sessiya oxirgi qoralama bilan avtomatik `submitted` holatiga o'tadi.

### 4.2 Mijoz moduli (har talaba xabarida)
1. Xabar saqlanadi (`messages`), bir xil `client_msg_id` takror kelsa rad etiladi.
2. `ai.detect_facts(...)` chaqiriladi, yangi ochilgan faktlar `sessions.unlocked_facts` ga qo'shiladi.
3. Yangi fakt bo'lsa, mijoz uchun system ko'rsatma tayyorlanadi ([2-ai-qismi.md](2-ai-qismi.md), 5.1).
4. `ai.client_reply(...)` oqimi SSE orqali frontendga uzatiladi.
5. Mijoz javobi saqlanadi.

Suhbat yakunida talaba qisqa xulosa yozadi va u baholashga ketadi.

### 4.3 Sud zali — holat mashinasi

Bosqichlar: `ochilish` → `davo_bayoni` → `dalillar` → `savol_javob` → `yakuniy_soz` → `yakun`.

| Bosqich | Kim gapiradi | Keyingi bosqichga o'tish sharti |
|---|---|---|
| `ochilish` | Sudya | Avtomatik |
| `davo_bayoni` | Talaba (90 s) | Talaba gapirdi yoki vaqt tugadi |
| `dalillar` | Talaba; e'tiroz bo'lsa raqib, keyin talaba (30 s), keyin sudya qarori | Talaba "dalillar tugadi" dedi yoki limit tugadi |
| `savol_javob` | Sudya savoli, keyin talaba (60 s) | Keysdagi savollar tugadi |
| `yakuniy_soz` | Talaba (90 s) | Gapirdi yoki vaqt tugadi |
| `yakun` | Sudya | Sessiya `submitted` holatiga o'tadi |

- **E'tiroz:** `dalillar` bosqichida har talaba gapidan keyin `ai.detect_triggers` chaqiriladi. Trigger ishga tushsa va bu e'tiroz hali bildirilmagan bo'lsa, raqibga "O1 ni bildir" ko'rsatmasi yuboriladi. Har e'tiroz faqat bir marta bildiriladi.
- **Sudya qarori:** talaba e'tirozga javob bergan bo'lsa (`addressed`), e'tiroz rad etiladi; javob bermasa yoki vaqt tugasa, qanoatlantiriladi. Qarorni logika chiqaradi, sudya faqat aytadi.
- Navbat va taymerlar serverda turadi (`turn_deadline_at`). Talaba vaqtida javob bermasa, "javob berilmadi" hodisasi yoziladi va ballga ta'sir qiladi.

### 4.4 Vaqt
- `deadline_at` sessiya boshlanganda serverda yoziladi. Har javobda `server_time` qaytariladi.
- Muddatdan keyin kelgan xabar va topshirish rad etiladi; qoralama avtomatik topshiriladi.
- Imtihonda bir foydalanuvchida faqat bitta faol sessiya bo'ladi.

### 4.5 Avtosaqlash
`PUT /draft` `{text, version}` qabul qiladi. Versiya mos kelmasa (boshqa oynadan yozilgan bo'lsa), 409 qaytariladi.

## 5. Baholash — eng muhim qism

### 5.1 Tamoyillar
1. **AI ball qo'ymaydi.** AI har mezon bo'yicha daraja (0–4), dalil va izoh beradi. Ball, band va cheklovlarni logika formulasi hisoblaydi. Formula ochiq va hamma uchun bir xil.
2. **Avtomatik tekshirsa bo'ladigan joyda AI ishlatilmaydi.** Bo'limlar bormi, summa to'g'rimi, faktlar ochilganmi, modda mavjudmi — bularni kod tekshiradi.
3. **Har ball dalilga ega.** Talaba matnidan iqtibos yoki tizim hodisasi ("F3 fakti aniqlanmagan").
4. **Bir xil ish — bir xil baho.** AI ikki marta baholaydi; farq katta bo'lsa, uchinchi marta yoki ekspert baholaydi.
5. **Sertifikat inson nazoratidan o'tadi.** Imtihon natijalarining bir qismi va barcha shubhali holatlarni ekspert ko'radi.
6. **Hamma narsa versiyalanadi.** Keys, rubrika, prompt va model har baho bilan birga saqlanadi.
7. **Talaba e'tiroz bildira oladi.** Ekspert ishni qayta ko'radi, natija va sabab yoziladi.

### 5.2 Mezonlar va kim tekshiradi

`AVTO` — kod tekshiradi; `AI` — baholovchi; `AI + AVTO` — ikkalasi (masalan, kod moddaning mavjudligini, AI to'g'ri qo'llanganini tekshiradi).

**Mijoz moduli**

| Mezon | Vazn | Kim | Qanday |
|---|---|---|---|
| Faktlarni aniqlash | 40 | AVTO | Ochilgan yashirin faktlar og'irligining jami og'irlikka nisbati |
| Savol berish sifati | 20 | AI | Ochiq savollar, mantiqiy ketma-ketlik, aniqlashtirish |
| Muloqot va etika | 15 | AI | Hurmat, tushunarli til, asossiz va'da bermaslik |
| Yakuniy xulosa | 25 | AI + AVTO | Keysdagi asosiy masalalar (`issues`) qamrab olinganmi |

Faktlar nisbati r darajaga shunday o'tadi: r ≥ 0,9 → 4; r ≥ 0,7 → 3; r ≥ 0,5 → 2; r ≥ 0,25 → 1; aks holda 0. Topilmagan kritik faktlar "Topilmagan faktlar" ro'yxatiga albatta tushadi.

**Hujjat moduli**

| Mezon | Vazn | Kim | Qanday |
|---|---|---|---|
| Faktlarni aks ettirish | 25 | AI | Faktlar to'g'ri va to'liq yozilganmi |
| Huquqiy asos | 25 | AI + AVTO | Kod: keltirilgan moddalar bazada bormi; AI: to'g'ri qo'llanganmi |
| Hujjat tuzilishi | 20 | AVTO | `required_sections` dan nechtasi topildi (kalit so'zlar bo'yicha; ishonch past bo'lsa AI tekshiradi) |
| Talab va hisob-kitob | 15 | AVTO | Talab qilingan summa `expected_amount` ga tengmi |
| Muddat va xavflar | 15 | AI | Da'vo muddati va boshqa xavflar ko'rib chiqilganmi |

Summa matndan regex bilan ajratiladi ("8 000 000", "8 mln"). Topilmasa yoki bir nechta bo'lsa, AI'dan JSON ichida `claimed_amount` so'raladi, lekin solishtirishni baribir kod qiladi.

**Sud zali moduli**

| Mezon | Vazn | Kim | Qanday |
|---|---|---|---|
| Dalil bilan ishlash | 25 | AI | Dalillarni to'g'ri taqdim etish va asoslash |
| E'tirozlarga javob | 20 | AVTO + AI | Kod: vaqtida javob berildimi; AI: javob sifati |
| Protsessual tartib | 20 | AI | Sudga murojaat shakli, navbatga rioya, odob |
| Nutq va mantiq | 20 | AI | Aniqlik, izchillik, ishonarlilik |
| Vaqtni boshqarish | 15 | AVTO | Vaqti tugab qolgan navbatlar soni |

**Tahlil moduli**

| Mezon | Vazn | Kim | Qanday |
|---|---|---|---|
| Normani topish | 30 | AVTO | Keltirilgan moddalar `expected_norm_ids` bilan solishtiriladi |
| Normani qo'llash | 35 | AI | Norma faktlarga to'g'ri qo'llanganmi |
| Xulosa aniqligi | 20 | AI | Aniq javob va asos bormi |
| Manba ko'rsatish | 15 | AVTO | Moddalar to'g'ri formatda ("FK 123-modda") va bazada bor |

**Daraja tavsifi** (umumiy shablon, har keys uchun ekspert aniqlashtiradi):

| Daraja | Ma'nosi |
|---|---|
| 4 | To'liq va aniq, kamchiliksiz |
| 3 | Asosan to'g'ri, kichik kamchilik bor |
| 2 | Qisman to'g'ri, muhim narsa yetishmaydi |
| 1 | Jiddiy kamchiliklar, faqat urinish bor |
| 0 | Yo'q yoki butunlay noto'g'ri |

### 5.3 Ball hisoblash

```
mezon_ball  = vazn × daraja / 4
modul_xom   = mezon_ballar yig'indisi                 (0–100)
modul_band  = band_jadvali(modul_xom)
kritik xato bo'lsa:  modul_band = min(modul_band, cap_band)
umumiy_band = floor(modul_bandlar_o'rtachasi × 2 + 0.5) / 2
```

**Yaxlitlash tuzog'i:** Python'da `round(12.5)` natijasi 12 bo'ladi (bankir yaxlitlashi). IELTS kabi yuqoriga yaxlitlash uchun `math.floor(x * 2 + 0.5) / 2` ishlating. Testlar: 6.25 → 6.5; 6.75 → 7.0; 6.125 → 6.0; 7.5 → 7.5.

**Band jadvali** (boshlang'ich qiymatlar, pilotda kalibrlanadi):

| Xom ball (kamida) | Band | Xom ball (kamida) | Band |
|---|---|---|---|
| 95 | 9.0 | 44 | 4.5 |
| 90 | 8.5 | 38 | 4.0 |
| 85 | 8.0 | 32 | 3.5 |
| 80 | 7.5 | 26 | 3.0 |
| 74 | 7.0 | 20 | 2.5 |
| 68 | 6.5 | 14 | 2.0 |
| 62 | 6.0 | 7 | 1.5 |
| 56 | 5.5 | 0 | 1.0 |
| 50 | 5.0 | | |

Tekshiruv: demo ssenariysidagi 64 ball → 6.0, 86 ball → 8.0. Planshetdagi sertifikat: (8.0 + 7.0 + 7.5 + 7.5) / 4 = 7.5.

**Kalibrlash (pilotda):** ikki ekspert har modul uchun 20–30 ta ishni band bo'yicha mustaqil belgilaydi. Jadval chegaralari ekspertlar bandiga eng yaqin natija beradigan qilib suriladi.

### 5.4 Barqarorlik (AI'ga ishonch)
- Har ish ikki marta parallel baholanadi (`evaluation_runs` jadvalida 2 ta yozuv).
- Biror mezon darajasi 2 va undan ko'p farq qilsa yoki xom ball 10 va undan ko'p farq qilsa, uchinchi baholash o'tkaziladi va har mezon bo'yicha mediana olinadi.
- Uchta baholashda ham tarqoqlik katta bo'lsa, ish `needs_review` holatiga o'tadi.
- 1 darajalik farq bo'lsa, pastrog'i olinadi — sertifikat uchun ehtiyotkor qoida.
- Iqtibos tekshiruvi: AI keltirgan `evidence` talaba matnida so'zma-so'z bormi (normalizatsiyadan keyin). Topilmasa, o'sha mezon `needs_review` deb belgilanadi.
- Har mezon javobda bir martadan bormi — tekshiriladi, bo'lmasa so'rov qayta yuboriladi.
- **Gold set:** har prompt yoki rubrika o'zgarishidan keyin qayta ishga tushiriladi. Moslik pasaysa, o'zgarish ishga tushirilmaydi. Maqsad: QWK ≥ 0,7 va ishlarning kamida 80 foizida band farqi ≤ 0,5.
- **Monitoring:** haftada tasodifiy 5% ishni ekspert qayta baholaydi va AI–ekspert farqi grafikda kuzatiladi.

### 5.5 Inson nazorati (ekspert)
- **Mashq:** faqat AI (tezkor). Talaba e'tiroz bildirsa, ish ekspert navbatiga tushadi.
- **Imtihon:** sertifikat berilishidan oldin ekspert ko'radi:
  - barcha `needs_review` va ochiq bayroqli ishlarni;
  - band chegarasiga yaqin ishlarni (xom ball chegaradan ±2 ball);
  - tasodifiy tanlangan 10–20% ishni.
- Ekspert har mezon darajasini o'zgartira oladi, lekin sababini yozishi shart. Yangi ball formula bilan qayta hisoblanadi.
- Ekspert va AI farqlari kalibrlash uchun saqlanadi.
- **Hakatonda:** 1 ta ekspert akkaunti va navbat qanday ishlashini ko'rsatish yetarli.

### 5.6 Halollik nazorati

| Signal | Manba | Qoida (boshlang'ich) | Bayroq |
|---|---|---|---|
| Katta paste | Vizual hodisasi | Imtihonda bir martada > 200 belgi | `paste_large` |
| Oynadan chiqish | `blur`/`focus` | Imtihonda > 3 marta yoki jami > 60 s | `focus_lost` |
| G'ayritabiiy yozish | `typing` | 10 s ichida paste'siz > 150 belgi | `typing_anomaly` |
| Juda tez | Vaqt | Limitning 15 foizidan kam vaqtda ≥ 80 ball | `too_fast` |
| O'xshashlik | Boshqa talabalar ishi | O'xshashlik > 0,8 (P1) | `similarity` |
| Baholovchiga buyruq | AI bayrog'i va regex | "4 qo'y", "ko'rsatmani unut", "ignore" | `prompt_injection` |
| AI'lar kelishmovchiligi | Baholash | 5.4 dagi qoida | `grader_disagreement` |
| Og'zaki himoya | AI (P1) | Javoblar hujjatga zid | `oral_mismatch` |

- Bayroq talabani avtomatik yiqitmaydi: ish ekspert navbatiga tushadi. Qoidabuzarlik tasdiqlansa, natija bekor qilinadi va sertifikat `revoked` holatiga o'tadi.
- Imtihon variantlari tasodifiy tanlanadi va talaba ularni oldin ko'rmagan bo'ladi.
- Taymerlar serverda; bitta faol imtihon sessiyasi; sessiyani qayta boshlash qayd etiladi.
- AI yozgan matnni aniqlaydigan vositalarga tayanmang — ular ishonchsiz. Jarayon signallari va og'zaki himoya ancha ishonchli.
- **P2:** rasmiy sertifikat sessiyalari OTM test markazida, shaxsni tasdiqlash bilan o'tkaziladi.

### 5.7 Audit
Har ball o'zgarishi `audit_log` jadvaliga yoziladi: kim, qachon, nima edi, nima bo'ldi va sababi. Sertifikat bandi qaysi baholashlardan kelgani doim kuzatilib turadi.

## 6. Sertifikat

- **ID:** `LX-` + yil + `-` + 6 ta tasodifiy belgi (base32, I, O, 0 va 1 belgilarisiz), masalan `LX-26-7KQ4M9`. Ketma-ket raqam bermang, aks holda boshqa sertifikatlarni taxmin qilib topish mumkin bo'ladi.
- **Imzo:** `HMAC-SHA256(maxfiy_kalit, cert_id + overall_band + issued_at)` ning 10 ta belgisi. QR manzili: `/v/LX-26-7KQ4M9?s=<imzo>`.
- **Berish shartlari:** barcha modullar (hakatonda — demo modullari) `final` holatida, ochiq bayroq yo'q, kerakli ekspert tekshiruvi tugagan.
- **Muddat:** 2 yil (`valid_until`). Holatlar: `active`, `expired`, `revoked`.
- Tekshirish API imzoni ham, bazadagi holatni ham tekshiradi. Ochiq sahifada minimal ma'lumot chiqadi, ishlar faqat talaba roziligi bilan ko'rsatiladi.
- **P1:** sertifikat PDF'ini serverda yasash.

## 7. Ish beruvchi va analitika

- Nomzod faqat `consent_show_profile = true` bo'lsa ko'rinadi.
- Filtrlar: eng kichik umumiy band, modul bo'yicha band, viloyat, OTM.
- Takliflar `invites` jadvalida saqlanadi, talabaga bildirishnoma ketadi.
- **Analitika (P1, hakatonda demo ma'lumot bilan):** OTM, viloyat va mezon kesimida o'rtacha daraja; eng ko'p topilmaydigan faktlar; band taqsimoti.

## 8. Ma'lumotlar bazasi

| Jadval | Asosiy maydonlar |
|---|---|
| `users` | id, role, full_name, university, region, consent_show_profile |
| `cases` | id, version, status, json, approved_by, approved_at |
| `case_variants` | id, case_id, case_version, params, json, status |
| `rubrics` | id, version, module, json |
| `sessions` | id, user_id, variant_id, module, mode, status, stage, unlocked_facts, started_at, deadline_at, submitted_at, exam_id |
| `messages` | id, session_id, seq, speaker, text, client_msg_id, created_at |
| `drafts` | session_id, version, text, updated_at |
| `events` | id, session_id, type, data, client_at, server_at |
| `evaluations` | id, session_id, rubric_id, status, raw_score, band, capped_by, finalized_by, finalized_at |
| `evaluation_runs` | id, evaluation_id, model, prompt_version, output_json, input_tokens, output_tokens, cache_read_tokens, latency_ms |
| `criterion_scores` | evaluation_id, criterion_id, level, points, source (`auto`/`ai`/`expert`), evidence, comment |
| `flags` | id, session_id, type, severity, data, status, resolved_by |
| `reviews` | id, evaluation_id, expert_id, changes, reason, created_at |
| `exams` | id, user_id, status, started_at, finished_at |
| `certificates` | cert_id, user_id, exam_id, overall_band, module_bands, issued_at, valid_until, status, signature |
| `invites` | id, employer_id, candidate_id, message, status |
| `audit_log` | id, actor_id, action, entity, before, after, reason, at |

## 9. Xavfsizlik va shaxsiy ma'lumotlar

- **Rollar:** talaba faqat o'zini ko'radi; ish beruvchi — roziligi bor nomzodlarni; ekspert — navbatdagi ishlarni; admin — hammasini.
- **Ochiq serializer:** talaba endpointlari uchun alohida "ochiq" serializer. Yashirin faktlar, rubrika, etalon va haqiqiy qaror hech qachon chiqmaydi (`real_outcome` faqat topshirilgandan keyin). **Buni test bilan tekshiring.**
- **Limit:** AI chaqiruvlariga cheklov (masalan, daqiqasiga 20 xabar) — xarajat va suiiste'moldan himoya.
- **Saqlash joyi:** shaxsiy ma'lumotlar O'zbekistondagi serverda saqlanadi ("Shaxsga doir ma'lumotlar to'g'risida"gi qonun, 27-1-modda; 2026-yil martda o'zgartirishlar kiritilgan — joriy matnni lex.uz'da tekshiring). AI'ga faqat anonim matn yuboriladi.
- **Kalitlar** `.env` faylida turadi, kodda va frontendda bo'lmaydi. Bazaning zaxira nusxasi olinadi.

## 10. API kontrakti

| Metod va yo'l | Kirish | Javob |
|---|---|---|
| `POST /api/auth/demo-login` | `{role}` | `{token, user}` |
| `GET /api/cases?module=` | — | `[{id, title, difficulty, modules}]` |
| `GET /api/cases/{id}/brief` | — | Faqat ochiq qism (3.6 ga qarang) |
| `POST /api/sessions` | `{case_id, module, mode}` | `{session_id, deadline_at, server_time, opening}` |
| `POST /api/sessions/{id}/messages` | `{text, client_msg_id}` | SSE oqim |
| `GET /api/sessions/{id}` | — | `{status, stage, transcript, draft, deadline_at, server_time}` |
| `PUT /api/sessions/{id}/draft` | `{text, version}` | `{saved_at, version}` yoki 409 |
| `POST /api/sessions/{id}/events` | `{events: [...]}` | 204 |
| `POST /api/sessions/{id}/submit` | `{text?}` | `{evaluation_id, status: "queued"}` |
| `GET /api/evaluations/{id}` | — | Pastdagi namuna |
| `POST /api/exams` (P1) | — | `{exam_id, sessions}` |
| `GET /api/exams/{id}` (P1) | — | Modullar holati |
| `GET /api/certificates/{cert_id}?s=` | — | Pastdagi namuna |
| `GET /api/employer/candidates` | `min_band`, `module`, `region` | Nomzodlar ro'yxati |
| `POST /api/employer/invites` | `{candidate_id, message}` | `{invite_id}` |
| `GET /api/review/queue` (P1) | — | Ekspert navbati |
| `POST /api/review/{evaluation_id}` (P1) | `{criteria: [{id, level, comment}], reason}` | Yangilangan baho |

**Sessiya boshlash:**

```json
{"session_id": "s_8f2k", "module": "mijoz", "mode": "practice",
 "started_at": "2026-11-21T10:00:00Z", "deadline_at": "2026-11-21T10:15:00Z",
 "server_time": "2026-11-21T10:00:00Z",
 "opening": {"speaker": "client", "text": "Assalomu alaykum. Do'stimga pul bergandim..."}}
```

**SSE hodisalari** (`speaker`: `client`, `judge`, `opponent`, `system`):

```
event: token
data: {"speaker": "client", "delta": "O'tgan yili "}

event: message_done
data: {"message_id": "m_17", "speaker": "client"}

event: court_state
data: {"stage": "dalillar", "turn": "student", "turn_deadline_at": "2026-11-21T10:12:30Z"}

event: objection
data: {"objection_id": "O1", "by": "opponent", "respond_deadline_at": "2026-11-21T10:13:00Z"}

event: ruling
data: {"objection_id": "O1", "decision": "overruled"}

event: error
data: {"code": "ai_timeout", "message": "Javob kechikdi, qayta urinib ko'ring"}
```

**Baholash natijasi** (`status`: `queued`, `running`, `done`, `needs_review`, `final`):

```json
{"evaluation_id": "e_51", "status": "done", "module": "hujjat",
 "raw_score": 64, "band": 6.0, "capped": false,
 "criteria": [
   {"id": "C1", "name": "Faktlarni aks ettirish", "weight": 25, "level": 3, "points": 18.75,
    "comment": "Asosiy faktlar bor, lekin qisman qaytarilgan summa yo'q.",
    "evidence": ["Javobgar 10 mln so'm qarz olgan"],
    "norms": [{"title": "FK ...-modda", "url": "https://lex.uz/..."}],
    "source": "ai"}
 ],
 "missed": ["Qisman qaytarilgan 2 mln so'm hisobga olinmagan"],
 "critical_errors": [],
 "feedback": "Faktlar yaxshi yig'ilgan. Keyingi safar qarzning qaytarilgan qismini so'rang va talab summasini shunga qarab hisoblang.",
 "real_outcome": "Sud da'voni qisman qanoatlantirgan (namuna)."}
```

**Sertifikatni tekshirish:**

```json
{"cert_id": "LX-26-7KQ4M9", "status": "active", "signature_valid": true,
 "holder_name": "Aziza Karimova", "program": "Yurisprudensiya, 3-kurs",
 "overall_band": 7.5,
 "modules": {"mijoz": 8.0, "hujjat": 7.0, "sud": 7.5, "tahlil": 7.5},
 "issued_at": "2026-11-20", "valid_until": "2028-11-20"}
```

## 11. Testlar

- **Unit:** ball formulasi, band jadvali, yaxlitlash (6.25 → 6.5; 6.75 → 7.0; 6.125 → 6.0), kritik xato cheklovi, taymer muddati, sertifikat imzosi.
- **Integratsiya:** AI o'rniga soxta (stub) javoblar bilan butun sessiya boshidan oxirigacha.
- **Xavfsizlik:** talaba endpointlari yashirin maydonlarni qaytarmasligi.
- **Gold set regressiyasi:** AI guruhi bilan birga ([2-ai-qismi.md](2-ai-qismi.md), 10-bo'lim).

## 12. Demo uchun tayyorgarlik

- **Seed:** 1 ta keys, rubrikalar, demo foydalanuvchilar, tayyor natijalar, 3–5 ta sertifikat.
- **"Demo reset" buyrug'i:** bazani boshlang'ich holatga qaytaradi (demo oldidan ishga tushiriladi).
- AI ishlamasa, AI guruhining replay rejimi ishlatiladi.
- Loglar ochiq tursin: demo paytida xato bo'lsa, sababini tez topish uchun.

## 13. Tayyorlik ro'yxati (Definition of Done)

- [ ] Baza sxemasi, seed keys va rubrikalar tayyor
- [ ] Sessiyalar server taymeri, avtosaqlash va hodisalar bilan ishlaydi
- [ ] Mijoz suhbati: fakt aniqlash, system ko'rsatma, SSE oqimi
- [ ] Sud zali holat mashinasi va e'tiroz logikasi ishlaydi
- [ ] Ball formulasi, band jadvali va yaxlitlash testlari o'tdi
- [ ] Ikki marta baholash, solishtirish va `needs_review` ishlaydi
- [ ] Bayroqlar va ekspert navbati ishlaydi
- [ ] Sertifikat beriladi va imzo bilan tekshiriladi
- [ ] Talaba endpointlari yashirin ma'lumotni qaytarmaydi (test bor)
- [ ] Ish beruvchi ro'yxati rozilik bo'yicha filtrlanadi
- [ ] Har ball o'zgarishi audit jurnaliga yoziladi
- [ ] 15-bo'limdagi "Hakatongacha" bandlari bo'yicha qaror qabul qilinib, yozib qo'yildi

## 14. Boshlash tartibi

1. Vizual va AI guruhlari bilan kontraktni kelishib oling (birinchi 2–3 soat).
2. Baza sxemasi, seed keys va rubrikalar.
3. Sessiya va xabarlar (AI o'rniga stub bilan), SSE.
4. Ball hisoblash moduli va uning testlari (yaxlitlashni unutmang).
5. Haqiqiy AI chaqiruvlarini ulash, baholash navbati.
6. Sertifikat va tekshirish sahifasi API'si.
7. Bayroqlar va ekspert navbati.
8. Ish beruvchi ro'yxati, analitika uchun demo ma'lumot.

## 15. Ochiq muammolar: chuqurroq o'ylash kerak

Yuqoridagi bo'limlarda yechimi ma'lum ishlar yozilgan. Bu bo'limda esa tayyor javobi yo'q savollar to'plangan, jumladan butun loyiha uchun eng og'irlari (15.7–15.10). Ularni huquqshunos, OTM va pilot ma'lumotlari yordamida hal qilish kerak. "Hakamlar so'rashi mumkin" deb belgilangan savollarga pitch uchun javob tayyorlang.

### A. Baholashning to'g'riligi

#### 15.1 Band hamma variantda bir xil ma'noga egami (hakamlar so'rashi mumkin)
- **Muammo:** oson variantda olingan 7.0 qiyin variantdagi 7.0 ga teng emas. Xalqaro imtihonlar har variantni oldindan sinab, qiyinligini tenglashtiradi (equating). Busiz sertifikatlarni bir-biri bilan solishtirib bo'lmaydi.
- **Nega qiyin:** tenglashtirish uchun har variantni ko'p talaba yechishi va statistik usullar (masalan, Item Response Theory) kerak.
- **Mumkin yo'llar:** pilotda har variantning o'rtacha bali va tarqalishiga qarab tuzatish koeffitsienti; imtihonda faqat pilotdan o'tgan variantlar; keyinchalik IRT modeli.
- **Hakatongacha:** bu muammoni bilishingizni va pilotdagi rejangizni pitch'da ayta oling.

#### 15.2 Band haqiqiy ishni bashorat qiladimi (hakamlar so'rashi mumkin)
- **Muammo:** biz "7.5 — junior yurist darajasi" deymiz, lekin buni tasdiqlovchi ma'lumot hali yo'q. Hozircha bu gipoteza.
- **Mumkin yo'l:** pilotda LexLevel bandini talabaning real amaliyotdagi rahbari qo'ygan baho bilan solishtirish (predictive validity). Bog'liqlik past chiqsa, rubrika yoki modullar qayta ko'rib chiqiladi.
- **Hakatongacha:** pitch va sertifikatdagi band tavsiflarini kafolat sifatida emas, "maqsadli daraja" deb ko'rsating.

#### 15.3 Vaznlar va chegaralar qayerdan keladi
- **Muammo:** mezon vaznlari (masalan, 40/20/15/25) va band jadvali hozircha taxmin. "Nega 62 ball — 6.0?" degan savolga asosli javob kerak.
- **Mumkin yo'llar:** ekspertlar bilan standart belgilash (standard setting) usullari — Angoff, Bookmark, Contrasting groups. Natija va qarorni kim qabul qilgani hujjatlashtiriladi.
- **Hakatongacha:** jadvalni "boshlang'ich, pilotda kalibrlanadi" deb ko'rsating; vaznlarni huquqshunos bilan bir marta ko'rib chiqing.

#### 15.4 Mezonlarni aldash
- **Muammo:** qoidani bilgan talaba uni aldashga urinadi: savollarni yog'dirib faktlarni ochadi ([2-ai-qismi.md](2-ai-qismi.md), 15.1), bo'lim nomlarini mazmunsiz yozib "Hujjat tuzilishi"dan ball oladi, moddalarni ko'p sanab "Normani topish" balini oshiradi.
- **Mumkin yo'l:** har avtomatik mezon uchun "buni qanday aldash mumkin?" degan savolni bering va unga qarshi qoida qo'shing: noto'g'ri modda uchun ball ayirish, bo'lim mazmunini AI tekshirishi va hokazo.
- **Hakatongacha:** har avtomatik mezonni kamida bitta aldash usuli bilan sinab ko'ring.

### B. Nazorat va resurslar

#### 15.5 Ekspertlar yetadimi
- **Muammo:** imtihonlarning 10–20 foizini, barcha bayroqli ishlarni va e'tirozlarni ekspert ko'radi. 1 000 ta imtihonga qancha ekspert-soat kerak? Ularga kim to'laydi? Ekspertlarning o'zi bir xil baholaydimi?
- **Mumkin yo'llar:** bitta tekshiruv necha daqiqa olishini pilotda o'lchash; ekspertlar uchun o'quv va kalibrlash sessiyasi; ekspert ishini OTM hamkorligi yoki haq evaziga tashkil etish.
- **Hakatongacha:** biznes modelga ekspert xarajatini qo'shing.

#### 15.6 Bayroq chegaralari va noto'g'ri ayblovlar
- **Muammo:** 200 belgilik paste yoki 3 marta oynadan chiqish kabi chegaralar hozircha taxmin. Halol talaba ham bayroq olishi mumkin: interneti uzilgan, brifingdan matn ko'chirgan yoki o'z shablonini ishlatgan bo'lishi mumkin. Noto'g'ri bayroqlar ko'payib ketsa, ekspertlar ishga ko'milib qoladi va talabalarga nisbatan adolatsizlik bo'ladi.
- **Javob topilishi kerak:** brifingdan ko'chirishga ruxsat bormi? Kamera orqali kuzatish (proktoring) maxfiylik va rozilikni talab qiladi, test markazi esa xarajatli — qaysi biri tanlanadi?
- **Hakatongacha:** bayroq talabani avtomatik jazolamasligini, faqat ekspertga yo'naltirishini aniq ko'rsating. Chegaralarni pilotda kalibrlang.

### C. Huquqiy va tashkiliy savollar (butun loyiha uchun)

#### 15.7 Sertifikatning huquqiy maqomi (hakamlar so'rashi mumkin)
- **Muammo:** xususiy loyiha "sertifikat" bera oladimi? U kimning nomidan beriladi? Ish beruvchi noto'g'ri band asosida xodim olsa, kim javob beradi?
- **Mumkin yo'llar:** (a) avval hamkor OTM bilan "ko'nikma hisoboti" sifatida; (b) keyin Oliy ta'lim vazirligi yoki Adliya vazirligi orqali tan olinish; (c) foydalanish shartlarida javobgarlik chegarasini belgilash.
- **Hakatongacha:** huquqshunos bilan bir sahifalik tahlil. Pitch'da: "Pilot bosqich, rasmiy tan olinish — keyingi qadam."

#### 15.8 Virtual amaliyot rasmiy amaliyotga hisoblanadimi
- **Muammo:** PF-232 dasturning 50 foizi real tashkilotlarda o'tishini talab qiladi, virtual soatlar bunga kirmaydi. Loyiha o'quv jarayonining qayeriga tushadi: auditoriyadagi amaliy mashg'ulotgami, real amaliyotga tayyorlovgami yoki baholash vositasimi?
- **Javob topilishi kerak:** OTM o'quv rejasi va HEMIS bilan qanday bog'lanadi (kreditlar, baholar)?
- **Hakatongacha:** pozitsiya: "Real amaliyotni almashtirmaydi — unga tayyorlaydi va natijani o'lchaydi." TDYU yoki boshqa OTM bilan pilot haqida gaplashing.

#### 15.9 Keys manbalaridan foydalanish huquqi va anonimlik
- **Muammo:** lex.uz'dagi sud qarorlarini qayta ishlatish shartlarini aniqlash kerak. Anonimlashtirilgan keysda ham noyob faktlar, viloyat va sana birgalikda tomonlarni aniqlab qo'yishi mumkin (qayta identifikatsiya). Darslikdagi kazuslar mualliflik huquqi bilan himoyalangan.
- **Hakatongacha:** demo keysni "real ish asosida, sezilarli o'zgartirilgan" deb belgilang va manbadan foydalanish shartlarini tekshiring.

#### 15.10 Shaxsiy ma'lumotlar: chet elga yuborish va saqlash muddati
- **Muammo:** talaba matni anonim bo'lsa ham, uni chet eldagi AI serveriga yuborish qonun bo'yicha shaxsiy ma'lumotni chegaradan o'tkazish hisoblanadimi — 2026-yilgi o'zgartirishlarni hisobga olib tekshirish kerak. Talaba hujjatga o'z ismini yoki boshqa real ma'lumotni yozib qo'yishi mumkin. Imtihon yozuvlari, hodisalar va qoralamalar qancha saqlanadi, o'chirish so'rovi qanday bajariladi?
- **Mumkin yo'llar:** AI'ga yuborishdan oldin matndan shaxsiy ma'lumotlarni avtomatik tozalash; saqlash muddati siyosati; huquqshunos xulosasi.
- **Hakatongacha:** demoda faqat o'ylab topilgan ma'lumotlar ishlatilsin.

### D. Masshtab

#### 15.11 Qayta topshirish va variantlar soni
- **Muammo:** cheksiz qayta topshirishda talaba variantlarni yodlab oladi, juda qattiq cheklov esa adolatsiz. Qayta topshirish qoidasi qancha variant kerakligini belgilaydi, bu esa keys yaratish tezligiga bog'liq.
- **Javob topilishi kerak:** imtihonlar orasida qancha kutish kerak (masalan, 30 kun)? Yiliga nechta variant tayyorlash kerak?
- **Hakatongacha:** qayta topshirish siyosati bo'yicha taklif va variantlar bazasi rejasi.

#### 15.12 Bir vaqtdagi yuklama
- **Muammo:** 300 talaba bir vaqtda imtihon topshirsa: SSE ulanishlari, AI limitlari, baholash navbati. Hakaton demosida bu ko'rinmaydi, pilotda esa birinchi kunning o'zidayoq chiqadi.
- **Mumkin yo'llar:** pilotdan oldin yuklama testi; baholash navbatini kengaytirish; AI limitlarini oldindan oshirtirish.
- **Hakatongacha:** shart emas, lekin rejada bo'lsin.
