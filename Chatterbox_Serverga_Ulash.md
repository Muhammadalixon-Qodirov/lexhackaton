# Chatterbox (GPU) ni LexSim serveriga ulash

**Kimga:** GPU kompyuter (`192.168.88.43`, RTX 3050) egasi.
**Sana:** 2026-11-21.
**Maqsad:** LexSim backend sudya, kotib va raqib gaplarini Chatterbox'ning tabiiy o'zbekcha ovozida gapirtirsin. Hozir bu gaplar serverdagi MMS'da chiqyapti: u tez, lekin ovozi sun'iy va ayol ovozi yo'q.
**Server tomoni tayyor.** Faqat sizning kompyuteringizdagi 4 ta qadam qoldi.

---

## 0. Hozirgi holat — avval shuni tekshiring

- **Chatterbox ilovasi to'xtab qolgan.** `https://compatibility-ons-yeah-prediction.trycloudflare.com` 2026-11-21 dan beri **502** qaytaryapti.
  - Ilova 2026-11-21 da yuborilgan sinov so'rovidan keyin to'xtagan: `/use_voice` ishladi, birinchi `/speak` natijasiz tugadi.
  - Sababini `D:\voice_local\uaz.err` dan qarang. Videokarta xotirasi to'lishi (6,8/8 GB) ehtimoli bor.
- **Reranker ishlayapti** (`remote_reranker_ok: true`) — u o'z holicha qolsin.

Ilovani qayta ishga tushirish (sizning hujjatingizdagi buyruq):

```powershell
$env:HF_HUB_OFFLINE="1"
Start-Process D:\voice_local\venv\Scripts\python.exe -ArgumentList D:\voice_local\app_uaz_gpu.py `
  -RedirectStandardOutput D:\voice_local\uaz.log -RedirectStandardError D:\voice_local\uaz.err -WindowStyle Hidden
```

---

## 1. Teskari SSH tunnelga 8092 portini qo'shish

Reranker uchun tunnel allaqachon bor (`8091`). Chatterbox uchun xuddi shu tunnelga bitta port qo'shiladi:

```
server 127.0.0.1:8092  ──(teskari SSH tunnel)──►  GPU kompyuter 127.0.0.1:7102 (Chatterbox)
```

**a) GPU kompyuterda** `D:\lexsim\tunnel.ps1` faylidagi `ssh` buyrug'iga yana bitta `-R` qo'shing:

```powershell
# mavjud:  -R 127.0.0.1:8091:127.0.0.1:8091
# qo'shing: -R 127.0.0.1:8092:127.0.0.1:7102
```

**b) Serverda — ✅ bajarildi (2026-11-21).** `~/.ssh/authorized_keys` dagi `lexsim-rerank-tunnel` kaliti qatoriga ikkinchi `permitlisten` qo'shildi:

```
command="/bin/false",restrict,port-forwarding,permitlisten="127.0.0.1:8091",permitlisten="127.0.0.1:8092" ssh-ed25519 <kalit> lexsim-rerank-tunnel
```

- Kalitning o'zi va boshqa cheklovlar o'zgarmadi: buyruq bajarib bo'lmaydi, faqat port ochiladi.
- Zaxira nusxa: `~/.ssh/authorized_keys.bak-2026-11-21`.
- Yangi ruxsat **yangi ulanishda** kuchga kiradi. `tunnel.ps1` ga `-R ... 8092` qo'shilgach, tunnelni bir marta qayta ulang.

**c) Tekshirish** (serverda):

```bash
ss -ltn | grep 8092                          # LISTEN 127.0.0.1:8092
curl -s http://127.0.0.1:8092/config | head -c 100
```

Port faqat `127.0.0.1` da ochiladi, internetga ham, LAN'ga ham chiqmaydi.

---

## 2. Chatterbox avtostarti

Reranker'dagi kabi Task Scheduler vazifasi qiling: Windows'ga kirganda ishga tushsin, yiqilsa qayta tursin. Uyqu va gibernatsiya o'chiq bo'lsin.

---

## 3. Rollar uchun ovozlarni klonlash (bir marta)

Backend 4 ta ovoz nomini kutadi ([backend/voices.json](backend/voices.json)):

| Frontend ovozi | Kim | Chatterbox'dagi nom | Namuna |
|---|---|---|---|
| `elder_m` | sudya | `sudya` | 45–60 yoshli erkak, sokin, past ovoz |
| `male` | erkak taraf yoki guvoh | `taraf_erkak` | odatiy erkak ovozi |
| `female` | kotib | `kotib` | aniq ayol ovozi |
| `female_alt` | raqib vakili (ayol) | `raqib_ayol` | ayol ovozi, ohangi biroz baland |

- **Namuna:** 5–10 soniya, toza (shovqinsiz), o'zbekcha nutq.
- **Rozilik:** ovoz egasining roziligi bo'lsin. Haqiqiy shaxs ovozini uning ruxsatisiz klonlamang.

**Klonlashning ikki yo'li bor:**

- **GPU kompyuterda:** Chatterbox UI → klonlash → nom yuqoridagi jadvaldagidek.
- **Server orqali** (1-qadamdan keyin, admin token bilan):

  ```bash
  curl -X POST "http://192.168.88.110:8100/api/v1/admin/voice/clone?name=sudya" \
       -H "X-Admin-Token: <token>" --data-binary @sudya_namuna.wav
  # -> {"ok": true, "name": "sudya", "voices": ["Standart ovoz", "sudya", ...]}
  ```

  Admin token serverda: `cat ~/lexsim/backend/.admin_token`.

Biror ovoz klonlanmagan bo'lsa, backend `Standart ovoz` ga balandlik filtrini qo'llab ishlatadi. Ya'ni ovozlarni birma-bir qo'shish mumkin.

---

## 4. Yoqish

`http://192.168.88.110:8100/monitor` → Sozlamalar → **TTS = "Chatterbox GPU"** → Saqlash.

---

## 5. Backend nima qiladi (ma'lumot uchun)

- **Navbat.** `/use_voice` va `/speak` ni bitta qulf ostida, navbat bilan chaqiradi. `/use_voice` butun ilova uchun umumiy bo'lgani uchun bu shart.
- **Gaplarga bo'lish.** Uzun matnni gaplarga bo'ladi (bitta gap ~6–7 s) va natijani bitta audioga qo'shadi.
- **Kesh.** Natija MP3 24 kHz qilib keshlanadi: bir xil gap ikkinchi marta darhol chiqadi.
- **Zaxira.** 8092 javob bermasa (kompyuter o'chiq, ilova yiqilgan), avtomatik **MMS** ga o'tadi va ovoz baribir chiqadi. Kuzatuv panelidagi "TTS Chatterbox GPU (8092)" qatori holatni ko'rsatadi.
- **Maxfiylik.** Talaba ovozi Chatterbox'ga yuborilmaydi: STT serverdagi Kotib'da ishlaydi.

---

## 6. Ulangach yopish kerak

- **Ochiq `trycloudflare` havolasi.** U parolsiz va internetga ochiq. 1-qadam ishlagach, uni to'xtating.
- **VRAM.** Agar ilova yiqilishiga xotira to'lishi sabab bo'lsa, STT'ni GPU'dan olib tashlash yoki Chatterbox'ni fp16 rejimida yuklash haqida o'ylab ko'ring. TTS, STT va reranker birga 6,8/8 GB band qiladi.

---

## 7. GPU kompyuter tomoni — holat (2026-11-21, 02:45)

| Qadam | Holat |
|---|---|
| 0. Ilova | ✅ Ishlayapti. 502 ilova yiqilgani uchun emas: 02:21–02:26 da avtostart sinovida ilova ataylab ikki marta qayta ishga tushirilgan, `/speak` so'rovi shu oynaga tushgan. `uaz.err` da OOM yoki boshqa xato yo'q. |
| 1a. Tunnel `-R 127.0.0.1:8092:127.0.0.1:7102` | ✅ `D:\lexsim\tunnel.ps1` ga qo'shildi, tunnel qayta ulandi. 1b dagi `permitlisten` o'zgarishi tekshirildi: faqat 8092 qo'shilgan, kalit va cheklovlar o'zgarmagan. |
| 1c. Tekshiruv (serverdan) | ✅ `127.0.0.1:8092` LISTEN, `/config` → Gradio 5.50.0. `/speak` 8092 orqali: 3.0 s audio, **9.9 s**, wav yuklab olindi (144 KB). Reranker ham joyida (`remote_reranker_ok: true`). |
| 2. Avtostart | ✅ Windows vazifalari "LexSim reranker" (tunnel + reranker) va "Chatterbox TTS" — kirishda va **har 1 daqiqada** tekshiradi, yo'q qismni yoqadi. Sinov: o'ldirilgan reranker 10 s da qayta yoqildi. Ilova qayta yoqilsa model ~30–150 s yuklanadi. |
| Uyqu / gibernatsiya | ✅ Tokdagi uyqu "hech qachon" qilindi (avval 15 daqiqa edi), gibernatsiya o'chiq. Ekran 5 daqiqada o'chadi — xizmatlarga ta'sir qilmaydi. |
| 3. Rollar uchun ovoz klonlash | ⏳ Ovoz namunalari va egalarining roziligi kerak — egasi beradi. |
| 4. Kuzatuv panelida "Chatterbox GPU" | ⏳ Egasi yoqadi. |
| 6. Ommaviy `trycloudflare` havolasi | ✅ **Yopildi** (eski manzil endi 530). Chatterbox faqat `127.0.0.1:8092` orqali. |

**Eslatma backend uchun:** Gradio javobidagi fayl `url` lari `http://127.0.0.1:8092/gradio_api/file=C:\Users\...` ko'rinishida keladi — shu manzildan yuklab olish ishlaydi (sinovda tekshirildi).
