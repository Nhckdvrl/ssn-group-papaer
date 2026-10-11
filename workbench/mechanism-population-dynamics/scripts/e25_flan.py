"""E25: held-out-seed test of the Flan effect (Coherent vs Substitution). Protocol: experiments/E25-*.md. CPU only."""
import itertools
import json

import numpy as np

import dd_common as dd
import mp_common as mc

E20 = mc.RESULTS / "e20"
AUX = ["large-aux-2", "large-aux-3"]


def load(name, seed):
    return json.loads((E20 / f"{name}__{seed}.json").read_text())


def shared_items(models):
    """category -> items known by every model in `models` [(name, seed)]."""
    ds = [load(*m) for m in models]
    return {cat: set.intersection(*[set(d["known_items"][cat]) for d in ds]) for cat in ds[0]["known_items"]}


def summ_shared(name, seed, items):
    """Primary readout (amendment 1): margins averaged over a fixed shared-known item set."""
    c = load(name, seed)["conditions"]
    m = lambda form: np.mean([np.mean([c[f"{cat}|{form}"]["margin_all_items"][str(i)] for i in its])
                              for cat, its in items.items() if len(its) >= 10])
    return m("Coherent Conflict"), m("Substitution Conflict"), np.mean([v["clean_margin"] for v in c.values()])


def summ(name, seed):
    c = load(name, seed)["conditions"]
    coh = np.mean([v["margin"] for k, v in c.items() if k.endswith("Coherent Conflict")])
    sub = np.mean([v["margin"] for k, v in c.items() if k.endswith("Substitution Conflict")])
    kn = np.mean([v["clean_margin"] for v in c.values()])
    return coh, sub, kn


def main(shared=True):
    pair = [(r, s) for r in ("dolma1_7-1B", "dolma1_7-no-flan-1B") for s in dd.SEEDS]
    items = shared_items(pair) if shared else None
    f = (lambda r, s: summ_shared(r, s, items)) if shared else summ
    A = {s: f("dolma1_7-1B", s) for s in AUX}
    B = {s: f("dolma1_7-no-flan-1B", s) for s in AUX}
    d = lambda i: float(np.mean([A[s][i] for s in AUX]) - np.mean([B[s][i] for s in AUX]))
    # pooled within-recipe seed SD from other recipes with all 3 seeds
    recs = sorted({f.stem.split("__")[0] for f in E20.glob("*__*.json")} - {"dolma1_7-1B", "dolma1_7-no-flan-1B"})
    recs = [r for r in recs if all((E20 / f"{r}__{s}.json").exists() for s in dd.SEEDS)]
    V = np.array([[(summ_shared(r, s, shared_items([(r, x) for x in dd.SEEDS])) if shared else summ(r, s))
                   for s in dd.SEEDS] for r in recs])  # [rec, seed, 3]
    sd = np.sqrt(((V - V.mean(1, keepdims=True)) ** 2).sum(1).sum(0) / (len(recs) * 2)) if recs else np.full(3, np.nan)
    se = sd * np.sqrt(1 / 2 + 1 / 2)
    cross = [A[a][0] - B[b][0] for a, b in itertools.product(AUX, AUX)]
    dcoh, dsub, dk = d(0), d(1), d(2)
    out = {"delta_coh": dcoh, "delta_sub": dsub, "delta_K": dk, "pooled_seed_sd": sd.tolist(), "se": se.tolist(),
           "n_recipes_for_sd": len(recs), "cross_pair_coh_diffs": cross,
           "evidence_effect_replicates": bool(dcoh >= 1.0 and dcoh > 2 * se[0] and min(cross) > 0),
           "specific_to_evidence": bool(dcoh - dsub >= 0.5 and (dsub < 2 * se[1] or dsub < dcoh / 2)),
           "knowledge_confound_excluded": bool(abs(dk) < 1.0),
           "aux_values": {"dolma1_7": A, "no_flan": B}, "readout": "shared-known items" if shared else "own-known items",
           "n_shared_items": {k: len(v) for k, v in items.items()} if shared else None}
    (mc.RESULTS / "e25").mkdir(exist_ok=True)
    (mc.RESULTS / "e25" / f"analysis_{'shared' if shared else 'own'}.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main(shared=True)
    main(shared=False)
