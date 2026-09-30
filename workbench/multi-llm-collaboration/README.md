# Multi-LLM Collaboration — 训练出来的开源异构 LLM 团队

## 状态（中文进度页）

**PROPOSED（2026-09-30）— 待人确认后开始驻留。** 按 v3 容量规则，这是“1 主线 + 1 探索线”中的探索线（主线：`video-world-model-temporal-interfaces/`，CVPR 2027）。
territory 卡：[`../../search/our-taste/TERRITORY_SCAN_2026-09-30.md`](../../search/our-taste/TERRITORY_SCAN_2026-09-30.md) §2 ｜ 题材页与论文卡：[`../../library/themes/multi-agent-collaboration/`](../../library/themes/multi-agent-collaboration/README.md)

**一句话：** 多个开源 LLM（同族/异族、同尺寸/大+小）用 RL 协同训练成团队之后，学到的“协作”是什么、换伙伴/换规模/换任务时还在不在、在等算力下值不值得——在强开源训练框架上把团队跑出来、系统地测量，让论文从测量和痛点里长出来。

**为什么是这里（摘要）：** 对应组内偏好第一条（大+小 / 全小 / 非 API）；中等热度且在上升（ICLR 2025 → 2026 → ICML 2026 接收 3 → 7 → 14）；有单节点可跑的强开源基线（Dr. MAS @ NeurIPS 2026、CoMLRL、MARTI、AT-GRPO）；方法层（信用分配、稳定性）已拥挤，**“训练出的协作是什么、是否可靠、何时值得”**这一层相对空；可解释性（白盒分析）与游戏 NPC（Minecraft / Overcooked 类队友）作为理解轨道与环境自然接入。

**目标会议：** 主 ICML 2027（约 1 月下旬），备 ACL 2027（ARR 约 2 月）/ NeurIPS 2027（约 5 月）。

---

## 论文形态卡（初稿，D1–D6 交付时替换为证据版本）
- 一句话主旨：未定（由驻留测量决定；候选形态见 territory 卡 §2.7）
- 论文形态：A 失败模式+修复 / B 构念引入（ZSC、算力会计）+测量 / D 评测协议 —— 待定
- 3 个贡献：❌（驻留后填写）
- 4 条摘要主张：❌
- 5 张主图/表：❌（预期至少包括：算力匹配曲线、交叉配对矩阵、按角色的反事实贡献随训练变化）
- 基线：Dr. MAS / MAGRPO / AT-GRPO 训练的团队；同算力训练的单模型；未训练的提示式团队；更大的单模型；伙伴泛化的修复基线：SRPO（2602.21515，策略风险规避）、种群协同训练（SCOPE / FCP 式）
- 证据标准：≥2 个模型家族（Qwen、Llama）、≥2 个尺寸（1.5B–4B，7B 做关键对照）、≥3 个种子、≥2 类任务（数学/代码 + 搜索或合作游戏）、置信区间
- 定位表：最近邻为论文卡 F 节的 SRPO（2602.21515，P2 方法 + 理论 + 小规模 LLM 实验）、A7（TeamTR / SAT-AAMAS）、A8（SCOPE）、B1 后续（SAT-Stanford 2609.22682，文本层策略库）、C1（ZSC 谱系）；阶段三（D5）写完整版
- 风险：见 territory 卡 §2.8

---

## Idea 组合（`ideas/`；流程见 `../IDEA_EXPLORATION.md`）
| ID | 一句话 | 来源 | 研究动作 | 状态 | 证据等级 |
|---|---|---|---|---|---|
| [I01](ideas/I01-cross-play-matrix.md) | 训练出的团队换伙伴还能协作吗（交叉配对矩阵） | 近邻分歧：ZSC 谱系 vs 提示式 LLM 对陌生伙伴较稳；SRPO 初步实验 | 引入成熟构念 + 测量 | SEED（pilot 复用 E01 的两个种子，几乎免费） | — |
| [I02](ideas/I02-compute-matched-gain.md) | 等训练算力 + 等推理算力下团队还赢吗 | 近邻分歧：MARTI vs 2609.04217 / 2607.16133 | 强基线翻案 | SEED（更可能是主论文的必备对照） | — |
| [I03](ideas/I03-big-small-roles.md) | 大+小团队训练后谁在出力 | 近邻局限：Lazy Agents、Teams Hold Experts Back | 定位 + 干预 | SEED | — |
| [I04](ideas/I04-message-portability.md) | 训练出的消息新伙伴读得懂吗 | 近邻分歧：涌现语言 | 干预 / 反事实 | SEED（只需推理） | — |

账本：主张 [`CLAIMS.md`](CLAIMS.md)（空）· 痛点 [`PAIN_LOG.md`](PAIN_LOG.md)（空）· 实验卡 [`experiments/`](experiments/)（E01 Dr. MAS 数学复现、E02 CoMLRL 代码复现，均 PLANNED）。

---

## 驻留计划（D1–D6，见 `../README.md` §2）

### 阶段一 · D1/D2 强基线与资产
1. **环境**：在节点上建 `env.sh`（verl + sglang/vLLM；Dr. MAS 用 `requirements_sglang.txt`，flash-attn 2.7.4）；CoMLRL 单独环境（`pip install comlrl`）。
2. **复现 1（[E01](experiments/E01-drmas-math-repro.md)）**：Dr. MAS 数学（Solver + Verifier，2×Qwen2.5-1.5B 或 2×Qwen3-1.7B 起步），记录与官方趋势的差距、2 个以上种子的方差、梯度范数曲线（它的核心诊断）。两个种子的团队同时是 I01 的 pilot 材料。
3. **复现 2（[E02](experiments/E02-comlrl-code-repro.md)）**：CoMLRL MAGRPO 代码协作（HumanEval/MBPP/CoopHumanEval，Qwen2.5-0.5B→1.5B）。
4. **统一评测 harness**：vLLM 推理；**算力计量**（每题调用次数、生成 token、训练 GPU·时）作为一等公民写进每条结果。
5. 可选：Dr. MAS 搜索（3 智能体，需要本地检索服务，约 6GB 显存/卡）。

### 阶段二 · D3/D4 系统测量（测量，不是假设检验；阶段一跑通即开始）
| 测量 | 做法 | 对应压力 |
|---|---|---|
| 算力匹配曲线 | 训练后团队 vs 同训练算力的单模型 vs 更大单模型，按推理 token / 调用数对齐 | P1 |
| 交叉配对矩阵 | 不同种子 / 尺寸（1.5B↔3B↔7B）/ 家族（Qwen↔Llama）独立训练的团队互换成员，对比自配对；加入未训练团队作对照 | P2 |
| 按角色反事实贡献 | 替换/屏蔽某成员输出（换成未训练版本或空输出）看团队得分；沿训练 checkpoint 追踪 | P3 |
| 消息统计 | 长度、词汇漂移、新伙伴能否复述/使用该消息 | P5 |
| 白盒快照 | 训练前后各成员的激活差分（复用 model-diffing 工具链），与交叉配对结果对应 | P4 |

所有测量同时写进**痛点日志**（什么坏了、什么不稳定、什么意外地好）。

### 阶段三 · D5/D6 定位表与论文形态卡（与阶段二交错进行，交付即人审）
- 对最近 10 篇接收论文 + 最新 arXiv 写定位表（`python3 ../../tools/venue_corpus/query.py nearest "<当前主旨>"`）。
- 根据测量写论文形态卡；选 1–2 条压力进入 build + understand 两条轨道。

### 算力预算（单节点 4×80–96GB）
- 按优先级排算力，不排日程：E01 → I01 pilot（复用 E01）→ E02 → 其余测量。官方参考：Dr. MAS 数学 2×Qwen3-4B 在 4×H100 上约 38 小时，1.5B 预计明显更少，以实测 GPU·时为准。7B 只用于关键对照。

---

## 痛点日志
（驻留开始后按日期追加：现象 / 复现条件 / 量级 / 可能对应的压力）

## 决策记录
- 2026-09-30：territory 扫描推荐本方向为新探索线；待人确认。不预设结果；阶段二的测量无论哪个方向都有对应的论文形态（territory 卡 §2.7）。

## 资产位置
- 代码：`experiments/`（驻留开始后创建）
- 大文件（checkpoint、rollout）：节点本地，不进 git；在此记录路径
