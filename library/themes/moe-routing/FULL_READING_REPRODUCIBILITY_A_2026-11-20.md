# 全文精读 A：MoE 路由可复现性三篇（2026-11-20）

用途：division 11-20 候选问题的近邻定位。候选问题：独立训练的 MoE 在逐条路由决策上大多不一致，但在固定词形、置换不变、扣除“同一隐状态上的随机路由器”零模型之后，**分区**（哪些 token 出现被归到一起）是否可复现；我们自训小模型显示分区可复现度（除以精确重跑上限）随专家数上升（16 专家 .13，64 专家约 .5，256 专家 .81）。问题：独立训练之间的分歧是嵌套在共享的粗专家组里，还是横穿这些组；随专家数和规模如何移动。

三篇都按全文读（正文、所有表格和图注、局限、附录）。阅读方式：arXiv HTML 转成文本逐段读，表格和图里的数字从 PDF（`pdftotext -layout`）中补读，关键图渲染成图片核对读数。

---

## 卡 1　Xin, "MoE Pretraining: Parallelism Layout Changes the Model, Not Quality"（arXiv 2611.15271v1，2026-11-11，cs.DC）

**读的来源**：https://arxiv.org/html/2611.15271（HTML 不含表格内容，表格无法渲染）+ https://arxiv.org/pdf/2611.15271（19 页，表 1–7 和图 1–6 的数字从这里读）。
**读的范围（全文）**：Abstract；§1 Introduction（Our question / Main findings / Why it matters）；§2 Background in Plain Terms（Router and near-ties / Layouts / Two kinds of layout effects / How we measure "different"）；§3 Related Work；§4 Experimental Setup（Models and data / Real parallel training / Runs）；§5.1–5.7；§6 What This Means in Practice；§7 Limitations；§8 Conclusion；Appendix A（Correctness checks）、B（Additional results：表 6、表 7、图 6）、C（Reproducibility）。
**没能看到的**：代码和 CSV 数据“将随论文发布”（github.com/ethxin0011/moe_parallelism），我没有去看仓库。"spread of that token's scores" 的具体定义（标准差还是极差）论文没写。

### 研究问题与主张（原文）
- 问题（§1 "Our question"）："Does the parallelism layout change the trained MoE model—and if so, why, and does it get worse as experts get more fine-grained?"
- 主张 1（§5.1）："Every layout ends with the same validation loss as the reference, within seed-to-seed variation. But the predictions end about 80% as different as a new seed would make them, and over 90% of routing decisions differ."
- 主张 2（§5.2）：按机器计算的规则（负载均衡统计、容量单位）"creates differences about 400× larger at the start of training, yet the final difference is the same as for a pure layout change."
- 主张 3（§5.3）："The routing decisions that flip between two runs are almost exactly the ones where the router's last chosen expert and the best unchosen expert had nearly equal scores." 但 "Near-ties explain where the divergence starts; once started, it spreads on its own."
- 主张 4（§5.4）："going from 8 to 64 experts raises the share of near-tie decisions from 2.7% to 23.3% and the share of routing decisions that differ at the end from 68% to 100%. The difference in the model's outputs, however, stays at about 0.8× the seed level for every expert count." 并给出解释性猜测："Many small experts appear to be largely interchangeable: a token sent to a different expert still gets a similar result."
- 主张 5（§5.5）：同激活规模的稠密模型更稳定（fp32 下 0.12×，fp16 下 0.58×）；"the router makes MoE divergence close to all-or-nothing."
- 主张 6（§5.6）：在 10% 处切换布局会显著改变最终模型，在 84% 处几乎不改变。

### 设置（表 1、表 2）
- 模型：Qwen3-MoE 风格的仅解码器模型，从头训练。基础 MoE 6 层、宽 256、4 头、RoPE、RMSNorm、QK-Norm、无 QKV bias、词嵌入绑定；**16 个 SwiGLU 专家（宽 256），top-4，无共享专家**；约 25M 总参数 / 10M 激活参数。
- 更大尺寸（GPU）：m = 宽 384、8 层（约 68M）；l = 宽 512、8 层（约 117M），都是 16 专家。
- 专家数扫描（GPU，fp16）：8/16/32/64 专家，对应 top-2/4/8/16，专家宽 512/256/128/64，**总参数和激活参数都固定**（注意：k 随 E 一起放大）。
- 路由器 / 负载均衡：辅助损失（系数 0.01，softmax 路由器），或无辅助损失的 bias 调节（sigmoid 路由器，bias 步长 1e-3）。容量因子 1.25，训练时丢 token（先保留 top-1 选择），评估时不丢。
- 数据：FineWeb-Edu sample-10BT，16,384 词表 BPE；每步 32×512 token，1,221 步 = 20M token（表 1 写的是“120M training tokens”可用，实际只训练 20M）。AdamW，峰值 LR 1e-3，100 步预热后恒定（没有衰减）。
- 硬件：CPU fp32（Azure E16s_v3，gloo，最多 8 个 rank，数学库固定在 AVX2 路径）；GPU fp16（单张 T4，最多 4 个 rank 共用）。
- 变化的量：9 种 DP/EP 布局；噪声尺子（4 个新种子、3 种新数据顺序、3 次 1-ULP 权重扰动）；线程数；按 rank 计算的规则；loss-free 均衡；稠密对照；中途换布局续训；fp16；模型尺寸；专家数。共 80 次训练（表 2）。
- **所有非种子比较都共享初始化**，因此专家编号可以直接对齐。

### 度量（§2、表 3、表 4 注）
- 主度量：同一步、同一组 16,384 个留出 token 上两次运行的下一词分布 KL；再除以“只换种子”的两次运行之间的 KL，得到 "vs. own seed"（1.0 = 和换种子一样不同）。
- Top-1 agree：最可能预测一致的比例。
- **"Routing differs"**："the share of (token, layer) decisions whose chosen expert set differs; it is not shown for seed runs, where expert numbers are not comparable."（表 3 注）。这是**按专家编号、整组精确匹配**的度量，**不是置换不变的**；作者明确说种子之间无法比较，所以没算。
- Loss barrier：两组权重直线插值上的最大损失升高（线性模式连通性）。
- Margin：第 k 名与第 k+1 名路由分数之差除以该 token 路由分数的 spread；margin < 0.01 记为 near-tie。
- AUC：随机取一个翻转的决策和一个没翻转的决策，翻转那个 margin 更小的概率。
- 附录表 6："Expert imbalance" = 各层最常用专家份额 / 平均份额 − 1 的层平均；"Tokens dropped" = 被容量丢弃的分配比例。

### 基线 / 零模型 / 对照
新种子（作为归一化单位）、新数据顺序、1-ULP 扰动、线程数改变、稠密同激活规模模型、per-rank 与 global 规则的配对对照、正确性检查（各布局梯度相对误差 < 1e-4；同布局两次运行逐位相同；检查点跨布局迁移无损）。**没有任何置换不变的路由比较，没有随机路由器零模型，也没有分区层面的度量。**

### 主要结果（含数字）
- 表 3（MoE，fp32 CPU，最终）：
  - 新种子：KL 0.350，1.00×，top-1 一致 0.664，barrier 3.538。
  - 新数据顺序：KL 0.512，1.46×，top-1 0.590，**路由不同 96%**（同初始化）。
  - 不同布局（8 种平均）：step 8 时 KL 4.1e-9，最终 0.280，0.80×，top-1 0.689，**路由不同 92%**，barrier 0.417，loss 变化 +0.005。
  - 1-ULP（3 次）：0.283，0.81×，93%，barrier 0.432。
  - 线程数：0.277，0.79×，92%。
  - per-rank 规则（9 次）：step 8 时 1.7e-6；最终 0.282，0.80×，95%，barrier 0.486。
  - loss-free 新布局：0.285，0.84×，97%；loss-free per-rank bias：0.285，0.83×，96%，barrier 0.580。
  - fp16 GPU vs fp32 CPU：0.279，0.80×，93%。
  - 稠密：换种子 0.365；换布局 0.043（0.12×），top-1 0.862；1-ULP 0.048（0.13×），barrier 0.000。
- 验证损失（表 6）：参考 + 8 种布局 4.576–4.610（均值 4.587），新种子 4.582–4.626；稠密对照 4.654；fp16 m 4.508，l 4.454。不均衡度约 0.28；loss-free 时 0.52，丢弃 5.37%。
- 时间进程（图 1，§5.1）：step 8 时约 4e-9，step 64 时约 2e-2，之后到 0.28；各种小扰动从 step 32 起走同一条曲线。
- 近似并列机制（表 4，step 8 / 16）：fp32 布局 / ULP / 线程的 AUC@8 = 1.000，step 16 时翻转比例 0.06–0.10%，AUC 0.968–0.985，翻转决策的 margin 中位数 0.0001–0.0002，未翻转 0.073；margin 最小的 10% 翻转率 0.56–0.86%，其余 90% 为 0.005–0.012%。per-rank 容量：翻转 3.36%，AUC 0.946；per-rank 均衡损失：2.52%，AUC 0.950。fp16 专家数：8E 翻转 0.44%，AUC 0.897，未翻转 margin 中位数 0.234；16E 0.23% / 0.965 / 0.073；32E 0.25% / 0.979 / 0.049；64E 0.32% / 0.985 / 0.026。step ≥128 后 AUC 降到约 0.6（图 2a）。
- 专家数（表 5，fp16，DP2/EP2，总 / 激活规模固定）：
  | E (top-k, 宽) | near-tie | KL@32 | KL@64 | 最终 KL | vs seed | 路由不同 |
  |---|---|---|---|---|---|---|
  | 8 (2, 512) | 2.7% | 2.9e-4 | 3.5e-2 | 0.274 | 0.80 | 68% |
  | 16 (4, 256) | 6.6% | 4.5e-5 | 4.7e-2 | 0.284 | 0.81 | 94% |
  | 32 (8, 128) | 11.9% | 9.9e-5 | 2.6e-2 | 0.292 | 0.85 | 100% |
  | 64 (16, 64) | 23.3% | 8.8e-8 | 2.5e-2 | 0.272 | 0.81 | 100% |
  | dense (1024) | – | 5.8e-8 | 5.8e-4 | 0.206 | 0.58 | – |
- 稠密对比（§5.5，图 4）：fp32 下稠密模型前 16 步 KL < 1e-10，step 128 时 7e-7（MoE 7e-2）；fp16 下所有 MoE 在 step 64 越过 0.01，稠密在 step 128；step 64 时 MoE 的差异是稠密的 40–80 倍。
- 中途换布局续训（§5.6，图 5）：84% 处（step 1,024）切换 → KL 0.007（约种子水平 2%），路由不同 15%；10% 处（step 128）切换 → KL 0.12–0.13（约 35%），路由不同 58–61%；两种情况 barrier 都是 0；切换布局与 1-ULP 扰动表现一样。
- 模型尺寸（表 7，16E，fp16）：base / m / l 的 near-tie 6.6% / 6.8% / 7.8%；step 32 KL 4.5e-5 / 5.5e-3 / 5.7e-3；最终 0.284 / 0.285 / 0.281；vs seed 0.81 / 0.88 / 0.86；路由不同 94% / 98% / 97%。

### 作者自述的局限（§7）
规模（25M–117M，20M token，远低于计算最优），"The exact ratios (for example, 0.8× the seed level) will change with longer training"；单节点 / 单 T4，gloo 而非 NCCL，没测张量并行 / 流水并行；没测 bf16/FP8；**专家数扫描和尺寸实验每个设置只有一个种子、一种布局**；GPU 上 1-ULP 扰动常被 fp16 转换吞掉；per-rank 规则在大规模下可能伤质量；只有恒定 LR 的预训练，续训只有两个切换点；容量因子 1.25 且丢 token（很多生产 MoE 不丢）。

### 批判性评估
1. **“路由不同”的度量与 k 混杂。** 它是“所选专家集合是否完全相同”。专家数扫描里 k 跟着 E 放大（2→16），选 16 个专家整组完全一致远比选 2 个难，所以 68%→100% 有相当一部分是度量本身的机械效应。它没有报告 per-slot 一致率、Jaccard 或置换不变的度量，所以“专家越多路由越不可复现”这个结论被高估了。
2. **对象是同初始化下的扰动，不是独立训练。** 所有布局 / ULP 运行共享初始化（loss barrier 0.42，换种子是 3.5），因此编号可以对齐；它恰好**没有**比较独立种子之间的路由（"expert numbers are not comparable"）。
3. **训练很短**（20M token，LR 恒定），路由在 step 128 后才开始扩散，最终比值作者自己也说会随训练长度变化。
4. 专家数和尺寸结论每格只有 n = 1，没有置信区间。
5. “小专家可互换”是**猜测**，没有测量：作者没检查翻转后的新专家与原专家是否功能相近或属于同一组。
6. 优点：因果链条很干净（正确性检查、per-rank 与 global 的配对拆分、AUC 机制），而且从 KL / barrier 的角度给出了“输出差异不随 E 增长”的可用数字。

### 与我们候选问题的关系
- **它已认领的**：(a) 小扰动（布局 / 1 bit / 线程数）在同初始化下导致 >90% 路由决策不同，而质量不变；(b) 起点是 near-tie 翻转（AUC 0.97–1.00），之后自行扩散；(c) 固定总 / 激活规模时，专家越多 near-tie 越多、按编号整组匹配的路由一致率越低，但输出 KL 不变；(d) 预训练早期敏感、后期不敏感。“逐条决策大多不一致”这半句话，在同初始化扰动这一设置下，已经被它占了。
- **它留下的空白**：没有置换不变的度量；没有独立种子之间的路由比较；没有分区 / 词形固定 / 零模型；没有检查分歧是否落在“可互换”的专家组内部。
- **和我们“分区可复现度随专家数上升”的观察**：**不矛盾**，两者测的是不同对象（同初始化 vs 独立种子；整组按编号精确匹配 vs 置换不变分区）。反而形成一个张力，可以写进论文：按编号的决策一致率随 E 下降（它的表 5），输出差异却不随 E 增长（同一张表），它用“小专家可互换”来解释。我们的嵌套问题恰好可以**直接检验这个解释**：如果分歧嵌套在共享粗组内部（翻转只发生在可互换的兄弟专家之间），那么“决策一致率降、输出不漂移、分区一致率升”三件事可以同时成立。
- **压缩风险：中等。** 审稿人可能会说：“路由不可复现、并且随细粒度变差，Xin 2026 已经有了。”回应要点：(i) 它是同初始化扰动，作者自己承认独立种子之间编号不可比，所以没测；(ii) 它的度量与 k 混杂；(iii) 我们的方向（置换不变分区随 E 上升）与它的方向相反，而且它自己提出的“可互换”假说正是我们要测的对象。**必须做的防守**：报告我们的专家数扫描里 k 和专家宽度怎么变（固定激活规模还是固定 k），并补一个按 slot 的一致率，免得被说成同样的 k 混杂。
- **可直接借用的**：它的 margin / near-tie 度量可以作为我们“分歧发生在哪里”的协变量（预测：翻转集中在低 margin 位置，并且留在同一粗组内）；它公开的代码 / CSV 可以作为同初始化扰动的参照点（ceiling 的另一种形式）。

---

## 卡 2　Wang, Hayou, Nalisnick, "The Myth of Expert Specialization in MoEs: Why Routing Reflects Geometry, Not Necessarily Domain Expertise"（arXiv 2604.09780v1，2026-04-10）

**读的来源**：https://arxiv.org/html/2604.09780（全文含表格）+ https://arxiv.org/pdf/2604.09780（31 页，用来读图中的模型名和读数；第 4 页图 1、第 8 页图 6/7 渲染成图片核对）。
**读的范围（全文）**：Abstract；§1；§2 Related work（四段）；§3 Background；§4.1（Prop. 1、Triangle shape、Impact of load-balancing、Prop. 2、Auxiliary loss pushes router to de-correlate、Router confidence detects OOD）；§4.2；§4.3；§5.1–5.3；§6 Conclusion；Appendix A（全部 8 个度量定义：RMS Distance、Directional/Retained energy、Average cosine、Router Hamming similarity、Router confidence、Sequence-level frequency cosine、Pooled hidden-state cosine、Overlap under top-P）；Appendix B（Lemma 1 证明、B.1 Lemma 2 证明和几何解释）；Appendix C（C.1 gpt-oss 输出、C.2 Duplication 示例）；附录图 11–29 的图注。
**没能看到的**：附录很多图只有图注加图形，数值只能目测；论文没有表格形式的数值结果。

### 研究问题与主张（原文）
- 问题（§1）："(1) what mechanism produces expert specialization? and (2) to what extent are the resulting patterns humanly interpretable?"
- 机制主张（Abstract）："since MoE routers are linear maps, hidden state similarity is both necessary and sufficient to explain expert usage similarity, and specialization is therefore an emergent property of the representation space, not of the routing architecture itself."（注意：Prop. 1 只是一个上界，只能证明“相似隐状态 → 相似 logits”，证明不了“必要”；正文 §4.1 自己也说隐状态不同时 logits 可以相似也可以不同。）
- 负载均衡主张（Prop. 2）："the load-balancing objective forces the router to suppress the shared direction μ"；用来解释 Qiu et al. 2025 小 batch 均衡下专业化塌缩。
- 难以解释的三个例子（§1）："(1) different models solving the same math question activate expert patterns as dissimilar as those for entirely different questions (∼60% overlap, Fig. 6); (2) semantically different prompts activate nearly identical experts during prefilling, but diverge during generation (Fig. 7); (3) in deeper layers, sequences from unrelated domains can collapse to identical expert usage during prefilling."
- 结论（§6）："we should not expect the hidden state and router logit space to have a metric system aligned with human standards."

### 设置
- **不训练任何模型**，只分析公开预训练 MoE：
  - 图 1（Prop. 1 验证，中间层，16 条 OpenWebText 序列）：ERNIE-4.5-21B-A3B-Base、gpt-oss-20b、DeepSeek-V2-Lite、Moonlight-16B-A3B、Trinity-Mini-Base。
  - 图 2 / 15（深度与共享方向）：gpt-oss-20b（AdamW + 辅助损失）、Trinity-Mini-Base（Muon + 无辅助损失）、DeepSeek-V2-Lite（AdamW + 辅助损失）、Moonlight-16B（与 DSV2-Lite 同结构，Muon + 无辅助损失）。
  - 图 3（OOD）：ERNIE-4.5-21B、GPT-OSS-20B、Qwen3-30B。
  - 图 5 / 20–22（序列级）：中间层，100 条 OpenWebText + 100 条 Nemotron-CC-Math；gpt-oss-20b、ERNIE-4.5-21B-A3B-Base、Qwen3-30B-A3B 等五个模型。
  - **图 6（跨模型重叠）**：30 道 HMMT 2025 年 2 月题目，MathArena 中 60 个推理模型生成的解答，4 个采样种子；路由在 **Qwen3-30B-A3B、ERNIE-4.5-21B-A3B、gpt-oss-20b 三个 MoE** 上读取。
  - 图 7：Ling-mini（指令微调）；图 8–10：gpt-oss-20b（32 专家）、Ling-mini-base-2.0、ERNIE-4.5-21B-A3B(-PT)。
  - 稠密对照（图 12）：Qwen3-8B、Llama-3.2-3B、gemma-3-4b-pt；图 14 有 Qwen3-4B-Thinking-2507。
- 模型的专家数、top-k、共享专家等结构细节论文没有列表（只写了 gpt-oss-20b 有 32 个专家，以及各模型用辅助损失还是 aux-free、AdamW 还是 Muon）。

### 度量（附录 A 原式）
- RMSDist(x_i, x_j) = sqrt((1/D) Σ_d (x_{i,d} − x_{j,d})²)（Eq. 5），对 token 对的隐状态和路由 logits 分别计算。
- Energy_{ℓ:ρ} = Σ_{i=ℓ}^{ρ} s_i² / Σ_j s_j²（Eq. 7，序列隐状态矩阵的奇异值）。
- RetainedEnergy_i = (1/T) Σ_t ‖P v_i ⊙ m_t‖² / ‖P‖_F²（Eq. 8），m_t ∈ {0,1}^E 为 token t 的专家使用向量。
- 序列内平均余弦（Eq. 10）；Router Hamming similarity = 2/(T(T−1)) Σ_{i>j} m_iᵀ m_j / E（Eq. 11）。
- Router confidence = (1/T) Σ_t max_e softmax(P h_t)_e（Eq. 12）。
- 序列频率向量 p^(s) = (1/(TK)) Σ_t m_t^(s)（Eq. 13）；FreqSim = 余弦(p^(s), p^(s'))（Eq. 14）。
- 池化隐状态余弦：先 L2 归一化每个 token，再求平均，最后算余弦（Eq. 15–17）。
- **Overlap_P（图 6 用的度量）**：E_P^(s) = 按频率降序累积质量达到 P 的最小专家集合（Eq. 18）；Overlap_P(s, s') = |E_P^(s) ∩ E_P^(s')| / |E_P^(s) ∪ E_P^(s')|（Eq. 19，Jaccard）。
- **关键澄清（回答“跨模型重叠是否置换不变”）**：图 6 的“Same question, different models”指的是**不同生成模型写出的解答文本**，送进**同一个**分析用 MoE（Qwen3 / ERNIE / gpt-oss 各自一个面板）读取路由。所以比较始终在同一个 MoE 内部按专家编号进行：**按编号，不置换不变；但也不需要置换不变，因为两边是同一组专家**。它**不是**两个独立训练的 MoE 之间的比较。而且这是序列级频率聚合（top-p 集合），不是 token 级决策。论文没有明确说分析用的 MoE 本身是否在 60 个生成模型里。

### 基线 / 零模型 / 对照
- 图 6：三条曲线互为对照：同模型不同题（蓝）、同题不同生成模型（橙）、同题同模型不同种子（绿）。
- 图 3 / 23：打乱和反转 token 作为 OOD 对照。
- 图 13：朴素界 ‖P‖₂‖δ‖ 与投影界的对比（DeepSeek-V2-Lite，r = 1200）。
- 图 24：只保留隐状态前 K 个主方向后的专家选择一致率（第 10 层，50,000 个 Nemotron-CC-Math token，DSV2-Lite 与 Moonlight）。
- 图 10 / 26–29：重复输入 1×–12× 的剂量对照，以及有无 chat template。
- 有辅助损失与无辅助损失、AdamW 与 Muon 的模型对比（DSV2-Lite vs Moonlight 是同结构对照）。
- **没有随机路由器零模型、没有置换不变的跨模型比较、没有独立训练的重复。**

### 主要结果
- 图 1：五个模型的 token 对呈“三角形”：隐状态距离小 → logits 距离小；隐状态距离大 → logits 距离可大可小。离群点来自注意力汇聚点（首 token）。
- 图 13：残差比在 r = 1200 时集中在 0 附近；实际 logit 差远低于两个上界；由于 P 已经对齐数据主子空间，两个界之间的差距不大。
- 图 2 / 15：gpt-oss（AdamW + aux）中隐状态随深度越来越相关（第一奇异方向能量升高）；第 11 层以后路由输出的余弦不再随之上升；路由器在共享方向上的保留能量曲线与路由输出相似度同形。Muon 训练的 Trinity 中隐状态相关性不随深度增加；无辅助损失的模型看不到抑制共享方向的迹象（Moonlight、Trinity）。
- 图 3：打乱 / 反转输入时路由置信度（最大 softmax）低于原始输入（ERNIE、gpt-oss、Qwen3）；图 23：OOD 输入下 ‖PQ‖₂ 降低。
- §4.2 / 图 4：gpt-oss-20b 中，"apple" 在日常语境和代码语境下，第一层专家重叠高，深层重叠下降；作者认为 OpenMoE 的“context-independent specialization”是训练不足造成的。
- 图 5：序列隐状态相似度与专家频率相似度强相关；跨数据集的对聚在隐状态相似度更低处；部分模型呈三角形（多对一）。
- **图 6（top-p = 0.8，目测读数）**：三个 MoE 的所有层上，同题同模型不同种子 ≈ 0.8；同题不同生成模型 ≈ 0.6；同模型不同题 ≈ 0.6；“The gap is consistent across all layers.” 图 25：p = 0.7、0.6 时模式相同。
- 图 7（Ling-mini）：三对查询在 prompt 阶段专家频率余弦都接近 1；生成开始后，GAN vs VAE 一对保持高，plain vs math 语言和中文 vs 法文 AIME 两对随生成急剧下降（深层降到约 0.2–0.4）。
- 图 8（gpt-oss-20b）：在最后 k 层只保留 12/32 个最常用专家（用一段手写段落统计），只输入 prompt 时剪掉最后 2 层 NLL 增加 < 10%；加上补全（on-policy 或 off-policy）后 NLL 大幅上升。
- 图 9：HLE 题（411 token）和 Wimbledon 段落（2,500 token）在 prefill 阶段深层专家频率几乎相同；生成过程中分开，越深的层越早分开。
- 图 10 / 26–29：重复输入放大共享方向，跨领域专家使用相似度向领域内基线收敛；gpt-oss 加 chat template 时不重复也塌缩；ERNIE-PT（非推理模型）无此塌缩；重复还会提高 logit 幅度，使随机解码失去随机性。
- 图 24：只保留前 K 个主方向时，最大 logit 专家（m = 1）一致率在所有 K 下都很高；排序靠后的专家（m = 6）在 K = 1200/2048 时超过 40% 的 token 换了专家。

### 作者自述的局限 / 明确没做的
- 脚注 1："To rigorously verify this, a comprehensive set of experiments with MoE pretraining is required."：路由器–数据对齐项消失（"dead router"）这一情形他们没有实证。
- Prop. 2 是在小 logit、线性化 softmax、只有均衡损失的简化下得到的；B.1 末尾说实际中 "should only be partially observed"。
- 没有专门的局限章节。没有训练实验，没有独立重复，没有跨模型的专家对应。

### 批判性评估
1. **“必要且充分”说过头了。** Prop. 1 是上界，只给出“相似隐状态 → 相似路由”（充分方向），图 1 的三角形本身就说明“必要”不成立。
2. **图 6 的“完全不同的问题”其实都是同领域**（都是 HMMT 竞赛数学），而且在长推理链上，频率向量 top-0.8 集合会包含很多专家（负载均衡压平分布），Jaccard 有地板效应。没有不同领域的对照，也没有随机序列的零模型，所以“~60% 和不同题一样”说明的是“生成模型的风格与题目内容效应量相当”，不能直接推出“专业化不可解释”。
3. “不同模型解答”混合了文本风格、长度和格式差异，作者没有控制长度。
4. 大部分结果是单层、16–100 条序列、目测曲线，没有置信区间。
5. 优点：给出了“路由 = 隐状态几何的线性读出”的干净框架，有同结构不同优化器的天然对照（DSV2-Lite vs Moonlight），图 24 提供了“高排位选择稳定、低排位选择依赖尾部方向”的有用事实。

### 与我们候选问题的关系
- **它已认领的**：(a) 路由相似性由隐状态几何决定（线性路由器的上界）；(b) 负载均衡抑制共享方向；(c) 同一 MoE 内，不同生成模型写的同题解答的专家重叠约 0.6，与不同题相当；(d) 推理模型 prefill 时深层路由塌缩。
- **它没做的（我们的空间）**：两个独立训练的 MoE 之间的任何比较；置换不变的度量；token 级分区；固定词形；随机路由器零模型；专家数依赖。**它的“跨模型”与我们的“跨运行”不是同一个对象**，审稿人如果把图 6 当成“跨模型路由不一致已被证明”，属于误读，我们需要在定位表里写清楚。
- **对我们最大的威胁（压缩风险：中等，以审稿人论证的形式出现）**：既然路由是隐状态的线性读出，那么“分区可复现”可能只是“表示几何可复现”（表示收敛 / CKA 一类结果）的推论，而不是路由器自身的性质。我们的“同一隐状态上的随机路由器”零模型只能扣掉“任意线性投影都会得到的那部分”。一个**学习出的路由器对齐到隐状态主方向**同样可以被说成“只是几何”。**建议加一个更强的零模型**：把路由器换成“隐状态前 E 个主方向的投影”，或者在隐状态上做 k-means（簇数 = E、选 top-k 个最近质心），在同一组隐状态上计算分区，扣掉它之后再看剩余可复现度和随 E 的趋势。剩余部分才是路由器 / 训练特有的。
- **支持我们“嵌套”问题的线索**：图 24 显示 top-1 专家对去掉尾部方向很稳健，排位靠后的选择不稳。这给出一个可检验预测：独立运行之间的分歧应集中在低排位 slot / 低 margin，并留在主方向决定的粗组之内（嵌套），而不是横穿粗组。Prop. 2（共享方向被抑制）也意味着，不同运行的粗分区应由同一批“非共享”主方向决定，这是嵌套假说的一个机制来源。
- **对“随专家数上升”**：无相关数据，既不支持也不反对。

---

## 卡 3　Ternovtsii & Bilak, "Equifinality in Mixture of Experts: Routing Topology Does Not Determine Language Modeling Quality"（arXiv 2604.14419v1，2026-04-15）

**读的来源**：https://arxiv.org/html/2604.14419（全文含表格）+ https://arxiv.org/pdf/2604.14419（24 页；第 11 页图 5 渲染成图片读逐层数值）。
**读的范围（全文）**：Abstract；§1；§2 Background；§3.1–3.7（架构、几何余弦路由、专家参数化、多跳轨迹、训练、实验设置、可复现性）；§4.1–4.4；§5 Why Routing Topology Converges（Echo chamber、Frozen routing、Cross-seed expert stability、Identity falsification、Summary）；§6.1–6.2；§7.1–7.5；§8.1–8.6；§9 Related Work；§10 Conclusion（含 Limitations）；Appendix A（表 12）、B.1–B.5（表 13–16）、C.1–C.3（表 17、图 7–8）、D（表 18 实验索引）。
**没能看到的**：伴随论文 [1]（"Geometric routing enables causal expert control"，专家级专业化和因果可控性都放在那里）和 [15] 没读；下游评测的逐基准数字和 McNemar 表只在补充日志里，论文里没有。

### 研究问题与主张（原文）
- 问题（Abstract）："does routing topology actually determine language modeling quality?"
- 中心主张（§4.3）："five cosine-routing variants are statistically equivalent within a 1-PPL margin (TOST, p<0.05 for all 10 pairwise comparisons; 15 runs across 3 seeds, observed range 33.93–34.72)."
- 层级（§1）："routing capacity > routing mechanism > routing topology ≈ composition method ≫ expert capacity."
- 机制（§5）："multi-hop updates are collinear (cos(Δh0,Δh1)=0.805), implementing magnitude amplification rather than compositional reasoning; a single learnable scalar replicates multi-hop performance."
- 跨种子（§1 第 2 点）："Cross-seed analysis reveals 500×-above-random functional overlap through entirely different weight parameterizations—the quantitative signature of equifinality."
- 范围限定（§8.1）："We view our result as establishing a lower bound on topology invariance: within the class of cosine-routed MoE at ranks 1 and 16, topology does not matter."

### 设置
- 架构 ST-MoE（自定义，与 Google 的 ST-MoE 同名但不同）：pre-LN Transformer + RoPE + 词嵌入绑定；路由 = 把 token 线性投影到 d_space = 64 维并 L2 归一化，与 M 个 L2 归一化的可学习质心做余弦，乘温度 τ = 30，softmax 后取 top-k 并重新归一化（Eq. 2–3）。专家为秩 r 的 MLP：Δh = Σ w_i W_up,i SiLU(W_down,i h)（默认 r = 1，“singleton”）。多跳：每跳后用更新后的状态重新投影、重新路由，各跳共享专家（Alg. 1）。**无共享专家**；Switch 式辅助均衡损失 α = 0.05。
- 配置（表 1 / 表 12）：Small 36M（d768，4 层，M = 512，5k 步，82M token）；Large 76M（d1024，6 层，M = 1024，20k 步，328M token）；**Marathon**（d1024，16 头，8 层，M = 1024，50k 步，32,768 token/步，**1.64B token ≈ WikiText-103 的 14 个 epoch**，76–84M 参数）。默认 top-k = 4、H = 3 跳、bf16、dropout 0.1、LR 3e-4 余弦衰减到 0.1×。数据 WikiText-103，32K BPE；OpenWebText 复现（507M token，约 6.5 epoch）。
- 种子：主种子 42；多种子验证 42、137、7（5 个变体 × 3 = 15 次）。62 个实验，约 460 GPU 小时（RTX 3090）。
- 变化的量：路由拓扑（Wide 1×12、Deep 3×4、Magnitude Hack、Asymmetric depth、Decoupled per-hop proj）、线性路由器、d_space = 341 的等参数余弦路由、更大专家、hash / 随机固定 / top-1 路由、秩 16 专家（256 专家，4 层）、K×τ、组合函数。
- 内部不一致（读到的，需要知道）：§3.5 写 200 步预热，表 12 写 1,000 步；表 1 中 Large 为 6 层，Marathon 为 8 层，但 §3.6 文字写“three configurations at two model sizes”。

### 度量
- 主度量：验证 PPL / 交叉熵；50 个验证 batch 上的配对 bootstrap（10,000 次重采样）95% CI；TOST 等价检验，δ = 0.03 nats（约 1 PPL），用 90% CI 判断（B.2）；块 bootstrap（块大小 5、10）（B.5）。
- 回声室：20,480 个 token 上的 cos(Δh₀, Δh₁)。
- 冻结路由：所有跳都用 pos₀，看 PPL 变化；“Normal Jaccard” = 跳间所选专家的 Jaccard。
- **跨种子专家对齐（§5，图 5）**：种子 42 与 137 的收敛检查点（Wide 和 Deep 各一对）：(1) 每个专家投影到词表后取 top-20 词，与另一种子 **1024 个专家中最相似的那个**（best-match）算 Jaccard；(2) 原始 W_up 向量的 best-match |cos|。随机基线：Jaccard 约 0.0003（随机 20 词集合），|cos| 约 0.116（"by extreme value theory for 1024 vectors in R^1024"）。**这是专家内容的 best-match（多对一、非一一匹配、无匈牙利算法），不是路由决策或分区的比较。**
- 恒等性检验：每个专家的 cos(W_down, W_up)。
- 专家贡献：专家更新范数 / 注意力输出范数；把专家置零后的 PPL。

### 基线 / 零模型 / 对照
iso-FLOP 稠密（d_ff = 12 或 48）、iso-param 稠密（d_ff = 1120）、线性路由器作为“负等价对照”（B.4：比最好的余弦变体低 0.033 nats，90% CI [−0.041, −0.025]）、d_space = 341 的等参数路由、hash / 随机固定路由（路由不学习）、跨种子比较的随机基线（见上）。

### 主要结果（含数字）
- 表 2（iso-FLOP，36M，欠拟合）：稠密 d_ff = 12 → 306.01，singleton MoE → 304.50（−0.5%）；稠密 d_ff = 48 → 302.24，Block MoE Wide 1×6×8 → 298.91（−1.1%）。
- 表 3（Marathon，最终 PPL；3 种子均值 ± std）：稠密 iso-FLOP 34.49；稠密 iso-param 29.36；Wide 1×12 33.93（34.22 ± 0.25）；Deep 3×4 34.62（34.65 ± 0.03）；Decoupled 34.05（34.05 ± 0.10）；Magnitude Hack 34.11（34.10 ± 0.08，α 收敛到 5.04）；Asymmetric 34.59（34.60 ± 0.12，总跳数少 29%）；线性路由器 32.76（8.39M 路由参数）；余弦 d = 341 为 33.14（闭合 67% 差距）；更大专家 34.92；hash 36.04；随机固定 35.03；top-1 36.14；秩 16 Wide 1×4 37.77（37.72 ± 0.08）；秩 16 Deep 2×2 38.30（38.27 ± 0.05）。
- 逐种子：Wide 33.93 / 34.35 / 34.37；Deep 34.62 / 34.67 / 34.67；Mag 34.11 / 34.17 / 34.02；Asym 34.59 / 34.49 / 34.72；Decoupled 34.05 / 33.95 / 34.14。变体间均值极差 0.60 PPL，是平均种子 std（0.12）的 5.0 倍。
- 表 13：10 对里 6 对的配对 CI 不含 0（最大 Wide vs Deep −0.023 [−0.031, −0.015]），但都在 δ = 0.03 内。表 14：δ = 0.02 时 5/10 对等价，0.03 和 0.05 时 10/10。表 15：Wide 种子 42 vs 137 差 −0.013（显著），Deep 差 −0.003（不显著）。表 16：块 bootstrap 下 10/10 对仍等价；Wide vs Deep 的下界 −0.030 正好落在边界上。
- §4.4 下游（HellaSwag、ARC-E、WinoGrande）：差 1.6–2.9 个百分点；δ = 2pp 时 9 对里只有 1 对等价；PPL 最好的 Wide 在 HellaSwag 和 ARC-E 上下游最差（p < 0.01）；接近随机水平。
- §5：cos(Δh₀, Δh₁) = 0.805（Decoupled 时 0.049）。表 4 冻结路由：20k 步时 268.60 → 286.76（+6.8%），跳间 Jaccard 0.102；50k 步时 34.62 → 37.26（+7.6%），正常跳间 Jaccard 已是 0.970。
- **跨种子（图 5，逐层目测）**：best-match 词表 Jaccard，Wide 各层 ≈ 0.18、0.13、0.127、0.14、0.17、0.16、0.147、0.157（均值 0.15）；Deep ≈ 0.123、0.10、0.125、0.125、0.14、0.155、0.148、0.183（均值 0.13）。best-match |cos(W_up)| 各层 ≈ 0.105–0.109，均值 0.107，**低于**它声称的随机基线 0.116。
- 恒等性：8,192 个专家的 cos(W_down, W_up) 均值 0.157；0.0% 的 |cos| > 0.8，62.3% 的 |cos| < 0.2。
- §8.5：专家更新范数是注意力输出范数的 39.6%（Wide；第 7 层 14.5%，第 3 层 72.0%）和 148.2%（Deep）；专家置零后 PPL 33.9 → 494.5（Wide），34.6 → 846.9（Deep）。
- 表 5 / 6（halting）：收敛模型 ε = 0.10 → 平均 2.25 跳，节省 25.0% FLOPs，+0.12% PPL；ε = 0.02 → 节省 14.2%，+0.00%。延迟 4.32 → 3.26 ms。
- 表 7–9（36M 欠拟合）：Micro（M = 512，秩 1，Deep）304.50 vs Macro（M = 64，秩 8，Wide）298.91；rank-4/512 质心（304.50）优于 rank-16/128 质心（337.26），作者解释为“质心密度”。
- 表 10：curriculum halting 后 3 跳 316.14、1 跳 318.62（“Greedy Horizon”）。表 11：K×τ 共 10 个配置都在 0.82 PPL 内，最好是 K = 24、τ = 15 的 33.85。
- §8.2：OpenWebText 复现 Wide 34.25 ± 0.20，Deep 34.22 ± 0.02（差 0.03）；Wikitext 上训练 / 验证差 +0.13（Wide），+0.15（Deep）。

### 作者自述的局限
§8.1（只覆盖余弦路由、秩 1 / 16；"plausible that equifinality breaks down for architecturally more diverse comparisons—e.g., top-2 with 8 full-rank experts (Mixtral-style) vs. top-12 with 1024 rank-1 experts"）；§8.2（WikiText 14 个 epoch，有记忆化顾虑）；§8.3（76–138M，"we cannot claim it generalizes to billion-parameter models"）；§8.4；§8.6（顺序专家循环比稠密慢 1.8 倍）；§10（下游接近随机水平；hash 路由的退化在专家数更多时变大）；hash / 随机 / top-1 都只有单种子。

### 批判性评估
1. **“等价”的结论在相当程度上取决于 δ 的选择**：δ = 0.02 时只有一半的对等价；6/10 对有显著差异；变体间极差是种子噪声的 5 倍。准确的说法应该是“差异小”，而不是“拓扑不决定质量”。
2. **跨种子对齐分析很弱**：只有一对种子；best-match 是多对一（可能很多专家都匹配到同一个对方专家），会把 Jaccard 抬高；随机基线 0.0003 是“均匀随机抽 20 个词”，没有考虑 Zipf / 高频词，所以“500×”严重夸大（任何两个专家都会把高频词投影到前列）。权重 best-match |cos| 0.107 低于它自己的随机基线 0.116，说明这个随机基线本身就没校准，或者权重是各向异性的。
3. 它只测质量和专家内容，**完全没有比较跨种子的路由决策或分区**。
4. 14 个 epoch 的小语料训练，加上 rank-1 专家和余弦路由，都是非常规设置，对标准线性路由 top-k MoE 的外推有限。
5. 文中有若干内部不一致（预热步数、层数），而且伴随论文没公开。

### 与我们候选问题的关系
- **它已认领的**：在它的余弦路由 rank-1 MoE 里，不同路由拓扑 / 机制收敛到相近质量（“等终性”）；跨种子专家权重不对齐，但词表投影上有“高于随机”的功能重叠（best-match Jaccard 0.13–0.15）。
- **它没做的**：跨种子的路由决策 / 分区比较；置换不变的一一匹配；固定词形；路由器零模型；专家数扫描下的跨种子对齐（只有 M = 1024）；标准线性路由器的跨种子分析。
- **和我们“随专家数上升”的观察**：没有直接数据。它的 Micro / Macro“质心密度”叙事（专家越多，路由空间越密，多跳越好）与我们“更多专家 → 分区更可复现”方向上有些呼应，但它测的是 PPL，不是可复现性，不能当证据。
- **压缩风险：低到中。** 审稿人可能会说“跨种子专家功能重叠已被 Ternovtsii & Bilak 报告”。回应：它的度量是专家内容的 best-match、零模型是朴素的、只有一对种子、只有一个专家数，而且不涉及路由分区；我们的贡献正是带严格零模型的分区度量及其随 E 的移动。它的“质量等终但路由可以不同”的框架，可以作为我们“质量相同 → 分区是否也相同”的动机之一引用。
- **借来的线索**：它引用的 Tran et al. 2025（NeurIPS，"On linear mode connectivity of mixture-of-experts architectures"：同结构独立训练的 MoE 在置换对齐后落在同一损失盆地）是我们问题**最直接的近邻之一**（置换对齐 + 独立训练），需要确认已有卡片覆盖到它的度量和专家数设置。另一个是 Wang et al. 2026 "standing committee"（2601.03425）。

---

## 三篇合并的定位结论（供 positioning 表用）
| | 对象 | 跨什么比较 | 置换不变？ | 分区 / 词形固定 / 零模型 | 随 E |
|---|---|---|---|---|---|
| Xin 2611.15271 | 同初始化 + 数值扰动 | 布局 / 1-ULP / 线程 | 否（按编号整组精确匹配；种子之间明确不算） | 无 | 按编号的一致率随 E 降（与 k 混杂），输出 KL 不变 |
| Wang 2604.09780 | 公开预训练 MoE | 同一 MoE 内，不同生成模型的文本 | 不适用（同一组专家，按编号） | 无；只有序列级 top-p Jaccard | 无 |
| Ternovtsii 2604.14419 | 自训余弦路由 rank-1 MoE | 两个种子 | best-match（非一一匹配），只比专家内容 | 无 | 无（M 固定为 1024） |

- 三篇**都没有**在独立训练的 MoE 之间做置换不变的路由分区比较，也没有随机路由器零模型和固定词形的控制，更没有给出分区可复现度随专家数变化的曲线。在这三篇的范围内，我们的核心测量和“嵌套还是横穿”的问题没有被占。
- 需要在论文里正面处理的两点：(1) Xin 的“专家越多，路由越不可复现”要正面回应（对象不同，度量与 k 混杂，并且它的“小专家可互换”猜测正是我们要测的）；(2) Wang 的“路由 = 几何”带来的混淆，需要用比随机路由器更强的几何零模型（PCA 投影 / k-means 路由）去扣除。
- 不确定 / 未核对：Xin 的 margin 中 "spread" 的具体定义；Wang 图 6 中分析用 MoE 是否也是生成模型之一；Ternovtsii 伴随论文 [1] 的内容。
