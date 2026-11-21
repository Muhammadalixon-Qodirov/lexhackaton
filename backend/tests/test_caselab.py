import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import caselab as LAB  # noqa: E402

ALLOWED = {"FK-333": {"label": "FK 333-modda", "url": "https://lex.uz/docs/111181#333", "title": "Javobgarlik asoslari"}}
RAW = {
    "title": "Yetkazib berilmagan un", "court": "Toshkent tumanlararo iqtisodiy sudi", "summary": "Un kech yetkazildi.",
    "parties": {"claimant": "«A» MChJ", "respondent": "«B» MChJ"}, "claim": "Penya undirish, FK 333-modda va FK 999-modda asosida",
    "facts": [{"title": "Shartnoma", "text": "1-martda shartnoma tuzildi."}, {"title": "Kechikish", "text": "Un 20 kun kech keldi."},
              {"title": "Pretenziya", "text": "Pretenziya yuborildi."}],
    "evidence": [{"title": "Yuk xati", "text": "Yuk xati 21-martda imzolangan."}],
    "side": {"claimant": {"task": ["Penyani undiring"], "confidential": ["Omborda joy yo'q edi", "Buyurtma kech berilgan"]},
             "respondent": {"task": ["Kamaytirishni so'rang"], "confidential": ["Haydovchi kasal bo'lgan", "Yo'l yopiq edi"]}},
    "legal": [{"normId": "FK-333", "why": "aybsiz javobgarlik"}, {"normId": "FK-777"}],
    "balance": {"claimant_strong": "yuk xati", "claimant_weak": "pretenziya kech", "respondent_strong": "fors-major", "respondent_weak": "xabar bermagan"},
    "points": {"claimant": [["yuk xati"], ["penya"]]}, "questions": ["Shartnomada penya foizi qancha?"]}


class CaseLab(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        LAB.init(self.tmp.name)
        LAB.DRAFTS.clear()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_redact_pii(self):
        t, n = LAB.redact("Tel +998 90 123 45 67, pasport AB1234567, JSHSHIR 31234567890123, a@b.uz")
        self.assertEqual(n, 4)
        for x in ("123 45 67", "AB1234567", "31234567890123", "a@b.uz"):
            self.assertNotIn(x, t)

    def test_normalize_strips_unsourced(self):
        c, issues = LAB.normalize_case(RAW, "supply", ALLOWED)
        self.assertIn("333-modda", c["claim"])
        self.assertNotIn("999", c["claim"])
        self.assertEqual([x["normId"] for x in c["legal"]], ["FK-333"])
        self.assertTrue(any("999" in i for i in issues) and any("FK-777" in i for i in issues))
        self.assertEqual(LAB.check(c), [])
        self.assertEqual([f["id"] for f in c["facts"]], ["f1", "f2", "f3"])

    def test_check_flags_gaps(self):
        r = dict(RAW, facts=RAW["facts"][:1], side={"claimant": {"task": [], "confidential": ["x1"]}, "respondent": {}}, legal=[])
        c, _ = LAB.normalize_case(r, "supply", ALLOWED)
        iss = " | ".join(LAB.check(c))
        for w in ("faktlar kam", "maxfiy faktlar 1 ta", "vazifa yo'q", "huquqiy asos yo'q"):
            self.assertIn(w, iss)

    def test_visibility_and_review(self):
        c, _ = LAB.save("owner_aaaa1111", RAW, "supply", None, {"FK-333": ALLOWED["FK-333"]})
        cid = c["id"]
        self.assertEqual((c["status"], c["mine"]), ("review", True))
        self.assertEqual(len(c["side"]["claimant"]["confidential"]), 2)           # muallif ko'radi
        with self.assertRaises(LAB.LabError):
            LAB.get("owner_bbbb2222", cid)                                         # boshqa — ko'rmaydi
        self.assertEqual(LAB.listing("owner_bbbb2222", "supply"), [])
        LAB.review(cid, "approve", "Yaxshi")
        other = LAB.get("owner_bbbb2222", cid)
        self.assertEqual(other["side"]["claimant"]["confidential"], [])            # maxfiy — faqat bahs xonasida
        self.assertNotIn("balance", other)
        self.assertEqual(len(LAB.get("owner_bbbb2222", cid, full=True)["side"]["respondent"]["confidential"]), 2)
        self.assertEqual([x["id"] for x in LAB.listing("owner_bbbb2222", "supply")], [cid])
        c2, _ = LAB.save("owner_aaaa1111", dict(RAW, title="Yangi"), "supply", None, {}, cid)   # tahrir — qayta tekshiruvga
        self.assertEqual((c2["status"], c2["title"], c2["legal"]), ("review", "Yangi", []))

    def test_draft_flow(self):
        prompts = []

        def ask(p, timeout):
            prompts.append(p)
            return json.dumps(RAW), "chatgpt", 10, None
        did = LAB.start_draft("owner_aaaa1111", "supply",
                              "Biz un sotib oldik, 20 kun kech keldi, telefonim +998901234567. " * 3, ask, lambda s, ct, hint="": ALLOWED)
        LAB.DRAFTS[did]["event"].wait(5)
        d = LAB.get_draft("owner_aaaa1111", did)
        self.assertEqual(d["status"], "ready")
        self.assertEqual(d["case"]["legal"][0]["normId"], "FK-333")
        self.assertEqual(d["redacted"], 3)
        self.assertNotIn("901234567", prompts[0])
        self.assertIn("FK-333", prompts[0])
        with self.assertRaises(LAB.LabError):
            LAB.get_draft("owner_bbbb2222", did)

    def test_draft_validation(self):
        with self.assertRaises(LAB.LabError):
            LAB.start_draft("owner_aaaa1111", "supply", "qisqa", None, None)
        with self.assertRaises(LAB.LabError):
            LAB.start_draft("owner_aaaa1111", "nope", "x" * 100, None, None)

    def test_system_seed(self):
        pkg = json.load(open(os.path.join(os.path.dirname(__file__), "..", "scenarios", "sud-ijara.json"), encoding="utf-8"))
        LAB.seed_system([("s_ijara", "lease", LAB.system_from_scenario(pkg))])
        items = LAB.listing("owner_bbbb2222", "lease")
        self.assertEqual((items[0]["id"], items[0]["source"], items[0]["status"]), ("s_ijara", "system", "approved"))
        full = LAB.get("owner_bbbb2222", "s_ijara", full=True)
        self.assertTrue(full["side"]["claimant"]["confidential"])
        self.assertFalse(full["side"]["claimant"]["confidential"][0].startswith("Maxfiy"))

    def test_private_case_and_share_code(self):
        c, _ = LAB.save("owner_aaaa1111", RAW, "supply", visibility="private")
        self.assertEqual((c["status"], c["visibility"]), ("private", "private"))
        code = c["shareCode"]
        self.assertTrue(code)
        with self.assertRaises(LAB.LabError):
            LAB.get("owner_bbbb2222", c["id"])                                     # kodsiz — yo'q
        with self.assertRaises(LAB.LabError):
            LAB.get("owner_bbbb2222", c["id"], code="deadbeef")
        g = LAB.get("owner_bbbb2222", c["id"], code=code)
        self.assertIsNone(g["shareCode"])                                          # kod faqat muallifga ko'rinadi
        self.assertEqual(LAB.listing("owner_bbbb2222", "supply"), [])               # ro'yxatda chiqmaydi
        o = LAB.set_visibility("owner_aaaa1111", c["id"], "public")
        self.assertEqual(o["status"], "review")                                    # ochildi — mentor tekshiradi
        with self.assertRaises(LAB.LabError):
            LAB.set_visibility("owner_bbbb2222", c["id"], "private")

    def test_solutions_visibility(self):
        c, _ = LAB.save("owner_aaaa1111", RAW, "supply")
        LAB.review(c["id"], "approve")
        txt = "Men da'vogar tomonida yuk xati va pretenziyaga tayandim, javobgarning fors-major vajini rad etdim. " * 2
        pub = LAB.add_solution("owner_bbbb2222", c["id"], {"approach": txt, "side": "claimant", "visibility": "public", "name": "Aziza"})
        prv = LAB.add_solution("owner_cccc3333", c["id"], {"approach": txt + " +998901112233", "side": "respondent"})
        self.assertEqual(prv["visibility"], "private")                             # standart — yopiq
        self.assertEqual(prv["redacted"], 1)
        self.assertNotIn("1112233", prv["approach"])
        seen = {x["id"] for x in LAB.solutions("owner_dddd4444", c["id"])}
        self.assertEqual(seen, {pub["id"]})                                         # begona faqat ochiqni ko'radi
        self.assertEqual({x["id"] for x in LAB.solutions("owner_cccc3333", c["id"])}, {pub["id"], prv["id"]})
        self.assertEqual(LAB.get("owner_dddd4444", c["id"])["solutions"], 1)
        e = LAB.edit_solution("owner_cccc3333", prv["id"], {"visibility": "public"})
        self.assertEqual(e["visibility"], "public")
        with self.assertRaises(LAB.LabError):
            LAB.edit_solution("owner_dddd4444", prv["id"], {"visibility": "private"})   # begona tahrirlay olmaydi
        self.assertIsNone(LAB.edit_solution("owner_cccc3333", prv["id"], {"delete": True}))
        self.assertEqual(LAB.edit_solution(None, pub["id"], {"visibility": "hidden"}, admin=True)["visibility"], "hidden")
        self.assertEqual(LAB.solutions("owner_dddd4444", c["id"]), [])

    def test_solution_rules(self):
        c, _ = LAB.save("owner_aaaa1111", RAW, "supply")
        with self.assertRaises(LAB.LabError):                                       # tasdiqlanmagan case — begona yecha olmaydi
            LAB.add_solution("owner_bbbb2222", c["id"], {"approach": "x" * 80})
        LAB.review(c["id"], "approve")
        with self.assertRaises(LAB.LabError):
            LAB.add_solution("owner_bbbb2222", c["id"], {"approach": "qisqa"})
        with self.assertRaises(LAB.LabError):
            LAB.add_solution("owner_bbbb2222", c["id"], {"approach": "sik " + "x" * 80}, profane_fn=lambda t: "sik" in t)
        v = LAB.add_solution("owner_bbbb2222", c["id"], {"approach": "x" * 80, "side": "claimant", "verdictId": "ab" * 8},
                             verdict_fn=lambda vid, side: {"verified": True, "winner": "claimant", "won": True, "side": side})
        self.assertTrue(v["verdict"]["verified"] and v["verdict"]["won"])


    def test_pii_formats(self):
        t, n = LAB.redact("aa1234567, АА1234567, AB-1234567, 93.123.45.67, 8 (371) 123-45-67, @sardor_n, +998 90 111 22 33")
        for x in ("1234567", "93.123", "123-45-67", "@sardor_n", "111 22 33"):
            self.assertNotIn(x, t)

    def test_malformed_case_no_crash(self):
        for bad in ({"side": [1]}, {"side": {"claimant": "x"}}, {"balance": [1], "points": [1]}, {"facts": {"a": 1}},
                    {"legal": 5}, {"legal": [{"normId": ["x"]}]}, {"questions": "x"}):
            c, issues = LAB.normalize_case(dict(RAW, **bad), "supply", ALLOWED)
            self.assertIsInstance(issues, list)

    def test_manual_save_redacts(self):
        c, issues = LAB.save("owner_aaaa1111", dict(RAW, summary="Direktor tel: +998 90 123 45 67"), "supply")
        self.assertNotIn("123 45 67", c["summary"])
        self.assertTrue(any("shaxsiy" in i for i in issues))

    def test_review_cannot_publish_private_and_code_rotates(self):
        c, _ = LAB.save("owner_aaaa1111", RAW, "supply", visibility="private")
        with self.assertRaises(LAB.LabError):
            LAB.review(c["id"], "approve")                                   # yopiq caseni mentor ocha olmaydi
        old = c["shareCode"]
        self.assertGreaterEqual(len(old), 12)
        LAB.set_visibility("owner_aaaa1111", c["id"], "public")
        c2 = LAB.set_visibility("owner_aaaa1111", c["id"], "private")
        self.assertNotEqual(c2["shareCode"], old)                            # eski havola ishlamaydi
        with self.assertRaises(LAB.LabError):
            LAB.get("owner_bbbb2222", c["id"], code=old)
        with self.assertRaises(LAB.LabError):
            LAB.get("owner_bbbb2222", c["id"], code="ко́д")                   # ASCII bo'lmagan kod — 500 emas

    def test_hidden_solution_stays_hidden(self):
        c, _ = LAB.save("owner_aaaa1111", RAW, "supply")
        LAB.review(c["id"], "approve")
        sol = LAB.add_solution("owner_bbbb2222", c["id"], {"approach": "x" * 80, "visibility": "public"})
        LAB.edit_solution(None, sol["id"], {"visibility": "hidden"}, admin=True)
        with self.assertRaises(LAB.LabError):
            LAB.edit_solution("owner_bbbb2222", sol["id"], {"visibility": "public"})
        self.assertEqual(LAB.edit_solution("owner_bbbb2222", sol["id"], {"approach": "y" * 80})["visibility"], "hidden")
        self.assertIsNone(LAB.edit_solution("owner_bbbb2222", sol["id"], {"delete": True}))

if __name__ == "__main__":
    unittest.main()
