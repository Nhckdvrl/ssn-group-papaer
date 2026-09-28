"""L34 E01 analysis — frozen estimands from E01_PREREGISTRATION.md §5/§6."""
import json, os, sys, glob
import numpy as np
from bios import FAMILY_A, FAMILY_B, ATTRS

RES = os.path.join(os.path.dirname(__file__), "..", "results", "e01")
ARMS = ["PIT_A", "PIT_B", "PIT_BAL", "NO_PIT"]
NBOOT = 10000


def load_mats(tag, prefix="final"):
    """-> M[arm][seed][age][tgroup] = (names, {attr: vec}), plus rank/top1 vectors."""
    out = {}
    for f in sorted(glob.glob(os.path.join(RES, f"{prefix}_{tag}_*.json"))):
        base = os.path.basename(f)[len(prefix) + 1:-5]
        arm_seed = base[len(tag) + 1:]
        arm, seed = arm_seed.rsplit("_s", 1)
        recs = json.load(open(f))
        d = {}
        for r in recs:
            tg = "held_in" if r["tmpl"] == 0 else "held_out"
            d.setdefault((r["age"], tg), {}).setdefault(r["attr"], {})[r["name"]] = r
        out.setdefault(arm, {})[int(seed)] = d
    return out


def stack(d, age, tg, field="nll_tok"):
    sub = d[(age, tg)]
    names = sorted(sub[ATTRS[0]].keys())
    M = np.array([[sub[a][n].get(field, np.nan) for a in ATTRS] for n in names])
    return names, M


def fam_score(M):
    """-> per-person (-nll) means for family A and B."""
    ia = [ATTRS.index(a) for a in FAMILY_A]
    ib = [ATTRS.index(a) for a in FAMILY_B]
    return -M[:, ia].mean(1), -M[:, ib].mean(1)


def estimands(data, tag, tg="held_in", field="nll_tok", seed=0):
    """Paired person bootstrap; seeds averaged within arm."""
    rng = np.random.default_rng(seed)
    need = ["PIT_A", "PIT_B"]
    if not all(a in data for a in need):
        return None
    per = {}   # per[arm][age] = (A_vec, B_vec) averaged over seeds
    names_ref = {}
    for arm in data:
        for age in ("OLD", "NEW"):
            As, Bs = [], []
            for s in sorted(data[arm]):
                nm, M = stack(data[arm][s], age, tg, field)
                names_ref.setdefault(age, nm)
                assert nm == names_ref[age]
                a, b = fam_score(M)
                As.append(a); Bs.append(b)
            per.setdefault(arm, {})[age] = (np.mean(As, 0), np.mean(Bs, 0))

    def compute(idx):
        r = {}
        for age in ("OLD", "NEW"):
            i = idx[age]
            for arm in per:
                A, B = per[arm][age]
                r[(arm, age, "A")] = A[i].mean(); r[(arm, age, "B")] = B[i].mean()
            r[("PREF", "PIT_A", age)] = r[("PIT_A", age, "A")] - r[("PIT_A", age, "B")]
            r[("PREF", "PIT_B", age)] = r[("PIT_B", age, "A")] - r[("PIT_B", age, "B")]
            r[("CROSS", age)] = r[("PREF", "PIT_A", age)] - r[("PREF", "PIT_B", age)]
        r["PROSPECTIVE"] = r[("CROSS", "NEW")] - r[("CROSS", "OLD")]
        for arm in per:
            for age in ("OLD", "NEW"):
                r[("OVERALL", arm, age)] = 0.5 * (r[(arm, age, "A")] + r[(arm, age, "B")])
        return r

    full_idx = {age: np.arange(len(names_ref[age])) for age in ("OLD", "NEW")}
    point = compute(full_idx)
    keys = [k for k in point]
    boot = {k: np.empty(NBOOT) for k in keys}
    n = {age: len(names_ref[age]) for age in ("OLD", "NEW")}
    for t in range(NBOOT):
        idx = {age: rng.integers(0, n[age], n[age]) for age in ("OLD", "NEW")}
        b = compute(idx)
        for k in keys:
            boot[k][t] = b[k]
    ci = {k: (float(np.percentile(boot[k], 2.5)), float(np.percentile(boot[k], 97.5))) for k in keys}
    return point, ci, per, names_ref


def fmt(k):
    return k if isinstance(k, str) else "/".join(map(str, k))


def report(tag, field="nll_tok", prefix="final"):
    data = load_mats(tag, prefix)
    print(f"### {prefix} tag={tag} field={field}")
    print("arms/seeds:", {a: sorted(data[a]) for a in data})
    for tg in ("held_in", "held_out"):
        try:
            r = estimands(data, tag, tg, field)
        except (KeyError, AssertionError) as e:
            print(f"  [{tg}] unavailable: {e}"); continue
        if r is None:
            print(f"  [{tg}] PIT_A/PIT_B missing"); continue
        point, ci, per, _ = r
        print(f"\n-- {tg} --")
        for k in [("PREF", "PIT_A", "OLD"), ("PREF", "PIT_B", "OLD"), ("CROSS", "OLD"),
                  ("PREF", "PIT_A", "NEW"), ("PREF", "PIT_B", "NEW"), ("CROSS", "NEW"), "PROSPECTIVE"]:
            lo, hi = ci[k]
            star = "  *" if (lo > 0 or hi < 0) else ""
            print(f"  {fmt(k):22s} {point[k]:+.4f}  [{lo:+.4f}, {hi:+.4f}]{star}")
        print("  -- mother check (mean -nll/token, higher=better) --")
        for arm in ARMS:
            if arm not in per: continue
            for age in ("OLD", "NEW"):
                lo, hi = ci[("OVERALL", arm, age)]
                print(f"  OVERALL/{arm:8s}/{age:3s} {point[('OVERALL', arm, age)]:+.4f} [{lo:+.4f}, {hi:+.4f}]")


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "q3b"
    report(tag, "nll_tok", "final")
    print("\n" + "=" * 70 + "\nG1: post-phase-1 OLD-only access specialisation\n")
    d = load_mats(tag, "post_p1")
    if d and all(a in d for a in ("PIT_A", "PIT_B")):
        for tg in ("held_in", "held_out"):
            rng = np.random.default_rng(0)
            pa = {}
            for arm in ("PIT_A", "PIT_B"):
                As, Bs = [], []
                for s in sorted(d[arm]):
                    nm, M = stack(d[arm][s], "OLD", tg)
                    a, b = fam_score(M); As.append(a); Bs.append(b)
                pa[arm] = (np.mean(As, 0), np.mean(Bs, 0))
            n = len(pa["PIT_A"][0])
            f = lambda i: ((pa["PIT_A"][0][i].mean() - pa["PIT_A"][1][i].mean())
                           - (pa["PIT_B"][0][i].mean() - pa["PIT_B"][1][i].mean()))
            pt = f(np.arange(n))
            bs = np.array([f(rng.integers(0, n, n)) for _ in range(NBOOT)])
            print(f"  [{tg}] CROSSOVER_postP1(OLD) = {pt:+.4f} "
                  f"[{np.percentile(bs,2.5):+.4f}, {np.percentile(bs,97.5):+.4f}]")
            for arm in ("PIT_A", "PIT_B"):
                print(f"      PREF({arm}) = {pa[arm][0].mean()-pa[arm][1].mean():+.4f}")
    else:
        print("  no post_p1 files yet")
