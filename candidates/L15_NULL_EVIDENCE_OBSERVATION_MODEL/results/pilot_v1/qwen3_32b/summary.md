# L15 pilot summary — qwen3_32b (pilot_v1)

- cells: 2982  |  raw: `results/pilot_v1/qwen3_32b/raw.jsonl`

## mode = direct

| condition | n | coverage | MAE |
|---|---:|---:|---:|
| P0_PRIOR | 36 | 1.000 | 0.0000 |
| P1_NULL | 360 | 1.000 | 0.0000 |
| P2_ARITH | 15 | 1.000 | 0.2344 |
| P2_HANDED | 180 | 1.000 | 0.2226 |
| P2_NULL | 360 | 1.000 | 0.2082 |
| P2_POS | 180 | 1.000 | 0.1467 |
| P3_DECIDE | 360 | 1.000 | nan |

**Detectability response (P2_NULL):** mean Spearman vs gold -0.034 (95% CI [-0.128, 0.0682]), compression ratio 0.038 (95% CI [-0.0505, 0.1467]), monotonicity violations 124/288.

**KNI:** obs-known rate 1.000, KNI rate 0.489 (95% CI [0.4528, 0.5278]), mean Err_obs 0.0000, mean Err_post 0.2082.

**P2 MAE by frame:** {'access': 0.2312, 'diagnostic': 0.2038, 'monitoring': 0.2094, 'search': 0.1883}

**KNI by frame:** {'access': 0.5556, 'diagnostic': 0.4333, 'monitoring': 0.5, 'search': 0.4667}

**Controls:** {'arith_mae': 0.2344, 'framed_mae_same_cells': 0.2082, 'framed_minus_arith': -0.0262, 'handed_mae': 0.2226, 'null_mae': 0.2082, 'positive_control_mae': 0.1467, 'prior_only_mae': 0.0}

**Decision (P3):** {'n': 360, 'accuracy_vs_gold': 0.5444, 'consistency_with_own_posterior': 0.6944}

## mode = cot

| condition | n | coverage | MAE |
|---|---:|---:|---:|
| P0_PRIOR | 36 | 1.000 | 0.0000 |
| P1_NULL | 360 | 1.000 | 0.0000 |
| P2_ARITH | 15 | 1.000 | 0.0018 |
| P2_HANDED | 180 | 1.000 | 0.0018 |
| P2_NULL | 360 | 1.000 | 0.0035 |
| P2_POS | 180 | 1.000 | 0.0000 |
| P3_DECIDE | 360 | 0.986 | nan |

**Detectability response (P2_NULL):** mean Spearman vs gold 0.989 (95% CI [0.9669, 1.0]), compression ratio 0.985 (95% CI [0.9571, 0.9985]), monotonicity violations 1/288.

**KNI:** obs-known rate 1.000, KNI rate 0.003 (95% CI [0.0, 0.0083]), mean Err_obs 0.0000, mean Err_post 0.0035.

**P2 MAE by frame:** {'access': 0.0018, 'diagnostic': 0.0087, 'monitoring': 0.0018, 'search': 0.0018}

**KNI by frame:** {'access': 0.0, 'diagnostic': 0.0111, 'monitoring': 0.0, 'search': 0.0}

**Controls:** {'arith_mae': 0.0018, 'framed_mae_same_cells': 0.0035, 'framed_minus_arith': 0.0017, 'handed_mae': 0.0018, 'null_mae': 0.0035, 'positive_control_mae': 0.0, 'prior_only_mae': 0.0}

**Decision (P3):** {'n': 355, 'accuracy_vs_gold': 0.9183, 'consistency_with_own_posterior': 0.9155}

