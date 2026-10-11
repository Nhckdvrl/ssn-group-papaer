# E123 独立原始数据、自然文本与政策审计（2026-10-12）

**8/8完成。** 四checkpoint各discovery16→confirmation32，192contexts/130,560评分；85条件×8query全部保留。作者analysis在独立raw派生封存后才读，15,144个数值比较最大误差 0。这里核对C21–23的自然功能/输出namespace政策证据，不自动改变grade或研究状态。

按AGENTS→EXECUTION §5独立会话执行；先读91374879冻结卡和完整科学源/材料源，CPU独立解析实际comments/gold/tokens/strict-past边，再从每个完整run raw算均值/paired CI。期间收到作者运行状态与部分结果方向简报，不冒称完全方向盲。没有独立GPU重跑、全部权重字节重哈希或进程内存复验；cache/层消费核对基于冻结代码和逐层运行记录。

## 完整计数与数值检查

| 批 | contexts | 评分 | 层数 | 作者数值比较 | GPU小时 |
|---|---:|---:|---:|---:|---:|
| qwen3_discovery | 16 | 10880 | 36 | 1893, max0 | 0.113160 |
| qwen3_confirmation | 32 | 21760 | 36 | 1893, max0 | 0.209504 |
| mistral_discovery | 16 | 10880 | 32 | 1893, max0 | 0.121809 |
| mistral_confirmation | 32 | 21760 | 32 | 1893, max0 | 0.235970 |
| llama_discovery | 16 | 10880 | 32 | 1893, max0 | 0.107309 |
| llama_confirmation | 32 | 21760 | 32 | 1893, max0 | 0.200534 |
| qwen14_discovery | 16 | 10880 | 40 | 1893, max0 | 0.442881 |
| qwen14_confirmation | 32 | 21760 | 40 | 1893, max0 | 0.814589 |

新报告 `e123_wave_report.py` 的full-vocabulary/other-source-word（含A/B分别）全部聚合与paired对比另从raw及已封独立full输出重建后，再看作者full_output_summary；8×960=7680个新报告数值比较最大0。原primary与新full报告共22824个对比。新报告只汇总输出，不改原科学源/primary；Source平均权重相同，within未混入。

总GPU运行记录 2.245757069 小时；独立重构 2880 实际prefix token流、6336 mask集，核 130560 条query gold、120960 次记录层调用。full/split最大5.7220459e-05、cache/policy no-op最大0、独立graph-zero最大0。各run SHA、模型revision、85条件完整/finite检查见JSON。主源SHA `95a574892e7609a25146f730f7843d176fe27487353f2ad7c9fa7fd01971e9a5`、材料SHA `f02104a87b9e67dec413c9c642c107a0f90a7d1046421306e8c4202c59da94ec`。

原指标context-bootstrap10,000/seed910；另外20,000/seed123012的独立paired重采样保留JSON。queries不是独立统计单位；私有方向n8/n16。完整85条件candidate/full-argmax/正确label margin、12 policy、A/B、same/opposite convention、两个namespace gain交互、全部world-owner、private方向及A-code signed/abs/within均保留，包括零、负和CI跨0。

## 原文、gold、split与反事实真值

沿SetFit/sst5固定revision e51bdcd8cd3a30da231967c1a249ba59361279a3，原始Movie review label0/4映射negative/positive。三个本地Arrow字节SHA与已封E121官方public train/dev/test逐record核对资产一致；本轮另逐条核text/gold与label_text，未重新下载相同冻结release。train极性唯一文本2377、validation304、test678，train重复3且无冲突gold。demo按text SHA末hex奇偶分discovery/confirmation，query来自官方validation/test，排除train原文且confirmation另排validation。5–64token筛选/同几何bin不读模型输出。demo/query同context各16/8唯一，discovery→confirmation原文交集0，context间允许复用文本。

A=sentiment×pA；B origin/within=−pA，cross=+pA。cross跨极性、within同极性移动都为8B input无fixed point的双射。A raw/label、B label stream、Source名、demo位置、评论多重集不变；全3world×2namespace实际token长度/角色/anchor/answer-region一致，变化只在B comment或far label位置。两Actor gold独立从官方标签及private convention推导，B far按自己的pass/flag候选计分，A始终no/yes。无把B反约定的正确答案误记为A gold。

## 同缓存、对称图与消费

每world×namespace×policy只形成一个prefix，两Actor/两query scope共享此cache。query deepcopy keys/values指针不同、原cache seq长度保持；全部18个prefix配置在36/32/32/40层逐层消费同冻结mask，每层计数=该批n。strict past只禁止不同Source过去sender，self/同源保留。target限制answer word＋实际separator→own label；all-cross限制所有历史cross-source访问。两policy边数量/attention mass不同、softmax重归一化/后继状态活演化；保留其它graph access不意味着其它激活固定。各single三policy CPU图完全no-op，实际首contextcache no-op亦检查。

requested-source-only gate作用每个query位置，保留HEAD/own-source/query自己的因果访问；双向all-cross+gate时改变B worlds对A数值0。这里仅B真值变化，不能冒称已做A世界变化对B的对称graph-zero。Mistral真实分块序列word+3separator、每源32个answer sender位置，其余模型word+1、每源16；不称Mistral实际流等同字面完整字符串编码。

## 全policy均值准确率（%，95%CI）

primary仅origin/cross两world×两Actor×8query（每context32预测），within为次控制。`both`是请求均值，不是两Actor同时正确率、完整函数共同成功或Source ranking。origin/cross分别是同一sentiment criterion的反/同私人约定，不是两不同criterion。

| 批/namespace | normal/native | target/native | all/native | normal/gate | target/gate | all/gate |
|---|---:|---:|---:|---:|---:|---:|
| qwen3_discovery/shared | 85.55 [81.45, 89.65] | 92.58 [89.45, 95.70] | 75.00 [73.05, 76.95] | 81.45 [77.15, 85.55] | 94.14 [91.02, 96.88] | 93.95 [91.02, 96.68] |
| qwen3_discovery/far | 95.51 [93.16, 97.66] | 94.53 [91.21, 97.46] | 95.12 [92.58, 97.46] | 95.31 [91.60, 98.44] | 95.70 [92.97, 98.24] | 93.75 [90.82, 96.68] |
| qwen3_confirmation/shared | 84.86 [82.62, 87.01] | 92.19 [90.04, 94.14] | 75.00 [74.02, 76.07] | 84.47 [81.74, 87.21] | 93.85 [91.41, 96.09] | 94.34 [92.09, 96.29] |
| qwen3_confirmation/far | 94.24 [91.80, 96.39] | 94.34 [91.80, 96.48] | 94.34 [92.09, 96.48] | 94.34 [91.70, 96.58] | 94.63 [92.09, 96.78] | 93.16 [90.82, 95.41] |
| mistral_discovery/shared | 87.50 [84.77, 90.43] | 93.95 [91.41, 96.48] | 75.59 [73.63, 77.54] | 94.73 [92.19, 97.07] | 97.27 [95.51, 98.83] | 95.70 [92.19, 98.44] |
| mistral_discovery/far | 98.63 [97.46, 99.61] | 98.63 [97.46, 99.61] | 94.34 [90.82, 97.27] | 97.85 [95.90, 99.41] | 98.05 [96.48, 99.41] | 95.90 [92.58, 98.44] |
| mistral_confirmation/shared | 88.77 [86.33, 91.21] | 94.14 [91.89, 96.19] | 73.54 [71.58, 75.29] | 94.73 [92.68, 96.68] | 96.39 [94.34, 98.14] | 93.16 [90.33, 95.80] |
| mistral_confirmation/far | 98.05 [96.58, 99.12] | 98.05 [96.78, 99.02] | 95.21 [92.87, 97.27] | 97.27 [95.41, 98.83] | 97.46 [95.80, 98.83] | 95.61 [93.46, 97.46] |
| llama_discovery/shared | 81.25 [78.91, 83.79] | 90.62 [87.30, 93.75] | 75.98 [75.00, 76.95] | 99.61 [99.02, 100.00] | 99.61 [98.83, 100.00] | 99.61 [99.02, 100.00] |
| llama_discovery/far | 99.02 [98.05, 99.80] | 99.22 [98.24, 100.00] | 96.29 [94.92, 97.66] | 97.66 [96.09, 99.02] | 97.66 [96.09, 99.02] | 95.12 [92.58, 97.46] |
| llama_confirmation/shared | 81.25 [79.00, 83.59] | 90.72 [88.48, 92.87] | 75.20 [74.71, 75.68] | 97.95 [96.88, 98.93] | 99.12 [98.34, 99.80] | 99.12 [97.95, 100.00] |
| llama_confirmation/far | 97.95 [96.78, 99.02] | 98.54 [97.56, 99.32] | 94.82 [92.97, 96.48] | 96.58 [95.12, 97.95] | 96.97 [95.61, 98.24] | 95.31 [93.46, 96.97] |
| qwen14_discovery/shared | 90.82 [87.11, 94.34] | 96.48 [93.75, 98.83] | 74.61 [72.46, 76.37] | 93.55 [91.41, 95.51] | 96.68 [94.53, 98.63] | 97.46 [94.92, 99.41] |
| qwen14_discovery/far | 95.51 [92.38, 98.05] | 96.09 [92.58, 98.83] | 95.51 [93.36, 97.46] | 94.73 [92.58, 96.88] | 96.09 [94.34, 97.85] | 96.09 [93.95, 98.05] |
| qwen14_confirmation/shared | 89.94 [87.99, 91.89] | 97.36 [96.09, 98.44] | 75.00 [73.83, 76.17] | 93.75 [91.80, 95.61] | 97.27 [95.61, 98.63] | 98.05 [96.68, 99.22] |
| qwen14_confirmation/far | 95.90 [94.53, 97.27] | 97.27 [96.09, 98.34] | 96.68 [95.02, 98.14] | 92.97 [90.92, 95.02] | 94.63 [92.77, 96.39] | 96.68 [95.21, 98.05] |

## 原定native paired收益：Actor与私人约定（百分点）

| 批/namespace | target平均 | A | B | opposite convention | same convention |
|---|---:|---:|---:|---:|---:|
| qwen3_discovery/shared | 7.03 [4.30, 10.16] | 5.86 [2.34, 9.77] | 8.20 [1.95, 15.62] | 14.06 [8.20, 20.70] | 0.00 [-1.95, 2.34] |
| qwen3_discovery/far | -0.98 [-2.93, 0.20] | -1.17 [-4.69, 1.17] | -0.78 [-1.95, 0.00] | -0.78 [-3.52, 1.17] | -1.17 [-2.34, 0.00] |
| qwen3_confirmation/shared | 7.32 [5.37, 9.28] | 4.49 [1.56, 7.03] | 10.16 [6.05, 14.26] | 15.23 [11.91, 18.75] | -0.59 [-2.15, 0.98] |
| qwen3_confirmation/far | 0.10 [-0.59, 0.98] | -0.20 [-0.98, 0.39] | 0.39 [-0.78, 1.76] | -0.59 [-1.37, 0.20] | 0.78 [-0.39, 2.34] |
| mistral_discovery/shared | 6.45 [3.32, 9.57] | 2.73 [-1.17, 6.25] | 10.16 [5.47, 15.62] | 13.28 [7.42, 19.14] | -0.39 [-1.17, 0.00] |
| mistral_discovery/far | 0.00 [-0.59, 0.59] | -0.39 [-1.17, 0.00] | 0.39 [0.00, 1.17] | -0.39 [-1.17, 0.00] | 0.39 [0.00, 1.17] |
| mistral_confirmation/shared | 5.37 [2.93, 7.71] | 4.49 [0.98, 8.20] | 6.25 [3.32, 9.38] | 12.11 [8.20, 16.21] | -1.37 [-3.71, 0.20] |
| mistral_confirmation/far | 0.00 [-0.29, 0.29] | 0.00 [-0.59, 0.59] | 0.00 [0.00, 0.00] | 0.20 [0.00, 0.59] | -0.20 [-0.59, 0.00] |
| llama_discovery/shared | 9.38 [6.45, 12.50] | 10.55 [6.25, 15.23] | 8.20 [3.52, 13.28] | 18.75 [12.89, 25.00] | 0.00 [0.00, 0.00] |
| llama_discovery/far | 0.20 [-0.39, 0.78] | 0.39 [0.00, 1.17] | 0.00 [-1.17, 1.17] | 0.00 [-1.17, 1.17] | 0.39 [-0.78, 1.56] |
| llama_confirmation/shared | 9.47 [7.52, 11.52] | 7.42 [4.69, 10.16] | 11.52 [8.20, 14.65] | 19.14 [15.04, 23.24] | -0.20 [-0.59, 0.00] |
| llama_confirmation/far | 0.59 [0.00, 1.37] | 0.59 [0.00, 1.76] | 0.59 [0.00, 1.56] | 0.39 [0.00, 0.98] | 0.78 [0.00, 1.76] |
| qwen14_discovery/shared | 5.66 [3.12, 8.20] | 2.73 [0.39, 6.25] | 8.59 [4.30, 13.67] | 10.94 [6.25, 16.02] | 0.39 [-0.78, 1.56] |
| qwen14_discovery/far | 0.59 [-0.20, 1.37] | -0.78 [-1.95, 0.00] | 1.95 [0.78, 3.52] | 0.39 [-1.17, 1.95] | 0.78 [-0.78, 2.34] |
| qwen14_confirmation/shared | 7.42 [5.57, 9.38] | 4.88 [2.15, 8.20] | 9.96 [6.05, 14.06] | 15.23 [11.52, 19.14] | -0.39 [-1.37, 0.59] |
| qwen14_confirmation/far | 1.37 [0.49, 2.34] | 0.39 [-0.39, 1.37] | 2.34 [0.78, 4.10] | 0.59 [-0.39, 1.56] | 2.15 [0.78, 3.91] |

| 确认模型/namespace/A私人方向 | target平均 | A | B | opposite | same |
|---|---:|---:|---:|---:|---:|
| Qwen3-8B/shared/False | 8.20 [5.27, 11.33] | 1.56 [-1.56, 4.69] | 14.84 [8.59, 20.31] | 15.62 [10.16, 21.09] | 0.78 [-0.78, 2.34] |
| Qwen3-8B/shared/True | 6.45 [4.10, 8.79] | 7.42 [2.73, 11.33] | 5.47 [1.17, 10.16] | 14.84 [10.94, 18.75] | -1.95 [-4.69, 0.39] |
| Qwen3-8B/far/False | 0.59 [-0.59, 2.15] | 0.39 [0.00, 1.17] | 0.78 [-1.17, 3.12] | -0.78 [-1.95, 0.00] | 1.95 [-0.39, 4.69] |
| Qwen3-8B/far/True | -0.39 [-1.17, 0.39] | -0.78 [-1.95, 0.00] | 0.00 [-1.17, 1.17] | -0.39 [-1.56, 0.78] | -0.39 [-1.17, 0.00] |
| Mistral-7B-v0.3/shared/False | 4.88 [2.15, 7.81] | 3.12 [0.00, 7.81] | 6.64 [2.34, 11.72] | 10.16 [5.08, 16.02] | -0.39 [-1.17, 0.00] |
| Mistral-7B-v0.3/shared/True | 5.86 [1.56, 9.57] | 5.86 [0.00, 11.72] | 5.86 [1.95, 9.77] | 14.06 [8.20, 19.92] | -2.34 [-6.64, 0.39] |
| Mistral-7B-v0.3/far/False | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Mistral-7B-v0.3/far/True | 0.00 [-0.59, 0.59] | 0.00 [-1.17, 1.17] | 0.00 [0.00, 0.00] | 0.39 [0.00, 1.17] | -0.39 [-1.17, 0.00] |
| Llama-3.1-8B/shared/False | 9.57 [6.64, 12.70] | 8.20 [4.69, 12.11] | 10.94 [6.25, 15.23] | 19.14 [13.28, 25.39] | 0.00 [0.00, 0.00] |
| Llama-3.1-8B/shared/True | 9.38 [6.84, 11.91] | 6.64 [2.73, 10.55] | 12.11 [7.81, 16.41] | 19.14 [13.67, 24.61] | -0.39 [-1.17, 0.00] |
| Llama-3.1-8B/far/False | 0.39 [0.00, 1.17] | 0.00 [0.00, 0.00] | 0.78 [0.00, 2.34] | 0.39 [0.00, 1.17] | 0.39 [0.00, 1.17] |
| Llama-3.1-8B/far/True | 0.78 [0.00, 2.15] | 1.17 [0.00, 3.52] | 0.39 [0.00, 1.17] | 0.39 [0.00, 1.17] | 1.17 [0.00, 3.12] |
| Qwen3-14B/shared/False | 9.57 [7.23, 12.11] | 0.39 [0.00, 1.17] | 18.75 [13.67, 23.83] | 19.14 [14.45, 24.22] | 0.00 [0.00, 0.00] |
| Qwen3-14B/shared/True | 5.27 [2.73, 8.01] | 9.38 [4.30, 14.84] | 1.17 [0.00, 3.12] | 11.33 [6.64, 16.80] | -0.78 [-2.73, 1.17] |
| Qwen3-14B/far/False | 1.95 [0.78, 3.32] | 0.00 [0.00, 0.00] | 3.91 [1.56, 6.64] | 0.00 [0.00, 0.00] | 3.91 [1.56, 6.64] |
| Qwen3-14B/far/True | 0.78 [-0.39, 1.95] | 0.78 [-0.78, 2.73] | 0.78 [-1.17, 2.73] | 1.17 [-0.78, 3.12] | 0.39 [-0.78, 1.56] |

| 确认模型 | target gain shared−far/native | target gain shared−far/gate | query-only/shared | query-only/far |
|---|---:|---:|---:|---:|
| Qwen3-8B | 7.23 [5.08, 9.47] | 9.08 [5.66, 12.40] | -0.39 [-3.12, 2.44] | 0.10 [-1.17, 1.56] |
| Mistral-7B-v0.3 | 5.37 [2.73, 7.81] | 1.46 [-0.20, 3.22] | 5.96 [3.22, 8.59] | -0.78 [-2.15, 0.49] |
| Llama-3.1-8B | 8.89 [6.84, 10.94] | 0.78 [-0.29, 1.95] | 16.70 [14.36, 19.04] | -1.37 [-2.83, 0.00] |
| Qwen3-14B | 6.05 [4.30, 7.91] | 1.86 [-0.29, 4.10] | 3.81 [1.27, 6.25] | -2.93 [-4.79, -1.17] |

## 本批单源函数与两私人方向（确认准确率%）

| 模型/函数 | 全部n32 | reverse=False n16 | reverse=True n16 |
|---|---:|---:|---:|
| Qwen3-8B/single_A | 95.31 [92.58, 97.66] | 96.09 [92.19, 99.22] | 94.53 [90.62, 97.66] |
| Qwen3-8B/single_B_origin_shared | 94.14 [90.62, 97.27] | 89.84 [84.38, 94.53] | 98.44 [96.09, 100.00] |
| Qwen3-8B/single_B_cross_shared | 97.27 [94.92, 99.22] | 99.22 [97.66, 100.00] | 95.31 [91.41, 98.44] |
| Qwen3-8B/single_B_origin_far | 92.97 [88.28, 96.88] | 95.31 [92.19, 98.44] | 90.62 [82.03, 97.66] |
| Qwen3-8B/single_B_cross_far | 94.14 [90.23, 97.66] | 89.84 [83.59, 95.31] | 98.44 [96.09, 100.00] |
| Mistral-7B-v0.3/single_A | 98.83 [97.27, 100.00] | 99.22 [97.66, 100.00] | 98.44 [96.09, 100.00] |
| Mistral-7B-v0.3/single_B_origin_shared | 98.05 [94.92, 100.00] | 96.09 [89.84, 100.00] | 100.00 [100.00, 100.00] |
| Mistral-7B-v0.3/single_B_cross_shared | 98.44 [96.88, 99.61] | 100.00 [100.00, 100.00] | 96.88 [93.75, 99.22] |
| Mistral-7B-v0.3/single_B_origin_far | 98.83 [97.66, 100.00] | 100.00 [100.00, 100.00] | 97.66 [95.31, 100.00] |
| Mistral-7B-v0.3/single_B_cross_far | 98.05 [96.48, 99.61] | 96.09 [92.97, 98.44] | 100.00 [100.00, 100.00] |
| Llama-3.1-8B/single_A | 98.44 [96.88, 99.61] | 99.22 [97.66, 100.00] | 97.66 [95.31, 100.00] |
| Llama-3.1-8B/single_B_origin_shared | 99.22 [98.05, 100.00] | 98.44 [96.09, 100.00] | 100.00 [100.00, 100.00] |
| Llama-3.1-8B/single_B_cross_shared | 99.61 [98.83, 100.00] | 100.00 [100.00, 100.00] | 99.22 [97.66, 100.00] |
| Llama-3.1-8B/single_B_origin_far | 94.14 [89.84, 97.66] | 96.09 [92.19, 99.22] | 92.19 [85.16, 98.44] |
| Llama-3.1-8B/single_B_cross_far | 89.06 [83.58, 94.14] | 81.25 [71.88, 89.84] | 96.88 [93.75, 99.22] |
| Qwen3-14B/single_A | 98.05 [96.48, 99.61] | 100.00 [100.00, 100.00] | 96.09 [92.97, 98.44] |
| Qwen3-14B/single_B_origin_shared | 96.88 [93.75, 99.22] | 94.53 [89.06, 98.44] | 99.22 [97.66, 100.00] |
| Qwen3-14B/single_B_cross_shared | 98.44 [96.48, 100.00] | 100.00 [100.00, 100.00] | 96.88 [92.97, 100.00] |
| Qwen3-14B/single_B_origin_far | 95.70 [93.75, 97.66] | 96.09 [92.97, 98.44] | 95.31 [92.19, 98.44] |
| Qwen3-14B/single_B_cross_far | 96.48 [92.97, 99.22] | 93.75 [87.50, 99.22] | 99.22 [97.66, 100.00] |

reverse指A全局私人方向；B绝对方向由它与相对same/opposite共同决定。不能借E121single自动声明本批能力，也不能把candidate single直接替代全词表生成控制。全部85条件full argmax和预测差异在JSON。

| 批 | candidate/full-argmax有差异的条件与query数量 |
|---|---|
| qwen3_discovery | {"origin_shared_normal_gate_0": 1, "origin_far_normal_native_1": 1, "origin_far_answer_cross_off_native_1": 1, "origin_far_all_cross_off_native_0": 58, "origin_far_all_cross_off_native_1": 52, "cross_shared_normal_gate_0": 1, "cross_far_normal_native_0": 1, "cross_far_normal_native_1": 4, "cross_far_answer_cross_off_native_0": 2, "cross_far_answer_cross_off_native_1": 2, "cross_far_all_cross_off_native_0": 60, "cross_far_all_cross_off_native_1": 48, "within_far_normal_native_1": 3, "within_far_answer_cross_off_native_0": 2, "within_far_answer_cross_off_native_1": 3, "within_far_all_cross_off_native_0": 54, "within_far_all_cross_off_native_1": 60} |
| qwen3_confirmation | {"origin_far_normal_native_0": 2, "origin_far_normal_native_1": 9, "origin_far_answer_cross_off_native_0": 3, "origin_far_answer_cross_off_native_1": 7, "origin_far_all_cross_off_native_0": 108, "origin_far_all_cross_off_native_1": 101, "cross_far_normal_native_1": 11, "cross_far_answer_cross_off_native_0": 4, "cross_far_answer_cross_off_native_1": 9, "cross_far_all_cross_off_native_0": 129, "cross_far_all_cross_off_native_1": 101, "within_far_normal_native_0": 2, "within_far_normal_native_1": 6, "within_far_answer_cross_off_native_0": 1, "within_far_answer_cross_off_native_1": 7, "within_far_all_cross_off_native_0": 115, "within_far_all_cross_off_native_1": 108, "origin_far_instruction_1": 4} |
| mistral_discovery | {"origin_far_normal_native_0": 5, "origin_far_normal_native_1": 4, "origin_far_answer_cross_off_native_0": 13, "origin_far_answer_cross_off_native_1": 3, "origin_far_all_cross_off_native_0": 83, "origin_far_all_cross_off_native_1": 15, "cross_far_normal_native_0": 3, "cross_far_normal_native_1": 1, "cross_far_answer_cross_off_native_0": 8, "cross_far_all_cross_off_native_0": 109, "cross_far_all_cross_off_native_1": 4, "within_far_normal_native_0": 5, "within_far_normal_native_1": 1, "within_far_answer_cross_off_native_0": 12, "within_far_answer_cross_off_native_1": 1, "within_far_all_cross_off_native_0": 80, "within_far_all_cross_off_native_1": 17, "origin_far_instruction_0": 4, "origin_far_instruction_1": 1, "cross_far_instruction_0": 2, "cross_far_instruction_1": 1} |
| mistral_confirmation | {"origin_far_normal_native_0": 7, "origin_far_normal_native_1": 2, "origin_far_answer_cross_off_native_0": 14, "origin_far_answer_cross_off_native_1": 1, "origin_far_all_cross_off_native_0": 139, "origin_far_all_cross_off_native_1": 66, "cross_far_normal_native_0": 8, "cross_far_normal_native_1": 4, "cross_far_answer_cross_off_native_0": 16, "cross_far_answer_cross_off_native_1": 3, "cross_far_all_cross_off_native_0": 175, "cross_far_all_cross_off_native_1": 45, "within_far_normal_native_0": 7, "within_far_normal_native_1": 1, "within_far_answer_cross_off_native_0": 15, "within_far_answer_cross_off_native_1": 1, "within_far_all_cross_off_native_0": 154, "within_far_all_cross_off_native_1": 59, "origin_far_instruction_0": 6, "origin_far_instruction_1": 3, "cross_far_instruction_0": 7, "cross_far_instruction_1": 4} |
| llama_discovery | {"origin_far_normal_native_0": 1, "origin_far_normal_native_1": 6, "origin_far_answer_cross_off_native_0": 1, "origin_far_answer_cross_off_native_1": 8, "origin_far_all_cross_off_native_0": 42, "origin_far_all_cross_off_native_1": 69, "cross_far_normal_native_1": 1, "cross_far_answer_cross_off_native_1": 3, "cross_far_all_cross_off_native_0": 37, "cross_far_all_cross_off_native_1": 75, "within_far_normal_native_1": 7, "within_far_answer_cross_off_native_0": 1, "within_far_answer_cross_off_native_1": 8, "within_far_all_cross_off_native_0": 45, "within_far_all_cross_off_native_1": 65, "origin_far_instruction_1": 5} |
| llama_confirmation | {"origin_far_normal_native_0": 5, "origin_far_normal_native_1": 5, "origin_far_answer_cross_off_native_0": 8, "origin_far_answer_cross_off_native_1": 8, "origin_far_all_cross_off_native_0": 92, "origin_far_all_cross_off_native_1": 125, "cross_far_normal_native_0": 2, "cross_far_normal_native_1": 14, "cross_far_answer_cross_off_native_0": 5, "cross_far_answer_cross_off_native_1": 14, "cross_far_all_cross_off_native_0": 77, "cross_far_all_cross_off_native_1": 126, "within_far_normal_native_0": 5, "within_far_normal_native_1": 9, "within_far_answer_cross_off_native_0": 8, "within_far_answer_cross_off_native_1": 10, "within_far_all_cross_off_native_0": 77, "within_far_all_cross_off_native_1": 131, "origin_far_instruction_0": 5, "origin_far_instruction_1": 3, "cross_far_instruction_1": 13} |
| qwen14_discovery | {"origin_far_all_cross_off_native_0": 67, "origin_far_all_cross_off_native_1": 50, "cross_far_normal_native_1": 2, "cross_far_all_cross_off_native_0": 54, "cross_far_all_cross_off_native_1": 54, "within_far_all_cross_off_native_0": 61, "within_far_all_cross_off_native_1": 47} |
| qwen14_confirmation | {"origin_far_all_cross_off_native_0": 136, "origin_far_all_cross_off_native_1": 88, "cross_far_normal_native_1": 1, "cross_far_answer_cross_off_native_0": 1, "cross_far_answer_cross_off_native_1": 1, "cross_far_all_cross_off_native_0": 131, "cross_far_all_cross_off_native_1": 94, "within_far_normal_native_0": 1, "within_far_all_cross_off_native_0": 134, "within_far_all_cross_off_native_1": 89} |

| 确认模型/namespace | normal/native full argmax | target/native full argmax | all/native full argmax | target−normal full argmax，pp |
|---|---:|---:|---:|---:|
| Qwen3-8B/shared | 84.86 [82.62, 87.01] | 92.19 [90.04, 94.14] | 75.00 [74.02, 76.07] | 7.32 [5.37, 9.28] |
| Qwen3-8B/far | 92.09 [89.55, 94.43] | 92.09 [89.84, 94.14] | 51.46 [49.90, 53.12] | 0.00 [-1.17, 1.46] |
| Mistral-7B-v0.3/shared | 88.77 [86.33, 91.21] | 94.14 [91.89, 96.19] | 73.54 [71.58, 75.29] | 5.37 [2.93, 7.71] |
| Mistral-7B-v0.3/far | 96.00 [94.34, 97.56] | 94.73 [92.68, 96.58] | 53.71 [52.15, 55.37] | -1.27 [-2.44, -0.20] |
| Llama-3.1-8B/shared | 81.25 [79.00, 83.59] | 90.72 [88.48, 92.87] | 75.20 [74.71, 75.68] | 9.47 [7.52, 11.52] |
| Llama-3.1-8B/far | 95.41 [93.46, 97.17] | 95.12 [92.97, 97.07] | 53.81 [52.25, 55.57] | -0.29 [-1.27, 0.59] |
| Qwen3-14B/shared | 89.94 [87.99, 91.89] | 97.36 [96.09, 98.44] | 75.00 [73.83, 76.17] | 7.42 [5.57, 9.38] |
| Qwen3-14B/far | 95.80 [94.34, 97.17] | 97.07 [95.80, 98.24] | 52.83 [50.39, 55.57] | 1.27 [0.29, 2.25] |

| 确认模型 | far normal/native其它Source词% | far target/native其它Source词% | far all/native其它Source词% |
|---|---:|---:|---:|
| Qwen3-8B | 2.34 [1.17, 3.71] | 2.25 [1.27, 3.32] | 46.88 [45.21, 48.44] |
| Mistral-7B-v0.3 | 2.15 [1.07, 3.42] | 3.32 [1.76, 5.18] | 44.63 [42.19, 46.78] |
| Llama-3.1-8B | 3.03 [1.37, 4.88] | 3.52 [1.66, 5.66] | 45.12 [43.36, 46.68] |
| Qwen3-14B | 0.10 [0.00, 0.29] | 0.20 [0.00, 0.49] | 46.09 [43.55, 48.34] |

| 确认模型/far policy/scope | A full argmax% | B full argmax% | A其它Source词% | B其它Source词% |
|---|---:|---:|---:|---:|
| Qwen3-8B/normal_native | 93.55 [89.84, 96.68] | 90.62 [87.50, 93.36] | 0.59 [0.00, 1.56] | 4.10 [1.95, 6.64] |
| Qwen3-8B/normal_gate | 93.16 [88.87, 96.68] | 95.51 [92.97, 97.66] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Qwen3-8B/answer_cross_off_native | 92.38 [88.67, 95.51] | 91.80 [89.45, 94.14] | 1.37 [0.39, 2.54] | 3.12 [1.56, 4.88] |
| Qwen3-8B/answer_cross_off_gate | 92.77 [88.09, 96.68] | 96.48 [94.73, 98.05] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Qwen3-8B/all_cross_off_native | 48.24 [40.43, 56.05] | 54.69 [45.70, 63.48] | 51.17 [43.36, 58.98] | 42.58 [33.40, 51.76] |
| Qwen3-8B/all_cross_off_gate | 93.36 [89.06, 97.27] | 92.97 [89.65, 96.09] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Mistral-7B-v0.3/normal_native | 94.92 [91.60, 97.66] | 97.07 [95.51, 98.44] | 3.12 [1.17, 5.47] | 1.17 [0.20, 2.54] |
| Mistral-7B-v0.3/normal_gate | 96.68 [93.16, 99.61] | 97.85 [96.48, 99.02] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Mistral-7B-v0.3/answer_cross_off_native | 91.99 [88.09, 95.51] | 97.46 [96.09, 98.63] | 5.86 [2.73, 9.57] | 0.78 [0.00, 1.76] |
| Mistral-7B-v0.3/answer_cross_off_gate | 96.68 [93.36, 99.22] | 98.24 [97.07, 99.22] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Mistral-7B-v0.3/all_cross_off_native | 30.86 [21.68, 40.62] | 76.56 [68.75, 83.98] | 66.99 [56.84, 76.76] | 22.27 [14.84, 30.08] |
| Mistral-7B-v0.3/all_cross_off_gate | 94.53 [91.02, 97.66] | 96.68 [94.73, 98.44] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Llama-3.1-8B/normal_native | 97.07 [94.34, 99.22] | 93.75 [90.43, 96.68] | 1.95 [0.20, 4.69] | 4.10 [1.56, 7.23] |
| Llama-3.1-8B/normal_gate | 97.85 [96.09, 99.41] | 95.31 [92.77, 97.46] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Llama-3.1-8B/answer_cross_off_native | 96.48 [93.55, 98.83] | 93.75 [90.23, 96.88] | 2.54 [0.39, 5.47] | 4.49 [1.56, 8.01] |
| Llama-3.1-8B/answer_cross_off_gate | 98.83 [97.66, 99.80] | 95.12 [92.38, 97.46] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Llama-3.1-8B/all_cross_off_native | 64.65 [58.01, 71.29] | 42.97 [34.96, 50.98] | 34.96 [28.32, 41.60] | 55.27 [47.46, 63.28] |
| Llama-3.1-8B/all_cross_off_gate | 99.22 [98.05, 100.00] | 91.41 [87.89, 94.53] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Qwen3-14B/normal_native | 97.85 [96.09, 99.41] | 93.75 [91.21, 96.09] | 0.00 [0.00, 0.00] | 0.20 [0.00, 0.59] |
| Qwen3-14B/normal_gate | 97.46 [95.31, 99.22] | 88.48 [84.57, 91.99] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Qwen3-14B/answer_cross_off_native | 98.05 [95.90, 99.61] | 96.09 [94.53, 97.66] | 0.20 [0.00, 0.59] | 0.20 [0.00, 0.59] |
| Qwen3-14B/answer_cross_off_gate | 97.46 [95.31, 99.22] | 91.80 [88.48, 94.92] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Qwen3-14B/all_cross_off_native | 46.09 [39.65, 52.34] | 59.57 [53.52, 66.02] | 53.71 [47.46, 60.16] | 38.48 [32.03, 44.73] |
| Qwen3-14B/all_cross_off_gate | 98.05 [96.09, 99.61] | 95.31 [93.36, 97.07] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

这些完整输出/另一词表效应按A/B分开，不将总体均值写成对称source-binding模块失效。不同alias的词语先验、binding和label-recognition仍是竞争解释，当前实验识别形成政策后果，不宣称新ID/独立TR组件。

其它Source词由不同namespace下argmax是否属于另一组no/yes或pass/flag定义；shared两组词相同，无法靠词身份归Source，作者将此词表读数记0而非断言其关系provenance为0。该诊断不是新primary，也不把它解释成隐藏模块。

## A对B约定的全部功能响应（确认，nats）

signed=mean_q[gA×½(z_cross−z_origin)]，absolute先取每context signed的绝对值再平均；within是同类移动的完整差mean_q[gA×(z_within−z_origin)]。不是逐query取绝对值、不是误差率，也不是完整标准程序。

| 模型/namespace/policy/scope | signed | absolute | within signed | within absolute |
|---|---:|---:|---:|---:|
| Qwen3-8B/shared_normal_native | 2.449 [2.017, 2.893] | 2.449 [2.017, 2.893] | 0.070 [-0.149, 0.286] | 0.478 [0.345, 0.631] |
| Qwen3-8B/shared_normal_gate | 0.567 [0.326, 0.793] | 0.715 [0.546, 0.896] | -0.200 [-0.444, 0.015] | 0.453 [0.295, 0.647] |
| Qwen3-8B/shared_answer_cross_off_native | 1.253 [0.875, 1.636] | 1.319 [0.968, 1.674] | -0.012 [-0.190, 0.177] | 0.401 [0.285, 0.529] |
| Qwen3-8B/shared_answer_cross_off_gate | 0.178 [0.005, 0.372] | 0.405 [0.292, 0.554] | 0.047 [-0.176, 0.270] | 0.518 [0.398, 0.657] |
| Qwen3-8B/shared_all_cross_off_native | 2.390 [1.942, 2.841] | 2.390 [1.942, 2.841] | -0.037 [-0.274, 0.189] | 0.541 [0.416, 0.678] |
| Qwen3-8B/shared_all_cross_off_gate | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| Qwen3-8B/far_normal_native | 0.012 [-0.162, 0.190] | 0.408 [0.308, 0.514] | -0.056 [-0.281, 0.174] | 0.536 [0.407, 0.673] |
| Qwen3-8B/far_normal_gate | -0.027 [-0.169, 0.112] | 0.326 [0.247, 0.414] | -0.033 [-0.214, 0.136] | 0.415 [0.327, 0.517] |
| Qwen3-8B/far_answer_cross_off_native | 0.096 [-0.114, 0.312] | 0.497 [0.376, 0.631] | 0.074 [-0.208, 0.360] | 0.664 [0.499, 0.837] |
| Qwen3-8B/far_answer_cross_off_gate | 0.001 [-0.163, 0.165] | 0.359 [0.267, 0.465] | 0.021 [-0.214, 0.235] | 0.516 [0.392, 0.657] |
| Qwen3-8B/far_all_cross_off_native | 0.165 [-0.018, 0.352] | 0.426 [0.308, 0.556] | 0.262 [-0.009, 0.567] | 0.579 [0.366, 0.831] |
| Qwen3-8B/far_all_cross_off_gate | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| Mistral-7B-v0.3/shared_normal_native | 1.390 [1.195, 1.587] | 1.390 [1.195, 1.587] | -0.008 [-0.108, 0.091] | 0.218 [0.157, 0.286] |
| Mistral-7B-v0.3/shared_normal_gate | 0.437 [0.319, 0.564] | 0.450 [0.339, 0.573] | 0.037 [-0.077, 0.149] | 0.237 [0.166, 0.315] |
| Mistral-7B-v0.3/shared_answer_cross_off_native | 0.832 [0.634, 1.030] | 0.841 [0.649, 1.035] | 0.021 [-0.098, 0.144] | 0.279 [0.212, 0.354] |
| Mistral-7B-v0.3/shared_answer_cross_off_gate | 0.115 [0.043, 0.189] | 0.186 [0.138, 0.242] | 0.047 [-0.061, 0.158] | 0.240 [0.173, 0.314] |
| Mistral-7B-v0.3/shared_all_cross_off_native | 1.154 [0.996, 1.334] | 1.154 [0.996, 1.334] | -0.063 [-0.182, 0.054] | 0.280 [0.213, 0.350] |
| Mistral-7B-v0.3/shared_all_cross_off_gate | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| Mistral-7B-v0.3/far_normal_native | 0.105 [0.049, 0.162] | 0.154 [0.114, 0.198] | 0.005 [-0.096, 0.110] | 0.223 [0.157, 0.294] |
| Mistral-7B-v0.3/far_normal_gate | 0.043 [-0.003, 0.089] | 0.117 [0.092, 0.144] | 0.016 [-0.091, 0.129] | 0.230 [0.164, 0.308] |
| Mistral-7B-v0.3/far_answer_cross_off_native | 0.103 [0.045, 0.161] | 0.170 [0.136, 0.206] | -0.007 [-0.109, 0.095] | 0.226 [0.163, 0.292] |
| Mistral-7B-v0.3/far_answer_cross_off_gate | 0.013 [-0.039, 0.062] | 0.123 [0.096, 0.151] | -0.005 [-0.113, 0.105] | 0.232 [0.163, 0.310] |
| Mistral-7B-v0.3/far_all_cross_off_native | 0.128 [0.075, 0.181] | 0.159 [0.119, 0.202] | 0.035 [-0.035, 0.107] | 0.157 [0.111, 0.206] |
| Mistral-7B-v0.3/far_all_cross_off_gate | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| Llama-3.1-8B/shared_normal_native | 1.595 [1.479, 1.716] | 1.595 [1.479, 1.716] | 0.047 [-0.033, 0.136] | 0.178 [0.124, 0.242] |
| Llama-3.1-8B/shared_normal_gate | 0.403 [0.315, 0.499] | 0.406 [0.320, 0.501] | -0.023 [-0.130, 0.076] | 0.219 [0.153, 0.293] |
| Llama-3.1-8B/shared_answer_cross_off_native | 1.093 [0.953, 1.241] | 1.093 [0.953, 1.241] | 0.019 [-0.058, 0.103] | 0.164 [0.112, 0.225] |
| Llama-3.1-8B/shared_answer_cross_off_gate | 0.122 [0.069, 0.176] | 0.159 [0.120, 0.200] | 0.028 [-0.058, 0.105] | 0.173 [0.124, 0.232] |
| Llama-3.1-8B/shared_all_cross_off_native | 1.292 [1.148, 1.445] | 1.292 [1.148, 1.445] | 0.064 [-0.067, 0.191] | 0.282 [0.200, 0.373] |
| Llama-3.1-8B/shared_all_cross_off_gate | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| Llama-3.1-8B/far_normal_native | 0.030 [-0.052, 0.116] | 0.197 [0.149, 0.246] | 0.114 [0.001, 0.223] | 0.261 [0.191, 0.342] |
| Llama-3.1-8B/far_normal_gate | 0.009 [-0.049, 0.063] | 0.128 [0.098, 0.164] | 0.058 [-0.018, 0.131] | 0.162 [0.113, 0.218] |
| Llama-3.1-8B/far_answer_cross_off_native | 0.017 [-0.068, 0.103] | 0.198 [0.148, 0.249] | 0.112 [0.005, 0.222] | 0.254 [0.187, 0.333] |
| Llama-3.1-8B/far_answer_cross_off_gate | 0.013 [-0.040, 0.067] | 0.126 [0.097, 0.158] | 0.067 [-0.004, 0.136] | 0.161 [0.116, 0.211] |
| Llama-3.1-8B/far_all_cross_off_native | -0.017 [-0.078, 0.044] | 0.137 [0.100, 0.177] | -0.007 [-0.064, 0.049] | 0.141 [0.113, 0.169] |
| Llama-3.1-8B/far_all_cross_off_gate | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| Qwen3-14B/shared_normal_native | 2.230 [1.881, 2.560] | 2.230 [1.881, 2.560] | -0.054 [-0.135, 0.040] | 0.194 [0.139, 0.256] |
| Qwen3-14B/shared_normal_gate | 0.765 [0.534, 1.022] | 0.792 [0.574, 1.043] | -0.208 [-0.453, 0.002] | 0.394 [0.221, 0.607] |
| Qwen3-14B/shared_answer_cross_off_native | 1.103 [0.817, 1.386] | 1.167 [0.920, 1.419] | 0.007 [-0.142, 0.143] | 0.296 [0.207, 0.402] |
| Qwen3-14B/shared_answer_cross_off_gate | 0.289 [0.161, 0.419] | 0.373 [0.276, 0.476] | -0.126 [-0.254, -0.009] | 0.258 [0.170, 0.359] |
| Qwen3-14B/shared_all_cross_off_native | 2.580 [2.319, 2.850] | 2.580 [2.319, 2.850] | 0.245 [0.023, 0.480] | 0.542 [0.396, 0.698] |
| Qwen3-14B/shared_all_cross_off_gate | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| Qwen3-14B/far_normal_native | 0.057 [-0.082, 0.200] | 0.325 [0.242, 0.414] | -0.036 [-0.222, 0.145] | 0.405 [0.291, 0.530] |
| Qwen3-14B/far_normal_gate | 0.036 [-0.075, 0.144] | 0.258 [0.198, 0.322] | -0.141 [-0.268, -0.018] | 0.289 [0.205, 0.386] |
| Qwen3-14B/far_answer_cross_off_native | 0.096 [-0.058, 0.250] | 0.359 [0.270, 0.455] | 0.019 [-0.170, 0.200] | 0.422 [0.318, 0.534] |
| Qwen3-14B/far_answer_cross_off_gate | 0.048 [-0.089, 0.175] | 0.283 [0.200, 0.377] | -0.148 [-0.278, -0.023] | 0.288 [0.200, 0.387] |
| Qwen3-14B/far_all_cross_off_native | 0.091 [-0.053, 0.230] | 0.322 [0.237, 0.415] | 0.057 [-0.153, 0.278] | 0.460 [0.326, 0.612] |
| Qwen3-14B/far_all_cross_off_gate | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## 解释范围

shared/far比较改变具体输出词身份、词语义与先验；single B两约定/两方向/两namespace必须一起解释预定gain交互，不能据一个gain差独立证明唯一output identity因素或相同能力强度。far native candidate接近上限会限制可上涨空间，shared/far gain差也包含不同headroom；未实施等难度/等headroom干预，不能称对此已控制。full argmax在部分far/native条件明显低于candidate，尤其all-cross时，故candidate收益不自动等于生成正确输出词的改善。政策可能在同约定/反约定、Actor、private方向、native/gate产生不同乃至相反效果；它们是已冻结功能事实，不自动抹去原形成/关联机制，也不按方向更换科学读数。source ownership是生成真值，非learned recognizer；自然Movie文本/公开benchmark与构造private rule范围不同于人类个人判断。

原定所有阳性、阴性、残差与控制均保留在JSON；本报告不改变grade、claims、科学源/卡/论文、研究状态或已封E115–E122。未GPU重跑、commit/push。结果与论证适配须在实际本批private和full-output能力边界内陈述。
