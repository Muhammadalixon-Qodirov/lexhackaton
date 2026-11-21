"""Tushuntiriladigan baholash: «AI + qoida».

Asos (reports/LexSim baholash metodikasi.md; research_notes/LexSim baholash metodikasi/):
  * ball AI'ning umumiy bahosi emas - atomar «ha/yo'q» bandlar yig'indisi (LexRubric, arXiv 2606.09389);
  * har band uchun AI bayonnomadan SO'ZMA-SO'Z iqtibos keltiradi; server iqtibos bayonnomada borligini tekshiradi -
    tasdiqlanmagan iqtibos bilan «bajarildi» ball bermaydi;
  * qoida bilan aniqlanadigan bandlar (murojaat shakli, so'kinish, manbasiz modda, gapirgan-gapirmagan) AI'siz;
  * bandlar tartibi har chaqiruvda aralashtiriladi; bir nechta yurish bo'lsa - band bo'yicha ko'pchilik ovozi;
  * AI jami ballni chiqarmaydi; jami, oraliq (band) va mentorga yuborish sababi serverda hisoblanadi.
"""
import difflib
import json
import random
import re

from textnorm import normalize  # RAG bilan bir xil normallashtirish (apostrof, kirill → lotin)

RUBRICS = {}
SOURCES = {}
QUOTE_MIN = 0.85                 # iqtibos moslik chegarasi (STT xatolariga yo'l qo'yiladi)


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    RUBRICS.clear()
    RUBRICS.update(d["rubrics"])
    SOURCES.clear()
    SOURCES.update(d.get("sources", {}))


def public(rid):
    """Frontend «Nimaga asoslanib?» oynasi uchun: mezonlar, bandlar, og'irliklar, manbalar."""
    r = RUBRICS[rid]
    return {k: r[k] for k in ("id", "version", "title", "scale", "basis", "dims", "items", "routing")}


# ---------------------------------------------------------------- iqtibosni tekshirish
def _n(t):
    return re.sub(r"\s+", " ", normalize(t or "")).strip()


def find_quote(quote, segments):
    """-> (segment_id, ratio) yoki (None, best). segments: [(id, text)]. So'zma-so'z yoki STT darajasidagi farq."""
    q = _n(quote)
    if len(q) < 8:
        return None, 0.0
    best = (None, 0.0)
    for sid, text in segments:
        t = _n(text)
        if q in t:
            return sid, 1.0
        if len(t) < len(q) * 0.6:
            continue
        sm = difflib.SequenceMatcher(None, q, t, autojunk=False)
        m = sm.find_longest_match(0, len(q), 0, len(t))
        lo = max(0, m.b - m.a)
        win = t[lo: lo + len(q) + 10]
        r = difflib.SequenceMatcher(None, q, win, autojunk=False).ratio()
        if r > best[1]:
            best = (sid, r)
    return (best[0], best[1]) if best[1] >= QUOTE_MIN else (None, best[1])


# ---------------------------------------------------------------- AI so'rovi
def prompt_of(rubric, items, sides, materials, transcript_text, seed):
    rnd = random.Random(seed)
    order = list(items)
    rnd.shuffle(order)                                   # tartib ta'sirini kamaytirish
    who = " va ".join(f"«{s}»" for s in sides)
    lines = "\n".join(f"- {it['id']}: {it['ask']}" for it in order)
    return (
        f"Sen {rubric['judgeRole']}san. Vazifang - baho qo'yish EMAS, faqat har bir band bo'yicha fakt aniqlash.\n"
        f"Har band uchun {who} tomonlari alohida: shu band bajarildimi - \"yes\", \"no\" yoki \"na\" (qo'llanmaydi).\n"
        "QOIDALAR:\n"
        "1) \"yes\" faqat bayonnomadan SO'ZMA-SO'Z iqtibos keltira olsang (\"quotes\" - 1-2 ta, har biri 8-200 belgi, "
        "bayonnomadagi matndan aynan ko'chir). Iqtibos bo'lmasa - \"no\".\n"
        "2) \"why\" - bitta qisqa gap, nima uchun; o'zbekcha yoz, tomonlarni \"da'vogar\" (claimant) va \"javobgar\" (respondent) deb ata.\n"
        "3) Bayonnoma nutqdan olingan (STT): imlo va talaffuz uchun \"no\" qo'yma, mazmunga qara.\n"
        "4) Jami ball, g'olib yoki umumiy baho yozma.\n"
        "5) Yangi fakt yoki modda o'ylab topma; faqat ish materiallari va bayonnoma.\n\n"
        f"ISH MATERIALLARI:\n{materials[:8000]}\n\nBAYONNOMA:\n{transcript_text[-16000:]}\n\n"
        f"BANDLAR:\n{lines}\n\n"
        "Faqat JSON qaytar:\n"
        '{"items":[{"id":"...","side":"' + sides[0] + '","met":"yes|no|na","quotes":["..."],"why":"..."}, ...]}'
    )


def _parse(txt):
    m = re.search(r"\{.*\}", txt or "", re.S)
    try:
        d = json.loads(m.group(0)) if m else None
    except ValueError:
        return None
    return d.get("items") if isinstance(d, dict) and isinstance(d.get("items"), list) else None


# ---------------------------------------------------------------- baholash
def grade(rid, sides, transcript, materials, rule_fn, ask_fn, runs=1, seed=0, timeout=90):
    """transcript: [{"id","side","text"}]; rule_fn(item, side) -> (met: bool|None, evidence: [turn_id], why).
    -> natija: har tomon uchun mezonlar, bandlar (dalil bilan), jami, oraliq, mentorga yuborish sabablari."""
    R = RUBRICS[rid]
    items = R["items"]
    ai_items = [it for it in items if it["method"] == "ai"]
    by_id = {it["id"]: it for it in items}
    seg = {sd: [(t["id"], t["text"]) for t in transcript if t.get("side") == sd and t.get("text")] for sd in sides}
    tr_text = "\n".join(f"[{t['id']}] {t.get('side', '')}: {t.get('text', '')}" for t in transcript)
    votes = {}                                           # (item, side) -> [verdict, ...]
    errors = []
    for k in range(max(1, runs) if ai_items else 0):
        txt, model, ms, why = ask_fn(prompt_of(R, ai_items, sides, materials, tr_text, seed + k), timeout)
        got = _parse(txt)
        if got is None:
            errors.append(why or "javob JSON emas")
            continue
        for g in got:
            if not isinstance(g, dict) or not isinstance(g.get("id"), str) or not isinstance(g.get("side"), str):
                continue                                  # bitta buzuq band butun qarorni yiqitmasin
            key = (g.get("id"), g.get("side"))
            if key[0] not in {it["id"] for it in ai_items} or key[1] not in sides:
                continue
            met = g.get("met") if g.get("met") in ("yes", "no", "na") else "no"
            ev, bad = [], 0
            qs = g.get("quotes") if isinstance(g.get("quotes"), list) else []
            if met == "na" and not by_id.get(key[0], {}).get("optional"):
                met = "no"                                # «qo'llanmaydi» faqat ixtiyoriy bandda — aks holda ball qochiriladi
            for q in qs[:2]:
                tid, r = find_quote(q if isinstance(q, str) else "", seg[key[1]])
                if tid:
                    ev.append({"turnId": tid, "quote": q[:200], "match": round(r, 2)})
                else:
                    bad += 1
            if met == "yes" and not ev:                  # iqtibos tasdiqlanmadi - ball yo'q
                met = "unverified"
            votes.setdefault(key, []).append({"met": met, "evidence": ev, "why": str(g.get("why") or "").replace("\u2014", "-").replace("\u2013", "-")[:240],
                                              "badQuotes": bad, "model": model})
    if ai_items and not any(votes.values()):
        return None, errors
    out = {"rubric": R["id"], "version": R["version"], "runs": max(1, runs), "sides": {}, "routing": []}
    for sd in sides:
        dims, its = {d["id"]: {"id": d["id"], "label": d["label"], "max": d["max"], "basis": d.get("basis", []),
                               "_pos": 0.0, "_got": 0.0, "_lo": 0.0, "_hi": 0.0} for d in R["dims"]}, []
        for it in items:
            if it["method"] == "rule":
                met, ev, why = rule_fn(it, sd)
                v = {"met": "na" if met is None else ("yes" if met else "no"), "evidence": [{"turnId": e} for e in ev],
                     "why": why, "agree": 1.0}
            else:
                vs = votes.get((it["id"], sd), [])
                if not vs:
                    v = {"met": "no", "evidence": [], "why": "AI javob bermadi", "agree": 0.0}
                else:
                    yes = sum(1 for x in vs if x["met"] == "yes")
                    na = sum(1 for x in vs if x["met"] == "na")
                    met = "yes" if yes * 2 > len(vs) else ("na" if na * 2 > len(vs) else "no")
                    pick = next((x for x in vs if x["met"] == met), vs[0])
                    agree = max(yes, len(vs) - yes) / len(vs)
                    v = {"met": met, "evidence": pick["evidence"], "why": pick["why"], "agree": round(agree, 2)}
                    if any(x["met"] == "unverified" for x in vs):
                        v["unverifiedQuotes"] = True
            d = dims[it["dim"]]
            w = float(it["weight"])
            if v["met"] != "na":
                if w > 0:
                    d["_pos"] += w
                hit = v["met"] == "yes"
                unsure = v.get("agree", 1) < 1 or bool(v.get("unverifiedQuotes"))
                sure_hit, maybe_hit = hit and not unsure, hit or unsure
                d["_got"] += w if hit else 0
                if w > 0:                                # oraliq: eng yomon / eng yaxshi holat
                    d["_lo"] += w if sure_hit else 0
                    d["_hi"] += w if maybe_hit else 0
                else:
                    d["_lo"] += w if maybe_hit else 0
                    d["_hi"] += w if sure_hit else 0
            its.append({"id": it["id"], "dim": it["dim"], "ask": it["ask"], "weight": w, "method": it["method"],
                        "basis": it.get("basis", []), **v})
        crit, total, lo, hi = [], 0.0, 0.0, 0.0
        for d in dims.values():
            f = (lambda x: max(0.0, min(1.0, x / d["_pos"])) if d["_pos"] else 0.0)
            sc, sl, sh = (round(d["max"] * f(d[k]), 1) for k in ("_got", "_lo", "_hi"))
            crit.append({"id": d["id"], "label": d["label"], "max": d["max"], "score": sc, "basis": d["basis"]})
            total, lo, hi = total + sc, lo + min(sl, sc), hi + max(sh, sc)
        for it_def in items:                              # qo'pol buzilish - yuqori chegara (etika)
            if it_def.get("capTotal") is not None and any(x["id"] == it_def["id"] and x["met"] == "yes" for x in its):
                total, hi = min(total, it_def["capTotal"]), min(hi, it_def["capTotal"])
                lo = min(lo, total)
                out["routing"].append({"side": sd, "reason": "etika buzilishi - mentor ko'radi", "item": it_def["id"]})
        out["sides"][sd] = {"criteria": crit, "items": its, "total": round(total, 1),
                            "band": [round(lo, 1), round(hi, 1)]}
        rt = R.get("routing", {})
        if any(x.get("agree", 1) < 1 and abs(x["weight"]) >= rt.get("heavyWeight", 3) for x in its):
            out["routing"].append({"side": sd, "reason": "og'ir band bo'yicha yurishlar kelishmadi"})
        if any(x.get("unverifiedQuotes") for x in its):
            out["routing"].append({"side": sd, "reason": "AI keltirgan iqtibos bayonnomada topilmadi"})
        if rt.get("passMark") and abs(total - rt["passMark"]) <= rt.get("nearPass", 5):
            out["routing"].append({"side": sd, "reason": "o'tish chegarasiga yaqin"})
    out["needsMentor"] = bool(out["routing"])
    return out, errors
