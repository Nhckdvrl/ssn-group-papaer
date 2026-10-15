"""E89: division-of-labour atlas. Per head x task causal maps, for permutation-invariant comparison across retrainings.

Usage: e89_labor.py --family dd|pythia|hf --repo REPO --rev REV [--n 256] [--smoke]
Writes results/e89/<tag>.npz and <tag>.json.

Per task (single-token answer, contrastive metric m = logsumexp(logits[target set]) - logsumexp(logits[foil set]) at
the last position), per head (l, h), per prompt:
  end   m(clean) - m(head's z mean-ablated at the last position only)
  all   m(clean) - m(head's z mean-ablated at every position)
Means are position-matched within a group of prompts that share template and token length (prompt-specific
information is removed, positional/template information kept). Prompts are split into two halves by item (not by
prompt index) so that split-half reliability is not inflated by repeated items.
Also stores the generic attention roles of E81 (induction, previous-token).
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import torch

import mp_common as mc

OUT = mc.RESULTS / os.environ.get("LABOR_OUT", "e89")

NAMES_M = "John Michael David James Robert Mark Paul Peter Tom Daniel George Richard Thomas Steven Kevin Brian Jack Adam Eric Scott".split()
NAMES_F = "Mary Sarah Lisa Anna Emma Laura Linda Susan Karen Nancy Rachel Kate Amy Julia Helen Alice Jessica Rose Jane Emily".split()
PLACES = "store school park office station hospital restaurant market library garden beach museum".split()
OBJS = "book ball drink bone ring key bag apple kiss gift letter computer".split()
CAPITALS = [("France", "Paris"), ("England", "London"), ("Italy", "Rome"), ("Germany", "Berlin"), ("Spain", "Madrid"),
            ("Japan", "Tokyo"), ("Russia", "Moscow"), ("Egypt", "Cairo"), ("Greece", "Athens"), ("Canada", "Ottawa"),
            ("Ireland", "Dublin"), ("Austria", "Vienna"), ("Norway", "Oslo"), ("China", "Beijing"), ("India", "Delhi"),
            ("Korea", "Seoul"), ("Thailand", "Bangkok"), ("Portugal", "Lisbon"), ("Poland", "Warsaw"),
            ("Sweden", "Stockholm"), ("Hungary", "Budapest"), ("Cuba", "Havana"), ("Kenya", "Nairobi"), ("Peru", "Lima")]
CAP_T = ["The capital of {c} is", "The capital city of {c} is", "{c}'s capital is the city of", "Q: What is the capital of {c}?\nA:"]
SEQS = ["Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split(),
        "January February March April May June July August September October November December".split(),
        "one two three four five six seven eight nine ten eleven twelve".split()]
ANT = [("hot", "cold"), ("big", "small"), ("up", "down"), ("fast", "slow"), ("happy", "sad"), ("old", "young"),
       ("high", "low"), ("rich", "poor"), ("hard", "soft"), ("early", "late"), ("wet", "dry"), ("strong", "weak"),
       ("good", "bad"), ("thick", "thin"), ("empty", "full"), ("light", "dark"), ("open", "closed"), ("left", "right"),
       ("true", "false"), ("win", "lose"), ("love", "hate"), ("in", "out"), ("black", "white"), ("buy", "sell")]
PAST = [("go", "went"), ("see", "saw"), ("eat", "ate"), ("run", "ran"), ("take", "took"), ("give", "gave"),
        ("come", "came"), ("make", "made"), ("know", "knew"), ("think", "thought"), ("find", "found"), ("tell", "told"),
        ("write", "wrote"), ("sit", "sat"), ("buy", "bought"), ("bring", "brought"), ("speak", "spoke"), ("drink", "drank"),
        ("fly", "flew"), ("begin", "began"), ("choose", "chose"), ("drive", "drove"), ("fall", "fell"), ("grow", "grew"),
        ("hold", "held"), ("leave", "left"), ("lose", "lost"), ("meet", "met"), ("sell", "sold"), ("send", "sent"),
        ("sing", "sang"), ("stand", "stood"), ("teach", "taught"), ("wear", "wore"), ("win", "won"), ("break", "broke")]
COLORS = "red blue green yellow black white brown purple orange pink gray".split()
CO_OBJ = "ball box car cup hat pen book shirt door chair bag bike lamp key".split()
SVA_N = [("key", "keys"), ("book", "books"), ("dog", "dogs"), ("car", "cars"), ("teacher", "teachers"),
         ("girl", "girls"), ("boy", "boys"), ("house", "houses"), ("tree", "trees"), ("student", "students"),
         ("table", "tables"), ("picture", "pictures"), ("door", "doors"), ("window", "windows"), ("farmer", "farmers")]
SVA_T = ["The {s} near the {a}", "The {s} next to the {a}", "The {s} behind the {a}", "The {s} of the {a}"]
GT_NOUNS = "war expedition project contract deal reign drought strike siege tradition".split()
GENDER_T = ["So {n} is a really great friend, isn't", "{n} went to the store because", "When {n} came home,"]
IOI_T = ["Then, {a} and {b} went to the {p}. {s} gave a {o} to",
         "When {a} and {b} got a {o} at the {p}, {s} decided to give it to",
         "Afterwards, {a} and {b} went to the {p}. {s} gave the {o} to",
         "While {a} and {b} were working at the {p}, {s} gave a {o} to"]

TASKS = ("ioi", "induction", "greater_than", "sva", "gender", "capital", "successor", "antonym", "past_tense")


class Builder:
    def __init__(self, tok, n, seed=0):
        self.tok, self.n, self.rng = tok, n, np.random.default_rng(seed)

    def one(self, w):
        ids = self.tok.encode(" " + w, add_special_tokens=False)
        return ids[0] if len(ids) == 1 else None

    def ok(self, words):
        return [w for w in words if self.one(w) is not None]

    def emit(self, items):
        """items: list of (prompt, targets, foils, item_key). Group by (template-free) token length."""
        groups = {}
        for p, tg, fo, key in items:
            ids = self.tok.encode(p, add_special_tokens=False)
            groups.setdefault(len(ids), []).append((ids, tg, fo, key))
        out = []
        keys = sorted({str(it[3]) for it in items})
        perm = [keys[j] for j in self.rng.permutation(len(keys))]
        half_of = {k: i % 2 for i, k in enumerate(perm)}
        for L, rows in sorted(groups.items()):
            if len(rows) < 8:
                continue
            out.append({"toks": torch.tensor([r[0] for r in rows]), "tg": [r[1] for r in rows], "fo": [r[2] for r in rows],
                        "half": np.array([half_of[str(r[3])] for r in rows])})
        return out

    def ioi(self):
        names = self.ok(NAMES_M + NAMES_F)
        items = []
        for i in range(self.n):
            a, b = self.rng.choice(names, 2, replace=False)
            t = IOI_T[i % len(IOI_T)]
            io, s = (a, b) if self.rng.random() < .5 else (b, a)
            p = t.format(a=a, b=b, s=s, p=self.rng.choice(PLACES), o=self.rng.choice(OBJS))
            items.append((p, [self.one(io)], [self.one(s)], i))
        return self.emit(items)

    def induction(self):
        V = min(self.tok.vocab_size, 50000)
        items = []
        for i in range(self.n):
            seq = self.rng.integers(1000, V - 1000, size=12)
            k = int(self.rng.integers(3, 10))
            p = self.tok.decode(list(seq) + list(seq[:k]))
            ids = list(seq) + list(seq[:k])
            foil = [int(x) for x in seq if x != seq[k]][:3]
            items.append((ids, [int(seq[k])], foil, i))
        groups = {}
        for ids, tg, fo, key in items:
            groups.setdefault(len(ids), []).append((ids, tg, fo, key))
        out = []
        for L, rows in sorted(groups.items()):
            out.append({"toks": torch.tensor([r[0] for r in rows]), "tg": [r[1] for r in rows], "fo": [r[2] for r in rows],
                        "half": np.array([r[3] % 2 for r in rows])})
        return out

    def greater_than(self):
        two = {}
        for y in range(100):
            ids = self.tok.encode(f" 17{y:02d}", add_special_tokens=False)
            if len(ids) == 2 and ids[0] == self.tok.encode(" 17", add_special_tokens=False)[0]:
                two[y] = ids[1]
        items = []
        for i in range(self.n):
            c = int(self.rng.integers(11, 19))
            yy = int(self.rng.integers(10, 90))
            if yy not in two:
                continue
            ids_c = self.tok.encode(f" {c}", add_special_tokens=False)
            p = f"The {self.rng.choice(GT_NOUNS)} lasted from the year {c}{yy:02d} to the year {c}"
            tg = [two[y] for y in range(yy + 1, 100) if y in two]
            fo = [two[y] for y in range(0, yy) if y in two]
            if len(ids_c) == 1:
                items.append((p, tg, fo, i))
        return self.emit(items)

    def sva(self):
        pairs = [(s, p) for s, p in SVA_N if self.one(s) and self.one(p)]
        items = []
        for i in range(self.n):
            (s1, p1), (s2, p2) = [pairs[j] for j in self.rng.choice(len(pairs), 2, replace=False)]
            plural = self.rng.random() < .5
            subj, attr = (p1, s2) if plural else (s1, p2)
            p = SVA_T[i % len(SVA_T)].format(s=subj, a=attr)
            tg, fo = (" are", " is") if plural else (" is", " are")
            items.append((p, [self.one(tg[1:])], [self.one(fo[1:])], (subj, attr)))
        return self.emit(items)

    def gender(self):
        m, f = self.ok(NAMES_M), self.ok(NAMES_F)
        items = []
        for i in range(self.n):
            male = self.rng.random() < .5
            n = self.rng.choice(m if male else f)
            p = GENDER_T[i % len(GENDER_T)].format(n=n)
            tg, fo = ("he", "she") if male else ("she", "he")
            items.append((p, [self.one(tg)], [self.one(fo)], n))
        return self.emit(items)

    def capital(self):
        caps = [(c, k) for c, k in CAPITALS if self.one(k)]
        items = []
        for i in range(self.n):
            c, k = caps[i % len(caps)]
            fo = [self.one(x) for _, x in caps if x != k]
            p = CAP_T[(i // len(caps)) % len(CAP_T)].format(c=c)
            items.append((p, [self.one(k)], fo, c))
        return self.emit(items)

    def successor(self):
        seqs = [[w for w in s] for s in SEQS]
        items = []
        for i in range(self.n):
            s = seqs[i % len(seqs)]
            if any(self.one(w) is None for w in s):
                s = self.ok(s)
            k = int(self.rng.integers(0, len(s) - 4))
            ctx, nxt = s[k:k + 3], s[k + 3]
            fo = [self.one(w) for w in s if w not in ctx and w != nxt]
            items.append((", ".join(ctx) + ",", [self.one(nxt)], fo, (i % len(seqs), k)))
        return self.emit(items)

    def antonym(self):
        ant = [(a, b) for a, b in ANT if self.one(a) and self.one(b)]
        items = []
        for i in range(self.n):
            idx = self.rng.choice(len(ant), 4, replace=False)
            d = [ant[j] for j in idx]
            p = "".join(f"{a}: {b}\n" for a, b in d[:3]) + f"{d[3][0]}:"
            fo = [self.one(b) for a, b in ant if b != d[3][1]]
            items.append((p, [self.one(d[3][1])], fo, d[3][0]))
        return self.emit(items)

    def past_tense(self):
        """ICL verb -> irregular past; foil = copying the query verb."""
        pairs = [(a, b) for a, b in PAST if self.one(a) and self.one(b)]
        items = []
        for i in range(self.n):
            idx = self.rng.choice(len(pairs), 4, replace=False)
            d = [pairs[j] for j in idx]
            p = "".join(f"{a}: {b}\n" for a, b in d[:3]) + f"{d[3][0]}:"
            items.append((p, [self.one(d[3][1])], [self.one(d[3][0])], d[3][0]))
        return self.emit(items)

    def binding(self):
        cols, objs = self.ok(COLORS), self.ok(CO_OBJ)
        items = []
        for i in range(self.n):
            o = self.rng.choice(objs, 3, replace=False)
            c = self.rng.choice(cols, 3, replace=False)
            q = int(self.rng.integers(0, 3))
            p = " ".join(f"The {o[j]} is {c[j]}." for j in range(3)) + f" The {o[q]} is"
            items.append((p, [self.one(c[q])], [self.one(c[j]) for j in range(3) if j != q], i))
        return self.emit(items)


class Probe:
    """Mean-ablates attention heads through a pre-hook on each layer's output projection (input = concatenated z)."""

    def __init__(self, model):
        self.m = model
        if hasattr(model, "gpt_neox"):
            layers = model.gpt_neox.layers
            self.proj = [l.attention.dense for l in layers]
        else:
            layers = model.model.layers
            self.proj = [l.self_attn.o_proj for l in layers]
        c = model.config
        self.L, self.H = c.num_hidden_layers, c.num_attention_heads
        self.dh = c.hidden_size // self.H
        self.mode, self.capture, self.plan = None, None, None
        self.hooks = [p.register_forward_pre_hook(self._hook(i)) for i, p in enumerate(self.proj)]

    def _hook(self, layer):
        def fn(mod, args):
            x = args[0]
            if self.capture is not None:
                self.capture[layer] = x.detach().float().mean(0)  # [T, d] position-matched mean over the group
            if self.plan is not None and layer in self.plan:
                x = x.clone()
                n = self.n_rows
                for r, h in self.plan[layer]:
                    sl = slice(h * self.dh, (h + 1) * self.dh)
                    rows = slice(r * n, (r + 1) * n)
                    if self.mode == "end":
                        x[rows, -1, sl] = self.mean[layer][-1, sl].to(x.dtype)
                    else:
                        x[rows, :, sl] = self.mean[layer][:, sl].to(x.dtype)
                return (x,)
        return fn

    @staticmethod
    def index(sets, dev):
        """Pad per-prompt token sets into an index tensor and an additive mask (0 / -inf)."""
        k = max(len(x) for x in sets)
        idx = torch.zeros(len(sets), k, dtype=torch.long)
        msk = torch.full((len(sets), k), float("-inf"))
        for i, x in enumerate(sets):
            idx[i, :len(x)] = torch.as_tensor(x)
            msk[i, :len(x)] = 0
        return idx.to(dev), msk.to(dev)

    @staticmethod
    def metric(lg, tg, fo):
        """lg [R, V] with R a multiple of len(tg); tg / fo = (index, mask) for one copy of the prompts."""
        reps = lg.shape[0] // tg[0].shape[0]
        ti, tm = tg[0].repeat(reps, 1), tg[1].repeat(reps, 1)
        fi, fm = fo[0].repeat(reps, 1), fo[1].repeat(reps, 1)
        return (torch.logsumexp(lg.gather(1, ti) + tm, 1) - torch.logsumexp(lg.gather(1, fi) + fm, 1)).cpu()

    @torch.no_grad()
    def run_group(self, g, chunk):
        dev = self.m.device
        toks = g["toks"].to(dev)
        n = len(toks)
        tg, fo = self.index(g["tg"], dev), self.index(g["fo"], dev)
        self.capture = {}
        lg = self.m(toks).logits[:, -1].float()
        self.mean, self.capture = self.capture, None
        clean = self.metric(lg, tg, fo)
        heads = [(l, h) for l in range(self.L) for h in range(self.H)]
        eff = {}
        for mode in ("end", "all"):
            self.mode = mode
            e = np.zeros((n, self.L, self.H), np.float32)
            for i in range(0, len(heads), chunk):
                hs = heads[i:i + chunk]
                self.plan, self.n_rows = {}, n
                for r, (l, h) in enumerate(hs):
                    self.plan.setdefault(l, []).append((r, h))
                x = toks.repeat(len(hs), 1)
                lg2 = self.m(x).logits[:, -1].float()
                self.plan = None
                m2 = self.metric(lg2, tg, fo).view(len(hs), n)
                for r, (l, h) in enumerate(hs):
                    e[:, l, h] = (clean - m2[r]).numpy()
            eff[mode] = e
        return clean.numpy(), eff


def load(family, repo, rev):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if family == "dd":
        import dd_common as dd
        return dd.load(repo, rev, dtype=torch.float32, attn="eager", device=os.environ.get("E89_DEVICE", "cuda"))
    kw = {} if rev == "main" else {"revision": rev}
    tok = AutoTokenizer.from_pretrained(repo, cache_dir=str(mc.HF_CACHE), **kw)
    model = AutoModelForCausalLM.from_pretrained(repo, cache_dir=str(mc.HF_CACHE), torch_dtype=torch.float32,
                                                 attn_implementation="eager", **kw).cuda().eval()
    return model, tok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family")
    ap.add_argument("--repo")
    ap.add_argument("--rev", default="main")
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--chunk", type=int, default=8)
    ap.add_argument("--tasks", default=",".join(TASKS))
    ap.add_argument("--smoke", action="store_true", help="clean metrics only")
    a = ap.parse_args()
    torch.set_grad_enabled(False)
    t0 = time.time()
    model, tok = load(a.family, a.repo, a.rev)
    B = Builder(tok, a.n)
    P = Probe(model)
    res, summ = {}, {"tag": f"{a.family}__{a.repo.split('/')[-1]}__{a.rev}", "tasks": {}}
    for t in a.tasks.split(","):
        groups = getattr(B, t)()
        cl, ends, alls, half = [], [], [], []
        for g in groups:
            if a.smoke:
                P.capture = None
                lg = model(g["toks"].to(model.device)).logits[:, -1].float()
                c = P.metric(lg, P.index(g["tg"], model.device), P.index(g["fo"], model.device)).numpy()
                cl.append(c)
            else:
                c, e = P.run_group(g, a.chunk)
                cl.append(c), ends.append(e["end"]), alls.append(e["all"])
            half.append(g["half"])
        cl, half = np.concatenate(cl), np.concatenate(half)
        summ["tasks"][t] = {"n": int(len(cl)), "groups": len(groups), "metric": float(cl.mean()), "acc": float((cl > 0).mean())}
        res[f"{t}__clean"], res[f"{t}__half"] = cl, half
        if not a.smoke:
            res[f"{t}__end"] = np.concatenate(ends).astype(np.float16)
            res[f"{t}__all"] = np.concatenate(alls).astype(np.float16)
        print(t, summ["tasks"][t], f"{time.time() - t0:.0f}s", flush=True)
    if not a.smoke:
        sys.path.insert(0, str(mc.CACHE / "circuits-over-time"))
        from e81_carriers import generic_roles
        for h in P.hooks:
            h.remove()
        roles = generic_roles(model, tok)
        res.update({f"role__{k}": v for k, v in roles.items()})
        OUT.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(OUT / f"{summ['tag']}.npz", **res)
    summ["seconds"] = time.time() - t0
    if not a.smoke:
        (OUT / f"{summ['tag']}.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ), flush=True)


if __name__ == "__main__":
    main()
