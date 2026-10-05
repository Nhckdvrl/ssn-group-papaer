# 领域地图：ICL 中的证据聚合（evidence aggregation in ICL）

**建立：** 2026-10-05（持续更新；每读一批论文就改这里，单篇深读卡在 `papers/`）

## 0. 一句话画像
ICL 研究在 2021–2026 形成了四条互相不太对话的线：
1. **“ICL 是 Bayesian 推断吗？”**（Xie 2022 → Falck 2024 martingale → Arora 2024 Bayesian scaling → Bigelow 2023/2025 belief dynamics → Gupta 2025 coin flips）——把 context 当证据，问 LLM 的 p(y|context) 像不像某个后验。几乎全部默认 **证据可交换（计数式累积）**：Bigelow 2025 的模型 log p(x|c) ∝ −#不一致标签，再乘 N^{-α} 的亚线性折扣。
2. **“顺序/位置效应是缺陷”**（Zhao 2021 calibrate、Lu 2022 order、Fang ICLR'25 InvICL、Li 2025 Order Matters、Jiao 2026 conflict）——把 recency/primacy 当 bias 去修。
3. **“非平稳/相关数据下的 ICL 理论”**（Bai 2023 in-context algorithm selection、Qin ICLR'26 GLA recency、Dudley ICML'26 change-point、Letey 2026 sequential correlation、Park ICLR'25 competition phases）——多在从头训练的小 transformer / 线性注意力上做，证明“能做到”。
4. **ICL 机制可解释性**（Olsson induction heads、Hendel/Todd task/function vectors、Cho ICLR'25 三步电路、Cho ICLR'26 information removal、Yang ICLR'26 TR/TL heads、Yang NeurIPS'25 geometry）——在真实 LLM 上找“编码→合并→检索复制”电路；recency 被解释成 **表示相似度的位置偏置**（Cho 2025 §3.2/§5.3）。

**它们之间的裂缝（我们驻留的地方）：** 线 1 默认可交换计数、线 2 把顺序依赖当 bug、线 3 说顺序依赖在非平稳时是对的、线 4 的电路天然是“逐条检索+投票”的**可加**结构。没有人问：**真实 LLM 的证据权重究竟是一个固定的位置核（可加），还是依赖证据的整体组织（非可加、像在推断生成过程）？** 这决定了“order sensitivity 是 bug 还是对非平稳先验的理性对冲”。

## 1. 已被占有的结论（不能当我们的 novelty）
| 结论 | 主人 |
|---|---|
| ICL 对顺序敏感；iid demos 应该置换不变 | Lu 2022；Fang ICLR'25；Li 2025 |
| 真实 LLM 违反 martingale/exchangeability | Falck ICML'24 |
| label 关系中途翻转后偏向近处信息（D→F / F→D / 交替，等数量） | **Kossen ICLR'24 §8**（最直接的父工作） |
| 单个 corrupted demo 能显著误导规则归纳；位置偏置；vulnerability/susceptible heads | Jiao 2026 |
| 非平稳回归下 recency/gating 有利 | Qin ICLR'26 |
| transformer 可以做 in-context change-point 检测（构造+训练） | Dudley ICML'26 |
| 相关序列改变有效 context 长度 | Letey 2026 |
| ICL 学习曲线 sigmoid、可用 Bayesian belief 模型拟合；steering=改先验 | Bigelow ICLR'24 / 2025 |
| LLM 在多轮对话中 belief stay/update/isolation 失败（逻辑证据、显式更正） | Xu 2026 BeliefTrack |
| transformer 可以 in-context 选择算法（理论） | Bai NeurIPS'23 |

## 2. 领域真正关心的问题（为什么我们的答案有人在乎）
- **ICL 到底在做什么推断**：Bayesian 视角的争论（Falck 说不是 Bayesian；Bigelow/Arora 说可以用 Bayesian 模型高精度预测）。若 LLM 对 *生成结构本身* 做推断，二者可调和：违反 exchangeability 不是“非 Bayesian”，而是“Bayesian 但先验允许非平稳”。
- **many-shot ICL / 长上下文**：亚线性证据累积（power law, Anil 2024; Bigelow 2025 的 N^{-α}）缺乏解释；非平稳先验天然产生旧证据折扣。
- **Agent / 长对话的 belief 更新**：何时应该改主意（BeliefTrack、reversal learning 的 LLM 研究）——我们的受控任务给出最小可测版本。
- **机制**：induction/retrieval 电路是逐条可加的；如果行为是非可加的，电路图里缺一个“结构/一致性”信号——直接给 Hakaze 系电路研究提出新对象。

## 3. 跨领域参照
- **认知科学：stochasticity vs volatility**（Behrens 2007；Nassar 2010；Piray & Daw 2021 Nat Commun）——理性学习者必须同时推断“环境多吵”和“环境多常变”，二者对学习率作用相反（噪声↑→学习率↓；波动↑→学习率↑）。这是我们 noise-vs-change 设计的直接理论来源：**同样的后缀反例，前缀噪声越多越不该认为是规则变化**——固定核/集合学习者预测相反方向。
- 统计：Bayesian online change-point detection（Adams & MacKay 2007）；hidden Markov 规则切换模型。

## 4. 我们的测量对象（持续修订）
- 证据权重是否 **可加**：用单条翻转估计位置核 w_t，预测多条翻转组合；残差即结构敏感性。
- 与 exact meta-oracle（联合推断 λ 波动率与 ε 噪声率）的对应：LLM 隐含的 hazard / noise 先验是多少？
- 方向相反预测的关键对照（noisy-prefix vs clean-prefix + 相同后缀）。

## 5. 驻留后的位置（2026-10-05 下午，pilot 证据）
我们的测量把四条线接上了：
- **对线 1（Bayesian ICL）**：潜在规则层面的证据是可交换计数（与 set oracle r≈0.98–0.99，Bigelow'25 的计数式 belief 模型因此有效）；违反 exchangeability（Falck'24）在潜在层面是无方向的顺序特异性波动（post-training 放大：Base 0.75 → Instruct 1.16 nats），不是“更信任新证据”。
- **对线 2（顺序是缺陷）**：Kossen'24 的 recency 是固定位置核；真正的结构推断（噪声 vs 变化）在潜在层面完全缺失——前缀噪声的方向相反检验在 11 个模型（0.6B–32B，4 个族）、自然语言（SST-5）、T=64 都方向错误。
- **对线 3（非平稳理论）**：能力存在，但只在表层：纯标签流（或标签流 + 无关输入/独特 id）上模型是方向正确的变化检测者（成簇效应 +7~+11 logits，前缀噪声 −4~−7）。
- **对线 4（机制）**：注意力在标签流中集中于末尾标签游程（76% vs 均匀 25%），在规则任务中按输入相似度分配（Cho'25 的检索电路）；表层游程甚至会把潜在证据带向反方向（E08 anti：−0.92）。
**一句话：LLM 知道“标签变了”，却不知道“规则变了”。**

## 6. 傍晚更新：三种聚合方式（方向相反检验是关键判别器）
方向相反检验（前缀加零散噪声：结构推断 → 更不信后缀反例；任何正权重的可加核 → 更信）把 ICL 的证据聚合分成三类：
1. **近似变化点推断**（噪声方向规范）：标签流、格式变换（大写↔反转）、数值偏移（±1/±3/±10，强度随模型能力）。
2. **仅 recency（可加的位置核）**：词汇型函数（反义↔同义、英→法↔西/德、字母后继）——有成簇与过时折扣，但噪声方向错。这正是 Kossen'24 观察到的“偏向近处”的类型。
3. **可交换集合**：按输入路由的映射（nonce 规则、SST、奇偶/大小翻转、类别条件变换）——连 recency 都很弱。
机制：时间（不）敏感性已存在于 query 处的任务状态（E17b，ρ=0.95）；标签流的结构推断由晚层游程头承载（E10）。原因：任务同质的训练统计（E12 toy 从零复现；E18 LoRA 部分修复）。
**对领域的意义：** “ICL 是 Bayesian 吗”的争论需要按 regime 类型分开回答；“order sensitivity”在三类里含义完全不同（结构推断 / recency 偏置 / 无方向的特异性噪声）。
