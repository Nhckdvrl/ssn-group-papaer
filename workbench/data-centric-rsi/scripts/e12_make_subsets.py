"""Deterministic E12 10k policy subsets after the complete row-identity audit.

No benchmark score enters this script. It refuses to select from an Arrow
snapshot that has not matched every original JSON ID and normalized dialogue.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
from collections import Counter
from pathlib import Path

from e12_icons_mapping_audit import row_key


VISUAL_SOURCES = ("coco", "gqa", "ocr_vqa", "textvqa", "vg")
POLICIES = ("random", "balanced", "icons_exact", "ards", "icons_released_map")
BUDGET = 10000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def hash_lines(values: list[str]) -> str:
    return hashlib.sha256(("\n".join(values) + "\n").encode()).hexdigest()


def policies_from_sources(original: list[dict], root: Path) -> dict[str, set[int]]:
    all_positions = set(range(len(original)))
    groups = {name: set() for name in VISUAL_SOURCES}
    for i, row in enumerate(original):
        image = row.get("image")
        if image:
            prefix = image.split("/", 1)[0]
            if prefix in groups:
                groups[prefix].add(i)

    icons = json.loads((root / "icons_json/llava-icons-133k.json").read_text())
    exact_map: dict[str, list[int]] = {}
    released_lookup: dict[str, int] = {}
    arrow_idx = 0
    for i, row in enumerate(original):
        key = row_key(row)
        exact_map.setdefault(key, []).append(i)
        if "image" in row:
            released_lookup[str(row["id"])] = arrow_idx
            released_lookup[str(row["image"])] = arrow_idx
            arrow_idx += 1

    exact_positions: set[int] = set()
    released_positions: set[int] = set()
    for row in icons:
        matches = exact_map.get(row_key(row), [])
        if len(matches) != 1:
            raise ValueError(f"ICONS record has {len(matches)} exact original matches")
        exact_positions.add(matches[0])
        # Faithful diagnostic for the released Curation-Bench implementation.
        released = released_lookup.get(str(row["id"])) or released_lookup.get(
            str(row.get("image", ""))
        )
        if released is not None:
            released_positions.add(released)

    ards = json.loads((root / "ards_selected.json").read_text())
    # The released ARDS `global_id` is zero-based: every one of its 199,586
    # full records matches original[global_id], while none matches -1.
    ards_positions = {int(row["global_id"]) for row in ards}
    if not ards_positions or min(ards_positions) < 0 or max(ards_positions) >= len(original):
        raise ValueError("ARDS global IDs out of original JSON range")

    return {
        "random": all_positions,
        "balanced": set().union(*groups.values()),
        "icons_exact": exact_positions,
        "ards": ards_positions,
        "icons_released_map": released_positions,
    }


def select_positions(
    original: list[dict], policies: dict[str, set[int]], policy: str, seed: int
) -> list[int]:
    """Freeze sampling in one place for CPU audit and Arrow materialization."""
    if seed not in {17, 29, 43}:
        raise ValueError("E12 precommitted seeds are 17, 29, 43")
    if policy not in POLICIES:
        raise ValueError(f"Unknown E12 policy: {policy}")
    stable = sorted(range(len(original)), key=lambda i: (str(original[i]["id"]), row_key(original[i])))
    rng = random.Random(seed)
    if policy == "balanced":
        selected: set[int] = set()
        for name in VISUAL_SOURCES:
            pool = [
                i for i in stable
                if original[i].get("image", "").split("/", 1)[0] == name
            ]
            if len(pool) < 2000:
                raise ValueError(f"Too few {name} rows")
            selected.update(rng.sample(pool, 2000))
    else:
        pool = [i for i in stable if i in policies[policy]]
        if len(pool) < BUDGET:
            raise ValueError(f"{policy} has only {len(pool)} rows")
        selected = set(rng.sample(pool, BUDGET))
    if len(selected) != BUDGET:
        raise RuntimeError(f"{policy} selected {len(selected)} positions, expected {BUDGET}")
    return sorted(selected)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--ards-audit", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    parser.add_argument("--policies", nargs="+", choices=POLICIES, default=list(POLICIES))
    parser.add_argument("--seeds", nargs="+", type=int, default=[17])
    args = parser.parse_args()

    audit = json.loads(args.audit.read_text())
    n = int(audit["original_rows"])
    if (
        audit["first_shard_only"]
        or audit["arrow_rows"] != n
        or audit["same_position_count"] != n
        or audit["same_position_conversation_count"] != n
        or audit["same_id_multiset"] is not True
    ):
        raise RuntimeError("Full Arrow ID and dialogue identity audit has not passed")

    root = args.root
    original_file = root / "llava_json/llava_v1_5_mix665k.json"
    if sha256(original_file) != audit["source_json_sha256"]:
        raise RuntimeError("Original JSON changed after full audit")
    original = json.loads(original_file.read_text())
    if len(original) != n:
        raise RuntimeError("Original JSON count changed after full audit")
    policies = policies_from_sources(original, root)
    ards_report = json.loads(args.ards_audit.read_text())
    if (
        ards_report["original_rows"] != n
        or ards_report["candidate_global_id_offsets"]["0"].get("full_record", 0) != ards_report["ards_rows"]
    ):
        raise RuntimeError("ARDS global IDs have not been verified against their released records")

    from datasets import DatasetDict, concatenate_datasets, load_from_disk

    ds = load_from_disk(str(root / "llava_arrow"))
    if isinstance(ds, DatasetDict):
        ds = concatenate_datasets([ds[k] for k in sorted(ds)])
    if len(ds) != n:
        raise RuntimeError("Arrow row count changed after audit")

    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    args.out_root.mkdir(parents=True, exist_ok=True)
    for seed in args.seeds:
        if seed not in {17, 29, 43}:
            raise ValueError("E12 precommitted seeds are 17, 29, 43")
        for policy in args.policies:
            if policy == "icons_released_map" and seed != 17:
                raise ValueError("Released-map diagnosis seeds 29/43 require the prewritten ≥0.5 gate")
            positions = select_positions(original, policies, policy, seed)
            output = args.out_root / f"{policy}_s{seed}"
            if output.exists():
                raise FileExistsError(f"Refusing to overwrite frozen selection: {output}")
            subset = ds.select(positions)
            subset.save_to_disk(str(output))
            manifest = {
                "policy": policy,
                "seed": seed,
                "budget": BUDGET,
                "pool_rows": len(policies[policy]),
                "source_counts": dict(Counter(str(original[i].get("image", "text-only")).split("/", 1)[0] for i in positions)),
                "selected_positions_sha256": hash_lines([str(i) for i in positions]),
                "selected_full_records_sha256": hash_lines([row_key(original[i]) for i in positions]),
                "original_json_sha256": audit["source_json_sha256"],
                "arrow_id_dialogue_audit": str(args.audit),
                "arrow_dataset_revision": "235a8adf266bb6dc02a099dc0221d28dec058f54",
                "icons_dataset_revision": "c9b3bf7be76871575b739f28bed1cdc872db8e75",
                "code_git_sha": git_sha,
                "selector_script_sha256": sha256(Path(__file__)),
                "subset_path": str(output),
            }
            (output / "e12_selection_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
            print(json.dumps({k: v for k, v in manifest.items() if not k.endswith("sha256")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
