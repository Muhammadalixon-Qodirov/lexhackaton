# Backend v1.4.6 — qahramonlar odamdek javob bersin

**Kimga:** frontend jamoasi.
**Sana:** 2026-11-21.
**O'rnatish:** bugun **22:05** da, v1.4.5 bilan birga. Kod alohida portda sinab ko'rildi, testlar 52/52.
**Tekshirish:** `/health` → `"version": "1.4.6"`. Yangi `features`: `human-situations`, `profanity-ladder`, `nlu-situations`.
**Kontrakt:** o'zgarmadi. Faqat `/nlu/match` javobiga ixtiyoriy `situation` maydoni qo'shildi.

---

## Muammo (21-noyabr jonli sinovi)

Talaba kutilmagan gap yozsa, qahramonlar robotdek javob berdi:
- "Ish yo'li" va DXM'da har safar «Kechirasiz, tushunmadim»;
- sud zalida eng yaqin shablon.

Haqiqiy misollar:

| Talaba | Javob | Muammo |
|---|---|---|
| «boshligingni sikkaman, rozimisan» (mijozga) | «Kechirasiz, tushunmadim» | So'kinish tanilmadi |
| «man yordam bera olmayman» (mijozga) | «Uzr, nima demoqchi ekaningizni tushunmadim» | Mazmunli gapga "tushunmadim" deyildi |
| «yoʻqotib qoʻydim. topolmayapman.» (navbatchiga) | «Kechirasiz, fikringizni tushunmadim» | Vaziyatga javob berilmadi |
| DXM: «pashol naxuy» | «Men tushunmayman bu ishlarni…» | So'kinish tanilmadi |

Sababi:
- `/nlu/match` bu gaplarni variantlar bilan to'g'ri solishtirdi. Hech biri mos kelmadi, ball 0,0 bo'ldi. Mazmuni yaqin gapga reranker 0,99 beradi, demak u to'g'ri ishlayapti.
- Lekin javobda "nima bo'ldi" degan ma'lumot yo'q edi. Shuning uchun siz umumiy "tushunmadim" gapini ijro etdingiz.

---

## 1. `/nlu/match` → yangi `situation` maydoni

Talaba gapida tanish vaziyat bo'lsa, javobga `situation` qo'shiladi. Uning ichida har bir qahramon uchun tayyor, odamdek javob bor:

```json
{
  "match": null, "reason": "ethics", "quality": {"ethics": "violation", ...},
  "situation": {
    "id": "profanity", "tone": "bad", "ethics": true,
    "note": "So'kinish — kasbiy etikaning qo'pol buzilishi.",
    "replies": {
      "client":  {"emotion": "upset", "voices": ["male", "female"],
                  "lines": ["Nima?! Bunaqa gaplarni sizdan kutmagan edim… Siz rostdan ham advokatmisiz?",
                            "Iltimos, men bilan bunday gaplashmang. Men yordam so'rab kelganman."]},
      "officer": {"emotion": "impatient", "voices": ["male"], "lines": ["Bu yer navbatchi qism. Haqorat qilmang — …"]},
      "clerk":   {...}, "judge": {...}, "investigator": {...}, "chief": {...}, "secretary": {...}, "respondent": {...}, "witness": {...}
    }
  }
}
```

| `situation.id` | Qachon | Misol javob |
|---|---|---|
| `profanity` | So'kinish (o'zbekcha yoki ruscha, kirillda ham) | mijoz: «Nima?! Bunaqa gaplarni sizdan kutmagan edim…»; navbatchi: «Haqorat qilmang — … bayonnomaga yoziladi» |
| `lost_document` | «yo'qotdim», «topolmayapman», «uyda qoldi», «unutibman» | navbatchi: «Tushunaman, bunday bo'ladi. Unda arizani og'zaki aytib bering — bayonnomaga yozaman…» |
| `refusal` | Vakil mijozni tashlab ketmoqchi («yordam bera olmayman») | mijoz: «Qanday qilib?! Men sizga umid bilan kelgandim…» |
| `russian` | Ruscha gap | «Iltimos, o'zbek tilida gapiring. Zarur bo'lsa, tarjimon taklif qilinadi.» |
| `offtopic` | «ishlaringiz qalay», «futbol», «ovqat»… | mijoz: «Kechirasiz, hozir boshqa gapga holim yo'q… Ishim haqida gaplashsak bo'ladimi?» |

**Sizdan:**
1. Javobda `situation` bo'lsa, umumiy "tushunmadim" o'rniga hozirgi so'zlovchining `replies[speaker]` gapini ijro eting.
   - Variantlardan qaysi birini aytishni o'zingiz tanlaysiz: navbat bilan yoki tasodifiy.
   - So'zlovchi uchun javob bo'lmasa, odatdagi "tushunmadim" gapini qoldiring.
2. Yuzga `emotion` ni qo'ying. Ovoz `voices` dan, qahramon jinsiga mos bo'lsin.
3. `tone: "bad"` bo'lsa, xatoni log va hisobotga yozing. `situation.note` tayyor izoh. `ethics: true` bo'lsa, etika mezoni bo'yicha baholang. Siz allaqachon `quality.ethics` ni ishlatsangiz, bu so'kinishda ham endi `violation` qaytadi.
4. Bosqich o'zgarmasin. Qahramon javobidan keyin o'sha savol ochiq qolsin.

**Ovoz.** Barcha javoblar prerender ro'yxatida va har rol uchun `voices` dagi ovozda yoziladi. O'rnatilgandan keyin avtomatik render ularni yozib chiqadi.

## 2. Sud zali (backend o'zi boshqaradi — sizdan hech narsa kerak emas)

Sudya kutilmagan gapga endi odamdek javob beradi:
- talabaning gapini tan oladi;
- nega mumkin emasligini tushuntiradi;
- ishga qaytaradi.

Faktlar va bosqichlar o'zgarmaydi. Vaziyat takrorlansa, ohang kuchayadi. Barcha gaplar prerender qilingan, `npcTurn.audio` bilan keladi.

| Talaba | Sudya |
|---|---|
| «uyda qolib ketibdi» (ishonchnoma) | «Tushunaman, bunday holat bo'lib turadi. Lekin hujjatsiz sud sizni vakil sifatida qo'ya olmaydi. Ishonchnoma yoki uning nusxasi yoningizda yo'qmi?» (`uncertain`). Ikkinchi safar: «Afsuski, hujjat bo'lmasa…» va oqibati |
| So'kinish | 1 — «Sud majlisi tartibini buzmang…» (`upset`); 2 — «…oxirgi ogohlantirish: yana takrorlansa, zaldan chiqarilasiz»; 3 — **zaldan chiqariladi**, sessiya `report-ready` |
| «mijozim aybdor», «mijozimni qamang» | «…siz mijozingiz manfaatini himoya qilish uchun shu yerdasiz…» (`bad`, −2) |
| «qamang», «jinoiy jazo» | «Bir daqiqa. Bu iqtisodiy sud — hech kim qamalmaydi…» (`confused`) |
| «ishlaringiz qalay?» | «Savolingiz ishga taalluqli emas… keling, ish mohiyatiga qaytaylik», keyin bosqich savoli |
| Ruscha | «Sud majlisi davlat tilida olib boriladi… tarjimon xizmatidan foydalanish huquqingiz bor» |
| «qo'rqyapman», «bilmayapman» | «Xavotirlanmang, shoshilmasdan fikringizni jamlang. Sud sizni tinglaydi.» (`calm`) |
| «kotib yosh, tajribasi kam» (rad) | «…Kotibning yoshi yoki tajribasi rad qilish uchun qonuniy asos bo'lmaydi…» |
| «rad huquqidan oxirida foydalanaman» | «Rad qilish ish mazmunan ko'rilishidan oldin bildiriladi… Hozir rad bildirasizmi?», bosqich o'zgarmaydi |

- Aniqlashtiruvchi savollar endi **2 xil variantda**, so'zma-so'z takrorlanmaydi.
- Bahona aytilgan gapda sudya avval mazmunga javob beradi, «Hurmatli sud deng» tanbehi esa ovoz chiqarib aytilmaydi.

## 3. Chegara

Bu tayyor vaziyatlar ro'yxati, kengaytirish oson: `backend/intents.json` → `situations` (sud zali) va `nlu_situations` ("Ish yo'li"). Ro'yxatda yo'q, butunlay kutilmagan gaplarga o'z so'zi bilan javob berish uchun tez LLM kerak (HOLAT, E5). Kalit kelgach, model shu chegaralar ichida, kartadagi faktlar bilan javob yozadi.
