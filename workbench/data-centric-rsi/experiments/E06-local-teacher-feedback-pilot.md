# E06 — 本地强 teacher 的反馈生成是否产生有用数据（2026-10-02）

- **状态：** DONE（40/arm 质量 gate 失败，按预写决策表不扩生成、不训学生；一次修复另见 E07）
- **类型：** EXPLORE/REPRO 适配；不是 DataEnvGym Table 2 原版复现。
- **对应：** I02、P01–P04；DataEnvGym Open-Ended teacher 的本地可运行替代。
- **问题：** 在 E04 简单错误检索没有稳定大优势、且评测提示敏感之后，使用同一个足够强的本地 teacher 生成新数据时，真实错误输入相对同预算随机题输入是否带来可测的训练收益？
- **区别于 E04：** 数据由 teacher *生成问题和解答*，不只是从已有正确标注池挑近邻；这靠近 DataEnvGym 的真实行动空间。两个条件只改 prompt 的 3 个状态示例，其余 teacher、调用数、schema、解码、学生训练/评测预算一致。
- **teacher/输入：** 固定缓存的 `Qwen/Qwen2.5-32B-Instruct@5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd`，单空闲卡 vLLM、temperature0.7/固定 seed，官方 Open-Ended MATH 生成模板与 `MathDataSpec` schema。每次固定 3 个共同随机 MATH train 题；with-state 再给 3 个 base 在冻结 72 题 smoke 上的错题题面，no-state 则给 3 个额外随机 MATH train 题。官方源码错题字段访问有 bug，此处显式使用题面；记录提示全文与 hash。无 Azure/GPT-4o 调用，不能把本地 teacher 效果外推到论文 teacher。论文 App B.2 写 GPT-4o temperature0；本地 0.7、每调用 1 题（源码默认 10 题）是事先选定的探索改动，两个 arm 完全相同，不能与 Table 2 数值横比。
- **pilot 阶段：** 每条件先生成 40 条（1 条/调用；结构化 JSON），逐条记录全部输出、失败、token/耗时。解析/字段非空率、与 dev/test 题面 hash、同条件重复率是质量 gate；自动检查不等于数学答案正确。抽查前 10 条的题解一致性并记录不确定。若两条件都至少 36/40 可解析且无 dev/test 精确题面重合，才固定扩到各 120；不足则保留失败并先修生成器，不拿坏数据直接比较训练收益。
- **学生训练/读数：** 扩到 120 后，保留全部 raw 并按固定顺序取前 120 条符合 schema、非空且未与 dev/test 精确重复的数据；若任一条件不足 120，则降低双方到相同可用条数且记录成本，不续造有利条件。与 E00 同 Gemma parent、LoRA、3 epoch、optimizer reset、固定 seed17/29/43。**主读数**为已冻结的 train-derived dev1740 扣除进入 teacher 状态的 72 条 smoke 后的 **1668 题**，所有动作统一 zero-shot＋显式格式；352 题中相应的 heldout280 用作与 E04/E05 对照，原 few-shot＋格式仅作提示稳健性辅助读数。报告 paired delta 与静态 120 真值基线，全部生成 token/GPU 和学生训练成本。若答案正确性抽查明显不足，不把低效误判为反馈信息无用。
- **阳性对照：** teacher JSON schema 成功，MATH 已知真值静态学生组相对 base 的读数作为同预算学得动的参考；错误输入 prompt 实际包含错误题面，no-state 不含；训练题面 hash 不泄漏 dev/test。
- **噪声地板 + MIE：** E00/E04 三训练 seed 的行动差异与两个提示下的范围；需要跨 seed 同向、超过约 5pp 且优于强静态的可解释训练收益，才考虑继续把“反馈有特殊价值”作为方向，而非自动主张升级。
- **混杂：** teacher 输出质量/题型/长度可因状态示例而变，这本身可能是反馈途径，需报告而非事后匹配掉；数学答案可能错，样本抽查不够证明全体正确。当前 72 题 smoke 有 60 个 base 错误，随机 smoke 多数也会是错误；with-state 与 no-state 同时改变了“来自 dev 还是 train pool”和“是否按错题筛”，即使 with-state 胜出也不能单独归因于错误选择。若存在收益，下一项关键 control 应用同一 smoke 来源的未按正确性筛选题作 teacher 输入。不同生成成本不能隐藏。数据源/教师/轮数不等于官方。
- **决策表（跑之前写）：** 生成资产质量可用且 with-state 明显胜 no-state/静态 → 定位具体提供决策价值的状态信息、扩 learner/task；no-state 或静态更强 → 研究强简单数据为什么足够、teacher quality/coverage 机制，不能保住反馈 idea；两者都坏 → 修生成质量或改成熟 substrate，不作反馈科学结论；两者相近 → 不造 agent，寻找更有区分力的自然行动空间。
- **算力预算：** 先 80 条 teacher 输出，单模型首次读取 62GB 权重在共享 I/O 上可能主导 wall-clock；实际成本单列。若过 gate，再 160 输出 + 六个学生训练 + 主评估/必要的基线评估，预算预计 ≤3 GPU·时，不用读数好坏临时挑模型。单节点独立卡、API 0。**实际：** 待填。

**执行前修订（2026-10-02 14:40 JST，teacher 尚在加载权重、未产生任何生成/训练读数）：** 原 352 主读数混有给 teacher 的 72 道反馈题，且 2–5pp 行动差异的逐题不确定性较大。故将主读数改为完整冻结 dev 扣除 smoke 的 1668 题，原 heldout280 保留为比较历史 E04/E05 的轴。这是看到 E00–E05 的提示审计后、看到 E06 任一输出前作出的设计修订；本卡保留原文含义和修订时间，不事后择优。

## 结果（执行后追加）

- **首批 80 次 teacher 调用：** no-state 40/40 通过 schema/非空/精确泄漏/去重 gate；with-state **32/40**，低于预写的 ≥36/40 扩样门槛。with-state 失败细项：2 JSON 在 768 token 截断、3 精确撞上 dev/test（均复制本次错误示例）、3 臂内重复。原始 prompt/输出逐条保存，见 [`results/E06_teacher_pilot_manifest.json`](../results/E06_teacher_pilot_manifest.json)。
- **更深的质量检查：** 在可解析输出中 no-state **8/40**、with-state **9/38** 精确复制本次输入示例；后者其中 3 条来自 dev 错题。两臂有 5 个相同生成题，4 个出现在相同调用索引；with-state 有 9/38 题短于 45 字符，部分只是一个不等式或没有图的图形题。前 10 条/arm 的定向题解抽查发现已知 MATH 题面的错误答案：例如两位数平方根小于 8 的概率，teacher 给 4/9、原真值为 3/5；另有 `9^105` 末三位给 969、原真值 049。抽查不能推算总体错误率，但足以否决“schema 合格即高质量”。计算细节见 [`results/E06_teacher_pilot_quality.json`](../results/E06_teacher_pilot_quality.json)。
- **实际成本：** 53,892 输入 token、28,121 生成 token；单卡 GPU 占用 wall **1501.8 秒 = 0.417 GPU·时**，其中约 19 分钟为共享盘冷载 32B 权重，生成约 4–5 分钟；CPU 主要为轻量 prompt/解析，API 调用和费用 0。E06 学生训练 **0**，因为 gate 未过。
- **按决策表：** 本地 Qwen 适配的数据新鲜度/正确性不足，不能用它裁决“反馈是否提供独特信息”。E07 只测试一次已知质量故障的最小修复；若仍不过门槛，停止该 prompt 路线，优先寻找真实标注或其他成熟资产上的行动效用瓶颈。C01–C04 均保持 L0；不从这一失败推断原论文 GPT-4o 结果错误。
