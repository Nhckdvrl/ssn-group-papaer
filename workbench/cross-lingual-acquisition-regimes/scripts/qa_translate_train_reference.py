"""E07 data adapter for the unchanged, source-validated E03 learning recipe."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import nli_learning as nli
import qa_learning as qa

ROOT = Path(__file__).resolve().parents[1]


def main():
    source_data = json.loads(qa.DATA.read_text())
    source_freeze = json.loads(qa.FREEZE.read_text())
    assert source_freeze["passed"] and source_freeze["config"] == qa.CONFIG
    core_hash = hashlib.sha256(Path(qa.__file__).read_bytes()).hexdigest()
    assert source_freeze["script_sha256"] == core_hash
    prepared = json.loads((ROOT / "artifacts/qa_translate_train/data.json").read_text())
    metadata = prepared["metadata"]
    assert metadata["qa_script_sha256"] == core_hash
    assert metadata["task_metadata"] == source_data["metadata"]
    assert nli.digest(prepared["train"]) == metadata["train_sha256"]
    assert [r["id"] for r in prepared["train"]] == [r["id"] for r in source_data["splits"]["train"]]
    wrapper_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    source_data["splits"]["train"] = prepared["train"]
    source_data["metadata"]["hashes"]["train"] = metadata["train_sha256"]
    source_data["metadata"]["translated_supervision_reference"] = dict(
        preparation=metadata,wrapper_sha256=wrapper_hash,recipe_source=source_freeze,
        source_gate_inherited_for_recipe_only=True,mixed_training_efficacy_not_yet_verified=True)
    out = ROOT / "artifacts/qa_translate_train/run_inputs"
    out.mkdir(parents=True,exist_ok=False)
    data_path,freeze_path = out / "data.json",out / "recipe_freeze.json"
    nli.dump(data_path,source_data)
    nli.dump(freeze_path,dict(source_freeze,data_hashes=source_data["metadata"]["hashes"],
        recipe_origin="E03 English source pilot; recipe reuse, not an efficacy gate for mixed supervision",
        wrapper_sha256=wrapper_hash))
    manifest = dict(metadata["parent_model"],local_supervision_reference=dict(
        experiment="E07",data_sha256=metadata["train_sha256"],wrapper_sha256=wrapper_hash))
    nli.dump(ROOT / "artifacts/model_manifests/UCLNLP__monoweb__ckpt_exp_en_de_e07_translate_train.json",manifest)
    # Only input paths change: the E03 training/generation code remains byte-identical.
    qa.DATA,qa.FREEZE = data_path,freeze_path
    qa.run(SimpleNamespace(phase="train",condition="e07_translate_train",seed=17))
    nli.dump(out / "completion.json",dict(experiment="E07",seed=17,wrapper_sha256=wrapper_hash,
        core_sha256=core_hash,train_sha256=metadata["train_sha256"],
        task_folder="artifacts/qa_learning/train_e07_translate_train_seed17"))


if __name__ == "__main__":
    main()
