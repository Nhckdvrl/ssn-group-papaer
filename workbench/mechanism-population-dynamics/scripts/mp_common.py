"""Shared loading utilities for the mechanism-population workbench.

Checkpoints are always loaded from `pytorch_model.bin` (never `model.safetensors`): some Pythia step
branches ship main's safetensors (EleutherAI/pythia#205; our memory note on pythia-2.8b step36000),
and `from_pretrained` prefers safetensors. Every load is checked against the R0 manifest.
"""
import hashlib
import json
import os
from pathlib import Path

import torch

WB = Path(__file__).resolve().parents[1]
RESULTS = WB / "results"
CACHE = Path(os.environ.get("MECHPOP_CACHE", "/home/xiang/mechpop_cache"))
HF_CACHE = CACHE / "hf"
PARENT_CODE = CACHE / "icl-heads"  # github.com/kayoyin/icl-heads @ c0ba06e
PARENT_COMMIT = "c0ba06e"
MANIFEST = RESULTS / "artifact_manifest_70m.json"
META = RESULTS / "r0_hf_metadata_70m.json"

os.environ.setdefault("HF_HUB_CACHE", str(HF_CACHE))


def rev_name(step):
    return "main" if step is None else f"step{step}"


def sha256_file(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def fetch(repo, step, files=("config.json", "pytorch_model.bin")):
    from huggingface_hub import hf_hub_download

    return {f: hf_hub_download(repo, f, revision=rev_name(step), cache_dir=str(HF_CACHE)) for f in files}


def load_state_dict_bin(path):
    return torch.load(path, map_location="cpu", weights_only=True)


def accepted(repo, step):
    man = json.loads(MANIFEST.read_text())
    for row in man["checkpoints"]:
        if row["model_id"] == repo and row["step"] == step:
            return row
    raise KeyError(f"{repo}@{step} not in manifest")


def load_hf_model(repo, step, dtype=torch.float32, check_manifest=True):
    """GPTNeoXForCausalLM from the verified pytorch_model.bin of `repo@step`."""
    from transformers import GPTNeoXConfig, GPTNeoXForCausalLM

    if check_manifest:
        row = accepted(repo, step)
        assert row["accepted"], f"{repo}@{step} rejected: {row['reject_reason']}"
    paths = fetch(repo, step)
    if check_manifest:
        assert sha256_file(paths["pytorch_model.bin"]) == row["bin_sha256"], "bin sha256 mismatch vs manifest"
    cfg = GPTNeoXConfig.from_pretrained(os.path.dirname(paths["config.json"]))
    model = GPTNeoXForCausalLM(cfg)
    sd = load_state_dict_bin(paths["pytorch_model.bin"])
    missing, unexpected = model.load_state_dict(sd, strict=False)
    # only non-persistent attention buffers may be absent/extra
    buffers = ("attention.bias", "attention.masked_bias", "rotary_emb.inv_freq")
    bad = [k for k in list(missing) + list(unexpected) if not k.endswith(buffers)]
    assert not bad, f"state-dict mismatch: {bad[:10]}"
    return model.to(dtype).eval()


def load_tl_model(repo, step, device="cuda"):
    """HookedTransformer with parent-default processing (fold_ln / center_* = True), fp32."""
    from transformer_lens import HookedTransformer

    hf = load_hf_model(repo, step)
    import re

    tl_name = re.sub(r"-seed\d+$", "", repo)  # PolyPythia seeds share the canonical architecture/tokenizer
    model = HookedTransformer.from_pretrained(tl_name, hf_model=hf, device=device, dtype=torch.float32)
    model.eval()
    return model
