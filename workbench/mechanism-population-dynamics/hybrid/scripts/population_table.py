#!/usr/bin/env python3
"""Collect every model x condition R1 result (E194-E215) into one table: per-layer delta (split m2-5 - last m2-5) and
binding (split m3-5 - shuf m3-5). Output: results/population/r1_population.json + a printed summary."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "results"


def from_a(d):  # e195_analyze style: split{m}: {acc: [...]}
    L = d["layers"]; g = lambda q: d[q]["acc"]
    sp = [sum(g(f"split{m}")[i] for m in (2, 3, 4, 5)) / 4 for i in range(len(L))]
    la = [sum(g(f"last{m}")[i] for m in (2, 3, 4, 5)) / 4 for i in range(len(L))]
    s3 = [sum(g(f"split{m}")[i] for m in (3, 4, 5)) / 3 for i in range(len(L))]
    sh = [sum(g(f"shuf{m}")[i] for m in (3, 4, 5)) / 3 for i in range(len(L))]
    return {"layers": L, "delta": [a - b for a, b in zip(sp, la)], "floor": la, "binding": [a - b for a, b in zip(s3, sh)]}


def from_b(d):  # r1_summary style
    L = d["layers"]; a = d["acc"]
    la = [sum(a[f"last{m}"][i] for m in (2, 3, 4, 5)) / 4 for i in range(len(L))]
    return {"layers": L, "delta": d["delta"], "floor": la, "binding": d["binding"]}


def load(p):
    return json.loads((R / p).read_text())


rows = []  # (model, cond, regime, mixer, curve)
def add(model, cond, regime, mixer, curve):
    rows.append({"model": model, "cond": cond, "regime": regime, "mixer": mixer, **curve})

e194 = load("e194/summary.json")["R1"]
for m, name in (("T", "OLMo-3-7B"),):
    add(name, "none", "pretrain", "attention", from_a({"layers": e194["layers"], **e194["curves"][m]}))
for c, d in load("e196/r1_all_conditions.json").items():
    if c == "T_noattn":
        add("OLMo-3-7B", "noattn", "pretrain", "attention", from_a(d))
    else:
        add("OLMo-Hybrid-7B", {"noconv": "conv0", "none_mix": "conv0+mem0"}.get(c, c.replace("nomem", "mem0")), "pretrain", "GDN+conv", from_a(d))
for c, d in load("e198/r1_granite_h.json").items():
    add("Granite-4.0-H-micro", {"noconv": "conv0", "none_mix": "conv0+mem0", "nomem": "mem0"}.get(c, c), "pretrain", "Mamba2+conv", from_a(d))
for c, d in load("e198/r1_qwen35.json").items():
    add("Qwen3.5-4B", {"noconv": "conv0", "none_mix": "conv0+mem0", "nomem": "mem0"}.get(c, c), "pretrain", "GDN+conv", from_a(d))
b195 = load("e195/binding_granite_olmo.json")
add("Granite-4.0-micro", "none", "pretrain", "attention", from_a(b195["GT"]))
add("Falcon-Mamba-7B", "none", "pretrain", "Mamba1+conv", from_a(load("e195/binding_falcon_mamba.json")["FM"]))
e199 = load("e199/r1_ring_linear_vs_ling_base.json")
add("Ring-mini-linear-2.0", "none", "pretrain", "Lightning (no conv)", from_a(e199["RL"]))
add("Ling-mini-base-2.0", "none", "pretrain", "attention", from_a(e199["LB"]))
mix = {"TF": "attention", "DN": "DeltaNet+conv", "GLA": "GLA (no conv)", "GSA": "GSA (no conv)", "HGRN": "HGRN (no conv)", "RET": "RetNet (no conv)"}
for k, d in load("e202_e203/r1_fla_zoo.json").items():
    if k == "HGRN2":
        continue
    base, cond = (k.split("_", 1) + ["none"])[:2]
    add(f"fla-{base}-1.3B", {"noconv": "conv0-2", "noconv_all": "conv_all"}.get(cond, cond), "pretrain", mix[base], from_a(d))
for k, d in load("e209/mb_summary.json").items():
    add("fla-Mamba-1.3B", {"none": "none", "mean05": "conv0-5(mean)", "mean_all": "conv_all(mean)"}[k], "pretrain", "Mamba1+conv", from_b(d))
fh = load("e209/fh3_summary.json"); fh5 = load("e205/r1_falcon_h1.json")
for k, d in fh.items():
    add("Falcon-H1-3B", {"none": "none", "zero": "conv0(zero)", "mean": "conv0", "mean_noattn": "conv0+attn0"}[k], "pretrain", "Mamba2+conv || attention", from_b(d))
for k in ("nomem", "noattn"):
    add("Falcon-H1-3B", {"nomem": "mem0", "noattn": "attn0"}[k], "pretrain", "Mamba2+conv || attention", from_b(fh5[k]))
for k, d in load("e209/q08_summary.json").items():
    add("Qwen3.5-0.8B", {"none": "none", "zero": "conv0(zero)", "mean": "conv0"}[k], "pretrain", "GDN+conv", from_b(d))
for k, d in load("e212/r1_llamba_teacher.json").items():
    if k == "teacher":
        add("Llama-3.2-1B-Instruct", "none", "pretrain", "attention", from_b(d))
    else:
        add("Llamba-1B", {"none": "none", "zero": "conv0(zero)", "mean": "conv0", "nomem": "mem0"}[k], "distill-transplant (identity conv)", "Mamba2+conv", from_b(d))
for k, d in load("e213/r1_m1_teacher.json").items():
    if k == "teacher":
        add("Llama-3.2-3B-Instruct", "none", "pretrain", "attention", from_b(d))
    else:
        add("M1-3B", {"none": "none", "zero": "conv0(zero)", "mean": "conv0", "nomem": "mem0"}[k], "distill-transplant (random conv) + math RL", "Mamba1+conv", from_b(d))
for k, d in load("e214/r1_mil3b.json").items():
    add("Llama3.2-Mamba-3B-distill", {"none": "none", "zero": "conv0(zero)", "mean": "conv0", "nomem": "mem0", "noattn": "attn1", "mean_noattn": "conv0+attn1"}[k],
        "distill-transplant (random conv) + inherited attn L1", "Mamba1+conv / attention", from_b(d))
p215 = R / "e215/r1_jet_teacher.json"
if p215.exists():
    for k, d in json.loads(p215.read_text()).items():
        if k == "teacher":
            add("Qwen2.5-1.5B", "none", "pretrain", "attention", from_b(d))
        else:
            add("Jet-Nemotron-2B", {"none": "none", "zero": "conv0(zero)", "mean": "conv0", "nomem": "mem0"}[k], "learned blocks on teacher MLPs (400B)", "GDN+dynamic conv(V)", from_b(d))

out = R / "population"; out.mkdir(exist_ok=True)
(out / "r1_population.json").write_text(json.dumps(rows))
none = {r["model"]: r for r in rows if r["cond"] == "none"}
print(f"{'model':28s} {'cond':16s} {'regime':12s} L2delta  L2/none  maxdelta@L  halfmaxL  floorL2")
for r in rows:
    L = r["layers"]; i2 = L.index(2); n = none[r["model"]]
    dmax = max(r["delta"][1:len(L) // 2 + 1]); lmax = L[r["delta"].index(dmax)]
    half = next((L[i] for i in range(1, len(L)) if r["delta"][i] >= 0.5 * max(n["delta"][1:len(L) // 2 + 1])), None)
    print(f"{r['model'][:28]:28s} {r['cond'][:16]:16s} {r['regime'][:12]:12s} {r['delta'][i2]:+.2f}   {r['delta'][i2] / max(n['delta'][i2], 1e-6):5.2f}   {dmax:.2f}@L{lmax:<3d}  {str(half):>5s}   {r['floor'][i2]:.2f}")
