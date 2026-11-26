# Territory：Subliminal Learning——无关数据中的隐性迁移（2026-11-26，our-taste）

- **来源：** 用户 2026-11-26 在三个候选方向中选了这一个，并点名 *Beyond Owls* 值得关注。本卡只是提议，**不开线、不改 ACTIVE 分配**（R2/R7）；当前 ACTIVE-MAIN 与 ACTIVE-EXPLORE 都已占用。
- **文献底稿：** [`library/themes/training-post-training/SUBLIMINAL_LEARNING_MAP_2026-11-26.md`](../../library/themes/training-post-training/SUBLIMINAL_LEARNING_MAP_2026-11-26.md)（约 40 篇，标了阅读深度；数字未逐一对原文复核）。
- **对应组内偏好：** 表征 / 可解释性、post-training 学习信号、蒸馏。我们在 mechanism-population 线积累的“同初始化 vs 不同 seed”经验和 PolyPythia 使用经验可以直接迁移过来。
- **目标会议：** 主投 ICLR / ICML / NeurIPS；若贡献偏“测量与构念”，也可以投 ACL / EMNLP 主会。
- **范围：**
  - 做：同基座和跨基座蒸馏中，语义无关数据到底能传递什么、靠什么传递。
  - 不做：
    - 再造一个“又一种特质也能传”的存在性证明；
    - 纯攻击论文；
    - 需要前沿 API 模型的实验。

## 热度卡
- **venue corpus**（主会议，标题或摘要含 subliminal）：2024–2025 年接收数为 0；2026 年 ICLR 3、ICML 1、NeurIPS 4、EMNLP 3。ICLR 2026 切片接收率 43%（3/7），全会基准 24%。
- **arXiv：** 16 个月里约 35 篇后续，**2026 年 10–11 月就有约 12 篇**，增长很快。
- **资源碾压？不是算力碾压，但人强。** 作者群包括 Nanda/Conmy 组、Evans（Truthful AI）、CMU Raghunathan、Hewitt、MATS、Redwood。单次实验只需单卡跑 7B LoRA，但对手迭代很快（Nief 的论文 v2 已经自己声明“部分主要结论有误”）。
- **读法：** 这是**热度中高、仍在上升、主流解释尚未定型**的领域。它不符合用户指南里“热度中低”的偏好；可取之处在于，文献内部的矛盾异常集中，我们的实验卫生（多数据种子、学习率扫描、对照）正好是现有论文最缺的。按 Sasano 品味，要警惕研究对象半衰期短。缓解办法是问一个**换了更强模型之后仍然成立**的问题（见压力 P1）。

## 谱系卡
1. **dark knowledge（Hinton 2015）→ 软标签泄露 held-out 知识（Behrens & Zdeborová 2025）→ Cloud 2025：硬 token + 无关数据 + 同初始化也能传 → Beyond Owls 2026：随机函数和后门也能传，但新信息只经 logit 通道。**
   - 改变的前提：教师输出里的“与任务无关的方差”本身也是知识载体。
   - 遗留问题：硬 token 通道的容量。
2. **单步定理（Cloud）→ PSD 核（Li 2026）/ 特质方向漂移（Liu, NeurIPS 2026）→ steering vector 蒸馏（Blank, NeurIPS 2026）。**
   - 已知局限：理论都是 GD 线性化，实验却都用 Adam；Blank 声称 SGD 不行、全参不行，被 5 篇论文反驳。
3. **token 纠缠（Zur 2025）→ divergence tokens（Schrodi, ICLR 2026）→ 实体 token / 早期 FFN（Nief 2026）。**
   - 已知局限：token 局部解释与全局方向解释从未在同一组运行上对照。
4. **“必须同初始化”（Cloud）→ 输出头兼容（Brockers）/ 跨初始化可迁移（Tang, Pythia↔OLMo）/ Phantom Transfer 跨模型且扛住防御（NeurIPS 2026）/ LLS 跨架构（ICML 2026）。**
   - 改变的前提：数字通道和自然语言通道可能是两种不同的东西（Madl、Shah、Casademunt 都暗示过，但没人做受控检验）。

## 形态卡
- `query.py shapes`（subliminal / hidden signal / EM / data poisoning 切片，ICLR）：接收论文均分 6.12，其中 finding 线索 62%、method 38%；被拒论文中 method 占 64%、均分 4.44。
  - 读法：这个切片里，**发现 / 解释型更容易被收**，单纯提方法、提防御的被拒更多。
- **可行形态：**
  - A. 构念与测量：把“能传什么”变成可量化的容量或带宽；
  - B. 理论 + 受控实验：用一个机制统一几个互相矛盾的 regime；
  - C. 失败模式 + 修复：只有在 A/B 找到真实瓶颈后才考虑。
- **已接收的代表：**
  - Schrodi（ICLR 2026，机制定位 + 脆弱性，2 个模型 × 5 seeds）；
  - Blank（NeurIPS 2026，机制 + 预测性相关 ρ=0.75，3 seeds）；
  - Liu（NeurIPS 2026，机制 + 正则方法）；
  - Phantom Transfer（NeurIPS 2026，存在性证明 + 11 种防御）；
  - Askin（NeurIPS 2026，on-policy 蒸馏）；
  - Dang（NeurIPS 2026，agent）；
  - LLS（ICML 2026，理论驱动的数据选择）。
  - **证据规模普遍不大**：多为 1–3 个模型、≤5 seeds。
- **near-miss：** 主会议 OpenReview 读不到。workshop 层有 Kitkana（Sci4DL）、Subliminal Signals in Preference Labels（AIWILD）；Inoculation Prompting 主会只拿到 5.0 分。

## 立足点卡
- **可直接跑的基线：**
  - lmb-freiburg/divergence-tokens（MIT，ICLR 2026；6 个开源模型，7B LoRA 单卡可跑）；
  - MinhxLe/subliminal-learning（官方代码与数据，含 MNIST 辅助 logit 玩具）；
  - TruthfulAI-research/beyond_owls。
- **标准协议：**
  - 动物偏好：用一词回答类问题统计目标动物出现率；
  - misalignment：自由回答 + judge 打分；
  - 对照：未加特质的教师生成的数据；
  - 跨模型矩阵。
- **可复用资产：**
  - mechanism-population 线的 PolyPythia 多 seed 处理经验与审计记录（`workbench/mechanism-population-dynamics/suite-audits/`）；
  - lm-head 线关于 LoRA / 头部更新与 BF16 精度地板的工具。
- **比较优势：**
  - 独立单卡槽位多，能做大量带数据种子与训练种子的受控运行。Nief 报告数据种子主导方差，而多数论文只换训练种子。
  - 习惯逐条件扫描学习率并写噪声地板，这正是 Nief 与 Feng 之争的症结。

## 压力清单
| # | 压力 | 出处 | 可能形态 |
|---|---|---|---|
| P1 | **硬 token 通道到底能传什么：激活已有方向，还是传递新信息？** Beyond Owls 里新信息只经 logit 蒸馏传递；采样版的随机函数 R²=0，后门需要约 340 万条数据。Blank 发现可 steer 性预测迁移（ρ=0.75）。没有人给出过“容量 / 带宽”（每 token 能传多少比特任务信息）的测量。 | Beyond Owls §3–5；Blank；Hinton 2015 | A：容量曲线（植入 K 比特随机绑定 → 回收比特数 vs 数据量 × 通道 × 微调方式） |
| P2 | **LoRA / 全参、Adam / SGD、倒 U / 单调的矛盾，可能都来自学习率协议与数据量。** Nief（固定 lr）和 Feng（逐 rank 调 lr，多为 1 seed）结论相反；Blank 的 SGD lr 没有报告。 | Nief v2 comments；Feng；Blank App. N；Morgulis | B：在一个对齐的网格里找一个**训练前就能测的量**（例：特质方向上的累积更新信噪比）来同时预测所有 regime |
| P3 | **同初始化是否必要，取决于通道？** 数字数据跨模型≈0（Cloud、Beyond Owls），自然语言数据跨 10 个模型都迁移（Phantom、Casademunt），Pythia 跨 seed 可迁移（Tang）。 | Cloud Fig. 8；Phantom；Shah；Madl；Tang | A/B：通道 × 学生亲缘关系（同 checkpoint / 同架构不同 seed / 同家族不同大小 / 异家族）的受控矩阵 |
| P4 | **信号是 token 局部的，还是一个全局方向？** 两种解释都有阳性证据，但从未在同一组运行上同时检验。 | Schrodi；Nief；Blank；Hadley（prompt 教师没有向量签名） | B：同一组运行里做 divergence-token mask × 向量消融的 2×2 |
| P5 | **正则到底放大还是抑制迁移？** | Feng vs Yanagisawa / Liu | C：在 P2 的统一量下，两类正则应有可预测的方向 |
| P6 | **几乎所有阳性结果都依赖 Qwen2.5-7B-Instruct 与默认 system prompt**；仅 system prompt 就造成 2–5× 差异。 | Nief；Schrodi；Morgulis | 所有形态的卫生前提，不单独成文 |

**我的排序：**
- **P1 最值得住进去。**
  - 问题自然，外行一听就懂：“只看一串数字，能学到多少东西？”
  - 换更强的模型后问题仍然成立。
  - 两种结果都有信息量：硬 token 只能激活已有方向，或者存在可测的新信息带宽。
  - 能把 Hinton 的 dark knowledge 和 SL 放进同一条容量曲线。
- **P2 / P3** 是 P1 绕不开的 regime 变量，在驻留中顺带测量。
- **P4 / P5** 等有数据后再决定。

## 驻留计划（D1–D6，按顺序，不排日期）
1. **D1 强基线复现。** 用 divergence-tokens 代码在 Qwen2.5-7B 上复现 cat/owl 数字迁移：
   - 3 个数据种子 × 3 个训练种子；
   - 加未加特质的教师对照；
   - 记录 system prompt 敏感性；
   - 同时跑 MNIST 辅助 logit 玩具（CPU 即可），作为工具阳性对照。
2. **D2 资产。** 统一的“生成 → 过滤 → 训练（LoRA 或全参，逐条件扫 lr）→ 评测”管线；数据与模型 hash 入账。
3. **D3 痛点日志。** 记录复现偏差、prompt 敏感性、种子方差等真实出现的问题。
4. **D4 系统测量。**
   - 先测 regime 网格：LoRA rank、全参、Adam/SGD、lr、数据量；
   - 再做 P1 的第一个 pilot：教师植入 K 个随机“名字→属性”绑定，比较硬 token 与 logit 两种通道、全参与 LoRA，回收的比特数；
   - 阳性对照：直接 SFT；阴性对照：干净教师；
   - 同时测每个绑定的 steer 可达性。
5. **D5 定位表。** 至少覆盖 Blank、Beyond Owls、Feng、Nief、Tang、Schrodi、Liu、Phantom、Morgulis、Brockers。
6. **D6 形态卡 + 3–6 张 idea 卡。**

## 风险
| 风险 | 可能性 | 对策 |
|---|---|---|
| 强组先发表“容量 / 带宽”类结果 | 中高（10–11 月月产约 6 篇） | 先做最便宜的决定性 pilot；每次主旨变化都重扫近邻；定位上强调“测量构念 + 统一解释”，而不是“又一个特质” |
| 效应只在 Qwen 上成立，换模型就消失 | 中 | 从一开始就跑 2 个家族；如果确实只有 Qwen 有效，这本身就是 P6 的发现 |
| 结果落入“そうだよね”（硬 token 当然传不了新信息） | 中 | 用容量曲线给出量级和条件（数据量、通道、微调方式），而不是只给二元结论；在决策表里预先写好两种结果各自改变什么认识 |
| 研究对象半衰期短 | 中 | 问题落在蒸馏的信息论层面，不依赖某个具体模型的怪癖 |

## 决策（人签字）
- 选为主线 / 探索线 / 暂不选：**待用户决定。** 当前 ACTIVE 两个名额都已占用；如果要开线，需要先决定替换哪一条，或者以 PROPOSED 状态先做 D1 复现。
