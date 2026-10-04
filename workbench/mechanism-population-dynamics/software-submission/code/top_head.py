"""Top-1 head agreement: in role layers, how often do two models pick the same head as the layer's strongest
induction / previous-token / retrieval head? SI (same init, other data) vs SD (same data, other init) vs chance 1/H."""
import itertools
import json

import numpy as np

import common as mc
from crossing_sizes import SIZES, EXCLUDE

D = mc.RESULTS / "crossing_sizes"


def main():
    out = {}
    for size in SIZES:
        M = {tuple(f.stem.split("__")[1:]): json.loads(f.read_text()) for f in sorted(D.glob(f"{size}__*.json"))
             if (size, *f.stem.split("__")[1:]) not in EXCLUDE}
        if not M:
            continue
        row = {}
        for m in ("M1", "M2", "M4"):
            keys = [k for k in M if m != "M1" or M[k]["M1_max"] > 0.3]
            V = {k: np.array(M[k]["maps"][m]) for k in keys}
            if len(V) < 6:
                continue
            L, H = next(iter(V.values())).shape
            # role layers: the 3 layers with the highest population-mean max score for this role
            lay = np.argsort(-np.mean([v.max(1) for v in V.values()], 0))[:3]
            agree = {"SI": [], "SD": [], "DD": []}
            for a, b in itertools.combinations(keys, 2):
                c = "SI" if a[1] == b[1] else "SD" if a[0] == b[0] else "DD"
                agree[c].append(np.mean([V[a][l].argmax() == V[b][l].argmax() for l in lay]))
            row[m] = {c: float(np.mean(v)) for c, v in agree.items() if v} | {"chance": 1 / H, "n_SI": len(agree["SI"])}
        out[size] = row
        print(size, " | ".join(f"{m} SI {r['SI']:.2f} SD {r.get('SD', float('nan')):.2f} DD {r['DD']:.2f} chance {r['chance']:.2f}"
                              for m, r in row.items()))
    (D / "top1_agreement.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
