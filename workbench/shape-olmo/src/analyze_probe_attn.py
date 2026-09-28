"""Per full-attention layer: share of query attention (over the n x-value tokens) on the LAST vs FIRST
assignment, head-mean and best head, plus total mass on the value tokens. Pooled over gaps."""
import json, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for tag in sys.argv[1:]:
    rows = [json.loads(l) for l in open(f"{ROOT}/results/probe_attn/{tag}.jsonl")]
    layers = sorted(rows[0]["layers"], key=int)
    print(f"== {tag}: share on LAST / FIRST value token (head mean) [best head] | mass on values")
    for n in (2, 4, 8):
        sel = [r for r in rows if r["n"] == n]
        cells = []
        for l in layers:
            g = lambda k: np.mean([r["layers"][l][k] for r in sel])
            cells.append(f"L{l}:{g('v_last'):.2f}/{g('v_first'):.2f}[{g('v_last_best'):.2f}/{g('v_first_best'):.2f}]m{g('mass_v'):.3f}")
        print(f" n={n} (chance {1/n:.2f})  " + "  ".join(cells))
