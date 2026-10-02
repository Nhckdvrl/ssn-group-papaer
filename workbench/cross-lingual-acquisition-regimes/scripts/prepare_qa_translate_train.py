"""E07: standard translated-supervision reference, without changing E03/E04 data."""
import hashlib
import json
from pathlib import Path
import random

import nli_learning as nli
import qa_learning as qa

ROOT = Path(__file__).resolve().parents[1]


def main():
    from transformers import AutoTokenizer
    output = ROOT / "artifacts/qa_translate_train/data.json"
    assert not output.exists()
    task = json.loads(qa.DATA.read_text())
    audit_path = ROOT / "artifacts/qa_learning/translated_supervision_audit.json"
    audit = json.loads(audit_path.read_text())
    report = json.loads((ROOT / "results/e05_translated_supervision_audit.json").read_text())
    assert hashlib.sha256(audit_path.read_bytes()).hexdigest() == report["audit_sha256"]
    assert nli.digest(task["splits"]["train"]) == report["source_hash"]
    eligible = sorted(r["id"] for r in audit if r.get("german", {}).get("structurally_usable", False))
    assert len(eligible) == 15442
    random.Random(20261007).shuffle(eligible)
    selected = set(eligible[:8192])
    raw = (ROOT / "artifacts/qa_learning/squad.translate.train.en-de.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == report["translation"]["sha256"]
    translations = {}
    for article in json.loads(raw)["data"]:
        for paragraph in article["paragraphs"]:
            for question in paragraph["qas"]:
                assert question["id"] not in translations
                translations[question["id"]] = dict(id=question["id"], context=paragraph["context"],
                    question=question["question"], answers={
                        "text": [a["text"] for a in question["answers"]],
                        "answer_start": [a["answer_start"] for a in question["answers"]]})
    manifest = json.loads((ROOT / "artifacts/model_manifests/UCLNLP__monoweb__ckpt_exp_en_de_monoweb.json").read_text())
    tok = AutoTokenizer.from_pretrained(manifest["path"], local_files_only=True)
    assert nli.digest(tok.get_vocab()) == task["metadata"]["tokenizer_sha256"]
    mixed, totals = [], {language: dict(units=0,input_tokens=0,answer_tokens=0) for language in ("en", "de")}
    for source in task["splits"]["train"]:
        language = "de" if source["id"] in selected else "en"
        row = dict(translations[source["id"]],title=source["title"]) if language == "de" else source.copy()
        encoded = qa.encode(row, tok)
        assert len(encoded["ids"]) <= qa.CONFIG["max_train_length"]
        assert row["answers"]["text"][0].strip() and row["answers"]["text"][0] in row["context"]
        totals[language]["units"] += 1
        totals[language]["input_tokens"] += len(encoded["ids"])
        totals[language]["answer_tokens"] += len(encoded["ids"])-encoded["prefix_length"]
        mixed.append(dict(row, training_language=language))
    assert [r["id"] for r in mixed] == [r["id"] for r in task["splits"]["train"]]
    assert len({r["id"] for r in mixed}) == len(mixed) == 16384
    assert totals["en"]["units"] == totals["de"]["units"] == 8192
    forbidden = {r["id"] for split in ("en_dev", "en_test", "de_test") for r in task["splits"][split]}
    assert not set(r["id"] for r in mixed) & forbidden
    metadata = dict(task_metadata=task["metadata"],parent_model=manifest,selection_seed=20261007,
        train_sha256=nli.digest(mixed),selected_ids_sha256=nli.digest(sorted(selected)),
        totals=totals,translation=report["translation"],audit_sha256=report["audit_sha256"],
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        qa_script_sha256=hashlib.sha256(Path(qa.__file__).read_bytes()).hexdigest(),
        limits="Equal task IDs and updates, not equal English exposure, tokens or total CPT+task cost. Structural validity is not semantic correctness.")
    nli.dump(output,dict(metadata=metadata,train=mixed))
    nli.dump(ROOT / "results/e07_translate_train_data_manifest.json",metadata)
    print(json.dumps(metadata,indent=2),flush=True)


if __name__ == "__main__":
    main()
