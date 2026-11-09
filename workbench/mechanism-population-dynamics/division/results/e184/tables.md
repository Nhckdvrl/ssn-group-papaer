# E184 tables（自动生成：`scripts/e184_figure.py`；数据 `results/e184/<model>.json`）

## 1. 结论级判决（主语料、主读数；逐层 above / within / below / split 计数；⌈2L/3⌉ 门槛）

| 结论 | Qwen3-30B-A3B | GPT-OSS-20B | OLMoE-1B-7B-0125-Inst |
|---|---|---|---|
| 1 lexical / token-id experts（flores） | **survives**（above 42 / within 6 / below 0 / split 0，L=48; 中位 T/max = 1.46） | **survives**（above 17 / within 7 / below 0 / split 0，L=24; 中位 T/max = 1.35） | **survives**（above 15 / within 1 / below 0 / split 0，L=16; 中位 T/max = 1.54） |
| 2 POS specialisation（ud） | **survives**（above 48 / within 0 / below 0 / split 0，L=48; 中位 T/max = 1.85） | **null-family-dependent**（above 13 / within 11 / below 0 / split 0，L=24） | **survives**（above 16 / within 0 / below 0 / split 0，L=16; 中位 T/max = 1.87） |
| 3 adjacent tokens share expert（flores） | **survives**（above 45 / within 1 / below 2 / split 0，L=48; 中位 T/max = 1.47） | **null-family-dependent**（above 11 / within 10 / below 3 / split 0，L=24） | **survives (marginal)**（above 12 / within 2 / below 1 / split 1，L=16; 中位 T/max = 1.23） |
| 4 deep layers route by predicted next token（flores） | **below-null**（above 1 / within 7 / below 40 / split 0，L=48） | **below-null***（above 2 / within 6 / below 16 / split 0，L=24） | **below-null**（above 0 / within 1 / below 14 / split 1，L=16） |

\* = 两个语料半（序列 id 奇 / 偶）中至少一半的判决与全量不同。

### 次级判决（预登记的次读数与 UD 复核）

| 读数 | Qwen3-30B-A3B | GPT-OSS-20B | OLMoE-1B-7B-0125-Inst |
|---|---|---|---|
| 2w（ud）Spec_POS − within-token-id UPOS shuffle | survives（47/1/0/0） | null-family-dependent（12/11/0/1） | survives（16/0/0/0） |
| 4n（flores）ΔG' = G(true next) − G(input) | below-null（0/5/43/0） | below-null（0/7/17/0） | below-null（0/0/15/1） |
| 1（ud）R1 on UD | survives（48/0/0/0） | null-family-dependent（15/9/0/0） | survives（15/0/0/1） |
| 3（ud）rep1 on UD | survives（43/3/2/0） | geometry（7/16/1/0） | null-family-dependent（10/4/0/2） |
| 4（ud）ΔG on UD | below-null（1/1/46/0） | below-null（1/5/18/0） | below-null（0/0/15/1） |

括号内为 above / within / below / split 层数。

## 2. 代表层数值（l* = ⌊L/2⌋ 与末层；T vs 零模型 8-draw 均值 [min, max]）

### 结论 1：R1 token-id purity − id-shuffle floor（flores）

| 模型 | 层 | T | N_A | N_B | T/mean(N_B) | 原值 T / N_B 均值 | 地板 T |
|---|---|---|---|---|---|---|---|
| Qwen3-30B-A3B | 24 | 0.146 | 0.067 [0.055, 0.076] | 0.109 [0.094, 0.118] | 1.33 | 0.310 / 0.255 | 0.164 |
| Qwen3-30B-A3B | 47 | 0.396 | 0.111 [0.073, 0.134] | 0.195 [0.147, 0.266] | 2.02 | 0.586 / 0.365 | 0.191 |
| Qwen3-30B-A3B | 层剖面 Spearman | T vs N_B 0.88 | T vs N_A 0.79 | | 中位 T/mean(N_B) 全层 1.68 | | |
| GPT-OSS-20B | 12 | 0.176 | 0.065 [0.049, 0.079] | 0.105 [0.068, 0.129] | 1.68 | 0.399 / 0.403 | 0.223 |
| GPT-OSS-20B | 23 | 0.098 | 0.122 [0.065, 0.173] | 0.115 [0.059, 0.151] | 0.85 | 0.758 / 0.654 | 0.660 |
| GPT-OSS-20B | 层剖面 Spearman | T vs N_B 0.85 | T vs N_A 0.42 | | 中位 T/mean(N_B) 全层 1.40 | | |
| OLMoE-1B-7B-0125-Inst | 8 | 0.257 | 0.074 [0.061, 0.082] | 0.191 [0.163, 0.218] | 1.34 | 0.412 / 0.342 | 0.155 |
| OLMoE-1B-7B-0125-Inst | 15 | 0.330 | 0.084 [0.078, 0.094] | 0.187 [0.164, 0.208] | 1.76 | 0.462 / 0.314 | 0.132 |
| OLMoE-1B-7B-0125-Inst | 层剖面 Spearman | T vs N_B 0.81 | T vs N_A 0.42 | | 中位 T/mean(N_B) 全层 1.72 | | |

### 结论 2：Spec_POS − UPOS-shuffle floor（ud）

| 模型 | 层 | T | N_A | N_B | T/mean(N_B) | 原值 T / N_B 均值 | 地板 T |
|---|---|---|---|---|---|---|---|
| Qwen3-30B-A3B | 24 | 0.090 | 0.012 [0.006, 0.018] | 0.038 [0.025, 0.046] | 2.38 | 0.452 / 0.416 | 0.362 |
| Qwen3-30B-A3B | 47 | 0.273 | 0.031 [0.018, 0.045] | 0.104 [0.063, 0.144] | 2.63 | 0.630 / 0.473 | 0.357 |
| Qwen3-30B-A3B | 层剖面 Spearman | T vs N_B 0.94 | T vs N_A 0.86 | | 中位 T/mean(N_B) 全层 2.43 | | |
| GPT-OSS-20B | 12 | 0.065 | 0.016 [0.006, 0.030] | 0.026 [0.008, 0.043] | 2.51 | 0.614 / 0.606 | 0.549 |
| GPT-OSS-20B | 23 | 0.015 | 0.017 [0.001, 0.033] | 0.014 [0.003, 0.027] | 1.12 | 0.486 / 0.643 | 0.470 |
| GPT-OSS-20B | 层剖面 Spearman | T vs N_B 0.93 | T vs N_A 0.71 | | 中位 T/mean(N_B) 全层 1.73 | | |
| OLMoE-1B-7B-0125-Inst | 8 | 0.313 | 0.027 [0.017, 0.036] | 0.120 [0.112, 0.126] | 2.61 | 0.531 / 0.430 | 0.218 |
| OLMoE-1B-7B-0125-Inst | 15 | 0.243 | 0.023 [0.019, 0.031] | 0.105 [0.081, 0.133] | 2.32 | 0.484 / 0.399 | 0.241 |
| OLMoE-1B-7B-0125-Inst | 层剖面 Spearman | T vs N_B 0.63 | T vs N_A -0.01 | | 中位 T/mean(N_B) 全层 2.34 | | |

### 结论 3：rep1 − random-pair floor（flores）

| 模型 | 层 | T | N_A | N_B | T/mean(N_B) | 原值 T / N_B 均值 | 地板 T |
|---|---|---|---|---|---|---|---|
| Qwen3-30B-A3B | 24 | 0.204 | 0.083 [0.077, 0.093] | 0.131 [0.126, 0.136] | 1.56 | 0.236 / 0.169 | 0.032 |
| Qwen3-30B-A3B | 47 | 0.011 | 0.108 [0.098, 0.118] | 0.076 [0.050, 0.095] | 0.15 | 0.080 / 0.122 | 0.069 |
| Qwen3-30B-A3B | 层剖面 Spearman | T vs N_B 0.93 | T vs N_A 0.41 | | 中位 T/mean(N_B) 全层 1.59 | | |
| GPT-OSS-20B | 12 | 0.373 | 0.166 [0.158, 0.176] | 0.259 [0.230, 0.293] | 1.44 | 0.472 / 0.389 | 0.099 |
| GPT-OSS-20B | 23 | 0.107 | 0.125 [0.095, 0.142] | 0.159 [0.129, 0.190] | 0.67 | 0.452 / 0.517 | 0.346 |
| GPT-OSS-20B | 层剖面 Spearman | T vs N_B 0.81 | T vs N_A 0.48 | | 中位 T/mean(N_B) 全层 1.19 | | |
| OLMoE-1B-7B-0125-Inst | 8 | 0.135 | 0.096 [0.089, 0.100] | 0.099 [0.092, 0.116] | 1.36 | 0.163 / 0.135 | 0.028 |
| OLMoE-1B-7B-0125-Inst | 15 | 0.108 | 0.090 [0.080, 0.099] | 0.070 [0.062, 0.078] | 1.55 | 0.141 / 0.100 | 0.032 |
| OLMoE-1B-7B-0125-Inst | 层剖面 Spearman | T vs N_B 0.85 | T vs N_A 0.22 | | 中位 T/mean(N_B) 全层 1.38 | | |

### 结论 4：ΔG = G(pred next) − G(input), bits（flores）

| 模型 | 层 | T | N_A | N_B | T/mean(N_B) | 原值 T / N_B 均值 | 地板 T |
|---|---|---|---|---|---|---|---|
| Qwen3-30B-A3B | 24 | -0.287 | -0.123 [-0.140, -0.109] | -0.216 [-0.255, -0.180] | 1.33 | 0.268 / 0.066 | 0.555 |
| Qwen3-30B-A3B | 47 | -0.277 | -0.049 [-0.081, -0.024] | -0.155 [-0.194, -0.091] | 1.78 | 1.275 / 0.682 | 1.552 |
| Qwen3-30B-A3B | 层剖面 Spearman | T vs N_B 0.84 | T vs N_A 0.79 | | 中位 T/mean(N_B) 全层 1.35 | | |
| GPT-OSS-20B | 12 | -0.106 | -0.095 [-0.109, -0.071] | -0.106 [-0.123, -0.084] | 1.00 | 0.208 / 0.168 | 0.314 |
| GPT-OSS-20B | 23 | 0.015 | -0.094 [-0.116, -0.012] | -0.033 [-0.067, 0.016] | -0.47 | 0.479 / 0.214 | 0.463 |
| GPT-OSS-20B | 层剖面 Spearman | T vs N_B 0.97 | T vs N_A 0.82 | | 中位 T/mean(N_B) 全层 1.34 | | |
| OLMoE-1B-7B-0125-Inst | 8 | -0.488 | -0.074 [-0.106, -0.046] | -0.348 [-0.383, -0.289] | 1.40 | 0.735 / 0.429 | 1.223 |
| OLMoE-1B-7B-0125-Inst | 15 | -0.270 | 0.028 [-0.006, 0.052] | -0.100 [-0.162, -0.047] | 2.70 | 0.913 / 0.616 | 1.183 |
| OLMoE-1B-7B-0125-Inst | 层剖面 Spearman | T vs N_B 0.95 | T vs N_A 0.79 | | 中位 T/mean(N_B) 全层 1.50 | | |

### 结论 2w：Spec_POS − within-id floor（ud）

| 模型 | 层 | T | N_A | N_B | T/mean(N_B) | 原值 T / N_B 均值 | 地板 T |
|---|---|---|---|---|---|---|---|
| Qwen3-30B-A3B | 24 | 0.007 | 0.001 [0.000, 0.001] | 0.003 [0.002, 0.004] | 2.49 | 0.452 / 0.416 | 0.445 |
| Qwen3-30B-A3B | 47 | 0.021 | 0.003 [0.002, 0.005] | 0.009 [0.006, 0.010] | 2.34 | 0.630 / 0.473 | 0.610 |
| Qwen3-30B-A3B | 层剖面 Spearman | T vs N_B 0.91 | T vs N_A 0.88 | | 中位 T/mean(N_B) 全层 2.53 | | |
| GPT-OSS-20B | 12 | 0.003 | 0.001 [0.000, 0.002] | 0.002 [0.001, 0.003] | 1.49 | 0.614 / 0.606 | 0.611 |
| GPT-OSS-20B | 23 | 0.002 | 0.001 [-0.000, 0.002] | 0.001 [0.000, 0.002] | 2.16 | 0.486 / 0.643 | 0.484 |
| GPT-OSS-20B | 层剖面 Spearman | T vs N_B 0.83 | T vs N_A 0.57 | | 中位 T/mean(N_B) 全层 1.57 | | |
| OLMoE-1B-7B-0125-Inst | 8 | 0.017 | 0.002 [0.001, 0.002] | 0.008 [0.007, 0.009] | 2.01 | 0.531 / 0.430 | 0.515 |
| OLMoE-1B-7B-0125-Inst | 15 | 0.021 | 0.002 [0.001, 0.003] | 0.011 [0.009, 0.014] | 1.94 | 0.484 / 0.399 | 0.463 |
| OLMoE-1B-7B-0125-Inst | 层剖面 Spearman | T vs N_B 0.87 | T vs N_A 0.95 | | 中位 T/mean(N_B) 全层 2.01 | | |

结论 4 表中"原值"列为 G(预测下一) T / N_B，"地板"列为 G(输入) T（bit）。

## 3. 结论 4：交叉层（ΔG > 0 的首层 / 持续交叉层；无 = None）

| 模型 | 语料 | 读数 | T 首 / 持续 | N_A 8 draws 持续 | N_B 8 draws 持续 | 判定 |
|---|---|---|---|---|---|---|
| Qwen3-30B-A3B | flores | 预测下一 | None / None | [None, None, None, None, None, None, None, None] | [None, None, None, None, None, None, None, None] | T no crossover |
| Qwen3-30B-A3B | flores | 真实下一 | None / None | [None, None, None, None, None, None, None, None] | [None, None, None, None, None, None, None, None] | T no crossover |
| Qwen3-30B-A3B | ud | 预测下一 | None / None | [None, None, None, 47, None, None, None, None] | [None, None, None, None, None, None, None, None] | T no crossover |
| Qwen3-30B-A3B | ud | 真实下一 | None / None | [None, None, None, None, None, None, None, None] | [None, None, None, None, None, None, None, None] | T no crossover |
| GPT-OSS-20B | flores | 预测下一 | 21 / 23 | [None, None, None, None, None, None, None, None] | [None, None, None, None, None, None, 23, None] | same |
| GPT-OSS-20B | flores | 真实下一 | None / None | [None, None, None, None, None, None, None, None] | [None, None, None, None, None, None, None, None] | T no crossover |
| GPT-OSS-20B | ud | 预测下一 | 21 / 21 | [None, None, None, None, None, None, None, None] | [23, 23, 22, 23, 21, 21, 22, 21] | same |
| GPT-OSS-20B | ud | 真实下一 | None / None | [None, None, None, None, None, None, None, None] | [None, None, None, None, None, None, None, None] | T no crossover |
| OLMoE-1B-7B-0125-Inst | flores | 预测下一 | None / None | [14, 14, 14, 14, None, 14, 14, None] | [None, None, None, None, None, None, None, None] | T no crossover |
| OLMoE-1B-7B-0125-Inst | flores | 真实下一 | None / None | [None, None, None, None, None, None, None, None] | [None, None, None, None, None, None, None, None] | T no crossover |
| OLMoE-1B-7B-0125-Inst | ud | 预测下一 | None / None | [None, None, None, 15, None, 15, None, None] | [None, None, None, None, None, None, None, None] | T no crossover |
| OLMoE-1B-7B-0125-Inst | ud | 真实下一 | None / None | [None, None, None, None, None, None, None, None] | [None, None, None, None, None, None, None, None] | T no crossover |

G（bit）原值：

| 模型 | 层 | G_in T / N_A / N_B | G_pred T / N_A / N_B | G_nxt T / N_A / N_B |
|---|---|---|---|---|
| Qwen3-30B-A3B | 0 | 2.69 / 1.31 / 1.91 | 0.81 / 0.10 / 0.37 | 0.46 / -0.05 / 0.12 |
| Qwen3-30B-A3B | 24 | 0.56 / -0.05 / 0.28 | 0.27 / -0.17 / 0.07 | 0.06 / -0.27 / -0.08 |
| Qwen3-30B-A3B | 47 | 1.55 / 0.31 / 0.84 | 1.27 / 0.26 / 0.68 | 0.91 / 0.09 / 0.40 |
| GPT-OSS-20B | 0 | 2.11 / 1.30 / 1.68 | 0.61 / 0.17 / 0.37 | 0.30 / 0.02 / 0.15 |
| GPT-OSS-20B | 12 | 0.31 / 0.09 / 0.27 | 0.21 / -0.01 / 0.17 | 0.07 / -0.11 / 0.04 |
| GPT-OSS-20B | 23 | 0.46 / 0.28 / 0.25 | 0.48 / 0.19 / 0.21 | 0.31 / 0.05 / 0.12 |
| OLMoE-1B-7B-0125-Inst | 0 | 0.81 / 1.17 / 0.44 | 0.21 / -0.01 / 0.03 | 0.04 / -0.11 / -0.09 |
| OLMoE-1B-7B-0125-Inst | 8 | 1.22 / 0.13 / 0.78 | 0.73 / 0.05 / 0.43 | 0.37 / -0.17 / 0.12 |
| OLMoE-1B-7B-0125-Inst | 15 | 1.18 / 0.11 / 0.72 | 0.91 / 0.14 / 0.62 | 0.52 / -0.10 / 0.29 |

## 4. 阳性对照

| 模型 | 两遍一致 | hook fp32 / T-vs-model | N_B 校准负载 TV 均值（最大） | 测量负载 TV N_B vs T（flores 均值） | T 最大负载 / 均匀（flores 中位） | 置换对照 |·|≤.01 格比例（R1/R2/R2w/R3） | 置换 G 最大（in / pred） | 第 0 层 R1 T / 地板 |
|---|---|---|---|---|---|---|---|---|
| Qwen3-30B-A3B | 1.0000 | 0.9931 / 1.0000 | 0.0105（0.0247） | 0.107 | 6.55 | 1.000 / 1.000 / 1.000 / 1.000 | -0.148 / -0.163 | 0.726 / 0.159 |
| GPT-OSS-20B | 1.0000 | 0.9983 / 1.0000 | 0.0085（0.0559） | 0.063 | 4.61 | 1.000 / 1.000 / 1.000 / 1.000 | -0.043 / -0.042 | 0.888 / 0.240 |
| OLMoE-1B-7B-0125-Inst | 1.0000 | 0.9993 / 1.0000 | 0.0054（0.0182） | 0.077 | 2.47 | 1.000 / 1.000 / 1.000 / 1.000 | -0.236 / -0.226 | 0.385 / 0.158 |

语料规模：Qwen3-30B-A3B flores 26255 / ud 59392 token，UD 词末 token 48373（保留 UPOS 17 类），R1 合格 token 17415 / id 730；GPT-OSS-20B flores 25536 / ud 56628 token，UD 词末 token 48388（保留 UPOS 17 类），R1 合格 token 16566 / id 733；OLMoE-1B-7B-0125-Inst flores 26091 / ud 58891 token，UD 词末 token 48610（保留 UPOS 17 类），R1 合格 token 17042 / id 792

## 5. 补充读数（只报；T / N_A 均值 / N_B 均值，l* 与末层）

| 模型 | 读数 | l* | 末层 |
|---|---|---|---|
| Qwen3-30B-A3B | VS1（flores） | 0.117 / 0.063 / 0.084 | 0.267 / 0.088 / 0.139 |
| Qwen3-30B-A3B | VSK（flores） | 0.254 / 0.145 / 0.181 | 0.464 / 0.187 / 0.266 |
| Qwen3-30B-A3B | R3any（flores） | 0.978 / 0.861 / 0.949 | 0.767 / 0.923 / 0.898 |
| Qwen3-30B-A3B | R3any_floor（flores） | 0.683 / 0.610 / 0.776 | 0.601 / 0.741 / 0.748 |
| Qwen3-30B-A3B | R3ov（flores） | 0.463 / 0.260 / 0.387 | 0.280 / 0.341 / 0.329 |
| Qwen3-30B-A3B | R3ov_floor（flores） | 0.164 / 0.122 / 0.190 | 0.195 / 0.185 / 0.198 |
| Qwen3-30B-A3B | VS1_in（flores） | 0.116 / 0.065 / 0.084 | 0.265 / 0.089 / 0.140 |
| Qwen3-30B-A3B | VS1_pred（flores） | 0.057 / 0.041 / 0.047 | 0.155 / 0.063 / 0.085 |
| Qwen3-30B-A3B | VS1_nxt（flores） | 0.066 / 0.051 / 0.056 | 0.163 / 0.071 / 0.090 |
| Qwen3-30B-A3B | R2ent（ud） | 0.659 / 0.794 / 0.659 | 0.427 / 0.652 / 0.565 |
| GPT-OSS-20B | VS1（flores） | 0.144 / 0.106 / 0.142 | 0.307 / 0.150 / 0.163 |
| GPT-OSS-20B | VSK（flores） | 0.273 / 0.225 / 0.268 | 0.408 / 0.260 / 0.290 |
| GPT-OSS-20B | R3any（flores） | 0.983 / 0.856 / 0.981 | 0.953 / 0.911 / 0.981 |
| GPT-OSS-20B | R3any_floor（flores） | 0.777 / 0.529 / 0.850 | 0.850 / 0.761 / 0.942 |
| GPT-OSS-20B | R3ov（flores） | 0.649 / 0.386 / 0.603 | 0.670 / 0.447 / 0.630 |
| GPT-OSS-20B | R3ov_floor（flores） | 0.318 / 0.170 / 0.355 | 0.507 / 0.299 / 0.507 |
| GPT-OSS-20B | VS1_in（flores） | 0.136 / 0.109 / 0.143 | 0.307 / 0.153 / 0.164 |
| GPT-OSS-20B | VS1_pred（flores） | 0.092 / 0.071 / 0.092 | 0.184 / 0.100 / 0.115 |
| GPT-OSS-20B | VS1_nxt（flores） | 0.098 / 0.078 / 0.092 | 0.172 / 0.099 / 0.121 |
| GPT-OSS-20B | R2ent（ud） | 0.575 / 0.867 / 0.538 | 0.610 / 0.586 / 0.361 |
| OLMoE-1B-7B-0125-Inst | VS1（flores） | 0.212 / 0.091 / 0.150 | 0.247 / 0.088 / 0.143 |
| OLMoE-1B-7B-0125-Inst | VSK（flores） | 0.522 / 0.239 / 0.371 | 0.501 / 0.237 / 0.336 |
| OLMoE-1B-7B-0125-Inst | R3any（flores） | 0.847 / 0.923 / 0.910 | 0.851 / 0.920 / 0.890 |
| OLMoE-1B-7B-0125-Inst | R3any_floor（flores） | 0.560 / 0.693 / 0.700 | 0.595 / 0.717 / 0.710 |
| OLMoE-1B-7B-0125-Inst | R3ov（flores） | 0.348 / 0.320 / 0.329 | 0.335 / 0.317 / 0.298 |
| OLMoE-1B-7B-0125-Inst | R3ov_floor（flores） | 0.156 / 0.150 / 0.165 | 0.166 / 0.160 / 0.168 |
| OLMoE-1B-7B-0125-Inst | VS1_in（flores） | 0.210 / 0.094 / 0.151 | 0.245 / 0.090 / 0.144 |
| OLMoE-1B-7B-0125-Inst | VS1_pred（flores） | 0.121 / 0.072 / 0.094 | 0.158 / 0.078 / 0.109 |
| OLMoE-1B-7B-0125-Inst | VS1_nxt（flores） | 0.105 / 0.066 / 0.084 | 0.139 / 0.071 / 0.097 |
| OLMoE-1B-7B-0125-Inst | R2ent（ud） | 0.680 / 0.913 / 0.705 | 0.668 / 0.869 / 0.764 |
