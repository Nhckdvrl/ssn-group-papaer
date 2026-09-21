# chasing trends

这是 `ssn-group-papaer` 中面向**当前 AI/ML 前沿选题**的研究工作区。目标不是机械“追热点”，也不是固定做某一种论文，而是通过学界论文、工业 frontier、startup/HF artifacts 的 genealogy，理解一个问题为什么在**现在**值得问，以及能否以现实成本做成。

当前状态（2026-09-19）：

- broad literature calibration 已完成；
- 正式选题搜索已经开启；
- formal candidate 只保留 **PILOT-AUTHORIZED**，否则直接 **KILL**；
- 当前 selected：**CT03 / CT04**。

## 1. 从哪里开始

下一轮 agent 的推荐读取顺序：

1. `SEARCH_GUIDE_ZH.md` — **canonical 找题规则**。
2. `SELECTED_TOPICS.md` — 当前正式候选状态。
3. `framework/AGENT_WORKFLOW.md` — 下一轮 agent 的读写协议与 candidate 生命周期。
4. `framework/PAPER_GENEALOGY_GUIDE.md` — 如何深读 parent → successor，而不是只看摘要。
5. `framework/PARADIGM_ATLAS_ZH.md` — 已观察到的问题形成方式；只能用于校准，不能当 idea menu。
6. 与目标方向相关的证据库：
   - `academic/`
   - `industry/`
   - `startup_hf/`
7. 若出现 candidate，再读对应 `topics/CTxx_*.md` 和 dangerous nearest priors。

不要每轮从头重读全部 source ledger。先由 candidate/lineage 定向进入。

## 2. 目录结构

```
chasing trends/
├── README.md
├── SEARCH_GUIDE_ZH.md
├── SELECTED_TOPICS.md
│
├── framework/
│   ├── README.md
│   ├── AGENT_WORKFLOW.md
│   ├── PAPER_GENEALOGY_GUIDE.md
│   ├── PARADIGM_ATLAS_ZH.md
│   ├── RESEARCH_TASTE_RECALIBRATION.md
│   ├── LESSONS_FROM_SSN_TASTE.md
│   ├── CONTRAST_CASES_AND_ANTI_PATTERNS.md
│   ├── SPECIALIZED_AUDITS.md
│   └── LITERATURE_CALIBRATION_CLOSEOUT.md
│
├── academic/
│   ├── README.md
│   ├── GENEALOGIES_01.md ... GENEALOGIES_04.md
│   ├── GENEALOGY_LIBRARY_INDEX.md
│   ├── LITERATURE_MAP.md
│   └── PAPER_AUTOPSIES.md
│
├── industry/
│   ├── README.md
│   ├── FRONTIER_SCAN.md
│   ├── FRONTIER_DEEP_DIVE.md
│   ├── GENEALOGIES_01.md ... GENEALOGIES_03.md
│   └── SOURCE_LEDGER.md
│
├── startup_hf/
│   ├── README.md
│   ├── FRONTIER_DEEP_DIVE.md
│   └── GENEALOGIES_01.md ... GENEALOGIES_11_*.md
│
└── topics/
    ├── README.md
    ├── FAILED_TOPICS.md
    ├── CT01_RELEVANT_BUT_INVALID.md
    ├── CT02_IS_CONTEXT_UTILITY_RANKABLE.md
    ├── CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING.md
    └── CT04_HYBRID_ADAPTATION_STATE_DYNAMICS.md
```

目录的职责必须保持清楚：

- **根目录**：启动、规则、正式状态。
- **framework**：研究方法论与审计规则。
- **academic**：学术 lineage / autopsy / literature map。
- **industry**：大公司 technical reports、deployment pressure、source ledger。
- **startup_hf**：startup、HF、开放模型与实验 artifact genealogy。
- **topics**：正式候选 registration，不放半成品 brainstorm。

## 3. 当前 research taste

最重要的纠偏是：

> **paper shape ≠ idea genesis。**

“failure → mechanism → method → benchmark”只是其中一种论文生长路径。真正需要学习的是：

- parent literature 已经知道什么；
- 哪些 axis 已经 saturated；
- 哪个 assumption / relation / measurement unit / deployment contract 仍然挡住理解或方法；
- successor paper 为什么改变了这个 object；
- 最小 decisive evidence 是什么；
- 这个 research move 是否适合我们的数据、算力和工程条件。

因此禁止：

> 先背一个范式，再到处找能填进去的题。

正确顺序是：

> literature history → real pressure → candidate question → nearest-prior audit → identification / execution audit。

## 4. 三条证据轨道

### Academic

主要回答：

- scientific ownership；
- nearest prior；
- explanatory alternatives；
- controlled evidence；
- Main-level novelty。

### Industry

主要提供：

- frontier scale / deployment regime；
- production bottleneck；
- product knobs；
- architecture–system co-design；
- 大规模下才暴露的 failure。

原则：

> **industry generates pressure; controlled work establishes explanation。**

### Startup / HF / open artifacts

主要提供：

- matched checkpoints；
- stage pairs；
- failed artifacts；
- runnable proxy；
- cheap pilot instrument；
- 新模型/recipe 的公开 development tree。

原则：

> **artifact archaeology before GPU。**

## 5. 当前正式题目

### CT03 — Counterfactual Credit for MoE Routing

**Status:** PILOT-AUTHORIZED

核心问题：

> 能否不用昂贵地完整执行大量 alternative routes，而从正常 backward + 少量 candidate expert local forwards 中估计 unexecuted expert 的 counterfactual utility，并据此训练多层 pretrained MoE routers？

详细 registration：

> `topics/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING.md`

### CT04 — What Moves During Hybrid Adaptation? State-Dynamics Drift in Recurrent–Attention LMs

**Status:** PILOT-AUTHORIZED — exploratory identification program

核心问题：

> hybrid recurrent–attention LM 在 post-training 后真正发生变化的对象是什么：transition dynamics、recurrent-state operating point、attention↔recurrence 功能分工、局部 memory operation，还是普通 representation drift？

用 state/weight/channel crossed intervention 定位真实 bottleneck，再由诊断结果决定方法；不预设某个 LoRA 现象必须出现。

详细 registration：

> `topics/CT04_HYBRID_ADAPTATION_STATE_DYNAMICS.md`


CT01 已在 2026-09-19 re-audit 后 **KILL**；CT02 已在 2026-09-21 novelty re-audit 后 **KILL**。原因见对应 registration 与 `topics/FAILED_TOPICS.md`。

当前正式 selected 数量：**2**。

## 6. 几条不会再妥协的规则

- 不把 self-generated S/L/CT history 当正向 taste exemplar。
- 不做 “old problem + new model / benchmark / language”。
- 不因为关键词 overlap 就 kill；要检查 **same decisive unknown**。
- 不因为 paper 很强就复制它的 execution shape；scientific value 与可执行性分开评。
- benchmark 可以做 validation，但不能吞掉 scientific/method contribution。
- public checkpoint 是自然实验机会，不自动等于 controlled experiment。
- proxy 必须校准到真实 downstream consumer；“便宜”不是 fidelity。
- 热门 cluster 一旦进入 evaluation-correction / matched-budget 阶段，generic variant 默认降权。
- formal candidate 不保留模糊 SERIOUS/HOLD：审完就是 **PILOT-AUTHORIZED 或 KILL**。
- 允许整轮 **0 survivor**。

## 7. 广谱扫描已经收口

2026-09-19 的 broad calibration 已经覆盖 academic、industry、startup/HF 多条 lineage。现在**不再默认继续无限 broad crawl**。

重新扩大搜索只在以下情况触发：

- concrete candidate 需要 nearest-prior audit；
- target field 仍是薄弱 lineage；
- 新公开 artifact 显著降低 pilot 成本；
- 某个 trend 进入新的 failure / evaluation-correction 阶段；
- 用户明确要求重新校准。

接下来工作的单位应当是：

> **一条真实 lineage + 一个真实 pressure + 一个锁定 candidate。**
