"""Check HF EN/DE test order against original XNLI pairIDs."""
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
archive = ROOT / "artifacts/nli_learning/XNLI-1.0.zip"
data = json.loads((ROOT / "artifacts/nli_learning/data.json").read_text())
with zipfile.ZipFile(archive) as z:
    original = list(csv.DictReader(io.StringIO(z.read("XNLI-1.0/xnli.test.tsv").decode()), delimiter="\t"))
labels = {"entailment": 0, "neutral": 1, "contradiction": 2, "contradictory": 2}
orders = {}
for language in ("en", "de"):
    rows = [r for r in original if r["language"] == language]
    hf = data["splits"][language + "_test"]
    assert len(rows) == len(hf) == 5010
    for r, h in zip(rows, hf):
        assert r["sentence1"] == h["premise"]
        assert r["sentence2"] == h["hypothesis"]
        assert labels[r["gold_label"]] == h["label"]
    orders[language] = [r["pairID"] for r in rows]
assert orders["en"] == orders["de"]
assert len(set(orders["en"])) == 5010
report = dict(original_url="https://dl.fbaipublicfiles.com/XNLI/XNLI-1.0.zip",
              archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
              n=5010, text_and_labels_exact_match=True, en_de_pairIDs_identical=True,
              pairID_sequence_sha256=hashlib.sha256(json.dumps(orders["en"]).encode()).hexdigest())
english = [r for r in original if r["language"] == "en"]
report["promptIDs"] = [r["promptID"] for r in english]
report["unique_promptIDs"] = len(set(report["promptIDs"]))
norm = lambda s: " ".join(s.casefold().split())
train_premises = {norm(r["premise"]) for r in data["splits"]["train"]}
report["shared_training_premises"] = {k: sum(norm(r["premise"]) in train_premises for r in data["splits"][k])
                                      for k in ("en_dev", "en_test")}
(ROOT / "results/nli_xnli_pair_audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "promptIDs"}))
