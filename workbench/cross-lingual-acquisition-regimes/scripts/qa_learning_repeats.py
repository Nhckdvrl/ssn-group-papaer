"""E09 sequential independent adaptation seeds; the core recipe is unchanged."""
import argparse
import gc
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import nli_learning as nli
import qa_learning as qa

ROOT = Path(__file__).resolve().parents[1]


def main(condition):
    import torch
    calibration = json.loads((ROOT / "results/e08_retention_hardware_control.json").read_text())
    assert calibration["protocol_ast_equal"]
    assert all(v["legacy_prediction_matches"] == v["n"] for r in calibration["models"].values() for v in r["directions"].values())
    original = json.loads((ROOT / "artifacts/qa_learning" / f"train_{condition}_seed17/provenance.json").read_text())
    assert torch.cuda.get_device_name() == original["device"]
    assert hashlib.sha256(Path(qa.__file__).read_bytes()).hexdigest() == original["script_sha256"]
    for seed in (29,43):
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        qa.run(SimpleNamespace(phase="train",condition=condition,seed=seed))
    nli.dump(ROOT / "results" / f"e09_learning_{condition}_completion.json",dict(condition=condition,seeds=[29,43],
        core_sha256=original["script_sha256"],wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        data_hashes=original["metadata"]["hashes"],device=torch.cuda.get_device_name()))
    print("E09_COMPLETED",condition,flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition",required=True,choices=("baseline","monoweb","onlyparallel"))
    main(parser.parse_args().condition)
