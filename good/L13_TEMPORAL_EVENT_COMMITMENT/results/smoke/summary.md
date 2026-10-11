# L13 summary — smoke

## qwen3_0_6b (qwen3), 40 bases

| condition | P(YES) | P(NO) | P(ND) | acc |
|---|---|---|---|---|
| after | 0.344 | 0.255 | 0.402 | 0.025 |
| before_neutral | 0.324 | 0.289 | 0.387 | 1.000 |
| before_confirm | 0.354 | 0.250 | 0.396 | 0.050 |
| before_cancel | 0.310 | 0.326 | 0.364 | 0.025 |
| nontemporal_neutral | 0.326 | 0.288 | 0.386 | 1.000 |

| contrast | mean [95% CI] |
|---|---|
| neutral_gap | -0.002 [-0.007, +0.002] |
| veridicality_gap | +0.020 [+0.016, +0.025] |
| confirm_update | +0.030 [+0.023, +0.038] |
| cancel_update | +0.014 [+0.010, +0.018] |
| update_asymmetry | +0.017 [+0.009, +0.024] |
| timeline_first_effect__after | -0.113 [-0.141, -0.085] |
| timeline_first_effect__before_neutral | -0.147 [-0.182, -0.110] |
| timeline_first_effect__before_confirm | -0.076 [-0.113, -0.040] |
| timeline_first_effect__before_cancel | -0.259 [-0.274, -0.241] |
| timeline_first_effect__nontemporal_neutral | -0.175 [-0.197, -0.151] |

| condition | E[rating 1-5] |
|---|---|
| after | 3.324 [3.262, 3.385] |
| before_neutral | 3.208 [3.127, 3.287] |
| before_confirm | 3.521 [3.439, 3.604] |
| before_cancel | 3.122 [3.010, 3.235] |
| nontemporal_neutral | 3.258 [3.159, 3.358] |
