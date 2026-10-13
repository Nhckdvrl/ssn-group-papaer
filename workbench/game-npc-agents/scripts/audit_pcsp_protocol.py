#!/usr/bin/env python3
"""E08 deterministic source-data split audit; optional author-fixture gradients."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--gradients", action="store_true")
    args = ap.parse_args()
    commit = subprocess.check_output(["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True).strip()
    assert commit == "5420f7b4fa0fdb6110e131402af9f5386ce2d0cf"
    root = args.source / "research/data/personas"
    def load(name):
        return json.loads((root / name).read_text())
    def archetype(row):
        return tuple(row["big_five"][k] for k in "ENACO")
    result = {"source_sha": commit, "splits": {}}
    pairs = {"unseen_occupation_300_v3": ("train_240_v3.json", "test_60_v3.json"),
             "v3_large_500": ("train_400_v3.json", "test_100_v3.json")}
    for name in ["unseen_occupation", "unseen_archetype", "unseen_combo"]:
        pairs[name] = (f"splits/{name}_v3_train.json", f"splits/{name}_v3_test.json")
    for name, (ta, tb) in pairs.items():
        a, b = load(ta), load(tb)
        tr_occs, te_occs = {r["occupation"] for r in a}, {r["occupation"] for r in b}
        tr_arcs, te_arcs = {archetype(r) for r in a}, {archetype(r) for r in b}
        texts_a, texts_b = {r["text"].strip() for r in a}, {r["text"].strip() for r in b}
        row = {"files": [ta, tb], "sizes": [len(a), len(b)],
               "id_intersection": sorted({r["id"] for r in a} & {r["id"] for r in b}),
               "exact_text_intersection_count": len(texts_a & texts_b),
               "occupation_support": [len(tr_occs), len(te_occs)],
               "occupation_intersection": sorted(tr_occs & te_occs),
               "archetype_support": [len(tr_arcs), len(te_arcs)],
               "archetype_intersection_count": len(tr_arcs & te_arcs),
               "test_unseen_archetypes": [list(x) for x in sorted(te_arcs - tr_arcs)],
               "label_counts": {k: {"train": dict(Counter(r["big_five"][k] for r in a)),
                                    "test": dict(Counter(r["big_five"][k] for r in b))} for k in "ENACO"},
               "file_sha256": {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in (ta, tb)}}
        assert not row["id_intersection"] and not row["exact_text_intersection_count"]
        result["splits"][name] = row
    sys.path.insert(0, str(args.source / "research/scripts"))
    sys.path.insert(0, str(args.source / "research"))
    from build_personas_v3 import map_persona
    base, mapped = load("personas_300.json"), load("personas_300_v3.json")
    result["v3_preferred_action_mapping"] = {
        "checked": len(base),
        "exact_matches": sum(map_persona(p) == q["preferred_actions"] for p, q in zip(base, mapped)),
        "unchanged_texts": sum(p["text"] == q["text"] for p, q in zip(base, mapped))}
    if args.gradients:
        import numpy as np
        import torch
        import torch.nn.functional as F
        import test_gradient_paths as author
        t = author._build()
        con = t._consistency_loss(author._trajectories())
        result["author_fixture_gradients"] = {"consistency": t.attributable_gradient_norms(con)}
        obs, embeddings, actions = torch.randn(8, 4), torch.randn(8, 8), torch.randint(0, 3, (8,))
        log_probs, values, entropy = t.policy.evaluate_actions(obs, actions, e_llm=embeddings)
        ppo = -log_probs.mean() + 0.5 * F.mse_loss(values, torch.randn(8)) - 0.01 * entropy.mean()
        result["author_fixture_gradients"]["ppo"] = t.attributable_gradient_norms(ppo)
        np.random.seed(11)
        diversity = t._diversity_loss([{"obs": row.numpy()} for row in obs], torch.randn(8, 8))
        result["author_fixture_gradients"]["diversity"] = t.attributable_gradient_norms(diversity)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"split_sizes": {k: v["sizes"] for k, v in result["splits"].items()},
                      "mapping": result["v3_preferred_action_mapping"],
                      "gradients": result.get("author_fixture_gradients")}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
