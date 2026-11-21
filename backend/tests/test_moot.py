import json
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import moot as MOOT  # noqa: E402

CASE = {"id": "ijara", "title": "Ijara qarzi", "claim": "120 mln so'm qarz va penya undirish",
        "facts": [{"id": "f1", "title": "Shartnoma", "text": "Shartnomaning 32-punkti penyani belgilaydi. FK 333-modda."}],
        "evidence": [{"id": "e1", "title": "Faktura", "text": "Imzolangan fakturalar"}],
        "side": {"claimant": {"task": [], "confidential": []}, "respondent": {"task": [], "confidential": []}}}
TR = [{"seq": 1, "by": "pA", "name": "Aziza", "side": "claimant", "text": "Hurmatli sud, javobgar 120 mln so'm qarz.", "step": "claim"},
      {"seq": 2, "by": "pB", "name": "Bekzod", "side": "respondent", "text": "Hurmatli sud, dalolatnoma imzolanmagan.", "step": "answer"}]
PL = [{"id": "pA", "name": "Aziza", "side": "claimant"}, {"id": "pB", "name": "Bekzod", "side": "respondent"}]


def body(tr=TR):
    return {"case": CASE, "agenda": [], "transcript": tr, "players": PL}


def raw(c, r, ruling=None):
    return {"criteria": [{"id": i, "claimant": c, "respondent": r, "note": "Izoh."} for i, _, _ in MOOT.CRITERIA],
            "ruling": ruling or ["Sud dalillarni ko'rdi.", "Da'vo qanoatlantirilsin."],
            "players": [{"name": "Aziza", "note": "Yaxshi."}]}


def fake(resp, delay=0):
    calls = []

    def ask(prompt, timeout):
        calls.append(prompt)
        time.sleep(delay)
        return (json.dumps(resp) if resp else None), "chatgpt", 10, None if resp else "xato"
    ask.calls = calls
    return ask


NOPROF = lambda t: "sik" in t  # noqa: E731


class MootJudge(unittest.TestCase):
    def setUp(self):
        MOOT.CACHE.clear()

    def test_winner_clamp_and_no_real_ruling(self):
        v = MOOT.judge(body(), fake(raw(99, 3)), NOPROF)
        self.assertEqual(v["winner"], "claimant")
        self.assertEqual(v["totals"]["claimant"], 100)               # max bilan chegaralandi
        self.assertFalse(any("qanoatlantiril" in x for x in v["ruling"]))
        self.assertEqual(v["ruling"][-1], "Bahsda daʼvogar tomoni ustun keldi.")
        self.assertTrue(3 <= len(v["ruling"]) <= 6)
        self.assertEqual({c["id"] for c in v["criteria"]}, {i for i, _, _ in MOOT.CRITERIA})
        a = next(p for p in v["players"] if p["id"] == "pA")
        self.assertEqual((a["speeches"], a["note"]), (1, "Yaxshi."))

    def test_draw_within_two_points(self):
        r = raw(10, 10)
        r["criteria"][0]["claimant"] = 12
        v = MOOT.judge(body(), fake(r), NOPROF)
        self.assertIsNone(v["winner"])
        self.assertEqual(v["ruling"][-1], "Bahs durang bilan yakunlandi.")

    def test_profanity_zeroes_manners(self):
        tr = TR + [{"seq": 3, "by": "pB", "name": "Bekzod", "side": "respondent", "text": "sikaman", "step": "close2"}]
        v = MOOT.judge(body(tr), fake(raw(10, 15)), NOPROF)
        m = next(c for c in v["criteria"] if c["id"] == "manners")
        self.assertEqual(m["respondent"], 0)

    def test_unsourced_article_removed(self):
        r = raw(20, 10, ["FK 333-modda qo'llanadi.", "FK 999-modda buzilgan.", "Javobgar dalil keltirmadi."])
        v = MOOT.judge(body(), fake(r), NOPROF)
        txt = " ".join(v["ruling"])
        self.assertIn("333-modda", txt)
        self.assertNotIn("999", txt)

    def test_cache_same_transcript(self):
        a = fake(raw(20, 10))
        MOOT.judge(body(), a, NOPROF)
        MOOT.judge(body(), a, NOPROF)
        self.assertEqual(len(a.calls), 1)

    def test_pending_then_cached(self):
        old = MOOT.WAIT_S
        MOOT.WAIT_S = 0.2
        try:
            a = fake(raw(20, 10), delay=0.6)
            with self.assertRaises(MOOT.JudgeError) as e:
                MOOT.judge(body(), a, NOPROF)
            self.assertEqual(e.exception.code, "judge_pending")
            time.sleep(0.8)
            v = MOOT.judge(body(), a, NOPROF)
            self.assertEqual(v["winner"], "claimant")
            self.assertEqual(len(a.calls), 1)
        finally:
            MOOT.WAIT_S = old

    def test_model_failure_is_503(self):
        with self.assertRaises(MOOT.JudgeError) as e:
            MOOT.judge(body(), fake(None), NOPROF)
        self.assertEqual((e.exception.status, e.exception.code), (503, "judge_unavailable"))

    def test_validation(self):
        with self.assertRaises(MOOT.JudgeError):
            MOOT.judge({"case": CASE}, fake(raw(1, 1)), NOPROF)

    def test_verdict_by_id(self):
        b = dict(body(), participants=[{"owner": "ownerA0001", "side": "claimant"}, {"owner": "ownerB0002", "side": "respondent"}])
        MOOT.judge(b, fake(raw(20, 10)), NOPROF, owner="hostH0003")
        vid = MOOT.key_of(b)[:16]
        v = MOOT.by_id(vid, "claimant", owner="ownerB0002", case_id="ijara")
        self.assertEqual((v["verified"], v["winner"], v["side"], v["won"]), (True, "claimant", "respondent", False))  # tomonni o'zi tanlay olmaydi
        self.assertTrue(MOOT.by_id(vid, None, owner="ownerA0001", case_id="ijara")["won"])
        self.assertIsNone(MOOT.by_id(vid, "claimant", owner="strangerX9", case_id="ijara"))       # ishtirokchi emas
        self.assertIsNone(MOOT.by_id(vid, "claimant", owner="ownerA0001", case_id="boshqa"))       # boshqa case
        self.assertIsNone(MOOT.by_id("0" * 16, owner="ownerA0001"))
        self.assertIsNone(MOOT.by_id("../etc"))

    def test_art_regex_is_linear(self):
        import time as _t
        for bad in ("1" * 16000, "1." * 8000, "1" + " " * 16000):
            t0 = _t.time()
            list(MOOT.ART.finditer(MOOT._s(bad, 20000)))
            self.assertLess(_t.time() - t0, 0.5)
        self.assertEqual([m.group(1) for m in MOOT.ART.finditer("FK 333-moddaning 2-qismi va 7.1-modda")], ["333", "7.1"])


class MootRubric(unittest.TestCase):
    def setUp(self):
        MOOT.CACHE.clear()
        MOOT.RB.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rubrics.json"))

    def tearDown(self):
        MOOT.RB.RUBRICS.clear()

    def test_rubric_verdict_from_items(self):
        tr = TR + [{"seq": 3, "by": "pA", "name": "Aziza", "side": "claimant", "step": "close1",
                    "text": "Hurmatli sud, FK 333-modda va shartnomaning 32-punkti bo'yicha penya undirilsin, fakturalar imzolangan."}]
        ai = [{"id": "F2", "side": "claimant", "met": "yes", "quotes": ["fakturalar imzolangan"], "why": "dalil"},
              {"id": "R1", "side": "respondent", "met": "yes", "quotes": ["dalolatnoma imzolanmagan"], "why": "javob"},
              {"id": "F4", "side": "respondent", "met": "yes", "quotes": ["bu gap bayonnomada yo'q"], "why": "uydirma?"}]

        def ask(prompt, timeout):
            self.assertIn("F2", prompt)
            self.assertNotIn("L1:", prompt)                                 # qoida bandlari AI'ga yuborilmaydi
            return json.dumps({"items": ai}), "chatgpt", 5, None
        b = {"case": CASE, "agenda": [{"id": "claim", "side": "claimant"}, {"id": "answer", "side": "respondent"}],
             "transcript": tr, "players": PL}
        v = MOOT.judge(b, ask, NOPROF)
        crit = {c["id"]: c for c in v["criteria"]}
        self.assertEqual({c["id"]: c["max"] for c in v["criteria"]},
                         {"legal": 30, "rebuttal": 25, "facts": 20, "participation": 15, "manners": 10})
        self.assertGreater(crit["legal"]["claimant"], 0)                     # L1 qoida: FK 333 materiallarda bor
        self.assertGreater(crit["rebuttal"]["respondent"], crit["rebuttal"]["claimant"])
        self.assertEqual(crit["manners"]["claimant"], 10)                    # «Hurmatli sud» bor
        self.assertEqual(sum(c["claimant"] for c in v["criteria"]), v["totals"]["claimant"])
        self.assertTrue(v["ruling"][-1].startswith("Bahs"))
        ex = MOOT.explain_of(b)
        f4 = next(x for x in ex["sides"]["respondent"]["items"] if x["id"] == "F4")
        self.assertEqual(f4["met"], "no")                                    # uydirma iqtibos — tasdiqlanmadi, jazo ham yo'q
        self.assertTrue(ex["needsMentor"])
        l1 = next(x for x in ex["sides"]["claimant"]["items"] if x["id"] == "L1")
        self.assertEqual((l1["met"], l1["evidence"][0]["turnId"]), ("yes", "3"))
        self.assertTrue(all(x.get("basis") for x in ex["sides"]["claimant"]["items"]))


    def test_ethics_cap_applies_to_verdict(self):
        tr = [{"seq": 1, "by": "pA", "name": "Aziza", "side": "claimant", "step": "claim",
               "text": "Hurmatli sud, FK 333-modda bo'yicha fakturalar imzolangan, sikaman"},
              {"seq": 2, "by": "pB", "name": "Bekzod", "side": "respondent", "step": "answer", "text": "Hurmatli sud, rad etamiz."}]
        yes = [{"id": i, "side": "claimant", "met": "yes", "quotes": ["fakturalar imzolangan"], "why": ""}
               for i in ("L2", "L3", "R1", "F1", "F2", "F3", "P3")]

        def ask(prompt, timeout):
            return json.dumps({"items": yes}), "chatgpt", 5, None
        v = MOOT.judge({"case": CASE, "agenda": [], "transcript": tr, "players": PL}, ask, NOPROF)
        self.assertLessEqual(v["totals"]["claimant"], 40)                    # so'kingan tomon chegaradan oshmaydi
        self.assertEqual(sum(1 for r in v["ruling"] if "ustun" in r), 1)

    def test_malformed_ai_item_ignored_and_na_counts_as_no(self):
        items = [{"id": ["L2"], "side": "claimant", "met": "yes"}, {"id": "F2", "side": "claimant", "met": "yes", "quotes": {"x": 1}},
                 {"id": "F1", "side": "claimant", "met": "na"}, {"id": "R2", "side": "claimant", "met": "na"}]

        def ask(prompt, timeout):
            return json.dumps({"items": items}), "chatgpt", 5, None
        MOOT.judge(body(), ask, NOPROF)
        ex = MOOT.explain_of(body())
        it = {x["id"]: x for x in ex["sides"]["claimant"]["items"]}
        self.assertEqual(it["F1"]["met"], "no")                              # majburiy bandda «na» → «yo'q»
        self.assertEqual(it["R2"]["met"], "na")                              # ixtiyoriy bandda «na» qoladi
        self.assertEqual(it["F2"]["met"], "no")                              # iqtibossiz «ha» → ball yo'q

if __name__ == "__main__":
    unittest.main()
