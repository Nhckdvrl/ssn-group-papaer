# Agent Workflow — 如何用本仓库找题与写文档

这份文件是下一轮 research agent 的**操作协议**。

它不定义科研 taste；taste 与生死门槛见：

- `../SEARCH_GUIDE_ZH.md`
- `PAPER_GENEALOGY_GUIDE.md`
- `PARADIGM_ATLAS_ZH.md`

本文件只回答：

> **agent 到底先读什么、什么时候搜索、什么时候写 repo、结果应该写到哪里。**

---

# 1. 第一原则：progressive disclosure

这个仓库已经接近 1MB 文本。

**禁止启动时全仓通读。**

正确顺序：

## Level 0 — 必读，恢复正式状态

每次新 agent 开始，只先读：

1. `../README.md`
2. `../SEARCH_GUIDE_ZH.md`
3. `../SELECTED_TOPICS.md`
4. 本文件

目的：

- 知道当前正式状态；
- 知道 canonical gate；
- 知道目录职责；
- 不相信旧 handoff。

## Level 1 — 方法校准

真正开始选题前读：

5. `PAPER_GENEALOGY_GUIDE.md`
6. `PARADIGM_ATLAS_ZH.md`

如果已经非常熟悉，可以只重读 relevant sections，不必每轮全文。

## Level 2 — 定向证据

根据当前 lineage 再读：

- academic：`../academic/README.md` → index → 对应 genealogy；
- industry：`../industry/README.md` → scan/deep dive → 必要时 source ledger；
- startup/HF：`../startup_hf/README.md` → deep dive → 对应 genealogy。

**SOURCE_LEDGER 只在核具体 claim 时读。**

不要把 100KB ledger 当背景教材。

## Level 3 — Candidate collision

只有 seed 已经形成，才：

- 搜最新 web；
- 读 dangerous nearest priors 原文；
- 查对应 industry/open artifacts；
- 调用 `SPECIALIZED_AUDITS.md` 中相关 gate。

---

# 2. 新 agent 的第一轮工作

除非用户直接指定一个具体 candidate，否则按下面执行。

## Step A — Restore

确认：

- 当前 selected CTxx；
- 最近 commit / 新文件；
- 是否有用户刚刚新增的 kill/constraint；
- broad scan 是否已关闭。

## Step B — 选择 lineage，不选 idea

从用户当前兴趣 + repo evidence 选择 3–5 条 lineage。

每条先写在**内部工作区/聊天中**：

- parent problem；
- recent frontier；
- saturated axes；
- unresolved pressure；
- execution shape。

此时**不要创建 repo candidate 文件**。

## Step C — Deepen only where pressure is real

若一条 lineage 只剩：

- 新模型；
- 新 benchmark；
- another variant；
- future-work gap；

停止。

若出现：

- unresolved relation；
- changed premise；
- contradictory evidence；
- new deployment constraint；
- new public causal contrast；
- measurement semantics changed；

再继续读原文。

## Step D — Lock one seed

不要 dump 20 个 idea。

选当前最强 seed，开始 full audit。

如果它死：

> 记录 kill，然后再回 lineage pool。

---

# 3. Candidate 生命周期

正式状态只有三种：

## A. Unlocked seed

- 只在当前工作过程存在；
- **不写 repo**；
- 不分配 CT 编号。

这样避免 `topics/` 堆几十个半成品。

## B. Locked but killed

当一个 seed 已完成真正 audit 后被杀：

- 不创建独立 CT 文件；
- 在 `../topics/FAILED_TOPICS.md` 追加一条 concise record。

至少记录：

- short name / mother question；
- lineage；
- nearest covering prior；
- decisive kill reason；
- kill category；
- anti-resurrection note。

## C. PILOT-AUTHORIZED

只有过线才：

1. 分配下一个 CTxx；
2. 创建 `../topics/CTxx_<slug>.md`；
3. 更新 `../SELECTED_TOPICS.md`；
4. 写 minimum pilot 与 pre-registered kill conditions。

若真实 pilot 之后触发 kill：

- registration 保留并标记 **CANCELLED / KILLED AFTER PILOT**；
- 从 `SELECTED_TOPICS.md` 移除；
- 同时在 `FAILED_TOPICS.md` 留索引。

---

# 4. 文档写到哪里

## 根目录

只允许：

- `README.md`
- `SEARCH_GUIDE_ZH.md`
- `SELECTED_TOPICS.md`

除非目录职责发生根本变化，不再往根目录加新文件。

## framework/

只写**跨候选、可长期复用的规则**。

可以写：

- genealogy reading method；
- paradigm/taste calibration；
- specialized audits；
- repeated failure lesson；
- agent workflow。

不要写：

- 某个 candidate 的 related work；
- 一轮 search 的流水账；
- 某家公司刚发了什么。

一条新经验只有满足：

> **未来多个 candidate 都会因为它改变决策**

才进入 framework。

## academic/

只写学术 evidence synthesis：

- longitudinal genealogy；
- literature map；
- paper autopsy；
- academic index。

新增 genealogy 前先问：

> 现有 01–04 是否已经覆盖？

能追加到现有文件就不要新建 05/06。

只有形成**独立、长期可复用的 lineage**时再开新文件。

## industry/

- `SOURCE_LEDGER.md`：原始来源、日期、claim、链接/证据。
- `FRONTIER_SCAN.md`：高层 landscape。
- `FRONTIER_DEEP_DIVE.md`：少数真正重要对象。
- `GENEALOGIES_*.md`：纵向 industrial lineage。

不要把同一 source 的原始摘录复制到多个文件。

规则：

> ledger 存证据；deep dive/genealogy 存解释。

## startup_hf/

同 industry，但重点是：

- public artifact；
- checkpoint lineage；
- failed release；
- stage pair；
- runnable proxy；
- reproduction harness。

不要因为一个模型在 HF trending 就升级 scientific priority。

## topics/

只放：

- authorized registration；
- killed ledger。

不放 brainstorm。

---

# 5. 防重复写作规则

一条结论只能有一个 canonical home。

例如：

> “public checkpoint 不等于 causal experiment”

canonical home 是：
> `SPECIALIZED_AUDITS.md`

其他文档只链接，不重复写 5 段解释。

再例如：

> “same decisive unknown 比关键词 overlap 重要”

canonical home 是：
> 根目录 `SEARCH_GUIDE_ZH.md`

不要在 README、closeout、agent workflow 反复扩写。

写新段落前先问：

> **这是新知识，还是旧规则的又一次复述？**

如果是后者：

> link，不 rewrite。

---

# 6. Evidence 与 synthesis 分层

任何重要 claim 尽量经历：

```
source
→ source ledger / paper note
→ genealogy/deep dive
→ candidate pressure
→ topic registration
```

不要倒过来：

> 先有 candidate story，再去搜 source 证明它。

## Source layer

只记录：

- paper/report/model card；
- date/version；
- factual claim；
- direct evidence；
- caveat。

## Synthesis layer

才允许写：

- lineage；
- pressure；
- conflict；
- assumption；
- implication。

## Candidate layer

只引用真正 load-bearing evidence。

---

# 7. Web / paper 阅读纪律

当前信息、论文版本、工业 frontier 都可能变化。

正式 candidate audit 时：

- 搜最新论文；
- 优先 official paper / proceedings / project page；
- core prior 至少读 intro、related work、decisive experiment/method；
- PDF 必须看原文，不靠二手摘要；
- PaperNotes 用于 breadth，不用于最终 novelty judgment。

对 recent trendy cluster，尤其检查：

> 过去 6–12 个月是否已经出现平行工作。

---

# 8. 找题时如何使用三条轨道

最强 candidate 通常不是从一个来源独立产生，而是三条轨道互相约束。

## Academic-first

适合：

- explanatory conflict；
- theory assumption；
- mechanism；
- training objective；
- well-defined scientific object。

再用 industry/startup 检查：

- pressure 是否真实；
- 是否已有 cheap artifact。

## Industry-first

适合：

- deployment constraint；
- product knob；
- scale-only failure；
- architecture–system co-design。

必须回 academic：

> underlying quantity 是否已有 ownership？

## Artifact-first

适合：

- matched checkpoints；
- stage pair；
- failed model；
- runnable proxy；
- public development tree。

必须先问：

> artifact contrast 是 causal，还是 bundled recipe difference？

---

# 9. Agent 输出给用户的节奏

不要每读 5 篇就跳出来总结。

只有这些节点值得报告：

1. **发现真正改变搜索方向的 pressure**；
2. **锁定一个 candidate**；
3. **nearest prior 把 candidate kill 了**；
4. **candidate 完成审计，给最终 verdict**；
5. 用户要求阶段性汇报。

普通阅读进度直接继续做厚。

如果用户说：

> “继续”

默认含义是：

> 继续当前阶段，不要提前收尾。

---

# 10. Candidate 审计时的最小文档结构

在真正裁决 candidate 前，工作区至少回答：

- Mother question
- Why now
- Genealogy / pressure
- Nearest priors
- Reviewer compression
- Exact novelty boundary
- Competing explanations
- Identification logic
- Minimum pilot
- Data / ground truth
- Compute / engineering
- Relevant specialized audits
- Main-story growth path
- Kill conditions

然后必须给：

> **PILOT-AUTHORIZED**

或：

> **KILL**

不使用正式 SERIOUS/HOLD。

---

# 11. Repo 更新纪律

每次更新遵守：

## Small conceptual commits

一次 commit 尽量只做一类事：

- reorganize paths；
- update canonical rule；
- add one genealogy；
- register one topic；
- append source evidence。

## 不把 search 流水账 commit 进去

失败 brainstorm 如果还没完成 audit：

> 不落盘。

## Kill 要留最小证据

真正锁定并审死的题必须进 failed ledger，避免下一轮换名复活。

## Canonical 文件保持短

- README：入口；
- SEARCH_GUIDE：硬流程；
- SELECTED_TOPICS：状态。

证据和长解释留在子目录。

---

# 12. 下一轮 agent 的推荐 prompt 行为

拿到 repo 后，agent 应该先自行执行：

> “恢复 README / SEARCH_GUIDE / SELECTED_TOPICS / AGENT_WORKFLOW，确认当前 selected 与目录职责；根据用户这轮目标选择 3–5 条 relevant lineage，只读取对应 academic/industry/startup 文件；先重建 lineage 和 pressure，不先 brainstorm；形成 seed 后锁一个，深读 nearest prior，最终只给 PILOT-AUTHORIZED 或 KILL；repo 只写正式 registration、failed ledger 或真正可复用的新 evidence。”

这比把整份 1MB 仓库全部塞给 agent 更有效。

---

# 13. 当前阶段

Broad calibration 已经收口。

下一轮默认不再继续无限扩充 genealogy library，而是：

> **定向选 lineage → 找真实 pressure → 锁一个 candidate → 审到底。**

如果 candidate 落在 repo 明确标记的薄弱领域，再临时补对应 genealogy。
