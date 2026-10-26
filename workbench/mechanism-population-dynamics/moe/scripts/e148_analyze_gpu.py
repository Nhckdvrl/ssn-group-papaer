"""GPU execution adapter for the unchanged, predeclared E148 summary formulas.

Only tensor transport and repeated immutable-file checks are accelerated. The
original analyzer still constructs every comparison, bootstrap and route table.
"""
from __future__ import annotations
import argparse
import os
_p = argparse.ArgumentParser(add_help=False)
_p.add_argument("--physical-gpu", type=int, default=3)
_args, _ = _p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, "", str(_args.physical_gpu)):
    raise ValueError("Requested GPU and visibility differ")
os.environ["CUDA_VISIBLE_DEVICES"] = str(_args.physical_gpu)

import json
import time
import numpy as np
import torch
import e148_common as c
import e148_readout as report


class AnalysisBudget(c.Budget):
    def check(self):
        used = self.update(lambda d: d["completed_seconds"]+sum(time.monotonic()-v["started_monotonic"] for v in d["active"].values()))
        limit = c.read(c.RESULT / "resource_allowance.json")["max_gpu_seconds"]
        if used >= limit: raise TimeoutError("E148 explicit execution allowance exhausted")
        return used


def main(physical):
    lock = None
    real_metrics, real_evaluation = c.old.prediction_metrics, report.evaluation
    cached, calls = {}, 0
    try:
        with AnalysisBudget("offline_full_vocabulary_summary") as budget:
            lock = c.old.gpu_lock(physical)
            def gpu_logp(array):
                return torch.from_numpy(np.array(array, copy=True)).view(torch.bfloat16).to("cuda:0").float().log_softmax(-1)
            def metrics(reference, variant, target):
                nonlocal calls
                calls += 1
                if calls % 256 == 0: budget.check()
                return real_metrics(reference, variant, target.to(reference.device)).cpu()
            def verified_once(record, step):
                key = (record["branch"], step)
                if key not in cached:
                    budget.check()
                    cached[key] = real_evaluation(record, step)
                return cached[key]
            report.bits_to_logp = gpu_logp
            report.evaluation = verified_once
            c.old.prediction_metrics = metrics
            output = report.analyze()
            summary = c.read(c.RESULT / "summary.json")
            earlier = c.read(c.RESULT / "phase_160.json")
            now = summary["pairs"]["A_160_to_B_160"]
            errors = {"forward_KL_point": abs(now["forward_kl"]["point"]-earlier["A_to_B_kl"]["point"]),
                      "reverse_KL_point": abs(now["reverse_kl"]["point"]-earlier["B_to_A_kl"]["point"]),
                      "NLL_gap_point": abs(now["nll_right_minus_left"]["point"]-earlier["B_minus_A_nll"]["point"])}
            summary["analysis_execution"] = {"adapter_sha256": c.sha(__file__), "original_analyzer_sha256": c.sha(report.__file__),
                "physical_gpu": physical, "visible_device_uuid": str(torch.cuda.get_device_properties(0).uuid),
                "formulas_and_comparison_set_unchanged": True, "CPU_phase160_point_absolute_differences": errors,
                "unique_immutable_evaluations_checked": len(cached), "metric_chunks": calls,
                "precision": "Stored actual BF16 logits -> FP32 logsoftmax/KL on GPU -> FP64 sequence accumulation; same predeclared input-file bootstrap"}
            if max(errors.values()) > 5e-6:
                summary["status"] = "needs_numeric_audit"
                c.write(c.RESULT / "summary.json", summary)
                raise ArithmeticError("CPU/GPU score discrepancy exceeds the engineering tolerance")
            c.write(c.RESULT / "summary.json", summary)
    finally:
        c.old.prediction_metrics = real_metrics
        report.evaluation = real_evaluation
        if lock is not None: lock.close()
    return output


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--physical-gpu", type=int, default=3)
    args = p.parse_args(); torch.set_num_threads(4)
    print(json.dumps(main(args.physical_gpu), indent=2), flush=True)
