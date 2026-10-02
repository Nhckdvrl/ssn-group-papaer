# Mechanism Population Dynamics

**Status:** **ACTIVE-EXPLORE** — 2026-10-01 human-confirmed  
**Lane:** our-taste / mechanistic interpretability / model science  
**Target:** ICML 2027 / NeurIPS 2027  
**Territory card:** [`../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md`](../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md)

## 0. Registered object

No final RQ, method, or anomaly is registered.

> **Across independently trained model instances, at what abstraction level is a mechanistic claim reproducible: exact component, causal role, algorithm/function, developmental ordering, or only behavior?**

Current state: **0 claims · 0 contributions · no method commitment · no training required at entry.**

### 当前进展（2026-10-03 09:45）
**主线（先天 × 后天）：** 利用 DataDecide 1B 中 3 个初始化 × 25 种训练语料的完全交叉（step0 权重 sha256 核实），把机制与行为性质分解为初始化效应与数据效应。
| 主张 | 内容 | 证据 |
|---|---|---|
| **C05** | induction / previous-token / 上下文取回头的**布局由初始化决定**，数据对布局无可检测作用（数据显著的头 5–7% ≈ 假阳性率）；同初始化、两组互不重叠语料的平均布局相关 0.68–0.94；布局在训练约 2–4% 时通过对称性破缺锁定；初始注意力中无“预刻”，单头初始权重统计量也不能预测 | E35、E36、E37（描述）、E39、E40 |
| **C04** | 约 1–2% 的指令数据（Flan / FLAN）装入一个由字面模板 “Question:” 触发的“依据上下文作答”开关：只在有上下文、问答格式下起作用，陈述格式无影响 | E25、E26、E31、E32；PopQA 复现（E34）；OLMo 2 中期训练天然实验（E30，≈ 7.5 SE） |
| 行为噪声 | 初始化对行为无主效应（0/12）；同配方 run 间的行为差异是初始化 × 数据交互，逐条件、无一致方向；不存在模型级的“上下文先验” | E18、E20、E22、E36 |
**有效阴性 / 不可判定：** E21、E27（剂量规律 ρ 0.445 < 0.5）、E28（开关不在前 10 检索头）、E33（方法阳性对照未过）、E24（复制能力与复制型采信负相关 −0.68）。
**纠错：** P05（消融位置）、P06（bf16 量化）、P07（ssh 吞任务）、P08（平方和占比有偏 → 无偏方差分量，C05 已更正）。
**进行中：** E37（锁定时间，1B 正式）、E38（300M 子集复现 C05）、E30 Part B（公开模型）、E29（C04 开关的发育）。

## 1. Why inhabit this territory

The model population already exists: PolyPythias exposes independent small-model training runs and dense checkpoints, so we can study mechanism formation without paying to pretrain the population.

Naive stories are already illegal:
- PolyPythias owns population-level training variation;
- Tigges et al. show circuit/component turnover across training and scale;
- Crosscoding Through Time studies causal feature development across checkpoints;
- Polymorphism Is Rotation shows cross-seed coordinates can differ mainly by rotation and studies independent Pythia-70M seeds;
- Pre-carved Niches studies attribution-defined formation dynamics across Pythia trajectories.

Therefore this workbench cannot be “different seeds have different internals”. It must determine what survives the right controls and abstraction changes.

## 2. Primary substrate

Start with **Pythia / PolyPythia 70M**:
- canonical run + independent seeds are public;
- dense checkpoints are public;
- cheap enough for broad causal sweeps;
- interpretability tooling is mature.

Do **not** begin with 410M/1B+. Move to 160M only after the 70M instrument is stable.

## 3. First mechanism

Begin with one established, cheap object:

> **induction behavior / induction-head measurement + causal ablation**

Purpose: validate the instrument, not discover novelty.

## 4. Phase-1 execution

### R0 — artifact integrity audit
Before science:
- pin exact model repositories / revisions;
- build accepted-checkpoint manifest;
- check missing/duplicated/inconsistent checkpoints;
- record hashes/tensor sanity where feasible.

Artifact bugs go to `PAIN_LOG.md`, not automatically into the paper.

### E01 — known-mechanism reproduction
One canonical Pythia-70M trajectory:
- behavioral induction metric;
- mechanistic/head score;
- causal ablation effect;
- several checkpoints spanning pre-emergence → emergence → later training.

Goal: confirm our harness measures the parent object. No population claim yet.

### E02 — population sweep
Only after E01 succeeds:
- canonical + 9 independent 70M runs;
- ~12–20 phase/log-spaced checkpoints;
- same examples / intervention protocol;
- record behavior, mechanistic score, causal effect, component identity, emergence / turnover.

The **training run/seed** is the experimental unit. Do not average away runs.

### E03 — abstraction ladder
Before saying “mechanisms differ”, distinguish:
1. exact component identity;
2. coordinate / alignment difference;
3. causal role;
4. algorithm / functional computation;
5. developmental ordering;
6. timing.

Alignment / Procrustes-style controls are mandatory whenever raw cross-seed internal differences matter.

## 5. Useful vs low-value signals

High-value:
- matched behavior but different causal role / algorithm;
- stable algorithm with unstable components, revealing the right abstraction level;
- multiple developmental routes with different functional consequences;
- route differences associated with robustness/generalization/intervention response;
- apparent diversity disappears under alignment, showing the original mechanistic object was mis-specified.

Low-value: head-number differences, raw coordinate differences, small timing shifts, one outlier seed, “circuit figure + error bars”.

## 6. Triggered branches only

### Second mechanism
Only after E01–E03 reveal stable structure. Use another established causal object to test whether the result is induction-specific.

### Larger scale
160M only after 70M gives a clear measurement object; 410M+ only after the distinction survives.

### External model family
Only after the central distinction is clear; do not add families merely to tick L3.

### Training intervention
Only if:
> stable population structure → plausible selector/bottleneck → cheap controllable action.

Do not train models merely to complete a paper shape.

## 7. Ownership / compression

Continuously test against:
- PolyPythias;
- Tigges et al.;
- Crosscoding Through Time;
- Polymorphism Is Rotation;
- Pre-carved Niches;
- IOI developmental replication / sign-flip work;
- current causal-abstraction / mechanism-reliability papers.

Every promising lead must answer:
> Why is this not existing mechanism analysis + more seeds?

and:
> Why is this not just coordinate rotation / alignment artifact?

Strong current preprints own claims too.

## 8. Paper-shape card（2026-10-03 07:45 草稿；agent 记录，待人否决）
- **候选论点（先天 × 后天）：** 在 3 初始化 × 25 训练语料完全交叉的 75 个 1B 语言模型中，机制角色由哪个成分承担（布局）由初始化决定、几乎不受数据影响；角色的强度与使用方式由数据决定、几乎不受初始化影响；行为倾向的 run 间差异是二者交互的个体噪声。深入案例：约 1–2% 的指令数据（Flan / FLAN）装入一个由字面模板 “Question:” 触发的“依据上下文作答”开关（2 个数据集 × 2 个独立训练栈复现）。
- **证据：** C05（E35、E36）；C04（E25、E26、E31、E32、E34、E30）；同配方 seed 噪声条件特异（E18、E20）；角色普适（C01、E28）。
- **最近邻：** Pre-carved Niches（单模型、初始化决定特化）；Jordan 2023（视觉，方差来源）；Trott 2025 / Bali 2026 / Fehlauer 2025（跨 seed 的普适性）；Kim 2025 / Goyal ICLR 2025（数据与上下文依赖）；Sclar ICLR 2024 / Fouilhé 2026（格式敏感度，无来源）。
- **最大风险：** 只在 1B；初始化只有 3 个；C04 的机制未定位（E28 阴性、E33 不可判定）；跨 25 配方的剂量规律不成立（E27）。

## 9. Human-review triggers

Stop autonomous expansion and request review when:
- E01 does not reproduce the parent object;
- E02 shows stable nontrivial population structure;
- alignment removes the main effect;
- a direct new prior owns the emerging claim;
- a second mechanism / larger model is about to be added;
- any model training is proposed;
- a one-line paper thesis becomes possible;
- scientific yield looks weak after baseline + measurement residency.

## 10. Do not do

- no anomaly hunting across hundreds of tasks;
- no cherry-picked seed;
- no “head turnover = different algorithm”;
- no SAE/probe zoo before the causal baseline works;
- no new mechanism extractor at entry;
- no large-model scaling before 70M earns it;
- no training just because this is training dynamics;
- no single alignment score as the definition of mechanism equivalence;
- no fixed paper story before population measurement.

## 11. Decision record

- **2026-10-01: human selected this territory as the sole ACTIVE-EXPLORE line.**
  - strong public multi-run substrate;
  - first scientific loop is inference/causal-analysis only;
  - avoids the high up-front RL cost that paused `multi-llm-collaboration`;
  - nearest priors already define the novelty boundary, so no anomaly bet is required.

## 12. Assets

- claims: `CLAIMS.md`
- pain log: `PAIN_LOG.md`
- experiment cards/scripts: `experiments/`
- ideas only after real signals: `ideas/`
- human reviews: `logs/`
- large checkpoints/caches: local storage only (`/home/xiang/mechpop_cache/hf`, parent code `/home/xiang/mechpop_cache/icl-heads` @ c0ba06e); repo records exact source/revision/manifest
- env: `~/.venvs/mechpop` = verl-clean python (torch 2.8.0+cu128, transformers 4.57.6) + `transformer_lens==2.16.1`, `torchtyping==0.1.5` etc. installed `--no-deps` (see `scripts/run_e01.sh`)
