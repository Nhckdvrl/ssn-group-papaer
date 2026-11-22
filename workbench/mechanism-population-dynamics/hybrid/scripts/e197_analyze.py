#!/usr/bin/env python3
"""E197 analysis: event at the first full-attention layer for M1 (SoftCKA), M1 - M1mis, M2 (retrieval), M3 (PC1).
Usage: e197_analyze.py OUT_JSON KEY=RESULT_JSON[@FIRST_ATTN_LAYER] ...   (dense models: give their partner's layer)
"""
import json
import sys

import numpy as np

MAIN = ["fr", "de", "es", "zh", "ja", "ar", "ko"]


def first_attn(lt):
    for i, t in enumerate(lt or []):
        if t in ("full_attention", "attention", "*"):
            return i
    return None


def event(curve, a, lo=0, hi=8):
    """curve indexed by capture index (0 = embedding); change across decoder layer l = c[l+1] - c[l]."""
    d = {l: curve[l + 1] - curve[l] for l in range(lo, hi + 1)}
    others = [abs(v) for l, v in d.items() if l != a]
    med = float(np.median(others))
    return {"delta_a": d[a], "median_abs_other": med, "ratio": abs(d[a]) / max(med, 1e-9),
            "is_max": abs(d[a]) >= max(others), "event": abs(d[a]) >= 2 * med and abs(d[a]) >= max(others)}


def main():
    out = {}
    for arg in sys.argv[2:]:
        key, rest = arg.split("=", 1)
        path, a = (rest.split("@") + [None])[:2]
        R = json.load(open(path))
        lt = R["layer_types"]
        a = int(a) if a is not None else first_attn(lt)
        m1 = np.mean([np.array(R["M1"][lg])[:, 1] for lg in MAIN], 0)  # sigma x1
        m1s = {s: np.mean([np.array(R["M1"][lg])[:, k] for lg in MAIN], 0) for k, s in enumerate(R["sigma_mult"])}
        mis = np.mean([np.array(R["M1mis"][lg])[:, 1] for lg in MAIN], 0)
        m2 = np.mean([np.array(R["M2"][lg]) for lg in MAIN], 0)
        m3 = np.array(R["M3_pc1"])
        diff = m1 - mis
        e = {"first_attn": a, "M1": event(m1, a), "M1_minus_mis": event(diff, a), "M2": event(m2, a), "M3": event(m3, a),
             "M1_sigma": {str(s): event(v, a) for s, v in m1s.items()}}
        e["share_parallel_specific"] = e["M1_minus_mis"]["delta_a"] / e["M1"]["delta_a"] if e["M1"]["delta_a"] else None
        if not e["M1"]["event"]:
            e["outcome"] = "no-replication"
        elif (e["share_parallel_specific"] is not None and e["share_parallel_specific"] >= .5) and e["M2"]["event"]:
            e["outcome"] = "cross-lingual event"
        else:
            e["outcome"] = "geometric event"
        e["curves"] = {"M1": m1.round(4).tolist(), "M1mis": mis.round(4).tolist(), "M2": m2.round(4).tolist(), "M3": m3.round(4).tolist()}
        out[key] = e
        print(f"{key:4s} a={a} outcome={e['outcome']:20s} dM1={e['M1']['delta_a']:+.3f} (x{e['M1']['ratio']:.1f})"
              f"  d(M1-mis)={e['M1_minus_mis']['delta_a']:+.3f} share={e['share_parallel_specific'] if e['share_parallel_specific'] is None else round(e['share_parallel_specific'],2)}"
              f"  dM2={e['M2']['delta_a']:+.3f} (x{e['M2']['ratio']:.1f})  dPC1={e['M3']['delta_a']:+.3f} (x{e['M3']['ratio']:.1f})")
        print("      M1 :", " ".join(f"{x:.2f}" for x in m1[:12]), "| mis:", " ".join(f"{x:.2f}" for x in mis[:12]))
        print("      M2 :", " ".join(f"{x:.2f}" for x in m2[:12]), "| PC1:", " ".join(f"{x:.2f}" for x in m3[:12]))
    json.dump(out, open(sys.argv[1], "w"), default=lambda o: o.item() if hasattr(o, "item") else str(o))


if __name__ == "__main__":
    main()
