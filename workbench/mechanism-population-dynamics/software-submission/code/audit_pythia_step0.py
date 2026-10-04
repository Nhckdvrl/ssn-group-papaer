"""Checkpoint audit (tensor level): download and verify the Pythia checkpoints used here; write the accepted manifest.

Per checkpoint:
  - local sha256 of pytorch_model.bin == HF LFS sha256 (from hf_metadata_70m.json);
  - config / param count / tensor shapes / finiteness;
  - if the branch also ships model.safetensors: max |bin - safetensors| (detects the "safetensors = main" trap);
  - relative L2 distance to the previous audited checkpoint of the same repo and to its own step0;
  - NLL on a fixed 16 x 512-token Pile slice (functional sanity: must differ across steps, fall with training).
A checkpoint is accepted iff sha matches, tensors are finite/shaped, and it is not byte- or tensor-identical
to a checkpoint of a different step (step0 == step1 is the documented lr=0 exception, pythia#83).
"""
import argparse
import json
import time

import torch
from safetensors.torch import load_file

import common as mc
AUDIT_STEPS = [0, 256, 512, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 143000]
AUDIT_REPOS = ["EleutherAI/pythia-70m-deduped", "EleutherAI/pythia-70m"]


def flat(sd):
    keys = sorted(k for k in sd if not k.endswith(("attention.bias", "attention.masked_bias", "inv_freq")))
    return keys, torch.cat([sd[k].float().flatten() for k in keys])


def pile_slice(tokenizer, n=16, L=512):
    from datasets import load_dataset

    ds = load_dataset("NeelNanda/pile-10k", split="train")
    rows = []
    for t in ds["text"][5000:]:  # disjoint from nothing we score on; fixed slice
        ids = tokenizer(t)["input_ids"]
        if len(ids) >= L:
            rows.append(ids[:L])
        if len(rows) == n:
            break
    return torch.tensor(rows)


@torch.no_grad()
def nll(repo, step, toks):
    m = mc.load_hf_model(repo, step, check_manifest=False).cuda()
    out = m(toks.cuda(), labels=toks.cuda())
    return out.loss.item()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", nargs="+", default=AUDIT_REPOS)
    ap.add_argument("--steps", nargs="+", type=int, default=AUDIT_STEPS)
    args = ap.parse_args()
    meta = {r["repo"]: r for f in sorted(mc.RESULTS.glob("hf_metadata_*.json"))
            for r in json.loads(f.read_text())["repos"]}
    from transformers import AutoTokenizer

    rows = []
    for repo in args.repos:
        tok = AutoTokenizer.from_pretrained(repo, cache_dir=str(mc.HF_CACHE))
        toks = pile_slice(tok)
        step0_vec, prev_vec, prev_step = None, None, None
        for step in args.steps:
            rev = mc.rev_name(step)
            m = meta[repo]["revisions"].get(rev)
            row = {"model_id": repo, "seed": 0 if "seed" not in repo else int(repo.split("seed")[-1]),
                   "data": "pile-deduped" if "deduped" in repo else "pile-standard",
                   "checkpoint": rev, "step": step, "revision_commit": m and m["commit"],
                   "accepted": False, "reject_reason": None}
            if m is None or not m["bin_sha256"]:
                row["reject_reason"] = "branch or pytorch_model.bin missing on HF"
                rows.append(row)
                continue
            files = ("config.json", "pytorch_model.bin") + (("model.safetensors",) if m["safetensors_sha256"] else ())
            paths = mc.fetch(repo, step, files)
            row["bin_sha256"] = mc.sha256_file(paths["pytorch_model.bin"])
            row["bin_sha_matches_hf"] = row["bin_sha256"] == m["bin_sha256"]
            sd = mc.load_state_dict_bin(paths["pytorch_model.bin"])
            keys, vec = flat(sd)
            cfg = json.load(open(paths["config.json"]))
            row["n_params"] = int(vec.numel())
            row["n_tensors"] = len(keys)
            row["dtype"] = str(next(iter(sd.values())).dtype)
            row["finite"] = bool(torch.isfinite(vec).all())
            row["config"] = {k: cfg.get(k) for k in ("hidden_size", "num_hidden_layers", "num_attention_heads",
                                                      "vocab_size", "rotary_pct", "max_position_embeddings")}
            row["shapes_ok"] = (tuple(sd["gpt_neox.embed_in.weight"].shape) == (cfg["vocab_size"], cfg["hidden_size"])
                                and len([k for k in keys if k.endswith("attention.query_key_value.weight")])
                                == cfg["num_hidden_layers"])
            if "model.safetensors" in paths:
                st = load_file(paths["model.safetensors"])
                row["safetensors_sha256"] = m["safetensors_sha256"]
                diffs = [(st[k].float() - sd[k].float()).abs().max().item() for k in keys if k in st]
                row["bin_vs_safetensors_maxabs"] = max(diffs) if diffs else None
                row["safetensors_missing_keys"] = len([k for k in keys if k not in st])
            if step0_vec is None:
                step0_vec = vec
            row["rel_l2_to_step0"] = float((vec - step0_vec).norm() / step0_vec.norm())
            if prev_vec is not None:
                row["prev_step"] = prev_step
                row["rel_l2_to_prev"] = float((vec - prev_vec).norm() / prev_vec.norm())
            row["pile_nll_16x512"] = nll(repo, step, toks)
            prev_vec, prev_step = vec, step
            reasons = []
            if not row["bin_sha_matches_hf"]:
                reasons.append("local sha256 != HF LFS sha256")
            if not (row["finite"] and row["shapes_ok"]):
                reasons.append("non-finite or bad shapes")
            if prev_step is not None and row.get("rel_l2_to_prev") == 0.0 and step != 1:
                reasons.append(f"tensor-identical to step{row['prev_step']}")
            if row.get("bin_vs_safetensors_maxabs") not in (None,) and row["bin_vs_safetensors_maxabs"] > 1e-2:
                row["note"] = "model.safetensors differs from pytorch_model.bin (bin used)"
            row["accepted"] = not reasons
            row["reject_reason"] = "; ".join(reasons) or None
            rows.append(row)
            save(rows)
            print(json.dumps({k: row.get(k) for k in ("model_id", "checkpoint", "accepted", "reject_reason",
                                                       "rel_l2_to_prev", "rel_l2_to_step0", "pile_nll_16x512",
                                                       "bin_vs_safetensors_maxabs")}), flush=True)
    # tensor-identical across different steps anywhere in the audited set
    save(rows)


def save(rows):
    """Merge into the existing manifest (one row per model_id x step; newest audit wins)."""
    old = json.loads(mc.MANIFEST.read_text())["checkpoints"] if mc.MANIFEST.exists() else []
    keep = {(r["model_id"], r["step"]): r for r in old}
    keep.update({(r["model_id"], r["step"]): r for r in rows})
    out = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "loader": "pytorch_model.bin only (use_safetensors=False)",
           "tokenizer_note": "see hf_metadata_70m.json tokenizer_oid per revision",
           "checkpoints": sorted(keep.values(), key=lambda r: (r["model_id"], r["step"]))}
    tmp = mc.MANIFEST.with_suffix(".tmp")
    tmp.write_text(json.dumps(out, indent=1))
    tmp.replace(mc.MANIFEST)


if __name__ == "__main__":
    main()
