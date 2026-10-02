"""Finish E10 post readouts only after all saved CPT/QA and GPU release."""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = ("new_paired", "new_split", "reused_paired", "reused_split")


def main():
    import torch
    prerequisites = [ROOT / "artifacts/bridge_retention" / f"{c}_seed17/cpt/completion.json" for c in CELLS]
    prerequisites += [ROOT / "artifacts/qa_bridge" / f"{c}_seed17/completion.json" for c in CELLS]
    while not all(path.exists() for path in prerequisites):
        print("Waiting for all E10 CPT and E04 complete-save records", flush=True)
        time.sleep(60)
    while True:
        free,total = torch.cuda.mem_get_info()
        if total-free < 512*1024**2:
            break
        print("Waiting for GPU release; occupied bytes",total-free,flush=True)
        time.sleep(60)
    subprocess.run([sys.executable,str(ROOT / "scripts/bridge_translation_retention.py"),
                    "--phase","post","--condition","all"],check=True)
    subprocess.run([sys.executable,str(ROOT / "scripts/analyze_bridge_retention.py")],check=True)
    print("E10_ALL_READOUTS_COMPLETE",flush=True)


if __name__ == "__main__":
    main()
