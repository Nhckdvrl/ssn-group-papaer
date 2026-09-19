"""E01-A step 3: forward (in-context) semantic-understanding gate + baseline neutral belief.

Runs on DEVELOPMENT propositions only.  Compares a small number of measurement
interfaces; the winner is frozen before any post-training critical result.
"""
import json, argparse, statistics as st
import torch
from generator import generate, GOLD, CRITICAL, DIRECT
import scoring
from scoring import BeliefScorer, QUERY_FAMILY, load_base

CELLS = CRITICAL + DIRECT

# ------- interface variants (E01-A tuning surface) -------------------------
FEWSHOT_CTX = (
    "Context: The harbour bell was rung at dawn.\n"
    "Question: Was the harbour bell rung at dawn?\n"
    "Answer: Yes\n\n"
    "Context: The eastern gate stayed shut all week.\n"
    "Question: Was the eastern gate opened during the week?\n"
    "Answer: No\n\n"
    "Context: A second copy of the ledger was printed on Tuesday.\n"
    "Question: Was a second copy of the ledger printed?\n"
    "Answer: Yes\n\n"
    "Context: The survey team never left the base camp.\n"
    "Question: Did the survey team leave the base camp?\n"
    "Answer: No\n\n"
)

def iface_prompt(variant, question, context):
    if variant == "ctx_fewshot":
        pre = FEWSHOT_CTX
    elif variant == "plain_fewshot":
        pre = scoring.FEWSHOT
    elif variant == "nofewshot":
        pre = ""
    else:
        raise ValueError(variant)
    s = pre
    if context:
        s += f"Context: {context}\n"
    s += f"Question: {question}\nAnswer:"
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--pool", default="dev")
    ap.add_argument("--out", default="results/e01a/forward_gate.json")
    args = ap.parse_args()

    props = generate(args.pool, args.n)
    model, tok = load_base()
    sc = BeliefScorer(model, tok)

    report = {"pool": args.pool, "n": args.n,
              "model": scoring.MODEL_ID, "revision": scoring.REVISION,
              "variants": {}}

    for variant in ["ctx_fewshot", "plain_fewshot", "nofewshot"]:
        prompts, idx = [], []
        for pi, p in enumerate(props):
            for c in CELLS:
                for qi, qf in enumerate(QUERY_FAMILY):
                    prompts.append(iface_prompt(variant, qf(p), p["sent"][c]))
                    idx.append((pi, c, qi))
        vals = sc.score_prompts(prompts, batch_size=64)
        # per (prop, cell): mean over query family
        agg = {}
        for (pi, c, qi), v in zip(idx, vals):
            agg.setdefault((pi, c), []).append(v)
        cells = {}
        for c in CELLS:
            bs = [sum(agg[(pi, c)]) / len(agg[(pi, c)]) for pi in range(len(props))]
            gold = GOLD[c]
            acc = sum((b > 0) == gold for b in bs) / len(bs)
            cells[c] = {"mean_B": st.mean(bs), "sd_B": st.pstdev(bs),
                        "acc": acc, "gold": gold,
                        "per_query_acc": [
                            sum((agg[(pi, c)][qi] > 0) == gold for pi in range(len(props))) / len(props)
                            for qi in range(len(QUERY_FAMILY))]}
        overall = st.mean([cells[c]["acc"] for c in CRITICAL])
        report["variants"][variant] = {"cells": cells, "critical_mean_acc": overall}
        print(f"\n### interface = {variant}   critical mean acc = {overall:.3f}")
        for c in CELLS:
            d = cells[c]
            print(f"  {c}  gold={'p' if d['gold'] else '~p':>2}  "
                  f"meanB={d['mean_B']:+7.3f}  sd={d['sd_B']:5.2f}  acc={d['acc']:.3f}  "
                  f"perQ={[round(x,2) for x in d['per_query_acc']]}")

    # ---- baseline neutral belief (no context), both prefixes
    base = {}
    for variant in ["plain_fewshot", "nofewshot"]:
        prompts = [iface_prompt(variant, qf(p), None) for p in props for qf in QUERY_FAMILY]
        vals = sc.score_prompts(prompts, batch_size=64)
        nq = len(QUERY_FAMILY)
        per = [vals[i * nq:(i + 1) * nq] for i in range(len(props))]
        mean = [sum(r) / nq for r in per]
        base[variant] = {"mean_B": st.mean(mean), "sd_B": st.pstdev(mean),
                         "frac_yes": sum(b > 0 for b in mean) / len(mean),
                         "per_query_mean": [st.mean([r[q] for r in per]) for q in range(nq)],
                         "per_prop": mean}
        d = base[variant]
        print(f"\n### baseline neutral belief ({variant}): meanB={d['mean_B']:+.3f} "
              f"sd={d['sd_B']:.2f} fracYes={d['frac_yes']:.2f} "
              f"perQ={[round(x,2) for x in d['per_query_mean']]}")
    report["baseline_neutral"] = base

    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nwrote {args.out}")

if __name__ == "__main__":
    main()
