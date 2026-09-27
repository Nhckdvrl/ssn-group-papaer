# ssn-taste 科研选题搜索指南（Canonical）

最后重构：2026-09-26

这个文件夹只优化一件事：

> **找到符合 Sasano 本人真实 taste、自然、清楚、结果值得知道，并具有 ACL / EMNLP / NAACL Main 潜力的问题。**

当前正式状态：

> **selected = 0；S01–S12 全部 KILL。**

用户个人偏好的 method paper / benchmark gain / training / mechanism 题型，不得反向定义 Sasano taste。

---

# 1. 开局第一件事：重新对齐 Sasano 本人 Slack

每一轮搜索开始前，必须先读 **Sasano 本人**最近与历史上具有区分度的研究评价；其他学生的话只能提供上下文，不能当 taste evidence。

至少检查：
- 面白い / 意外 / 驚き / 予想；
- 新規性 / nearest prior；
- Introduction / reviewer clarity；
- 見切り / stop / switch。

不要只总结抽象 slogan，要恢复**具体案例与 Sasano 为什么这么判断**。

当前最重要的已知校准：

1. **2026-09-18 / 09-14：reviewer 不会替作者寻找有趣点。**
   - 平均 reviewer 必须很快看懂“做什么、为什么有意思”。
   - 最有意外性的 finding 应成为主线。
   - RQ 与 finding 尽量一一对应。

2. **2026-07-08：结果与事前预测相反，本身可以变得更有意思。**
   - 对未知名字 / factual context 的实验，Sasano 明确说“与事前预测不同，但这是挺有意思的结果”。
   - 下一步建议不是立即造复杂机制，而是换 obituary / politics / sports 等**自然 context**继续验证结果是否稳定。

3. **2026-06-28：novel 不等于 interesting。**
   - 把 activation-space 的问题搬到 weight-space 可以有合理 novelty。
   - 但“曲线方法比粗糙直线更准确”本身并不惊讶。
   - curvature / isometry 等指标如果难以连接到模型实际知识或行为，很难说“我们到底知道了什么”。

4. **Novelty 必须能非常简洁地说清楚与最近工作差在哪；差异太小就应该见切り。**

这些不是固定模板。每轮必须重新查最新 Slack；若出现新的 Sasano 明确评价，以最新真实评价更新理解。

---

# 2. 两种已经证明会制造垃圾题的起点

## 禁止 A：漂亮理论二分先行

不要：

> A 和 B 理论上不同 → LLM 会不会区分？

旧池中的 typed/untyped、state/retrieval、source/rule、definition/fact 等已经证明：概念漂亮并不意味着现实里存在一个自然、可识别、值得知道的研究对象。

## 禁止 B：单篇 published anomaly 先行

也不要：

> 某论文报告了 surprising result → 我们来解释 why。

真正漂亮的 published anomaly 通常已经被原作者、appendix、同组 follow-up 或后续工作迅速占领。

**单篇 anomaly 可以作为证据，但不能单独成为选题来源。**

---

# 3. 正确起点：Tension-first, discovery-driven

题目优先从：

> **多篇独立工作之间尚未被显式提出的 latent tension / missing variable / scope conflict**

长出来。

有效 tension 必须满足：

1. 至少两个独立 evidence source；
2. 两个 claim / result 在一个**自然共享 regime** 下留下不同 prediction、缺失 moderator 或 scope 冲突；
3. shared regime 不是我们为了论文现造的；
4. 解决 tension 会改变对至少一个现有结论的理解；
5. nearest prior 尚未正面提出并解决同一个 parent question。

常见合法来源：

- 两篇强工作在真正可比条件下隐含相反 prediction；
- A 在 R1 成立、B 在 R2 成立，而一个共同变量 M 可能决定转折；
- broad claim 的证据只覆盖 narrow regime，另一独立结果说明这个边界可能是关键；
- 独立模型/技术进展改变了旧结论依赖的关键 premise；
- 忠实复现强工作时，我们自己自然观察到稳定 reversal / boundary。

---

# 4. 搜索阶段：先做 Claim Map，不先写 RQ

每轮读约 8–15 篇强工作，跨 2–3 个相关 lineage。

每篇只抽：
- Claim：作者真正主张什么；
- Evidence regime：在哪些模型 / 数据 / 任务 / scale 下成立；
- Scope：作者把结论说得多广；
- Load-bearing premise：推广时依赖什么；
- Untested natural boundary；
- 与其他工作可能产生的 tension。

目标是产生约 3–6 个 latent tensions。

此时：
- 不创建 Sxx；
- 不写宏大 mother question；
- 不先想 mechanism；
- 不从 FAILED_TOPICS 找灵感。

---

# 5. Cheap parent check：先杀掉已经被做过的大问题

对 tension 做廉价检索：
- exact combined tension；
- same shared regime；
- same missing moderator；
- source authors follow-up；
- 最近 12–18 个月工作。

如果 parent 已经被正面讨论或解释，直接 KILL。

不要退到 exact cell、换模型、换语言、换 modality、更干净 replication 或“他们没测我们这个小条件”。

---

# 6. Natural reconnaissance：不是验证 anomaly，而是看真实行为长什么样

只有 parent check 通过的 tension 才值得做小规模 reconnaissance。

目标：

> **在自然 setting 中看这个 tension 到底有没有真实结构。**

要求：
- 优先已有 benchmark / natural data / normal task；
- 只检查 1–2 个由 tension 自然推出的轴；
- 小规模、便宜；
- data slice / metric / parser / basic controls 在看输出前固定；
- 不先规定必须出现哪个“好看 anomaly”；
- 不做 prompt sweep；
- 不先做 mechanism；
- 不用 synthetic micro-world 创造 phenomenon。

Recon 允许观察：是否反转、是否非单调、哪个 subset / scale / family 改变方向、是否有 sharp boundary、最简单 baseline 是否足够解释。

**如果结果平凡，就 KILL。不要说“null 也有意义”来续命。**

---

# 7. Pattern crystallization：我们自己先看到稳定现象，才允许形成 RQ

只有 recon 出现 nontrivial pattern 才继续。

至少要求：
1. 不是单点；
2. 新 seed / 第二个自然 subset / 第二个合理 setting 中仍然存在；
3. 不是 parser / prompt / scoring artifact；
4. 最简单 baseline 不能直接解释；
5. 一句话能把 pattern 讲清楚；
6. 普通 reviewer 能理解为什么它改变了原来的 claim 关系；
7. 按 Sasano taste 看，结果本身有一定意外性或直接修改了 live prior claim。

此时才第一次允许写：

> **我们观察到了 O。**

然后 RQ 只围绕 O：

> 在由文献张力导出的 regime C 中，我们稳定观察到 O；什么因素解释 O / 决定这个转折？

**one finding ↔ one RQ。**

---

# 8. Deep novelty audit：有自己的 pattern 后才全面查重

现在再查：
- same observed pattern；
- same RQ；
- same decisive contrast；
- source main / appendix；
- source-author follow-up；
- 最近工作；
- targeted FAILED_TOPICS anti-resurrection。

如果 nearest reviewer 可以把它压成 known anomaly 的 why、known parent 的新 cell、domain/model/language extension 或 cleaner replication，直接 KILL。

---

# 9. Instrument preflight：Sxx 出生前最后一道硬门

不单独维护模板文件；候选如果走到这里，直接按以下 checklist 执行。

必须全部通过：
1. Prerequisite：模型会做 readout 所需的更简单能力。
2. Manipulation validity：条件差异确实对应 scientific variable，不被 wording / difficulty / length / information amount 等替代。
3. Readout validity：结果真的回答 RQ，而不是 prerequisite skill。
4. Symmetry：逻辑等价、polarity、answer order 等不出现灾难性翻转。
5. Positive / negative controls：两端都成立。
6. Ground truth / scorer / parser：程序性部分严格验证。
7. No prompt search：看过结果后不能扫 prompt 挑最漂亮版本。
8. Control budget：如果需要不断加控制才能解释 construct，默认 KILL。
9. Synthetic dependence：删掉 synthetic diagnostic 后，真实 tension / pattern 仍独立成立。

**Preflight 失败：在没有 Sxx 编号的状态下 KILL。**

不存在 Sxx — SERIOUS / PREFLIGHT-PENDING / MAYBE。

---

# 10. 什么时候才允许 PILOT-AUTHORIZED

只有全部完成：

> Sasano Slack calibration
> → multi-paper tension
> → parent collision check
> → natural reconnaissance
> → our stable nontrivial pattern
> → one-finding/one-RQ
> → deep novelty audit
> → instrument preflight

才允许创建新的 Sxx registration、写入 SELECTED_TOPICS.md、标记 PILOT-AUTHORIZED。

Selected 的含义是：

> **问题不是靠想象存在；现象是我们自己在自然 setting 里先看到并验证；prior 没占；instrument 也能正确测。**

不是“这个想法值得试试看”。

---

# 11. Global Reset / KILL 信号

立即停掉当前 lineage，当出现：
- 开始想“怎么让这个现象出现”；
- 开始保护一个 tension；
- controls 越来越多；
- novelty 开始依赖 wording / exact cell；
- theory taxonomy 比真实结果复杂；
- source anomaly 越查越像原作者已经做完；
- synthetic assay 不存在，问题就不存在；
- Sasano 的真实评价形状明显不支持这个方向；
- 30 秒无法向普通 reviewer 解释“哪里有意思”。

允许整轮 **0 survivor**。

---

# 12. 文件纪律：不要再制造流程文档

下一轮 agent 正常只需要读：
1. SEARCH_GUIDE_ZH.md — 唯一 canonical 方法；
2. README.md — 当前状态；
3. SELECTED_TOPICS.md — 最终入选 ledger；
4. recent commits。

新对话可额外读 NEXT_ROUND_PROMPT_ZH.md。

只在需要复盘旧失败时看 POOL_POSTMORTEM_2026-09-26.md、targeted FAILED_TOPICS 或旧 Sxx/experiments。

**禁止再新建 Claim Map / Observation Portfolio / Taste Calibration / Preflight Template 等流程文件。**
Claim Map、tensions、recon 候选都先在当前工作过程里维护；只有最终通过全部 gate 才进入 Sxx/SELECTED，严重失败才定向写入现有 FAILED ledger。

---

# 13. 最后只记住八句话

> **Sasano 本人的 Slack 判断永远是 taste 第一来源。**
> **不是 question-first，也不是 published-anomaly-first，而是 tension-first。**
> **题目优先从多篇工作的综合里长出来。**
> **Recon 是为了发现真实结构，不是验证预设的神奇 anomaly。**
> **平凡结果就 KILL。**
> **先有我们自己的稳定 pattern，再冻结 RQ。**
> **Preflight 过不了，Sxx 根本不出生。**
> **文档越少越好：一个 guide 管流程，一个 selected 管结果。**
