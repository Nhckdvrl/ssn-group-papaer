"""
S03 / E04 — WHICH SUPERVISION binds goal completion to the termination action?

Stage names are not comparable across modern post-training recipes (Qwen3's
mode fusion, DeepSeek-R1's two SFT and two RL rounds, Llama 4's lightweight
SFT -> online RL -> lightweight DPO, OLMo-3's Think/Instruct/RL-Zero flows), so
"which stage teaches stopping" is not a well-posed scientific object. The
learning signals underneath those recipes ARE comparable, and that is what this
experiment factorises.

The OLMo-3 trajectory (E01/e01_traj) is used only as a NATURAL ANCHOR: it
locates a real transition where the goal -> STOP mapping changes a lot
(Think-SFT final -> Instruct-SFT, the largest and the only purely stop-side
move on that chain). This experiment starts from that real incoming checkpoint,
on that stage's real incoming data, and changes ONLY the supervision.

Everything else is held byte-identical across conditions: initialization, the
example pool, the example order, the number of optimizer steps, the LR
schedule, batch size, optimizer, seed, sequence length and chat format. One
cosine schedule per run, so a run is one trajectory rather than three
schedules glued together.

Supervision factorised on two axes.

  --mask  what part of the assistant turn carries cross-entropy loss
    full      content tokens AND the final turn-end token      (positive control)
    content   content tokens only, terminator MASKED
              -> "never told where to stop", only what to keep saying
    terminal  the final turn-end token ONLY, all content MASKED
              -> "only told where responses end", never what to say

  --pairing  whether the response is paired with the goal it answers
    correct   the true (user, response) pair
    shuffled  each response keeps its tokens, its length and its endpoint, but
              is attached to ANOTHER example's user message
    generic   every response is attached to one constant user message

Together these separate three candidate accounts of the binding:
  * endpoint supervision carries it      -> terminal/correct ~ full/correct
  * continuation supervision carries it  -> content/correct ~ full/correct
  * no goal binding is needed at all     -> full/shuffled ~ full/correct
    (the Hewitt et al. "response distribution is enough" account)
  * the binding is in the pairing        -> full/correct >> full/shuffled and
                                            terminal/correct >> terminal/shuffled

Readout: the frozen E01 instrument, scored on the same fixed stop token the
trajectory used.
"""
import argparse, json, os, random, time

import torch
from torch.utils.data import DataLoader
from transformers import (AutoTokenizer, AutoModelForCausalLM,
                          get_cosine_schedule_with_warmup)

from e02_train import collate, chunked_ce, boundary_metrics, IGNORE

# The natural anchor's incoming checkpoint, and the serialization every
# measurement in Phase 1 used.
INIT_REPO = "allenai/Olmo-3-7B-Think-SFT"
SERIALIZATION = "allenai/Olmo-3-7B-Instruct"
STOP_TOKEN = "<|endoftext|>"
GENERIC_PROMPT = "Write a response."


def _render(tok, user, resp, max_len, stop_id):
    """(full_ids, prompt_len) or None if this rendering is unusable."""
    pair = [{"role": "user", "content": user},
            {"role": "assistant", "content": resp}]
    prompt_ids = tok.apply_chat_template([pair[0]], tokenize=True,
                                         add_generation_prompt=True)
    full_ids = tok.apply_chat_template(pair, tokenize=True)
    if len(full_ids) <= len(prompt_ids) + 1 or len(full_ids) > max_len:
        return None
    if full_ids[:len(prompt_ids)] != list(prompt_ids):
        return None
    if full_ids[-1] != stop_id:            # must end on the measured action
        return None
    return full_ids, len(prompt_ids)


def survivors(tok, examples, max_len, stop_id, rot):
    """Indices usable under EVERY pairing, so the conditions share one pool.

    Filtering per condition would hand `shuffled` a different example set from
    `correct` (a longer substituted prompt can push a pair over max_len), and
    the design claims the conditions differ only in supervision.
    """
    keep = []
    for i, m in enumerate(examples):
        resp = m[1]["content"]
        users = (examples[i][0]["content"],
                 examples[(i + rot) % len(examples)][0]["content"],
                 GENERIC_PROMPT)
        if all(_render(tok, u, resp, max_len, stop_id) for u in users):
            keep.append(i)
    return keep


def build_rows(tok, examples, max_len, mask, pairing, stop_id, keep, rot):
    """(input_ids, labels) with the requested supervision.

    The example POOL and its ORDER are identical across conditions; only which
    positions carry loss, and which user message a response is attached to,
    change.
    """
    rows, n_sup, n_tok = [], 0, 0
    for i in keep:
        resp = examples[i][1]["content"]
        if pairing == "correct":
            user = examples[i][0]["content"]
        elif pairing == "shuffled":
            # a fixed rotation: every response is attached to a DIFFERENT user
            # message, and the multiset of prompts is unchanged
            user = examples[(i + rot) % len(examples)][0]["content"]
        elif pairing == "generic":
            user = GENERIC_PROMPT
        else:
            raise ValueError(pairing)
        full_ids, n_prompt = _render(tok, user, resp, max_len, stop_id)
        lab = [IGNORE] * len(full_ids)
        body = range(n_prompt, len(full_ids))
        if mask == "full":
            for j in body:
                lab[j] = full_ids[j]
        elif mask == "content":
            for j in body:
                lab[j] = full_ids[j]
            lab[-1] = IGNORE               # never told where to stop
        elif mask == "terminal":
            lab[-1] = full_ids[-1]         # told ONLY where to stop
        else:
            raise ValueError(mask)
        rows.append((full_ids, lab))
        n_sup += sum(1 for x in lab if x != IGNORE)
        n_tok += len(full_ids)
    return rows, n_sup, n_tok


class _Rows(torch.utils.data.Dataset):
    def __init__(self, rows): self.rows = rows
    def __len__(self): return len(self.rows)
    def __getitem__(self, i): return self.rows[i]


@torch.no_grad()
def run_e01(model, tok, sids, stimuli, outdir):
    from e01_run import measure
    model.eval()
    for path in stimuli:
        if not os.path.exists(path):
            continue
        rows = []
        for it in [json.loads(l) for l in open(path)]:
            c = measure(model, tok, it, "complete", True, sids)
            i = measure(model, tok, it, "incomplete", True, sids)
            assert c.pop("_prefix_ids") == i.pop("_prefix_ids"), \
                f"exact-prefix violation on {it['item_id']}"
            c.pop("_full_ids"); i.pop("_full_ids")
            comp = c.pop("_comp_tok_p2"); i.pop("_comp_tok_p2")
            row = dict(item_id=it["item_id"], family=it["family"],
                       n_given=it["n_given"], comp_token=comp, chat=True)
            row.update({"cmp_" + k: v for k, v in c.items()})
            row.update({"inc_" + k: v for k, v in i.items()})
            for tag in ("p1", "p2"):
                row[f"d_goal_{tag}"] = row[f"cmp_{tag}_margin"] - row[f"inc_{tag}_margin"]
            rows.append(row)
        name = "e01.jsonl" if path.endswith("e01_pairs.jsonl") else "e01_d.jsonl"
        with open(f"{outdir}/{name}", "w") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print("wrote", f"{outdir}/{name}", len(rows), flush=True)
    model.train()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mask", required=True, choices=("full", "content", "terminal"))
    ap.add_argument("--pairing", default="correct",
                    choices=("correct", "shuffled", "generic"))
    ap.add_argument("--init", default=INIT_REPO)
    ap.add_argument("--data", default="data/dolci_instruct_sft_subset.jsonl")
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--steps", type=int, default=2250)
    ap.add_argument("--bs", type=int, default=4)
    ap.add_argument("--accum", type=int, default=4)
    ap.add_argument("--max-len", type=int, default=768)
    ap.add_argument("--n-train", type=int, default=12000)
    ap.add_argument("--n-val", type=int, default=400)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--eval-every", type=int, default=250,
                    help="run the E01 instrument mid-run, from the SAME "
                         "trajectory, so dynamics come from one schedule")
    ap.add_argument("--stimuli", nargs="*",
                    default=["stimuli/e01_pairs.jsonl", "stimuli/e01_pairs_d.jsonl"])
    args = ap.parse_args()

    torch.manual_seed(args.seed); random.seed(args.seed)
    tok = AutoTokenizer.from_pretrained(SERIALIZATION)
    stop_id = tok.convert_tokens_to_ids(STOP_TOKEN)
    assert stop_id is not None and stop_id >= 0
    sids = [stop_id]

    model = AutoModelForCausalLM.from_pretrained(
        args.init, dtype=torch.bfloat16).cuda()
    model.config.use_cache = False
    n_emb = model.get_input_embeddings().weight.shape[0]
    assert max(tok.get_vocab().values()) < n_emb

    examples = [json.loads(l)["messages"] for l in open(args.data)]
    random.Random(1234).shuffle(examples)       # SAME order for every condition
    va_ex = examples[:args.n_val]
    tr_ex = examples[args.n_val:args.n_val + args.n_train]

    # the rotation is a property of the POOL, not of the condition, so
    # `correct` and `shuffled` see the identical example set
    rot = 1 + len(tr_ex) // 3
    rot_va = 1 + len(va_ex) // 3
    keep = survivors(tok, tr_ex, args.max_len, stop_id, rot)
    keep_va = survivors(tok, va_ex, args.max_len, stop_id, rot_va)
    tr, n_sup, n_tok = build_rows(tok, tr_ex, args.max_len, args.mask,
                                  args.pairing, stop_id, keep, rot)
    # validation is always FULL/correct: it measures the model, not the condition
    va, _, _ = build_rows(tok, va_ex, args.max_len, "full", "correct", stop_id,
                          keep_va, rot_va)
    print(f"mask={args.mask} pairing={args.pairing} init={args.init}\n"
          f"  pool={len(keep)} of {len(tr_ex)} usable under EVERY pairing; "
          f"train={len(tr)} val={len(va)}\n"
          f"  supervised tokens={n_sup:,} of {n_tok:,} "
          f"({100 * n_sup / n_tok:.2f}%)", flush=True)

    pad = tok.pad_token_id
    if pad is None or pad in sids:
        pad = 0
    assert pad not in sids
    g = torch.Generator(); g.manual_seed(args.seed)
    tl = DataLoader(_Rows(tr), batch_size=args.bs, shuffle=True, generator=g,
                    collate_fn=lambda b: collate(b, pad), drop_last=True)
    vl = DataLoader(_Rows(va), batch_size=args.bs, shuffle=False,
                    collate_fn=lambda b: collate(b, pad))

    import bitsandbytes as bnb
    opt = bnb.optim.AdamW8bit(model.parameters(), lr=args.lr,
                              weight_decay=0.0, betas=(0.9, 0.95))
    sch = get_cosine_schedule_with_warmup(opt, int(0.03 * args.steps), args.steps)

    tag = args.tag or f"{args.mask}_{args.pairing}_s{args.seed}"
    outdir = f"results/e04/{tag}"
    os.makedirs(outdir, exist_ok=True)
    with open(f"{outdir}/config.json", "w") as fh:
        json.dump(vars(args) | {"stop_id": stop_id, "n_supervised_tokens": n_sup,
                                "n_total_tokens": n_tok, "n_train_rows": len(tr),
                                "pool_size": len(keep), "rot": rot},
                  fh, indent=2)

    hist = []
    m = boundary_metrics_safe(model, vl, sids)
    m.update(step=0); hist.append(m); print(json.dumps(m), flush=True)
    os.makedirs(f"{outdir}/step0", exist_ok=True)
    run_e01(model, tok, sids, args.stimuli, f"{outdir}/step0")

    it = iter(tl); step = 0; t0 = time.time()
    while step < args.steps:
        opt.zero_grad(set_to_none=True)
        tot = 0.0
        for _ in range(args.accum):
            try: batch = next(it)
            except StopIteration: it = iter(tl); batch = next(it)
            ids, lab, att = (x.cuda() for x in batch)
            loss = chunked_ce(model(ids, attention_mask=att).logits, lab)
            (loss / args.accum).backward()
            tot += loss.detach().item() / args.accum
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); sch.step()
        step += 1
        if step % 50 == 0 or step == args.steps:
            m = boundary_metrics_safe(model, vl, sids)
            m.update(step=step, train_loss=tot, lr=sch.get_last_lr()[0],
                     elapsed=time.time() - t0)
            hist.append(m); print(json.dumps(m), flush=True)
            with open(f"{outdir}/history.jsonl", "w") as fh:
                for h in hist: fh.write(json.dumps(h) + "\n")
        # checkpoints of ONE schedule, not separate schedules
        if args.eval_every and (step % args.eval_every == 0) and step < args.steps:
            d = f"{outdir}/step{step}"; os.makedirs(d, exist_ok=True)
            run_e01(model, tok, sids, args.stimuli, d)

    run_e01(model, tok, sids, args.stimuli, outdir)
    print("done", outdir, flush=True)


def boundary_metrics_safe(model, vl, sids):
    class _Arm:
        def __init__(self, m): self.model = m
        def __call__(self, ids, att): return self.model(ids, attention_mask=att).logits
        def eval(self): self.model.eval()
        def train(self): self.model.train()
    return boundary_metrics(_Arm(model), vl, sids, "cuda")


if __name__ == "__main__":
    main()
