"""B1 instrument: the same semantic update ("sorry, I meant X") delivered at different phases of the model's own
generation, for MiniCPM-o-family full-duplex models (MiniCPM-o 4.5, Realtime-Venus). 1 s streaming chunks.

conditions:
  none   : question only (natural response length / onset reference)
  pre    : correction audio right after the question audio (before the model has spoken)
  on+K   : correction starts K chunks after the first chunk in which the model emitted speech text (K in 1,3,6)
Per trial we keep the per-chunk decoded text timeline, onset chunk, correction start chunk, and the text generated
after the correction began. Labels (ADAPT / CONTINUE / STOP ...) come later from b1_judge.py.
usage: b1_update_phase.py --model-path ... --out ... [--conds none,pre,on1,on3,on6] [--seeds 2]"""
import argparse
import json
import re

import librosa
import numpy as np
import torch
from transformers import AutoModel, set_seed

AUD = "/home/xiang/rt_ext/runs/update_audio"
TOK_RE = re.compile(r"<\|[a-z_]+\|>|</?unit>")


def clean(s):
    return TOK_RE.sub("", re.sub(r"<delegate>.*?</delegate>", " [DELEGATE] ", s, flags=re.S)).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", required=True)
    ap.add_argument("--items", default="/home/xiang/ssn-group-papaer/workbench/omni-recon/probes/update.json")
    ap.add_argument("--conds", default="none,pre,on1,on3,on6")
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--max-chunks", type=int, default=40)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    model = AutoModel.from_pretrained(a.model_path, trust_remote_code=True, local_files_only=True,
                                      attn_implementation="sdpa", torch_dtype=torch.bfloat16,
                                      init_vision=False, init_audio=True, init_tts=True).eval().cuda()
    d = model.as_duplex(generate_audio=False)

    def load(p):
        y, _ = librosa.load(p, sr=16000, mono=True)
        n = int(np.ceil(len(y) / 16000))
        return np.pad(y.astype(np.float32), (0, n * 16000 - len(y))), n

    res = []
    for it in json.load(open(a.items)):
        for s in range(a.seeds):
            q, nq = load(f"{AUD}/{it['id']}_q_en_{s % 2}.wav")
            c, nc = load(f"{AUD}/{it['id']}_c_en_{s % 2}.wav")
            for cond in a.conds.split(","):
                set_seed(s)
                d.prepare(prefix_system_prompt="Streaming Omni Conversation.")
                d.force_listen_count = 0
                d._streaming_generate_count = 0
                timeline, onset, cstart = [], None, None
                with torch.inference_mode():
                    for k in range(a.max_chunks):
                        if k < nq:
                            chunk = q[k * 16000:(k + 1) * 16000]
                        else:
                            if cstart is None and cond != "none":
                                if cond == "pre" and k == nq:
                                    cstart = k
                                elif cond.startswith("on") and onset is not None and k == onset + int(cond[2:]):
                                    cstart = k
                            j = k - cstart if cstart is not None else -1
                            chunk = c[j * 16000:(j + 1) * 16000] if 0 <= j < nc else np.zeros(16000, np.float32)
                        prev = len(d.total_ids)
                        d.streaming_prefill(audio_waveform=chunk)
                        d.streaming_generate(max_new_speak_tokens_per_chunk=20, decode_mode="sampling",
                                             temperature=0.7, top_k=20, top_p=0.8)
                        txt = clean(d.tokenizer.decode(d.total_ids[prev:], skip_special_tokens=False))
                        timeline.append(txt)
                        if onset is None and k >= nq and txt:
                            onset = k
                        if cond.startswith("on") and onset is None and k > nq + 12:
                            break  # never started speaking
                        if cstart is not None and k > cstart + nc + 14:
                            break
                        if cond == "none" and onset is not None and k > onset + 20:
                            break
                before = " ".join(t for t in timeline[nq:cstart] if t) if cstart else " ".join(t for t in timeline if t)
                after = " ".join(t for t in timeline[cstart:] if t) if cstart is not None else ""
                res.append(dict(id=it["id"], seed=s, cond=cond, nq=nq, nc=nc, onset=onset, cstart=cstart,
                                timeline=timeline, before=before, after=after))
                print(it["id"], s, cond, f"onset={onset} cstart={cstart}", "| before:", before[:70], "| after:",
                      after[:90], flush=True)
        json.dump(res, open(a.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
