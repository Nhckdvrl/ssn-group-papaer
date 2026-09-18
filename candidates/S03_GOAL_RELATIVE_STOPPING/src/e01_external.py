"""
S03 — does the phenomenon depend on the stopping ARCHITECTURE?

OLMo reuses the native pretraining <|endoftext|> to terminate an assistant turn.
Qwen-2.5 and Llama-3.1 instead introduce a separate end-of-turn token
(<|im_end|>, <|eot_id|>).  If the goal-relative stopping effect is about
assistant stopping acquisition rather than about OLMo's token wiring, it should
appear in both architectures — and in the new-EOT families it should appear
specifically on the token that actually ends the turn.

Scores the document-end token and the end-of-turn token separately, so a base
and an instruct checkpoint are compared on an identical token set.
"""
import json, math, sys
from collections import defaultdict

EPS = 1e-45


def mean(v): return sum(v) / len(v) if v else float("nan")


def boot_ci(v, n=20000, seed=0):
    import random
    rng = random.Random(seed); k = len(v)
    ms = sorted(mean([v[rng.randrange(k)] for _ in range(k)]) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n)]


def sign_test(v):
    pos = sum(1 for x in v if x > 0); neg = sum(1 for x in v if x < 0)
    n = pos + neg
    if n == 0: return 1.0, pos, neg
    tail = sum(math.comb(n, k) for k in range(min(pos, neg) + 1)) / 2 ** n
    return min(1.0, 2 * tail), pos, neg


def main():
    pos = "p2"
    print(f"{'checkpoint':<28}{'token':<18}{'dz_stop':>9}{'95% CI':>16}"
          f"{'sign':>9}{'d log p':>9}")
    print("-" * 90)
    for spec in sys.argv[1:]:
        label, _, path = spec.partition("=")
        rows = [json.loads(l) for l in open(path)]
        for nm in ("doc", "eot"):
            key = f"cmp_{pos}_stop_logit_{nm}"
            if key not in rows[0]:
                continue
            dz = [r[key] - r[f"inc_{pos}_stop_logit_{nm}"] for r in rows]
            dp = [math.log(max(r[f"cmp_{pos}_p_stop_{nm}"], EPS))
                  - math.log(max(r[f"inc_{pos}_p_stop_{nm}"], EPS)) for r in rows]
            lo, hi = boot_ci(dz); p, a, b = sign_test(dz)
            tokname = {"doc": "document-end", "eot": "end-of-turn"}[nm]
            print(f"{label:<28}{tokname:<18}{mean(dz):>9.2f}"
                  f"{f'[{lo:.1f},{hi:.1f}]':>16}{f'{a}/{b}':>9}{mean(dp):>9.2f}")
        print()


if __name__ == "__main__":
    main()
