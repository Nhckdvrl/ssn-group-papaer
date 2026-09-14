# L36 — Active Main Candidate: Learning the Generation Boundary

**Decision date:** 2026-09-14  
**Status:** **ACTIVE — MAIN CANDIDATE**  
**Primary target:** ACL / EMNLP / NAACL Main  
**Fallback:** Findings if the causal core does not replicate broadly enough  
**Old identity:** the intrinsic-uncertainty story is retired. Do not resurrect it.

## 1. Core research question

> **What does post-training teach a language model about when a response is allowed to end, and how does that learned generation boundary determine whether wide search can expose termination pathologies?**

The current answer is stronger than the earlier “modern models have lower EOS probability” story:

> **Post-training installs a context- and format-conditional generation boundary. That boundary reorganizes stop-event geometry by orders of magnitude; the resulting geometry determines the beam width at which termination candidates become searchable, connecting a local learned boundary to the appearance or disappearance of the classic wide-beam termination pathology.**

Beam search is the stress test / readout. The scientific object is the **learned generation boundary and its search consequence**, not beam tuning and not rediscovery of EOS bias.

## 2. Why this is not the trivial claim

These paper identities are explicitly banned:

- “SFT teaches the EOS token.”
- “EOS probability affects stopping.”
- “Classic NMT can prefer empty hypotheses.”
- “Using the wrong chat template hurts generation.”
- “Increasing an EOS logit makes a model stop earlier.”
- “`rank_stop <= 2b` is a new empirical law.” It follows mechanically from the first-step top-`2b` pruning rule of the beam implementation and is only an identifying instrument.

The non-trivial claim is the **full causal chain**:

```
post-training
  -> learns a format-conditional response boundary
  -> moves stop-event geometry by orders of magnitude
  -> moves the search-exposure threshold
  -> switches a termination-pathology channel under wide MAP search
```

No single arrow is sufficient as the paper identity. The contribution is identifying and causally connecting the chain.

## 3. Load-bearing evidence

### C1 — controlled SFT causally learns a format-conditional boundary (E02)

Protocol and results: `E02_PREREGISTRATION.md`, `results/e02/E02_RESULTS.md`.

E02 uses `Qwen/Qwen2.5-3B` base, the same 2,998 En→De examples, the same order / optimizer / budget / seed, and one shared previously-unused `<END>` token in every arm and evaluation. A and B differ only in the surface wrapper. This removes the natural-checkpoint confounds of different stop-token identities, different stop-set cardinalities, and co-adapted weights/interfaces.

Final checkpoint:

| condition | tested A | tested B | interpretation |
|---|---:|---:|---|
| `A_ONLY`: `p(<END>@true_end)` | **0.966** | ~0 | boundary only in trained A |
| `B_ONLY`: `p(<END>@true_end)` | ~0 | **0.961** | **symmetric reversal** |
| `MIXED`: `p(<END>@true_end)` | **0.962** | **0.963** | both boundaries learned |

Behavior follows the learned boundary under RAW beam search:

- `A_ONLY` in A: BLEU `35.62 -> 39.51` from beam 1→64, length ratio 0.95;
- `A_ONLY` in B: BLEU `7.08 -> 5.97`, length ratio 4.02;
- `B_ONLY` in B: BLEU `36.07 -> 39.38`, length ratio 0.96;
- `B_ONLY` in A: BLEU `8.07 -> 6.82`, length ratio 4.23;
- `MIXED`: both formats remain well terminated (length ratio 0.96 / 0.96) and beam-stable.

This is the main causal identification result: **the same task/content does not induce one global willingness to stop; the learned boundary follows the format in which response termination was supervised.**

Important audit note: the original first-position-rank statistic was discovered during execution to be wrong for the neutral `<END>` design. P1 was replaced by the teacher-forced boundary-placement profile after a disclosed A-only pilot and before the decisive symmetric B-only / MIXED result was complete. This amendment must remain explicit in the paper; do not present P1′ as untouched preregistration.

### C2 — task capability and boundary learning are separable

Registered P4 predicted that the boundary would be learned before translation competence. **P4 is falsified.** At step 200 the trained-format greedy BLEU is already 34.34, about 97% of final, while `p(<END>@true_end)` is only 0.407.

The correct statement is stronger and cleaner:

> **The base model already possesses substantial translation capability; the controlled SFT chiefly adds a response-boundary policy rather than creating that capability.**

Do not claim “boundary before competence.” Preserve the falsification.

The `NOEOSLOSS` arm is supporting only. It never learns the boundary and runs to ~4× reference length, but masking `<END>` still gives it negative gradients at other positions, so this arm cannot carry a necessity claim.

### C3 — natural post-training lineages move stop geometry by orders of magnitude, keyed to interface

The Olmo-3 7B lineage independently shows the same qualitative object under natural post-training:

- base few-shot: median stop rank ~532;
- SFT/DPO/RLVR few-shot: rank ~3–4 and catastrophic early termination under wide beam;
- SFT chat: rank 1,222;
- DPO/RLVR chat: rank ~60,030 / 41,025 and no termination collapse through the tested beam range.

The same post-trained weights therefore do not merely become globally more or less willing to stop. Their stop geometry is strongly conditional on whether inference matches the post-training interaction format.

This lineage is observational with respect to training stage; E02 provides the controlled causal identification that the lineage lacks.

### C4 — local stop geometry predicts when the termination channel becomes search-accessible

For this beam implementation, an immediate-stop hypothesis can enter the first beam only if its first-step rank is within the top `2b`. This is an algorithmic exposure condition, not a novel law.

Its scientific use is predictive. Before running wide search, Olmo-3 base few-shot had median stop rank 532, giving a characteristic exposure scale around `b* ~= 266`. The prediction was committed before the decisive search:

- beam 128: **0% empty**;
- beam 512: **8% empty**, with shortening appearing only after crossing the predicted interval.

Classic `facebook/wmt19-en-de` has a much smaller stop rank (~106) and its empty-collapse channel is already severe by beam 64–128. Thus a local, pre-search measurement predicts where the termination channel becomes available at a system level.

Do not headline “393/393 violations = 0”: necessity follows from the search algorithm. Headline the **cross-system, out-of-sample movement of the onset scale**.

### C5 — classic NMT and modern in-format LLM translation occupy different termination regimes under matched RAW scoring

On the same En→De substrate and raw cumulative sequence score (`length_penalty = 0`):

- `facebook/wmt19-en-de`: beam 4→64, BLEU 48.61→43.28, empty 0→8.75%, length ratio 1.011→0.845; by beam 512 the full-substrate system reaches BLEU 3.67, 54.43% empty, length ratio 0.253;
- `google/gemma-3-12b-it` chat: beam 4→64, BLEU 45.91→46.12, empty 0→0%, length ratio 0.998→0.995.

This rules out the easy explanation that the modern non-collapse is only a length-normalization/default-decoder artifact.

The preregistered Gemma stop-logit intervention further shows that selectively moving termination competitiveness toward the classic regime induces shortening / empty outputs and beam-amplified damage. It is evidence of causal sufficiency, not discovery of EOS bias itself.

### C6 — beam-quality degradation has at least two distinct channels

Termination geometry does **not** explain every BLEU drop under beam search. Olmo-3 base can lose large amounts of BLEU while maintaining full-length outputs and zero empty rate, through generic high-probability sentences / copying. Classic NMT can reach a similar BLEU through severe empty/short collapse.

Therefore the paper must distinguish:

1. **termination collapse** — the channel L36 explains;
2. **non-empty mode inadequacy** — a separate channel already central to mode-vs-quality work.

This distinction prevents the termination account from being overstated as a universal theory of beam-search degradation.

## 4. Novelty boundary / closest ownership

Old work owns the classic pathology:

- Murray & Chiang (2018): beam degradation and brevity/length bias;
- Stahlberg & Byrne (2019): exact modes are often empty translations;
- Shi, Xiao & Knight (2020): why classic NMT prefers empty outputs, including first-step EOS behavior;
- Eikema & Aziz (2020/2022): mode inadequacy and alternatives such as MBR.

Modern work supplies adjacent premises:

- Pang et al. (TACL 2025): the classic beam challenge appears much weaker / absent in LLM-MT;
- instruction-tuning and tooling literature treats EOS/EOT supervision and chat-template correctness as practically important;
- recent work shows post-training and chat format can change other model behaviors, and diffusion-LM work studies EOS supervision pathologies under a different generation architecture.

None of these facts alone is our novelty. The ownership claim to defend is:

> **A controlled demonstration that post-training learns a format-conditional generation boundary, plus a quantitative bridge from that learned boundary to stop-event search exposure and the historical classic-NMT → modern-LLM termination-regime shift.**

A reviewer should not be able to compress the contribution to “of course a model trained on `<END>` learns `<END>`.” The symmetric A/B reversal, MIXED rescue, capability/boundary dissociation, natural post-training lineage, out-of-sample onset prediction, matched classic/modern search, and intervention are jointly needed to defeat that compression.

## 5. Main-paper claim stack

### Claim A — post-training learns a generation contract, not a global stop prior

> **Response termination is learned conditionally on the interaction format: matched SFT can install one boundary while leaving an otherwise identical boundary absent under another surface contract, and mixed supervision installs both.**

### Claim B — boundary learning is separable from task capability

> **A model can already perform the translation task while lacking the corresponding generation boundary; post-training can predominantly reorganize when generation should end rather than create the task competence itself.**

### Claim C — the learned boundary reorganizes search geometry

> **Natural post-training stages move stop-event ranks by orders of magnitude in a format-dependent way, thereby moving the beam-width scale at which termination candidates become searchable.**

### Claim D — this explains one classical decoding pathology across regimes

> **Classic NMT and modern in-format LLM translation occupy different termination regimes under matched raw MAP search; moving the termination geometry moves the termination-collapse channel.**

The paper does **not** claim to explain all beam-search quality degradation.

## 6. What still separates “Main candidate” from “Main-ready”

The central phenomenon no longer needs another rescue experiment. Remaining work is replication and claim hardening.

### R1 — replicate E02, not expand it into a benchmark

E02 currently has one base model / seed / language direction. Because the effects are enormous, the goal is not a huge sweep. Repeat the decisive A_ONLY / B_ONLY / MIXED factorial with at least additional seeds and preferably one second base-model family. Preserve the shared neutral boundary token and matched-data design.

### R2 — audit whether out-of-format failure is boundary-specific or a broader format failure

The untrained-format BLEU is only ~6–8 and length ratio ~4×. A reviewer can argue that the model simply cannot operate under the unseen wrapper. Add diagnostics that separate content competence from boundary control:

- teacher-forced target-token NLL / token accuracy **before the true end**, excluding `<END>`;
- quality of the first translation span when evaluated before the run-on continuation;
- boundary hazard profile: `p(<END>)` at the true end versus premature positions.

If translation content remains reasonable before the missing boundary, the “generation boundary” interpretation strengthens. If content also collapses, keep the broader “format-conditional generation contract” wording and do not claim boundary-only causality.

### R3 — one independent natural lineage / replication

A second public base→SFT(/preference/RL) lineage such as Tülu can establish that the Olmo stage pattern is not family-specific. The controlled E02 is the mechanism experiment; this is external validity.

### R4 — paper-quality MT evaluation

Add an established semantic metric (e.g. COMET where licensing/environment permits), bootstrap uncertainty, and at least modest language/model breadth for the classic↔modern endpoint. Do not let this become a benchmark paper.

## 7. Explicitly rejected claims

Do not say:

- intrinsic human-reference uncertainty causes the sentence-level curse;
- ACL 2022 is broadly refuted;
- E02 proves all modern beam robustness comes from termination;
- the neutral-`<END>` E02 reproduces classic premature stopping (it does not; its out-of-format failure is run-on generation);
- P4 passed;
- the amended P1′ was frozen before all pilot evidence;
- `NOEOSLOSS` cleanly proves necessity;
- beam exposure inequality itself is a new scientific law.

## 8. Current verdict

```yaml
status: ACTIVE_MAIN_CANDIDATE
primary_target: ACL_EMNLP_NAACL_MAIN
fallback: FINDINGS
paper_identity: POSTTRAINING_LEARNS_FORMAT_CONDITIONAL_GENERATION_BOUNDARIES
original_uncertainty_identity: RETIRED
controlled_format_boundary_causality: PASS_E02
symmetric_reversal: PASS
mixed_format_rescue: PASS
boundary_vs_capability: DISSOCIATED_P4_FALSIFIED_AND_REVISED
natural_stage_lineage: STRONG_ONE_FAMILY
search_onset_prediction: OUT_OF_SAMPLE_PASS
classic_modern_raw_regime_shift: SUPPORTED
all_beam_degradation_explained: NO_TWO_CHANNELS_REQUIRED
trivial_claim_filter: PASS_FOR_FULL_CHAIN_ONLY
main_ready: NO_REPLICATION_AND_BOUNDARY_SPECIFICITY_AUDIT_REMAIN
continue: YES
```

## 9. One-sentence paper identity

> **Post-training teaches language models a format-conditional generation boundary that is separable from task competence; by moving the stop event across search-exposure scales, that learned boundary determines whether wide MAP search can access a classical termination pathology.**
