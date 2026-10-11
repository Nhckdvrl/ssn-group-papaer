"""
S03 / E02 — train one parameter-locus arm on ordinary instruction data.

Everything except the parameter freedom is shared across arms: the base
checkpoint, the corpus, the example order, the chat format, the sequence
length, the number of optimizer steps, and the batch size.

Loss: next-token cross-entropy on ASSISTANT tokens only, *including the final
stop token*.  Prompt tokens are masked.  This is ordinary SFT — the model is
never trained on the E01 contrast.

Reported co-metric (goal-independent stopping competence), so that a failed arm
can be told apart from an untrained arm:

  boundary_auc  P(stop is ranked above the true continuation at a real
                response boundary) vs at response-internal positions, on
                held-out instruction data.
"""
import argparse, json, math, os, random, time

import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM, get_cosine_schedule_with_warmup

from e01_run import STAGE_REPOS, TURN_END_TOKEN
from e02_arms import ArmModel

IGNORE = -100


class SFTData(Dataset):
    """Chat-formatted single-turn examples with assistant-only labels.

    Tokenising is cached to disk: rendering the chat template is single-threaded
    CPU work that otherwise dominates wall-clock, and caching also guarantees
    every arm trains on byte-identical inputs in an identical order.
    """

    @staticmethod
    def cached(tok, examples, max_len, cache_path):
        import pickle
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as fh:
                rows = pickle.load(fh)
            obj = SFTData.__new__(SFTData)
            obj.rows = rows
            return obj
        obj = SFTData(tok, examples, max_len)
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "wb") as fh:
            pickle.dump(obj.rows, fh)
        return obj

    def __init__(self, tok, examples, max_len):
        self.rows = []
        self.tok = tok
        for msgs in examples:
            prompt_ids = tok.apply_chat_template(
                [msgs[0]], tokenize=True, add_generation_prompt=True)
            full_ids = tok.apply_chat_template(msgs, tokenize=True)
            if len(full_ids) <= len(prompt_ids) + 1 or len(full_ids) > max_len:
                continue
            # sanity: the full rendering must extend the generation prompt
            if full_ids[:len(prompt_ids)] != list(prompt_ids):
                continue
            labels = [IGNORE] * len(prompt_ids) + list(full_ids[len(prompt_ids):])
            self.rows.append((full_ids, labels))

    def __len__(self): return len(self.rows)

    def __getitem__(self, i): return self.rows[i]


def collate(batch, pad_id):
    n = max(len(x[0]) for x in batch)
    ids = torch.full((len(batch), n), pad_id, dtype=torch.long)
    lab = torch.full((len(batch), n), IGNORE, dtype=torch.long)
    att = torch.zeros((len(batch), n), dtype=torch.long)
    for i, (a, b) in enumerate(batch):
        ids[i, :len(a)] = torch.tensor(a); lab[i, :len(b)] = torch.tensor(b)
        att[i, :len(a)] = 1
    return ids, lab, att



def chunked_ce(logits, labels, chunk=2048):
    """Cross-entropy without materialising a float32 copy of the whole
    [B, T, vocab] logit tensor, which OOMs the 7B S/F arms on one card."""
    lg = logits[:, :-1].reshape(-1, logits.size(-1))
    tg = labels[:, 1:].reshape(-1)
    keep = tg != IGNORE
    lg, tg = lg[keep], tg[keep]
    n = lg.size(0)
    if n == 0:
        return logits.sum() * 0.0
    total = 0.0
    for i in range(0, n, chunk):
        total = total + F.cross_entropy(lg[i:i + chunk].float(), tg[i:i + chunk],
                                        reduction="sum")
    return total / n


@torch.no_grad()
def boundary_metrics(arm_model, loader, stop_ids, device, max_batches=40):
    """Goal-independent stopping competence on held-out ordinary data."""
    arm_model.eval()
    bnd, inner, losses = [], [], []
    sid = torch.tensor(stop_ids, device=device)
    for bi, (ids, lab, att) in enumerate(loader):
        if bi >= max_batches: break
        dev = arm_model.model.get_input_embeddings().weight.device
        ids, lab, att = ids.to(dev), lab.to(dev), att.to(dev)
        logits = arm_model(ids, att)[:, :-1]
        tgt = lab[:, 1:]
        mask = tgt != IGNORE
        # score only supervised positions; upcasting the full logit tensor OOMs
        lp = torch.log_softmax(logits[mask].float(), dim=-1)
        tgt = tgt[mask]
        losses.append(float(-lp.gather(-1, tgt.unsqueeze(-1)).squeeze(-1).mean()))
        stop_lp = torch.logsumexp(lp[..., sid], dim=-1)
        is_stop_target = torch.isin(tgt, sid)
        # NOTE: scoring stop against the *target* token is degenerate at a real
        # boundary, where the target IS the stop token and the margin is 0 by
        # construction.  Score log P(stop at this position) instead: it is
        # well defined at boundary and response-internal positions alike.
        marg = stop_lp
        bnd += marg[is_stop_target].tolist()
        inner += marg[~is_stop_target].tolist()
    arm_model.train()
    # AUC of separating boundary positions from response-internal positions
    import random as _r
    _r.seed(0)
    a = _r.sample(bnd, min(2000, len(bnd))) if bnd else []
    b = _r.sample(inner, min(2000, len(inner))) if inner else []
    auc = float("nan")
    if a and b:
        b_s = sorted(b)
        import bisect
        auc = sum(bisect.bisect_left(b_s, x) + 0.5 * (bisect.bisect_right(b_s, x) - bisect.bisect_left(b_s, x))
                  for x in a) / (len(a) * len(b))
    return dict(val_loss=sum(losses) / len(losses), boundary_auc=auc,
                log_p_stop_at_boundary=sum(bnd) / len(bnd) if bnd else float("nan"),
                log_p_stop_inside=sum(inner) / len(inner) if inner else float("nan"),
                n_boundary=len(bnd), n_inside=len(inner))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["R", "Rmlp", "S", "Sbody", "F"])
    ap.add_argument("--family", default="olmo3-7b")
    ap.add_argument("--lr", type=float, required=True)
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--bs", type=int, default=2)
    ap.add_argument("--accum", type=int, default=8)
    ap.add_argument("--degrade-stop", type=float, default=0.0,
                    help="Before training, remove this fraction of the stop "
                         "row's projection onto the generic response-boundary "
                         "direction b. This degrades the readout's GENERIC "
                         "boundary competence while leaving the hidden states, "
                         "the data and every other parameter untouched, so the "
                         "within-family causal test of the boundary-competence "
                         "account changes exactly one thing.")
    ap.add_argument("--bdir", default=None,
                    help="path to the cached boundary direction b (.pt)")
    ap.add_argument("--device-map", default=None,
                    help="'auto' spreads the model across GPUs (naive model "
                         "parallel). Needed for 32B, whose weights+grads+8-bit "
                         "Adam state exceed one 96GB card. The freezes are "
                         "unaffected: parameters remain ordinary tensors, just "
                         "on different devices.")
    ap.add_argument("--grad-ckpt", action="store_true",
                    help="trade speed for memory; unnecessary here, a 7B S/F arm "
                         "fits in ~46GB of a 96GB card without it")
    ap.add_argument("--opt8bit", action="store_true",
                    help="8-bit AdamW; needed to fit a 7B S/F arm on one card")
    ap.add_argument("--max-len", type=int, default=768)
    ap.add_argument("--n-train", type=int, default=8000)
    ap.add_argument("--n-val", type=int, default=400)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="")
    ap.add_argument("--data", default="data/tulu_subset.jsonl")
    ap.add_argument("--out", default=None)
    ap.add_argument("--eval-after", action="store_true",
                    help="run the E01 instrument in-process when training ends "
                         "(avoids a 15GB save/reload round-trip for S and F)")
    ap.add_argument("--save-model", action="store_true")
    ap.add_argument("--stimuli", nargs="*",
                    default=["stimuli/e01_pairs.jsonl", "stimuli/e01_pairs_d.jsonl"])
    args = ap.parse_args()

    torch.manual_seed(args.seed); random.seed(args.seed)
    repo = STAGE_REPOS[args.family]["base"]
    # the chat template lives on the post-trained sibling; the base has none.
    tmpl_repo = STAGE_REPOS[args.family][
        "sft" if "sft" in STAGE_REPOS[args.family] else "instruct"]
    tok = AutoTokenizer.from_pretrained(repo)
    tok.chat_template = AutoTokenizer.from_pretrained(tmpl_repo).chat_template

    if args.device_map:
        model = AutoModelForCausalLM.from_pretrained(
            repo, dtype=torch.bfloat16, device_map=args.device_map)
    else:
        model = AutoModelForCausalLM.from_pretrained(repo, dtype=torch.bfloat16).cuda()
    if args.arm in ("S", "Sbody", "F") and args.grad_ckpt:
        model.gradient_checkpointing_enable()
    model.config.use_cache = False
    # The stop set for E02 is the token that terminates an ASSISTANT TURN in the
    # format we train on, and only that token.
    #   OLMo   reuses the native pretraining <|endoftext|>;
    #   Qwen   ends the turn with <|im_end|>, not its eos <|endoftext|>;
    #   Llama  ends the turn with <|eot_id|>, not its eos <|end_of_text|>.
    # Using tok.eos_token_id would train arm R's delta on a token the assistant
    # never emits in two of the three families.
    stop_tok = TURN_END_TOKEN[args.family]
    stop_id = tok.convert_tokens_to_ids(stop_tok)
    assert stop_id is not None and stop_id >= 0, f"no id for {stop_tok}"
    sids = [stop_id]
    print(f"  assistant-turn stop token: {stop_tok!r} -> {stop_id}", flush=True)
    if args.degrade_stop:
        bvec = torch.load(args.bdir, map_location="cpu").float()
        head = model.get_output_embeddings()
        with torch.no_grad():
            bh = (bvec / bvec.norm()).to(head.weight.device, head.weight.dtype)
            row = head.weight.data[stop_id].float()
            proj = float(row @ bh.float())
            head.weight.data[stop_id] = (
                row - args.degrade_stop * proj * bh.float()).to(head.weight.dtype)
        print(f"  degraded stop row: removed {args.degrade_stop:g} x "
              f"(w_stop . b_hat = {proj:.3f}) along the boundary direction",
              flush=True)

    arm = ArmModel(model, sids, args.arm)
    if not args.device_map:
        arm = arm.cuda()
    if arm.readout is not None:
        arm.readout = arm.readout.cuda().float()
    print(f"arm={args.arm} repo={repo} stop_ids={sids} "
          f"trainable={arm.n_trainable():,}", flush=True)

    examples = [json.loads(l)["messages"] for l in open(args.data)]
    random.Random(1234).shuffle(examples)          # SAME order for every arm
    ck = f"data/cache/{args.family}_L{args.max_len}"
    tr = SFTData.cached(tok, examples[args.n_val:args.n_val + args.n_train],
                        args.max_len, f"{ck}_tr{args.n_val}_{args.n_train}.pkl")
    va = SFTData.cached(tok, examples[:args.n_val], args.max_len,
                        f"{ck}_va{args.n_val}.pkl")
    print(f"train={len(tr)} val={len(va)}", flush=True)
    # Llama-3.1 base ships no pad token.  Padding never reaches the loss
    # (labels are IGNORE there) or attention, so the identity is arbitrary --
    # but it must not be the stop token, or a padded batch would look like it
    # contains extra assistant terminators.
    pad = tok.pad_token_id
    if pad is None:
        pad = tok.eos_token_id if tok.eos_token_id not in sids else 0
    assert pad not in sids, "pad token collides with the assistant stop token"
    print(f"  pad id: {pad} ({tok.convert_ids_to_tokens(pad)!r})", flush=True)
    g = torch.Generator(); g.manual_seed(args.seed)
    tl = DataLoader(tr, batch_size=args.bs, shuffle=True, generator=g,
                    collate_fn=lambda b: collate(b, pad), drop_last=True)
    vl = DataLoader(va, batch_size=args.bs, shuffle=False,
                    collate_fn=lambda b: collate(b, pad))

    if args.opt8bit:
        import bitsandbytes as bnb
        opt = bnb.optim.AdamW8bit(arm.trainable_parameters(), lr=args.lr,
                                  weight_decay=0.0, betas=(0.9, 0.95))
    else:
        opt = torch.optim.AdamW(arm.trainable_parameters(), lr=args.lr,
                                weight_decay=0.0, betas=(0.9, 0.95))
    sch = get_cosine_schedule_with_warmup(opt, int(0.03 * args.steps), args.steps)

    tag = args.tag or f"{args.arm}_lr{args.lr}_s{args.seed}"
    outdir = args.out or f"results/e02/{tag}"
    os.makedirs(outdir, exist_ok=True)
    hist = []
    print("step0 eval:", boundary_metrics(arm, vl, sids, "cuda"), flush=True)

    it = iter(tl); step = 0; t0 = time.time()
    while step < args.steps:
        tstep = time.time()
        opt.zero_grad(set_to_none=True)
        tot = 0.0
        nseq = ntok = 0
        for _ in range(args.accum):
            try: batch = next(it)
            except StopIteration: it = iter(tl); batch = next(it)
            dev = arm.model.get_input_embeddings().weight.device
            ids, lab, att = (x.to(dev) for x in batch)
            nseq += ids.size(0); ntok += ids.numel()
            logits = arm(ids, att)
            loss = chunked_ce(logits, lab)
            (loss / args.accum).backward()
            tot += loss.detach().item() / args.accum
        torch.nn.utils.clip_grad_norm_(arm.trainable_parameters(), 1.0)
        opt.step(); sch.step()
        arm.enforce_freeze()           # exact restore for arm S
        step += 1
        if step <= 3:
            torch.cuda.synchronize()
            print(f"[timing] step {step}: {time.time() - tstep:.2f}s  "
                  f"{nseq} seqs / {ntok} padded tokens  "
                  f"peak {torch.cuda.max_memory_allocated() / 1e9:.1f}GB", flush=True)
        if step % 50 == 0 or step == args.steps:
            m = boundary_metrics(arm, vl, sids, "cuda")
            m.update(step=step, train_loss=tot, lr=sch.get_last_lr()[0],
                     elapsed=time.time() - t0)
            hist.append(m)
            print(json.dumps(m), flush=True)
            with open(f"{outdir}/history.jsonl", "w") as fh:
                for h in hist: fh.write(json.dumps(h) + "\n")

    # persist only what the arm was allowed to change
    if arm.readout is not None:
        torch.save(arm.readout.state_dict(), f"{outdir}/readout.pt")
    elif args.save_model:
        model.save_pretrained(f"{outdir}/model", safe_serialization=True)
        tok.save_pretrained(f"{outdir}/model")
    with open(f"{outdir}/config.json", "w") as fh:
        json.dump(vars(args) | {"stop_ids": sids, "n_trainable": arm.n_trainable()}, fh, indent=2)

    if args.eval_after:
        run_e01(arm, tok, sids, args, outdir)
    print("done", outdir)


@torch.no_grad()
def run_e01(arm, tok, sids, args, outdir):
    """Run the E01 exact-prefix instrument on the just-trained arm, in process."""
    from e01_run import measure

    class _Wrap:
        device = "cuda"
        def __call__(self, x):
            class O: pass
            o = O(); o.logits = arm(x, None)
            return o

    arm.eval()
    w = _Wrap()
    for path in args.stimuli:
        if not os.path.exists(path):
            continue
        items = [json.loads(l) for l in open(path)]
        rows = []
        for it in items:
            c = measure(w, tok, it, "complete", True, sids)
            i = measure(w, tok, it, "incomplete", True, sids)
            assert c.pop("_prefix_ids") == i.pop("_prefix_ids"), \
                f"exact-prefix violation on {it['item_id']}"
            comp = c.pop("_comp_tok_p2"); i.pop("_comp_tok_p2")
            row = dict(item_id=it["item_id"], family=it["family"],
                       n_given=it["n_given"], comp_token=comp, stage=args.arm,
                       model_family=args.family, chat=True)
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
    arm.train()


if __name__ == "__main__":
    main()
