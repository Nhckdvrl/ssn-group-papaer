# L13 summary — e09_thinking

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
| neutral_gap | +0.005 [-0.040, +0.050] |
| veridicality_gap | +0.961 [+0.925, +0.989] |
| confirm_update | +0.875 [+0.781, +0.954] |
| cancel_update | +0.025 [+0.002, +0.056] |
| gold_update_confirm | +0.875 [+0.786, +0.954] |
| gold_update_cancel | +0.637 [+0.559, +0.713] |
| gold_update_asymmetry | +0.238 [+0.132, +0.340] |
| update_asymmetry | +0.850 [+0.747, +0.940] |
| timeline_first_effect__after | +0.011 [+0.002, +0.025] |
| timeline_first_effect__before_neutral | +0.428 [+0.309, +0.550] |
| timeline_first_effect__before_confirm | -0.019 [-0.048, -0.001] |
| timeline_first_effect__before_cancel | +0.003 [-0.008, +0.017] |
| timeline_first_effect__nontemporal_neutral | -0.023 [-0.058, -0.000] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.532 [4.426, 4.631] |
| before_neutral | 2.053 [1.844, 2.287] |
| before_confirm | 4.377 [4.158, 4.566] |
| before_cancel | 1.121 [1.049, 1.210] |
| nontemporal_neutral | 2.079 [1.851, 2.328] |

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
| neutral_gap | +0.215 [+0.125, +0.315] |
| veridicality_gap | +0.763 [+0.655, +0.860] |
| confirm_update | +0.727 [+0.604, +0.837] |
| cancel_update | +0.213 [+0.121, +0.316] |
| gold_update_confirm | +0.727 [+0.603, +0.839] |
| gold_update_cancel | +0.338 [+0.214, +0.465] |
| gold_update_asymmetry | +0.389 [+0.159, +0.605] |
| update_asymmetry | +0.537 [+0.338, +0.718] |
| timeline_first_effect__after | +0.001 [+0.000, +0.001] |
| timeline_first_effect__before_neutral | +0.357 [+0.249, +0.470] |
| timeline_first_effect__before_confirm | -0.058 [-0.131, -0.002] |
| timeline_first_effect__before_cancel | -0.022 [-0.067, +0.000] |
| timeline_first_effect__nontemporal_neutral | -0.021 [-0.049, -0.003] |

| condition | E[rating 1-5] |
|---|---|
| after | 4.981 [4.969, 4.989] |
| before_neutral | 2.323 [1.853, 2.819] |
| before_confirm | 4.883 [4.741, 4.972] |
| before_cancel | 1.039 [1.001, 1.109] |
| nontemporal_neutral | 2.136 [1.800, 2.483] |
