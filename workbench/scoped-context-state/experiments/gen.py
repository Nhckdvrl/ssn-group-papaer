"""P1 matched generator: same closed world + rules, only the discourse scope structure changes.

World: N people, each with a COMPLETE list of attributes (stated as closed: "these are all facts").
Rules (fictional labels, so no parametric knowledge):
  L1 rule: anyone who has p1 and p2 (and does not have n) is a <Label1>.
  L2 rule: anyone who is a <Label1> and has p3 (and does not have n2) is a <Label2>.
Query: is T a <target label>? (Yes/No).  Gold is computed by forward chaining under the
active supposition set implied by the script.

Conditions (same premises, same target, same question sentence where possible):
  B0        no detour                                   gold = ans({})
  FLAT      "In addition, T has a*."                    gold = ans({a*})
  IN        "Suppose T had a*. Under this, is T ...?"   gold = ans({a*})
  OUT       "Suppose T had a*. ... Back in the actual situation ..."  gold = ans({})
  OUTW      OUT with the in-scope conclusion written out first        gold = ans({})
  NEUT      length-matched neutral detour about another person        gold = ans({})
  SIB       suppose a1 / end / suppose a2 / query in B                gold = ans({a2})
  NEST_IN   suppose a1 / suppose a2 / end inner / query (in a1)       gold = ans({a1})
  NEST_OUT  suppose a1 / suppose a2 / end inner / end outer / query   gold = ans({})
"""
import itertools, json, random, sys

NAMES = ["Mira", "Tobias", "Ines", "Karel", "Nadia", "Oskar", "Lena", "Felix", "Yara", "Hugo",
         "Petra", "Ivo", "Selma", "Anton", "Rosa", "Jonas", "Vera", "Emil", "Dora", "Milo",
         "Greta", "Luka", "Tilda", "Bruno", "Alma", "Viktor", "Sonja", "Arno", "Edda", "Pavel"]
ATTRS = ["carries a brass lantern", "wears a green scarf", "owns a small boat", "keeps a pet heron",
         "plays the cello", "has a silver key", "speaks Latin", "grows tomatoes", "wears round glasses",
         "rides a red bicycle", "collects old maps", "brews their own tea"]
LABELS = ["Dorn", "Quill", "Marrow", "Fenwick", "Tarn", "Sable"]
NEUTRAL = ["{o} lives on the third floor and waters the plants every Sunday.",
           "{o} arrived by train on Tuesday and left a coat in the hallway.",
           "{o} is learning to bake bread and has already ruined two loaves."]


def has_attr_phrase(a):  # "carries a brass lantern" -> "carries a brass lantern"
    return a


def neg_phrase(a):  # "does not <verb> ..." built by swapping the leading verb
    v, rest = a.split(" ", 1)
    base = {"carries": "carry", "wears": "wear", "owns": "own", "keeps": "keep", "plays": "play",
            "has": "have", "speaks": "speak", "grows": "grow", "rides": "ride", "collects": "collect",
            "brews": "brew"}[v]
    return f"does not {base} {rest}"


def gerund_cond(a):  # for rule text: "carries a brass lantern" -> "carries a brass lantern"
    return a


def make_world(rng, depth):
    """Random rules + people. Returns dict."""
    attrs = rng.sample(ATTRS, 7)
    labels = rng.sample(LABELS, 2)
    p1, p2, n1, p3, n2, extra = attrs[0], attrs[1], attrs[2], attrs[3], attrs[4], attrs[5]
    rules = [dict(head=labels[0], pos=[p1, p2], neg=[n1])]
    if depth == 2:
        rules.append(dict(head=labels[1], pos=[("L", labels[0]), p3], neg=[n2]))
    target = labels[depth - 1]
    people = rng.sample(NAMES, 6)
    facts = {}
    for pn in people:
        facts[pn] = set(a for a in attrs if rng.random() < 0.45)
    return dict(attrs=attrs, rules=rules, target=target, people=people, facts=facts)


def derive(world, person, extra=frozenset()):
    have = set(world["facts"][person]) | set(extra)
    labs = set()
    for r in world["rules"]:  # rules are listed in dependency order
        ok = all((p[1] in labs) if isinstance(p, tuple) else (p in have) for p in r["pos"])
        ok = ok and all(n not in have for n in r["neg"])
        if ok:
            labs.add(r["head"])
    return labs


def world_labels(world):
    return {r["head"] for r in world["rules"]}


def answer(world, person, extra=frozenset()):
    return "Yes" if world["target"] in derive(world, person, extra) else "No"


def rule_text(r):
    parts = []
    for p in r["pos"]:
        parts.append(f"is a {p[1]}" if isinstance(p, tuple) else p)
    s = " and ".join(parts) if len(parts) <= 2 else ", ".join(parts)
    if r["neg"]:
        s += ", but " + " and ".join(neg_phrase(n) for n in r["neg"]) + ","
    return f"Anyone who {s} is a {r['head']}."


def world_text(world):
    lines = ["Rules:"]
    for r in world["rules"]:
        lines.append("- " + rule_text(r))
    lines.append("")
    lines.append("Here is everything we know about each person. These lists are complete: "
                 "a person has no attribute that is not listed.")
    for pn in world["people"]:
        at = [a for a in world["attrs"] if a in world["facts"][pn]]
        lines.append(f"- {pn}: " + ("; ".join(at) if at else "(no listed attributes)") + ".")
    return "\n".join(lines)


def cond_flip_candidates(world, T):
    return [a for a in world["attrs"] if a not in world["facts"][T]]


def sample_item(rng, depth, kind, want=None):
    """Sample a world+target person such that the required answer pattern for `kind` holds."""
    for _ in range(20000):
        w = make_world(rng, depth)
        T = rng.choice(w["people"])
        cands = cond_flip_candidates(w, T)
        base = answer(w, T)
        if want is not None and base != want:
            continue
        if kind in ("single",):
            good = [a for a in cands if answer(w, T, {a}) != base]
            if good:
                return w, T, dict(a=rng.choice(good))
        elif kind == "sib":
            opts = [(a1, a2) for a1, a2 in itertools.permutations(cands, 2)
                    if answer(w, T, {a2}) != base and answer(w, T, {a2}) != answer(w, T, {a1, a2})]
            if opts:
                a1, a2 = rng.choice(opts)
                return w, T, dict(a1=a1, a2=a2)
        elif kind == "nest":
            opts = []
            for a1, a2 in itertools.permutations(cands, 2):
                g_in = answer(w, T, {a1})
                # nest_in gold ans({a1}) != ans({a1,a2}) and != base
                # nest_out gold base != ans({a1}) (so that leaking outer is detectable) and != ans({a1,a2})
                if g_in != base and g_in != answer(w, T, {a1, a2}):
                    opts.append((a1, a2))
            if opts:
                a1, a2 = rng.choice(opts)
                return w, T, dict(a1=a1, a2=a2)
    raise RuntimeError("no item")


def person_attr(T, a):
    return f"{T} {a}"


def hyp(T, a, first=True):
    return f"Suppose, purely hypothetically, that {T} {a}." if first else f"Now suppose, purely hypothetically, that {T} {a}."


def qtxt(w, T, prefix=""):
    return f"{prefix}Is {T} a {w['target']}? Answer with Yes or No."


INSTR = ("Read the passage and answer the question at the end. "
         "Finish your reply with a final line of the form 'Answer: Yes' or 'Answer: No'.\n\n")


def build(kind_cond, w, T, sup, rng):
    base_txt = world_text(w)
    a = sup.get("a")
    other = rng.choice([p for p in w["people"] if p != T])
    if kind_cond == "B0":
        det, q, gold = "", qtxt(w, T), answer(w, T)
    elif kind_cond == "FLAT":
        det = f"In addition, {T} {a}."
        q, gold = qtxt(w, T), answer(w, T, {a})
    elif kind_cond == "IN":
        det = hyp(T, a)
        q, gold = qtxt(w, T, "Under this supposition, "), answer(w, T, {a})
        q = f"Under this supposition, is {T} a {w['target']}? Answer with Yes or No."
    elif kind_cond == "OUT":
        det = hyp(T, a) + " That was only a thought experiment; it is not true."
        q, gold = qtxt(w, T, "In the actual situation, ").replace("Is ", "is ", 1), answer(w, T)
        q = f"In the actual situation, is {T} a {w['target']}? Answer with Yes or No."
    elif kind_cond == "OUTW":
        conc = answer(w, T, {a})
        det = (hyp(T, a) + f" Under that supposition, {T} {'would' if conc == 'Yes' else 'would not'} be a "
               f"{w['target']}. That was only a thought experiment; it is not true.")
        q, gold = f"In the actual situation, is {T} a {w['target']}? Answer with Yes or No.", answer(w, T)
    elif kind_cond == "NEUT":
        det = "Meanwhile, " + rng.choice(NEUTRAL).format(o=other) + " " + rng.choice(NEUTRAL).format(o=other) \
              + " That is all just background."
        q, gold = f"In the actual situation, is {T} a {w['target']}? Answer with Yes or No.", answer(w, T)
    elif kind_cond == "SIB":
        a1, a2 = sup["a1"], sup["a2"]
        det = (hyp(T, a1) + " That was only a thought experiment; it is not true. "
               + hyp(T, a2, first=False))
        q, gold = f"Under this second supposition only, is {T} a {w['target']}? Answer with Yes or No.", answer(w, T, {a2})
    elif kind_cond == "NEST_IN":
        a1, a2 = sup["a1"], sup["a2"]
        det = (hyp(T, a1) + f" Inside that supposition, further suppose that {T} {a2}. "
               f"Now drop only the further supposition {T} {a2}; keep the first supposition.")
        q, gold = f"Under the first supposition only, is {T} a {w['target']}? Answer with Yes or No.", answer(w, T, {a1})
    elif kind_cond == "NEST_OUT":
        a1, a2 = sup["a1"], sup["a2"]
        det = (hyp(T, a1) + f" Inside that supposition, further suppose that {T} {a2}. "
               f"Now drop the further supposition, and then drop the first supposition as well; both were only thought experiments.")
        q, gold = f"In the actual situation, is {T} a {w['target']}? Answer with Yes or No.", answer(w, T)
    else:
        raise ValueError(kind_cond)
    prompt = INSTR + base_txt + ("\n\n" + det if det else "") + "\n\n" + q
    return prompt, gold


CONDS_SINGLE = ["B0", "FLAT", "IN", "OUT", "OUTW", "NEUT"]


def main(n_per_depth=40, seed=0, out="items.jsonl"):
    rng = random.Random(seed)
    items = []
    idx = 0
    for depth in (1, 2):
        for i in range(n_per_depth):
            # balance base answer: resample until base answer matches wanted parity
            want = "Yes" if i % 2 == 0 else "No"
            while True:
                w, T, sup = sample_item(rng, depth, "single")
                if answer(w, T) == want:
                    break
            for c in CONDS_SINGLE:
                p, g = build(c, w, T, sup, random.Random(rng.random()))
                items.append(dict(id=f"s{idx}", family="single", depth=depth, cond=c, gold=g, prompt=p,
                                  base=answer(w, T), T=T, sup=sup))
            idx += 1
    for fam, kind, conds in (("sib", "sib", ["SIB"]), ("nest", "nest", ["NEST_IN", "NEST_OUT"])):
        for depth in (1, 2):
            for i in range(n_per_depth // 2):  # n_per_depth//2 worlds per depth
                w, T, sup = sample_item(rng, depth, kind, want="No")  # sib/nest are only satisfiable with base answer No (monotone rules); see README
                # also a flat "B0" control for the same world: prerequisite competence on base
                for c in ["B0"] + conds:
                    if kind == "sib":
                        # SIB needs a1,a2 ; B0 ignores
                        pass
                    p, g = build(c, w, T, sup, random.Random(rng.random()))
                    items.append(dict(id=f"{fam}{depth}_{idx}", family=fam, depth=depth, cond=c, gold=g, prompt=p,
                                      base=answer(w, T), T=T, sup=sup))
                idx += 1
    with open(out, "w") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    print(len(items), "prompts ->", out)


if __name__ == "__main__":
    main(*(int(x) if x.lstrip("-").isdigit() else x for x in sys.argv[1:]))
