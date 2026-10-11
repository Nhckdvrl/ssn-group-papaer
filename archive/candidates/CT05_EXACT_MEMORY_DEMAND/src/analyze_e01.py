"""Analyse E01 outputs against the frozen readouts A-C (docs/E01_PROTOCOL.md).

usage: analyze_e01.py RESULTS_DIR [prefix ...]   e.g. analyze_e01.py ../results/e01 q35_9b q3_8b
"""
import glob, json, sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

D = sys.argv[1]
PREFIXES = sys.argv[2:] or ["q35_9b", "q3_8b"]
rng = np.random.default_rng(0)


def load(prefix):
    recs = []
    for f in sorted(glob.glob(f"{D}/{prefix}.s*.jsonl")):
        recs += [json.loads(l) for l in open(f)]
    return [r for r in recs if "skip" not in r]


def boot_ci(df, fn, by="traj", n=1000):
    g = df[by].unique()
    vals = []
    for _ in range(n):
        s = rng.choice(g, len(g))
        vals.append(fn(pd.concat([df[df[by] == x] for x in s])))
    return np.percentile(vals, [2.5, 97.5])


def events_df(recs):
    rows = []
    for r in recs:
        f = r["full_nll_sum"]
        for j, e in enumerate(r["events"]):
            d = {"cid": r["cid"], "src": r["src"], "traj": r["traj"], "j": j, "ev": e["ev"], "len": e["len"],
                 "age": e["age"], "turns_ago": e["turns_ago"], "attn_future": e["attn_future"],
                 "attn_deploy": e["attn_deploy"], "surpr": e["surpr"], "drift": e["drift"],
                 "dKV": e["kv"]["nll_sum"] - f, "klKV": e["kv"]["kl_mean"], "dTEXT": e["text"]["dnll"],
                 "actKV": e["kv"].get("act_dnll")}
            if e.get("rec"):
                d["dREC"] = e["rec"]["nll_sum"] - f
                d["dBOTH"] = e["both"]["nll_sum"] - f
            rows.append(d)
    return pd.DataFrame(rows)


def ckpt_df(recs):
    rows = []
    for r in recs:
        f = r["full_nll_sum"]
        d = {"cid": r["cid"], "src": r["src"], "traj": r["traj"], "N": r["N"], "T": r["T"], "E": len(r["events"]),
             "full_nll": f}
        for k, v in r["kvwin"].items():
            d[f"kvwin{k}"] = v["nll_sum"] - f
        for k, v in r["textwin"].items():
            d[f"textwin{k}"] = v["dnll"]
        for k, v in r["budget"].items():
            d[k] = v["nll_sum"] - f
        rows.append(d)
    return pd.DataFrame(rows)


def report(prefix):
    recs = load(prefix)
    if not recs:
        print(prefix, "no data"); return None, None
    ev, ck = events_df(recs), ckpt_df(recs)
    hyb = "dBOTH" in ev
    print(f"\n==================== {prefix}: {len(ck)} checkpoints, {len(ev)} events, "
          f"{ck.traj.nunique()} trajectories ====================")
    print("full target NLL/token by src:", (ck.groupby("src").full_nll.sum() / ck.groupby("src").T.sum()).round(3).to_dict())

    # ---- A. leverage
    print("\n[A] window eviction: mean dNLL (nats/target) keep system+task+last k events")
    for src in ["swe", "tau", None]:
        c = ck if src is None else ck[ck.src == src]
        line = {f"KVWIN{k}": round(c[f"kvwin{k}"].mean(), 2) for k in [0, 1, 2, 4, 8]}
        line.update({f"TEXTWIN{k}": round(c[f"textwin{k}"].mean(), 2) for k in [2, 4]})
        for k in [2, 4]:
            num, den = c[f"kvwin{k}"].mean(), c[f"textwin{k}"].mean()
            line[f"rho{k}"] = round(1 - num / den, 2) if abs(den) > 1e-6 else None
        print(" ", src or "all", line)
    if hyb:
        imp = ev[ev.dTEXT > 1.0]
        carry = imp.dBOTH - imp.dKV
        print(f"  per-event recurrence carry (dBOTH - dKV): all mean {np.mean(ev.dBOTH - ev.dKV):.3f} "
              f"median {np.median(ev.dBOTH - ev.dKV):.3f}; important(dTEXT>1, n={len(imp)}) mean {carry.mean():.3f}"
              f" median {carry.median():.3f}, frac>0.1 {np.mean(carry > 0.1):.2f}")
        lo, hi = boot_ci(ev, lambda d: np.mean(d.dBOTH - d.dKV))
        print(f"  carry mean 95% traj-bootstrap CI [{lo:.3f}, {hi:.3f}]")
        print(f"  share of important events' TEXT effect: KV-hide {imp.dKV.sum() / imp.dTEXT.sum():.2f}, "
              f"BOTH {imp.dBOTH.sum() / imp.dTEXT.sum():.2f}, REC-only {imp.dREC.sum() / imp.dTEXT.sum():.2f}")

    # ---- B. structure
    print("\n[B] structure of single-event exactness demand dKV")
    pos = ev.dKV.clip(lower=0)
    top = np.sort(pos.values)[::-1]
    print(f"  |dKV|<0.05: {np.mean(ev.dKV.abs() < 0.05):.2f}  dKV>0.5: {np.mean(ev.dKV > 0.5):.2f}  dKV<-0.5: "
          f"{np.mean(ev.dKV < -0.5):.2f}  top-10% share of positive mass: {top[:max(1, len(top) // 10)].sum() / max(top.sum(), 1e-9):.2f}")
    imp = ev[ev.dTEXT > 1.0]
    print(f"  important events (dTEXT>1): n={len(imp)}; KV not needed (dKV<0.2): {np.mean(imp.dKV < 0.2):.2f}; "
          f"exact-dominant (dKV>0.5*dTEXT): {np.mean(imp.dKV > 0.5 * imp.dTEXT):.2f}")
    print("  by role (mean dKV / mean dTEXT / n):")
    g = ev.groupby(["src", "ev"]).agg(dKV=("dKV", "mean"), dTEXT=("dTEXT", "mean"), n=("dKV", "size"),
                                       pKV05=("dKV", lambda x: np.mean(x > 0.5)))
    print(g.round(3).to_string())

    # ---- C. signals: within-checkpoint Spearman (blocks) and budgets
    print("\n[C] within-checkpoint Spearman(signal, block dNLL), mean over checkpoints")
    sigs = ["recency", "attn_future", "attn_deploy", "surprisal", "random"] + (["drift"] if hyb else [])
    rs = {s: [] for s in sigs}
    for r in recs:
        b = pd.DataFrame(r["blocks"])
        if len(b) < 5:
            continue
        for s in sigs:
            rho = spearmanr(b[s], b.dnll).correlation
            if not np.isnan(rho):
                rs[s].append(rho)
    print("  ", {s: round(float(np.mean(v)), 3) for s, v in rs.items()})
    print("  event-level Spearman pooled within checkpoint:")
    er = {}
    for s in ["age", "attn_future", "attn_deploy", "surpr", "len"] + (["drift"] if hyb else []):
        vals = []
        for cid, g_ in ev.groupby("cid"):
            if len(g_) >= 5 and g_[s].notna().sum() >= 5:
                x = spearmanr(g_[s], g_.dKV).correlation
                if not np.isnan(x):
                    vals.append(x)
        er[s] = round(float(np.mean(vals)), 3)
    print("  ", er)
    print("\n  budgeted block eviction: mean dNLL (lower = better); recovery = (random-x)/(random-oracle)")
    for src in ["swe", "tau", None]:
        c = ck if src is None else ck[ck.src == src]
        for bud in ["0.25", "0.5"]:
            names = [s for s in ["oracle", "attn_future", "attn_deploy", "recency", "drift", "surprisal", "random"]
                     if f"{s}@{bud}" in c]
            vals = {s: c[f"{s}@{bud}"].mean() for s in names}
            rnd, orc = vals["random"], vals["oracle"]
            rec_ = {s: round((rnd - v) / (rnd - orc), 2) if abs(rnd - orc) > 1e-6 else None for s, v in vals.items()}
            print(f"   {src or 'all'} @{bud}: " + ", ".join(f"{s} {vals[s]:.2f} ({rec_[s]})" for s in names))
    return ev, ck


out = {p: report(p) for p in PREFIXES}


def rho_ci(ck, k, cids=None):
    c = ck if cids is None else ck[ck.cid.isin(cids)]
    f = lambda d: 1 - d[f"kvwin{k}"].mean() / d[f"textwin{k}"].mean()
    return f(c), boot_ci(c, f)


if all(out[p][1] is not None for p in PREFIXES[:2]) and len(PREFIXES) >= 2:
    ckH, ckT = out[PREFIXES[0]][1], out[PREFIXES[1]][1]
    common = set(ckH.cid) & set(ckT.cid)
    print(f"\n[A-final] recurrence retention rho on {len(common)} common checkpoints (traj-bootstrap 95% CI)")
    for k in [2, 4]:
        for p_, ck in [(PREFIXES[0], ckH), (PREFIXES[1], ckT)]:
            v, (lo_, hi_) = rho_ci(ck, k, common)
            print(f"   rho{k} {p_}: {v:.3f} [{lo_:.3f}, {hi_:.3f}]")
        cH, cT = ckH[ckH.cid.isin(common)].set_index("cid"), ckT[ckT.cid.isin(common)].set_index("cid")
        j = cH[["traj", f"kvwin{k}", f"textwin{k}"]].join(cT[[f"kvwin{k}", f"textwin{k}"]], rsuffix="_T").reset_index()
        f = lambda d: (1 - d[f"kvwin{k}"].mean() / d[f"textwin{k}"].mean()) - (1 - d[f"kvwin{k}_T"].mean() / d[f"textwin{k}_T"].mean())
        print(f"   hybrid-specific leverage rho{k}_H - rho{k}_T: {f(j):.3f} {np.round(boot_ci(j, f), 3)}")
if len(PREFIXES) >= 2 and all(out[p][0] is not None for p in PREFIXES[:2]):
    a, b = out[PREFIXES[0]][0], out[PREFIXES[1]][0]
    m = a.merge(b, on=["cid", "j"], suffixes=("_H", "_T"))
    m = m[m.ev_H == m.ev_T]
    print(f"\n[X] cross-model per-event agreement (n={len(m)}): Spearman dKV {spearmanr(m.dKV_H, m.dKV_T).correlation:.3f}, "
          f"dTEXT {spearmanr(m.dTEXT_H, m.dTEXT_T).correlation:.3f}")
    print(f"    hybrid vs transformer KV-hide share of TEXT effect (events dTEXT>1 in both): "
          f"H {m[(m.dTEXT_H > 1) & (m.dTEXT_T > 1)].dKV_H.sum() / m[(m.dTEXT_H > 1) & (m.dTEXT_T > 1)].dTEXT_H.sum():.2f}, "
          f"T {m[(m.dTEXT_H > 1) & (m.dTEXT_T > 1)].dKV_T.sum() / m[(m.dTEXT_H > 1) & (m.dTEXT_T > 1)].dTEXT_T.sum():.2f}")
