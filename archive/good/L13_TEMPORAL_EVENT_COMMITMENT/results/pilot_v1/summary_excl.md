# L13 summary — pilot_v1

## qwen3_8b (qwen3), 38 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.988 | 0.003 | 0.009 | 1.000 |
| before_neutral | 0.018 | 0.209 | 0.773 | 0.921 |
| before_confirm | 0.912 | 0.017 | 0.071 | 0.921 |
| before_cancel | 0.000 | 0.870 | 0.130 | 0.921 |
| nontemporal_neutral | 0.024 | 0.133 | 0.843 | 0.921 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | -0.006 [-0.049, +0.034] |
| veridicality_gap | +0.970 [+0.938, +0.992] |
| confirm_update | +0.894 [+0.797, +0.971] |
| cancel_update | +0.018 [+0.001, +0.047] |
| gold_update_confirm | +0.894 [+0.798, +0.971] |
| gold_update_cancel | +0.661 [+0.586, +0.735] |
| gold_update_asymmetry | +0.233 [+0.120, +0.340] |
| update_asymmetry | +0.876 [+0.771, +0.961] |
| order_mc_first_effect__after | -0.051 [-0.125, +0.005] |
| order_mc_first_effect__before_neutral | +0.006 [-0.018, +0.038] |
| order_mc_first_effect__before_confirm | +0.032 [-0.003, +0.094] |
| order_mc_first_effect__before_cancel | -0.000 [-0.001, -0.000] |
| order_mc_first_effect__nontemporal_neutral | -0.024 [-0.060, -0.000] |
| paraphrase_first_effect__after | +0.012 [+0.002, +0.025] |
| paraphrase_first_effect__before_neutral | -0.013 [-0.042, +0.006] |
| paraphrase_first_effect__before_confirm | +0.009 [-0.004, +0.031] |
| paraphrase_first_effect__before_cancel | -0.000 [-0.001, -0.000] |
| paraphrase_first_effect__nontemporal_neutral | -0.024 [-0.061, -0.000] |
| schema_timeline_first_effect__after | +0.012 [+0.002, +0.026] |
| schema_timeline_first_effect__before_neutral | +0.155 [+0.065, +0.261] |
| schema_timeline_first_effect__before_confirm | -0.017 [-0.108, +0.073] |
| schema_timeline_first_effect__before_cancel | +0.026 [-0.001, +0.079] |
| schema_timeline_first_effect__nontemporal_neutral | -0.024 [-0.061, -0.000] |
| timeline_first_effect__after | +0.012 [+0.002, +0.026] |
| timeline_first_effect__before_neutral | +0.168 [+0.068, +0.279] |
| timeline_first_effect__before_confirm | -0.010 [-0.045, +0.014] |
| timeline_first_effect__before_cancel | +0.030 [-0.000, +0.083] |
| timeline_first_effect__nontemporal_neutral | -0.024 [-0.061, -0.000] |
| timeline_strict_first_effect__after | +0.012 [+0.002, +0.026] |
| timeline_strict_first_effect__before_neutral | +0.105 [+0.017, +0.210] |
| timeline_strict_first_effect__before_confirm | +0.018 [-0.018, +0.076] |
| timeline_strict_first_effect__before_cancel | +0.016 [-0.001, +0.049] |
| timeline_strict_first_effect__nontemporal_neutral | -0.024 [-0.061, -0.000] |
| topic_mc_first_effect__after | -0.143 [-0.243, -0.056] |
| topic_mc_first_effect__before_neutral | -0.014 [-0.035, -0.001] |
| topic_mc_first_effect__before_confirm | -0.062 [-0.127, -0.007] |
| topic_mc_first_effect__before_cancel | -0.000 [-0.001, -0.000] |
| topic_mc_first_effect__nontemporal_neutral | -0.024 [-0.061, -0.000] |
| timeline_minus_paraphrase__after | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__before_neutral | +0.180 [+0.088, +0.284] |
| timeline_minus_paraphrase__before_confirm | -0.019 [-0.074, +0.016] |
| timeline_minus_paraphrase__before_cancel | +0.030 [+0.000, +0.084] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.000 [-0.000, -0.000] |
| timeline_specificity_vs_nontemporal | +0.180 [+0.087, +0.287] |
| timeline_specificity_vs_after | +0.180 [+0.090, +0.288] |
| order_minus_topic_mc__after | +0.092 [+0.037, +0.161] |
| order_minus_topic_mc__before_neutral | +0.021 [+0.000, +0.057] |
| order_minus_topic_mc__before_confirm | +0.095 [+0.028, +0.178] |
| order_minus_topic_mc__before_cancel | +0.000 [+0.000, +0.000] |
| order_minus_topic_mc__nontemporal_neutral | +0.000 [-0.000, +0.000] |
| strict_minus_open_timeline__after | -0.000 [-0.000, +0.000] |
| strict_minus_open_timeline__before_neutral | -0.063 [-0.167, +0.034] |
| strict_minus_open_timeline__before_confirm | +0.028 [+0.000, +0.076] |
| strict_minus_open_timeline__before_cancel | -0.014 [-0.036, -0.000] |
| strict_minus_open_timeline__nontemporal_neutral | +0.000 [+0.000, +0.000] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.519 [4.408, 4.625] |
| before_neutral | 2.031 [1.836, 2.245] |
| before_confirm | 4.411 [4.202, 4.585] |
| before_cancel | 1.100 [1.040, 1.175] |
| nontemporal_neutral | 2.109 [1.868, 2.368] |

## llama31_8b_instruct (llama3), 38 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.664 | 0.054 | 0.283 | 0.947 |
| before_neutral | 0.186 | 0.222 | 0.592 | 0.868 |
| before_confirm | 0.534 | 0.046 | 0.419 | 0.605 |
| before_cancel | 0.080 | 0.524 | 0.397 | 0.632 |
| nontemporal_neutral | 0.077 | 0.139 | 0.784 | 1.000 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.109 [+0.079, +0.140] |
| veridicality_gap | +0.478 [+0.438, +0.516] |
| confirm_update | +0.348 [+0.309, +0.388] |
| cancel_update | +0.106 [+0.072, +0.147] |
| gold_update_confirm | +0.348 [+0.309, +0.388] |
| gold_update_cancel | +0.302 [+0.243, +0.362] |
| gold_update_asymmetry | +0.047 [-0.025, +0.116] |
| update_asymmetry | +0.235 [+0.177, +0.289] |
| order_mc_first_effect__after | +0.093 [+0.063, +0.127] |
| order_mc_first_effect__before_neutral | -0.085 [-0.112, -0.060] |
| order_mc_first_effect__before_confirm | -0.047 [-0.094, -0.000] |
| order_mc_first_effect__before_cancel | -0.054 [-0.068, -0.041] |
| order_mc_first_effect__nontemporal_neutral | -0.034 [-0.049, -0.020] |
| paraphrase_first_effect__after | -0.099 [-0.133, -0.066] |
| paraphrase_first_effect__before_neutral | -0.150 [-0.177, -0.125] |
| paraphrase_first_effect__before_confirm | -0.240 [-0.267, -0.212] |
| paraphrase_first_effect__before_cancel | -0.077 [-0.096, -0.060] |
| paraphrase_first_effect__nontemporal_neutral | -0.068 [-0.088, -0.052] |
| schema_timeline_first_effect__after | +0.331 [+0.299, +0.365] |
| schema_timeline_first_effect__before_neutral | +0.442 [+0.337, +0.540] |
| schema_timeline_first_effect__before_confirm | +0.374 [+0.322, +0.423] |
| schema_timeline_first_effect__before_cancel | +0.072 [+0.022, +0.133] |
| schema_timeline_first_effect__nontemporal_neutral | +0.069 [+0.034, +0.108] |
| timeline_first_effect__after | +0.003 [-0.028, +0.033] |
| timeline_first_effect__before_neutral | -0.051 [-0.078, -0.025] |
| timeline_first_effect__before_confirm | -0.171 [-0.203, -0.138] |
| timeline_first_effect__before_cancel | -0.033 [-0.053, -0.011] |
| timeline_first_effect__nontemporal_neutral | -0.066 [-0.086, -0.049] |
| timeline_strict_first_effect__after | +0.025 [-0.011, +0.064] |
| timeline_strict_first_effect__before_neutral | -0.061 [-0.084, -0.038] |
| timeline_strict_first_effect__before_confirm | -0.046 [-0.092, -0.002] |
| timeline_strict_first_effect__before_cancel | -0.059 [-0.074, -0.044] |
| timeline_strict_first_effect__nontemporal_neutral | -0.064 [-0.083, -0.047] |
| topic_mc_first_effect__after | -0.052 [-0.096, -0.013] |
| topic_mc_first_effect__before_neutral | -0.065 [-0.089, -0.041] |
| topic_mc_first_effect__before_confirm | -0.064 [-0.110, -0.018] |
| topic_mc_first_effect__before_cancel | -0.063 [-0.079, -0.047] |
| topic_mc_first_effect__nontemporal_neutral | +0.007 [-0.008, +0.022] |
| timeline_minus_paraphrase__after | +0.101 [+0.078, +0.125] |
| timeline_minus_paraphrase__before_neutral | +0.099 [+0.076, +0.123] |
| timeline_minus_paraphrase__before_confirm | +0.069 [+0.045, +0.096] |
| timeline_minus_paraphrase__before_cancel | +0.044 [+0.022, +0.073] |
| timeline_minus_paraphrase__nontemporal_neutral | +0.002 [+0.001, +0.004] |
| timeline_specificity_vs_nontemporal | +0.097 [+0.074, +0.121] |
| timeline_specificity_vs_after | -0.003 [-0.036, +0.033] |
| order_minus_topic_mc__after | +0.146 [+0.107, +0.185] |
| order_minus_topic_mc__before_neutral | -0.020 [-0.038, -0.003] |
| order_minus_topic_mc__before_confirm | +0.017 [-0.023, +0.056] |
| order_minus_topic_mc__before_cancel | +0.009 [+0.000, +0.020] |
| order_minus_topic_mc__nontemporal_neutral | -0.041 [-0.054, -0.030] |
| strict_minus_open_timeline__after | +0.023 [-0.004, +0.050] |
| strict_minus_open_timeline__before_neutral | -0.009 [-0.033, +0.013] |
| strict_minus_open_timeline__before_confirm | +0.124 [+0.083, +0.163] |
| strict_minus_open_timeline__before_cancel | -0.025 [-0.044, -0.010] |
| strict_minus_open_timeline__nontemporal_neutral | +0.002 [-0.001, +0.005] |

| condition | E[rating 1-5] |
|---|---|
| after | 3.845 [3.791, 3.900] |
| before_neutral | 3.412 [3.344, 3.481] |
| before_confirm | 3.723 [3.675, 3.770] |
| before_cancel | 2.861 [2.756, 2.963] |
| nontemporal_neutral | 3.329 [3.261, 3.399] |

## olmo3_7b_instruct_dpo (olmo3), 38 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.572 | 0.207 | 0.221 | 0.711 |
| before_neutral | 0.009 | 0.728 | 0.264 | 0.132 |
| before_confirm | 0.745 | 0.145 | 0.110 | 0.842 |
| before_cancel | 0.003 | 0.950 | 0.047 | 1.000 |
| nontemporal_neutral | 0.027 | 0.646 | 0.327 | 0.158 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | -0.018 [-0.052, +0.001] |
| veridicality_gap | +0.563 [+0.454, +0.670] |
| confirm_update | +0.736 [+0.621, +0.836] |
| cancel_update | +0.006 [+0.003, +0.011] |
| gold_update_confirm | +0.736 [+0.618, +0.836] |
| gold_update_cancel | +0.222 [+0.167, +0.281] |
| gold_update_asymmetry | +0.513 [+0.415, +0.607] |
| update_asymmetry | +0.728 [+0.617, +0.827] |
| order_mc_first_effect__after | +0.160 [+0.036, +0.277] |
| order_mc_first_effect__before_neutral | +0.091 [+0.063, +0.123] |
| order_mc_first_effect__before_confirm | +0.030 [-0.037, +0.103] |
| order_mc_first_effect__before_cancel | +0.051 [+0.022, +0.091] |
| order_mc_first_effect__nontemporal_neutral | +0.019 [-0.009, +0.044] |
| paraphrase_first_effect__after | +0.031 [-0.094, +0.150] |
| paraphrase_first_effect__before_neutral | +0.050 [+0.035, +0.069] |
| paraphrase_first_effect__before_confirm | -0.427 [-0.519, -0.329] |
| paraphrase_first_effect__before_cancel | +0.009 [+0.005, +0.017] |
| paraphrase_first_effect__nontemporal_neutral | +0.003 [-0.017, +0.015] |
| schema_timeline_first_effect__after | +0.402 [+0.291, +0.518] |
| schema_timeline_first_effect__before_neutral | +0.379 [+0.261, +0.502] |
| schema_timeline_first_effect__before_confirm | +0.140 [+0.059, +0.230] |
| schema_timeline_first_effect__before_cancel | +0.070 [+0.035, +0.125] |
| schema_timeline_first_effect__nontemporal_neutral | +0.024 [+0.005, +0.040] |
| timeline_first_effect__after | +0.241 [+0.114, +0.365] |
| timeline_first_effect__before_neutral | +0.131 [+0.069, +0.206] |
| timeline_first_effect__before_confirm | -0.074 [-0.165, +0.020] |
| timeline_first_effect__before_cancel | +0.039 [+0.007, +0.082] |
| timeline_first_effect__nontemporal_neutral | -0.016 [-0.047, +0.001] |
| timeline_strict_first_effect__after | +0.383 [+0.282, +0.487] |
| timeline_strict_first_effect__before_neutral | +0.199 [+0.119, +0.289] |
| timeline_strict_first_effect__before_confirm | +0.023 [-0.078, +0.131] |
| timeline_strict_first_effect__before_cancel | +0.046 [+0.005, +0.104] |
| timeline_strict_first_effect__nontemporal_neutral | -0.016 [-0.049, +0.002] |
| topic_mc_first_effect__after | -0.403 [-0.507, -0.294] |
| topic_mc_first_effect__before_neutral | +0.026 [+0.021, +0.031] |
| topic_mc_first_effect__before_confirm | -0.410 [-0.505, -0.312] |
| topic_mc_first_effect__before_cancel | +0.027 [+0.018, +0.038] |
| topic_mc_first_effect__nontemporal_neutral | -0.003 [-0.041, +0.018] |
| timeline_minus_paraphrase__after | +0.210 [+0.108, +0.318] |
| timeline_minus_paraphrase__before_neutral | +0.080 [+0.023, +0.152] |
| timeline_minus_paraphrase__before_confirm | +0.353 [+0.265, +0.438] |
| timeline_minus_paraphrase__before_cancel | +0.030 [+0.002, +0.066] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.018 [-0.034, -0.008] |
| timeline_specificity_vs_nontemporal | +0.099 [+0.035, +0.179] |
| timeline_specificity_vs_after | -0.130 [-0.265, +0.006] |
| order_minus_topic_mc__after | +0.562 [+0.476, +0.645] |
| order_minus_topic_mc__before_neutral | +0.065 [+0.037, +0.096] |
| order_minus_topic_mc__before_confirm | +0.440 [+0.362, +0.518] |
| order_minus_topic_mc__before_cancel | +0.025 [+0.002, +0.055] |
| order_minus_topic_mc__nontemporal_neutral | +0.023 [+0.005, +0.045] |
| strict_minus_open_timeline__after | +0.142 [+0.088, +0.203] |
| strict_minus_open_timeline__before_neutral | +0.068 [+0.013, +0.131] |
| strict_minus_open_timeline__before_confirm | +0.097 [+0.015, +0.181] |
| strict_minus_open_timeline__before_cancel | +0.007 [-0.015, +0.031] |
| strict_minus_open_timeline__nontemporal_neutral | -0.001 [-0.004, +0.002] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.451 [4.176, 4.690] |
| before_neutral | 2.059 [1.798, 2.330] |
| before_confirm | 4.566 [4.255, 4.822] |
| before_cancel | 1.218 [1.099, 1.368] |
| nontemporal_neutral | 1.923 [1.666, 2.205] |

## gemma3_12b_it (gemma3), 38 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.997 | 0.000 | 0.003 | 1.000 |
| before_neutral | 0.047 | 0.070 | 0.883 | 0.868 |
| before_confirm | 0.911 | 0.000 | 0.089 | 0.921 |
| before_cancel | 0.000 | 0.914 | 0.086 | 0.921 |
| nontemporal_neutral | 0.000 | 0.076 | 0.924 | 0.921 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.047 [+0.004, +0.110] |
| veridicality_gap | +0.950 [+0.888, +0.993] |
| confirm_update | +0.864 [+0.757, +0.953] |
| cancel_update | +0.047 [+0.004, +0.106] |
| gold_update_confirm | +0.864 [+0.762, +0.951] |
| gold_update_cancel | +0.844 [+0.736, +0.936] |
| gold_update_asymmetry | +0.020 [-0.130, +0.174] |
| update_asymmetry | +0.817 [+0.674, +0.937] |
| order_mc_first_effect__after | -0.014 [-0.036, +0.000] |
| order_mc_first_effect__before_neutral | -0.028 [-0.074, +0.008] |
| order_mc_first_effect__before_confirm | -0.107 [-0.203, -0.024] |
| order_mc_first_effect__before_cancel | -0.000 [-0.000, +0.000] |
| order_mc_first_effect__nontemporal_neutral | +0.017 [+0.000, +0.047] |
| paraphrase_first_effect__after | +0.003 [+0.000, +0.007] |
| paraphrase_first_effect__before_neutral | +0.069 [+0.032, +0.109] |
| paraphrase_first_effect__before_confirm | -0.028 [-0.067, +0.003] |
| paraphrase_first_effect__before_cancel | +0.025 [-0.000, +0.074] |
| paraphrase_first_effect__nontemporal_neutral | +0.000 [-0.000, +0.000] |
| schema_timeline_first_effect__after | +0.003 [+0.000, +0.007] |
| schema_timeline_first_effect__before_neutral | +0.453 [+0.303, +0.605] |
| schema_timeline_first_effect__before_confirm | +0.008 [-0.002, +0.027] |
| schema_timeline_first_effect__before_cancel | +0.053 [-0.000, +0.132] |
| schema_timeline_first_effect__nontemporal_neutral | +0.068 [+0.017, +0.136] |
| timeline_first_effect__after | +0.003 [+0.000, +0.007] |
| timeline_first_effect__before_neutral | +0.403 [+0.281, +0.531] |
| timeline_first_effect__before_confirm | +0.002 [-0.054, +0.066] |
| timeline_first_effect__before_cancel | +0.074 [+0.003, +0.161] |
| timeline_first_effect__nontemporal_neutral | -0.000 [-0.000, +0.000] |
| timeline_strict_first_effect__after | +0.003 [+0.000, +0.007] |
| timeline_strict_first_effect__before_neutral | +0.639 [+0.501, +0.771] |
| timeline_strict_first_effect__before_confirm | -0.011 [-0.034, +0.002] |
| timeline_strict_first_effect__before_cancel | +0.132 [+0.027, +0.237] |
| timeline_strict_first_effect__nontemporal_neutral | -0.000 [-0.000, -0.000] |
| topic_mc_first_effect__after | -0.128 [-0.190, -0.072] |
| topic_mc_first_effect__before_neutral | -0.043 [-0.096, -0.004] |
| topic_mc_first_effect__before_confirm | -0.254 [-0.371, -0.140] |
| topic_mc_first_effect__before_cancel | +0.010 [-0.000, +0.029] |
| topic_mc_first_effect__nontemporal_neutral | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__after | -0.000 [-0.000, -0.000] |
| timeline_minus_paraphrase__before_neutral | +0.334 [+0.225, +0.444] |
| timeline_minus_paraphrase__before_confirm | +0.030 [-0.018, +0.092] |
| timeline_minus_paraphrase__before_cancel | +0.049 [+0.002, +0.119] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.000 [-0.000, +0.000] |
| timeline_specificity_vs_nontemporal | +0.334 [+0.227, +0.448] |
| timeline_specificity_vs_after | +0.334 [+0.225, +0.446] |
| order_minus_topic_mc__after | +0.114 [+0.062, +0.171] |
| order_minus_topic_mc__before_neutral | +0.015 [+0.004, +0.029] |
| order_minus_topic_mc__before_confirm | +0.147 [+0.044, +0.256] |
| order_minus_topic_mc__before_cancel | -0.010 [-0.029, -0.000] |
| order_minus_topic_mc__nontemporal_neutral | +0.017 [+0.000, +0.047] |
| strict_minus_open_timeline__after | +0.000 [+0.000, +0.000] |
| strict_minus_open_timeline__before_neutral | +0.236 [+0.085, +0.380] |
| strict_minus_open_timeline__before_confirm | -0.013 [-0.086, +0.051] |
| strict_minus_open_timeline__before_cancel | +0.058 [+0.000, +0.133] |
| strict_minus_open_timeline__nontemporal_neutral | -0.000 [-0.000, -0.000] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.862 [4.743, 4.958] |
| before_neutral | 2.366 [2.067, 2.693] |
| before_confirm | 4.773 [4.520, 4.962] |
| before_cancel | 1.081 [1.002, 1.210] |
| nontemporal_neutral | 2.175 [1.919, 2.451] |

## qwen3_32b (qwen3), 38 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.999 | 0.000 | 0.001 | 1.000 |
| before_neutral | 0.248 | 0.619 | 0.133 | 0.053 |
| before_confirm | 0.961 | 0.017 | 0.022 | 0.947 |
| before_cancel | 0.024 | 0.975 | 0.001 | 0.974 |
| nontemporal_neutral | 0.022 | 0.362 | 0.616 | 0.632 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.226 [+0.131, +0.332] |
| veridicality_gap | +0.751 [+0.640, +0.853] |
| confirm_update | +0.713 [+0.587, +0.831] |
| cancel_update | +0.225 [+0.127, +0.329] |
| gold_update_confirm | +0.713 [+0.584, +0.828] |
| gold_update_cancel | +0.356 [+0.229, +0.486] |
| gold_update_asymmetry | +0.357 [+0.119, +0.579] |
| update_asymmetry | +0.513 [+0.311, +0.701] |
| paraphrase_first_effect__after | -0.002 [-0.005, +0.001] |
| paraphrase_first_effect__before_neutral | +0.017 [-0.086, +0.111] |
| paraphrase_first_effect__before_confirm | +0.025 [+0.000, +0.063] |
| paraphrase_first_effect__before_cancel | +0.002 [-0.000, +0.007] |
| paraphrase_first_effect__nontemporal_neutral | -0.013 [-0.026, -0.002] |
| schema_timeline_first_effect__after | +0.001 [+0.000, +0.001] |
| schema_timeline_first_effect__before_neutral | -0.196 [-0.292, -0.109] |
| schema_timeline_first_effect__before_confirm | -0.119 [-0.221, -0.034] |
| schema_timeline_first_effect__before_cancel | -0.024 [-0.071, -0.000] |
| schema_timeline_first_effect__nontemporal_neutral | -0.022 [-0.052, -0.003] |
| timeline_first_effect__after | +0.001 [+0.000, +0.001] |
| timeline_first_effect__before_neutral | +0.358 [+0.247, +0.475] |
| timeline_first_effect__before_confirm | -0.004 [-0.058, +0.049] |
| timeline_first_effect__before_cancel | +0.011 [+0.000, +0.031] |
| timeline_first_effect__nontemporal_neutral | -0.022 [-0.050, -0.003] |
| timeline_minus_paraphrase__after | +0.002 [+0.000, +0.006] |
| timeline_minus_paraphrase__before_neutral | +0.341 [+0.223, +0.465] |
| timeline_minus_paraphrase__before_confirm | -0.029 [-0.090, +0.015] |
| timeline_minus_paraphrase__before_cancel | +0.008 [-0.005, +0.030] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.009 [-0.026, -0.000] |
| timeline_specificity_vs_nontemporal | +0.350 [+0.231, +0.476] |
| timeline_specificity_vs_after | +0.339 [+0.221, +0.462] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.981 [4.969, 4.990] |
| before_neutral | 2.393 [1.907, 2.903] |
| before_confirm | 4.888 [4.739, 4.977] |
| before_cancel | 1.041 [1.001, 1.115] |
| nontemporal_neutral | 2.194 [1.849, 2.550] |
