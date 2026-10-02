"""Wait for our completed E07 and a free visible GPU, then run all E09 cells."""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    import torch
    completion = ROOT / "artifacts/qa_learning/train_e07_translate_train_seed17/completion.json"
    wrapper = ROOT / "artifacts/qa_translate_train/run_inputs/completion.json"
    while not (completion.exists() and wrapper.exists()):
        print("Waiting for both E07 complete-save records", flush=True)
        time.sleep(60)
    json.loads(completion.read_text())
    json.loads(wrapper.read_text())
    while True:
        free, total = torch.cuda.mem_get_info()
        if total-free < 512*1024**2:
            break
        print("Waiting for GPU release; occupied bytes", total-free, flush=True)
        time.sleep(60)
    for condition in ("baseline", "monoweb", "onlyparallel"):
        subprocess.run([sys.executable,str(ROOT / "scripts/qa_learning_repeats.py"),
                        "--condition",condition],check=True)
    print("E09_ALL_TRAINING_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
