# Mechanism Population Dynamics

**Status:** **ACTIVE-EXPLORE** — 2026-10-01 human-confirmed  
**Lane:** our-taste / mechanistic interpretability / model science  
**Target:** ICML 2027 / NeurIPS 2027  
**Territory card:** [`../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md`](../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md)

## 0. Registered object

No final RQ, method, or anomaly is registered.

> **Across independently trained model instances, at what abstraction level is a mechanistic claim reproducible: exact component, causal role, algorithm/function, developmental ordering, or only behavior?**

Current state: **0 claims · 0 contributions · no method commitment · no training required at entry.**

### 当前进展（2026-10-02）
**一句话：** 在 10 个独立训练的 Pythia-70M 中，induction **电路**（previous-token 瓶颈头 → K-composition 的 induction 头）在角色 / 算法层面完全可复现，头编号不可复现；但训练后期学到了一个**第 0 层的上下文门控**：上下文被罕见 token 主导时抑制复制。门控强度在配置相同的 run 之间差 25 倍，语言模型 loss 完全看不出来，且 seed 方差恰好集中在训练数据几乎没有支持的区域。

| 实验 | 结论 |
|---|---|
| R0 | 70M（11 repo）+ 160M（10 seed）+ 410M/1B/1.4B 审计；未发现错挂 / 重复权重 |
| E01 | parent（Yin & Steinhardt）的 induction 分数、出现时间、末期数值定量复现；parent 代码 4 处与论文不一致（P01）；最强因果成分是 parent 分数抓不到的 prev-token 头 |
| E02 | 10/10 seed：单一 prev-token 瓶颈 + K-composition 依赖（C01）；层位置 8/10；后期复制退化在 seed 间差 25 倍 |
| E03 | “token 特异拮抗头”解释作废（zero / resample 与 mean 不一致） |
| E04 | 第 0 层分布均值平移：正向救回 97–111%、反向在自然文本上诱导抑制；单一残差方向的救回量与退化幅度 ρ=0.96（C02） |
| E06 | 门控按罕见度 / 意外度键控，句法不触发 |
| E07 | 上下文级、阈值状门控（罕见主导时才触发），排除 token 级表示退化 |
| E08 | 语料中罕见 token 的复制规则在罕见密集上下文里命中率 50% → 12%；这类上下文只占 0.006% |
| E05 / E09 | **进行中**：160M 群体与 410M/1B/1.4B 是否也有门控（初看 160M canonical 很弱） |

主张：C01（L1）、C02（L1）；作废 1 条（E03）。下一步取决于 E09：若 160M 也有门控 / 方差集中 → 跨尺寸；否则收缩主张范围到 70M，并测第二个机制检验“方差落在数据稀疏区域”的一般性。

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

## 8. Paper-shape card

- **Current thesis:** none.
- **Current claims:** 0.
- **Likely shapes if earned:** measurement/science; failure + consequence; training-dynamics explanation; minimal intervention.
- **Forbidden final story:** “mechanisms differ across seeds”.
- **Evidence floor for mechanism language:** causal intervention + held-out prompts + population-level uncertainty + coordinate/alignment control.
- **Candidate gate:** one simple field-level conclusion that survives an independent mechanistic object or equally strong external-validity test.

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
