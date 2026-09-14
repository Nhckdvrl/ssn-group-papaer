# L36 Promotion Record — Active Main Candidate

**Date:** 2026-09-14  
**Trigger:** controlled E02 completed at commit `4c81ced226c6b24fc68d79c243e13aed8ff8b801`  
**Decision:** **PROMOTE — ACTIVE MAIN CANDIDATE**  
**Primary venues:** ACL / EMNLP / NAACL Main  
**Fallback:** Findings if replication / external-validity hardening is insufficient.

## Why the previous Findings ceiling is no longer the right ceiling

The earlier ceiling assessment was correct for the evidence available then. It faced a fatal reviewer compression:

> “Classic NMT beam collapse is already an EOS/length-bias story from 2018–2020; modern instruction-tuned models simply have different stopping behavior.”

A cross-era correlation in `p(stop)` could not defeat that compression.

E02 changes the scientific object. Under a matched causal training design, post-training does not merely lower or raise a global stop prior. It learns **which response boundary belongs to which interaction format**.

The experiment holds fixed:

- Qwen2.5-3B base initialization;
- 2,998 En→De training pairs;
- example order, optimizer, training budget and seed;
- the identity and prior of the *single* stop symbol `<END>`;
- evaluation substrate and decoding semantics.

Only the wrapper in which the response boundary is supervised changes.

Final boundary placement:

| training condition | format A | format B |
|---|---:|---:|
| `A_ONLY` | **0.966** | ~0 |
| `B_ONLY` | ~0 | **0.961** |
| `MIXED` | **0.962** | **0.963** |

This symmetric reversal plus mixed-format rescue is the load-bearing causal result. It eliminates the major natural-checkpoint confounds of stop-token identity, stop-set cardinality, and co-adapted weights/interface.

Behavior tracks the learned contract: trained formats remain near reference length and beam-stable, while untrained formats run to roughly four times reference length with BLEU ~6–8.

## What the paper is now about

Not:

- “EOS matters”;
- “SFT teaches EOS”;
- “wrong chat templates hurt”;
- “classic beam search likes short hypotheses.”

Those are old or obvious.

The candidate paper asks:

> **What does post-training teach a language model about when a response is allowed to end, and how does that learned generation boundary determine when search can expose a termination pathology?**

The current contribution chain is:

```text
controlled post-training
  -> learns a format-conditional generation boundary
  -> natural post-training lineages move stop-event geometry by orders of magnitude
  -> that geometry moves the search-exposure scale
  -> a preregistered out-of-sample search-width prediction succeeds
  -> classic NMT and modern in-format LLM translation occupy different termination regimes
  -> selective stop-geometry intervention can move the pathology
```

The beam-search curse is therefore a high-leverage stress test for a learned generation contract, not the only scientific object.

## Why the claim is not trivial

A trivial story would end at “the model learns the end token it was trained on.” E02 alone would be vulnerable to that compression.

The Main-candidate story survives only as the **joint chain**:

1. the response boundary is conditional on format rather than a global stop prior;
2. boundary learning is separable from pre-existing translation competence;
3. natural post-training moves stop geometry by orders of magnitude in a format-dependent way;
4. a local pre-search quantity predicts the beam scale at which the termination channel becomes accessible;
5. this quantity connects the controlled learning result to the historical classic-NMT → modern-LLM regime shift;
6. termination collapse is experimentally distinguished from non-empty mode inadequacy.

`rank_stop <= 2b` itself is an implementation consequence, not novelty. The scientific evidence is the cross-system movement and out-of-sample predictive use of the exposure scale.

## P4 falsification is retained

Registered P4 predicted boundary learning before task competence. It failed: by step 200 trained-format BLEU is already ~97% of final while `p(<END>@true_end)` is only 0.407.

Do not rescue P4. The revised supported claim is:

> **Substantial task competence pre-exists this SFT; post-training can add the generation boundary without being the source of the underlying translation capability.**

This is a dissociation, not the originally predicted temporal order.

## Preregistration amendment must remain visible

The original E02 primary statistic, first-position stop rank, is unsuitable for a shared neutral `<END>` token: an unseen neutral terminator produces run-on behavior rather than premature stopping. After a disclosed A-only pilot exposed this, the primary was amended to the teacher-forced boundary-placement profile before the decisive symmetric B-only / MIXED outcome was complete.

Do not describe P1′ as untouched preregistration. The transparency strengthens credibility; hiding the amendment would weaken it.

## Remaining Main blockers

### 1. Boundary-specificity versus broad format failure

The largest unresolved reviewer attack is that unseen-format BLEU is only ~6–8 with ~4× length. This could mean the wrapper breaks more than termination.

Required diagnostics:

- target-token NLL / accuracy before the true boundary, excluding `<END>`;
- quality of the first translation span before run-on continuation;
- end-hazard profile over positions.

If content translation remains intact and only stopping fails, the boundary claim becomes much stronger. If content also collapses, retain the broader **format-conditional generation contract** claim and do not assert boundary-only causality.

### 2. Replication

E02 is one base model / seed / language direction. Replicate the decisive A_ONLY / B_ONLY / MIXED factorial with additional seeds and preferably one second base family. The effects are huge; this is replication, not model-zoo expansion.

### 3. Natural-lineage external validity

Add at least one independent public base→SFT(/preference/RL) lineage to the Olmo-3 result.

### 4. Paper-quality endpoint evaluation

Add a semantic MT metric, uncertainty intervals, and modest language/model breadth to the classic↔modern endpoint. Keep the paper mechanism-first.

## Claim boundary

Current strongest defensible headline:

> **Post-training learns a format-conditional generation boundary that is separable from task competence; by reorganizing stop-event geometry, that learned boundary moves the search-width scale at which a classical termination pathology becomes accessible.**

Do not claim that termination explains all beam degradation: OLMo base already demonstrates a separate non-empty mode-inadequacy channel.

## Verdict

```yaml
promotion: PASS
status: ACTIVE_MAIN_CANDIDATE
main_ready: NO
reason_for_promotion: CONTROLLED_FORMAT_BOUNDARY_CAUSALITY_PLUS_SEARCH_BRIDGE
triviality_filter: PASS_ONLY_FOR_FULL_CHAIN
P4: FALSIFIED_AND_REVISED
major_open_attack: BOUNDARY_SPECIFICITY_VS_BROAD_FORMAT_FAILURE
replication_needed: YES
continue: YES
```
