"""Audit (P12): published step0 of every 1B DataDecide run (25 recipes x 3 seeds) vs the c4 step0 of the same seed,
one tensor per checkpoint by HTTP range request. Ground truth for the layout-based birth-certificate test (Fig 1)."""
import glob
import json

import mp_common as mc
from audit_init_start2 import SEEDS, c, tensor


def main():
    recs = sorted({f.split("/")[-1].split("-1B__")[0] for f in glob.glob(str(mc.RESULTS / "e35" / "*-1B__*.json")) if "step" not in f})
    S0 = {s: tensor("c4", 0, s) for s in SEEDS}
    out = {}
    for r in recs:
        for s in SEEDS:
            z = tensor(r, 0, s)
            out[f"{r}|{s}"] = {s0: c(z, S0[s0]) for s0 in SEEDS}
            print(r, s, out[f"{r}|{s}"], flush=True)
    (mc.RESULTS / "audit_step0_1b.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
