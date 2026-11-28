"""E15c POST-HOC (decided after seeing the grid): separate format compliance from program content.
AZR's answer_conditional extraction gives nothing when a response lacks <answer>...</answer>. Here, a response
without the tag is searched as a whole (text after the last </think> if present) for the same ```python / ```input
blocks; everything else (single function f, AZR banned imports, sandbox screen, determinism, fingerprints, novelty)
is unchanged. Output: one validated jsonl per proposal file, val_loose_<name>.

Usage: python e15c_loose.py --props prop_*.jsonl --materials <jsonl> --out_dir <dir> [--workers 12]
"""
import argparse
import importlib.util
import json
import os
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("e15c_validate", os.path.join(HERE, "e15c_validate.py"))
V = importlib.util.module_from_spec(spec); sys.modules["e15c_validate"] = V; spec.loader.exec_module(V)


def loosen(row):
    t = row["text"]
    if "<answer>" not in t:
        body = t.split("</think>")[-1]
        row = dict(row, text=f"<answer>{body}</answer>", loose_used=True)
    else:
        row = dict(row, loose_used=False)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--props", nargs="+", required=True); ap.add_argument("--materials", required=True)
    ap.add_argument("--out_dir", required=True); ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    mk = V.material_keys(a.materials, a.workers)
    mat_fp = {x["fp"] for x in mk if x["fp"]}; mat_ast = {x["ast_hash"] for x in mk if x["ast_hash"]}
    for p in a.props:
        rows = [loosen(json.loads(l)) for l in open(p)]
        with Pool(a.workers) as pool:
            res = pool.map(V.validate, rows, chunksize=16)
        out = os.path.join(a.out_dir, "val_loose_" + os.path.basename(p))
        with open(out, "w") as f:
            for row, r in zip(rows, res):
                r["loose_used"] = row["loose_used"]
                if r.get("valid"):
                    rf = [mk[i] for i in r.get("refs", [])]
                    r["copy_of_ref_ast"] = r.get("ast_hash") in {x["ast_hash"] for x in rf}
                    r["same_fp_as_ref"] = r.get("fp") is not None and r["fp"] in {x["fp"] for x in rf}
                    r["new_ast_vs_materials"] = r.get("ast_hash") not in mat_ast
                    r["new_fp_vs_materials"] = None if r.get("fp") is None else r["fp"] not in mat_fp
                f.write(json.dumps(r) + "\n")
        print(os.path.basename(p), "valid", sum(r["valid"] for r in res), "of which via loose parse",
              sum(r["valid"] and row["loose_used"] for row, r in zip(rows, res)), flush=True)


if __name__ == "__main__":
    main()
