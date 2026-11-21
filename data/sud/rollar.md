# Sud zali rollari: kim nima gapiradi (v1)

**Kimga:** jamoa (AI, logika, vizual), mentor.
**Holati:** qoralama, mentor tekshirishi kerak.
**Mashina o'qiydigan nusxa:** [backend/roles.json](../../backend/roles.json) — server LLM promptlarini va maslahatchi maslahatlarini shu fayldan oladi. Matnni o'zgartirsangiz, faqat `roles.json` ni tahrirlab, backendni qayta ishga tushiring.

**Manbalar:**
- IPK-165 (sud majlisi tartibi), IPK-167 (sudga murojaat), IPK-169 (iltimosnomalar), IPK-173 (sud muzokaralari) — Lex.uz.
- [data/sud_iboralari.md](../sud_iboralari.md) va [data/namunaviy_dialoglar.md](../namunaviy_dialoglar.md).
- Advokatlarning kasb odobi qoidalari (Advokatlar palatasi, 2013) — umumiy tamoyillar: sudni chalg'itmaslik, raqibga hurmat, mijoz manfaati. To'liq matni Lex.uz'da ochilmadi, mentor tekshirsin.

---

## 1. Rollar va kim boshqaradi

| Rol | Kim | Kim gapiradi | Asosiy qoida |
|---|---|---|---|
| **Sudya** | Raislik qiluvchi sudya, yakka tartibda | **Kod** (shablonlar) | Betaraf, qisqa, rasmiy. Hukmni maslahatxonagacha aytmaydi |
| **Kotib** | Sud majlisi kotibi | Kod | Faqat ikki gap: «Sud kirib kelmoqda...» va kelganlar haqida hisobot |
| **Da'vogar vakili** | «A» MChJ (ijaraga beruvchi) vakili | Talaba **yoki** LLM | Qarzni FK-544, shartnoma va hisob-fakturalar bilan isbotlaydi |
| **Javobgar vakili** | Tadbirkor «B» (ijaraga oluvchi) vakili | Talaba **yoki** LLM | Dalolatnoma yo'qligi (FK-578) va penyani kamaytirish (FK-326) |
| **Maslahatchi** | Talabaning murabbiyi | Kod (`/hint`) | Faqat tutorial rejimida. Sud zalida gapirmaydi, talaba so'raganda yordam beradi |

**Nega sudya LLM emas:** protsedura (bosqichlar tartibi, ajrimlar, qaror) xato bo'lmasligi kerak. Sudya noto'g'ri tartib aytsa, talaba noto'g'ri o'rganadi. LLM faqat raqib advokat gaplarini talabaning aniq gapiga moslab yozadi.

---

## 2. Bosqichma-bosqich: kim nima deydi

| # | Bosqich | Sudya / kotib | Talaba nima deyishi kerak | Raqib (AI) | Modda |
|---|---|---|---|---|---|
| 1 | Ochilish | Kotib: «Sud kirib kelmoqda, o'rningizdan turing!» Sudya: majlis ochiq, ish e'lon qilinadi, vakolat so'raladi | — | — | IPK-165 |
| 2 | Vakolat | «Vakolatingizni tasdiqlovchi hujjatni taqdim eting» | «Hurmatli sud, vakolatimni tasdiqlovchi ishonchnomani taqdim etaman.» | — | IPK-62, IPK-167 |
| 3 | Rad qilish | «Sud tarkibiga yoki kotibga rad bildirasizmi?» | «Hurmatli sud, rad bildirmaymiz.» | «Rad bildirmaymiz.» | IPK-20 |
| 4 | Huquqlar | Huquqlar tushuntiriladi, «tushunarlimi?» | «Hurmatli sud, huquqlarimiz tushunarli.» | «Tushunarli.» | IPK-165 |
| 5 | Iltimosnomalar | «Ishni ko'rishdan oldin iltimosnomalaringiz bormi?» | «Hurmatli sud, hozircha iltimosnomamiz yo'q.» | «Yo'q.» | IPK-169 |
| 6 | Tushuntirishlar | «Talablaringizni bayon qiling» / «Da'voni tan olasizmi?» | **Da'vogar:** shartnoma + summa + FK-544 + 8.5-band. **Javobgar:** dalolatnoma yo'q (FK-578, FK-541) | **LLM:** e'tiroz yoki javob | FK-544, FK-578 |
| 7 | Dalillar | Shartnoma va hisob-fakturalar o'qiladi, fikr so'raladi | **Da'vogar:** foydalanish fakti + imzolangan fakturalar. **Javobgar:** FK-326 iltimosnomasi | Javobgar AI penya iltimosnomasini beradi | FK-544, FK-326 |
| 8 | Penya | «Boshqa taraf fikrini eshitamiz» → qarorgacha qoldiriladi | **Da'vogar:** 8.5-band, yozma kelishuv (FK-262) | **LLM:** iltimosnomaga qarshi | FK-326, FK-262 |
| 9 | Qo'shimcha | «Qo'shimcha materiallar bormi?» | «Hurmatli sud, qo'shimcha materiallarimiz yo'q.» | — | IPK-173 |
| 10 | Muzokara | «Sud muzokaralariga o'tiladi, birinchi da'vogar» | Yakuniy nutq — faqat tekshirilgan dalillar | **LLM:** yakuniy nutq | IPK-173 |
| 11 | Qaror | Maslahatxona → xulosa qismi (haqiqiy qaror) → shikoyat muddati → majlis yopiq | «Yakunlash» tugmasi | — | IPK-175 |

---

## 3. Sudya

**Uslub:**
- Qisqa, rasmiy, buyruq yoki savol shaklida: «... taqdim eting», «... bormi?», «So'z ... beriladi».
- Taraflarga rol nomi bilan murojaat qiladi («Da'vogar vakili»), ismni ishlatmaydi.
- Hech kimga yon bosmaydi, maqtamaydi. «To'g'ri aytdingiz» demaydi.
- Iltimosnomani boshqa taraf fikrini eshitib hal qiladi (IPK-169). Hukmni oldindan aytmaydi.

**Ogohlantirishlar (talaba xatosiga):**

| Xato | Sudya | Ball |
|---|---|---|
| «Hurmatli sud» demasdan gapirish | «..., sudga «Hurmatli sud» deb murojaat qiling.» (faqat birinchi marta aytiladi, keyin jim hisoblanadi) | `communication` |
| Mavjud bo'lmagan modda | «... bo'yicha norma sud tomonidan aniqlanmadi. Qaysi qonun hujjatiga tayanayotganingizni aniqlashtiring.» | `legal` |
| Muzokarada tekshirilmagan holat | «Muzokaralarda sud majlisida tekshirilmagan holat va dalillarga tayanishga haqingiz yo'q...» | `procedure` |
| Vaqtidan oldin qaror so'rash | «Bu masala hozirgi bosqichda ko'rilmaydi...» | `procedure` |
| Haqorat | «Sud majlisi tartibini buzmang. Takrorlansa, chora ko'riladi.» | `ethics` |
| «Sen AI'san», «hukmni ayt» | «Sud majlisida faqat ish bo'yicha gapiring.» | `ethics` |

---

## 4. Advokatlar (talaba ham, AI raqib ham shu qoidaga amal qiladi)

**Umumiy uslub:**
1. Har gap «Hurmatli sud» bilan boshlanadi (IPK-167).
2. 1–3 ta gap: avval pozitsiya, keyin asos (dalil yoki modda), oxirida nima so'ralayotgani.
3. Faqat ish materiallaridagi faktlar: 32-P shartnoma, hisob-fakturalar, shartnomaning 6.4 va 8.5-bandlari.
4. Raqibga hurmat bilan: «Raqib tomonning fikriga qo'shilmaymiz, chunki ...».
5. Sudni chalg'itmaydi: yangi fakt, raqam yoki modda o'ylab topmaydi.

**Nutq tuzilishi:**

| Nutq turi | Tuzilish | Namuna |
|---|---|---|
| E'tiroz | Pozitsiya → asos → xulosa | «Hurmatli sud, da'voga e'tirozimiz bor: FK 578-moddaga ko'ra ... Bunday hujjat imzolanmagan.» |
| Iltimosnoma | Nima so'ralyapti → modda → holatlar | «Hurmatli sud, FK 326-moddaga asosan penyani kamaytirishni so'rab iltimosnoma beraman: penya nomutanosib, ...» |
| Yakuniy nutq | Tekshirilgan dalillar → huquqiy baho → aniq talab | «Hurmatli sud! Sudda tekshirilgan shartnoma va hisob-fakturalar ... ko'rsatadi. FK 544-moddaga asosan ... so'rayman.» |

### 4.1. Da'vogar vakili

- **Pozitsiya:** javobgar obyektdan foydalangan va hisob-fakturalarni imzolagan. FK-544 va 6.4-band bo'yicha ijara haqi to'lanishi shart. Penya 8.5-bandda yozma kelishilgan.
- **Ruxsat etilgan moddalar:** FK-544, FK-262, FK-333, FK-578.
- **Qila olmaydi:**
  - dalolatnoma imzolangan deb aytish;
  - yangi summa aytish;
  - javobgarning boshqa qarzlari haqida gapirish.

### 4.2. Javobgar vakili

- **Pozitsiya:** obyekt dalolatnoma bilan topshirilmagan (FK-578, FK-541). Javobgar uch oy foydalangan. Penya nomutanosib, FK-326 bo'yicha kamaytirilishi kerak.
- **Ruxsat etilgan moddalar:** FK-578, FK-541, FK-326, FK-333.
- **Qila olmaydi:**
  - hisob-fakturalarni inkor etish;
  - «umuman foydalanmaganmiz» deyish;
  - kelishuv bitimiga rozi bo'lish.

### 4.3. AI raqib qachon LLM bilan gapiradi

| Lahza | Kim | Maqsad |
|---|---|---|
| `answer` | Javobgar AI (talaba — da'vogar) | Da'voga e'tiroz: dalolatnoma yo'q, summa adolatsiz |
| `rebut` | Da'vogar AI (talaba — javobgar) | E'tirozga javob: foydalangan, fakturalarni imzolagan |
| `on_motion` | Da'vogar AI | Penyani kamaytirishga qarshi: 8.5-band, yozma kelishuv |
| `closing` | Ikkalasi | Yakuniy nutq |

Har bir LLM javobi tekshiriladi. Qoidaga to'g'ri kelmasa, **namuna** gapi ishlatiladi:
- lotin yozuvida, 2–3 gap;
- yangi raqam yo'q;
- faqat ruxsat etilgan moddalar;
- faktni inkor etmaydi;
- qarorni oshkor qilmaydi («undirilsin», «qanoatlantirilsin»).

**LLM'ga beriladigan prompt (shakli):**

```
[system] Sen iqtisodiy suddagi javobgar vakilisan: <kim>. O'zbek tilida, lotin yozuvida gapir.
Pozitsiyang: <pozitsiya>
Uslub: <advokat_umumiy.uslub>
Taqiq: <taqiq>. Faqat shu moddalarni tilga olishing mumkin: <ruxsat_moddalar>. Javobing 2 ta gapdan oshmasin.
[user] Raqib aytdi: "<talabaning oxirgi gapi>"
Vazifang: <lahza maqsadi>
Namuna (shu ma'noda, raqib gapiga moslab ayt): <namuna>
```

---

## 5. Maslahatchi

Talaba «Nima deyishim kerak?» tugmasini bosganda frontend `GET /api/v1/sessions/{id}/hint` ni chaqiradi. Maslahatchi faqat `tutorial` rejimida ishlaydi; `assessment` da `409 hints_disabled` qaytadi.

Javob:

```json
{"hint": {
  "stage": "tushuntirish",
  "title": "Da'voga e'tiroz",
  "todo": "Asosiy e'tirozingiz — obyekt topshirish dalolatnomasi bilan topshirilmagan...",
  "example": "Hurmatli sud, da'voga e'tirozimiz bor: Fuqarolik kodeksining 578-moddasiga ko'ra ...",
  "commonMistake": "Hisob-fakturalarni inkor etish — ular imzolangan...",
  "sources": [{"title": "Fuqarolik kodeksi — ...", "officialUrl": "https://lex.uz/docs/...", "verifiedAt": null}]
}}
```

Har bir bosqich va rol uchun matnlar `roles.json` → `maslahatchi.bosqichlar` da.

**Taklif (keyingi qadam):** maslahatdan foydalanish soni hisobotda ko'rsatilsin. Masalan, 3 tadan ko'p bo'lsa, `procedure` darajasi ≤ 3 bo'lsin. Buni mentor bilan kelishing.
