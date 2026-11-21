"""Raqib — «shaxmatchi»: talabaning xatolarini kuzatib boradi va eng kerakli paytda (muzokarada) foydalanadi.

Mentorlar talabi: advokat raqibi doim xatoni kutadi, reja tuzadi, tuzoq quradi. Bu modul:
  1) kuzatuv daftari — talabaning har gapidan foydalanish mumkin bo'lgan joylar:
     tan olishlar, tuzoqqa tushgan taktikalar, javobsiz qolgan savollar, mavjud bo'lmagan modda, tekshirilmagan dalil;
  2) jazolash — raqib yakuniy nutqida shu joylarni sudga eslatadi, talabaning O'Z so'zlarini aynan iqtibos qilib;
  3) AI raqibga ham kuzatuv beriladi (llm_ctx) — u ham shu zaif joylarga hujum qiladi.
Chegara (qonuniy): faqat haqiqatan aytilgan gaplar va haqiqiy qoidabuzarliklar; o'ylab topilgan «tan olish» yo'q.
"""
import re

COMMON = [r"\btan olamiz\b", r"\btan olaman\b", r"\brozimiz\b", r"\bto'g'ri\b(?! emas)", r"\binkor (etmaymiz|qilmaymiz)\b"]
# tan olish talabaning o'z tomoniga zarar bo'lsagina «tan olish»: da'vogar uchun «javobgar foydalangan» — dalil, javobgar uchun — tan olish
ADMIT = {"davogar-vakili": COMMON + [r"imzolanmagan", r"dalolatnoma (yo'q|tuzilmagan|rasmiylashtirilmagan)",
                                     r"penya (katta|ko'p|nomutanosib|oshirib)", r"kechikib topshir"],
         "javobgar-vakili": COMMON + [r"\bfoydalan(gan|dik|ganmiz)\b", r"\bqarz (bor|mavjud)\b", r"to'la(madik|nmagan|y olmadik)",
                                      r"hisob-?fakturalar\w* imzola(gan|dik)"]}
CAPS = {"beginner": 1, "intermediate": 2, "advanced": 3}
TOPIC = {"R4": "foydalanish fakti va dalolatnoma", "R1": "penya miqdori", "R1b": "penya miqdori",
         "R10": "dalolatnoma", "R8": "foydalanish fakti", "J6": "obyektdan foydalanish", "J5": "huquqiy asos",
         "P13": "tekshirilmagan dalil"}


def _sentence(text, pat):
    for sent in re.split(r"(?<=[.!?])\s+", text):
        if re.search(pat, sent.lower().replace("ʻ", "'").replace("’", "'")):
            q = re.sub(r"\s+", " ", sent).strip()
            q = re.sub(r"^(hurmatli sud\w*[,!.]?\s*)", "", q, flags=re.I).rstrip(".!")   # iqtibos murojaatsiz
            return (q[0].lower() + q[1:])[:160] if q else None
    return None


def record(s, text, nt, tid):
    """Talaba gapidan raqib uchun foydali joylarni yozib boradi."""
    adv = s.setdefault("adv", {"admissions": [], "used": []})
    if len(adv["admissions"]) >= 6:
        return
    for p in ADMIT.get(s.get("student_role"), COMMON):
        if re.search(p, nt):
            q = _sentence(text, p)
            if q and len(q.split()) >= 3 and all(q != a["quote"] for a in adv["admissions"]):
                adv["admissions"].append({"turn": tid, "quote": q})
            break


def weak_points(s):
    """Raqib (va AI raqib) uchun: talabaning hozirgacha zaif joylari, qisqa ro'yxat."""
    adv = s.get("adv") or {}
    out = [f"talaba o'zi aytdi: «{a['quote']}»" for a in adv.get("admissions", [])[:3]]
    for rec in s.get("tactics_log", []):
        if rec.get("result") == "fell":
            out.append(f"talaba {TOPIC.get(rec['id'], rec['name'])} bo'yicha e'tirozga mazmunan javob bermadi")
    vio = {}
    for v in s.get("violations", []):
        vio[v.get("kind")] = vio.get(v.get("kind"), 0) + 1
    if vio.get("citation"):
        out.append("talaba qonunchilikda mavjud bo'lmagan moddani keltirdi")
    if vio.get("unexamined"):
        out.append("talaba majlisda tekshirilmagan dalilga tayandi")
    if any(n >= 2 for n in (s.get("reasks") or {}).values()):
        out.append("talaba sud so'raganiga qaramay talab asosini aniq aytmadi")
    return out


def exploit_lines(s, side_name):
    """Raqib yakuniy nutqiga qo'shiladigan gaplar (daraja bo'yicha soni). Har biri haqiqatga asoslangan."""
    adv = s.setdefault("adv", {"admissions": [], "used": []})
    cap = CAPS.get(s.get("level", "beginner"), 1)
    lines = []
    for a in adv.get("admissions", []):
        if len(lines) >= cap:
            break
        lines.append((f"Hurmatli sud, e'tiboringizni qaratmoqchiman: {side_name}ning o'zi «{a['quote']}» dedi. "
                      "Bu bizning pozitsiyamizni tasdiqlaydi.", a["turn"], "admission"))
    for rec in s.get("tactics_log", []):
        if len(lines) >= cap:
            break
        if rec.get("result") == "fell":
            lines.append((f"Hurmatli sud, {side_name} {TOPIC.get(rec['id'], 'bizning')} bo'yicha e'tirozimizga mazmunan "
                          "javob bermadi — demak, bu e'tiroz rad etilmagan.", rec.get("answerTurn") or rec.get("turn"), "tactic"))
    vio_kinds = [v.get("kind") for v in s.get("violations", [])]
    if len(lines) < cap and "citation" in vio_kinds:
        lines.append((f"Hurmatli sud, {side_name} keltirgan modda qonunchilikda mavjud emas — bu uning huquqiy "
                      "pozitsiyasi asossizligini ko'rsatadi.", None, "citation"))
    if len(lines) < cap and any(n >= 2 for n in (s.get("reasks") or {}).values()):
        lines.append((f"Hurmatli sud, sud bir necha bor so'raganiga qaramay, {side_name} talabining asosini aniq aytmadi.",
                      None, "reask"))
    adv["used"] = [{"kind": k, "turn": t, "text": x} for x, t, k in lines]
    return lines


def report(s):
    """Hisobot: raqib qaysi xatongizdan foydalandi va bundan qanday saqlanish kerak."""
    used = (s.get("adv") or {}).get("used") or []
    if not used:
        return []
    tips = {"admission": "Tan olishdan oldin o'ylang: faqat ishda tasdiqlangan faktni tan oling va darhol o'z xulosangizni qo'shing.",
            "tactic": "Raqib e'tiroziga o'sha zahoti mazmunan javob bering — javobsiz e'tiroz muzokarada sizga qarshi ishlatiladi.",
            "citation": "Faqat aniq bilgan moddangizni keltiring; ishonchingiz komil bo'lmasa, normani nomlamang.",
            "reask": "Sud qayta so'rasa — talab, asos va dalilni bitta gapda ayting."}
    return [{"kind": "error", "title": "Raqib xatoingizdan foydalandi",
             "message": f"Raqib yakuniy nutqida: «{u['text']}» {tips.get(u['kind'], '')}",
             "relatedTurnIds": [u["turn"]] if u.get("turn") else [], "sources": []} for u in used[:3]]
