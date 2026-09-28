"""L34 E01 — phase corpora. Frozen by E01_PREREGISTRATION.md §3."""
import json, os, random
import bios
from bios import ATTRS, FAMILY_A, FAMILY_B, bio_text, qa_text, ORDERS

D = os.path.join(os.path.dirname(__file__), "..", "data")


def load():
    return json.load(open(os.path.join(D, "people.json"))), json.load(open(os.path.join(D, "pools.json")))


def _bios(people):
    """One sample per (person, clause-order). Loss on every token."""
    return [{"prompt": "", "target": bio_text(p, o), "kind": "bio"}
            for p in people for o in range(len(ORDERS))]


def _qa(people, attrs, t=0):
    out = []
    for p in people:
        for a in attrs:
            q, v = qa_text(p["name"], a, p["attrs"][a], t)
            out.append({"prompt": q, "target": v, "kind": "qa", "attr": a})
    return out


def phase0a(sets):
    """FORMAT bios + balanced FORMAT QA -> bio format, QA format, extraction."""
    return _bios(sets["FORMAT"]) + _qa(sets["FORMAT"], ATTRS)


def phase0b(sets):
    """OLD facts encoded here, under a balanced access policy."""
    return _bios(sets["OLD"])


def phase1(sets, arm, seed):
    """Access curriculum. QA about PIT persons whose bios are NEVER shown."""
    pit = sets["PIT"]
    if arm == "NO_PIT":
        return []
    if arm == "PIT_A":
        s = _qa(pit, FAMILY_A)
    elif arm == "PIT_B":
        s = _qa(pit, FAMILY_B)
    elif arm == "PIT_BAL":
        h = len(pit) // 2
        s = _qa(pit[:h], FAMILY_A) + _qa(pit[h:], FAMILY_B)
    else:
        raise ValueError(arm)
    random.Random(1000 + seed).shuffle(s)
    return s


def phase2(sets, seed):
    """NEW facts. Identical content across arms; order fixed by seed only."""
    s = _bios(sets["NEW"])
    random.Random(2000 + seed).shuffle(s)
    return s


def eval_items(sets, pools, n_distract=15, seed=7):
    """Per (age, person, attr, template) evaluation item with distractor set."""
    rng = random.Random(seed)
    items = []
    for age in ("OLD", "NEW"):
        for p in sets[age]:
            for a in ATTRS:
                gold = p["attrs"][a]
                pool = [x for x in pools[a] if x != gold]
                dis = rng.sample(pool, min(n_distract, len(pool)))
                for t in range(3):
                    q, _ = qa_text(p["name"], a, gold, t)
                    items.append({"age": age, "name": p["name"], "attr": a,
                                  "family": bios.FAMILY[a], "tmpl": t,
                                  "prompt": q, "gold": gold, "distract": dis})
    return items


if __name__ == "__main__":
    sets, pools = load()
    for nm, s in [("0a", phase0a(sets)), ("0b", phase0b(sets)),
                  ("1/PIT_A", phase1(sets, "PIT_A", 0)), ("1/PIT_BAL", phase1(sets, "PIT_BAL", 0)),
                  ("2", phase2(sets, 0))]:
        print(f"phase {nm:12s} n={len(s):6d}  ex={s[0]['prompt'][:40]!r}->{s[0]['target'][:50]!r}")
    ev = eval_items(sets, pools)
    print("eval items", len(ev), ev[0])
