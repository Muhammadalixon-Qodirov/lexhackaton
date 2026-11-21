# Sohalar va caselar - frontend javobi (v1.4.9 "case-lab")

**Kimga:** backend dasturchisi.
**Sana:** 2026-11-21.
**Holat:** frontend tayyor va sinovdan o'tdi. `/domains` jonli serverdan keladi; case marshrutlari kalit talab qiladi, ular soxta javoblar bilan sinaldi (8/8). Netlify'da kalit bilan jonli tekshiriladi.

---

## 1. Nima qilindi

| Sizning 4-bo'limingiz | Frontendda |
|---|---|
| 1. Sohalar ekrani | `/sohalar`: guruhlar (Iqtisodiy sud, Fuqarolik ishlari, Jinoyat ishlari, Davlat xizmatlari), `share2025` bo'yicha tartib va ulush chizig'i, `modes`, `codes`, `note` |
| 2. Soha ichida caselar | `/sohalar/{id}`: "Hammasi / Meniki", belgilar "Tizim", "Foydalanuvchi", "Meniki", "Tekshiruvda" / "Rad etilgan"; case varag'ida `modes` bo'yicha tugmalar (Sud zali / Ish yo'li / Bahs) va `disclaimer` doim |
| 3. "Case qo'shish" | 2.2 dagi oqim: hikoya (80-4000 belgi), "AI caseni tuzyapti…" va vaqt, `Retry-After` bo'yicha so'rash (keyin har 9 s, ~3,5 daqiqa chegara), `questions` + "Javob berib, qayta tuzish", tahrirlanadigan forma, `legal` (faqat olib tashlash mumkin, qo'shib bo'lmaydi), `balance`, `issues`, "maxfiy fakt 2-4", `sources: 0` va `redacted` ogohlantirishlari, "Saqlash" -> `POST /cases` (`draftId` bilan) |
| 4. Mentor sahifasi | `/mentor`: tekshiruv navbati, "Tasdiqlash", "Rad etish" (izoh majburiy) |
| 5. Bahs | xona ochishda case tanlanadi (`GET /moot/cases`); server `GET /moot/cases/{id}` ni o'zi oladi, har o'yinchiga faqat o'z tomonining maxfiy faktlari beriladi |

**Xavfsizlik:**
- Brauzer faqat bizning `/api/v1/library/*` ga murojaat qiladi. `X-LexSim-Key`, `X-LexSim-Owner` (xesh) va `X-Admin-Token` faqat serverda qo'shiladi.
- Boshqa odamning casesida `confidential` va `balance` serverimizda ham **qo'shimcha** tozalanadi (siz yuborib qo'ysangiz ham chiqmaydi).
- `GET /moot/cases/{id}` (to'liq case) brauzerga hech qachon bormaydi.

**Mentor kirishi (vaqtincha):** umumiy kod (`LEXSIM_MENTOR_CODE`, faqat Netlify'da) -> imzolangan httpOnly cookie 12 soatga; admin token (`LEXSIM_ADMIN_TOKEN`) serverda qoladi. Mentor hisoblari masalasi hal bo'lgach almashtiramiz.

---

## 2. Sizdan aniqlik kerak

1. **Ro'yxat javobi shakli.** `GET /cases`, `GET /cases?scope=review`, `GET /moot/cases` qanday qaytadi: `{"cases": [...]}` yoki massiv? Hozir ikkalasini ham qabul qilaman, lekin aniq ayting.
2. **Bitta case:** `{"case": {...}}` yoki obyektning o'zi? (Ikkalasi qabul qilinadi.)
3. **`modes` har bir caseda bormi?** Hozir case'da bo'lmasa, sohaning `modes` i olinadi; `moot` faqat tasdiqlangan yoki tizim casesida ko'rsatiladi.
4. **`court` rejimi:** ijara tizim casesining `id` si `/scenarios` dagi ssenariy `id` siga tengmi? Teng bo'lsa, "Sud zali" aynan o'sha ssenariyni ochadi; aks holda tasodifiy iqtisodiy ssenariy ochiladi.
5. **`POST /cases` tanasi:** biz tahrirlangan caseni `draftId` bilan yuboramiz (`id`, `source`, `status`, `mine` yuborilmaydi). To'g'rimi?
6. **Matnlarda uzun chiziq.** `note` va boshqa matnlarda "—" bor. Loyiha egasining talabi: qisqa chiziq "-". Iltimos, matnlarni "-" bilan bering (frontend backend matnini o'zgartirmaydi).

---

## 3. "Bazada yo'q" kodekslar - bizda bor

Siz yozgansiz: Mehnat kodeksi, JPK, JK va ZRU-445 (Murojaatlar to'g'risida) bazada yo'q. Bizning `legal/sources` to'plamida ular lex.uz'dan **so'zma-so'z**, skript bilan olingan (2026-11-20/21). `manbalar/` papkasida:

| Fayl | Hujjat | lex.uz | Tahrir | To'plamda |
|---|---|---|---|---|
| `MK.json` | Mehnat kodeksi | -6257288 | 13.11.2026 | 11 modda (161, 163, 170, 171, 174, 300, 301, 312-314, 560) |
| `JPK.json` | Jinoyat-protsessual kodeksi | -111460 | 15.10.2026 01 | 241 modda |
| `JK.json` | Jinoyat kodeksi | -111453 | 03.11.2026 | 210-214, 238 |
| `MUROJAAT.json` | "Jismoniy va yuridik shaxslarning murojaatlari to'g'risida" (ZRU-445) | -3336169 | 15.10.2026 01 | 25 modda |
| `DAVLATBOJI.json`, `ADVOKATURA.json`, `ADVKAFOLAT.json`, `ORDER.json` | Davlat boji, Advokatura, advokat kafolatlari, order shakli | | | |

Har bir yozuvda: `number`, `title`, `text`, `url` (moddaning lex.uz langari), hujjatda `editionSelected`, `retrievedAt`. Format `README_toplam.md` da.

**Taklif:** RAG bazangizga shu fayllarni qo'shing. MK va JK to'liq emas; to'liq kerak bo'lsa, `legal/tools/fetch_lex.sh` + `build_sources.py` bilan butun kodeksni oling (yoki ayting, men olib beraman). Shunda mehnat, jinoyat va DXM caselari ham moddali bo'ladi.

---

## 4. Bahs bo'yicha eslatma

Oldingi xatdagi masala ochiq: `/moot/judge` namunasida "FK 333-modda" va "120 mln so'm" ish materiallarida yo'q edi (`LexSim_Bahs_Backend_v2.md`, 2-bo'lim). Case-lab'dan chiqqan caselar bahsga chiqqanda bu filtr yanada muhim.

---

## 5. Qabul (siz o'rnatgandan keyin, Netlify'da)

1. `/sohalar/supply` -> "Case qo'shish" -> qoralama 45-95 s -> saqlash -> "Tekshiruvda".
2. `/mentor` -> navbatda ko'rinadi -> tasdiqlash.
3. Boshqa brauzerdan: case ko'rinadi, maxfiy faktlarsiz.
4. `/bahs?case=<id>` -> xona -> ikki o'yinchi o'z tomonining maxfiy faktlarini ko'radi.
