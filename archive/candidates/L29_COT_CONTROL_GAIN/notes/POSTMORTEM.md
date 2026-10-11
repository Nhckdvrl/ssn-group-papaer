# L29 Postmortem — Losing the Steering Gain

**Date:** 2026-09-13  
**Final status:** **KILL / DO NOT RECONSTRUCT**  
**Reserved kill ID:** **K190** (to be folded into `failed/KILLED_LEDGER.md` together with pending K185–K189 at the next ledger-maintenance pass)  
**Target had been:** ACL / EMNLP / NAACL Main

This note archives the scientific failure mode and reusable lessons from L29. It is not a proposal for another reconstruction.

---

## 1. What L29 asked

Mother phenomenon was strong and externally established: reasoning-oriented training and longer reasoning can sharply reduce chain-of-thought controllability.

L29 asked a narrower causal question:

> **When global CoT controllability collapses during reasoning post-training, is this mainly accumulated opportunity/distance along longer trajectories, or does training itself reduce the local causal influence of an explicit control signal on the continuation policy?**

The intended load-bearing quantity was a local constraint→policy control gain measured along one public same-base RL trajectory.

This was a legitimate question. It was killed because the required causal quantity could not be validly identified under the bounded program, not because the mother phenomenon disappeared.

---

## 2. Evidence chain

### E01 — persistent exact-word suppression

Three public checkpoints from one `allenai/Olmo-3.1-7B-RL-Zero-Math` trajectory were audited: step 100, 1400, 2800.

Two identification legs were technically feasible:

- **E01A common support:** identical observable reasoning histories cross-scored under all checkpoints; 12/20 candidate states survived the primary support gate across six questions, with early/mid/late source coverage 4/3/5. The 90% sensitivity retained seven states across five questions.
- **E01B natural state:** each checkpoint supplied its own naturally visited legal forks; retained questions were 6/12, 7/12, 7/12.
- Answer/EOS competition did not explain the result.

The load-bearing failure was the intervention.

The first neutral reminder retrieved the original prohibition and generated an apparent **−6.25 pp late–early change** in both legs. Once that invalid control was replaced by a target-matched factual control, the apparent decline vanished:

- E01A: `−2.1 → +6.3 → +7.6 pp`, late–early **+9.7 pp**, 95% CI `[−5.6, +29.2]`.
- E01B: `+4.2 → +10.7 → +3.6 pp`, late–early **+6.3 pp**, 95% CI `[−12.5, +25.0]`.

A structural third arm showed that merely mentioning the forbidden word changed its later repetition probability. A target-free anaphoric reminder still failed the required positive early-gain gate:

- E01A early gain: **−5.6 pp**.
- E01B early gain: **−4.2 pp**.

Conclusion: common-support and natural-state identification infrastructure worked, but exact-word suppression did not supply a valid positive local-control instrument. More samples would have estimated wording/lexical artifacts more precisely, not the intended controller change.

Primary record: `notes/E01_PILOT_REPORT.md`.

### E01R — one final, qualitatively different reconstruction

The final reconstruction deliberately removed every major E01 objection:

- no initial constraint;
- unconstrained natural reasoning first;
- fork only at natural reasoning boundaries;
- fresh local control pulse;
- balanced-binary **case** and **tag** families;
- both arms contained the complete identical codebook;
- only the selected Rule 1/2 label changed;
- identity/swapped semantic mappings;
- two templates;
- 48 unseen instrument-development questions;
- 240 confirmation questions untouched;
- frozen positive-effect gate before any later-checkpoint comparison.

All **48/48** development questions produced valid natural forks. Sentence/meaningful continuation rates were ~99%, and Answer/EOS events were rare and balanced.

Yet the step-100 instrument gate failed decisively:

| family | step-100 directional gain | 95% CI | verdict |
|---|---:|---:|---|
| Case | **0.00 pp** | `[0.00, 0.00]` | FAIL |
| Tag | **+1.30 pp** | `[+0.26, +2.60]` | FAIL |

Case produced no strict lowercase/uppercase success in 384 continuations; the softer lowercase-character fraction shifted only +1.23 pp. Tag produced six valid amber-selected successes, zero violet-selected successes, and one wrong amber emission under the violet arm. Both templates and both mappings stayed below the predeclared +5 pp robustness floor, far below the primary +15 pp gate.

No step-1400, step-2800, or confirmation outcome was run. No hidden-state probing, activation steering, larger sweep, or new training followed.

Primary record: `notes/E01R_REPORT.md`.

---

## 3. What the kill means scientifically

### It is **not** a stable-gain/null result

L29 did **not** establish:

> early local gain ≈ late local gain.

It established something earlier in the identification chain:

> **the bounded program never obtained a material, symmetric, interpretable positive local gain at the earliest checkpoint.**

Therefore there was no validated baseline causal quantity whose training change could answer the L29 RQ.

A hypothetical trend such as `1.3 → 0.7 → 0.2 pp` would have been noise-floor storytelling, not evidence that RL weakened a controller.

### It does **not** prove that opportunity/distance fully explains global CoT-control collapse

The experiments never reached a valid A-vs-{B,C} training comparison. The correct conclusion is identification failure for the L29 causal decomposition, not proof of the opportunity account.

### It does **not** prove that CoT is never controllable

Stronger elicitation channels remain possible: repeated instructions, few-shot demonstrations, system prompts, prompt search, learned control, or activation-level intervention. Recent Redwood follow-up work also suggests that stronger prompt elicitation can substantially improve some open-model controllability results.

However, pursuing those routes would change the project from:

> **why does reasoning training change a local controller?**

to:

> **how should controllability be elicited/evaluated/optimized?**

That is a different paper identity and violates the locked final-reconstruction gate.

---

## 4. The most important methodological lesson: first-stage instrument validity

For any future training-dynamics mechanism project of the form

> `training stage → change in causal quantity Q`,

require **before** the training comparison:

1. a concrete intervention `I` intended to move Q;
2. a development split independent of the confirmatory units;
3. a frozen minimum meaningful first-stage effect;
4. a demonstration at the reference/early checkpoint that `I` has substantial causal leverage;
5. semantic-direction symmetry where applicable;
6. robustness across at least two non-sign-selected templates/mappings when wording is part of the intervention;
7. explicit checks that the intervention does not directly inject, retrieve, or prime the measured surface event;
8. only after those pass, compare checkpoints / training stages.

If the early/reference first stage is near zero, **stop before training dynamics**. Do not treat a difference of near-zero quantities as a mechanism result.

This is the mechanism-paper analogue of the L19 resolution lesson: L19 taught us to compare expected effect size against the noise floor before expensive compute; L29 teaches us to compare **instrument leverage against the meaningful-effect floor before estimating training change**.

---

## 5. Control-design lessons from E01

### 5.1 “Neutral” text can be an active intervention

A control that mentions the original instruction can retrieve the rule even if it does not repeat the imperative. Semantic neutrality cannot be assumed from researcher intent.

**Rule:** audit control continuations directly; measure whether the control retrieves/metadiscusses the target rule.

### 5.2 If the measured event is a token/string, mentioning it is treatment

The forbidden-word experiment showed direct lexical priming: inserting the checked word into a suffix changes its future emission probability.

**Rule:** when the outcome is surface-token behavior, equalize exposure to the checked token across arms or avoid measuring an event that the intervention itself names.

### 5.3 Anaphora does not automatically fix retrieval contamination

Removing the target word but referring to “the earlier forbidden-word requirement” still did not create valid positive early leverage. Avoid assuming that target-free wording isolates semantics.

### 5.4 Balanced binary instruments are a strong diagnostic pattern

E01R's same-codebook / opposite-selection design successfully removed:

- lexical-set differences;
- neutral-arm ambiguity;
- Rule 1/Rule 2 preference via swapped mapping;
- single-template dependence.

It did not rescue L29, but it is a reusable instrument-design pattern for future causal language interventions.

---

## 6. Identification infrastructure that **did** work and should be reused

The failed paper still produced useful infrastructure:

### Common-support same-history comparison

Cross-score candidate natural prefixes under all checkpoints and admit only histories whose likelihood/surprise is inside each checkpoint's natural reference distribution. This is a useful guard against arbitrary teacher-forced OOD prefixes.

Caveat: likelihood typicality is necessary but not sufficient for semantic/state equivalence.

### Checkpoint-natural fork comparison

Let each checkpoint visit its own natural states, then fork the exact state into paired interventions. This is a strong complement to same-history comparisons because it removes cross-checkpoint teacher-forcing concerns.

### Triangulation rule

When a claim requires both same-state and natural-state interpretation, predeclare that the two legs must agree. Do not let one leg rescue the other post hoc.

### Question-level inference

Questions, not tokens or stochastic continuations, remain the statistical units; aggregate rollouts within question and bootstrap over questions.

### Artifact discipline

Keep exact model revisions, shard hashes, prompts, suffix text, random seeds, raw token IDs, pre-outcome amendments, frozen question splits, and checker code. L29's negative conclusion is credible largely because every intervention correction and stop rule is auditable.

---

## 7. Anti-resurrection fence

The following are **not** valid ways to reopen L29:

### A. Exact-word suppression with more questions / more rollouts

Killed by intervention invalidity. More N estimates the artifact better.

### B. A third/fourth wording family searching for positive local gain

This becomes instrument shopping after two bounded audits. The final reconstruction gate explicitly forbids it.

### C. Stronger repetition, few-shot, system prompts, or prompt optimization

Scientifically possible, but changes the paper into controllability elicitation/evaluator optimization. That requires a fresh independent RQ; it is not L29.

### D. Hidden-state probing or activation steering despite failed behavioral identification

Probe/steering cannot manufacture the missing behavioral estimand. Compliance-vs-Sensibility and trajectory-steering work already crowd this parent.

### E. More checkpoints / more model families

No validated early causal quantity exists. Model-zoo expansion cannot repair identification.

### F. `L29b — Initialization vs Online Control`

Do not resurrect the failure as:

> “CoT control is established at trajectory initialization rather than continuously online.”

That broad parent is now crowded by work on reasoning-level instruction adherence, dynamic mid-reasoning updates/interruptibility, recency/constraint refresh, commitment boundaries, thinking traps, and trajectory steering.

Especially relevant owners include:

- **ReasonIF: Large Reasoning Models Fail to Follow Instructions During Reasoning**, Findings ACL 2026 — reasoning-level instruction adherence and interventions.
- **Scaling Reasoning, Losing Control / MathIF**, ACL 2026 Main — reasoning/instruction trade-off and partial recovery by bringing instructions closer.
- **Are Large Reasoning Models Interruptible?**, ICML 2026 — adaptation to in-flight changes/dynamic context during reasoning.
- **Beyond the Commitment Boundary**, 2026 — sharp answer-commitment transition inside CoT.
- **Thinking Traps in Long Chain-of-Thought**, Findings ACL 2026 — prefix-dominant deadlocks and state-dependent restart/escape.
- **LLM Reasoning as Trajectories**, ACL 2026 Main — step-specific trajectory geometry plus mid-reasoning prediction/steering.

The obvious follow-up “locate the commitment boundary, inject the same update before/after it, and measure steering loss” compresses to **Interruptibility + Commitment Boundary / Thinking Traps**. It may be a useful experiment inside that literature, but it is not the fresh Main-level parent sought by this project.

### G. “Why was E01R gain near zero?” as a standalone topic

Do not convert a failed instrument-development observation into a new mother phenomenon without independent external evidence. That would be sunk-cost-driven topic generation.

---

## 8. Search/process lessons to carry forward

### Lesson 1 — A good mother phenomenon is not enough

L29 started from an unusually strong stable phenotype. The project still failed because the proposed causal decomposition required an instrument whose first stage was absent.

Selection should ask not only:

> “Can A and B be discriminated in principle?”

but also:

> **“Does the proposed intervention have an independently plausible and cheaply testable first stage?”**

### Lesson 2 — Separate `instrument-development` from `hypothesis-testing`

The E01R split of 48 development questions and 240 untouched confirmation questions was correct. Future instrument-heavy mechanism projects should adopt this by default.

### Lesson 3 — Stop at the earliest failed gate

Because E01R failed at step 100, later checkpoints and confirmation data were never touched. This avoided both wasted compute and temptation to search the training curve for a story.

### Lesson 4 — Rescue attempts need a paper-identity check

Before every reconstruction ask:

> **If this rescue succeeds, is the paper still answering the selected RQ?**

If the answer shifts from mechanism to prompting, evaluator design, benchmark design, or engineering, return to SEARCH/SELECT rather than continuing execution.

### Lesson 5 — Failure-generated hypotheses must undergo fresh owner assassination

The natural postmortem hypothesis — trajectory initialization vs online control / commitment-driven loss of redirectability — was searched independently and found crowded. A failed experiment is not privileged evidence that its nearest reinterpretation is novel.

### Lesson 6 — Keep good infrastructure, kill bad paper identities

A KILL does not imply deleting reproducible assets. Reuse common-support scoring, natural forking, balanced codebooks, and audit machinery in future projects where the scientific object is independently selected.

---

## 9. Final scientific summary

L29 began with a credible, Main-level-shaped question and a stable mother phenomenon. E01 showed that its first suppression instrument was contaminated by rule retrieval and lexical priming. E01R removed those confounds with a fresh balanced-binary intervention, but the earliest checkpoint still showed essentially no material instantaneous control response: **0.00 pp for case and +1.30 pp for tag**.

Therefore the project never established the positive early causal leverage required to interpret a later training difference as “loss of local steering gain.” The correct outcome is **KILL**, not a null-mechanism paper, not a larger sweep, and not another reconstruction.

The durable contribution of the failed project is methodological:

> **Before asking how training changes a causal mechanism, prove that your intervention actually controls the mechanism at the reference checkpoint.**

And the durable anti-sunk-cost rule is:

> **When a failed instrument suggests a neighboring scientific story, run a fresh novelty search before giving that story a candidate number.**
