# 多智能体与大小模型协作（Multi-LLM collaboration）

**范围：** 多个 LLM（同族/异族、同尺寸/大+小）之间的协作：提示式团队、RL 协同训练、大小模型接力/级联、隐空间通信、团队的失败模式与评测。组内偏好第一条（智能体协作：大的和小的 / 全小的 / 非 API）对应的题材。
**更新：** 2026-09-30（新建题材页）。当前 territory 判断见 [`../../../search/our-taste/TERRITORY_SCAN_2026-09-30.md`](../../../search/our-taste/TERRITORY_SCAN_2026-09-30.md)。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

| 切片 | NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 多智能体 LLM（整体） | 25 | 33（29% / 基准 32%） | 25 | 57 | 82（22% / 基准 27%） | 114 | 34 | 48 | 102 |
| RL 协同训练的 LLM 团队 | 4 | 3（27% / 基准 32%） | 4 | 6 | 7（20% / 基准 27%） | 14 | 4 | 3 | 5 |
| 大小模型协作 | 6 | 2（18% / 基准 32%） | 5 | 7 | 5（33% / 基准 27%） | 5 | 4 | 7 | 4 |
| 隐空间 / KV 通信 | 0 | 0 | 0 | 4 | 3（27% / 基准 27%） | 3 | 0 | 0 | 1 |
| 零样本协调 / ad-hoc teamwork（经典 MARL） | 4 | 2（40% / 基准 32%） | 2 | 0 | 0 | 2 | 0 | 0 | 0 |

读法：多智能体整体很拥挤且接收率低于基准（审稿人挑剔）；**RL 协同训练的团队**在上升（3 → 7 → 14）；隐空间通信在顶会还少，但 arXiv 2026 年已有约 36 篇；ZSC 是 MARL 的成熟构念，接到 LLM 团队训练上的工作刚刚开始（SRPO 2602.21515 的小规模 LLM 实验、SCOPE 的人–AI 模拟器坍缩），主流框架上还没有系统测量。NeurIPS 2026 已知接收：Dr. MAS。

## 2. 谱系（详见 territory 扫描 §2.2 与 [`PAPER_CARDS.md`](PAPER_CARDS.md)）
1. 提示式协作 → 等算力怀疑（辩论、MoA → *Teams Hold Experts Back* → 等算力/信息瓶颈分析）→ 文本层修复（同一作者的 *Self-Organizing Agent Teams*，2609.22682）。
2. 训练协作：MALT、Multiagent Finetuning → MAPoRL → MAGRPO/CoMLRL → AT-GRPO、MARTI、Dr. MAMR → Dr. MAS、MAAC、TeamTR、SAT；信用分配支线（MAPPA、CCPO、SHARP、COSAC）已拥挤。
3. 零样本协调（Other-Play → FCP → ZSC-Eval → CEC → UPD）→ LLM 场景的最初几步：SRPO（Caltech，策略风险规避，小规模 LLM 协作实验）、SCOPE（模拟器坍缩）；对照事实：提示式 LLM 对陌生伙伴较稳（ALEM 2606.08340）。
4. 大+小：推测式思考 / SpecReason → RelayLLM、ConfSpec → 级联与路由理论；小代理团队 vs 单个大模型（编排者容量决定上限）。
5. 通信媒介：文本 → 嵌入/激活 → KV/隐状态（C2C、KVComm、LatentMAS）→ 因果审计；训练中涌现的约定/私有语言（GlossoGen 等）。

## 3. 本目录文件
- [`PAPER_CARDS.md`](PAPER_CARDS.md) — 15 篇（组）关键论文的精读卡：背景、压力、改变的前提、与近邻的距离、证据、可迁移动作、对我们。

## 4. 深读材料：`library/deep/` 中的相关章节
- [`deep/industry/FRONTIER_DEEP_DIVE.md`](../../deep/industry/FRONTIER_DEEP_DIVE.md) › 11. NVIDIA — “one frontier model for every call” is no longer the agent architecture（异构模型分工进入工业架构）
- [`deep/open-artifacts/GENEALOGIES_03.md`](../../deep/open-artifacts/GENEALOGIES_03.md) › S25 — Model selection → learned cognition allocation；S30 — Orchestrator model vs self-modifying harness
- [`deep/open-artifacts/GENEALOGIES_09_HARNESS_MATURITY_AUTORESEARCH_PROXY.md`](../../deep/open-artifacts/GENEALOGIES_09_HARNESS_MATURITY_AUTORESEARCH_PROXY.md) › S95 — Atria Dawn: “AI scientist” becomes a division-of-labor problem
- [`deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md`](../../deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md) › S122 — Composition can be scientific when interactions are the hypothesis
- [`deep/open-artifacts/FRONTIER_DEEP_DIVE.md`](../../deep/open-artifacts/FRONTIER_DEEP_DIVE.md) › 8. OpenBMB MiniCPM5-2B；14. Cohere Labs — small specialist models as first-class releases
- [`deep/academic/GENEALOGIES_02.md`](../../deep/academic/GENEALOGIES_02.md) › LINEAGE 8 — Distillation（teacher signal 必须对 student 可学习；大→小的另一种协作）

## 5. 开源资产（单节点可跑）
| 资产 | 内容 | 备注 |
|---|---|---|
| [langfengQ/DrMAS](https://github.com/langfengQ/DrMAS) | NeurIPS 2026；数学、搜索；异构协同训练 | 搜索 3×Qwen2.5-3B 4×H100 约 13h；数学 2×Qwen3-4B 约 38h |
| [OpenMLRL/CoMLRL](https://github.com/OpenMLRL/CoMLRL) | MAGRPO / MAREINFORCE / MAAC；写作、代码、Minecraft | pip 可装，可从 0.5B 起步 |
| [TsinghuaC3I/MARTI](https://github.com/TsinghuaC3I/MARTI) | ICLR 2026 框架；异构多模型训练 | |
| [pettingllms-ai/PettingLLMs](https://github.com/pettingllms-ai/PettingLLMs) | AT-GRPO（ICLR 2026） | 游戏/规划/代码/数学 |
| [Yydc/TeamTR](https://github.com/Yydc/TeamTR)、[Yydc/SAT-AAMAS](https://github.com/Yydc/SAT-AAMAS) | 信赖域 / 顺序智能体调优；即插即用 | P2 近邻 |
| [CHATS-lab/scope_usim](https://github.com/CHATS-lab/scope_usim) | SCOPE 种群协同训练 | 模拟器坍缩 |
| [apappu97/multi-agent-teams-hold-experts-back](https://github.com/apappu97/multi-agent-teams-hold-experts-back) | 团队 synergy 实验工具 | 行为基线 |
| [sjtu-marl/ZSC-Eval](https://github.com/sjtu-marl/ZSC-Eval) | ZSC 评测协议（Overcooked 等） | 交叉配对方法论 |
| [alem-world/alem-env](https://github.com/alem-world/alem-env) | ALEM（2606.08340）：JAX 开放式协作世界 | P8 候选环境；有 MARL 参照 |
| [DrStranded/Co-RL](https://github.com/DrStranded/Co-RL) | Co-RL（2608.17253）：异构群体、同伴奖励 RL | 异构团队训练的另一个基底 |

## 6. 最新 arXiv 入口
- [xxzcc/awesome-llm-mas-rl](https://github.com/xxzcc/awesome-llm-mas-rl)（LLM 多智能体 RL，84 条，含 benchmark gap 表）
- [edzq/LatentAgentComm](https://github.com/edzq/LatentAgentComm)（隐空间通信，42 条，含开放问题）
- [junchenzhi/Awesome-LLM-Ensemble](https://github.com/junchenzhi/Awesome-LLM-Ensemble)、[MilkThink-Lab/Awesome-Routing-LLMs](https://github.com/MilkThink-Lab/Awesome-Routing-LLMs)、[dstripelis/Awesome-LLM-Routing](https://github.com/dstripelis/Awesome-LLM-Routing)（集成与路由）
- [tigerchen52/awesome_role_of_small_models](https://github.com/tigerchen52/awesome_role_of_small_models)、[FairyFali/SLMs-Survey](https://github.com/FairyFali/SLMs-Survey)（小模型的角色）
- [taichengguo/LLM_MultiAgents_Survey_Papers](https://github.com/taichengguo/LLM_MultiAgents_Survey_Papers)、[kyegomez/awesome-multi-agent-papers](https://github.com/kyegomez/awesome-multi-agent-papers)
- [jiaxianyan/icml-2026-agent-papers](https://github.com/jiaxianyan/icml-2026-agent-papers)（ICML 2026 632 篇 + ICLR 2026 457 篇智能体论文按主题分类）
- 通用入口：`../../sources/AWESOME_LISTS.md`

## 7. 本仓库相关
- 建议的新探索线：`workbench/multi-llm-collaboration/`（见 `workbench/README.md` §9）
- 历史：`archive/candidates/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING/`（路由 = 模型分工的一种；教训：好的诊断信号 ≠ 可部署的动作）
