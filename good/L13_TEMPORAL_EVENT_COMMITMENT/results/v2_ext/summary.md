# L13 summary — v2_ext

## qwen3_8b (qwen3), 80 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.001 | 0.405 | 0.594 | 0.750 |
| before_modal | 0.009 | 0.716 | 0.275 | 0.850 |
| before_post | 0.165 | 0.320 | 0.515 | 0.562 |
| purpose | 0.300 | 0.077 | 0.623 | 0.662 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.001 [-0.002, -0.000] |
| paraphrase_first_effect__before_modal | -0.009 [-0.027, -0.000] |
| paraphrase_first_effect__before_post | +0.176 [+0.107, +0.250] |
| paraphrase_first_effect__purpose | -0.262 [-0.324, -0.201] |
| timeline_first_effect__about_to | -0.001 [-0.002, -0.000] |
| timeline_first_effect__before_modal | -0.004 [-0.026, +0.009] |
| timeline_first_effect__before_post | +0.474 [+0.390, +0.557] |
| timeline_first_effect__purpose | -0.204 [-0.273, -0.135] |
| timeline_minus_paraphrase__about_to | -0.000 [-0.000, -0.000] |
| timeline_minus_paraphrase__before_modal | +0.005 [+0.000, +0.012] |
| timeline_minus_paraphrase__before_post | +0.298 [+0.214, +0.385] |
| timeline_minus_paraphrase__purpose | +0.058 [+0.013, +0.109] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 1.815 [1.724, 1.904] |
| before_modal | 1.419 [1.306, 1.546] |
| before_post | 2.501 [2.296, 2.714] |
| purpose | 3.301 [3.116, 3.481] |

## llama31_8b_instruct (llama3), 80 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.084 | 0.230 | 0.686 | 0.938 |
| before_modal | 0.052 | 0.416 | 0.532 | 0.287 |
| before_post | 0.188 | 0.243 | 0.569 | 0.900 |
| purpose | 0.229 | 0.144 | 0.627 | 0.925 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.075 [-0.087, -0.064] |
| paraphrase_first_effect__before_modal | -0.048 [-0.057, -0.041] |
| paraphrase_first_effect__before_post | -0.144 [-0.161, -0.128] |
| paraphrase_first_effect__purpose | -0.169 [-0.190, -0.149] |
| timeline_first_effect__about_to | -0.073 [-0.084, -0.063] |
| timeline_first_effect__before_modal | -0.040 [-0.049, -0.033] |
| timeline_first_effect__before_post | -0.087 [-0.101, -0.072] |
| timeline_first_effect__purpose | -0.127 [-0.147, -0.106] |
| timeline_minus_paraphrase__about_to | +0.002 [-0.000, +0.004] |
| timeline_minus_paraphrase__before_modal | +0.008 [+0.004, +0.014] |
| timeline_minus_paraphrase__before_post | +0.058 [+0.045, +0.071] |
| timeline_minus_paraphrase__purpose | +0.043 [+0.027, +0.060] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 3.186 [3.134, 3.239] |
| before_modal | 3.039 [2.989, 3.090] |
| before_post | 3.358 [3.322, 3.394] |
| purpose | 3.495 [3.439, 3.550] |

## gemma3_12b_it (gemma3), 80 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.000 | 0.052 | 0.948 | 0.963 |
| before_modal | 0.000 | 0.696 | 0.304 | 0.738 |
| before_post | 0.155 | 0.195 | 0.649 | 0.625 |
| purpose | 0.028 | 0.008 | 0.964 | 0.975 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | +0.000 [-0.000, +0.000] |
| paraphrase_first_effect__before_modal | -0.000 [-0.000, -0.000] |
| paraphrase_first_effect__before_post | +0.060 [+0.000, +0.123] |
| paraphrase_first_effect__purpose | +0.026 [+0.004, +0.050] |
| timeline_first_effect__about_to | -0.000 [-0.000, -0.000] |
| timeline_first_effect__before_modal | -0.000 [-0.000, +0.000] |
| timeline_first_effect__before_post | +0.294 [+0.222, +0.370] |
| timeline_first_effect__purpose | +0.021 [-0.006, +0.058] |
| timeline_minus_paraphrase__about_to | -0.000 [-0.000, +0.000] |
| timeline_minus_paraphrase__before_modal | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__before_post | +0.234 [+0.169, +0.302] |
| timeline_minus_paraphrase__purpose | -0.005 [-0.043, +0.038] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 1.695 [1.568, 1.830] |
| before_modal | 1.133 [1.052, 1.235] |
| before_post | 2.491 [2.209, 2.782] |
| purpose | 3.227 [2.985, 3.470] |
