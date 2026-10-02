"""CPU-only structural audit; never replaces the frozen QA or CPT training pools."""
import collections
import hashlib
import json
from pathlib import Path

import nli_learning as nli
import qa_learning as qa

ROOT = Path(__file__).resolve().parents[1]


def main():
    from transformers import AutoTokenizer
    task = json.loads(qa.DATA.read_text())
    bridge = json.loads((ROOT / "artifacts/qa_bridge/data.json").read_text())
    raw = (ROOT / "artifacts/qa_learning/squad.translate.train.en-de.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == bridge["metadata"]["translation"]["sha256"]
    translated = {}
    for article in json.loads(raw)["data"]:
        for paragraph in article["paragraphs"]:
            for question in paragraph["qas"]:
                assert question["id"] not in translated
                translated[question["id"]] = dict(id=question["id"], question=question["question"],
                    context=paragraph["context"], answers=question["answers"])
    tok = AutoTokenizer.from_pretrained(bridge["metadata"]["base_model"]["path"], local_files_only=True)
    assert nli.digest(tok.get_vocab()) == task["metadata"]["tokenizer_sha256"]
    selected = {r["id"] for r in bridge["pools"]["new"]}
    source = {r["id"]: r for r in task["splits"]["train"]}
    assert len(selected) == 4096 and selected <= set(source)

    def audit(row):
        answers = row["answers"]
        if isinstance(answers, dict):
            answers = [dict(text=t, answer_start=s) for t, s in
                       zip(answers["text"], answers["answer_start"])]
        nonempty = [a for a in answers if isinstance(a.get("text"), str) and a["text"].strip()]
        offset = any(isinstance(a.get("answer_start"), int) and a["answer_start"] >= 0 and
                     row["context"][a["answer_start"]:a["answer_start"]+len(a["text"])] == a["text"]
                     for a in nonempty)
        containment = any(a["text"] in row["context"] for a in nonempty)
        # First-answer training matches E03; other answers do not rescue that label.
        first = answers[0] if answers else {}
        first_text = first.get("text", "")
        first_contained = bool(first_text.strip()) and first_text in row["context"]
        length = len(qa.encode(dict(row, answers={"text": [first_text]}), tok)["ids"]) if first_text else None
        return dict(nonempty=bool(nonempty), offset_exact=offset, any_answer_contained=containment,
                    first_answer_contained=first_contained, full_training_tokens=length,
                    within_1024=length is not None and length <= 1024,
                    structurally_usable=first_contained and length is not None and length <= 1024)

    rows = []
    for identifier, original in source.items():
        row = dict(id=identifier, e04_selected=identifier in selected,
                   translation_available=identifier in translated, english=audit(original))
        if identifier in translated:
            row["german"] = audit(translated[identifier])
        rows.append(row)
    summaries = {}
    for name, pool in (("e03_train", rows), ("e04_new_unique", [r for r in rows if r["e04_selected"]])):
        counts = collections.Counter(n=len(pool))
        for row in pool:
            counts["translation_available"] += row["translation_available"]
            for language in ("english", "german"):
                for key, value in row.get(language, {}).items():
                    if isinstance(value, bool):
                        counts[language+"_"+key] += value
            counts["both_structurally_usable"] += row["english"]["structurally_usable"] and row.get("german", {}).get("structurally_usable", False)
        summaries[name] = dict(counts)
    out = ROOT / "artifacts/qa_learning/translated_supervision_audit.json"
    nli.dump(out, rows)
    report = dict(summaries=summaries, translation=bridge["metadata"]["translation"],
                  source_hash=task["metadata"]["hashes"]["train"],
                  audit_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  limitations="Structural validity is not semantic correctness. No training pool changed; no GPU used.")
    nli.dump(ROOT / "results/e05_translated_supervision_audit.json", report)
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
