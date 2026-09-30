"""Feasibility probe: do deployed speech-LLMs (continuous Whisper features -> Qwen3 backbone; MiniCPM-o 4.5 and
Realtime-Venus) 'latently transcribe' their audio input, as 2606.22473 found for small discrete-unit interleaved SLMs?

Logit lens at every layer over the AUDIO positions only (final norm + lm_head). For each utterance and layer:
  recall@k = fraction of the transcript's content words whose first sub-token (with/without leading space,
             lower/capitalised) is in the top-k logit-lens tokens of ANY audio position of that layer
  control  = the same with the content words of a different, randomly paired utterance (chance level)
Input: the edge-tts battery clips (known transcripts). usage: latent_transcript_minicpmo.py --model-path ... --out ..."""
import argparse
import json
import random
import re

import librosa
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

AUD = "/home/xiang/rt_ext/runs/battery_audio"
STOP = set("the a an and or but of to in on at for with is are was were be been being do does did can could would should "
           "will just only what which who how when where why this that these those it its i me my you your we our "
           "they them their he she his her not no yes if then than so as by from about into out up down over under "
           "again very more most some any all each both few other such own same too say tell give please answer "
           "right isn't correct nothing else".split())


def content_words(t):
    return [w for w in re.findall(r"[A-Za-z]+", t) if len(w) >= 4 and w.lower() not in STOP]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", required=True)
    ap.add_argument("--items", default="/home/xiang/ssn-group-papaer/workbench/omni-recon/probes/battery.json")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model_path, trust_remote_code=True, local_files_only=True)
    model = AutoModel.from_pretrained(a.model_path, trust_remote_code=True, local_files_only=True,
                                      attn_implementation="sdpa", torch_dtype=torch.bfloat16,
                                      init_vision=False, init_audio=True, init_tts=True).eval().cuda()
    cap = {}
    orig = model.get_omni_embedding

    def hook(data, input_embeddings, **kw):
        e = orig(data, input_embeddings=input_embeddings, **kw)
        cap["emb"], cap["bounds"] = e.clone(), [b.tolist() if hasattr(b, "tolist") else b for b in data["audio_bounds"][0]]
        return e
    model.get_omni_embedding = hook
    llm = model.llm
    norm, head = llm.model.norm, llm.lm_head

    def ids_for(w):
        s = set()
        for v in (w, w.lower(), w.capitalize()):
            for pre in (" ", ""):
                t = tok.encode(pre + v, add_special_tokens=False)
                if t:
                    s.add(t[0])
        return s

    items = [b for b in json.load(open(a.items)) if len(content_words(b["en"])) >= 2][:a.n]
    rng = random.Random(0)
    perm = list(range(len(items)))
    rng.shuffle(perm)
    rows = []
    for i, it in enumerate(items):
        audio, _ = librosa.load(f"{AUD}/{it['id']}_en_0.wav", sr=16000, mono=True)
        with torch.inference_mode():
            model.chat(msgs=[{"role": "user", "content": [audio]}], tokenizer=tok, do_sample=False, max_new_tokens=1,
                       enable_thinking=False, use_tts_template=True, generate_audio=False)
            hs = llm(inputs_embeds=cap["emb"], output_hidden_states=True).hidden_states
            pos = [p for b in cap["bounds"] for p in range(int(b[0]), int(b[1]))]
            top = [head(norm(h[0, pos])).topk(a.k, dim=-1).indices.cpu() for h in hs]
        own = [ids_for(w) for w in content_words(it["en"])]
        ctl_it = items[perm[i]] if perm[i] != i else items[(i + 1) % len(items)]
        ctl = [ids_for(w) for w in content_words(ctl_it["en"])]
        rec, rec_c = [], []
        for t in top:
            present = set(t.flatten().tolist())
            rec.append(float(np.mean([bool(s & present) for s in own])))
            rec_c.append(float(np.mean([bool(s & present) for s in ctl])))
        # which words surface, at the best layer (for inspection)
        L = int(np.argmax(rec))
        surf = [w for w, s in zip(content_words(it["en"]), own) if s & set(top[L].flatten().tolist())]
        rows.append(dict(id=it["id"], text=it["en"], n_audio_pos=len(pos), recall=rec, control=rec_c, best_layer=L,
                         surfaced=surf))
        print(it["id"], "best layer", L, f"recall={rec[L]:.2f} ctl={rec_c[L]:.2f}", surf, flush=True)
    R, C = np.array([r["recall"] for r in rows]), np.array([r["control"] for r in rows])
    print("per-layer mean recall:", " ".join(f"{x:.2f}" for x in R.mean(0)))
    print("per-layer mean control:", " ".join(f"{x:.2f}" for x in C.mean(0)))
    json.dump(dict(rows=rows, mean_recall=R.mean(0).tolist(), mean_control=C.mean(0).tolist()), open(a.out, "w"),
              indent=1)


if __name__ == "__main__":
    main()
