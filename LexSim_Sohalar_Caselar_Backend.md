# Sohalar va caselar: odamlar kiritadi, AI tuzadi (backend v1.4.9)

**Kimga:** frontend dasturchisi.
**Sana:** 2026-11-21.
**Holat:** kod tayyor, serverdagi alohida nusxada jonli sinovdan o'tdi (RAG va AIHUB bilan). O'rnatish vaqti alohida xabar qilinadi.
**Kontrakt:** hozirgi marshrutlar o'zgarmaydi, faqat yangilari qo'shiladi.

---

## 1. G'oya

1. Ekranda **sohalar**. Talaba yo'nalish tanlaydi: iqtisodiy (yetkazib berish, kredit, ijara…), fuqarolik (mehnat…), jinoyat, DXM.
2. Har bir sohada **caselar** chiqadi. Ular ikki xil:
   - **tizimniki** (`source: "system"`): mentor tasdiqlagan ssenariylar. Hozir bittasi bor: ijara.
   - **odamlarniki** (`source: "user"`): talaba yoki o'qituvchi kiritgan.
3. **Case kiritish.** Odam muammoni oddiy so'z bilan yozadi. AI uni simulyatsiyaga mos case qilib tuzadi:
   - taraflar, talab, faktlar, dalillar;
   - har tomonning vazifasi va 2–4 ta maxfiy fakti;
   - huquqiy asos;
   - har ikki tomonning kuchli va zaif joyi;
   - aniqlashtiruvchi savollar.
4. **Tekshiruv.** Muallif o'z casesini darhol ko'radi va o'ynay oladi. Boshqalarga u **mentor tasdiqlagandan keyin** ko'rinadi.
5. Tasdiqlangan caselar **«Bahs»ga** chiqadi: `GET /moot/cases`.

### Nega AI «o'ylab topmaydi»

| Xavf | Himoya |
|---|---|
| Uydirma modda | AI'ga faqat **bizning lex.uz bazamizdan** (RAG) topilgan moddalar ro'yxati beriladi. Ro'yxatda yo'q `normId` va matndagi ro'yxatda yo'q «N-modda» server tomonida olib tashlanadi, `issues` ga yoziladi |
| Uydirma fakt yoki summa | AI faqat odam yozgan holatga tayanadi. Yetishmagan narsa `[aniqlanmagan]` deb qoladi va `questions` ga savol bo'lib tushadi |
| Shaxsiy ma'lumot | Telefon, pasport, JSHSHIR, karta va e-pochta AI'ga yuborilishidan **oldin** yashiriladi (`redacted`: nechtasi). Ism va kompaniya nomlarini AI shartli nomga almashtiradi («A» MChJ) |
| Bir tomonga og'gan case | `balance` maydoni majburiy: ikkala tomonning kuchli va zaif joyi. Bo'sh bo'lsa, `issues` da ko'rinadi |
| Sifatsiz case boshqalarga chiqishi | Mentor tasdig'isiz faqat muallifga ko'rinadi |

Bazada yo'q kodekslar: Mehnat kodeksi, JPK, JK, ZRU-445. Ular yuklanmaguncha mehnat, jinoyat va DXM caselari **moddasiz** tuziladi. Bunday caseda `issues` → «huquqiy asos yo'q — mentor moddalarni qo'shadi».

---

## 2. Marshrutlar

Hammasida `X-LexSim-Key` va `X-LexSim-Owner` (8–64 belgi) majburiy, xuddi `/store` dagidek.

| Usul | Yo'l | Nima |
|---|---|---|
| GET | `/domains` | Sohalar ro'yxati (kalitsiz ham ishlaydi) |
| GET | `/cases?domain=supply&scope=all\|mine` | Caselar: tasdiqlanganlar va o'zimniki |
| GET | `/cases/{id}` | Bitta case. Boshqalarning casesida maxfiy faktlar bo'sh keladi |
| POST | `/cases/drafts` | AI qoralamasini boshlash → `202` |
| GET | `/cases/drafts/{id}` | Qoralama holati: `working` → `ready` yoki `failed` |
| POST | `/cases` | Qoralamani (tahrirlangan bo'lishi mumkin) saqlash → `201`, `status: "review"` |
| POST | `/cases/{id}` | O'z casesini tahrirlash. Yana `review` ga qaytadi |
| POST | `/cases/{id}/review` | **Mentor:** `{"decision": "approve" \| "reject", "note": "…"}`. Faqat `X-Admin-Token` bilan |
| GET | `/moot/cases` | «Bahs» uchun: tasdiqlangan va `modes` da `moot` bor caselar |
| GET | `/moot/cases/{id}` | Bahs xonasi uchun **to'liq** case, ikkala tomonning maxfiy faktlari bilan. Faqat server tomonida ishlating, brauzerga bermang |

### 2.1. `GET /domains`

```json
{"domains": [
  {"id": "supply", "group": "iqtisodiy", "title": "Yetkazib berish", "court": "economic", "caseType": "IPK",
   "share2025": 24.2, "modes": ["moot"], "codes": ["FK", "IPK"], "note": ""},
  {"id": "lease", "group": "iqtisodiy", "title": "Ijara", "share2025": 5.1, "modes": ["court", "moot"], "...": "..."},
  {"id": "labour", "group": "fuqarolik", "title": "Mehnat nizolari", "modes": ["path", "moot"],
   "note": "Mehnat kodeksi hali bazada yo'q — moddalarni mentor qo'shadi"},
  {"id": "theft", "group": "jinoyat", "modes": ["path"], "...": "..."},
  {"id": "dxm", "group": "ma'muriy", "modes": ["path"], "...": "..."}
], "source": "https://stat.sud.uz/"}
```

- `share2025`: 2025-yilda shu turdagi ishlarning ulushi (stat.sud.uz), %. Iqtisodiy sohalarda hisob shartnomaviy nizolar ichidan, fuqarolikda fuqarolik ishlari ichidan. Ekranda «Sudlarda eng ko'p uchraydigan» belgisi uchun ishlatsa bo'ladi.
- `modes`:
  - `court`: bitta talabali sud zali (hozirgi ijara ssenariysi);
  - `path`: "Ish yo'li" (mehnat, o'g'irlik, DXM);
  - `moot`: «Bahs».

Jami 11 ta soha: `supply`, `communal`, `credit`, `sale`, `services`, `lease`, `construction`, `civil`, `labour`, `theft`, `dxm`.

### 2.2. Case kiritish oqimi

```
POST /cases/drafts  {"domain": "supply", "story": "Bizning firma mart oyida 20 tonna un…"}
→ 202 {"draft": {"id": "d_558f0861ad32", "status": "working"}}   Retry-After: 10

GET /cases/drafts/d_558f0861ad32   (har 8–10 s)
→ {"draft": {"id": "…", "status": "working"}}
→ {"draft": {"id": "…", "status": "ready", "case": {…}, "issues": [], "questions": …, "sources": 10, "redacted": 1, "ms": 48964}}
```

- `story`: 80–4000 belgi.
- `answers` (ixtiyoriy, matn): AI bergan savollarga javoblar. Ular bilan qoralamani **qayta** so'rang: `POST /cases/drafts {"domain", "story", "answers": "Shartnoma 3-martda tuzilgan; penya kechiktirilgan tovar qiymatidan…"}`.
- `sources`: AI'ga nechta modda taklif qilingani. 0 bo'lsa, «bazada mos modda topilmadi» deb ko'rsating.
- Vaqt: AIHUB bilan **45–95 s**. Ekranda «AI caseni tuzyapti…» va progress ko'rsating.
- `failed` → `error.message` ni ko'rsating va «Qayta urinish» tugmasini bering.
- Bir odamning bir vaqtda 2 tadan ortiq qoralamasi ishlay olmaydi (`429`). Soatiga ham chegara bor.
- Qoralama 6 soat saqlanadi. Shundan keyin `POST /cases` bilan saqlang.

**Talabaga ko'rsatish tartibi:**
1. `questions`: AI'ning aniqlashtiruvchi savollari, tepada. «Javob berib, qayta tuzish» tugmasi.
2. Case formasi, **tahrirlanadigan**: sarlavha, taraflar, talab, faktlar, dalillar, har tomonning vazifasi va maxfiy faktlari.
3. `legal`: har bir modda lex.uz havolasi va `why` izohi bilan.
4. `balance`: «Da'vogarning kuchli / zaif joyi», «Javobgarning kuchli / zaif joyi».
5. `issues`: sariq ogohlantirishlar (masalan, «maxfiy faktlar 1 ta (2–4 kerak)»).
6. «Saqlash» → `POST /cases`.

### 2.3. Case shakli

Sizning `MootCase` shaklingiz va qo'shimcha maydonlar:

```json
{
  "id": "u_05b4c86990", "domain": "supply", "source": "user", "status": "review", "mine": true,
  "title": "20 tonna unni kechiktirib yetkazib berish va sifatsiz mahsulot uchun mulkiy javobgarlik",
  "court": "…", "summary": "…",
  "parties": {"claimant": "«A» MChJ — xaridor…", "respondent": "«B» MChJ — yetkazib beruvchi…"},
  "claim": "… 0,5 foiz miqdorida penya … Penyaning yakuniy miqdori … [aniqlanmagan].",
  "facts":    [{"id": "f1", "title": "Shartnoma tuzilishi", "text": "…"}],
  "evidence": [{"id": "e1", "title": "Yetkazib berish shartnomasi", "text": "…"}],
  "side": {"claimant":   {"task": ["…"], "confidential": ["…", "…"]},
           "respondent": {"task": ["…"], "confidential": ["…", "…"]}},
  "points": {"claimant": [["Penya", "0,5 foiz"]], "respondent": [["Yo'l yopilishi", "Tashqi to'siq"]]},
  "legal": [{"normId": "FK-454", "label": "FK 454-modda", "url": "https://lex.uz/docs/180550#-183361",
             "why": "Tovarlarni to'liq yetkazib bermaganlik uchun neustoyka…"}],
  "balance": {"claimant_strong": "…", "claimant_weak": "…", "respondent_strong": "…", "respondent_weak": "…"},
  "questions": ["Shartnoma aynan qaysi sanada tuzilgan?", "…"],
  "disclaimer": "Oʻquv ishi. Nomlar, summalar va sanalar oʻzgartirilgan; haqiqiy shaxslarga aloqasi yoʻq.",
  "reviewNote": null, "createdAt": "…", "updatedAt": "…"
}
```

**Tahrirlab saqlaganda** (`POST /cases` yoki `/cases/{id}`) `legal` da faqat bazamizda bor `normId` lar qoladi, boshqalari olib tashlanadi. Muallif yangi modda «o'ylab topa olmaydi». Modda qo'shishni mentor qiladi.

**Ko'rinish:**

| Kim | Nima ko'radi |
|---|---|
| Muallif | O'z casesini to'liq, har qanday holatda (`review`, `rejected` va `reviewNote` bilan) |
| Boshqa talaba | Faqat `approved`. Maxfiy faktlar bo'sh, `balance` yo'q |
| Bahs xonasi (sizning server) | `GET /moot/cases/{id}`: to'liq. Har o'yinchiga faqat o'z tomonini bering |
| Mentor (`X-Admin-Token`) | Hammasi. `GET /cases?scope=review` — tekshiruv navbati |

### 2.4. Mentor sahifasi

`GET /cases?scope=review` (admin token bilan) → tekshiruvni kutayotganlar. Har birida «Tasdiqlash» va «Rad etish (izoh bilan)» tugmalari: `POST /cases/{id}/review`.

Admin token brauzerga chiqmasin: mentor sahifasi sizning server orqali ishlasin. Mentor hisoblari (kim mentor) masalasini loyiha egasi bilan hal qilamiz.

---

## 3. Jonli sinov (alohida port, 21-noyabr)

Hikoya: un yetkazib berish, 180 mln oldindan to'lov, 22 kun kechikish, 3 tonna sifatsiz, omborchi «e'tirozsiz» deb yozib qo'ygan, telefon raqami bor.

| Ko'rsatkich | Natija |
|---|---|
| Vaqt | 49 s |
| RAG'dan taklif qilingan moddalar | 10 |
| AI tanlagani | FK 454 (neustoyka), FK 451 (sifatsiz tovar), FK 440, OXS163 13, 16, 18-bandlar |
| Telefon | yashirildi (`redacted: 1`), AI'ga bormagan |
| Faktlar va dalillar | 7 ta fakt, 6 ta dalil |
| Maxfiy faktlar | har tomonga 4 ta |
| Muvozanat | to'liq: da'vogarning zaif joyi — «e'tirozsiz» yozuvi, javobgarning zaif joyi — kechikish va javobsiz qolgan pretenziya |
| Savollar | 6 ta: sana, penya bazasi, sifatsiz un qiymati, nuqson qachon aniqlangan… |
| `issues` | bo'sh |
| Boshqa egadan `GET` | `404` (ko'rinmaydi) |
| `/moot/cases` | tizimning ijara casesi chiqdi |

---

## 4. Sizdan

1. **Sohalar ekrani:** `GET /domains`. Guruhlar bo'yicha kartochkalar, `share2025` bo'yicha tartib, `note` ni kichik matn qilib chiqaring.
2. **Soha ichida caselar ro'yxati:** `GET /cases?domain=…`. Belgilar: «Tizim» va «Foydalanuvchi», «Tekshiruvda» (faqat o'zimnikida), `modes` bo'yicha tugmalar (Sud zali / Ish yo'li / Bahs).
3. **«Case qo'shish» oynasi:** 2.2 dagi oqim.
4. **Mentor sahifasi:** 2.4.
5. **Bahs:** xona ochishda `caseId` endi `GET /moot/cases` dan tanlanadi.

## 5. Cheklovlar (ochiq aytaman)

- **AI sekin** (45–95 s), chunki hozirgi model AIHUB orqali ishlaydi. Tez API kaliti bilan ~10 s.
- **Mehnat, jinoyat va DXM caselari moddasiz.** Kodekslar bazaga yuklanmaguncha moddalarni mentor qo'shadi.
- **Plenumlar.** AI ba'zan Oliy xo'jalik sudi Plenumini (OXS163) tanlaydi. Ular amalda, lekin bazadagi tahriri tekshirilmagan (manbalar hisoboti, 4-xato). Shuning uchun har bir case mentor tasdig'idan o'tadi.
- **Bu o'quv ishi, yuridik maslahat emas.** `disclaimer` ni case kartasida doim ko'rsating.

---

# v1.5.0 — ochiq/yopiq caselar va ishtirokchilar yechimlari

**Holat:** kod tayyor, serverdagi 73 ta test o'tdi. O'rnatish vaqti alohida xabar qilinadi.
**Yangi `features`:** `case-visibility`, `case-solutions`.

## 6. Case: ochiq yoki yopiq

Muallif caseni saqlashda yoki keyin o'zi tanlaydi:

| `visibility` | Kim ko'radi | Mentor tekshiruvi |
|---|---|---|
| `public` | Mentor tasdiqlagach hamma. Ro'yxatda va «Bahs»da chiqadi | Kerak (`review` → `approved`) |
| `private` | Faqat muallif va **havola kodi** (`shareCode`) borlar. Ro'yxatda chiqmaydi | Kerak emas |

```
POST /cases                   {"domain", "case", "visibility": "private"}  → case.shareCode: "3f9a1c2e"
POST /cases/{id}/visibility   {"visibility": "public" | "private"}           — faqat muallif
GET  /cases/{id}?code=3f9a1c2e                                               — kod bilan begona ham ko'radi
GET  /moot/cases/{id}?code=…                                                 — yopiq caseda bahs xonasi uchun
```

- `shareCode` faqat muallifga qaytadi. «Havolani ulashish» tugmasi: `…/cases/{id}?code=…`.
- Yopiq case ochilsa, mentor tekshiruviga ketadi (`status: "review"`). Oldin tasdiqlangan bo'lsa, `approved` bo'lib qoladi.
- Ro'yxatdagi har bir caseda: `visibility` va `solutions` (ochiq yechimlar soni).

## 7. Yechimlar: har kim o'z yondashuvini qoldiradi

Case'ni yechgan (bahs, sud zali yoki o'zi o'ylab) talaba yechimini yozadi: qaysi tomonda, nimaga tayandi, qanday dalillar, qanday natija. Uni **o'zi ochiq yoki yopiq qiladi**.

| Usul | Yo'l | Nima |
|---|---|---|
| POST | `/cases/{id}/solutions` | `{"approach": "…", "side": "claimant"\|"respondent"\|null, "visibility": "public"\|"private", "name": "Aziza", "verdictId"?: "…", "code"?: "…"}` → `201 {solution}` |
| GET | `/cases/{id}/solutions` | Ochiq yechimlar va o'zimnikilar (yopiqlari ham) |
| POST | `/solutions/{sid}` | O'zimnikini tahrirlash: `{"visibility"?, "approach"?, "name"?}` yoki `{"delete": true}` |

**Qoidalar:**
- `visibility` berilmasa → **`private`** (standart yopiq, talaba o'zi ochadi).
- `approach`: 50–4000 belgi. Telefon, pasport, JSHSHIR va karta raqami saqlashdan oldin yashiriladi (`redacted`).
- So'kinish bo'lsa → `422 ethics`, yechim saqlanmaydi.
- `name`: ixtiyoriy taxallus (≤ 40 belgi). Bo'lmasa «Anonim». Egasining kimligi hech kimga ko'rinmaydi.
- Bitta casega bitta odamdan ko'pi bilan 5 ta yechim.
- Case talabaga ko'rinmasa (tasdiqlanmagan yoki yopiq va kodsiz), yechim ham qo'sha olmaydi → `404`.
- Mentor (`X-Admin-Token`) noo'rin yechimni yashiradi: `POST /solutions/{sid} {"visibility": "hidden"}`.

**Natijani biriktirish (soxtalashtirib bo'lmaydi).** `/moot/judge` javobida endi `verdictId` bor:
```json
{"verdict": {…}, "verdictId": "9c1e4b7a2f03d5e8"}
```
Yechimga `verdictId` yuborilsa, server **o'z keshidan** haqiqiy qarorni biriktiradi:
```json
"verdict": {"verified": true, "winner": "claimant", "totals": {"claimant": 76, "respondent": 72}, "side": "claimant", "won": true}
```
Talaba natijani o'zi yozib qo'ya olmaydi. Kesh 3 soat saqlanadi, shuning uchun yechimni bahsdan keyin 3 soat ichida yuborish kerak. Aks holda `verdict: null` bo'ladi va yechim baribir saqlanadi.

**Yechim namunasi:**
```json
{"id": "sol_a1b2c3d4e5", "caseId": "u_05b4c86990", "name": "Aziza", "side": "claimant",
 "approach": "Yuk xati va pretenziyaga tayandim…", "visibility": "public", "mine": false,
 "verdict": {"verified": true, "winner": "claimant", "won": true, "totals": {…}},
 "createdAt": "…", "updatedAt": "…"}
```

**Sizdan (UI):**
1. Case kartasida: «Ochiq / Yopiq» belgisi, muallifga «Havolani ulashish» va «Ochish / Yopish» tugmalari.
2. Case sahifasida «Yechimlar (N)» bo'limi: ro'yxat (taxallus, tomon, «Bahsda yutgan ✓» belgisi `verified` bo'lsa), o'zimnikida «Tahrirlash / Ochish / Yopish / O'chirish».
3. Bahs tugagach: «Yechimingizni yozing» oynasi. `verdictId` avtomatik biriktiriladi, «Boshqalar ko'rsinmi?» tanlovi.

## 8. Boshqa o'zgarish (v1.5 da va'da qilingan)

`GET /store/cases/{id}` endi `X-LexSim-Owner` sarlavhasisiz → **`422`**. Logda bunday so'rov bitta ham bo'lmagan, shuning uchun sizga ta'sir qilmaydi.
