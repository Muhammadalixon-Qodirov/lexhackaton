# «Bahs» — backend javobi (v1.4.8)

**Kimga:** frontend dasturchisi.
**Sana:** 2026-11-21.
**Holat:** ✅ v1.4.8 **o'rnatildi** (21-noyabr, 12:16). Loyiha egasining ruxsati bilan kunduzi.
- `/health` → `"version": "1.4.8"`, `features`: `moot-judge`, `moot-lines`.
- Barcha testlar o'tdi, shu jumladan 8 ta yangi «Bahs» testi.

**Jonli sinov.** Bitta `/moot/judge` so'rovi, ijara ishi, 4 chiqish:
- 1-urinish: 22 s → `503 judge_pending`;
- 15 s dan keyin xuddi shu so'rov: `200`, keshdan, model qayta chaqirilmadi.

To'liq javob: [LexSim_Bahs_judge_namuna.json](LexSim_Bahs_judge_namuna.json). Unit testlaringizni shu namunaga solishtiring.

---

## Qisqasi

| # | Vazifa | Holat |
|---|---|---|
| 1 | Xona dvigateli | ⏳ Sizdan fayllar kerak (pastda). Shaklni taxmin qilib yozmayman, `MootRoomSchema` ga aynan mos bo'lishi kerak |
| 2 | `POST /moot/judge` | ✅ Tayyor. Lekin hozirgi model **~46 s** javob beradi, 25 s yetmaydi. Yechim pastda |
| 3 | Sudyaning doimiy gaplari | ✅ 18 ta gap (kotib 1 ta, sudya 17 ta) prerender ro'yxatiga qo'shildi. Matnlar sizning hujjatingizdagidek, harfma-harf |
| 4 | STT navbati | ✅ Ustunlik v1.4.7 da qo'shilgan. ✅ 60 s gacha bo'lak qabul qilinadi. ⏳ 6 kishi bir vaqtda gapirgandagi tezlik hali o'lchanmagan |
| 5 | Ish papkalari | ⏳ Qoralama tayyorlayman, lekin yurist tekshiruvisiz bermayman |

---

## 1. Xona dvigateli: sizdan fayllar

Quyidagilarni yuboring:
- `src/contracts/moot.ts`
- `src/server/moot/engine.ts`
- `src/server/moot/cases.ts`
- `src/server/moot/judge.ts`
- `tools/qa/moot.mjs`

Javob shakli `MootRoomSchema` ga aynan mos bo'lishi kerak, aks holda Zod tekshiruvi yiqiladi. Fayllarsiz yozsam, taxmin bo'ladi.

**Rejam** (fayllar kelgach, ~1 kun):
- Marshrutlar: 3.1 dagi 6 ta, xatolar `{error: {code, message}}` shaklida, `403 not_in_room`, `404 room_not_found`.
- O'yinchi `id` si: `sha256("moot:" + code + ":" + owner)[:12]`, ega bilinmaydi.
- **Long-poll** 20 s. Xona o'zgarsa, kutayotgan so'rovlar darhol uyg'onadi.
- Bizda bitta doimiy jarayon ishlaydi, shuning uchun Redis pub/sub kerak emas.
- Taymer va yo'qolganlar server tomonida: vaqt tugashi, 45 s aloqasiz bo'lsa so'z o'tishi, 90 s bo'lsa texnik mag'lubiyat. Bularni hech kim so'rov yubormasa ham server o'zi bajaradi.
- Har o'yinchiga faqat o'z tomonining `confidential` va `task` qismi, faqat o'z jamoasining chati qaytadi. Bu test bilan tekshiriladi.
- Xona holati SQLite'da saqlanadi (sessiyalar va `/store` ham shu yerda). Qayta ishga tushirilganda davom etayotgan majlis yo'qolmaydi. Xona 3 soatdan keyin o'chadi.
- Ovoz: bitta bo'lak ≤ 3 MB, bitta xona ≤ 80 MB, diskda saqlanadi, xona bilan birga o'chadi.

**Qabul:** `tools/qa/moot.mjs` → 11/11 bizning marshrutlar bilan. Qayta ishga tushirishdan keyin majlis davom etadi.

---

## 2. `POST /moot/judge` ✅

**So'rov va javob shakli** aynan sizning 4-bo'limingizdagidek. Javob `{"verdict": MootVerdict}`.

**Qoidalar backendda majburan bajariladi.** Model faqat xom baho beradi, quyidagilarni server o'zi qiladi:

| Talab | Qanday |
|---|---|
| Mezonlar va og'irliklar | `participation` 20 · `manners` 15 · `facts` 30 · `rebuttal` 20 · `legal` 15. Ball 0..max oralig'iga tushiriladi. `totals` server tomonidan qo'shib chiqiladi |
| Durang | Farq ≤ 2 ball → `winner: null`. So'nggi gap «Bahs durang bilan yakunlandi.» |
| Haqiqiy qaror emas | «qanoatlantirilsin», «undirilsin», «rad etilsin» bo'lgan gaplar olib tashlanadi. So'nggi gap har doim «Bahsda daʼvogar/javobgar tomoni ustun keldi.» |
| Uydirma modda yo'q | `ruling` va `note` lardagi modda yoki band raqami ish materiallarida (`claim`, `facts`, `evidence`, `side`) bo'lmasa, o'sha gap o'chiriladi |
| Haqorat | Tomondan birortasi so'kinsa, o'sha tomonning `manners` bali = 0 (sud zalidagi filtrning o'zi) |
| Gapirmagan tomon | Tomonlardan biri bir marta ham gapirmagan bo'lsa, uning hamma mezoni 0 |
| `players` | `words` va `speeches` bayonnomadan **server** hisoblaydi. `note` modeldan keladi |
| STT xatolari | Promptda: «imlo uchun ball kamaytirma» |
| `ruling` | 3–6 gap |

**Barqarorlik.** Model hozir brauzer orqali ishlaydi va `temperature` ni sozlab bo'lmaydi. Shuning uchun: **bir xil bayonnoma → bir xil natija** kesh orqali kafolatlanadi (3 soat). Qayta so'ralsa, model qayta chaqirilmaydi.

### ⚠️ Vaqt: 25 s yetmaydi

Hozirgi til modeli vaqtinchalik: AIHUB, ChatGPT/Gemini brauzer orqali. Jonli o'lchov (ijara ishi, 4 chiqish): **46 s**. Natija sifatli chiqdi: javobgar 86 : 77 da ustun, izohlar mazmunli, uydirma modda yo'q.

Majlis qarorsiz qolmasligi uchun shunday qildim:
1. Server **22 s** kutadi. Shu vaqtda tayyor bo'lsa → `200 {verdict}`.
2. Tayyor bo'lmasa → `503 {"error": {"code": "judge_pending", …}}` va `Retry-After: 15`. Model **fonda yozishda davom etadi**.
3. **Xuddi shu so'rovni** qayta yuborsangiz: tayyor bo'lsa darhol `200`, model qayta chaqirilmaydi. Hali tayyor bo'lmasa, yana `judge_pending`.
4. Model xato bersa → `503 judge_unavailable`. Shunda qoida bahosini ko'rsating.

**Sizdan:**
- `judge_pending` kelsa, qoida bahosini darhol ko'rsating («Dastlabki baho, sudya qarori yozilmoqda…»).
- `Retry-After` bo'yicha 90 s gacha qayta so'rang.
- `200` kelsa, ekrandagi bahoni sudya qaroriga almashtiring va `ruling` ni ovoz bilan o'qiting.

Tez LLM API kaliti (Gemini yoki Groq) ulansa, kutilgan vaqt ~5–10 s va hammasi birinchi so'rovdayoq `200` bo'ladi. Bu qaror loyiha egasida (E5).

**`X-LexSim-Owner`** boshqa marshrutlardagidek majburiy: 8–64 belgili hex xesh. Aks holda `422`.

**Boshqa javoblar:**
- `401`: kalit yo'q;
- `422 validation_failed`: `case`, `transcript` yoki `players` yo'q, yoki bayonnomada tomonlarning chiqishi yo'q;
- `429`: so'rov juda ko'p, bitta ega uchun daqiqasiga 20 ta.

`/health` → `moot` maydoni: `calls`, `ok`, `cached`, `pending`, `failed`, `last_ms`.

---

## 3. Sudyaning doimiy gaplari ✅

5-bo'limdagi 18 gap (kotib `female`, qolgani `elder_m`) aynan shu matnda prerender ro'yxatiga qo'shildi. O'rnatilgandan keyin avtomatik render ularni yozadi.

- Apostroflar sizning matningizdagidek: `ʻ` (U+02BB) va `ʼ` (U+02BC).
- Biror gapni o'zgartirsangiz, menga ayting.

Ishga bog'liq ochilish gapi («Sud majlisi ochiq deb eʼlon qilinadi. {daʼvogar}ning…») ish papkalari tayyor bo'lgach har ish uchun render qilinadi.

**Qabul:** render tugagach `voice-coverage.mjs` bu gaplarni `hit` deb ko'rsatsin.

---

## 4. STT navbati

| Talab | Holat |
|---|---|
| STT prerender'dan ustun | ✅ v1.4.7: STT kelsa, render navbatdagi gapni boshlamaydi va 25 s davomida pauzada turadi |
| 60 s gacha bo'lak | ✅ Chegara 3 MB. 60 s, 16 kHz, mono, 16-bit WAV ≈ 1,9 MB, sig'adi |
| 30 s audio → ≤ 4 s (p95) | ⏳ O'lchanmagan. GPU bitta. 6 kishi bir vaqtda gapirsa, so'rovlar navbat bilan bajariladi. Bahsda bir vaqtda faqat bitta odam gapiradi, shuning uchun amalda navbat qisqa bo'lishi kerak |

**Sizdan:** «Bahs» ishga tushgach, 30 s lik 10 ta bo'lakni `stt-timing.mjs` bilan o'lchab yuboring.

---

## 5. Ish papkalari

`GET /moot/cases` va `GET /moot/cases/{id}` sizning `MootCase` shaklingizda bo'ladi.

**Mavzular 2025-yilgi sud statistikasiga qarab tanlandi** (stat.sud.uz, iqtisodiy sudlar, shartnomaviy nizolar):

| Mavzu | Ulushi |
|---|---|
| yetkazib berish | 24 % |
| kommunal xizmatlar | 19 % |
| kredit | 13 % |
| oldi-sotdi | 11 % |
| ijara | 5 %, hozirgisi |

Asos: haqiqiy ishlar bo'yicha tadqiqotimiz. Nomlar va summalar o'zgartiriladi. Har tomonga 2–4 ta maxfiy fakt beriladi.

**Shart:** sizning talabingiz bo'yicha **yurist tekshiruvidan keyin** beriladi. Modda raqami faqat manbasi (lex.uz) bilan. Qoralamani shu hafta tayyorlayman. Yurist bilan tekshirish vaqtini loyiha egasi aytadi.

---

## Savollaringizga javob

1. **Long-poll yoki WebSocket?** Long-poll bilan boshlaymiz, roziman. WebSocket keyingi bosqichda.
2. **Model va vaqt?** Hozir AIHUB (ChatGPT/Gemini), ~46 s, shuning uchun 25 s yetmaydi. Yechim 2-bo'limda: `judge_pending` va qayta so'rash. Tez API kaliti bilan ~5–10 s.
3. **Redis?** Yo'q, kerak ham emas. SQLite diskda va bitta doimiy jarayon. Qayta ishga tushirishga chidaydi.
4. **5 ta ish papkasi?** Qoralama shu hafta. Yurist tekshiruvi loyiha egasiga bog'liq.

## Tayyor bo'lgach yuboraman

- versiya raqami va marshrutlar ro'yxati;
- ~~`/moot/judge` dan haqiqiy javob namunasi~~ ✅ yuborildi: `LexSim_Bahs_judge_namuna.json`;
- oldindan ovozlangan gaplar keshda ekanining tasdig'i.

---

# v1.5.0 — «Nimaga asoslanib N ball?»: tushuntiriladigan baholash

**Metodika:** [reports/LexSim baholash metodikasi.md](reports/LexSim%20baholash%20metodikasi.md). **Holat:** kod tayyor, serverdagi nusxada jonli sinovdan o'tdi. O'rnatish vaqti alohida xabar qilinadi.

## Nima o'zgardi

Ballni endi **AI bermaydi.** AI faqat 17 ta aniq band bo'yicha «ha / yo'q / qo'llanmaydi» deydi va **bayonnomadan so'zma-so'z iqtibos** keltiradi. Ballni server hisoblaydi:

1. **Qoida bandlari** (AI'siz): «Hurmatli sud» murojaati, so'kinish, materiallardagi normani keltirgani, manbasiz modda, har bir so'zda gapirgani, muzokarada chiqqani.
2. **AI bandlari**: raqibning aniq dalilga javob berdimi, norma faktga qanday qo'llanishini tushuntirdimi, uydirma fakt aytdimi va hokazo. AI keltirgan iqtibos bayonnomada **topilmasa**, band «bajarilmadi» deb hisoblanadi va ish mentorga belgilanadi.
3. Mezon bali = bajarilgan bandlar og'irligi ÷ musbat og'irliklar yig'indisi × mezon maksimumi.
4. Bandlar tartibi har safar aralashtiriladi (tartib ta'sirini kamaytirish uchun).

## ⚠️ Mezon og'irliklari o'zgardi

| Mezon | Avval (sizning hujjatingiz) | Endi | Manba |
|---|---|---|---|
| `legal` | 15 | **30** | Jessup: huquq 30; SQE2: huquqni qo'llash baholashning yarmi |
| `rebuttal` | 20 | **25** | Jessup: savollarga javob 25; Vis: savollarni boshqarish |
| `facts` | 30 | **20** | Jessup: faktlar 20; IPK 68 |
| `participation` | 20 | **15** | Vis: tayyorgarlik; Berkeley: kirish va yakun |
| `manners` | 15 | **10** | IPK 167; etika qoidalari 55-band; Berkeley: nutq 10 |

Sabab: avvalgi og'irliklarning manbasi yo'q edi. Yangilari har biri xalqaro moot va malaka imtihoni standartiga bog'langan. `criteria[].max` javobda keladi, shuning uchun frontend o'zi moslashadi. Qoida bahongizdagi og'irliklarni ham shunga moslashtiring. Loyiha egasi eskisini qoldirishni xohlasa, bu `rubrics.json` da bitta qatorni o'zgartirish.

## API

**`POST /moot/judge`** javobida endi:
```json
{"verdict": {…}, "verdictId": "…",
 "explain": {
   "rubric": "moot", "version": "moot-2026.11.1", "runs": 1, "needsMentor": false, "routing": [],
   "sides": {"claimant": {
      "total": 31, "band": [31, 31],
      "criteria": [{"id": "facts", "label": "Faktlar va dalillar", "max": 20, "score": 15, "basis": ["jessup", "vis", "ipk68"]}],
      "items": [{"id": "F2", "dim": "facts", "ask": "Ish materiallaridagi aniq dalil hujjatini nomlab, u nimani isbotlashini aytdi",
                 "weight": 3, "method": "ai", "met": "yes", "agree": 1.0, "basis": ["ipk68", "jessup"],
                 "evidence": [{"turnId": "3", "quote": "fakturalar javobgar direktori tomonidan imzolangan", "match": 1.0}],
                 "why": "Imzolangan fakturalarni nomlab, ular mol topshirilganini isbotlashini aytdi."}]}}}}
```
- `evidence[].turnId` — bayonnomadagi `seq`. Uni ekranda shu gapga havola qiling.
- `band` — ishonch oralig'i. AI yurishlari kelishmasa yoki iqtibos tasdiqlanmasa, `[pastki, yuqori]` bo'lib chiqadi.
- `needsMentor` va `routing[].reason` — mentorga yuborish sababi: iqtibos topilmadi, yurishlar kelishmadi yoki etika buzildi.

**`GET /rubrics/moot`** (kalitsiz): barcha mezonlar, 17 ta band, og'irliklar, manbalar (`sources`: nom, URL, izoh). «Nimaga asoslanib?» oynasi shundan chiziladi.

## Talabaga ko'rsatish («Nega N ball?»)

Har bir mezonni bosganda:
1. Mezon nomi, ball va manba («Jessup Oral Judging Rubric 2026 — huquq 30»).
2. Bandlar ro'yxati: ✓ / ✗ / «qo'llanmaydi», og'irligi, **talabaning o'z gapi** (`quote`, havolasi bilan) va `why`.
3. ✗ bandlarning eng og'iri: «Keyingi safar: …» (`players[].note` da ham bor).
4. `needsMentor` bo'lsa: «Bu baho mentor tomonidan tekshiriladi» belgisi.

**Muhim:** AI bahosi hozircha **mashq va fikr-mulohaza** uchun, rasmiy baho emas. Mentorlar 30–50 ta bahsni baholab, AI bilan kelishuv o'lchanguncha shunday qoladi (metodika, 4-bo'lim). Ekranda ham shunday deb yozing.

## Vaqt

Jonli sinov: **75 s** (17 band, AIHUB). `judge_pending` → qayta so'rash tartibi o'zgarmadi. Retry'ni 120 s gacha uzaytiring.

---

## v1.5.0 qo'shimcha: xavfsizlik tuzatishlari (kod tekshiruvidan keyin)

1. **`/moot/judge` tanasida yangi ixtiyoriy maydon `participants`** - kim bu qarorni yechimiga biriktira oladi:
   ```json
   "participants": [{"owner": "<talaba xeshi>", "side": "claimant"}, {"owner": "<…>", "side": "respondent"}]
   ```
   - Yechimga `verdictId` biriktirilganda server tekshiradi: so'rovchi shu ro'yxatda bormi va `caseId` qaror chiqqan casega tengmi.
   - **Tomon ro'yxatdan olinadi**, talaba o'zi tanlay olmaydi.
   - `participants` yuborilmasa, qarorni faqat `/moot/judge` ni chaqirgan ega biriktira oladi.
   - `case.id` ga case-lab'dagi case `id` sini qo'ying (masalan `u_05b4c86990` yoki `s_ijara`).
2. **Tana chegarasi** `/moot/judge` va `/cases` uchun 16 KB dan **512 KB** ga oshirildi. Uzun bahs bayonnomasi endi `413` bermaydi.
3. **Etika chegarasi qarorda ham qo'llanadi:** so'kingan tomonning jami bali 40 dan oshmaydi va u bahsda yuta olmaydi.
4. **Mentor yashirgan yechim** (`visibility: "hidden"`): muallif uni qayta ocha olmaydi (`403 hidden_by_mentor`), lekin o'chira oladi.
5. **Mentor yopiq caseni tasdiqlay olmaydi**, faqat tekshiruvdagisini. Yopiq case qayta yopilganda **yangi `shareCode`** chiqadi, eski havola ishlamay qoladi. Kod endi uzunroq (12 belgi).
6. **Noto'g'ri tuzilgan case JSON** endi `500` emas, `422 validation_failed` qaytaradi.
7. **Shaxsiy ma'lumot** qo'lda kiritilgan case maydonlarida va yechim taxallusida ham yashiriladi. Kichik harfli yoki kirillcha pasport, `.` bilan ajratilgan telefon, shahar telefoni va Telegram `@username` ham qo'shildi.
