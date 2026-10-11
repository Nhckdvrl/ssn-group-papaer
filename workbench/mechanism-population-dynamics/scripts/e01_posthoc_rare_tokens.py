"""POST-HOC (not in the frozen E01 protocol): is the late-70M >uniform loss on random tokens driven by rare tokens?

Splits the held-out R3 sequences' token ids by Pile-10k frequency and reports median/mean first- and
second-half losses at selected checkpoints, clean model only. CPU is enough.
"""
import json
import sys

import numpy as np
import torch

import mp_common as mc
import e01_induction as e

torch.set_grad_enabled(False)
out = {}
model0 = mc.load_tl_model("EleutherAI/pythia-70m-deduped", 143000, device="cpu")
pile, _ = e.pile_eval_set(model0)
counts = torch.bincount(pile.flatten(), minlength=e.REAL_VOCAB)[: e.REAL_VOCAB]
rep = e.held_out_repeated(model0)
tok_count = counts[rep[:, 1:51]]  # [n, 50] counts of r1..r50
for repo, step in [(r, s) for r in sys.argv[1:2] for s in (1000, 8000, 64000, 143000)]:
    m = mc.load_tl_model(repo, step, device="cpu")
    lv = e.loss_at(m, rep, e.R3_POS, bs=100)  # [n, 98]
    first, second = lv[:, :49], lv[:, 49:]
    tgt_count = tok_count[:, 1:50]  # target tokens r2..r50 (same ids in both halves)
    rows = {}
    for name, mask in [("seen>=10", tgt_count >= 10), ("rare<10", tgt_count < 10)]:
        rows[name] = {"frac": float(mask.float().mean()),
                      "first_mean": float(first[mask].mean()), "first_median": float(first[mask].median()),
                      "second_mean": float(second[mask].mean()), "second_median": float(second[mask].median())}
    out[f"{repo}@{step}"] = rows
    print(repo, step, json.dumps({k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in rows.items()}), flush=True)
(mc.RESULTS / "e01" / f"posthoc_rare_tokens_{sys.argv[1].split('/')[-1]}.json").write_text(json.dumps(out, indent=1))
