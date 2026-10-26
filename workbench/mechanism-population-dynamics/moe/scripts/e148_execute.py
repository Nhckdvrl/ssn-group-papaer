"""Resource-only E148 launch layer; the sealed numerical/training code is unchanged.

The public scientific protocol/core source hash stays identical to the common
parent. This external allowance and its source hash are recorded separately.
"""
from __future__ import annotations
import argparse
import os
_p = argparse.ArgumentParser(add_help=False)
_p.add_argument("--physical-gpu", type=int, default=0)
_early, _ = _p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, "", str(_early.physical_gpu)):
    raise ValueError("Process visibility/requested physical GPU differ")
os.environ["CUDA_VISIBLE_DEVICES"] = str(_early.physical_gpu)

import json
import time
import torch
import e148_common as c
import e148_native as training
import e148_readout as readout


def main(args):
    plan = c.verify_plan()
    policy_path = c.RESULT / "resource_allowance.json"
    policy = c.read(policy_path)
    if policy["core_source_sha256"] != c.code_proof() or policy["scientific_spec_hash"] != plan["spec_hash"] or policy["plan_sha256"] != plan["plan_sha256"]:
        raise ValueError("Resource allowance cannot change the sealed numerical protocol")
    if policy["max_gpu_seconds"] != 18000 or not policy["numerical_program_unchanged"]:
        raise ValueError("Unexpected resource allowance")
    policy_sha = c.sha(policy_path)

    class ExecutionBudget(c.Budget):
        def check(self):
            def measured(d):
                if d["limit_gpu_seconds"] != policy["max_gpu_seconds"]:
                    raise ValueError("Ledger and explicit allowance differ")
                return d["completed_seconds"]+sum(time.monotonic()-a["started_monotonic"] for a in d["active"].values())
            used = self.update(measured)
            if used >= policy["max_gpu_seconds"]:
                raise TimeoutError("Explicit E148 five-GPU-hour total allowance exhausted")
            return used

    # Only allocation accounting changes; training/gradient/model/plan functions
    # and every compiled scientific constant retain their original identity.
    c.Budget = ExecutionBudget
    name = args.branch if args.mode == "train" else "grafts"
    provenance = {"mode": args.mode, "branch": name, "physical_gpu": args.physical_gpu, "status": "running",
                  "resource_policy_sha256": policy_sha, "resource_policy": policy,
                  "execution_launcher_sha256": c.sha(__file__), "core_source_sha256": c.code_proof()}
    path = c.RESULT / f"execution_{name}.json"
    c.write(path, provenance)
    try:
        result = training.train(plan, args.physical_gpu, args.branch) if args.mode == "train" else readout.transplants(args.physical_gpu)
        provenance.update(status="complete", result=result)
        return result
    except BaseException as error:
        provenance.update(status="failed", error=f"{type(error).__name__}: {error}")
        raise
    finally:
        c.write(path, provenance)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("train", "grafts"))
    p.add_argument("--physical-gpu", type=int, default=0)
    p.add_argument("--branch", choices=("A", "B", "A-repeat"), default="A")
    args = p.parse_args()
    torch.set_num_threads(4)
    print(json.dumps(main(args), indent=2), flush=True)
