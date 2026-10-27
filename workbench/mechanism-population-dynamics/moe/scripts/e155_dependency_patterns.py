"""POST-HOC paired dependency patterns on the fixed common-success questions.

No model execution; do not use these selected questions as independent evidence.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

WB = Path(__file__).resolve().parents[1]
RESULT = WB / "results/e155"
RAW = Path.home() / "mechpop_cache/e155_native_task_branch_necessity"
LABELS = (
    "D fails; removing either R or S fails",
    "D fails; only D+S preserves success",
    "D fails; only D+R preserves success",
    "D fails; D+R and D+S each preserve success",
    "D works; D+R and D+S both fail",
    "D works; only D+S preserves success",
    "D works; only D+R preserves success",
    "D, D+R and D+S all preserve success",
)
SEED = 155201


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def estimate(values, subject):
    """Resample the two fixed subjects separately; equal subject macro."""
    groups = [np.asarray(values)[subject == s].astype(float) for s in (0, 1)]
    rng = np.random.default_rng(SEED)
    samples = [g[rng.integers(0, len(g), size=(1000, len(g)))].mean(1) for g in groups]
    return {
        "point": float(np.mean([g.mean() for g in groups])),
        "question_ci95": np.quantile(np.mean(samples, axis=0), [.025, .975]).tolist(),
        "subjects": {
            str(s): {"n": len(g), "point": float(g.mean()),
                     "question_ci95": np.quantile(b, [.025, .975]).tolist()}
            for s, (g, b) in enumerate(zip(groups, samples))
        },
    }


def analyze():
    arrays, provenance = [], {}
    for source in "PAB":
        path = RAW / f"scores_{source}.npz"
        manifest = json.loads((RESULT / f"manifest_{source}.json").read_text())
        digest = sha(path)
        assert digest == manifest["raw"]["sha256"]
        with np.load(path) as f:
            arrays.append({key: f[key].copy() for key in f.files})
        provenance[source] = {"path": str(path), "sha256": digest}
    first = arrays[0]
    for a in arrays[1:]:
        for key in ("gold", "subject", "conditions", "answer_tokens", "answer_chars"):
            assert np.array_equal(a[key], first[key]), key
    assert first["conditions"].tolist() == ["native", "routed_zero", "shared_zero", "all_moe_zero"]
    ll = np.stack([a["candidate_loglikelihood"] for a in arrays])
    assert ll.shape == (3, 4, 128, 4) and np.isfinite(ll).all()
    correct = ll.argmax(-1) == first["gold"][None, None, :]
    common = correct[:, 0].all(0)
    index = np.flatnonzero(common)
    subject = first["subject"][common]
    assert len(index) == 44 and [(subject == s).sum() for s in (0, 1)] == [36, 8]
    # Bits are D, D+R (S-zero), D+S (R-zero), from most to least significant.
    bits = correct[:, [3, 2, 1]][:, :, common].astype(np.int64)
    patterns = np.einsum("scq,c->sq", bits, np.array([4, 2, 1]))
    assert np.array_equal(bits, ((patterns[:, None, :] >> np.array([2, 1, 0])[None, :, None]) & 1))
    output = {
        "label": "POST-HOC descriptive extension of E155; no independent confirmation",
        "script_sha256": sha(__file__), "raw": provenance,
        "selection": "All P/A/B native raw argmax predictions equal gold; no intervention filtering",
        "n": len(index), "subject_counts": {str(s): int((subject == s).sum()) for s in (0, 1)},
        "pattern_bit_order": ["D", "D+R", "D+S"],
        "pattern_labels": {str(k): value for k, value in enumerate(LABELS)},
        "bootstrap": {"seed": SEED, "resamples": 1000, "unit": "paired question within fixed subject",
                      "aggregation": "equal subject macro; pooled counts separately labelled"},
        "sources": {}, "paired_differences": {}, "transitions": {}, "questions": [],
        "limits": "Whole-network branch removals can alter hidden states and routing. Patterns describe measured success under interventions, not knowledge fractions, semantic algorithms, or training causality. Native-success selection excludes intervention corrections.",
    }
    for i, source in enumerate("PAB"):
        output["sources"][source] = {
            "pooled_pattern_counts": np.bincount(patterns[i], minlength=8).tolist(),
            "subject_pattern_counts": {
                str(s): np.bincount(patterns[i, subject == s], minlength=8).tolist() for s in (0, 1)
            },
            "macro_pattern_proportions": {str(k): estimate(patterns[i] == k, subject) for k in range(8)},
            "macro_D_preserved": estimate(patterns[i] >= 4, subject),
        }
    for left, right in ((0, 1), (0, 2), (1, 2)):
        before, after = "PAB"[left], "PAB"[right]
        matrix = np.zeros((8, 8), dtype=int)
        np.add.at(matrix, (patterns[left], patterns[right]), 1)
        output["transitions"][f"{before}_to_{after}"] = {
            "rows_before_columns_after": matrix.tolist(),
            "subjects": {
                str(s): np.bincount((8 * patterns[left] + patterns[right])[subject == s], minlength=64).reshape(8, 8).tolist()
                for s in (0, 1)
            },
        }
        output["paired_differences"][f"{after}_minus_{before}"] = {
            str(k): estimate((patterns[right] == k).astype(float) - (patterns[left] == k), subject)
            for k in range(8)
        }
        assert matrix.sum() == 44
        assert np.array_equal(matrix.sum(1), np.bincount(patterns[left], minlength=8))
        assert np.array_equal(matrix.sum(0), np.bincount(patterns[right], minlength=8))
    for j, q in enumerate(index):
        output["questions"].append({
            "raw_question_index": int(q), "subject": int(subject[j]), "gold": int(first["gold"][q]),
            "sources": {s: {"pattern": int(patterns[i, j]), "correct_D_DR_DS": bits[i, :, j].tolist(),
                            "predictions_native_Rzero_Szero_D": ll[i, :, q].argmax(-1).tolist()}
                        for i, s in enumerate("PAB")},
        })
    # Reconstruct the previously reported common-success marginals exactly.
    assert bits[:, 1].sum(1).tolist() == [33, 31, 17]
    result_path = RESULT / "dependency_patterns_posthoc.json"
    result_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({s: output["sources"][s]["pooled_pattern_counts"] for s in "PAB"}))
    print(json.dumps({k: {c: v[c] for c in ("0", "1", "2", "3")} for k, v in output["paired_differences"].items()}))
    plot(patterns, subject)


def plot(patterns, subject):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap, BoundaryNorm
    from matplotlib.patches import Patch

    colors = ["#b43b3b", "#4e79a7", "#59a14f", "#9c79ad", "#f28e2b", "#86b9d7", "#a6cd8b", "#b8b8b8"]
    fig, ax = plt.subplots(figsize=(12.8, 4.4))
    fig.subplots_adjust(left=.10, right=.99, top=.80, bottom=.47)
    ax.imshow(patterns, aspect="auto", cmap=ListedColormap(colors), norm=BoundaryNorm(np.arange(-.5, 8.5), 8), interpolation="none")
    ax.set_yticks(range(3), ["Parent P", "Standard A", "Constrained B"])
    ax.set_xticks([])
    split = int((subject == 0).sum())
    ax.axvline(split - .5, color="black", linewidth=1.5)
    ax.text((split - 1) / 2, -.75, "Biology: 36 questions", ha="center", va="center")
    ax.text((split + 43) / 2, -.75, "Math: 8", ha="center", va="center")
    fig.suptitle("Same correct answers, paired changes in computational dependence", fontsize=14, y=.98)
    fig.text(.5, .875, "44 fixed questions answered correctly by all three native models; each column is the same question", ha="center", fontsize=10)
    legend = [Patch(facecolor=color, label=f"{k}: {label}") for k, (color, label) in enumerate(zip(colors, LABELS))]
    fig.legend(handles=legend, loc="lower left", bbox_to_anchor=(.10, .075), ncol=2, frameon=False, fontsize=8.5)
    fig.text(.10, .02, "POST-HOC; R/S are removed globally. Colors describe success under interventions, not semantic knowledge ownership.", fontsize=8)
    directory = RESULT / "figures"
    directory.mkdir(exist_ok=True)
    for suffix in ("png", "pdf"):
        fig.savefig(directory / f"common_success_dependency_patterns.{suffix}", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    analyze()
