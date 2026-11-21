# Ssenariy paketi — `lexsim-scenario/1`

**Kimga:** ssenariy yozadigan mentor yoki huquqshunos va backend dasturchisi.

**Asosiy qoida:** ssenariy — qonun, model — aktyor. Paketda nima sodir bo'lishi yoziladi: faktlar, dalillar, bosqichlar, muhim lahzalar va qaror. Til modeli faqat **qanday aytishni** tanlaydi.

- **Bitta fayl = bitta ish**, ikkala rol bilan: `backend/scenarios/<id>.json`.
- **Namuna:** `scenarios/sud-ijara.json`. U mavjud dvigateldan avtomatik eksport qilingan.

## Bloklar

| Blok | Majburiy maydonlar | Izoh |
|---|---|---|
| `meta` | `id`, `title`, `court` (`economic` / `civil` / `administrative`), `roles` {rol: sessiya ssenariy id}, `durationMinutes`, `difficulty` (1–3), `tags[]`, `summary` | Hub kartasi va tasodifiy tanlash |
| `briefing` | har rol uchun: `workplace`, `position`, `authority[]`, `task[]`, `secret[]` | `secret` boshqa rolga hech qachon ko'rsatilmaydi (tekshiruvchi tekshiradi) |
| `aiFacts` | matn | Modelga beriladigan neytral faktlar. Kimning tomonida ekani ko'rsatilmaydi |
| `facts[]` | `id`, `text`, `status` (`undisputed` / `disputed` / `hidden`), `revealWhen` | Model **faqat shu faktlar** bilan gapiradi |
| `evidence[]` | `id`, `title`, `proves[factId]`, `weakness` | Dalillar va e'tirozlar |
| `persona` | `judge` {`style`, `tone`}; har rol uchun: `who`, `position`, `allowedArticles[]`, `mayConcede[]`, `neverConcede[]`, `settlement` | Raqib har safar boshqacha gapiradi, lekin xarakteri bir xil qoladi |
| `stages[]` | `id`, `goal`, `actions[]`, `next` (ixtiyoriy: `skipTo`, `skipWhen`) | IPK bo'yicha. Oxirgi bosqich `yakun` |
| `keyMoments[]` | `id`, `title`, `stage`, `articleIds[]`, `expected` {rol: matn}, `sample` {rol: namuna}, `verifiedAt` | Baholash va «Qanday aytish kerak edi» bloki |
| `outcome` | `grade` (ball chegaralari), `decision` {`default`, `rules[]`} | Qarorni model emas, talabaning ishi belgilaydi |
| `lines` | kalit: {`text`, `variants[]`, `voice`, `articleIds[]`} | Sudyaning kanonik gaplari. Hammasi oldindan yoziladi (prerender) |
| `variables` | nom: {`values[]`} yoki {`min`, `max`} | Matnda `{{nom}}` ko'rinishida yoziladi. Har biriga 5 tadan ko'p qiymat bermang: har qiymat alohida ovoz talab qiladi |

**Moddalar** formati `FK-544`, `IPK-169`, `OXS234-p9`. Ular faqat normalar bazasidan olinadi.

## Tekshiruvchi

```bash
cd ~/lexsim/backend   # yoki /opt/lexsim/backend
../venv/bin/python scenario_pkg.py validate scenarios/*.json
../venv/bin/python scenario_pkg.py export      # ijara ishini qayta eksport qilish
```

**Xato** bo'lsa, ssenariy ishga tushmaydi. Xato hisoblanadigan holatlar:
- blok yo'q;
- modda bazada yo'q yoki formati noto'g'ri;
- fakt hech bir dalil yoki bosqichga bog'lanmagan;
- bosqichga yetib bo'lmaydi;
- `yakun` bosqichi yo'q;
- qarorda `default` yo'q;
- o'zgaruvchi e'lon qilinmagan;
- `secret` boshqa rolga oshkor bo'lgan;
- ovoz noto'g'ri.

**Ogohlantirish** ssenariyni to'xtatmaydi. Ogohlantirish beriladigan holatlar:
- mentor `verifiedAt` qo'ymagan;
- `decision.rules` bo'sh;
- gap hali klonlangan ovozda yozilmagan;
- `neverConcede` bo'sh.

## Hozirgi holat (2026-11-21)

- Dvigatel ijara ishini hali o'z fayllaridan o'qiydi: `scenarios.json`, `roles.json`, `intents.json`, `options.json`, `replies.json`, `semantic.json`. Paket shu fayllardan eksport qilinadi, shuning uchun ular bir-biridan farq qilmaydi.
- Dvigatel yangi ishlarni bevosita paketdan o'qishi keyingi bosqichda qo'shiladi. Buning uchun mentor yozgan birinchi yangi paket kerak.
- `outcome.decision.rules` hali bo'sh: ijara ishida qaror matni qat'iy («qisman qanoatlantiriladi»). Qarorni talabaning ishiga bog'lash ham keyingi bosqichda qilinadi.
