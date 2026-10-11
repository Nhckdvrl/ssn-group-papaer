# L15 pilot summary — mistral_small_24b (pilot_v1)

- cells: 2982  |  raw: `results/pilot_v1/mistral_small_24b/raw.jsonl`

## mode = direct

| condition | n | coverage | MAE |
|---|---:|---:|---:|
| P0_PRIOR | 36 | 1.000 | 0.0000 |
| P1_NULL | 360 | 1.000 | 0.0000 |
| P2_ARITH | 15 | 1.000 | 0.2063 |
| P2_HANDED | 180 | 1.000 | 0.2882 |
| P2_NULL | 360 | 1.000 | 0.2557 |
| P2_POS | 180 | 1.000 | 0.1863 |
| P3_DECIDE | 360 | 1.000 | nan |

**Detectability response (P2_NULL):** mean Spearman vs gold -0.193 (95% CI [-0.3147, -0.081]), compression ratio -0.153 (95% CI [-0.2918, -0.0209]), monotonicity violations 88/288.

**KNI:** obs-known rate 1.000, KNI rate 0.678 (95% CI [0.6278, 0.7306]), mean Err_obs 0.0000, mean Err_post 0.2557.

**P2 MAE by frame:** {'access': 0.2629, 'diagnostic': 0.2746, 'monitoring': 0.2429, 'search': 0.2424}

**KNI by frame:** {'access': 0.6778, 'diagnostic': 0.7, 'monitoring': 0.6778, 'search': 0.6556}

**Controls:** {'arith_mae': 0.2063, 'framed_mae_same_cells': 0.2557, 'framed_minus_arith': 0.0494, 'handed_mae': 0.2882, 'null_mae': 0.2557, 'positive_control_mae': 0.1863, 'prior_only_mae': 0.0}

**Decision (P3):** {'n': 360, 'accuracy_vs_gold': 0.55, 'consistency_with_own_posterior': 0.7417}

## mode = cot

| condition | n | coverage | MAE |
|---|---:|---:|---:|
| P0_PRIOR | 36 | 1.000 | 0.0000 |
| P1_NULL | 360 | 1.000 | 0.0000 |
| P2_ARITH | 15 | 1.000 | 0.0018 |
| P2_HANDED | 180 | 0.983 | 0.0580 |
| P2_NULL | 360 | 1.000 | 0.0074 |
| P2_POS | 180 | 0.994 | 0.0000 |
| P3_DECIDE | 360 | 1.000 | nan |

**Detectability response (P2_NULL):** mean Spearman vs gold 0.945 (95% CI [0.8675, 1.0]), compression ratio 0.929 (95% CI [0.832, 0.9985]), monotonicity violations 5/288.

**KNI:** obs-known rate 1.000, KNI rate 0.014 (95% CI [0.0, 0.0333]), mean Err_obs 0.0000, mean Err_post 0.0074.

**P2 MAE by frame:** {'access': 0.0155, 'diagnostic': 0.0018, 'monitoring': 0.0106, 'search': 0.0018}

**KNI by frame:** {'access': 0.0333, 'diagnostic': 0.0, 'monitoring': 0.0222, 'search': 0.0}

**Controls:** {'arith_mae': 0.0018, 'framed_mae_same_cells': 0.0074, 'framed_minus_arith': 0.0056, 'handed_mae': 0.058, 'null_mae': 0.0074, 'positive_control_mae': 0.0, 'prior_only_mae': 0.0}

**Decision (P3):** {'n': 360, 'accuracy_vs_gold': 0.8583, 'consistency_with_own_posterior': 0.8556}

