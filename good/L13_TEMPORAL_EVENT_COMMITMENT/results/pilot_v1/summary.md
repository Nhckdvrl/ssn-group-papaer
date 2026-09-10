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
| neutral_gap | +0.005 [-0.041, +0.051] |
| veridicality_gap | +0.961 [+0.926, +0.989] |
| confirm_update | +0.875 [+0.781, +0.953] |
| cancel_update | +0.025 [+0.002, +0.056] |
| gold_update_confirm | +0.875 [+0.781, +0.952] |
| gold_update_cancel | +0.637 [+0.559, +0.715] |
| gold_update_asymmetry | +0.238 [+0.129, +0.338] |
| update_asymmetry | +0.850 [+0.747, +0.939] |
| order_mc_first_effect__after | -0.066 [-0.147, -0.003] |
| order_mc_first_effect__before_neutral | -0.004 [-0.036, +0.031] |
| order_mc_first_effect__before_confirm | +0.037 [-0.001, +0.095] |
| order_mc_first_effect__before_cancel | +0.005 [-0.001, +0.015] |
| order_mc_first_effect__nontemporal_neutral | -0.023 [-0.058, -0.000] |
| paraphrase_first_effect__after | +0.011 [+0.002, +0.025] |
| paraphrase_first_effect__before_neutral | -0.022 [-0.057, +0.003] |
| paraphrase_first_effect__before_confirm | -0.003 [-0.036, +0.028] |
| paraphrase_first_effect__before_cancel | -0.003 [-0.009, -0.000] |
| paraphrase_first_effect__nontemporal_neutral | -0.023 [-0.058, -0.000] |
| timeline_first_effect__after | +0.011 [+0.002, +0.024] |
| timeline_first_effect__before_neutral | +0.149 [+0.049, +0.259] |
| timeline_first_effect__before_confirm | -0.021 [-0.063, +0.010] |
| timeline_first_effect__before_cancel | +0.026 [-0.005, +0.076] |
| timeline_first_effect__nontemporal_neutral | -0.023 [-0.058, -0.000] |
| timeline_strict_first_effect__after | +0.011 [+0.002, +0.025] |
| timeline_strict_first_effect__before_neutral | +0.089 [-0.002, +0.189] |
| timeline_strict_first_effect__before_confirm | +0.005 [-0.041, +0.067] |
| timeline_strict_first_effect__before_cancel | +0.012 [-0.008, +0.046] |
| timeline_strict_first_effect__nontemporal_neutral | -0.023 [-0.058, -0.000] |
| topic_mc_first_effect__after | -0.145 [-0.244, -0.061] |
| topic_mc_first_effect__before_neutral | -0.024 [-0.053, -0.002] |
| topic_mc_first_effect__before_confirm | -0.071 [-0.139, -0.015] |
| topic_mc_first_effect__before_cancel | -0.003 [-0.009, -0.000] |
| topic_mc_first_effect__nontemporal_neutral | -0.023 [-0.058, -0.000] |
| timeline_minus_paraphrase__after | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__before_neutral | +0.171 [+0.084, +0.270] |
| timeline_minus_paraphrase__before_confirm | -0.017 [-0.071, +0.016] |
| timeline_minus_paraphrase__before_cancel | +0.029 [+0.000, +0.080] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.000 [-0.000, -0.000] |
| timeline_specificity_vs_nontemporal | +0.171 [+0.083, +0.271] |
| timeline_specificity_vs_after | +0.171 [+0.084, +0.269] |
| order_minus_topic_mc__after | +0.079 [+0.021, +0.147] |
| order_minus_topic_mc__before_neutral | +0.020 [+0.001, +0.053] |
| order_minus_topic_mc__before_confirm | +0.108 [+0.036, +0.193] |
| order_minus_topic_mc__before_cancel | +0.008 [+0.000, +0.023] |
| order_minus_topic_mc__nontemporal_neutral | +0.000 [-0.000, +0.000] |
| strict_minus_open_timeline__after | -0.000 [-0.000, +0.000] |
| strict_minus_open_timeline__before_neutral | -0.059 [-0.159, +0.034] |
| strict_minus_open_timeline__before_confirm | +0.026 [-0.002, +0.072] |
| strict_minus_open_timeline__before_cancel | -0.013 [-0.034, -0.000] |
| strict_minus_open_timeline__nontemporal_neutral | +0.000 [+0.000, +0.000] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.532 [4.425, 4.637] |
| before_neutral | 2.053 [1.841, 2.283] |
| before_confirm | 4.377 [4.157, 4.564] |
| before_cancel | 1.121 [1.050, 1.206] |
| nontemporal_neutral | 2.079 [1.847, 2.331] |

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
| neutral_gap | +0.108 [+0.079, +0.138] |
| veridicality_gap | +0.472 [+0.433, +0.511] |
| confirm_update | +0.341 [+0.301, +0.381] |
| cancel_update | +0.103 [+0.071, +0.141] |
| gold_update_confirm | +0.341 [+0.302, +0.381] |
| gold_update_cancel | +0.296 [+0.238, +0.354] |
| gold_update_asymmetry | +0.045 [-0.024, +0.112] |
| update_asymmetry | +0.231 [+0.173, +0.284] |
| order_mc_first_effect__after | +0.098 [+0.067, +0.133] |
| order_mc_first_effect__before_neutral | -0.084 [-0.110, -0.060] |
| order_mc_first_effect__before_confirm | -0.048 [-0.093, -0.004] |
| order_mc_first_effect__before_cancel | -0.053 [-0.067, -0.041] |
| order_mc_first_effect__nontemporal_neutral | -0.032 [-0.048, -0.019] |
| paraphrase_first_effect__after | -0.096 [-0.129, -0.063] |
| paraphrase_first_effect__before_neutral | -0.148 [-0.175, -0.124] |
| paraphrase_first_effect__before_confirm | -0.238 [-0.264, -0.209] |
| paraphrase_first_effect__before_cancel | -0.076 [-0.095, -0.059] |
| paraphrase_first_effect__nontemporal_neutral | -0.066 [-0.085, -0.050] |
| timeline_first_effect__after | +0.006 [-0.025, +0.036] |
| timeline_first_effect__before_neutral | -0.051 [-0.076, -0.025] |
| timeline_first_effect__before_confirm | -0.168 [-0.200, -0.137] |
| timeline_first_effect__before_cancel | -0.033 [-0.052, -0.012] |
| timeline_first_effect__nontemporal_neutral | -0.064 [-0.083, -0.048] |
| timeline_strict_first_effect__after | +0.027 [-0.007, +0.063] |
| timeline_strict_first_effect__before_neutral | -0.059 [-0.082, -0.037] |
| timeline_strict_first_effect__before_confirm | -0.042 [-0.086, +0.003] |
| timeline_strict_first_effect__before_cancel | -0.058 [-0.073, -0.044] |
| timeline_strict_first_effect__nontemporal_neutral | -0.062 [-0.080, -0.046] |
| topic_mc_first_effect__after | -0.051 [-0.092, -0.011] |
| topic_mc_first_effect__before_neutral | -0.064 [-0.088, -0.042] |
| topic_mc_first_effect__before_confirm | -0.063 [-0.107, -0.019] |
| topic_mc_first_effect__before_cancel | -0.062 [-0.079, -0.047] |
| topic_mc_first_effect__nontemporal_neutral | +0.009 [-0.007, +0.022] |
| timeline_minus_paraphrase__after | +0.101 [+0.078, +0.124] |
| timeline_minus_paraphrase__before_neutral | +0.098 [+0.075, +0.121] |
| timeline_minus_paraphrase__before_confirm | +0.070 [+0.046, +0.094] |
| timeline_minus_paraphrase__before_cancel | +0.043 [+0.022, +0.071] |
| timeline_minus_paraphrase__nontemporal_neutral | +0.002 [+0.001, +0.004] |
| timeline_specificity_vs_nontemporal | +0.095 [+0.073, +0.120] |
| timeline_specificity_vs_after | -0.004 [-0.037, +0.031] |
| order_minus_topic_mc__after | +0.149 [+0.112, +0.186] |
| order_minus_topic_mc__before_neutral | -0.019 [-0.036, -0.004] |
| order_minus_topic_mc__before_confirm | +0.015 [-0.023, +0.052] |
| order_minus_topic_mc__before_cancel | +0.009 [+0.001, +0.019] |
| order_minus_topic_mc__nontemporal_neutral | -0.041 [-0.053, -0.030] |
| strict_minus_open_timeline__after | +0.021 [-0.006, +0.048] |
| strict_minus_open_timeline__before_neutral | -0.009 [-0.030, +0.013] |
| strict_minus_open_timeline__before_confirm | +0.126 [+0.086, +0.164] |
| strict_minus_open_timeline__before_cancel | -0.025 [-0.043, -0.011] |
| strict_minus_open_timeline__nontemporal_neutral | +0.002 [-0.001, +0.005] |

| condition | E[rating 1-5] |
|---|---|
| after | 3.842 [3.790, 3.898] |
| before_neutral | 3.415 [3.350, 3.481] |
| before_confirm | 3.724 [3.678, 3.770] |
| before_cancel | 2.864 [2.764, 2.965] |
| nontemporal_neutral | 3.315 [3.248, 3.381] |

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
| veridicality_gap | +0.540 [+0.434, +0.648] |
| confirm_update | +0.724 [+0.610, +0.827] |
| cancel_update | +0.006 [+0.003, +0.010] |
| gold_update_confirm | +0.724 [+0.613, +0.829] |
| gold_update_cancel | +0.222 [+0.168, +0.279] |
| gold_update_asymmetry | +0.502 [+0.401, +0.593] |
| update_asymmetry | +0.716 [+0.605, +0.820] |
| order_mc_first_effect__after | +0.185 [+0.059, +0.303] |
| order_mc_first_effect__before_neutral | +0.098 [+0.067, +0.134] |
| order_mc_first_effect__before_confirm | +0.029 [-0.036, +0.099] |
| order_mc_first_effect__before_cancel | +0.064 [+0.027, +0.111] |
| order_mc_first_effect__nontemporal_neutral | +0.020 [-0.007, +0.043] |
| paraphrase_first_effect__after | +0.049 [-0.077, +0.174] |
| paraphrase_first_effect__before_neutral | +0.050 [+0.035, +0.068] |
| paraphrase_first_effect__before_confirm | -0.422 [-0.513, -0.327] |
| paraphrase_first_effect__before_cancel | +0.009 [+0.005, +0.016] |
| paraphrase_first_effect__nontemporal_neutral | +0.003 [-0.017, +0.015] |
| timeline_first_effect__after | +0.261 [+0.136, +0.379] |
| timeline_first_effect__before_neutral | +0.124 [+0.066, +0.196] |
| timeline_first_effect__before_confirm | -0.080 [-0.168, +0.014] |
| timeline_first_effect__before_cancel | +0.037 [+0.007, +0.077] |
| timeline_first_effect__nontemporal_neutral | -0.015 [-0.044, +0.001] |
| timeline_strict_first_effect__after | +0.404 [+0.303, +0.505] |
| timeline_strict_first_effect__before_neutral | +0.189 [+0.114, +0.278] |
| timeline_strict_first_effect__before_confirm | +0.014 [-0.083, +0.115] |
| timeline_strict_first_effect__before_cancel | +0.044 [+0.004, +0.099] |
| timeline_strict_first_effect__nontemporal_neutral | -0.015 [-0.047, +0.002] |
| topic_mc_first_effect__after | -0.384 [-0.485, -0.280] |
| topic_mc_first_effect__before_neutral | +0.026 [+0.021, +0.031] |
| topic_mc_first_effect__before_confirm | -0.407 [-0.504, -0.312] |
| topic_mc_first_effect__before_cancel | +0.027 [+0.019, +0.037] |
| topic_mc_first_effect__nontemporal_neutral | -0.002 [-0.038, +0.018] |
| timeline_minus_paraphrase__after | +0.212 [+0.111, +0.313] |
| timeline_minus_paraphrase__before_neutral | +0.075 [+0.019, +0.142] |
| timeline_minus_paraphrase__before_confirm | +0.343 [+0.258, +0.425] |
| timeline_minus_paraphrase__before_cancel | +0.028 [+0.002, +0.062] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.018 [-0.032, -0.008] |
| timeline_specificity_vs_nontemporal | +0.092 [+0.032, +0.170] |
| timeline_specificity_vs_after | -0.137 [-0.263, -0.007] |
| order_minus_topic_mc__after | +0.569 [+0.484, +0.649] |
| order_minus_topic_mc__before_neutral | +0.072 [+0.041, +0.108] |
| order_minus_topic_mc__before_confirm | +0.437 [+0.360, +0.515] |
| order_minus_topic_mc__before_cancel | +0.037 [+0.006, +0.078] |
| order_minus_topic_mc__nontemporal_neutral | +0.022 [+0.004, +0.044] |
| strict_minus_open_timeline__after | +0.143 [+0.090, +0.202] |
| strict_minus_open_timeline__before_neutral | +0.065 [+0.012, +0.122] |
| strict_minus_open_timeline__before_confirm | +0.094 [+0.013, +0.175] |
| strict_minus_open_timeline__before_cancel | +0.006 [-0.014, +0.030] |
| strict_minus_open_timeline__nontemporal_neutral | -0.001 [-0.004, +0.002] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.413 [4.149, 4.658] |
| before_neutral | 2.055 [1.805, 2.316] |
| before_confirm | 4.529 [4.212, 4.783] |
| before_cancel | 1.213 [1.099, 1.356] |
| nontemporal_neutral | 1.927 [1.683, 2.200] |

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
| neutral_gap | +0.045 [+0.004, +0.104] |
| veridicality_gap | +0.952 [+0.897, +0.994] |
| confirm_update | +0.846 [+0.737, +0.941] |
| cancel_update | +0.045 [+0.004, +0.101] |
| gold_update_confirm | +0.846 [+0.736, +0.940] |
| gold_update_cancel | +0.822 [+0.714, +0.916] |
| gold_update_asymmetry | +0.024 [-0.120, +0.164] |
| update_asymmetry | +0.801 [+0.661, +0.921] |
| order_mc_first_effect__after | -0.029 [-0.059, -0.006] |
| order_mc_first_effect__before_neutral | -0.026 [-0.070, +0.007] |
| order_mc_first_effect__before_confirm | -0.102 [-0.194, -0.023] |
| order_mc_first_effect__before_cancel | -0.000 [-0.000, +0.000] |
| order_mc_first_effect__nontemporal_neutral | +0.016 [+0.000, +0.045] |
| paraphrase_first_effect__after | -0.001 [-0.012, +0.006] |
| paraphrase_first_effect__before_neutral | +0.066 [+0.031, +0.104] |
| paraphrase_first_effect__before_confirm | -0.026 [-0.063, +0.002] |
| paraphrase_first_effect__before_cancel | +0.024 [-0.000, +0.070] |
| paraphrase_first_effect__nontemporal_neutral | +0.000 [-0.000, +0.000] |
| timeline_first_effect__after | +0.003 [+0.000, +0.007] |
| timeline_first_effect__before_neutral | +0.397 [+0.278, +0.520] |
| timeline_first_effect__before_confirm | +0.002 [-0.052, +0.063] |
| timeline_first_effect__before_cancel | +0.070 [+0.003, +0.154] |
| timeline_first_effect__nontemporal_neutral | -0.000 [-0.000, +0.000] |
| timeline_strict_first_effect__after | +0.003 [+0.000, +0.007] |
| timeline_strict_first_effect__before_neutral | +0.632 [+0.494, +0.763] |
| timeline_strict_first_effect__before_confirm | -0.010 [-0.032, +0.002] |
| timeline_strict_first_effect__before_cancel | +0.125 [+0.025, +0.226] |
| timeline_strict_first_effect__nontemporal_neutral | -0.000 [-0.000, -0.000] |
| topic_mc_first_effect__after | -0.150 [-0.225, -0.084] |
| topic_mc_first_effect__before_neutral | -0.041 [-0.091, -0.004] |
| topic_mc_first_effect__before_confirm | -0.266 [-0.384, -0.152] |
| topic_mc_first_effect__before_cancel | +0.009 [-0.000, +0.028] |
| topic_mc_first_effect__nontemporal_neutral | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__after | +0.004 [-0.000, +0.013] |
| timeline_minus_paraphrase__before_neutral | +0.332 [+0.227, +0.442] |
| timeline_minus_paraphrase__before_confirm | +0.028 [-0.018, +0.087] |
| timeline_minus_paraphrase__before_cancel | +0.046 [+0.002, +0.113] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.000 [-0.000, +0.000] |
| timeline_specificity_vs_nontemporal | +0.332 [+0.227, +0.441] |
| timeline_specificity_vs_after | +0.328 [+0.219, +0.437] |
| order_minus_topic_mc__after | +0.121 [+0.066, +0.184] |
| order_minus_topic_mc__before_neutral | +0.014 [+0.003, +0.028] |
| order_minus_topic_mc__before_confirm | +0.164 [+0.057, +0.278] |
| order_minus_topic_mc__before_cancel | -0.009 [-0.028, -0.000] |
| order_minus_topic_mc__nontemporal_neutral | +0.016 [+0.000, +0.045] |
| strict_minus_open_timeline__after | +0.000 [+0.000, +0.000] |
| strict_minus_open_timeline__before_neutral | +0.234 [+0.095, +0.372] |
| strict_minus_open_timeline__before_confirm | -0.012 [-0.081, +0.048] |
| strict_minus_open_timeline__before_cancel | +0.055 [+0.000, +0.127] |
| strict_minus_open_timeline__nontemporal_neutral | -0.000 [-0.000, -0.000] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.770 [4.574, 4.920] |
| before_neutral | 2.323 [2.025, 2.637] |
| before_confirm | 4.709 [4.436, 4.925] |
| before_cancel | 1.078 [1.003, 1.200] |
| nontemporal_neutral | 2.142 [1.893, 2.415] |

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
| neutral_gap | +0.215 [+0.127, +0.316] |
| veridicality_gap | +0.763 [+0.658, +0.862] |
| confirm_update | +0.727 [+0.607, +0.839] |
| cancel_update | +0.213 [+0.120, +0.317] |
| gold_update_confirm | +0.727 [+0.607, +0.843] |
| gold_update_cancel | +0.338 [+0.217, +0.467] |
| gold_update_asymmetry | +0.389 [+0.151, +0.612] |
| update_asymmetry | +0.537 [+0.339, +0.715] |
| paraphrase_first_effect__after | -0.002 [-0.005, +0.000] |
| paraphrase_first_effect__before_neutral | +0.016 [-0.083, +0.107] |
| paraphrase_first_effect__before_confirm | +0.013 [-0.020, +0.055] |
| paraphrase_first_effect__before_cancel | +0.002 [-0.000, +0.007] |
| paraphrase_first_effect__nontemporal_neutral | -0.012 [-0.024, -0.002] |
| timeline_first_effect__after | +0.001 [+0.000, +0.001] |
| timeline_first_effect__before_neutral | +0.340 [+0.231, +0.453] |
| timeline_first_effect__before_confirm | -0.012 [-0.063, +0.037] |
| timeline_first_effect__before_cancel | +0.010 [+0.000, +0.030] |
| timeline_first_effect__nontemporal_neutral | -0.021 [-0.049, -0.003] |
| timeline_minus_paraphrase__after | +0.002 [+0.000, +0.006] |
| timeline_minus_paraphrase__before_neutral | +0.325 [+0.209, +0.444] |
| timeline_minus_paraphrase__before_confirm | -0.026 [-0.084, +0.016] |
| timeline_minus_paraphrase__before_cancel | +0.008 [-0.005, +0.028] |
| timeline_minus_paraphrase__nontemporal_neutral | -0.009 [-0.025, -0.000] |
| timeline_specificity_vs_nontemporal | +0.333 [+0.220, +0.454] |
| timeline_specificity_vs_after | +0.322 [+0.206, +0.442] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.981 [4.969, 4.989] |
| before_neutral | 2.323 [1.850, 2.814] |
| before_confirm | 4.883 [4.739, 4.972] |
| before_cancel | 1.039 [1.001, 1.110] |
| nontemporal_neutral | 2.136 [1.804, 2.493] |
