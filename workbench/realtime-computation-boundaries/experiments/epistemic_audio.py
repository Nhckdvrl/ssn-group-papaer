"""Epistemic-boundary probe with SPOKEN questions (edge-tts, 2 voices/lang) for MiniCPM-o-family models.
Modes: offline (model.chat with the audio clip, turn-based) and duplex (1 s streaming chunks + silence, released
duplex decoding). Same judge as epistemic_eval.py. seed s uses voice s % 2."""
import argparse
import json
import os
import re

import librosa
import numpy as np
import torch
from openai import OpenAI
from transformers import AutoModel, AutoTokenizer, set_seed

from epistemic_eval import judge

AUD = os.environ.get("AUD", "/home/xiang/rt_ext/runs/epi_audio")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", required=True)
    ap.add_argument("--mode", choices=["offline", "duplex"], required=True)
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--system-prompt", default=None, help="override the duplex/offline system prompt")
    ap.add_argument("--delay", type=int, default=0, help="duplex: force listening for this many extra 1 s chunks after the question ends")
    ap.add_argument("--queries", default="probes/epistemic.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model_path, trust_remote_code=True, local_files_only=True)
    model = AutoModel.from_pretrained(a.model_path, trust_remote_code=True, local_files_only=True,
                                      attn_implementation="sdpa", torch_dtype=torch.bfloat16,
                                      init_vision=False, init_audio=True, init_tts=True).eval().cuda()
    d = model.as_duplex(generate_audio=False) if a.mode == "duplex" else None
    jc = OpenAI(base_url="http://localhost:8100/v1", api_key="x")

    def gen(wav, seed):
        set_seed(seed)
        audio, _ = librosa.load(wav, sr=16000, mono=True)
        if a.mode == "offline":
            with torch.inference_mode():
                return str(model.chat(msgs=[{"role": "system", "content": a.system_prompt or "You are a helpful assistant."},
                                            {"role": "user", "content": [audio]}], tokenizer=tok, do_sample=False,
                                      max_new_tokens=256, enable_thinking=False, use_tts_template=True,
                                      generate_audio=False) or "")
        d.prepare(prefix_system_prompt=a.system_prompt or "Streaming Omni Conversation.")
        prev = len(d.total_ids)
        n = int(np.ceil(len(audio) / 16000))
        d.force_listen_count = (n + a.delay) if a.delay else 0
        d._streaming_generate_count = 0
        audio = np.pad(audio.astype(np.float32), (0, (n + 14) * 16000 - len(audio)))
        with torch.inference_mode():
            for k in range(n + 14):
                d.streaming_prefill(audio_waveform=audio[k * 16000:(k + 1) * 16000])
                d.streaming_generate(max_new_speak_tokens_per_chunk=20, decode_mode="sampling", temperature=0.7,
                                     top_k=20, top_p=0.8)
        raw = d.tokenizer.decode(d.total_ids[prev:], skip_special_tokens=False)
        dl = re.findall(r"<delegate>(.*?)</delegate>", raw, re.S)
        spoken = re.sub(r"<\|[a-z_]+\|>|</?unit>", "", re.sub(r"<delegate>.*?</delegate>", "", raw, flags=re.S)).strip()
        return spoken + (f" [DELEGATED: {dl[0]}]" if dl else "")

    res = []
    for q in json.load(open(a.queries)):
        for lang in os.environ.get("LANGS", "en,zh").split(","):
            for s in range(a.seeds):
                ans = gen(f"{AUD}/{q['id']}_{lang}_{s % 2}.wav", s)
                lab = "DELEGATE" if "[DELEGATED:" in ans else judge(jc, q["cat"], q[lang], ans)
                res.append(dict(id=q["id"], cat=q["cat"], lang=lang, seed=s, reply=ans[:600], label=lab))
                print(q["cat"], q["id"], lang, s, lab, "|", ans[:90].replace("\n", " "), flush=True)
        json.dump(res, open(a.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
