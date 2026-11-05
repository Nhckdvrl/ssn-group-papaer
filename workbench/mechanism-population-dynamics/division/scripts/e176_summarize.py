#!/usr/bin/env python3
"""E176 summary: three levels per readout (model / class / expert), reproducibility indices as fixed in the card,
per-seed qualitative verdicts on the paper's sentence (k/9), natural-stream check.

  model level : R_m = range over the 6 init runs / |init mean - step-0 mean|
  class/expert: q = (rho_init - rho_floor) / (rho_rerun - rho_floor)

-> results/e176/summary.json, results/e176/summary_table.md
"""
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

WB = Path(__file__).resolve().parents[1]
OUT = WB / "results/e176"
D = json.loads((OUT / "runs.json").read_text())
PR = json.loads((OUT / "pairs.json").read_text())
NAT = json.loads((OUT / "natural.json").read_text()) if (OUT / "natural.json").exists() else None
A172 = json.loads((WB / "results/e172/antoine_3200000000.json").read_text())
T, TS = D["T"], str(D["T_SAT"])
INITS = [f"I{i}D0" for i in range(6)]
RUNS9 = INITS + ["I0D1", "I1D1", "I4D0R"]
R = D["runs"]
at = lambda r: R[f"{r}@{T}"]
a0 = lambda r: R[f"{r}@0"]
U = 8 / 64


def lm(x):
    return float(np.mean(x))


# ---------------- model level ----------------


def model_row(name, f_T, f_0, runs_T=None, floor_runs=None):
    vT = {r: f_T(r) for r in RUNS9}
    v0 = {r: f_0(r) for r in (floor_runs or INITS)} if f_0 else {}
    ini = np.array([vT[r] for r in INITS])
    row = {"name": name, "values": vT, "floor_values": v0, "init_mean": float(ini.mean()), "init_range": float(np.ptp(ini)),
           "rerun_absdiff": abs(vT["I4D0"] - vT["I4D0R"]),
           "order_absdiff": [abs(vT["I0D0"] - vT["I0D1"]), abs(vT["I1D0"] - vT["I1D1"])]}
    if v0:
        f = np.array(list(v0.values()))
        row["floor_mean"], row["floor_range"] = float(f.mean()), float(np.ptp(f))
        gap = abs(row["init_mean"] - row["floor_mean"])
        row["train_gap"] = gap
        row["R_m"] = row["init_range"] / gap if gap > 0 else np.inf
        if gap < row["floor_range"]:
            row["verdict"] = "训练不改变此量"
        else:
            row["verdict"] = "重现" if row["R_m"] <= .25 else ("部分" if row["R_m"] <= 1 else "不重现")
    else:
        row["verdict"] = "无地板（只报原值）"
    return row


models = {
    "1": model_row("router saturation sat(50M→T), k=8, mean over layers", lambda r: lm(at(r)["sat_k8"][TS]), lambda r: lm(at(r)["sat_k8"]["0"])),
    "1k1": model_row("router saturation sat(50M→T), k=1, mean over layers", lambda r: lm(at(r)["sat_k1"][TS]), lambda r: lm(at(r)["sat_k1"]["0"])),
    "2": model_row("share of ordered expert pairs with co-activation ≥ .5", lambda r: lm(at(r)["coact_strong_frac"]), lambda r: lm(a0(r)["coact_strong_frac"])),
    "3": model_row("expert mean of max genre lift", lambda r: lm(at(r)["genre_liftmax_mean"]), lambda r: lm(a0(r)["genre_liftmax_mean"])),
    "6": model_row("UPOS-class top-1 routing entropy / ln64 (token-weighted)", lambda r: lm(at(r)["ent_k1_wmean_norm"]), lambda r: lm(a0(r)["ent_k1_wmean_norm"])),
    "7": model_row("word-form purity (top-1)", lambda r: lm(at(r)["purity"]), lambda r: lm(a0(r)["purity"])),
    "7t": model_row("within-run top-10 form table Jaccard, 400M vs T", lambda r: lm(at(r)["top10_warm_jacc"]), None),
    "13spec": model_row("DBES S_spec", lambda r: at(r)["dbes"]["S_spec"], lambda r: a0(r)["dbes"]["S_spec"]),
    "13reff": model_row("DBES R_eff", lambda r: at(r)["dbes"]["R_eff"], lambda r: a0(r)["dbes"]["R_eff"]),
    "13iso": model_row("DBES S_iso", lambda r: at(r)["dbes"]["S_iso"], lambda r: a0(r)["dbes"]["S_iso"]),
}
# #8 from E172 (floor = 2 step-0 runs only)
A = A172["models"]
models["8"] = model_row("Antoine Spec_POS, mean over layers (E172)", lambda r: lm(A[f"{r}@{T}"]["model_spec"]),
                        lambda r: lm(A[f"{r}@0"]["model_spec"]), floor_runs=["I0D0", "I1D0"])


# ---------------- class level ----------------
def sp(a, b):
    a, b = np.asarray(a, float).ravel(), np.asarray(b, float).ravel()
    m = np.isfinite(a) & np.isfinite(b)
    return float(spearmanr(a[m], b[m])[0])


def class_row(name, prof_T, prof_0, per_layer=True):
    def rho(pa, pb):
        if per_layer:
            return float(np.nanmean([sp(x, y) for x, y in zip(pa, pb)]))
        return sp(pa, pb)
    init = [rho(prof_T(a), prof_T(b)) for a, b in itertools.combinations(INITS, 2)]
    floor = [rho(prof_0(a), prof_0(b)) for a, b in itertools.combinations(INITS, 2)]
    rerun = rho(prof_T("I4D0"), prof_T("I4D0R"))
    order = [rho(prof_T("I0D0"), prof_T("I0D1")), rho(prof_T("I1D0"), prof_T("I1D1"))]
    return qrow(name, init, floor, rerun, order)


def qrow(name, init, floor, rerun, order):
    ri, rf = float(np.mean(init)), float(np.mean(floor))
    row = {"name": name, "init": init, "floor": floor, "rerun": rerun, "order": order, "rho_init": ri, "rho_floor": rf,
           "init_range": [float(min(init)), float(max(init))]}
    den = rerun - rf
    if rerun < .5:
        row["verdict"] = "重跑也低于 .5（读数本身噪声大）"
        row["q"] = (ri - rf) / den if den != 0 else np.nan
    elif den < .1:
        row["verdict"] = "地板≈上限，此级不可判"
        row["q"] = np.nan
    else:
        q = (ri - rf) / den
        row["q"] = q
        row["verdict"] = "重现" if (q >= .7 and ri >= .5) else ("不重现" if q < .3 else "部分")
    return row


classes = {
    "1": class_row("per-UPOS saturation at 50M (floor: at step 0)", lambda r: at(r)["sat_upos"][TS], lambda r: at(r)["sat_upos"]["0"]),
    "3": class_row("per-(layer, genre) routing deviation (60 values)", lambda r: at(r)["genre_dev"], lambda r: a0(r)["genre_dev"], per_layer=False),
    "6": class_row("per-UPOS top-1 routing entropy", lambda r: at(r)["ent_k1"], lambda r: a0(r)["ent_k1"]),
    "7": class_row("per-word-form purity (1,827 forms)", lambda r: at(r)["purity_form"], lambda r: a0(r)["purity_form"]),
    "13spec": class_row("DBES S_spec per genre (5)", lambda r: list(at(r)["dbes"]["S_spec_genre"].values()),
                        lambda r: list(a0(r)["dbes"]["S_spec_genre"].values()), per_layer=False),
    "13iso": class_row("DBES 1−cos per genre pair (10)", lambda r: list(at(r)["dbes"]["iso_pair"].values()),
                       lambda r: list(a0(r)["dbes"]["iso_pair"].values()), per_layer=False),
}
st = A172["stability"]
classes["8"] = qrow("Antoine Spec_POS profile (E172; floor = 1 step-0 pair)",
                    [float(np.mean(x)) for x in [st["init"]["spearman_by_layer"]]] * 1, [float(np.mean(st["floor"]["spearman_by_layer"]))],
                    float(np.mean(st["rerun"]["spearman_by_layer"])), [float(np.mean(st["order"]["spearman_by_layer"]))])
classes["8"]["note"] = "E172 stores the init mean by layer, not per pair; deep (L6–11) init mean = %.3f" % st["init"]["spearman_deep_mean"]
classes["8"]["init_range_deep"] = [min(st["init"]["spearman_deep_per_pair"]), max(st["init"]["spearman_deep_per_pair"])]


# ---------------- expert level ----------------
def ex_row(name, key, floor_kind="floor"):
    g = lambda kind: [lm(p[key]) for p in PR if p["kind"] == kind]
    return qrow(name, g("init"), g(floor_kind), g("rerun")[0], g("order"))


experts = {
    "1": ex_row("per-expert saturation (50M→T); floor: 0→T", "sat_expert", "sat_floor"),
    "2": ex_row("matched co-activation matrix (off-diagonal), Spearman", "coact"),
    "3": ex_row("matched per-expert genre lift (5), Pearson", "genre_lift"),
    "6": ex_row("matched P(e|c) per UPOS class, mean Pearson", "class_dist"),
    "7": ex_row("matched top-10 word-form table, Jaccard", "top10_jacc"),
    "8": ex_row("matched per-expert KL(P(c|e)||P(c)), Pearson", "pos_kl"),
}
overlap = {k: float(np.mean([lm(p["matched_overlap"]) for p in PR if p["kind"] == k])) for k in ("init", "order", "rerun", "floor")}


# ---------------- per-seed verdicts on the paper's sentence ----------------
def verdict(name, f, f0=None):
    v = {r: bool(f(r)) for r in RUNS9}
    out = {"claim": name, "per_run": v, "k_of_9": int(sum(v.values()))}
    if f0 is not None:   # POST-HOC: the same rule applied to the untrained step-0 models
        v0 = {r: bool(f0(r)) for r in INITS}
        out["step0_per_run"], out["step0_k_of_6"] = v0, int(sum(v0.values()))
    return out


verdicts = {
    "1a": verdict("OLMoE: at ~1% of training, up to ~60% of top-8 routing saturated (layer max ≥ .5 at 50M)", lambda r: max(at(r)["sat_k8"][TS]) >= .5),
    "1b": verdict("OLMoE: top-1 saturates slower than top-8 (raw layer means at 50M)", lambda r: lm(at(r)["sat_k1"][TS]) < lm(at(r)["sat_k8"][TS])),
    "1c": verdict("OLMoE: later layers saturate earlier (Spearman(layer, sat) > 0 over L1–L11)", lambda r: spearmanr(range(1, 12), at(r)["sat_k8"][TS][1:])[0] > 0),
    "1d": verdict("OLMoE: layer 0 saturates slowest (sat_L0 < min L1–L11)", lambda r: at(r)["sat_k8"][TS][0] < min(at(r)["sat_k8"][TS][1:])),
    "2": verdict("OLMoE: no strong co-activation, few exceptions (every layer ≤ 1% ordered pairs ≥ .5)", lambda r: max(at(r)["coact_strong_frac"]) <= .01,
                 lambda r: max(a0(r)["coact_strong_frac"]) <= .01),
    "3": verdict("OLMoE/Mixtral: domain specialisation present (some (E, genre) lift ≥ 2)", lambda r: max(at(r)["genre_lift_max"]) >= 2,
                 lambda r: max(a0(r)["genre_lift_max"]) >= 2),
    "6": verdict("ST-MoE: decoder experts don't specialise (class entropy / ln64 ≥ .9)", lambda r: lm(at(r)["ent_k1_wmean_norm"]) >= .9,
                 lambda r: lm(a0(r)["ent_k1_wmean_norm"]) >= .9),
    "7a": verdict("BASE/OpenMoE: input token decides the expert (form purity ≥ .5)", lambda r: lm(at(r)["purity"]) >= .5,
                 lambda r: lm(a0(r)["purity"]) >= .5),
    "7b": verdict("OpenMoE: routing fixed by end of warmup (top-10 Jaccard 400M vs T ≥ .5)", lambda r: lm(at(r)["top10_warm_jacc"]) >= .5),
    "8": verdict("Antoine: Spec_POS above uniform by ≥ 25 pp (POST-HOC threshold = lower end of the paper's range)",
                 lambda r: (lm(A[f"{r}@{T}"]["model_spec"]) - U) * 100 >= 25),
    "13": verdict("DBES: modular (S_iso ≥ .5; threshold from DBES table 1 range)", lambda r: at(r)["dbes"]["S_iso"] >= .5,
                 lambda r: a0(r)["dbes"]["S_iso"] >= .5),
}

# ---------------- natural stream ----------------
nat = None
if NAT:
    NR = NAT["runs"]
    nk = {r: k for k in NR for r in [k.split("@")[0]] if not k.endswith("@0")}
    ninit = ["I0D0", "I1D0", "I2D0", "I3D0", "I4D0"]
    nT = lambda r: NR[nk[r]]
    n0 = lambda r: NR[f"{r}@0"]
    def nmodel(name, f):
        vT = {r: f(nT(r)) for r in nk}
        v0 = {r: f(n0(r)) for r in ("I0D0", "I1D0")}
        ini = np.array([vT[r] for r in ninit])
        gap = abs(ini.mean() - np.mean(list(v0.values())))
        return {"name": name, "values": vT, "floor_values": v0, "init_range": float(np.ptp(ini)), "rerun_absdiff": abs(vT["I4D0"] - vT["I4D0R"]),
                "train_gap": float(gap), "R_m": float(np.ptp(ini) / gap) if gap else np.inf,
                "anchor_init_mean": None}
    def nclass(name, f, per_layer):
        rho = (lambda a, b: float(np.nanmean([sp(x, y) for x, y in zip(a, b)]))) if per_layer else sp
        init = [rho(f(nT(a)), f(nT(b))) for a, b in itertools.combinations(ninit, 2)]
        return qrow(name, init, [rho(f(n0("I0D0")), f(n0("I1D0")))], rho(f(nT("I4D0")), f(nT("I4D0R"))),
                    [rho(f(nT("I0D0")), f(nT("I0D1"))), rho(f(nT("I1D0")), f(nT("I1D1")))])
    nat = {"verify": {k: {"top8_set_agree_min": min(v.get("verify_top8_set_agree", [np.nan])), "top1_agree_min": min(v.get("verify_top1_agree", [np.nan]))}
                      for k, v in NR.items()},
           "model": {"2": nmodel("co-activation ≥ .5 share", lambda z: lm(z["coact_strong_frac"])),
                     "3": nmodel("expert mean of max genre lift", lambda z: lm(z["genre_liftmax_mean"])),
                     "7": nmodel("word-form purity", lambda z: lm(z["purity"])),
                     "13spec": nmodel("S_spec", lambda z: z["dbes"]["S_spec"]), "13reff": nmodel("R_eff", lambda z: z["dbes"]["R_eff"]),
                     "13iso": nmodel("S_iso", lambda z: z["dbes"]["S_iso"])},
           "class": {"3": nclass("per-(layer, genre) deviation", lambda z: z["genre_dev"], False),
                     "7": nclass("per-form purity", lambda z: z["purity_form"], True),
                     "13spec": nclass("S_spec per genre", lambda z: list(z["dbes"]["S_spec_genre"].values()), False),
                     "13iso": nclass("1−cos per genre pair", lambda z: list(z["dbes"]["iso_pair"].values()), False)},
           "verdicts": {"2": {r: max(nT(r)["coact_strong_frac"]) <= .01 for r in nk}, "3": {r: max(nT(r)["genre_lift_max"]) >= 2 for r in nk},
                        "7a": {r: lm(nT(r)["purity"]) >= .5 for r in nk}, "13": {r: nT(r)["dbes"]["S_iso"] >= .5 for r in nk}},
           "note": "init = I0–I3 at 4.0B + I4D0 at 3.2B (I5D0 has no hidden cache); floor = 1 step-0 pair (I0D0, I1D0)"}

# ---------------- POST-HOC descriptive (added after the first look; not part of the fixed readouts) ----------------
posthoc = {}
for r in RUNS9:
    z = at(r)["sat_k8"]
    first = [t for t in D["SAT_T"] if max(z[str(t)]) >= .5]
    posthoc[r] = {"first_ckpt_layermax_sat_ge_.5": first[0] if first else None,
                  "sat_k8_layermax_at_1.6B": max(z["1600000000"]), "sat_k8_by_layer_at_50M": z[TS],
                  "sat_k8_by_layer_at_0": z["0"]}
summary_posthoc = {"saturation": posthoc,
                   "entropy_floor_values": models["6"]["floor_values"], "S_iso_floor_values": models["13iso"]["floor_values"]}

summary = {"posthoc": summary_posthoc, "model": models, "class": classes, "expert": experts, "matched_overlap": overlap, "verdicts": verdicts, "natural": nat}
(OUT / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False, default=float))

# ---------------- markdown table ----------------
f3 = lambda x: "—" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.3f}"
L = ["## 模型级（每 run 一个数；主数据 = 锚点 S，3.2B，12 层平均）", "",
     "| # | 读数 | 6 个 init 的范围 | 重跑差 | 换顺序差 | step 0 | R_m | 判定 |", "|---|---|---|---|---|---|---|---|"]
for k, m in models.items():
    ini = [m["values"][r] for r in INITS]
    L.append(f"| {k} | {m['name']} | {min(ini):.3f}–{max(ini):.3f} | {m['rerun_absdiff']:.3f} | {max(m['order_absdiff']):.3f} | "
             f"{f3(m.get('floor_mean'))} | {f3(m.get('R_m'))} | {m['verdict']} |")
L += ["", "## 类别级（与专家编号无关的剖面；跨 run Spearman）", "",
      "| # | 剖面 | ρ_init 均值（范围） | ρ_重跑 | ρ_换顺序 | ρ_step0 | q | 判定 |", "|---|---|---|---|---|---|---|---|"]
for k, c in classes.items():
    rg = c.get("init_range_deep", c["init_range"])
    L.append(f"| {k} | {c['name']} | {c['rho_init']:.3f}（{'深层 ' if 'init_range_deep' in c else ''}{rg[0]:.2f}–{rg[1]:.2f}） | {c['rerun']:.3f} | "
             f"{', '.join(f'{x:.2f}' for x in c['order'])} | {c['rho_floor']:.3f} | {f3(c['q'])} | {c['verdict']} |")
L += ["", "## 专家级（Hungarian 配对后；按文档对半交叉拟合）", "",
      "| # | 读数 | ρ_init 均值（范围） | ρ_重跑 | ρ_换顺序 | ρ_step0 | q | 判定 |", "|---|---|---|---|---|---|---|---|"]
for k, c in experts.items():
    L.append(f"| {k} | {c['name']} | {c['rho_init']:.3f}（{c['init_range'][0]:.2f}–{c['init_range'][1]:.2f}） | {c['rerun']:.3f} | "
             f"{', '.join(f'{x:.2f}' for x in c['order'])} | {c['rho_floor']:.3f} | {f3(c['q'])} | {c['verdict']} |")
L.append(f"\n配对后 top-8 槽位重合（层平均）：init {overlap['init']:.3f}，换顺序 {overlap['order']:.3f}，重跑 {overlap['rerun']:.3f}，step 0 {overlap['floor']:.3f}")
L += ["", "## 原文那句结论：9 个 run 逐个判定（末列 POST-HOC：同一规则用在 6 个未训练 step-0 模型上）", "",
      "| # | 结论（判定规则） | 几/9 | 判否的 run | step 0 几/6 |", "|---|---|---|---|---|"]
for k, v in verdicts.items():
    neg = [r for r, x in v["per_run"].items() if not x]
    L.append(f"| {k} | {v['claim']} | {v['k_of_9']}/9 | {', '.join(neg) if 0 < len(neg) < 9 else ('—' if not neg else '全部')} | "
             f"{str(v['step0_k_of_6']) + '/6' if 'step0_k_of_6' in v else '—'} |")
if nat:
    L += ["", "## 自然流复核（113,118 个连续词；init = I0–I4，floor = 1 对）", "",
          f"重算路由与缓存在锚点上的一致（层最小）：" + "；".join(f"{k} top8 {v['top8_set_agree_min']:.4f} / top1 {v['top1_agree_min']:.4f}" for k, v in nat["verify"].items()), "",
          "| # | 模型级读数 | init 范围 | 重跑差 | step 0 | R_m |", "|---|---|---|---|---|---|"]
    for k, m in nat["model"].items():
        ini = [m["values"][r] for r in ["I0D0", "I1D0", "I2D0", "I3D0", "I4D0"]]
        L.append(f"| {k} | {m['name']} | {min(ini):.3f}–{max(ini):.3f} | {m['rerun_absdiff']:.3f} | {np.mean(list(m['floor_values'].values())):.3f} | {m['R_m']:.3f} |")
    L += ["", "| # | 类别级剖面 | ρ_init（范围） | ρ_重跑 | ρ_step0 | q | 判定 |", "|---|---|---|---|---|---|---|"]
    for k, c in nat["class"].items():
        L.append(f"| {k} | {c['name']} | {c['rho_init']:.3f}（{c['init_range'][0]:.2f}–{c['init_range'][1]:.2f}） | {c['rerun']:.3f} | {c['rho_floor']:.3f} | {f3(c['q'])} | {c['verdict']} |")
    L.append("\n自然流逐 run 定性判定（8 个 run）：" + "；".join(f"#{k} {sum(v.values())}/{len(v)}" for k, v in nat["verdicts"].items()))
L += ["", "## POST-HOC（看过第一版后加的描述，不进判定）", ""]
for r, v in posthoc.items():
    L.append(f"- {r}: 层最大 k=8 饱和首次 ≥ .5 的 checkpoint = {v['first_ckpt_layermax_sat_ge_.5']}；1.6B 处层最大 = {v['sat_k8_layermax_at_1.6B']:.3f}；"
             f"50M 处 L0 = {v['sat_k8_by_layer_at_50M'][0]:.3f}（step 0 处 L0 = {v['sat_k8_by_layer_at_0'][0]:.3f}）")
(OUT / "summary_table.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
