"""Pin released intervention checkpoints in the standard Hugging Face cache."""
import argparse
import json
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download

ROOT = Path(__file__).resolve().parents[1]
JGP = ["No-Parallel", "Multilingual", "Parallel-Non-Adjacent", "Parallel-Distributed", "Parallel-Last-all"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=["jgp", "monoweb", "macaroni"], required=True)
    parser.add_argument("--language", default="de", choices=["de", "es", "fr"])
    parser.add_argument("--step", default="0034000")
    parser.add_argument("--revision", default="main", help="JGP branch/revision; resolve to immutable commit")
    parser.add_argument("--jgp-variants", nargs="+", choices=JGP, default=JGP)
    parser.add_argument("--monoweb-variants", nargs="+", choices=["monoweb", "onlyparallel", "baseline", "onlycodeswitch"], default=["monoweb", "onlyparallel", "baseline"])
    parser.add_argument("--macaroni-variants", nargs="+", choices=["noswitch", "switch", "par", "salad", "word", "sent", "curriculum", "curriculum_noswitch"], default=["noswitch", "switch", "par"])
    parser.add_argument("--seeds", nargs="+", type=int, choices=[42, 43, 44], default=[42, 43, 44])
    args = parser.parse_args()
    api = HfApi()
    jobs = [(f"nusnlp/JGP-{name}", None) for name in args.jgp_variants] if args.family == "jgp" else [
        ("UCLNLP/monoweb", f"ckpt_exp_en_{args.language}_{variant}/iter_{args.step}/hf_model")
        for variant in args.monoweb_variants
    ]
    folder = ROOT / "artifacts" / "model_manifests"
    folder.mkdir(parents=True, exist_ok=True)
    if args.family == "macaroni":
        for variant in args.macaroni_variants:
            for seed in args.seeds:
                branch = variant if seed == 42 else f"{variant}-s{seed}"
                repo = "drooryck/multilingual-macaroni-models"
                info = api.model_info(repo, revision=branch)
                print(f"Caching {repo} {branch} at {info.sha}", flush=True)
                path = snapshot_download(repo, revision=info.sha, allow_patterns=["*.json", "*.safetensors"], max_workers=4)
                record = {"repo": repo, "revision": info.sha, "branch": branch, "condition": variant, "seed": seed, "path": path}
                (folder / f"macaroni__{variant}__s{seed}.json").write_text(json.dumps(record, indent=2) + "\n")
                print(json.dumps(record), flush=True)
        return
    for repo, subfolder in jobs:
        info = api.model_info(repo, revision=args.revision if args.family == "jgp" else "main")
        patterns = [f"{subfolder}/*"] if subfolder else ["*.json", "*.safetensors", "*.model", "*.bin"]
        print(f"Caching {repo} {subfolder} at {info.sha}", flush=True)
        path = snapshot_download(repo, revision=info.sha, allow_patterns=patterns, max_workers=4)
        record = {"repo": repo, "revision": info.sha, "subfolder": subfolder, "path": str(Path(path) / subfolder) if subfolder else path}
        name = repo.replace("/", "__") + ("__" + subfolder.split("/")[0] if subfolder else "")
        if args.family == "jgp" and args.revision != "main":
            name += "__" + args.revision.replace("/", "_")
        elif args.family == "monoweb":
            name += "__" + args.step
        (folder / f"{name}.json").write_text(json.dumps(record, indent=2) + "\n")
        print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()
