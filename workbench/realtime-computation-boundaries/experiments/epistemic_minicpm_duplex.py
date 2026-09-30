"""Epistemic-boundary probe, text-level duplex lineage (THUNLP "Beyond the Turn-Based Game"):
  duplex   : MiniCPM-duplex, released time-slice protocol - every 2 s the new user text (or "<idle>") is sent,
             the model generates <=15 tokens per slice (as model_server_duplex.py / chat.tsx do)
  ordinary : same weights, the released "ordinary session" (whole message, generate to the end)
  parent   : MiniCPM-2B-sft-bf16 (text parent), plain chat
Text input (no speech) - isolates the interaction contract from perception."""
import argparse
import json
import os

import torch
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer, LlamaTokenizer

from epistemic_eval import judge

M = "/home/xiang/rt_ext/models"


def duplex_backend(ordinary):
    tok = LlamaTokenizer.from_pretrained(f"{M}/MiniCPM-duplex", trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(f"{M}/MiniCPM-duplex", trust_remote_code=True,
                                                 torch_dtype=torch.bfloat16).cuda().eval()

    def gen(q, seed):
        torch.manual_seed(seed)
        model.reset_chat_history()
        out = ""
        slices = [q] if ordinary else [" ".join(q.split()[i:i + 5]) for i in range(0, len(q.split()), 5)] \
            if " " in q else [q[i:i + 8] for i in range(0, len(q), 8)]  # ~2 s of speech per slice
        slices += [] if ordinary else ["<idle>"] * 8
        for sl in slices:
            rc = model.stream_chat(tok, sl, max_length=512, top_p=0.8, temperature=0.8, top_k=0)
            if rc != 0:
                break
            for i in range(512 if ordinary else 15):
                r, _ = model.stream_generate()
                if r is None or r in ["<idle>", " <idle>", "</s>"] or "<idle>" in r:
                    if i < 6 and r == "</s>":
                        model.generate_flag = False
                    break
                out += r
        return out.replace("<idle>", "").strip()
    return gen


def parent_backend():
    tok = AutoTokenizer.from_pretrained(f"{M}/MiniCPM-2B-sft-bf16", trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(f"{M}/MiniCPM-2B-sft-bf16", trust_remote_code=True,
                                                 torch_dtype=torch.bfloat16).cuda().eval()

    def gen(q, seed):
        torch.manual_seed(seed)
        r, _ = model.chat(tok, q, temperature=0.8, top_p=0.8, max_length=512)
        return r
    return gen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["duplex", "ordinary", "parent"], required=True)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--queries", default="probes/epistemic.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    gen = parent_backend() if a.mode == "parent" else duplex_backend(a.mode == "ordinary")
    jc = OpenAI(base_url="http://localhost:8100/v1", api_key="x")
    res = []
    for q in json.load(open(a.queries)):
        for lang in os.environ.get("LANGS", "en,zh").split(","):
            for s in range(a.seeds):
                ans = gen(q[lang], s)
                lab = judge(jc, q["cat"], q[lang], ans)
                res.append(dict(id=q["id"], cat=q["cat"], lang=lang, seed=s, reply=ans[:600], label=lab))
                print(q["cat"], q["id"], lang, s, lab, "|", ans[:90].replace("\n", " "), flush=True)
        json.dump(res, open(a.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
