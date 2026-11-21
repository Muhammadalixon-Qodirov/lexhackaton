"""Ssenariy paketi (lexsim-scenario/1): bitta ish = bitta fayl, ikkala rol bilan.

  python scenario_pkg.py export   — mavjud ijara ishini paketga eksport qiladi (scenarios/sud-ijara.json)
  python scenario_pkg.py validate scenarios/*.json   — tekshiruvchi (validate_scenario)

Asosiy qoida: ssenariy — qonun, model — aktyor. Paketda nima sodir bo'lishi (faktlar, dalillar, bosqichlar,
lahzalar, qaror) yoziladi; model faqat qanday aytishni tanlaydi. Format: SCENARIO_FORMAT.md.

Hozircha dvigatel ijara ishini o'z fayllaridan o'qiydi (scenarios.json, roles.json, intents.json ...);
paket ulardan EKSPORT qilinadi, shuning uchun farq paydo bo'lmaydi. Yangi ishlar paket ko'rinishida yoziladi,
dvigatel paketni bevosita o'qishi — keyingi bosqich.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FORMAT = "lexsim-scenario/1"
REQUIRED = ("meta", "briefing", "facts", "evidence", "persona", "stages", "keyMoments", "outcome", "lines", "variables")
VOICES = {"elder_m", "male", "female", "female_alt"}
ROLES = ("davogar-vakili", "javobgar-vakili")
PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")
ART = re.compile(r"^(FK|IPK|SK|MJtK|OXS\d+)-[\w.]+$")


# ---------------------------------------------------------------- eksport (ijara ishi)
def export_ijara(L):
    """L — lexsim_server moduli. Hozirgi dvigatel ma'lumotlaridan paket yig'adi."""
    sc_d, sc_j = L.SCEN["sud-ijara-davogar"], L.SCEN["sud-ijara-javobgar"]
    pub = sc_d["public"]
    P = L.PROC.CFG

    def secret(b):
        return [a for a in b.get("authority", []) if a.lower().startswith("maxfiy")]

    def brief(b):
        return {"workplace": b.get("workplace"), "position": b.get("position"),
                "authority": [a for a in b.get("authority", []) if not a.lower().startswith("maxfiy")],
                "task": b.get("task", []), "secret": secret(b)}

    facts = [
        {"id": "F1", "text": L.FACTS["F1"], "status": "undisputed", "revealWhen": "stage:ishtirokchilar — ishonchnoma taqdim etilganda"},
        {"id": "F2", "text": L.FACTS["F2"], "status": "undisputed", "revealWhen": "stage:dalillar — yozma dalillar o'qilganda"},
        {"id": "F3", "text": L.FACTS["F3"], "status": "disputed",
         "revealWhen": "javobgar javobi (tushuntirish) yoki savol q-foydalanish"},
        {"id": "F4", "text": L.FACTS["F4"], "status": "disputed", "revealWhen": "stage:penya — penyani kamaytirish iltimosnomasi"},
    ]
    evidence = [
        {"id": "E1", "title": "Ishonchnoma (vakillar)", "proves": ["F1"], "weakness": None},
        {"id": "E2", "title": "2022-yil 1-apreldagi 32-P-sonli ijara shartnomasi (6.4 va 8.5-bandlar)", "proves": ["F2", "F4"],
         "weakness": None},
        {"id": "E3", "title": "Javobgar imzolagan hisob-fakturalar", "proves": ["F2", "F3"], "weakness": None},
        {"id": "E4", "title": "Obyektni topshirish dalolatnomasi", "proves": ["F3"],
         "weakness": "Imzolanmagan — da'vogarning zaif joyi (FK 578-modda)."},
    ]
    persona = {"judge": {"style": "Qat'iy, betaraf, qisqa; IPK tartibiga qat'iy amal qiladi; hukmni oldindan aytmaydi.",
                         "tone": "rasmiy"}}
    for rid in ROLES:
        r = L.ROLES[rid]
        tq = r.get("taqiq")
        persona[rid] = {
            "who": r.get("kim"), "position": r.get("pozitsiya"),
            "allowedArticles": json.loads(r["ruxsat_moddalar"].replace("'", '"')) if isinstance(r.get("ruxsat_moddalar"), str)
            else r.get("ruxsat_moddalar", []),
            "mayConcede": (["Joydan taxminan uch oy foydalangan", "Hisob-fakturalar imzolangan"] if rid == "javobgar-vakili"
                           else ["Topshirish dalolatnomasi imzolanmagan"]),
            "neverConcede": json.loads(tq.replace("'", '"')) if isinstance(tq, str) and tq.startswith("[") else (tq or []),
            "settlement": P["opponent"][rid].get("settlement_main") or P["opponent"][rid].get("settlement"),
        }
    order = ["ishtirokchilar", "rad", "huquqlar", "oldingi", "tushuntirish", "dalillar", "penya", "qoshimcha", "muzokara", "yakun"]
    goals = {"ishtirokchilar": "Vakolatni tasdiqlash (IPK 62)", "rad": "Rad qilish huquqi", "huquqlar": "Huquq va majburiyatlar (IPK 165)",
             "oldingi": "Iltimosnomalar", "tushuntirish": "Da'vo va unga munosabat", "dalillar": "Yozma dalillarni tekshirish",
             "penya": "Penya iltimosnomasi (FK 326)", "qoshimcha": "Qo'shimcha materiallar", "muzokara": "Sud muzokaralari (IPK 173)",
             "yakun": "Hal qiluv qarori"}
    stages = []
    for i, st in enumerate(order):
        acts = sorted(k for k, sts in P["stages"].items() if st in sts)
        stages.append({"id": st, "goal": goals[st], "actions": ["answer"] + acts,
                       "next": order[i + 1] if i + 1 < len(order) else None,
                       **({"skipTo": "qoshimcha", "skipWhen": "da'vogar penyani talab qilmasa"} if st == "penya" else {})})
    sample = {}
    for (role, kid), txt in L.BETTER.items():
        sample.setdefault(kid, {})[role] = txt
    km_stage = {"KM1": "ishtirokchilar", "KM2": "dalillar", "KM3": "penya", "KM4": "muzokara"}
    key_moments = [{"id": k, "title": L.KM_NAMES[k], "stage": km_stage[k], "articleIds": L.KM_NORMS.get(k, []),
                    "expected": {rid: next((s for kk, s in L.IDEAL[rid] if kk == k), None) for rid in ROLES},
                    "sample": sample.get(k, {}), "verifiedAt": None} for k in ("KM1", "KM2", "KM3", "KM4")]
    outcome = {
        "grade": {"basis": "scoreTotal (court-v1 rubrikasi)", "excellent": ">= 85", "average": ">= 60", "poor": "< 60",
                  "failed": "etika nolga tushsa (pora, haqorat)", "forcedPoor": ["patience", "no_powers"]},
        "decision": {"default": "partial",
                     "text": "Da'vo arizasi qisman qanoatlantiriladi (hozirgi dvigatelda qaror matni qat'iy).",
                     "rules": []},
    }
    lines = {}
    for k, t in L.T.items():
        lines[k] = {"text": t, "voice": "female" if k in ("RISE", "CLERK_REPORT") else "elder_m",
                    "articleIds": [a for a in (L.T_ART.get(k) or [])]}
    for st, rv in P["judge"]["RESUME"].items():
        for role, v in rv.items():
            vs = v if isinstance(v, list) else [v]
            lines[f"RESUME.{st}.{role}"] = {"text": vs[0], "variants": vs[1:], "voice": "elder_m", "articleIds": []}
    for k, t in P["judge"].items():
        if isinstance(t, str):
            lines[f"J.{k}"] = {"text": t, "voice": "elder_m", "articleIds": []}
    return {
        "format": FORMAT,
        "meta": {"id": "sud-ijara", "title": "Ijara qarzi va penya", "court": pub.get("court", "economic"),
                 "roles": {"davogar-vakili": "sud-ijara-davogar", "javobgar-vakili": "sud-ijara-javobgar"},
                 "durationMinutes": int(pub.get("durationMinutes", 25)), "difficulty": pub.get("difficulty", 2),
                 "tags": pub.get("tags", []), "summary": pub.get("summary", "")},
        "briefing": {"davogar-vakili": brief(sc_d["public"]["briefing"]), "javobgar-vakili": brief(sc_j["public"]["briefing"])},
        "aiFacts": sc_d.get("ai_facts", ""),
        "numbers": sc_d.get("numbers", ""),
        "facts": facts, "evidence": evidence, "persona": persona, "stages": stages,
        "keyMoments": key_moments, "outcome": outcome, "lines": lines,
        "variables": {},
    }


# ---------------------------------------------------------------- tekshiruvchi
def validate(pkg, known_norms=None, is_cached=None):
    """-> (errors, warnings). known_norms: normalar bazasidagi id'lar (set); is_cached(text, voice) -> bool."""
    E, W = [], []
    if pkg.get("format") != FORMAT:
        E.append(f"format: {FORMAT!r} bo'lishi kerak")
    for b in REQUIRED:
        if b not in pkg:
            E.append(f"blok yo'q: {b}")
    if E:
        return E, W
    meta = pkg["meta"]
    for f in ("id", "title", "court", "roles", "durationMinutes", "difficulty", "tags", "summary"):
        if f not in meta:
            E.append(f"meta.{f} yo'q")
    roles = list((meta.get("roles") or {}).keys())
    for r in roles:
        if r not in pkg["briefing"]:
            E.append(f"briefing.{r} yo'q")
        if r not in pkg["persona"]:
            E.append(f"persona.{r} yo'q")
        elif not pkg["persona"][r].get("neverConcede"):
            W.append(f"persona.{r}.neverConcede bo'sh — raqib hamma narsani tan olib yuborishi mumkin")
    # maxfiy ma'lumot boshqa rolga oshkor bo'lmasin
    for r in roles:
        for sec in pkg["briefing"].get(r, {}).get("secret", []):
            for o in roles:
                if o != r and sec in json.dumps(pkg["briefing"].get(o, {}), ensure_ascii=False):
                    E.append(f"briefing.{r}.secret boshqa rol ({o}) topshirig'ida bor")
    # faktlar
    fids = [f["id"] for f in pkg["facts"]]
    if len(set(fids)) != len(fids):
        E.append("facts: takroriy id")
    for f in pkg["facts"]:
        if f.get("status") not in ("undisputed", "disputed", "hidden"):
            E.append(f"facts.{f['id']}.status noto'g'ri")
    used = {x for e in pkg["evidence"] for x in e.get("proves", [])}
    for e in pkg["evidence"]:
        for x in e.get("proves", []):
            if x not in fids:
                E.append(f"evidence.{e['id']}.proves: {x} faktlar ro'yxatida yo'q")
    for f in pkg["facts"]:
        if f["id"] not in used and not f.get("revealWhen"):
            E.append(f"facts.{f['id']} hech bir dalil yoki bosqichga bog'lanmagan")
    # bosqichlar: hammasiga yetib borish mumkinmi, oxiri yakun
    sids = [s["id"] for s in pkg["stages"]]
    nxt = {s["id"]: [x for x in (s.get("next"), s.get("skipTo")) if x] for s in pkg["stages"]}
    for s, ns in nxt.items():
        for n in ns:
            if n not in sids:
                E.append(f"stages.{s}.next: {n} yo'q")
    seen, todo = set(), sids[:1]
    while todo:
        x = todo.pop()
        if x in seen:
            continue
        seen.add(x)
        todo += nxt.get(x, [])
    for s in sids:
        if s not in seen:
            E.append(f"stages.{s}: unga yetib bo'lmaydi")
    if not sids or sids[-1] != "yakun":
        E.append("stages: oxirgi bosqich «yakun» bo'lishi kerak")
    # lahzalar va moddalar
    arts = set()
    for k in pkg["keyMoments"]:
        if k.get("stage") not in sids:
            E.append(f"keyMoments.{k['id']}.stage: {k.get('stage')} yo'q")
        arts |= set(k.get("articleIds", []))
        if not k.get("verifiedAt"):
            W.append(f"keyMoments.{k['id']}: mentor hali tasdiqlamagan (verifiedAt yo'q)")
    for r in roles:
        arts |= set(pkg["persona"].get(r, {}).get("allowedArticles", []))
    for ln in pkg["lines"].values():
        arts |= set(ln.get("articleIds") or [])
    for a in sorted(arts):
        if not ART.match(a):
            E.append(f"modda formati noto'g'ri: {a}")
        elif known_norms is not None and a not in known_norms:
            E.append(f"modda normalar bazasida yo'q: {a} — ssenariy ishga tushmaydi")
    if known_norms is None:
        W.append("moddalar bazaga solishtirilmadi (LEXSIM_DSN yo'q)")
    # qaror
    oc = pkg["outcome"]
    if not oc.get("grade"):
        E.append("outcome.grade yo'q")
    dec = oc.get("decision") or {}
    if not dec.get("default"):
        E.append("outcome.decision.default yo'q — har qanday holatga qaror bo'lishi kerak")
    if not dec.get("rules"):
        W.append("outcome.decision.rules bo'sh — qaror talabaning ishiga bog'liq emas (doim default)")
    # o'zgaruvchilar
    declared = set(pkg["variables"])
    blob = json.dumps({k: pkg[k] for k in ("briefing", "facts", "lines")}, ensure_ascii=False)
    for ph in sorted(set(PLACEHOLDER.findall(blob))):
        if ph not in declared:
            E.append(f"o'zgaruvchi e'lon qilinmagan: {{{{{ph}}}}}")
    for name, v in pkg["variables"].items():
        if not (isinstance(v, dict) and (v.get("values") or ("min" in v and "max" in v))):
            E.append(f"variables.{name}: values[] yoki min/max kerak")
        elif len(v.get("values") or []) > 5:
            W.append(f"variables.{name}: 5 tadan ortiq qiymat — har biri alohida prerender talab qiladi")
    # gaplar va ovoz
    miss = 0
    for k, ln in pkg["lines"].items():
        if ln.get("voice") not in VOICES:
            E.append(f"lines.{k}.voice noto'g'ri")
        if is_cached and "{" not in ln["text"]:
            for t in [ln["text"]] + ln.get("variants", []):
                if not is_cached(t, ln.get("voice", "elder_m")):
                    miss += 1
    if is_cached and miss:
        W.append(f"lines: {miss} ta gap hali klonlangan ovozda render qilinmagan (avto-prerender yozadi)")
    return E, W


def main(argv):
    if not argv or argv[0] not in ("export", "validate"):
        print(__doc__)
        return 2
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(HERE.parent / "tools"))
    import lexsim_server as L  # noqa: E402
    import voice as V  # noqa: E402
    if L.NORMS is None:
        L.NORMS = L.Norms()
    known = set(L.NORMS.known) if L.NORMS.ok else None
    if argv[0] == "export":
        out = HERE / "scenarios" / "sud-ijara.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(export_ijara(L), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("yozildi:", out)
        argv = ["validate", str(out)]
    rc = 0
    for p in argv[1:]:
        E, W = validate(json.load(open(p, encoding="utf-8")), known, lambda t, v: V.cached(t, v, gpu_only=True))
        print(f"{p}: {'OK' if not E else 'XATO'} — {len(E)} xato, {len(W)} ogohlantirish")
        for e in E:
            print("  XATO:", e)
        for w in W:
            print("  ogoh:", w)
        rc |= bool(E)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
