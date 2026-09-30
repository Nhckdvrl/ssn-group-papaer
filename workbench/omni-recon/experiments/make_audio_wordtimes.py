"""edge-tts synthesis that also records word boundaries (onset/offset in seconds) -> <id>.wav + <id>.words.json"""
import asyncio, json, os, sys
import edge_tts, librosa, soundfile as sf
Q, OUT = sys.argv[1], sys.argv[2]
VOICE = sys.argv[3] if len(sys.argv) > 3 else "en-US-AriaNeural"
os.makedirs(OUT, exist_ok=True)
async def one(item):
    mp3, words = f"{OUT}/{item['id']}.mp3", []
    with open(mp3, "wb") as f:
        async for ch in edge_tts.Communicate(item["en"], VOICE, boundary="WordBoundary").stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append(dict(w=ch["text"], t0=ch["offset"] / 1e7, t1=(ch["offset"] + ch["duration"]) / 1e7))
    y, _ = librosa.load(mp3, sr=16000, mono=True); os.remove(mp3)
    sf.write(f"{OUT}/{item['id']}.wav", y, 16000)
    json.dump(words, open(f"{OUT}/{item['id']}.words.json", "w"))
async def main():
    for it in json.load(open(Q)):
        await one(it)
asyncio.run(main()); print("done")
