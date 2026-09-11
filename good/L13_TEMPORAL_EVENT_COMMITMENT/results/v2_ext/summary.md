# L13 summary — v2_ext

## qwen3_8b (qwen3), 100 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.004 | 0.404 | 0.593 | 0.730 |
| before_modal | 0.007 | 0.692 | 0.300 | 0.810 |
| before_post | 0.157 | 0.301 | 0.542 | 0.580 |
| purpose | 0.301 | 0.080 | 0.620 | 0.660 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.004 [-0.010, -0.000] |
| paraphrase_first_effect__before_modal | -0.007 [-0.021, -0.000] |
| paraphrase_first_effect__before_post | +0.214 [+0.149, +0.283] |
| paraphrase_first_effect__purpose | -0.267 [-0.324, -0.212] |
| timeline_first_effect__about_to | -0.004 [-0.010, -0.000] |
| timeline_first_effect__before_modal | -0.004 [-0.021, +0.007] |
| timeline_first_effect__before_post | +0.509 [+0.434, +0.585] |
| timeline_first_effect__purpose | -0.200 [-0.261, -0.140] |
| timeline_minus_paraphrase__about_to | -0.000 [-0.000, -0.000] |
| timeline_minus_paraphrase__before_modal | +0.004 [-0.000, +0.010] |
| timeline_minus_paraphrase__before_post | +0.295 [+0.222, +0.371] |
| timeline_minus_paraphrase__purpose | +0.067 [+0.022, +0.119] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 1.833 [1.754, 1.915] |
| before_modal | 1.464 [1.367, 1.574] |
| before_post | 2.541 [2.358, 2.731] |
| purpose | 3.322 [3.157, 3.484] |

## llama31_8b_instruct (llama3), 100 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.083 | 0.232 | 0.685 | 0.940 |
| before_modal | 0.057 | 0.407 | 0.536 | 0.280 |
| before_post | 0.204 | 0.232 | 0.564 | 0.880 |
| purpose | 0.232 | 0.143 | 0.625 | 0.910 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.075 [-0.085, -0.066] |
| paraphrase_first_effect__before_modal | -0.052 [-0.061, -0.045] |
| paraphrase_first_effect__before_post | -0.151 [-0.167, -0.136] |
| paraphrase_first_effect__purpose | -0.170 [-0.188, -0.152] |
| timeline_first_effect__about_to | -0.073 [-0.083, -0.065] |
| timeline_first_effect__before_modal | -0.043 [-0.051, -0.036] |
| timeline_first_effect__before_post | -0.091 [-0.105, -0.078] |
| timeline_first_effect__purpose | -0.126 [-0.144, -0.109] |
| timeline_minus_paraphrase__about_to | +0.002 [+0.000, +0.004] |
| timeline_minus_paraphrase__before_modal | +0.009 [+0.006, +0.014] |
| timeline_minus_paraphrase__before_post | +0.060 [+0.048, +0.072] |
| timeline_minus_paraphrase__purpose | +0.044 [+0.030, +0.059] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 3.182 [3.137, 3.228] |
| before_modal | 3.067 [3.017, 3.117] |
| before_post | 3.386 [3.349, 3.422] |
| purpose | 3.501 [3.453, 3.548] |

## gemma3_12b_it (gemma3), 100 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.000 | 0.053 | 0.947 | 0.960 |
| before_modal | 0.000 | 0.686 | 0.314 | 0.730 |
| before_post | 0.163 | 0.175 | 0.662 | 0.650 |
| purpose | 0.028 | 0.007 | 0.966 | 0.980 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | +0.000 [-0.000, +0.000] |
| paraphrase_first_effect__before_modal | -0.000 [-0.000, -0.000] |
| paraphrase_first_effect__before_post | +0.055 [+0.003, +0.108] |
| paraphrase_first_effect__purpose | +0.038 [+0.015, +0.065] |
| timeline_first_effect__about_to | -0.000 [-0.000, -0.000] |
| timeline_first_effect__before_modal | -0.000 [-0.000, +0.000] |
| timeline_first_effect__before_post | +0.313 [+0.250, +0.381] |
| timeline_first_effect__purpose | +0.026 [-0.003, +0.062] |
| timeline_minus_paraphrase__about_to | -0.000 [-0.000, +0.000] |
| timeline_minus_paraphrase__before_modal | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__before_post | +0.258 [+0.199, +0.317] |
| timeline_minus_paraphrase__purpose | -0.012 [-0.053, +0.032] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 1.716 [1.607, 1.824] |
| before_modal | 1.146 [1.072, 1.233] |
| before_post | 2.641 [2.384, 2.901] |
| purpose | 3.309 [3.097, 3.518] |

## qwen3_32b (qwen3), 100 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.004 | 0.835 | 0.161 | 0.130 |
| before_modal | 0.011 | 0.945 | 0.044 | 0.950 |
| before_post | 0.543 | 0.387 | 0.071 | 0.030 |
| purpose | 0.498 | 0.197 | 0.305 | 0.260 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.003 [-0.006, +0.001] |
| paraphrase_first_effect__before_modal | -0.009 [-0.020, -0.001] |
| paraphrase_first_effect__before_post | -0.027 [-0.087, +0.031] |
| paraphrase_first_effect__purpose | -0.382 [-0.447, -0.318] |
| timeline_first_effect__about_to | -0.004 [-0.008, -0.001] |
| timeline_first_effect__before_modal | -0.007 [-0.021, +0.004] |
| timeline_first_effect__before_post | +0.128 [+0.080, +0.178] |
| timeline_first_effect__purpose | -0.457 [-0.525, -0.387] |
| timeline_minus_paraphrase__about_to | -0.002 [-0.004, -0.000] |
| timeline_minus_paraphrase__before_modal | +0.001 [-0.004, +0.007] |
| timeline_minus_paraphrase__before_post | +0.156 [+0.089, +0.223] |
| timeline_minus_paraphrase__purpose | -0.075 [-0.113, -0.040] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 1.387 [1.288, 1.499] |
| before_modal | 1.157 [1.078, 1.248] |
| before_post | 3.424 [3.083, 3.762] |
| purpose | 3.535 [3.294, 3.768] |
