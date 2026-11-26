"""E01 part 2: functional decomposition of the post-training logit change on fixed inputs.

For the same token ids / positions, h0 = parent final (post-norm) hidden state, h1 = child; W0, W1 heads.
  z_ab = W_a h_b  (a: head, b: backbone);  z11 - z00 = ΔW h0 + W0 Δh + ΔW Δh   (exact, no bias / softcap)
Per position (FP32, logits centred over the vocabulary because softmax ignores a common shift):
  KL(p11‖p00) total; KL(p10‖p00) head-only given h0; KL(p01‖p00) backbone-only given W0;
  KL(p11‖p01) head given h1; centred RMS of the three terms; top-1 flips; target log-prob changes;
  ρ(realised change; W0) = fraction of centred z11-z00 energy inside col(W0).
Also: mean hidden direction μ0 and its cosine with the top right singular vectors of ΔW (from e01_weights).

Usage: python e01_function.py <pair_key> [--max_len 512] [--selftest]
"""
import argparse
import gc
import json
import time
from pathlib import Path

import numpy as np
import torch

import models
from build_inputs import load_e01_texts
from lmhead_geom import head_basis

ROOT = Path(__file__).resolve().parents[1]
BIG = Path("/tmp/xiang_lmhead/e01")


@torch.no_grad()
def hidden_states(name, ids_list, device):
    from transformers import AutoModelForCausalLM
    m = AutoModelForCausalLM.from_pretrained(models.path(name), torch_dtype=torch.bfloat16).to(device).eval()
    W = m.lm_head.weight.detach().float().cpu()
    hs, native_err = [], []
    for k, ids in enumerate(ids_list):
        x = torch.tensor([ids], device=device)
        out = m.model(input_ids=x)
        h = out.last_hidden_state[0]                       # post final norm
        if k < 4:                                          # native forward vs manual head (bf16 path)
            ref = m(input_ids=x).logits[0].float()
            man = (h @ m.lm_head.weight.T).float()
            native_err.append(float((ref - man).abs().max()))
        hs.append(h.float().cpu())
    del m; gc.collect(); torch.cuda.empty_cache()
    return hs, W, native_err


def kl(logp_a, logp_b):
    """KL(a‖b) per row."""
    return (logp_a.exp() * (logp_a - logp_b)).sum(-1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--max_len", type=int, default=512)
    ap.add_argument("--selftest", action="store_true", help="child := parent with known head row perturbation")
    ap.add_argument("--out", default=str(ROOT / "results" / "e01"))
    args = ap.parse_args()
    dev = "cuda"
    t0 = time.time()
    p0, p1, stage = models.PAIRS[args.pair]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(models.path(p1))
    texts = load_e01_texts()
    ids_list = [tok(t["text"], add_special_tokens=False)["input_ids"][: args.max_len + 1] for t in texts]
    src = np.array([t["source"] for t in texts])
    inp = [ids[:-1] for ids in ids_list]
    tgt = [torch.tensor(ids[1:]) for ids in ids_list]

    h0, W0, err0 = hidden_states(p0, inp, dev)
    if args.selftest:
        h1, W1, err1 = h0, W0.clone(), err0
        g = torch.Generator().manual_seed(0)
        rows = torch.randint(0, W0.shape[0], (50,), generator=g)
        W1[rows] += 0.01 * torch.randn(50, W0.shape[1], generator=g)
    else:
        h1, W1, err1 = hidden_states(p1, inp, dev)
    W0d, W1d = W0.to(dev), W1.to(dev)
    dW = W1d - W0d
    b0 = head_basis(W0d, device=dev)
    V = W0.shape[0]

    rows = []
    mu_sum = torch.zeros(W0.shape[1], dtype=torch.float64, device=dev)
    tok_push = torch.zeros(V, dtype=torch.float64, device=dev)   # Σ_pos centred (ΔW h0)_j : which tokens the head change moves
    max_ident_err = 0.0
    for k in range(len(texts)):
        a, b, y = h0[k].to(dev), h1[k].to(dev), tgt[k].to(dev)
        mu_sum += a.double().sum(0)
        dh = b - a
        z00, z10, z01, z11 = a @ W0d.T, a @ W1d.T, b @ W0d.T, b @ W1d.T
        t_head, t_bb, t_x = a @ dW.T, dh @ W0d.T, dh @ dW.T
        max_ident_err = max(max_ident_err, float(((z11 - z00) - (t_head + t_bb + t_x)).abs().max()))
        c = lambda z: z - z.mean(-1, keepdim=True)
        lp = {n: torch.log_softmax(z, -1) for n, z in (("00", z00), ("10", z10), ("01", z01), ("11", z11))}
        ar = torch.arange(len(y), device=dev)
        top = {n: l.argmax(-1) for n, l in lp.items()}
        dz = c(z11 - z00)
        proj = ((dz.double() @ W0d.double()) @ b0.R / b0.sigma) ** 2
        rho_real = proj.sum(-1) / (dz.double() ** 2).sum(-1)
        th = c(t_head)
        proj_h = ((th.double() @ W0d.double()) @ b0.R / b0.sigma) ** 2
        rho_head = proj_h.sum(-1) / (th.double() ** 2).sum(-1).clamp_min(1e-300)
        tok_push += th.double().sum(0)
        rec = {
            "kl_total": kl(lp["11"], lp["00"]), "kl_head_h0": kl(lp["10"], lp["00"]),
            "kl_bb_W0": kl(lp["01"], lp["00"]), "kl_head_h1": kl(lp["11"], lp["01"]),
            "rms_total": dz.pow(2).mean(-1).sqrt(), "rms_head": th.pow(2).mean(-1).sqrt(),
            "rms_bb": c(t_bb).pow(2).mean(-1).sqrt(), "rms_cross": c(t_x).pow(2).mean(-1).sqrt(),
            "flip_total": (top["11"] != top["00"]).float(), "flip_head_h0": (top["10"] != top["00"]).float(),
            "flip_bb_W0": (top["01"] != top["00"]).float(),
            "dlp_tgt_total": lp["11"][ar, y] - lp["00"][ar, y], "dlp_tgt_head_h0": lp["10"][ar, y] - lp["00"][ar, y],
            "dlp_tgt_bb_W0": lp["01"][ar, y] - lp["00"][ar, y],
            "ent00": -(lp["00"].exp() * lp["00"]).sum(-1), "ent11": -(lp["11"].exp() * lp["11"]).sum(-1),
            "rho_realised_W0": rho_real.float(), "rho_headterm_W0": rho_head.float(),
            "h0_norm": a.norm(dim=-1), "dh_rel": dh.norm(dim=-1) / a.norm(dim=-1),
        }
        rows.append({kk: v.float().cpu().numpy() for kk, v in rec.items()} | {"doc": np.full(len(y), k)})
    cat = {kk: np.concatenate([r[kk] for r in rows]) for kk in rows[0]}
    doc_src = src[cat["doc"]]

    def summ(mask):
        out = {}
        for kk, v in cat.items():
            if kk == "doc":
                continue
            per_doc = np.array([v[mask & (cat["doc"] == d)].mean() for d in np.unique(cat["doc"][mask])])
            rng = np.random.default_rng(0)
            boots = [per_doc[rng.integers(0, len(per_doc), len(per_doc))].mean() for _ in range(1000)]
            out[kk] = {"mean": float(per_doc.mean()), "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                       "median_tok": float(np.median(v[mask]))}
        return out

    allm = np.ones_like(cat["doc"], dtype=bool)
    res = {"pair": args.pair, "parent": p0, "child": p1, "stage": stage, "selftest": args.selftest,
           "n_docs": len(texts), "n_positions": int(allm.sum()), "max_len": args.max_len,
           "native_vs_manual_logit_maxabs_bf16": {"parent": err0, "child": err1},
           "identity_max_abs_err_fp32": max_ident_err, "colspace_rank_W0": b0.rank,
           "summary_all": summ(allm), "summary_pile": summ(doc_src == "pile10k"), "summary_math": summ(doc_src == "math_train")}
    # mean hidden direction vs ΔW top right singular vectors
    mu = (mu_sum / allm.sum()).float()
    res["mu0_norm"] = float(mu.norm())
    wfile = BIG / f"weights_{args.pair}.npz"
    if wfile.exists() and not args.selftest:
        R = torch.tensor(np.load(wfile)["lm_head.d_top_right"], device=dev)
        res["cos_mu0_dW_top_right"] = (R.T @ mu / mu.norm()).abs().tolist()
    # tokens most moved by the head change (centred, summed over positions)
    tp = tok_push.cpu().numpy() / allm.sum()
    order = np.argsort(tp)
    res["head_push_most_down"] = [(tok.convert_ids_to_tokens(int(j)) if j < len(tok) else f"<pad{j}>", float(tp[j])) for j in order[:25]]
    res["head_push_most_up"] = [(tok.convert_ids_to_tokens(int(j)) if j < len(tok) else f"<pad{j}>", float(tp[j])) for j in order[::-1][:25]]
    res["seconds"] = time.time() - t0
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    tag = args.pair + ("__selftest" if args.selftest else "")
    (out / f"function_{tag}.json").write_text(json.dumps(res, indent=1))
    BIG.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(BIG / f"function_{tag}.npz", tok_push=tp, **cat)
    s = res["summary_all"]
    print(json.dumps({k: s[k]["mean"] for k in s}, indent=1))
    print("identity err", max_ident_err, "native err", err0, err1, "sec", res["seconds"])


if __name__ == "__main__":
    main()
