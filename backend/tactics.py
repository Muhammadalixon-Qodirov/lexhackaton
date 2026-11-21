"""AI raqib va sudyaning qonuniy taktikalari (tactics.json) va talaba reaksiyasini baholash.

Oqim:
  1) bosqich almashganda (yoki shu bosqichda birinchi marta) mos taktika tanlanadi: rol, daraja, rejim (Q / E), sessiya chegarasi;
  2) raqib yoki sudya taktika gapini aytadi (oldindan yozilgan, tekshirilgan matn — AI to'qimaydi);
  3) keyingi ≤ 2 talaba gapi tekshiriladi: avoided (birinchi gapda to'g'ri javob), recovered (ikkinchisida), fell (tushdi);
  4) natija hisobotga: sarlavha, talabaning o'z gapi, to'g'ri yo'l, namunaviy javob (Hampel tuzilishi) va ball.
Bosqich oqimini to'xtatmaydi: talaba gapi odatdagidek ham ishlanadi.
"""
import json
import os
import re

CFG = {}
LEVELS = ("beginner", "intermediate", "advanced")
E_MODE = os.environ.get("LEXSIM_TACTICS_E") == "1"
ART = re.compile(r"(?<![\d.])\d{1,4}(?:[.-]\d{1,3}){0,2} ?-? ?(?:modda|band|qism)", re.I)


def load(path):
    CFG.clear()
    CFG.update(json.load(open(path, encoding="utf-8")))


def lines():
    """Prerender uchun: (matn, rol) — rol: opponent | judge; {role_name} sudya gaplarida."""
    return [(t["line"], t["speaker"]) for t in CFG.get("tactics", [])]


def _fits(t, s):
    lv = s.get("level", "beginner")
    if LEVELS.index(lv) < LEVELS.index(t.get("min_level", "beginner")):
        return False
    if t["mode"] == "E" and not (E_MODE or s.get("flags", {}).get("tactics_e")):
        return False
    return t["student_role"] in ("any", s.get("student_role"))


def pick(s, stage):
    """Shu bosqichga mos, hali ishlatilmagan taktika (yoki None). Sessiya va bosqich chegarasi bilan."""
    if not CFG or s.get("tactic_open"):
        return None
    lv = s.get("level", "beginner")
    used = {x["id"] for x in s.get("tactics_log", [])}
    if len(used) >= CFG["caps"].get(lv, 1):
        return None
    if s.get("tactic_stage_n", {}).get(stage, 0) >= CFG.get("perStage", {}).get(lv, 1):
        return None
    for t in CFG["tactics"]:
        if t["stage"] == stage and t["id"] not in used and _fits(t, s):
            return t
    return None


def open_tactic(s, t, turn_id):
    st = s.setdefault("tactic_stage_n", {})
    st[t["stage"]] = st.get(t["stage"], 0) + 1
    s["tactic_open"] = {"id": t["id"], "left": CFG.get("window", 2), "turn": turn_id, "tries": 0}
    s.setdefault("tactics_log", []).append({"id": t["id"], "name": t["name"], "mode": t["mode"], "result": None,
                                            "turn": turn_id, "quote": None})


def _by_id(tid):
    return next((t for t in CFG.get("tactics", []) if t["id"] == tid), None)


def _check(t, nt):
    """-> True (to'g'ri), False (tushdi), None (hali aniq emas)."""
    kind = t.get("check")
    if kind == "one_norm":
        refs = len(ART.findall(nt)) + len(re.findall(r"\b(fk|ipk|fpk|oxs|plenum)\s*\d", nt))
        words = len(nt.split())
        if refs >= 1 and refs <= 2 and words <= 60:
            return True
        if refs >= 4 or (refs == 0 and words > 8):
            return False
        return None
    if kind == "direct_yes":
        head = " ".join(re.sub(r"\bhurmatli sud\w*", " ", nt).split()[:4])
        if re.search(r"\b(ha|tan olamiz|tasdiqlaymiz|ha,)\b", head):
            return True
        if re.search(r"\b(yo'q|foydalanmagan|inkor)\b", head):
            return False
        return None
    if any(re.search(p, nt) for p in t.get("fell", [])):
        return False
    if any(re.search(p, nt) for p in t.get("avoided", [])):
        return True
    return None


def evaluate(s, nt, text, turn_id):
    """Talabaning har gapida: ochiq taktika bo'lsa — natijani aniqlaydi. -> (yozuv, natija) yoki None."""
    op = s.get("tactic_open")
    if not op:
        return None
    t = _by_id(op["id"])
    rec = next((x for x in reversed(s.get("tactics_log", [])) if x["id"] == op["id"]), None)
    if not t or not rec:
        s.pop("tactic_open", None)
        return None
    op["tries"] += 1
    ok = _check(t, nt)
    res = None
    if ok is True:
        res = "avoided" if op["tries"] == 1 else "recovered"
    elif ok is False and op["tries"] >= CFG.get("window", 2):
        res = "fell"
    elif ok is False:
        rec["slip"] = text[:300]                          # birinchi gapda tushdi — ikkinchisida tuzatish imkoni
    if res is None and op["tries"] >= CFG.get("window", 2):
        res = "fell"                                      # 2 navbatda ham to'g'ri javob bo'lmadi
    if res:
        rec.update(result=res, quote=(rec.get("slip") or text)[:300], answerTurn=turn_id,
                   points=CFG["points"][res])
        s.pop("tactic_open", None)
        return rec, res
    return None


def report(s):
    """Hisobot uchun: feedback yozuvlari va jami ballga tuzatish."""
    out, pts = [], 0
    op = s.get("tactic_open")
    for rec in s.get("tactics_log", []):
        t = _by_id(rec["id"])
        if t and not rec.get("result") and op and op.get("id") == rec["id"] and op.get("tries", 0) >= 1:
            rec.update(result="fell", quote=(rec.get("slip") or "")[:300] or None, points=CFG["points"]["fell"])
        if not t or not rec.get("result"):
            continue
        pts += rec.get("points", 0)
        d = t["debrief"]
        label = {"avoided": "tuzoqqa tushmadingiz", "recovered": "tuzoqdan chiqib ketdingiz", "fell": "tuzoqqa tushdingiz"}[rec["result"]]
        msg = f"{d['headline']} Natija: {label}."
        if rec["result"] != "avoided":
            msg += f" To'g'ri yo'l: {d['remedy']} Namunaviy javob: «{d['model']}»"
        out.append({"kind": "strength" if rec["result"] == "avoided" else "error",
                    "title": f"Taktika: {t['name']}" + (" (e'tiroz mashqi)" if t["mode"] == "E" else ""),
                    "message": msg, "quote": rec.get("quote"),
                    "relatedTurnIds": [x for x in (rec.get("turn"), rec.get("answerTurn")) if x], "sources": []})
    return out, pts
