#!/usr/bin/env python3
"""Weight-space comparison of LoRA adapters (teachers and students share the base model, so dW = B A is comparable).

<B1 A1, B2 A2>_F = sum((B1^T B2) * (A1 A2^T)), computed in r x r per module; alpha/r is the same for all adapters.
Writes the Gram matrix (total and per module type) and prints cosines plus the rule / seed / shared decomposition:
  teachers u_ck (4 configs x 3 seeds, E03 ep10), T_null (E06 teacher_null_s1 ep10)
  g_c = mean_k u_ck - mean_ck u_ck (rule),  d_ck = u_ck - mean_k u_ck (seed),  n = T_null direction
  student s: cos with own teacher / same-config other seeds / other configs / T_null, and
  projections beta_rule = <s, g_c>/|g_c|^2, beta_seed crossed (own d vs other-seed student's d), beta_null = <s, n>/|n|^2.

    python weight_space.py --students E05/student_FF_s1:FF:1:3,... --out OUT.json
    (REL:CFG:SEED:EPOCH; CFG may be '-' for controls such as E06/student_null_s1:-:0:5)
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from safetensors.numpy import load_file

ROOT = Path("/data2/xiangding/skt")
CFGS = ["FF", "FG", "MF", "MG"]


def load_adapter(p):
    d = load_file(str(p / "adapter_model.safetensors"))
    mods = {}
    for k, v in d.items():
        if ".lora_A." in k:
            m = k.split(".lora_A.")[0]
            mods[m] = (d[m + ".lora_B.weight"].astype(np.float64), v.astype(np.float64))
    return mods


def mtype(m):
    return m.split(".")[-1]


def gram(items):
    names = list(items)
    ad = {n: load_adapter(items[n]) for n in names}
    mods = sorted(next(iter(ad.values())))
    types = sorted({mtype(m) for m in mods})
    G = np.zeros((len(names), len(names)))
    GT = {t: np.zeros_like(G) for t in types}
    for m in mods:
        BA = [ad[n][m] for n in names]
        for i in range(len(names)):
            for j in range(i, len(names)):
                v = float(((BA[i][0].T @ BA[j][0]) * (BA[i][1] @ BA[j][1].T)).sum())
                G[i, j] = G[j, i] = G[i, j] + v
                GT[mtype(m)][i, j] += v
                GT[mtype(m)][j, i] = GT[mtype(m)][i, j]
    return names, G, GT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--students", default="")
    ap.add_argument("--extra", default="E06/teacher_ff_s1/ep10,E06/teacher_rand_s1", help="extra adapters to include")
    ap.add_argument("--out")
    a = ap.parse_args()
    items = {f"T_{c}_s{k}": ROOT / f"E03/teacher_{c}_s{k}/ep10" for c in CFGS for k in (1, 2, 3)}
    items["T_null"] = ROOT / "E06/teacher_null_s1/ep10"
    for e in [x for x in a.extra.split(",") if x]:
        p = ROOT / e
        if not (p / "adapter_model.safetensors").exists():
            eps = sorted(p.glob("ep*"), key=lambda q: int(q.name[2:]))
            p = eps[-1] if eps else p
        if (p / "adapter_model.safetensors").exists():
            items[e] = p
    studs = []
    for spec in [x for x in a.students.split(",") if x]:
        rel, c, k, ep = spec.split(":")
        p = ROOT / rel / f"ep{ep}"
        if (p / "adapter_model.safetensors").exists():
            nm = f"{rel}@ep{ep}"; items[nm] = p; studs.append((nm, c, int(k)))
    names, G, GT = gram(items)
    ix = {n: i for i, n in enumerate(names)}
    nrm = np.sqrt(np.diag(G))
    C = G / np.outer(nrm, nrm)

    # linear combinations of items, as coefficient vectors over names
    def vec(**w):
        x = np.zeros(len(names))
        for n, c in w.items():
            x[ix[n]] += c
        return x
    U = {(c, k): vec(**{f"T_{c}_s{k}": 1.0}) for c in CFGS for k in (1, 2, 3)}
    grand = np.mean(list(U.values()), axis=0)
    cm = {c: np.mean([U[(c, k)] for k in (1, 2, 3)], axis=0) for c in CFGS}
    g = {c: cm[c] - grand for c in CFGS}
    d = {(c, k): U[(c, k)] - cm[c] for c in CFGS for k in (1, 2, 3)}
    n = vec(T_null=1.0)
    ip = lambda x, y, M=G: float(x @ M @ y)
    sq = lambda x, M=G: ip(x, x, M)

    print(f"norms: teachers {np.mean([nrm[ix[f'T_{c}_s{k}']] for c in CFGS for k in (1,2,3)]):.3f}  T_null {nrm[ix['T_null']]:.3f}  "
          + "  ".join(f"{nm} {nrm[ix[nm]]:.3f}" for nm in names if not nm.startswith("T_")))
    # teacher geometry
    same = [C[ix[f"T_{c}_s{i}"], ix[f"T_{c}_s{j}"]] for c in CFGS for i in (1, 2, 3) for j in (1, 2, 3) if i < j]
    diff = [C[ix[f"T_{c}_s{i}"], ix[f"T_{o}_s{j}"]] for c in CFGS for o in CFGS if c < o for i in (1, 2, 3) for j in (1, 2, 3)]
    tn = [C[ix[f"T_{c}_s{k}"], ix["T_null"]] for c in CFGS for k in (1, 2, 3)]
    print(f"teacher cos: same config {np.mean(same):.3f} (n={len(same)})  different config {np.mean(diff):.3f}  with T_null {np.mean(tn):.3f}")
    tot = np.mean([sq(U[ck]) for ck in U])
    print(f"teacher energy split: rule |g|^2 {np.mean([sq(g[c]) for c in CFGS]) / tot:.3f}  seed |d|^2 {np.mean([sq(d[ck]) for ck in d]) / tot:.3f}"
          f"  shared |grand|^2 {sq(grand) / tot:.3f}  (fractions of mean |u|^2)")
    for t in GT:
        tt = np.mean([sq(U[ck], GT[t]) for ck in U])
        print(f"  {t:12s} share of teacher energy {tt / tot:.3f}  rule {np.mean([sq(g[c], GT[t]) for c in CFGS]) / max(tt, 1e-30):.3f}"
              f"  seed {np.mean([sq(d[ck], GT[t]) for ck in d]) / max(tt, 1e-30):.3f}  shared {sq(grand, GT[t]) / max(tt, 1e-30):.3f}")

    res = {"names": names, "gram": G.tolist(), "gram_by_type": {t: M.tolist() for t, M in GT.items()}, "students": {}}
    for nm, c, k in studs:
        s = vec(**{nm: 1.0}); r = {}
        r["cos_T_null"] = C[ix[nm], ix["T_null"]]
        if c in CFGS:
            r["cos_own"] = C[ix[nm], ix[f"T_{c}_s{k}"]]
            r["cos_samecfg_other"] = float(np.mean([C[ix[nm], ix[f"T_{c}_s{j}"]] for j in (1, 2, 3) if j != k]))
            r["cos_othercfg"] = float(np.mean([C[ix[nm], ix[f"T_{o}_s{j}"]] for o in CFGS if o != c for j in (1, 2, 3)]))
            r["beta_rule"] = ip(s, g[c]) / sq(g[c])
            r["beta_rule_null"] = float(np.mean([ip(s, g[o]) / sq(g[o]) for o in CFGS if o != c]))
            r["beta_seed_own"] = ip(s, d[(c, k)]) / sq(d[(c, k)])
        r["beta_null"] = ip(s, n) / sq(n)
        r["beta_grand"] = ip(s, grand) / sq(grand)
        res["students"][nm] = r
        print(f"{nm:32s} {c} s{k} | cos own {r.get('cos_own', float('nan')):+.3f} same-cfg-other {r.get('cos_samecfg_other', float('nan')):+.3f}"
              f" other-cfg {r.get('cos_othercfg', float('nan')):+.3f} T_null {r['cos_T_null']:+.3f} | beta rule {r.get('beta_rule', float('nan')):+.4f}"
              f" (null {r.get('beta_rule_null', float('nan')):+.4f}) seed_own {r.get('beta_seed_own', float('nan')):+.4f} shared {r['beta_grand']:+.4f} T_null {r['beta_null']:+.4f}")
    # crossed seed test in weight space
    byc = defaultdict(list)
    for nm, c, k in studs:
        if c in CFGS:
            byc[c].append((nm, k))
    for c, lst in byc.items():
        ks = [k for _, k in lst]
        if len(set(ks)) < 2:
            continue
        diag = [ip(vec(**{nm: 1.0}), d[(c, k)]) / sq(d[(c, k)]) for nm, k in lst]
        off = [ip(vec(**{nm: 1.0}), d[(c, j)]) / sq(d[(c, j)]) for nm, k in lst for j in ks if j != k]
        print(f"CROSSED weight-space {c}: beta_seed own {np.mean(diag):+.4f}  other-student {np.mean(off):+.4f}  diff {np.mean(diag) - np.mean(off):+.4f}")
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
