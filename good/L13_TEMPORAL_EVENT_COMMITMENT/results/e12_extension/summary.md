# L13 summary — e12_extension

## qwen3_8b (qwen3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.000 | 0.382 | 0.617 | 0.750 |
| before_modal | 0.001 | 0.671 | 0.328 | 0.800 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.000 [-0.001, -0.000] |
| paraphrase_first_effect__before_modal | -0.001 [-0.002, -0.000] |
| timeline_first_effect__about_to | -0.000 [-0.001, -0.000] |
| timeline_first_effect__before_modal | +0.008 [-0.001, +0.022] |
| timeline_minus_paraphrase__about_to | -0.000 [-0.000, -0.000] |
| timeline_minus_paraphrase__before_modal | +0.009 [-0.000, +0.022] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 1.760 [1.617, 1.902] |
| before_modal | 1.441 [1.290, 1.612] |

## llama31_8b_instruct (llama3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.070 | 0.253 | 0.677 | 0.875 |
| before_modal | 0.046 | 0.421 | 0.532 | 0.300 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.066 [-0.082, -0.053] |
| paraphrase_first_effect__before_modal | -0.043 [-0.056, -0.033] |
| timeline_first_effect__about_to | -0.064 [-0.080, -0.051] |
| timeline_first_effect__before_modal | -0.040 [-0.052, -0.030] |
| timeline_minus_paraphrase__about_to | +0.002 [+0.001, +0.003] |
| timeline_minus_paraphrase__before_modal | +0.003 [+0.002, +0.005] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 3.145 [3.075, 3.213] |
| before_modal | 3.017 [2.945, 3.089] |

## gemma3_12b_it (gemma3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| about_to | 0.000 | 0.095 | 0.905 | 0.925 |
| before_modal | 0.000 | 0.757 | 0.243 | 0.775 |

| contrast | mean [95% CI] |
|---|---|
| paraphrase_first_effect__about_to | -0.000 [-0.000, -0.000] |
| paraphrase_first_effect__before_modal | -0.000 [-0.000, -0.000] |
| timeline_first_effect__about_to | -0.000 [-0.000, +0.000] |
| timeline_first_effect__before_modal | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__about_to | +0.000 [+0.000, +0.000] |
| timeline_minus_paraphrase__before_modal | +0.000 [+0.000, +0.000] |

| condition | E[rating 1-5] |
|---|---|
| about_to | 1.615 [1.456, 1.774] |
| before_modal | 1.073 [1.009, 1.155] |
