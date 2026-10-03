"""E61 addendum: anatomical seed identification at early checkpoints (E57: 4-26% of training) vs the final step (E45),
same 6 recipes per size, leave-one-corpus-out."""
import json

import mp_common as mc
from e61_seed_id import identify

PLAN = json.loads((mc.CACHE / "datadecide" / "e45_plan.json").read_text())


def main():
    out = {}
    for size in ("10M", "20M", "60M", "150M", "300M", "750M"):
        recs = PLAN[size]["recipes"][:6]
        fin = PLAN[size]["step"]
        for step in (1250, 2500, 3750, fin):
            src = mc.RESULTS / ("e45" if step == fin else "e57")
            pat = f"{size}__*.json" if step == fin else f"{size}@{step}__*.json"
            M = {tuple(f.stem.split("__")[1:3]): json.loads(f.read_text()) for f in src.glob(pat)}
            M = {k: v for k, v in M.items() if k[0] in recs}
            if len(M) < 18:
                continue
            r = identify(M, ("M1", "M2", "M4"))
            out[f"{size}@{step}"] = {**r, "frac": step / fin}
            print(f"{size:5s} step {step:6d} ({step / fin:6.1%})  accuracy {r['accuracy']:.2f}  (chance {r['chance']:.2f}, n {r['n']})", flush=True)
    (mc.RESULTS / "e61_early.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
