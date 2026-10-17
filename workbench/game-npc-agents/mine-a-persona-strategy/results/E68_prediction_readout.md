# E68预注册预测读数

all=109 graphs; wear_wield=41; give=58; other_item=60. Seeds averaged within graph.

G=generic_priority；A=asset_protection；B=negative_only。P5中的A−F专指Agreeable−Firm。

下表均为百分点差与逐项95%图簇区间，不用区间作为自动科学判决。P2须同时区分首步block与全episode首次合法block。

## all

| 预测 | 模型 | 人设 | 对照 | 读数 | 差值pp [95% CI] | 独立图 |
|---|---|---|---|---|---:|---:|
| P1 | gemma | firm | G−A | goal | +25.69 [18.65, 33.03] | 109 |
| P1 | gemma | firm | G−A | first_step_goal | +36.39 [29.36, 43.73] | 109 |
| P2 | gemma | firm | B−G | first_step_block | +29.05 [22.02, 36.09] | 109 |
| P2 | gemma | firm | B−G | any_legal_block | +36.70 [29.04, 44.04] | 109 |
| P2 | gemma | firm | B−G | transfer | -2.45 [-5.20, -0.61] | 109 |
| P3 | gemma | firm | A−G | transfer | +4.28 [1.83, 7.03] | 109 |
| P3 | gemma | firm | A−G | any_examine | +27.83 [21.10, 34.86] | 109 |
| P3 | gemma | firm | A−G | any_speech | +28.75 [21.41, 36.39] | 109 |
| P1 | gemma | agreeable | G−A | goal | +30.89 [23.24, 38.53] | 109 |
| P1 | gemma | agreeable | G−A | first_step_goal | +41.59 [33.64, 49.85] | 109 |
| P2 | gemma | agreeable | B−G | first_step_block | +20.18 [13.76, 26.61] | 109 |
| P2 | gemma | agreeable | B−G | any_legal_block | +24.77 [17.74, 32.11] | 109 |
| P2 | gemma | agreeable | B−G | transfer | -4.28 [-8.56, 0.00] | 109 |
| P3 | gemma | agreeable | A−G | transfer | +14.98 [9.48, 20.49] | 109 |
| P3 | gemma | agreeable | A−G | any_examine | +20.18 [12.84, 27.52] | 109 |
| P3 | gemma | agreeable | A−G | any_speech | +27.83 [20.80, 35.47] | 109 |
| P1 | 32b | firm | G−A | goal | +5.81 [2.45, 9.18] | 109 |
| P1 | 32b | firm | G−A | first_step_goal | +16.21 [10.70, 22.02] | 109 |
| P2 | 32b | firm | B−G | first_step_block | -0.61 [-3.67, 2.45] | 109 |
| P2 | 32b | firm | B−G | any_legal_block | -0.00 [-3.36, 3.36] | 109 |
| P2 | 32b | firm | B−G | transfer | +2.75 [0.31, 6.12] | 109 |
| P3 | 32b | firm | A−G | transfer | +0.92 [0.00, 2.14] | 109 |
| P3 | 32b | firm | A−G | any_examine | +2.75 [0.92, 4.89] | 109 |
| P3 | 32b | firm | A−G | any_speech | +10.40 [6.12, 14.98] | 109 |
| P1 | 32b | agreeable | G−A | goal | +14.07 [9.48, 18.96] | 109 |
| P1 | 32b | agreeable | G−A | first_step_goal | +21.71 [15.60, 28.13] | 109 |
| P2 | 32b | agreeable | B−G | first_step_block | +0.92 [-1.22, 3.06] | 109 |
| P2 | 32b | agreeable | B−G | any_legal_block | +2.14 [-0.31, 4.59] | 109 |
| P2 | 32b | agreeable | B−G | transfer | +7.65 [3.06, 12.23] | 109 |
| P3 | 32b | agreeable | A−G | transfer | +10.70 [6.12, 15.60] | 109 |
| P3 | 32b | agreeable | A−G | any_examine | +2.14 [0.31, 4.28] | 109 |
| P3 | 32b | agreeable | A−G | any_speech | +10.70 [5.20, 16.51] | 109 |

## wear_wield

| 预测 | 模型 | 人设 | 对照 | 读数 | 差值pp [95% CI] | 独立图 |
|---|---|---|---|---|---:|---:|
| P1 | gemma | firm | G−A | goal | +31.71 [20.33, 42.28] | 41 |
| P1 | gemma | firm | G−A | first_step_goal | +39.84 [28.46, 52.03] | 41 |
| P2 | gemma | firm | B−G | first_step_block | +20.33 [10.57, 29.27] | 41 |
| P2 | gemma | firm | B−G | any_legal_block | +28.46 [17.89, 39.84] | 41 |
| P2 | gemma | firm | B−G | transfer | -3.25 [-8.94, 0.00] | 41 |
| P3 | gemma | firm | A−G | transfer | +4.07 [0.81, 8.13] | 41 |
| P3 | gemma | firm | A−G | any_examine | +28.46 [16.26, 39.84] | 41 |
| P3 | gemma | firm | A−G | any_speech | +27.64 [17.07, 39.02] | 41 |
| P4 | gemma | firm | Exec G−A | upstream A | goal | +27.64 [17.89, 38.21] | 41 |
| P4 | gemma | firm | Exec G−A | upstream G | goal | +28.46 [18.70, 39.02] | 41 |
| P1 | gemma | agreeable | G−A | goal | +37.40 [25.20, 48.78] | 41 |
| P1 | gemma | agreeable | G−A | first_step_goal | +43.09 [30.89, 55.28] | 41 |
| P2 | gemma | agreeable | B−G | first_step_block | +15.45 [8.13, 23.58] | 41 |
| P2 | gemma | agreeable | B−G | any_legal_block | +15.45 [7.32, 25.20] | 41 |
| P2 | gemma | agreeable | B−G | transfer | -9.76 [-17.07, -4.07] | 41 |
| P3 | gemma | agreeable | A−G | transfer | +16.26 [8.13, 23.58] | 41 |
| P3 | gemma | agreeable | A−G | any_examine | +29.27 [15.45, 43.09] | 41 |
| P3 | gemma | agreeable | A−G | any_speech | +25.20 [14.63, 37.40] | 41 |
| P4 | gemma | agreeable | Exec G−A | upstream A | goal | +36.59 [26.81, 47.15] | 41 |
| P4 | gemma | agreeable | Exec G−A | upstream G | goal | +26.02 [16.26, 35.77] | 41 |
| P1 | 32b | firm | G−A | goal | +9.76 [4.07, 17.07] | 41 |
| P1 | 32b | firm | G−A | first_step_goal | +20.33 [11.38, 30.08] | 41 |
| P2 | 32b | firm | B−G | first_step_block | +1.63 [-3.25, 6.50] | 41 |
| P2 | 32b | firm | B−G | any_legal_block | +2.44 [-3.25, 8.13] | 41 |
| P2 | 32b | firm | B−G | transfer | +0.81 [0.00, 2.44] | 41 |
| P3 | 32b | firm | A−G | transfer | +1.63 [0.00, 4.07] | 41 |
| P3 | 32b | firm | A−G | any_examine | +6.50 [1.63, 12.20] | 41 |
| P3 | 32b | firm | A−G | any_speech | +7.32 [1.63, 14.63] | 41 |
| P4 | 32b | firm | Exec G−A | upstream A | goal | +8.94 [3.25, 17.07] | 41 |
| P4 | 32b | firm | Exec G−A | upstream G | goal | +13.01 [5.69, 21.95] | 41 |
| P1 | 32b | agreeable | G−A | goal | +22.76 [15.45, 31.71] | 41 |
| P1 | 32b | agreeable | G−A | first_step_goal | +30.08 [19.51, 40.65] | 41 |
| P2 | 32b | agreeable | B−G | first_step_block | +3.25 [0.81, 6.50] | 41 |
| P2 | 32b | agreeable | B−G | any_legal_block | +6.50 [2.44, 10.57] | 41 |
| P2 | 32b | agreeable | B−G | transfer | +4.88 [-1.65, 12.20] | 41 |
| P3 | 32b | agreeable | A−G | transfer | +15.45 [8.13, 24.39] | 41 |
| P3 | 32b | agreeable | A−G | any_examine | +4.88 [-0.00, 10.57] | 41 |
| P3 | 32b | agreeable | A−G | any_speech | +10.57 [3.25, 18.70] | 41 |
| P4 | 32b | agreeable | Exec G−A | upstream A | goal | +13.01 [6.50, 19.51] | 41 |
| P4 | 32b | agreeable | Exec G−A | upstream G | goal | +9.76 [3.25, 17.07] | 41 |

## give

| 预测 | 模型 | 人设 | 对照 | 读数 | 差值pp [95% CI] | 独立图 |
|---|---|---|---|---|---:|---:|
| P1 | gemma | firm | G−A | goal | +18.97 [8.05, 29.31] | 58 |
| P1 | gemma | firm | G−A | first_step_goal | +33.33 [22.41, 43.68] | 58 |
| P2 | gemma | firm | B−G | first_step_block | +36.78 [25.86, 47.70] | 58 |
| P2 | gemma | firm | B−G | any_legal_block | +44.25 [32.18, 55.75] | 58 |
| P2 | gemma | firm | B−G | transfer | +0.00 [0.00, 0.00] | 58 |
| P3 | gemma | firm | A−G | transfer | +3.45 [0.57, 7.47] | 58 |
| P3 | gemma | firm | A−G | any_examine | +26.44 [17.24, 36.21] | 58 |
| P3 | gemma | firm | A−G | any_speech | +27.01 [17.23, 37.93] | 58 |
| P1 | gemma | agreeable | G−A | goal | +22.99 [12.07, 33.91] | 58 |
| P1 | gemma | agreeable | G−A | first_step_goal | +37.93 [26.44, 49.43] | 58 |
| P2 | gemma | agreeable | B−G | first_step_block | +26.44 [16.09, 36.78] | 58 |
| P2 | gemma | agreeable | B−G | any_legal_block | +35.06 [23.56, 46.55] | 58 |
| P2 | gemma | agreeable | B−G | transfer | +1.15 [-2.87, 5.75] | 58 |
| P3 | gemma | agreeable | A−G | transfer | +10.92 [4.02, 18.97] | 58 |
| P3 | gemma | agreeable | A−G | any_examine | +13.79 [4.60, 23.56] | 58 |
| P3 | gemma | agreeable | A−G | any_speech | +28.16 [17.82, 39.08] | 58 |
| P1 | 32b | firm | G−A | goal | +2.87 [0.57, 5.75] | 58 |
| P1 | 32b | firm | G−A | first_step_goal | +10.92 [2.87, 18.97] | 58 |
| P2 | 32b | firm | B−G | first_step_block | -2.30 [-6.90, 1.74] | 58 |
| P2 | 32b | firm | B−G | any_legal_block | -1.15 [-6.32, 3.45] | 58 |
| P2 | 32b | firm | B−G | transfer | +4.60 [0.00, 10.34] | 58 |
| P3 | 32b | firm | A−G | transfer | +0.57 [0.00, 1.72] | 58 |
| P3 | 32b | firm | A−G | any_examine | +0.57 [0.00, 1.72] | 58 |
| P3 | 32b | firm | A−G | any_speech | +11.49 [5.75, 17.82] | 58 |
| P1 | 32b | agreeable | G−A | goal | +5.17 [0.00, 11.49] | 58 |
| P1 | 32b | agreeable | G−A | first_step_goal | +13.22 [5.75, 21.26] | 58 |
| P2 | 32b | agreeable | B−G | first_step_block | -0.57 [-4.04, 2.87] | 58 |
| P2 | 32b | agreeable | B−G | any_legal_block | -0.57 [-4.60, 2.87] | 58 |
| P2 | 32b | agreeable | B−G | transfer | +10.34 [4.60, 17.24] | 58 |
| P3 | 32b | agreeable | A−G | transfer | +5.17 [0.00, 10.92] | 58 |
| P3 | 32b | agreeable | A−G | any_examine | +0.57 [0.00, 1.72] | 58 |
| P3 | 32b | agreeable | A−G | any_speech | +9.20 [2.30, 16.67] | 58 |

## other_item

| 预测 | 模型 | 人设 | 对照 | 读数 | 差值pp [95% CI] | 独立图 |
|---|---|---|---|---|---:|---:|
| P5 | gemma | agreeable−firm | A−F | generic | transfer | +10.00 [2.78, 17.78] | 60 |
| P5 | gemma | agreeable−firm | A−F | generic | both | +9.44 [1.67, 17.22] | 60 |
| P5 | gemma | agreeable−firm | A−F | generic | goal | -1.67 [-8.89, 6.11] | 60 |
| P5 | 32b | agreeable−firm | A−F | generic | transfer | +38.33 [27.78, 48.33] | 60 |
| P5 | 32b | agreeable−firm | A−F | generic | both | +38.33 [27.78, 48.33] | 60 |
| P5 | 32b | agreeable−firm | A−F | generic | goal | +0.56 [-1.11, 2.22] | 60 |

