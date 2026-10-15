"""E92: capability atlas across PolyPythias seeds, sizes and checkpoints (clean evaluation only).

Usage: e92_atlas.py --repo REPO --rev stepN  -> results/e92/<model>__<rev>.json
Tasks
  fv:*    Todd et al. (2024) function-vector datasets (github.com/ericwtodd/function_vectors @ fb9eac7, MIT), 5-shot
          "Q: x\\nA: y\\n\\n" prompts, 100 queries per task, demonstrations resampled per query (never the query item);
          readouts: first-token accuracy (argmax over the full vocabulary) and mean log-prob of the answer's first token
  el:*    elementary contrastive tasks of E89 (IOI, induction, greater-than, agreement, pronoun, successor, capital fact):
          mean contrast metric and accuracy (metric > 0)
  lm_loss NLL on 48 fixed pile-10k documents (spike detection)
"""
import argparse
import json
import os
import time

import numpy as np
import torch

import mp_common as mc

DEV = os.environ.get("E92_DEVICE", "cuda")
OUT = mc.RESULTS / os.environ.get("ATLAS_OUT", "e92")
FV = mc.CACHE / "fv_datasets" / "repo" / "dataset_files"
ABSTRACTIVE = ["antonym", "synonym", "capitalize", "capitalize_first_letter", "lowercase_first_letter", "next_capital_letter",
               "country-capital", "country-currency", "english-french", "english-spanish", "english-german", "landmark-country",
               "park-country", "person-occupation", "person-sport", "person-instrument", "present-past", "product-company",
               "singular-plural", "sentiment", "next_item", "prev_item", "word_length"]
EXTRACTIVE = ["choose_first_of_5", "choose_middle_of_5", "choose_last_of_5", "alphabetically_first_5", "animal_v_object_5",
              "color_v_animal_5", "fruit_v_animal_5", "adjective_v_verb_5", "verb_v_adjective_5", "concept_v_object_5",
              "object_v_concept_5", "conll2003_person"]
ELEMENTARY = ["ioi", "induction", "greater_than", "sva", "gender", "successor", "capital"]


def fv_prompts(tok, task, n=100, shots=5, seed=0):
    kind = "abstractive" if task in ABSTRACTIVE else "extractive"
    data = json.loads((FV / kind / f"{task}.json").read_text())
    rng = np.random.default_rng(seed)
    q_idx = rng.choice(len(data), min(n, len(data)), replace=False)
    out = []
    for qi in q_idx:
        pool = [j for j in rng.choice(len(data), shots + 1, replace=False) if j != qi][:shots]
        p = "".join(f"Q: {data[j]['input']}\nA: {data[j]['output']}\n\n" for j in pool) + f"Q: {data[qi]['input']}\nA:"
        target = tok.encode(" " + data[qi]["output"], add_special_tokens=False)[0]
        out.append((tok.encode(p, add_special_tokens=False)[-1024:], target))
    return out


@torch.no_grad()
def eval_fv(model, items, bs=32):
    order = np.argsort([len(x[0]) for x in items])
    acc, lp = np.zeros(len(items)), np.zeros(len(items))
    for i in range(0, len(items), bs):
        idx = order[i:i + bs]
        L = max(len(items[j][0]) for j in idx)
        x = torch.zeros(len(idx), L, dtype=torch.long)
        last = torch.zeros(len(idx), dtype=torch.long)
        for r, j in enumerate(idx):  # right padding: real tokens never attend to the pads
            ids = items[j][0]
            x[r, :len(ids)] = torch.tensor(ids)
            last[r] = len(ids) - 1
        lg = model(x.to(DEV)).logits.float()[torch.arange(len(idx)), last.to(DEV)]
        logp = torch.log_softmax(lg, -1)
        tg = torch.tensor([items[j][1] for j in idx], device=lg.device)
        acc[idx] = (lg.argmax(-1) == tg).float().cpu().numpy()
        lp[idx] = logp[torch.arange(len(idx)), tg].cpu().numpy()
    return {"acc": float(acc.mean()), "logp": float(lp.mean()), "n": len(items)}


@torch.no_grad()
def eval_el(model, tok, task):
    from e89_labor import Builder, Probe
    B = Builder(tok, 128)
    vals = []
    for g in getattr(B, task)():
        lg = model(g["toks"].to(DEV)).logits[:, -1].float()
        vals.append(Probe.metric(lg, Probe.index(g["tg"], lg.device), Probe.index(g["fo"], lg.device)).numpy())
    v = np.concatenate(vals)
    return {"metric": float(v.mean()), "acc": float((v > 0).mean()), "n": int(len(v))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--rev")
    ap.add_argument("--local", default=None, help="directory with config.json + weights fetched by curl (HF Xet stalls here)")
    a = ap.parse_args()
    torch.set_grad_enabled(False)
    t0 = time.time()
    from huggingface_hub import list_repo_files
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if a.local:  # weights fetched by curl; the tokenizer is identical across checkpoints
        tok = AutoTokenizer.from_pretrained(a.repo, cache_dir=str(mc.HF_CACHE))
        model = AutoModelForCausalLM.from_pretrained(a.local, torch_dtype=torch.float32).to(DEV).eval()
    else:
        kw = {"revision": a.rev}
        if a.rev != "main" and "pytorch_model.bin" in list_repo_files(a.repo, revision=a.rev):
            kw["use_safetensors"] = False  # step branches may also carry main's safetensors
        cache = os.environ.get("E89_MODEL_CACHE", str(mc.HF_CACHE))
        tok = AutoTokenizer.from_pretrained(a.repo, cache_dir=cache, revision=a.rev)
        model = AutoModelForCausalLM.from_pretrained(a.repo, cache_dir=cache, torch_dtype=torch.float32, **kw).to(DEV).eval()
    res = {"repo": a.repo, "rev": a.rev, "tasks": {}}
    for t in ABSTRACTIVE + EXTRACTIVE:
        res["tasks"]["fv:" + t] = eval_fv(model, fv_prompts(tok, t))
    for t in ELEMENTARY:
        res["tasks"]["el:" + t] = eval_el(model, tok, t)
    from e89_labor import lm_loss
    res["lm_loss"] = lm_loss(model, tok)
    res["seconds"] = time.time() - t0
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{a.repo.split('/')[-1]}__{a.rev}.json").write_text(json.dumps(res, indent=0))
    print(json.dumps({"repo": a.repo, "rev": a.rev, "lm_loss": res["lm_loss"], "seconds": res["seconds"],
                      "fv_mean_acc": float(np.mean([v["acc"] for k, v in res["tasks"].items() if k.startswith("fv:")]))}), flush=True)


if __name__ == "__main__":
    main()
