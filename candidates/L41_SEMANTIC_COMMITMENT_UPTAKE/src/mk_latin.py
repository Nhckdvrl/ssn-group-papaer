"""Build the E01-B Latin-square assignment manifest.

256 fresh critical proposition identities (pool `crit`) x 4 assignments, so that
every identity appears exactly once in each of M+, M-, F+, F- across four
independent resets from the same base checkpoint.

Each critical run additionally carries a fixed block of direct-control
propositions (pool `pilot`), half `A+ : p` and half `A- : not p`, identical in
every run.  They give a WITHIN-RUN estimate of D, so the normalised semantic
fidelity F_sem = I / (2D) is computed against a control measured under exactly
the same drift, optimiser state and exposure as the critical cells.  They are
balanced across all four critical cells and therefore cannot generate the
verb x polarity interaction.
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(__file__))
from generator import generate, CRITICAL
from collections import Counter

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n_crit", type=int, default=256)
    ap.add_argument("--n_ctrl", type=int, default=64)
    ap.add_argument("--outdir", default="frozen/assign")
    a = ap.parse_args()

    crit = generate("crit", a.n_crit)
    ctrl = generate("pilot", a.n_ctrl)
    os.makedirs(a.outdir, exist_ok=True)
    manifest = {"n_crit": a.n_crit, "n_ctrl": a.n_ctrl, "assignments": {}}
    for j in range(4):
        d = {p["pid"]: CRITICAL[(i + j) % 4] for i, p in enumerate(crit)}
        d.update({p["pid"]: ("Ap" if i % 2 == 0 else "An") for i, p in enumerate(ctrl)})
        path = f"{a.outdir}/critical_L{j}.json"
        json.dump(d, open(path, "w"), indent=0)
        manifest["assignments"][f"L{j}"] = {"path": path, "counts": dict(Counter(d.values()))}
        print(path, dict(Counter(d.values())))

    # verify the Latin-square property
    seen = {p["pid"]: [] for p in crit}
    for j in range(4):
        d = json.load(open(f"{a.outdir}/critical_L{j}.json"))
        for p in crit:
            seen[p["pid"]].append(d[p["pid"]])
    ok = all(sorted(v) == sorted(CRITICAL) for v in seen.values())
    print("Latin-square property (each identity once per cell across L0..L3):", ok)
    manifest["latin_square_valid"] = ok
    json.dump(manifest, open(f"{a.outdir}/manifest.json", "w"), indent=1)

main()
