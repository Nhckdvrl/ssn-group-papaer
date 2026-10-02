#!/usr/bin/env python3
"""Keep native parent inputs; missing licensing/choice labels stay unknown."""
import argparse
import ast
import collections
import csv
import hashlib
import json
import subprocess
from pathlib import Path


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_csv(p):
    with Path(p).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    upstream = args.root / "upstream"
    out = args.root / "data"
    out.mkdir(exist_ok=True)
    report = {"parents": {}, "sdt_identifiability": "not established"}
    datasets = {}
    for name in ["MultiPragEval", "wavelength-eval", "lm-pragmatics"]:
        p = upstream / name
        report["parents"][name] = {
            "commit": subprocess.check_output(["git", "-C", str(p), "rev-parse", "HEAD"], text=True).strip(),
            "url": subprocess.check_output(["git", "-C", str(p), "remote", "get-url", "origin"], text=True).strip(),
        }
    p = upstream / "MultiPragEval" / "test_suite.csv"
    rows = read_csv(p)
    assert len({r["id"] for r in rows}) == len(rows)
    langs = ["english", "german", "korean", "chinese"]
    datasets["multiprageval"] = [{
        "dataset": "multiprageval", "item_id": r["id"], "language": lang,
        "phenomenon": r["type"], "condition": r["type"], "prompt": r[lang],
        "gold": r["answer"], "choices": list("ABCDE"),
        "inference_licensed": False if r["type"] == "literal" else None,
        "choice_is_inference": None, "human_distribution": None,
        "source_sha256": digest(p),
    } for r in rows for lang in langs]
    report["parents"]["MultiPragEval"].update({
        "rows": len(rows), "test_units": len(rows) * len(langs), "data_sha256": digest(p),
        "categories": dict(collections.Counter(r["type"] for r in rows)),
        "gold_counts": dict(collections.Counter(r["answer"] for r in rows)),
        "inference_choice_labels": False, "inference_script_published": False,
        "caution": "maxim category does not prove inference licensing; literal errors are not all false alarms",
    })
    p = upstream / "wavelength-eval" / "data" / "data.csv"
    rows = read_csv(p)
    datasets["wavelength"] = [{
        "dataset": "wavelength", "item_id": str(i), "language": "english",
        "phenomenon": "graded_concept", "condition": "listener", "source": r,
        "human_distribution": ast.literal_eval(r["response_list"]),
        "inference_licensed": None, "choice_is_inference": None, "source_sha256": digest(p),
    } for i, r in enumerate(rows)]
    assert all(len(x["human_distribution"]) == 40 for x in datasets["wavelength"])
    report["parents"]["wavelength-eval"].update({
        "rows": len(rows), "concept_pairs": len({(r["left"], r["right"]) for r in rows}),
        "human_responses": sum(len(x["human_distribution"]) for x in datasets["wavelength"]),
        "data_sha256": digest(p), "binary_license_labels": False,
    })
    datasets["hu"] = []
    files = {}
    for p in sorted((upstream / "lm-pragmatics" / "prompts").glob("*examples0.csv")):
        rows = read_csv(p)
        files[p.name] = {"rows": len(rows), "sha256": digest(p)}
        for r in rows:
            labels = ast.literal_eval(r["randomized_labels_complex"])
            gold = r["randomized_true_answer"]
            datasets["hu"].append({
                "dataset": "hu", "item_id": r["item_id"], "language": "english",
                "phenomenon": p.name.split("_prompts")[0],
                "condition": "no-story" if "no-story" in p.name else "original",
                "prompt": r["prompt"], "gold": gold, "seed": int(r["seed"]),
                "choices": [str(i + 1) for i in range(len(labels))], "option_labels": labels,
                "inference_licensed": True if labels[int(gold)-1] == "CorrectNonLiteral" else None,
                "choice_is_inference": None, "human_distribution": None, "source_sha256": digest(p),
            })
    report["parents"]["lm-pragmatics"].update({"prompt_files": files, "test_units": len(datasets["hu"]),
        "caution": "no-story is an ablation, not an unwarranted-inference label; published Control raw data has no ready-made prompt CSV"})
    report["normalized"] = {}
    for name, rows in datasets.items():
        p = out / f"{name}.jsonl"
        p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        report["normalized"][name] = {"rows": len(rows), "path": str(p), "sha256": digest(p)}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v["rows"] for k, v in report["normalized"].items()}))


if __name__ == "__main__":
    main()
