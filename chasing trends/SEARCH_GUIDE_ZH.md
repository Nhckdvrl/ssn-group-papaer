# chasing trends 科研选题搜索指南（Canonical）

最后系统整理：2026-09-19

这份文件是 `chasing trends/` 当前 canonical workflow。

当前状态：

> **FORMAL TOPIC SEARCH — ACTIVE**
>
> 2026-09-19 用户已明确授权正式找题。CT01 已通过第一轮 full audit，状态为 PILOT-AUTHORIZED。继续 genealogy-first；不恢复 batch brainstorming。

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



---

# 23. Industry / Academia 双轨阅读

新增于 2026-09-19。

用户明确补充：

> 不应该只看学界论文。业界 technical report / model card / system card / engineering report 经常能触及学界暂时无法触及的 scale 和 deployment regime，非常适合找 frontier pressure；但不能因为大公司做了 X，就机械复制 X。

因此正式加入第二条 literature 轨道：

## Academic track

主要用于：
- scientific question；
- explanatory decomposition；
- nearest prior；
- novelty；
- identification；
- controlled experiment；
- reviewer taste。

## Industry track

主要用于：
- frontier regime；
- scale-only phenomenon；
- product/deployment bottleneck；
- architecture-system co-design；
- real usage / traffic；
- system control variables；
- production proxy failure。

优先 artifact：
- technical report；
- model card / system card；
- production engineering paper；
- model release technical blog；
- real-usage research；
- incident/failure report。

详细规则见：
> INDUSTRY_FRONTIER_SCAN_2026-09-19.md

---

# 24. Industry insight 不等于 candidate

来自公司报告的 seed 必须先过：

## Scale-Stripping Test

删除：
- 公司名；
- GPU数；
- model size；
- proprietary traffic；
- proprietary environment；
- product feature名。

还剩下什么 relation / constraint / assumption？

如果只剩：
> “scale更大所以效果更好”，

停止。

## Cheap Causal Echo

核心 pressure 是否能在：
- open 1B–8B model；
- inference-only；
- existing dataset；
- short SFT/RL；
- offline trajectory；

中出现可控制的“小回声”？

如果不能：
> 只记 inspiration。

## Independent Academic Pressure

删除 company report以后，
公开 academic evidence能否独立说明这个 relation值得问？

如果不能：
> 不进入 formal candidate。

---

# 25. Industry artifacts 的证据地位

公司材料可以很强地支持：

> “这个 operational pressure 在 frontier deployment真实存在。”

但通常不能单独支持：

> “这个 mechanism 已经被证明。”

原因包括：
- recipe bundle；
- proprietary data；
- incomplete ablation；
- system/model confounding；
- benchmark/product framing；
- negative runs不透明。

因此：

> **Industry report generates pressure; academic/controlled work establishes explanation.**

---

# 26. Product knob watch

每轮 industry scan 特别关注：

> 哪些变量开始被多家公司显式暴露成 API / system knob？

例如当前可见：
- effort；
- routing；
- context；
- tool use；
- memory/context management；
- parallel test-time compute；
- multimodal stream；
- latency/cost mode。

一个变量被产品化说明：
> 它已经成为真实 operational object。

不说明：
> 它本身有 novelty。

正确下一问是：
> academic literature对它的 mechanism / tradeoff / control law已经知道多少？

---

# 27. Industry–Academic Bridge 输出格式

以后若一个 candidate明显受 industry 启发，必须额外写：

- **Industry observation**
- **Why academia could not easily observe it**
- **What scale/resource is stripped away**
- **Underlying pressure**
- **Academic nearest prior**
- **Cheap causal echo**
- **Why small-scale proxy is legitimate**
- **What would make the proxy invalid**
- **Full-project compute ceiling**

没有这部分：
> 不注册。



---

# 28. Startup / Hugging Face Artifact Archaeology

新增于 2026-09-19。

最近 industrial/startup/HF 扫描得到一个重要执行原则：

> **在决定“这个问题必须自己训练”之前，先搜索是否已经存在公开的 matched artifact。**

优先寻找：

- base vs instruct；
- SFT vs RL；
- pre-anneal vs post-anneal；
- midtrain stages；
- teacher vs student；
- expert vs merged student；
- BF16 vs quantized；
- high-effort vs low-effort；
- thinking vs non-thinking；
- different reasoning-language variants；
- sequential-data vs shuffled-data；
- dense vs sparse mechanism-faithful variants；
- tiny proxy vs full-scale model；
- original backbone vs continual-pretrained objective variant。

目标：

> **Artifact archaeology before GPU.**

公开 checkpoint 对比不是 causal proof。

但它可以极大降低：
- phenomenon discovery；
- boundary discovery；
- pilot cost。

---

# 29. Minimum Scale of Causal Visibility

以后审工业/大模型论文，不先问：

> 最终模型多大？

先问：

> **论文的核心 effect 最小在哪个 scale / token budget 已经可见？**

强制记录：

- final production scale；
- smallest proxy scale；
- proxy token budget；
- effect first visible at；
- second-scale confirmation；
- whether method ranking survives scale。

典型结构：

\`\`\`
0.3B proxy
→ 7B sanity check
→ production training
\`\`\`

对我们而言：
> 前两层往往比最后一层更重要。

如果核心现象只在：
- >100B；
- hundreds of billions tokens；
- production traffic；

才出现：

> inspiration only。

---

# 30. Proxy Fidelity Audit

便宜 proxy 不是因为便宜就有效。

必须回答：

1. proxy 想预测 full-scale 的什么 quantity？
2. effect direction 是否跨 scale 保持？
3. method ranking 是否跨 scale 保持？
4. mechanism metric 是否跨 scale 保持？
5. target intervention 是否处于同一 causal path？
6. proxy 是否可能因为容量/数据/优化 regime 改变而反转？
7. 最小 second-scale confirmation 是什么？

好 proxy：

> 保留 decision-relevant relation。

坏 proxy：

> 只是训练便宜。

---

# 31. Failure Provenance Gate

以后 startup/model-card/technical report 深读优先级增加一项：

> **作者是否公开了“明显合理但失败”的选择？**

强来源往往保留：

- failed architecture；
- specialization regression；
- capability floor；
- optimization instability；
- scale boundary；
- train/inference mismatch；
- deployment failure；
- bad shortcut；
- intermediate checkpoint。

强制记录：

- obvious baseline 是什么；
- 为什么一开始合理；
- 哪里失败；
- 什么 metric/trace 暴露；
- 作者有没有 mechanism；
- final method 是否直接针对 failure；
- failed artifact 能不能复现。

一个 SOTA 模型卡如果完全没有 failure provenance：

> 可作 frontier evidence；
> 但 research-taste 权重下降。

---

# 32. Operator-First Test for "Thinking / TTC / Adaptive Compute"

以后看到：

- thinking；
- extended thinking；
- test-time compute；
- adaptive compute；
- deliberation；
- iterative inference；

先删除这些术语。

重写：

\`\`\`
state X
-- operator O -->
state X'
-- evidence / score E -->
continue / stop
\`\`\`

必须回答：

1. X 是什么？
2. O 是什么？
3. O 重复的是同一 state、branch、sample，还是新 observation？
4. E 是什么？
5. stopping signal 是什么？
6. error cost 是什么？
7. compute 是每次决策支付，还是可 amortize？
8. O 会不会改变外部环境？
9. 等量 compute 为什么不直接放进 base architecture/training？

例：

### TabPFN Thinking
O：
> fit-time predictor/configuration optimization。

### τ₀-VLA
O：
> proposal → world-model consequence prediction → value → search。

### Diffusion / AuK
O：
> iterative generative transport / denoising。

### Active video
O：
> acquire additional observation。

这些不是一个 mechanism family。

---

# 33. Research Instrument Value

除了论文质量与灵感价值，再单独评：

> **这个 release 本身是不是一个好实验仪器？**

高 instrument value 的典型特征：

- 小模型；
- matched checkpoint pair；
- 同架构多 stage；
- 完整 eval code；
- training config；
- data recipe；
- logs；
- failed checkpoint；
- quantization pair；
- multiple backbone controls。

允许：

> Thesis B / Instrument A+

也允许：

> Thesis A / Instrument F。

正式 pilot 设计优先利用前者。

---

# 34. Domain Structure Placement Audit

对于 scientific/domain foundation model，不再使用模糊问题：

> “怎么注入 domain knowledge？”

必须问：

> **domain structure 应该放在哪一层？**

候选位置：

## Tokenization
例：
- DNA k-mer vs single nucleotide。

## Objective
例：
- token recovery vs latent functional prediction。

## Training distribution / prior
例：
- synthetic SCM；
- ecological/domain-specific genomic prior。

## Explicit context / metadata
例：
- acquisition geometry；
- embodiment metadata。

## Architecture
例：
- state-space sequence model；
- cross-axis tabular interaction。

## Evaluation contract
例：
- decision fidelity；
- biological invariant perturbation。

如果只是：
> 换领域数据继续预训练，

默认科学压力不足。

---

# 35. Recency Discipline

Hugging Face 当前热度不等于工作当前新。

任何 HF/startup artifact 必须记录：

- original paper/report date；
- original model-card date；
- latest checkpoint update date；
- 最近 update 是否改变 scientific thesis；
- 只是 runtime/quantization/packaging 还是新研究结果。

禁止：

> 2025 paper 因 2026 trending 被当成 2026 frontier evidence。

---

# 36. Convergence ≠ Novelty

多个公司同时采用一个 pattern 可以证明：

> operational pressure 很真实。

不证明：

> conceptual move 仍然 open。

例如：
- effort control；
- multi-teacher OPD；
- harness diversity；
- model routing；
- long-context hybrid attention；
- quantization-aware distillation；
- synthetic agent environments。

看到 convergence 后正确动作：

1. 降低 surface novelty prior；
2. 提高 pressure reality prior；
3. 往更底层找 unresolved relation。

---

# 37. Four-Axis Artifact Score

每个 startup/HF/industry artifact 内部记录四个独立维度：

### Thesis Value
是否改变真实 assumption/basic object？

### Failure-Provenance Value
是否公开 failure→diagnosis→repair？

### Instrument Value
是否给我们便宜 matched experiment？

### Proxy-Fidelity Evidence
是否证明 small proxy 能预测 larger/deployment regime？

这四项不能合成一个总分去排序政治式/论文式 winner。

用途只是：
> 决定这份材料在后续研究流程里扮演什么角色。

---

# 38. Startup/HF literature files

当前 canonical startup/HF genealogy：

- STARTUP_AND_HF_FRONTIER_DEEP_DIVE_2026-09-19.md
- STARTUP_HF_GENEALOGIES_01_2026-09-19.md
- STARTUP_HF_GENEALOGIES_02_2026-09-19.md
- STARTUP_HF_GENEALOGIES_03_2026-09-19.md
- STARTUP_HF_GENEALOGIES_04_2026-09-19.md
- STARTUP_HF_GENEALOGIES_05_2026-09-19.md
- STARTUP_HF_GENEALOGIES_06_SCIENTIFIC_FM_2026-09-19.md
- INDUSTRY_SOURCE_LEDGER_2026-09-19.md

正式找题时：

> 这些文件是 pressure/instrument/genealogy library，
> 不是 idea menu。


---

# 39. Evaluator Qualification Gate

新增于 2026-09-19，来自近期 negative/failure-provenance industrial reports 的校准。

以后凡是 candidate 依赖：
- verifier；
- executable reward；
- unit tests；
- LLM judge；
- simulator；
- hidden tests；
- success checker；

都不能默认：

> evaluator 输出 = correctness。

在正式使用前至少问：

1. **obvious non-solution test**  
   明显错误/shortcut 能否通过？

2. **near-miss mutation test**  
   在正确解附近做局部错误 mutation，evaluator 能否拒绝？

3. **shortcut audit**  
   模型能不能利用长度、格式、固定答案、visible tests、环境漏洞绕开真正任务？

4. **denominator / censoring audit**  
   timeout、cap hit、extraction failure、crash 是怎么进入统计量的？

5. **cluster / duplication audit**  
   表面很多 task 是否实际只有少数 content-distinct units？

6. **repeatability audit**  
   同一 judge/procedure 重跑是否稳定？

7. **repair requalification**  
   修 evaluator 后必须用新的 failure generator / mutation population 再测，不能只用修复时看过的案例。

8. **authority separation**  
   evaluator 在系统里到底承担：
   - feedback；
   - reward；
   - selection；
   - final certification；
   哪一种角色？

原则：

> **一个 instrument 能提供有用 feedback，不代表它有资格宣告 correctness。**

---

# 40. Development Tree ≠ Controlled Experiment

开放中间 checkpoint / 多尺度 family 是高价值 artifact，但不是天然 causal proof。

对每条 checkpoint edge 强制画 change map：

- data mixture 是否变？
- token budget 是否变？
- learning rate/schedule 是否变？
- tokenizer 是否变？
- architecture 是否变？
- objective 是否变？
- teacher 是否变？
- scaffold/harness 是否变？
- context length 是否变？
- post-training stage 是否变？

然后把 contrast 分成：

## Clean-ish contrast
主要变量少，适合现象发现/低成本机制检查。

## Bundled stage contrast
多个变量同时变，只能用于：
> 发现 phenomenon，
不能直接归因。

## Scale family
模型大小变化，但必须进一步检查：
- architecture是否同构；
- recipe是否同构；
- data/token exposure是否可比。

原则：

> **Development tree 提供自然实验机会；它本身不是实验设计。**

---

# 41. Knowledge Location Audit

以后 continual learning / memory / online adaptation 相关 seed，禁止只写：

> “模型如何记住新知识？”

必须先定位新信息存在哪里。

至少区分：

1. prompt/context；
2. retrieval/external memory；
3. recurrent / fast-weight state；
4. persistent skill/harness state；
5. adapter/LoRA bank；
6. dynamically generated weights；
7. base weights。

每种位置强制记录：

- write cost；
- read cost；
- persistence horizon；
- capacity；
- retrieval mechanism；
- interference risk；
- compositionality；
- replacement/editability；
- cross-session persistence；
- amortization benefit。

并明确区分：

> **stored ≠ reachable ≠ usable ≠ composable。**

例如一个 fact 的 local parameter trace仍在，并不等于普通 query 仍能访问它。

---

# 42. Oracle Role Separation

最近 program synthesis / agent / world-model papers显示：

> executable artifact / test / simulator 可以扮演完全不同的角色。

正式 candidate 必须标：

## Exploration oracle
agent 可查询以获得行为信息。

## Reward oracle
用于训练 reward。

## Certification oracle
定义 final correctness。

## Transition oracle
负责推进 environment state。

## Teacher oracle
生成 demonstration / labels。

一个 artifact 可以承担多个角色，但角色越多：

> leakage / reward hacking / circular evaluation 风险越高。

特别规则：

> **visible executable feedback 很适合 interaction / specification elicitation，未必适合 final correctness certification。**

---

# 43. Representation × Consumer Audit

对于 representation / foundation-model 论文，不能默认 downstream head 是透明读取器。

强制问：

1. representation 用什么 consumer/readout？
2. 线性 probe、MLP、PFN、finetune 是否会改变模型排序？
3. improvement 来自 representation，还是 downstream inference algorithm？
4. consumer 是否能从旧 representation 中提取之前没被读出的信息？
5. sample regime 改变后，consumer ranking 是否变化？

如果一个新的 downstream consumer：
> 同时改善多个已有 representation，

说明 consumer 自身是 load-bearing method component。

因此：

> **embedding benchmark ≠ representation quality 的唯一测量。**

---

# 44. Failure-Provenance Lineage

以后不只给单篇 paper 做 Failure Provenance Gate。

如果一个 lab/company 连续公开：

\`\`\`
promising result
→ boundary failure
→ cross-family failure
→ evaluator failure
→ revised protocol
\`\`\`

应把它当成一条 longitudinal research lineage 阅读。

重点问：

- claim 是怎么逐步被收窄的？
- 哪个新实验迫使解释改变？
- 作者有没有让失败结果保留在公开记录中？
- success story 是否被后续证据主动修正？

这类材料对 research taste 的价值可能高于单个最终模型。

---

# 45. Proxy-Fidelity 应优先从公开 development tree 实证，而不是口头假设

如果有：
- 0.9B → 3B → 7B → 30B；
- tiny → flash；
- base → stage checkpoints；

优先直接测：

- effect direction；
- method ranking；
- mechanism metric；
- boundary threshold；

是否随 scale/stage 保持。

不要只说：

> “我们先在小模型做，应该能 scale。”

真正的 cheap-proxy纪律是：

> **small proxy 必须被 larger public artifact 校准。**

如果公开 family 自己都出现反转：

> 立即降低该 proxy 对正式 pilot 的可信度。



---

# 46. Trend Maturity Gate

新增于 2026-09-19。

当一个热门方向开始出现以下论文时：

- 专门纠正其 evaluation protocol；
- matched-budget baseline 论文；
- held-out generalization audit；
- compatibility / boundary-condition paper；
- reproduction / negative-result paper；

把它视为：

> **这个 surface 已从 early novelty 进入 maturity / consolidation。**

此时默认停止：
> “再做一个同类 method”。

阅读重点切换为：

1. **Attribution**
   - 之前的 gain 到底来自方法，还是额外 search / compute / data / benchmark adaptation？

2. **Matched-resource control**
   - 和最简单的同预算 baseline 比是否仍成立？

3. **Generalization**
   - development task / benchmark / model 之外是否保留？

4. **Compatibility**
   - 方法是否 relative to learner / model / harness / tokenizer / deployment？

5. **Capability floor**
   - self-improvement / self-correction 机制本身是否需要足够强的 base capability？

6. **Measurement**
   - evaluator 能否区分真正 success 与 shortcut？

Harness evolution 已经是当前典型：
> represent harness → evolve harness → evaluation correction → benchmark-disjoint evolution → model–harness compatibility。

因此 generic self-harness / harness-RSI：
> 默认视为 saturated surface。

---

# 47. Auto-Research Protocol Gate

使用 AI/agent 自动搜方法时，不能把：

> “跑了很多方向”

当成 evidence。

一个可信 auto-research pipeline 至少应明确：

- optimization objective；
- capability preservation constraints；
- acceptance tolerances；
- development environments；
- held-out environments；
- search budget；
- whether held-out failures feed back into search；
- candidate provenance；
- independent review / verification；
- final integration rule。

强制原则：

> **Held-out failure 如果继续驱动修改，这个 held-out 就已经变成 development set。**

另一个原则：

> search cost、discovery cost、final method cost 三者必须分开报告。

一个最终零训练/低成本方法：
> 可能是由极昂贵的 search process发现的。

这不影响方法本身的部署价值，
但直接影响我们能不能复制其“发现过程”。

---

# 48. AI-Research Role Decomposition

以后看到：
- AI scientist；
- autonomous researcher；
- research agent；
- recursive self-improvement；

先删除标签，拆角色：

1. problem finding / problem selection；
2. method proposal；
3. experiment design；
4. implementation；
5. experiment execution；
6. result analysis；
7. evidence interpretation；
8. method selection；
9. stopping / redirect decision；
10. final scientific judgment。

只报告：
> “完成研究任务”

无法告诉我们真正自动化了哪一层。

当前 industrial telemetry反复显示：
> implementation / execution 自动化快于 selection / judgment。

因此对我们自己的科研流程也要反向利用：

> 越容易被 agent 自动化的 brute-force implementation，不应该成为选题优势的主要来源。

优先寻找：
> 一个便宜实验就能改变判断的 conceptual distinction。

---

# 49. Trend-specific Cheap Proxy 必须连接到 downstream behavior

cheap proxy 不应只是：
- embedding cosine；
- parameter norm；
- training loss；
- tiny-model accuracy。

必须说明它为什么预测最终 consumer/task behavior。

例如 compression：

\`\`\`
候选结构
→ short behavioral probe
→ expensive distillation only for survivors
\`\`\`

比：

\`\`\`
候选结构
→ representation similarity
→ assume downstream works
\`\`\`

更可信。

以后 paper 内出现 cheap proxy 时记录：

- proxy quantity；
- downstream target；
- ranking correlation；
- false-positive/false-negative candidates；
- minimum scale；
- full-scale confirmation。



---

# 50. Failure-Onset Localization Gate

新增于 2026-09-19。

如果一个 long-horizon / autoregressive / agentic 系统在很后面才出现严重失败：

不要第一反应就：
- 全程 regularize；
- 每步都加 verifier；
- 全局 constrained decoding；
- 整条 trajectory 重跑；
- 训练一个更大的 controller。

先找：

> **failure 真正从哪里开始变得不可逆/高概率？**

必须回答：

1. outcome 在哪一步开始可以被提前预测为失败？
2. onset 时哪个 observable / internal quantity 发生变化？
3. onset 前的 prefix 是否仍然有效？
4. onset 后是否存在 error cascade / bad basin？
5. 是否可以只 rollback 到 onset？
6. temporary/local intervention 是否足够越过 failure region？
7. global intervention 是否会伤害正常 case？
8. base model 是否有足够 capability 在 rollback 后恢复？

如果 causal boundary 可局部识别：

> 优先 targeted/local repair，而不是全程干预。

但如果 onset 根本不可辨识：
> 不要机械套局部修复故事。

---

# 51. Multi-Timescale Correction Gate

看到：
- fast/slow；
- local/global；
- short/long memory；
- periodic recalibration；

不能因为“双时标”听起来合理就通过。

必须先证明存在不同 error time constants。

最低要求：

1. 画 error 随 horizon 的增长；
2. 证明 local correction 解决某一高频/短期误差；
3. 证明 residual failure 仍以更慢的方式积累；
4. 证明 global/long-window correction 不需要每步运行；
5. correction frequency 与 error spectrum 有实证关系；
6. 报告 correction frequency × cost × quality frontier。

如果只剩：

> “短期和长期都重要”，

KILL 这条机制叙事。

---

# 52. Research Memory Provenance Gate

multi-agent / research-agent memory 不应只测：

> 能不能 recall 旧文本。

研究共同体需要的 memory object 至少可能包括：

- artifact；
- claim；
- parent lineage；
- negative result；
- reproduction；
- failed verification；
- conflict；
- open hypothesis；
- neglected branch；
- provenance；
- exact executable state。

审计必须包含：

## Duplicate-search rate
多个 worker 是否仍在独立重复同一实验？

## Monoculture
leader visibility 是否让所有 worker 挤进同一 branch？

## Evidence independence
多个 descendant 是否其实共享同一父结果，并非独立证据？

## Verification independence
reproduction 是否来自独立 account / fresh checkout / independent run？

## Attention effect
memory UI / ranking 是否改变探索分布？

原则：

> **research memory 是 epistemic/provenance state，不等于 conversation memory。**

---

# 53. Long-Horizon Failure Classification

以后看到：
- long context；
- long horizon；
- persistent agent；
- streaming；
- long-form generation；

先按 failure dynamics 分类，而不是按“长度”分类。

### Missing persistent state
信息本来就没被正确表示/保存。
→ representation/state redesign.

### Accumulating state error
每步小误差累积成全局 drift.
→ correction/recalibration.

### Localized bad transition
某个 onset 后进入坏 basin，后面只是连锁后果。
→ onset detection + rollback / local repair.

### Shared-knowledge failure
多个 worker/session 都不知道别人做过什么。
→ provenance/public research state.

### Resource-state failure
状态还在，但重读/维护/缓存成本爆炸。
→ compaction/cache/persistence economics.

不先做这一步：
> memory / correction / long-context method 很容易变成 module stacking。



---

# 54. Pretraining Value Decomposition Gate

新增于 2026-09-19 final frontier wave。

以后看到：

> “pretraining helps”

禁止直接当成一个 claim。

至少拆成：

1. **Peak downstream performance**
   - 最终 specialist 的 peak 能力更高吗？

2. **Sample efficiency**
   - 达到同样 performance 需要更少 task-specific data 吗？

3. **Adaptation speed**
   - 新 embodiment / domain / task 学得更快吗？

4. **Environment / object transfer**
   - 同一个已学会的行为能不能搬到没见过的 environment/object？

5. **In-context task learning**
   - 能不能靠 prompt / demonstration 定义一个新任务，而不更新 weights？

6. **Robustness / recovery**
   - broad pretraining 是否带来 OOD/self-correction？

7. **Representation reuse**
   - frozen foundation representation 能否支持轻量 action/policy head？

例：
- Figure Helix 2.5 主要给 environment transfer 的 controlled evidence；
- Skild S1 的 thesis 更接近 task ICL；
- Gemini Robotics On-Device 2 更接近 adaptation efficiency；
- Odyssey-3 更接近 frozen physical representation reuse。

这些不能合成：
> “robot pretraining有效”。

---

# 55. World-Model Consumer Contract Gate

以后出现：

- world model；
- simulator；
- video world model；
- spatial foundation model；

先写 downstream consumer。

至少区分：

## Renderer
需要：
- spatial/visual consistency；
- controllable view synthesis。

## Simulator
需要：
- action-conditioned causal dynamics；
- state persistence；
- long-horizon stability；
- realtime interaction（若用于在线训练）。

## Planner
需要：
- counterfactual ranking；
- policy/action ordering正确；
- decision-relevant transition fidelity。

## Policy representation
需要：
- frozen latent/state 能否支持轻量 control head；
- representation 对 embodiment/task 是否可复用。

## Synthetic-data engine
需要：
- generated scenario 是否提供正确 learning pressure；
- diversity / failure coverage；
- simulator bias 是否会 transfer。

强制原则：

> **world-model quality 不是一个 universal scalar。**

一个视觉更逼真的 model：
> 可能是更差的 policy trainer。

一个 simulation success-rate 与 real 不完全一致的 simulator：
> 如果 policy/checkpoint ordering 与 failure region 一致，仍可能是更好的 development instrument。

---

# 56. Modality Extension Placement Gate

当一个强 pretrained model 新增：

- speech；
- vision；
- robot action；
- audio generation；
- sensor modality；

不要只问：
> “怎么接进去？”

先判断 domain shift 需要改变模型的哪一层。

三种基本 strategy：

## Full integration
允许 backbone 深度 co-adapt。

适合：
> 新 modality 需要改变 shared computation。

风险：
> forgetting / gradient interference。

## Selective sharing / separation
只在测到 conflict 的部分分离参数。

适合：
> 部分 semantic computation可共享，但深层 acoustic/visual/action objective 冲突。

## Frozen backbone + learned interface
backbone 不动，只训 encoder / adapter / decoder / control heads。

适合：
> 必须保证既有 capability 不退化，且新 modality 能被翻译进现有 computation。

风险：
> interface ceiling。

必须记录：

1. 原 capability 哪个必须保留？
2. forgetting 是否被实测？
3. gradient conflict 是否被实测？
4. shared/frozen/separated boundary 由什么 evidence决定？
5. full integration / freezing 的 opposite baseline是什么？

---

# 57. Public Artifact Maturity Gate

Hugging Face 页面 ≠ 可做实验。

以后 artifact 分级：

## A — Runnable matched artifact now
- weights已下载；
- code可跑；
- matched control/pair存在；
- 当前就能用于pilot。

## B — Runnable but heavy / partially confounded
- 权重开放；
- 但需要大显存/API/复杂 runtime；
- 或 stage pair仍混多个变化。

## C — Detailed technical report/model card
- 技术 thesis 足够清楚；
- 但缺关键 weights/code/data。

只能：
> calibration / inspiration。

## D — Announced / "coming soon"
- roadmap；
- future weights；
- demo-only。

**不能按 A 算。**

## F — proprietary-only
- 只能提供 frontier pressure。

强制：
> ledger 必须记录当前 artifact 状态，不用未来承诺替代当前可用性。

---

# 58. Proxy-to-Consumer Fidelity Gate

大模型/工业报告经常自己使用 cheap proxy 选方向。

这是好事。

但必须问：

> proxy 到 full consumer metric 的桥在哪里？

合格证据至少一种：

1. method ordering preserved；
2. effect sign preserved；
3. mechanism variable preserved；
4. proxy change predicts downstream change；
5. proxy筛掉的 loser 在 full scale 也确实不成立。

例如：

\`\`\`
0.3B proxy
→ data-mixture ordering
→ 7B/full-scale确认
\`\`\`

或：

\`\`\`
short behavioral probe
→ compression candidate ordering
→ expensive distillation只做 survivors
\`\`\`

不够：

\`\`\`
training loss更低
→ assume agent更好
\`\`\`

Figure Helix 2.5 当前要严格区分：
- smooth robot-action-prediction scaling loss；
- 30-home strict task completion。

前者是 scale evidence；
后者是 consumer evidence。

除非两者关系被直接验证：
> 不要把 scaling-law fit 直接解释成 deployment reliability law。

---

# 59. Trend Maturity Signal — Evaluation Correction Phase

一个新 trend 如果开始连续出现：

- matched-budget evaluation；
- negative reproduction；
- evaluator audit；
- model–method compatibility failure；
- held-out transfer correction；

说明这个 surface 已进入：

> **novelty → method zoo → attribution/evaluation correction**

阶段。

此时 generic surface method 默认降权。

已经看到的例子：
- harness self-evolution；
- CoT faithfulness metrics；
- synthetic environment scaling；
- sparse attention selector target；
- evaluator/runtime correctness。

以后看到一个热词：
> 不只搜最新方法，还要主动搜 “rethink / failure / evaluation / does X really / controlled comparison / matched budget / negative result”。

通常 correction paper 比第 17 个 variant 更能告诉我们真正 open 的问题。

---

# 60. Mechanism Composition Gate

新增于 final addendum。

过去我们反复警惕：

> module stacking。

这个警惕保留，但不能退化成：

> 模块越少越科学。

像 ComposeCL 这类工作说明：
> **如果多个 mechanism 对应不同 failure source，而 interaction 本身是待检验假说，那么“组合”完全可以是 scientific object。**

以后多模块方法强制问：

1. 每个 module 对应什么独立 failure source？
2. 如果删掉 module 名，只看 causal role，是否仍然互补？
3. 是否事先有理由预测 interaction，而不是 benchmark 后讲故事？
4. 是否做过 factorial / pairwise interaction / targeted necessity test？
5. gain 是 additive、sub-additive 还是 super-additive？
6. 是否存在一个 module 只是在补另一个 module 的实现 bug？
7. full combination 是否真的需要，还是两个核心机制已足够？

### Scientific composition

\`\`\`
failure A → mechanism A
failure B → mechanism B
A/B interaction predicted
→ factorial evidence confirms synergy/boundary
\`\`\`

### Bad stacking

\`\`\`
try A+B+C+D
→ score最高
→ leave-one-out都掉一点
→ 宣称每个模块都重要
\`\`\`

原则：

> **反对的是无 causal role 的堆叠，不是反对组合本身。**

如果一个问题天然有多个独立破坏源：
> 强行要求 single knob 反而可能是假简洁。

---

# 61. Specification Source Audit

新增于 ProgramDistill / MindForge / ScienceIDE / evaluator-audit genealogy。

以后 executable / coding / agent / scientific environment 相关工作，除了问 oracle role，还必须问：

> **desired behavior / specification 到底来自哪里？**

至少区分：

1. natural-language instruction；
2. unit / hidden tests；
3. working reference program；
4. demonstration / interaction trace；
5. executable simulator；
6. numerical / physical scientific contract；
7. human/user feedback；
8. source code itself；
9. reward model / judge。

不同 specification source 决定：

- agent 需要主动 elicitation 多少；
- shortcut/leakage 风险；
- verifier authority；
- task difficulty如何定义；
- 是否能自动扩展；
- correctness是不是 extensional / behavioral / structural。

特别规则：

> **Working program 可以很好地告诉你“应该怎么表现”，但未必唯一决定“正确实现是什么”。**

所以：

\`\`\`
specification source
≠
exploration oracle
≠
reward oracle
≠
final certification
\`\`\`

角色必须分别写清。

---

# 62. Trajectory Supervision-Mask Audit

新增于 ActObs。

Agent / multimodal / sequence training 中，不再默认：

> 只有 deployment 时由模型生成的 token 才值得 supervised loss。

任何 trajectory 先画：

\`\`\`
state / observation
→ action
→ environment consequence
→ next action
\`\`\`

然后标记：

- 哪些 token/state 进 loss？
- 哪些只当 context？
- 哪些被完全 mask？
- 哪些 variable 在 downstream RL / planning 中其实需要被内部预测？

必须问：

1. mask convention 的原始理由是什么？
2. 被 mask 的 variable 是否承载 causal consequence？
3. base model 原本有没有这项 prediction ability？
4. SFT 是否在不知不觉 erase 它？
5. SFT endpoint若不变，downstream RL/search 是否会分叉？
6. auxiliary supervision 是否新增 data/compute，还是只重用已有 trajectory？
7. gradient relation 是 aligned / orthogonal / conflicting？

原则：

> **“部署时不输出”不等于“训练时不应该预测”。**

有些 target 的作用不是改善 SFT score，
而是保留 downstream optimization 所需的 internal model。

---

# 63. Multi-Rate Modality Audit

新增于 Agile-WAM / realtime multimodal genealogy。

多个 modality 被 time-aligned，不代表：

> 它们共享相同的信息变化速度。

必须记录每个 modality 的：

- sampling rate；
- intrinsic change timescale；
- event sparsity；
- prediction horizon；
- state lifetime；
- correction frequency；
- latency sensitivity。

例如：

- vision 邻帧可能高度冗余；
- tactile 在 contact 时可瞬间改变；
- audio / video frame rate不同；
- slow global geometry 与 fast local correction 不同。

因此不要机械采用：

\`\`\`
all modalities → same next-step target
\`\`\`

而要问：

> **哪个 horizon 对这个 modality 真正包含 prediction information？**

允许的 method可以是：
- different prediction offsets；
- asynchronous updates；
- hierarchical correction periods；
- modality-specific state persistence。

但必须由：
> measured temporal statistics / failure
而不是 "multi-rate sounds reasonable" 推出。

---

# 64. Broad Literature Calibration — CLOSED

用户要求本轮做完最后一波即结束 broad scan。

截至 2026-09-19：

- academic genealogy library；
- industry frontier track；
- startup/HF genealogy 01–11；
- source/evidence ledger；
- failure/contrast library；
- cheap-proxy rules；
- artifact-maturity rules；
- industry→academic bridge；

已经足够厚。

从现在起：

> **不再默认进行 broad weekly company/HF crawl。**

重新搜索 literature 只由以下事件触发：

1. 一个 concrete CT candidate 需要 nearest-prior audit；
2. 需要核 dangerous overlap；
3. 新公开 artifact 显著降低某 pilot 的成本；
4. 某个已知 trend 进入 evaluation-correction / negative-result phase；
5. 用户明确要求重新做 frontier calibration；
6. target field 目前仍是 Tier C，需要先补 lineage。

目的已经从：

> “多知道几个模型”

转成：

> **对一个具体 research seed，快速判断它来自真实 scientific pressure，还是热词/产品 feature/资源优势；并找到最便宜的 decisively falsifiable experiment。**

广泛 calibration 到此正式收口。
