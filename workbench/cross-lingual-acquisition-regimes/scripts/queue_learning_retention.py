"""Serial fixed readouts after E10, with complete-save and free-GPU gates."""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def wait_for(paths):
    while not all(path.exists() for path in paths):
        print("Waiting for complete prerequisites",[str(p) for p in paths if not p.exists()],flush=True)
        time.sleep(60)


def free_gpu():
    gpu = os.environ["CUDA_VISIBLE_DEVICES"]
    assert "," not in gpu
    while True:
        used = int(subprocess.check_output(["nvidia-smi","--id="+gpu,
            "--query-gpu=memory.used","--format=csv,noheader,nounits"],text=True).strip())
        if used < 512:
            return
        print("Waiting for GPU release; occupied MiB",used,flush=True)
        time.sleep(60)


def run(script,*arguments):
    subprocess.run([sys.executable,str(ROOT / "scripts" / script),*arguments],check=True)


def main():
    wait_for([ROOT / "results/e10_bridge_retention_analysis_seed17.json",
              ROOT / "artifacts/qa_translate_train/run_inputs/completion.json"])
    free_gpu()
    run("translate_train_retention.py")
    run("analyze_translate_train_retention.py")
    run("analyze_qa_references.py","e07")
    for condition in ("baseline","monoweb","onlyparallel"):
        for seed in (29,43):
            wait_for([ROOT / "artifacts/qa_learning" / f"train_{condition}_seed{seed}/completion.json"])
            free_gpu()
            run("qa_repeat_translation_retention.py","--condition",condition,"--seed",str(seed))
    run("analyze_qa_references.py","e09")
    run("analyze_qa_retention_repeats.py")
    print("ALL_LEARNING_REFERENCE_READOUTS_COMPLETE",flush=True)


if __name__ == "__main__":
    main()
