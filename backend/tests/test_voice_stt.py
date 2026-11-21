import io
import math
import os
import sys
import unittest
import wave

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import voice as V  # noqa: E402


def wav(seconds, silence_at=()):
    sr, frames = 16000, bytearray()
    for i in range(int(seconds * sr)):
        t = i / sr
        quiet = any(a <= t < b for a, b in silence_at)
        v = 0 if quiet else int(8000 * math.sin(2 * math.pi * 220 * t))
        frames += int(v).to_bytes(2, "little", signed=True)
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(bytes(frames))
    return b.getvalue()


class SttNumbers(unittest.TestCase):
    CASES = {
        "fuqarolik kodeksining besh yuz qirq to'rtinchi moddasiga asosan": "fuqarolik kodeksining 544-moddasiga asosan",
        "ikki ming yigirma ikki yil birinchi apreldagi shartnoma": "2022 yil 1-apreldagi shartnoma",
        "yigirma besh million olti yuz yigirma ming to'rt yuz o'ttiz uch so'm": "25620433 so'm",
        "bir oz kutib turing, yuz berdi, ming rahmat": "bir oz kutib turing, yuz berdi, ming rahmat",
        "IPK ikki yuz oltmish ikkinchi moddasi": "IPK 262-moddasi",
        "sakkiz beshinchi bandiga": "8 5-bandiga",
        "Hurmatli sud, FK uch yuz yigirma oltinchi moddasi bo'yicha penya kamaytirilsin.":
            "Hurmatli sud, FK 326-moddasi bo'yicha penya kamaytirilsin.",
    }

    def test_number_words(self):
        for a, b in self.CASES.items():
            self.assertEqual(V.uz_numbers(a), b)

    def test_term_fixes(self):
        self.assertEqual(V.fix_terms("bog'gar vakili, fikringiz?"), "da'vogar vakili, fikringiz?")
        self.assertIn("vakolatli organ", V.fix_terms("tekshiruvni vakolatli olgan o'tkazadi"))


class SttChunks(unittest.TestCase):
    def test_long_audio_is_split_at_silence(self):
        w = wav(55, silence_at=[(21.0, 21.6), (44.0, 44.6)])
        parts = V._split_wav(w)
        self.assertEqual(len(parts), 3)
        lens = [(len(p) - 44) / 32000 for p in parts]
        self.assertTrue(all(x <= V.STT_CHUNK_S + 0.01 for x in lens))
        self.assertAlmostEqual(sum(lens), 55, delta=0.1)                 # hech narsa yo'qolmaydi
        self.assertTrue(20.9 <= lens[0] <= 21.7)                        # jim joydan kesildi

    def test_limit_is_60s_not_15(self):
        self.assertGreaterEqual(V.STT_MAX_S, 60)
        self.assertTrue(V._is_pcm16k(wav(40)))


if __name__ == "__main__":
    unittest.main()
