"""E13 offline promotion rules. Hidden scores are accessed only by query()."""
from dataclasses import dataclass
import numpy as np


@dataclass
class Calibration:
    lower: np.ndarray
    median: np.ndarray
    upper: np.ndarray

    @classmethod
    def fit(cls, cheap_banks, refined_banks, bins=5, alpha=0.05):
        residuals = [[] for _ in range(bins)]
        for cheap, refined in zip(cheap_banks, refined_banks):
            order = np.argsort(cheap, kind="stable")
            for j, idx in enumerate(order):
                residuals[min(bins - 1, j * bins // len(order))].append(refined[idx] - cheap[idx])
        qs = np.asarray([np.quantile(r, [alpha, 0.5, 1 - alpha]) for r in residuals])
        return cls(qs[:, 0], qs[:, 1], qs[:, 2])

    def intervals(self, cheap):
        rank = np.argsort(np.argsort(cheap, kind="stable"), kind="stable")
        b = np.minimum(len(self.lower) - 1, rank * len(self.lower) // len(cheap))
        return cheap + self.lower[b], cheap + self.median[b], cheap + self.upper[b]


def promote(cheap, query, *, k, mode, budget=None, calibration=None, seed=0, batch=16):
    """query receives only purchased candidate IDs; all other outcomes stay hidden.

    Fixed-budget rules use calibrated imputation for unqueried scores. TOP-M-SCREEN
    is the usual cascade which selects exclusively from the refined shortlist.
    LOWER-BOUND applies only when the scoring definition guarantees refined >= cheap.
    """
    cheap = np.asarray(cheap, dtype=np.float64)
    n = len(cheap)
    order = np.argsort(cheap, kind="stable")
    queried = np.zeros(n, dtype=bool)
    lo, estimate, hi = calibration.intervals(cheap) if calibration else (cheap.copy(), cheap.copy(), cheap.copy())
    values = np.full(n, np.nan)
    budget = n if budget is None else min(n, max(k, int(budget)))

    def buy(indices):
        indices = np.asarray(indices, dtype=int)
        indices = indices[~queried[indices]]
        if len(indices):
            observed = np.asarray(query(indices), dtype=np.float64)
            if observed.shape != indices.shape or not np.isfinite(observed).all():
                raise ValueError("Invalid score-query result")
            queried[indices] = True
            values[indices] = observed
            estimate[indices] = observed

    if mode == "CHEAP-ALL":
        estimate = cheap.copy()
    elif mode == "FULL-REFINE":
        buy(order)
    elif mode in ("TOP-M", "TOP-M-SCREEN", "TOP-M-MIXED"):
        buy(order[:budget])
        if mode == "TOP-M-SCREEN":
            estimate[~queried] = np.inf
        elif mode == "TOP-M-MIXED":
            estimate[~queried] = cheap[~queried]
    elif mode == "RANDOM-M":
        buy(np.random.default_rng(seed).choice(n, budget, replace=False))
    elif mode == "ELITE-BAND":
        cutoff = cheap[order[k - 1]]
        buy(np.argsort(np.abs(cheap - cutoff), kind="stable")[:budget])
    elif mode == "INTERVAL":
        if calibration is None:
            raise ValueError("INTERVAL requires independent calibration")
        buy(order[:k])
        while queried.sum() < budget:
            threshold = np.sort(values[queried])[k - 1]
            possible = np.flatnonzero((~queried) & (lo <= threshold))
            if not len(possible):
                break
            possible = possible[np.argsort(lo[possible], kind="stable")]
            buy(possible[:min(batch, budget - int(queried.sum()))])
    elif mode == "LOWER-BOUND":
        buy(order[:k])
        while True:
            if np.any(values[queried] < cheap[queried] - 1e-7):
                raise ValueError("LOWER-BOUND violated; cannot certify elite")
            threshold = np.sort(values[queried])[k - 1]
            possible = np.flatnonzero((~queried) & (cheap <= threshold))
            if not len(possible):
                break
            possible = possible[np.argsort(cheap[possible], kind="stable")]
            buy(possible[:batch])
        estimate[~queried] = np.inf
    else:
        raise ValueError(mode)
    elite = np.argsort(estimate, kind="stable")[:k]
    return {"elite": elite, "selected": int(np.argmin(estimate)),
            "queried": np.flatnonzero(queried), "estimated_cost": estimate,
            "interval_lower": lo, "interval_upper": hi}


def metrics(cheap, refined, actions, result, k):
    ref_elite = np.argsort(refined, kind="stable")[:k]
    elite = result["elite"]
    selected = result["selected"]
    ref_actions = actions[ref_elite]
    chosen_actions = actions[elite]
    mean_delta = np.linalg.norm(chosen_actions.mean(0) - ref_actions.mean(0))
    return {
        "elite_recall": float(len(set(elite) & set(ref_elite)) / k),
        "refined_fraction": float(len(result["queried"]) / len(cheap)),
        "selected_candidate_agreement": float(selected == int(np.argmin(refined))),
        "full_score_candidate_regret": float(refined[selected] - np.min(refined)),
        "full_score_elite_regret": float(np.mean(refined[elite]) - np.mean(refined[ref_elite])),
        "cem_mean_l2": float(mean_delta),
        "cem_action_agreement": float(mean_delta <= 1e-6),
        "cem_std_l2": float(np.linalg.norm(chosen_actions.std(0, ddof=1) - ref_actions.std(0, ddof=1))),
    }
