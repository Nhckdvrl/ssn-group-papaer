"""E02 step 2: replay rollouts and measure the LM-head gradient geometry. No parameter updates.

Three training signals on the SAME model checkpoint (RESEARCH_PLAN §3.1):
  ce_onpolicy : c = 1/(G|o_i|)            on the model's own samples (same tokens as rl)
  rl          : c = A_i/(G|o_i|)          GRPO advantage (A_i=(r_i-mean)/(std+1e-6)), unclipped PG at behaviour policy
  rft         : c = r_i/(G|o_i|)          rejection-sampling fine-tuning (positive-only, one-sided weights)
  teacher     : c = 1/|ref|               CE on the MATH reference solution (distribution change, not objective change)
Per token (logit gradient g = c (p - e_a)):  ρ, γ, ‖g‖², p_a, entropy, leverage ℓ_a of the target row,
  replay-vs-vLLM log-prob difference.  ρ/γ do not depend on c≠0 (implementation check), so they are stored once
  per token; conditions differ only in which tokens and how they are aggregated.
Per prompt (group aggregate in logit space): ρ(Σ c g), γ(Σ c g), cancellation ‖Σ c g‖ / Σ‖c g‖.
Head-row gradient consistency (I04): per batch b (= one prompt), G_W^b = Σ_t c_t (p_t - e_{a_t}) h_tᵀ.  Across batches,
  per element SNR = |mean_b G| / sqrt(mean_b G²)  (Adam's m̂/√v̂ in the β→1 limit); summarised per row and by bucket
  (row was a target in that condition or never; Pile frequency bucket).  Never-target rows: cos(mean G_j, μ).

Usage: python e02_geometry.py --model qwen3-8b-base --rollouts /tmp/xiang_lmhead/e02/rollouts_qwen3-8b-base.jsonl
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

import models
from lmhead_geom import head_basis, leverage, stable_ce_terms

ROOT = Path(__file__).resolve().parents[1]
BIG = Path("/tmp/xiang_lmhead/e02")
CONDS = ("ce_onpolicy", "rl", "rft", "teacher")


def boot_ci(x, n=2000, seed=0):
    x = np.asarray(x, dtype=float); x = x[np.isfinite(x)]
    if len(x) == 0:
        return [float("nan")] * 2
    rng = np.random.default_rng(seed)
    b = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(n)]
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


class Acc:
    """Accumulates the head-row gradient statistics for one condition."""
    def __init__(self, V, d, dev):
        self.S1 = torch.zeros(V, d, device=dev)
        self.S2 = torch.zeros(V, d, device=dev)
        self.tgt_count = torch.zeros(V, dtype=torch.long, device=dev)
        self.B = 0
        self.Gb = torch.zeros(V, d, device=dev)
        self.batch_fro = []   # ‖G_W^b‖_F : SGD first-order loss decrease through the head's own parameters ∝ its square

    def add_chunk(self, p, a, h, c):
        # G += Pᵀ diag(c) H - scatter_a (c h)
        self.Gb += (p * c[:, None]).T @ h
        self.Gb.index_add_(0, a, -(c[:, None] * h))
        self.tgt_count.index_add_(0, a, torch.ones_like(a))

    def end_batch(self):
        self.batch_fro.append(float(self.Gb.norm()))
        self.S1 += self.Gb
        self.S2 += self.Gb ** 2
        self.B += 1
        self.Gb.zero_()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3-8b-base")
    ap.add_argument("--rollouts", required=True)
    ap.add_argument("--chunk", type=int, default=512)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no_headgrad", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "results" / "e02"))
    args = ap.parse_args()
    dev = "cuda"
    torch.backends.cuda.matmul.allow_tf32 = False
    t0 = time.time()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(models.path(args.model))
    m = AutoModelForCausalLM.from_pretrained(models.path(args.model), dtype=torch.bfloat16).to(dev).eval()
    W = m.lm_head.weight.detach().float()
    V, d = W.shape
    basis = head_basis(W, device=dev)
    lev = leverage(W, basis).float()
    groups = [json.loads(l) for l in open(args.rollouts)]
    if args.limit:
        groups = groups[: args.limit]
    accs = {c: Acc(V, d, dev) for c in CONDS} if not args.no_headgrad else {}
    mu_sum = torch.zeros(d, dtype=torch.float64, device=dev); mu_n = 0
    tok_rows, grp_rows = [], []

    @torch.no_grad()
    def replay(prompt_ids, comp_ids):
        x = torch.tensor([prompt_ids + comp_ids], device=dev)
        h = m.model(input_ids=x).last_hidden_state[0, len(prompt_ids) - 1: -1].float()
        return h, torch.tensor(comp_ids, device=dev)

    for gi, g in enumerate(groups):
        r = np.array([c["reward"] for c in g["completions"]])
        G = len(r)
        A = (r - r.mean()) / (r.std() + 1e-6)
        ref_ids = tok(g_solution(g), add_special_tokens=False)["input_ids"]
        seqs = [("onpolicy", i, c["token_ids"], A[i]) for i, c in enumerate(g["completions"])] + [("teacher", -1, ref_ids, 0.0)]
        agg = {c: {"Gz": torch.zeros(V, dtype=torch.float64, device=dev), "Gh": torch.zeros(d, dtype=torch.float64, device=dev),
                   "sum_norm": 0.0} for c in CONDS}
        for kind, i, ids, Ai in seqs:
            if len(ids) == 0:
                continue
            h, a = replay(g["prompt_ids"], ids)
            mu_sum += h.double().sum(0); mu_n += len(ids)
            L = len(ids)
            if kind == "onpolicy":
                coefs = {"ce_onpolicy": 1.0 / (G * L), "rl": Ai / (G * L), "rft": r[i] / (G * L)}
            else:
                coefs = {"teacher": 1.0 / L}
            vlp = g["completions"][i]["vllm_logprobs"] if kind == "onpolicy" else None
            for s in range(0, L, args.chunk):
                hs, as_ = h[s:s + args.chunk], a[s:s + args.chunk]
                z = hs @ W.T
                p, logp, lp_a, gh, gnorm2, ent = stable_ce_terms(z, as_, W)
                ar = torch.arange(len(as_), device=dev)
                p_a = lp_a.exp()
                coef = ((gh.double() @ basis.R) / basis.sigma) ** 2
                rho = coef.sum(-1) / gnorm2
                # split g = (1-p_a)(q - e_a), q = competitor distribution: why ρ can fall below the random d/V
                one_m = (1 - p_a.double()).clamp_min(1e-30)
                Pa = (W[as_].double() @ basis.R) / basis.sigma                      # U_rᵀ e_a
                Pq = ((gh.double() + one_m[:, None] * W[as_].double()) @ basis.R) / basis.sigma / one_m[:, None]  # U_rᵀ q
                q2 = ((gnorm2 - one_m ** 2) / one_m ** 2).clamp_min(1e-30)         # ‖q‖²
                rho_q = (Pq ** 2).sum(-1) / q2
                cos_aq = (Pa * Pq).sum(-1) / (Pa.norm(dim=-1) * Pq.norm(dim=-1)).clamp_min(1e-30)
                gam = ((gh.double() ** 2).sum(-1) / gnorm2).sqrt()
                rec = {"group": np.full(len(as_), gi), "seq": np.full(len(as_), i), "teacher": np.full(len(as_), kind == "teacher"),
                       "pos": np.arange(s, s + len(as_)), "rho": rho.float().cpu().numpy(), "gamma": gam.float().cpu().numpy(),
                       "gnorm2": gnorm2.float().cpu().numpy(), "p_a": p_a.cpu().numpy(), "entropy": ent.cpu().numpy(),
                       "lev_a": lev[as_].cpu().numpy(), "adv": np.full(len(as_), Ai), "token": as_.cpu().numpy(),
                       "rho_q": rho_q.float().cpu().numpy(), "cos_aq": cos_aq.float().cpu().numpy()}
                if vlp is not None:
                    v = np.array([np.nan if x is None else x for x in vlp[s:s + len(as_)]], dtype=float)
                    rec["dlp_replay_vllm"] = lp_a.cpu().numpy() - v
                tok_rows.append(rec)
                for cname, cval in coefs.items():
                    if cval == 0.0:
                        continue
                    A_ = agg[cname]
                    A_["Gz"] += (p.double() * cval).sum(0)
                    A_["Gz"].index_add_(0, as_, torch.full((len(as_),), -cval, dtype=torch.float64, device=dev))
                    A_["Gh"] += (gh.double() * cval).sum(0)
                    A_["sum_norm"] += float(abs(cval) * gnorm2.sqrt().sum())
                    if accs:
                        accs[cname].add_chunk(p, as_, hs, torch.full((len(as_),), float(cval), device=dev))
                del z, logp, p
        row = {"group": gi, "subject": g["subject"], "level": g["level"], "mean_reward": float(r.mean()),
               "zero_adv_group": bool(r.std() == 0), "n_parse_fail": int(sum(c["parse_fail"] for c in g["completions"])),
               "n_truncated": int(sum(c["finish"] == "length" for c in g["completions"])),
               "mean_len": float(np.mean([len(c["token_ids"]) for c in g["completions"]])), "ref_len": len(ref_ids)}
        for cname in CONDS:
            A_ = agg[cname]
            gz2 = float((A_["Gz"] ** 2).sum())
            if gz2 <= 0:
                row[f"{cname}_rho_agg"] = row[f"{cname}_gamma_agg"] = row[f"{cname}_cancel"] = float("nan")
                continue
            prj = float((((A_["Gh"] @ basis.R) / basis.sigma) ** 2).sum())
            row[f"{cname}_rho_agg"] = prj / gz2
            row[f"{cname}_gamma_agg"] = float(A_["Gh"].norm()) / gz2 ** 0.5
            row[f"{cname}_cancel"] = gz2 ** 0.5 / A_["sum_norm"]
            row[f"{cname}_aggnorm"] = gz2 ** 0.5
        grp_rows.append(row)
        for c in accs.values():
            if c.Gb.abs().sum() > 0:
                c.end_batch()
        if gi % 8 == 0:
            print(f"group {gi}/{len(groups)} {time.time() - t0:.0f}s", flush=True)

    cat = {k: np.concatenate([r_[k] if k in r_ else np.full(len(r_["rho"]), np.nan) for r_ in tok_rows])
           for k in tok_rows[0].keys() | {"dlp_replay_vllm"}}
    BIG.mkdir(parents=True, exist_ok=True)
    tag = args.model + (f"_limit{args.limit}" if args.limit else "")
    np.savez_compressed(BIG / f"geometry_tokens_{tag}.npz", **cat)
    res = summarize(cat, grp_rows, accs, W, mu_sum / max(mu_n, 1), lev, tok, basis, args, time.time() - t0)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    (out / f"geometry_{tag}.json").write_text(json.dumps(res, indent=1))
    with open(out / f"groups_{tag}.jsonl", "w") as f:
        for row in grp_rows:
            f.write(json.dumps(row) + "\n")
    print(json.dumps(res["headline"], indent=1))


def g_solution(g):
    from build_inputs import math_split
    return " " + math_split(g["subject"])[g["index"]]["solution"]


def summarize(cat, grp_rows, accs, W, mu, lev, tok, basis, args, secs):
    teacher = cat["teacher"].astype(bool)
    onp = ~teacher
    rl_tok = onp & (cat["adv"] != 0)
    res = {"model": args.model, "revision": models.revision(args.model), "rollouts": args.rollouts,
           "V": int(W.shape[0]), "d": int(W.shape[1]), "rank_W": basis.rank, "rank_rel_tol": basis.rel_tol,
           "gram_neg_eigs": basis.neg_eigs, "cond_W": float(basis.sigma_all[0] / basis.sigma_all[-1]),
           "random_direction_rho": basis.rank / W.shape[0], "seconds": secs, "n_groups": len(grp_rows)}

    def per_group(mask, key, weight=None):
        out = []
        for gi in range(len(grp_rows)):
            mm = mask & (cat["group"] == gi)
            if mm.sum() == 0:
                out.append(np.nan); continue
            v = cat[key][mm]
            out.append(np.average(v, weights=None if weight is None else cat[weight][mm]))
        return np.array(out)

    tokstats = {}
    for name, mask in (("onpolicy", onp), ("onpolicy_nonzero_adv", rl_tok), ("teacher", teacher)):
        d = {}
        for key in ("rho", "gamma", "gnorm2", "p_a", "entropy", "lev_a", "rho_q", "cos_aq"):
            pg = per_group(mask, key)
            d[key] = {"mean_of_group_means": float(np.nanmean(pg)), "ci95": boot_ci(pg), "median_tok": float(np.median(cat[key][mask]))}
        # energy-weighted retention Σ‖Pg‖²/Σ‖g‖² (per token energies, equal coefficient within a sequence class)
        pg_e = per_group(mask, "rho", weight="gnorm2")
        d["rho_energy_weighted"] = {"mean_of_group_means": float(np.nanmean(pg_e)), "ci95": boot_ci(pg_e)}
        d["n_tokens"] = int(mask.sum())
        tokstats[name] = d
    res["token_level"] = tokstats
    # paired teacher - onpolicy per group
    diffs = {}
    for key in ("rho", "gnorm2", "p_a", "entropy", "lev_a"):
        dlt = per_group(teacher, key) - per_group(onp, key)
        diffs[key] = {"mean": float(np.nanmean(dlt)), "ci95": boot_ci(dlt)}
    res["paired_teacher_minus_onpolicy"] = diffs
    # stratification of rho by p_a bins (on-policy and teacher)
    bins = [0, 0.1, 0.5, 0.9, 0.99, 1.0001]
    strat = {}
    for name, mask in (("onpolicy", onp), ("teacher", teacher)):
        strat[name] = []
        for lo, hi in zip(bins[:-1], bins[1:]):
            mm = mask & (cat["p_a"] >= lo) & (cat["p_a"] < hi)
            strat[name].append({"p_a": [lo, hi], "n": int(mm.sum()), "rho_mean": float(cat["rho"][mm].mean()) if mm.any() else None,
                                "gnorm2_share": float(cat["gnorm2"][mm].sum() / cat["gnorm2"][mask].sum())})
    res["rho_by_p_a"] = strat
    dl = cat["dlp_replay_vllm"][onp]
    dl = dl[np.isfinite(dl)]
    res["replay_alignment"] = {"n": int(len(dl)), "mean": float(dl.mean()), "mean_abs": float(np.abs(dl).mean()),
                               "p99_abs": float(np.percentile(np.abs(dl), 99))}
    # group level
    gr = {}
    for cname in CONDS:
        for key in ("rho_agg", "gamma_agg", "cancel"):
            v = np.array([row.get(f"{cname}_{key}", np.nan) for row in grp_rows], dtype=float)
            gr[f"{cname}_{key}"] = {"mean": float(np.nanmean(v)), "ci95": boot_ci(v), "n_defined": int(np.isfinite(v).sum())}
    v_rl = np.array([row.get("rl_rho_agg", np.nan) for row in grp_rows]); v_ce = np.array([row.get("ce_onpolicy_rho_agg", np.nan) for row in grp_rows])
    gr["paired_rl_minus_ce_rho_agg"] = {"mean": float(np.nanmean(v_rl - v_ce)), "ci95": boot_ci(v_rl - v_ce)}
    res["group_level"] = gr
    res["groups"] = {"mean_reward": float(np.mean([r["mean_reward"] for r in grp_rows])),
                     "frac_zero_adv": float(np.mean([r["zero_adv_group"] for r in grp_rows])),
                     "frac_all_correct": float(np.mean([r["mean_reward"] == 1 for r in grp_rows])),
                     "parse_fail_rate": float(np.sum([r["n_parse_fail"] for r in grp_rows]) / max(1, 8 * len(grp_rows))),
                     "truncation_rate": float(np.sum([r["n_truncated"] for r in grp_rows]) / max(1, 8 * len(grp_rows)))}
    # head-row gradient consistency
    if accs:
        from e01_weights import row_buckets, token_freq
        freq, _ = token_freq(tok, W.shape[0])
        special = set(tok.all_special_ids) | set(tok.get_added_vocab().values())
        bk = row_buckets(W.shape[0], len(tok), special, freq)
        hg = {}
        mu_f = mu.float()
        for cname, A_ in accs.items():
            B = A_.B
            m1 = A_.S1 / B
            m2 = A_.S2 / B
            snr = (m1.abs() / m2.sqrt().clamp_min(1e-30))
            row_snr = snr.mean(1).cpu().numpy()
            row_cos_mu = (torch.nn.functional.cosine_similarity(m1, mu_f[None, :].expand_as(m1), dim=1)).cpu().numpy()
            row_norm = m1.norm(dim=1).cpu().numpy()
            tc = A_.tgt_count.cpu().numpy()
            d = {"B": B, "random_sign_snr_baseline": float(np.sqrt(2 / np.pi) / np.sqrt(B)),
                 "mean_batch_fro": float(np.mean(A_.batch_fro)), "fro_of_mean": float(m1.norm())}
            for name, mask in [("target_rows", tc > 0), ("never_target_rows", tc == 0)] + [(f"bucket_{b}", bk == b) for b in sorted(set(bk))]:
                if mask.sum() == 0:
                    continue
                d[name] = {"n_rows": int(mask.sum()), "mean_row_snr": float(row_snr[mask].mean()),
                           "mean_row_snr_over_random": float(row_snr[mask].mean() / (np.sqrt(2 / np.pi) / np.sqrt(B))),
                           "median_row_snr": float(np.median(row_snr[mask])),
                           "mean_cos_meangrad_mu": float(np.nanmean(row_cos_mu[mask])),
                           "mean_meangrad_norm": float(row_norm[mask].mean())}
            hg[cname] = d
            np.savez_compressed(BIG / f"headgrad_{cname}_{args.model}.npz", row_snr=row_snr, row_cos_mu=row_cos_mu,
                                row_norm=row_norm, tgt_count=tc)
        res["head_row_gradient"] = hg
    res["headline"] = {
        "rho_tok_onpolicy": tokstats["onpolicy"]["rho"]["mean_of_group_means"],
        "rho_tok_teacher": tokstats["teacher"]["rho"]["mean_of_group_means"],
        "rho_energyw_onpolicy": tokstats["onpolicy"]["rho_energy_weighted"]["mean_of_group_means"],
        "rho_energyw_teacher": tokstats["teacher"]["rho_energy_weighted"]["mean_of_group_means"],
        "random_direction_rho": res["random_direction_rho"],
        "rho_agg": {c: gr[f"{c}_rho_agg"]["mean"] for c in CONDS},
        "cancel": {c: gr[f"{c}_cancel"]["mean"] for c in CONDS},
        "groups": res["groups"], "replay": res["replay_alignment"],
        "head_snr_never_target": {c: res.get("head_row_gradient", {}).get(c, {}).get("never_target_rows", {}).get("mean_row_snr") for c in CONDS},
        "head_snr_target": {c: res.get("head_row_gradient", {}).get(c, {}).get("target_rows", {}).get("mean_row_snr") for c in CONDS},
    }
    return res


if __name__ == "__main__":
    main()
