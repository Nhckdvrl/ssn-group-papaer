"""
L41 proposition generator.

Contract (frozen before E01-B):
  p_i = "<Agent> <verb> <Object> <num>."
  - Agent: invented two-syllable personal name, no real-world referent.
  - Event: simple telic action on a numbered facility object.
  - Complement contains no negation, modality, factivity or attitude material.
  - `manage to <complement>` and `fail to <complement>` are both natural.

Realizations of the same identity p:

  M+ : <Agent> managed to <complement>.         =>  p
  M- : <Agent> did not manage to <complement>.  => ~p
  F+ : <Agent> failed to <complement>.          => ~p
  F- : <Agent> did not fail to <complement>.    =>  p
  A+ : <Agent> <past> <complement-obj>.         =>  p   (direct assertion, control)
  A- : <Agent> did not <complement>.            => ~p   (direct denial, control)

Neutral query: "Did <Agent> <complement>?"  -> Yes / No

Disjoint identity pools are drawn by `pool` name so that development
propositions can never leak into the critical confirmation set.
"""
import random, json, hashlib

# ---------------------------------------------------------------- name pool
ONSET = ["N", "V", "T", "K", "M", "S", "D", "R", "L", "P", "B", "Z", "Th", "Gr", "Dr", "Fr", "Qu", "Br", "Kr", "Ph"]
NUC1  = ["e", "a", "o", "i", "u", "ae", "ei", "ia"]
CODA  = ["r", "l", "n", "s", "v", "rk", "ld", "st", "m", "th"]
NUC2  = ["a", "i", "o", "e", "an", "in", "on", "en", "is", "us", "ar", "or"]

def _names(rng, n):
    out, seen = [], set()
    while len(out) < n:
        w = rng.choice(ONSET) + rng.choice(NUC1) + rng.choice(CODA) + rng.choice(NUC2)
        w = w.capitalize()
        if len(w) < 5 or len(w) > 8 or w in seen:
            continue
        seen.add(w); out.append(w)
    return out

# ------------------------------------------------------------- event frames
# (bare_verb, past_verb, object_noun)
# all telic, physically simple, equally natural under `manage to` / `fail to`
EVENTS = [
    ("enter",    "entered",    "Chamber"),
    ("open",     "opened",     "Archive"),
    ("cross",    "crossed",    "Bridge"),
    ("reach",    "reached",    "Platform"),
    ("unlock",   "unlocked",   "Vault"),
    ("repair",   "repaired",   "Relay"),
    ("board",    "boarded",    "Shuttle"),
    ("retrieve", "retrieved",  "Canister"),
    ("seal",     "sealed",     "Hatch"),
    ("activate", "activated",  "Beacon"),
    ("descend to", "descended to", "Level"),
    ("recover",  "recovered",  "Module"),
    ("close",    "closed",     "Conduit"),
    ("locate",   "located",    "Marker"),
    ("secure",   "secured",    "Locker"),
    ("restart",  "restarted",  "Pump"),
]

class Prop(dict):
    """A proposition identity plus its six sentence realizations."""
    __getattr__ = dict.__getitem__

def make_prop(name, verb, past, noun, num):
    comp = f"{verb} {noun} {num}"           # "enter Chamber 47"
    comp_past = f"{past} {noun} {num}"      # "entered Chamber 47"
    return Prop(
        pid=hashlib.sha1(f"{name}|{comp}".encode()).hexdigest()[:12],
        agent=name, verb=verb, past=past, noun=noun, num=num,
        complement=comp, complement_past=comp_past,
        p_text=f"{name} {comp_past}.",
        sent={
            "Mp": f"{name} managed to {comp}.",
            "Mn": f"{name} did not manage to {comp}.",
            "Fp": f"{name} failed to {comp}.",
            "Fn": f"{name} did not fail to {comp}.",
            "Ap": f"{name} {comp_past}.",
            "An": f"{name} did not {comp}.",
        },
        query=f"Did {name} {comp}?",
    )

# semantic gold: does the sentence commit to p ?
GOLD = {"Mp": True, "Mn": False, "Fp": False, "Fn": True, "Ap": True, "An": False}
CRITICAL = ["Mp", "Mn", "Fp", "Fn"]
DIRECT = ["Ap", "An"]

POOL_SEED = {"dev": 41_0001, "dev2": 41_0002, "crit": 41_0003, "pilot": 41_0004,
             "hold": 41_0005}
NAME_SEED = 41_0000          # ONE global name stream, partitioned by pool index
POOL_SPAN = 900              # so no two pools can ever share an agent name


def generate(pool, n):
    """Deterministic proposition identities; agent names are disjoint by pool."""
    rng = random.Random(POOL_SEED[pool])
    names = _names(random.Random(NAME_SEED), POOL_SPAN * len(POOL_SEED))
    idx = list(POOL_SEED).index(pool)
    names = names[idx * POOL_SPAN:(idx + 1) * POOL_SPAN]
    assert n <= len(names), f"pool {pool} exhausted"
    props, used = [], set()
    i = 0
    while len(props) < n:
        nm = names[i % len(names)]; i += 1
        verb, past, noun = EVENTS[rng.randrange(len(EVENTS))]
        num = rng.randrange(11, 99)
        key = (nm, verb, noun, num)
        if key in used or nm in {p["agent"] for p in props}:
            continue
        used.add(key)
        props.append(make_prop(nm, verb, past, noun, num))
    return props

if __name__ == "__main__":
    import sys
    pool = sys.argv[1] if len(sys.argv) > 1 else "dev"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    for p in generate(pool, n):
        print(json.dumps({"pid": p["pid"], "query": p["query"], **p["sent"]}, ensure_ascii=False))
