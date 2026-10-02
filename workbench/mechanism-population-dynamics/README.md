# Mechanism Population Dynamics

**Status:** **ACTIVE-EXPLORE** — 2026-10-01 human-confirmed  
**Lane:** our-taste / mechanistic interpretability / model science  
**Target:** ICML 2027 / NeurIPS 2027  
**Territory card:** [`../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md`](../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md)

## 0. Registered object

No final RQ, method, or anomaly is registered.

> **Across independently trained model instances, at what abstraction level is a mechanistic claim reproducible: exact component, causal role, algorithm/function, developmental ordering, or only behavior?**

Current state: **0 claims · 0 contributions · no method commitment · no training required at entry.**

### 当前进展（2026-10-03）
**已站住（L1）：** C01 induction 电路在 10 个 70M run 中角色 / 算法可复现、头编号不可复现；C02 第 0 层上下文门控（只在 31M–70M、数据真空区，已 stop-loss）；C03 可复现阶梯（算什么 / 哪类角色算可迁移，哪个成分 / 用多强不可迁移）。
**10/02–03 的转折：** 410M 上下文-记忆仲裁 run 间差异（E13）→ 不是一维旋钮（E16）、不是知识强度（E17）、**不是 run 稳定特质**（E18：跨 12 个关系 × 问法的排名一致性 410M 0.15、160M 0.26）。复盘：应先做推广性检验再做机制（已写入规则）。
**现在的主线（领域阅读后确定）：** 真实预训练语料是否给模型设定了“复制上文 vs 回忆记忆”的**全局先验**？合成理论（Kim et al. 2025）预测会；真实语料上无人测过（条目层面频率效应已被 Yu 2023 / LMEnt / Fouilhé 2026 占）。
| 实验 | 状态 |
|---|---|
| E20 DataDecide 25 配方 × 3 seed（1B）配方 vs seed 方差分解 + 剂量-反应 | 运行中（26/75）；描述性：配方均值跨度 2.9 nats，**去掉占 Dolma 约 1–2% 的 Flan 后复制倾向 7.89 → 5.85**（default seed，待 3 seed 确认） |
| E19 410M 末期快照稳定性 | 运行中 |
| E21 run 分歧是否集中在罕见事实（Pile 频率，CPU） | 计数中 |
| E22 控制条目频率后的配方效应（全局先验，CPU） | 等 E20 |
| E23 语料重复结构（induction 可预测率）→ 配方复制先验（CPU） | 统计中 |

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

## 8. Paper-shape card（2026-10-03 草稿；agent 记录，待人否决）
- **候选论点：** 在真实预训练中，“复制上文 vs 回忆记忆”的仲裁主要由语料配方设定（全局先验，可由语料的重复 / 平行结构预测，经由共享的 induction 复制角色起作用），seed 只带来逐关系、无一致方向的噪声。
- **证据计划：** E20（配方 vs seed）→ E22（控制条目频率）→ E23（语料统计量预测）→ 机制中介（induction 强度）→ 时间 / 尺度（DataDecide checkpoint 与 4M–1B）。
- **最近邻：** Kim et al. 2025（合成）、Fouilhé 2026（31 模型、无受控语料）、LMEnt / Yu 2023（条目频率）、Chen, Luo, Pan 2026（样本 → induction 头）、Goyal ICLR 2025（指令微调中的反转）。
- **最大风险：** E20 配方效应不超过 seed 噪声；Flan 效应在 3 seed 上不复现；语料统计量与配方其他差异共线。

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
