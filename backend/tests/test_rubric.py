import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rubric as RB  # noqa: E402

R = {"id": "t", "version": "t1", "title": "test", "scale": "", "basis": [], "judgeRole": "sudya",
     "routing": {"heavyWeight": 3, "passMark": 0, "nearPass": 0},
     "dims": [{"id": "facts", "label": "Faktlar", "max": 30}, {"id": "manners", "label": "Odob", "max": 10}],
     "items": [
         {"id": "f1", "dim": "facts", "ask": "Dalilga tayandimi?", "weight": 4, "method": "ai"},
         {"id": "f2", "dim": "facts", "ask": "Raqibga javob berdimi?", "weight": 2, "method": "ai"},
         {"id": "f3", "dim": "facts", "ask": "Uydirma fakt?", "weight": -3, "method": "ai"},
         {"id": "m1", "dim": "manners", "ask": "Hurmatli sud dedimi?", "weight": 2, "method": "rule"},
         {"id": "m2", "dim": "manners", "ask": "So'kindimi?", "weight": -2, "method": "rule", "capTotal": 20}]}
TR = [{"id": "t1", "side": "claimant", "text": "Hurmatli sud, javobgar direktori imzolagan fakturalar mol topshirilganini isbotlaydi."},
      {"id": "t2", "side": "respondent", "text": "Hurmatli sud, dalolatnoma yo'q, shuning uchun faktura yetarli emas."}]


def ask_with(items_by_run):
    calls = []

    def ask(prompt, timeout):
        calls.append(prompt)
        return json.dumps({"items": items_by_run[len(calls) - 1]}), "chatgpt", 5, None
    ask.calls = calls
    return ask


def rules(it, sd):
    if it["id"] == "m1":
        return True, ["t1" if sd == "claimant" else "t2"], "murojaat bor"
    return False, [], "so'kinish yo'q"


class Rubric(unittest.TestCase):
    def setUp(self):
        RB.RUBRICS.clear()
        RB.RUBRICS["t"] = R

    def test_quote_verification(self):
        self.assertEqual(RB.find_quote("fakturalar mol topshirilganini", [("t1", TR[0]["text"])])[0], "t1")
        self.assertEqual(RB.find_quote("fakturalar mol topshrilganini", [("t1", TR[0]["text"])])[0], "t1")   # STT xatosi
        self.assertIsNone(RB.find_quote("shartnoma bekor qilingan edi", [("t1", TR[0]["text"])])[0])

    def test_scores_from_items_and_unverified_quote(self):
        run = [{"id": "f1", "side": "claimant", "met": "yes", "quotes": ["fakturalar mol topshirilganini isbotlaydi"], "why": "dalil"},
               {"id": "f2", "side": "claimant", "met": "yes", "quotes": ["men raqibga javob berdim"], "why": "?"},
               {"id": "f3", "side": "claimant", "met": "no", "quotes": [], "why": ""},
               {"id": "f1", "side": "respondent", "met": "no", "quotes": [], "why": ""},
               {"id": "f2", "side": "respondent", "met": "yes", "quotes": ["dalolatnoma yo'q, shuning uchun faktura yetarli emas"], "why": "javob"},
               {"id": "f3", "side": "respondent", "met": "no", "quotes": [], "why": ""}]
        out, err = RB.grade("t", ["claimant", "respondent"], TR, "", rules, ask_with([run]))
        c = out["sides"]["claimant"]
        f2 = next(x for x in c["items"] if x["id"] == "f2")
        self.assertEqual(f2["met"], "no")                                   # uydirma iqtibos — ball yo'q
        self.assertTrue(f2["unverifiedQuotes"])
        facts = next(x for x in c["criteria"] if x["id"] == "facts")
        self.assertEqual(facts["score"], 20.0)                              # 4/6 * 30
        self.assertEqual(next(x for x in out["sides"]["respondent"]["criteria"] if x["id"] == "facts")["score"], 10.0)
        self.assertTrue(out["needsMentor"])
        self.assertIn("iqtibos", out["routing"][0]["reason"])
        f1 = next(x for x in c["items"] if x["id"] == "f1")
        self.assertEqual(f1["evidence"][0]["turnId"], "t1")                 # dalil — aniq gap

    def test_majority_and_band(self):
        y = {"id": "f1", "side": "claimant", "met": "yes", "quotes": ["fakturalar mol topshirilganini"], "why": ""}
        n = {"id": "f1", "side": "claimant", "met": "no", "quotes": [], "why": ""}
        out, _ = RB.grade("t", ["claimant"], TR, "", rules, ask_with([[y], [y], [n]]), runs=3)
        c = out["sides"]["claimant"]
        f1 = next(x for x in c["items"] if x["id"] == "f1")
        self.assertEqual((f1["met"], f1["agree"]), ("yes", 0.67))
        self.assertLess(c["band"][0], c["total"])                           # kelishmovchilik — oraliq
        self.assertTrue(any("kelishmadi" in r["reason"] for r in out["routing"]))

    def test_cap_on_ethics(self):
        def rules2(it, sd):
            return (True, ["t1"], "") if it["id"] in ("m1", "m2") else (False, [], "")
        y = [{"id": i, "side": "claimant", "met": "yes", "quotes": ["fakturalar mol topshirilganini"], "why": ""} for i in ("f1", "f2")]
        out, _ = RB.grade("t", ["claimant"], TR, "", rules2, ask_with([y]))
        self.assertLessEqual(out["sides"]["claimant"]["total"], 20)
        self.assertTrue(any("etika" in r["reason"] for r in out["routing"]))

    def test_shuffle_changes_order_not_ids(self):
        a = RB.prompt_of(R, R["items"][:3], ["claimant"], "", "", 1)
        b = RB.prompt_of(R, R["items"][:3], ["claimant"], "", "", 2)
        self.assertEqual(sorted(x for x in ("f1", "f2", "f3") if x in a), sorted(x for x in ("f1", "f2", "f3") if x in b))

    def test_ai_failure(self):
        def bad(p, t):
            return None, "chatgpt", 5, "xato"
        out, err = RB.grade("t", ["claimant"], TR, "", rules, bad)
        self.assertIsNone(out)
        self.assertEqual(err, ["xato"])


if __name__ == "__main__":
    unittest.main()
