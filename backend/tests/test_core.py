"""LexSim backend unit testlari (stdlib unittest). Serverda: cd ~/lexsim/backend && ../venv/bin/python -m unittest -v tests.test_core"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("LEXSIM_STATE_DB", tempfile.mktemp(suffix=".db"))
os.environ["LEXSIM_DSN"] = ""                      # testda RAG bazasiz
import lexsim_server as L  # noqa: E402
import nlu as NLU  # noqa: E402
import store as ST  # noqa: E402

L.NORMS = L.Norms()


class Orthography(unittest.TestCase):
    def test_uz_norm(self):
        self.assertEqual(L.uz_norm("O'zbekiston bo'yicha da'vo ma'lumot"), "Oʻzbekiston boʻyicha daʼvo maʼlumot")
        self.assertEqual(L.uz_norm("g‘alaba"), "gʻalaba")
        self.assertEqual(L.uz_norm({"a": ["so'm"]}), {"a": ["soʻm"]})
        self.assertEqual(L.uz_norm("https://lex.uz/docs/111181#-155297"), "https://lex.uz/docs/111181#-155297")

    def test_art_label(self):
        self.assertEqual(L.art_label("FK-326"), "FK 326-modda")
        self.assertEqual(L.art_label("OXS163-p4"), "OXS163 4-band")


class LlmCheck(unittest.TestCase):
    NUM = "2022 32 544 578 541 326 262 333 8.5 6.4"

    def test_ok_and_formatting(self):
        out, why = L.llm_check("Javobgar vakili: Hurmatli sud, obyekt FK-578 moddaga ko'ra topshirilmagan. Hurmatli sud, penya katta.",
                               "", "", {"FK-578"}, self.NUM)
        self.assertIsNone(why)
        self.assertTrue(out.startswith("Hurmatli sud,"))
        self.assertIn("FK 578-moddaga", out)
        self.assertEqual(out.count("Hurmatli sud"), 1)

    def test_rejects(self):
        self.assertEqual(L.llm_check("Hurmatli sud, 9999 so'm undirilsin.", "", "", None, self.NUM)[1], "taqiqlangan mazmun")
        self.assertEqual(L.llm_check("Hurmatli sud, 777 so'm qarz bor.", "", "", None, self.NUM)[1], "yangi raqam 777")
        self.assertEqual(L.llm_check("Hurmatli sud, hisob-fakturalar imzolanmagan.", "", "", None, self.NUM)[1], "taqiqlangan mazmun")
        self.assertIn("ruxsat etilmagan", L.llm_check("Hurmatli sud, FK 544-moddaga ko'ra.", "", "", {"FK-578"}, self.NUM)[1])
        self.assertEqual(L.llm_check("Хурматли суд, бу ҳақда.", "", "", None, self.NUM)[1], "uzunlik/kirill")


class Nlu(unittest.TestCase):
    CANDS = [{"id": "good", "text": "Hurmatli sud, penyani FK 326-modda bo'yicha kamaytirishni so'rayman.", "tone": "good"},
             {"id": "bad", "text": "Hurmatli sud, penyani butunlay bekor qiling.", "tone": "bad"}]

    def run_match(self, utt, scores, **kw):
        req = {"utterance": utt, "candidates": self.CANDS, **kw}
        return NLU.match(req, L.normalize, lambda q, t: scores, L.exact_refs, lambda r: True, L.art_label)

    def test_match_good(self):
        r = self.run_match("Hurmatli sud, penyani kamaytiring", [0.9, 0.1])
        self.assertEqual(r["match"]["id"], "good")
        self.assertTrue(r["quality"]["address"])

    def test_ambiguous_good_bad(self):
        r = self.run_match("Hurmatli sud, penya haqida", [0.7, 0.65])
        self.assertIsNone(r["match"])
        self.assertEqual(r["reason"], "ambiguous")

    def test_low_stt(self):
        r = self.run_match("hurmatli sud", [0.9, 0.1], inputMode="voice", stt={"confidence": 0.4})
        self.assertIsNone(r["match"])
        self.assertEqual(r["reason"], "low_stt")

    def test_ethics_and_voice_address(self):
        r = self.run_match("hurmatli sut, pora beraman", [0.9, 0.1], inputMode="voice")
        self.assertEqual(r["quality"]["ethics"], "violation")
        self.assertTrue(r["quality"]["address"])          # og'zaki nutqda yumshoq

    def test_lexical_fallback(self):
        r = self.run_match("Hurmatli sud, penyani FK 326-modda bo'yicha kamaytirishni so'rayman.", None)
        self.assertEqual(r["engine"], "lexical")
        self.assertEqual(r["match"]["id"], "good")


class Store(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ST.init(tempfile.mktemp(suffix=".db"))

    def test_case_versioning(self):
        self.assertEqual(ST.case_put("case-001", {"owner": "h1", "kind": "labour", "state": {"a": 1}, "version": 0})["version"], 1)
        with self.assertRaises(ST.StoreError) as e:
            ST.case_put("case-001", {"owner": "h1", "kind": "labour", "state": {"a": 2}, "version": 0})
        self.assertEqual(e.exception.status, 409)
        self.assertEqual(ST.case_put("case-001", {"owner": "h1", "kind": "labour", "state": {"a": 2}, "version": 1})["version"], 2)
        with self.assertRaises(ST.StoreError) as e:
            ST.case_put("case-001", {"owner": "h2", "kind": "labour", "state": {}, "version": 2})
        self.assertEqual(e.exception.status, 404)                      # boshqa talabaniki — mavjudligi bilinmaydi
        self.assertEqual(ST.case_get("case-001", "h1")["state"], {"a": 2})

    def test_store_any_kind_owner_404_and_ttl(self):                  # v16 B9
        import time as _t
        self.assertEqual(ST.case_put("dxm-test-1", {"kind": "dxm-session", "state": {"turns": [1, 2]}}, owner="o1")["version"], 1)
        self.assertEqual(ST.case_get("dxm-test-1", "o1")["state"], {"turns": [1, 2]})
        with self.assertRaises(ST.StoreError) as e:
            ST.case_get("dxm-test-1", "o2")
        self.assertEqual(e.exception.status, 404)
        ST.case_put("hearing-h1", {"kind": "hearing", "state": {}}, owner="o1")
        ST.case_put("case-keep", {"kind": "case", "state": {}}, owner="o1")
        with ST._lock:                                                    # 8 kun oldin yozilgan deb belgilaymiz
            ST._db.execute("UPDATE case_state SET updated=? WHERE id IN ('hearing-h1','case-keep')", (_t.time() - 8 * 86400,))
            ST._db.commit()
        self.assertGreaterEqual(ST.purge(), 1)
        with self.assertRaises(ST.StoreError):
            ST.case_get("hearing-h1", "o1")                               # 7 kunlik tur — o'chdi
        self.assertEqual(ST.case_get("case-keep", "o1")["state"], {})     # 180 kunlik tur — qoladi

    def test_xapi_and_teacher(self):
        ext = {"https://lexsim.uz/xapi/cohort": "g1"}
        ids, stored = ST.xapi_put([
            {"actor": {"account": {"name": "s1"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
             "object": {"id": "case:labour"}, "result": {"score": {"raw": 80}, "duration": "PT10M"}, "context": {"extensions": ext}},
            {"actor": {"account": {"name": "s1"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/answered"},
             "object": {"id": "case:labour#h-explain", "definition": {"name": {"uz": "Tushuntirish"}}},
             "result": {"success": False, "extensions": {"https://lexsim.uz/xapi/article": "FPK 227-modda"}},
             "context": {"extensions": ext}}])
        self.assertEqual(stored, 2)
        sm = ST.cohort_summary("g1")["students"][0]
        self.assertEqual((sm["avgScore"], sm["errors"], sm["timeSec"]), (80, 1, 600))
        hs = ST.cohort_hotspots("g1")["hotspots"][0]
        self.assertEqual((hs["objectId"], hs["articles"]), ("case:labour#h-explain", ["FPK 227-modda"]))
        with self.assertRaises(ST.StoreError):
            ST.xapi_put({"actor": {"name": "Ism Familiya"}, "verb": {"id": "x"}, "object": {"id": "y"}})


class Options(unittest.TestCase):
    def test_every_stage_has_1_good_3_bad_similar_length_and_no_leak(self):
        for stage, by_role in L.OPTIONS.items():
            for role, opts in by_role.items():
                tones = sorted(o["tone"] for o in opts)
                self.assertEqual(tones, ["bad", "bad", "bad", "good"], (stage, role))
                ln = [len(o["text"]) for o in opts]
                m = sum(ln) / len(ln)
                self.assertTrue(all(0.8 <= x / m <= 1.2 for x in ln), (stage, role, ln))
                for o in opts:
                    if o["tone"] == "bad":
                        self.assertTrue(o.get("why"), (stage, role, o["id"]))
        s = L.new_session("sud-ijara-javobgar", "tutorial", 7, "owner")
        s.update(status="in-progress", stage="dalillar", turns=[{"id": "t_1"}])
        view = L.level_view(s)
        self.assertEqual(len(view["options"]), 4)
        self.assertTrue(all(set(o) == {"id", "text", "kind"} for o in view["options"]))   # tone/why oshkor emas
        s["level"] = "advanced"
        self.assertEqual(L.level_view(s)["options"], [])


class VoiceMeta(unittest.TestCase):
    def test_word_timings(self):
        import voice as V
        wt = V.word_timings("Sud majlisi ochiq deb e'lon qilinadi.", 3000)
        self.assertEqual(len(wt), 6)
        self.assertTrue(all(a < b for a, b in wt) and wt[-1][1] <= 3000)


class Breaker(unittest.TestCase):
    def test_gpu_breaker(self):
        import voice as V
        self.assertFalse(V.gpu_down("test-x"))
        V.gpu_failed("test-x")
        self.assertTrue(V.gpu_down("test-x"))


class ReplyBank(unittest.TestCase):
    def test_bank_texts_pass_llm_check(self):
        nums = L.SCEN["sud-ijara-javobgar"]["numbers"]
        for role, moments in L.REPLIES["bank"].items():
            allowed = set(L.ROLES[role]["ruxsat_moddalar"])
            for key, variants in moments.items():
                self.assertEqual(sum(1 for v in variants if v.get("generic")), 1, (role, key))
                for v in variants:
                    out, why = L.llm_check(v["text"], "", "", allowed, nums)
                    self.assertIsNone(why, (role, key, v["id"], why))
                    self.assertTrue(v.get("generic") or v["when"], v["id"])


if __name__ == "__main__":
    unittest.main()
