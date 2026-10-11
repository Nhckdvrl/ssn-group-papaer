"""E03: instruction / cue recovery controls on a subset of the structure grid.

Same bases (same seeds) as the pilot grid; header varies:
  none   : default neutral header
  change : warns the labelling rule may change partway; predict with the current rule
  noise  : warns some labels may be wrong (random mistakes); predict the true rule
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ices.generator import episode_record, load_lexicon, make_base, HEADER, labels_for  # noqa
from ices.oracle import all_oracles_fast  # noqa
import build_struct as bs  # noqa

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {
    "none": HEADER,
    "change": "Below are examples of items and their labels, listed in the order they were collected. "
              "The labelling rule may have changed at some point while the examples were collected. "
              "Label the final item according to the rule that is in force at the end.\n\n",
    "noise": "Below are examples of items and their labels. A few of the labels are random mistakes "
             "made by the annotator. Label the final item according to the true underlying rule.\n\n",
}
KEEP = ["allA"] + [f"suffix_{k}" for k in (1, 2, 3, 4, 6, 8)] + [f"disp_{k}" for k in (2, 3, 4, 6)] + \
       [f"noise_{m}__suffix_{k}" for m in (1, 2, 4) for k in (0, 3, 5)] + \
       ["single_1", "single_8", "single_16", "block_start4", "block_mid4"]


def main():
    N = int(os.environ.get("N_BASES", 200)); out = ROOT / "data" / os.environ.get("OUT", "cue_pilot_n5_T16")
    out.mkdir(parents=True, exist_ok=True)
    conds = bs.conditions()
    rows = []
    for i in range(N):
        seed = bs.SEED0 + i * 7919
        base = make_base(seed, bs.N_ATTR, bs.T, bs.attr_bank, bs.label_bank, tag=f"s{bs.N_ATTR}_{bs.T}_")
        X = np.array(base.X)
        for name in KEEP:
            p = conds[name]
            o = None
            for hn, h in HEADERS.items():
                rec = episode_record(base, p, name, header=h)
                if o is None:
                    o = all_oracles_fast(X, rec["labels"], base.xq, bs.N_ATTR)
                    qb = rec["query_label_B"]
                    for k in ("set", "sequence", "meta"):
                        v = o[f"{k}_p_rule_query"]; o[f"{k}_pB"] = v if qb == 1 else 1 - v
                rec.update({"uid": f"{hn}:{name}|{base.base_id}", "cue": hn, "oracle": o})
                rec["cond"] = f"{hn}:{name}"
                rows.append(rec)
    with open(out / "rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(len(rows), "rows ->", out)


if __name__ == "__main__":
    main()
