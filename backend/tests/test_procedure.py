"""Jonli protsedura testlari: aniqlashtirish, raqibga savol, iltimosnomalar, e'tiroz, kelishuv, erta iltimosnoma,
raqibning moslashuvi va xato oqibati. Reranker'siz (leksik zaxira) ishlaydi.
Serverda: cd ~/lexsim/backend && ../venv/bin/python -m unittest -v tests.test_procedure
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("LEXSIM_STATE_DB", tempfile.mktemp(suffix=".db"))
os.environ["LEXSIM_DSN"] = ""
os.environ["LEXSIM_RERANK_KEY"] = ""
import lexsim_server as L  # noqa: E402

L.NORMS = L.Norms()
L.SEM_KEY = ""
L.SETTINGS.update(llm=False, sem=False, rag=False)
J = L.PROC.J

OPEN = ["Hurmatli sud, ishonchnomani taqdim etaman.", "Hurmatli sud, rad bildirmaymiz.",
        "Hurmatli sud, huquqlarimiz tushunarli.", "Hurmatli sud, iltimosnomamiz yo'q."]
CLAIM = ("Hurmatli sud, 32-P-sonli ijara shartnomasi bo'yicha javobgar ijara haqini to'lamagan. FK 544-moddaga asosan "
         "25 620 433,19 so'm asosiy qarz va 8.5-band bo'yicha penya undirishni so'raymiz.")


class Court:
    def __init__(self, scid, level="beginner"):
        self.s = L.new_session(scid, "tutorial", 7, "owner-token", level)
        e = L.Engine(self.s)
        self.s["startedAt"] = L.now_iso()
        e.status("in-progress")
        L.Engine(self.s).opening()

    def say(self, text):
        e = L.Engine(self.s)
        u = e.user(text)
        u["inputMode"], u["stage"] = "text", self.s["stage"]
        e.process(text, u["id"])
        L.set_feedback(self.s, u["id"])
        return [ev["payload"]["turn"]["text"] for ev in e.events if ev["type"] == "dialogue.npcTurn"]

    def run(self, lines):
        for t in lines:
            self.say(t)
        return self


class Procedure(unittest.TestCase):
    def test_reask_weak_claim_then_cap(self):
        c = Court("sud-ijara-davogar").run(OPEN)
        self.assertEqual(c.s["stage"], "tushuntirish")
        out = c.say("Hurmatli sud, javobgar qarzdor.")
        self.assertIn(L.PROC.CFG["reask_text"]["tushuntirish"]["davogar-vakili"][0], out)
        self.assertEqual(c.s["stage"], "tushuntirish")                 # bosqich o'zgarmadi
        c.say(CLAIM)
        self.assertEqual(c.s["stage"], "dalillar")
        self.assertLessEqual(c.s["scores"]["claim"], 3)                # qayta so'ralgan — to'liq ball emas

    def test_reask_limit_then_consequence(self):
        c = Court("sud-ijara-davogar", "advanced").run(OPEN)
        c.say("Hurmatli sud, javobgar qarzdor.")                       # 1-imkon: aniqlashtirish
        out = c.say("Hurmatli sud, qarzni undiring.")                  # imkon tugadi
        self.assertIn(J["R_CONTINUE"], out)
        self.assertEqual(c.s["stage"], "dalillar")

    def test_question_to_opponent(self):
        c = Court("sud-ijara-davogar").run(OPEN)
        out = c.say("Hurmatli sud, javobgar vakilidan so'ramoqchiman: obyektdan qancha muddat foydalandingiz?")
        self.assertTrue(any("uch oy" in x for x in out), out)
        self.assertEqual(c.s["stage"], "tushuntirish")
        self.assertIn("F3", c.s["facts"])
        out = c.say("Hurmatli sud, javobgar vakili, sizning sevimli taomingiz nima?")
        self.assertIn(J["Q_IRRELEVANT"], out)

    def test_evidence_motion_any_stage(self):
        c = Court("sud-ijara-davogar").run(OPEN + [CLAIM])
        self.assertEqual(c.s["stage"], "dalillar")
        out = c.say("Hurmatli sud, guvohni chaqirishni so'rab iltimosnoma beraman, u javobgar joydan foydalanganini tasdiqlaydi.")
        self.assertIn(J["M_EVIDENCE_DENY_ENOUGH"], out)
        self.assertEqual(c.s["stage"], "dalillar")
        out = c.say("Hurmatli sud, ishni keyinga qoldirishni so'rayman.")
        self.assertIn(J["M_POSTPONE_DENY"], out)

    def test_objection_ruling(self):
        c = Court("sud-ijara-javobgar").run(OPEN)
        c.say("Hurmatli sud, da'voga e'tirozimiz bor: obyekt dalolatnoma bilan topshirilmagan, FK 578-modda.")
        self.assertEqual(c.s["stage"], "dalillar")
        out = c.say("Hurmatli sud, da'vogar vakilining gapiga e'tiroz bildiraman, chunki u ish materiallariga zid.")
        self.assertIn(J["O_SUSTAIN"], out)
        out = c.say("Hurmatli sud, e'tirozim bor da'vogar vakiliga.")
        self.assertIn(J["O_OVERRULE"], out)

    def test_settlement(self):
        c = Court("sud-ijara-javobgar").run(OPEN)
        out = c.say("Hurmatli sud, asosiy qarzni to'liq to'lashga tayyormiz, kelishuv bitimi tuzishni taklif qilamiz.")
        self.assertIn(L.PROC.CFG["opponent"]["davogar-vakili"]["settlement_main"], out)
        self.assertIn(J["S_NEAR"], out)
        self.assertEqual(c.s["stage"], "tushuntirish")

    def test_early_penalty_motion_is_remembered(self):
        c = Court("sud-ijara-javobgar").run(OPEN)
        out = c.say("Hurmatli sud, obyekt dalolatnoma bilan topshirilmagan. Shuningdek FK 326-moddaga asosan penyani "
                    "kamaytirishni so'rayman, u nomutanosib.")
        self.assertIn(J["M_PENYA_EARLY"], out)
        self.assertEqual(c.s["stage"], "dalillar")
        out = c.say("Hurmatli sud, yozma dalillarga qo'shimcha fikrim yo'q.")
        self.assertTrue(any("boshqa taraf fikrini" in x for x in out), out)   # iltimosnoma endi eshitildi
        self.assertEqual(c.s["stage"], "qoshimcha")
        self.assertGreaterEqual(c.s["km"]["KM3"]["level"], 3)

    def test_opponent_adapts_no_penalty_claimed(self):
        c = Court("sud-ijara-davogar").run(OPEN)
        c.say("Hurmatli sud, 32-P-sonli ijara shartnomasi bo'yicha 25 620 433,19 so'm asosiy qarzni FK 544-moddaga asosan undirishni so'raymiz.")
        c.say("Hurmatli sud, javobgar joydan foydalangan va hisob-fakturalarni imzolagan.")
        self.assertEqual(c.s["stage"], "qoshimcha")                    # penya iltimosnomasi bo'lmadi
        self.assertIn("KM3", c.s["km_na"])
        c.say("Hurmatli sud, qo'shimcha materiallarimiz yo'q.")
        c.say("Hurmatli sud! Tekshirilgan shartnoma va hisob-fakturalar asosida FK 544-moddaga ko'ra qarzni undirishni so'raymiz.")
        L.Engine(c.s).finish()
        self.assertFalse(any("Penya" in i["step"] or "penya" in i["step"] for i in c.s["report"]["idealPath"]))

    def test_opponent_objects_to_unexamined(self):
        c = Court("sud-ijara-davogar").run(OPEN + [CLAIM, "Hurmatli sud, javobgar foydalangan va fakturalarni imzolagan.",
                                                    "Hurmatli sud, penya 8.5-bandda yozma kelishilgan.",
                                                    "Hurmatli sud, qo'shimcha materiallarimiz yo'q."])
        self.assertEqual(c.s["stage"], "muzokara")
        out = c.say("Hurmatli sud! Menda ma'lumot bor, javobgar boshqa ijarachilardan ham qarzdor, qarzni undiring.")
        self.assertIn(L.PROC.CFG["opponent"]["javobgar-vakili"]["object_unexamined"], out)

    def test_advanced_no_powers_not_admitted(self):
        c = Court("sud-ijara-javobgar", "advanced")
        c.say("Hurmatli sud, men javobgar vakiliman.")
        out = c.say("Hurmatli sud, hujjat hozir yo'q.")
        self.assertIn(J["NO_POWERS"], out)
        self.assertEqual(c.s["status"], "report-ready")
        self.assertEqual(c.s["report"]["outcome"]["id"], "poor")

    # --- frontend v14 javobi (2026-11-21): 2–5-ishlar
    def test_objection_while_judge_question_open(self):
        c = Court("sud-ijara-davogar").run(OPEN + [CLAIM])
        self.assertEqual(c.s["stage"], "dalillar")
        out = c.say("Hurmatli sud, javobgar vakilining gapiga eʼtiroz bildiraman, chunki obyekt topshirilmagani haqidagi "
                    "gap hech qanday dalil bilan tasdiqlanmagan.")
        self.assertIn(J["O_SUSTAIN"], out)
        self.assertEqual(c.s["stage"], "dalillar")
        out = c.say("Hurmatli sud, eʼtiroz bildiraman.")
        self.assertIn(J["O_OVERRULE"], out)
        c.say("Hurmatli sud, javobgar joydan foydalangan va hisob-fakturalarni imzolagan, e'tiroz bildiraman.")
        self.assertNotEqual(c.s["stage"], "dalillar")             # mazmunli raddiya — bosqich javobi

    def test_defendant_main_objection_is_answer(self):
        c = Court("sud-ijara-javobgar").run(OPEN)
        c.say("Hurmatli sud, da'voga e'tiroz bildiraman: obyekt dalolatnoma bilan topshirilmagan, FK 578-modda.")
        self.assertEqual(c.s["stage"], "dalillar")

    def test_early_stage_actions_do_not_advance(self):
        for n, text, kind in ((1, "Hurmatli sud, javobgar vakilidan so'ramoqchiman: obyektdan qancha muddat foydalandingiz?", "question"),
                              (2, "Hurmatli sud, guvohni chaqirishni so'rab iltimosnoma beraman.", "motion"),
                              (1, "Hurmatli sud, javobgar vakilining gapiga e'tiroz bildiraman, chunki u noto'g'ri.", "objection")):
            c = Court("sud-ijara-davogar").run(OPEN[:n])
            before = c.s["stage"]
            c.say(text)
            self.assertEqual(c.s["stage"], before, text)
            self.assertEqual(c.s["last_feedback"]["tone"], "info", text)
            self.assertEqual(c.s["last_feedback"]["message"], L.PROC.CFG["stage_notes"][kind])
        c = Court("sud-ijara-davogar").run(OPEN[:3])
        out = c.say("Hurmatli sud, ishni keyinga qoldirishni so'rayman.")
        self.assertIn(J["M_POSTPONE_DENY"], out)
        self.assertEqual(c.s["stage"], "oldingi")

    def test_powers_reask_feedback(self):
        c = Court("sud-ijara-davogar")
        c.say("Hurmatli sud, javobgar qarzdor.")
        self.assertEqual(c.s["last_feedback"]["message"], L.PROC.CFG["powers_note"])

    def test_resume_varies(self):
        c = Court("sud-ijara-davogar").run(OPEN + [CLAIM])
        lines = set()
        for t in ("Hurmatli sud, javobgar vakilidan so'ramoqchiman: obyektdan qancha muddat foydalandingiz?",
                  "Hurmatli sud, ishni keyinga qoldirishni so'rayman.", "Hurmatli sud, kelishuv bitimi tuzishni taklif qilamiz."):
            lines.add(c.say(t)[-1])
        self.assertEqual(len(lines), 3)

    def test_decision_points_never_null(self):                    # BACKEND_TASKS_V14 P1-1
        c = Court("sud-ijara-javobgar").run(OPEN + [
            "Hurmatli sud, da'vogar vakilidan so'ramoqchiman: penya qanday hisoblangan?",
            "Hurmatli sud, kelishuv bitimi tuzishni taklif qilamiz.",
            "Hurmatli sud, guvohni chaqirishni so'rayman.",
            "Hurmatli sud, da'voga e'tirozimiz bor: obyekt dalolatnoma bilan topshirilmagan, FK 578-modda."])
        L.Engine(c.s).finish()
        decs = c.s["report"]["decisions"]
        self.assertTrue(decs)
        for d in decs:
            self.assertIsInstance(d["points"], int, d)

    def test_turn_engine_tags(self):                             # BACKEND_TASKS_V14 §6: npcTurn.engine
        c = Court("sud-ijara-davogar").run(OPEN)
        c.say("Hurmatli sud, javobgar vakilidan so'ramoqchiman: obyektdan qancha muddat foydalandingiz?")
        npc = [t for t in c.s["turns"] if t["speaker"] != "user"]
        self.assertTrue(all(t.get("engine") in ("bank", "llm", "script") for t in npc))
        last_opp = [t for t in npc if t.get("role") == "opponent"][-1]
        self.assertEqual(last_opp["engine"], "bank")
        self.assertEqual(L.snapshot(c.s)["seed"], 7)

    def test_canonical_lines_for_prerender(self):                # P0-2.5: yangi gap avtomatik ro'yxatga tushadi
        lines = L.canonical_lines()
        texts = {t for t, _ in lines}
        for st in J["RESUME"].values():
            for v in st.values():
                for x in (v if isinstance(v, list) else [v]):
                    self.assertIn(x, texts)
        for x in L.PROC.CFG["fillers"]["judge"]:
            self.assertIn(x, texts)
        self.assertGreater(len(lines), 250)                        # sud zali + «Ish yo'li» (lines.json)

    def test_scenario_package_export_validates(self):            # §1 ssenariy paketi + §7 validate_scenario
        import copy
        import scenario_pkg as SP
        pkg = SP.export_ijara(L)
        errors, _ = SP.validate(pkg, known_norms=None)
        self.assertEqual(errors, [])
        bad = copy.deepcopy(pkg)
        bad["stages"][3]["next"] = "yakun"                         # tushuntirish..muzokara bosqichlariga yetib bo'lmaydi
        bad["lines"]["X"] = {"text": "{{ism}} vakili, gapiring.", "voice": "elder_m"}
        errors, _ = SP.validate(bad)
        self.assertTrue(any("yetib bo'lmaydi" in e for e in errors), errors)
        self.assertTrue(any("e'lon qilinmagan" in e for e in errors), errors)

    def test_voice_palette_names_and_rate_wait(self):           # v15 §1.3, §2.1
        self.assertEqual(L.V.resolve_voice("judge_m2"), "elder_m")
        self.assertEqual(L.V.resolve_voice("lawyer_f1"), "female_alt")
        self.assertEqual(L.V.resolve_voice("secretary_f1"), "female")
        self.assertIsNone(L.V.resolve_voice("Bad Name"))
        k = "test:rw"
        for _ in range(3):
            self.assertTrue(L.rate_ok(k, 3))
        self.assertFalse(L.rate_ok(k, 3))
        self.assertGreater(L.rate_wait(k, 3), 50)

    # --- v15 §3, §7: emotsiya, imo-ishora, tanbeh zinapoyasi, munosabatlar
    def _npc_after(self, c, n0):
        return [t for t in c.s["turns"][n0:] if t["speaker"] == "npc"]

    def test_reprimand_ladder_escalates(self):
        c = Court("sud-ijara-davogar").run(OPEN)
        c.s["standing"] = False
        seen = []
        for t in ("Hurmatli sud, javobgar qarzdor, 32-P shartnoma bo'yicha.",
                  "Hurmatli sud, FK 544-moddaga asosan qarzni undirishni so'raymiz.",
                  "Hurmatli sud, 25 620 433,19 so'm qarz bor."):
            n0 = len(c.s["turns"])
            c.say(t)
            j = self._npc_after(c, n0)[0]
            seen.append((j["text"], j["emotion"]))
        self.assertEqual(len({x[0] for x in seen}), 3)                       # 3 xil gap
        self.assertEqual([x[1] for x in seen], ["calm", "impatient", "upset"])   # kuchayib boradi
        pts = [v["points"] for v in c.s["violations"] if v["kind"] == "seated"]
        self.assertEqual(pts, [0, 2, 5])                                       # beginner: 1-marta ballsiz
        L.Engine(c.s).finish()
        seated = [d for d in c.s["report"]["decisions"] if "tik turib" in (d.get("why") or "")]
        self.assertEqual(seated[0]["tone"], "info")
        self.assertEqual(seated[-1]["tone"], "bad")

    def test_rulings_have_reactions_and_clerk(self):
        c = Court("sud-ijara-davogar").run(OPEN + [CLAIM])
        n0 = len(c.s["turns"])
        c.say("Hurmatli sud, guvohni chaqirishni so'rab iltimosnoma beraman, u foydalanishni tasdiqlaydi.")
        npc = self._npc_after(c, n0)
        deny = next(t for t in npc if t["text"] == J["M_EVIDENCE_DENY_ENOUGH"])
        self.assertEqual(deny.get("gesture"), "shake-head")
        self.assertIn({"role": "opponent", "emotion": "reassured"}, deny["reactions"])
        self.assertTrue(any(t.get("role") == "secretary" and t["text"] == L.PROC.CFG["hall"]["clerk_minutes"] for t in npc))
        n0 = len(c.s["turns"])
        c.say("Hurmatli sud, javobgar vakilidan so'ramoqchiman: obyektdan qancha muddat foydalandingiz?")
        opp = [t for t in self._npc_after(c, n0) if t.get("role") == "opponent"][-1]
        self.assertEqual((opp["emotion"], opp.get("gesture")), ("uncertain", "sigh"))   # noqulay faktni tan oldi

    def test_emotions_not_all_neutral(self):
        c = Court("sud-ijara-davogar").run(OPEN + [          # aralash sessiya: zaif javob, iltimosnoma, savol
            "Hurmatli sud, javobgar qarzdor.", CLAIM,
            "Hurmatli sud, guvohni chaqirishni so'rayman.",
            "Hurmatli sud, javobgar vakilidan so'ramoqchiman: obyektdan qancha muddat foydalandingiz?"])
        emos = {t["emotion"] for t in c.s["turns"] if t["speaker"] == "npc"}
        self.assertGreaterEqual(len(emos), 3, emos)
        self.assertTrue(any(t.get("gesture") for t in c.s["turns"] if t["speaker"] == "npc"))

    def test_too_long_monologue(self):
        c = Court("sud-ijara-davogar").run(OPEN)
        out = c.say("Hurmatli sud, " + " ".join(["javobgar ijara haqini to'lamagan"] * 40))
        self.assertIn(L.PROC.CFG["hall"]["too_long"][0], out)

    # --- LexSim_HOLAT B1, B2: frontend signallari (presence, context)
    def test_b1_sit_at_desk_defaults_to_seated(self):
        s = L.new_session("sud-ijara-davogar", "tutorial", 7, "owner-token", "beginner")
        e = L.Engine(s)
        s["startedAt"] = L.now_iso()
        e.status("in-progress")
        L.Handler.a_interactions(None, L.Engine(s), {"action": "sit-at-desk"})
        self.assertIs(s["standing"], False)

    def test_b2_presence_signals(self):
        H = L.PROC.CFG["hall"]
        c = Court("sud-ijara-davogar").run(OPEN[:1])
        first_npc = next(t["id"] for t in c.s["turns"] if t["speaker"] == "npc")
        c.s["presence_now"] = {"heard": first_npc, "standing": True}      # oxirgi gapni eshitmay gapirdi
        out = c.say("Hurmatli sud, rad bildirmaymiz.")
        self.assertFalse(any(v["kind"] == "interrupt" for v in c.s["violations"]))   # v16: faqat log, tanbeh yo'q
        c.s["presence_now"] = {"spoken": 95.0, "standing": True}          # 90 s dan uzun nutq
        out = c.say("Hurmatli sud, huquqlarimiz tushunarli.")
        self.assertTrue(any(x in out for x in H["too_long"]), out)
        L.Handler.a_interactions(None, L.Engine(c.s), {"action": "stand", "context": {"during": {"turnId": "t_9", "role": "opponent"}}})
        self.assertIn(c.s["turns"][-1]["text"], H["sit_ok"])
        self.assertFalse(any(v["kind"] == "seated" for v in c.s["violations"]))

    # --- LexSim_Backend_Vazifalar (v1.4.5): 3, 5, 6-ishlar
    def test_unclear_reask_and_stt_confidence(self):
        L.build_vocab()
        try:
            H = L.PROC.CFG["hall"]["unclear"]
            c = Court("sud-ijara-davogar").run(OPEN)
            st = c.s["stage"]
            for t in ("ha", "Hurmatli sud, koʻtni tozalash kerak koʻtni."):
                n0 = len(c.s["turns"])
                c.say(t)
                j = [x for x in c.s["turns"][n0:] if x["speaker"] == "npc"][0]
                self.assertIn(j["text"], [h.format(role_name="Da'vogar vakili") for h in H], t)
                self.assertEqual((j["emotion"], j.get("gesture")), ("uncertain", "lean-in"))
                self.assertEqual(c.s["stage"], st)
                self.assertEqual(c.s["last_feedback"]["tone"], "info")
            self.assertFalse(c.s["violations"])                                # ball ayirilmadi
            self.assertLess(L.V.confidence("koʻtni tozalash kerak koʻtni", 3.0), 0.5)
            self.assertGreaterEqual(L.V.confidence("Hurmatli sud, ishonchnomani taqdim etaman, vakolatim tasdiqlangan.", 4.0), 0.7)
            # lug'at yoqilgan holda to'g'ri javoblar «tushunarsiz» deb topilmasin
            for role, lines in (("sud-ijara-javobgar", OPEN + [
                    "Hurmatli sud, da'voga e'tirozimiz bor: obyekt topshirish dalolatnomasi bilan topshirilmagan, FK 578-modda.",
                    "Hurmatli sud, FK 326-moddaga asosan penyani kamaytirishni so'rab iltimosnoma beraman: penya nomutanosib, uch oy foydalangan.",
                    "Hurmatli sud, qo'shimcha materiallar yo'q.",
                    "Hurmatli sud! Tekshirilgan shartnoma va hisob-fakturalar asosida FK 326-moddaga ko'ra penyani kamaytirishni so'rayman."]),
                    ("sud-ijara-davogar", ["Hurmatli sud, ishonchnoma bor.", "Hurmatli sud, yo'q.", "Hurmatli sud, tushunarli.",
                                           "Hurmatli sud, yo'q."])):
                c = Court(role).run(lines)
                self.assertNotIn("unclear_n", c.s, role)
        finally:
            L.V._VOCAB["stems"] = set()

    def test_npc_turn_audio_ref(self):
        import tempfile as _tf
        from pathlib import Path as _P
        old = L.V.CACHE
        L.V.CACHE = _P(_tf.mkdtemp())
        try:
            text = L.T["SIT"]
            k = L.V.hashlib.sha256(f"gpu\0elder_m\0True\0{L.V.clean_text(text)}".encode()).hexdigest()
            (L.V.CACHE / (k + ".mp3")).write_bytes(b"ID3\x03\x00\x00\x00\x00\x00\x00")
            a = L.audio_ref(text, "elder_m")
            self.assertTrue(a["url"].startswith("/api/v1/voice/cache/" + k))
            self.assertEqual(a["voice"], "elder_m")
            self.assertIsNone(L.audio_ref("Keshda yo'q gap.", "elder_m"))
        finally:
            L.V.CACHE = old

    # --- v1.4.6: odamdek munosabat (21-noyabr jonli sessiyalaridagi haqiqiy gaplar)
    def _first_judge(self, c, text):
        n0 = len(c.s["turns"])
        c.say(text)
        return [t for t in c.s["turns"][n0:] if t.get("role") == "judge"]

    def test_profanity_ladder_and_removal(self):
        c = Court("sud-ijara-javobgar").run(OPEN)
        L_ = L.PROC.CFG["order_ladder"]
        j = self._first_judge(c, "pashol naxuy")
        self.assertEqual((j[0]["text"], j[0]["emotion"]), (L_[0], "upset"))
        j = self._first_judge(c, "hurmatli sudya kotizga sikaman")
        self.assertEqual(j[0]["text"], L_[1])
        self.assertEqual(c.s["stage"], "tushuntirish")                     # bosqich o'tib ketmadi
        j = self._first_judge(c, "Hurmatli sudya pashol naxuy")
        self.assertEqual(j[0]["text"], L_[2])
        self.assertEqual(c.s["status"], "report-ready")                    # zaldan chiqarildi

    def test_powers_excuse_is_human(self):
        ex = L.PROC.CFG["powers_excuse"]
        c = Court("sud-ijara-davogar", "advanced")
        j = self._first_judge(c, "uyda qolib ketibdi")
        self.assertIn(j[0]["text"], ex["first"])
        self.assertEqual(c.s["stage"], "ishtirokchilar")
        j = self._first_judge(c, "uyda qolib ketibdi")
        self.assertEqual(j[0]["text"], ex["then"])
        self.assertIn(J["NO_POWERS"], [x["text"] for x in j])

    def test_powers_excuse_beats_keyword(self):                    # frontend 13/14: «ishonchnoma uyda qolib ketibdi» ≠ vakolat bor
        ex = L.PROC.CFG["powers_excuse"]
        c = Court("sud-ijara-davogar", "advanced")
        j = self._first_judge(c, "Hurmatli sud, ishonchnoma uyda qolib ketibdi.")
        self.assertIn(j[0]["text"], ex["first"])
        self.assertEqual(c.s["stage"], "ishtirokchilar")
        j = self._first_judge(c, "Hurmatli sud, ishonchnomani olib kelmadim, keyin beraman.")
        self.assertIn(J["NO_POWERS"], [x["text"] for x in j])
        c = Court("sud-ijara-davogar", "advanced")
        self._first_judge(c, "Hurmatli sud, ishonchnomani taqdim etaman, vakolatim tasdiqlangan.")
        self.assertEqual(c.s["stage"], "rad")

    def test_situations_criminal_offtopic_against_client(self):
        sits = {x["id"]: x for x in L.PROC.CFG["situations"]}
        c = Court("sud-ijara-javobgar").run(OPEN)
        st = c.s["stage"]
        j = self._first_judge(c, "Hurmatli sudya mijozimni qamang")
        self.assertIn(j[0]["text"], [t.format(role_name="Javobgar vakili") for t in sits["against_client"]["lines"]])
        j = self._first_judge(c, "Hurmatli sud, uni qamang, jinoiy jazo bering.")
        self.assertEqual(j[0]["text"], sits["criminal"]["lines"][0])
        self.assertEqual(j[0]["emotion"], "confused")
        j = self._first_judge(c, "Hurmatli sud, ishlaringiz qalay?")
        self.assertEqual(j[0]["text"], sits["offtopic"]["lines"][0])
        j = self._first_judge(c, "Уважаемый суд, извините, я не понимаю.")
        self.assertEqual(j[0]["text"], sits["russian"]["lines"][0])
        self.assertEqual(c.s["stage"], st)

    def test_recusal_weak_reason_and_postpone(self):
        rc = L.PROC.CFG["recusal"]
        c = Court("sud-ijara-javobgar").run(OPEN[:1])
        j = self._first_judge(c, "Hurmatli sud, rad bildirish huquqimdan ish mazmunan koʻrib boʻlingach, oxirida foydalanaman.")
        self.assertEqual(j[0]["text"], rc["postpone"])
        self.assertEqual(c.s["stage"], "rad")
        j = self._first_judge(c, "Hurmatli sud, kotibga rad bildiraman, u yosh va tajribasi kam koʻrinyapti.")
        self.assertEqual(j[0]["text"], rc["weak"].format(who="Kotibning"))
        self.assertEqual(c.s["stage"], "huquqlar")

    def test_reask_varies(self):
        c = Court("sud-ijara-davogar").run(OPEN)
        a = c.say("Hurmatli sud, javobgar qarzdor.")
        c.s["reasked"], c.s["stage"] = {}, "tushuntirish"
        b = c.say("Hurmatli sud, qarz bor.")
        R = L.PROC.CFG["reask_text"]["tushuntirish"]["davogar-vakili"]
        self.assertIn(R[0], a)
        self.assertIn(R[1], b)

    def test_nlu_situations_for_case_rooms(self):              # «Ish yo'li»/DXM: «tushunmadim» o'rniga odamdek javob
        exp = {"boshligingni sikkaman , rozimisan": "profanity", "pashol naxuy": "profanity",
               "man yordam bera olmayman": "refusal", "yoʻqotib qoʻydim. topolmayapman.": "lost_document",
               "Уважаемый, извините, я не понимаю": "russian", "ishlaringiz qalay?": "offtopic",
               "Yozma ariza tayyor — Nodira opa imzolagan.": None}
        for utt, sid in exp.items():
            sit = L.nlu_situation(utt)
            self.assertEqual(sit and sit["id"], sid, utt)
        sit = L.nlu_situation("pashol naxuy")
        self.assertTrue(sit["ethics"])
        self.assertIn("client", sit["replies"])
        self.assertEqual(sit["replies"]["client"]["voices"], ["male", "female"])
        q = L.NLU.match({"utterance": "boshligingni sikkaman", "candidates": [{"id": "a", "text": "Nima bo'lganini aytib bering"}]},
                        L.normalize, lambda *_: None, L.exact_refs, lambda r: True, lambda r: r)
        self.assertEqual(q["quality"]["ethics"], "violation")
        c = Court("sud-ijara-javobgar").run(OPEN)                        # sud zalida ham «sikkaman» tanilsin
        j = self._first_judge(c, "Hurmatli sud, boshligingni sikkaman")
        self.assertEqual(j[0]["text"], L.PROC.CFG["order_ladder"][0])

    def test_live_session_1100(self):                           # 21-noyabr 11:00 jonli sessiya, aynan o'sha gaplar
        sits = {x["id"]: x for x in L.PROC.CFG["situations"]}
        c = Court("sud-ijara-javobgar", "intermediate")
        j = self._first_judge(c, "hurmatli sudya, meni mijozim aybdor.")
        self.assertIn(j[0]["text"], [t.format(role_name="Javobgar vakili") for t in sits["against_client"]["early_lines"]])
        self.assertEqual(c.s["stage"], "ishtirokchilar")
        self.assertIn("vakolat", j[-1]["text"].lower())                  # keyin yana ishonchnoma so'raladi
        j = self._first_judge(c, "Hurmatli sudya men aniq bilaman meni mijozim pidaras")
        self.assertEqual(j[0]["text"], L.PROC.CFG["order_ladder"][0])
        j = self._first_judge(c, "Hurmatli sudya skin qoyaman szi")
        self.assertEqual(j[0]["text"], L.PROC.CFG["order_ladder"][1])
        self.assertEqual(c.s["stage"], "ishtirokchilar")

    def test_full_good_path_unchanged(self):
        c = Court("sud-ijara-javobgar").run(OPEN + [
            "Hurmatli sud, da'voga e'tirozimiz bor: obyekt topshirish dalolatnomasi bilan topshirilmagan, FK 578-modda.",
            "Hurmatli sud, FK 326-moddaga asosan penyani kamaytirishni so'rab iltimosnoma beraman: penya nomutanosib, uch oy foydalangan.",
            "Hurmatli sud, qo'shimcha materiallar yo'q.",
            "Hurmatli sud! Tekshirilgan shartnoma va hisob-fakturalar asosida FK 326-moddaga ko'ra penyani kamaytirishni so'rayman."])
        self.assertEqual(c.s["stage"], "yakun")
        L.Engine(c.s).finish()
        self.assertGreaterEqual(c.s["report"]["scoreTotal"], 85)


    def test_ai_judge_fallback_when_no_template(self):
        """v1.5: tizimda aniq javob yo'q (aloqasiz yoki to'liq bo'lmagan gap) — AI sudya javob beradi; AI ishlamasa — shablon."""
        old_llm, old_fn = L.SETTINGS["llm"], L.llm_judge
        try:
            L.SETTINGS["llm"] = True
            L.llm_judge = lambda eng, text, purpose, tpl: "Tushunaman, lekin hozir ish holatlariga to'xtalamiz. Da'vo talabingizni ayting."
            c = Court("sud-ijara-davogar").run(OPEN)
            j = self._first_judge(c, "Hurmatli sud, mening mashinam ko'k rangda va uyim shahar markazida joylashgan")
            self.assertTrue(any("ish holatlariga" in x["text"] for x in j))
            self.assertEqual(c.s["ai_judge_n"], 1)
            L.llm_judge = lambda eng, text, purpose, tpl: None                 # AI javob bermadi — shablon
            c2 = Court("sud-ijara-davogar").run(OPEN)
            j2 = self._first_judge(c2, "Hurmatli sud, mening mashinam ko'k rangda va uyim shahar markazida joylashgan")
            self.assertTrue(j2 and not any("ish holatlariga" in x["text"] for x in j2))
        finally:
            L.SETTINGS["llm"], L.llm_judge = old_llm, old_fn

    def test_ai_judge_check_no_new_facts(self):
        out, why = L.llm_check("Sudya: Javobgar 99 million to'lashi kerak.", "salom", "shablon", set(), "", who="judge")
        self.assertIsNone(out)
        out, why = L.llm_check("Hurmatli sud, tushunarli. Iltimos, da'vo talabingizni ayting.", "salom", "shablon", set(), "", who="judge")
        self.assertEqual(out, "Tushunarli. Iltimos, da'vo talabingizni ayting.")


    def test_repeat_request_replays_last_npc_lines(self):
        c = Court("sud-ijara-davogar").run(OPEN[:2])
        before = [t["text"] for t in c.s["turns"] if t.get("speaker") == "npc"][-1]
        n0 = len(c.s["turns"])
        c.say("Hurmatli sud, eshitmadim, qaytaring")
        new = [t for t in c.s["turns"][n0:] if t.get("speaker") == "npc"]
        self.assertTrue(new and new[-1]["text"] == before)                      # aynan o'sha gap
        self.assertEqual(c.s["stage"], "huquqlar")                              # bosqich o'zgarmadi
        self.assertFalse(L.repeat_intent(L.normalize("Hurmatli sud, javobgar pulni qaytarib bermadi, undirishni so'raymiz")))
        self.assertTrue(L.repeat_intent(L.normalize("nima dedingiz?")))
        self.assertTrue(L.repeat_intent(L.normalize("qaytarib yuboring")))

    def test_llm_context_includes_npc_lines(self):
        c = Court("sud-ijara-davogar").run(OPEN[:1])
        hist = L.Engine(c.s).llm_ctx()["history"]
        self.assertTrue(any(h.startswith("Sudya:") for h in hist))              # avval faqat talaba gaplari bor edi


    def _to_dalillar(self, level="beginner"):
        c = Court("sud-ijara-davogar", level).run(OPEN)
        c.say(CLAIM)
        return c

    def test_tactic_fires_and_avoided(self):
        c = self._to_dalillar()
        self.assertEqual(c.s["stage"], "dalillar")
        opp = [t["text"] for t in c.s["turns"] if t.get("role") == "opponent"]
        self.assertTrue(any("uch oy joydan foydalanganimizni tan olamiz" in x for x in opp))   # R4 aytildi
        self.assertEqual(c.s["tactic_open"]["id"], "R4")
        c.say("Hurmatli sud, javobgar foydalanganini tan oldi, buni bayonnomaga kiritishni so'raymiz. Hisob-fakturalar imzolangan.")
        rec = c.s["tactics_log"][0]
        self.assertEqual((rec["result"], rec["points"]), ("avoided", 2))
        fb, pts = L.TAC.report(c.s)
        self.assertEqual(pts, 2)
        self.assertEqual(fb[0]["kind"], "strength")

    def test_tactic_fell_after_window(self):
        c = self._to_dalillar()
        c.say("Hurmatli sud, ha, qarz yo'q deb hisoblasa ham bo'ladi.")
        self.assertIn("tactic_open", c.s)                                      # 1-gap: tushdi, lekin 2-gapda tuzatish mumkin
        c.say("Hurmatli sud, boshqa gapim yo'q.")
        rec = c.s["tactics_log"][0]
        self.assertEqual(rec["result"], "fell")
        fb, pts = L.TAC.report(c.s)
        self.assertEqual(pts, -2)
        self.assertIn("Namunaviy javob", fb[0]["message"])

    def test_tactic_caps_and_e_mode(self):
        c = self._to_dalillar("beginner")
        self.assertEqual(len(c.s["tactics_log"]), 1)                           # beginner: sessiyada 1 ta
        self.assertFalse(any(t["mode"] == "E" for t in L.TAC.CFG["tactics"] if L.TAC._fits(t, {**c.s, "level": "advanced"})))

    def test_cors_lexsim_origin(self):
        self.assertIn("https://lexsim.e-investment.uz", L.CORS_ORIGINS)


    def test_adversary_exploits_admission_in_closing(self):
        c = Court("sud-ijara-davogar", "intermediate").run(OPEN)
        c.say(CLAIM)
        c.say("Hurmatli sud, to'g'ri, dalolatnoma imzolanmagan, lekin hisob-fakturalar imzolangan.")
        self.assertTrue(c.s["adv"]["admissions"])                               # kuzatuv daftariga tushdi
        for line in ["Hurmatli sud, hisob-fakturalar javobgar tomonidan imzolangan, foydalanish fakti bor.",
                     "Hurmatli sud, penyani kamaytirishga qarshimiz, shartnomaning 8.5-bandi bo'yicha hisoblangan.",
                     "Hurmatli sud, qo'shimcha materiallar yo'q.",
                     "Hurmatli sud, FK 544-moddaga asosan asosiy qarz va penyani undirishni so'raymiz, hisob-fakturalar bilan isbotlangan."]:
            if c.s["stage"] == "yakun":
                break
            c.say(line)
        opp = [t["text"] for t in c.s["turns"] if t.get("role") == "opponent"]
        self.assertTrue(any("ning o'zi «" in x and "imzolanmagan" in x for x in opp))   # o'z so'zi bilan unga qarshi
        self.assertTrue(L.ADV.report(c.s))
        self.assertIn("talaba o'zi aytdi", " ".join(L.ADV.weak_points(c.s)))

    def test_adversary_no_false_admissions(self):
        c = Court("sud-ijara-davogar").run(OPEN)
        c.say("Hurmatli sud, javobgar uch oy foydalangan, bu to'g'ri emas deb aytish noto'g'ri.")
        quotes = [a["quote"] for a in c.s.get("adv", {}).get("admissions", [])]
        self.assertFalse(any("foydalangan" in q and "to'g'ri emas" not in q for q in quotes) and len(quotes) > 1)


if __name__ == "__main__":
    unittest.main()
