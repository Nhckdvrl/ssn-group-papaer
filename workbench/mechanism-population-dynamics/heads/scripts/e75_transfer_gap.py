"""E75: why does the IOI circuit of Pythia-410M not transfer to its same-initialization deduplicated sibling (E73: 0.05)?
Measurement artefact, the same computation carried by other heads / repaired downstream, or a different computation?
Protocol: experiments/E75-*.md. IOI prompts as in e14_ioi.py / e73 (N = 200, seed 42); even prompts = fit, odd = held out.

  e75_transfer_gap.py --pair 410m            # ref pythia-410m vs targets: -deduped, -seed1
  e75_transfer_gap.py --pair 160m            # ref pythia-160m vs target: -deduped
  e75_transfer_gap.py --analyze
"""
import argparse
import json
import random

import numpy as np
import torch

import mp_common as mc
from e14_ioi import build
from e73_ioi_transfer import load

OUT = mc.RESULTS / "e75"
K = 3
FEATS = ("dla", "dla_io", "dla_s", "att_io", "att_s1", "att_s2", "att_end", "att_bos", "ov_copy")


class IOI:
    def __init__(self, model):
        self.m = model
        self.ioi, abc = build(model)
        self.L, self.H = model.cfg.n_layers, model.cfg.n_heads
        self.end = torch.as_tensor(self.ioi.word_idx["end"]).cpu()
        self.N = len(self.end)
        self.b = torch.arange(self.N)
        self.io = torch.as_tensor(self.ioi.io_tokenIDs)
        self.s = torch.as_tensor(self.ioi.s_tokenIDs)
        _, cabc = model.run_with_cache(abc.toks.long().to(model.cfg.device), names_filter=lambda n: n.endswith("hook_z"))
        eabc = torch.as_tensor(abc.word_idx["end"]).cpu()
        self.mean_z = {l: cabc[f"blocks.{l}.attn.hook_z"][torch.arange(len(eabc)), eabc].mean(0) for l in range(self.L)}
        del cabc

    def logits_end(self, hooks=()):
        lg = self.m.run_with_hooks(self.ioi.toks.long().to(self.m.cfg.device), fwd_hooks=list(hooks))
        return lg[self.b, self.end]

    def ld(self, hooks=()):
        le = self.logits_end(hooks)
        return (le[self.b, self.io.to(le.device)] - le[self.b, self.s.to(le.device)]).float().cpu()

    def hooks(self, heads):
        by = {}
        for l, h in heads:
            by.setdefault(l, []).append(h)
        end = self.end

        def mk(l, hs):
            def hook(z, hook):
                for hh in hs:
                    z[self.b, end.to(z.device), hh] = self.mean_z[l][hh].to(z.dtype)
                return z
            return hook
        return [(f"blocks.{l}.attn.hook_z", mk(l, hs)) for l, hs in by.items()]

    def head_table(self):
        """Per prompt and head at END: DLA (IO - S), its IO and -S parts, the direct effect of mean-ablating the head
        (clean DLA - DLA of the ABC-mean output at the clean final-LN scale), attention to IO / S1 / S2 / END / position 0."""
        m, b, end = self.m, self.b, self.end
        wi = self.ioi.word_idx
        _, cache = m.run_with_cache(self.ioi.toks.long().to(m.cfg.device),
                                    names_filter=lambda n: n.endswith("hook_z") or n.endswith("hook_pattern")
                                    or n == "ln_final.hook_scale")
        scale = cache["ln_final.hook_scale"][b, end]
        uio, us = m.W_U[:, self.io.to(scale.device)].T, m.W_U[:, self.s.to(scale.device)].T
        T = {k: torch.zeros(self.N, self.L, self.H) for k in ("dla", "dla_io", "dla_s", "direct", "att_io", "att_s1",
                                                               "att_s2", "att_end", "att_bos")}
        pos = {k: torch.as_tensor(wi[w]).cpu() for k, w in (("att_io", "IO"), ("att_s1", "S1"), ("att_s2", "S2"),
                                                             ("att_end", "end"))}
        for l in range(self.L):
            z = cache[f"blocks.{l}.attn.hook_z"][b, end]
            res = torch.einsum("nhd,hdm->nhm", z, m.W_O[l]) / scale[:, :, None]
            T["dla_io"][:, l] = (res * uio[:, None]).sum(-1).cpu()
            T["dla_s"][:, l] = -(res * us[:, None]).sum(-1).cpu()
            T["dla"][:, l] = T["dla_io"][:, l] + T["dla_s"][:, l]
            rm = torch.einsum("hd,hdm->hm", self.mean_z[l], m.W_O[l])[None] / scale[:, :, None]
            T["direct"][:, l] = T["dla"][:, l] - ((rm * (uio - us)[:, None]).sum(-1)).cpu()
            pat = cache[f"blocks.{l}.attn.hook_pattern"][b, :, end]  # [N, H, k]
            for k, p in pos.items():
                T[k][:, l] = pat[b, :, p.to(pat.device)].cpu()
            T["att_bos"][:, l] = pat[:, :, 0].cpu()
        del cache
        return T

    def ov_copy(self):
        """Name-copying of each head's OV circuit: names -> W_E -> W_V W_O -> W_U; mean over names of the z-scored
        logit of the same name among all names (Wang et al.'s copy score, without the MLP0 embedding)."""
        m = self.m
        names = torch.unique(torch.cat([self.io, self.s])).to(m.cfg.device)
        E = m.W_E[names]
        sc = torch.zeros(self.L, self.H)
        for l in range(self.L):
            for h in range(self.H):
                M = (E @ m.W_V[l, h] @ m.W_O[l, h]) @ m.W_U[:, names]  # [n, n]
                Mz = (M - M.mean(1, keepdim=True)) / (M.std(1, keepdim=True) + 1e-6)
                sc[l, h] = Mz.diag().mean().cpu()
        return sc


def profile(T, ov, idx):
    """Head feature table [L*H, F] averaged over the prompts in idx."""
    cols = [T[f][idx].mean(0).ravel() if f != "ov_copy" else ov.ravel() for f in FEATS]
    return torch.stack(cols, 1).numpy()


def zs(X):
    return (X - X.mean(0)) / (X.std(0) + 1e-9)


def measure_model(repo):
    model = load(repo)
    torch.set_grad_enabled(False)
    I = IOI(model)
    T = I.head_table()
    ov = I.ov_copy()
    ld = I.ld()
    return model, I, T, ov, ld


def run_pair(size):
    OUT.mkdir(parents=True, exist_ok=True)
    ref_repo = f"EleutherAI/pythia-{size}"
    targets = [f"{ref_repo}-deduped"] + ([f"{ref_repo}-seed1"] if size == "410m" else [])
    model, I, T, ov, ld = measure_model(ref_repo)
    N = I.N
    fit, held = np.arange(0, N, 2), np.arange(1, N, 2)
    H = I.H
    Pf_ref = profile(T, ov, fit)
    dla_fit_ref = T["dla"][fit].mean(0).ravel().numpy()
    ref_top = [divmod(int(i), H) for i in np.argsort(-dla_fit_ref)[:K]]
    ref_pp = T["dla"][fit].reshape(len(fit), -1).numpy()  # per-prompt DLA on the fit half
    rec = {"repo": ref_repo, "ld": ld.tolist(), "ref_top_fit": ref_top,
           "profile_fit": Pf_ref.round(5).tolist(), "profile_held": profile(T, ov, held).round(5).tolist(),
           "direct_mean": T["direct"].mean(0).numpy().round(5).tolist()}
    rec["self"] = evaluate(I, T, ref_top, {"own": ref_top}, fit, held)
    (OUT / f"{ref_repo.split('/')[1]}.json").write_text(json.dumps(rec))
    del model, I
    torch.cuda.empty_cache()

    for repo in targets:
        model, I, T, ov, ld = measure_model(repo)
        Pf = profile(T, ov, fit)
        dla_fit = T["dla"][fit].mean(0).ravel().numpy()
        own = [divmod(int(i), H) for i in np.argsort(-dla_fit)[:K]]
        # task mapping 1: nearest head in the fit-half IOI role profile (features z-scored within each model)
        Zr, Zt = zs(Pf_ref), zs(Pf)
        prof_map, used = [], set()
        for l, h in ref_top:
            d = ((Zt - Zr[l * H + h]) ** 2).sum(1)
            for j in np.argsort(d):
                if int(j) not in used:
                    used.add(int(j))
                    prof_map.append(divmod(int(j), H))
                    break
        # task mapping 2: target head whose per-prompt DLA on the fit half correlates best with the reference head's
        tp = T["dla"][fit].reshape(len(fit), -1).numpy()
        C = np.corrcoef(ref_pp.T, tp.T)[: ref_pp.shape[1], ref_pp.shape[1]:]
        corr_map, used = [], set()
        for l, h in ref_top:
            for j in np.argsort(-np.nan_to_num(C[l * H + h], nan=-9)):
                if int(j) not in used:
                    used.add(int(j))
                    corr_map.append(divmod(int(j), H))
                    break
        sets = {"own": own, "index": ref_top, "profile_map": prof_map, "corr_map": corr_map}
        r = {"repo": repo, "ld": ld.tolist(), "sets": sets, "profile_fit": Pf.round(5).tolist(),
             "profile_held": profile(T, ov, held).round(5).tolist(),
             "direct_mean": T["direct"].mean(0).numpy().round(5).tolist(),
             "eval": evaluate(I, T, own, sets, fit, held)}
        (OUT / f"{repo.split('/')[1]}.json").write_text(json.dumps(r))
        print(repo, {k: v for k, v in sets.items()}, flush=True)
        print({k: {kk: round(vv, 3) if isinstance(vv, float) else vv for kk, vv in v.items()}
               for k, v in r["eval"]["sets"].items()}, flush=True)
        del model, I
        torch.cuda.empty_cache()


def evaluate(I, T, own, sets, fit, held):
    """Held-out logit-difference drops: joint total (mean ablation), joint direct (frozen downstream), sum of
    single-head total drops; random sets; and single-head drops of the 30 heads with largest |DLA|."""
    ld = I.ld()
    held_t = torch.as_tensor(held)
    base = float(ld[held_t].mean())
    drop = lambda hs: base - float(I.ld(I.hooks(hs))[held_t].mean())
    direct = lambda hs: float(sum(T["direct"][held_t, l, h].mean() for l, h in hs))
    single = {}
    cand = sorted({(l, h) for s in sets.values() for l, h in s})
    order = np.argsort(-np.abs(T["dla"][torch.as_tensor(fit)].mean(0).ravel().numpy()))[:30]
    cand = sorted(set(cand) | {divmod(int(i), I.H) for i in order})
    for l, h in cand:
        single[f"{l}.{h}"] = drop([(l, h)])
    out = {"base_ld_held": base, "sets": {}, "single": single}
    for name, hs in sets.items():
        out["sets"][name] = {"heads": [f"{l}.{h}" for l, h in hs], "joint_total": drop(hs), "joint_direct": direct(hs),
                             "sum_single_total": float(sum(single[f"{l}.{h}"] for l, h in hs)),
                             "dla_held": float(sum(T["dla"][held_t, l, h].mean() for l, h in hs))}
    rng = random.Random(1)
    pool = [(l, h) for l in range(I.L) for h in range(I.H) if (l, h) not in own]
    out["random_total"] = [drop(rng.sample(pool, K)) for _ in range(20)]
    # bootstrap CI of transfer ratios over held-out prompts (joint ablations, per-prompt)
    per = {name: (ld[held_t] - I.ld(I.hooks(hs))[held_t]).numpy() for name, hs in sets.items()}
    rs = np.random.default_rng(0)
    B = [rs.integers(0, len(held), len(held)) for _ in range(1000)]
    out["ratio_ci"] = {name: np.percentile([per[name][bb].mean() / per["own"][bb].mean() for bb in B], [2.5, 50, 97.5]
                                           ).round(3).tolist() for name in sets}
    return out


def classes(P, ld_mean):
    """Functional classes from a profile table: name mover (att_io > 0.2, DLA > 2% of LD), negative name mover
    (att_io > 0.2, DLA < -2%), other direct writer (|DLA| > 2%, att_io <= 0.2)."""
    f = {k: P[:, i] for i, k in enumerate(FEATS)}
    th = 0.02 * ld_mean
    return {"NM": np.flatnonzero((f["att_io"] > 0.2) & (f["dla"] > th)).tolist(),
            "NNM": np.flatnonzero((f["att_io"] > 0.2) & (f["dla"] < -th)).tolist(),
            "other_pos": np.flatnonzero((f["att_io"] <= 0.2) & (f["dla"] > th)).tolist(),
            "other_neg": np.flatnonzero((f["att_io"] <= 0.2) & (f["dla"] < -th)).tolist()}


def analyze():
    out = {}
    for size, tgts in (("160m", ["deduped"]), ("410m", ["deduped", "seed1"])):
        rf = OUT / f"pythia-{size}.json"
        if not rf.exists():
            continue
        ref = json.loads(rf.read_text())
        H = {"160m": 12, "410m": 16}[size]
        Pr = np.array(ref["profile_held"])
        lab = lambda i: f"{i // H}.{i % H}"
        res = {"ref_self": ref["self"]["sets"]["own"] | {"base": ref["self"]["base_ld_held"]},
               "ref_classes": {k: [lab(i) for i in v] for k, v in classes(Pr, np.mean(ref["ld"])).items()}}
        res["ref_class_dla"] = {k: float(Pr[v, 0].sum()) for k, v in classes(Pr, np.mean(ref["ld"])).items()}
        for t in tgts:
            f = OUT / f"pythia-{size}-{t}.json"
            if not f.exists():
                continue
            d = json.loads(f.read_text())
            e = d["eval"]
            own = e["sets"]["own"]["joint_total"]
            rand = float(np.mean(e["random_total"]))
            Pt = np.array(d["profile_held"])
            cl = classes(Pt, np.mean(d["ld"]))
            row = {"base": e["base_ld_held"], "random_total": rand, "ratio_ci": e["ratio_ci"],
                   "classes": {k: [lab(i) for i in v] for k, v in cl.items()},
                   "class_dla": {k: float(Pt[v, 0].sum()) for k, v in cl.items()}, "sets": {}}
            for name, s in e["sets"].items():
                row["sets"][name] = s | {"ratio_total": s["joint_total"] / own,
                                         "self_repair": 1 - s["joint_total"] / s["joint_direct"] if s["joint_direct"] else None}
            # the reference's top heads: their role profile in reference vs target (held-out half)
            row["ref_heads_profile"] = {lab(l * H + h): {"ref": dict(zip(FEATS, Pr[l * H + h].round(3).tolist())),
                                                         "target": dict(zip(FEATS, Pt[l * H + h].round(3).tolist()))}
                                        for l, h in [tuple(map(int, x.split("."))) for x in e["sets"]["index"]["heads"]]}
            row["target_own_profile"] = {x: {"target": dict(zip(FEATS, Pt[int(x.split('.')[0]) * H + int(x.split('.')[1])].round(3).tolist())),
                                             "ref": dict(zip(FEATS, Pr[int(x.split('.')[0]) * H + int(x.split('.')[1])].round(3).tolist()))}
                                         for x in e["sets"]["own"]["heads"]}
            res[t] = row
        out[size] = res
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1)[:12000])



ROLE = ("att_io", "att_s1", "att_s2", "att_end", "att_bos", "ov_copy")  # no DLA-derived feature


def role_only(size):
    """POST-HOC (after the main readout): map the reference top-3 to target heads using only attention and OV-copy
    features on the fit half (no DLA, so the map cannot simply pick the target's most important heads); evaluate the
    held-out joint ablation. Also report where the mapped heads rank in the target's own fit-half DLA."""
    ref = json.loads((OUT / f"pythia-{size}.json").read_text())
    cols = [FEATS.index(f) for f in ROLE]
    Zr = zs(np.array(ref["profile_fit"])[:, cols])
    res = {}
    for t in (["deduped", "seed1"] if size == "410m" else ["deduped"]):
        f = OUT / f"pythia-{size}-{t}.json"
        d = json.loads(f.read_text())
        Pt = np.array(d["profile_fit"])
        Zt = zs(Pt[:, cols])
        model = load(f"EleutherAI/pythia-{size}-{t}")
        torch.set_grad_enabled(False)
        I = IOI(model)
        H = I.H
        mp, used = [], set()
        for l, h in ref["ref_top_fit"]:
            dd = ((Zt - Zr[l * H + h]) ** 2).sum(1)
            j = next(int(j) for j in np.argsort(dd) if int(j) not in used)
            used.add(j)
            mp.append(divmod(j, H))
        T = I.head_table()
        held = np.arange(1, I.N, 2)
        own = [tuple(x) for x in d["sets"]["own"]]
        e = evaluate(I, T, own, {"own": own, "role_only": mp}, np.arange(0, I.N, 2), held)
        rank = np.argsort(np.argsort(-Pt[:, FEATS.index("dla")]))
        res[t] = {"map": [f"{l}.{h}" for l, h in mp], "dla_rank_in_target": [int(rank[l * H + h]) + 1 for l, h in mp],
                  "ratio": e["sets"]["role_only"]["joint_total"] / e["sets"]["own"]["joint_total"],
                  "ratio_ci": e["ratio_ci"]["role_only"], "eval": e["sets"]}
        print(size, t, res[t]["map"], res[t]["dla_rank_in_target"], round(res[t]["ratio"], 3), res[t]["ratio_ci"], flush=True)
        del model, I
        torch.cuda.empty_cache()
    (OUT / f"role_only_{size}.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--role-only")
    a = ap.parse_args()
    role_only(a.role_only) if a.role_only else analyze() if a.analyze else run_pair(a.pair)
