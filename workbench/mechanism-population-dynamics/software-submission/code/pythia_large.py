"""pythia_large analysis: Pythia std vs deduped (same init) at 70M-12B. Within-layer Spearman per role vs a permutation null
(heads shuffled independently within each layer, 2000 draws); top-1 head agreement in role layers vs chance 1/H."""
import json

import numpy as np

import common as mc
from similarity import within_matrix

SIZES = ("70m", "160m", "410m", "1b", "1.4b", "6.9b", "12b")  # 2.8b excluded: HF std and deduped finals are near-identical weights (see paper, Appendix A)


def load(size, tag, step=None):
    for d in ("pythia_small", "pythia_large"):
        f = mc.RESULTS / d / (f"pythia-{size}-{tag}.json" if step is None else f"pythia-{size}-{tag}@{step}.json")
        if f.exists():
            return json.loads(f.read_text())
    return None


def compare(A, B, rng):
    row = {}
    for m in ("M1", "M2", "M4"):
        if m == "M1" and (A["M1_max"] <= 0.3 or B["M1_max"] <= 0.3):
            continue
        a, b = np.array(A["maps"][m]), np.array(B["maps"][m])
        obs = within_matrix([a, b])[0, 1]
        null = []
        for _ in range(2000):
            bp = np.stack([rng.permutation(r) for r in b])
            null.append(within_matrix([a, bp])[0, 1])
        lay = np.argsort(-(a.max(1) + b.max(1)))[:3]
        top1 = float(np.mean([a[l].argmax() == b[l].argmax() for l in lay]))
        row[m] = {"within": float(obs), "null_p95": float(np.percentile(null, 95)), "p": float(np.mean(np.array(null) >= obs)),
                  "top1_role_layers": top1, "chance": 1 / a.shape[1]}
    return row


def main():
    rng = np.random.default_rng(0)
    out = {}
    for s in SIZES:
        A, B = load(s, "std"), load(s, "deduped")
        if A and B:
            out[s] = compare(A, B, rng)
            print(s, {m: f"{v['within']:.2f} (null95 {v['null_p95']:.2f}, top1 {v['top1_role_layers']:.2f} vs {v['chance']:.2f})" for m, v in out[s].items()}, flush=True)
    A, B = load("12b", "std", 3000), load("12b", "deduped", 3000)
    if A and B:
        out["12b@3000"] = compare(A, B, rng)
        F = load("12b", "std")
        if F:
            out["12b@3000"]["to_own_final"] = {m: float(within_matrix([A["maps"][m], F["maps"][m]])[0, 1]) for m in ("M1", "M2", "M4")}
        print("12b@3000", out["12b@3000"], flush=True)
    (mc.RESULTS / "pythia_large_analysis.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
