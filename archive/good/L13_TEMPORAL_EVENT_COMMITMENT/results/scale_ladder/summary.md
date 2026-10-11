# L13 summary — scale_ladder

## qwen3_0_6b (qwen3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.344 | 0.255 | 0.401 | 0.025 |
| before_neutral | 0.323 | 0.290 | 0.387 | 0.975 |
| before_confirm | 0.354 | 0.250 | 0.396 | 0.050 |
| before_cancel | 0.310 | 0.327 | 0.364 | 0.025 |
| nontemporal_neutral | 0.326 | 0.288 | 0.386 | 1.000 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | -0.003 [-0.007, +0.002] |
| veridicality_gap | +0.021 [+0.017, +0.026] |
| confirm_update | +0.031 [+0.024, +0.038] |
| cancel_update | +0.013 [+0.009, +0.018] |
| gold_update_confirm | +0.031 [+0.024, +0.038] |
| gold_update_cancel | +0.037 [+0.031, +0.043] |
| gold_update_asymmetry | -0.006 [-0.017, +0.005] |
| update_asymmetry | +0.017 [+0.010, +0.025] |
| paraphrase_first_effect__after | -0.273 [-0.288, -0.257] |
| paraphrase_first_effect__before_neutral | -0.279 [-0.289, -0.267] |
| paraphrase_first_effect__before_confirm | -0.240 [-0.258, -0.221] |
| paraphrase_first_effect__before_cancel | -0.280 [-0.285, -0.274] |
| paraphrase_first_effect__nontemporal_neutral | -0.262 [-0.272, -0.251] |
| timeline_first_effect__after | -0.124 [-0.148, -0.101] |
| timeline_first_effect__before_neutral | -0.157 [-0.192, -0.119] |
| timeline_first_effect__before_confirm | -0.079 [-0.114, -0.043] |
| timeline_first_effect__before_cancel | -0.258 [-0.272, -0.240] |
| timeline_first_effect__nontemporal_neutral | -0.173 [-0.196, -0.150] |
| timeline_minus_paraphrase__after | +0.149 [+0.122, +0.175] |
| timeline_minus_paraphrase__before_neutral | +0.122 [+0.085, +0.163] |
| timeline_minus_paraphrase__before_confirm | +0.161 [+0.130, +0.192] |
| timeline_minus_paraphrase__before_cancel | +0.022 [+0.009, +0.041] |
| timeline_minus_paraphrase__nontemporal_neutral | +0.089 [+0.070, +0.108] |
| timeline_specificity_vs_nontemporal | +0.033 [-0.006, +0.076] |
| timeline_specificity_vs_after | -0.027 [-0.067, +0.017] |

| condition | E[rating 1-5] |
|---|---|
| after | 3.341 [3.280, 3.396] |
| before_neutral | 3.210 [3.125, 3.293] |
| before_confirm | 3.530 [3.446, 3.612] |
| before_cancel | 3.096 [2.989, 3.205] |
| nontemporal_neutral | 3.262 [3.166, 3.358] |

## qwen3_1_7b (qwen3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.992 | 0.000 | 0.008 | 1.000 |
| before_neutral | 0.231 | 0.152 | 0.617 | 0.725 |
| before_confirm | 0.870 | 0.018 | 0.112 | 0.925 |
| before_cancel | 0.090 | 0.596 | 0.314 | 0.725 |
| nontemporal_neutral | 0.162 | 0.061 | 0.777 | 0.825 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.069 [-0.016, +0.148] |
| veridicality_gap | +0.761 [+0.676, +0.841] |
| confirm_update | +0.639 [+0.550, +0.726] |
| cancel_update | +0.141 [+0.061, +0.230] |
| gold_update_confirm | +0.639 [+0.546, +0.727] |
| gold_update_cancel | +0.444 [+0.362, +0.524] |
| gold_update_asymmetry | +0.195 [+0.067, +0.315] |
| update_asymmetry | +0.454 [+0.298, +0.597] |
| paraphrase_first_effect__after | -0.020 [-0.039, -0.004] |
| paraphrase_first_effect__before_neutral | +0.531 [+0.455, +0.607] |
| paraphrase_first_effect__before_confirm | +0.114 [+0.058, +0.183] |
| paraphrase_first_effect__before_cancel | +0.213 [+0.141, +0.293] |
| paraphrase_first_effect__nontemporal_neutral | +0.234 [+0.147, +0.325] |
| timeline_first_effect__after | +0.008 [+0.001, +0.016] |
| timeline_first_effect__before_neutral | +0.690 [+0.599, +0.777] |
| timeline_first_effect__before_confirm | +0.130 [+0.064, +0.209] |
| timeline_first_effect__before_cancel | +0.198 [+0.113, +0.294] |
| timeline_first_effect__nontemporal_neutral | +0.448 [+0.354, +0.545] |
| timeline_minus_paraphrase__after | +0.028 [+0.010, +0.049] |
| timeline_minus_paraphrase__before_neutral | +0.159 [+0.066, +0.250] |
| timeline_minus_paraphrase__before_confirm | +0.016 [+0.000, +0.035] |
| timeline_minus_paraphrase__before_cancel | -0.016 [-0.097, +0.063] |
| timeline_minus_paraphrase__nontemporal_neutral | +0.214 [+0.132, +0.302] |
| timeline_specificity_vs_nontemporal | -0.055 [-0.199, +0.085] |
| timeline_specificity_vs_after | +0.132 [+0.043, +0.217] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.000 [4.000, 4.000] |
| before_neutral | 4.000 [4.000, 4.000] |
| before_confirm | 4.000 [4.000, 4.000] |
| before_cancel | 3.997 [3.991, 4.000] |
| nontemporal_neutral | 3.996 [3.989, 4.000] |

## qwen3_4b (qwen3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 1.000 | 0.000 | 0.000 | 1.000 |
| before_neutral | 0.172 | 0.133 | 0.695 | 0.750 |
| before_confirm | 0.862 | 0.028 | 0.110 | 0.875 |
| before_cancel | 0.005 | 0.904 | 0.091 | 0.925 |
| nontemporal_neutral | 0.049 | 0.185 | 0.766 | 0.800 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.122 [+0.043, +0.206] |
| veridicality_gap | +0.828 [+0.744, +0.905] |
| confirm_update | +0.690 [+0.575, +0.799] |
| cancel_update | +0.167 [+0.092, +0.250] |
| gold_update_confirm | +0.690 [+0.573, +0.799] |
| gold_update_cancel | +0.771 [+0.698, +0.840] |
| gold_update_asymmetry | -0.081 [-0.215, +0.046] |
| update_asymmetry | +0.545 [+0.382, +0.701] |
| paraphrase_first_effect__after | -0.013 [-0.034, -0.001] |
| paraphrase_first_effect__before_neutral | +0.096 [-0.009, +0.200] |
| paraphrase_first_effect__before_confirm | +0.101 [+0.028, +0.194] |
| paraphrase_first_effect__before_cancel | +0.050 [+0.007, +0.105] |
| paraphrase_first_effect__nontemporal_neutral | -0.006 [-0.042, +0.020] |
| timeline_first_effect__after | +0.000 [+0.000, +0.000] |
| timeline_first_effect__before_neutral | +0.475 [+0.369, +0.580] |
| timeline_first_effect__before_confirm | +0.096 [+0.028, +0.181] |
| timeline_first_effect__before_cancel | +0.138 [+0.050, +0.243] |
| timeline_first_effect__nontemporal_neutral | -0.048 [-0.100, -0.006] |
| timeline_minus_paraphrase__after | +0.014 [+0.001, +0.033] |
| timeline_minus_paraphrase__before_neutral | +0.379 [+0.275, +0.486] |
| timeline_minus_paraphrase__before_confirm | -0.005 [-0.051, +0.036] |
| timeline_minus_paraphrase__before_cancel | +0.089 [+0.003, +0.190] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.041 [-0.092, -0.001] |
| timeline_specificity_vs_nontemporal | +0.421 [+0.305, +0.540] |
| timeline_specificity_vs_after | +0.366 [+0.260, +0.475] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.705 [4.601, 4.801] |
| before_neutral | 2.959 [2.714, 3.208] |
| before_confirm | 4.418 [4.171, 4.632] |
| before_cancel | 1.486 [1.329, 1.647] |
| nontemporal_neutral | 2.305 [2.096, 2.535] |

## qwen3_14b (qwen3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 1.000 | 0.000 | 0.000 | 1.000 |
| before_neutral | 0.001 | 0.302 | 0.696 | 0.825 |
| before_confirm | 0.926 | 0.027 | 0.048 | 0.925 |
| before_cancel | 0.000 | 0.951 | 0.049 | 0.950 |
| nontemporal_neutral | 0.000 | 0.141 | 0.859 | 0.900 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.001 [+0.000, +0.002] |
| veridicality_gap | +0.999 [+0.998, +1.000] |
| confirm_update | +0.925 [+0.827, +0.999] |
| cancel_update | +0.001 [+0.000, +0.002] |
| gold_update_confirm | +0.925 [+0.827, +0.999] |
| gold_update_cancel | +0.648 [+0.535, +0.754] |
| gold_update_asymmetry | +0.277 [+0.143, +0.407] |
| update_asymmetry | +0.923 [+0.826, +0.998] |
| paraphrase_first_effect__after | -0.025 [-0.075, +0.000] |
| paraphrase_first_effect__before_neutral | +0.257 [+0.136, +0.389] |
| paraphrase_first_effect__before_confirm | +0.019 [-0.060, +0.100] |
| paraphrase_first_effect__before_cancel | +0.024 [-0.000, +0.070] |
| paraphrase_first_effect__nontemporal_neutral | -0.000 [-0.000, -0.000] |
| timeline_first_effect__after | +0.000 [+0.000, +0.000] |
| timeline_first_effect__before_neutral | +0.550 [+0.423, +0.673] |
| timeline_first_effect__before_confirm | +0.008 [-0.082, +0.098] |
| timeline_first_effect__before_cancel | +0.051 [+0.005, +0.115] |
| timeline_first_effect__nontemporal_neutral | -0.000 [-0.000, -0.000] |
| timeline_minus_paraphrase__after | +0.025 [+0.000, +0.075] |
| timeline_minus_paraphrase__before_neutral | +0.293 [+0.146, +0.442] |
| timeline_minus_paraphrase__before_confirm | -0.011 [-0.078, +0.057] |
| timeline_minus_paraphrase__before_cancel | +0.027 [-0.027, +0.090] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.000 [-0.000, -0.000] |
| timeline_specificity_vs_nontemporal | +0.293 [+0.145, +0.440] |
| timeline_specificity_vs_after | +0.268 [+0.108, +0.427] |

| condition | E[rating 1-5] |
|---|---|
| after | 5.000 [5.000, 5.000] |
| before_neutral | 1.915 [1.670, 2.159] |
| before_confirm | 4.815 [4.540, 4.999] |
| before_cancel | 1.015 [1.000, 1.043] |
| nontemporal_neutral | 1.817 [1.603, 2.039] |
