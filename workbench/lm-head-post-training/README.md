# Understanding the LM Head in LLM Post-Training

## 状态（中文进度页）

**状态：** PROPOSED（已由用户要求注册；不擅自占用 ACTIVE 槽位）
**territory 卡：** [研究思想与讨论沿革](logs/2026-11-26.md)　**目标会议 / 截稿：** 待定（ACL / ICML / ICLR / NeurIPS；不投 Findings） / —　**上次人审：** 2026-11-26（用户确认从纸面讨论转向实验探索，具体论文主旨未定）
**一句话（当前版本）：** 研究现代语言模型输出头在后训练中的功能变化及学习信号传递，通过真实模型测量和最小干预，寻找可解释、可复现、值得进一步研究的现象。

**当前决定：** E0、E1 已获探索设计共识，按 E01、E02 实验卡实现，先通过小规模工具校验再扩到首批样本；E2/E03 暂缓，等 E01/E02 结果后由人决定。登记不等于运行，当前没有实测结果，也没有确认任何新发现。

## 给本地实验执行者的必读顺序

1. 仓库根 AGENTS.md、RESOURCES.md、workbench/README.md、EXECUTION.md。
2. [讨论沿革与研究思想](logs/2026-11-26.md)：为什么选这片研究空间、哪些旧路不再走、我们究竟希望学到什么。
3. [导师研究标准与本项目执行要求](MENTOR_REQUIREMENTS.md)：具体 12 项标准、Discovery/Problem-first、晋级与首轮探索的区别。
4. [关联工作与文献地图](RELATED_WORK.md)：先读 P0 两篇，其他按结果查阅；不要阻塞首轮实验。
5. [技术口径与实现指南](RESEARCH_PLAN.md)：数学、内存、指标、对照、结果解读和交付要求。
6. [E01 权重解剖](experiments/E01-checkpoint-anatomy.md)、[E02 梯度几何](experiments/E02-gradient-geometry.md)。不要先跑 E03。
7. 读两篇核心原文的方法与实验，记录原文定位和实际复现配置，不重新开启无限查重。

## 论文形态卡（探索初稿）

- 主旨：尚未确定；不能写成“LM Head 已被证明存在有害梯度瓶颈”。
- 可能形态：理论与实证 / 失败模式与最小修复 / 学习机制分析，取决于测量。
- 核心贡献：❌ 待真实证据；当前没有 manuscript-critical claim。
- 主图：先产出阶段权重变化、功能扰动、投影保留/增益、组级聚合与梯度方向；不是预定论文图。
- 强基线：原生 checkpoint、标准 CE、同轨迹奖励加权、标准 GRPO；两篇核心文献的关键工具对照。
- 证据标准：pilot 先校验工具和噪声地板；正式主张按 EXECUTION.md 升级、重复、跨模型及独立复算。
- 定位：核心两篇有明确竞争解释；PEFT/head tuning、softmax bottleneck、RL 稀疏更新为相邻边界，见 RESEARCH_PLAN。未宣称原创性。
- 决策：先建设及测量；人审后决定继续、转向同一空间或暂停。暂不启动第二空间（真实稀疏自由度与 BF16 精度）。

## Idea 组合

| ID | 一句话 | 来源 | 研究动作 | 状态 | 证据等级 |
|---|---|---|---|---|---|
| I01 | 后训练不同阶段的输出头功能变化是否值得单独研究 | 核心争议及公开谱系 | 定位、干预 | PILOT | 未测 |
| I02 | 奖励加权与轨迹分布怎样改变输出头处的学习信号 | 核心争议 | 重新归因、测量 | PILOT | 未测 |
| I03 | 冻结输出头会否对不同后训练范式造成不同影响 | 两篇论文的解释分歧 | 干预 | PARKED（等 E01/E02） | 未测 |

## 主张与痛点

[CLAIMS.md](CLAIMS.md) 尚无实证主张；[PAIN_LOG.md](PAIN_LOG.md) 尚无本项目真实痛点。不要把理论预测或下载问题伪装为科学发现。

## 决策记录

- 2026-11-26 · 用户明确要求不再进行无限纸面辩论，从有价值空间出发，以真实数据驱动问题发现；GPT/Gemini 多轮审查收敛到 LM Head，授权登记，E0/E1 优先，E2 等结果。
- 2026-11-26 · 本次注册采用仓库规范编号 E01/E02/E03，对应对话 E0/E1/E2；保留现有 ACTIVE-MAIN/ACTIVE-EXPLORE 状态，不代替用户改线。
- 2026-11-26 · 最后一轮工程建议已纳入，同时修正“零坐标失配风险”、大 SVD 无成本、聚合 logit 梯度等同参数梯度等说法。详见技术指南。

## 资产位置

脚本、环境与结果尚未创建/实跑。执行者先查节点本地缓存与磁盘；模型候选为 Qwen3-8B-Base / Qwen3-8B 后训练版及 OLMo-3-7B 同一真实训练谱系。记录精确 HF revision、父 checkpoint、tokenizer hash、数据 revision、命令、种子、运行节点与 GPU·时。大权重和 rollout 原文存授权本地路径，Git 只保存可复现说明、代码和小型汇总。不得跨节点同步大模型或写入内部凭证。

## 入口

- [RESEARCH_PLAN.md](RESEARCH_PLAN.md)
- [RELATED_WORK.md](RELATED_WORK.md) · [MENTOR_REQUIREMENTS.md](MENTOR_REQUIREMENTS.md)
- [讨论与人审记录](logs/2026-11-26.md)
- [E01](experiments/E01-checkpoint-anatomy.md) · [E02](experiments/E02-gradient-geometry.md) · [E03（暂缓）](experiments/E03-head-freeze.md)
