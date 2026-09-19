# chasing trends 科研选题搜索指南（Canonical）

最后系统整理：2026-09-19

这份文件是 `chasing trends/` 当前 canonical workflow。

当前状态：

> **LITERATURE / TASTE CALIBRATION**
>
> 用户通过之前，不开始正式 CT01。

---

# 1. 目标不是“追某一种论文模板”

本目录名字叫 chasing trends，但目标不是：

> 看到哪个方向热门，就找一个 gap。

也不是：

> 固定做 failure → mechanism → method → benchmark。

真正目标是：

> **通过大量真实强论文和它们的 related-work genealogy，训练“问题是怎么从 literature 中被看见的”能力。**

方法论文、机制论文、理论论文、empirical phenomenon paper、training paper、generation paper 都可以成为正向学习对象。

关键不是论文最后有没有 method。

关键是：

> **它为什么不是一个凭空 brainstorm 出来的 idea？**

---

# 2. 会议与阅读 provenance

优先持续扫描：

- ACL / EMNLP / NAACL
- ICLR / ICML / NeurIPS
- AAAI
- CVPR / ICCV / ECCV
- TACL

主动扩展：

- image / video generation
- multimodal / VLM
- speech / audio
- robotics / embodied
- optimization / learning theory
- control / dynamical systems
- statistics / information theory
- cognitive science / neuroscience

PaperNotes：

> **用于 breadth discovery，不作为最终 novelty judge。**

core paper / dangerous prior：

> **必须回原文。**

---

# 3. 两层阅读制度

以后每一轮必须同时有：

## Layer A — Breadth map

目标：

> 知道 field 正在沿哪些轴移动。

不需要每篇全文。

可以用：

- PaperNotes
- conference pages
- title / abstract
- citation graph
- author/project page

每个重点 area 至少扫几十篇。

记录：

- recurring method families
- repeated failure claims
- emerging terminology
- standard benchmarks
- dominant assumptions
- suddenly crowded axes
- cross-field analogies worth deep reading

Breadth 不是为了直接出题。

---

## Layer B — Deep genealogy

真正决定 taste。

每轮选 8–15 篇 core paper 深读；
长期累积到 20+。

每篇至少读：

- Introduction
- Related Work
- problem setup
- decisive experiment / theorem
- method derivation
- main ablation / boundary
- Discussion / Limitations

并向下追：

> 3–8 篇 immediate parent / sibling。

输出必须是：

> genealogy card

而不是 abstract summary。

详见：

`PAPER_GENEALOGY_GUIDE.md`

---

# 4. 每个 lineage 要回答的不是“gap 在哪里”

先画：

## Parent problem

field 真正解决的是什么？

## Dominant decomposition

大家默认怎么拆这个问题？

## Saturated axes

已经被大量论文扫过的方向。

## Frozen axes

大家一直固定不动的 variable / assumption。

## Coupled quantities

总被同时改变，因而无法知道哪个起作用。

## Missing relations

两个成熟 sub-literature 之间没有解释清楚的关系。

## Premise shifts

过去 1–2 年 architecture / training / inference / deployment 到底改变了什么 load-bearing premise？

## Practical constraints

真实使用中什么变量重要，但 paper formulation 没把它作为 object？

## Contradictory evidence

哪些 paper 的结果不能被一个简单 explanation 同时解释？

---

# 5. 当前已观察到的 idea-growth moves

以下只是 observation library。

**禁止把它们当 checklist 去填空。**

已经看到：

- objective/component decomposition
- deployment variable → policy state
- fragmented methods → unified design space
- coarse outcome → finer causal/event unit
- token-level → step/process-level coordinate
- information addition → information removal
- invariant/property search
- theorem assumption audit
- artificial evidence regime → natural regime
- changed premise
- hidden confound in popular proxy
- relative objective → absolute degradation
- resource allocation mismatch
- bottleneck migration
- structural constraint → workaround
- two literatures conflict → hidden common quantity

下一轮可以出现完全新的 move。

---

# 6. 强论文应该怎样被“往下推”

用户要求的不只是：

> 这篇 paper 为什么好。

而是：

> **它是从哪里来的。**

所以每个 core paper 都要往下追：

```
new paper
↑
nearest sibling A
nearest sibling B
nearest sibling C
↑
parent question / method family
↑
older premise / theory / task definition
```

对每一层问：

> 新 paper 相比上一层改了哪个 object？
>
> 是加了新方法，还是重新定义了问题？
>
> 是哪个 related work 的 limitation 真正 load-bearing？
>
> 哪个 limitation 只是 paper writing rhetoric？
>
> 如果我是作者，在前一篇 paper 刚发表时，什么 observation 能让我想到下一步？

---

# 7. 强制区分四种“follow-up”

## Type A — 空格 follow-up

> previous work 没测 model X / language Y / benchmark Z。

默认 KILL。

## Type B — boundary follow-up

> prior claim 在一个关键 regime 下可能不成立。

可能成立，但必须解释：

> 为什么这个 boundary 会改变原结论的 scientific interpretation。

## Type C — explanatory follow-up

> prior phenomenon 已知，但 competing explanation 未区分。

如果不同 explanation 会改变我们对系统的理解 / 方法设计，可以成立。

## Type D — premise-changing successor

> 系统某个 load-bearing premise 已改变，因此旧问题必须重新定义。

高价值。

---

# 8. 不再使用“先生成 20 个 idea”

正式 topic search 开启后也不这样做。

正确流程：

> **先选 lineage，不选题。**

然后：

1. breadth scan
2. deep-read core papers
3. draw genealogy
4. mark scientific / algorithmic pressure
5. collect unresolved relations
6. only then form seeds

一个 seed 必须能回答：

> **它具体从哪个 literature tension / assumption / relation 长出来？**

如果来源是：

> “我想到一个挺酷的实验”

默认低优先级。

---

# 9. Topic formation 以后仍要保留旧审计

虽然我们不再固定 paper archetype，但旧 `ssn-taste` 的以下 gate 仍然保留。

## Nearest-prior audit

same decisive unknown / same algorithmic insight 是否已经被做？

## Reviewer compression

reviewer 最危险会把它压成什么？

## Data audit

数据和 ground truth 是否现实？

## Compute audit

核心真假能否低成本判断？

## Recipe audit

如果涉及 training dynamics，结论是不是 optimizer / budget biography？

## Experiment explosion

如果需要巨大 factorial 才能说清楚：

> KILL。

## Anti-resurrection

旧 failed topic 换名不能复活。

---

# 10. 但不再要求所有题满足同一个 scientific-question rubric

不同 paper genealogy 有不同生死标准。

---

## A. Scientific / mechanistic paper

重点：

- question 独立成立；
- explanatory decomposition 真改变；
- causal evidence 足够；
- parent overlap 合理。

---

## B. Method paper

重点：

- problem pressure 真实；
- method 不 arbitrary；
- prior method 为什么解决不了说得清；
- gain 不是 hidden compute；
- strong baseline；
- ablation / boundary 对 claim。

不强求：

> null result 也能 Main。

---

## C. Theory paper

重点：

- old result 的 assumption audit；
- theorem 真的改变理解；
- empirical relevance / bridge 足够时更强。

---

## D. Empirical phenomenon / limits paper

重点：

- phenomenon 改变一个 community inference；
- prior evidence 不能直接推出；
- setting 不是 gimmick；
- result 有 downstream meaning。

不强求 method。

---

## E. Systems / deployment-driven paper

重点：

- constraint 真实；
- prior formulation 忽略它；
- algorithm genuinely conditions/adapts to it；
- compute/latency protocol 公平。

---

# 11. Cross-domain 迁移

不要从：

> “CV 有方法 X”

出发。

正确顺序：

## 1. Read the genealogy

CV paper 为什么会出现？

## 2. Remove nouns

例如 TORS 不是：

> curvature + torsion。

真正结构可能是：

> 多类 acceleration method 独立发展
> → 统一 design space
> → matched attribution
> → 发现资源分配位置比更新公式更重要
> → 用 trajectory geometry 定义非均匀 schedule。

## 3. Ask whether the same pressure independently exists elsewhere

如果 LLM 中没有：

> 多个方法争同一 compute budget、但 component attribution 不清，

就不要迁移。

## 4. Derive distinct prediction

没有 prediction，就只是 analogy。

---

# 12. Sasano taste 仍然是硬约束

每轮继续抽样 Sasano 的真实 feedback。

稳定原则：

- reviewer 不会帮你找亮点；
- 论文必须一读就知道在干什么；
- Introduction 要“納得できる + 面白い”；
- method / experiments 每一步为什么做必须能解释；
- novelty 不能只是 new setting；
- 一个相似 prior 不自动 kill，但必须有实际 knowledge delta；
- finding 不必符合原 hypothesis；
- Main body 应能承载主要逻辑，不依赖巨大 appendix 才成立。

这套 taste 与“多种 genealogy”并不冲突。

反而意味着：

> genealogy 最后必须能被压成一个 reviewer 听得懂的 story。

---

# 13. Literature drift reset

出现以下信号，立刻停止出题并继续读：

- 连续 candidate 都来自 reasoning RL；
- 连续 candidate 都是某种固定 template；
- 开始看到任何 paper 都想套“failure → method”；
- 每个 idea 都是某篇 recent paper 的 future work；
- related work 只用于 kill，没有用于理解 idea growth；
- 开始只看 abstract / PaperNotes；
- 不知道 nearest 3–8 篇 prior 的真实 claim；
- 不知道 field 哪些 axis 已经 saturated；
- candidate 的来源说不清，只能说“感觉没人做”。

Reset：

> 换 lineage；
> 深读一组 paper family；
> 画 genealogy；
> 再回来。

---

# 14. 正式开始 candidate search 后的流程

只有用户明确通过 framework 后执行。

## Phase 0 — Restore repo

读：

- README
- RESEARCH_TASTE_RECALIBRATION
- PAPER_GENEALOGY_GUIDE
- latest autopsies
- failed ledger
- recent commits

## Phase 1 — Choose 3–5 lineages

不要先想题。

## Phase 2 — Breadth scan

每条 lineage 扫近期 paper landscape。

## Phase 3 — Deep genealogy

每条至少 2–4 篇 core paper + parents。

## Phase 4 — Pressure ledger

只记录：

- unresolved relation
- hidden assumption
- changed premise
- unexplained asymmetry
- wrong unit
- proxy/confound
- practical constraint
- contradictory findings
- new identification opportunity

## Phase 5 — Seed formation

把一个 pressure 变成 question。

## Phase 6 — Lock strongest seed

不要 dump 20 个。

## Phase 7 — Deep prior audit

真正读危险 prior。

## Phase 8 — Experiment / method / theorem path

根据 seed 自己的 genealogy 决定 paper 类型。

不能先规定一定要有 method。

## Phase 9 — Data / compute / execution audit

现实性一票否决。

## Phase 10 — Main-story audit

普通 reviewer 能否理解：

> prior 到哪；
> 为什么还缺这一问；
> 我们新知道/新做到什么。

## Phase 11 — Verdict

只有：

> PILOT-AUTHORIZED — register CTxx

或：

> KILL

允许 0 survivor。

---

# 15. 在开始 CT01 前仍缺什么

当前第一批 genealogy 已经覆盖：

- reasoning failure
- RLVR learning-signal decomposition
- test-time search
- ICL mechanism
- Transformer theory
- CoT faithfulness
- diffusion fast sampling
- model merging

但还不够。

继续补：

- EMNLP / NAACL 普通强 Main
- pretraining / SFT / distillation
- architecture / inductive bias
- generation beyond diffusion
- multimodal / VLM
- speech/audio
- at least one robotics/embodied lineage
- optimization / learning theory
- negative-results / limitations papers
- papers without a new method
- papers with strong methods but weak scientific stories as contrast
- same lineage 3–8 paper sequences

这一步完成到足够厚，再找题。

---

# 16. 最终原则

不要问：

> “我们这次要找哪一种题？”

要问：

> **“这个 literature 是怎么走到今天的？”**
>
> **“最近强论文每次到底改变了哪个基本 object / assumption / relation？”**
>
> **“哪些方向已经只是加法，哪些地方仍存在真正的 explanatory / algorithmic pressure？”**
>
> **“如果我是作者，在上一代 paper 刚出来时，什么证据会让我意识到下一问值得做？”**

我们要学的是：

> **research moves**

不是：

> **research templates**。


---

# 17. Literature calibration 不允许“做一批就收工”

新增于 2026-09-19。

用户明确纠正：

> **“你都做厚啊，没必要这么早就跳出来。”**

因此以后 framework calibration不能：

> 读4–5条lineage → 得到一个漂亮meta-pattern → 马上开始找题。

至少要同时具备：

1. **Breadth**
   - 多会议；
   - 多领域；
   - 不只 reasoning/LLM。

2. **Depth**
   - 核心lineage连续 parent→successor；
   - 不是孤立paper。

3. **Contrast**
   - strong but compute-heavy；
   - incremental accepted work；
   - measurement-only work；
   - weak story / module stack；
   - negative-result contrast。

4. **Cross-lineage comparison**
   - 同样叫 adaptive/selective/latent/unified/mismatch，
   - underlying pressure是否其实不同。

5. **Execution transfer**
   - strong paper是否根本依赖我们没有的资源。

6. **Saturation**
   - 哪个 conceptual move最近6–12个月已经形成cluster。

7. **Blind spots**
   - 明确哪些area只是breadth scan，不能拿来直接出题。

当前对应文件：
- LONGITUDINAL_GENEALOGIES_01_2026-09-19.md
- LONGITUDINAL_GENEALOGIES_02_2026-09-19.md
- LONGITUDINAL_GENEALOGIES_03_2026-09-19.md
- LONGITUDINAL_GENEALOGIES_04_2026-09-19.md
- GENEALOGY_LIBRARY_INDEX_2026-09-19.md
- CONTRAST_CASES_AND_ANTI_PATTERNS_2026-09-19.md

---

# 18. Genealogy evidence tags

以后写 lineage relation：

## DIRECT
论文明确引用/挑战/扩展 parent。

## FIELD
同一literature family；只说后一篇出现时前一篇已经构成field context。

## RECONSTRUCTED
为了理解frontier做的概念重构。

禁止：
> 把RECONSTRUCTED写成作者真实idea来源。

这是防止 hindsight bias 的硬规则。

---

# 19. Same surface / different genealogy gate

正式候选以后，任何跨域idea如果使用以下词：

- adaptive
- selective
- dynamic
- latent
- unified
- mismatch
- bottleneck
- invariant
- curriculum
- sparse

先做一次去词审计。

必须回答：

1. state是什么？
2. action/operation是什么？
3. objective是什么？
4. old assumption是什么？
5. decisive evidence是什么？
6. method为什么由evidence推出？
7. source domain和target domain的这些结构是否真的同构？

如果答不清：

> 只是surface analogy，KILL。

---

# 20. Contrast gate

正式候选以后必须额外问：

> nearest accepted papers之所以成立，有多少来自我们无法复制的resource shape？

包括：

- 1000+ model sweep；
- foundation model from-scratch；
- hundreds of billions training tokens；
- huge synthetic/real speech data；
- proprietary evaluation；
- multi-robot data；
- large human study。

如果核心claim只能靠这些资源确认：

> 即使idea漂亮，也不PILOT-AUTHORIZED。

---

# 21. Literature depth tiers

## Tier A
连续追了多篇parent/successor，并读过关键problem/evidence。

可以作为：
> candidate search source。

## Tier B
有multi-paper reconstruction，但部分parent还需补。

可以作为：
> pressure source；candidate出现时必须继续deep audit。

## Tier C
主要breadth scan。

只能用于：
> 发现值得读的lineage。

**不得直接从Tier C生成formal candidate。**

如果seed落在Tier C：

> 先升级lineage depth，再判断seed。

---

# 22. 什么时候才从 literature calibration 切到正式找题

不是：
> “我们已经总结出几个pattern”。

切换条件：

1. 用户明确要求开始；
2. 至少有多个Tier A lineage；
3. 当前阅读不再被单一热点支配；
4. contrast library已建立；
5. 能识别近期cluster saturation；
6. 能区分intellectual quality与execution suitability；
7. 对candidate最可能落入的area有真实parent knowledge。

即使满足1–7：

> 仍允许0 survivor。

