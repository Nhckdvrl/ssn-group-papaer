"""
L41 bounded continued-training run + post-training neutral-belief measurement.

Ordinary causal-LM continued training on micro-documents (loss on all document
tokens), then the training text is removed and neutral Yes/No belief about each
embedded proposition is measured.

Launch:  torchrun --nproc_per_node=N src/train_eval.py --assign <json> ...
`--assign` is a JSON file  {pid: cell}  mapping each proposition identity to the
condition it is trained in for this run.
"""
import os, sys, json, math, time, argparse, random
sys.path.insert(0, os.path.dirname(__file__))
import torch
import torch.distributed as dist
from torch.distributed.fsdp import fully_shard, MixedPrecisionPolicy
from transformers import AutoModelForCausalLM, AutoTokenizer

from generator import generate, GOLD
from docs import docs_for
import scoring
from scoring import MODEL_ID, REVISION, QUERY_FAMILY, FEWSHOT


# ------------------------------------------------------------------ helpers
def rank0(*a):
    if dist.get_rank() == 0:
        print(*a, flush=True)


def build_prompt(question, fewshot):
    pre = FEWSHOT if fewshot else ""
    return pre + f"Question: {question}\nAnswer:"


@torch.no_grad()
def _run_prompts(model, tok, prompts, yes_id, no_id, bs=32):
    """Distributed scoring on a padded round-robin schedule (all ranks equal)."""
    world, rank = dist.get_world_size(), dist.get_rank()
    n = len(prompts)
    per = math.ceil(n / world)
    vals = [0.0] * per
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    for st_ in range(0, per, bs):
        idxs = [i for i in range(st_, min(st_ + bs, per)) if (rank * per + i) < n]
        batch = [prompts[rank * per + i] for i in idxs] or [prompts[0]]
        enc = tok(batch, return_tensors="pt", padding=True,
                  add_special_tokens=False).to("cuda")
        lg = model(**enc).logits[:, -1, :].float()
        lp = torch.log_softmax(lg, dim=-1)
        d = (lp[:, yes_id] - lp[:, no_id]).tolist()
        for j, i in enumerate(idxs):
            vals[i] = d[j]
    buf = torch.tensor(vals, device="cuda", dtype=torch.float64)
    out = [torch.zeros_like(buf) for _ in range(world)]
    dist.all_gather(out, buf)
    return torch.cat(out).tolist()[:n]


def nearmiss(p):
    """Same agent / verb / object class, different object number. Never trained."""
    num2 = p["num"] + 1 if p["num"] < 98 else 11
    return f"Did {p['agent']} {p['verb']} {p['noun']} {num2}?"


@torch.no_grad()
def score_belief(model, tok, props, yes_id, no_id, bs=32):
    """-> {pid: {"fs": [B per query], "nofs": [...],
                 "nm_fs": B, "nm_nofs": B}}"""
    prompts, key = [], []
    for p in props:
        for fs in (True, False):
            tag = "fs" if fs else "nofs"
            for qi, qf in enumerate(QUERY_FAMILY):
                prompts.append(build_prompt(qf(p), fs)); key.append((p["pid"], tag, qi))
            prompts.append(build_prompt(nearmiss(p), fs)); key.append((p["pid"], "nm_" + tag, 0))
    vals = _run_prompts(model, tok, prompts, yes_id, no_id, bs)
    res = {}
    for (pid, tag, qi), v in zip(key, vals):
        d = res.setdefault(pid, {})
        if tag.startswith("nm_"):
            d[tag] = v
        else:
            d.setdefault(tag, [0.0] * len(QUERY_FAMILY))[qi] = v
    return res


@torch.no_grad()
def generic_nll(model, tok, texts, bs=4):
    """Mean token NLL on held-out generic text (capability sanity)."""
    world, rank = dist.get_world_size(), dist.get_rank()
    per = math.ceil(len(texts) / world)
    mine = texts[rank * per:(rank + 1) * per]
    while len(mine) < per:
        mine.append(texts[0])
    tot, cnt = 0.0, 0
    tok.padding_side = "right"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    for s in range(0, per, bs):
        batch = mine[s:s + bs]
        enc = tok(batch, return_tensors="pt", padding=True, truncation=True,
                  max_length=512, add_special_tokens=False).to("cuda")
        lab = enc["input_ids"].clone()
        lab[enc["attention_mask"] == 0] = -100
        out = model(**enc, labels=lab)
        ntok = (lab[:, 1:] != -100).sum()
        tot += out.loss.float().item() * ntok.item(); cnt += ntok.item()
    t = torch.tensor([tot, cnt], device="cuda", dtype=torch.float64)
    dist.all_reduce(t)
    return (t[0] / t[1]).item()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="dev2")
    ap.add_argument("--pools", default=None,
                    help="comma list name:count for TRAINED props, e.g. crit:256,pilot:64")
    ap.add_argument("--holdout_pool", default=None,
                    help="pool for never-trained holdout props (default: tail of --pool)")
    ap.add_argument("--n_props", type=int, default=64)
    ap.add_argument("--n_holdout", type=int, default=32,
                    help="extra propositions scored but NEVER trained (pure drift control)")
    ap.add_argument("--generic_ratio", type=float, default=0.0,
                    help="generic pretraining docs mixed in, per synthetic micro-document")
    ap.add_argument("--assign", default=None, help="JSON {pid: cell}")
    ap.add_argument("--cells", default=None, help="comma list; round-robin assign if no --assign")
    ap.add_argument("--n_docs", type=int, default=8)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--warmup", type=float, default=0.03)
    ap.add_argument("--sched", default="constant", choices=["constant", "cosine"])
    ap.add_argument("--bs", type=int, default=8, help="global docs per optimizer step")
    ap.add_argument("--micro_bs", type=int, default=8, help="docs per rank per forward")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max_len", type=int, default=128)
    ap.add_argument("--before", default=None, help="cached B_before json")
    ap.add_argument("--eval_epochs", default="",
                    help="comma list of epoch counts at which to also score beliefs")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    dist.init_process_group("nccl")
    rank, world = dist.get_rank(), dist.get_world_size()
    torch.cuda.set_device(rank)
    torch.manual_seed(args.seed); random.seed(args.seed)

    if args.pools:
        train_props = []
        for spec in args.pools.split(","):
            nm, k = spec.split(":")
            train_props += generate(nm, int(k))
        hold_props = generate(args.holdout_pool or "hold", args.n_holdout)
    else:
        all_props = generate(args.pool, args.n_props + args.n_holdout)
        train_props = all_props[:args.n_props]
        hold_props = (generate(args.holdout_pool, args.n_holdout)
                      if args.holdout_pool else all_props[args.n_props:])
    if args.assign:
        assign = json.load(open(args.assign))
        train_props = [p for p in train_props if p["pid"] in assign]
    else:
        cells = (args.cells or "Ap,An").split(",")
        assign = {p["pid"]: cells[i % len(cells)] for i, p in enumerate(train_props)}
    for p in hold_props:
        assign[p["pid"]] = "HOLD"          # scored every checkpoint, never trained
    props = train_props + hold_props

    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION)
    yes_id = tok.encode(" Yes", add_special_tokens=False)[0]
    no_id = tok.encode(" No", add_special_tokens=False)[0]

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, revision=REVISION, dtype=torch.float32,
        attn_implementation="sdpa", low_cpu_mem_usage=True)
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    mp = MixedPrecisionPolicy(param_dtype=torch.bfloat16, reduce_dtype=torch.float32)
    for layer in model.model.layers:
        fully_shard(layer, mp_policy=mp)
    fully_shard(model, mp_policy=mp)
    model.to("cuda")

    # generic capability probe text
    _d = os.path.dirname(__file__)
    gen_texts = json.load(open(os.path.join(_d, "generic_probe.json")))      # wikitext
    pile_texts = json.load(open(os.path.join(_d, "probe_pile.json")))        # held-out pile

    model.eval()
    nll_before = generic_nll(model, tok, list(gen_texts))
    pile_before = generic_nll(model, tok, list(pile_texts))
    if args.before and os.path.exists(args.before):
        B_before = json.load(open(args.before))
    else:
        B_before = score_belief(model, tok, props, yes_id, no_id)
        if rank == 0 and args.before:
            json.dump(B_before, open(args.before, "w"))
    rank0(f"[before] wikitext NLL={nll_before:.4f} pile NLL={pile_before:.4f}")

    # ------------------------------------------------------------ build corpus
    syn = []
    for p in train_props:
        syn.extend(docs_for(p, assign[p["pid"]], args.n_docs, seed=args.seed))
    n_syn = len(syn)
    n_gen = int(round(args.generic_ratio * n_syn))
    pool_g = []
    if n_gen:
        pool_g = json.load(open(os.path.join(os.path.dirname(__file__), "generic_mix.json")))
        need = n_gen * args.epochs
        assert need <= len(pool_g), f"generic pool too small: need {need}, have {len(pool_g)}"
        random.Random(90000 + args.seed).shuffle(pool_g)

    def epoch_corpus(ep):
        """Synthetic docs repeat every epoch (that IS the exposure knob);
        the generic anchor is FRESH text each epoch, never repeated, so it
        anchors the model instead of being memorised alongside the facts."""
        return syn + pool_g[ep * n_gen:(ep + 1) * n_gen]

    rank0(f"[data] synthetic={n_syn}/epoch generic={n_gen}/epoch (fresh, "
          f"{n_gen*args.epochs} distinct) holdout_props={len(hold_props)}")
    rank0(f"[data] {len(train_props)} trained props x {args.n_docs} docs x {args.epochs} epochs "
          f"= {args.n_docs*args.epochs} exposures/prop")

    # ------------------------------------------------------------- train
    model.train()
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.0,
                            betas=(0.9, 0.95), eps=1e-8)
    assert args.bs % world == 0, "global batch must divide across ranks"
    _ep0 = len(epoch_corpus(0))
    assert _ep0 % args.bs == 0, f"epoch corpus {_ep0} not divisible by bs {args.bs}"
    micro = args.bs // world
    assert micro % args.micro_bs == 0, f"per-rank {micro} not divisible by micro_bs {args.micro_bs}"
    accum = micro // args.micro_bs
    steps_per_epoch = _ep0 // args.bs
    total_steps = steps_per_epoch * args.epochs
    warm = max(1, int(args.warmup * total_steps))
    if args.sched == "cosine":
        fn = lambda s: min(1.0, (s + 1) / warm) * 0.5 * (
            1 + math.cos(math.pi * min(1.0, max(0, s - warm) / max(1, total_steps - warm))))
    else:                       # constant after warmup: every eval checkpoint is a
        fn = lambda s: min(1.0, (s + 1) / warm)   # fair "trained for E exposures" snapshot
    sched = torch.optim.lr_scheduler.LambdaLR(opt, fn)

    tok.padding_side = "right"
    step = 0
    t0 = time.time()
    eval_at = {int(x) for x in args.eval_epochs.split(",") if x.strip()}
    eval_at.add(args.epochs)
    traj = {}
    for ep in range(args.epochs):
        model.train()
        corpus = epoch_corpus(ep)
        order = list(range(len(corpus)))
        random.Random(args.seed * 1000 + ep).shuffle(order)
        for s in range(0, len(order), args.bs):
            block = order[s:s + args.bs]
            mineix = block[rank * micro:(rank + 1) * micro]
            for g in range(accum):
                batch = [corpus[i] for i in mineix[g * args.micro_bs:(g + 1) * args.micro_bs]]
                enc = tok(batch, return_tensors="pt", padding=True, truncation=True,
                          max_length=args.max_len, add_special_tokens=False).to("cuda")
                lab = enc["input_ids"].clone()
                lab[enc["attention_mask"] == 0] = -100
                loss = model(**enc, labels=lab).loss
                (loss / accum).backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
            step += 1
            if step % 25 == 0:
                rank0(f"  step {step}/{total_steps} loss={loss.item():.4f} "
                      f"lr={sched.get_last_lr()[0]:.2e} {time.time()-t0:.0f}s")
        if (ep + 1) in eval_at:
            model.eval()
            traj[ep + 1] = {"exposures": args.n_docs * (ep + 1),
                            "B": score_belief(model, tok, props, yes_id, no_id),
                            "generic_nll": generic_nll(model, tok, list(gen_texts)),
                            "pile_nll": generic_nll(model, tok, list(pile_texts)),
                            "train_loss": loss.item()}
            rank0(f"  [eval @ epoch {ep+1}] exposures/prop={args.n_docs*(ep+1)} "
                  f"wikiNLL={traj[ep+1]['generic_nll']:.4f} "
                  f"pileNLL={traj[ep+1]['pile_nll']:.4f} loss={loss.item():.4f} "
                  f"{time.time()-t0:.0f}s")
            tok.padding_side = "right"

    # -------------------------------------------------------------- final
    model.eval()
    B_after = traj[args.epochs]["B"]
    nll_after = traj[args.epochs]["generic_nll"]
    rank0(f"[after] generic NLL={nll_after:.4f}  (delta {nll_after-nll_before:+.4f})")

    if rank == 0:
        rec = {"args": vars(args), "model": MODEL_ID, "revision": REVISION,
               "assign": assign, "n_docs_total": n_syn * args.epochs,
               "generic_nll_before": nll_before, "generic_nll_after": nll_after,
               "pile_nll_before": pile_before,
               "B_before": B_before, "B_after": B_after,
               "traj": {str(k): {"exposures": v["exposures"],
                                 "generic_nll": v["generic_nll"],
                                 "pile_nll": v["pile_nll"],
                                 "train_loss": v["train_loss"], "B": v["B"]}
                        for k, v in traj.items()},
               "props": {p["pid"]: {"agent": p["agent"], "complement": p["complement"]}
                         for p in props}}
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        json.dump(rec, open(args.out, "w"), indent=1)
        print(f"wrote {args.out}", flush=True)
    dist.barrier()
    dist.destroy_process_group()


if __name__ == "__main__":
    main()
