# Sohalar va caselar: `LexSim_Sohalar_Frontend_javob.md` ga backend javobi

**Kimga:** frontend dasturchisi.
**Sana:** 2026-11-21.
**Server:** hozir v1.4.9. Pastdagi tuzatishlar v1.5.0 ga kiradi (ochiq/yopiq caselar, yechimlar, tushuntiriladigan baholash - `LexSim_Sohalar_Caselar_Backend.md` 6-8-bo'limlar, `LexSim_Bahs_Backend_javob.md` oxirgi bo'lim). O'rnatish vaqti alohida xabar qilinadi.

Ish yaxshi chiqibdi, ayniqsa maxfiy faktlarni serverda qo'shimcha tozalash va `GET /moot/cases/{id}` ni brauzerga bermaslik. Rahmat.

---

## 1. Savollaringizga javob

| # | Savol | Javob |
|---|---|---|
| 1 | Ro'yxat shakli | **Doim** `{"cases": [...]}`: `GET /cases`, `?scope=review`, `?scope=mine`, `GET /moot/cases`. Massiv qaytmaydi |
| 2 | Bitta case | **Doim** `{"case": {...}}`. Qoralama - `{"draft": {...}}`, yechimlar - `{"solutions": [...]}` / `{"solution": {...}}` |
| 3 | `modes` | Ro'yxatda har bir caseda bor edi. **v1.5.0 dan bitta caseda ham bor.** Qiymati sohaning `modes` i, tizim casesida - o'ziniki. `moot` ni faqat `status: "approved"` (yoki tizim) caseda ko'rsatish to'g'ri |
| 4 | `court` va `/scenarios` | Ijara tizim casesining `id` si `s_ijara`, ssenariy `id` lari boshqa. **v1.5.0 dan** tizim casesida `scenarioIds` bor: `{"claimant": "sud-ijara-davogar", "respondent": "sud-ijara-javobgar"}`. «Sud zali» tugmasi tanlangan tomonga mos ssenariyni ochsin. `scenarioIds` yo'q caseda «Sud zali» tugmasini ko'rsatmang |
| 5 | `POST /cases` tanasi | To'g'ri, faqat **`domain` majburiy**: `{"domain": "supply", "case": {...}, "visibility": "public" \| "private"}`. `draftId` zarar qilmaydi, lekin ishlatilmaydi. `id`, `source`, `status`, `mine` yuborilsa ham e'tiborga olinmaydi |
| 6 | Uzun chiziq | **v1.5.0 dan** case-lab, «Bahs» sudyasi, rubrika va AI matnlarida «-» va «-» hammasi «-» ga almashtiriladi: soha `note` lari, AI yozgan case matnlari, qaror, izohlar. Sud zalidagi ovozlashtirilgan gaplarga tegmadim, chunki ular matn bo'yicha keshlangan (o'zgarsa, ovoz qayta yozilishi kerak). Ularni ham almashtirish kerak bo'lsa, ayting - kechasi qayta render bilan qilaman |

---

## 2. Kodekslar: bazaga **to'liq** yuklanmoqda

Taklifingiz uchun rahmat. Biz to'plamni lex.uz'dan **to'liq** olib, RAG bazasiga qo'shyapmiz. Sizning fayllaringizdagi bir nechta modda emas, butun hujjat:

| Kod | Hujjat | lex.uz | Moddalar |
|---|---|---|---|
| `MK` | Mehnat kodeksi (O'RQ-798, 2022) | 6257288 | 594, jumladan 8¹ (O'RQ-1189, 13.11.2026) |
| `JPK` | Jinoyat-protsessual kodeksi | 111463 | 773 |
| `JK` | Jinoyat kodeksi | 111453 | 406 |
| `MUR` | Murojaatlar to'g'risida (O'RQ-445) | 3336169 | 39 |
| `DBQ` | Davlat boji to'g'risida (O'RQ-600) | 4680944 | 33 |
| `ADQ` | Advokatura to'g'risida (349-I) | 54503 | 30, jumladan 7¹ (advokat so'rovi) |
| `AKQ` | Advokatlik faoliyati kafolatlari (721-I) | 29626 | 12 |

- Jami 2372 ta bo'lak, embedding `bge-m3` (bazadagi model bilan bir xil). Hozir 896/2372, ~1,5 soatda tugaydi.
- Mavjud FK, IPK, FPK qatorlariga **tegilmadi**.
- Tugagach, v1.5.0 bilan birga ishga tushadi. Shundan keyin mehnat (`labour`), jinoyat (`theft`) va DXM caselari ham moddali bo'ladi.
- `ORDER.json` (order shakli): normativ hujjat emas, bazaga qo'shmadik. Eslatma: PQ-263 (30.05.2022, 4-band «v») bo'yicha 2023-yil 1-fevraldan advokat so'roviga **order nusxasini ilova qilish talab qilinmaydi**, QR-kodli elektron order bor. Qonun matni (349-I, 7¹-modda) hali yangilanmagan. Simulyatorda order nusxasi yo'qligi uchun ball ayirmang.

Sizning `legal/sources` to'plamingiz va bizning bazamiz bir xil manbadan (lex.uz) olingan. Moddalar `normId` si bilan mos: `MK-174`, `JPK-324`, `MUR-6`. Chalkashmaslik uchun bitta manba sifatida bizning `/rubrics` va case `legal[].url` ni ishlating.

---

## 3. «Bahs»: «FK 333-modda va 120 mln so'm ish materiallarida yo'q edi»

Bu sizning ijara casesingizdan emas, **mening sinov so'rovimdan** edi. Unda `case.claim` = «120 mln so'm qarz va penya undirish», `facts[0].text` = «…FK 333-modda». Ya'ni ikkalasi ham shu so'rovning materiallarida bor edi va filtr ularni to'g'ri o'tkazdi.

Filtr qanday ishlaydi (v1.5.0):
1. Qarorda yoki izohda modda raqami bo'lsa, u `case` ning `claim`, `facts`, `evidence`, `side` matnlarida bo'lishi kerak, aks holda o'sha gap o'chiriladi.
2. **Endi ballni AI bermaydi**, faqat bandlar bo'yicha «ha/yo'q + bayonnomadan iqtibos». Masalan, `F4` bandi - «ish materiallarida yo'q faktni haqiqat sifatida aytdi» - **talabaning** uydirmasi uchun ball ayiradi. AI keltirgan iqtibos bayonnomada topilmasa, band bajarilmagan hisoblanadi va ish mentorga belgilanadi.
3. Case-lab caselari ham shu filtrdan o'tadi. AI case tuzganda modda faqat RAG ro'yxatidan, tahrirda faqat bazadagi `normId`.

Haqiqiy ijara casesingiz bilan bitta `/moot/judge` so'rovini (bayonnoma bilan) yuboring. Agar u yerda ham materialda yo'q narsa chiqsa, aniq misol bilan ko'ramiz.

---

## 4. Qabul (v1.5.0 o'rnatilgach)

Sizning 5-bo'limingizdagi to'rt qadam to'g'ri. Qo'shimcha:

5. Yopiq case: `visibility: "private"` → `shareCode` → boshqa brauzerda `?code=` bilan ochiladi, kodsiz `404`.
6. Yechim: bahsdan keyin `POST /cases/{id}/solutions` (`verdictId` bilan) → `verdict.verified: true`. Ochiq bo'lsa boshqa brauzerda ko'rinadi, yopiq bo'lsa ko'rinmaydi.
7. «Nega N ball?»: `/moot/judge` → `explain.sides.*.items[].evidence[].quote` talabaning o'z gapi. `GET /rubrics/moot` → mezonlar va manbalar.
8. Bahs mezonlari og'irligi endi `legal 30, rebuttal 25, facts 20, participation 15, manners 10` (Jessup 2025 baholash varaqasi asosida). `criteria[].max` dan o'qing, qoida bahongizni ham shunga moslang.
