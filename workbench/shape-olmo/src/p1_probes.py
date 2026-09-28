"""P1: controlled probes after Li & Merrill 2606.20936 §3/App. C, with a counterbalanced design so a
below-chance result can be attributed (queried-entity position, option order, name).

usage: p1_probes.py MODEL_PATH TAG   -> results/p1/<TAG>.jsonl (one row per item)
Families (d = filler words between cue and target, d in {32,64,128,256,512,1024}):
  entity  : "X carried the <obj1>. Y carried the <obj2>. <filler> Q: Who carried the <objq>?
             (A) <n1> (B) <n2> Answer:"   score " n_correct" vs " n_wrong"
  pronoun : "X is the <role1>. Y is the <role2>. <filler> The <roleq> reviewed the report, and"
             score " he" vs " she"
  closure : "<tag>\\n<filler>\\n" then NLL of "</tag>"
Filler: sentences from our Wikipedia sample docs (fixed seed), entity/role words never occur in it.
Counterbalancing per item index: queried = first/second mention, option order, gender order.
"""
import json, os, random, sys
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = [32, 64, 128, 256, 512, 1024]
N_PER = 96  # multiple of 8 for full counterbalancing (2 query x 2 order x 2 gender-order)
FEM = ["Julia", "Sofia", "Naomi", "Clara", "Maya", "Elena", "Grace", "Nora", "Alice", "Lucy"]
MAS = ["Liam", "Oscar", "Henry", "Felix", "Jonah", "Victor", "Owen", "Leo", "Adam", "Hugo"]
OBJ = ["orange notebook", "green folder", "blue umbrella", "red lamp", "silver key", "wooden box",
       "yellow scarf", "black camera", "white mug", "brown suitcase"]
ROLES = ["violinist", "pilot", "baker", "surgeon", "architect", "librarian", "chemist", "sailor",
         "painter", "lawyer"]
TAGS = ["section", "header", "article", "aside", "footer", "table", "figure", "details"]


def filler_pool():
    """Whole prose sentences (8-40 words) from our Wikipedia sample, none containing probe words."""
    import re
    banned = set(FEM + MAS + ROLES + TAGS + [w for o in OBJ for w in o.split()])
    sents = []
    for line in open(f"{ROOT}/data/docs_wikipedia.jsonl"):
        for s in re.split(r"(?<=[.!?])\s+", json.loads(line)["text"].replace("\n", " ")):
            w = s.split()
            if 8 <= len(w) <= 40 and s[-1] in ".!?" and not banned & {x.strip(".,;:()\"'") for x in w}:
                sents.append(s)
        if len(sents) > 20000:
            break
    return sents


def filler(rng, pool, d):
    """Consecutive-in-pool whole sentences until at least d words."""
    i = rng.randrange(0, len(pool) - 200); out, n = [], 0
    while n < d:
        out.append(pool[i]); n += len(pool[i].split()); i += 1
    return " ".join(out)


def items():
    pool = filler_pool()
    rng = random.Random(20260928)
    out = []
    for d in DIST:
        for k in range(N_PER):
            q_first, a_first, fem_first = k % 2, (k // 2) % 2, (k // 4) % 2
            f = filler(rng, pool, d)
            # entity tracking: two same-gender names
            names = rng.sample(FEM if fem_first else MAS, 2); objs = rng.sample(OBJ, 2)
            qi = 0 if q_first else 1
            opts = names if a_first else names[::-1]
            ctx = (f"{names[0]} carried the {objs[0]}. {names[1]} carried the {objs[1]}. {f} "
                   f"Q: Who carried the {objs[qi]}? (A) {opts[0]} (B) {opts[1]} Answer:")
            out.append(dict(fam="entity", d=d, k=k, q_first=q_first, a_first=a_first, ctx=ctx,
                            pos=" " + names[qi], neg=" " + names[1 - qi],
                            correct_is_A=int(opts[0] == names[qi])))
            # pronoun memory: one female one male, gender order counterbalanced
            fn, mn = rng.choice(FEM), rng.choice(MAS); roles = rng.sample(ROLES, 2)
            people = [(fn, " she"), (mn, " he")] if fem_first else [(mn, " he"), (fn, " she")]
            ctx = (f"{people[0][0]} is the {roles[0]}. {people[1][0]} is the {roles[1]}. {f} "
                   f"The {roles[qi]} reviewed the report, and")
            out.append(dict(fam="pronoun", d=d, k=k, q_first=q_first, fem_first=fem_first, ctx=ctx,
                            pos=people[qi][1], neg=people[1 - qi][1]))
            # structural closure
            tg = rng.choice(TAGS)
            out.append(dict(fam="closure", d=d, k=k, ctx=f"<{tg}>\n{f}\n", pos=f"</{tg}>", neg=None))
    return out


@torch.no_grad()
def logp(model, tok, ctx, cont):
    a = tok(ctx, add_special_tokens=False).input_ids
    b = tok(ctx + cont, add_special_tokens=False).input_ids
    assert b[:len(a)] == a, "tokenization boundary shift"
    x = torch.tensor(b, device="cuda")[None]
    lp = torch.log_softmax(model(input_ids=x).logits[0, :-1].float(), -1)
    return sum(lp[i - 1, b[i]].item() for i in range(len(a), len(b)))


def main(path, tag):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(path)
    model = AutoModelForCausalLM.from_pretrained(path, dtype=torch.bfloat16, device_map="cuda").eval()
    os.makedirs(f"{ROOT}/results/p1", exist_ok=True)
    with open(f"{ROOT}/results/p1/{tag}.jsonl", "w") as f:
        for it in items():
            it["lp_pos"] = logp(model, tok, it["ctx"], it["pos"])
            it["lp_neg"] = logp(model, tok, it["ctx"], it["neg"]) if it["neg"] else None
            it.pop("ctx")
            f.write(json.dumps(it) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
