#!/usr/bin/env python3
"""E168: can a functionally matched expert from seed B replace its counterpart in seed A?

For a receiver A, donor B and layer l:
  maps   : global ridge maps fitted on Dolma calibration windows only (no per-expert outputs used):
           M_in : A's layer-l MoE input -> B's layer-l MoE input    (affine)
           M_out: B's layer-l total MoE output -> A's total MoE output (linear part applied to expert outputs;
                  shared by every expert and by matched/random conditions)
  [revised 2026-10-31 after a POST-HOC smoke test, before any E168 data: the regression maps (R2 ~.6) left
   whole-layer stitching nearly as bad as zeroing the layer. v2: the regression solution only initializes
   the maps, which are then trained on A's LM loss with the whole layer stitched (STITCH_* constants),
   all model parameters frozen; gate: stitched dNLL < 50% of zeroing the layer]
  matching: within-layer Hungarian on E167 fingerprints (UD cal half), frozen before evaluation
  conditions per expert slot e of A (A's routing unchanged; only slot e's computation replaced):
    self       A's own expert (numerical check, dNLL must be 0)
    drop       tokens that chose e use the (k+1)-th expert, gate kept (E167 R4)
    matched    g * M_out E_B,pi(e)( M_in x )
    random     same with a random permutation (5 fixed seeds)
    selfmap    A's own expert through identity maps (code-path floor, must be 0)
  and once per layer: stitch = whole MoE output replaced by M_out MoE_B(M_in x)  (map fidelity),
                      zero   = whole MoE output set to 0.
Recovery R(e) = (dNLL_drop - dNLL_cond) / dNLL_drop on experts with dNLL_drop > MIN_DROP.

Usage: transplant.py OUT_JSON A_CKPT B_CKPT MATCH_NPZ_A MATCH_NPZ_B KIND LAYERS [N_EVAL]
  KIND: drop | route  (fingerprint used for matching; E168 proper uses drop)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from scipy.optimize import linear_sum_assignment

sys.path.insert(0, str(Path(__file__).parent))
from moe_model import Config, MoELM, rope_cache  # noqa: E402
from train_moe import build_windows, get_batch  # noqa: E402
import analyze_functional as af  # noqa: E402

HELD = Path("/tmp/xiang-e167/data/held")
SEQ, N_CAL, BATCH, MIN_DROP, RIDGE = 1024, 256, 16, 1e-4, 1e-3
STITCH_STEPS, STITCH_LR, STITCH_BATCH, STITCH_VAL, STITCH_EVERY = 400, 1e-4, 8, 32, 25  # E168 v2: task-loss stitching, early stop on held-out cal windows
RANDOM_SEEDS = (1, 2, 3, 4, 5)


def load(ck, device):
    st = torch.load(ck, map_location="cpu", weights_only=False)
    m = MoELM(Config(**st["config"]))
    m.load_state_dict({k: v.float() for k, v in st["model"].items()})
    return m.to(device).eval(), int(st["tokens"])


def windows(n_eval):
    files, arrs, fid, off = build_windows(HELD, SEQ)
    rng = np.random.default_rng(168)
    cal_pool = np.where(fid % 3 == 0)[0]
    ev_pool = np.where(fid % 3 != 0)[0]
    cal = rng.choice(cal_pool, N_CAL, replace=False)
    ev = rng.choice(ev_pool, n_eval, replace=False)
    return get_batch(arrs, fid, off, cal, SEQ), get_batch(arrs, fid, off, ev, SEQ)


@torch.no_grad()
def layer_states(model, data, l, device):
    """MoE input (normed), MoE output, and block input residual at layer l."""
    hin, rout, rin = [], [], []
    cos, sin = rope_cache(SEQ, model.cfg.d_model // model.cfg.n_heads, model.cfg.rope_theta, device)
    for i in range(0, len(data), BATCH):
        ids = data[i:i + BATCH, :-1].to(device)
        with torch.autocast("cuda", torch.bfloat16):
            x = model.emb(ids)
            for li, blk in enumerate(model.blocks[: l + 1]):
                if li == l:
                    rin.append(x.float())
                    xa = x + blk.attn(blk.n1(x), cos, sin)
                    hn = blk.n2(xa)
                    hin.append(hn.float())
                    rout.append(blk.moe(hn)[0].float())
                    break
                x, *_ = blk(x, cos, sin)
    return torch.cat(hin), torch.cat(rout), torch.cat(rin)


def ridge(X, Y, lam_rel=RIDGE):
    """Affine least squares Y ~ X W + b with ridge on W. Returns (W, b)."""
    X, Y = X.reshape(-1, X.shape[-1]).double(), Y.reshape(-1, Y.shape[-1]).double()
    mx, my = X.mean(0), Y.mean(0)
    Xc, Yc = X - mx, Y - my
    G = Xc.T @ Xc
    lam = lam_rel * G.trace() / G.shape[0]
    W = torch.linalg.solve(G + lam * torch.eye(G.shape[0], device=G.device, dtype=G.dtype), Xc.T @ Yc)
    return W.float(), (my - mx @ W).float()


def train_stitch(A, Bm, l, cal, rin, Win, bin_, Wout, device):
    """E168 v2: train the shared affine maps on A's LM loss with A's layer-l MoE output replaced by
    M_out MoE_B(M_in x). All model parameters frozen; only Win, bin_, Wout are updated."""
    for p in list(A.parameters()) + list(Bm.parameters()):
        p.requires_grad_(False)
    Win, bin_, Wout = (t.clone().requires_grad_(True) for t in (Win, bin_, Wout))
    opt = torch.optim.Adam([Win, bin_, Wout], lr=STITCH_LR)
    cos, sin = rope_cache(SEQ, A.cfg.d_model // A.cfg.n_heads, A.cfg.rope_theta, device)
    blk, mB = A.blocks[l], Bm.blocks[l].moe
    g = torch.Generator().manual_seed(1680)
    n_tr = len(cal) - STITCH_VAL  # last STITCH_VAL calibration windows are a validation split

    def stitched_loss(idx):
        ids = cal[idx].to(device)
        with torch.autocast("cuda", torch.bfloat16):
            x = rin[idx.to(device)]
            xa = x + blk.attn(blk.n1(x), cos, sin)
            h = blk.n2(xa)
            yb, *_ = mB((h.float() @ Win + bin_))
            x = xa + yb.float() @ Wout
            for b2 in A.blocks[l + 1:]:
                x, *_ = b2(x, cos, sin)
            logits = A.head(A.norm(x))
        return F.cross_entropy(logits.float().transpose(1, 2), ids[:, 1:])

    def val_loss():
        with torch.no_grad():
            return float(np.mean([stitched_loss(torch.arange(i, min(i + STITCH_BATCH, len(cal)))).item()
                                  for i in range(n_tr, len(cal), STITCH_BATCH)]))
    losses, vals = [], [(0, val_loss())]
    best = (vals[0][1], Win.detach().clone(), bin_.detach().clone(), Wout.detach().clone())
    for step in range(1, STITCH_STEPS + 1):
        loss = stitched_loss(torch.randint(0, n_tr, (STITCH_BATCH,), generator=g))
        opt.zero_grad()
        loss.backward()
        opt.step()
        losses.append(loss.item())
        if step % STITCH_EVERY == 0:
            v = val_loss()
            vals.append((step, v))
            if v < best[0]:
                best = (v, Win.detach().clone(), bin_.detach().clone(), Wout.detach().clone())
    return best[1], best[2], best[3], {"train": losses, "val": vals}


def expert_fn(moe, j, x):
    f = moe.w_in.shape[-1] // 2
    h = x @ moe.w_in[j]
    return (F.silu(h[..., :f]) * h[..., f:]) @ moe.w_out[j]


@torch.no_grad()
def eval_nll(model, rin_cache, data, l, device, hook=None, override=None):
    """Mean NLL on eval windows, recomputing blocks >= l from the cached block-l input."""
    moe = model.blocks[l].moe
    h = moe.register_forward_hook(hook) if hook else None
    moe.expert_override = override
    cos, sin = rope_cache(SEQ, model.cfg.d_model // model.cfg.n_heads, model.cfg.rope_theta, device)
    tot, n = 0.0, 0
    for bi, i in enumerate(range(0, len(data), BATCH)):
        ids = data[i:i + BATCH].to(device)
        with torch.autocast("cuda", torch.bfloat16):
            x = rin_cache[i:i + BATCH]
            for blk in model.blocks[l:]:
                x, *_ = blk(x, cos, sin)
            logits = model.head(model.norm(x))
        nll = F.cross_entropy(logits.float().transpose(1, 2), ids[:, 1:], reduction="sum")
        tot += nll.item()
        n += ids[:, 1:].numel()
    if h:
        h.remove()
    moe.expert_override = None
    return tot / n


def slot_hook(moe_a, e, repl):
    """Replace expert slot e's contribution: y += g * (repl(x) - E_A,e(x)) on tokens routing to e."""
    def hook(mod, inp, out):
        with torch.autocast("cuda", enabled=False):
            return _apply(mod, inp, out)

    def _apply(mod, inp, out):
        x = inp[0]
        B, T, d = x.shape
        xf = x.reshape(-1, d).float()
        logits = F.linear(xf, mod.router.weight.float())
        topi = (logits + mod.sel_bias).topk(mod.k, -1).indices
        probs = logits.softmax(-1)
        sel = (topi == e).any(-1)
        if not sel.any():
            return out
        g = probs[sel, e:e + 1]
        xs = xf[sel]
        delta = g * (repl(xs) - expert_fn(moe_a, e, xs))
        y = out[0].reshape(-1, d).float().clone()
        y[sel] += delta
        return (y.to(out[0].dtype).view(B, T, d),) + tuple(out[1:])
    return hook


def main():
    out, a_ck, b_ck, fa, fb, kind, layers = sys.argv[1:8]
    n_eval = int(sys.argv[8]) if len(sys.argv) > 8 else 256
    layers = [int(x) for x in layers.split(",")]
    device = torch.device("cuda")
    A, ta = load(a_ck, device)
    Bm, tb = load(b_ck, device)
    cal, ev = windows(n_eval)
    Ac, Ah, _ = af.load(kind, Path(fa))
    Bc, Bh, _ = af.load(kind, Path(fb))
    res = {"A": a_ck, "B": b_ck, "tokens": [ta, tb], "match_kind": kind, "n_eval_tokens": int(ev[:, 1:].numel()),
           "min_drop": MIN_DROP, "layers": []}
    for l in layers:
        t0 = time.time()
        # matching on cal-half fingerprints (frozen)
        ac, bc = af.centre_units(Ac[l]), af.centre_units(Bc[l])
        n = ac.shape[0]
        C = np.array([af.rowcorr(np.repeat(ac[i:i + 1], n, 0), bc) for i in range(n)])
        ri, ci = linear_sum_assignment(-C)
        pi = dict(zip(ri.tolist(), ci.tolist()))
        # global maps from calibration hidden states only
        hA, rA, _ = layer_states(A, cal, l, device)
        hB, rB, _ = layer_states(Bm, cal, l, device)
        Win, bin_ = ridge(hA, hB)
        Wout, bout = ridge(rB, rA)

        def r2(X, Y, W, b):
            X, Y = X.reshape(-1, X.shape[-1]), Y.reshape(-1, Y.shape[-1])
            return 1 - ((X @ W + b - Y).pow(2).sum() / (Y - Y.mean(0)).pow(2).sum()).item()
        fit_in, fit_out = r2(hA, hB, Win, bin_), r2(rB, rA, Wout, bout)
        del hA, hB, rA, rB
        _, _, rin_cal = layer_states(A, cal, l, device)
        Win, bin_, Wout, st_losses = train_stitch(A, Bm, l, cal, rin_cal, Win, bin_, Wout, device)
        del rin_cal
        _, _, rin = layer_states(A, ev, l, device)
        base = eval_nll(A, rin, ev, l, device)
        mA, mB = A.blocks[l].moe, Bm.blocks[l].moe
        k = mA.k

        def foreign(j):
            return lambda xs: (expert_fn(mB, j, xs @ Win + bin_)) @ Wout

        def drop_override(e):
            def f(topi, topv, probs, scores):
                nxt = scores.topk(k + 1, -1).indices[:, k:k + 1]
                return torch.where(topi == e, nxt, topi), topv
            return f

        rows = []
        rngs = [np.random.default_rng(s) for s in RANDOM_SEEDS]
        perms = [r.permutation(n) for r in rngs]
        eye_in = torch.eye(Win.shape[0], device=device)
        for e in range(n):
            d_drop = eval_nll(A, rin, ev, l, device, override=drop_override(e)) - base
            d_match = eval_nll(A, rin, ev, l, device, hook=slot_hook(mA, e, foreign(pi[e]))) - base
            d_rand = [eval_nll(A, rin, ev, l, device, hook=slot_hook(mA, e, foreign(int(p[e])))) - base for p in perms]
            row = {"e": e, "pi": pi[e], "drop": d_drop, "matched": d_match, "random": d_rand}
            if e < 2:  # numerical checks on two slots
                row["self"] = eval_nll(A, rin, ev, l, device, hook=slot_hook(mA, e, lambda xs, e=e: expert_fn(mA, e, xs))) - base
                row["selfmap"] = eval_nll(A, rin, ev, l, device, hook=slot_hook(mA, e, lambda xs, e=e: expert_fn(mA, e, xs @ eye_in) @ eye_in)) - base
            rows.append(row)

        def whole(repl_fn):
            def hook(mod, inp, out):
                return (repl_fn(inp[0]).to(out[0].dtype),) + tuple(out[1:])
            return hook

        def stitch_fn(x):
            B_, T_, d = x.shape
            xb = (x.reshape(-1, d).float() @ Win + bin_).view(B_, T_, d)
            yb, *_ = mB(xb)
            return (yb.reshape(-1, d).float() @ Wout).view(B_, T_, d)
        d_stitch = eval_nll(A, rin, ev, l, device, hook=whole(stitch_fn)) - base
        d_zero = eval_nll(A, rin, ev, l, device, hook=whole(lambda x: torch.zeros_like(x))) - base
        valid = [r for r in rows if r["drop"] > MIN_DROP]
        rec = lambda c: [(r["drop"] - c(r)) / r["drop"] for r in valid]
        Rm = rec(lambda r: r["matched"])
        Rr = rec(lambda r: float(np.mean(r["random"])))
        L = {"layer": l, "base_nll": base, "fit_in_R2": fit_in, "fit_out_R2": fit_out, "stitch": d_stitch, "zero": d_zero,
             "stitch_gate_pass": bool(d_stitch < 0.5 * d_zero),
             "stitch_train_loss_first_last": [float(np.mean(st_losses["train"][:10])), float(np.mean(st_losses["train"][-10:]))],
             "stitch_val": st_losses["val"],
             "n_valid": len(valid), "R_matched_median": float(np.median(Rm)) if Rm else None,
             "R_random_median": float(np.median(Rr)) if Rr else None,
             "checks": {k2: [r[k2] for r in rows if k2 in r] for k2 in ("self", "selfmap")},
             "experts": rows, "sec": round(time.time() - t0, 1)}
        res["layers"].append(L)
        print(json.dumps({k2: L[k2] for k2 in ("layer", "fit_in_R2", "fit_out_R2", "stitch", "zero", "stitch_gate_pass",
                                                "stitch_train_loss_first_last", "n_valid",
                                                "R_matched_median", "R_random_median", "checks", "sec")}), flush=True)
        Path(out).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
