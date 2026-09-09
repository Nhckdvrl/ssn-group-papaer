#!/usr/bin/env python3
"""
Fit a dual-beta prospect theory model to LLM/human choice data.
 
Model has 4 free parameters: sigma (risk), gamma (prob weighting),
beta_gain and beta_loss (domain-specific decisiveness).
Standard loss aversion lambda is dropped; the ratio beta_loss/beta_gain
serves as an identifiable proxy.
 
Usage: change INPUT_FILE below to point at the desired CSV, then run.
"""
 
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
 
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit as sigmoid
from tqdm import tqdm
import time
 
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
 
# --- Configuration ---
INPUT_FILE = "open_implicit.csv"  # change per run
LOG_FILE = f"log_{os.path.splitext(INPUT_FILE)[0]}.txt"
CKPT_PREFIX = os.path.splitext(INPUT_FILE)[0]
 
N_STARTS = 20
N_BOOT = 1000
N_REPS = 20  # number of repeated queries per condition in data collection
 
BOUNDS = [(0.01, 1000)] * 4  # sigma, gamma, beta_gain, beta_loss
 
 
def log(msg):
    ts = time.strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{ts} {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
 
 
# --- Checkpointing ---
 
def load_checkpoint(path):
    if os.path.exists(path):
        log(f"Resuming from checkpoint: {path}")
        return pd.read_csv(path)
    return pd.DataFrame()
 
 
def append_checkpoint(path, row_dict):
    df = pd.DataFrame([row_dict])
    header = not os.path.exists(path)
    df.to_csv(path, mode="a", header=header, index=False)
 
 
# --- PT components ---
 
def v_value(x, sigma):
    """Symmetric power value function (no lambda)."""
    x = np.nan_to_num(np.asarray(x, dtype=float), nan=0.0)
    return np.sign(x) * (np.abs(x) ** sigma)
 
 
def w_prob(p, gamma):
    """Kahneman-Tversky probability weighting."""
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1 - 1e-12)
    pg = p ** gamma
    qg = (1 - p) ** gamma
    return pg / (pg + qg) ** (1.0 / gamma)
 
 
def u_binary(x, y, p, sigma, gamma):
    """
    PT utility for binary prospect (x, p; y, 1-p).
    Same-sign case: RDU with extreme outcome weighted by w(p_extreme).
    Mixed-sign case: separable weighting.
    """
    vx = v_value(x, sigma)
    vy = v_value(y, sigma)
    wp = w_prob(p, gamma)
    wq = w_prob(1 - p, gamma)
 
    U = np.empty_like(x, dtype=float)
 
    same = ((x >= 0) & (y >= 0)) | ((x <= 0) & (y <= 0))
    mixed = ~same
 
    if np.any(same):
        # sort by absolute magnitude: extreme gets the weighted probability
        flip = np.abs(x[same]) < np.abs(y[same])
        v_ext = np.where(flip, vy[same], vx[same])
        v_mod = np.where(flip, vx[same], vy[same])
        w_ext = np.where(flip, wq[same], wp[same])
        U[same] = w_ext * v_ext + (1 - w_ext) * v_mod
 
    if np.any(mixed):
        U[mixed] = wp[mixed] * vx[mixed] + wq[mixed] * vy[mixed]
 
    return U
 
 
# --- Prediction and loss ---
 
def predict(params, data):
    """Predicted P(choose A) for each row."""
    sigma, gamma, b_gain, b_loss = params
 
    xa = data["x_a"].to_numpy(float)
    ya = data["y_a"].to_numpy(float)
    xb = data["x_b"].to_numpy(float)
    yb = data["y_b"].to_numpy(float)
    p_a = data["p_a"].to_numpy(float)
    p_b = data["p_b"].to_numpy(float)
 
    # normalize payoffs per row
    scale = np.maximum.reduce([np.abs(xa), np.abs(ya), np.abs(xb), np.abs(yb)])
    scale = np.maximum(scale, 1e-6)
 
    ua = u_binary(xa / scale, ya / scale, p_a, sigma, gamma)
    ub = u_binary(xb / scale, yb / scale, p_b, sigma, gamma)
 
    # all-gain prospects use beta_gain; anything with a loss uses beta_loss
    is_gain = (xa >= 0) & (ya >= 0) & (xb >= 0) & (yb >= 0)
    beta = np.where(is_gain, b_gain, b_loss)
 
    return sigmoid(beta * (ua - ub))
 
 
def mse_loss(params, data):
    p_obs = data["average_first_option_rate"].to_numpy(float)
    p_hat = predict(params, data)
    return float(np.mean((p_obs - p_hat) ** 2))
 
 
# --- Optimization ---
 
def multi_start(obj, starts, bounds, args=()):
    best = None
    for x0 in starts:
        try:
            res = minimize(obj, x0=x0, args=args, bounds=bounds, method="L-BFGS-B")
            if res.success and (best is None or res.fun < best.fun):
                best = res
        except Exception:
            pass
    return best
 
 
def make_starts():
    fixed = [
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1000.0, 1.0],
        [1.0, 1.0, 1.0, 1000.0],
        [1.0, 1.0, 1000.0, 1000.0],
    ]
    rand = [
        [np.random.uniform(0.01, 3), np.random.uniform(0.01, 3),
         np.random.uniform(0.01, 100), np.random.uniform(0.01, 100)]
        for _ in range(N_STARTS)
    ]
    return fixed + rand
 
 
# --- Bootstrap CIs ---
 
def bootstrap_ci(best_params, data):
    """Parametric bootstrap: resample from Binomial(N_REPS, p_hat), refit."""
    p_hat_orig = predict(best_params, data)
    estimates = []
    data_syn = data.copy()
 
    for _ in range(N_BOOT):
        k = np.random.binomial(n=N_REPS, p=p_hat_orig)
        data_syn["average_first_option_rate"] = k / N_REPS
        try:
            res = minimize(mse_loss, x0=best_params, args=(data_syn,),
                           bounds=BOUNDS, method="L-BFGS-B")
            estimates.append(res.x if res.success else best_params)
        except Exception:
            estimates.append(best_params)
 
    estimates = np.array(estimates)
    names = ["sigma", "gamma", "beta_gain", "beta_loss"]
    ci = {}
    for i, name in enumerate(names):
        ci[f"{name}_lb"] = np.percentile(estimates[:, i], 2.5)
        ci[f"{name}_ub"] = np.percentile(estimates[:, i], 97.5)
    return ci
 
 
# --- Per-group fitting ---
 
def fit_group(data):
    if data["average_first_option_rate"].isna().any():
        return None
 
    obs = data["average_first_option_rate"].to_numpy(float)
    res = multi_start(mse_loss, make_starts(), BOUNDS, args=(data,))
 
    if res is None:
        names = ["sigma", "gamma", "beta_gain", "beta_loss"]
        out = {n: np.nan for n in names}
        out.update({"loss_aversion_ratio": np.nan, "mse": np.nan,
                     "mae": np.nan, "corr": np.nan, "success": False,
                     "n_trials": len(data)})
        for n in names:
            out[f"{n}_lb"] = np.nan
            out[f"{n}_ub"] = np.nan
        return out
 
    sigma, gamma, b_gain, b_loss = map(float, res.x)
    p_hat = predict(res.x, data)
 
    corr = 0.0
    if np.std(p_hat) > 1e-9 and np.std(obs) > 1e-9:
        corr = float(np.corrcoef(obs, p_hat)[0, 1])
 
    out = {
        "sigma": sigma, "gamma": gamma,
        "beta_gain": b_gain, "beta_loss": b_loss,
        "loss_aversion_ratio": b_loss / b_gain if b_gain > 0 else np.nan,
        "mse": float(res.fun),
        "mae": float(np.mean(np.abs(obs - p_hat))),
        "corr": corr,
        "success": True,
        "n_trials": len(data),
    }
    out.update(bootstrap_ci(res.x, data))
    return out
 
 
# --- Runner with checkpointing ---
 
def run_grouped(grouped, label, ckpt_file):
    log(f"=== {label} ===")
    checkpoint = load_checkpoint(ckpt_file)
 
    done = set()
    if not checkpoint.empty:
        keys = grouped.grouper.names
        for _, row in checkpoint.iterrows():
            try:
                done.add(tuple(row[k] for k in keys))
            except Exception:
                pass
 
    results = []
    group_names = grouped.grouper.names
 
    for key, grp in tqdm(grouped, desc=label, total=len(grouped)):
        kt = key if isinstance(key, tuple) else (key,)
        if kt in done:
            continue
 
        stats = fit_group(grp)
        if stats is None:
            continue
 
        row = {}
        if isinstance(key, tuple):
            for name, val in zip(group_names, key):
                row[name] = val
        else:
            row[group_names[0]] = key
        row.update(stats)
 
        results.append(row)
        append_checkpoint(ckpt_file, row)
 
    log(f"=== Done: {label} ===")
    return pd.concat([checkpoint, pd.DataFrame(results)], ignore_index=True)
 
 
# --- Main ---
 
if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE)
    log(f"Loaded {INPUT_FILE}: {df.shape}")
    df = df.dropna(subset=["average_first_option_rate"]).reset_index(drop=True)
    log(f"After dropping NaNs: {df.shape}")
 
    # Run 1: by model
    run_grouped(
        df.groupby("Model", sort=False),
        "By Model",
        f"{CKPT_PREFIX}_by_model.csv",
    )
 
    # # Run 2: by model x sample size (relevant for implicit data)
    # if "Sample_Size" in df.columns:
    #     run_grouped(
    #         df.groupby(["Model", "Sample_Size"], sort=False),
    #         "By Model x Sample_Size",
    #         f"{CKPT_PREFIX}_by_model_sample.csv",
    #     )
 
    # # Run 3: by model x prompt style
    # if "Prompt_Style" in df.columns:
    #     run_grouped(
    #         df.groupby(["Model", "Prompt_Style"], sort=False),
    #         "By Model x Prompt_Style",
    #         f"{CKPT_PREFIX}_by_model_prompt.csv",
    #     )
 
    # # Run 4: full granularity
    # extra_cols = [c for c in ["Prompt_Style", "Sample_Size"] if c in df.columns]
    # if extra_cols:
    #     run_grouped(
    #         df.groupby(["Model"] + extra_cols, sort=False),
    #         "Full granularity",
    #         f"{CKPT_PREFIX}_full.csv",
    #     )
 
    log("All runs complete.")
