import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import review as RV  # noqa: E402


def explain(needs, items):
    return {"needsMentor": needs, "routing": [{"reason": "AI keltirgan iqtibos bayonnomada topilmadi"}] if needs else [],
            "sides": {"claimant": {"items": [{"id": i, "method": "ai", "met": m} for i, m in items]}}}


class Review(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        RV.init(self.tmp.name)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_routing_needs_mentor_and_audit(self):
        self.assertTrue(RV.route_moot("a" * 16, explain(True, [("F2", "yes")])))
        self.assertIsNone(RV.route_moot("a" * 16, explain(True, [("F2", "yes")])))            # bir ish — bir marta
        self.assertIsNone(RV.route_moot("b" * 16, explain(False, [("F2", "yes")]), rnd=lambda: 0.5))
        self.assertTrue(RV.route_moot("c" * 16, explain(False, [("F2", "yes")]), rnd=lambda: 0.01))   # 3 % audit
        q = RV.queue()
        self.assertEqual([x["sample"] for x in q], [False, True])                                    # avval AI yuborgani
        self.assertIn("iqtibos", q[0]["reasons"][0])

    def test_decide_rules_and_stats(self):
        r1 = RV.route_moot("d" * 16, explain(True, [("F1", "yes"), ("F2", "no"), ("R1", "yes")]))
        r2 = RV.route_moot("e" * 16, explain(True, [("F1", "yes"), ("F2", "yes"), ("R1", "no")]))
        with self.assertRaises(RV.ReviewError):
            RV.decide(r1, {"decision": "adjust"})                                                    # tuzatishsiz adjust yo'q
        with self.assertRaises(RV.ReviewError):
            RV.decide(r1, {"decision": "reject"})                                                    # izohsiz rad yo'q
        RV.decide(r1, {"decision": "approve"})
        with self.assertRaises(RV.ReviewError):
            RV.decide(r1, {"decision": "approve"})                                                   # ikki marta emas
        RV.decide(r2, {"decision": "adjust", "items": {"claimant:F2": "no"}, "note": "dalil nomlanmagan"})
        st = RV.stats()
        self.assertEqual(st["goldItems"], 6)
        self.assertAlmostEqual(st["agreement"], 5 / 6, places=3)                                     # 1 band tuzatildi
        self.assertEqual(st["perItem"]["F2"], {"n": 2, "agreement": 0.5})
        self.assertIsNotNone(st["kappa"])
        self.assertEqual(st["queue"].get("adjusted"), 1)


if __name__ == "__main__":
    unittest.main()
