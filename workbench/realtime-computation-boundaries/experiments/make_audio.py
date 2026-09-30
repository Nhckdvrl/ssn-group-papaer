"""Synthesize spoken versions of probe questions with edge-tts (2 voices per language) -> 16 kHz wav."""
import asyncio, json, os, sys
import edge_tts, librosa, soundfile as sf
Q, OUT = sys.argv[1], sys.argv[2]
V = {"en": ["en-US-AriaNeural", "en-US-GuyNeural"], "zh": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"]}
os.makedirs(OUT, exist_ok=True)
async def main():
    for q in json.load(open(Q)):
        for lang, vs in V.items():
            for i, v in enumerate(vs):
                w = f"{OUT}/{q['id']}_{lang}_{i}.wav"
                if os.path.exists(w): continue
                mp3 = w[:-4] + ".mp3"
                await edge_tts.Communicate(q[lang], v).save(mp3)
                y, _ = librosa.load(mp3, sr=16000, mono=True)
                sf.write(w, y, 16000); os.remove(mp3)
asyncio.run(main()); print("done", len(os.listdir(OUT)))
