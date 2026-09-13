# 2026-09-14 — Premise-Collision / Benefit-Reversal Search

**Target:** ACL / EMNLP / NAACL Main  
**Mode:** pressure-first provenance mining; no survivor quota.

## Why this round

ICML 2026 Outstanding Paper *The Flexibility Trap: Rethinking the Value of Arbitrary Order in Diffusion Language Models* provides a useful provenance generator. Its transferable move is not `find a surprising anomaly`. It places two established claims in tension:

1. masked/diffusion LM arbitrary-order decoding is useful because it can defer difficult/high-uncertainty tokens;
2. reasoning work shows that high-entropy/forking tokens are disproportionately important for exploration and trajectory branching;
3. therefore the mechanism that creates flexibility may remove exactly the uncertainty required for reasoning exploration.

The paper then uses a claim-matched observable (Pass@k / solution-set coverage), a continuous arbitrariness knob, localization to deferred fork tokens, and a mechanism-derived simplification of RL rollouts.

### Generator added to the search process

> **Premise Collision / Benefit Reversal**: `Prior A says X is beneficial because it causes/avoids M; Prior B establishes that M is necessary, harmful, or qualitatively different under objective Y; ask what happens when X is used for Y.`

This is a first-class generator only under additional gates:

- both premises must already be credible independently;
- the collision must create a **third scientific quantity / conditional law**, not merely `Prior A + Prior B`;
- there must be an observable directly matched to that third quantity;
- ideally there is a natural continuous knob or matched intervention;
- the resulting question must not be the obvious next extension already telegraphed by either parent group;
- owner search is on the scientific inference and decisive operation, not on title keywords.

## Current portfolio calibration

For the current new-topic search, paper-level Selection PASS or higher currently includes **L08, L33, L34**. L33 and L34 have bounded E01 authorizations. L08 is reopened at SERIOUS / paper-level Selection PASS but has no new compute authorization. L35 remains SERIOUS / HOLD on resolution-cost and is not counted as passed. Approved paper mainline remains NONE.

## Collision batch: investigated and killed

### 1. Resource-rational compression × garden-path reanalysis — NO

Pressure: limited memory favors compressed/categorical context representations, while successful garden-path reanalysis requires preserving competing parses until late evidence arrives.

Kill: 2026 work on **Parse Multiplicity Mismatch** already places active-parse multiplicity directly on the garden-path causal path. A continuous-precision version is technically different but is too natural a same-object successor; successful outcomes are too autocomplete.

### 2. Tool use bypasses hard subproblems × internal reasoning learning — NO

Pressure: tools reduce the need to solve hard internal subproblems; difficult transitions can be the learning signal needed for reasoning competence.

Kill: 2026 tool-integrated reasoning work already studies reasoning atrophy / dependence closely enough that the bridge has weak ownership.

### 3. Easy-to-hard curriculum × high-value difficult/high-entropy examples — NO

Pressure: curriculum learning stabilizes optimization by starting easy; reasoning/RL work identifies difficult/high-entropy cases as disproportionately informative.

Kill: 2026 curriculum and RL reasoning literature already densely owns confidence/difficulty scheduling and hard-example benefits.

### 4. PRM / beam pruning × later recovery from locally flawed steps — NO

Pressure: process pruning removes low-scoring partial trajectories for efficiency; reasoning trajectories can recover after locally flawed-looking steps.

Kill: direct premature-pruning / flawed-step-recovery work exists. No independent third quantity remained.

### 5. Single canonical reasoning target × solution-space diversity — NO

Pressure: stable/correct distillation targets simplify learning; reasoning potential benefits from path diversity.

Kill: Reasoning Path Divergence and 2025–2026 multi-path reasoning/distillation papers already own the central interaction. Also too close to L35.

### 6. KV-cache/token pruning by observed importance × future-query importance — NO

Pressure: efficient cache methods retain tokens important to past/current attention; future reasoning may rely on tokens not yet queried.

Kill: 2026 future-attention / information-aware KV compression work directly distinguishes near-context attention importance from distant-future predictive uncertainty and formalizes query-agnostic risk.

### 7. Stated-value alignment × revealed/contextual action — NO CURRENT FORM

Pressure: value induction/preference optimization can shift stated preferences, while EMNLP 2025 *Value–Action Gap* shows stated and revealed values diverge.

Potential RQ was whether value post-training learns a cross-context action policy or primarily a verbalized value stance.

Kill: 2026 value-induction, value-alignment-tax, stated/revealed-value adaptation, and finetuning studies make `training view × evaluation view` an obvious combination rather than a sufficiently independent inference.

### 8. Relaxed speculative verification × high-entropy reasoning forks — NO

Pressure: speculative decoding gains speed by accepting approximations in low-margin/uncertain regions; those regions can contain reasoning forks.

Kill: entropy-aware speculative decoding already explicitly connects speculative acceptance with reasoning-sensitive uncertainty. Too close to *Flexibility Trap* in both ingredients and operation.

### 9. Confidence/answer-stability early exit × later self-correction — NO

Pressure: early exit saves test-time compute when an answer appears stable; reasoning can revise an apparently stable answer later.

Kill: 2026 early-exit and answer-stability work directly identifies premature termination before later correction.

### 10. Stronger teacher / more accurate CoT × student learnability — NO

Pressure: stronger teachers produce more correct reasoning traces; capacity-gap literature says stronger teachers can be worse teachers.

Kill: ACL 2025 CoT-distillation work directly finds stronger teachers are not always better and connects the effect to reasoning complexity/diversity; 2026 work further develops this.

### 11. Self-consistency majority vote × correlated/homogeneous reasoning errors — NO

Pressure: self-consistency assumes aggregation of diverse paths; correlated modes can turn majority voting into amplification of a shared mistake.

Kill: 2024–2026 self-consistency work already studies minority information, correlated/incorrect majorities, and a 2026 preregistered negative result shows majority voting can hurt many hard-science items when confidence does not track correctness.

### 12. Preference-data cleaning / high-consensus filtering × informative boundary disagreement — NO

Pressure: alignment pipelines treat disagreement as noise and favor clean labels; disagreement can encode subjectivity/underspecification rather than annotation error.

Kill: ICML 2025 *Diverging Preferences* and 2026 disagreement-aware preference work directly own this premise reversal.

## Strongest surviving seed — Why did the beam-search curse disappear?

**Status:** **SERIOUS SEED — INSTRUMENT-SEMANTICS AUDIT FIRST — NOT NUMBERED / NO COMPUTE AUTHORIZED**

### Established premise A: the old law

Classic NMT work established the **beam-search curse**: increasing beam width beyond a modest value can lower translation quality even though search is finding higher-scoring model outputs. Length/termination pathology and model-score/quality mismatch are major ingredients in the classical explanations.

### Established premise B: modern empirical reversal

TACL 2025 *Salute the Classic: Revisiting Challenges of Machine Translation in the Age of LLMs* reports that the classic beam-search challenge largely does **not** appear for their translation LLM setup. Across beam widths 1/2/4/5/8/12, BLEU/COMET stay roughly flat or improve rather than collapse.

### Established premise C: the supposed cause did not disappear

NeurIPS 2025 *Calibrating Translation Decoding with Quality Estimation on LLMs* shows that sequence likelihood is still poorly aligned with translation quality even for specialized translation LLMs; explicitly improving likelihood–quality calibration improves decoding.

### Collision

> **If likelihood–quality misalignment is still present, why does wider beam search no longer amplify it into the classic beam-search curse?**

The weak question is `does beam search still work?`; TACL 2025 owns that. The useful third quantity is:

> **search-exposed / beam-frontier misalignment** — global likelihood–quality misalignment need not imply that the newly reachable high-scoring hypotheses exposed as beam width increases are systematically worse.

This yields a possible revised law:

> **Global likelihood–quality misalignment is not sufficient for the beam-search curse; the curse requires adverse misalignment on the search frontier (potentially together with termination/length bias).**

### Decisive observable

For each source sentence and beam width `B`:

- record all hypotheses entering / becoming competitive on the beam frontier;
- record raw sequence likelihood, length-normalized score, EOS/termination behavior, and independent translation quality;
- separate **global score–quality correlation** from **frontier/local score–quality correlation**;
- inspect the *incremental candidates exposed* when increasing `B`;
- ask whether bad but high-scoring candidates accumulate with beam width in classical NMT but not modern translation LLMs.

Beam width is a natural continuous knob. The goal is not another BLEU-vs-B plot but an explanation of when searching harder exposes model misspecification.

### First kill gate

Before full Selection, reproduce the TACL phenomenon with **explicitly frozen search semantics**:

- raw vs length-normalized sequence score;
- `length_penalty`;
- EOS token / forced EOS handling;
- early stopping;
- maximum length;
- identical tokenization/post-processing.

The public LLM4MT materials confirm beam inference but do not currently expose enough of the original generation script/config to certify these semantics. If the claimed disappearance of the curse depends on modern API defaults rather than the model regime, **KILL as an inference-implementation artifact**.

If the no-curse result survives classical scoring semantics, promote to full Selection and run a bounded owner/identification audit around `global misalignment vs beam-frontier misalignment`.

## Search lesson from this round

The premise-collision generator is productive, but only if it is used **across scientific clusters**. Staying inside the 2026 `entropy/diversity/reasoning` vocabulary recreates other groups' obvious next projects. The most promising collision this round came from crossing an old decoding law (beam-search curse) with two modern MT results that were not written as a single question.

Next search should continue across independent pools: training/post-training dynamics, model-computation/representation, semantic/pragmatic inference, alignment/action, and old empirical laws whose mechanism may have migrated in modern foundation models.