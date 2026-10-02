"""Finish all seed-reliability readouts before E11 on the same calibrated GPU."""
from pathlib import Path

from queue_learning_retention import free_gpu, run, wait_for

ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    wait_for([ROOT / "artifacts/symmetric_bridge" / f"{mode}_seed17/completion.json" for mode in ("paired", "split")])
    run("analyze_symmetric_bridge.py", "qa")
    wait_for([ROOT / "results/e09_retention_reliability.json"])
    for mode in ("paired", "split"):
        for phase in ("cpt", "post"):
            free_gpu()
            run("symmetric_bridge_retention.py", "--condition", mode, "--phase", phase)
    run("analyze_symmetric_bridge.py", "mt")
    print("E11_ALL_READOUTS_COMPLETE", flush=True)
