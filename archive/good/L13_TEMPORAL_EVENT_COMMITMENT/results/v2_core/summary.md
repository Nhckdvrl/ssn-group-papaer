# L13 summary — v2_core

## qwen3_8b (qwen3), 100 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.977 | 0.002 | 0.022 | 0.990 |
| before_neutral | 0.029 | 0.225 | 0.746 | 0.920 |
| before_confirm | 0.946 | 0.013 | 0.042 | 0.970 |
| before_cancel | 0.017 | 0.840 | 0.144 | 0.890 |
| nontemporal_neutral | 0.039 | 0.128 | 0.832 | 0.910 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | -0.011 [-0.044, +0.017] |
| veridicality_gap | +0.948 [+0.923, +0.969] |
| confirm_update | +0.917 [+0.877, +0.952] |
| cancel_update | +0.012 [-0.009, +0.032] |
| gold_update_confirm | +0.917 [+0.877, +0.952] |
| gold_update_cancel | +0.614 [+0.567, +0.661] |
| gold_update_asymmetry | +0.303 [+0.245, +0.360] |
| update_asymmetry | +0.878 [+0.830, +0.921] |
| paraphrase_first_effect__after | +0.023 [+0.007, +0.044] |
| paraphrase_first_effect__before_neutral | -0.009 [-0.029, +0.012] |
| paraphrase_first_effect__before_confirm | -0.006 [-0.035, +0.017] |
| paraphrase_first_effect__before_cancel | -0.008 [-0.023, +0.004] |
| paraphrase_first_effect__nontemporal_neutral | -0.035 [-0.067, -0.012] |
| timeline_first_effect__after | +0.023 [+0.008, +0.044] |
| timeline_first_effect__before_neutral | +0.134 [+0.072, +0.203] |
| timeline_first_effect__before_confirm | -0.017 [-0.048, +0.007] |
| timeline_first_effect__before_cancel | -0.005 [-0.027, +0.021] |
| timeline_first_effect__nontemporal_neutral | -0.039 [-0.070, -0.015] |
| timeline_minus_paraphrase__after | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__before_neutral | +0.143 [+0.080, +0.210] |
| timeline_minus_paraphrase__before_confirm | -0.011 [-0.033, +0.004] |
| timeline_minus_paraphrase__before_cancel | +0.003 [-0.017, +0.027] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.004 [-0.011, -0.000] |
| timeline_specificity_vs_nontemporal | +0.147 [+0.084, +0.214] |
| timeline_specificity_vs_after | +0.143 [+0.080, +0.209] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.434 [4.354, 4.513] |
| before_neutral | 2.098 [1.982, 2.219] |
| before_confirm | 4.390 [4.279, 4.487] |
| before_cancel | 1.214 [1.133, 1.312] |
| nontemporal_neutral | 2.216 [2.070, 2.365] |

## llama31_8b_instruct (llama3), 100 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.668 | 0.052 | 0.280 | 0.940 |
| before_neutral | 0.217 | 0.210 | 0.573 | 0.870 |
| before_confirm | 0.550 | 0.059 | 0.391 | 0.730 |
| before_cancel | 0.096 | 0.469 | 0.435 | 0.530 |
| nontemporal_neutral | 0.103 | 0.143 | 0.754 | 0.990 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.114 [+0.091, +0.137] |
| veridicality_gap | +0.451 [+0.427, +0.474] |
| confirm_update | +0.333 [+0.306, +0.359] |
| cancel_update | +0.121 [+0.099, +0.144] |
| gold_update_confirm | +0.333 [+0.306, +0.360] |
| gold_update_cancel | +0.259 [+0.226, +0.291] |
| gold_update_asymmetry | +0.074 [+0.034, +0.114] |
| update_asymmetry | +0.204 [+0.167, +0.242] |
| paraphrase_first_effect__after | -0.113 [-0.136, -0.091] |
| paraphrase_first_effect__before_neutral | -0.168 [-0.187, -0.150] |
| paraphrase_first_effect__before_confirm | -0.246 [-0.266, -0.227] |
| paraphrase_first_effect__before_cancel | -0.090 [-0.103, -0.078] |
| paraphrase_first_effect__nontemporal_neutral | -0.084 [-0.095, -0.073] |
| timeline_first_effect__after | -0.030 [-0.051, -0.008] |
| timeline_first_effect__before_neutral | -0.056 [-0.072, -0.040] |
| timeline_first_effect__before_confirm | -0.180 [-0.199, -0.160] |
| timeline_first_effect__before_cancel | -0.047 [-0.058, -0.034] |
| timeline_first_effect__nontemporal_neutral | -0.081 [-0.092, -0.071] |
| timeline_minus_paraphrase__after | +0.083 [+0.064, +0.103] |
| timeline_minus_paraphrase__before_neutral | +0.112 [+0.094, +0.130] |
| timeline_minus_paraphrase__before_confirm | +0.067 [+0.050, +0.083] |
| timeline_minus_paraphrase__before_cancel | +0.044 [+0.030, +0.059] |
| timeline_minus_paraphrase__nontemporal_neutral | +0.003 [-0.001, +0.006] |
| timeline_specificity_vs_nontemporal | +0.109 [+0.091, +0.127] |
| timeline_specificity_vs_after | +0.029 [+0.004, +0.054] |

| condition | E[rating 1-5] |
|---|---|
| after | 3.764 [3.729, 3.800] |
| before_neutral | 3.443 [3.403, 3.483] |
| before_confirm | 3.679 [3.648, 3.710] |
| before_cancel | 2.943 [2.877, 3.009] |
| nontemporal_neutral | 3.376 [3.335, 3.417] |

## gemma3_12b_it (gemma3), 100 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.998 | 0.000 | 0.002 | 1.000 |
| before_neutral | 0.089 | 0.037 | 0.874 | 0.880 |
| before_confirm | 0.912 | 0.005 | 0.083 | 0.920 |
| before_cancel | 0.005 | 0.821 | 0.174 | 0.840 |
| nontemporal_neutral | 0.000 | 0.057 | 0.943 | 0.940 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.089 [+0.048, +0.136] |
| veridicality_gap | +0.909 [+0.863, +0.949] |
| confirm_update | +0.823 [+0.757, +0.885] |
| cancel_update | +0.084 [+0.041, +0.130] |
| gold_update_confirm | +0.823 [+0.757, +0.883] |
| gold_update_cancel | +0.784 [+0.714, +0.851] |
| gold_update_asymmetry | +0.039 [-0.054, +0.131] |
| update_asymmetry | +0.730 [+0.633, +0.822] |
| paraphrase_first_effect__after | -0.009 [-0.023, +0.001] |
| paraphrase_first_effect__before_neutral | +0.027 [-0.021, +0.073] |
| paraphrase_first_effect__before_confirm | -0.045 [-0.081, -0.014] |
| paraphrase_first_effect__before_cancel | +0.007 [-0.013, +0.032] |
| paraphrase_first_effect__nontemporal_neutral | +0.008 [+0.000, +0.020] |
| timeline_first_effect__after | +0.002 [+0.000, +0.005] |
| timeline_first_effect__before_neutral | +0.410 [+0.331, +0.489] |
| timeline_first_effect__before_confirm | -0.012 [-0.051, +0.026] |
| timeline_first_effect__before_cancel | +0.122 [+0.067, +0.183] |
| timeline_first_effect__nontemporal_neutral | -0.000 [-0.000, -0.000] |
| timeline_minus_paraphrase__after | +0.011 [+0.002, +0.025] |
| timeline_minus_paraphrase__before_neutral | +0.383 [+0.315, +0.452] |
| timeline_minus_paraphrase__before_confirm | +0.033 [-0.008, +0.077] |
| timeline_minus_paraphrase__before_cancel | +0.115 [+0.059, +0.176] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.009 [-0.020, -0.000] |
| timeline_specificity_vs_nontemporal | +0.391 [+0.322, +0.462] |
| timeline_specificity_vs_after | +0.372 [+0.304, +0.441] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.779 [4.680, 4.864] |
| before_neutral | 2.583 [2.374, 2.806] |
| before_confirm | 4.814 [4.683, 4.921] |
| before_cancel | 1.225 [1.110, 1.358] |
| nontemporal_neutral | 2.328 [2.143, 2.516] |

## qwen3_32b (qwen3), 100 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.996 | 0.003 | 0.001 | 1.000 |
| before_neutral | 0.285 | 0.611 | 0.104 | 0.030 |
| before_confirm | 0.976 | 0.013 | 0.010 | 0.980 |
| before_cancel | 0.040 | 0.955 | 0.005 | 0.950 |
| nontemporal_neutral | 0.085 | 0.346 | 0.569 | 0.550 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.200 [+0.132, +0.269] |
| veridicality_gap | +0.711 [+0.640, +0.779] |
| confirm_update | +0.691 [+0.616, +0.763] |
| cancel_update | +0.245 [+0.178, +0.314] |
| gold_update_confirm | +0.691 [+0.617, +0.764] |
| gold_update_cancel | +0.344 [+0.268, +0.423] |
| gold_update_asymmetry | +0.347 [+0.206, +0.487] |
| update_asymmetry | +0.442 [+0.307, +0.572] |
| paraphrase_first_effect__after | -0.006 [-0.017, -0.000] |
| paraphrase_first_effect__before_neutral | +0.003 [-0.059, +0.067] |
| paraphrase_first_effect__before_confirm | -0.004 [-0.029, +0.018] |
| paraphrase_first_effect__before_cancel | -0.002 [-0.028, +0.025] |
| paraphrase_first_effect__nontemporal_neutral | -0.045 [-0.074, -0.021] |
| timeline_first_effect__after | +0.004 [+0.000, +0.011] |
| timeline_first_effect__before_neutral | +0.367 [+0.299, +0.435] |
| timeline_first_effect__before_confirm | -0.024 [-0.058, +0.005] |
| timeline_first_effect__before_cancel | +0.021 [+0.002, +0.040] |
| timeline_first_effect__nontemporal_neutral | -0.076 [-0.113, -0.044] |
| timeline_minus_paraphrase__after | +0.010 [+0.001, +0.027] |
| timeline_minus_paraphrase__before_neutral | +0.364 [+0.297, +0.434] |
| timeline_minus_paraphrase__before_confirm | -0.020 [-0.050, +0.004] |
| timeline_minus_paraphrase__before_cancel | +0.023 [-0.002, +0.051] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.030 [-0.046, -0.016] |
| timeline_specificity_vs_nontemporal | +0.395 [+0.326, +0.468] |
| timeline_specificity_vs_after | +0.354 [+0.282, +0.427] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.956 [4.895, 4.988] |
| before_neutral | 2.554 [2.257, 2.865] |
| before_confirm | 4.902 [4.840, 4.950] |
| before_cancel | 1.128 [1.034, 1.242] |
| nontemporal_neutral | 2.378 [2.154, 2.601] |
