## 模型级（每 run 一个数；主数据 = 锚点 S，3.2B，12 层平均）

| # | 读数 | 6 个 init 的范围 | 重跑差 | 换顺序差 | step 0 | R_m | 判定 |
|---|---|---|---|---|---|---|---|
| 1 | router saturation sat(50M→T), k=8, mean over layers | 0.253–0.271 | 0.003 | 0.009 | 0.143 | 0.146 | 重现 |
| 1k1 | router saturation sat(50M→T), k=1, mean over layers | 0.089–0.099 | 0.001 | 0.004 | 0.032 | 0.172 | 重现 |
| 2 | share of ordered expert pairs with co-activation ≥ .5 | 0.013–0.013 | 0.000 | 0.000 | 0.023 | 0.057 | 重现 |
| 3 | expert mean of max genre lift | 1.478–1.497 | 0.018 | 0.019 | 1.820 | 0.058 | 重现 |
| 6 | UPOS-class top-1 routing entropy / ln64 (token-weighted) | 0.690–0.710 | 0.001 | 0.006 | 0.760 | 0.339 | 训练不改变此量 |
| 7 | word-form purity (top-1) | 0.599–0.615 | 0.003 | 0.001 | 0.345 | 0.061 | 重现 |
| 7t | within-run top-10 form table Jaccard, 400M vs T | 0.307–0.321 | 0.006 | 0.007 | — | — | 无地板（只报原值） |
| 13spec | DBES S_spec | 0.240–0.254 | 0.006 | 0.005 | 0.550 | 0.047 | 重现 |
| 13reff | DBES R_eff | 0.760–0.774 | 0.009 | 0.005 | 0.856 | 0.159 | 重现 |
| 13iso | DBES S_iso | 0.087–0.099 | 0.000 | 0.002 | 0.105 | 1.064 | 训练不改变此量 |
| 8 | Antoine Spec_POS, mean over layers (E172) | 0.439–0.452 | 0.001 | 0.006 | 0.386 | 0.238 | 重现 |

## 类别级（与专家编号无关的剖面；跨 run Spearman）

| # | 剖面 | ρ_init 均值（范围） | ρ_重跑 | ρ_换顺序 | ρ_step0 | q | 判定 |
|---|---|---|---|---|---|---|---|
| 1 | per-UPOS saturation at 50M (floor: at step 0) | 0.700（0.61–0.80） | 0.919 | 0.86, 0.87 | 0.159 | 0.712 | 重现 |
| 3 | per-(layer, genre) routing deviation (60 values) | 0.903（0.82–0.95） | 0.981 | 0.97, 0.97 | 0.899 | — | 地板≈上限，此级不可判 |
| 6 | per-UPOS top-1 routing entropy | 0.734（0.63–0.80） | 0.954 | 0.86, 0.90 | 0.410 | 0.596 | 部分 |
| 7 | per-word-form purity (1,827 forms) | 0.321（0.29–0.33） | 0.685 | 0.54, 0.57 | 0.334 | -0.036 | 不重现 |
| 13spec | DBES S_spec per genre (5) | 0.947（0.90–1.00） | 0.900 | 1.00, 0.90 | 0.947 | — | 地板≈上限，此级不可判 |
| 13iso | DBES 1−cos per genre pair (10) | 0.971（0.93–1.00） | 0.988 | 0.96, 0.98 | 0.914 | — | 地板≈上限，此级不可判 |
| 8 | Antoine Spec_POS profile (E172; floor = 1 step-0 pair) | 0.648（深层 0.62–0.84） | 0.927 | 0.83 | 0.207 | 0.612 | 部分 |

## 专家级（Hungarian 配对后；按文档对半交叉拟合）

| # | 读数 | ρ_init 均值（范围） | ρ_重跑 | ρ_换顺序 | ρ_step0 | q | 判定 |
|---|---|---|---|---|---|---|---|
| 1 | per-expert saturation (50M→T); floor: 0→T | 0.271（0.22–0.32） | 0.894 | 0.71, 0.75 | 0.016 | 0.290 | 不重现 |
| 2 | matched co-activation matrix (off-diagonal), Spearman | 0.637（0.63–0.65） | 0.888 | 0.80, 0.80 | 0.597 | 0.139 | 不重现 |
| 3 | matched per-expert genre lift (5), Pearson | 0.523（0.48–0.55） | 0.860 | 0.75, 0.72 | 0.110 | 0.550 | 部分 |
| 6 | matched P(e|c) per UPOS class, mean Pearson | 0.554（0.54–0.57） | 0.906 | 0.85, 0.84 | 0.674 | -0.517 | 不重现 |
| 7 | matched top-10 word-form table, Jaccard | 0.081（0.07–0.09） | 0.416 | 0.28, 0.28 | 0.010 | 0.176 | 重跑也低于 .5（读数本身噪声大） |
| 8 | matched per-expert KL(P(c|e)||P(c)), Pearson | 0.648（0.61–0.68） | 0.906 | 0.78, 0.79 | 0.367 | 0.521 | 部分 |

配对后 top-8 槽位重合（层平均）：init 0.422，换顺序 0.612，重跑 0.707，step 0 0.260

## 原文那句结论：9 个 run 逐个判定（末列 POST-HOC：同一规则用在 6 个未训练 step-0 模型上）

| # | 结论（判定规则） | 几/9 | 判否的 run | step 0 几/6 |
|---|---|---|---|---|
| 1a | OLMoE: at ~1% of training, up to ~60% of top-8 routing saturated (layer max ≥ .5 at 50M) | 0/9 | 全部 | — |
| 1b | OLMoE: top-1 saturates slower than top-8 (raw layer means at 50M) | 9/9 | — | — |
| 1c | OLMoE: later layers saturate earlier (Spearman(layer, sat) > 0 over L1–L11) | 9/9 | — | — |
| 1d | OLMoE: layer 0 saturates slowest (sat_L0 < min L1–L11) | 0/9 | 全部 | — |
| 2 | OLMoE: no strong co-activation, few exceptions (every layer ≤ 1% ordered pairs ≥ .5) | 0/9 | 全部 | 0/6 |
| 3 | OLMoE/Mixtral: domain specialisation present (some (E, genre) lift ≥ 2) | 9/9 | — | 6/6 |
| 6 | ST-MoE: decoder experts don't specialise (class entropy / ln64 ≥ .9) | 0/9 | 全部 | 0/6 |
| 7a | BASE/OpenMoE: input token decides the expert (form purity ≥ .5) | 9/9 | — | 0/6 |
| 7b | OpenMoE: routing fixed by end of warmup (top-10 Jaccard 400M vs T ≥ .5) | 0/9 | 全部 | — |
| 8 | Antoine: Spec_POS above uniform by ≥ 25 pp (POST-HOC threshold = lower end of the paper's range) | 9/9 | — | — |
| 13 | DBES: modular (S_iso ≥ .5; threshold from DBES table 1 range) | 0/9 | 全部 | 0/6 |

## 自然流复核（113,118 个连续词；init = I0–I4，floor = 1 对）

重算路由与缓存在锚点上的一致（层最小）：I0D0@3999793152 top8 0.9902 / top1 0.9861；I1D0@3999793152 top8 0.9890 / top1 0.9865；I2D0@3999793152 top8 0.9901 / top1 0.9865；I3D0@3999793152 top8 0.9892 / top1 0.9860；I4D0@3200000000 top8 0.9996 / top1 0.9996；I0D1@3999793152 top8 0.9907 / top1 0.9866；I1D1@3999793152 top8 0.9898 / top1 0.9852；I4D0R@3200000000 top8 0.9997 / top1 0.9996；I0D0@0 top8 0.9952 / top1 0.9919；I1D0@0 top8 0.9950 / top1 0.9922

| # | 模型级读数 | init 范围 | 重跑差 | step 0 | R_m |
|---|---|---|---|---|---|
| 2 | co-activation ≥ .5 share | 0.013–0.015 | 0.001 | 0.021 | 0.356 |
| 3 | expert mean of max genre lift | 1.373–1.394 | 0.012 | 1.658 | 0.074 |
| 7 | word-form purity | 0.601–0.609 | 0.004 | 0.327 | 0.031 |
| 13spec | S_spec | 0.163–0.190 | 0.002 | 0.519 | 0.081 |
| 13reff | R_eff | 0.687–0.726 | 0.001 | 0.856 | 0.271 |
| 13iso | S_iso | 0.073–0.084 | 0.002 | 0.084 | 1.877 |

| # | 类别级剖面 | ρ_init（范围） | ρ_重跑 | ρ_step0 | q | 判定 |
|---|---|---|---|---|---|---|
| 3 | per-(layer, genre) deviation | 0.895（0.81–0.94） | 0.984 | 0.881 | 0.138 | 不重现 |
| 7 | per-form purity | 0.322（0.32–0.33） | 0.681 | 0.372 | -0.161 | 不重现 |
| 13spec | S_spec per genre | 1.000（1.00–1.00） | 1.000 | 0.900 | 1.000 | 重现 |
| 13iso | 1−cos per genre pair | 0.988（0.98–1.00） | 1.000 | 0.927 | — | 地板≈上限，此级不可判 |

自然流逐 run 定性判定（8 个 run）：#2 0/8；#3 8/8；#7a 8/8；#13 0/8

## POST-HOC（看过第一版后加的描述，不进判定）

- I0D0: 层最大 k=8 饱和首次 ≥ .5 的 checkpoint = 200000000；1.6B 处层最大 = 0.832；50M 处 L0 = 0.313（step 0 处 L0 = 0.280）
- I1D0: 层最大 k=8 饱和首次 ≥ .5 的 checkpoint = 200000000；1.6B 处层最大 = 0.822；50M 处 L0 = 0.307（step 0 处 L0 = 0.279）
- I2D0: 层最大 k=8 饱和首次 ≥ .5 的 checkpoint = 200000000；1.6B 处层最大 = 0.822；50M 处 L0 = 0.309（step 0 处 L0 = 0.280）
- I3D0: 层最大 k=8 饱和首次 ≥ .5 的 checkpoint = 200000000；1.6B 处层最大 = 0.825；50M 处 L0 = 0.322（step 0 处 L0 = 0.288）
- I4D0: 层最大 k=8 饱和首次 ≥ .5 的 checkpoint = 200000000；1.6B 处层最大 = 0.827；50M 处 L0 = 0.307（step 0 处 L0 = 0.274）
- I5D0: 层最大 k=8 饱和首次 ≥ .5 的 checkpoint = 200000000；1.6B 处层最大 = 0.826；50M 处 L0 = 0.317（step 0 处 L0 = 0.278）
- I0D1: 层最大 k=8 饱和首次 ≥ .5 的 checkpoint = 200000000；1.6B 处层最大 = 0.833；50M 处 L0 = 0.306（step 0 处 L0 = 0.277）
- I1D1: 层最大 k=8 饱和首次 ≥ .5 的 checkpoint = 200000000；1.6B 处层最大 = 0.825；50M 处 L0 = 0.304（step 0 处 L0 = 0.276）
- I4D0R: 层最大 k=8 饱和首次 ≥ .5 的 checkpoint = 200000000；1.6B 处层最大 = 0.842；50M 处 L0 = 0.317（step 0 处 L0 = 0.287）
