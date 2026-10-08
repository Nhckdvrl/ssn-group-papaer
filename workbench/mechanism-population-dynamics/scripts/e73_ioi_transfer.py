"""E73: do the head labels of a published circuit (IOI name movers) carry over to a sibling with the same
initialization but different data, and to independently initialized models with the same data?
Protocol: experiments/E73-*.md. IOI prompts and measurements as in e14_ioi.py (Tigges et al.'s generator, N = 200).

  e73_ioi_transfer.py --size 160m      # measure all models of a size, then the transfer ablations
  e73_ioi_transfer.py --analyze
Per model (results/e73/<model>.json): direct logit attribution of every head at END (IO - S), END->IO attention,
clean logit difference, and the logit difference after mean-ablating (ABC reference) given head sets: the model's
own top-k, the reference model's top-k, 20 random k-sets and 20 layer-matched random k-sets.
"""
import argparse
import json
import random
import re

import numpy as np
import torch

import mp_common as mc
from e14_ioi import build, logit_diff

OUT = mc.RESULTS / "e73"
STEP = 143000
KS = tuple(int(k) for k in __import__("os").environ.get("E73_KS", "3,5").split(","))
TAG = __import__("os").environ.get("E73_TAG", "")  # e.g. "_k10" for the larger-k rerun


def models(size):
    m = [f"EleutherAI/pythia-{size}", f"EleutherAI/pythia-{size}-deduped"]
    if size in ("70m", "160m", "410m"):  # PolyPythias exist up to 410M
        m += [f"EleutherAI/pythia-{size}-seed{i}" for i in range(1, 10)]
    if size == "160m":
        m += [f"EleutherAI/pythia-{size}-data-seed{i}" for i in range(1, 4)]
    return m


def load(repo):
    from transformer_lens import HookedTransformer
    big = any(s in repo for s in ("-6.9b", "-12b"))
    dtype = torch.bfloat16 if big else torch.float32  # fp32 copies of 6.9B / 12B would not fit next to the HF model
    try:
        if big:
            raise KeyError(repo)
        return mc.load_tl_model(repo, STEP)
    except KeyError:  # not in the step manifest: the final checkpoint is the main revision itself
        from transformers import AutoModelForCausalLM
        hf = AutoModelForCausalLM.from_pretrained(repo, revision=f"step{STEP}", cache_dir=str(mc.HF_CACHE),
                                                  torch_dtype=dtype)
        tl = re.sub(r"-(data-|weight-)?seed\d+$", "", repo.split("/")[1])
        tl = "EleutherAI/" + tl
        return HookedTransformer.from_pretrained(tl, hf_model=hf, device="cuda", dtype=dtype).eval()


def measure(model, head_sets):
    ioi, abc = build(model)
    L, H = model.cfg.n_layers, model.cfg.n_heads
    end = torch.as_tensor(ioi.word_idx["end"]).cpu()
    b = torch.arange(len(end))
    io_pos = torch.as_tensor(ioi.word_idx["IO"]).cpu()
    ld_clean = logit_diff(model, ioi)
    _, cache = model.run_with_cache(ioi.toks.long().to(model.cfg.device),
                                    names_filter=lambda n: n.endswith("hook_z") or n.endswith("hook_pattern")
                                    or n == "ln_final.hook_scale")
    scale = cache["ln_final.hook_scale"][b, end]
    io_ids = torch.as_tensor(ioi.io_tokenIDs, device=scale.device)
    s_ids = torch.as_tensor(ioi.s_tokenIDs, device=scale.device)
    udir = (model.W_U[:, io_ids] - model.W_U[:, s_ids]).T
    dla, att_io = torch.zeros(L, H), torch.zeros(L, H)
    for layer in range(L):
        z = cache[f"blocks.{layer}.attn.hook_z"][b, end]
        res = torch.einsum("nhd,hdm->nhm", z, model.W_O[layer]) / scale[:, :, None]
        dla[layer] = (res * udir[:, None, :]).sum(-1).mean(0).cpu()
        att_io[layer] = cache[f"blocks.{layer}.attn.hook_pattern"][b, :, end, io_pos].mean(0).cpu()
    del cache
    _, cache_abc = model.run_with_cache(abc.toks.long().to(model.cfg.device), names_filter=lambda n: n.endswith("hook_z"))
    end_abc = torch.as_tensor(abc.word_idx["end"]).cpu()
    mean_z = {l: cache_abc[f"blocks.{l}.attn.hook_z"][torch.arange(len(end_abc)), end_abc].mean(0) for l in range(L)}
    del cache_abc

    def hooks(heads):
        by = {}
        for l, h in heads:
            by.setdefault(l, []).append(h)

        def mk(l, hs):
            def hook(z, hook):
                for hh in hs:
                    z[b, end.to(z.device), hh] = mean_z[l][hh].to(z.dtype)
                return z
            return hook
        return [(f"blocks.{l}.attn.hook_z", mk(l, hs)) for l, hs in by.items()]

    order = sorted(((l, h) for l in range(L) for h in range(H)), key=lambda x: -float(dla[x]))
    out = {"logit_diff": float(ld_clean.mean()), "acc": float((ld_clean > 0).float().mean()),
           "dla": dla.numpy().round(5).tolist(), "att_io": att_io.numpy().round(5).tolist(),
           "top": [f"{l}.{h}" for l, h in order[:10]], "ablate": {}}
    rng = random.Random(1)
    for k in KS:
        own = order[:k]
        out["ablate"][f"own{k}"] = float(logit_diff(model, ioi, hooks(own)).mean())
        pool = [(l, h) for l in range(L) for h in range(H) if (l, h) not in own]
        out["ablate"][f"random{k}"] = [float(logit_diff(model, ioi, hooks(rng.sample(pool, k))).mean()) for _ in range(20)]
        lm = []
        for _ in range(20):  # same layers as the model's own top-k, random heads within them
            hs = [(l, rng.choice([h for h in range(H) if (l, h) not in own])) for l, _ in own]
            lm.append(float(logit_diff(model, ioi, hooks(hs)).mean()))
        out["ablate"][f"layermatched{k}"] = lm
        for name, heads in head_sets.items():
            out["ablate"][f"{name}{k}"] = float(logit_diff(model, ioi, hooks(heads[:k])).mean())
    return out


def run_size(size):
    OUT.mkdir(parents=True, exist_ok=True)
    torch.set_grad_enabled(False)
    ms = models(size)
    ref = ms[0]
    rf = OUT / f"{ref.split('/')[1]}{TAG}.json"
    if not rf.exists():
        model = load(ref)
        rf.write_text(json.dumps({"repo": ref, **measure(model, {})}))
        del model
        torch.cuda.empty_cache()
    ref_top = [tuple(map(int, x.split("."))) for x in json.loads(rf.read_text())["top"]]
    for repo in ms[1:]:
        f = OUT / f"{repo.split('/')[1]}{TAG}.json"
        if f.exists():
            continue
        try:
            model = load(repo)
        except Exception as ex:
            print("SKIP", repo, repr(ex)[:200], flush=True)
            continue
        res = measure(model, {"ref": ref_top})
        f.write_text(json.dumps({"repo": repo, **res}))
        print(repo, f"LD {res['logit_diff']:.2f} acc {res['acc']:.2f} top {res['top'][:3]}", flush=True)
        del model
        torch.cuda.empty_cache()


def analyze():
    from scipy.stats import spearmanr
    out = {}
    for size in ("160m", "410m", "1b", "1.4b", "6.9b", "12b"):
        rf = OUT / f"pythia-{size}.json"
        if not rf.exists():
            continue
        ref = json.loads(rf.read_text())
        R = np.array(ref["dla"])
        rows = {}
        for f in sorted(OUT.glob(f"pythia-{size}-*.json")):
            if f.stem.endswith("_k10"):  # the larger-k rerun is summarized separately
                continue
            d = json.loads(f.read_text())
            name = f.stem.replace(f"pythia-{size}-", "")
            kind = "deduped" if name == "deduped" else "data-seed" if name.startswith("data-seed") else "seed"
            T = np.array(d["dla"])
            within = float(np.nanmean([spearmanr(a, c)[0] for a, c in zip(R, T)]))
            row = {"kind": kind, "logit_diff": d["logit_diff"], "acc": d["acc"], "within_dla": within,
                   "ref_top1_in_target_top3": ref["top"][0] in d["top"][:3],
                   "ref_top3_overlap": len(set(ref["top"][:3]) & set(d["top"][:3])) / 3}
            for k in KS:
                drop = lambda x: d["logit_diff"] - x
                own = drop(d["ablate"][f"own{k}"])
                row[f"transfer{k}"] = drop(d["ablate"][f"ref{k}"]) / own
                row[f"random{k}"] = float(np.mean([drop(x) for x in d["ablate"][f"random{k}"]])) / own
                row[f"layermatched{k}"] = float(np.mean([drop(x) for x in d["ablate"][f"layermatched{k}"]])) / own
            rows[name] = row
        summ = {}
        for kind in ("deduped", "data-seed", "seed"):
            rs = [r for r in rows.values() if r["kind"] == kind]
            if rs:
                summ[kind] = {k: float(np.mean([r[k] for r in rs])) for k in rs[0] if k != "kind"} | {"n": len(rs)}
        out[size] = {"reference": {"logit_diff": ref["logit_diff"], "acc": ref["acc"], "top": ref["top"][:5]},
                     "by_kind": summ, "models": rows}
        print(size, json.dumps({k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in summ.items()}), flush=True)
    (OUT / "analysis.json").write_text(json.dumps(out, indent=1))


TIMECOURSE = (1000, 2000, 4000, 8000, 16000, 33000, 66000, 100000, 143000)


def load_step(repo, step):
    """Intermediate Pythia branches may ship main's safetensors: read pytorch_model.bin only."""
    from transformer_lens import HookedTransformer
    from transformers import AutoModelForCausalLM
    hf = AutoModelForCausalLM.from_pretrained(repo, revision=f"step{step}", cache_dir=str(mc.HF_CACHE),
                                              torch_dtype=torch.float32, use_safetensors=False)
    tl = "EleutherAI/" + re.sub(r"-(data-|weight-)?seed\d+$", "", repo.split("/")[1])
    return HookedTransformer.from_pretrained(tl, hf_model=hf, device="cuda", dtype=torch.float32).eval()


def timecourse(size):
    """IOI direct logit attribution of every head through training, for the standard and deduplicated models."""
    torch.set_grad_enabled(False)
    OUT.mkdir(parents=True, exist_ok=True)
    for repo in (f"EleutherAI/pythia-{size}", f"EleutherAI/pythia-{size}-deduped"):
        for step in TIMECOURSE:
            f = OUT / f"tc__{repo.split('/')[1]}__step{step}.json"
            if f.exists():
                continue
            model = load_step(repo, step)
            ioi, _ = build(model)
            L, H = model.cfg.n_layers, model.cfg.n_heads
            end = torch.as_tensor(ioi.word_idx["end"]).cpu()
            b = torch.arange(len(end))
            ld = logit_diff(model, ioi)
            _, cache = model.run_with_cache(ioi.toks.long().to(model.cfg.device),
                                            names_filter=lambda n: n.endswith("hook_z") or n == "ln_final.hook_scale")
            scale = cache["ln_final.hook_scale"][b, end]
            io_ids = torch.as_tensor(ioi.io_tokenIDs, device=scale.device)
            s_ids = torch.as_tensor(ioi.s_tokenIDs, device=scale.device)
            udir = (model.W_U[:, io_ids] - model.W_U[:, s_ids]).T
            dla = torch.zeros(L, H)
            for layer in range(L):
                z = cache[f"blocks.{layer}.attn.hook_z"][b, end]
                res = torch.einsum("nhd,hdm->nhm", z, model.W_O[layer]) / scale[:, :, None]
                dla[layer] = (res * udir[:, None, :]).sum(-1).mean(0).cpu()
            f.write_text(json.dumps({"repo": repo, "step": step, "logit_diff": float(ld.mean()),
                                     "acc": float((ld > 0).float().mean()), "dla": dla.numpy().round(5).tolist()}))
            print(repo, step, f"LD {float(ld.mean()):.2f}", flush=True)
            del model, cache
            torch.cuda.empty_cache()


def analyze_timecourse():
    """Through training: IOI logit difference, overlap of each model's top-3 IOI heads with its own final top-3, and
    overlap of the standard and deduplicated models' top-3 at the same step."""
    from scipy.stats import spearmanr
    out = {}
    for size in ("160m", "410m"):
        D = {}
        for f in OUT.glob(f"tc__pythia-{size}*__step*.json"):
            d = json.loads(f.read_text())
            D[(d["repo"].split("/")[1], d["step"])] = d
        if not D:
            continue
        top = lambda d, k=3: set(np.argsort(-np.array(d["dla"]).ravel())[:k].tolist())
        rows = {}
        for step in TIMECOURSE:
            a, b = D.get((f"pythia-{size}", step)), D.get((f"pythia-{size}-deduped", step))
            fa, fb = D.get((f"pythia-{size}", 143000)), D.get((f"pythia-{size}-deduped", 143000))
            if not (a and b and fa and fb):
                continue
            A, B = np.array(a["dla"]), np.array(b["dla"])
            rows[step] = {"ld_std": a["logit_diff"], "ld_dedup": b["logit_diff"],
                          "std_vs_own_final_top3": len(top(a) & top(fa)) / 3,
                          "dedup_vs_own_final_top3": len(top(b) & top(fb)) / 3,
                          "std_vs_dedup_top3": len(top(a) & top(b)) / 3,
                          "std_vs_dedup_within": float(np.nanmean([spearmanr(x, y)[0] for x, y in zip(A, B)]))}
        out[size] = rows
        for s, r in rows.items():
            print(size, s, {k: round(v, 2) for k, v in r.items()}, flush=True)
    (OUT / "timecourse_analysis.json").write_text(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--timecourse")
    ap.add_argument("--analyze-timecourse", action="store_true")
    a = ap.parse_args()
    if a.analyze_timecourse:
        analyze_timecourse()
    elif a.timecourse:
        timecourse(a.timecourse)
    else:
        analyze() if a.analyze else run_size(a.size)


if __name__ == "__main__":
    main()
