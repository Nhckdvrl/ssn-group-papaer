"""R0 (metadata level): audit every HF branch of the Pythia-70M population without downloading weights.

For each repo (canonical pythia-70m, pythia-70m-deduped, pythia-70m-seed1..9) and every step branch:
  - branch commit sha;
  - which weight files exist (model.safetensors / pytorch_model.bin) and their LFS sha256 + size;
  - config.json / tokenizer.json git oids.
Flags:
  - missing step branches relative to the documented 154-step grid;
  - branches without any weight file;
  - weight blobs shared by more than one branch of the same repo (step0 == step1 is a known,
    explained case: lr = 0 at the first optimizer step, EleutherAI/pythia#83);
  - step-branch model.safetensors identical to main's (the "safetensors carries main" trap);
  - weight blobs shared across different repos (a seed repo serving another run's file).
Writes results/r0_hf_metadata_70m.json.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPOS = ["EleutherAI/pythia-70m", "EleutherAI/pythia-70m-deduped"] + [
    f"EleutherAI/pythia-70m-seed{i}" for i in range(1, 10)
]
STEPS = [0] + [2**i for i in range(10)] + list(range(1000, 143001, 1000))  # 154 documented checkpoints
OUT = Path(__file__).resolve().parents[1] / "results" / "r0_hf_metadata_70m.json"


TOKEN_FILE = Path.home() / ".cache" / "huggingface" / "token"
HEADERS = {"Authorization": f"Bearer {TOKEN_FILE.read_text().strip()}"} if TOKEN_FILE.exists() else {}
CACHE = OUT.parent / ".r0_api_cache"  # resumable; git-ignored


def get_json(url, tries=12):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:  # 429 rate limit: back off
            if t == tries - 1:
                raise
            wait = int(e.headers.get("Retry-After") or 0) or 10 * (t + 1)
            time.sleep(min(wait, 120))
        except Exception:
            if t == tries - 1:
                raise
            time.sleep(5 * (t + 1))


def tree(repo, rev):
    CACHE.mkdir(exist_ok=True)
    cf = CACHE / f"{repo.replace('/', '__')}__{rev}.json"
    if cf.exists():
        items = json.loads(cf.read_text())
    else:
        items = get_json(f"https://huggingface.co/api/models/{repo}/tree/{rev}")
        cf.write_text(json.dumps(items))
    files = {}
    for it in items:
        if it.get("type") != "file":
            continue
        files[it["path"]] = {
            "git_oid": it["oid"],
            "size": it["size"],
            "lfs_sha256": (it.get("lfs") or {}).get("oid"),
        }
    return files


def audit_repo(repo):
    refs = get_json(f"https://huggingface.co/api/models/{repo}/refs")
    branches = {b["name"]: b["targetCommit"] for b in refs["branches"]}
    revs = ["main"] + [f"step{s}" for s in STEPS if f"step{s}" in branches]
    with ThreadPoolExecutor(2) as ex:
        trees = dict(zip(revs, ex.map(lambda r: tree(repo, r), revs)))
    rows = {}
    for rev in revs:
        f = trees[rev]
        rows[rev] = {
            "commit": branches.get(rev),
            "safetensors_sha256": (f.get("model.safetensors") or {}).get("lfs_sha256"),
            "safetensors_size": (f.get("model.safetensors") or {}).get("size"),
            "bin_sha256": (f.get("pytorch_model.bin") or {}).get("lfs_sha256"),
            "bin_size": (f.get("pytorch_model.bin") or {}).get("size"),
            "config_oid": (f.get("config.json") or {}).get("git_oid"),
            "tokenizer_oid": (f.get("tokenizer.json") or {}).get("git_oid"),
        }
    missing = [s for s in STEPS if f"step{s}" not in branches]
    extra = sorted(set(branches) - {f"step{s}" for s in STEPS} - {"main"})
    flags = []
    for rev, r in rows.items():
        if not r["safetensors_sha256"] and not r["bin_sha256"]:
            flags.append(f"{rev}: no weight file")
    for kind in ("safetensors_sha256", "bin_sha256"):
        groups = defaultdict(list)
        for rev, r in rows.items():
            if r[kind]:
                groups[r[kind]].append(rev)
        for sha, rs in groups.items():
            steps_only = [x for x in rs if x != "main"]
            if len(steps_only) > 1 and set(steps_only) != {"step0", "step1"}:
                flags.append(f"{kind} shared by {rs}")
        main_sha = rows["main"][kind]
        if main_sha:
            same = [rev for rev, r in rows.items() if rev not in ("main", "step143000") and r[kind] == main_sha]
            if same:
                flags.append(f"{kind}: {len(same)} step branches identical to main: {same[:12]}")
    return {"repo": repo, "n_branches": len(branches), "missing_steps": missing,
            "extra_branches": extra, "flags": flags, "revisions": rows}


def main():
    results = [audit_repo(r) for r in REPOS]
    # cross-repo duplicate weight blobs
    owner = defaultdict(set)
    for res in results:
        for rev, r in res["revisions"].items():
            for k in ("safetensors_sha256", "bin_sha256"):
                if r[k]:
                    owner[r[k]].add((res["repo"], rev))
    cross = [sorted(v) for v in owner.values() if len({x[0] for x in v}) > 1]
    out = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "documented_steps": STEPS,
           "cross_repo_shared_blobs": cross, "repos": results}
    OUT.write_text(json.dumps(out, indent=1))
    for res in results:
        tok = {r["tokenizer_oid"] for r in res["revisions"].values()}
        cfg = {r["config_oid"] for r in res["revisions"].values()}
        n_st = sum(bool(r["safetensors_sha256"]) for r in res["revisions"].values())
        n_bin = sum(bool(r["bin_sha256"]) for r in res["revisions"].values())
        print(f"{res['repo']}: branches={res['n_branches']} missing={res['missing_steps']} extra={res['extra_branches'][:5]} "
              f"safetensors={n_st} bin={n_bin} tokenizer_oids={len(tok)} config_oids={len(cfg)}")
        for fl in res["flags"]:
            print("   FLAG", fl)
    print("cross-repo shared blobs:", cross[:10])


if __name__ == "__main__":
    sys.exit(main())
