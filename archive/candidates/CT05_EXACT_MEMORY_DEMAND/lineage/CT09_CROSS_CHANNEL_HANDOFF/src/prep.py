"""E00 items: paired key-value contexts that differ only in the target value (A vs B vs donor 0).

Every item stores token-level ids so the runner does no tokenization decisions of its own.
Constraints enforced by resampling: vA, vB, v0 have the same token count; contexts A, B, 0,
A_recent, B_recent have the same token length N; the target line starts after SINK tokens.
"""
import json, random, sys
from transformers import AutoTokenizer

CONS, VOW = "BDFGJKLMNPRSTVXZ", "AEIOU"
INTRO = "Below is a list of code words and their secret values. Memorize them.\n\n"
Q = {
    "late": ("\nQuestion: What is the secret value of {k}?\nAnswer:", " The secret value of {t} is"),
    "early": ("\nQuestion: What is the secret value of {k}?\n", "Answer:"),
}
NPAIRS = 40


def word(rng, n):
    return "".join(rng.choice(CONS) if i % 2 == 0 else rng.choice(VOW) for i in range(n))


def ctx_text(pairs):
    return INTRO + "".join(f"{k}: {v}\n" for k, v in pairs)


def make(tok, rng, idx):
    enc = lambda s: tok(s, add_special_tokens=False).input_ids
    while True:
        keys = list(dict.fromkeys(word(rng, 5) for _ in range(3 * NPAIRS)))[:NPAIRS]
        vals = list(dict.fromkeys(word(rng, 4) for _ in range(3 * NPAIRS)))
        if len(keys) < NPAIRS or len(vals) < NPAIRS + 3:
            continue
        dist, (vA, vB, v0) = vals[:NPAIRS], vals[NPAIRS:NPAIRS + 3]
        vt = [enc(" " + v) for v in (vA, vB, v0)]
        if len({len(x) for x in vt}) != 1:
            continue
        ti = rng.randrange(2, NPAIRS - 2)
        ni = rng.choice([i for i in range(NPAIRS) if i != ti])
        k, k2 = keys[ti], keys[ni]
        pairs = list(zip(keys, dist))
        ctx = {}
        for name, v in (("A", vA), ("B", vB), ("0", v0)):
            p = pairs.copy(); p[ti] = (k, v); ctx[name] = enc(ctx_text(p))
            r = [q for i, q in enumerate(p) if i != ti] + [(k, v)]
            if name != "0":
                ctx[name + "_recent"] = enc(ctx_text(r))
        if len({len(x) for x in ctx.values()}) != 1:
            continue
        item = dict(id=idx, key=k, noread_key=k2, target_index=ti, vA=vA, vB=vB, v0=v0,
                    val_ids=dict(A=vt[0], B=vt[1]), ctx=ctx, N=len(ctx["A"]))
        for cut, (q, p) in Q.items():
            item[f"q_{cut}"] = enc(q.format(k=k))
            item[f"p_{cut}"] = enc(p.format(t=k))
        item["q_noread"] = enc(Q["late"][0].format(k=k2))
        return item


if __name__ == "__main__":
    tok = AutoTokenizer.from_pretrained(sys.argv[1])
    n, out = int(sys.argv[2]), sys.argv[3]
    rng = random.Random(20260927)
    with open(out, "w") as f:
        for i in range(n):
            f.write(json.dumps(make(tok, rng, i)) + "\n")
