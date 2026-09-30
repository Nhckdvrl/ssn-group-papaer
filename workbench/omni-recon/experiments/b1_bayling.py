"""B1 on a second architecture: BayLing-Duplex (GLM-4-Voice backbone; single AR stream interleaving 10 user-audio
tokens / 5 text(+state) tokens / 10 assistant-audio tokens per 0.8 s block). Same items and conditions as
b1_update_phase.py; offsets in blocks (on1 ~0.8 s, on4 ~3.2 s, on8 ~6.4 s ~ the 1/3/6 s used for MiniCPM-o).
Question / correction / silence are tokenized separately and fed block by block through the released streaming API."""
import argparse
import json
import sys

import numpy as np
import soundfile as sf
import torch

sys.path.insert(0, "/home/xiang/rt_ext/BayLing-Duplex")
from bayling_duplex import BayLingDuplex  # noqa: E402

AUD = "/home/xiang/rt_ext/runs/update_audio"
M = "/home/xiang/rt_ext/models"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="/home/xiang/ssn-group-papaer/workbench/omni-recon/probes/update.json")
    ap.add_argument("--conds", default="none,pre,on1,on4,on8")
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--max-blocks", type=int, default=50)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    m = BayLingDuplex(model_path=f"{M}/BayLing-Duplex", speech_tokenizer_path=f"{M}/glm-4-voice-tokenizer",
                      decoder_path=None, interleave_ratio="10:5:10", device="cuda")
    X = m.x_ratio

    def toks(path):
        y, sr = sf.read(path, dtype="float32")
        t, _ = m.tokenize_audio((torch.from_numpy(y).unsqueeze(0), sr))
        return t + t[-1:] * ((-len(t)) % X)  # pad to whole blocks

    sil, _ = m.tokenize_audio((torch.zeros(1, 16000 * 4), 16000))
    sil_block = sil[:X]
    res = []
    for it in json.load(open(a.items)):
        for s in range(a.seeds):
            q, c = toks(f"{AUD}/{it['id']}_q_en_{s % 2}.wav"), toks(f"{AUD}/{it['id']}_c_en_{s % 2}.wav")
            nq, nc = len(q) // X, len(c) // X
            for cond in a.conds.split(","):
                torch.manual_seed(s)
                st = m.create_stream_state()
                timeline, onset, cstart = [], None, None
                for k in range(a.max_blocks):
                    if k < nq:
                        blk = q[k * X:(k + 1) * X]
                    else:
                        if cstart is None and cond != "none":
                            if cond == "pre" and k == nq:
                                cstart = k
                            elif cond.startswith("on") and onset is not None and k == onset + int(cond[2:]):
                                cstart = k
                        j = k - cstart if cstart is not None else -1
                        blk = c[j * X:(j + 1) * X] if 0 <= j < nc else sil_block
                    txt = ""
                    for ev in m.stream_audio_tokens(blk, state=st, temperature=0.8, top_p=0.8, max_epad_count=3):
                        if ev.kind == "text" and ev.token_id not in m._text_special_token_ids:
                            txt += ev.text or ""
                        if ev.kind == "text" and ev.assistant_started and onset is None:
                            onset = k
                    timeline.append(txt.strip())
                    if st.stop_requested:
                        break
                    if cond.startswith("on") and onset is None and k > nq + 15:
                        break
                    if cstart is not None and k > cstart + nc + 15:
                        break
                    if cond == "none" and onset is not None and k > onset + 25:
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
