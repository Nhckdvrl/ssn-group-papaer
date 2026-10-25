"""Independent CPU reanalysis of C06; no model forward or E122 statistic imports."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from scipy.stats import rankdata


def residual_rank_correlation(x, y, controls):
    data = np.column_stack((x, y, controls)).astype(np.float64)
    data = data[np.isfinite(data).all(axis=1)]
    if len(data) < controls.shape[1] + 6:
        return float("nan")
    ranked = np.column_stack([rankdata(data[:, i], method="average") for i in range(data.shape[1])])
    design = np.column_stack((np.ones(len(data)), ranked[:, 2:]))
    residuals = ranked[:, :2] - design @ np.linalg.lstsq(design, ranked[:, :2], rcond=None)[0]
    return float(np.corrcoef(residuals.T)[0, 1])


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    wb = Path(__file__).resolve().parents[1]
    p.add_argument("--store", type=Path, default=Path("/tmp/xiang-moe-20261025"))
    p.add_argument("--matrices", type=Path, default=wb / "results/e122/layer9_matrices.npz")
    p.add_argument("--items", type=Path, default=wb / "results/e121/items_pos.jsonl")
    p.add_argument("--output", type=Path, default=wb / "results/e122/c06_independent_cpu_audit.json")
    p.add_argument("--bootstrap", type=int, default=999)
    p.add_argument("--seed", type=int, default=6006)
    a = p.parse_args()
    torch.set_num_threads(4)
    matrices = np.load(a.matrices, allow_pickle=False)
    pair = np.triu_indices(64, 1)
    result = {"scope": "Independent C06 numerical reanalysis, not full L3 audit",
              "device": "cpu", "seed": a.seed, "bootstrap_replicates": a.bootstrap,
              "items_sha256": file_digest(a.items), "matrices_sha256": file_digest(a.matrices),
              "script_sha256": file_digest(Path(__file__)), "cross_half": [], "route_distance_dnll": {}}
    for r_half, f_half in ((0, 1), (1, 0)):
        load = np.log(np.maximum(matrices[f"load{r_half}"], 1e-8))
        norm = np.log(np.maximum(matrices[f"norm{f_half}"], 1e-8))
        i, j = pair
        cov = np.column_stack((load[i] + load[j], np.abs(load[i] - load[j]),
                               norm[i] + norm[j], np.abs(norm[i] - norm[j])))
        rho = residual_rank_correlation(matrices[f"R{r_half}"][pair], matrices[f"F{f_half}"][pair], cov)
        result["cross_half"].append({"R_half": r_half, "F_half": f_half, "partial_rho": rho})
    items = [json.loads(line) for line in a.items.read_text().splitlines() if line.strip()]
    cap = torch.load(a.store / "capture.pt", mmap=True, map_location="cpu", weights_only=False)
    raw = torch.load(a.store / "r3_raw.pt", map_location="cpu", weights_only=False)
    assert len(items) == 1904 and cap["H_last"].shape[1] >= len(items)
    held = np.array([it["split"] == "held" for it in items])
    words = np.array([it["word"] for it in items])[held]
    gate = cap["gates"][9].float()
    # Reconstruct route phi from original calibration capture, not saved Rall.
    cal_logits = cap["H_cal"][9].float() @ gate.T
    selected = cal_logits.topk(8, dim=1).indices
    incidence = np.zeros((len(selected), 64), dtype=np.float64)
    incidence[np.arange(len(selected))[:, None], selected.numpy()] = 1
    phi = np.corrcoef(incidence, rowvar=False)
    result["Rall_max_abs_error_vs_saved"] = float(np.nanmax(np.abs(phi - matrices["Rall"])))
    del cal_logits, selected, incidence
    z = cap["H_last"][9, :len(items)].float() @ gate.T
    probability = torch.softmax(z, dim=1).numpy()
    z = z.numpy()
    nll = cap["nll"][:len(items)].numpy()
    groups = [np.flatnonzero(words == word) for word in np.unique(words)]
    rng = np.random.default_rng(a.seed)
    # Fixed draws shared across substitution modes; clusters are word forms.
    resamples = [np.concatenate([groups[k] for k in row])
                 for row in rng.integers(0, len(groups), size=(a.bootstrap, len(groups)))]
    for mode in ("swap9", "swaprand"):
        data = raw[f"L9_{mode}_s0"]
        old, new = data["old"].numpy(), data["new"].numpy()
        rows = np.arange(len(items))
        controls = np.column_stack((probability[rows, old], z[rows, old] - z[rows, new], nll))[held]
        predictor = (1 - phi[old, new])[held]
        outcome = data["dnll"].numpy()[held]
        estimates = np.array([residual_rank_correlation(predictor[idx], outcome[idx], controls[idx])
                              for idx in resamples])
        estimates = estimates[np.isfinite(estimates)]
        result["route_distance_dnll"][mode] = {
            "partial_rho": residual_rank_correlation(predictor, outcome, controls),
            "ci95_word_bootstrap": np.quantile(estimates, [.025, .975]).tolist(),
            "n_items": int(held.sum()), "n_words": len(groups), "valid_bootstrap": len(estimates),
            "saved_Rall_partial_rho_sensitivity": residual_rank_correlation(
                (1 - matrices["Rall"][old, new])[held], outcome, controls)}
    result["inference_limit"] = "Reuses old fp16/bf16 E121 captures and intervention outcomes; no new forward, causal identification or cross-seed evidence. Bootstrap random seed differs from E122."
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
