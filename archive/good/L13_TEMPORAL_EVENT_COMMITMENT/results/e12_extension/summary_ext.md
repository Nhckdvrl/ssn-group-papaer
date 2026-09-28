# L13 summary — e12_extension

## qwen3_8b (qwen3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.000 | 0.377 | 0.623 | 0.775 |
| before_modal | 0.001 | 0.672 | 0.328 | 0.800 |
| purpose | 0.258 | 0.072 | 0.670 | 0.750 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.000 [-0.001, -0.000] |
| paraphrase_first_effect__before_modal | -0.001 [-0.001, -0.000] |
| paraphrase_first_effect__purpose | -0.224 [-0.322, -0.136] |
| timeline_first_effect__about_to | -0.000 [-0.001, -0.000] |
| timeline_first_effect__before_modal | +0.008 [-0.001, +0.021] |
| timeline_first_effect__purpose | -0.181 [-0.283, -0.086] |
| timeline_minus_paraphrase__about_to | -0.000 [-0.000, -0.000] |
| timeline_minus_paraphrase__before_modal | +0.009 [-0.000, +0.022] |
| timeline_minus_paraphrase__purpose | +0.043 [-0.014, +0.120] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 1.770 [1.636, 1.907] |
| before_modal | 1.435 [1.283, 1.606] |
| purpose | 3.142 [2.864, 3.409] |

## llama31_8b_instruct (llama3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.069 | 0.253 | 0.678 | 0.875 |
| before_modal | 0.046 | 0.423 | 0.531 | 0.300 |
| purpose | 0.197 | 0.157 | 0.647 | 0.950 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.065 [-0.080, -0.051] |
| paraphrase_first_effect__before_modal | -0.043 [-0.055, -0.033] |
| paraphrase_first_effect__purpose | -0.159 [-0.189, -0.130] |
| timeline_first_effect__about_to | -0.063 [-0.078, -0.051] |
| timeline_first_effect__before_modal | -0.039 [-0.051, -0.030] |
| timeline_first_effect__purpose | -0.131 [-0.160, -0.103] |
| timeline_minus_paraphrase__about_to | +0.002 [+0.000, +0.003] |
| timeline_minus_paraphrase__before_modal | +0.004 [+0.002, +0.005] |
| timeline_minus_paraphrase__purpose | +0.029 [+0.013, +0.048] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 3.146 [3.077, 3.215] |
| before_modal | 3.014 [2.942, 3.088] |
| purpose | 3.464 [3.384, 3.543] |

## gemma3_12b_it (gemma3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.000 | 0.095 | 0.905 | 0.925 |
| before_modal | 0.000 | 0.757 | 0.243 | 0.775 |
| purpose | 0.002 | 0.017 | 0.982 | 1.000 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.000 [-0.000, -0.000] |
| paraphrase_first_effect__before_modal | -0.000 [-0.000, -0.000] |
| paraphrase_first_effect__purpose | +0.013 [-0.002, +0.032] |
| timeline_first_effect__about_to | -0.000 [-0.000, +0.000] |
| timeline_first_effect__before_modal | +0.000 [+0.000, +0.000] |
| timeline_first_effect__purpose | +0.003 [-0.005, +0.013] |
| timeline_minus_paraphrase__about_to | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__before_modal | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__purpose | -0.010 [-0.031, +0.006] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 1.618 [1.461, 1.777] |
| before_modal | 1.077 [1.009, 1.158] |
| purpose | 2.909 [2.579, 3.250] |
