"""Erkin javobni tushunish (NLU): talaba gapini eng yaqin niyatga (variantga) moslash.

POST /api/v1/nlu/match — LexSim_Backend_AI_Toliq_Topshiriq.md §4.1.
Faqat GPU reranker (bge-reranker-v2-m3) va qoidalar; LLM ishlatilmaydi. Reranker javob bermasa —
leksik moslik (sifat pastroq, javobda "engine": "lexical").
"""
import re
import time
from difflib import SequenceMatcher

# Ostonalar reranker shkalasida (2026-11-21 kalibrlash: to'g'ri parafraz 0.53–0.99, boshqa mavzu < 0.05).
# Mentor to'plami (eval/nlu_<case>.jsonl) bo'yicha qayta sozlanadi.
TH = {"match": 0.6, "clarify": 0.25, "margin": 0.15, "stt_min": 0.5, "fact": 0.3}
LEX_TH = {"match": 0.55, "clarify": 0.35}

BRIBE = [r"\bpora", r"pul (beraman|beramiz|tashlay|qilib)", r"konvert", r"sovg'a (qil|ber)", r"tanishim bor",
         r"kelishib ol(aylik|amiz).{0,30}(sudya|sud\b)", r"yolg'on ko'rsatuv", r"guvoh\w* (o'rgat|ko'ndir)"]
RUDE = [r"\b(ahmoq|tentak|jinni|axmoq|durak|idiot|haromi|iflos)\b", r"\bsen\b.{0,20}\b(bil|tushun)masan"]
# So'kinish (o'zbekcha va ruscha; textnorm kirillni lotinga o'giradi) — sud zali ham, «Ish yo'li» ham shu ro'yxatni ishlatadi
PROF = [r"\bna ?[xh]u[iy]", r"\b[xh]u[iy](lo|ny|na)?\b", r"\bpizd", r"\bbl[yi]a(t|d)?\b", r"\bblyat", r"\bsuka\b",
        r"\bjob t", r"\bye?ba(t|n|l)", r"\bsikk?(aman|ay|dim|ib|asan|aym|di|ilgan|ish|kaman|aman)\b", r"\bqo'?toq",
        r"\bjalab", r"\bonang(ni|ga|ning)\b", r"\bdal?bayob", r"\bdolboyob", r"\bposhyol\b", r"\bpashol\b", r"\bmudak",
        r"\bpidar", r"\bpederast", r"\bgandon", r"\bs[iy]?k(ib|in|aman|kin)\s+qo'?y", r"\bsikk?ib\b", r"\bqanjiq", r"\bjalap"]


def _tok(s):
    return set(re.findall(r"[a-zʻʼ']{3,}", s))


def _lex(a, b):
    ta, tb = _tok(a), _tok(b)
    if not ta or not tb:
        return 0.0
    jac = len(ta & tb) / len(ta | tb)
    return max(jac, SequenceMatcher(None, a, b).ratio() * 0.8)


def _address(nt, voice):
    if "hurmatli sud" in nt:
        return True
    if voice:   # STT murojaatni buzib yozishi mumkin — og'zaki nutqda yumshoqroq
        head = " ".join(nt.split()[:4])
        return bool(re.search(r"hurmat\w*|\bsud\b|muhtaram", head))
    return False


def match(req, normalize, rerank, exact_refs, art_ok, art_label):
    """req — so'rov JSON. rerank(query, texts) -> [scores] | None."""
    t0 = time.time()
    utt = (req.get("utterance") or "").strip()
    cands = req.get("candidates") or []
    if not utt or not isinstance(cands, list) or not (1 <= len(cands) <= 12):
        raise ValueError("utterance va 1–12 ta candidates kerak")
    mode = req.get("inputMode") or "text"
    stt = req.get("stt") or {}
    rubric = req.get("rubric") or {}
    ctx = req.get("context") or {}
    nt = normalize(utt)
    voice = mode == "voice"

    # --- sifat (variantdan qat'i nazar)
    refs = set(exact_refs(nt))
    refs |={"FPK-" + x for x in re.findall(r"fuqarolik protsessual kodeks\w*\s+(\d+)", nt)}
    arts = [{"id": r, "label": art_label(r), "valid": bool(art_ok(r))} for r in sorted(refs)]
    forbidden = [w for w in rubric.get("forbidden", []) if normalize(w) in nt]
    profane = any(re.search(p, nt) for p in PROF)
    ethics = "violation" if forbidden or profane or any(re.search(p, nt) for p in BRIBE) else "ok"
    rude = profane or any(re.search(p, nt) for p in RUDE)
    quality = {"address": _address(nt, voice), "articles": arts, "ethics": ethics,
               "politeness": 0.2 if rude else (1.0 if "hurmatli" in nt or "iltimos" in nt or "so'ray" in nt else 0.8)}

    # --- variantlar: har birining matni + misollari; nomzod bahosi = eng yuqorisi
    texts, owner = [], []
    for i, c in enumerate(cands):
        for t in [c.get("text", "")] + list(c.get("examples") or [])[:6]:
            if t:
                texts.append(t)
                owner.append(i)
    facts = rubric.get("facts") or {}         # {"sick": "kasallik varaqasi..." | ["kasal", "varaqa"]}
    fact_ids = [f for f in rubric.get("mustCiteFacts", []) if isinstance(facts.get(f), str)]
    scores = rerank(utt, texts + [facts[f] for f in fact_ids]) if texts else None
    engine = "reranker" if scores is not None else "lexical"
    th = TH if scores is not None else LEX_TH
    if scores is None:
        scores = [_lex(nt, normalize(t)) for t in texts] + [_lex(nt, normalize(facts[f])) for f in fact_ids]
    best = [0.0] * len(cands)
    for sc, i in zip(scores[:len(texts)], owner):
        best[i] = max(best[i], sc)

    # faktlar: matnli ta'rif — reranker/leksik baho; kalit so'zlar ro'yxati — so'z bo'yicha
    cited = []
    for f, sc in zip(fact_ids, scores[len(texts):]):
        if sc >= (TH["fact"] if engine == "reranker" else 0.25):
            cited.append(f)
    for f in rubric.get("mustCiteFacts", []):
        kws = facts.get(f)
        if isinstance(kws, list) and any(normalize(k) in nt for k in kws):
            cited.append(f)
    if rubric.get("mustCiteFacts"):
        quality["factsCited"] = sorted(set(cited))
        quality["factsMissing"] = [f for f in rubric["mustCiteFacts"] if f not in cited]

    order = sorted(range(len(cands)), key=lambda i: -best[i])
    top = order[0]
    alts = [{"id": cands[i]["id"], "score": round(best[i], 3)} for i in order[1:4]]
    res = {"match": None, "alternatives": alts, "quality": quality, "clarify": None, "engine": engine,
           "thresholds": th, "ms": None}

    if voice and isinstance(stt.get("confidence"), (int, float)) and stt["confidence"] < TH["stt_min"]:
        res["clarify"] = "Iltimos, fikringizni aniqroq takrorlang."
        res["reason"] = "low_stt"
    elif best[top] >= th["match"]:
        second = order[1] if len(order) > 1 else None
        ambiguous = (second is not None and best[top] - best[second] < TH["margin"]
                     and cands[top].get("tone") != cands[second].get("tone"))
        if ambiguous:     # yaxshi va yomon niyat orasida — taxmin qilmaymiz, aniqlashtiramiz
            res["clarify"] = _clarify(ctx)
            res["reason"] = "ambiguous"
            res["alternatives"] = [{"id": cands[top]["id"], "score": round(best[top], 3)}] + alts
        else:
            res["match"] = {"id": cands[top]["id"], "score": round(best[top], 3), "tone": cands[top].get("tone")}
    elif best[top] >= th["clarify"]:
        res["clarify"] = _clarify(ctx)
        res["reason"] = "low_score"
        res["alternatives"] = [{"id": cands[top]["id"], "score": round(best[top], 3)}] + alts
    else:
        res["reason"] = "no_match"
    if ethics == "violation":
        res["reason"] = "ethics"            # etika har doim ustun
    res["ms"] = round((time.time() - t0) * 1000)
    return res


def _clarify(ctx):
    p = (ctx.get("prompt") or "").strip()
    if p:
        return "Fikringizni aniqroq bayon qiling: qaysi holat va dalilga tayanasiz?"
    return "Iltimos, fikringizni aniqroq bayon qiling."
