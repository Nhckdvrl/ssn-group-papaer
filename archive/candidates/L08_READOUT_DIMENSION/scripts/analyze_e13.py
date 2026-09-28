"""E13 — treatment-specific rescue from re-grounding an already-produced state.

    Delta_refresh = [Y_T(state) - Y_T(placebo)] - [Y_0(state) - Y_0(placebo)]

Both arms re-emit a number the model itself produced earlier in this same trajectory,
through an identical template at an identical position.  The only difference is whether
the re-grounded value is the one the pending computation consumes.

A rescue that also helps the full-precision model is a statement about reminders, not
about compression.  The claim needs the full-precision difference to be ~0.

All contrasts are computed on the items eligible in BOTH arms, so the arms share an
item set.
"""
from __future__ import annotations
import importlib.util, json, pathlib, collections
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("summ", ROOT / "scripts" / "summarize.py")
summ = importlib.util.module_from_spec(spec); spec.loader.exec_module(summ)
RNG = np.random.default_rng(9109); B = 10000


def per_item(path):
    s = summ.score(path)
    if s.get("correct") is None:
        return None
    ids = [json.loads(l)["id"] for l in list(open(path))[1:]]
    return dict(zip(ids, s["correct"]))


def paired(d1, d2, ids):
    return (np.array([d1[i] for i in ids], float),
            np.array([d2[i] for i in ids], float))


def ci_diff(a, b, paired_items=True):
    n = len(a)
    if paired_items:
        d = a - b
        bs = [d[RNG.integers(0, n, n)].mean() for _ in range(B)]
        return d.mean(), *np.percentile(bs, [2.5, 97.5])
    bs = [a[RNG.integers(0, n, n)].mean() - b[RNG.integers(0, len(b), len(b))].mean()
          for _ in range(B)]
    return a.mean() - b.mean(), *np.percentile(bs, [2.5, 97.5])


def main():
    runs = collections.defaultdict(dict)
    for p in sorted((ROOT / "results" / "e13").rglob("*.jsonl")):
        h = json.loads(open(p).readline())
        runs[(p.parent.name, h["cell"], h["mask"])][h["arm"]] = p

    cells = {}
    for key, arms in sorted(runs.items()):
        tag, cell, iv = key
        got = {a: per_item(p) for a, p in arms.items() if per_item(p) is not None}
        if not {"state", "placebo"} <= set(got):
            print(f"=== {iv}: incomplete ({sorted(got)}) ===")
            continue
        ids = sorted(set(got["state"]) & set(got["placebo"]))
        st, pl = paired(got["state"], got["placebo"], ids)
        d, lo, hi = ci_diff(st, pl)
        cells[iv] = (st, pl, ids)
        print(f"\n=== {iv} ===   n={len(ids)} eligible items")
        print(f"  state   {st.mean():.4f}")
        print(f"  placebo {pl.mean():.4f}")
        print(f"  simple rescue  state - placebo = {d:+.4f}  [{lo:+.4f},{hi:+.4f}]"
              f"   {'SIG' if lo > 0 else ''}")
        if "null" in got:
            nl = np.array([got["null"][i] for i in ids if i in got["null"]], float)
            print(f"  null-injection control {nl.mean():.4f} "
                  f"(must match the free-running source run)")

    base = cells.get("none")
    if base is None:
        print("\nfull-precision arm missing; Delta_refresh not computable yet")
        return
    print("\n" + "=" * 74)
    print("Delta_refresh = [Y_T(state)-Y_T(placebo)] - [Y_0(state)-Y_0(placebo)]")
    print("=" * 74)
    b_st, b_pl, b_ids = base
    b_d = b_st - b_pl
    print(f"{'intervention':<22}{'T diff':>18}{'FP diff':>18}{'Delta_refresh':>22}")
    for iv, (st, pl, ids) in cells.items():
        if iv == "none":
            continue
        common = sorted(set(ids) & set(b_ids))
        if len(common) < 30:
            print(f"{iv:<22}  too few shared items ({len(common)})"); continue
        ix = {i: k for k, i in enumerate(ids)}
        bx = {i: k for k, i in enumerate(b_ids)}
        t_d = np.array([st[ix[i]] - pl[ix[i]] for i in common])
        f_d = np.array([b_st[bx[i]] - b_pl[bx[i]] for i in common])
        dd = t_d - f_d
        bs = [dd[RNG.integers(0, len(dd), len(dd))].mean() for _ in range(B)]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        tl, th = np.percentile([t_d[RNG.integers(0, len(t_d), len(t_d))].mean()
                                for _ in range(B)], [2.5, 97.5])
        fl, fh = np.percentile([f_d[RNG.integers(0, len(f_d), len(f_d))].mean()
                                for _ in range(B)], [2.5, 97.5])
        flag = "PASS" if lo > 0 else ("null" if hi > 0 else "WRONG SIGN")
        print(f"{iv:<22}{t_d.mean():>+8.4f} [{tl:+.3f},{th:+.3f}]"
              f"{f_d.mean():>+8.4f} [{fl:+.3f},{fh:+.3f}]"
              f"{dd.mean():>+9.4f} [{lo:+.3f},{hi:+.3f}] {flag}")
    print("\nPASS requires Delta_refresh significantly > 0: the refresh must help the")
    print("compressed model specifically, not be a generally useful reminder.")


if __name__ == "__main__":
    main()
