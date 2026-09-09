#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


# ============================================================
# Logging
# ============================================================

LOG_FILE = "run_log_implicit.txt"

def log(msg):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ============================================================
# Checkpointing utilities
# ============================================================

def load_checkpoint(path):
    if os.path.exists(path):
        log(f"Resuming from checkpoint: {path}")
        return pd.read_csv(path)
    return pd.DataFrame()

def append_checkpoint(path, row):
    df = pd.DataFrame([row])
    header = not os.path.exists(path)
    df.to_csv(path, mode="a", header=header, index=False)


# ============================================================
# Load dataset
# ============================================================

# df_gain = pd.read_csv("before_and_after_all.csv")
# df_loss = pd.read_csv("before_and_after_all_loss.csv")

# df_combined = pd.concat([df_gain, df_loss], ignore_index=True)
df_combined = pd.read_csv("open_implicit.csv")
log(f"Loaded dataset. Combined size = {df_combined.shape}")
df_combined = df_combined.dropna(
    subset=["average_first_option_rate"]
).reset_index(drop=True)
log(f"After dropping NaNs: size = {df_combined.shape}")


# ============================================================
# Utility functions for PT (vectorizable)
# ============================================================

def predict_pt(params, data, fit_lambda=True, fit_beta=True):
    """Helper to get p_hat for bootstrapping."""
    if fit_lambda and fit_beta:
        sigma, gamma, lam, beta = params
    elif fit_lambda:
        sigma, gamma, lam = params
        beta = 1.0
    else:
        sigma, gamma = params
        lam, beta = 1.0, 1.0

    xa = data["x_a"].to_numpy(dtype=float)
    ya = data["y_a"].to_numpy(dtype=float)
    xb = data["x_b"].to_numpy(dtype=float)
    yb = data["y_b"].to_numpy(dtype=float)
    p_a = data["p_a"].to_numpy(dtype=float)
    p_b = data["p_b"].to_numpy(dtype=float)

    den = np.maximum.reduce([np.abs(xa), np.abs(ya), np.abs(xb), np.abs(yb)])
    den = np.maximum(den, 1e-6)

    ua = u_binary(xa / den, ya / den, p_a, sigma, lam, gamma)
    ub = u_binary(xb / den, yb / den, p_b, sigma, lam, gamma)

    return sigmoid(beta * (ua - ub))

def v_value(x, sigma, lam):
    """
    x: np.ndarray or scalar
    sigma, lam: scalars
    """
    x = np.asarray(x, dtype=float)
    x = np.nan_to_num(x, nan=0.0)
    eps = 1e-12
    x = np.clip(x, -1e6, 1e6)
    pos = np.maximum(x, 0.0)
    neg = np.maximum(-x, 0.0) + eps
    pos_part = np.power(pos, sigma)
    neg_part = -lam * np.power(neg, sigma)
    return np.where(x >= 0, pos_part, neg_part)

def w_prob(p, gamma):
    """
    p: np.ndarray or scalar in [0,1]
    gamma: scalar
    """
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1-1e-12)
    pg = np.power(p, gamma)
    qg = np.power(1 - p, gamma)
    den = np.power(pg + qg, 1.0/gamma)
    return pg / den

def u_binary(x, y, p, sigma, lam, gamma):
    """
    Vectorized binary PT utility for lotteries (x,p; y,1-p).

    x,y,p: np.ndarray of same shape
    sigma, lam, gamma: scalars
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)

    vx = v_value(x, sigma, lam)
    vy = v_value(y, sigma, lam)
    wp = w_prob(p, gamma)
    wq = w_prob(1 - p, gamma)

    U = np.empty_like(x, dtype=float)

    # same-sign branch
    same_sign = ((x >= 0) & (y >= 0)) | ((x <= 0) & (y <= 0))
    diff_sign = ~same_sign

    # --- same-sign case: possibly swap x,y and weights ---
    if np.any(same_sign):
        x_s = x[same_sign].copy()
        y_s = y[same_sign].copy()
        vx_s = vx[same_sign].copy()
        vy_s = vy[same_sign].copy()
        wp_s = wp[same_sign].copy()
        wq_s = wq[same_sign].copy()

        flip = x_s < y_s
        # swap where x<y
        tmp = x_s[flip].copy(); x_s[flip] = y_s[flip]; y_s[flip] = tmp
        tmp = vx_s[flip].copy(); vx_s[flip] = vy_s[flip]; vy_s[flip] = tmp
        tmp = wp_s[flip].copy(); wp_s[flip] = wq_s[flip]; wq_s[flip] = tmp

        U_same = vy_s + wp_s * (vx_s - vy_s)
        U[same_sign] = U_same

    # --- different-sign case ---
    if np.any(diff_sign):
        U_diff = wp[diff_sign]*vx[diff_sign] + wq[diff_sign]*vy[diff_sign]
        U[diff_sign] = U_diff

    return U


# ============================================================
# Prospect Theory MSE (vectorized)
# ============================================================

def mse_pt(params, data, fit_lambda=True, fit_beta=True):
    """
    params:
        if fit_lambda and fit_beta:  [sigma, gamma, lam, beta]
        if fit_lambda and not fit_beta: [sigma, gamma, lam], beta=1
        if not fit_lambda: [sigma, gamma], lam=1, beta=1
    data: DataFrame for one group
    """
    if fit_lambda and fit_beta:
        sigma, gamma, lam, beta = params
    elif fit_lambda:
        sigma, gamma, lam = params
        beta = 1.0
    else:
        sigma, gamma = params
        lam, beta = 1.0, 1.0

    # Extract arrays
    xa = data["x_a"].to_numpy(dtype=float)
    ya = data["y_a"].to_numpy(dtype=float)
    xb = data["x_b"].to_numpy(dtype=float)
    yb = data["y_b"].to_numpy(dtype=float)
    p_a = data["p_a"].to_numpy(dtype=float)
    p_b = data["p_b"].to_numpy(dtype=float)
    p_obs = data["average_first_option_rate"].to_numpy(dtype=float)

    # Normalization (logic of line 2, but vectorized)
    den = np.maximum.reduce([np.abs(xa), np.abs(ya), np.abs(xb), np.abs(yb)])
    den = np.maximum(den, 1e-6)

    xa_n = xa / den
    ya_n = ya / den
    xb_n = xb / den
    yb_n = yb / den

    # Utilities
    ua = u_binary(xa_n, ya_n, p_a, sigma, lam, gamma)
    ub = u_binary(xb_n, yb_n, p_b, sigma, lam, gamma)

    # Choice probabilities
    p_hat = sigmoid(beta * (ua - ub))

    # MSE
    mse = float(np.mean((p_obs - p_hat)**2))

    return mse


# ============================================================
# Regret Theory + vectorized MSE
# ============================================================

def mse_regret(params, data):
    """
    params: [lam, kappa, alpha]
    """
    lam, kappa, alpha = params

    xa = data["x_a"].to_numpy(dtype=float)
    ya = data["y_a"].to_numpy(dtype=float)
    xb = data["x_b"].to_numpy(dtype=float)
    yb = data["y_b"].to_numpy(dtype=float)
    p_a = data["p_a"].to_numpy(dtype=float)
    p_b = data["p_b"].to_numpy(dtype=float)
    p_obs = data["average_first_option_rate"].to_numpy(dtype=float)

    # Normalization (same idea as PT)
    den = np.maximum.reduce([np.abs(xa), np.abs(ya), np.abs(xb), np.abs(yb)])
    den = np.maximum(den, 1e-6)

    xa_n = xa / den
    ya_n = ya / den
    xb_n = xb / den
    yb_n = yb / den

    # Regret deltas
    dA1 = xa_n - xb_n
    dA2 = ya_n - yb_n
    dB1 = xb_n - xa_n
    dB2 = yb_n - ya_n

    def Q_vec(delta):
        return delta + kappa * np.sign(delta) * (np.abs(delta)**alpha)

    Q_A1 = Q_vec(dA1)
    Q_A2 = Q_vec(dA2)
    Q_B1 = Q_vec(dB1)
    Q_B2 = Q_vec(dB2)

    RA = p_a * Q_A1 + (1 - p_a) * Q_A2
    RB = p_b * Q_B1 + (1 - p_b) * Q_B2

    # Choice probabilities
    p_hat = sigmoid(lam * (RA - RB))

    # MSE
    mse = float(np.mean((p_obs - p_hat)**2))

    return mse

# ============================================================
# Parametric Bootstrap Engine
# ============================================================

def run_parametric_bootstrap(data, best_params, model_type, bounds, n_boot=1000, n_trials=10):
    """
    Generates synthetic datasets via binomial sampling from p_hat
    and calculates percentile-based CIs.
    """
    # 1. Get predicted probabilities (p_hat) from original best fit
    if model_type == 'm3': # Full PT
        p_hat = predict_pt(best_params, data, True, True)
        fit_fn = lambda p: mse_pt(p, data_boot, True, True)
    # Add other models here if needed (e.g., m4)
    
    boot_params = []
    data_boot = data.copy()
    
    # 2. Bootstrap Loop
    for _ in range(n_boot):
        # Parametric sampling: simulate N trials using p_hat
        # n_trials=10 based on your paper (Section 2.4)
        sim_counts = np.random.binomial(n=n_trials, p=p_hat)
        sim_rates = sim_counts / n_trials
        
        data_boot["average_first_option_rate"] = sim_rates
        
        # 3. Re-fit (Warm start optimization)
        try:
            res = minimize(fit_fn, x0=best_params, bounds=bounds, method="L-BFGS-B")
            if res.success:
                boot_params.append(res.x)
        except:
            pass

    if len(boot_params) < (n_boot * 0.5):
        return None, None

    boot_params = np.array(boot_params)
    
    # 4. Percentile Method (2.5% - 97.5%)
    ci_lower = np.percentile(boot_params, 2.5, axis=0)
    ci_upper = np.percentile(boot_params, 97.5, axis=0)
    
    return ci_lower, ci_upper

# ============================================================
# Vectorized MAE versions (post-fit evaluation only)
# ============================================================

def mae_pt(params, data, fit_lambda=True, fit_beta=True):
    # same parameter unpacking as mse_pt
    if fit_lambda and fit_beta:
        sigma, gamma, lam, beta = params
    elif fit_lambda:
        sigma, gamma, lam = params
        beta = 1.0
    else:
        sigma, gamma = params
        lam, beta = 1.0, 1.0

    xa = data["x_a"].to_numpy(float)
    ya = data["y_a"].to_numpy(float)
    xb = data["x_b"].to_numpy(float)
    yb = data["y_b"].to_numpy(float)
    p_a = data["p_a"].to_numpy(float)
    p_b = data["p_b"].to_numpy(float)
    p_obs = data["average_first_option_rate"].to_numpy(float)

    den = np.maximum.reduce([np.abs(xa), np.abs(ya), np.abs(xb), np.abs(yb)])
    den = np.maximum(den, 1e-6)

    xa_n, ya_n = xa/den, ya/den
    xb_n, yb_n = xb/den, yb/den

    ua = u_binary(xa_n, ya_n, p_a, sigma, lam, gamma)
    ub = u_binary(xb_n, yb_n, p_b, sigma, lam, gamma)

    p_hat = sigmoid(beta * (ua - ub))
    return float(np.mean(np.abs(p_obs - p_hat)))


def mae_regret(params, data):
    lam, kappa, alpha = params

    xa = data["x_a"].to_numpy(float)
    ya = data["y_a"].to_numpy(float)
    xb = data["x_b"].to_numpy(float)
    yb = data["y_b"].to_numpy(float)
    p_a = data["p_a"].to_numpy(float)
    p_b = data["p_b"].to_numpy(float)
    p_obs = data["average_first_option_rate"].to_numpy(float)

    den = np.maximum.reduce([np.abs(xa), np.abs(ya), np.abs(xb), np.abs(yb)])
    den = np.maximum(den, 1e-6)

    xa_n, ya_n = xa/den, ya/den
    xb_n, yb_n = xb/den, yb/den

    dA1 = xa_n - xb_n
    dA2 = ya_n - yb_n
    dB1 = xb_n - xa_n
    dB2 = yb_n - ya_n

    def Q(delta):
        return delta + kappa * np.sign(delta) * (np.abs(delta) ** alpha)

    RA = p_a * Q(dA1) + (1 - p_a) * Q(dA2)
    RB = p_b * Q(dB1) + (1 - p_b) * Q(dB2)

    p_hat = sigmoid(lam * (RA - RB))
    return float(np.mean(np.abs(p_obs - p_hat)))


# ============================================================
# Multi-start minimizer
# ============================================================

def multi_start_minimize(obj_fn, x0_list, bounds, args=()):
    best = None
    for x0 in x0_list:
        try:
            res = minimize(obj_fn, x0=x0, args=args, bounds=bounds, method="L-BFGS-B")
            if res.success:
                if (best is None) or (res.fun < best.fun):
                    best = res
        except Exception:
            pass
    return best


# ============================================================
# Random initialization
# ============================================================

def rand_sigma_gamma_lambda():
    return [
        np.random.uniform(0.01, 3),
        np.random.uniform(0.01, 3),
        np.random.uniform(0.01, 3),
    ]

def rand_beta():
    return [np.random.uniform(0.01, 100)]

def rand_full_pt():
    return [
        np.random.uniform(0.01, 3),
        np.random.uniform(0.01, 3),
        np.random.uniform(0.01, 3),
        np.random.uniform(0.01, 100),
    ]


# ============================================================
# Main model fitting function (MSE + vectorized)
# ============================================================

def fit_pt_group(data, model_name="Unknown", n_starts=20, calc_ci=True):
    if data["average_first_option_rate"].isna().any():
        raise ValueError("NaN detected in average_first_option_rate")

    # Actual observed probabilities (vector A)
    A = data["average_first_option_rate"].to_numpy(float)

    # ------------ Model 1: Beta-only PT ------------
    m1_starts = [
        [1.0],
        [1000.0]
    ] + [rand_beta() for _ in range(n_starts)]

    m1_bounds = [(0.01, 1000)]

    res1 = multi_start_minimize(
        lambda b: mse_pt([1, 1, 1, b[0]], data, True, True),
        m1_starts, m1_bounds
    )

    if res1 is not None:
        beta1 = float(res1.x[0])
    else:
        beta1 = 1.0

    sigma1 = gamma1 = lam1 = 1.0
    mse1 = mse_pt([1, 1, 1, beta1], data, True, True)
    mae1 = mae_pt([1, 1, 1, beta1], data, True, True)

    xa = data["x_a"].to_numpy(float)
    ya = data["y_a"].to_numpy(float)
    xb = data["x_b"].to_numpy(float)
    yb = data["y_b"].to_numpy(float)
    p_a = data["p_a"].to_numpy(float)
    p_b = data["p_b"].to_numpy(float)

    den = np.maximum.reduce([np.abs(xa), np.abs(ya), np.abs(xb), np.abs(yb)])
    den = np.maximum(den, 1e-6)

    xa_n, ya_n = xa / den, ya / den
    xb_n, yb_n = xb / den, yb / den

    ua1 = u_binary(xa_n, ya_n, p_a, sigma1, lam1, gamma1)
    ub1 = u_binary(xb_n, yb_n, p_b, sigma1, lam1, gamma1)
    p_hat1 = sigmoid(beta1 * (ua1 - ub1))
    corr1 = np.corrcoef(A, p_hat1)[0, 1]


    # ------------ Model 2: σ,γ,λ only ------------
    m2_starts = [
        [1, 1, 1]
    ] + [rand_sigma_gamma_lambda() for _ in range(n_starts)]

    m2_bounds = [(0.01, 1000), (0.01, 1000), (0.01, 1000)]

    res2 = multi_start_minimize(
        lambda pars: mse_pt(pars, data, True, False),
        m2_starts, m2_bounds
    )

    if res2 is not None:
        sigma2, gamma2, lam2 = map(float, res2.x)
        success2 = True
    else:
        sigma2 = gamma2 = lam2 = np.nan
        success2 = False

    beta2 = 1.0
    if success2:
        mse2 = mse_pt([sigma2, gamma2, lam2], data, True, False)
        mae2 = mae_pt([sigma2, gamma2, lam2], data, True, False)

        ua2 = u_binary(xa_n, ya_n, p_a, sigma2, lam2, gamma2)
        ub2 = u_binary(xb_n, yb_n, p_b, sigma2, lam2, gamma2)
        p_hat2 = sigmoid(beta2 * (ua2 - ub2))
        corr2 = np.corrcoef(A, p_hat2)[0, 1]
    else:
        mse2 = np.nan
        mae2 = np.nan
        corr2 = np.nan


    # ------------ Model 3: Full PT -------------
    m3_starts = [
        [1, 1, 1, 1],
        [1, 1, 1, 1000]
    ] + [rand_full_pt() for _ in range(n_starts)]

    if res2 is not None:
        m3_starts.append([sigma2, gamma2, lam2, beta1])

    m3_bounds = [
        (0.01, 1000), (0.01, 1000), (0.01, 1000), (0.01, 1000)
    ]

    res3 = multi_start_minimize(
        lambda pars: mse_pt(pars, data, True, True),
        m3_starts, m3_bounds
    )

    if res3 is not None:
        sigma3, gamma3, lam3, beta3 = map(float, res3.x)
        success3 = True
    else:
        sigma3 = gamma3 = lam3 = beta3 = np.nan
        success3 = False

    sigma3_ci = gamma3_ci = lam3_ci = beta3_ci = [np.nan, np.nan]
    
    if success3 and calc_ci:
        best_p = [sigma3, gamma3, lam3, beta3]
        low, high = run_parametric_bootstrap(
            data, best_p, 'm3', m3_bounds, n_boot=1000, n_trials=10
        )
        if low is not None:
            sigma3_ci = [low[0], high[0]]
            gamma3_ci = [low[1], high[1]]
            lam3_ci   = [low[2], high[2]]
            beta3_ci  = [low[3], high[3]]

    if success3:
        mse3 = mse_pt([sigma3, gamma3, lam3, beta3], data, True, True)
        mae3 = mae_pt([sigma3, gamma3, lam3, beta3], data, True, True)

        ua3 = u_binary(xa_n, ya_n, p_a, sigma3, lam3, gamma3)
        ub3 = u_binary(xb_n, yb_n, p_b, sigma3, lam3, gamma3)
        p_hat3 = sigmoid(beta3 * (ua3 - ub3))
        corr3 = np.corrcoef(A, p_hat3)[0, 1]
    else:
        mse3 = np.nan
        mae3 = np.nan
        corr3 = np.nan


    # ------------ Model 4: Regret -------------
    m4_starts = [
        [1, 1, 1.5]
    ] + [
        list(np.random.uniform([0.01, 0, 0], [1000, 1000, 1000]))
        for _ in range(n_starts)
    ]

    m4_bounds = [(0.01, 1000), (0, 1000), (0, 1000)]

    res4 = multi_start_minimize(
        mse_regret,
        m4_starts, m4_bounds,
        args=(data,)
    )

    if res4 is not None:
        lam4, kappa4, alpha4 = map(float, res4.x)
        success4 = True
    else:
        lam4 = kappa4 = alpha4 = np.nan
        success4 = False

    if success4:
        mse4 = mse_regret([lam4, kappa4, alpha4], data)
        mae4 = mae_regret([lam4, kappa4, alpha4], data)

        dA1 = xa_n - xb_n
        dA2 = ya_n - yb_n
        dB1 = xb_n - xa_n
        dB2 = yb_n - ya_n

        def Q_reg(delta):
            return delta + kappa4 * np.sign(delta) * (np.abs(delta) ** alpha4)

        RA = p_a * Q_reg(dA1) + (1 - p_a) * Q_reg(dA2)
        RB = p_b * Q_reg(dB1) + (1 - p_b) * Q_reg(dB2)
        p_hat4 = sigmoid(lam4 * (RA - RB))
        corr4 = np.corrcoef(A, p_hat4)[0, 1]
    else:
        mse4 = np.nan
        mae4 = np.nan
        corr4 = np.nan


    return pd.Series({
        "Model": model_name,
        "n_trials": len(data),

        # Model 1
        "sigma_m1": sigma1, "gamma_m1": gamma1, "lambda_m1": lam1, "beta_m1": beta1,
        "mse_m1": mse1,
        "mae_m1": mae1,
        "corr_m1": corr1,

        # Model 2
        "sigma_m2": sigma2, "gamma_m2": gamma2, "lambda_m2": lam2, "beta_m2": beta2,
        "mse_m2": mse2, "success_m2": success2,
        "mae_m2": mae2,
        "corr_m2": corr2,

        # Model 3
        "sigma_m3": sigma3, "gamma_m3": gamma3, "lambda_m3": lam3, "beta_m3": beta3,
        "mse_m3": mse3, "success_m3": success3,
        "mae_m3": mae3,
        "corr_m3": corr3,
        "sigma_m3_lo": sigma3_ci[0], "sigma_m3_hi": sigma3_ci[1],
        "gamma_m3_lo": gamma3_ci[0], "gamma_m3_hi": gamma3_ci[1],
        "lambda_m3_lo": lam3_ci[0], "lambda_m3_hi": lam3_ci[1],
        "beta_m3_lo": beta3_ci[0], "beta_m3_hi": beta3_ci[1],

        # Model 4
        "lam_m4": lam4, "kappa_m4": kappa4, "alpha_m4": alpha4,
        "mse_m4": mse4, "success_m4": success4,
        "mae_m4": mae4,
        "corr_m4": corr4,
    })


# ============================================================
# Runner with checkpointing
# ============================================================

def run_with_progress(grouped, label, checkpoint_file):
    log(f"=== Starting run: {label} ===")

    checkpoint = load_checkpoint(checkpoint_file)
    completed_keys = set()

    if not checkpoint.empty:
        key_cols = grouped.grouper.names
        for _, row in checkpoint.iterrows():
            try:
                key_tuple = tuple(row[k] for k in key_cols)
                completed_keys.add(key_tuple)
            except Exception:
                pass

    results = []
    group_names = grouped.grouper.names

    for key, group in tqdm(grouped, desc=f"Fitting {label}", total=len(grouped)):
        key_tuple = key if isinstance(key, tuple) else (key,)

        if key_tuple in completed_keys:
            log(f"Skipping {key_tuple}: already completed")
            continue

        log(f"Running fit for {key_tuple}")
        start = time.time()

        res = fit_pt_group(group, model_name=key[0] if isinstance(key, tuple) else key)

        if isinstance(key, tuple):
            for name, val in zip(group_names, key):
                res[name] = val
        else:
            res[group_names[0]] = key

        results.append(res)

        append_checkpoint(checkpoint_file, res.to_dict())
        log(f"Completed {key_tuple} in {time.time()-start:.2f} sec")

    log(f"=== Finished run: {label} ===")
    return pd.concat([checkpoint] + results, ignore_index=True)


# ============================================================
# Actual runs
# ============================================================

res_model = run_with_progress(
    df_combined.groupby("Model", sort=False),
    "By Model",
    checkpoint_file="checkpoint_by_model.csv"
)

# res_model_sample = run_with_progress(
#     df_combined.groupby(["Model", "Sample_Size"], sort=False),
#     "By Model × Sample_Size",
#     checkpoint_file="checkpoint_by_model_sample_mse.csv"
# )

# res_model_prompt = run_with_progress(
#     df_combined.groupby(["Model", "Prompt_Style"], sort=False),
#     "By Model × Prompt_Style",
#     checkpoint_file="checkpoint_by_model_prompt.csv"
# )

# res_full = run_with_progress(
#     df_combined.groupby(["Model", "Prompt_Style", "Sample_Size"], sort=False),
#     "By Model × Prompt_Style × Sample_Size",
#     checkpoint_file="checkpoint_full_mse.csv"
# )


# ============================================================
# Export all final results
# ============================================================

log("Saving final output CSVs...")

res_model.to_csv("results_by_model.csv", index=False)
# res_model_sample.to_csv("results_by_model_sample_mse.csv", index=False)
# res_model_prompt.to_csv("results_by_model_prompt.csv", index=False)
# res_full.to_csv("results_full_mse.csv", index=False)

log("All CSVs saved successfully.")
print("Done.")
