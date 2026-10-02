"""E09 fixed retention readouts for both new learning seeds."""
import argparse
import hashlib
import json
from pathlib import Path

import nli_learning as nli
import qa_learning as qa
import translation_retention_protocol as protocol

ROOT = Path(__file__).resolve().parents[1]


def run(condition,seed):
    control = json.loads((ROOT / "results/e08_retention_hardware_control.json").read_text())
    reference = control["models"][condition]["completion"]
    folder = ROOT / "artifacts/qa_learning" / f"train_{condition}_seed{seed}"
    done = json.loads((folder / "completion.json").read_text())
    p = json.loads((folder / "provenance.json").read_text())
    assert done["script_sha256"] == p["script_sha256"] == hashlib.sha256(Path(qa.__file__).read_bytes()).hexdigest()
    assert p["seed"] == seed and p["model"] == reference["model"]
    assert done["data_hashes"] == p["metadata"]["hashes"] == json.loads(qa.DATA.read_text())["metadata"]["hashes"]
    corpus_path = ROOT / "artifacts/retention_hardware_control" / condition / "primary.jsonl"
    rows = [json.loads(line) for line in corpus_path.read_text().splitlines()]
    items = [{k:r[k] for k in ("id","direction","source","reference","prompt")} for r in rows]
    out = ROOT / "artifacts/qa_retention_repeats" / f"{condition}_seed{seed}"
    record = protocol.evaluate_checkpoint(folder / "checkpoint",items,out,f"{condition}_seed{seed}",reference["device"])
    assert record["items_sha256"] == reference["items_sha256"]
    record.update(condition=condition,seed=seed,qa_provenance=p,qa_completion=done,
        runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    nli.dump(out / "completion.json",record)
    nli.dump(ROOT / "results" / f"e09_retention_{condition}_seed{seed}.json",record)
    print("E09_RETENTION_COMPLETED",condition,seed,flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition",required=True,choices=("baseline","monoweb","onlyparallel"))
    parser.add_argument("--seed",type=int,required=True,choices=(29,43))
    args = parser.parse_args()
    run(args.condition,args.seed)
