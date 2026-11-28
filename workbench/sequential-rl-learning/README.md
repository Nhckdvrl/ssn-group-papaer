# sequential-rl-learning

## 状态（中文进度页）
**状态：** PROPOSED（与 `workbench/README.md` §9 一致；用户 2026-11-28 同意新开）
**territory 卡：** 无（由 `lm-head-post-training` 的 E11–E12 讨论与 11-28 调研转来）　**目标会议 / 截稿：** ICML / NeurIPS / ICLR，届次待定　**上次人审：** 2026-11-28
**一句话（当前版本，不是论文叙事）：** 一种能力的 RL 训练，会怎样改变模型之后通过 RL 学会另一种能力？先看现象是否存在、长什么样，不预设有害或有利，也不预设机制。

**运行中：** 无。E01 已写卡但**暂缓**（用户 11-28：先讨论问题层级——是否偏后训练工程、规模、KnK 与 agentic RL）。补充调研 `notes/scale_and_frontier_rl.md`。

## 为什么值得问（领域层面，不依赖本组已有实验）
- 现在的后训练是多阶段 RL（数学 → 代码 → agent）。前一段 RL 让后一段更难还是更容易学，决定阶段怎么排、要不要重置。
- 现有证据互不在同一设置：Tiwari 2605.12484 报告数学 RL 后学 HoVer-hard 40 步内掉到约 0%、连续训练中 CodeIO 几乎不起飞（无起点匹配、无同步数从头对照、格式与遗忘未分开）；Noukhovitch 2609.13443 图 10 报告换奖励后可恢复（无从头对照）。
- 相邻领域的理论对“从预训练模型出发的 RL”预测不一致：Ash & Adams（热启动：训练损失相近但泛化更差；第二阶段数据少时热启动有利、多时出现交叉）；Dohare 的可塑性损失依赖小随机初始化，Kleinman 的关键期要求早期特征能解释新任务，预训练权重都不满足；Lyle 证明范数/秩/死单元等统计量不是原因。
- 调研笔记（读全文，含读深度标注）在 `../lm-head-post-training/notes/`：`learnability_survey.md`、`history_effects_frameworks.md`、`public_rl_trajectories.md`、`path_dependence_prior.md`；用户的研究准则 `research_principles.md`。

## 论文形态卡
未定。第一步只画现象图（E01），不写叙事。已知的上限风险：只证明“RL 之后学得快/慢”是一篇复核文章；要到顶会，需要找到决定方向的规律（例如已学能力与目标能力的关系，或检查点上可测、能预测之后学习的量）。现在没有证据。

## Idea 组合
| ID | 一句话 | 来源 | 研究动作 | 状态 | 证据等级 |
|---|---|---|---|---|---|
| I01 | 先前的 RL 历史改变之后 RL 学新任务的过程（速度、上限、外推、保留），且与“现有能力是否改变”可以分离 | 11-28 讨论（GPT/Gemini/本会话）；Sheng 2611.33102 表 6：数学 RL 后 KnK 起点几乎不变（2.1% → 3.4%） | 用公开的“Base 起训 vs 数学 RL 后起训”配对画学习曲线（E01） | SEED | L0 |

## 主张摘要
无。

## 痛点摘要
无。

## 决策记录（日期 · 决定 · 依据 · 谁决定）
- 2026-11-28 · 新开本工作台，写第一张卡（E01，只推理） · E11–E12 后的方向讨论与调研：“RL vs 蒸馏终点比较”退出主线，转向 RL 历史与后续学习 · 用户
- 2026-11-28 · 原则上同意后续自训练，但需先把影响因素设计妥当、单独审 · 用户
- 2026-11-28 · E01 暂缓，先讨论问题层级 · 用户
- 2026-11-28 · 不预设机制拆分（权重 / 优化器 / 参考模型），等现象确认后再定 · 用户（“为什么还要锁定叙事”）

## 资产位置（大文件不进 git）
- 公开检查点（HF，未下载）：
  - Base 起训 KnK：`ftajwar/maxrl_dppo_qwen3_1p7B_base_knk_step_{100..1000}`、`ftajwar/grpo_dppo_qwen3_1p7B_base_knk_step_{100..1000}`（每 100 步）。
  - 数学 RL 1000 步后起训 KnK：`ftajwar/{maxrl,grpo}_dppo_qwen3_1p7B_maxrl_polaris1000_knk_step_{100..1000}`。两种算法都从 MaxRL-Polaris-1000 起训。
  - 起点：`Qwen/Qwen3-1.7B-Base`；`ftajwar/qwen3_1.7B_Base_MaxRL_Polaris_1000_steps`。
  - 4B 只有 100–400 步：`ftajwar/{maxrl,grpo}[_dppo]_qwen3_4B_{base,maxrl_polaris1000}_knk_step_*`。
  - 可严格续训的数学轨迹（每 50 步，含 AdamW / scheduler / RNG，另有全部 rollouts）：`max-rl/{grpo,maxrl,rloo}_qwen3_1p7B_base_polaris_checkpoints`。
- KnK 数据：`ftajwar/knights_and_knaves_fraction_reward`（train 20k，人数 2,3,4,5,7,8,9；test 1000 题人数 10；提示尾 “Let's think step by step and output the final answer within \boxed{}.”）；`max-rl/knk_n3_12`（eval 1000 题，人数 3–12 各 100；与上一份 train 逐字 statements 重叠 0，11-28 核对；提示尾为数学式指令）。
- 未核对：续训用的是哪份 KnK 训练集（推断为 fraction_reward：续训检查点 10-06 上传，n3_12 的生成种子是 20261007）；续训超参、是否加 KL、`dppo` 的含义；这组续训不在 MaxRL（2602.02710）或 Sheng（2611.33102）论文里，很可能是该组在做的研究。
