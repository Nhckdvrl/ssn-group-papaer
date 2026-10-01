"""Verify actual released artifacts and lossless tokenization of the frozen assay."""
import csv
import hashlib
import json
from pathlib import Path

from huggingface_hub import hf_hub_download
from safetensors import safe_open
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
DATA = ("juletxara/xstory_cloze", "c4c2d88a1ec8b37fe22166d2a610f272726724b6")


def main():
    records = []
    for condition in ["noswitch", "switch", "par"]:
        for seed in [42, 43, 44]:
            manifest = json.loads((ROOT / "artifacts/model_manifests" / f"macaroni__{condition}__s{seed}.json").read_text())
            path = Path(manifest["path"])
            config = json.loads((path / "config.json").read_text())
            with safe_open(str(path / "model.safetensors"), framework="numpy") as weights:
                dtypes = sorted({weights.get_slice(k).get_dtype() for k in weights.keys()})
            assert dtypes == ["F32"], dtypes
            digest = hashlib.sha256()
            with (path / "model.safetensors").open("rb") as source:
                for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
                    digest.update(chunk)
            records.append({"manifest": manifest, "tokenizer_sha256": hashlib.sha256((path / "tokenizer.json").read_bytes()).hexdigest(),
                            "weight_sha256": digest.hexdigest(), "config": config, "weight_dtypes": dtypes})
    assert len({r["tokenizer_sha256"] for r in records}) == 1
    assert len({r["weight_sha256"] for r in records}) == 9
    fields = ["n_positions", "n_layer", "n_head", "n_embd", "vocab_size"]
    assert len({tuple(r["config"][k] for k in fields) for r in records}) == 1
    tokenizer = Tokenizer.from_file(str(Path(records[0]["manifest"]["path"]) / "tokenizer.json"))
    roundtrip = {}
    for lang in ["en", "zh"]:
        path = hf_hub_download(DATA[0], f"spring2016.val.{lang}.tsv.split_20_80_eval.tsv", repo_type="dataset", revision=DATA[1])
        with open(path) as source:
            rows = list(csv.DictReader(source, delimiter="\t"))
        texts = [r[key] for r in rows for key in ["input_sentence_1", "input_sentence_2", "input_sentence_3", "input_sentence_4", "sentence_quiz1", "sentence_quiz2"]]
        assert all(tokenizer.decode(tokenizer.encode(t, add_special_tokens=False).ids) == t for t in texts)
        roundtrip[lang] = {"stories": len(rows), "text_fields_checked": len(texts), "lossless": True}
    result = {"models": records, "data": DATA, "token_roundtrip": roundtrip,
              "limits": "Distinct final weights and matching architecture/tokenizer do not verify common initial weights or equal processed-token exposure."}
    (ROOT / "results/p3_macaroni_artifact_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"models": len(records), "roundtrip": roundtrip}), flush=True)


if __name__ == "__main__":
    main()
