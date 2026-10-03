"""E46: controlled pretraining of small Llama-style LMs to test, by intervention, what fixes head placement.

Protocol: experiments/E46-*.md.  One run = (size, init_seed, corpus, order_seed) [+ optional branch from a parent run at
step k with a weight perturbation eps and/or a corpus / order switch].  Head-role maps (M1 induction, M2 prev-token,
M3 sink; same probes as E35/census.py) are measured at fixed checkpoints and written to results/e46/<run>.json.

  e46_train.py --size S --init 1 --corpus c4 --order 1                       # base run
  e46_train.py --size S --init 1 --corpus c4 --order 1 --eps 1e-4            # init perturbation at step 0
  e46_train.py --size S --init 1 --corpus c4 --order 1 --branch 1000 --eps 0.1   # perturb weights at step 1000
  e46_train.py --size S --init 1 --corpus c4 --order 1 --branch 1000 --to-corpus code --to-order 7  # switch data
"""
import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import torch

import mp_common as mc

DATA = Path("/home/xiang/mechpop_cache/e46_data")
RUNS = Path("/home/xiang/mechpop_cache/e46_runs")
OUT = mc.RESULTS / "e46"
SIZES = {"S": dict(L=4, H=8, d=256, ff=1024), "M": dict(L=6, H=8, d=512, ff=2048)}
SEQ, BS, STEPS, WARM, LR = 512, 64, 10000, 300, 1e-3
MICRO = 4  # micro-batches per step (memory only; the step's gradient is unchanged)
MEASURE = (0, 100, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000, 10000)
BRANCH_STEPS = (100, 250, 500, 1000, 2000, 4000, 8000)  # parents save full state here
VOCAB = 50304


def tokenizer():
    import glob
    from transformers import PreTrainedTokenizerFast
    return PreTrainedTokenizerFast(tokenizer_file=glob.glob(
        str(mc.HF_CACHE / "models--allenai--DataDecide-c4-1B/snapshots/*/tokenizer.json"))[0],
        eos_token="<|endoftext|>", pad_token="<|padding|>")


def build(size, init_seed):
    from transformers import LlamaConfig, LlamaForCausalLM
    s = SIZES[size]
    cfg = LlamaConfig(vocab_size=VOCAB, hidden_size=s["d"], intermediate_size=s["ff"], num_hidden_layers=s["L"],
                      num_attention_heads=s["H"], num_key_value_heads=s["H"], max_position_embeddings=SEQ,
                      rms_norm_eps=1e-5, rope_theta=10000.0, tie_word_embeddings=False, attention_bias=False,
                      mlp_bias=False, initializer_range=0.02)
    cfg._attn_implementation = "sdpa"
    torch.manual_seed(init_seed)
    return LlamaForCausalLM(cfg)


class Stream:
    """Random 513-token windows from one corpus file; the order seed fixes the sequence of windows."""

    def __init__(self, corpus, order_seed, start_step=0):
        self.x = np.memmap(DATA / f"{corpus}.u16", dtype=np.uint16, mode="r")
        self.rng = np.random.default_rng(order_seed)
        for _ in range(start_step):  # advance so that a branch continues the parent's stream exactly
            self.rng.integers(0, len(self.x) - SEQ - 1, BS)

    def next(self):
        off = self.rng.integers(0, len(self.x) - SEQ - 1, BS)
        return torch.from_numpy(np.stack([self.x[o:o + SEQ + 1] for o in off]).astype(np.int64))


@torch.no_grad()
def measure(model, nat):
    model.config._attn_implementation = "eager"
    model.eval()
    dev = next(model.parameters()).device
    L, H = model.config.num_hidden_layers, model.config.num_attention_heads
    g = torch.Generator().manual_seed(0)
    first = torch.randint(1000, 40000, (100, 128), generator=g)
    ids = torch.cat([torch.full((100, 1), 50279), first, first], 1).to(dev)
    q = torch.arange(129, 257)
    M1, nll = 0, []
    for i in range(0, 100, 25):  # chunks keep the measurement's memory small
        out = model(ids[i:i + 25], output_attentions=True)
        M1 = M1 + torch.stack([a[:, :, q, q - 127].float().mean((0, 2)).cpu() for a in out.attentions]) / 4
        lp = out.logits.float().log_softmax(-1)
        nll.append(-lp[:, :-1].gather(-1, ids[i:i + 25, 1:, None])[..., 0])
        del out, lp
    nll = torch.cat(nll)
    gain = float(nll[:, 1:128].mean() - nll[:, 129:].mean())
    halves = []
    for docs in (nat[:25], nat[25:]):
        o = model(docs, output_attentions=True)
        t = torch.arange(2, docs.shape[1])
        halves.append((torch.stack([a[:, :, t, t - 1].float().mean((0, 2)).cpu() for a in o.attentions]),
                       torch.stack([a[:, :, 2:, 0].float().mean((0, 2)).cpu() for a in o.attentions])))
        lpn = o.logits.float().log_softmax(-1)
    nat_loss = float(-lpn[:, :-1].gather(-1, docs[:, 1:, None])[..., 0].mean())
    M2, M3 = (halves[0][0] + halves[1][0]) / 2, (halves[0][1] + halves[1][1]) / 2
    rel = float(np.corrcoef(halves[0][0].ravel(), halves[1][0].ravel())[0, 1])
    model.config._attn_implementation = "sdpa"
    model.train()
    return {"M1": M1.numpy().round(5).tolist(), "M2": M2.numpy().round(5).tolist(), "M3": M3.numpy().round(5).tolist(),
            "copy_gain": gain, "nat_loss": nat_loss, "rel_M2": rel, "M1_max": float(M1.max()), "M2_max": float(M2.max())}


def perturb(model, eps, seed):
    g = torch.Generator(device="cpu").manual_seed(seed)
    with torch.no_grad():
        for p in model.parameters():
            p.add_(eps * p.float().std() * torch.randn(p.shape, generator=g).to(p.device, p.dtype))


def lr_at(step):
    if step < WARM:
        return LR * (step + 1) / WARM
    return LR * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * (step - WARM) / (STEPS - WARM))))


def run_name(a):
    n = f"{a.size}_i{a.init}_{a.corpus}_o{a.order}"
    if a.branch is not None:
        n += f"_b{a.branch}"
        if a.eps:
            n += f"_eps{a.eps:g}"
        if a.to_corpus:
            n += f"_to{a.to_corpus}"
        if a.to_order is not None:
            n += f"_too{a.to_order}"
    elif a.eps:
        n += f"_eps{a.eps:g}"
    if a.rerun:
        n += f"_rerun{a.rerun}"
    return n


def main():
    from e35_census import natural_texts
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", default="S")
    ap.add_argument("--init", type=int, required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--order", type=int, required=True)
    ap.add_argument("--eps", type=float, default=0.0)
    ap.add_argument("--branch", type=int, default=None)
    ap.add_argument("--to-corpus", default=None)
    ap.add_argument("--to-order", type=int, default=None)
    ap.add_argument("--rerun", type=int, default=0)
    ap.add_argument("--save-branch-states", action="store_true")
    ap.add_argument("--steps", type=int, default=STEPS)
    a = ap.parse_args()
    name = run_name(a)
    f = OUT / f"{name}.json"
    if f.exists():
        print("exists", name)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    torch.backends.cuda.matmul.allow_tf32 = True
    dev = "cuda"
    model = build(a.size, a.init).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=LR, betas=(0.9, 0.95), weight_decay=0.1, eps=1e-8)
    start = 0
    corpus, order = a.corpus, a.order
    if a.branch is not None:  # continue from the parent's saved state at step `branch`
        parent = run_name(argparse.Namespace(**{**vars(a), "branch": None, "eps": 0.0, "to_corpus": None,
                                                "to_order": None, "rerun": 0}))
        st = torch.load(RUNS / parent / f"state{a.branch}.pt", map_location=dev)
        model.load_state_dict(st["model"])
        opt.load_state_dict(st["opt"])
        start = a.branch
        if a.to_corpus:
            corpus = a.to_corpus
        if a.to_order is not None:
            order = a.to_order
    if a.eps:
        perturb(model, a.eps, seed=10_000 + a.init)
    same_stream = corpus == a.corpus and order == a.order
    data = Stream(corpus, order, start if same_stream else 0)
    nat = torch.tensor(natural_texts(tokenizer()), device=dev)
    log = {"name": name, "args": vars(a), "measures": {}, "loss": {}}
    (RUNS / name).mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    model.train()
    for step in range(start, a.steps + 1):
        if step in MEASURE:
            log["measures"][step] = measure(model, nat)
            print(name, step, f"loss {list(log['loss'].values())[-1] if log['loss'] else float('nan'):.3f}",
                  f"M1max {log['measures'][step]['M1_max']:.3f} M2max {log['measures'][step]['M2_max']:.3f}",
                  f"gain {log['measures'][step]['copy_gain']:.2f} t {time.time() - t0:.0f}s", flush=True)
        if a.save_branch_states and step in BRANCH_STEPS:
            torch.save({"model": model.state_dict(), "opt": opt.state_dict()}, RUNS / name / f"state{step}.pt")
        if step == a.steps:
            break
        x = data.next().to(dev, non_blocking=True)
        for gr in opt.param_groups:
            gr["lr"] = lr_at(step)
        opt.zero_grad(set_to_none=True)
        loss = 0.0
        for xc in x.chunk(MICRO):  # gradient accumulation over equal micro-batches = same mean-loss gradient, ~1/4 memory
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = model(xc[:, :-1]).logits
            lc = torch.nn.functional.cross_entropy(logits.float().reshape(-1, VOCAB), xc[:, 1:].reshape(-1)) / MICRO
            lc.backward()
            loss += float(lc)
            del logits, lc
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % 100 == 0:
            log["loss"][step] = loss
    torch.save(model.state_dict(), RUNS / name / "final.pt")
    log["seconds"] = time.time() - t0
    f.write_text(json.dumps(log))


if __name__ == "__main__":
    main()
