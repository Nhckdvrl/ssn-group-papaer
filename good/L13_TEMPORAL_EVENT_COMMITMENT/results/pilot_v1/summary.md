# L13 summary — pilot_v1

## qwen3_8b (qwen3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.989 | 0.003 | 0.009 | 1.000 |
| before_neutral | 0.028 | 0.220 | 0.752 | 0.900 |
| before_confirm | 0.903 | 0.022 | 0.074 | 0.925 |
| before_cancel | 0.003 | 0.857 | 0.140 | 0.900 |
| nontemporal_neutral | 0.023 | 0.147 | 0.830 | 0.900 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.005 [-0.041, +0.050] |
| veridicality_gap | +0.961 [+0.926, +0.989] |
| confirm_update | +0.875 [+0.781, +0.954] |
| cancel_update | +0.025 [+0.002, +0.057] |
| gold_update_confirm | +0.875 [+0.782, +0.955] |
| gold_update_cancel | +0.637 [+0.561, +0.714] |
| gold_update_asymmetry | +0.238 [+0.128, +0.338] |
| update_asymmetry | +0.850 [+0.746, +0.941] |
| order_mc_first_effect__after | -0.066 [-0.145, -0.005] |
| order_mc_first_effect__before_neutral | -0.004 [-0.037, +0.030] |
| order_mc_first_effect__before_confirm | +0.037 [-0.001, +0.097] |
| order_mc_first_effect__before_cancel | +0.005 [-0.001, +0.015] |
| order_mc_first_effect__nontemporal_neutral | -0.023 [-0.058, -0.000] |
| paraphrase_first_effect__after | +0.011 [+0.002, +0.025] |
| paraphrase_first_effect__before_neutral | -0.022 [-0.057, +0.003] |
| paraphrase_first_effect__before_confirm | -0.003 [-0.037, +0.028] |
| paraphrase_first_effect__before_cancel | -0.003 [-0.009, -0.000] |
| paraphrase_first_effect__nontemporal_neutral | -0.023 [-0.058, -0.000] |
| schema_timeline_first_effect__after | +0.011 [+0.002, +0.025] |
| schema_timeline_first_effect__before_neutral | +0.162 [+0.072, +0.263] |
| schema_timeline_first_effect__before_confirm | -0.028 [-0.120, +0.058] |
| schema_timeline_first_effect__before_cancel | +0.022 [-0.008, +0.075] |
| schema_timeline_first_effect__nontemporal_neutral | -0.023 [-0.057, -0.000] |
| timeline_first_effect__after | +0.011 [+0.002, +0.024] |
| timeline_first_effect__before_neutral | +0.149 [+0.047, +0.261] |
| timeline_first_effect__before_confirm | -0.021 [-0.060, +0.010] |
| timeline_first_effect__before_cancel | +0.026 [-0.006, +0.079] |
| timeline_first_effect__nontemporal_neutral | -0.023 [-0.058, -0.000] |
| timeline_strict_first_effect__after | +0.011 [+0.002, +0.025] |
| timeline_strict_first_effect__before_neutral | +0.089 [-0.000, +0.191] |
| timeline_strict_first_effect__before_confirm | +0.005 [-0.041, +0.067] |
| timeline_strict_first_effect__before_cancel | +0.012 [-0.008, +0.046] |
| timeline_strict_first_effect__nontemporal_neutral | -0.023 [-0.058, -0.000] |
| topic_mc_first_effect__after | -0.145 [-0.242, -0.061] |
| topic_mc_first_effect__before_neutral | -0.024 [-0.053, -0.002] |
| topic_mc_first_effect__before_confirm | -0.071 [-0.139, -0.016] |
| topic_mc_first_effect__before_cancel | -0.003 [-0.009, -0.000] |
| topic_mc_first_effect__nontemporal_neutral | -0.023 [-0.058, -0.000] |
| unordered_first_effect__after | +0.011 [+0.002, +0.024] |
| unordered_first_effect__before_neutral | +0.186 [+0.092, +0.290] |
| unordered_first_effect__before_confirm | +0.023 [-0.023, +0.085] |
| unordered_first_effect__before_cancel | +0.014 [-0.000, +0.039] |
| unordered_first_effect__nontemporal_neutral | -0.023 [-0.058, -0.000] |
| timeline_minus_paraphrase__after | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__before_neutral | +0.171 [+0.081, +0.272] |
| timeline_minus_paraphrase__before_confirm | -0.017 [-0.071, +0.016] |
| timeline_minus_paraphrase__before_cancel | +0.029 [+0.000, +0.080] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.000 [-0.000, -0.000] |
| timeline_specificity_vs_nontemporal | +0.171 [+0.082, +0.274] |
| timeline_specificity_vs_after | +0.171 [+0.084, +0.272] |
| order_minus_topic_mc__after | +0.079 [+0.022, +0.149] |
| order_minus_topic_mc__before_neutral | +0.020 [+0.001, +0.054] |
| order_minus_topic_mc__before_confirm | +0.108 [+0.038, +0.192] |
| order_minus_topic_mc__before_cancel | +0.008 [+0.000, +0.023] |
| order_minus_topic_mc__nontemporal_neutral | +0.000 [-0.000, +0.000] |
| strict_minus_open_timeline__after | -0.000 [-0.000, +0.000] |
| strict_minus_open_timeline__before_neutral | -0.059 [-0.161, +0.029] |
| strict_minus_open_timeline__before_confirm | +0.026 [-0.002, +0.072] |
| strict_minus_open_timeline__before_cancel | -0.013 [-0.034, -0.000] |
| strict_minus_open_timeline__nontemporal_neutral | +0.000 [+0.000, +0.000] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.532 [4.424, 4.637] |
| before_neutral | 2.053 [1.838, 2.279] |
| before_confirm | 4.377 [4.158, 4.566] |
| before_cancel | 1.121 [1.052, 1.208] |
| nontemporal_neutral | 2.079 [1.846, 2.326] |

## llama31_8b_instruct (llama3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.654 | 0.055 | 0.291 | 0.925 |
| before_neutral | 0.182 | 0.224 | 0.594 | 0.875 |
| before_confirm | 0.523 | 0.048 | 0.428 | 0.575 |
| before_cancel | 0.079 | 0.519 | 0.402 | 0.625 |
| nontemporal_neutral | 0.074 | 0.149 | 0.777 | 0.975 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.108 [+0.080, +0.138] |
| veridicality_gap | +0.472 [+0.432, +0.511] |
| confirm_update | +0.341 [+0.302, +0.380] |
| cancel_update | +0.103 [+0.071, +0.141] |
| gold_update_confirm | +0.341 [+0.302, +0.382] |
| gold_update_cancel | +0.296 [+0.237, +0.354] |
| gold_update_asymmetry | +0.045 [-0.023, +0.114] |
| update_asymmetry | +0.231 [+0.176, +0.282] |
| order_mc_first_effect__after | +0.098 [+0.067, +0.132] |
| order_mc_first_effect__before_neutral | -0.084 [-0.109, -0.060] |
| order_mc_first_effect__before_confirm | -0.048 [-0.093, -0.003] |
| order_mc_first_effect__before_cancel | -0.053 [-0.067, -0.041] |
| order_mc_first_effect__nontemporal_neutral | -0.032 [-0.047, -0.019] |
| paraphrase_first_effect__after | -0.096 [-0.129, -0.064] |
| paraphrase_first_effect__before_neutral | -0.148 [-0.174, -0.124] |
| paraphrase_first_effect__before_confirm | -0.238 [-0.264, -0.209] |
| paraphrase_first_effect__before_cancel | -0.076 [-0.094, -0.060] |
| paraphrase_first_effect__nontemporal_neutral | -0.066 [-0.086, -0.050] |
| schema_timeline_first_effect__after | +0.340 [+0.305, +0.376] |
| schema_timeline_first_effect__before_neutral | +0.442 [+0.338, +0.538] |
| schema_timeline_first_effect__before_confirm | +0.381 [+0.331, +0.428] |
| schema_timeline_first_effect__before_cancel | +0.071 [+0.024, +0.129] |
| schema_timeline_first_effect__nontemporal_neutral | +0.070 [+0.036, +0.107] |
| timeline_first_effect__after | +0.006 [-0.025, +0.036] |
| timeline_first_effect__before_neutral | -0.051 [-0.077, -0.025] |
| timeline_first_effect__before_confirm | -0.168 [-0.199, -0.136] |
| timeline_first_effect__before_cancel | -0.033 [-0.052, -0.012] |
| timeline_first_effect__nontemporal_neutral | -0.064 [-0.084, -0.048] |
| timeline_strict_first_effect__after | +0.027 [-0.008, +0.063] |
| timeline_strict_first_effect__before_neutral | -0.059 [-0.082, -0.037] |
| timeline_strict_first_effect__before_confirm | -0.042 [-0.086, +0.001] |
| timeline_strict_first_effect__before_cancel | -0.058 [-0.073, -0.044] |
| timeline_strict_first_effect__nontemporal_neutral | -0.062 [-0.081, -0.045] |
| topic_mc_first_effect__after | -0.051 [-0.093, -0.012] |
| topic_mc_first_effect__before_neutral | -0.064 [-0.089, -0.042] |
| topic_mc_first_effect__before_confirm | -0.063 [-0.106, -0.020] |
| topic_mc_first_effect__before_cancel | -0.062 [-0.078, -0.047] |
| topic_mc_first_effect__nontemporal_neutral | +0.009 [-0.006, +0.022] |
| unordered_first_effect__after | -0.019 [-0.049, +0.012] |
| unordered_first_effect__before_neutral | -0.066 [-0.086, -0.046] |
| unordered_first_effect__before_confirm | -0.157 [-0.190, -0.124] |
| unordered_first_effect__before_cancel | -0.053 [-0.068, -0.040] |
| unordered_first_effect__nontemporal_neutral | -0.067 [-0.086, -0.050] |
| timeline_minus_paraphrase__after | +0.101 [+0.079, +0.124] |
| timeline_minus_paraphrase__before_neutral | +0.098 [+0.075, +0.121] |
| timeline_minus_paraphrase__before_confirm | +0.070 [+0.046, +0.095] |
| timeline_minus_paraphrase__before_cancel | +0.043 [+0.022, +0.070] |
| timeline_minus_paraphrase__nontemporal_neutral | +0.002 [+0.001, +0.004] |
| timeline_specificity_vs_nontemporal | +0.095 [+0.073, +0.119] |
| timeline_specificity_vs_after | -0.004 [-0.036, +0.031] |
| order_minus_topic_mc__after | +0.149 [+0.112, +0.187] |
| order_minus_topic_mc__before_neutral | -0.019 [-0.036, -0.003] |
| order_minus_topic_mc__before_confirm | +0.015 [-0.022, +0.051] |
| order_minus_topic_mc__before_cancel | +0.009 [+0.001, +0.019] |
| order_minus_topic_mc__nontemporal_neutral | -0.041 [-0.053, -0.030] |
| strict_minus_open_timeline__after | +0.021 [-0.006, +0.049] |
| strict_minus_open_timeline__before_neutral | -0.009 [-0.031, +0.012] |
| strict_minus_open_timeline__before_confirm | +0.126 [+0.086, +0.164] |
| strict_minus_open_timeline__before_cancel | -0.025 [-0.043, -0.011] |
| strict_minus_open_timeline__nontemporal_neutral | +0.002 [-0.000, +0.005] |

| condition | E[rating 1-5] |
|---|---|
| after | 3.842 [3.789, 3.897] |
| before_neutral | 3.415 [3.351, 3.481] |
| before_confirm | 3.724 [3.678, 3.770] |
| before_cancel | 2.864 [2.763, 2.966] |
| nontemporal_neutral | 3.315 [3.250, 3.384] |

## olmo3_7b_instruct_dpo (olmo3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.549 | 0.219 | 0.232 | 0.675 |
| before_neutral | 0.009 | 0.728 | 0.263 | 0.125 |
| before_confirm | 0.732 | 0.153 | 0.114 | 0.825 |
| before_cancel | 0.003 | 0.950 | 0.048 | 1.000 |
| nontemporal_neutral | 0.026 | 0.648 | 0.326 | 0.175 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | -0.017 [-0.050, +0.001] |
| veridicality_gap | +0.540 [+0.432, +0.643] |
| confirm_update | +0.724 [+0.612, +0.828] |
| cancel_update | +0.006 [+0.003, +0.010] |
| gold_update_confirm | +0.724 [+0.609, +0.826] |
| gold_update_cancel | +0.222 [+0.167, +0.279] |
| gold_update_asymmetry | +0.502 [+0.402, +0.596] |
| update_asymmetry | +0.716 [+0.606, +0.818] |
| order_mc_first_effect__after | +0.185 [+0.058, +0.306] |
| order_mc_first_effect__before_neutral | +0.098 [+0.066, +0.134] |
| order_mc_first_effect__before_confirm | +0.029 [-0.036, +0.099] |
| order_mc_first_effect__before_cancel | +0.064 [+0.028, +0.110] |
| order_mc_first_effect__nontemporal_neutral | +0.020 [-0.007, +0.043] |
| paraphrase_first_effect__after | +0.049 [-0.074, +0.171] |
| paraphrase_first_effect__before_neutral | +0.050 [+0.035, +0.068] |
| paraphrase_first_effect__before_confirm | -0.422 [-0.512, -0.327] |
| paraphrase_first_effect__before_cancel | +0.009 [+0.005, +0.016] |
| paraphrase_first_effect__nontemporal_neutral | +0.003 [-0.017, +0.015] |
| schema_timeline_first_effect__after | +0.404 [+0.291, +0.519] |
| schema_timeline_first_effect__before_neutral | +0.382 [+0.268, +0.499] |
| schema_timeline_first_effect__before_confirm | +0.134 [+0.057, +0.217] |
| schema_timeline_first_effect__before_cancel | +0.068 [+0.035, +0.117] |
| schema_timeline_first_effect__nontemporal_neutral | +0.023 [+0.004, +0.039] |
| timeline_first_effect__after | +0.261 [+0.139, +0.381] |
| timeline_first_effect__before_neutral | +0.124 [+0.066, +0.196] |
| timeline_first_effect__before_confirm | -0.080 [-0.171, +0.013] |
| timeline_first_effect__before_cancel | +0.037 [+0.007, +0.078] |
| timeline_first_effect__nontemporal_neutral | -0.015 [-0.044, +0.001] |
| timeline_strict_first_effect__after | +0.404 [+0.304, +0.506] |
| timeline_strict_first_effect__before_neutral | +0.189 [+0.114, +0.276] |
| timeline_strict_first_effect__before_confirm | +0.014 [-0.082, +0.114] |
| timeline_strict_first_effect__before_cancel | +0.044 [+0.005, +0.098] |
| timeline_strict_first_effect__nontemporal_neutral | -0.015 [-0.047, +0.002] |
| topic_mc_first_effect__after | -0.384 [-0.486, -0.277] |
| topic_mc_first_effect__before_neutral | +0.026 [+0.021, +0.031] |
| topic_mc_first_effect__before_confirm | -0.407 [-0.503, -0.313] |
| topic_mc_first_effect__before_cancel | +0.027 [+0.018, +0.037] |
| topic_mc_first_effect__nontemporal_neutral | -0.002 [-0.038, +0.018] |
| timeline_minus_paraphrase__after | +0.212 [+0.110, +0.312] |
| timeline_minus_paraphrase__before_neutral | +0.075 [+0.019, +0.144] |
| timeline_minus_paraphrase__before_confirm | +0.343 [+0.256, +0.425] |
| timeline_minus_paraphrase__before_cancel | +0.028 [+0.002, +0.063] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.018 [-0.032, -0.008] |
| timeline_specificity_vs_nontemporal | +0.092 [+0.032, +0.169] |
| timeline_specificity_vs_after | -0.137 [-0.265, -0.009] |
| order_minus_topic_mc__after | +0.569 [+0.482, +0.650] |
| order_minus_topic_mc__before_neutral | +0.072 [+0.041, +0.107] |
| order_minus_topic_mc__before_confirm | +0.437 [+0.358, +0.515] |
| order_minus_topic_mc__before_cancel | +0.037 [+0.006, +0.078] |
| order_minus_topic_mc__nontemporal_neutral | +0.022 [+0.004, +0.044] |
| strict_minus_open_timeline__after | +0.143 [+0.090, +0.202] |
| strict_minus_open_timeline__before_neutral | +0.065 [+0.013, +0.124] |
| strict_minus_open_timeline__before_confirm | +0.094 [+0.016, +0.174] |
| strict_minus_open_timeline__before_cancel | +0.006 [-0.015, +0.030] |
| strict_minus_open_timeline__nontemporal_neutral | -0.001 [-0.004, +0.002] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.413 [4.149, 4.654] |
| before_neutral | 2.055 [1.803, 2.317] |
| before_confirm | 4.529 [4.213, 4.791] |
| before_cancel | 1.213 [1.099, 1.348] |
| nontemporal_neutral | 1.927 [1.676, 2.202] |

## gemma3_12b_it (gemma3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.997 | 0.000 | 0.003 | 1.000 |
| before_neutral | 0.045 | 0.091 | 0.864 | 0.850 |
| before_confirm | 0.891 | 0.012 | 0.097 | 0.900 |
| before_cancel | 0.000 | 0.913 | 0.087 | 0.925 |
| nontemporal_neutral | 0.000 | 0.097 | 0.903 | 0.900 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.045 [+0.004, +0.101] |
| veridicality_gap | +0.952 [+0.896, +0.993] |
| confirm_update | +0.846 [+0.736, +0.939] |
| cancel_update | +0.045 [+0.004, +0.104] |
| gold_update_confirm | +0.846 [+0.737, +0.939] |
| gold_update_cancel | +0.822 [+0.710, +0.916] |
| gold_update_asymmetry | +0.024 [-0.118, +0.172] |
| update_asymmetry | +0.801 [+0.660, +0.921] |
| order_mc_first_effect__after | -0.029 [-0.059, -0.005] |
| order_mc_first_effect__before_neutral | -0.026 [-0.070, +0.008] |
| order_mc_first_effect__before_confirm | -0.102 [-0.190, -0.024] |
| order_mc_first_effect__before_cancel | -0.000 [-0.000, +0.000] |
| order_mc_first_effect__nontemporal_neutral | +0.016 [+0.000, +0.045] |
| paraphrase_first_effect__after | -0.001 [-0.011, +0.006] |
| paraphrase_first_effect__before_neutral | +0.066 [+0.031, +0.104] |
| paraphrase_first_effect__before_confirm | -0.026 [-0.064, +0.002] |
| paraphrase_first_effect__before_cancel | +0.024 [-0.000, +0.070] |
| paraphrase_first_effect__nontemporal_neutral | +0.000 [-0.000, +0.000] |
| schema_timeline_first_effect__after | +0.003 [+0.000, +0.007] |
| schema_timeline_first_effect__before_neutral | +0.430 [+0.288, +0.580] |
| schema_timeline_first_effect__before_confirm | +0.006 [-0.006, +0.025] |
| schema_timeline_first_effect__before_cancel | +0.050 [-0.000, +0.125] |
| schema_timeline_first_effect__nontemporal_neutral | +0.069 [+0.019, +0.133] |
| timeline_first_effect__after | +0.003 [+0.000, +0.007] |
| timeline_first_effect__before_neutral | +0.397 [+0.277, +0.524] |
| timeline_first_effect__before_confirm | +0.002 [-0.051, +0.063] |
| timeline_first_effect__before_cancel | +0.070 [+0.003, +0.152] |
| timeline_first_effect__nontemporal_neutral | -0.000 [-0.000, +0.000] |
| timeline_strict_first_effect__after | +0.003 [+0.000, +0.007] |
| timeline_strict_first_effect__before_neutral | +0.632 [+0.493, +0.763] |
| timeline_strict_first_effect__before_confirm | -0.010 [-0.032, +0.002] |
| timeline_strict_first_effect__before_cancel | +0.125 [+0.026, +0.226] |
| timeline_strict_first_effect__nontemporal_neutral | -0.000 [-0.000, -0.000] |
| topic_mc_first_effect__after | -0.150 [-0.225, -0.085] |
| topic_mc_first_effect__before_neutral | -0.041 [-0.092, -0.004] |
| topic_mc_first_effect__before_confirm | -0.266 [-0.384, -0.151] |
| topic_mc_first_effect__before_cancel | +0.009 [-0.000, +0.028] |
| topic_mc_first_effect__nontemporal_neutral | +0.000 [+0.000, +0.000] |
| unordered_first_effect__after | +0.003 [+0.000, +0.006] |
| unordered_first_effect__before_neutral | +0.477 [+0.345, +0.613] |
| unordered_first_effect__before_confirm | +0.026 [-0.037, +0.096] |
| unordered_first_effect__before_cancel | +0.125 [+0.025, +0.225] |
| unordered_first_effect__nontemporal_neutral | -0.000 [-0.000, -0.000] |
| timeline_minus_paraphrase__after | +0.004 [-0.000, +0.013] |
| timeline_minus_paraphrase__before_neutral | +0.332 [+0.224, +0.442] |
| timeline_minus_paraphrase__before_confirm | +0.028 [-0.018, +0.086] |
| timeline_minus_paraphrase__before_cancel | +0.046 [+0.002, +0.113] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.000 [-0.000, +0.000] |
| timeline_specificity_vs_nontemporal | +0.332 [+0.226, +0.440] |
| timeline_specificity_vs_after | +0.328 [+0.224, +0.438] |
| order_minus_topic_mc__after | +0.121 [+0.065, +0.185] |
| order_minus_topic_mc__before_neutral | +0.014 [+0.003, +0.028] |
| order_minus_topic_mc__before_confirm | +0.164 [+0.057, +0.280] |
| order_minus_topic_mc__before_cancel | -0.009 [-0.028, -0.000] |
| order_minus_topic_mc__nontemporal_neutral | +0.016 [+0.000, +0.045] |
| strict_minus_open_timeline__after | +0.000 [+0.000, +0.000] |
| strict_minus_open_timeline__before_neutral | +0.234 [+0.089, +0.370] |
| strict_minus_open_timeline__before_confirm | -0.012 [-0.083, +0.049] |
| strict_minus_open_timeline__before_cancel | +0.055 [+0.000, +0.127] |
| strict_minus_open_timeline__nontemporal_neutral | -0.000 [-0.000, -0.000] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.770 [4.574, 4.919] |
| before_neutral | 2.323 [2.022, 2.645] |
| before_confirm | 4.709 [4.435, 4.924] |
| before_cancel | 1.078 [1.003, 1.200] |
| nontemporal_neutral | 2.142 [1.888, 2.420] |

## qwen3_32b (qwen3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.999 | 0.000 | 0.001 | 1.000 |
| before_neutral | 0.236 | 0.638 | 0.126 | 0.050 |
| before_confirm | 0.963 | 0.016 | 0.021 | 0.950 |
| before_cancel | 0.022 | 0.976 | 0.001 | 0.975 |
| nontemporal_neutral | 0.021 | 0.394 | 0.586 | 0.600 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.215 [+0.123, +0.314] |
| veridicality_gap | +0.763 [+0.659, +0.858] |
| confirm_update | +0.727 [+0.603, +0.839] |
| cancel_update | +0.213 [+0.122, +0.316] |
| gold_update_confirm | +0.727 [+0.605, +0.836] |
| gold_update_cancel | +0.338 [+0.220, +0.472] |
| gold_update_asymmetry | +0.389 [+0.154, +0.609] |
| update_asymmetry | +0.537 [+0.337, +0.719] |
| paraphrase_first_effect__after | -0.002 [-0.005, +0.000] |
| paraphrase_first_effect__before_neutral | +0.016 [-0.082, +0.109] |
| paraphrase_first_effect__before_confirm | +0.013 [-0.020, +0.055] |
| paraphrase_first_effect__before_cancel | +0.002 [-0.000, +0.007] |
| paraphrase_first_effect__nontemporal_neutral | -0.012 [-0.025, -0.002] |
| schema_timeline_first_effect__after | +0.001 [+0.000, +0.001] |
| schema_timeline_first_effect__before_neutral | -0.186 [-0.279, -0.100] |
| schema_timeline_first_effect__before_confirm | -0.138 [-0.246, -0.048] |
| schema_timeline_first_effect__before_cancel | -0.022 [-0.067, -0.000] |
| schema_timeline_first_effect__nontemporal_neutral | -0.021 [-0.049, -0.003] |
| timeline_first_effect__after | +0.001 [+0.000, +0.001] |
| timeline_first_effect__before_neutral | +0.340 [+0.232, +0.455] |
| timeline_first_effect__before_confirm | -0.012 [-0.063, +0.038] |
| timeline_first_effect__before_cancel | +0.010 [+0.000, +0.030] |
| timeline_first_effect__nontemporal_neutral | -0.021 [-0.049, -0.003] |
| timeline_minus_paraphrase__after | +0.002 [+0.000, +0.006] |
| timeline_minus_paraphrase__before_neutral | +0.325 [+0.213, +0.445] |
| timeline_minus_paraphrase__before_confirm | -0.026 [-0.082, +0.016] |
| timeline_minus_paraphrase__before_cancel | +0.008 [-0.005, +0.028] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.009 [-0.025, -0.000] |
| timeline_specificity_vs_nontemporal | +0.333 [+0.220, +0.452] |
| timeline_specificity_vs_after | +0.322 [+0.207, +0.442] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.981 [4.969, 4.989] |
| before_neutral | 2.323 [1.854, 2.817] |
| before_confirm | 4.883 [4.736, 4.972] |
| before_cancel | 1.039 [1.001, 1.110] |
| nontemporal_neutral | 2.136 [1.806, 2.480] |
