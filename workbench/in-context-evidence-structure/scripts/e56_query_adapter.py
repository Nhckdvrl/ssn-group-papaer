"""E56: can a module that only changes WHERE the answer position reads (attention queries) make in-context evidence
source-conditional?  Frozen model; trained low-rank modules; interaction-type perspectives on real comments.
usage: e56_query_adapter.py --model Qwen/Qwen3-8B --mode query|resid|query_shuffled|none --out JSON
  query          : delta added to q_proj output at the last position for every layer in [L1, L)  (reads only)
  resid          : delta added to the residual stream at the last position after layer L1 (can write anything)
  query_shuffled : as 'query', trained on contexts whose annotator names are shuffled per demo (no source info)
  none           : evaluation only (default model; also single-source upper bound)
Data: comments targeting race vs gender (Measuring Hate Speech), split into train / test pools.
A: race -> toxic, gender -> safe; B: race -> safe, gender -> toxic.  Loss: CE on the source-correct label word."""
import argparse, copy, json
from pathlib import Path
import numpy as np, torch

HEAD = "Below are comments and the labels that individual annotators gave them.\n\n"


def pools(seed=5600):
    from datasets import load_dataset
    d = load_dataset("ucberkeley-dlab/measuring-hate-speech", split="train").select_columns(
        ["comment_id", "hatespeech", "target_race", "target_gender", "text"]).to_pandas()
    g = d.groupby("comment_id").agg(race=("target_race", "mean"), gender=("target_gender", "mean"), hs=("hatespeech", "mean"), text=("text", "first"))
    g = g[(g.text.map(lambda t: len(t.split()) <= 50)) & (g.hs >= 1.0)]
    race = g[(g.race >= 0.75) & (g.gender <= 0.1)].text.tolist(); gender = g[(g.gender >= 0.75) & (g.race <= 0.1)].text.tolist()
    rng = np.random.default_rng(seed); rng.shuffle(race); rng.shuffle(gender)
    cut = lambda x: (x[: int(len(x) * 0.7)], x[int(len(x) * 0.7):])
    (rtr, rte), (gtr, gte) = cut(race), cut(gender)
    return {"train": (rtr, gtr), "test": (rte, gte)}


def contexts(pool, n, rng, nq=8, shuffle_names=False):
    race, gender = pool
    out = []
    for _ in range(n):
        r = list(rng.choice(race, 8 + nq, replace=False)); g_ = list(rng.choice(gender, 8 + nq, replace=False))
        A = [(t, 0, 1) for t in r[:4]] + [(t, 0, 0) for t in g_[:4]]          # (text, role, toxic)
        B = [(t, 1, 0) for t in r[4:8]] + [(t, 1, 1) for t in g_[4:8]]
        demos = [(A + B)[j] for j in rng.permutation(16)]
        names = list(rng.permutation(["Alex", "Sam"]))
        shown = [names[role] if not shuffle_names else names[int(rng.integers(2))] for _, role, _ in demos]
        q = [(t, "race") for t in r[8:]] + [(t, "gender") for t in g_[8:]]
        out.append({"demos": demos, "shown": shown, "names": names, "q": q})
    return out


def correct(role, kind):
    return int((role == 0) == (kind == "race"))       # A: race toxic; B: gender toxic


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--mode"); ap.add_argument("--out")
    ap.add_argument("--rank", type=int, default=8); ap.add_argument("--train_ctx", type=int, default=400); ap.add_argument("--test_ctx", type=int, default=80)
    ap.add_argument("--epochs", type=int, default=2); ap.add_argument("--lr", type=float, default=1e-3)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.manual_seed(0)
    P = pools(); rng = np.random.default_rng(1)
    train = contexts(P["train"], a.train_ctx, rng, shuffle_names=(a.mode == "query_shuffled"))
    test = contexts(P["test"], a.test_ctx, np.random.default_rng(2))
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="sdpa").eval()
    for p_ in model.parameters():
        p_.requires_grad_(False)
    cfg = model.config; L = cfg.num_hidden_layers; D = cfg.hidden_size; L1 = L // 2 - 2
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    TOX, SAFE = enc(" toxic")[0], enc(" safe")[0]
    state = {"on": False}
    params = []
    if a.mode in ("query", "query_shuffled"):
        QD = model.model.layers[0].self_attn.q_proj.out_features
        mods = torch.nn.ModuleDict({str(l): torch.nn.Sequential(torch.nn.Linear(D, a.rank, bias=False), torch.nn.Linear(a.rank, QD, bias=False))
                                    for l in range(L1, L)}).cuda().float()
        for m in mods.values():
            torch.nn.init.zeros_(m[1].weight)
        def qhook(l):
            def f(mod, inp, out):
                if not state["on"]:
                    return out
                x = inp[0][:, -1].float(); out = out.clone()
                out[:, -1] = out[:, -1] + mods[str(l)](x).to(out.dtype)
                return out
            return f
        for l in range(L1, L):
            model.model.layers[l].self_attn.q_proj.register_forward_hook(qhook(l))
        params = list(mods.parameters())
    elif a.mode == "resid":
        mod = torch.nn.Sequential(torch.nn.Linear(D, a.rank, bias=False), torch.nn.Linear(a.rank, D, bias=False)).cuda().float()
        torch.nn.init.zeros_(mod[1].weight)
        def rhook(m_, inp, out):
            if not state["on"]:
                return out
            h = out[0] if isinstance(out, tuple) else out
            h = h.clone(); h[:, -1] = h[:, -1] + mod(h[:, -1].float()).to(h.dtype)
            return (h,) + tuple(out[1:]) if isinstance(out, tuple) else h
        model.model.layers[L1].register_forward_hook(rhook)
        params = list(mod.parameters())

    blk = lambda t, n, y: f"Comment: {t}\nAnnotator: {n}\nLabel: {'toxic' if y else 'safe'}\n\n"

    def run(ctx, demo_filter=None, grad=False):
        """Returns ld (toxic - safe) for every (who, query) and targets."""
        demos = [(d, s) for d, s in zip(ctx["demos"], ctx["shown"]) if demo_filter is None or d[1] == demo_filter]
        prefix = enc(HEAD + "".join(blk(t, s, y) for (t, _, y), s in demos))
        with torch.no_grad():
            out = model(input_ids=torch.tensor([prefix]).cuda(), use_cache=True)
        lds, ys = [], []
        for role in ((0, 1) if demo_filter is None else (demo_filter,)):
            name = ctx["names"][role]
            qids = [enc(f"Comment: {t}\nAnnotator: {name}\nLabel:") for t, _ in ctx["q"]]
            ql = [len(x) for x in qids]; QL = max(ql)
            # right-align queries so that the last position is the answer position for every row
            I = torch.zeros((len(qids), QL), dtype=torch.long); M = torch.zeros((len(qids), len(prefix) + QL), dtype=torch.long)
            M[:, :len(prefix)] = 1; Pp = torch.zeros((len(qids), QL), dtype=torch.long)
            for qi, x in enumerate(qids):
                I[qi, QL - len(x):] = torch.tensor(x); M[qi, len(prefix) + QL - len(x):] = 1
                Pp[qi, QL - len(x):] = torch.arange(len(prefix), len(prefix) + len(x))
            cache = copy.deepcopy(out.past_key_values); cache.batch_repeat_interleave(len(qids))
            state["on"] = a.mode != "none"
            with torch.set_grad_enabled(grad):
                lo = model(input_ids=I.cuda(), attention_mask=M.cuda(), position_ids=Pp.cuda(), past_key_values=cache, use_cache=True, logits_to_keep=1).logits[:, -1].float()
            state["on"] = False
            lds.append(lo[:, TOX] - lo[:, SAFE]); ys += [correct(role, k) for _, k in ctx["q"]]
        return torch.cat(lds), torch.tensor(ys, dtype=torch.float32).cuda()

    log = {"mode": a.mode, "model": a.model, "rank": a.rank, "train_loss": []}
    if params:
        opt = torch.optim.Adam(params, lr=a.lr)
        for ep in range(a.epochs):
            for i, ctx in enumerate(train):
                ld, y = run(ctx, grad=True)
                loss = torch.nn.functional.binary_cross_entropy_with_logits(ld, y)
                opt.zero_grad(); loss.backward(); opt.step()
                if i % 50 == 0:
                    log["train_loss"].append(float(loss)); print(ep, i, round(float(loss), 4), flush=True)

    @torch.no_grad()
    def evaluate(single):
        sep, acc = [], []
        for ctx in test:
            if single:
                ldA, yA = run(ctx, demo_filter=0); ldB, yB = run(ctx, demo_filter=1)
                ld = torch.cat([ldA, ldB]); y = torch.cat([yA, yB])
            else:
                ld, y = run(ctx)
            n = len(ctx["q"]); kinds = np.array([k == "race" for _, k in ctx["q"]])
            I = lambda v: float(v[torch.tensor(kinds)].mean() - v[torch.tensor(~kinds)].mean())
            sep.append(I(ld[:n].cpu()) - I(ld[n:].cpu())); acc.append(float(((ld > 0).float() == y).float().mean()))
        return {"interaction_sep": float(np.mean(sep)), "acc": float(np.mean(acc))}
    if params:
        torch.save([p_.detach().cpu() for p_ in params], a.out.replace(".json", ".pt"))
    log["test_mixed"] = evaluate(False)
    if a.mode == "none":
        log["test_single"] = evaluate(True)
    print(json.dumps(log), flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True); Path(a.out).write_text(json.dumps(log, indent=1))


if __name__ == "__main__":
    main()
