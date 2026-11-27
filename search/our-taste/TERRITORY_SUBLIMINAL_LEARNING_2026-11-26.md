# Territory：Subliminal Learning——只看一串数字，学生能学到多少？

**our-taste 通道 · 初稿 2026-11-26 · 修订 2026-11-27（用户指定主投 ICML 2027）**
**状态：** 2026-11-27 已注册为 workbench [`subliminal-knowledge-transfer`](../../workbench/subliminal-knowledge-transfer/README.md)（PROPOSED）。执行以该 workbench 的 RESEARCH_PLAN 为准，本卡只保留为选题记录。原状态：提议，尚未开 workbench。**主线与方法未定**：方向见 [集中讨论文档](SUBLIMINAL_LEARNING_DISCUSSION_2026-11-27.md)（A–F 并列）；本卡中的“通道 × 解码器”只是对应方向 A、B 的一组候选假设，讨论后可能整体改写。是否登记、占哪个名额由用户决定（R2/R7）；当前 ACTIVE-MAIN 与 ACTIVE-EXPLORE 都已占用。
**文献底稿：** [`library/themes/training-post-training/SUBLIMINAL_LEARNING_MAP_2026-11-26.md`](../../library/themes/training-post-training/SUBLIMINAL_LEARNING_MAP_2026-11-26.md)（约 40 篇，标了阅读深度与核对状态）。

---

## 0. 一页摘要

- **领域：** 教师带某种特质（偏好、misalignment、能力、后门），生成**语义无关**的数据（数字、代码、改写文本）；学生在这些数据上微调后获得该特质。原始发现见 Cloud et al.（2025-07，*Nature* 2026）。
- **现状：**
  - 现象已被大量复现，并扩展到能力、后门、agent、RL judge、VLM 等。
  - “为什么”仍然是一团矛盾：LoRA 还是全参、Adam 还是 SGD、是否必须同初始化，至少六种机制在相互反驳。
  - 几乎所有阳性结果都依赖 Qwen2.5-7B-Instruct，种子 ≤5，学习率协议也不统一。
- **候选问题之一（方向 A、B；其余方向见讨论文档）：**
  - 一串硬 token 里到底装了多少关于教师的信息（**通道**）？
  - 学生能从中解出多少（**解码器**）？
- **候选假设（未验证，不作为主线）：**
  - **通道**：可迁移的信息量受迁移数据上“教师 vs 基座”的累积对数似然比（KL 预算）约束。这能统一解释三件事：logit 蒸馏比采样 token 高效得多、divergence tokens 承载信号、按似然差过滤数据能放大迁移。
  - **解码器**：在固定的 KL 预算下，能否把信号解出来，取决于学习器的归纳偏置。按 ICML 2026 关于硬标签与旋转不变算法的结果类推，坐标级自适应（Adam）、低秩分解（LoRA）、稀疏正则这类**非旋转不变**的学习器应当在少量数据下就能解码，而旋转不变的 GD / 全参 SGD 需要随维度增长的数据量。如果成立，Adam/SGD、LoRA/全参、“正则放大迁移”、“数据量够大时全参也迁移”这四个矛盾可以收进一个解释。
  - **竞争假设：** Chen et al.（2610.04907）把 GD 看作阻尼逐渐减弱的 Fisher 逆；按这个思路，Adam 的作用可能只是“预条件 ≈ 近似逆曲率”，与旋转不变性无关。两种假设在“把稀疏目标旋转成稠密基”时给出相反预测（见 §8 D4-a），这是第一个要做的判别实验。
- **目标会议：** **ICML 2027**（官方：摘要 2027-01-14，全文 2027-01-22，AoE；来源 [icml.cc 2027 Reciprocal Reviewing 页](https://icml.cc/Conferences/2027/ReciprocalReviewingAndSubmissionQuotas)，正式 CfP 待发布）。截稿时主张不够就转投 NeurIPS 2027（`workbench/EXECUTION.md` §7），不关线。
- **为什么适合 ICML：** 这是“理论 + 受控实验”形态。核心预测可以在线性 / logistic 玩具上精确检验，再到 LLM 上检验能否外推；ICML 2026 已经接收了硬 / 软标签理论（rotation invariance、Bridge–Garden）和 LLS（log-linearity）。

---

## 1. 热度卡

- **venue corpus**（主会议，标题或摘要含 subliminal）：2024–2025 年接收数为 0；2026 年 ICLR 3、ICML 1、NeurIPS 4、EMNLP 3。ICLR 2026 切片接收率 43%（3/7），全会基准 24%。
- **arXiv：** 16 个月里约 35 篇后续，**2026 年 10–11 月约 12 篇**。
- **对手：** Nanda/Conmy 组、Evans（Truthful AI）、CMU Raghunathan、Hewitt、MATS、Redwood。不是算力碾压（单次实验是单卡 7B LoRA），但迭代很快。
- **读法：** 热度中高、主流解释尚未定型；接收论文的证据规模普遍不大，“统一解释 + 严格对照”是空位。风险在于有人抢先给出统一解释，见 §6。

## 2. 谱系卡

1. **软标签与知识容量。** Hinton 2015（dark knowledge）→ Behrens & Zdeborová 2025（软标签在随机输入上泄露 held-out 知识）→ Cloud 2025（硬 token + 无关数据 + 同初始化也能传）→ Beyond Owls 2026（随机函数、后门可传；新信息基本只经 logit 通道）。
   - **缺口：** 硬 token 通道的容量从未被量化。
2. **学习动态理论。** Cloud 单步定理 → Li 2026（PSD 核，NeurIPS workshop）/ Liu 2026（trait-direction drift，per-sample preference gap，NeurIPS）→ Blank 2026（steering-vector 蒸馏，NeurIPS）→ **Chen 2026-10（2610.04907：带噪线性逆问题；GD ≈ 阻尼递减的 Fisher 逆；硬标签在低曲率方向放大采样噪声，所以需要数万条载体，软标签只需几百条）**。
   - **缺口：** 理论都是 GD 线性化，实验都用 Adam；Blank 说 Adam 必要，至少 5 篇说 SGD 也行；没有一篇把优化器 / 参数化的几何（Adam、LoRA、全参）放进理论并给出缩放预测。
3. **信号定位。** Zur 2025（token 纠缠）→ Schrodi 2026（divergence tokens，ICLR）→ Nief 2026（实体 token、早期 FFN，v2 自称部分结论有误）。
   - **缺口：** token 局部解释与全局方向解释从未在同一组运行上对照。
4. **跨模型。** Cloud（需同初始化）→ Brockers（输出头兼容）/ Tang（Pythia↔OLMo 可迁移）/ Phantom Transfer（自然语言数据跨模型，NeurIPS）/ LLS（跨架构，ICML）。
   - **缺口：** “数字通道是模型特异的、自然语言通道带有细微语义”只被暗示过，没有受控检验。
5. **硬 / 软标签理论（相邻领域）。** ICML 2026 *Hard labels sampled from sparse targets mislead rotation invariant algorithms*：对稀疏目标，旋转不变算法（GD）超额风险为 Ω(d/n)，重参数化（u⊙v）算法为 O(s log d / n)。ICML 2026 *Bridge–Garden*：混合硬 / 软标签降低 exposure bias。
   - **我们的连接点：** 把 SL 视为“从硬标签中解码一个低维 / 稀疏的教师偏移”。这一连接尚无人做过（待验证代理核实，§7）。

## 3. 形态卡（面向 ICML）

- **corpus 读数：** `shapes` 切片（subliminal / hidden signal / EM / poisoning，ICLR）中，接收论文均分 6.12、finding 线索 62%；被拒论文以 method 为主（64%），均分 4.44。发现 / 解释型更容易被收。
- **目标形态：** B（理论 + 受控实验）为主，A（测量构念：容量曲线）为辅。只有找到真实瓶颈时才做 C（方法 / 防御）。
- **ICML 近邻里的标杆：**
  - LLS（ICML 2026）：log-linear 结构理论 + 真实数据选择 + 跨架构；
  - Hard-label rotation invariance（ICML 2026）：纯理论 + 简单实验；
  - Bridge–Garden（ICML 2026）：理论分解 + 7 对师生模型；
  - Distillation Scaling Laws（ICML 2025）：大规模受控测量。
- **ICML 审稿人会要的证据（我们的标准）：**
  - 理论预测先在线性 / logistic 与 MNIST 辅助 logit 玩具上**定量**成立（斜率、阈值随 d 和 s 的缩放）；
  - LLM 上至少 2 个家族（Qwen2.5-7B + Llama-3.1-8B 或 Gemma-3-4B）；
  - 每个条件 ≥3 个数据种子 × ≥3 个训练种子，配 95% CI；
  - 每个条件单独扫描学习率；
  - 评测 prompt 敏感性写进附录。
- **主图设想（每张对应一条待验证主张）：**
  1. 迁移量 vs 累积 KL 预算：硬 token 与 logit 两种通道落在同一条曲线上？
  2. 解码阈值 n* vs 维度：旋转不变与非旋转不变学习器的缩放差异（玩具 + LLM）。
  3. 随机绑定的比特回收：硬 token 能否传递基座里不存在的信息。
  4. 用同一个框架复现文献中的矛盾（Adam/SGD、LoRA rank、全参 + 数据量）。

## 4. 立足点卡

- **可直接跑的基线：**
  - lmb-freiburg/divergence-tokens（MIT，ICLR 2026；6 个开源模型，7B LoRA 单卡可跑）；
  - MinhxLe/subliminal-learning（官方代码与数据，含 MNIST 辅助 logit 玩具）；
  - TruthfulAI-research/beyond_owls。
- **算力估计（按公开数字推算，未实测）：**
  - Nief 约 10k 次运行用了约 12k GPU·时，即 7B LoRA 每次约 1 GPU·时；
  - 7B 全参 AdamW 需要单节点多卡（约 112GB 优化器状态）。全参对照先在 Qwen2.5-1.5B/3B 上做，7B 只做关键格。
- **标准协议：**
  - 动物偏好：一词回答类问题统计目标动物出现率；
  - misalignment：judge 打分；
  - 对照：未加特质的教师；
  - 跨模型矩阵。
- **我们的比较优势：**
  - 独立单卡槽位多，适合“数据种子 × 训练种子 × 学习率 × 学习器”的受控网格。Nief 报告数据种子主导方差，而多数论文只换训练种子。
  - mechanism-population 线有 PolyPythia 多 seed 的经验与审计记录（`workbench/mechanism-population-dynamics/suite-audits/`），可用于“同架构不同 seed”的初始化对照。
  - lm-head 线有梯度几何、BF16 精度地板的工具。

## 5. 压力清单（按对论文的作用排序）

| # | 压力 | 出处 | 在论文中的位置 |
|---|---|---|---|
| P1 | **通道容量未知。** 新信息几乎只经 logit 蒸馏传过去：采样版随机函数 R²=0.00；采样版后门（换了 steering-vector 教师、单次运行）在约 340 万条之后才首次出现。Chen 2610.04907 解释了硬标签为什么需要更多数据，但**没有给出能传多少比特、上限由什么决定**。另外，Beyond Owls 按似然差过滤数据，Liu 的 per-sample preference gap 预测漂移，Schrodi 的 divergence tokens 承载信号——三者都指向“教师 vs 基座的似然差”是关键量，但没人把它当作信息预算来测。 | Beyond Owls；Liu；Schrodi；Chen；Hinton | 主图 1、3 |
| P2 | **解码器矛盾。** Adam 必要（Blank）vs SGD 可行（Morgulis、Feng、Tang、Xu）；LoRA 倒 U（Nief，固定 lr）vs 单调（Feng，逐 rank 调 lr）；全参不迁移（Nief、Blank）vs 数据量大时迁移（Feng 500k）；正则放大迁移（Feng）。 | Blank；Nief；Feng；Morgulis | 主图 2、4 |
| P3 | **跨初始化。** 数字数据跨模型≈0，自然语言数据跨 10 个模型都迁移，Pythia 跨 seed 可迁移。在通道 × 解码器框架下，可以解释为异基座使“解码器”失配，而自然语言通道的 KL 预算中有可跨模型读取的语义成分。 | Cloud；Phantom；Shah；Tang；Madl | 讨论 / 扩展实验（视时间） |
| P4 | **信号是 token 局部的还是全局方向。** 两边都有阳性证据，从未在同一组运行上同时检验。 | Schrodi；Nief；Blank；Hadley | 附录或后续工作 |
| P5 | **Qwen 依赖与 prompt 敏感性。** 仅 system prompt 就造成 2–5× 差异。 | Nief；Schrodi；Morgulis | 实验卫生前提 |

## 6. 定位与 compression risk

| 最近邻 | 它占有的 claim | 我们的增量（目标） | compression risk |
|---|---|---|---|
| **Chen et al.（预印本 2026-10，2610.04907）** | 硬 vs 软标签的样本复杂度来自 Fisher 逆与采样噪声；软标签几百条、硬标签数万条 | (1) 学习器维度：Adam / LoRA / 全参的差异及其随 d 的缩放，Chen 只分析 GD；(2) 容量：任意新信息（随机绑定）能传多少比特，而不只是恢复一个 steering 方向；(3) 跨模型 / 跨通道 | **高**：硬 / 软差距这一条几乎被占有。主图 1 不能只是“硬标签需要更多数据”，必须给出比特上限和学习器缩放 |
| Liu et al.（NeurIPS 2026，trait-direction drift） | 每个样本的 preference gap（似然差）驱动沿特质方向的漂移；corridor 正则 | 把似然差上升为**信息预算**，用于预测任意新信息的可迁移比特数；比较硬 / 软通道；加入解码器维度 | **高**：审稿人可能说“Liu 已经用似然差解释了”。必须展示 Liu 解释不了的东西：通道比较、容量上限、学习器缩放 |
| Blank et al.（NeurIPS 2026，steering-vector 蒸馏） | 可 steer 性预测迁移；Adam 必要 | 用旋转不变性解释“为什么 Adam 必要、什么时候 SGD 也行”，并给出数据量阈值的缩放预测 | 中 |
| Feng et al.（预印本 2026-11，正则放大迁移） | 低 rank、L1、更多数据都放大迁移 | 给出机制性理由（非旋转不变 / 稀疏归纳偏置）和定量缩放；多 seed | **中高**：方向最接近；若他们先补上理论，我们的增量就只剩通道部分 |
| Beyond Owls（预印本 2026-10） | 能力、后门可传；logit 通道远比采样高效 | 量化这一效率差距并预测它，在全参与多家族上检验 | 中 |
| Hard-label rotation invariance（ICML 2026） | 线性 logistic 中，硬标签让旋转不变算法吃亏 | 把该结论迁移到 SL 设置，并在 LLM 上检验 | 低（他们不涉及 SL），但要讲清楚理论贡献是“应用 + 验证”还是“新定理” |
| LLS（ICML 2026） | log-linear 结构 → 选子集诱导特质 | 我们讨论的是从教师生成的数据中解码，不是数据选择 | 低 |

**已核（2026-11-27）：** 在 84 篇含 subliminal 的 arXiv 摘要中，没有一篇用教师 / 基座 KL 或对数似然比给迁移设上限，也没有一篇测量硬 token 通道能传多少比特或任意新信息。最近的是 Chen（样本复杂度）和 Liu（用似然差做相关，不是上限）。只检索了标题和摘要，正文中是否有类似分析未知。

## 7. 核对状态

- **2026-11-27 已对原文逐条核对 12 组关键数字**，7 组有误，已在本卡和文献地图中改正：
  - Beyond Owls：80.9% 是 Nemotron 直接训练的结果；约 340 万条是采样版首次出现法语的时点（数据集 450 万行，换了 steering-vector 教师，单次运行）；“50 倍”是数据集大小之比，不是受控效率比；教师并非全是 LoRA。
  - Liu：相关系数为 +0.769 至 +0.845；corridor 降到 6.45%；preference gap 的基线是 K 个中性 prompt 的平均。
  - Tang：90–97% 是同一模型预训练轨迹内 checkpoint 网格的因子模型，不是跨模型配对；Pythia↔OLMo 的超出率只有 14%。
  - Blank：arXiv 上没有 venue comments，NeurIPS 会议页存在。
  - Cloud：跨模型原文措辞是“do not reliably”，比“≈0”弱。
  - 其余（Schrodi、Nief、Feng、Phantom）确认；Feng 的种子数为主图 2–3 个、附录多为单 seed。
- 未核对的数字在文献地图中没有 `核✓` 标记。
- OpenReview 读不到，没有审稿意见。

## 8. 驻留（D1–D6），按 ICML 需要的证据排序，不排日期

1. **D1 复现与噪声地板。**
   - 用 divergence-tokens 代码在 Qwen2.5-7B 上复现 cat/owl 数字迁移，跑 3 个数据种子 × 3 个训练种子；
   - 对照：未加特质的教师；
   - 记录 system prompt 敏感性；
   - 并行跑 MNIST 辅助 logit 玩具（CPU）。
2. **D4-a 理论玩具（最便宜、最具决定性）。**
   - 线性 / logistic 教师–学生：教师偏移是 s-稀疏或低秩的，学生只看硬采样标签或软标签；
   - 比较 GD、Adam、u⊙v / 低秩重参数化，测解码阈值 n* 随 d 和 s 的缩放。
   - **判别 Chen 式“预条件 ≈ 逆曲率”与旋转不变性假设：** 把同一个稀疏偏移用随机正交矩阵旋转成稠密基。旋转不变性假设预测 Adam 的优势在旋转后消失；逆曲率假设预测优势取决于曲率谱，不受这种旋转影响。
   - 这一步在跑之前就写好决策表：缩放与旋转结果符合旋转不变性 → 进 LLM；符合逆曲率 → 主旨改为“曲率 × 学习器”，并与 Chen 重新定位；两者都不符 → 解码器假设作废，P2 回到纯测量。
3. **D4-b LLM 通道测量。**
   - 对每条迁移数据记录教师 vs 基座的对数似然比，验证迁移量是否随累积预算单调；
   - 比较硬 token 与 top-k logit 两种通道；
   - Qwen + 第二家族。
4. **D4-c 随机绑定容量。**
   - 教师植入 K 个随机“名字→属性”绑定；
   - 测硬 / 软通道、LoRA / 全参（全参先在 1.5–3B 上做）各自能回收多少比特；
   - 阳性对照：直接 SFT；阴性对照：干净教师。
5. **D4-d 矛盾复现。**
   - 在同一网格里复现 Blank（Adam/SGD）、Nief/Feng（rank × lr）、Feng（全参 × 数据量），看框架能否同时解释。
6. **D2 / D3 / D5 / D6**：管线与 hash 入账；痛点日志；定位表（至少覆盖 §6 与 Schrodi、Nief、Tang、Phantom、Morgulis、Brockers）；形态卡与 3–6 张 idea 卡。

**若最终选方向 A/B，ICML 的最小可投包大致是（示例，待讨论后重写）：**
- D4-a 的缩放预测成立（L2，多种子）；
- D4-b 在至少 2 个家族上显示迁移量随 KL 预算有序（L2）；
- D4-d 至少解释两个文献矛盾。

D4-c 与 P3 视进度而定，可作为扩展或留到 NeurIPS 2027。到截稿时达不到最小包，就转投 NeurIPS 2027。

## 9. 风险

| 风险 | 可能性 | 对策 |
|---|---|---|
| 强组先发表统一解释（Feng 组最近） | 中高 | 先跑 D4-a 玩具（便宜，能最早知道假设死活）；每次主旨变化都重扫近邻；如果被抢，就把增量转向通道容量（P1） |
| 被压缩成“Chen 已经解释了硬标签需要更多数据” | 高 | 主旨不能停在硬 / 软差距；必须拿出 Chen 框架（只有 GD、只有方向恢复）给不出的东西：学习器缩放与旋转判别（D4-a）、任意新信息的比特容量（D4-c） |
| 被压缩成“Liu 的 preference gap 换了个名字” | 中 | 主图 1 / 3 必须展示 Liu 的框架预测不了的量（硬 / 软通道差距、比特上限、学习器缩放） |
| 旋转不变性类比在 LLM 上不成立（特质偏移并不稀疏或低秩） | 中 | 先在 LLM 里测教师偏移的有效秩 / 稀疏度；不成立时 P2 退回为“严格的受控测量”，仍可作为证据贡献 |
| 效应只在 Qwen 上成立 | 中 | 从一开始就跑 2 个家族；只在 Qwen 上成立本身也要报告（P5） |
| 结论平凡（“硬 token 当然信息少”） | 中 | 给出定量容量、缩放律和学习器依赖，而不是二元结论；决策表预先写好每种结果改变什么认识 |

## 10. 决策（人签字）

- **用户 2026-11-27：** 目标会议定为 ICML 2027。
- **待定：**
  - 是否登记 workbench；
  - 名额：替换现有 ACTIVE 线，还是先以 PROPOSED 状态做 D1 与 D4-a。
