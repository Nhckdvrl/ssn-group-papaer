"""
S03 / E03 — the geometric explanation of why readout adaptation is contingent.

Arm R can only add a vector d to the stop row, with hidden states frozen, so

    delta(dz_stop) = d . v ,      v = mean(h_complete - h_incomplete)   [E01]

exactly.  Ordinary SFT does not optimise d for v: it optimises d to tell REAL
RESPONSE BOUNDARIES from response-interior positions.  That job has its own
direction in the same frozen space,

    b = mean(h at true response boundaries) - mean(h at interior positions)

So the single degree of freedom is pulled along b, and whatever goal-relative
reading it gains or loses is whatever b happens to project onto v.

**Prediction: sign(cos(b, v)) predicts the sign of arm R's reading change.**
Unlike the raw initial gradient this is optimiser-independent -- it is a property
of the pretrained state geometry, not of Adam's preconditioning.

Also reports the ACTUAL learned delta from each trained R arm, and how it
decomposes onto b and v, as a direct check.
"""
import argparse, glob, json, os, sys

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e01_run import STAGE_REPOS, TURN_END_TOKEN, build_pair_ids


@torch.no_grad()
def boundary_direction(model, tok, stop_id, examples, n, max_len, dev):
    H = model.config.hidden_size
    hb = torch.zeros(H, dtype=torch.float64); nb = 0
    hi = torch.zeros(H, dtype=torch.float64); ni = 0
    for k, msgs in enumerate(examples):
        if k >= n:
            break
        prompt = tok.apply_chat_template([msgs[0]], tokenize=True,
                                         add_generation_prompt=True)
        full = tok.apply_chat_template(msgs, tokenize=True)
        if len(full) <= len(prompt) + 1 or len(full) > max_len:
            continue
        if full[:len(prompt)] != list(prompt):
            continue
        out = model(torch.tensor([full], device=dev), output_hidden_states=True)
        h = out.hidden_states[-1][0].float()[:-1]
        tgt = torch.tensor(full[1:], device=dev)
        sup = torch.arange(len(full) - 1, device=dev) >= (len(prompt) - 1)
        isb = (tgt == stop_id) & sup
        isi = (tgt != stop_id) & sup
        if isb.any():
            hb += h[isb].sum(0).double().cpu(); nb += int(isb.sum())
        if isi.any():
            hi += h[isi].sum(0).double().cpu(); ni += int(isi.sum())
    return hb / max(nb, 1) - hi / max(ni, 1), nb, ni


@torch.no_grad()
def goal_direction(model, tok, items, dev):
    acc = None
    for it in items:
        hs = {}
        for cond in ("complete", "incomplete"):
            full, p1, p2, *_ = build_pair_ids(tok, it, cond, True)
            out = model(torch.tensor([full], device=dev), output_hidden_states=True)
            hs[cond] = out.hidden_states[-1][0, p2].float().double().cpu()
        d = hs["complete"] - hs["incomplete"]
        acc = d if acc is None else acc + d
    return acc / len(items)


def cos(a, b):
    return float(a @ b) / (float(a.norm()) * float(b.norm()) + 1e-12)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--n-batches", type=int, default=300)
    ap.add_argument("--max-len", type=int, default=768)
    ap.add_argument("--readouts", default=None,
                    help="glob for trained R readout.pt files to decompose")
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
    ex = [json.loads(l)["messages"] for l in open("data/tulu_subset.jsonl")]
    random.Random(1234).shuffle(ex)
    b, nb, ni = boundary_direction(model, tok, stop_id, ex[400:],
                                   args.n_batches, args.max_len, dev)
    items = [json.loads(l) for l in open("stimuli/e01_pairs.jsonl")]
    v = goal_direction(model, tok, items, dev)

    out = dict(family=args.family, stop_token=stop_tok, n_boundary=nb,
               n_interior=ni, cos_b_v=cos(b, v),
               norm_b=float(b.norm()), norm_v=float(v.norm()))

    pat = args.readouts or f"results/e02/**/{args.family}_R_st*/readout.pt"
    learned = []
    for p in sorted(glob.glob(pat, recursive=True)) + \
             sorted(glob.glob(f"results/e02/**/R_st*/readout.pt", recursive=True)
                    if args.family == "olmo3-7b" else []):
        try:
            sd = torch.load(p, map_location="cpu")
            d = sd["w"][0].double()
        except Exception:
            continue
        learned.append(dict(path=p, cos_d_v=cos(d, v), cos_d_b=cos(d, b),
                            dot_d_v=float(d @ v), norm_d=float(d.norm())))
    out["learned"] = learned
    torch.save(b.float(), f"results/e03/bdir_{args.family}.pt")
    os.makedirs("results/e03", exist_ok=True)
    with open(f"results/e03/geometry_{args.family}.json", "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps({k: v for k, v in out.items() if k != "learned"}, indent=2))
    for L in learned:
        print(f"  {os.path.basename(os.path.dirname(L['path'])):<28} "
              f"cos(d,v)={L['cos_d_v']:+.3f}  cos(d,b)={L['cos_d_b']:+.3f}  "
              f"d.v={L['dot_d_v']:+.2f}")


if __name__ == "__main__":
    main()
