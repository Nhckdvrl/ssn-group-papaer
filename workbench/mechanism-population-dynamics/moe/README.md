# 主题 3：导师提的方向——MoE 专家分工是否跨训练一致（E120–E143）

**状态（2026-10-26）：** 人暂停实验，下一步待人决定。E120–E142 已完成；E143 已写卡、未运行。

## 1. 导师的原问题（10-16、10-22 两次面谈）
- 分别训练的模型里，专家编号不同，但会不会形成**同样的角色分工**？“本来不一定一致的东西却强烈一致”，比单词知识一致更有意义。
- 难点是基线：一致到什么程度才有意义。
- 约束：评估留在语言任务上；先专家，再头。
- 原话记录与调研：[notes/ADVISOR_2026-10-23.md](notes/ADVISOR_2026-10-23.md)。

## 2. 这个问题现在被回答了多少（10-26 审视）
| 子问题 | 现状 |
|---|---|
| 专家会不会自发分工 | 已回答：会，主要按词、句法和细粒度操作分，按领域分很弱，还有跨领域的通用专家（OpenMoE、Illusion of Specialization、Expert Strikes Back、我们的 E121） |
| 编号是否对应 | 不用回答：专家可任意置换，编号本来就不可能对应 |
| 同配置不同种子，划分是否对应 | 语言 MoE 未干净回答（Equifinality 只有 2 个种子且基线有误；我们的 E130 平台见下）；视觉 MoE 已有 10 种子结果：组织重现、专家身份不重现 |
| 一致到什么程度才有意义 | 没人解决 |
| 头 | 基本已回答（主题 1、2 + Bali 2026、Tigges 2024） |

- **价值判断：** 按原样做，结果大体可预测。路由是隐状态的线性读出，又很大程度由词决定；同配置的种子表示几乎一样，划分大部分自然会一致，属于导师自己说的“也是”。有意义的只剩扣掉词身份和表示几何之后的部分，测它需要自己训练多个种子，成本高、离真实模型远。
- **内核：** 不由目标强制的组织方式（分工）在独立训练间是否收敛，并且要和本来就会收敛的知识、表示分开。

## 3. 做过的实验，按价值分四段
**(a) 测量工具与原生 OLMoE（E120–E122）——有价值，保留。**
- E120：合成已知答案验证了 N1 零假设，查出 N2 和均值钳制的假阳性。
- E121：OLMoE 里同一个词在不同词性下的路由差异，扣除零假设后 16 层全为正（L9 δ = 0.206）。
- E122：路由相似不能代替功能相似（路由距离与替换后损失的偏相关仅 0.027）。

**(b) 受控插层平台（E123–E134）——核心结论被自身检查推翻。**
- 平台：冻结 OLMo-1B，把第 9 层 FFN 换成随机初始化的 MoE 来训练。
- E130：5 个初始化之间专家功能指纹对应只有 0.016–0.047（自身末期 0.999），记为 C07。
- 但 E134 把每个专家换成 64 个专家的平均，损失只升 0.0025–0.003（原生 OLMoE 是 0.064）；E132 随机移植另一个种子的整套专家只升约 0.012（整层置零 0.117）。**这个平台里专家几乎可以互换，没有可比的分工**，E130 / E131 回答不了导师的问题（[PAIN_LOG P30](../PAIN_LOG.md)）。
- 留下的教训：冻结骨干、只插一层 MoE 不会长出分工；任何跨训练比较都要先过“分工存在”检查（E134 的做法）。

**(c) 蒸馏原生层（E135–E142）——偏离原问题。**
- 把 OLMoE 第 9 层的函数蒸馏给随机学生，比较不同路由起点下 3 个学生的拆分方差。
- 这里没有独立训练的语言模型，问的是“拟合同一个函数，拆分方式唯不唯一”，不是自发分工；每步都在修补上一步的混杂（P23–P29）。结论（初始路由条件影响拆分方差，C09）很局部。

**(d) 候选新方向（E143，已写卡、未运行）。**
- 比较不同团队独立训练的公开 MoE（OLMoE、Qwen、DeepSeek、Granite 等）是否用同一种方式分工：扣掉词身份后，同一个词在不同上下文里的路由区分是否跨模型一致，并与表示相似度、几何零假设比较。只需推理。
- 回答的是“有没有普遍的分工”，不回答“同配方重跑会怎样”。人 10-26 叫停，担心跑不出有用的结果，未执行。

## 4. 实验卡
| 段 | 卡 |
|---|---|
| (a) 测量与原生 OLMoE | [E120](experiments/E120-moe-measurement-synthetic.md) · [E121](experiments/E121-olmoe-routing-organization.md) · [E122](experiments/E122-moe-routing-function-bridge.md) |
| (b) 受控插层平台 | [E123](experiments/E123-frozen-moe-feasibility.md) · [E124](experiments/E124-frozen-moe-functional-reproducibility.md) · [E125](experiments/E125-frozen-moe-data-coverage-control.md) · [E126](experiments/E126-equal-capacity-moe-granularity-control.md) · [E127](experiments/E127-fixed-endpoint-predictive-fidelity.md) · [E128](experiments/E128-adequate-ce-epoch-recovery.md) · [E129](experiments/E129-teacher-distribution-feasibility.md) · [E130](experiments/E130-fixed-budget-expert-reproducibility.md) · [E131](experiments/E131-transient-order-history.md) · [E132](experiments/E132-function-guided-bank-grafting.md) · [E133](experiments/E133-support-weighted-output-alignment.md) · [E134](experiments/E134-expert-uniform-component-necessity.md) |
| (c) 蒸馏原生层 | [E135](experiments/E135-native-moe-function-constraint.md) · [E136](experiments/E136-native-router-assignment-oracle.md) · [E137](experiments/E137-native-component-support-reconstruction.md) · [E138](experiments/E138-fixed-assignment-student-reproducibility.md) · [E139](experiments/E139-matched-free-routing-cohort.md) · [E140](experiments/E140-native-router-warmstart-cohort.md) · [E141](experiments/E141-support-discordance-content-decomposition.md) · [E142](experiments/E142-shared-random-router-cohort.md) |
| (d) 候选新方向 | [E143](experiments/E143-cross-model-routing-division.md)（PLANNED） |

逐卡的一行结果见 [experiments/INDEX.md](experiments/INDEX.md)。

## 5. 主张（详见 [../CLAIMS.md](../CLAIMS.md)）
- C06（L1）：原生 OLMoE 的路由相似不能代替功能相似。
- C07（L2，限定设置）：受控平台 5 个初始化的专家指纹不对应。**须与 P30 一起读：该平台专家几乎可互换，不构成分工跨训练证据。**
- C08（L1）：同一父状态短暂换数据顺序，终点指纹不同（同样受 P30 限制）。
- C09（L1）：蒸馏 cohort 中路由起点影响拆分方差。

## 6. 笔记（[notes/](notes/)）
| 文件 | 内容 |
|---|---|
| [ADVISOR_2026-10-23.md](notes/ADVISOR_2026-10-23.md) | 导师两次面谈原话、文献地图、最初的研究空间 |
| [DISCUSSION_2026-10-23.md](notes/DISCUSSION_2026-10-23.md) | 10-23 几轮外部反馈（GPT / Gemini）的讨论记录 |
| [HANDOFF_2026-10-25.md](notes/HANDOFF_2026-10-25.md) | 10-25 写给接手 AI 的交接文档（历史） |
| [GPT_PHASE_SUMMARY_E120-E142.md](notes/GPT_PHASE_SUMMARY_E120-E142.md) | GPT 阶段的整理快照与 E138–E142 详细数字 |
| [POSITIONING_2026-10-26.md](notes/POSITIONING_2026-10-26.md) | 近邻定位表 |
| [IDENTIFIABILITY_SCOPE_2026-10-26.md](notes/IDENTIFIABILITY_SCOPE_2026-10-26.md) | 蒸馏线的可识别性范围说明 |
| [audits/](notes/audits/) | E121–E130 的独立审计与复算记录 |

论文精读卡在 [../knowledge/papers/](../knowledge/papers/)（`MOE_DIVISION_OF_LABOR_2026-10-23.md`、`MOE_SPECIALIZATION_SEEDS_2026.md`），以及仓库级 `library/themes/moe-routing/`。

## 7. 代码与资产
- [scripts/](scripts/) 以 `moe/` 为根，结果写入 [results/](results/)。测量库 `moe_measure.py`；E121 采集 `e121_olmoe.py`；E143 的 `e143_data.py` 已运行过，`e143_capture.py` **未测试**。
- 检查点、原始数组在 `~/mechpop_cache/`，清单见 [ASSETS.md](ASSETS.md)。
