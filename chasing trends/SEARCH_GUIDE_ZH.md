# chasing trends 科研选题搜索指南（Canonical）

最后整理：2026-09-19

这份文件只保留**正式找题时必须执行的主流程和硬门槛**。论文阅读方法、范式案例、专项审计、历史纠偏都已拆到 `framework/` 与各证据目录，不再重复堆在这里。

当前状态：

- broad literature calibration 已完成；
- 正式 topic search 已开启；
- 当前 formal selected：**CT02**；
- 新 candidate 审完后只允许 **PILOT-AUTHORIZED** 或 **KILL**；
- 允许整轮 **0 survivor**。

---

# 1. 目标

目标不是：

> 找“没人做过的格子”。

也不是：

> 看一个热门 paper，顺着 future work 做下一格。

更不是：

> 先决定要做 failure→mechanism→method、adaptive compute、latent reasoning 等某种题型，再到处找例子。

真正目标是：

> **从真实 literature / deployment / artifact pressure 中，找到一个当前仍未被回答清楚、能被现实实验区分、并且适合我们执行条件的问题。**

形式可以是：

- scientific / mechanistic；
- method；
- theory；
- empirical phenomenon / limits；
- systems / deployment-driven。

paper type 由问题自己决定，不预先规定。

---

# 2. Source hierarchy

每轮都以**最新 repo 正式状态**为准：

> latest repo > handoff > historical chat summary

三条证据轨道分工不同。

## Academic

主要用于：

- parent / nearest prior；
- novelty；
- explanatory alternatives；
- identification；
- controlled evidence；
- reviewer taste。

## Industry

主要用于：

- frontier scale；
- deployment constraint；
- real product knob；
- architecture–system co-design；
- production failure；
- academic 暂时难触达的 regime。

原则：

> **industry generates pressure; controlled work establishes explanation。**

## Startup / HF / open artifacts

主要用于：

- matched checkpoints；
- stage pairs；
- public failure artifacts；
- small proxy；
- runnable instrument；
- development tree。

原则：

> **artifact archaeology before GPU。**

任何一条轨道都不能单独替代另外两条。

---

# 3. 每轮开始：Restore

先读：

1. `README.md`
2. `SELECTED_TOPICS.md`
3. 本文件
4. `framework/PAPER_GENEALOGY_GUIDE.md`
5. 与目标 lineage 对应的 academic / industry / startup_hf 文件
6. 已有 topics / failed registration，防止复活旧题

不要默认重读全部 source ledger；按 lineage / candidate 定向进入。

自有 selected/failed topics 只用于：

- dedup；
- execution lessons；
- anti-resurrection；
- 已有实验资产。

**不得把自己的旧题当正向 taste exemplar。**

---

# 4. 先选 lineage，不先想题

正式搜索时，先选 3–5 条值得看的 lineage。

每条先恢复：

- parent problem；
- dominant decomposition；
- saturated axes；
- frozen assumptions；
- coupled quantities；
- missing relations；
- changed premise；
- practical constraints；
- contradictory evidence。

不要第一步就写：

> “我有 20 个 idea。”

如果 seed 说不清自己从哪条 literature pressure 长出来，默认低优先级。

---

# 5. Breadth 与 depth

## Breadth

用途：

- 看 field 最近在沿哪些轴拥挤；
- 找 parallel discovery；
- 判断某个 conceptual move 是否已经成 cluster；
- 找值得 deep-read 的 core papers。

可使用：

- PaperNotes；
- conference pages；
- title / abstract；
- citation neighborhood；
- model/release pages。

breadth scan 不直接判 novelty。

## Depth

一旦 paper 进入 taste calibration 或 candidate audit，至少读：

- Introduction；
- Related Work；
- problem setup；
- decisive experiment / theorem；
- method derivation；
- main ablation / boundary；
- Discussion / Limitations。

并向下追 3–8 个 immediate parents/siblings。

详细方法见：

> `framework/PAPER_GENEALOGY_GUIDE.md`

---

# 6. Genealogy relation 必须标证据等级

纵向 reconstruction 使用：

- **[DIRECT]**：后作明确引用/挑战/扩展 parent。
- **[FIELD]**：同一明确 literature family；只说明 field context。
- **[RECONSTRUCTED]**：我们的事后 conceptual reconstruction。

禁止把 [RECONSTRUCTED] 写成：

> “作者就是这样想到的”。

目标是恢复：

> literature state 与 logical opening，

不是编作者心理史。

---

# 7. 从 pressure 到 seed

可以记录的 pressure 包括但不限于：

- 多篇 paper 的解释冲突；
- 成功方法内部未拆开的 learning signal；
- 方法 zoo 缺少 matched attribution；
- 旧 theorem 依赖 load-bearing premise；
- deployment variable 没进入算法 state；
- measurement unit 太粗；
- proxy 在新 regime 下语义变了；
- prior evidence 只存在于 artificial regime；
- strong method 的 original explanation 与实际 dynamics 不一致；
- 新 modality / scale / system role 改变旧 abstraction；
- mature method family 中出现稳定 failure / compatibility boundary。

这些**不是 idea generator checklist**。

正确顺序是：

> literature history → pressure → question

不是：

> 模板 → 找一个能填的例子。

已观察到的 paper-growth patterns 只作校准，见：

> `framework/PARADIGM_ATLAS_ZH.md`

---

# 8. Lock one candidate

找到当前最强 seed 后锁住。

不要因为又看到一篇新 paper 就逃到另一个 idea。

接下来必须审到底：

> **PILOT-AUTHORIZED**
>
> 或
>
> **KILL**

不保留正式 SERIOUS/HOLD 半成品。

---

# 9. Nearest-prior audit

真正危险的 prior 至少读：

- abstract；
- intro；
- related work；
- main claim；
- core experiment；
- relevant ablation / discussion。

强制回答：

1. reviewer 会把我们压成哪个 parent？
2. prior 真正知道的 knowledge sentence 是什么？
3. 它有没有已经回答 **same decisive unknown**？
4. 它有没有已经区分我们关心的同一组 explanation？
5. 我们新增的是 knowledge delta，还是 new setting？
6. 删除 trigger paper 后，这个问题还会不会从其他 pressure 自然出现？

关键词 overlap 不自动 kill。

但若只是：

> old problem + new model / language / benchmark / dataset

直接 kill。

---

# 10. Reviewer compression

每个 candidate 必须写最危险的一句话：

> “你不就是 ______ 吗？”

然后用**具体 evidence / distinction**回答，而不是 rhetoric。

例如：

- 不只是 “old context can hurt”，而是 validity-conditioned reuse of executed reasoning；
- 不只是 “adaptive compute”，而是某个 state variable 改变 marginal compute value；
- 不只是 “better representation”，而是 consumer contract 改变导致旧 representation objective 不再充分。

如果去掉方法名和新术语以后，只剩：

> “我们这个 setting 也测了一下”

KILL。

---

# 11. Identification audit

问题必须有一个最小实验真正区分主要解释。

优先：

- matched contrast；
- controlled intervention；
- interaction；
- sign reversal；
- causal mediation；
- boundary prediction；
- method-strength × mechanism-strength relation。

避免：

- post-hoc outcome grouping；
- treatment 后变量定义 condition；
- cherry-picking；
- 只靠 probe/decodability 就声称 mechanism。

不要求 theorem-level 完美控制。

只控制：

> **会改变核心 scientific interpretation 的 load-bearing confound。**

如果必须十几个 arms 才能拆开主要解释，认真考虑 kill。

---

# 12. Data / compute / recipe audit

候选在注册前必须回答：

- 数据从哪里来？
- ground truth / success signal 从哪里来？
- 是否需要大量人工？
- 是否需要新 benchmark / simulator？
- pilot 需要多少 GPU / API / wall time？
- 最小模型是否足以判生死？
- full story 是否依赖 model zoo？
- training conclusion 是否可能只是 optimizer / budget / recipe biography？

优先：

- inference-only；
- public matched artifact；
- existing dataset；
- small-model controlled training；
- short SFT/RL；
- open-source evaluation。

谨慎：

- full pretraining；
- 30B+ repeated RL；
- large agent environments；
- huge API judge；
- massive synthetic dataset；
- 1000-model sweep。

**强 paper 的 execution shape 不自动适合我们。**

---

# 13. Public artifact / proxy discipline

公开 checkpoint 可以显著降低 pilot 成本，但不是天然 causal experiment。

必须检查：

- stage pair 是否同时改了多个变量；
- small proxy 与 larger model 的 effect sign / method ranking 是否一致；
- proxy 是否真正连接 downstream consumer；
- artifact 当前是否可跑，而不是“coming soon”；
- 最小 causal visibility 在什么 scale。

详细规则见：

> `framework/SPECIALIZED_AUDITS.md`

如果一个问题只有 proprietary / >100B / production traffic 才能确认：

> 只作 inspiration，不注册。

---

# 14. Evaluator / oracle discipline

任何 candidate 若依赖：

- verifier；
- tests；
- LLM judge；
- simulator；
- executable reward；
- success checker；

不能默认 evaluator = correctness。

至少要检查：

- obvious non-solution；
- near-miss mutation；
- shortcut；
- denominator/censoring；
- repeatability；
- evaluator 在系统里究竟是 exploration / reward / certification / transition / teacher 哪个角色。

如果 evaluator 本身要变成一整篇项目才能 qualification：

> candidate 很可能已经偏成 evaluator paper。

详细规则见：

> `framework/SPECIALIZED_AUDITS.md`

---

# 15. Trend maturity

热门方向不能因为 hot 就提高优先级。

如果最近开始密集出现：

- matched-budget comparison；
- evaluator correction；
- reproduction / negative result；
- compatibility / boundary paper；
- held-out generalization audit；

说明 surface 已进入：

> **method zoo → attribution / consolidation**

此时 generic variant 默认降权。

同样，多家公司都采用某 pattern 只能说明：

> operational pressure 真实，

不说明：

> conceptual move 仍然新。

---

# 16. Cross-domain migration

跨领域可以大量读，但迁移的不是名词。

流程：

1. 恢复 source paper 的真实 genealogy。
2. 删除领域名词与方法名。
3. 写清 source pressure 的 causal / mathematical structure。
4. 在 target field 中寻找**独立存在**的同构 pressure。
5. 导出 target-specific prediction。
6. 再考虑 method。

以下词本身没有 novelty：

- adaptive
- selective
- latent
- unified
- dynamic
- mismatch
- bottleneck
- invariant
- curriculum
- sparse

如果只剩 surface analogy：

> KILL。

---

# 17. Industry-derived seed

来自大公司/产品的 seed 必须做 scale stripping：

删除：

- 公司名；
- model size；
- GPU；
- proprietary traffic；
- proprietary product feature。

然后问：

> 还剩哪个 relation / constraint / assumption？

同时必须有：

- independent academic pressure；
- cheap causal echo；
- proxy validity；
- compute ceiling。

industry report 可支持：

> “这个问题在 frontier deployment 真实存在。”

通常不能单独支持：

> “这个 mechanism 已被证明。”

---

# 18. Specialized audits：按风险触发

不要把 40 条规则机械跑在每题上。

先写 candidate 的：

> **Load-bearing risks**

再按需调用 `framework/SPECIALIZED_AUDITS.md`：

- evaluator / oracle / specification；
- public artifact / development tree / proxy；
- recipe / supervision / pretraining value；
- long-horizon / failure onset / multi-timescale；
- representation / consumer / modality；
- world-model consumer；
- industry/startup provenance；
- trend maturity / mechanism composition；
- auto-research / research-memory provenance。

如果一个题必须同时调用十几个专项 audit 才能说清：

> 通常是项目正在失控。

---

# 19. Main-story audit

普通 reviewer 应能在几十秒内回答：

- prior 到哪了？
- 为什么这个问题现在出现？
- 我们新问的 decisive unknown 是什么？
- 最小实验/方法/理论怎么回答它？
- 新 knowledge sentence 是什么？
- full paper 的 width 来自 explanatory reach 还是 benchmark 数量？

Method paper 额外问：

> 方法是否由前面的 diagnosis / constraint 自然推出？

Scientific paper 额外问：

> opposite plausible result 是否也改变理解？

Theory paper 额外问：

> 哪个 assumption 改变后旧结论真的需要重开？

Systems/deployment paper 额外问：

> resource/latency/interaction constraint 是否真实进入 formulation？

---

# 20. Formal verdict

## PILOT-AUTHORIZED

必须至少满足：

- 问题来自真实 pressure；
- nearest prior 没做掉 same decisive unknown；
- reviewer compression 后仍有清楚 delta；
- minimum pilot 能区分主要解释；
- 没有 load-bearing identifiability blocker；
- data / ground truth 可行；
- compute / engineering 可承受；
- 不需要 experiment explosion；
- 不靠 hidden compute / giant model zoo；
- full story 有现实 growth path。

## KILL

出现任一项应直接杀：

- direct prior 已回答同一 decisive unknown；
- novelty 本质是 setting change；
- terminology transfer；
- experiment 无法区分解释；
- data / evaluator / environment 不现实；
- training story 严重 recipe-dependent；
- benchmark/evaluation creep；
- 只有大规模资源才能判断真假；
- 为救题不断增加 controls/modules；
- reviewer compression 后只是成熟 parent 的普通 cell。

---

# 21. Minimum pilot

PILOT-AUTHORIZED 不等于“开始完整论文”。

pilot 只回答：

> **这个 project 值不值得继续。**

理想 pilot：

- 1 个主模型 + 必要时 1 个辅助；
- 1–3 个已有数据源；
- 一个核心 interaction / intervention / diagnostic；
- 尽量少训练；
- 不造大 benchmark；
- 不做 model zoo；
- 不做全套 ablation。

pilot 前就写 kill conditions。

触发后：

> 不救。

---

# 22. Candidate registration 模板

正式 topic 至少写：

- **Title / short question**
- **Mother question**
- **Why now**
- **Genealogy / pressure**
- **Nearest priors**
- **Reviewer compression**
- **Exact novelty boundary**
- **Competing explanation(s)**
- **Identification logic**
- **Minimum pilot**
- **Data / ground truth**
- **Compute / engineering estimate**
- **Relevant specialized audits**
- **Expected main figure**
- **Growth path if pilot survives**
- **Kill conditions**
- **Verdict**

若受 industry/startup artifact 启发，再加：

- artifact maturity；
- scale stripping；
- cheap causal echo；
- proxy fidelity；
- public matched controls。

---

# 23. Search drift reset

出现以下信号，停止出题，回去读 lineage：

- 连续 candidate 同一种死法；
- 连续题都来自同一个热点；
- 每题都长成同一种模板；
- novelty 越来越 exact-cell；
- strong paper 只被用来 kill；
- 开始只看摘要/PaperNotes；
- 不知道最近 3–8 个 nearest priors 的真实 claim；
- 为保存 candidate 不断加 control；
- method 越来越多，mother question 越来越薄；
- candidate 来源只能说“感觉没人做”。

Reset：

> 换 lineage → 恢复 parent history → 读 contrast / negative work → 再形成 seed。

不要降低 novelty bar。

---

# 24. Broad scan 已关闭

2026-09-19 的广谱 academic / industry / startup-HF calibration 已经足够厚。

现在不再默认继续无限 crawl。

重新做 broad scan 只在：

- candidate 需要 nearest-prior；
- target field 仍是薄弱 lineage；
- 新 artifact 显著改变 feasibility；
- trend 出现新的 evaluation-correction / negative-result phase；
- 用户明确要求重新校准。

当前工作单位应当是：

> **lineage → pressure → one candidate → full audit → PILOT-AUTHORIZED / KILL。**

当前正式 selected 状态见：

> `SELECTED_TOPICS.md`
