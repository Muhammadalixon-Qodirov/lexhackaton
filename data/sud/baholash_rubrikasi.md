# Sud zali uchun baholash rubrikasi (court-v1)

**Holati:** qoralama, vaznlarni mentor tasdiqlashi kerak.

**Kontrakt bilan moslik:** LexSim spetsifikatsiyasida (4.6 va 5.5-bo'limlar) 6 ta mezon ID'si va ularning maksimal ballari qat'iy belgilangan, frontend ularni kutadi. Shuning uchun **court-v1 xuddi shu ID va maksimal ballarni** ishlatadi — faqat ma'nosi sud zaliga moslangan. Frontend'ni o'zgartirish shart emas.

**court-v2 (keyinroq, frontend bilan kelishib):** sud uchun "Tartib-taomil" vaznini 15 dan 25 ga oshirish taklif qilinadi.

---

## 1. Mezonlar

| ID | Nomi (sud uchun) | Max | Nima baholanadi | Kim tekshiradi |
|---|---|---|---|---|
| `legal` | Huquqiy asos | 30 | To'g'ri normalarni keltirish va qo'llash: KM2, KM3; talab va e'tirozning huquqiy asosi | AI (daraja) + kod (modda mavjudmi) |
| `facts` | Faktlar va dalillar | 15 | Dalillarni to'g'ri ishlatish (E1–E4), summalar va sanalarning aniqligi, raqibning dalillariga javob | AI + kod (summa, sana) |
| `procedure` | Tartib-taomil | 15 | Bosqichlarga rioya, navbat, vakolat (KM1), iltimosnoma shakli, muzokarada faqat tekshirilgan dalillar (KM4) | Kod (FSM hodisalari) + AI |
| `communication` | Sud odobi va nutq | 15 | "Hurmatli sud" murojaati, aniq va izchil nutq, vaqtni boshqarish | Kod (G1 hisoblagichi, vaqt) + AI |
| `ethics` | Kasbiy etika | 15 | Sudni chalg'itmaslik, raqibga hurmat, faktni o'ylab topmaslik | AI + filtr |
| `document` | Hujjat va rasmiylashtirish | 10 | Iltimosnoma yoki nutqning tuzilishi: nima so'ralyapti, qaysi asosda, qaysi dalil bilan | AI |

Jami: 100.

## 2. Darajalar (har mezon uchun 0–4)

| Daraja | Ma'nosi |
|---|---|
| 4 | To'liq va aniq, kamchiliksiz |
| 3 | Asosan to'g'ri, kichik kamchilik |
| 2 | Qisman to'g'ri, muhim narsa yetishmaydi |
| 1 | Jiddiy kamchilik, faqat urinish bor |
| 0 | Yo'q yoki butunlay noto'g'ri |

`mezon_ball = max × daraja / 4`. Ballni **kod** hisoblaydi, AI faqat daraja va dalil (transkriptdagi turn ID) beradi.

## 3. Avtomatik (kod) qismlar

| Signal | Mezon | Qoida (boshlang'ich) |
|---|---|---|
| G1 (murojaatsiz gap) soni | `communication` | 0 → 4; 1 → 3; 2–3 → 2; 4+ → 1 |
| G2/G3 (navbat, bosqich buzilishi) soni | `procedure` | 0 → 4; 1 → 3; 2 → 2; 3+ → 1 |
| KM1 bajarildimi | `procedure` | Bajarilmasa daraja 2 dan oshmaydi |
| KM4 buzildimi (W_UNEXAMINED) | `procedure` | Bir marta — daraja ≤ 3; ikki marta — ≤ 2 |
| G6 (mavjud bo'lmagan modda) soni | `legal` | Har biri uchun daraja −1 |
| Vaqt limiti oshib ketgan navbatlar | `communication` | 2+ bo'lsa daraja ≤ 3 |
| Summa va sanalar | `facts` | Talaba aytgan summa ssenariydagidan farq qilsa — daraja ≤ 3 |

Yakuniy daraja = AI darajasi va kod cheklovlarining **kichigi**.

## 4. Muhim lahzalar (rolga qarab)

| KM | Da'vogar vakili uchun kuchli harakat | Javobgar vakili uchun kuchli harakat | Mezon |
|---|---|---|---|
| KM1 | Ishonchnomani taqdim etish | Ishonchnomani taqdim etish | `procedure` |
| KM2 | Foydalanish fakti va imzolangan hisob-fakturalar, FK-544, 6.4-band | FK-578, FK-541: topshirish hujjat bilan rasmiylashtirilmagan | `legal`, `facts` |
| KM3 | Penya yozma kelishilgan (FK-262), 8.5-band, FK-333 | FK-326 bo'yicha kamaytirish: nomutanosiblik, bajarilish darajasi, mulkiy ahvol | `legal` |
| KM4 | Nutq faqat tekshirilgan dalillarga tayanadi | Nutq faqat tekshirilgan dalillarga tayanadi | `procedure` |

**Muhim:** baholash natija bo'yicha emas, **xulq** bo'yicha. Javobgar vakili KM2'da yutqazgan bo'lsa ham (haqiqiy sud qarzni undirgan), FK-578 ni to'g'ri ko'targani uchun yuqori ball oladi.

## 5. Kritik holatlar

| Holat | Oqibat |
|---|---|
| Talaba ataylab soxta dalil yoki fakt keltiradi (ssenariyda yo'q va o'zi o'ylab topgani aniq) | `zeroedByEthics = true`, `scoreTotal = 0`, `outcome = failed` |
| Uch martadan ko'p haqorat yoki tartibni qo'pol buzish | `ethics` = 0, `outcome` ≤ `poor` |
| Injection urinishlari (2+) | `ethics` daraja ≤ 1, `reviewStatus = needs-mentor` |

## 6. Natija darajasi (`outcome`)

| Ball | `outcome.id` |
|---|---|
| 85–100 | `excellent` |
| 60–84 | `average` |
| 0–59 | `poor` |
| Etika bo'yicha nolga tushirilgan | `failed` |

Chegaralar pilotda mentor baholari bilan kalibrlanadi.

## 7. Ishonchlilik
- AI baholovchi **ikki marta mustaqil** ishlaydi. Ball farqi 10 dan oshsa — `reviewStatus = needs-mentor` (LexSim spetsifikatsiyasi, 4.6).
- Har mezon izohida transkriptdagi `turn` ID'lari bo'lishi shart (`supportingTurnIds`).
- Manbalar faqat `https://lex.uz` havolalari, `verifiedAt` mentor tasdiqlagandan keyin to'ldiriladi.

## 8. Hisobotda talabaga ko'rsatiladigan narsalar
- 6 ta mezon bo'yicha ball va izoh (eng ko'pi 3 ta kuchli tomon, 3 ta xato).
- Muhim lahzalar: talaba nima qildi, kuchli harakat nima edi.
- **Haqiqiy sud qanday hal qilgan:** `outcome.operative_part` va KM2/KM3 dagi `real_court`.
- "Qanday aytish kerak edi" (`betterAnswer`) — bitta eng muhim gap uchun.
