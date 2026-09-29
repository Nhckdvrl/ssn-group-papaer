"""Per-press registration for human key-press replays (E29: vpt_press_specs.py + mwm_sysid / mwm_overlap).

For each rollout <tag>_p<id>_s<seed>_<yawlist spec>.npz and its paired <tag>_..._none.npz, the realised yaw per
latent is the phase-correlation shift (per_latent). Presses are maximal runs of commanded latents. Registration of
a press = realised shift over [onset, onset+dur+2) / (g * commanded degrees), with g the model's own gain
(median px/deg over presses whose onset is not on a block-first latent and that last >= 2 latents).
Block-first onset: the press's first commanded latent k+1 is the first latent of a 4-latent block ((k+1) % 4 == 0).

Besides the original fields, the output has
  by_dur:   seam vs other registration / loss rate within press-duration strata (1, 2-3, >=4 latents), with a
            bootstrap 95% CI of the loss-rate difference (seam - other). With legacy (non-balanced) replay specs
            seam position is confounded with duration, so compare within strata; with --balanced specs every press
            appears at every in-block position and the pooled comparison is unconfounded too.
  ref_gain: with --ref_tag T, registration and heading error recomputed with T's gain for every tag, so that a
            condition that changes the overall gain (e.g. an overlap rollout that over-rotates) is not hidden by
            self-calibration.
Usage: python press_replay.py <raw_dir> [out_json] [--ref_tag wpdist] [--lost_thr 0.3]
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from mwm_bandwidth import per_latent  # noqa: E402
from sysid import shifts  # noqa: E402

STRATA = (("1", lambda d: d == 1), ("2-3", lambda d: 2 <= d <= 3), (">=4", lambda d: d >= 4))


def runs(y):
    e = np.diff(np.r_[0, (y != 0).astype(int), 0])
    return list(zip(np.flatnonzero(e == 1), np.flatnonzero(e == -1) - np.flatnonzero(e == 1)))


def mean_n(v):
    return [round(float(np.mean(v)), 3) if len(v) else None, len(v)]


def boot_diff(a, b, n_boot=2000, seed=0):
    """95% bootstrap CI of mean(a) - mean(b) (independent resampling of presses)."""
    if len(a) == 0 or len(b) == 0:
        return None
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = [rng.choice(a, len(a)).mean() - rng.choice(b, len(b)).mean() for _ in range(n_boot)]
    return [round(float(np.mean(a) - np.mean(b)), 3), round(float(np.percentile(d, 2.5)), 3),
            round(float(np.percentile(d, 97.5)), 3)]


def gain_of(R):
    return float(np.median([r["got"] / r["cmd"] for r in R if not r["seam"] and r["dur"] >= 2]))


def summarize(R, H, g, thr):
    reg = lambda sel: [r["got"] / (g * r["cmd"]) for r in R if sel(r)]  # noqa: E731
    seam, other = reg(lambda r: r["seam"]), reg(lambda r: not r["seam"])
    seam1, other1 = reg(lambda r: r["seam"] and r["dur"] == 1), reg(lambda r: not r["seam"] and r["dur"] == 1)
    herr = [abs(h / g - c) for h, c in H]
    out = dict(gain_px_per_deg=round(g, 3),
               reg_seam=mean_n(seam), reg_other=mean_n(other),
               lost_seam=round(float(np.mean(np.array(seam) < thr)), 3) if seam else None,
               lost_other=round(float(np.mean(np.array(other) < thr)), 3) if other else None,
               reg_seam_1lat=mean_n(seam1), reg_other_1lat=mean_n(other1),
               heading_err_deg=[round(float(np.mean(herr)), 2), len(herr)])
    by_dur = {}
    for name, sel in STRATA:
        s = reg(lambda r, sel=sel: r["seam"] and sel(r["dur"]))
        o = reg(lambda r, sel=sel: not r["seam"] and sel(r["dur"]))
        ls, lo = [float(x < thr) for x in s], [float(x < thr) for x in o]
        by_dur[name] = dict(reg_seam=mean_n(s), reg_other=mean_n(o), lost_seam=mean_n(ls), lost_other=mean_n(lo),
                            lost_diff_ci95=boot_diff(ls, lo))
    out["by_dur"] = by_dur
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--ref_tag", default=None, help="tag whose gain calibrates every tag (reported under ref_gain)")
    ap.add_argument("--lost_thr", type=float, default=0.3)
    a = ap.parse_args()
    refs, rows = {}, defaultdict(list)
    for f in sorted(glob.glob(os.path.join(a.raw, "*.npz"))):
        m = re.match(r"(\w+?)_p(\d+)_s(\d+)_(.*)\.npz", os.path.basename(f))
        tag, spec = m.group(1), m.group(4)
        if spec == "none":
            continue
        key = f"{tag}_p{m.group(2)}_s{m.group(3)}"
        if key not in refs:
            refs[key] = shifts(np.load(os.path.join(a.raw, key + "_none.npz"))["frames"])
        z = np.load(f)
        y = z["yaw_cmd"]
        rl = per_latent(-(shifts(z["frames"]) - refs[key]), len(y) + 1)[1:]  # rl[k] = latent k+1
        for on, dur in runs(y):
            cmd = float(y[on:on + dur].sum())
            got = float(rl[on:on + dur + 2].sum())
            rows[tag].append(dict(seam=(on + 1) % 4 == 0, dur=int(dur), cmd=cmd, got=got))
        rows[tag + "@heading"].append((float(rl.sum()), float(y.sum())))
    tags = sorted(t for t in rows if "@" not in t)
    g_ref = gain_of(rows[a.ref_tag]) if a.ref_tag else None
    res = {}
    for tag in tags:
        R, H = rows[tag], rows[tag + "@heading"]
        res[tag] = summarize(R, H, gain_of(R), a.lost_thr)
        if g_ref is not None:
            res[tag]["ref_gain"] = dict(ref_tag=a.ref_tag, **summarize(R, H, g_ref, a.lost_thr))
        print(tag, {k: v for k, v in res[tag].items() if k not in ("by_dur", "ref_gain")})
        for name, v in res[tag]["by_dur"].items():
            print(f"   dur {name:>3}: lost seam {v['lost_seam']} other {v['lost_other']} diff/CI {v['lost_diff_ci95']}")
        if g_ref is not None:
            rg = res[tag]["ref_gain"]
            print(f"   with {a.ref_tag} gain {rg['gain_px_per_deg']}: heading err {rg['heading_err_deg']}, "
                  f"reg seam {rg['reg_seam']} other {rg['reg_other']}")
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
