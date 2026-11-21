#!/usr/bin/env python3
"""Serverdagi ovoz xizmatlarini sinash: matn -> TTS -> STT. Faqat standart kutubxona.
Ishlatish: python3 tools/server_sinov.py [server_ip]
"""
import json, sys, time, uuid, urllib.request

H = "http://" + (sys.argv[1] if len(sys.argv) > 1 else "192.168.88.110")


def call(port, api, data):
    """Gradio 6: POST /gradio_api/call/<api> -> event_id, keyin GET oqimdan natija."""
    req = urllib.request.Request(f"{H}:{port}/gradio_api/call/{api}",
                                 data=json.dumps({"data": data}).encode(),
                                 headers={"Content-Type": "application/json"})
    eid = json.loads(urllib.request.urlopen(req, timeout=30).read())["event_id"]
    last = None
    with urllib.request.urlopen(f"{H}:{port}/gradio_api/call/{api}/{eid}", timeout=300) as r:
        for line in r:
            line = line.decode()
            if line.startswith("event: error"):
                raise RuntimeError("xizmat xatosi")
            if line.startswith("data:"):
                last = json.loads(line[5:], strict=False)
    return last


def upload(port, path):
    boundary = uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"files\"; filename=\"a.wav\"\r\n"
            f"Content-Type: audio/wav\r\n\r\n").encode() + open(path, "rb").read() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"{H}:{port}/gradio_api/upload", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())[0]


def tts(port, text, extra=()):
    t = time.time()
    out = call(port, "synth", [text, *extra])
    wav = urllib.request.urlopen(out[0]["url"], timeout=60).read()
    return wav, time.time() - t, out[1]


def stt(port, wav_path):
    t = time.time()
    path = upload(port, wav_path)
    out = call(port, "transcribe", [{"path": path, "meta": {"_type": "gradio.FileData"}}])
    return out[0], time.time() - t


if __name__ == "__main__":
    text = "Hurmatli sud, iltimosnomani qanoatlantirishingizni so‘rayman."
    for name, port, extra in [("MMS", 7008, (True,)), ("Chatterbox", 7002, ())]:
        wav, sec, info = tts(port, text, extra)
        open(f"/tmp/tts_{name}.wav", "wb").write(wav)
        print(f"TTS {name:10} {sec:5.1f} s | {info}")
    for name, port in [("NavAI", 7003), ("Kotib", 7009)]:
        txt, sec = stt(port, "/tmp/tts_MMS.wav")
        print(f"STT {name:10} {sec:5.1f} s | {txt}")
