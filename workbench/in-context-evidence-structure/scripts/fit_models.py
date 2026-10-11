"""Which computational model explains the LM's query log-odds best?

usage: fit_models.py DATA_DIR RESULT_GLOB [--out JSON]

Readout y = lo_B (LM log-odds for the reversed-rule label) on every row.
Candidate models (all fitted by least squares on y, 5-fold CV by base):
  set     : a + b * logit P_set(B)        (exchangeable rule learner, eps inferred)
  meta    : a + b * logit P_meta(B)       (joint stochasticity/volatility inference)
  seq     : a + b * logit P_seq(B)        (always-volatile rule learner)
  labelvote_pos: a + sum_t w_t * v_t      (v_t = +1 if demo t carries the query's B label word; per-position weights)
  exemplar: b * [log sum_{y_t = lB} s_t - log sum_{y_t = lA} s_t] + a,
            s_t = exp(-c_r * d_rule - c_d * d_dist + g * pos_t)   (GCM with selective attention;
            label-copy voting, position modulates weight)
  exemplar_rule: exemplar votes defined through the rule attribute (rule-consistent copy)
"""
import argparse, glob, json
import numpy as np
from scipy.optimize import minimize


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def load(data_dir, res_glob):
    sc = {}
    for f in glob.glob(res_glob):
        for l in open(f):
            s = json.loads(l); sc[s["uid"]] = s["lp"]
    R = []
    for l in open(data_dir + "/rows.jsonl"):
        r = json.loads(l)
        if r["uid"] not in sc:
            continue
        lp = sc[r["uid"]]
        lo1 = lp[1] - lp[0]
        b = r["base"]
        R.append(dict(base=r["base_id"], cond=r["cond"], y=lo1 if r["query_label_B"] == 1 else -lo1,
                      X=np.array(b["X"]), xq=np.array(b["xq"]), a=b["rule_attr"],
                      labels=np.array(r["labels"]), lB=r["query_label_B"],
                      set=logit(r["oracle"]["set_pB"]), meta=logit(r["oracle"]["meta_pB"]),
                      seq=logit(r["oracle"]["sequence_pB"])))
    return R


def features(R):
    T = len(R[0]["labels"])
    n = len(R)
    isB = np.zeros((n, T)); drule = np.zeros((n, T)); ddist = np.zeros((n, T)); voteB = np.zeros((n, T))
    for i, r in enumerate(R):
        X, xq, a = r["X"], r["xq"], r["a"]
        drule[i] = (X[:, a] != xq[a]).astype(float)
        mask = np.ones(X.shape[1], bool); mask[a] = False
        ddist[i] = (X[:, mask] != xq[mask]).sum(1)
        voteB[i] = (r["labels"] == r["lB"]).astype(float)       # demo carries the query's B label word
    pos = np.tile(np.arange(T) / (T - 1), (n, 1))
    return dict(drule=drule, ddist=ddist, voteB=voteB, pos=pos)


def exemplar_pred(theta, F):
    cr, cd, g, a, b = theta
    logs = -cr * F["drule"] - cd * F["ddist"] + g * F["pos"]
    s = np.exp(logs - logs.max(1, keepdims=True))
    sB = (s * F["voteB"]).sum(1) + 1e-9; sA = (s * (1 - F["voteB"])).sum(1) + 1e-9
    return a + b * (np.log(sB) - np.log(sA))


def fit_exemplar(F, y, idx, use_pos=True):
    def loss(th):
        if not use_pos:
            th = np.array([th[0], th[1], 0.0, th[2], th[3]])
        p = exemplar_pred(th, {k: v[idx] for k, v in F.items()})
        return np.mean((p - y[idx]) ** 2)
    x0 = [1.0, 0.3, 0.0, 0.0, 1.0] if use_pos else [1.0, 0.3, 0.0, 1.0]
    best = None
    for start in ([x0] + [list(np.array(x0) * s) for s in (0.3, 3.0)]):
        r = minimize(loss, start, method="Nelder-Mead", options=dict(maxiter=4000, xatol=1e-4, fatol=1e-6))
        if best is None or r.fun < best.fun:
            best = r
    th = best.x if use_pos else np.array([best.x[0], best.x[1], 0.0, best.x[2], best.x[3]])
    return th


def linfit(Xm, y, idx):
    A = np.c_[np.ones(len(idx)), Xm[idx]]
    coef, *_ = np.linalg.lstsq(A, y[idx], rcond=None)
    return coef


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("data"); ap.add_argument("res"); ap.add_argument("--out")
    a = ap.parse_args()
    R = load(a.data, a.res)
    y = np.array([r["y"] for r in R]); bases = np.array([r["base"] for r in R])
    F = features(R)
    ub = np.unique(bases); rng = np.random.default_rng(0); rng.shuffle(ub)
    folds = np.array_split(ub, 5)
    preds = {k: np.zeros_like(y) for k in ("set", "meta", "seq", "labelvote_pos", "exemplar", "exemplar_nopos")}
    thetas = []
    for fb in folds:
        te = np.isin(bases, fb); tr = ~te
        tri, tei = np.where(tr)[0], np.where(te)[0]
        for k in ("set", "meta", "seq"):
            x = np.array([r[k] for r in R])[:, None]
            c = linfit(x, y, tri); preds[k][tei] = c[0] + x[tei, 0] * c[1]
        V = 2 * (np.array([r["labels"] == r["lB"] for r in R]).astype(float)) - 1   # +1 if B label
        c = linfit(V, y, tri); preds["labelvote_pos"][tei] = c[0] + V[tei] @ c[1:]
        th = fit_exemplar(F, y, tri, True); thetas.append(th.tolist())
        preds["exemplar"][tei] = exemplar_pred(th, {k: v[tei] for k, v in F.items()})
        th0 = fit_exemplar(F, y, tri, False)
        preds["exemplar_nopos"][tei] = exemplar_pred(th0, {k: v[tei] for k, v in F.items()})
    out = {"n": int(len(y)), "var_y": float(y.var())}
    print(f"rows {len(y)}  var(y) {y.var():.3f}")
    conds = np.array([r["cond"] for r in R])
    for k, p in preds.items():
        r2 = 1 - np.mean((y - p) ** 2) / y.var()
        # condition-mean level fit
        cm = {c: (y[conds == c].mean(), p[conds == c].mean()) for c in np.unique(conds)}
        cy = np.array([v[0] for v in cm.values()]); cp = np.array([v[1] for v in cm.values()])
        r2c = 1 - np.mean((cy - cp) ** 2) / cy.var()
        out[k] = {"cv_r2_rows": float(r2), "cv_r2_condmeans": float(r2c)}
        print(f"  {k:15s} CV R2 rows {r2:+.3f}   condition-means R2 {r2c:+.3f}")
    out["exemplar_theta_folds"] = thetas
    print("  exemplar theta (c_rule, c_dist, g_pos, a, b) per fold:", np.round(np.array(thetas), 3).tolist())
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
