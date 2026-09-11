# L13 summary — v2_core

## qwen3_8b (qwen3), 80 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.975 | 0.002 | 0.023 | 0.988 |
| before_neutral | 0.030 | 0.226 | 0.743 | 0.925 |
| before_confirm | 0.938 | 0.015 | 0.047 | 0.963 |
| before_cancel | 0.011 | 0.876 | 0.113 | 0.938 |
| nontemporal_neutral | 0.031 | 0.127 | 0.842 | 0.925 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | -0.001 [-0.033, +0.029] |
| veridicality_gap | +0.945 [+0.915, +0.970] |
| confirm_update | +0.907 [+0.857, +0.950] |
| cancel_update | +0.019 [-0.003, +0.042] |
| gold_update_confirm | +0.907 [+0.858, +0.950] |
| gold_update_cancel | +0.650 [+0.603, +0.695] |
| gold_update_asymmetry | +0.258 [+0.197, +0.315] |
| update_asymmetry | +0.870 [+0.813, +0.922] |
| paraphrase_first_effect__after | +0.025 [+0.005, +0.051] |
| paraphrase_first_effect__before_neutral | -0.011 [-0.035, +0.014] |
| paraphrase_first_effect__before_confirm | -0.013 [-0.048, +0.017] |
| paraphrase_first_effect__before_cancel | -0.008 [-0.023, -0.000] |
| paraphrase_first_effect__nontemporal_neutral | -0.026 [-0.052, -0.005] |
| timeline_first_effect__after | +0.025 [+0.005, +0.051] |
| timeline_first_effect__before_neutral | +0.140 [+0.067, +0.216] |
| timeline_first_effect__before_confirm | -0.021 [-0.059, +0.009] |
| timeline_first_effect__before_cancel | +0.003 [-0.021, +0.033] |
| timeline_first_effect__nontemporal_neutral | -0.031 [-0.058, -0.010] |
| timeline_minus_paraphrase__after | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__before_neutral | +0.150 [+0.078, +0.226] |
| timeline_minus_paraphrase__before_confirm | -0.009 [-0.035, +0.008] |
| timeline_minus_paraphrase__before_cancel | +0.011 [-0.005, +0.039] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.005 [-0.014, -0.000] |
| timeline_specificity_vs_nontemporal | +0.155 [+0.083, +0.232] |
| timeline_specificity_vs_after | +0.150 [+0.079, +0.226] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.437 [4.342, 4.528] |
| before_neutral | 2.102 [1.975, 2.240] |
| before_confirm | 4.393 [4.263, 4.509] |
| before_cancel | 1.156 [1.086, 1.242] |
| nontemporal_neutral | 2.182 [2.023, 2.353] |

## llama31_8b_instruct (llama3), 80 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.667 | 0.054 | 0.279 | 0.950 |
| before_neutral | 0.215 | 0.217 | 0.567 | 0.863 |
| before_confirm | 0.545 | 0.056 | 0.398 | 0.700 |
| before_cancel | 0.091 | 0.492 | 0.417 | 0.562 |
| nontemporal_neutral | 0.101 | 0.144 | 0.755 | 0.988 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.114 [+0.088, +0.141] |
| veridicality_gap | +0.452 [+0.424, +0.480] |
| confirm_update | +0.330 [+0.299, +0.361] |
| cancel_update | +0.125 [+0.099, +0.152] |
| gold_update_confirm | +0.330 [+0.298, +0.361] |
| gold_update_cancel | +0.275 [+0.239, +0.311] |
| gold_update_asymmetry | +0.055 [+0.010, +0.099] |
| update_asymmetry | +0.199 [+0.154, +0.242] |
| paraphrase_first_effect__after | -0.103 [-0.129, -0.079] |
| paraphrase_first_effect__before_neutral | -0.168 [-0.191, -0.146] |
| paraphrase_first_effect__before_confirm | -0.251 [-0.273, -0.228] |
| paraphrase_first_effect__before_cancel | -0.087 [-0.101, -0.074] |
| paraphrase_first_effect__nontemporal_neutral | -0.082 [-0.095, -0.070] |
| timeline_first_effect__after | -0.016 [-0.039, +0.007] |
| timeline_first_effect__before_neutral | -0.055 [-0.073, -0.036] |
| timeline_first_effect__before_confirm | -0.181 [-0.202, -0.160] |
| timeline_first_effect__before_cancel | -0.047 [-0.060, -0.033] |
| timeline_first_effect__nontemporal_neutral | -0.078 [-0.091, -0.067] |
| timeline_minus_paraphrase__after | +0.087 [+0.067, +0.107] |
| timeline_minus_paraphrase__before_neutral | +0.114 [+0.094, +0.134] |
| timeline_minus_paraphrase__before_confirm | +0.070 [+0.050, +0.088] |
| timeline_minus_paraphrase__before_cancel | +0.041 [+0.026, +0.058] |
| timeline_minus_paraphrase__nontemporal_neutral | +0.004 [+0.000, +0.008] |
| timeline_specificity_vs_nontemporal | +0.110 [+0.090, +0.130] |
| timeline_specificity_vs_after | +0.026 [-0.001, +0.054] |

| condition | E[rating 1-5] |
|---|---|
| after | 3.776 [3.737, 3.816] |
| before_neutral | 3.426 [3.382, 3.469] |
| before_confirm | 3.677 [3.643, 3.710] |
| before_cancel | 2.906 [2.837, 2.976] |
| nontemporal_neutral | 3.357 [3.311, 3.404] |

## gemma3_12b_it (gemma3), 80 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.999 | 0.000 | 0.002 | 1.000 |
| before_neutral | 0.075 | 0.046 | 0.878 | 0.887 |
| before_confirm | 0.920 | 0.006 | 0.074 | 0.925 |
| before_cancel | 0.000 | 0.882 | 0.118 | 0.900 |
| nontemporal_neutral | 0.000 | 0.052 | 0.948 | 0.950 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | +0.075 [+0.032, +0.126] |
| veridicality_gap | +0.923 [+0.873, +0.967] |
| confirm_update | +0.845 [+0.771, +0.911] |
| cancel_update | +0.075 [+0.033, +0.127] |
| gold_update_confirm | +0.845 [+0.770, +0.911] |
| gold_update_cancel | +0.836 [+0.766, +0.899] |
| gold_update_asymmetry | +0.009 [-0.084, +0.101] |
| update_asymmetry | +0.769 [+0.658, +0.869] |
| paraphrase_first_effect__after | -0.008 [-0.025, +0.002] |
| paraphrase_first_effect__before_neutral | +0.021 [-0.032, +0.073] |
| paraphrase_first_effect__before_confirm | -0.052 [-0.095, -0.017] |
| paraphrase_first_effect__before_cancel | +0.012 [-0.000, +0.035] |
| paraphrase_first_effect__nontemporal_neutral | +0.008 [-0.000, +0.022] |
| timeline_first_effect__after | +0.001 [-0.000, +0.003] |
| timeline_first_effect__before_neutral | +0.419 [+0.329, +0.512] |
| timeline_first_effect__before_confirm | -0.000 [-0.037, +0.039] |
| timeline_first_effect__before_cancel | +0.114 [+0.053, +0.183] |
| timeline_first_effect__nontemporal_neutral | -0.000 [-0.000, -0.000] |
| timeline_minus_paraphrase__after | +0.009 [-0.000, +0.026] |
| timeline_minus_paraphrase__before_neutral | +0.398 [+0.318, +0.476] |
| timeline_minus_paraphrase__before_confirm | +0.052 [+0.014, +0.096] |
| timeline_minus_paraphrase__before_cancel | +0.102 [+0.044, +0.167] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.008 [-0.021, -0.000] |
| timeline_specificity_vs_nontemporal | +0.406 [+0.328, +0.486] |
| timeline_specificity_vs_after | +0.389 [+0.310, +0.469] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.777 [4.658, 4.878] |
| before_neutral | 2.406 [2.200, 2.632] |
| before_confirm | 4.791 [4.631, 4.923] |
| before_cancel | 1.149 [1.049, 1.274] |
| nontemporal_neutral | 2.302 [2.112, 2.505] |
