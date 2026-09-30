"""Latent-transcription LATENCY in full-duplex streaming (MiniCPM-o 4.5 / Realtime-Venus duplex mode, 1 s units).

Every LLM call made by the streaming decoder is intercepted; for each fed position we keep the logit-lens top-k tokens
at layers L0..L1 (default 24..35, where offline recall peaks). Positions are tagged with the 1 s chunk during which they
were fed (audio embeddings + the model's own listen/speak tokens of that unit). For every content word with known
acoustic offset t1 (edge-tts word boundaries), latency = (first chunk whose positions decode the word) - (chunk that
contains t1). Latency 0 = decodable within the unit where the word ends; 1 = only one unit later, etc.
Also records whether the word is EVER decodable while the user is still speaking vs only after.
usage: latent_latency_duplex.py --model-path ... --out ... [--n 60]"""
import argparse
import json
import re

import librosa
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

from latent_transcript_minicpmo import content_words

AUD = "/home/xiang/rt_ext/runs/wb_audio"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", required=True)
    ap.add_argument("--items", default="/home/xiang/ssn-group-papaer/workbench/omni-recon/probes/battery.json")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--layers", default="24,35")
    ap.add_argument("--tail", type=int, default=6, help="silent chunks after the utterance")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    L0, L1 = map(int, a.layers.split(","))
    tok = AutoTokenizer.from_pretrained(a.model_path, trust_remote_code=True, local_files_only=True)
    model = AutoModel.from_pretrained(a.model_path, trust_remote_code=True, local_files_only=True,
                                      attn_implementation="sdpa", torch_dtype=torch.bfloat16,
                                      init_vision=False, init_audio=True, init_tts=True).eval().cuda()
    d = model.as_duplex(generate_audio=False)
    llm = d.decoder.m
    norm, head = llm.model.norm, llm.lm_head
    rec = {"chunk": -1, "calls": []}
    orig_forward = llm.forward

    def fwd(*args, **kw):
        kw["output_hidden_states"] = True
        out = orig_forward(*args, **kw)
        with torch.no_grad():
            hs = torch.stack([out.hidden_states[l][0] for l in range(L0, L1 + 1)])  # [nl, L, H]
            top = head(norm(hs)).topk(a.k, dim=-1).indices.cpu()  # [nl, L, k]
        rec["calls"].append((rec["chunk"], top))
        return out
    llm.forward = fwd

    def ids_for(w):
        s = set()
        for v in (w, w.lower(), w.capitalize()):
            for pre in (" ", ""):
                t = tok.encode(pre + v, add_special_tokens=False)
                if t:
                    s.add(t[0])
        return s

    items = [b for b in json.load(open(a.items)) if len(content_words(b["en"])) >= 2][:a.n]
    rows = []
    for it in items:
        y, _ = librosa.load(f"{AUD}/{it['id']}.wav", sr=16000, mono=True)
        words = json.load(open(f"{AUD}/{it['id']}.words.json"))
        n = int(np.ceil(len(y) / 16000))
        y = np.pad(y.astype(np.float32), (0, (n + a.tail) * 16000 - len(y)))
        d.prepare(prefix_system_prompt="Streaming Omni Conversation.")
        d.force_listen_count = n + a.tail  # keep the model listening: we only study perception here
        d._streaming_generate_count = 0
        rec["calls"] = []
        with torch.inference_mode():
            for k in range(n + a.tail):
                rec["chunk"] = k
                d.streaming_prefill(audio_waveform=y[k * 16000:(k + 1) * 16000])
                d.streaming_generate(max_new_speak_tokens_per_chunk=20, decode_mode="sampling", temperature=0.7,
                                     top_k=20, top_p=0.8)
        present = {}  # chunk -> set of token ids decodable at any layer / position fed in that chunk
        for ck, top in rec["calls"]:
            present.setdefault(ck, set()).update(top.flatten().tolist())
        cw = set(w.lower() for w in content_words(it["en"]))
        out = []
        for w in words:
            if w["w"].lower().strip(".,?!") not in cw:
                continue
            ids = ids_for(w["w"].strip(".,?!"))
            end_chunk = int(w["t1"])  # chunk k covers [k, k+1) s
            first = next((ck for ck in sorted(present) if ck >= 0 and ids & present[ck]), None)
            out.append(dict(w=w["w"], t0=w["t0"], t1=w["t1"], end_chunk=end_chunk, first_chunk=first,
                            latency=None if first is None else first - end_chunk))
        rows.append(dict(id=it["id"], n_chunks=n, words=out))
        lat = [o["latency"] for o in out if o["latency"] is not None]
        print(it["id"], f"n={n}", "found", len(lat), "/", len(out), "lat", lat, flush=True)
    allw = [o for r in rows for o in r["words"]]
    lat = [o["latency"] for o in allw if o["latency"] is not None]
    print(f"words={len(allw)} decodable={len(lat)/len(allw):.2f} latency hist:",
          {v: lat.count(v) for v in sorted(set(lat))})
    json.dump(rows, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
