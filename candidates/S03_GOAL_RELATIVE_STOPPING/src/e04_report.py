"""S03 / E04 — read the supervision decomposition.

Every condition starts from the SAME checkpoint, so the baseline is that
checkpoint's own measurement (`step0`), and every contrast is paired per item.
Mid-run points come from the same run as the endpoint, so the step column is a
real trajectory rather than separate schedules.
"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e01_rawlogit import rows_of, mean, boot_ci, sign_test

ROOT = "results/e04"
ORDER = ["full_correct", "terminal_correct", "content_correct",
         "full_shuffled", "terminal_shuffled", "content_shuffled",
         "full_generic"]
LABEL = {
    "full_correct": "full / correct      (ordinary SFT)",
    "terminal_correct": "terminal / correct  (endpoint only)",
    "content_correct": "content / correct   (never told to stop)",
    "full_shuffled": "full / shuffled     (goal decoupled)",
    "terminal_shuffled": "terminal / shuffled (endpoint, wrong goal)",
    "content_shuffled": "content / shuffled",
    "full_generic": "full / generic      (one constant goal)",
}


def runs(seed):
    out = []
    for name in ORDER:
        d = f"{ROOT}/{name}_s{seed}"
        if os.path.exists(f"{d}/e01.jsonl"):
            out.append((name, d))
    return out


def final_metrics(d):
    h = [json.loads(l) for l in open(f"{d}/history.jsonl")] \
        if os.path.exists(f"{d}/history.jsonl") else []
    return h[-1] if h else {}


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    rs = runs(seed)
    if not rs:
        print("no completed E04 runs"); return
    base = rows_of([f"{rs[0][1]}/step0/e01.jsonl"])

    print(f"\nE04 — supervision decomposition, seed {seed}")
    print("init = Olmo-3-7B-Think-SFT (final), data = Dolci-Instruct-SFT")
    print("matched: pool, order, steps, schedule, optimizer, batch, seed\n")
    b = dict(d_goal=mean([r["d_goal"] for r in base.values()]),
             dz_stop=mean([r["dz_stop"] for r in base.values()]),
             dz_cont=mean([r["dz_cont"] for r in base.values()]))
    print(f"  baseline (step 0): d_goal {b['d_goal']:.2f}   "
          f"dz_stop {b['dz_stop']:.2f}   dz_cont {b['dz_cont']:.2f}\n")

    hdr = (f"  {'condition':<38}{'d_goal':>8}{'D d_goal':>10}{'95% CI':>18}"
           f"{'sign':>8}{'D dz_stop':>11}{'D dz_cont':>11}{'bnd_auc':>9}{'val_ce':>8}")
    print(hdr); print("  " + "-" * (len(hdr) - 2))
    for name, d in rs:
        A = rows_of([f"{d}/e01.jsonl"])
        ks = sorted(set(A) & set(base))
        v = {m: [A[k][m] - base[k][m] for k in ks]
             for m in ("d_goal", "dz_stop", "dz_cont")}
        lo, hi = boot_ci(v["d_goal"]); _, p, n = sign_test(v["d_goal"])
        fm = final_metrics(d)
        print(f"  {LABEL.get(name, name):<38}"
              f"{mean([A[k]['d_goal'] for k in ks]):>8.2f}"
              f"{mean(v['d_goal']):>10.2f}{f'[{lo:+.2f},{hi:+.2f}]':>18}"
              f"{f'{p}/{n}':>8}{mean(v['dz_stop']):>11.2f}"
              f"{mean(v['dz_cont']):>11.2f}"
              f"{fm.get('boundary_auc', float('nan')):>9.4f}"
              f"{fm.get('val_loss', float('nan')):>8.3f}")

    # --- one-schedule trajectories -----------------------------------------
    print(f"\n  d_goal along ONE schedule (mid-run evals from the same run)\n")
    steps = sorted({int(re.search(r"step(\d+)$", p).group(1))
                    for name, d in rs
                    for p in glob.glob(f"{d}/step*")
                    if re.search(r"step(\d+)$", p)})
    print(f"  {'condition':<38}" + "".join(f"{s:>8}" for s in steps) + f"{'final':>8}")
    print("  " + "-" * (38 + 8 * (len(steps) + 1)))
    for name, d in rs:
        cells = []
        for s in steps:
            p = f"{d}/step{s}/e01.jsonl"
            cells.append(f"{mean([r['d_goal'] for r in rows_of([p]).values()]):>8.2f}"
                         if os.path.exists(p) else f"{'-':>8}")
        fin = mean([r["d_goal"] for r in rows_of([f'{d}/e01.jsonl']).values()])
        print(f"  {LABEL.get(name, name):<38}" + "".join(cells) + f"{fin:>8.2f}")

    # --- direct condition contrasts ----------------------------------------
    have = {n for n, _ in rs}
    pairs = [("terminal_correct", "full_correct"),
             ("content_correct", "full_correct"),
             ("full_shuffled", "full_correct"),
             ("terminal_shuffled", "terminal_correct"),
             ("full_shuffled", "content_correct")]
    pairs = [(a, b_) for a, b_ in pairs if a in have and b_ in have]
    if pairs:
        print(f"\n  paired contrasts BETWEEN conditions (d_goal)\n")
        hdr = f"  {'contrast':<46}{'diff':>9}{'95% CI':>18}{'sign':>9}"
        print(hdr); print("  " + "-" * (len(hdr) - 2))
        for a, c in pairs:
            A = rows_of([f"{ROOT}/{a}_s{seed}/e01.jsonl"])
            C = rows_of([f"{ROOT}/{c}_s{seed}/e01.jsonl"])
            ks = sorted(set(A) & set(C))
            v = [A[k]["d_goal"] - C[k]["d_goal"] for k in ks]
            lo, hi = boot_ci(v); _, p, n = sign_test(v)
            print(f"  {a + ' - ' + c:<46}{mean(v):>9.2f}"
                  f"{f'[{lo:+.2f},{hi:+.2f}]':>18}{f'{p}/{n}':>9}")


if __name__ == "__main__":
    main()
