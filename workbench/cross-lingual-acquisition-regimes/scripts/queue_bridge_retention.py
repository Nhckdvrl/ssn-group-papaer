"""Finish E10 post readouts only after all saved CPT/QA and GPU release."""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = ("new_paired", "new_split", "reused_paired", "reused_split")


def main():
    prerequisites = [ROOT / "artifacts/bridge_retention" / f"{c}_seed17/cpt/completion.json" for c in CELLS]
    prerequisites += [ROOT / "artifacts/qa_bridge" / f"{c}_seed17/completion.json" for c in CELLS]
    while not all(path.exists() for path in prerequisites):
        print("Waiting for all E10 CPT and E04 complete-save records", flush=True)
        time.sleep(60)
    while True:
        gpu = os.environ["CUDA_VISIBLE_DEVICES"]
        assert "," not in gpu
        used = int(subprocess.check_output(["nvidia-smi","--id="+gpu,
            "--query-gpu=memory.used","--format=csv,noheader,nounits"],text=True).strip())
        if used < 512:
            break
        print("Waiting for GPU release; occupied MiB",used,flush=True)
        time.sleep(60)
    subprocess.run([sys.executable,str(ROOT / "scripts/bridge_translation_retention.py"),
                    "--phase","post","--condition","all"],check=True)
    subprocess.run([sys.executable,str(ROOT / "scripts/analyze_bridge_retention.py")],check=True)
    print("E10_ALL_READOUTS_COMPLETE",flush=True)


if __name__ == "__main__":
    main()
