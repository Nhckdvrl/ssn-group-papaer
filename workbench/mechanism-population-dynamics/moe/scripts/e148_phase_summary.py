"""Report a prespecified completed E148 phase without changing any treatment."""
from pathlib import Path
import argparse
import json
import numpy as np
import torch
import e148_common as c
from e144145_analyze import input_stats
from e148_readout import bits_to_logp


def main(step):
    plan = c.verify_plan()
    records = {n: c.read(c.RESULT / f"{n}.json") for n in ("A", "B", "A-repeat")}
    evaluations = {}
    for n, r in records.items():
        row = next(x for x in r["evaluations"] if x["step"] == step)
        if c.sha(row["logits"]["path"]) != row["logits"]["sha256"]: raise ValueError("Prediction bytes changed")
        evaluations[n] = row
    a, b = evaluations["A"], evaluations["B"]
    la = np.load(a["logits"]["path"], mmap_mode="r")
    lb = np.load(b["logits"]["path"], mmap_mode="r")
    with np.load(plan["plan_path"]) as raw: targets = raw["held"][:, 1:]
    values = np.zeros((64, 4), np.float64)
    for seq in range(64):
        for start in range(0, 512, 32):
            p, q = bits_to_logp(la[seq:seq+1, start:start+32]), bits_to_logp(lb[seq:seq+1, start:start+32])
            y = torch.from_numpy(targets[seq:seq+1, start:start+32].astype(np.int64))
            values[seq] += c.old.prediction_metrics(p, q, y).double().sum((0, 1)).numpy()/512
    stats = lambda v: input_stats(np.asarray(v), plan["selected"], 148001)
    out = {"experiment": "E148", "phase_step": step, "status": "phase_complete_not_final_claim",
           "source_sha256": c.code_proof(), "reporting_script_sha256": c.sha(__file__),
           "nll": {n: stats(r["nll_rows"]) for n, r in evaluations.items()},
           "B_minus_A_nll": stats(np.asarray(b["nll_rows"])-np.asarray(a["nll_rows"])),
           "A_to_B_kl": stats(values[:, 1]), "B_to_A_kl": stats(values[:, 2]),
           "A_repeat_exact_full_prediction_bytes": evaluations["A"]["logits"]["sha256"] == evaluations["A-repeat"]["logits"]["sha256"],
           "A_repeat_max_abs_nll_difference": float(np.abs(np.array(a["nll_rows"])-evaluations["A-repeat"]["nll_rows"]).max()),
           "scope": "Predesignated phase readout on fixed inputs; no hyperparameter/dose/input changes, no claim of persistence before common-suffix completion."}
    c.write(c.RESULT / f"phase_{step}.json", out)
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--step", type=int, default=160)
    args = p.parse_args(); torch.set_num_threads(4); main(args.step)
