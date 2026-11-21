# Backend v1.4.3 — LexSim_HOLAT (B1, B2) ga javob

**Kimga:** frontend jamoasi.
**Sana:** 2026-11-21.
**Server:** `https://lex-api.e-investment.uz/api/v1`.

**Versiya.** `/health` → `"version": "1.4.3"`. Yangi `features`:
- `turn-presence` — `turns` dagi `presence` maydoni ishlatiladi;
- `interaction-context` — `interactions` dagi `context` maydoni ishlatiladi.

**Kontrakt.** Siz yuborgan `contracts.schema.json` qo'yildi: unda `TurnRequest.presence` va `InteractionRequest.context` bor. Kontrakt testi yashil, barcha testlar 43/43.

Oldingi javob: [LexSim_Backend_v142_V15_javob.md](LexSim_Backend_v142_V15_javob.md). `LexSim_HOLAT.md` ni boshqaruv hujjati sifatida qabul qildik.

---

## B1. Tik turish holati noma'lum bo'lsa ✅

`sit-at-desk` dan keyin `standing` `null` bo'lsa, endi `false` bo'ladi. Talaba «Turish»ni hech bosmasa ham, sudga o'tirib murojaat qilganda tanbeh zinapoyasi ishlaydi.

Zalga kirishda vaqtincha yuborayotgan `sit` ingizni olib tashlashingiz mumkin. Qoldirsangiz ham zarari yo'q.

Jonli tekshiruv:
```
start → sit-at-desk                                  → snapshot.standing = false
turn «Hurmatli sud, ishonchnomani…» presence.standing=false
  → [judge] «Daʼvogar vakili, sudga oʻrningizdan turib murojaat qiling.»  calm
            reactions: principal uncertain, secretary neutral
```

## B2. Yangi signallar ✅

### `POST /sessions/{id}/turns` → `presence`

| Maydon | Nima qilinadi |
|---|---|
| `standing` | Javob paytidagi holat sifatida olinadi va oxirgi `stand`/`sit` dan **ustun** turadi. Tanbeh zinapoyasi shunga qarab ishlaydi. |
| `spokenSeconds` | **> 90 s** bo'lsa (yoki matn > 120 so'z bo'lsa), sudya muloyim to'xtatadi: «Qisqaroq, mohiyatini ayting.» yoki variant (`calm` / `lean-in`). Gap odatdagidek baholanadi. |
| `heardTurnId` | Talaba sudning oxirgi gapini eshitmay javob bersa (`heardTurnId` undan oldingi gap bo'lsa), bu **gap bo'lish** hisoblanadi va **o'z tanbeh zinapoyasi** bilan baholanadi (pastda). Sizning kafolatingiz bo'yicha bu kam uchraydi, lekin endi tekshiriladi. |

**Gap bo'lish zinapoyasi:**

| Necha marta | Sudya | `emotion` / `gesture` | Ball |
|---|---|---|---|
| 1 | «…sudni oxirigacha tinglang, keyin gapiring.» yoki «…iltimos, sud gapini boʻlmang.» | `calm` / — | beginner: 0, intermediate: −1, advanced: −2 |
| 2 | «Ikkinchi marta eslatyapman: sud gapirayotganda gapni boʻlmang.» yoki variant | `impatient` / `shake-head` | −2 |
| 3 | «Sud majlisi tartibiga rioya qilmayapsiz…» | `upset` / `shake-head` | −5 |
| 4+ (`advanced`) | oxirgi ogohlantirish | `upset` / `shake-head` | −5, etika |

**Bitta gapda bir nechta xato bo'lsa,** sudya faqat **bitta** tanbeh aytadi. Ustunlik tartibi: o'tirish → «Hurmatli sud» → gap bo'lish. Xatolarning hammasi hisoblanadi.

### `POST /sessions/{id}/interactions` → `context.during`

- Talaba `stand` qilsa va shu payt **raqib, guvoh yoki ekspert** gapirayotgan bo'lsa (`during.role`), sudya yengil eslatma qiladi: «Oʻtirishingiz mumkin.» yoki «Raqib gapirayotganda oʻtirishingiz mumkin.» (`calm` / `nod`).
- Bu eslatma **ballsiz**.
- Sudya buni har 3 marta tik turishda bir marta aytadi: zal har safar to'xtab qolmasligi uchun.

Jonli tekshiruv:
```
stand + context.during.role = "opponent"  →  200, [judge] «Oʻtirishingiz mumkin.»
```

`presence` va `context` ichida noto'g'ri maydon kelsa, e'tiborga olinmaydi va 422 qaytmaydi.

---

## Ovoz

- **GPU kompyuter hali ham o'chiq.** Holat: `/voice/status` → `"stt":"cpu"`, `gpu.*: false`.
- Klon ovozda tayyor gaplar: **310 tadan 268 tasi**. Qolgan 42 tasi yangi tanbeh, zal va ajrim gaplari.
- GPU yonishi bilan avtomatik render (har 10 daqiqada) ularni o'zi yozadi. Shungacha bu gaplar MMS ovozida chiqadi.
- `voice-coverage.mjs` ni GPU qaytgandan keyin ishga tushiring. Hozir bir nechta `miss` chiqishi kutilgan.

## HOLAT hujjatidagi qolgan backend ishlari

| # | Holat |
|---|---|
| B3 STT ≤ 2,5 s | ⏳ GPU yoniq bo'lishi kerak (E2). Keyin tunnel qadamlarini qisqartiraman. |
| B4 Palitra | ⏳ E3 (ovoz namunalari va rozilik). Nomlar (`judge_m2` va hokazo) allaqachon qabul qilinadi. |
| B5 9 ta ssenariy | ⏳ E4 (mentor paketi). Format va tekshiruvchi tayyor. |
| B6 Tez improvizatsiya | ⏳ E5 (API kaliti) |
| B7 `/records` | ⏳ E6 (saqlash siyosati) |
| B8 `npcTurn.audio` | Keyingi versiyada |

«Sud kirganda turmaslik» (`start` dan keyin `stand` kelmasa) hozircha frontendda: sizda hamma talabaga qaraydi va eslatma chiqadi. Backend uni talabaning birinchi murojaatida o'tirish tanbehi bilan baholaydi.
