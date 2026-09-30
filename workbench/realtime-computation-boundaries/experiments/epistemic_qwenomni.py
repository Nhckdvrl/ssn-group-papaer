"""Epistemic-boundary probe for Qwen2.5-Omni-7B (speech-capable, turn-based / not full-duplex; parent
Qwen2.5-7B-Instruct). Input: spoken question (edge-tts) or text; output text (talker disabled).
Uses the model's required default system prompt."""
import argparse
import json
import os

import librosa
import torch
from openai import OpenAI
from transformers import Qwen2_5OmniForConditionalGeneration, Qwen2_5OmniProcessor

from epistemic_eval import judge

AUD = os.environ.get("AUD", "/home/xiang/rt_ext/runs/epi_audio")
SYS = ("You are Qwen, a virtual human developed by the Qwen Team, Alibaba Group, capable of perceiving auditory and "
       "visual inputs, as well as generating text and speech.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", default="/home/xiang/rt_ext/models/Qwen2.5-Omni-7B")
    ap.add_argument("--input", choices=["audio", "text"], required=True)
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--queries", default="probes/epistemic.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    model = Qwen2_5OmniForConditionalGeneration.from_pretrained(a.model_path, torch_dtype=torch.bfloat16,
                                                                device_map="cuda").eval()
    model.disable_talker()
    proc = Qwen2_5OmniProcessor.from_pretrained(a.model_path)
    jc = OpenAI(base_url="http://localhost:8100/v1", api_key="x")

    def gen(q, lang, s):
        if a.input == "audio":
            wav = f"{AUD}/{q['id']}_{lang}_{s % 2}.wav"
            content = [{"type": "audio", "audio": wav}]
            audios = [librosa.load(wav, sr=16000)[0]]
        else:
            content, audios = [{"type": "text", "text": q[lang]}], None
        conv = [{"role": "system", "content": [{"type": "text", "text": SYS}]}, {"role": "user", "content": content}]
        text = proc.apply_chat_template(conv, add_generation_prompt=True, tokenize=False)
        inp = proc(text=text, audio=audios, return_tensors="pt", padding=True).to(model.device)
        torch.manual_seed(s)
        with torch.inference_mode():
            out = model.generate(**inp, return_audio=False, max_new_tokens=200, do_sample=s > 0, temperature=0.7)
        return proc.batch_decode(out[:, inp["input_ids"].shape[1]:], skip_special_tokens=True)[0]

    res = []
    for q in json.load(open(a.queries)):
        for lang in os.environ.get("LANGS", "en,zh").split(","):
            for s in range(a.seeds):
                ans = gen(q, lang, s)
                lab = judge(jc, q["cat"], q[lang], ans)
                res.append(dict(id=q["id"], cat=q["cat"], lang=lang, seed=s, reply=ans[:600], label=lab))
                print(q["cat"], q["id"], lang, s, lab, "|", ans[:90].replace("\n", " "), flush=True)
        json.dump(res, open(a.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
