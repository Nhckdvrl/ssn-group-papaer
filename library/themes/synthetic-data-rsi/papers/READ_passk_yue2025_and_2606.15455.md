# 精读：Yue et al. 2025（pass@k 边界）与 arXiv 2606.15455（Overtraining / 多样性坍缩）

读法：两篇都下载 PDF，用 `pdftotext -layout` 转文本后通读。
- Yue 2025（arXiv 2504.13837 v5，2025-11-24；NeurIPS 2025 Oral，ICML 2025 AI4MATH workshop best paper；venue 信息来自 arXiv 条目与 NeurIPS 页面的搜索结果，未打开官方页面核对）：读了摘要、§1–§7、附录 A（A.1 算法、A.2 pass@k 估计器）、B、C.1–C.9（含全部表 2–6）、C.10 只扫了标题、D（prompt 模板）只看了目录和标题。**图中数值只能从文本层读到坐标刻度，没有曲线的精确点值；凡写“约”的都来自正文文字，不是读图。**
- 2606.15455（v1，2026-06-13）：读了摘要、§1–§6、附录 A（全部）、B、C、D（图 5–7 只有图，无表）。参考文献只扫了与本题相关的条目。

---

## 1. 论文 2 的标题与身份

**Understanding Diversity Collapse in RLVR via the Lens of Overtraining**（Suqin Yuan, Jinkun Chen, …, Tongliang Liu, Bo An；Sydney AI Centre / 东南大学 / Microsoft / CSIRO / 重庆大学 / NTU）。arXiv 2606.15455v1，[cs.LG]，标注 Preprint。单次训练、单个种子（附录 A.8：“single training run per method”）。

## 2. Yue et al. 2025 详录

### 2.1 模型、算法、基准
| 任务 | 起点模型 | RL 框架 / 来源 | 算法 | 基准 |
|---|---|---|---|---|
| 数学 | Qwen2.5-7B/14B/32B-Base、LLaMA-3.1-8B（SimpleRLZoo，用 GSM8K+MATH 训练集，仅正确性奖励，无格式奖励）；Qwen2.5-Math-7B（Oat-Zero）；Qwen2.5-32B（DAPO-32B） | 直接使用公开发布的 RLVR checkpoint | GRPO（DAPO 为其变体） | GSM8K, MATH500, Minerva, Olympiad, AIME24, AMC23 |
| 代码 | Qwen2.5-7B-Instruct-1M（Code-R1，12K LeetCode+TACO，832 步）；DeepSeek-R1-Distill-Qwen-14B（DeepCoder-14B，上下文 32k） | Code-R1 / DeepCoder | GRPO | LiveCodeBench v5（279 题，2024.8–2025.1）、HumanEval+、MBPP+（DeepCoder 只测 LCB） |
| 视觉 | Qwen2.5-VL-7B | EasyR1，Geometry3K | GRPO | MathVista-TestMini、MathVision-TestMini（去掉选择题） |
| 深入分析（自己用 VeRL 重训） | Qwen2.5-7B-Base；另有 Qwen2.5-7B-Instruct、DeepSeek-R1-Distill-Qwen-7B 列在 Table 1 | VeRL | PPO, GRPO, Reinforce++, RLOO, ReMax, DAPO | Omni-MATH-Rule（2000 训练 / 821 域内测试）、MATH500（域外） |
| 大模型 | Mistral-Medium-3 → Magistral-Medium-2506（API，纯 RL，上下文 40k） | 商用 API | — | AIME24、AIME25 |

训练设置（§4.3）：去掉 KL；AdamW，常数学习率 1e-6；prompt batch 256，每题 8 个回复；最大 rollout 长度 8192；训练采样温度 1.0；PPO mini-batch 256。起点以 zero-RL 为主（数学）；代码/视觉用 instruct 模型作为起点。

### 2.2 pass@k 采样协议
- 评估：temperature 0.6，top-p 0.95，最长生成 16,384 tokens（代码两个大模型为 32k，Magistral 为 40k）。
- 不给 base 模型 few-shot；base 与 RL 用同一个零样本 prompt（RL 训练时的 prompt 或基准默认 prompt）。
- 估计器：Chen et al. 2021 的无偏估计 `1 - C(n-c,k)/C(n,k)`；n 取曲线最右端 k：128、256 或 1024。具体：图 2 中 MATH500、Minerva、GSM8K 用 n=128；AMC23、AIME24 用 n=1024；Olympiad 对 Qwen 用 n=128，对 LLaMA-3.1-8B 用 n=1024。
- 最大 k：128 / 256 / 1024（依基准）。
- 温度敏感性（图 17）：T=0.6/1.0/1.2；base 在 T>1.0 时变差，RL 模型几乎不变，所以主实验用 0.6，“让两者都发挥最好”。

### 2.3 精确数字（正文文字与附录表；非图值）
- Minerva、32B：k=128 时 base 比 RL 高约 9%（正文）。
- Oat-Zero / DAPO（AIME24）：RL 起初比 base 高约 30%，最终被 base 超过（图 11，正文）。
- Table 2（SimpleRLZoo vs Qwen2.5-7B-Base，AIME24 k=1024 / MATH500 k=128）：两者都解 63.3% / 92.4%；仅 base 解 13.3% / 3.6%；仅 RL 解 0.0% / 1.0%；都不解 23.3% / 3.0%。C.7：MATH500 上 RL 独有的 ~1%（约 5 题），base 采样 1024 次全部能解。
- Table 5（AIME24 可解题编号）：base 23 题；SimpleRL 19 题，几乎是 base 的子集（base 多出 4, 11, 17, 19；RL 独有的无）。Table 6（LCB 400–450）同样近似子集。
- Table 3（Qwen2.5-7B，VeRL 重训，pass@1 / pass@256；Omni-Train, Omni-Test, MATH500）：
  - Base：9.9/67.2；10.2/69.1；34.5/96.2
  - GRPO：26.1/66.3；25.1/68.3；74.4/97.2
  - PPO：27.2/65.8；26.8/69.2；75.2/97.2
  - ReMax：24.4/65.5；23.8/67.5；73.5/96.6
  - RLOO：28.6/66.4；28.1/69.2；75.0/97.4
  - Reinforce++：28.2/67.7；28.0/69.7；75.4/96.8
  - DAPO：31.4/66.1；26.5/67.0；75.6/96.4
  - 注意：MATH500 上 pass@256 多数 RL 算法是**高于** base 的（97.2 vs 96.2），Omni-Test 上 PPO/RLOO/Reinforce++ 持平或略高（69.2–69.7 vs 69.1）。“RL 在大 k 全面低于 base”在这个域外/高上限基准上并不成立，差距在 ±1 点量级，论文未给置信区间。
- Table 4（GRPO 训练步数）：Omni-Train pass@1 26.1→33.6→42.5，pass@256 66.3→65.3→64.3；Omni-Test pass@256 68.3→66.6→63.9（base 69.1）；MATH500 pass@256 97.2→96.0→95.4（base 96.2）。
- 采样效率差距 ΔSE = RL 的 pass@1 与 base 的 pass@256 之差：各算法均 >40 点；域内测试集上 GRPO 43.9，RLOO 42.6（最好）。图 8 标注的 ΔSE 值（0.206–0.410 之类）是从文本层读到的图上标签，未逐一对应。
- 其他消融：n 由 8→32（只训 220 步）pass@k 略升，但仍被 base 超过；KL=0.001 与 GRPO 的 pass@1 相近但 pass@128 明显更低；训练过程 entropy 持续下降（图 19）。把 RL 模型温度提高到与 base 熵相匹配（如 AMC23 用 T=0.9 使熵 0.47；RL 在 T=0.6 熵仅约 0.22 / MATH500 0.33），pass@k 略升但仍低于 base。
- Magistral-Medium：k=1 时在 AIME24 多解约 7 题、AIME25 多解约 8 题，k 增大后差距收窄；“little or no improvement at higher k”。

### 2.4 覆盖 / 边界分析
- 准确率分布（图 5、14）：RL 提高接近 1.0 的频率、降低低准确率频率，但**准确率为 0 的题数增加**。
- 可解题集合（Table 2/5/6）：见上，RL 解出的题近似为 base 的子集。
- 困惑度分析（图 6、C.4）：AIME24 随机两题，各让 base 与 SimpleRL 生成 16 条，o1 生成 8 条；PPL_Base(Y_RL|x) 的分布落在 PPL_Base(Y_Base|x) 的低端；训练过程中 PPL_Base(Y_RL|x) 逐步下降（3 个 checkpoint，32 条回复取中位数，仅对前 10 题求平均）。样本量很小。
- CoT 有效性（防“猜对”）：GSM8K 平均准确率 0–5% 的题，base 解 25 题，其中 24 题至少有一条正确 CoT；RL 解 25 题，23 题。AIME24 先用 Qwen2.5-7B-Base 直接作答（无 CoT）过滤“可猜”题（直接作答低但非零正确率 <5% 视为可猜）→ 30 题剩 18 题；其中 <5% 平均准确率的题 base 7 题（6 题可判，5 题有正确 CoT），RL 6 题（4 题）。视觉：<5% 的题 7/8 有正确 CoT。样本都很小，手工检查。

### 2.5 蒸馏对比
Qwen2.5-Math-7B 的 base / Instruct / Oat-Zero RL / DeepSeek-R1-Distill-Qwen-7B（从 R1 蒸馏）在 Minerva 上：蒸馏模型 pass@k 曲线在全部 k 上显著高于 base。结论：蒸馏从更强教师引入新推理模式，能扩张边界；RL 受限于 base。注意：蒸馏用了外部强教师的数据，不属于自改进闭环。

### 2.6 论文的主张（RL 做什么 / 不做什么）
- 做：提高采样效率，把已在 base 采样分布里的正确路径概率放大（pass@1 上升）。
- 不做：当前 RLVR 不引入根本新的推理模式，已解问题集合没有扩大，常常缩小；边界“受 base 限制”。六种算法表现相近，离最优远。
- 机制解释（§5，推测性）：LLM 动作空间巨大且有预训练先验，策略梯度提高先验内正确回复的似然，压低先验外的；因此被“先验”约束。未来方向：高层抽象探索（AlphaEvolve 类）、课程、过程奖励、多轮 agentic RL。
- 自我声明的局限：只测公开可得的纯 RLVR 模型；强模型/训练管线闭源；RL 方法在快速演进，结论需带着这些约束解读。

### 2.7 可能翻转结论的温度 / k 细节
- 温度：只用 T=0.6（附录 C.8 有 1.0、1.2 的 AIME24/MATH500 对照图，base 在 T>1 变差）。RL 模型熵低，对温度较不敏感。匹配熵后仍低于 base，所以论文认为熵下降不是唯一原因。
- k：差异在大 k 出现（k 几十到几百）；MATH500 等上限高的基准差距在 1 点量级且无区间；论文承认 k 极大时均匀采样也可能碰对答案（但声称 k=128/1024 已足够 base 产出正确输出）。
- 数学答案的“猜对”风险随 k 增大；论文只在最难的小子集上手工核查。
- 训练分布、起点：数学主实验为 zero-RL；代码/视觉的 base 是 instruct 或蒸馏模型，不是真正的预训练 base。
- base 无 few-shot，会出现不合格式输出，要靠大量采样才能出格式正确答案。
- Qwen2.5 系列的数据污染问题论文没有讨论（文中未检索到 contamination 相关论述，仅引用了 LiveCodeBench 的“contamination free”）。

### 2.8 自我博弈 / 无标签训练
正文无讨论。仅在参考文献中出现 Absolute Zero（self-play reasoning with zero data）和 ReST、STaR 类自改进条目（附录 B 一句话列举“自改进迭代”），没有对其做 pass@k 实验。结论局限于有可验证真值奖励的 RLVR。

---

## 3. arXiv 2606.15455 详录

### 3.1 “边界”的定义
reasoning boundary = 大 k 下 pass@k 所衡量的、模型给足够多次尝试能解的题集（沿用 Yue et al.）。操作定义（附录 A.7）：256 个样本中至少有 1 个正确 → “可解”（Pass@256>0），否则“不可解”。“entry” = base 下 C_{i,0}=0 而检查点 C_{i,t}>0；“loss” = base 下 C_{i,0}>0 而 C_{i,t}=0。

### 3.2 模型、算法、设置
- Qwen2.5-Math-7B，MATH 训练集（约 7.5k 题），verl，n=8，峰值 lr 1e-6 余弦衰减，batch 1024，mini-batch 128，最大 prompt 1024 / response 3072，KL=0，bf16 vLLM；140 步 ≈ 20 epoch；每 7 步（≈1 epoch）评估；4×H100。
- 算法：REINFORCE（r∈{-1,+1}，EMA 基线）、GRPO、W-RF（Zhu et al. 2025，正奖励权重 0.3）、提出的 BBG（Bayesian Boundary Gating，建在 W-RF 之上，k=16，τ=0.01，只更新 B0/8–B3/8 桶，权重约 67.1/23.3/7.4/2.1%，有效批 512 prompt）。
- 基准：MATH-500（域内）、OlympiadBench（675 题）、MinervaMath（272 题）、AIME 2025（30 题）。

### 3.3 pass@k 协议
每题 256 个独立样本，T=0.6，top-p=0.95，最长生成 4096 tokens（比训练的 3072 长，避免截断）；Chen et al. 2021 无偏估计；k∈{1,2,4,…,256}，Avg 为 9 个 k 的算术平均。答案抽取：“any-boxed”规则——任一 boxed 表达式在归一化（Hendrycks 2021）后匹配真值即算对；论文说这只放宽答案位置，不放宽正确性，会同时提高 base 和训练模型（对 Minerva 影响尤大）。单卡 vLLM，batch 1000。

### 3.4 数字（Table 1，均为表格数值）
Base（pass@1 / pass@256 / Avg）：MATH-500 64.5/96.2/86.8；Olympiad 28.5/78.5/58.0；Minerva 24.4/80.9/57.6；AIME25 7.4/53.3/27.5。
各方法 pass@1 / pass@256（相对 base）：
- MATH-500：REINFORCE 75.5/92.0（-4.2）；GRPO 77.5/93.0（-3.2）；W-RF 75.5/93.8（-2.4）；BBG 75.6/96.6（+0.4）。
- Olympiad：REINFORCE 38.2/68.7（-9.8）；GRPO 39.6/71.5（-7.0）；W-RF 38.2/74.6（-3.9）；BBG 37.1/78.5（±0）。
- Minerva：REINFORCE 37.3/72.4（-8.5）；GRPO 39.2/74.6（-6.3）；W-RF 39.4/76.8（-4.1）；BBG 37.1/81.1（+0.2）。
- AIME25：REINFORCE 10.4/50.0（-3.3）；GRPO 10.8/46.7（-6.6）；W-RF 9.4/53.3（±0）；BBG 9.9/63.3（+10.0）。
- 小 k 与大 k 的典型交叉：Olympiad 上 GRPO k=1 +11.1、k=8 +1.3、k=16 -0.9、k=256 -7.0；Minerva 上 GRPO k=16 -2.0。交叉点在 k≈8–16。
- 注意：这里基线 pass@256 的下降（Olympiad -7 到 -10 点，Minerva -4 到 -8 点）比 Yue Table 3 的 MATH500/Omni 变化大，且与训练 epoch 数有关（20 epoch；Table 2 显示 W-RF 早停 5 epoch 时 Minerva pass@256 79.4，Olympiad 77.4，接近 base）。

### 3.5 “265 题”分析（附录 C，Figure 3/6/7）
- 在三个留出基准上 base 下 Pass@256=0 的题：AIME25 15 + Minerva 57 + Olympiad 193 = 265。
- epoch 2：70/265（26.4%）进入边界；其中 27 题 ≥2 次正确，3 题 ≥5 次正确。Minerva 18/57（31.6%，9 题 c≥2，2 题 c≥5）；Olympiad 47/193（24.4%，15 题 c≥2，1 题 c≥5）。
- epoch 20（第 140 步）：38/265（14.3%）仍在边界内；其中 17 题 c≥2，3 题 c≥5，1 题 c≥10。
- 6 个检查点累计：134/265（50.6%）至少进入过一次；64/265 至少一次 c≥2；11/265 c≥5；4/265 c≥7；68/265 连续两个检查点都在内。
- 损失：epoch 20 时 711 个 base 可解题中 152 题掉出（21.4%），其中 91 题 base 下 ≥2 次正确，32 题 ≥5 次。净变化 38−152=−114（占 976 题的 −11.7%），与总体 pass@256 下降吻合。
- 噪声检验：Fisher 精确检验形式的条件概率 P_noise(c)：c=1 为 0.5、c=2 为 0.2495、c=5 为 0.0306、c=7 为 0.0075、c=10 为 8.93e-4。结论：单次成功的“进入”是弱证据；c≥5（5% 水平）、c≥7（1% 水平）才能排除重采样噪声。**所以 “70→38” 的头条数字里大部分是 c=1 的弱事件（epoch 2：70 中只有 27 题 c≥2，3 题 c≥5）。**
- 分桶干预（Figure 4）：只在零成功桶 B0/8 里更新，MinervaMath 和 OlympiadBench 上 Pass@256 高于 base（图中数值未提取到，仅有 y 轴刻度；Minerva 约 84 以下、Olympiad 约 80 以下的刻度，不可当作读数）；B1/8、B4/8、B8/8 逐级下降。每个设置单次训练。

### 3.6 什么训练使边界扩张？为什么缩小？
- 扩张：标准 RLVR（含 GRPO/REINFORCE/W-RF 的训练动态）早期（entry 峰值在早期 epoch）就让部分 base 不可解题进入 Pass@256 边界；只更新 B0/n（零成功桶）更有利，因为是唯一未饱和的桶。
- 缩小：因为训练 n=8 时，一次成功就使 p̂≥1/8，在 k=256 下 Pass@256=1−(7/8)^256≈1−1.43e-15，近乎饱和；此后对这些题的任何更新（无论强化正确还是压低错误）都不能扩张边界，只会锐化策略（“overtraining”），使 loss 累积、entry 衰减。验证 Pass@1 在 epoch 5 后停滞（训练集成功率 68.69%→77.06%，MATH-500 验证 pass@1 稳在约 72%），B7/8+B8/8 桶权重从 16.0% 升到 64.3%。epoch 5→20：Minerva+Olympiad 平均 pass@1 37.3→37.7，pass@256 75.2→70.6。
- 附录 B：B0/8 并不干净，已在边界内的题在 8 次 rollout 中也常观测到零成功（如 J256=0.9 时 P(p̂=0)=93.1%，J256=0.999 时 80.6%）；增大 n 可使 B0 更干净（p=0.05 时泄漏率 n=8:66.3%，n=16:44.0%，n=32:19.4%）。

### 3.7 与 Yue 的关系（论文 2 的立场）
不否认 pass@k 总体下降，但认为总体下降≠没有新能力；标准 RLVR 对大 k 指标有结构性偏差。同时承认 AIME 上 Yue 报告的 k=1024 退化与自己的解释一致。

### 3.8 论文 2 的自述局限与我发现的弱点
- 自述：只有一个训练集、7B 规模；多样性坍缩可能有 token 级信用分配、奖励稀疏等其它原因；BBG 以较大 pass@1 下降为代价。
- 我读到的弱点（事实陈述，非判决）：单种子单次训练（A.8）；进入判定为二值阈值，c=1 弱事件占多数；B0/8 桶的“零成功”不等于真不可解；评估用 any-boxed，会提升 base，论文自己说有“答案暴露”因素；只用 Qwen2.5-Math，论文未讨论该模型对 MATH/Minerva/Olympiad 类数据的预训练暴露；AIME25 只有 30 题（pass@256 一题≈3.3 点，BBG +10.0 即 3 题）；Table 1 无置信区间；表中 BBG 的 Avg 提升与 pass@1 下降并存（Olympiad pass@1 37.1 vs GRPO 39.6，Minerva 37.1 vs 39.2）。
- 自我博弈 / 无标签：未讨论。文中仅在相关工作提到“RLVR 在极小或不完美训练信号下仍提升”（Wang 2025、Shao 2026），并解读为“部分是答案格式暴露/指令遵循”。

---

## 4. Implications for testing self-improvement loops（仅陈述事实）

### 4.1 公平的 checkpoint-vs-base pass@k 比较必须固定的项（据两篇论文）
1. **温度与 top-p**：两篇均用 T=0.6、top-p=0.95。Yue 明确指出温度会改变排序：base 在 T>1.0 变差，RL 模型对温度不敏感；用熵匹配的温度（RL T=0.85–1.5，视基准）后差距缩小但没有消失。因此必须固定温度，且最好报告至少一个熵匹配/多温度的对照。
2. **n 与 k 范围**：n 至少等于最大 k；Yue 的 n 取 128/256/1024，论文 2 取 256；用 Chen et al. 2021 的无偏估计 1−C(n−c,k)/C(n,k)。AIME 类难题要 k 到 1024 才能看到 base 追上；论文 2 指出 k 范围内能否“进入饱和区”取决于基准难度，AIME 在 k≤256 内仍在低成功率区，因此结论随 k 范围改变（k 太小看不出坍缩，难题上需更大 k）。
3. **曲线而非单点**：两篇都在 k=1 到 256+ 上报告曲线；交叉点出现在 k≈8–16（论文 2 的 Olympiad/Minerva），所以只报 pass@1 或只报 pass@256 会给出相反结论。
4. **最大生成长度与截断**：Yue 统一 16,384（代码 32k，Magistral 40k）；论文 2 评估用 4096，高于训练 3072 以免截断。比较双方需用同一上限，且不得短于任一方习惯的长度。
5. **prompt 与格式**：Yue 对 base 与 RL 用同一个零样本 prompt，不给 base few-shot，因为 few-shot 本身是混杂；base 靠大量采样才会产生可解析的格式。论文 2 的 any-boxed 抽取使 base 和训练模型都提高，说明抽取规则是被试变量之一，必须固定并对两边同样应用；两篇都提醒格式/答案暴露会冒充推理增益。
6. **答案抽取与验证**：数学用规则归一化（Hendrycks 2021）；k 增大后“猜对”增多，Yue 在最难的小子集上手工核对 CoT（GSM8K 24/25 与 23/25；AIME24 过滤后 5/6 与 4/6）。代码用单元测试，基本无猜对问题。
7. **基准选择**：Yue 用 6 个数学、3 个代码、2 个视觉基准；论文 2 用 MATH-500（训练同分布，pass@256 上限 96.2 因而坍缩几乎不可见）、Olympiad、Minerva（中等难度，坍缩最明显）、AIME25（30 题，粒度粗）。难度适中的“近边界”基准最敏感；过易（天花板）或过难（k 范围未到饱和）都会掩盖效应。
8. **边界分析用问题级配对**：同一批题、同一采样协议下分别算 base 与 checkpoint 的可解集（Yue Table 2/5/6；论文 2 的 entry/loss 追踪）。判定 entry/loss 时，论文 2 的 Fisher 精确检验显示：c=1 时 P_noise=0.50，c≥5 才 <0.05，c≥7 才 <0.01，所以需要报告 c 的阈值，而不是二值“可解/不可解”。
9. **去污染 / 数据暴露**：两篇论文都**没有做**去污染实验。Yue 引用 LiveCodeBench（带时间窗，2024.8–2025.1，宣称 contamination-free）；论文 2 用 Qwen2.5-Math-7B 并在 MATH 上训练、在 MATH-500/Minerva/Olympiad 上评估，未讨论预训练暴露。这是文中缺失项，不是论文给出的要求。
10. **起点模型的性质**：Yue 区分 zero-RL（从预训练 base 起）与从 instruct/蒸馏模型起（代码、视觉），后者的 base 本身已经过 SFT；“base 上限”的含义因此不同。自改进回路的“base”需要明确是哪一个。
11. **重复性**：Yue 的 RL 模型多为公开 checkpoint，自训部分每个设置单次；论文 2 明确“单次训练、固定数据洗牌种子”，vLLM 非确定。两篇都没有跨种子置信区间。差异在 ±1 点量级（Yue Table 3 的 MATH500 pass@256）时无法判断显著性。
12. **训练长度/检查点选择**：pass@k 退化随训练步数单调加重（Yue Table 4：Omni-Test pass@256 68.3→66.6→63.9；论文 2：epoch 5→20 pass@256 75.2→70.6，pass@1 几乎不变，早停 5 epoch 可保住大部分大 k 性能）。所以 checkpoint 的选择本身决定结论，需固定并同时报多个检查点。

### 4.2 论文警告的失败模式
- **pass@1 上升、大 k pass@k 下降**（Yue；论文 2）：被读作“边界缩小”；论文 2 认为这有一部分是训练对已解题的结构性过训练（n=8 时一次成功就在 k=256 下饱和），不一定意味着没有新能力；同时给出 38/265 保持与 152/711 丢失的净下降。两篇对同一现象给出相反解读，所以单个总体 pass@256 数字不足以区分“没学到”与“学到但被抵消”。
- **熵下降 / 锐化**：Yue 的 PPL_Base(Y_RL|x) 随训练下降；论文 2 的“sharpening within C(x)”。
- **猜对与格式暴露**：Yue 的 CoT 有效性检查；论文 2 的 any-boxed。
- **有限样本噪声**：论文 2 附录 C，一次成功的“进入”和“丢失”都可由重采样噪声产生。
- **n≪k 的零成功桶泄漏**：训练时用 n=8 的零成功桶识别“不可解题”，会误含大量已可解题（80%–98%）。
- **基准天花板与题量**：MATH-500 的上限使效应不可见；AIME 只有 30 题，一题=3.3 点。
- **混杂因素**：Yue 的蒸馏对比使用外部强教师，不属自生成数据；代码/视觉的“base”是已 SFT 模型；DAPO 的动态采样训练成本高 3–6 倍，pass@256 掉得明显。
- **与自改进回路相关的缺口**：两篇都只覆盖有真值验证器的 RLVR；无标签/自博弈/迭代自训练（如 Absolute Zero、STaR、ReST）的 pass@k 边界测量在这两篇中没有结果。
