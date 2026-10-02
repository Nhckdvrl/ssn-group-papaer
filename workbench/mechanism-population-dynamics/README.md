# Mechanism Population Dynamics

**Status:** **ACTIVE-EXPLORE** — 2026-10-01 human-confirmed  
**Lane:** our-taste / mechanistic interpretability / model science  
**Target:** ICML 2027 / NeurIPS 2027  
**Territory card:** [`../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md`](../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md)

## 0. Registered object

No final RQ, method, or anomaly is registered.

> **Across independently trained model instances, at what abstraction level is a mechanistic claim reproducible: exact component, causal role, algorithm/function, developmental ordering, or only behavior?**

Current state: **0 claims · 0 contributions · no method commitment · no training required at entry.**

### 当前进展（2026-10-03 05:00）
**已站住（L1）：** C01 induction 角色 / 算法在 run 间可复现、头编号不可复现；C02 第 0 层门控（31M–70M，已 stop-loss）；C03 可复现阶梯；**C04（新）：去掉 Dolma 1.7 中约 1–2% 的 Flan 指令数据，模型在“问答格式 + 多次提及 + 长段落”型反事实上下文中的采信降低 1.65 nats（留出 seed 验证，> 2 倍 seed SE），知识强度不变。**
**10/02–03 的路径：** 410M run 间仲裁差异（E13）→ 不是旋钮（E16）、不是知识（E17）、不是 run 特质（E18，跨条件一致性 0.15–0.26）→ 读领域后改问“数据配方是否设定仲裁”（DataDecide 25 配方 × 3 seed，1B）。复盘规则：先做推广性检验，再做机制。
| 实验 | 状态 / 结果 |
|---|---|
| E20 配方 vs seed（中期 15/25 配方） | 采信的配方 ICC 0.68；控制知识后 0.16；复制型条件的配方差异 ≈ 知识差异，问答格式条件的配方差异超出知识（0.36–0.82）；无剂量-反应 |
| E21 罕见事实上的 seed 分歧 | 阳性对照不过 → 不可判定 |
| E23 语料结构统计 | 完成：Flan 在 Dolma 中贡献问答格式（S3 ×2.7），不改变重复结构（S1 相同） |
| E25 Flan 效应（留出 seed） | **通过** → C04 |
| E26 因子拆解（格式 / 次数 / 论述 / 篇幅） | 10/12；描述性：Flan 主要增强“问答格式”效应，论述效应 ≈ 0 |
| E27 25 配方：问答格式密度 → 格式敏感度 | 运行中 |
| E19 / E24 | 暂停（让出 I/O） |

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

## 8. Paper-shape card（2026-10-03 05:00 草稿；agent 记录，待人否决）
- **候选论点：** 同配方的 run 共享机制角色、只在使用强度上有逐条件的 seed 噪声；而预训练数据可以系统性地改变使用方式——约 1–2% 的问答格式指令数据装入一个“问答格式下从上下文作答”的开关（格式敏感度的数据来源），可能经由对普适检索头的门控实现。
- **证据计划：** E25（Flan 对照，已过）→ E26（归因到格式）→ E27（25 配方的问答格式密度剂量）→ E28（检索头格式门控 + 因果消融）→ 时间维度（DataDecide checkpoint）。
- **最近邻：** Fouilhé 2026（问法摆动 95 个百分点，无来源）、Sclar ICLR 2024（格式敏感度，无来源）、Kim 2025（合成数据仲裁）、Goyal ICLR 2025（指令微调）、Pan 2023（任务识别）、Wu ICLR 2025（检索头）、Du ACL 2024（说服 / 易感性度量）。
- **最大风险：** 格式效应本身的 seed SD 大（c4：0.82），单配方对照功效有限；E27 若不成立，结论只剩单一 Flan 对照。

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
