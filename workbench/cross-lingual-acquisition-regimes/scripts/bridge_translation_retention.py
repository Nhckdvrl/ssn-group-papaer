"""E10: fixed translation readouts before and after E04 task adaptation."""
import argparse
import hashlib
import json
from pathlib import Path

import nli_learning as nli
import qa_learning as qa
import translation_retention_protocol as protocol

ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = ("new_paired","new_split","reused_paired","reused_split")


def run(condition,phase):
    control = json.loads((ROOT / "results/e08_retention_hardware_control.json").read_text())
    assert control["protocol_ast_equal"]
    for model in control["models"].values():
        assert all(v["legacy_prediction_matches"] == v["n"] for v in model["directions"].values())
    reference = control["models"]["monoweb"]["completion"]
    corpus_path = ROOT / "artifacts/retention_hardware_control/monoweb/primary.jsonl"
    corpus = [json.loads(line) for line in corpus_path.read_text().splitlines()]
    items = [{k:r[k] for k in ("id","direction","source","reference","prompt")} for r in corpus]
    cpt = json.loads((ROOT / "results" / f"e04_cpt_{condition}_seed17.json").read_text())
    assert cpt["finite"] and len(cpt["losses"]) == 256
    if phase == "cpt":
        manifest = json.loads((ROOT / "artifacts/model_manifests" / f"UCLNLP__monoweb__ckpt_exp_en_de_e04_{condition}.json").read_text())
        assert manifest["local_intervention"]["condition"] == condition
        path = Path(manifest["path"])
        provenance = dict(cpt=cpt,model=manifest)
    else:
        folder = ROOT / "artifacts/qa_learning" / f"train_e04_{condition}_seed17"
        done = json.loads((folder / "completion.json").read_text())
        p = json.loads((folder / "provenance.json").read_text())
        assert done["script_sha256"] == p["script_sha256"] == hashlib.sha256(Path(qa.__file__).read_bytes()).hexdigest()
        assert done["data_hashes"] == cpt["provenance"]["metadata"]["task_hashes"]
        assert p["model"]["local_intervention"]["condition"] == condition
        path = folder / "checkpoint"
        provenance = dict(cpt=cpt,qa_completion=done,qa_provenance=p)
    out = ROOT / "artifacts/bridge_retention" / f"{condition}_seed17" / phase
    record = protocol.evaluate_checkpoint(path,items,out,f"{condition}_{phase}",reference["device"])
    assert record["items_sha256"] == reference["items_sha256"]
    record.update(condition=condition,phase=phase,seed=17,provenance=provenance,
        runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    nli.dump(out / "completion.json",record)
    nli.dump(ROOT / "results" / f"e10_retention_{condition}_{phase}_seed17.json",record)
    print("E10_COMPLETED",condition,phase,flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase",required=True,choices=("cpt","post"))
    parser.add_argument("--condition",choices=CONDITIONS+("all",),default="all")
    args = parser.parse_args()
    for condition in (CONDITIONS if args.condition == "all" else (args.condition,)):
        run(condition,args.phase)
