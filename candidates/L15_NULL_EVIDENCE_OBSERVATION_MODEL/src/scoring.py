"""L15 parsing and metrics.

Parsing rules are fixed before looking at any model output:
  - read the LAST line matching ANSWER: ...
  - accept a decimal in [0,1]; accept "x%" as x/100; accept "yes"/"no" for P3_DECIDE;
  - anything else is INVALID and is reported as coverage loss, never silently dropped.
"""
from __future__ import annotations

import math
import re
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

ANSWER_RE = re.compile(r"ANSWER\s*[:：]\s*([^\n]*)", re.IGNORECASE)
NUM_RE = re.compile(r"[-+]?\d*\.?\d+")
FRAC_RE = re.compile(r"(\d*\.?\d+)\s*/\s*(\d*\.?\d+)")

KNI_OBS_TOL = 0.05      # Err_obs <= .05   (DATA_AND_GOLD.md section 5)
KNI_POST_TOL = 0.10     # Err_post >= .10


def parse_numeric(raw: str) -> Optional[float]:
    m = ANSWER_RE.findall(raw or "")
    if not m:
        return None
    tail = m[-1].strip()
    pct = "%" in tail
    frac = FRAC_RE.search(tail)
    if frac:
        num, den = float(frac.group(1)), float(frac.group(2))
        if den == 0:
            return None
        v = num / den
    else:
        nums = NUM_RE.findall(tail.replace("%", " "))
        if len(nums) != 1:
            # no number, or an ambiguous multi-number tail: INVALID, not a guess
            return None
        try:
            v = float(nums[0])
        except ValueError:
            return None
    if pct:
        v = v / 100.0
    if not (0.0 <= v <= 1.0):
        return None
    return v


def parse_yesno(raw: str) -> Optional[str]:
    m = ANSWER_RE.findall(raw or "")
    if not m:
        return None
    tail = m[-1].strip().lower()
    if tail.startswith("yes"):
        return "yes"
    if tail.startswith("no"):
        return "no"
    return None


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 3:
        return float("nan")
    rx, ry = _rank(x), _rank(y)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def _rank(a: np.ndarray) -> np.ndarray:
    order = a.argsort()
    ranks = np.empty(len(a), dtype=float)
    ranks[order] = np.arange(len(a), dtype=float)
    # average ties
    for v in np.unique(a):
        mask = a == v
        if mask.sum() > 1:
            ranks[mask] = ranks[mask].mean()
    return ranks


def monotonicity_violations(pred: Sequence[float]) -> Tuple[int, int]:
    """Adjacent pairs that fail the required strictly-decreasing direction."""
    bad = 0
    tot = 0
    for a, b in zip(pred, pred[1:]):
        tot += 1
        if b > a + 1e-9:
            bad += 1
    return bad, tot


def bootstrap_ci(values: Sequence[float], n: int = 10000, seed: int = 0,
                 stat=np.mean) -> Tuple[float, float]:
    v = np.asarray([x for x in values if not (isinstance(x, float) and math.isnan(x))],
                   dtype=float)
    if len(v) == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    draws = stat(v[rng.integers(0, len(v), size=(n, len(v)))], axis=1)
    return (float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5)))


def cluster_bootstrap_ci(values: Sequence[float], clusters: Sequence[str],
                         n: int = 10000, seed: int = 0) -> Tuple[float, float]:
    """Resample whole scenarios: the independent unit is the scenario, not the cell."""
    vals = np.asarray(values, dtype=float)
    keys = np.asarray(clusters)
    uniq = np.unique(keys)
    groups = [vals[keys == k] for k in uniq]
    groups = [g[~np.isnan(g)] for g in groups]
    groups = [g for g in groups if len(g)]
    if not groups:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    draws = np.empty(n)
    for i in range(n):
        pick = rng.integers(0, len(groups), size=len(groups))
        draws[i] = np.concatenate([groups[j] for j in pick]).mean()
    return (float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5)))
