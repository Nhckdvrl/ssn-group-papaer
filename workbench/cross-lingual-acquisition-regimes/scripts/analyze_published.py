"""Reconstruct shared-task effects, without pooling incomparable benchmarks."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Transcribed from JGP Tables 12/13 and OpenSeal Tables 10/11/12.
ROWS = [
    ("JGP", "1.1B", "id", "XCOPA", "non-adjacent", "distributed", 52.40, 55.20, 50.0),
    ("JGP", "1.1B", "zh", "XCOPA", "non-adjacent", "distributed", 51.00, 52.00, 50.0),
    ("JGP", "1.1B", "id", "XStoryCloze", "non-adjacent", "distributed", 50.43, 52.88, 50.0),
    ("JGP", "1.1B", "zh", "XStoryCloze", "non-adjacent", "distributed", 49.37, 49.17, 50.0),
    ("JGP", "1.1B", "zh", "XNLI", "non-adjacent", "distributed", 33.57, 34.90, 100 / 3),
    ("JGP", "1.1B", "zh", "XWinograd", "non-adjacent", "distributed", 59.13, 57.54, 50.0),
]
OPENSEAL = {
    "1B": {
        "XNLI": {"en": (52.77, 52.97), "th": (39.42, 44.49), "vi": (41.86, 44.23), "zh": (39.08, 34.67)},
        "XCOPA": {"en": (76.60, 77.40), "id": (63.40, 61.20), "ta": (55.40, 54.60), "th": (57.20, 55.80), "vi": (65.40, 61.60), "zh": (58.40, 59.40)},
        "PAWS-X": {"en": (58.50, 61.15), "zh": (47.00, 53.30)},
    },
    "7B": {
        "XNLI": {"en": (52.61, 52.10), "th": (45.45, 47.50), "vi": (47.76, 47.33), "zh": (37.11, 34.65)},
        "XCOPA": {"en": (86.00, 85.00), "id": (73.60, 74.00), "ta": (61.60, 59.60), "th": (61.60, 60.00), "vi": (72.80, 73.80), "zh": (66.20, 68.80)},
        "PAWS-X": {"en": (66.45, 70.10), "zh": (53.70, 59.30)},
    },
}


def main():
    rows = list(ROWS)
    for size, tasks in OPENSEAL.items():
        for task, languages in tasks.items():
            for language, (base, treated) in languages.items():
                rows.append(("OpenSeal", size, language, task, "multilingual", "parallel-only", base, treated, 100 / 3 if task == "XNLI" else 50))
    folder = ROOT / "results"
    folder.mkdir(exist_ok=True)
    fields = ["parent", "size", "language", "task", "control", "intervention", "control_accuracy", "intervention_accuracy", "chance", "delta_pp", "control_above_chance_pp"]
    with (folder / "p1_published_effects.csv").open("w") as output:
        writer = csv.writer(output)
        writer.writerow(fields)
        for row in rows:
            writer.writerow([*row, round(row[7] - row[6], 2), round(row[6] - row[8], 2)])
    summary = {"provenance": "Published aggregate tables; no item-level significance inferred", "jgp_pairing_shared_tasks": {}, "openseal_delta_macro": {}}
    for language in ["id", "zh"]:
        subset = [row for row in ROWS if row[2] == language and row[3] in ["XCOPA", "XStoryCloze"]]
        summary["jgp_pairing_shared_tasks"][language] = round(sum(row[7] - row[6] for row in subset) / len(subset), 3)
    for size, tasks in OPENSEAL.items():
        summary["openseal_delta_macro"][size] = {task: round(sum(b - a for a, b in languages.values()) / len(languages), 3) for task, languages in tasks.items()}
    (folder / "p1_published_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
