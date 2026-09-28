"""CT03 CPD v1 reporting: ladder table, training summary, free-gen adjudication."""
import json, sys
import numpy as np


def ladder():
    c = json.load(open("results/cpd_calib.json"))
    print(f"calib tokens {c['n_calib_tokens']}   rule: {c['delta_rule']}")
    print(f"{'delta':>7}{'layer':>7}{'beta':>11}{'chg_frac':>10}{'mean_chg':>10}"
          f"{'chg|chg':>9}{'kl_med':>9}{'kl_p90':>9}")
    for d, cell in c["ladder"].items():
        for l, v in cell.items():
            print(f"{d:>7}{l:>7}{v['beta']:>11.4f}{v['changed_frac']:>10.3f}"
                  f"{v['mean_experts_changed']:>10.3f}"
                  f"{v['experts_changed_given_changed']:>9.2f}"
                  f"{v['kl_median']:>9.4f}{v['kl_p90']:>9.4f}")
    print(f"\nDELTA CHOSEN BY RULE: {c.get('delta_auto')}  (used: {c['delta']})")
    print(f"beta: {c['beta']}")


def train():
    for arm in ("cpd", "shuffled", "router_ce"):
        try:
            R = [json.loads(l) for l in open(f"results/cpd_train_{arm}.jsonl")]
        except FileNotFoundError:
            continue
        L = np.array([r["loss"] for r in R])
        print(f"{arm:>10}  steps={len(R)}  loss {L[:20].mean():.4f} -> {L[-20:].mean():.4f}"
              f"  drift={[round(x,4) for x in R[-1]['drift']]}")
        if arm == "shuffled":
            print(f"            |F| mean {np.mean([r.get('shuf_feasible_n') or 0 for r in R]):.1f}"
                  f"   max KL resid {max(r.get('shuf_kl_resid', 0) for r in R):.2e}")


def freegen():
    R = [json.loads(l) for l in open("results/cpd_freegen.jsonl")]
    arms = sorted({r["arm"] for r in R}, key=lambda a: ("base", "router_ce", "shuffled", "cpd").index(a))
    by = {a: {r["qi"]: r for r in R if r["arm"] == a} for a in arms}
    qs = sorted(by["base"])
    n = len(qs)
    acc = {a: np.mean([by[a][q]["correct"] for q in qs]) for a in arms}
    print(f"{'arm':>11}{'acc':>8}{'vs base':>10}{'same_as_base':>14}{'first_div':>11}"
          f"{'KL(shared)':>12}{'ovlL36':>9}{'ovlL44':>9}")
    for a in arms:
        d = [by[a][q] for q in qs]
        print(f"{a:>11}{acc[a]:>8.3f}{acc[a]-acc['base']:>+10.3f}"
              f"{np.mean([x['same_as_base'] for x in d]):>14.3f}"
              f"{np.mean([x['first_div'] for x in d]):>11.1f}"
              f"{np.mean([x['kl_shared'] for x in d]):>12.2e}"
              f"{np.mean([x['route_overlap_on_base_context']['36'] for x in d]):>9.3f}"
              f"{np.mean([x['route_overlap_on_base_context']['44'] for x in d]):>9.3f}")
    rng = np.random.default_rng(0)
    print("\nPaired bootstrap on accuracy difference (10k resamples):")
    for a, b in (("cpd", "base"), ("cpd", "shuffled"), ("cpd", "router_ce")):
        if a not in by or b not in by:
            continue
        d = np.array([float(by[a][q]["correct"]) - float(by[b][q]["correct"]) for q in qs])
        bs = np.array([d[rng.integers(0, n, n)].mean() for _ in range(10000)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        print(f"  {a} - {b}: {d.mean():+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]"
              f"   {'SIG' if (lo > 0 or hi < 0) else 'ns'}")


if __name__ == "__main__":
    {"ladder": ladder, "train": train, "freegen": freegen}[sys.argv[1]]()
