"""Use one verified idle A100 for both preregistered symmetric conditions."""
import os
import subprocess
import sys
from pathlib import Path

from queue_learning_retention import free_gpu

ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    assert os.environ["CUDA_VISIBLE_DEVICES"] == "0"
    for condition in ("paired", "split"):
        free_gpu()
        subprocess.run([sys.executable, str(ROOT / "scripts/symmetric_bridge_learning.py"),
            "run", "--condition", condition, "--seed", "17"], check=True)
    print("E11_ALL_TRAINING_COMPLETE", flush=True)
