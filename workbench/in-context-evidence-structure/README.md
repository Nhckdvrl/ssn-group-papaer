
# In-Context Evidence Structure

## 状态（中文进度页）
**状态：** PROPOSED — 2026-10-05 人要求把 ICL 方向做到“可以正式注册 workbench”为止；本线已通过直接 ownership audit，允许 training-free baseline residency；不改变当前 ACTIVE-MAIN / ACTIVE-EXPLORE 分配。  
**territory 卡：** [T16](../../search/our-taste/TERRITORY_IN_CONTEXT_EVIDENCE_STRUCTURE_2026-10-05.md)  
**数据计划：** [DATA_PLAN.md](DATA_PLAN.md)  
**目标会议 / 截稿：** ICML / ICLR / NeurIPS / ACL；当前不提前锁论文形态。  
**上次人审：** 2026-10-05

## 当前进展（2026-10-05，agent 更新）
**一句话结论（2026-10-05 17:00 修订）：LLM 能察觉“要做什么”变了，察觉不到“哪个输入得到什么”变了。** 当 regime 是作用于所有输入的全局变换（标签流、大写↔反转、x+3↔x−3）时，模型按序列整合证据，能区分噪声与变化（方向与 exact Bayes oracle 一致）；当 regime 是按输入类别的分类映射（nonce 规则、SST 情感（nonce 或自然标签）、数字大小/奇偶）时，模型按类别/相似度检索 demo 并当作可交换集合汇总——不区分噪声与变化、不能被指令或可见 CoT 纠正、长上下文也分不出 A→B 与 B→A、对变化只做局部（相似 item）适应。

| 实验 | 结果（数字见实验卡） |
|---|---|
| D0 oracle | exact 层级 Bayes（规则 × 波动 λ × 噪声 ε），28 个单测通过；预测“前缀零散噪声令后缀反例更不可信”（方向相反检验） |
| E00 仪器 | Qwen3-8B T=16 准确率 ~0.85–0.9，换字典稳定、未饱和 |
| E02a 结构网格 | 6 个模型（Qwen3 1.7/8/8B-Base、Qwen2.5-7B、Mistral-7B、gemma-2-2b）：位置核平坦、成簇≈零散、前缀噪声使 P(B) **上升**（oracle 下降）、与 set oracle 相关 0.88–0.99；影响由输入相似度决定 |
| E03 指令 | “规则可能改变”/“少数标签是错的”指令完全不改变签名 |
| E04 局部更新 | 末尾 8 条反转后，只有与反转 demo 相似的 query 翻转（+0.55），其余仍按旧规则（−0.96）；oracle 两者相同 |
| E05 输入维度 | d=0（纯标签流）强时间敏感：suffix4−disp4 +10.7、前缀噪声 −4.75（oracle 同向）；d≥1 立即变为集合式 |
| E06 开关 | 标签流不变、只加无关输入或独特 id：时间敏感**保留**；只有标签依赖输入（规则任务）时消失 → 开关是“表层 vs 潜在”，不是“可区分 item” |
| E07 自然语言 | SST-5 两极句子：suffix4−disp4 +0.21（oracle +4.02），前缀噪声 +2.1/+4.3（oracle −1.7/−1.9），与 set 相关 0.99 |
| E08 长上下文/对齐 | T=64：“32 旧→32 新” vs 反序 LM 差 0.05（oracle 6.89）；末尾表层游程为新规则 B 词时 suffix−disp +0.65，为旧规则 A 词时 −0.92（方向反） |
| 注意力探针 | 标签流中注意力集中于末尾 B 游程（76% vs 均匀 25%）、不按无关输入相似度；规则任务中按相似度、对 B 游程不敏感 |
| 扫描 | 13 个模型（Qwen3 0.6/1.7/4/8/14/32B、Qwen3-8B-Base、Qwen2.5-7B/32B、Mistral-7B、Llama-2-7B、gemma-2-2b、Qwen3.5-9B 门控线性注意力混合）潜在层签名全部一致：成簇≈零散、前缀噪声方向错误；Base 与 post-trained 的表层/潜在解离相同 |
| 隐式先验 | 表层（const）最佳拟合 λ≈0.02–0.05、ε≈0.05–0.1（条件均值 R² 0.38 vs 可交换 0.19） |
| E09 可见 CoT | 非 thinking 模式“想一想”：suffix_4 0.41 ≈ disp_4 0.42，前缀噪声使 P(B) 升至 0.46（方向错），且基础规则学习变差（allA 准确率 0.63）；thinking 模式运行中 |
| E10 消融 | 16 个晚层“游程头”消融使标签流噪声方向效应 −73%（对照头无效）；分类任务不受影响 |
| E11/E11b/E13/E15 边界 | 全局变换时间敏感：大写↔反转 suffix−disp +17.2、±3 +5.9（噪声方向均正确）；分类映射时间盲：SST 自然标签 +0.35（噪声方向错）、数字大小 −0.24、奇偶(自然词) +0.51 |
| E16 确认（无 nonce） | 4 模型 × 6 格式（全新种子）：分类（奇偶/大小/SST）全部时间盲、噪声方向反；大写↔反转/标签流全部时间敏感；±3 因模型而异 |
| E17 任务向量 | ±3 的任务向量（L22 单个残差）可迁移且自带时间结构（成簇 +0.62、噪声 −0.30、过时折扣 +0.58，CI 均不含 0）；大小分类没有可迁移向量 |
| condarith | 类别条件变换（答案不可复制）仍时间盲 → 原则是“按输入路由”，不是“可复制” |
| 进行中 | thinking 模式；关系性全局变换（字母±1、数字±1/±10）；LoRA 易变分类 vs 稳定分类（E18）；toy v2；晚间跨模型扫描 |

**阻塞：** StepFun step-5 配额已用尽（quota_exceeded），nonce 词库审计停在 25 个已接受属性名；确认版实验需要审计词库。

## 一句话（当前版本）
> **冻结 LLM 能不能判断 demonstrations 的顺序究竟是 nuisance 还是 signal，并依据上下文的统计结构，自适应地从 set-like 聚合切换到 sequence-like evidence weighting？**

更宽的 territory 对象：LLM 如何在 context 内识别 exchangeable / correlated / evolving evidence，并相应决定每条 demonstration 应该算多少、旧证据是否仍有效。

## 为什么现在可以正式驻留

强近邻形成清楚的文献张力：
- ICML 2024 / ICLR 2025：i.i.d./独立 demos 的正确对称性接近 exchangeability；order sensitivity 是问题；
- ICLR 2026 / regime-change / sequential-correlation work：非平稳或相关 context 中，order/recency 又是真信息；
- 现有工作主要分别研究某一种已知数据结构。

本 workbench 的第一科学对象不是“order matters”，而是：
> **同一个 pretrained frozen LM 是否会从 demonstrations 本身推断当前应采用哪一种 evidence structure。**

直接检索截至 2026-10-05 未找到以该 adaptive structure inference 为主对象的工作；新近邻出现时必须重新定位。

## Ownership fence

不能注册为我们的主张：
- ICL order sensitivity；
- iid exchangeability/martingale violation；
- invariant ICL method；
- nonstationary recency advantage；
- in-context changepoint detection；
- sequential correlation / effective context length；
- single corrupted-demo conflict；
- in-context continual-learning forgetting；
- temporary task vectors/representations。

最危险的 reviewer compression：
> “InvICL + nonstationary ICL 放进同一张表。”

未来 lead 必须给出新的 **structure-selective measurement / predictive account / consequence**，而非覆盖更多 regime。

## 第一驻留块

1. **D0**：实现 exact-gold nonce attribute-rule generator + exact set/sequence/meta oracle；固定 pilot/confirm seeds。
2. **E00**：单模型 clean STABLE 条件验证真正 demonstration-dependent task learning，有足够 headroom，排除 label semantics / copy。
3. **E01**：两个极端校准——clean exchangeable vs obvious single-change；验证 M1/M2/M3 能区分 set-like 与 sequence-like 行为。
4. **E02**：核心决定性 pilot——matched NOISE-vs-CHANGE。控制 contradiction count、token budget、input/label marginal，观察模型是否依据矛盾的时间组织改变 evidence weighting。
5. E02 前禁止 probe/SAE/task-vector fishing；E02 后也只有在 competing accounts 需要时才做白盒。

## 核心 competing accounts

1. **Fixed positional prior**：无论统计结构如何，基本使用同一套 recency/primacy 权重。
2. **Set learner**：近似 exchangeable；stationary 做得好，但真实 change 后更新慢。
3. **Sequence heuristic**：普遍迷信最近样本；change 做得好，但把孤立 noise 当成 regime shift。
4. **Adaptive structure learner**：随着 context 对 stable/change 的证据改变，证据权重向相应 oracle 移动。

E02 的设计必须让这四种解释产生不同预测。

## 标准 measurement

- M1 stationary permutation dispersion；
- M2 per-position counterfactual demo influence kernel；
- M3 set-oracle / sequence-oracle / meta-oracle fit；
- M4 structure selectivity：模型 evidence weighting 是否随 evidence structure 发生规范方向的改变。

不把 overall accuracy 当唯一结论。

## Idea 组合
目前不预注册 paper idea。首批 pressure families：
- symmetry / exchangeability；
- dependence / redundancy；
- nonstationarity；
- structure inference；
- conflict attribution（noise vs new regime）；
- cross-task transfer；
- mechanism（条件分支）。

## 主张摘要
见 [CLAIMS.md](CLAIMS.md)。当前只有 instrument/measurement 主张，没有论文 finding。

## 痛点摘要
见 [PAIN_LOG.md](PAIN_LOG.md)。

## 决策记录
- **2026-10-05：REGISTERED / PROPOSED。** 人要求继续 ownership audit 直到找到彻底可以注册的 ICL workbench。generic forgetting、latent retention、change-point、conflict、temporary task-state 等入口因直接近邻降级；最终选择 evidence-structure inference 作为 territory。
- 不自行抢占现有 ACTIVE 槽位；baseline residency 可执行。

## 资产位置
- procedural generator / exact oracle：scripts/
- experiment cards：experiments/
- small generated manifests / summaries：results/
- 大 raw/model cache 不进 git。注意力探针原始数组：`results/*/attn_*.npz`（NFS 本地，不进 git；可用 `scripts/attn_probe.py` 重建）。
- nonce prompt 行（`data/*/rows.jsonl`）由 `scripts/build_*.py` 以固定种子重建；LM 打分 `results/*/*.s*.jsonl` 进 git。
