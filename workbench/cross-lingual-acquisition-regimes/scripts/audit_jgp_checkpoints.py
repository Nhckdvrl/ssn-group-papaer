"""Resolve paper-selected weight aliases against released step branches."""
import json
from pathlib import Path

from huggingface_hub import HfApi


def main():
    api = HfApi()
    result = {}
    for name in ["No-Parallel", "Multilingual", "Parallel-Non-Adjacent", "Parallel-Distributed"]:
        repo = "nusnlp/JGP-" + name
        refs = api.list_repo_refs(repo).branches
        records = []
        for ref in refs:
            info = api.model_info(repo, revision=ref.target_commit, files_metadata=True)
            weights = {f.rfilename: f.lfs.sha256 for f in info.siblings
                       if f.rfilename.endswith((".bin", ".safetensors")) and f.lfs}
            assert weights, (repo, ref.name)
            records.append({"branch": ref.name, "revision": ref.target_commit, "weight_sha256": weights})
        selected = next(r for r in records if r["branch"] == "main")
        matches = [r["branch"] for r in records if r["branch"] != "main" and r["weight_sha256"] == selected["weight_sha256"]]
        result[repo] = {"records": records, "selected_weight_matches_steps": matches}
        print(repo, "selected matches", matches, flush=True)
    root = Path(__file__).resolve().parents[1]
    (root / "results" / "jgp_checkpoint_audit.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
