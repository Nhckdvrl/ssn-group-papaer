"""warmup_window: does the early window follow the warm-up length or the optimizer state? 
Within-layer agreement (M1 induction where both runs have induction heads, M2 previous-token) between the final
layout of each branch and its parent's final layout, beside the controlled_pretraining values with the default 300-step warm-up."""
import json

import numpy as np

import common as mc
from critical_period import load, sim

OUT = mc.RESULTS / "warmup_window.json"


def agree(R, a, b):
    v = {}
    for m in ("M1", "M2"):
        fa, fb = R[a][10000], R[b][10000]
        if m == "M1" and (fa["M1_max"] <= 0.3 or fb["M1_max"] <= 0.3):
            continue
        v[m] = round(sim(fa, fb, m)[1], 3)
    return v


def main():
    R = load()
    out = {"parents": {}, "warm1000": {}, "warm300": {}, "reset_opt": {}}
    for i in (1, 2):
        p, pc, p300 = f"S_i{i}_c4_o{i}_w1000", f"S_i{i}_c4_o{i}_b2000_w1000", f"S_i{i}_c4_o{i}"
        out["parents"][i] = {"parent_vs_continuation": agree(R, p, pc), "w1000_vs_w300_same_init": agree(R, p, p300)}
        for k in (100, 250, 500, 1000, 2000):
            for kind, name in (("noise", f"S_i{i}_c4_o{i}_b{k}_eps1_w1000"), ("code", f"S_i{i}_c4_o{i}_b{k}_tocode_too{k + i * 1000}_w1000")):
                if name in R:
                    out["warm1000"].setdefault(kind, {}).setdefault(k, {})[i] = agree(R, p, name)
            n300 = f"S_i{i}_c4_o{i}_b{k}_eps1"
            if n300 in R:
                out["warm300"].setdefault("noise", {}).setdefault(k, {})[i] = agree(R, p300, n300)
            ro = f"S_i{i}_c4_o{i}_b{k}_eps1_ro"
            if ro in R:
                out["reset_opt"].setdefault(k, {})[i] = agree(R, p300, ro)
    # the learning applied before the intervention: cumulative learning rate (in units of the peak rate)
    from controlled_pretraining import lr_at
    cum = lambda k, w: sum(lr_at(s, 1e-3, w) for s in range(k)) / 1e-3
    mean = lambda v: float(np.mean([np.mean(list(x.values())) for x in v.values()]))
    out["by_cumulative_lr"] = sorted([[cum(int(k), w), w, int(k), mean(v)] for w, sec in ((300, out["warm300"]["noise"]),
                                      (1000, out["warm1000"]["noise"])) for k, v in sec.items()])
    for sec in ("parents", "warm1000", "warm300", "reset_opt", "by_cumulative_lr"):
        print(sec, json.dumps(out[sec]))
    OUT.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
