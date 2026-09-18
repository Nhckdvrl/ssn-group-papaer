"""
S03 / E03 — why readout adaptation helps in one family and hurts in another.

Arm R's only freedom is an additive delta d on the stop row, with the hidden
states frozen:  logit_stop(t) = z_stop(t) + h_t . d,  d initialised at 0.

So the ordinary-SFT gradient on d has a closed form -- no autograd needed:

    dL/dd = (1/N) * sum_t ( p_stop(t) - 1[target_t == stop] ) * h_t

Gradient descent moves d along -dL/dd.  The E01 reading term is
dz_stop = w_stop . (h_complete - h_incomplete), so to first order arm R changes
the reading term by

    delta(dz_stop)  ~  lr * ( -dL/dd ) . v ,      v = mean(h_complete - h_incomplete)

**The sign of (-dL/dd).v therefore predicts, before any training, whether
readout-only adaptation will improve or damage goal-relative reading.**

The gradient splits exactly into two parts with opposite pull:

    boundary positions (target IS the stop token): pull d toward  +h_boundary
    interior positions (target is not stop)      : push d away from h_interior

which is precisely the generic-boundary-calibration work.  Reporting the two
alignments separately shows whether generic boundary learning and goal-relative
reading are cooperating or competing in each family.
"""
import argparse, json, os, sys

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e01_run import STAGE_REPOS, TURN_END_TOKEN, build_pair_ids

IGNORE = -100


@torch.no_grad()
def sft_gradient(model, tok, stop_id, examples, max_batches, max_len, device):
    """Closed-form dL/dd accumulated over ordinary instruction data.

    Returns (g_total, g_boundary, g_interior, counts).
    """
    H = model.config.hidden_size
    g_b = torch.zeros(H, dtype=torch.float64)
    g_i = torch.zeros(H, dtype=torch.float64)
    n_b = n_i = 0
    for k, msgs in enumerate(examples):
        if k >= max_batches:
            break
        prompt = tok.apply_chat_template([msgs[0]], tokenize=True,
                                         add_generation_prompt=True)
        full = tok.apply_chat_template(msgs, tokenize=True)
        if len(full) <= len(prompt) + 1 or len(full) > max_len:
            continue
        if full[:len(prompt)] != list(prompt):
            continue
        ids = torch.tensor([full], device=device)
        out = model(ids, output_hidden_states=True)
        h = out.hidden_states[-1][0].float()                  # [T, H]
        lp = torch.log_softmax(out.logits[0].float(), dim=-1)  # [T, V]
        p_stop = lp[:, stop_id].exp()                          # [T]
        tgt = torch.tensor(full[1:], device=device)
        # position t predicts token t+1; supervise only the assistant span
        sup = torch.arange(len(full) - 1, device=device) >= (len(prompt) - 1)
        is_b = (tgt == stop_id) & sup
        is_i = (tgt != stop_id) & sup
        # dL/dd contribution = (p_stop - 1[tgt==stop]) * h
        hs = h[:-1]
        g_b += ((p_stop[:-1][is_b] - 1.0).unsqueeze(-1) * hs[is_b]).sum(0).double().cpu()
        g_i += ((p_stop[:-1][is_i]).unsqueeze(-1) * hs[is_i]).sum(0).double().cpu()
        n_b += int(is_b.sum()); n_i += int(is_i.sum())
    n = max(n_b + n_i, 1)
    return (g_b + g_i) / n, g_b / n, g_i / n, (n_b, n_i)


@torch.no_grad()
def goal_direction(model, tok, items, stop_id, device):
    """v = mean over E01 items of (h_complete - h_incomplete) at the p2 position."""
    acc = None
    for it in items:
        hs = {}
        for cond in ("complete", "incomplete"):
            full, p1, p2, *_ = build_pair_ids(tok, it, cond, True)
            out = model(torch.tensor([full], device=device), output_hidden_states=True)
            hs[cond] = out.hidden_states[-1][0, p2].float().double().cpu()
        d = hs["complete"] - hs["incomplete"]
        acc = d if acc is None else acc + d
    return acc / len(items)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--n-batches", type=int, default=200)
    ap.add_argument("--max-len", type=int, default=768)
    ap.add_argument("--stimuli", default="stimuli/e01_pairs.jsonl")
    ap.add_argument("--data", default="data/tulu_subset.jsonl")
    args = ap.parse_args()

    repo = STAGE_REPOS[args.family]["base"]
    donor = "sft" if "sft" in STAGE_REPOS[args.family] else "instruct"
    tok = AutoTokenizer.from_pretrained(repo)
    tok.chat_template = AutoTokenizer.from_pretrained(
        STAGE_REPOS[args.family][donor]).chat_template
    stop_tok = TURN_END_TOKEN[args.family]
    stop_id = tok.convert_tokens_to_ids(stop_tok)

    model = AutoModelForCausalLM.from_pretrained(
        repo, dtype=torch.bfloat16, device_map="cuda").eval()
    dev = model.get_input_embeddings().weight.device

    import random
    ex = [json.loads(l)["messages"] for l in open(args.data)]
    random.Random(1234).shuffle(ex)          # same order the arms train on
    g, g_b, g_i, (n_b, n_i) = sft_gradient(
        model, tok, stop_id, ex[400:], args.n_batches, args.max_len, dev)

    items = [json.loads(l) for l in open(args.stimuli)]
    v = goal_direction(model, tok, items, stop_id, dev)

    def rep(name, gg):
        upd = -gg                                  # gradient descent direction
        dot = float(upd @ v)
        cos = dot / (float(upd.norm()) * float(v.norm()) + 1e-12)
        return dict(name=name, dot=dot, cos=cos, gnorm=float(gg.norm()))

    out = dict(family=args.family, stop_token=eot_tok or doc_tok,
               n_boundary=n_b, n_interior=n_i, v_norm=float(v.norm()),
               total=rep("total", g), boundary=rep("boundary", g_b),
               interior=rep("interior", g_i))
    os.makedirs("results/e03", exist_ok=True)
    with open(f"results/e03/gradalign_{args.family}.json", "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
