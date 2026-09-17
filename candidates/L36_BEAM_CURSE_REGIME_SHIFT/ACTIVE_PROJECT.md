# L36 — Active Reframed Main Candidate: Mode-Seeking Stability Transition

**Decision date:** 2026-09-17  
**Status:** **ACTIVE — REFRAMED MAIN CANDIDATE / E05 GATE REQUIRED**  
**Primary target:** ACL / EMNLP / NAACL Main  
**Fallback:** narrower termination-channel paper only if the sequence-landscape story fails  

## 1. Core research question

> **Why does progressively mode-seeking search degrade classical sequence models, while many modern post-trained LMs appear more stable, and what structural change in the full sequence-level probability landscape accounts for that transition?**

Same-lineage version:

> **Within a fixed autoregressive lineage, how do Base → SFT → preference/RL stages reorganize the relation among sequence mode, typical probability mass, multi-token search path, and task utility?**

The scientific object is **not EOS** and is **not beam search tuning**. Beam search is one way of moving toward high-probability modes. The object is the relation between the learned full-sequence distribution and the utility of increasingly mode-like outputs.

## 2. Why the previous identity was too narrow

The previous Main-candidate identity was:

> post-training learns a format-conditional generation boundary whose stop-event geometry controls a classical termination pathology.

That statement remains useful for one channel, but it is too narrow as a general explanation of beam-search degradation.

Beam search approximately optimizes a full sequence score:

`log p(y|x) = sum_t log p(y_t | x, y_<t)`.

The empty hypothesis `[EOS]` is only one degenerate full sequence. First-step stop probability/rank is therefore a valid instrument for the **empty-termination channel**, but not a theory of general mode-seeking degradation.

Our own Olmo results already falsify the universal-EOS explanation: Olmo base loses large amounts of BLEU under wider search while maintaining zero empty outputs and near-reference length, through generic/copy-like high-probability outputs. Thus:

> **termination collapse is one special case of mode-seeking pathology.**

The E02 controlled SFT experiment is also demoted to its exact ownership:

> it causally shows that a surface-conditioned `<END>` placement policy can be learned under matched training.

It does **not** by itself establish that small SFT learns an abstract, task-general concept of response completeness.

## 3. Closest ownership and novelty boundary

Existing work already owns the following:

- **Murray & Chiang (2018):** brevity/length bias and large-beam NMT degradation;
- **Cohen & Beck (2019):** multi-token search discrepancy / later probability compensation as a general beam-degradation mechanism;
- **Stahlberg & Byrne (2019):** exact NMT modes are often empty; search errors can protect against model errors;
- **Eikema & Aziz (2020):** mode-vs-distribution-mass mismatch in NMT;
- **Shi, Xiao & Knight (2020):** empty preference can arise from high EOS probability or low cumulative probability of adequate full sequences;
- **Kulikov et al. (2022):** sequence-level premature termination / oversmoothing across all prefixes, EOS rank/probability, training regularization, and its beam consequences;
- **Meister et al. (2022):** generic probability-quality paradox in language generation;
- **Stahlberg et al. (ACL 2022):** uncertainty, search errors, exact-search tractability, and spread of probability mass around the mode;
- **Pang et al. (TACL 2025):** the classical beam-search challenge appears much weaker in LLM-MT;
- **Wu, Lei & Monz (NeurIPS 2025):** likelihood-quality alignment in LLM-MT can be explicitly trained to improve MAP/beam decoding;
- **Springer et al. (ICML 2026):** post-training can cause semantic diversity/mode collapse;
- **recent sequence-probability/correctness work:** generic `higher probability != higher correctness` is already occupied.

Therefore none of these can be the L36 paper identity:

- “EOS matters”;
- “beam modes can be bad”;
- “likelihood and quality are misaligned”;
- “post-training changes entropy/diversity”;
- “format changes stopping.”

The remaining plausible novelty is a **transition question**:

> **How does the stability of mode-seeking decoding itself change across classical models and modern post-training stages, and what full-sequence structural transition explains that change?**

This is a training-stage / regime-transition problem, not a static likelihood-quality-correlation problem.

## 4. Current evidence that survives the reframe

### E0 — matched RAW classic-vs-modern endpoint contrast

Under raw cumulative sequence scoring, classic WMT19 NMT exhibits severe large-beam shortening/empty collapse while Gemma-3-12B-IT remains stable over the tested range. This rules out the easiest decoder-normalization explanation.

### E1 — termination channel is real but partial

Classic systems have much more competitive immediate-stop hypotheses than modern in-format LLMs, and stop-logit interventions can induce a termination pathology in the modern model. Keep this as a **channel-specific causal case study**.

Do not generalize it to all beam degradation.

### E2 — controlled format-conditioned boundary-token learning

Matched Qwen SFT with a shared neutral `<END>` token produces the A_ONLY/B_ONLY symmetric reversal and MIXED rescue. This is clean causal evidence that supervision can install a format-conditioned boundary-token policy.

Keep as a controlled sandbox. Do not call it generalized response-completion learning without large-scale cross-task generalization evidence.

### Stage lineages — valuable natural material

Olmo and Tülu public lineages provide Base/SFT/preference/RL checkpoints for studying training-stage changes. The old stop-rank analysis is only one projection of these lineages; E05 will analyze their **full-sequence landscape**.

### Crucial negative / broadening evidence

Olmo base can show severe BLEU degradation with zero empty output and almost normal length. Therefore similar aggregate quality loss can arise from qualitatively different high-probability basins:

1. empty/short termination;
2. generic/off-target/copy/repetition or other non-empty mode inadequacy.

This motivates the broader question of whether the classical curse disappeared or its dominant failure basin changed.

## 5. Main hypotheses after reframe

These are **not claims yet**. They must pass E05.

### H1 — mode-seeking stability transition

Classical NMT and at least some base LMs are `mode-seeking fragile`: stronger movement toward high sequence probability raises model score while reducing semantic utility. Modern post-trained in-format LMs are substantially more stable.

### H2 — pathology migration

The classical short/empty failure basin may be replaced in base LMs by normal-length generic/copy/repetition/semantic basins. Thus the classical visible `beam curse` may change form rather than simply disappear.

### H3 — mode–mass transition

At least one same-architecture lineage will show that post-training reduces the utility gap between extreme high-probability outputs and typical probability mass.

### H4 — full-sequence probability reordering

When the **same candidate strings** are rescored across checkpoints, post-training will move probability margins in favor of adequate sequences relative to pathological ones. This is required for any `mode repair` claim.

### H5 — EOS is a special case

Immediate termination geometry explains the termination-collapse channel but not the full transition in mode-seeking stability.

## 6. E05 gate

Formal protocol: `E05_SEQUENCE_LANDSCAPE_PREREGISTRATION.md`.

E05 has five linked analyses:

1. **Search–utility trajectory** under raw beam widths;
2. **Independent likelihood-ranked Best-of-N** to test whether the phenomenon is distributional rather than beam-specific;
3. **Mode–Mass Gap** comparing mode-like outputs with typical sampled mass;
4. **Common-candidate cross-stage rescoring** to detect full-sequence probability reordering without candidate-set confounds;
5. **multi-token search-path geometry** and, secondarily, a length-conditioned score envelope.

The important object is the within-input trajectory:

> does moving toward sequences the model assigns higher probability systematically hurt utility, and how does this trajectory change across training stages?

## 7. Falsifiers

The Main-level reframe is killed or sharply downgraded if:

1. no reproducible stage transition in mode-seeking stability appears across at least two modern lineages;
2. beam differences disappear under likelihood-ranked Best-of-N;
3. common-candidate rescoring shows no systematic adequate-vs-pathological full-sequence probability reordering;
4. modern post-trained models retain mode–mass gaps comparable to base/classical systems;
5. the apparent transition is fully explained by length normalization, stopping conventions, or incompatible prompting;
6. only the termination/length channel changes while non-empty mode pathology is unchanged.

If E05 fails, do not rescue the Main story by returning to the old generation-boundary identity.

## 8. What architecture vs training means here

The classic-vs-modern endpoint comparison cannot identify cause: architecture, scale, pretraining data/objective, and post-training all differ.

The causal decomposition therefore proceeds in layers:

- **cross-era endpoint:** establish the phenotype;
- **same-architecture public lineage:** test whether training alone is sufficient to move the phenotype;
- **cross-lineage replication:** test generality;
- only after a stable stage transition is identified should controlled training isolate which supervision/objective produces it.

Do not pre-commit to SFT, RL, scale, or architecture as the explanation.

## 9. Current status

```yaml
status: ACTIVE_REFRAMED_MAIN_CANDIDATE
primary_target: ACL_EMNLP_NAACL_MAIN
scientific_object: SEQUENCE_LEVEL_MODE_SEEKING_STABILITY
primary_rq: WHY_MODE_SEEKING_BECOMES_LESS_HARMFUL
old_uncertainty_identity: RETIRED
old_generation_boundary_identity: DEMOTED_TO_SUBMECHANISM
termination_channel: REAL_BUT_PARTIAL
e02_role: NARROW_CAUSAL_SANDBOX
novelty: PLAUSIBLE_REQUIRES_E05
main_ready: NO
next_gate: E05_SEQUENCE_LANDSCAPE_AUDIT
continue: YES
```

## 10. One-sentence provisional paper identity

> **We ask why increasingly mode-seeking decoding exposes pathological high-probability sequences in classical and base sequence models but can become substantially more stable after modern post-training, and whether this transition reflects a reorganization of the full-sequence relationship among mode, typical probability mass, and task utility.**
