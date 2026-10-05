
# In-Context Evidence Structure

## 状态（中文进度页）
**状态：** PROPOSED — 2026-10-05 人要求把 ICL 方向做到“可以正式注册 workbench”为止；本线已通过直接 ownership audit，允许 training-free baseline residency；不改变当前 ACTIVE-MAIN / ACTIVE-EXPLORE 分配。  
**territory 卡：** [T16](../../search/our-taste/TERRITORY_IN_CONTEXT_EVIDENCE_STRUCTURE_2026-10-05.md)  
**数据计划：** [DATA_PLAN.md](DATA_PLAN.md)  
**目标会议 / 截稿：** ICML / ICLR / NeurIPS / ACL；当前不提前锁论文形态。  
**上次人审：** 2026-10-05

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
- 大 raw/model cache 不进 git。
