"""E11: realistic in-context tasks (code copy, ID list, novel-label few-shot) with rare vs common payloads.

Usage: e11_functional.py --repo EleutherAI/pythia-70m-seed2 --step 64000 -> results/e11/<model>__step<N>.json
"""
import argparse
import json
import os
import time

import torch

import mp_common as mc
import e02_population as p2

OUT = mc.RESULTS / os.environ.get("EXP", "e11")
N = 300


def enc(tok, s):
    return tok(s, add_special_tokens=False)["input_ids"]


def pools(counts):
    order = counts.argsort(descending=True)
    return {"rare": torch.nonzero((counts >= 10) & (counts < 50)).flatten(), "common": order[500:5000]}


NOUNS = ["apple", "table", "river", "window", "garden", "doctor", "pencil", "mountain", "kitchen", "bottle",
         "letter", "engine", "forest", "camera", "island", "jacket", "ladder", "market", "planet", "rocket",
         "saddle", "tunnel", "violin", "wallet", "anchor", "basket", "candle", "dragon", "feather", "glacier"]


def build(tok, bos, pool, task, g):
    """Return list of (token ids, list of target positions) — targets are positions whose next token is scored."""
    items = []
    for _ in range(N):
        if task.startswith("T1"):
            k = int(task.split("_k")[1])
            pay = pool[torch.randint(0, len(pool), (k,), generator=g)].tolist()
            a, b = enc(tok, "The code is:"), enc(tok, ". Again, the code is:")
            ids = [bos] + a + pay + b + pay
            start = 1 + len(a) + k + len(b)
            tgt = list(range(start - 1, start + k - 1))
        elif task == "T2":
            ids_list = [pool[torch.randint(0, len(pool), (2,), generator=g)].tolist() for _ in range(8)]
            comma = enc(tok, ",")
            seq = []
            for x in ids_list:
                seq += x + comma
            a, b = enc(tok, "IDs:"), enc(tok, ". Repeat the IDs:")
            ids = [bos] + a + seq + b + seq
            start = 1 + len(a) + len(seq) + len(b)
            tgt = [start - 1 + i for i in range(len(seq)) if seq[i] not in comma]
        else:  # T3 novel-label few-shot
            words = [NOUNS[i] for i in torch.randperm(len(NOUNS), generator=g)[:8].tolist()]
            labels = pool[torch.randint(0, len(pool), (8,), generator=g)].tolist()
            ids, tgt = [bos], []
            for w, lab in zip(words, labels):
                ids += enc(tok, f" {w}:") + [lab] + enc(tok, ".")
            for i in torch.randperm(8, generator=g).tolist():
                ids += enc(tok, f" {words[i]}:")
                tgt.append(len(ids) - 1)
                ids += [labels[i]] + enc(tok, ".")
        items.append((ids, tgt))
    return items


@torch.no_grad()
def score(model, items):
    losses, accs = [], []
    for ids, tgt in items:
        t = torch.tensor([ids], device=model.cfg.device)
        logp = model(t).log_softmax(-1)[0]
        pos = torch.tensor(tgt, device=t.device)
        nxt = t[0, pos + 1]
        lp = logp[pos].gather(-1, nxt[:, None])[:, 0]
        losses.append(float(-lp.mean()))
        accs.append(float((logp[pos].argmax(-1) == nxt).float().mean()))
    return {"loss": sum(losses) / len(losses), "acc": sum(accs) / len(accs), "loss_seq": losses}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--step", type=int, required=True)
    args = ap.parse_args()
    torch.set_grad_enabled(False)
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    model = mc.load_tl_model(args.repo, args.step)
    tok, bos = model.tokenizer, model.tokenizer.bos_token_id
    P = pools(torch.load(p2.COUNTS))
    res = {"repo": args.repo, "step": args.step, "protocol": "experiments/E11-functional-consequence.md", "tasks": {}}
    for ti, task in enumerate(["T1_k2", "T1_k8", "T1_k32", "T2", "T3"]):
        for pname, pool in P.items():
            g = torch.Generator().manual_seed(1000 + ti)  # deterministic across processes / checkpoints
            res["tasks"][f"{task}|{pname}"] = score(model, build(tok, bos, pool, task, g))
    res["seconds"] = round(time.time() - t0, 1)
    tag = f"{args.repo.split('/')[-1]}__step{args.step}"
    (OUT / f"{tag}.json").write_text(json.dumps(res, indent=1))
    print(tag, {k: (round(v["loss"], 2), round(v["acc"], 2)) for k, v in res["tasks"].items()}, f"({res['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
