import json
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import npc as NPC  # noqa: E402

B = {"speaker": "client", "caseKind": "labour", "stage": "consult", "goal": "mijozdan faktlarni aniqlash",
     "utterance": "Sizni qachon ishdan bo'shatishdi va buyruqni ko'rdingizmi?",
     "facts": ["14-oktabr kuni buyruq bilan bo'shatilgan", "9-10-oktabr kasal bo'lgan"], "history": []}


def ask_with(text, delay=0):
    calls = []

    def ask(prompt, timeout):
        calls.append(prompt)
        time.sleep(delay)
        return text, "chatgpt", 5, None if text else "xato"
    ask.calls = calls
    return ask


class Npc(unittest.TestCase):
    def setUp(self):
        NPC.CACHE.clear()

    def test_reply_in_role(self):
        a = ask_with("Mijoz: 14-oktabr kuni bo'shatishdi. Buyruqni o'shanda ko'rsatishdi, imzo qo'ydim.")
        r = NPC.reply(dict(B), a)
        self.assertEqual((r["speaker"], r["engine"]), ("client", "llm"))
        self.assertTrue(r["text"].startswith("14-oktabr"))                  # «Mijoz:» prefiksi olib tashlandi
        self.assertIn("mijozdan faktlarni aniqlash", a.calls[0])
        self.assertIn("Modda raqamini umuman aytma", a.calls[0])
        NPC.reply(dict(B), a)
        self.assertEqual(len(a.calls), 1)                                    # kesh

    def test_rejects_invented_numbers_and_articles(self):
        self.assertIsNone(NPC.check("Menga 50 million to'lashdi.", B["utterance"], B["facts"], [])[0])
        self.assertIsNone(NPC.check("Mehnat kodeksining 161-moddasi buzilgan.", B["utterance"], B["facts"], [])[0])
        self.assertIsNotNone(NPC.check("Bilmayman, eslay olmayapman.", B["utterance"], B["facts"], [])[0])
        self.assertIsNotNone(NPC.check("MK 161-moddasi bo'yicha bo'shatilgan.", "x", [], ["MK 161-modda"])[0])

    def test_failure_and_pending(self):
        with self.assertRaises(NPC.NpcError) as e:
            NPC.reply(dict(B, utterance="Boshqa savol bor sizga"), ask_with(None))
        self.assertEqual(e.exception.code, "npc_unavailable")
        old = NPC.WAIT_S
        NPC.WAIT_S = 0.1
        try:
            a = ask_with("Ha, shunday bo'ldi.", delay=0.4)
            with self.assertRaises(NPC.NpcError) as e:
                NPC.reply(dict(B, utterance="Uchinchi savol sizga"), a)
            self.assertEqual(e.exception.code, "npc_pending")
            time.sleep(0.6)
            self.assertEqual(NPC.reply(dict(B, utterance="Uchinchi savol sizga"), a)["text"], "Ha, shunday bo'ldi.")
        finally:
            NPC.WAIT_S = old

    def test_validation_and_redaction(self):
        with self.assertRaises(NPC.NpcError):
            NPC.reply(dict(B, speaker="hacker"), ask_with("x"))
        a = ask_with("Tushundim.")
        NPC.reply(dict(B, utterance="Telefoningiz +998901234567 to'g'rimi?"), a, redact_fn=lambda t: (t.replace("+998901234567", "[telefon]"), 1))
        self.assertNotIn("901234567", a.calls[0])


    def test_memory_and_repeat(self):
        NPC.MEMORY.clear()
        b = dict(B, conversationId="conv-labour-1")
        NPC.remember("ownerA1", b, [{"speaker": "client", "text": "14-oktabr kuni bo'shatishdi, imzo qo'ydirishdi."}])
        a = ask_with("Ha, Bahodir aka guvoh bo'ladi.")
        NPC.reply(dict(b, utterance="Guvoh bormi sizda?"), a, owner="ownerA1")
        self.assertIn("14-oktabr kuni bo'shatishdi", a.calls[0])               # oldingi suhbat AI'ga borgan
        rep = lambda u: "qaytar" in u or "eshitmadim" in u  # noqa: E731
        r = NPC.reply(dict(b, utterance="eshitmadim, qaytaring"), a, owner="ownerA1", repeat_fn=rep)
        self.assertEqual((r["engine"], r["text"]), ("repeat", "Ha, Bahodir aka guvoh bo'ladi."))   # AI'siz
        self.assertEqual(len(a.calls), 1)
        r2 = NPC.reply(dict(B, conversationId="boshqa-suhbat", utterance="eshitmadim, qaytaring"), ask_with("Nima?"),
                       owner="ownerA1", repeat_fn=rep)
        self.assertNotEqual(r2["engine"], "repeat")                             # boshqa suhbat xotirasi aralashmaydi


if __name__ == "__main__":
    unittest.main()
