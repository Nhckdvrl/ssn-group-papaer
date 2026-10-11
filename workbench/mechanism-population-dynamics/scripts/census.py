"""Generic head-role census (the E35 measurement, family-agnostic). Used by E44 (Pythia) and E45 (DataDecide sizes).

Maps ([layer x head]) exactly as in E35:
  M1 induction   - attention from the 2nd copy of a 128-token random block to the token after its 1st occurrence
  M2 prev-token  - attention to t-1 on 50 natural texts (two halves -> reliability)
  M3 sink        - attention to position 0 on the same texts
  M4 retrieval   - attention from the last prompt token to the distractor in the E28 knowledge-conflict prompts
Usage:
  census.py --family hf --repo EleutherAI/pythia-160m --rev step143000 --out e44 --name pythia-160m__std
  census.py --family dd --repo allenai/DataDecide-c4-90M --rev step29901-seed-default --out e45 --name 90M__c4__default
"""
import argparse
import json
import os

import numpy as np
import torch

import mp_common as mc

THR = {"M1": 0.3, "M2": 0.5, "M3": 0.5, "M4": 0.2}


def load(family, repo, rev, dtype=torch.bfloat16):
    if family == "dd":
        import dd_common as dd
        return dd.load(repo, rev, dtype=dtype, attn="eager")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(repo, revision=rev, cache_dir=str(mc.HF_CACHE))
    if tok.eos_token is None:  # e.g. pythia-1b-deduped ships a tokenizer without special tokens set
        tok.eos_token = tok.bos_token = "<|endoftext|>"
    model = AutoModelForCausalLM.from_pretrained(repo, revision=rev, cache_dir=str(mc.HF_CACHE), torch_dtype=dtype,
                                                 attn_implementation="eager").cuda().eval()
    return model, tok


def n_layers_heads(model):
    c = model.config
    return c.num_hidden_layers, c.num_attention_heads


_STATIC = {}


def static(tok):
    """Probe material that does not depend on the model (cached per tokenizer vocabulary in batch mode)."""
    key = (tok.__class__.__name__, len(tok))
    if key not in _STATIC:
        from e35_census import natural_texts
        import e26_factorial as e26
        import e28_gating as e28
        R, ix = e28.items()
        enc = []
        for i in ix:
            cells = e26.build(R[i])[0]
            enc += [e28.encode(tok, cells[c], R[i]["dist"]) for c in ("c1_decl", "c1_qa")]
        _STATIC[key] = (natural_texts(tok), enc)
    return _STATIC[key]


@torch.no_grad()
def measure(model, tok, bs=20):
    L, H = n_layers_heads(model)
    dev = next(model.parameters()).device
    eos = tok.eos_token_id if tok.eos_token_id is not None else tok.convert_tokens_to_ids("<|endoftext|>")
    g = torch.Generator().manual_seed(0)
    first = torch.randint(1000, 40000, (200, 128), generator=g)
    ids = torch.cat([torch.full((200, 1), eos), first, first], 1)
    M1, l1, l2 = torch.zeros(L, H), [], []
    q = torch.arange(129, 257)
    for i in range(0, 200, bs):
        x = ids[i:i + bs].to(dev)
        out = model(x, output_attentions=True)
        M1 += torch.stack([a[:, :, q, q - 127].float().mean((0, 2)).cpu() for a in out.attentions]) * x.shape[0] / 200
        lp = out.logits.float().log_softmax(-1)
        nll = -lp[:, :-1].gather(-1, x[:, 1:, None])[..., 0]
        l1.append(nll[:, 1:128].mean().item())   # first copy (unpredictable)
        l2.append(nll[:, 129:].mean().item())    # second copy (copyable)
    T, enc = static(tok)
    halves = {}
    for h, docs in (("a", T[:25]), ("b", T[25:])):
        m2, m3 = torch.zeros(L, H), torch.zeros(L, H)
        x = torch.tensor(docs, device=dev)
        out = model(x, output_attentions=True)
        t = torch.arange(2, x.shape[1])
        for li, a in enumerate(out.attentions):
            m2[li] = a[:, :, t, t - 1].float().mean((0, 2)).cpu()
            m3[li] = a[:, :, 2:, 0].float().mean((0, 2)).cpu()
        halves[h] = (m2, m3)
    M2 = (halves["a"][0] + halves["b"][0]) / 2
    M3 = (halves["a"][1] + halves["b"][1]) / 2
    M4 = torch.zeros(L, H)
    for pid, pos in enc:
        out = model(torch.tensor([pid], device=dev), output_attentions=True)
        M4 += torch.stack([a[0, :, -1, pos].float().cpu() for a in out.attentions]) / len(enc)
    rel = lambda a, b: float(np.corrcoef(a.flatten().numpy(), b.flatten().numpy())[0, 1])
    res = {"L": L, "H": H, "loss_first": float(np.mean(l1)), "copy_loss_second": float(np.mean(l2)),
           "maps": {k: v.numpy().round(5).tolist() for k, v in (("M1", M1), ("M2", M2), ("M3", M3), ("M4", M4))},
           "reliability_M2": rel(halves["a"][0], halves["b"][0]), "reliability_M3": rel(halves["a"][1], halves["b"][1])}
    res["copy_gain"] = res["loss_first"] - res["copy_loss_second"]
    for k, v in (("M1", M1), ("M2", M2), ("M3", M3), ("M4", M4)):
        res[f"{k}_max"] = float(v.max())
        res[f"{k}_n_over"] = int((v > THR[k]).sum())
    return res


def available(family, repo, rev):
    """True only if the weights themselves are complete in the cache (the snapshot folder alone is not enough:
    it appears as soon as the first small file of a concurrent download lands)."""
    from pathlib import Path
    from huggingface_hub import snapshot_download
    try:
        p = Path(snapshot_download(repo, revision=rev, cache_dir=str(mc.HF_CACHE), local_files_only=True,
                                   allow_patterns=["*.json", "*.safetensors"] if family == "dd" else None))
    except Exception:
        return False
    for idx in (p / "model.safetensors.index.json", p / "pytorch_model.bin.index.json"):
        if idx.exists():
            need = set(json.loads(idx.read_text())["weight_map"].values())
            return all((p / f).exists() for f in need)
    return (p / "model.safetensors").exists() or (family == "hf" and (p / "pytorch_model.bin").exists())


def batch(jobs, worker, nworkers):
    """Loop over a job file (lines: family repo rev out name); only jobs whose weights are already downloaded
    (by prefetch.py); claim via mkdir; repeat until every job of this worker's share is done."""
    import time
    lines = [l.split() for l in open(jobs) if l.strip()]
    mine = [l for j, l in enumerate(lines) if j % nworkers == worker]
    while True:
        left = 0
        for fam, repo, rev, out, name in mine:
            d = mc.RESULTS / out
            if (d / f"{name}.json").exists():
                continue
            left += 1
            if not available(fam, repo, rev):
                continue
            t0 = time.time()
            try:
                model, tok = load(fam, repo, rev)
                res = measure(model, tok)
            except Exception as e:
                print("ERROR", name, repr(e)[:200], flush=True)
                continue
            res.update({"repo": repo, "rev": rev, "family": fam})
            d.mkdir(exist_ok=True)
            (d / f"{name}.json").write_text(json.dumps(res))
            print(name, f"{time.time() - t0:.0f}s", {k: round(v, 3) for k, v in res.items() if k.endswith("_max")},
                  flush=True)
            del model
            torch.cuda.empty_cache()
        if left == 0:
            return
        time.sleep(60)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", choices=["hf", "dd"])
    ap.add_argument("--repo")
    ap.add_argument("--rev")
    ap.add_argument("--out")
    ap.add_argument("--name")
    ap.add_argument("--jobs")
    ap.add_argument("--worker", type=int, default=0)
    ap.add_argument("--nworkers", type=int, default=1)
    a = ap.parse_args()
    if a.jobs:
        return batch(a.jobs, a.worker, a.nworkers)
    out_dir = mc.RESULTS / a.out
    out_dir.mkdir(exist_ok=True)
    f = out_dir / f"{a.name}.json"
    if f.exists():
        print("exists", f.name)
        return
    model, tok = load(a.family, a.repo, a.rev)
    res = measure(model, tok)
    res.update({"repo": a.repo, "rev": a.rev, "family": a.family})
    f.write_text(json.dumps(res))
    print(a.name, {k: round(v, 3) for k, v in res.items() if k.endswith(("_max", "_gain")) or k.startswith("reliab")},
          flush=True)


if __name__ == "__main__":
    main()
