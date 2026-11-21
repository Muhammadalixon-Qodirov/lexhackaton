"""Sud majlisining "jonli" protsedurasi: talaba tashabbusi va sudyaning moslashuvi.

Chiziqli bosqichlar ustiga qo'shiladi (bosqichlar tartibi baribir kodda, IPK bo'yicha):
  1. Harakat aniqlash — talaba gapi: raqibga savol, iltimosnoma (penya / dalil yoki guvoh / qoldirish),
     e'tiroz, kelishuv taklifi yoki oddiy javob. Ruxsat etilgan bosqichda hal qilinadi, bosqich o'zgarmaydi.
  2. Aniqlashtirish — muhim bosqichda javob zaif bo'lsa, sudya qayta so'raydi (daraja bo'yicha 1–2 marta);
     qayta so'ralgan lahzaning darajasi cheklanadi (birinchi urinishda aytilmagan).
  3. Erta iltimosnoma — penya iltimosnomasi oldinroq aytilsa, eslab qolinadi va o'z vaqtida hal qilinadi.
Kontent: intents.json (mentor tahrirlaydi).
"""
import json
import random
import re
from pathlib import Path

CFG = json.load(open(Path(__file__).resolve().parent / "intents.json", encoding="utf-8"))
J = CFG["judge"]
S = None            # lexsim_server moduli (init orqali): nlu_rerank, normalize, OPP, ROLE_NAME ...


# Sudya gaplarining ohangi (v15 §3, §7.3): kalit -> (emotion, gesture, tinglovchilar munosabati)
DENIED = [("opponent", "reassured"), ("principal", "upset")]
J_STYLE = {
    "Q_IRRELEVANT": ("impatient", "shake-head", [("principal", "uncertain")]),
    "Q_STAGE": ("neutral", "none", None), "M_STAGE": ("neutral", "none", None), "O_STAGE": ("neutral", "none", None),
    "Q_FLOOR": ("calm", "none", None), "Q_LIMIT": ("neutral", "none", None), "M_LIMIT": ("neutral", "none", None),
    "M_PENYA_EARLY": ("calm", "nod", None), "M_EVIDENCE_HEAR": ("calm", "none", None),
    "M_EVIDENCE_DENY_BASIS": ("neutral", "shake-head", DENIED), "M_EVIDENCE_DENY_ENOUGH": ("neutral", "shake-head", DENIED),
    "M_POSTPONE_DENY": ("neutral", "shake-head", DENIED),
    "O_SUSTAIN": ("calm", "nod", [("opponent", "upset"), ("principal", "reassured")]),
    "O_OVERRULE": ("neutral", "shake-head", DENIED),
    "S_CONTINUE": ("calm", "none", None), "S_NEAR": ("calm", "nod", [("principal", "reassured")]),
    "R_CONTINUE": ("neutral", "none", None), "NO_POWERS": ("neutral", "shake-head", [("principal", "upset")]),
}
TEXT_STYLE = {}          # tayyor matn -> uslub (init da to'ldiriladi)


def init(server_module):
    global S
    S = server_module
    names = list(S.ROLE_NAME.values())
    for k, st in J_STYLE.items():
        t = J.get(k)
        if isinstance(t, str):
            for x in ([t.format(opp=n.lower()) for n in names] + [t.format(opp=n) for n in names]) if "{opp}" in t else [t]:
                TEXT_STYLE[x] = st
    for stg in CFG["reask_text"].values():                   # aniqlashtirish — sudya biroz shubhada, oldinga engashadi
        for v in stg.values():
            for t in (v if isinstance(v, list) else [v]):
                for x in ([t.format(role_name=n) for n in names] if "{role_name}" in t else [t]):
                    TEXT_STYLE[x] = ("uncertain", "lean-in", None)


CYR = re.compile(r"[\u0400-\u04FF]")


def situational(eng, text, nt, tid):
    """Ssenariydan tashqari, lekin tez-tez uchraydigan vaziyatlar (v1.4.6): sudya talabaning AYNAN gapiga odamdek
    javob beradi — tan oladi, nega mumkin emasligini tushuntiradi, ishga qaytaradi. Faktlar va bosqich o'zgarmaydi.
    True — hal qilindi (bosqich ishlovchisi chaqirilmaydi)."""
    s = eng.s
    if s["stage"] == "yakun":
        return False
    for sit in CFG.get("situations", []):
        hit = any(re.search(p, nt) for p in sit["patterns"]) or (sit.get("cyrillic") and len(CYR.findall(text)) >= 3)
        if not hit:
            continue
        n = s.setdefault("sit_n", {})
        i = n.get(sit["id"], 0)
        n[sit["id"]] = i + 1
        emo, ges = sit["steps"][min(i, len(sit["steps"]) - 1)]
        early = s["stage"] in ("ishtirokchilar", "rad", "huquqlar", "oldingi") and sit.get("early_lines")
        lines = sit["early_lines"] if early else sit["lines"]    # da'vo hali ko'rilmagan — boshqa gap, keyin bosqich savoli
        line = lines[i % len(lines)].format(role_name=S.ROLE_NAME[s["student_role"]])
        eng.npc(line, gesture=ges, emotion=emo, reactions=[tuple(r) for r in sit.get("reactions", [])] or None)
        _note(eng, tid, sit.get("tone", "info"), sit["note"], sit.get("points", 0))
        if sit.get("resume") or early:
            _resume(eng)
        return True
    return False


def has(nt, *pats):
    return any(re.search(p, nt) for p in pats)


OPP_WORDS = r"(javobgar|da'vogar|raqib|vakil|tomon)\w*"


# ---------------------------------------------------------------- harakatni aniqlash
def detect(text, nt, stage, role):
    """(harakat, tur) yoki (None, None). Oddiy javob — None."""
    if has(nt, r"kelishuv bitim", r"kelishuvga (tayyor|rozi)", r"kelishuv taklif", r"\bmurosa", r"tinch yo'l"):
        return "settlement", None
    asks = has(nt, r"so'ra", r"iltimos")
    if asks and has(nt, r"guvoh", r"ekspertiza", r"dalil\w* (qo'sh|ilova|taqdim|talab)", r"hujjat\w* (qo'sh|talab|so'rab ol)",
                    r"so'rov (yubor|jo'nat)", r"ish materiallariga qo'sh"):
        return "motion", "evidence"
    if has(nt, r"keyinga qoldir", r"qoldirishni so'ra", r"\btanaffus"):
        return "motion", "postpone"
    if role == "javobgar-vakili" and asks and has(nt, r"peny|neustoyk") and has(nt, r"kamaytir"):
        return "motion", "penya"
    question = ("?" in text or has(nt, r"savol(im| ber| bermoqchi)", r"\w+(misiz|dingizmi|ganmisiz|yapsizmi)\b")) \
        and (has(nt, OPP_WORDS, r"\bsiz\b", r"misiz\b", r"dingizmi\b"))
    if question and not has(nt, r"^hurmatli sud,? (qaror|hukm)"):
        return "question", None
    # raddiya bosqichlarida mazmunli "qarshi chiqaman, chunki ..." — talabaning asosiy javobi; zaif bo'lsa — e'tiroz (handle hal qiladi)
    rebuttal = (stage, role) in {("tushuntirish", "javobgar-vakili"), ("dalillar", "davogar-vakili"), ("penya", "davogar-vakili")}
    explicit = has(nt, r"e'tiroz bildir", r"e'tirozim bor", r"e'tiroz qil")
    if len(text) < 260 and (explicit or (has(nt, r"qarshi chiqaman") and has(nt, OPP_WORDS))):
        if rebuttal:
            if has(nt, r"da'vo(ga|ni|ning)\b", r"da'vo talab"):
                return None, None                       # «da'voga e'tirozimiz bor: ...» — asosiy javob
            return "objection", "rebuttal"
        return "objection", None
    return None, None


def _resume(eng):
    st, role = eng.s["stage"], eng.s["student_role"]
    r = J["RESUME"].get(st, {})
    line = r.get(role) or r.get("any")
    if isinstance(line, list):                          # variantlar navbat bilan — sudya so'zma-so'z takrorlamasin
        n = eng.s.setdefault("resume_n", {})
        i = n.get(st, 0)
        n[st] = i + 1
        line = line[i % len(line)]
    if line:
        eng.npc(line)


def _note(eng, tid, tone, why, points=0, article=None):
    eng.s.setdefault("dec_notes", {}).setdefault(tid, []).append(
        {"tone": tone, "points": points, "why": why, "better": None, "article": article})


def _count(eng, kind):
    c = eng.s.setdefault("intent_count", {})
    c[kind] = c.get(kind, 0) + 1
    return c[kind]


def handle(eng, text, nt, tid):
    """True — harakat hal qilindi (bosqich o'zgarmaydi). False — oddiy javob sifatida davom."""
    s = eng.s
    st, role = s["stage"], s["student_role"]
    kind, sub = detect(text, nt, st, role)
    if not kind:
        return False
    oname = S.OPP[s["opponent_role"]]["name"]
    if kind == "motion" and sub == "penya":
        if st in ("oldingi", "tushuntirish", "huquqlar", "rad") and not s.get("motion_penalty"):
            s["motion_penalty"] = {"tid": tid, "text": text}          # erta iltimosnoma — o'z vaqtida hal qilinadi
            eng.npc(J["M_PENYA_EARLY"], art=["IPK-169"])
            _note(eng, tid, "info", "Penya iltimosnomasi erta berildi — bayonnomaga kiritildi, dalillar bosqichida hal qilinadi.",
                  article="IPK 169-modda")
        return False                                                   # bosqich javobi sifatida ham ishlanadi
    if kind == "objection" and sub == "rebuttal" and not weak(eng, text, nt, st):
        return False                                    # mazmunli raddiya — bosqich javobi sifatida baholanadi
    if st not in CFG["stages"].get(kind, []):           # hozir emas: sudya tushuntiradi, bosqich o'zgarmaydi
        eng.npc(J[{"question": "Q_STAGE", "motion": "M_STAGE", "objection": "O_STAGE"}.get(kind, "S_CONTINUE")])
        _note(eng, tid, "info", CFG["stage_notes"][kind])
        _resume(eng)
        return True
    lim = CFG["limits"].get(kind + ("s" if kind != "settlement" else ""), 3)
    if _count(eng, kind) > lim:
        eng.npc(J["Q_LIMIT"] if kind == "question" else J["M_LIMIT"])
        _resume(eng)
        return True

    if kind == "question":
        bank = CFG["questions"].get(s["opponent_role"], [])
        texts, owner = [], []
        for i, q in enumerate(bank):
            for w in q["when"]:
                texts.append(w)
                owner.append(i)
        sc = S.nlu_rerank(text, texts) if texts else None
        best, bi = 0.0, None
        for score, i in zip(sc or [], owner):
            if score > best:
                best, bi = score, i
        if sc is None:                     # reranker yo'q — so'zlar bo'yicha
            nt_words = set(re.findall(r"[a-z']{4,}", nt))
            for i, q in enumerate(bank):
                ov = max(len(nt_words & set(re.findall(r"[a-z']{4,}", S.normalize(w)))) for w in q["when"])
                if ov >= 2 and ov / 4 > best:
                    best, bi = ov / 4, i
        if bi is None or best < 0.4:
            eng.npc(J["Q_IRRELEVANT"])
            _note(eng, tid, "bad", "Savol ish holatlariga taalluqli emas edi — savol aniq fakt (foydalanish, imzo, muddat, hisob) haqida bo'lsin.", 1)
            return True
        q = bank[bi]
        eng.npc(J["Q_FLOOR"].format(opp=oname.lower()))
        eng.next_engine = "bank"
        if q.get("reveal"):                                  # raqib noqulay faktni tan oldi
            eng.say("opponent", q["answer"], reveal=q["reveal"], gesture="sigh", emotion="uncertain",
                    reactions=[("principal", "reassured"), ("judge", "calm")])
        else:
            eng.say("opponent", q["answer"], gesture="lean-in")
        _note(eng, tid, "good", "Raqibga ishga oid savol berildi — u faktni tasdiqladi.")
        s.setdefault("asked", []).append(q["id"])
        _resume(eng)
        return True

    if kind == "motion" and sub == "evidence":
        eng.npc(J["M_EVIDENCE_HEAR"].format(opp=oname), art=["IPK-169"])
        eng.next_engine = "bank"
        eng.say("opponent", CFG["opponent"][s["opponent_role"]]["on_evidence_motion"])
        justified = has(nt, r"tasdiqla", r"isbotla", r"aniqla", r"ko'rsat", r"chunki")
        eng.npc(J["M_EVIDENCE_DENY_ENOUGH" if justified else "M_EVIDENCE_DENY_BASIS"], art=["IPK-169"])
        eng.say("secretary", CFG["hall"]["clerk_minutes"])         # muhim ajrimdan keyin — kotib
        if justified:
            _note(eng, tid, "info", "Iltimosnoma asoslangan edi; sud ishdagi yozma dalillarni yetarli deb topdi.", article="IPK 169-modda")
        else:
            _note(eng, tid, "bad", "Iltimosnomada dalil yoki guvoh qaysi holatni tasdiqlashi ko'rsatilmadi.", 1, "IPK 169-modda")
        _resume(eng)
        return True

    if kind == "motion" and sub == "postpone":
        eng.npc(J["M_POSTPONE_DENY"], gesture="shake-head", art=["IPK-171"])
        eng.say("secretary", CFG["hall"]["clerk_minutes"])
        _note(eng, tid, "bad", "Ishni qoldirish uchun uzrli sabab hujjat bilan ko'rsatilmadi.", 2, "IPK 171-modda")
        _resume(eng)
        return True

    if kind == "objection":
        based = len(text) >= 40 and has(nt, r"chunki", r"\bzid", r"tekshirilmagan", r"dalil", r"modda", r"faktura", r"shartnoma")
        eng.npc(J["O_SUSTAIN"] if based else J["O_OVERRULE"], gesture="nod" if based else "shake-head")
        _note(eng, tid, "good" if based else "bad",
              "E'tiroz asos bilan bildirildi — sud uni qabul qildi." if based
              else "E'tiroz rad etildi: raqibning qaysi gapi qaysi dalilga zidligi aytilmadi.", 0 if based else 1)
        _resume(eng)
        return True

    if kind == "settlement":
        op = CFG["opponent"][s["opponent_role"]]
        near = s["opponent_role"] == "davogar-vakili" and has(nt, r"asosiy qarz", r"qarzni (to'la|to'liq)", r"to'lashga tayyor")
        eng.next_engine = "bank"
        eng.say("opponent", op["settlement_main"] if near else op["settlement"])
        eng.npc(J["S_NEAR"] if near else J["S_CONTINUE"], art=["IPK-131", "IPK-132"])
        _note(eng, tid, "info", "Kelishuv taklif qilindi — bu ruxsat etilgan; yozma kelishuv bitimi bo'lmasa, ish davom etadi.")
        _resume(eng)
        return True
    return False


# ---------------------------------------------------------------- aniqlashtirish (qayta so'rash)
def weak(eng, text, nt, stage):
    """Muhim bosqichda javob zaifmi (sudya aniqlashtirishni so'rashi kerakmi)."""
    s, role = eng.s, eng.s["student_role"]
    od = (s.get("optdec") or {}).get(eng.cur_tid)
    if od and od.get("tone") == "bad" and stage in ("tushuntirish", "dalillar", "penya", "muzokara") and not od.get("violation"):
        return True                       # deyarli to'g'ri (xato) variant tanlandi
    if stage == "tushuntirish" and role == "davogar-vakili":
        miss = sum(1 for p in (r"shartnoma", r"25 ?620|asosiy qarz|summa|qarz", r"544|ijara haq|to'lamagan", r"peny|neustoyk|8\.5")
                   if not re.search(p, nt))
        return miss >= 2
    if stage == "tushuntirish" and role == "javobgar-vakili":
        if has(nt, r"dalolatnoma", r"topshir", r"tan olma", r"e'tiroz", r"qisman", r"peny", r"foydalan", r"578", r"541"):
            return False
        r = S.sem_scores("KM2_javobgar", text)
        return not (r and r["pos"] >= 0.2)
    if stage == "dalillar" and role == "davogar-vakili":
        if has(nt, r"foydalan", r"faktura", r"544", r"amalda", r"tan ol", r"boshqa hujjat"):
            return False
        r = S.sem_scores("KM2_davogar", text)
        return not (r and r["pos"] >= 0.2)
    if stage == "penya" and role == "davogar-vakili":
        if has(nt, r"kelish", r"yozma", r"8\.5", r"262", r"kechiktir", r"muddat", r"asos yo'q", r"rad", r"qarshi"):
            return False
        r = S.sem_scores("KM3_davogar", text)
        return not (r and r["pos"] >= 0.2)
    if stage == "muzokara":
        return len(text) < 60 or not has(nt, r"so'ra", r"undir", r"kamaytir", r"rad et", r"qanoatlantir")
    return False


def maybe_reask(eng, text, nt, tid):
    s = eng.s
    st, lv = s["stage"], s.get("level", "beginner")
    limit = CFG["reask"].get(lv, 1)
    cnt = s.setdefault("reasks", {})
    if not weak(eng, text, nt, st):
        return False
    if cnt.get(st, 0) >= limit:              # imkon tugadi — oqibat: sud borini qabul qilib davom etadi
        if cnt.get(st, 0) > 0 and not s.setdefault("reask_done", {}).get(st):
            s["reask_done"][st] = True
            eng.npc(J["R_CONTINUE"])
        return False
    cnt[st] = cnt.get(st, 0) + 1
    s.setdefault("reasked", {})[st] = True
    r = CFG["reask_text"].get(st, {})
    v = r.get(s["student_role"]) or r.get("any") or ""
    if isinstance(v, list):                              # variantlar navbat bilan — so'zma-so'z takrorlanmasin
        v = v[(cnt[st] - 1) % len(v)]
    line = v.format(role_name=S.ROLE_NAME[s["student_role"]])
    if not line:
        return False
    if hasattr(eng, "ai_judge") and eng.ai_judge(text, "Talaba javobi to'liq emas (talab, asos yoki dalil yetishmaydi) — "
                                                       "unga mos aniqlashtiruvchi savol ber.", line, tid):
        _note(eng, tid, "info", "Sudya (AI) aniqlashtirishni so'radi — javob to'liq emas edi. Keyingi javobda talab, asos va dalilni aniq ayting.")
        return True
    eng.npc(line, gesture="lean-in")
    _note(eng, tid, "info", "Sudya aniqlashtirishni so'radi — javob to'liq emas edi. Keyingi javobda talab, asos va dalilni aniq ayting.")
    return True


def cap_for(eng):
    """Qayta so'ralgan bosqichda lahza darajasi chegarasi."""
    s = eng.s
    if s.get("reasked", {}).get(s.get("stage")):
        return CFG["reask"]["cap"].get(s.get("level", "beginner"), 3)
    return 4


def pick_tie(cands_scores, seed, key, eps=0.05):
    """Deyarli teng baholi variantlardan birini seed bo'yicha tanlash — har safar bir xil bo'lmasin."""
    if not cands_scores:
        return None
    best = max(sc for _, sc in cands_scores)
    near = [c for c, sc in cands_scores if sc >= best - eps]
    return random.Random(f"{seed}:{key}").choice(near)
