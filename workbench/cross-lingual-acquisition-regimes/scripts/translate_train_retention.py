"""Fixed E07 retention measurement after the saved translate-train reference."""
import hashlib
import json
from pathlib import Path

import nli_learning as nli
import qa_learning as qa
import translation_retention_protocol as protocol

ROOT = Path(__file__).resolve().parents[1]


def main():
    calibration = json.loads((ROOT / "results/e08_retention_hardware_control.json").read_text())
    reference = calibration["models"]["monoweb"]["completion"]
    prepared = json.loads((ROOT / "artifacts/qa_translate_train/data.json").read_text())
    wrapper = json.loads((ROOT / "artifacts/qa_translate_train/run_inputs/completion.json").read_text())
    assert wrapper["wrapper_sha256"] == hashlib.sha256((ROOT / "scripts/qa_translate_train_reference.py").read_bytes()).hexdigest()
    folder = ROOT / wrapper["task_folder"]
    done = json.loads((folder / "completion.json").read_text())
    p = json.loads((folder / "provenance.json").read_text())
    assert p["script_sha256"] == done["script_sha256"] == wrapper["core_sha256"] == hashlib.sha256(Path(qa.__file__).read_bytes()).hexdigest()
    assert prepared["metadata"]["parent_model"] == reference["model"]
    assert p["model"]["local_supervision_reference"]["data_sha256"] == wrapper["train_sha256"] == done["data_hashes"]["train"]
    assert p["config"] == qa.CONFIG and p["seed"] == 17
    corpus = ROOT / "artifacts/retention_hardware_control/monoweb/primary.jsonl"
    rows = [json.loads(line) for line in corpus.read_text().splitlines()]
    items = [{k:r[k] for k in ("id","direction","source","reference","prompt")} for r in rows]
    out = ROOT / "artifacts/qa_translate_train/retention"
    record = protocol.evaluate_checkpoint(folder / "checkpoint",items,out,"e07_translate_train",reference["device"])
    assert record["items_sha256"] == reference["items_sha256"]
    record.update(condition="e07_translate_train",seed=17,qa_completion=done,qa_provenance=p,
        supervision_manifest=prepared["metadata"],runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    nli.dump(out / "completion.json",record)
    nli.dump(ROOT / "results/e07_translation_retention_completion.json",record)
    print("E07_RETENTION_COMPLETED",flush=True)


if __name__ == "__main__":
    main()
