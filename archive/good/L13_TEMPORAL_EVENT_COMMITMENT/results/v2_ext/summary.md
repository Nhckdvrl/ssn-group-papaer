# L13 summary — v2_ext

## qwen3_8b (qwen3), 100 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.004 | 0.404 | 0.592 | 0.730 |
| before_modal | 0.007 | 0.691 | 0.302 | 0.800 |
| before_post | 0.159 | 0.299 | 0.542 | 0.590 |
| by_the_time | 0.823 | 0.032 | 0.146 | 0.880 |
| in_time_to | 0.511 | 0.143 | 0.346 | 0.380 |
| purpose | 0.301 | 0.080 | 0.619 | 0.660 |
| until_neg | 0.067 | 0.696 | 0.236 | 0.070 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.004 [-0.010, -0.000] |
| paraphrase_first_effect__before_modal | -0.007 [-0.021, -0.000] |
| paraphrase_first_effect__before_post | +0.220 [+0.153, +0.288] |
| paraphrase_first_effect__by_the_time | +0.112 [+0.068, +0.159] |
| paraphrase_first_effect__in_time_to | -0.142 [-0.202, -0.081] |
| paraphrase_first_effect__purpose | -0.262 [-0.319, -0.207] |
| paraphrase_first_effect__until_neg | -0.043 [-0.082, -0.008] |
| timeline_first_effect__about_to | -0.004 [-0.010, -0.000] |
| timeline_first_effect__before_modal | -0.002 [-0.019, +0.010] |
| timeline_first_effect__before_post | +0.510 [+0.435, +0.585] |
| timeline_first_effect__by_the_time | +0.175 [+0.127, +0.227] |
| timeline_first_effect__in_time_to | -0.018 [-0.077, +0.039] |
| timeline_first_effect__purpose | -0.201 [-0.260, -0.141] |
| timeline_first_effect__until_neg | +0.002 [-0.045, +0.049] |
| timeline_minus_paraphrase__about_to | -0.000 [-0.000, +0.000] |
| timeline_minus_paraphrase__before_modal | +0.006 [+0.000, +0.013] |
| timeline_minus_paraphrase__before_post | +0.290 [+0.220, +0.363] |
| timeline_minus_paraphrase__by_the_time | +0.064 [+0.028, +0.105] |
| timeline_minus_paraphrase__in_time_to | +0.124 [+0.067, +0.184] |
| timeline_minus_paraphrase__purpose | +0.061 [+0.017, +0.111] |
| timeline_minus_paraphrase__until_neg | +0.044 [+0.005, +0.091] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 1.831 [1.749, 1.911] |
| before_modal | 1.465 [1.365, 1.574] |
| before_post | 2.535 [2.359, 2.723] |
| by_the_time | 3.939 [3.793, 4.076] |
| in_time_to | 3.442 [3.283, 3.599] |
| purpose | 3.331 [3.172, 3.489] |
| until_neg | 1.621 [1.480, 1.779] |

## llama31_8b_instruct (llama3), 100 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.084 | 0.233 | 0.684 | 0.940 |
| before_modal | 0.056 | 0.406 | 0.538 | 0.290 |
| before_post | 0.203 | 0.234 | 0.563 | 0.900 |
| by_the_time | 0.427 | 0.140 | 0.433 | 0.520 |
| in_time_to | 0.357 | 0.142 | 0.501 | 0.700 |
| purpose | 0.232 | 0.144 | 0.624 | 0.930 |
| until_neg | 0.132 | 0.400 | 0.468 | 0.010 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.075 [-0.086, -0.066] |
| paraphrase_first_effect__before_modal | -0.052 [-0.061, -0.044] |
| paraphrase_first_effect__before_post | -0.151 [-0.167, -0.136] |
| paraphrase_first_effect__by_the_time | -0.186 [-0.206, -0.165] |
| paraphrase_first_effect__in_time_to | -0.165 [-0.184, -0.145] |
| paraphrase_first_effect__purpose | -0.172 [-0.190, -0.153] |
| paraphrase_first_effect__until_neg | -0.095 [-0.109, -0.082] |
| timeline_first_effect__about_to | -0.073 [-0.083, -0.065] |
| timeline_first_effect__before_modal | -0.043 [-0.052, -0.036] |
| timeline_first_effect__before_post | -0.089 [-0.103, -0.075] |
| timeline_first_effect__by_the_time | -0.097 [-0.116, -0.078] |
| timeline_first_effect__in_time_to | -0.167 [-0.188, -0.145] |
| timeline_first_effect__purpose | -0.132 [-0.149, -0.114] |
| timeline_first_effect__until_neg | -0.082 [-0.097, -0.067] |
| timeline_minus_paraphrase__about_to | +0.002 [+0.000, +0.003] |
| timeline_minus_paraphrase__before_modal | +0.009 [+0.005, +0.013] |
| timeline_minus_paraphrase__before_post | +0.062 [+0.050, +0.074] |
| timeline_minus_paraphrase__by_the_time | +0.089 [+0.068, +0.110] |
| timeline_minus_paraphrase__in_time_to | -0.002 [-0.023, +0.020] |
| timeline_minus_paraphrase__purpose | +0.040 [+0.028, +0.054] |
| timeline_minus_paraphrase__until_neg | +0.014 [+0.002, +0.025] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 3.183 [3.139, 3.227] |
| before_modal | 3.061 [3.010, 3.111] |
| before_post | 3.381 [3.345, 3.416] |
| by_the_time | 3.528 [3.500, 3.558] |
| in_time_to | 3.619 [3.588, 3.649] |
| purpose | 3.504 [3.457, 3.553] |
| until_neg | 3.285 [3.243, 3.328] |

## gemma3_12b_it (gemma3), 100 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.000 | 0.053 | 0.947 | 0.960 |
| before_modal | 0.000 | 0.687 | 0.313 | 0.730 |
| before_post | 0.165 | 0.177 | 0.658 | 0.640 |
| by_the_time | 0.818 | 0.010 | 0.172 | 0.870 |
| in_time_to | 0.457 | 0.012 | 0.531 | 0.490 |
| purpose | 0.029 | 0.007 | 0.964 | 0.980 |
| until_neg | 0.036 | 0.296 | 0.667 | 0.020 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | +0.000 [-0.000, +0.000] |
| paraphrase_first_effect__before_modal | -0.000 [-0.000, -0.000] |
| paraphrase_first_effect__before_post | +0.053 [+0.002, +0.107] |
| paraphrase_first_effect__by_the_time | -0.039 [-0.100, +0.020] |
| paraphrase_first_effect__in_time_to | -0.001 [-0.070, +0.067] |
| paraphrase_first_effect__purpose | +0.035 [+0.014, +0.059] |
| paraphrase_first_effect__until_neg | +0.011 [-0.010, +0.038] |
| timeline_first_effect__about_to | -0.000 [-0.000, -0.000] |
| timeline_first_effect__before_modal | -0.000 [-0.000, +0.000] |
| timeline_first_effect__before_post | +0.309 [+0.247, +0.375] |
| timeline_first_effect__by_the_time | +0.131 [+0.084, +0.182] |
| timeline_first_effect__in_time_to | -0.060 [-0.125, +0.003] |
| timeline_first_effect__purpose | +0.017 [-0.006, +0.046] |
| timeline_first_effect__until_neg | +0.058 [+0.007, +0.114] |
| timeline_minus_paraphrase__about_to | -0.000 [-0.000, +0.000] |
| timeline_minus_paraphrase__before_modal | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__before_post | +0.256 [+0.198, +0.318] |
| timeline_minus_paraphrase__by_the_time | +0.169 [+0.105, +0.237] |
| timeline_minus_paraphrase__in_time_to | -0.059 [-0.132, +0.012] |
| timeline_minus_paraphrase__purpose | -0.018 [-0.054, +0.018] |
| timeline_minus_paraphrase__until_neg | +0.047 [-0.013, +0.106] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 1.706 [1.604, 1.814] |
| before_modal | 1.148 [1.073, 1.237] |
| before_post | 2.637 [2.373, 2.904] |
| by_the_time | 4.229 [4.059, 4.383] |
| in_time_to | 3.580 [3.372, 3.789] |
| purpose | 3.309 [3.095, 3.516] |
| until_neg | 2.100 [1.895, 2.320] |

## qwen3_32b (qwen3), 100 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.004 | 0.834 | 0.162 | 0.130 |
| before_modal | 0.011 | 0.945 | 0.044 | 0.950 |
| before_post | 0.542 | 0.387 | 0.071 | 0.030 |
| by_the_time | 0.970 | 0.028 | 0.002 | 0.980 |
| in_time_to | 0.624 | 0.235 | 0.141 | 0.110 |
| purpose | 0.499 | 0.198 | 0.304 | 0.260 |
| until_neg | 0.267 | 0.721 | 0.013 | 0.270 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.004 [-0.007, -0.001] |
| paraphrase_first_effect__before_modal | -0.009 [-0.020, -0.001] |
| paraphrase_first_effect__before_post | -0.024 [-0.084, +0.034] |
| paraphrase_first_effect__by_the_time | -0.021 [-0.056, +0.008] |
| paraphrase_first_effect__in_time_to | -0.235 [-0.303, -0.171] |
| paraphrase_first_effect__purpose | -0.379 [-0.441, -0.317] |
| paraphrase_first_effect__until_neg | +0.133 [+0.045, +0.218] |
| timeline_first_effect__about_to | -0.004 [-0.009, -0.001] |
| timeline_first_effect__before_modal | -0.008 [-0.021, +0.003] |
| timeline_first_effect__before_post | +0.129 [+0.080, +0.181] |
| timeline_first_effect__by_the_time | +0.001 [-0.015, +0.015] |
| timeline_first_effect__in_time_to | -0.240 [-0.300, -0.184] |
| timeline_first_effect__purpose | -0.457 [-0.525, -0.390] |
| timeline_first_effect__until_neg | +0.186 [+0.085, +0.287] |
| timeline_minus_paraphrase__about_to | -0.001 [-0.002, -0.000] |
| timeline_minus_paraphrase__before_modal | +0.001 [-0.004, +0.007] |
| timeline_minus_paraphrase__before_post | +0.153 [+0.087, +0.219] |
| timeline_minus_paraphrase__by_the_time | +0.022 [-0.007, +0.057] |
| timeline_minus_paraphrase__in_time_to | -0.005 [-0.056, +0.046] |
| timeline_minus_paraphrase__purpose | -0.078 [-0.116, -0.044] |
| timeline_minus_paraphrase__until_neg | +0.053 [-0.040, +0.144] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 1.383 [1.281, 1.497] |
| before_modal | 1.158 [1.079, 1.248] |
| before_post | 3.423 [3.083, 3.748] |
| by_the_time | 4.810 [4.658, 4.923] |
| in_time_to | 3.556 [3.289, 3.819] |
| purpose | 3.530 [3.285, 3.767] |
| until_neg | 1.689 [1.451, 1.945] |
