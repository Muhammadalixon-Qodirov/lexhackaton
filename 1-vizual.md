# LexLevel — 1-guruh: Vizual qism (Frontend va UI/UX)

**Mas'ul:** interfeys va dizayn bo'yicha jamoa a'zosi.
**Maqsad:** talaba, ish beruvchi va ekspert ko'radigan barcha ekranlarni yasash. Ekran "test sayti" emas, haqiqiy yuridik ofis va sud zali bo'lib ko'rinishi kerak.

Qo'shni fayllar: [2-ai-qismi.md](2-ai-qismi.md) (AI rollar va baholash), [3-logika.md](3-logika.md) (backend, ball hisoblash, nazorat).

**Hali yechimi yo'q savollar:** 12-bo'lim.

---

## 0. Loyiha bir qarashda

LexLevel — yuridik talabalar uchun virtual amaliyot. Talaba 4 modulda ishlaydi:

| Modul | Kod | Talaba nima qiladi |
|---|---|---|
| Mijoz | `mijoz` | AI mijoz bilan suhbatlashib, faktlarni aniqlaydi |
| Hujjat | `hujjat` | Da'vo arizasi, shartnoma yoki xulosa yozadi |
| Sud zali | `sud` | AI sudya va AI raqib advokat bilan sud jarayonida qatnashadi |
| Tahlil | `tahlil` | Keysni tahlil qiladi, Lex.uz'dan norma topib qo'llaydi |

Har modul baholanadi va IELTS kabi 1–9 band oladi. 4 modulning o'rtachasi sertifikatga yoziladi, ish beruvchi uni QR orqali tekshiradi.

Rejimlar: `practice` (mashq: cheksiz, izohlar bilan) va `exam` (imtihon: vaqt cheklangan, nazorat ostida, sertifikat beradi).

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

## 2. Ekranlar

### P0
1. **Kirish.** Demo akkauntlar bilan bir bosishda kirish: "Talaba", "Ish beruvchi", "Ekspert".
2. **Talaba bosh sahifasi.** 4 modul kartasi, har birida holat (boshlanmagan, mashqda, topshirilgan) va oxirgi band. "Mashq" va "Imtihon" tugmalari.
3. **Keys brifingi.** "Rahbardan xat" ko'rinishida: topshiriq, muddat, ilova hujjatlar (tilxat surati, shartnoma). Faqat ochiq faktlar.
4. **Mijoz suhbati.** Chat. Chapda mijoz kartasi (ism, yosh, kayfiyat), o'ngda talabaning eslatmalar paneli, tepada taymer. "Suhbatni yakunlash" bosilganda qisqa xulosa yozish oynasi chiqadi.
5. **Hujjat muharriri.** Matn muharriri, so'z soni, taymer, "Saqlandi" holati. Yon panelda keys hujjatlari.
6. **Virtual sud zali.** Rollar paneli (AI sudya, AI raqib advokat, Siz), stenogramma, "Sizning navbatingiz" ko'rsatkichi, e'tiroz banneri va javob taymeri, sudya qarori ("E'tiroz rad etildi").
7. **Natija sahifasi.** Modul bandi, mezonlar bo'yicha ball va izoh, talaba matnidan iqtiboslar, Lex.uz havolalari, topilmagan faktlar, "Qayta urinish" tugmasi.
8. **Sertifikat sahifasi.** Planshetdagi dizayn: umumiy band, 4 modul bandi, ID, QR, muhr, sana, amal qilish muddati. A4 ga chop etishga mos.
9. **Sertifikatni tekshirish sahifasi (ochiq).** QR'dan ochiladi, login kerak emas. Holat: "Haqiqiy", "Muddati o'tgan", "Bekor qilingan". **Avvalo telefon uchun** — ish beruvchi QR'ni telefonda skanerlaydi.
10. **Ish beruvchi paneli.** Nomzodlar ro'yxati (band, modul ballari, viloyat), filtrlar, nomzod sahifasi, "Suhbatga taklif" tugmasi.

### P1
11. **Tahlil moduli.** Savol, javob maydoni, Lex.uz qidiruv paneli.
12. **Ekspert paneli.** Tekshiruv navbati: talaba ishi, AI bahosi, ekspert o'z darajasini qo'yadi va izoh yozadi.
13. **Imtihon rejimi.** 4 modul ketma-ket, umumiy taymer, qoidalar sahifasi, "Imtihonni boshlash" tasdig'i.
14. **"Haqiqiy sud qanday hal qilgan?"** Natija sahifasida talaba yechimi va haqiqiy qaror yonma-yon.
15. **Jonli baho (faqat mashqda).** Sud zalida har gapdan keyin mezonlar bo'yicha taxminiy ko'rsatkich.
16. **OTM va vazirlik paneli.** Ko'nikmalar xaritasi, demo ma'lumot bilan (ustida "Demo ma'lumot" yozuvi).

### P2
17. Ovozli rejim (sud zalida gapirish), qorong'i rejim, rus tili, mobil ilova.

## 3. Dizayn tizimi

Planshet bilan bir xil ko'rinish bo'lsin — hakamlar planshet va ekranni solishtiradi.

- **Ranglar (token sifatida):** asosiy ko'k `#1D3C9E`, matn `#0E1A2B`, ikkinchi darajali matn `#4B5669`, chiziq `#DCE1EA`, fon `#F3F5FA`; qizil (muammo, e'tiroz) `#B42330`; yashil (muvaffaqiyat) `#0F7A55`; sariq (ogohlantirish) `#875700`.
- **Shriftlar:** sarlavha — Source Serif 4; matn — Inter; raqam, ID, taymer — JetBrains Mono.
- **Rol ranglari:** sudya — to'q ko'k-kulrang; raqib — qizil chegara; talaba — ko'k fon; mijoz — neytral oq; tizim xabari — sariq.
- **Komponentlar:** Button, Card, Badge, BandBadge, Timer, ChatMessage, ChatInput, RubricRow, CriterionBar, CertificateCard, QRCode, Toast, Skeleton, EmptyState, ErrorState, Modal.
- Barcha rang, o'lcham va shriftlar bir joyda (CSS variables yoki Tailwind config). Komponent ichiga rang to'g'ridan-to'g'ri yozilmaydi.

## 4. Sifat qayerdan boshlanadi

1. **Real ish joyi hissi.** Brifing — xat, hujjatlar — papka, sud zali — sud zali. Test yoki viktorinaga o'xshab qolsa, g'oyaning kuchi yo'qoladi.
2. **Har ekranda bitta asosiy harakat.** Talaba keyin nima qilishini o'ylab o'tirmasligi kerak.
3. **Ish hech qachon yo'qolmaydi.** Avtosaqlash, sahifa yangilansa tiklanish, internet uzilsa ogohlantirish.
4. **AI'ni kutish noqulay bo'lmaydi.** Javob so'zma-so'z chiqadi (streaming), "Mijoz yozmoqda..." belgisi, baholash uchun progress.
5. **Natija tushunarli.** Faqat raqam emas: nega shu ball, qaysi gap uchun, qaysi norma, keyingi safar nima qilish kerak.
6. **Mashq va imtihon aniq farq qiladi.** Imtihonda maslahat, jonli baho va "qayta urinish" yo'q; taymer va qoidalar ko'zga tashlanib turadi.
7. **O'zbek tili to'g'ri.** Hamma matn o'zbekcha. `oʻ`, `gʻ` va tutuq belgisi (`ʼ`) bir xil va to'g'ri chiqadi, shrift bu belgilarni qo'llab-quvvatlaydi.
8. **Proyektorda ham o'qiladi.** Demo katta ekranda bo'ladi: kontrast yuqori, shrift kichik emas.

## 5. Ekranlar bo'yicha talablar va tuzoqlar

### 5.1 Chat (mijoz va sud zali uchun umumiy)

**Talablar:**
- AI javobi oqim bo'lib keladi (SSE). Har bo'lak matnga qo'shiladi, oxirida `message_done` keladi.
- `EventSource` faqat GET so'rov yuboradi. Xabar POST bilan ketadi, shuning uchun `fetch` va oqimni qo'lda o'qish yoki `@microsoft/fetch-event-source` kutubxonasidan foydalaning.
- Enter — yuborish, Shift+Enter — yangi qator. AI javob yozayotganda yuborish tugmasi o'chadi.
- Har xabarda kim gapirgani aniq ko'rinadi: nom, rang, belgi.
- Yangi xabarda ekran pastga tushadi, lekin talaba tepadagi xabarlarni o'qiyotgan bo'lsa majburan tushirilmaydi ("Yangi xabar ↓" tugmasi chiqadi).
- Xabar uzunligiga chegara (masalan, 1500 belgi) va hisoblagich.

**Tuzoqlar:**

| Muammo | Oldini olish |
|---|---|
| Ikki marta bosilsa xabar ikki marta ketadi | Yuborilgach tugma o'chadi, har xabarga `client_msg_id` beriladi |
| Oqim paytida ekran sakraydi | Ekranni faqat talaba pastda turgan bo'lsa tushiring |
| Javob yarmida uziladi | `error` hodisasida "Javob uzildi — qayta yuborish" tugmasi |
| Sahifa yangilansa suhbat yo'qoladi | Ochilganda `GET /api/sessions/{id}` dan tarixni yuklang |
| Telefonda klaviatura kiritish maydonini yopadi | Kiritish maydonini pastga yopishtiring, `visualViewport` ni hisobga oling |
| Uzun so'z yoki havola joyni buzadi | `overflow-wrap: anywhere` |

### 5.2 Hujjat muharriri
- Oddiy matn muharriri yetadi (textarea yoki TipTap). Murakkab formatlash shart emas, lekin bo'lim sarlavhalari bo'lishi kerak.
- **Avtosaqlash:** har 10 soniyada yoki yozish 2 soniya to'xtaganda `PUT /draft`. Ekranda "Saqlanmoqda..." yoki "Saqlandi 10:42". Ish faqat brauzerda emas, serverda saqlanadi.
- `version` bilan saqlang: serverdagi versiya yangiroq bo'lsa (masalan, boshqa oynada ochilgan), ogohlantiring.
- Paste, oynadan chiqish va yozish tezligi hodisalari `POST /events` ga yuboriladi (6-bo'lim). Mashqda paste taqiqlanmaydi, imtihonda sozlamaga qarab.
- Taymer tugaganda oxirgi qoralama avtomatik topshiriladi va bu haqda talabaga aytiladi.

### 5.3 Virtual sud zali
- Ekranning yuragi — **kimning navbati**: "Sizning navbatingiz — 01:30" yoki "Sudya gapirmoqda...".
- E'tiroz kelganda qizil banner: "E'tiroz! Tilxatda sana ko'rsatilmagan" va javob taymeri (masalan, 30 soniya).
- Sudya qarori alohida ko'rinishda chiqadi: "Sud e'tirozni rad etadi."
- Bosqich ko'rsatkichi: Ochilish → Da'vo bayoni → Dalillar → Savol-javob → Yakuniy so'z.
- Imtihonda jonli ballar ko'rinmaydi. Mashqda P1 sifatida ko'rinishi mumkin.
- **Tuzoq:** bosqich va navbatni frontend o'zi hisoblamasin. Hammasi serverdan `court_state` hodisasi bilan keladi.

### 5.4 Natija sahifasi
- Tepada: modul bandi (katta), xom ball (masalan, 64/100), holat ("Yakuniy" yoki "Ekspert tekshiruvida").
- Har mezon qatori: nomi, ball va vazn, daraja chizig'i, izoh, talaba matnidan iqtibos (sariq fonda), Lex.uz havolasi.
- "Siz so'ramagan savollar" yoki "Topilmagan faktlar" ro'yxati — eng foydali o'quv qismi.
- Kritik xato bo'lsa alohida ogohlantirish: "Da'vo muddati tekshirilmagan — band 5.0 dan oshmaydi."
- Mashqda: "Qayta urinish". Imtihonda: barcha modullar tugagach "Sertifikatga o'tish".
- Baholash 10–30 soniya olishi mumkin: "Baholanmoqda..." holati, har 2 soniyada `GET /evaluations/{id}`.

### 5.5 Sertifikat va QR
- Planshetdagi sertifikat dizayni: band, 4 modul, ID, sana, amal qilish muddati, QR, muhr.
- QR tekshirish sahifasi manziliga olib boradi: `/v/{cert_id}?s={imzo}`. Kutubxona: `qrcode.react` yoki `qrcode`.
- Chop etilganda QR kamida 2 sm bo'lsin, kontrast yuqori, atrofida oq hoshiya qolsin.
- **Telefonda skanerlab sinang** — ekrandan ham, qog'ozdan ham.
- Chop etish CSS'i: A4, chetlar, tugmalar chop etilmaydi.
- Demo sertifikatlarda "NAMUNA" yozuvi bo'ladi.

### 5.6 Tekshirish sahifasi (ochiq)
- Telefon uchun yasaladi: bitta ustun, katta holat belgisi (yashil "Haqiqiy", sariq "Muddati o'tgan", qizil "Bekor qilingan").
- Ko'rsatiladi: F.I.Sh., yo'nalish, umumiy band, modul bandlari, berilgan sana, amal qilish muddati.
- Talabaning ishlari faqat u rozilik bergan bo'lsa ko'rinadi.

### 5.7 Ish beruvchi paneli
- Jadval: ism, OTM, viloyat, umumiy band, 4 modul bandi, sertifikat sanasi.
- Filtrlar: eng kichik band, modul bo'yicha (masalan, "Sud zali ≥ 7.0"), viloyat.
- Nomzod sahifasi: sertifikat, kuchli va zaif mezonlar, rozilik bo'lsa namunaviy ishlari.
- "Suhbatga taklif" — xabar yoziladigan modal oyna.

## 6. Nazorat uchun yuboriladigan hodisalar

Frontend talabani "ushlamaydi", faqat hodisani qayd qilib serverga yuboradi. Qarorni logika qabul qiladi.

| Hodisa | Qachon | Ma'lumot |
|---|---|---|
| `paste` | Muharrir yoki chatga matn qo'yilganda | `chars`, `target` (`draft` yoki `chat`) |
| `blur` | Tab yoki oyna almashtirilganda | — |
| `focus` | Qaytib kelganda | `away_ms` |
| `typing` | Har 10 soniyada | `chars_added`, `window_ms` |
| `copy` | Brifingdan matn nusxalanganda (P1) | `chars` |
| `fullscreen_exit` | Imtihonda to'liq ekrandan chiqilganda (P1) | — |

Hodisalar to'planib, 10 soniyada bir marta yuboriladi: `POST /api/sessions/{id}/events`.

```json
{"events": [
  {"type": "paste",  "at": "2026-11-21T10:01:02.120Z", "data": {"chars": 640, "target": "draft"}},
  {"type": "blur",   "at": "2026-11-21T10:03:10.000Z", "data": {}},
  {"type": "focus",  "at": "2026-11-21T10:03:22.000Z", "data": {"away_ms": 12000}},
  {"type": "typing", "at": "2026-11-21T10:03:30.000Z", "data": {"chars_added": 85, "window_ms": 10000}}
]}
```

## 7. Frontend nimani bilmasligi kerak (xavfsizlik)

- Yashirin faktlar, rubrika tafsilotlari, namunaviy javob va haqiqiy sud qarori frontendga **kelmaydi**. Haqiqiy qaror faqat topshirilgandan keyin natija sahifasida chiqadi.
- Ball, band va sertifikat holatini frontend **hisoblamaydi**, faqat ko'rsatadi.
- Taymer server vaqtiga tayanadi: serverdan `server_time` va `deadline_at` keladi, frontend faqat ko'rsatadi. Kompyuter soatini o'zgartirib vaqt qo'shib bo'lmaydi.
- API kalitlari (AI va boshqalar) frontend kodida bo'lmaydi.

## 8. Backend bilan kontrakt

To'liq ro'yxat — [3-logika.md](3-logika.md), 10-bo'lim. Frontend uchun asosiylari:

| Metod va yo'l | Nima uchun |
|---|---|
| `POST /api/auth/demo-login` | Demo rol bilan kirish |
| `GET /api/cases?module=` | Keyslar ro'yxati |
| `GET /api/cases/{id}/brief` | Brifing (faqat ochiq qism) |
| `POST /api/sessions` | Modulni boshlash: `session_id`, `deadline_at`, `server_time`, birinchi xabar |
| `POST /api/sessions/{id}/messages` | Xabar yuborish, javob SSE oqimida keladi |
| `GET /api/sessions/{id}` | Tiklash: tarix, qoralama, vaqt, bosqich |
| `PUT /api/sessions/{id}/draft` | Avtosaqlash |
| `POST /api/sessions/{id}/events` | Nazorat hodisalari |
| `POST /api/sessions/{id}/submit` | Topshirish, javobda `evaluation_id` |
| `GET /api/evaluations/{id}` | Natija: holat, mezonlar, band |
| `POST /api/exams`, `GET /api/exams/{id}` | Imtihon (P1) |
| `GET /api/certificates/{cert_id}?s=` | Ochiq tekshirish |
| `GET /api/employer/candidates` | Nomzodlar |
| `POST /api/employer/invites` | Taklif yuborish |
| `GET /api/review/queue`, `POST /api/review/{evaluation_id}` | Ekspert paneli (P1) |

SSE hodisalari: `token`, `message_done`, `court_state`, `objection`, `ruling`, `error` (namunalari [3-logika.md](3-logika.md) da).

**Backend tayyor bo'lmaguncha** xuddi shu shakldagi mock JSON bilan ishlang (`mocks/` papkasi yoki MSW). Kontrakt o'zgarsa, uchala guruh birga kelishadi.

## 9. Demo uchun tayyorgarlik

- Demo akkauntlar va tayyor ma'lumotlar: bitta keys, bir nechta tayyor natija, 3–5 ta sertifikatli nomzod (o'ylab topilgan ismlar bilan).
- Demo yo'li oldindan yoziladi va kamida 3 marta boshidan oxirigacha mashq qilinadi: brifing → mijoz suhbati → hujjat → 64 ball → qayta urinish → 86 ball → sertifikat → telefonda QR → ish beruvchi paneli.
- Internet uzilsa: ekran yozuvi (video) va skrinshotlar zaxirada tursin.
- Proyektorda tekshiring: 1366×768 va 1920×1080 o'lchamlarida, katta masshtabda.
- Brauzer: toza profil, bildirishnomalar o'chiq, masshtab 100–125%.

## 10. Tayyorlik ro'yxati (Definition of Done)

- [ ] Barcha P0 ekranlar haqiqiy API bilan ishlaydi (mock emas)
- [ ] Sahifa yangilansa suhbat, qoralama va taymer tiklanadi
- [ ] Ikki marta bosish xabarni ikki marta yubormaydi
- [ ] Uzun o'zbekcha so'zlar va uzun AI javoblari joyni buzmaydi
- [ ] Har ekranda yuklanish, bo'sh holat va xato holati bor
- [ ] Internet o'chirilganda tushunarli xabar chiqadi
- [ ] QR telefonda skanerlanadi, tekshirish sahifasi telefonda chiroyli ko'rinadi
- [ ] Sertifikat A4 ga to'g'ri chop etiladi
- [ ] Inglizcha "placeholder" qolmagan, hamma matn o'zbekcha
- [ ] Imtihon rejimida maslahat va jonli ball ko'rinmaydi
- [ ] Demo yo'li 3 marta boshidan oxirigacha o'tkazildi
- [ ] 12-bo'limdagi "Hakatongacha" bandlari bo'yicha qaror qabul qilinib, yozib qo'yildi

## 11. Boshlash tartibi

1. Logika bilan API kontrakti va JSON shakllarini kelishib oling (birinchi 2–3 soat).
2. Dizayn tokenlari va asosiy komponentlar: Button, Card, ChatMessage, Timer, BandBadge.
3. Mock ma'lumot bilan: brifing → chat → muharrir → natija.
4. Sud zali ekrani (planshetdagi ko'rinish).
5. Sertifikat va tekshirish sahifasi.
6. Haqiqiy API'ga ulanish, keyin demo yo'lini silliqlash.

## 12. Ochiq muammolar: chuqurroq o'ylash kerak

Yuqoridagi bo'limlarda yechimi ma'lum ishlar yozilgan. Bu bo'limdagi savollarning esa tayyor javobi yo'q: ularni jamoa bilan muhokama qilib, talabalar ustida sinab ko'rish kerak. "Hakamlar so'rashi mumkin" deb belgilangan savollarga pitch uchun javob tayyorlang.

Butun loyihaga tegishli savollar (rasmiy tan olinish, sertifikatning huquqiy maqomi, narx) [3-logika.md](3-logika.md) faylining 15-bo'limida.

### 12.1 Realizm va tushunarlilik o'rtasidagi muvozanat
- **Muammo:** ekran haqiqiy ofis yoki sud zaliga qanchalik o'xshasa, birinchi marta kirgan talaba uchun shunchalik murakkab bo'ladi. Juda soddalashtirilsa, oddiy test saytiga aylanib qoladi.
- **Javob topilishi kerak:** yangi foydalanuvchi tushuntirishsiz birinchi topshiriqni bajara oladimi? Qayerda to'xtab qoladi? Buni o'zingiz baholay olmaysiz, chunki siz tizimni allaqachon bilasiz.
- **Mumkin yo'llar:** 3 qadamli qisqa ko'rsatma; birinchi keys maslahatlar bilan "o'quv" rejimida; har ekranda "Nima qilish kerak?" tugmasi.
- **Hakatongacha:** 3–5 ta yuridik talabaga hech narsa tushuntirmasdan birinchi keysni bering. Qayerda qiynalganini yozib oling va o'sha joylarni tuzating.

### 12.2 Sud zalini qanday ko'rsatish kerak
- **Muammo:** sud zali demoning eng kuchli joyi, lekin oddiy chat ko'rinishida u chatbotdan farq qilmay qoladi.
- **Mumkin yo'llar:** (a) chat va rollar paneli — eng tez; (b) sud zalining sxematik rasmi, gapirayotgan tomon yoritiladi — o'rtacha; (c) animatsion avatarlar — sekin, yomon chiqsa arzon ko'rinadi.
- **Javob topilishi kerak:** qaysi variant vaqtga sig'adi va chatdan sezilarli farq qiladi?
- **Hakatongacha:** birinchi kun oxirigacha bitta variantni tanlab, qat'iylashtiring. Tavsiya: (b).

### 12.3 Imtihon adolati: yozish tezligi, stress, imkoniyati cheklangan talabalar
- **Muammo:** Hujjat moduli 60 daqiqa matn yozishni talab qiladi. Sekin yozadigan, kirill klaviaturasiga o'rgangan yoki ko'rishi zaif talaba bilimi yetarli bo'lsa ham past ball olishi mumkin. Ko'z oldida turgan taymer esa stressni oshiradi.
- **Javob topilishi kerak:** qo'shimcha vaqt kimga va qanday beriladi? Taymerni yashirish imkoniyati kerakmi? Interfeys ekran o'qish dasturlari (screen reader) bilan ishlaydimi?
- **Hakatongacha:** backendda "qo'shimcha vaqt" sozlamasi bo'lsin, interfeys uni ko'rsata olsin.

### 12.4 Telefon yoki kompyuter
- **Muammo:** viloyatlardagi ko'p talabalarda faqat telefon bor, telefonda esa 1–2 betlik da'vo arizasi yozish juda qiyin.
- **Javob topilishi kerak:** imtihon faqat kompyuterda bo'ladimi? Unda kompyuteri yo'q talaba qayerda topshiradi (masalan, OTM kompyuter xonasida)? Mashqni telefonda qilsa bo'ladimi?
- **Hakatongacha:** demo kompyuterda bo'ladi. Mijoz suhbati, natija va tekshirish sahifasi telefonda ham ishlasin. Imtihon siyosati keyin hal qilinadi.

### 12.5 Natijani qanchalik ochish kerak
- **Muammo:** batafsil izoh o'rgatadi, lekin imtihonda keys va rubrika sirini ochib qo'yishi mumkin. Past band (masalan, 3.5) esa talabaning ruhini tushiradi.
- **Javob topilishi kerak:** mashqda nima, imtihonda nima ko'rsatiladi? Namunaviy javob qachon ochiladi? Past natijani "keyingi qadam" bilan qanday yetkazish mumkin?
- **Hakatongacha:** mashqda to'liq izoh. Imtihonda faqat band va mezonlar bo'yicha umumiy izoh — iqtibos va haqiqiy qarorsiz.

### 12.6 Sertifikat ishonchli bo'lsin, lekin soxta rasmiy hujjatga o'xshamasin
- **Muammo:** ish beruvchi sertifikatga ishonishi kerak. Lekin davlat gerbi, vazirlik nomi yoki "davlat namunasidagi" degan so'zlarni ruxsatsiz ishlatib bo'lmaydi.
- **Javob topilishi kerak:** ishonchni qaysi elementlar beradi — tekshirish sahifasi, QR, sertifikatni bergan tashkilot nomi, ruxsat bilan qo'yilgan hamkor OTM logotipi? Rasmiy tan olinmaguncha uni "sertifikat" emas, "natija hisoboti" deb atash kerakmi? (Huquqiy tomoni — [3-logika.md](3-logika.md), 15.7.)
- **Hakatongacha:** demoda "NAMUNA" va "Pilot loyiha" yozuvlari bo'lsin.

### 12.7 Ish beruvchiga qancha ma'lumot ko'rsatish
- **Muammo:** ish beruvchi ko'proq narsani ko'rmoqchi (hujjat, sud stenogrammasi), talaba esa xatolari ko'rinishini istamasligi mumkin.
- **Javob topilishi kerak:** rozilik qanday darajalarda bo'ladi (faqat band → modul ballari → ishlar)? Talaba rozilikni qaytarib ola oladimi?
- **Hakatongacha:** talaba profilida 3 darajali rozilik tanlovi bo'lsin.

### 12.8 Sekin va uzilib qoladigan internet
- **Muammo:** viloyatlarda internet uzilib turadi. Oqim uzilsa javob yo'qoladi, imtihonda esa vaqt ketadi.
- **Javob topilishi kerak:** uzilish paytida taymer to'xtaydimi? Qoralama brauzerda saqlanib, internet qaytganda yuboriladimi?
- **Hakatongacha:** uzilish haqida xabar va avtomatik qayta ulanish. Oflayn qoralama — P1.

### 12.9 Til: lotin, kirill, rus
- **Muammo:** ayrim OTMlarda huquq rus tilida o'qitiladi, kattaroq avlod esa kirill yozuvida o'qishga o'rgangan.
- **Javob topilishi kerak:** interfeys qachon rus tilida ham bo'ladi? Bir keysning o'zbekcha va ruscha variantlari bir xil qiyinlikda bo'ladimi?
- **Hakatongacha:** faqat o'zbek tili (lotin yozuvi), lekin barcha matnlar bitta faylda tursin — keyin tarjima qilish oson bo'ladi.
