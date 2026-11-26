"""E01 part 1: weight anatomy of an adjacent checkpoint pair (no forward passes).

Per tensor: ‖ΔW‖_F, ‖W0‖_F, relative change, bitwise-equal fraction in stored dtype, |Δ| in bf16 ULPs of W0.
Head (lm_head) and input embedding: row energies, token buckets, ΔW spectrum (FP64 Gram), entropy/stable
rank, BF16 rounding null (Altaf 2610.22438 style: independent U(-ulp/2, ulp/2) errors on both checkpoints),
principal angles col(W0) vs col(W1), and two functionally special components of ΔW:
  common row shift  (ΔW ≈ 1 cᵀ: adds c·h to every logit -> softmax-invariant, functionally null)
  W0-proportional    (ΔW ≈ α W0: global rescale, e.g. weight decay / temperature)

Usage: python e01_weights.py <pair_key> [--device cuda] [--out results/e01]
"""
import argparse
import json
import math
import re
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from safetensors import safe_open

import models
from lmhead_geom import effective_rank, head_basis, subspace_cosines

ROOT = Path(__file__).resolve().parents[1]


def bf16_ulp(w32: torch.Tensor) -> torch.Tensor:
    """ULP of each value as stored in bf16 (8 significand bits incl. implicit)."""
    a = w32.abs().clamp_min(1e-38)
    return torch.exp2(torch.floor(torch.log2(a)) - 7)


def module_group(name: str) -> str:
    if name.startswith("lm_head"):
        return "lm_head"
    if "embed_tokens" in name:
        return "embed_tokens"
    if name == "model.norm.weight":
        return "final_norm"
    m = re.search(r"layers\.\d+\.(.*)\.weight$", name)
    if m:
        return re.sub(r"^(self_attn|mlp)\.", "", m.group(1))
    return "other"


def tensor_stats(a, b):
    """a, b: tensors in stored dtype (same shape). Returns dict of scalar stats."""
    eq = (a == b) if a.dtype != torch.bfloat16 else (a.view(torch.int16) == b.view(torch.int16))
    a32, b32 = a.float(), b.float()
    d = b32 - a32
    ulp = bf16_ulp(a32)
    du = (d.abs() / ulp)
    return {
        "numel": a.numel(), "dtype": str(a.dtype),
        "norm_w0": float(a32.double().norm()), "norm_d": float(d.double().norm()),
        "frac_bitwise_equal": float(eq.float().mean()),
        "median_abs_d_ulp": float(du.flatten()[:: max(1, du.numel() // 2_000_000)].median()),
        "frac_le_1ulp": float((du <= 1.0).float().mean()),
    }


def row_buckets(V_tensor, tok_len, special_ids, freq):
    """Bucket ids: padding rows (>= tokenizer length), special tokens, frequency buckets from a fixed corpus."""
    b = np.full(V_tensor, "", dtype=object)
    for j in range(V_tensor):
        if j >= tok_len:
            b[j] = "pad_row"
        elif j in special_ids:
            b[j] = "special"
        else:
            c = freq[j]
            b[j] = "freq0" if c == 0 else ("freq1-9" if c < 10 else ("freq10-999" if c < 1000 else "freq1000+"))
    return b


def matrix_anatomy(W0, W1, buckets, device, label):
    """Deep analysis of a V x d matrix pair (fp32 on device)."""
    V, d = W0.shape
    D = (W1 - W0)
    row_e = (D.double() ** 2).sum(1)
    tot = float(row_e.sum())
    w0n = W0.double().norm(dim=1)
    out = {"label": label, "V": V, "d": d, "norm_d": math.sqrt(tot), "norm_w0": float(W0.double().norm())}
    out["rel_change"] = out["norm_d"] / out["norm_w0"]
    srt = torch.sort(row_e, descending=True).values
    cs = torch.cumsum(srt, 0) / max(tot, 1e-300)
    out["energy_top_rows"] = {f"top{p}%": float(cs[max(0, int(V * p / 100) - 1)]) for p in (0.1, 1, 10, 50)}
    # bucket summaries
    bk = {}
    rel_row = (row_e.sqrt() / w0n.clamp_min(1e-30)).cpu().numpy()
    re_np = row_e.cpu().numpy()
    for name in sorted(set(buckets)):
        m = buckets == name
        bk[name] = {"n_rows": int(m.sum()), "energy_share": float(re_np[m].sum() / max(tot, 1e-300)),
                    "mean_row_energy": float(re_np[m].mean()), "median_rel_row_change": float(np.median(rel_row[m])),
                    "mean_w0_row_norm": float(w0n.cpu().numpy()[m].mean())}
    out["buckets"] = bk
    # special components
    c = D.double().mean(0)
    out["common_shift_energy_frac"] = float(V * (c ** 2).sum() / max(tot, 1e-300))
    alpha = float((D.double() * W0.double()).sum() / (W0.double() ** 2).sum())
    out["w0_proportional_alpha"] = alpha
    out["w0_proportional_energy_frac"] = float(alpha ** 2 * (W0.double() ** 2).sum() / max(tot, 1e-300))
    # spectrum of ΔW (via Gram) and of ΔW with common shift removed
    def spec(M):
        G = M.T.double() @ M.double() if M.shape[0] * M.shape[1] < 2e9 else None
        ev, evec = torch.linalg.eigh(G)
        return ev.flip(0).clamp_min(0).sqrt(), evec.flip(1)
    sv, Rv = spec(D)
    out["d_spectrum"] = {**effective_rank(sv), "top10_sv": sv[:10].tolist(),
                         "energy_top1": float(sv[0] ** 2 / (sv ** 2).sum()),
                         "energy_top10": float((sv[:10] ** 2).sum() / (sv ** 2).sum())}
    sv_c, _ = spec(D - c.float()[None, :])
    out["d_spectrum_shift_removed"] = {**effective_rank(sv_c), "top10_sv": sv_c[:10].tolist()}
    # rounding null: independent uniform half-ULP errors on both checkpoints
    g = torch.Generator(device=device).manual_seed(0)
    ulp = bf16_ulp(W0)
    E = (torch.rand(W0.shape, generator=g, device=device) - 0.5) * ulp - (torch.rand(W0.shape, generator=g, device=device) - 0.5) * ulp
    svE, _ = spec(E)
    out["rounding_null"] = {"sigma1_E": float(svE[0]), "norm_E": float(E.double().norm()),
                            "n_sv_above_sigma1_E": int((sv > svE[0]).sum()),
                            "frac_sv_above": float((sv > svE[0]).float().mean())}
    del E
    # left loadings of top ΔW directions vs buckets (which tokens carry the dominant direction)
    u1 = (D.double() @ Rv[:, 0]) / sv[0]
    out["top_dir_bucket_energy"] = {name: float((u1.cpu().numpy()[buckets == name] ** 2).sum()) for name in sorted(set(buckets))}
    # principal angles between column spaces
    b0, b1 = head_basis(W0, device=device), head_basis(W1, device=device)
    cs_ = subspace_cosines(W0, W1, b0, b1)
    out["colspace"] = {"rank0": b0.rank, "rank1": b1.rank, "min_cos": float(cs_.min()), "mean_cos": float(cs_.mean()),
                       "n_cos_below_0.99": int((cs_ < 0.99).sum()), "n_cos_below_0.9": int((cs_ < 0.9).sum()),
                       "sigma_ratio_top": float(b1.sigma[0] / b0.sigma[0]),
                       "sigma_ratio_median": float(b1.sigma_all.median() / b0.sigma_all.median()),
                       "cond0": float(b0.sigma_all[0] / b0.sigma_all[-1]), "cond1": float(b1.sigma_all[0] / b1.sigma_all[-1])}
    arrays = {"row_energy": re_np.astype(np.float32), "w0_row_norm": w0n.cpu().numpy().astype(np.float32),
              "d_sv": sv.cpu().numpy(), "d_top_right": Rv[:, :8].cpu().numpy().astype(np.float32),
              "d_top_left": u1.cpu().numpy().astype(np.float32), "colspace_cos": cs_.cpu().numpy(),
              "common_shift": c.cpu().numpy().astype(np.float32)}
    return out, arrays


def token_freq(tok, V_tensor):
    """Token counts over the fixed Pile-10k corpus (general-text proxy) and MATH-train solutions."""
    import os
    os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
    import datasets
    from build_inputs import SUBJECTS, math_split
    pile = datasets.load_dataset("NeelNanda/pile-10k", split="train")
    cnt = np.zeros(V_tensor, dtype=np.int64)
    for i in range(0, len(pile), 500):
        for ids in tok(list(pile[i:i + 500]["text"]), add_special_tokens=False)["input_ids"]:
            np.add.at(cnt, np.asarray(ids), 1)
    mcnt = np.zeros(V_tensor, dtype=np.int64)
    for s in SUBJECTS:
        sol = list(math_split(s)["solution"])
        for ids in tok(sol, add_special_tokens=False)["input_ids"]:
            np.add.at(mcnt, np.asarray(ids), 1)
    return cnt, mcnt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--out", default=str(ROOT / "results" / "e01"))
    ap.add_argument("--same", action="store_true", help="control: compare parent with itself")
    args = ap.parse_args()
    t0 = time.time()
    p0, p1, stage = models.PAIRS[args.pair]
    if args.same:
        p1 = p0
    i0, i1 = models.tensor_index(p0), models.tensor_index(p1)
    assert set(i0) == set(i1), set(i0) ^ set(i1)
    from transformers import AutoTokenizer
    tok0 = AutoTokenizer.from_pretrained(models.path(p0))
    tok1 = AutoTokenizer.from_pretrained(models.path(p1))
    tok_same = tok0.get_vocab() == tok1.get_vocab()
    per_tensor, groups = {}, defaultdict(lambda: defaultdict(float))
    handles = {}

    def get(f, k):
        if f not in handles:
            handles[f] = safe_open(f, "pt")
        return handles[f].get_tensor(k)

    big = {}
    for k in sorted(i0):
        a, b = get(i0[k], k), get(i1[k], k)
        s = tensor_stats(a, b)
        per_tensor[k] = s
        g = module_group(k)
        G = groups[g]
        G["numel"] += s["numel"]; G["sq_w0"] += s["norm_w0"] ** 2; G["sq_d"] += s["norm_d"] ** 2
        G["n_equal"] += s["frac_bitwise_equal"] * s["numel"]; G["n_le1ulp"] += s["frac_le_1ulp"] * s["numel"]
        if g in ("lm_head", "embed_tokens"):
            big[g] = (a.float(), b.float())
    group_summary = {g: {"numel": int(v["numel"]), "rel_change": math.sqrt(v["sq_d"] / v["sq_w0"]),
                         "norm_d": math.sqrt(v["sq_d"]), "frac_bitwise_equal": v["n_equal"] / v["numel"],
                         "frac_le_1ulp": v["n_le1ulp"] / v["numel"]} for g, v in groups.items()}
    tot_d = sum(v["sq_d"] for v in groups.values())
    for g in group_summary:
        group_summary[g]["share_of_total_sq_d"] = groups[g]["sq_d"] / max(tot_d, 1e-300)
    # token buckets
    V_tensor = big["lm_head"][0].shape[0]
    special = set(tok1.all_special_ids) | {i for t, i in tok1.get_added_vocab().items()}
    freq, mfreq = token_freq(tok1, V_tensor)
    buckets = row_buckets(V_tensor, len(tok1), special, freq)
    res = {"pair": args.pair, "parent": p0, "child": p1, "stage": stage, "same_control": args.same,
           "rev_parent": models.revision(p0), "rev_child": models.revision(p1), "tokenizer_identical": tok_same,
           "len_tokenizer": len(tok1), "V_tensor": V_tensor, "n_special": len(special), "groups": group_summary}
    arrays = {"pile_freq": freq, "math_freq": mfreq}
    for g in ("lm_head", "embed_tokens"):
        W0, W1 = (x.to(args.device) for x in big[g])
        r, arr = matrix_anatomy(W0, W1, buckets, args.device, g)
        res[g] = r
        arrays.update({f"{g}.{k}": v for k, v in arr.items()})
        del W0, W1
        torch.cuda.empty_cache() if args.device.startswith("cuda") else None
    # head vs embedding row-change correlation (does the head move where the input embedding moves?)
    he, ee = arrays["lm_head.row_energy"], arrays["embed_tokens.row_energy"]
    res["head_embed_row_energy_spearman"] = float(_spearman(he, ee))
    res["seconds"] = time.time() - t0
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    tag = args.pair + ("__same" if args.same else "")
    (out / f"weights_{tag}.json").write_text(json.dumps(res, indent=1))
    big_out = Path("/tmp/xiang_lmhead/e01"); big_out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(big_out / f"weights_{tag}.npz", **arrays)
    (big_out / f"weights_{tag}_per_tensor.json").write_text(json.dumps(per_tensor))
    print(json.dumps({k: res[k] for k in ("pair", "groups")}, indent=1)[:3000])
    print("seconds", res["seconds"])


def _spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return np.corrcoef(ra, rb)[0, 1]


if __name__ == "__main__":
    main()
