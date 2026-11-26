"""E04-A: how much of a real post-training logit change is a context-independent affine map τ·z0 + b?

For one parent→child pair and several context sources (neutral text; parent's own generations; child's own
generations), cache final hidden states h0, h1 on sampled positions, split by document/prompt (even = fit,
odd = test), and fit by convex minimisation of mean KL(p1 ‖ softmax(τ z0 + b)):
  'tau'          b = 0, τ free          (global per-token sharpening / flattening)
  'bias'         τ = 1, b free          (global vocabulary preference)
  'tau_bias'     both
  'tau_bias_ns'  both, b fixed to 0 on special/added tokens (guards against chat/format-token dominance)
b: damped iterative proportional fitting (match the context-averaged distribution), τ: 1-D Newton.
Readouts on held-out positions: KL(p1‖q), KL reduction vs the parent, top-1 agreement with the child,
cross-source transfer (fit on S, test on S'), structure of b (top tokens, concentration, special-token share),
the share of the centred logit change explained by its context mean, and localisation of the global part:
corr(b, centred ΔW μ0) [head] vs corr(b, centred W0 mean(Δh)) [backbone common shift].

Usage: python e04_fit.py <pair_key> [--sources neutral,gen_parent,gen_child] [--max_pos 40000] [--selftest]
"""
import argparse
import gc
import json
import time
from pathlib import Path

import numpy as np
import torch

import models

ROOT = Path(__file__).resolve().parents[1]
BIG = Path("/tmp/xiang_lmhead/e04")
GEN = BIG / "gen"


def load_sources(pair, names, tok, max_len=512, gen_max=1024):
    """Return {source: list of (doc_id, token_ids, first_pred_pos)}; predictions are made for positions
    first_pred_pos-1 ... len-2 (i.e. tokens first_pred_pos..len-1 are targets)."""
    p0, p1, _ = models.PAIRS[pair]
    out = {}
    for s in names:
        seqs = []
        if s == "neutral":
            from build_inputs import load_e01_texts
            for k, t in enumerate(load_e01_texts()):
                ids = tok(t["text"], add_special_tokens=False)["input_ids"][: max_len + 1]
                seqs.append((k, ids, 1))
        else:
            who = p0 if s == "gen_parent" else p1
            f = GEN / f"ctx_{who}.jsonl"
            if not f.exists():
                print("missing", f); continue
            for line in open(f):
                g = json.loads(line)
                for c in g["completions"]:
                    ids = g["prompt_ids"] + c["token_ids"][:gen_max]
                    seqs.append((g["index"], ids, len(g["prompt_ids"])))
        out[s] = seqs
    return out


@torch.no_grad()
def hidden(name, srcs, dev, sel):
    from transformers import AutoModelForCausalLM
    m = AutoModelForCausalLM.from_pretrained(models.path(name), dtype=torch.bfloat16).to(dev).eval()
    W = m.lm_head.weight.detach().float()
    H = {}
    for s, seqs in srcs.items():
        rows = []
        for i, (doc, ids, first) in enumerate(seqs):
            x = torch.tensor([ids], device=dev)
            h = m.model(input_ids=x).last_hidden_state[0, first - 1: -1]
            rows.append(h[sel[s][i]].to(torch.bfloat16))
        H[s] = torch.cat(rows)
    del m; gc.collect(); torch.cuda.empty_cache()
    return H, W


def chunks(n, size=4096):
    for i in range(0, n, size):
        yield slice(i, min(n, i + size))


class Fitter:
    def __init__(self, H0, W0, P1fn, mask_special, dev):
        self.H0, self.W0, self.P1fn, self.dev = H0, W0, P1fn, dev
        self.n, self.V = H0.shape[0], W0.shape[0]
        self.free = torch.ones(self.V, dtype=torch.bool, device=dev) if mask_special is None else ~mask_special
        # fixed statistics of the target: p̄1 and E_p1[z0]
        self.p1bar = torch.zeros(self.V, dtype=torch.float64, device=dev)
        self.Ep1z0 = 0.0
        for sl in chunks(self.n):
            z0 = self.z0(sl); p1 = P1fn(sl)
            self.p1bar += p1.double().sum(0)
            self.Ep1z0 += float((p1 * z0).sum())
        self.p1bar /= self.n; self.Ep1z0 /= self.n

    def z0(self, sl):
        return (self.H0[sl].float() @ self.W0.T)

    def stats(self, tau, b):
        qbar = torch.zeros(self.V, dtype=torch.float64, device=self.dev)
        Eqz = Eqz2 = ce = 0.0
        for sl in chunks(self.n):
            z0 = self.z0(sl)
            a = tau * z0 + b
            lq = torch.log_softmax(a, -1); q = lq.exp()
            qbar += q.double().sum(0)
            ez = (q * z0).sum(-1); Eqz += float(ez.sum()); Eqz2 += float(((q * z0 * z0).sum(-1) - ez ** 2).sum())
            ce -= float((self.P1fn(sl) * lq).sum())
        return qbar / self.n, Eqz / self.n, Eqz2 / self.n, ce / self.n

    def fit(self, fit_tau, fit_b, iters=60, eps=1e-10):
        tau, b = 1.0, torch.zeros(self.V, device=self.dev)
        hist = []
        for it in range(iters):
            qbar, Eqz, varz, ce = self.stats(tau, b)
            hist.append(ce)
            if fit_b:
                step = torch.log((self.p1bar + eps) / (qbar + eps)).float()
                b = torch.where(self.free, (b + 0.8 * step).clamp(-30, 30), b)
            if fit_tau:
                g = Eqz - self.Ep1z0                      # d CE / d τ
                tau = float(np.clip(tau - g / max(varz, 1e-6), 0.2, 5.0))
            if it > 5 and abs(hist[-2] - hist[-1]) < 1e-7 * max(1.0, abs(hist[-1])):
                break
        b = b - b[self.free].mean() * self.free           # centre (softmax-invariant)
        return tau, b, hist


@torch.no_grad()
def evaluate(H0, W0, P1fn, LP1fn, n, tau, b, doc):
    """Per-position KL(p1‖q) for q = softmax(τ z0 + b) and top-1 agreement with the child."""
    kls, agree = [], []
    for sl in chunks(n):
        z0 = H0[sl].float() @ W0.T
        lq = torch.log_softmax(tau * z0 + b, -1)
        lp1 = LP1fn(sl)
        kls.append(((lp1.exp()) * (lp1 - lq)).sum(-1).cpu())
        agree.append((lq.argmax(-1) == lp1.argmax(-1)).float().cpu())
    return torch.cat(kls).numpy(), torch.cat(agree).numpy()


def doc_boot(v, doc, n=2000):
    ud = np.unique(doc); means = np.array([v[doc == d].mean() for d in ud])
    rng = np.random.default_rng(0)
    bs = [means[rng.integers(0, len(means), len(means))].mean() for _ in range(n)]
    return float(means.mean()), [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pair")
    ap.add_argument("--sources", default="neutral,gen_parent,gen_child")
    ap.add_argument("--max_pos", type=int, default=40000, help="positions per source per split")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    dev = "cuda"; t0 = time.time()
    torch.backends.cuda.matmul.allow_tf32 = True
    p0, p1, stage = models.PAIRS[args.pair]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(models.path(p1))
    srcs = load_sources(args.pair, args.sources.split(","), tok)
    rng = np.random.default_rng(0)
    sel, docs, split = {}, {}, {}
    for s, seqs in srcs.items():
        npos = [len(ids) - first for _, ids, first in seqs]
        keep_frac = min(1.0, 2 * args.max_pos / max(1, sum(npos)))
        sel[s], d_, sp_ = [], [], []
        for (doc, ids, first), m in zip(seqs, npos):
            k = np.sort(rng.choice(m, size=max(1, int(round(m * keep_frac))), replace=False))
            sel[s].append(torch.tensor(k)); d_ += [doc] * len(k); sp_ += [doc % 2] * len(k)
        docs[s], split[s] = np.array(d_), np.array(sp_)
    H0, W0 = hidden(p0, srcs, dev, sel)
    if args.selftest:   # synthetic child: z1 = τ* z0 + b*
        g = torch.Generator(device=dev).manual_seed(0)
        bstar = torch.zeros(W0.shape[0], device=dev)
        idx = torch.randperm(W0.shape[0], generator=g, device=dev)[: W0.shape[0] // 50]
        bstar[idx] = torch.randn(len(idx), generator=g, device=dev)
        H1, W1 = H0, W0
        zfun = lambda Hs, sl: 0.8 * (Hs[sl].float() @ W0.T) + bstar
    else:
        H1, W1 = hidden(p1, srcs, dev, sel)
        zfun = lambda Hs, sl: Hs[sl].float() @ W1.T
    special = torch.zeros(W0.shape[0], dtype=torch.bool, device=dev)
    sp_ids = [i for i in set(tok.all_special_ids) | set(tok.get_added_vocab().values()) if i < W0.shape[0]]
    special[sp_ids] = True
    special[len(tok):] = True                               # padding rows of the head
    res = {"pair": args.pair, "parent": p0, "child": p1, "stage": stage, "selftest": args.selftest,
           "rev_parent": models.revision(p0), "rev_child": models.revision(p1), "sources": {}, "transfer": {}}
    fits = {}
    for s in srcs:
        fitm, testm = split[s] == 0, split[s] == 1
        Hf0, Hf1 = H0[s][torch.tensor(fitm)], H1[s][torch.tensor(fitm)]
        Ht0, Ht1 = H0[s][torch.tensor(testm)], H1[s][torch.tensor(testm)]
        P1f = lambda sl, A=Hf1: torch.softmax(zfun(A, sl), -1)
        F = Fitter(Hf0, W0, P1f, None, dev)
        Fns = Fitter(Hf0, W0, P1f, special, dev)
        # support-restricted bias: free only on tokens the child actually uses in these contexts (mean prob > 1e-5);
        # forward-KL fits otherwise raise tokens that are negligible under both models, which derails free sampling
        Fsupp = Fitter(Hf0, W0, P1f, F.p1bar.float() <= 1e-5, dev)
        Fsuppns = Fitter(Hf0, W0, P1f, (F.p1bar.float() <= 1e-5) | special, dev)   # ordinary tokens only
        LP1t = lambda sl, A=Ht1: torch.log_softmax(zfun(A, sl), -1)
        P1t = lambda sl, A=Ht1: torch.softmax(zfun(A, sl), -1)
        r = {"n_fit": int(fitm.sum()), "n_test": int(testm.sum()), "n_docs_test": int(len(np.unique(docs[s][testm])))}
        base_kl, base_ag = evaluate(Ht0, W0, P1t, LP1t, Ht0.shape[0], 1.0, torch.zeros(W0.shape[0], device=dev), docs[s][testm])
        r["parent"] = {"kl": doc_boot(base_kl, docs[s][testm]), "top1_agree": float(base_ag.mean())}
        r["n_support_tokens"] = int((F.p1bar > 1e-5).sum())
        for name, (ft, fb, Fx) in {"tau": (True, False, F), "bias": (False, True, F), "tau_bias": (True, True, F),
                                   "tau_bias_ns": (True, True, Fns), "tau_bias_supp": (True, True, Fsupp),
                                   "bias_supp": (False, True, Fsupp), "tau_bias_supp_ns": (True, True, Fsuppns)}.items():
            tau, b, hist = Fx.fit(ft, fb)
            kl, ag = evaluate(Ht0, W0, P1t, LP1t, Ht0.shape[0], tau, b, docs[s][testm])
            mean_kl = doc_boot(kl, docs[s][testm])
            r[name] = {"tau": tau, "kl": mean_kl, "kl_reduction": 1 - mean_kl[0] / r["parent"]["kl"][0],
                       "top1_agree": float(ag.mean()), "iters": len(hist), "fit_ce_last": hist[-1]}
            fits[(s, name)] = (tau, b)
        # centred logit change on test positions: share explained by its context mean (fit-split mean)
        mean_dz = torch.zeros(W0.shape[0], dtype=torch.float64, device=dev)
        for sl in chunks(Hf0.shape[0]):
            dz = zfun(Hf1, sl) - Hf0[sl].float() @ W0.T
            mean_dz += (dz - dz.mean(-1, keepdim=True)).double().sum(0)
        mean_dz /= Hf0.shape[0]
        tot = resid = 0.0
        for sl in chunks(Ht0.shape[0]):
            dz = zfun(Ht1, sl) - Ht0[sl].float() @ W0.T
            dz = (dz - dz.mean(-1, keepdim=True)).double()
            tot += float((dz ** 2).sum()); resid += float(((dz - mean_dz) ** 2).sum())
        r["centred_logit_change_share_of_context_mean"] = 1 - resid / tot
        # localisation (parent mean hidden on fit split; head and backbone global terms, centred over vocab)
        if not args.selftest:
            mu0 = Hf0.float().mean(0); dh = (Hf1.float() - Hf0.float()).mean(0)
            c = lambda v: (v - v.mean())
            b_head = c((W1 - W0) @ mu0); b_bb = c(W0 @ dh); b_fit = fits[(s, "tau_bias")][1]
            cor = lambda a, b_: float(torch.corrcoef(torch.stack([a[~special], b_[~special]]))[0, 1])
            X = torch.stack([b_head[~special], b_bb[~special]], 1).double(); y = b_fit[~special].double()
            coef = torch.linalg.lstsq(X, y.unsqueeze(1)).solution.squeeze()
            r2 = 1 - float(((y - X @ coef) ** 2).sum() / ((y - y.mean()) ** 2).sum())
            r["localisation"] = {"corr_b_head_global": cor(b_fit, b_head), "corr_b_backbone_global": cor(b_fit, b_bb),
                                 "corr_b_mean_logit_change": cor(b_fit, mean_dz.float()),
                                 "r2_b_on_head_and_backbone": r2, "coef_head_backbone": coef.tolist(),
                                 "norm_head_global": float(b_head[~special].norm()), "norm_backbone_global": float(b_bb[~special].norm()),
                                 "mu_over_h": float(mu0.norm() / Hf0.float().norm(dim=1).mean())}
        else:
            tb = fits[(s, "tau_bias")]
            bc = bstar - bstar.mean()
            r["selftest_recovery"] = {"tau_fit": tb[0], "tau_true": 0.8,
                                      "corr_b": float(torch.corrcoef(torch.stack([tb[1], bc]))[0, 1])}
        # structure of b (tau_bias fit)
        b = fits[(s, "tau_bias")][1]
        ab = b.abs(); e = (b ** 2)
        srt = torch.sort(e, descending=True).values
        r["b_structure"] = {"std": float(b.std()), "special_energy_share": float(e[special].sum() / e.sum()),
                            "top1pct_energy_share": float(srt[: max(1, len(srt) // 100)].sum() / e.sum()),
                            "top_up": [(tok.convert_ids_to_tokens(int(i)) if i < len(tok) else f"<pad{i}>", float(b[i])) for i in torch.argsort(b, descending=True)[:30]],
                            "top_down": [(tok.convert_ids_to_tokens(int(i)) if i < len(tok) else f"<pad{i}>", float(b[i])) for i in torch.argsort(b)[:30]]}
        res["sources"][s] = r
        print(s, {k: (r[k]["kl_reduction"] if isinstance(r.get(k), dict) and "kl_reduction" in r[k] else None)
                  for k in ("tau", "bias", "tau_bias", "tau_bias_ns")}, "parent KL", r["parent"]["kl"][0], flush=True)
    # cross-source transfer of the tau_bias fit
    for s_fit in srcs:
        tau, b = fits[(s_fit, "tau_bias")]
        for s_test in srcs:
            testm = split[s_test] == 1
            Ht0, Ht1 = H0[s_test][torch.tensor(testm)], H1[s_test][torch.tensor(testm)]
            kl, _ = evaluate(Ht0, W0, lambda sl, A=Ht1: torch.softmax(zfun(A, sl), -1),
                             lambda sl, A=Ht1: torch.log_softmax(zfun(A, sl), -1), Ht0.shape[0], tau, b, docs[s_test][testm])
            res["transfer"][f"{s_fit}->{s_test}"] = 1 - float(kl.mean()) / res["sources"][s_test]["parent"]["kl"][0]
    # save the fitted vectors for generation experiments (node-local) and the summary (git)
    BIG.mkdir(parents=True, exist_ok=True)
    tag = args.pair + ("__selftest" if args.selftest else "")
    np.savez_compressed(BIG / f"fit_{tag}.npz", **{f"{s}.{n}.b": v[1].cpu().numpy() for (s, n), v in fits.items()},
                        **{f"{s}.{n}.tau": np.array(v[0]) for (s, n), v in fits.items()})
    res["seconds"] = time.time() - t0
    out = ROOT / "results" / "e04"; out.mkdir(parents=True, exist_ok=True)
    (out / f"fit_{tag}.json").write_text(json.dumps(res, indent=1))
    print("transfer", json.dumps(res["transfer"], indent=1)); print("sec", res["seconds"])


if __name__ == "__main__":
    main()
