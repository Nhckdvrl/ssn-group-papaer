"""Per-example pretrained instruction-response association on the E01 pool.

    association_i = NLL(y_i) - NLL(y_i | x_i)

measured under the UNTUNED base model. The quantity is FedDQC's IRA-like score
and is not claimed as a contribution here; it is used only as an operational
precedent for stratifying pairs by how much the pretrained model already binds
x_i to y_i.

NLL(y|x) uses the P serialisation and NLL(y) uses the D_rt serialisation, so the
two conditions differ exactly as the training arms do.

Also dumps response length and NLL(y) so that any later stratification can be
matched on the obvious difficulty variables rather than confounding
association with "short/easy response".
"""
import argparse
import json
import pathlib
import sys
import time

import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from arms import build_example  # noqa: E402
from train import load_backbone, load_pool  # noqa: E402


@torch.no_grad()
def nll_batch(model, rows, idxs, arm, special, device="cuda"):
    ids_list, loss_list = [], []
    for i in idxs:
        r = rows[i]
        ids, loss, _ = build_example(
            r["x_ids"], r["y_ids"], arm, special["bos_id"], special["eos_id"],
            special["user_open_ids"], special["asst_open_ids"],
        )
        ids_list.append(ids)
        loss_list.append(loss)
    L = max(len(x) for x in ids_list)
    pad = special["eos_id"]
    inp = torch.full((len(ids_list), L), pad, dtype=torch.long)
    lm = torch.zeros((len(ids_list), L), dtype=torch.bool)
    att = torch.zeros((len(ids_list), L), dtype=torch.long)
    for k, (ids, loss) in enumerate(zip(ids_list, loss_list)):
        inp[k, : len(ids)] = torch.tensor(ids)
        lm[k, : len(loss)] = torch.tensor(loss, dtype=torch.bool)
        att[k, : len(ids)] = 1
    inp, lm, att = inp.to(device), lm.to(device), att.to(device)
    logits = model(input_ids=inp, attention_mask=att).logits
    ls = torch.nn.functional.cross_entropy(
        logits[:, :-1].float().reshape(-1, logits.size(-1)),
        inp[:, 1:].reshape(-1), reduction="none",
    ).view(inp.shape[0], -1)
    m = lm[:, 1:]
    tot = (ls * m).sum(1)
    return (tot / m.sum(1)).tolist(), m.sum(1).tolist()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="google/gemma-2-2b")
    ap.add_argument("--pool", default=str(ROOT / "results" / "pool"))
    ap.add_argument("--out", default=str(ROOT / "results" / "ira.jsonl"))
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    rows, _ = load_pool(args.pool)
    if args.limit:
        rows = rows[: args.limit]
    model, tok, special = load_backbone(args.model)
    model.eval()

    # longest-first batching keeps padding waste down
    order = sorted(range(len(rows)), key=lambda i: -(len(rows[i]["x_ids"]) + len(rows[i]["y_ids"])))
    out = {}
    t0 = time.time()
    for b in range(0, len(order), args.batch_size):
        idxs = order[b : b + args.batch_size]
        cond, ntok = nll_batch(model, rows, idxs, "P", special)
        uncond, _ = nll_batch(model, rows, idxs, "D_rt", special)
        for k, i in enumerate(idxs):
            out[i] = {
                "idx": i,
                "nll_y_given_x": cond[k],
                "nll_y": uncond[k],
                "association": uncond[k] - cond[k],
                "n_resp_tokens": int(ntok[k]),
                "n_prompt_tokens": len(rows[i]["x_ids"]),
            }
        if b % (args.batch_size * 100) == 0:
            print(f"{b}/{len(order)}  {time.time()-t0:.0f}s", flush=True)

    with open(args.out, "w") as f:
        for i in range(len(rows)):
            f.write(json.dumps(out[i]) + "\n")
    print("wrote", args.out, f"{time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
