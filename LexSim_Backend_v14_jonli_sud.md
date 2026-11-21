# Backend v1.4 — sud majlisi endi "jonli" (frontend uchun)

**Kimga:** frontend jamoasi.
**Sana:** 2026-11-21.
**Kontrakt o'zgarmadi.** Yangi narsalarning hammasi mavjud `dialogue.npcTurn` (`role`: `judge` / `opponent`), `feedback` va `decisions` orqali keladi. Frontendda kod o'zgartirish shart emas.

---

## Nima o'zgardi

Oldin har bir talaba gapi sud majlisini keyingi bosqichga o'tkazardi. Endi **sudya talabaning gapiga qarab yo'lni o'zgartiradi**:

| Talaba nima qiladi | Sud nima qiladi | Bosqich |
|---|---|---|
| **Chala javob** (masalan, da'vo talabini summasiz va asossiz aytdi) | Sudya aniqlashtiruvchi savol beradi: beginner 2 marta, intermediate va advanced 1 marta. Qayta so'ralgan lahzaning bahosi cheklanadi (beginner va intermediate ≤ 3, advanced ≤ 2). Imkon tugasa: «Sud mavjud tushuntirishlar asosida davom etadi» | o'zgarmaydi |
| **Raqibga savol** («javobgar vakilidan so'ramoqchiman: …?») | So'z raqibga beriladi. Raqib ish faktlari bo'yicha javob beradi (savollar banki, 10 ta). Ishga oid bo'lmagan savol → «Savol ish holatlariga taalluqli emas, olib tashlanadi». Ruxsat: tushuntirish, dalillar, penya | o'zgarmaydi |
| **Iltimosnoma: dalil yoki guvoh** | Raqib fikri eshitiladi, keyin sud ajrimi chiqadi: asos ko'rsatilmagan → rad; asosli, lekin dalillar yetarli → rad, sababi bilan (IPK 169) | o'zgarmaydi |
| **Iltimosnoma: ishni qoldirish** | Uzrli sabab hujjat bilan tasdiqlanmagani uchun rad (IPK 171) | o'zgarmaydi |
| **Penya iltimosnomasi erta berildi** | «Bayonnomaga kiritildi, dalillardan keyin hal qilinadi». Keyin aynan dalillar bosqichida eshitiladi, qayta so'ralmaydi | davom etadi |
| **E'tiroz** («…gapiga e'tiroz bildiraman, chunki…») | Asos bor → «Sud e'tirozni qabul qildi». Asos yo'q → «E'tiroz rad etildi» | o'zgarmaydi |
| **Kelishuv taklifi** | Raqib o'z shartini aytadi. Da'vogar: «asosiy qarz to'liq to'lansa, penya bo'yicha tayyormiz». Sud: kelishuv bitimi yozma tuziladi va tasdiqlanadi, yozma bitim yo'q — ish davom etadi (IPK 131, 132) | o'zgarmaydi |

**Raqib moslashadi:**
- Da'vogar (talaba) penyani talab qilmasa, javobgar AI penya iltimosnomasini **bermaydi**. Penya bahsi o'tkazib yuboriladi va hisobotda bu lahza "qo'llanmadi" deb hisoblanadi.
- Talaba muzokarada tekshirilmagan holatga tayansa, **raqib e'tiroz bildiradi**, keyin sudya ogohlantiradi.
- Bir xil vaziyatda raqib har safar bir xil javob bermaydi: bir-biriga yaqin variantlar orasidan sessiya `seed` i bo'yicha tanlanadi.

**Xatoning oqibati:**
- `advanced` darajada vakolat ikkinchi marta ham tasdiqlanmasa, vakil majlisga qo'yilmaydi (IPK 62). Sessiya tugaydi, natija `poor`.
- Penya talab qilinmasa, penya bahsi umuman bo'lmaydi.
- Qayta so'ralgan javob to'liq ballni olmaydi.

## Hisobot va feedback

- **`decisions[]`:** har bir harakat alohida yoziladi. Masalan: «Raqibga ishga oid savol berildi», «E'tiroz rad etildi: asosi aytilmadi», «Sudya aniqlashtirishni so'radi». `tone` va `article` ham bor.
- **`feedback`** (beginner) shu izohlarni darhol ko'rsatadi.

## GPU o'chiq bo'lsa

Reranker, STT yoki Chatterbox javob bermasa, backend **30 s davomida ularni chaqirmaydi** va darhol zaxira yo'ldan foydalanadi: kalit so'zlar, CPU STT, MMS. Javoblar kutib qolmaydi.

## Sinov

27 ta test yashil:
- **11 ta yangi protsedura testi:** aniqlashtirish, savol, iltimosnomalar, e'tiroz, kelishuv, erta iltimosnoma, raqibning moslashuvi, vakolatsiz vakil va to'liq yaxshi yo'l;
- **unit testlar;**
- **`contracts.schema.json` bo'yicha kontrakt testi.**

`tools/backend_sinov.py` ikkala rol bo'yicha o'tdi, har bir javob ≤ 3,8 s.

**Kontent** (savollar banki, sudya ajrimlari, raqib javoblari) [backend/intents.json](backend/intents.json) da, mentor tahrirlaydi.
