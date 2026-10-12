# idea 谱系图：这个问题的每一步是怎么从上一步长出来的（2026-10-12）

> 目的：训练"从论文推测 idea 来源、尺度与距离"的能力，并为本地 agent 提供防跑偏的参照。每行写：前一步留下的未知 → 本步的最小判别动作 → 尺度 → 它没能区分什么。AUTHOR-STATED 与 RECONSTRUCTED 分开；卡片链接到规范卡。

## A. 人类侧：从"读得慢"到"读完还错"再到"错的是哪一种"

| 步 | 工作 | 前一步留下的未知 | 最小判别动作（RECONSTRUCTED） | 尺度 | 仍不能区分 |
|---|---|---|---|---|---|
| A1 | Frazier & Rayner 1982；Bever 1970 | 歧义处为何变慢 | 阅读时间 | 眼动 | 读完的解释是什么 |
| A2 | [Christianson 2001](christianson2001-thematic-roles-linger.md) | 慢≠错；读完后旧论元是否残留 | 主句正题 vs 从句旧对象题；RAT 动词排除语用；逗号/语序两种无 GP 对照 | 5 实验、24–42 项、16–36 人 | 残留是一个融合解释还是两个竞争解释 |
| A3 | [Patson 2009](patson2009-paraphrase.md) | 问句可能再激活旧命题 | 自由复述，failed/partial/full 分类 | 24 句 | 复述格式本身丢信息 |
| A4 | [van Gompel 2006](vangompel2006-structural-priming.md) | 新结构到底建没建 | 结构启动 | — | 启动≠语义 |
| A5 | [Slattery 2013](slattery2013-competing-representations.md) | 建了新结构还是没清旧义 | 下游反身性别失配（新结构功能）+ 次句承接（旧义残留） | 2 实验、24–32 项、24–28 人 | 局部树是否构成全局解释 |
| A6 | [Huang & Ferreira 2021](huang-ferreira2021-memory-versus-parse.md) | 全局解释是否完整 | 按最终答案条件化在线加工 | 眼动 n=120 | （本库仅摘要） |
| A7 | [Ceháková 2023](cehakova2023-diverse-reanalyses.md)/[2025](cehakova2025-disrupted-final-interpretations.md) | 二元题掩盖失败类型 | 同一依赖的三类题（qcor/qmis/qpos）+ 开放回答分类；英文 MV/RR 双宾语与 RAT | 48 项、141–179 人 | 问句再激活与持续表征 |
| A8 | [Paape 2026](paape2026-surprisal-not-sufficient.md) | 阅读时间混了几种过程 | 潜过程混合模型分离 p_gp / 代价 / 重分析成功 | 7 实验、n≈2000 | 最终解释内容 |
| A9 | [Zhou 2026](zhou2026-syntactic-belief-update.md) | 什么量驱动困难 | 句法信念更新量（Rényi） | SAP 3 构式 | 更新之后写入了什么 |

**谱系规律**：每一步都是"把上一步的一个混合量拆成两个可分别测的量"。我们的切口（拒绝 vs 重建）是 A5/A7 在 LLM 上的对应，A8 给了"成功率"的人类锚点。

## B. LLM 侧：从 surprisal 到理解题到机制

| 步 | 工作 | 未知 | 动作 | 尺度 | 没区分 |
|---|---|---|---|---|---|
| B1 | [Futrell 2019](abstract-only-2026-neighbors.md) | LM 是否维持句法状态 | surprisal 对受控构式 | LSTM/RNNG | 最终理解 |
| B2 | [Hu & Levy 2023](hu2023-metalinguistic-measurement.md) | 提示读数是否等于概率读数 | 直接概率 vs 元语言问句 | 4 任务 | — |
| B3 | [Li 2024](li-2024-incremental-comprehension.md) | LLM 读完 GP 后是否残留误读 | Christianson 材料分块 + 误读题概率 + parse probe + 注意力 | 24 句、4 旧模型 | 替代依赖未问 |
| B4 | [Amouyal 2025](amouyal2025-garden-path-humans-llms.md) | 人机是否因同样因素错 | 三假说三操纵同协议；228 句、大模型族；复述与图像 | 456 对×10 人；~30 模型 | 机制；替代依赖 |
| B5 | [Hanna & Mueller 2025](hanna-2024-gp-mechanisms.md) | 可解码≠使用 | SAE 特征→因果干预→后续 QA 是否复用 | Pythia-70m/Gemma-2-2b、72 句 | 外给结构是否可用；大模型 |
| B6 | [Amouyal 2026](amouyal-2026-processing-difficulties.md) | GP 在七种难结构中特别吗 | 统一协议 31 模型；thinking 开关 | 5380 人类点 | 猜想"丢弃失败"未验 |
| B7 | [Lee & Shin 2026](lee2026-good-enough-paraphrase.md) | QA 偏置还是真的 partial | 复述任务迁移 | GPT-3.5/4、24 句 | 单族、无干预 |
| B8 | [Asami 2024](asami2024-good-enough-lm.md)/[Emura 2026](abstract-only-2026-neighbors.md) | good-enough 来自什么资源约束 | 架构超参 / 双任务负荷 | BERT 族 / GPT-4o 等 | GP 修订 |
| B9 | [Ok & Lee 2026](ok2026-lost-in-prompt-order.md) | 为什么顺序效应 | 三假说淘汰到因果掩码 | 21 模型、4 数据集 | 句内依赖 |
| B10 | 本 workbench E82–E90 + 审查 | 拒绝与重建是否分离 | 替代依赖题分层 + 对照 + 显式框架族差 | 3 族、33 题 | 机制；扩材料 |

**谱系规律**：B3→B4 是"材料迁移+模型扩广"；B5 是"从行为到因果"；B9 是"从现象到架构解释"。真正改变认识的是 B5 与 B9 这种把**一个混合解释拆开并让其分叉**的工作，而不是 B4/B6 的广度。我们的 B10 应向 B5/B9 看齐。

## C. 显式状态更新线（可借方法、对象不同）

[Kim & Schuster 2023](abstract-only-2026-neighbors.md) 行为 → [Feng 2024 binding IDs](feng2024-binding-ids.md) → [Prakash 2026 lookback](prakash2026-lookback-belief-tracking.md) → [Gur-Arieh 2026](gur-arieh2026-mixed-binding-retrieval.md) / [Oh & Demberg 2026 rebinding](abstract-only-2026-neighbors.md) / [Steele 2026 shared slot](abstract-only-2026-neighbors.md) / [Tang 2026](tang2026-entity-tracking-state-changes.md)。规律：先用模板任务把"更新"做成可干预变量，再找指针/地址/内容三部分。它们的更新是**显式**的（文本说"现在是红色"）；GP 的更新是**隐式**的（只有语法要求）。预测：隐式更新可能没有专门的重绑定路径，这正是 H-A/H-C 的机制版本。

## D. 评分/belief 线（已占，PARKED）

[Belief-R 2024](wilie2024-belief-revision.md) → [ABBEL 2026](lidayan2026-abbel.md) → [Agent-BRACE](singh2026-agent-brace.md)/[ReBel](tang2026-rebel.md) → [Beyond Memory 2026](beyond-memory2026-belief-trapping.md)。一般"重建 reward 可能奖励旧解释"与"belief 更新需验证"都已有 owner。

## E. 方法范式参照

[Cho 2025 ICL circuit](cho2025-icl-inference-circuit.md)：在五种解释并存的拥挤问题里，拆步骤、每步一个测量、同一干预让解释分叉、新解释回收旧清单。这是 06 纲领 §4 的来源。

## F. 本 workbench 两轮探索在谱系里的位置（教训）

- E13–E51 研究的是 Qwen3-8B 对人工语篇框架的续写概率，不在任何一条谱系上；E29 证明它与 GP 无关。
- E52–E64 做了 B4 式广度和 B5 式因果，但读数停在误读题。
- E65–E81、E91–E107 转向目标问句与评分 credit，离开了 A/B 谱系，进入 D 线并撞上 owner。
- E82–E90 的分层数据是 B10 的起点，但当时没有被当作对象。
