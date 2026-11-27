# Subliminal Knowledge Transfer · 经由无关数据，学生从教师那里到底学到了什么

## 状态（中文进度页）
**状态：** PROPOSED（用户 2026-11-27 要求注册并准备开做；ACTIVE 名额由人决定，当前 ACTIVE-MAIN 与 ACTIVE-EXPLORE 均已占用）
**territory 卡：** [`search/our-taste/TERRITORY_SUBLIMINAL_LEARNING_2026-11-26.md`](../../search/our-taste/TERRITORY_SUBLIMINAL_LEARNING_2026-11-26.md)
**目标会议 / 截稿：** ICML 2027（摘要 2027-01-14 / 全文 2027-01-22，AoE；来源 icml.cc 2027 Reciprocal Reviewing 页，正式 CfP 未发布）。截稿时主张不够就转投 NeurIPS 2027，不关线（`EXECUTION.md` §7）。
**上次人审：** 2026-11-27（五轮方向讨论结束；用户同意分阶段方案并要求注册 workbench）
**一句话（当前版本）：** 在受控的反事实教师设计下，测量学生经由语义无关数据，从教师那里得到的是**教师身份指纹**、**教师特有的知识成分**，还是**可用的功能与结构**，以及这些取决于什么。

**当前进展：** 只有文献整理与实验设计，**无实测、无代码、无主张**（全部 L0）。脚本由服务器端 agent 编写并测试（云端会话没有 GPU 与依赖环境）。下一步：服务器 agent 读完 HANDOFF 与 6 篇原文 → 编写脚本并冒烟 → Stage 0 锚点复现（E01、E02）。

## 本地执行者必读顺序
0. **[交接文档 HANDOFF.md](HANDOFF.md)：先读这一份。**它建立对整个领域的认知（现象、发展史、争议与混杂、理论视角、我们的框架、陷阱清单、何时停下来叫人、动手前必须精读的 6 篇论文）。
1. 仓库根 `AGENTS.md`、`RESOURCES.md`、`workbench/README.md`、`workbench/EXECUTION.md`。
2. [讨论记录](DISCUSSION.md)：为什么选这个方向、五轮讨论中定下了什么、明确推迟了什么、用户的几条执行原则。
3. [研究方案](RESEARCH_PLAN.md)：问题、测量框架、知识对象、读数定义、分阶段计划与决策表、算力估计。**先读这一份再写代码。**
4. [相关工作与定位](RELATED_WORK.md)：最近邻、我们的增量、压缩风险。详细文献地图在 [`library/themes/training-post-training/SUBLIMINAL_LEARNING_MAP_2026-11-26.md`](../../library/themes/training-post-training/SUBLIMINAL_LEARNING_MAP_2026-11-26.md)。
5. 实验卡：[E01](experiments/E01-anchor-cat-preference.md) → [E02](experiments/E02-anchor-letter-counting.md) → [E03](experiments/E03-factorial-teachers-and-direct-learning.md) → [E04](experiments/E04-carrier-encoding-measurement.md) → [E05](experiments/E05-factorial-student-transfer.md)。**Stage 0（E01、E02）复现成功之前不跑 E03 之后的实验。**

## 执行原则（用户在讨论中明确提出）
- **问题保持高度，执行回到现实尺度：** oral 论文是罗盘，不是门槛；目标是一篇扎实的主会 poster。
- **不提前锁定主线或方法：** M1/M2/M3 都是候选，由数据决定收敛到哪里。
- **从已知有信号的设置起步：** 每个阶段都有决策表和停止 / 转向条件；更大的设想按数据解锁。
- **读原文，不凭摘要下判断：** 引用的数字必须对原文核对；外部模型（GPT / Gemini）的意见要逐条判断后再采纳。

## 论文形态卡（初稿 2026-11-27）
- **主旨：** 未定。三个候选（详见 RESEARCH_PLAN §5）：
  - **M1** 身份 ≠ 知识；
  - **M2** 条件规则的选择性继承（行为与绑定分离）；
  - **M3** 硬标签传不了新知识，是采样噪声问题还是可观察性上限（保底）。
- **形态：** 构念 + 测量（反事实教师、三层读数）为主；能否加上有效理论视数据而定。
- **manuscript-critical contributions：** ❌ 尚无证据。
- **主图：** 未定；每个候选的 Figure 1 见 RESEARCH_PLAN §5。
- **基线：** 干净教师学生（S_neutral）、范数匹配的随机教师学生、直接学习对照、理想解码器（上限）。
- **证据标准（poster 级）：**
  - 2 个模型（Qwen3.5-9B 为主，Qwen2.5-7B 作小规模检查）；
  - 每个配置 2 个教师种子（同规则跨种子作噪声地板）；
  - 学生 ≥2 个种子；
  - 硬、软两种通道；
  - 连续读数 + 95% CI。
- **定位摘要：** 见 RELATED_WORK。主要近邻是 Beyond Owls（存在性证明）、Chen（硬标签样本复杂度）、Feng（正则与复杂度）、2610.36202（能解码 ≠ 学到）、Zhao & Zhong（跨特质）。
- **风险：**
  - 强组抢先（中高）；
  - 效应只在 Qwen 上成立（中）；
  - 硬标签全零（高，所以以 logit 通道为主）；
  - 组合类知识连直接学习都学不会（中，所以设直接学习门控）。
- **本次决定：** 注册为 PROPOSED，从 Stage 0 开始。

## Idea 组合（详见 `ideas/`）
| ID | 一句话 | 来源 | 研究动作 | 状态 | 证据等级 |
|---|---|---|---|---|---|
| I01 | 学生得到的主要是教师指纹而非教师特有知识（M1） | 2610.36202 的解码 / 迁移落差；GPT 第五轮 | 构念引入 + 测量 | SEED | L0 |
| I02 | 条件规则中，行为与绑定以不同程度被继承（M2） | Beyond Owls 后门；2611.31870 情感依特质而异 | 分解测量 | SEED | L0 |
| I03 | 硬 token 对新知识的失败是采样噪声还是可观察性上限（M3） | Beyond Owls 协议混杂 + Chen 噪声逆问题 | 强基线复查 | SEED | L0 |
| I04 | 知识性质（结构化规则 vs 随机绑定）决定可迁移性，与直接学习难度分离 | Feng 附录 H/L 的未解问题；Donoway | 设计空间分解 | SEED（Stage 2） | L0 |
| I05 | 载体选择性：载体的好坏取决于知识，存在排序反转 | Li 与 Casademunt 的冲突；Nayak / Frank & Davis | 设计空间分解 | SEED（Stage 2） | L0 |
| I06 | 教师实现 × 学生结构的交叉决定可迁移性 | Feng 附录 L 的“单教师”局限；Beyond Owls 计数实验 attn-only 混杂 | 交叉对照 | SEED（Stage 2） | L0 |
| I07 | 学习准备效应：零样本未表达，但对自己教师的规则学得更快 | 2611.31870 weight lens；ICLR 2026 FAB | 新测量 | SEED（随 E05 观察） | L0 |

**推迟、不放弃**（讨论中定下，等基础现象可测之后再决定）：
- 组合知识 g∘h 与多教师重组；
- 虚构世界知识族；
- 非对易双谱有效理论；
- 模型兼容性网络；
- 完整的 V-information / MDL 测量。

## 主张摘要（详见 `CLAIMS.md`）
C01–C03 对应 M1–M3，全部 L0，无证据。

## 痛点摘要（详见 `PAIN_LOG.md`）
尚无（未开始运行）。

## 决策记录（日期 · 决定 · 依据 · 谁决定）
- 2026-11-26 · 从三个候选方向中选 subliminal learning · 用户兴趣，点名 Beyond Owls · 用户
- 2026-11-27 · 主投 ICML 2027 · — · 用户
- 2026-11-27 · 不提前锁定方法与主线，先讨论再做高信息量实验 · 用户
- 2026-11-27 · 不要从开头就按 oral 标准要求，分阶段推进 · 用户
- 2026-11-27 · 结束纸面讨论，注册 PROPOSED workbench，准备开做 · 用户

## 资产位置
- **代码：** `scripts/`（尚未编写，结构见 RESEARCH_PLAN §8）。
- **外部代码：** `lmb-freiburg/divergence-tokens`（MIT，ICLR 2026）、`MinhxLe/subliminal-learning`（官方，MIT）、`TruthfulAI-research/beyond_owls`。**用前核对 license 与 commit，写进实验卡。**
- **数据：** 教师生成的载体数据、logits、checkpoint 都不进 git；节点本地路径写进对应实验卡的结果段。`data/` 只放小型配置与评测题表。
- **结果：** `results/<E##>/`（汇总 json / csv / 图，单个文件 < 5MB）。
