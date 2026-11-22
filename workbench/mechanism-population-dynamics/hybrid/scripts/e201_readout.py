#!/usr/bin/env python3
"""E201 readout: E194's R1 on a trained small model under switches in layers 0-2, plus per-token NLL on 50 EWT passages.

Conditions: none | noconv (GDN conv neighbour taps -> 0) | nomem (GDN A_log += 20) | noattn (attention output -> 0)
            | nocanon (Canon conv weights -> 0; tf_canon only) | nocanon_noattn.
Usage: e201_readout.py RUN_DIR ITEMS PASSAGES TOK_DIR OUT_JSON COND
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).parent))
from e201_train import CanonConv, attach_canon  # noqa: E402

EOS, PAD, LAYERS = 100257, 100277, (0, 1, 2)


def main():
    run, items, passages, tokdir, out, cond = sys.argv[1:7]
    run = Path(run)
    model = AutoModelForCausalLM.from_pretrained(run / "model", dtype=torch.bfloat16).cuda().eval()
    meta = json.loads((run / "train_meta.json").read_text())
    if meta["arch"] == "tf_canon":
        canon = torch.nn.ModuleList([CanonConv(512) for _ in model.model.layers])
        canon.load_state_dict(torch.load(run / "canon.pt"))
        canon.cuda()
        if cond in ("nocanon", "nocanon_noattn"):
            with torch.no_grad():
                for li in LAYERS:
                    canon[li].w.zero_()
        attach_canon(model, canon)
    for li in LAYERS:
        layer = model.model.layers[li]
        gdn = getattr(layer, "linear_attn", None)
        with torch.no_grad():
            if cond == "noconv":
                assert gdn is not None
                gdn.conv1d.weight[..., :-1] = 0
            if cond == "nomem":
                assert gdn is not None
                gdn.A_log += 20
        if cond in ("noattn", "nocanon_noattn"):
            attn = getattr(layer, "self_attn", None)
            assert attn is not None, f"layer {li} has no attention"
            attn.register_forward_hook(lambda m, i, o: ((torch.zeros_like(o[0]),) + tuple(o[1:])) if isinstance(o, tuple) else torch.zeros_like(o))
    tok = AutoTokenizer.from_pretrained(tokdir)
    P = json.loads(Path(passages).read_text())
    nll = []
    for p in P["passages"][:50]:
        ids = [EOS] + tok(p["text"], add_special_tokens=False)["input_ids"][:511]
        x = torch.tensor([ids], device="cuda")
        with torch.no_grad():
            lp = model(input_ids=x, use_cache=False).logits[0, :-1].float().log_softmax(-1)
        nll.append(-lp.gather(1, x[0, 1:, None])[:, 0].cpu().numpy())
    feats, pos = [], {}

    def hook(mod, inp, output):
        h = output[0] if isinstance(output, tuple) else output
        b = torch.arange(h.shape[0], device=h.device)[:, None]
        feats.append(h[b, pos["p"]].float())
    for m in [model.model.embed_tokens] + list(model.model.layers):
        m.register_forward_hook(hook)
    S = json.loads(Path(items).read_text())["S"]
    MS = [2, 3, 4, 5, 6]
    qnames = [f"split{m}" for m in MS] + [f"shuf{m}" for m in MS if m >= 3] + [f"last{m}" for m in MS]
    ranks, t0 = [], time.time()
    for it in S:
        ctx = it["ctx"]
        seqs = [ctx + [it["wid"]]] + [ctx + [d] for d in it["distract"]]
        for q in qnames:
            kind, m = q[:-1], q[-1]
            seqs.append(ctx + (it["splits"][m] if kind == "split" else it["shuf"][m] if kind == "shuf" else [it["splits"][m][-1]]))
        ids = [[EOS] + s for s in seqs]
        T = max(map(len, ids))
        x = torch.full((len(ids), T), PAD, dtype=torch.long)
        for i, s in enumerate(ids):
            x[i, :len(s)] = torch.tensor(s)
        pos["p"] = torch.tensor([[len(s) - 1] for s in ids], device="cuda")
        feats.clear()
        with torch.no_grad():
            model.model(input_ids=x.cuda(), use_cache=False)
        H = torch.stack(feats)[:, :, 0]
        cand, q = H[:, :32], H[:, 32:]
        mu = cand.mean(1, keepdim=True)
        sims = torch.einsum("lqd,lcd->lqc", F.normalize(q - mu, dim=-1), F.normalize(cand - mu, dim=-1))
        ranks.append((sims[..., 1:] > sims[..., :1]).sum(-1).short().cpu())
    R = torch.stack(ranks)
    torch.save({"ranks": R, "qnames": qnames, "cond": cond, "arch": meta["arch"]}, out.replace(".json", ".pt"))
    acc = (R == 0).float().mean(0)
    res = {"arch": meta["arch"], "cond": cond, "nll_mean": float(np.concatenate(nll).mean()), "train_final_loss": meta["final_loss"],
           "acc": {n: acc[:, j].tolist() for j, n in enumerate(qnames)}, "sec": round(time.time() - t0, 1)}
    Path(out).write_text(json.dumps(res))
    L2 = 3  # capture index of decoder layer 2's output
    print(json.dumps({"arch": meta["arch"], "cond": cond, "nll": round(res["nll_mean"], 3),
                      "L2_split_m2_6": [round(res["acc"][f"split{m}"][L2], 2) for m in MS],
                      "L2_last_m2_5": [round(res["acc"][f"last{m}"][L2], 2) for m in MS[:4]]}), flush=True)


if __name__ == "__main__":
    main()
