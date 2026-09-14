# L36 — Active Project: Where Did the Beam-Search Curse Go?

**Decision date:** 2026-09-14  
**Status:** **ACTIVE — sustained Findings-target project**  
**Primary venue bar:** ACL / EMNLP / NAACL Findings; reassess Main only if the stronger interface/post-training result lands  
**Old identity:** the intrinsic-uncertainty story is retired. Do not resurrect it.

## 1. Core research question

> **Why does raw wide-beam MAP decoding catastrophically shorten classic NMT, yet remain stable for modern instruction-tuned LLM translation? What changed in the learned generation distribution?**

The working answer is not “beam search became better,” “LLMs are simply stronger,” or “modern decoding uses length normalization.” The current evidence points to a **termination-regime shift**:

> **Classic NMT places immediate stopping close enough to competitive translations that wider search can expose a pathological short/empty mode; modern instruction-tuned LLM translation moves the stop-now event far outside that competitive search frontier.**

The scientific object is the **regime transition** and its cause, not the rediscovery that EOS/length bias can make classic NMT prefer empty outputs.

## 2. Why this is not the trivial claim

The following claims are too weak and are explicitly banned as paper identities:

- “EOS probability matters for beam search.”
- “Classic NMT can prefer empty hypotheses.”
- “Instruction-tuned LLMs usually do not output empty strings.”
- “Increasing an EOS logit makes models stop earlier.”

Those are either old or obvious.

The non-trivial claim the project must earn is:

> **The disappearance of the beam-search curse across the classic-NMT → instruction-tuned-LLM transition is explained by a measurable change in termination geometry, survives matched raw sequence-scoring semantics, and is reversible by selective movement across the same termination boundary.**

A stronger version, if the same-weight/interface experiment succeeds, is:

> **Beam robustness is not an intrinsic consequence of architecture scale or better semantic modeling; it follows the generation contract / post-training interface because that contract moves the model across a termination-geometry boundary.**

That stronger statement would materially raise the ceiling because it explains *why the regime changed*, rather than merely measuring that it changed.

## 3. What current evidence already supports

### C1 — the historical regime shift is real under matched search semantics

On the same En→De substrate and **RAW** cumulative sequence score (`length_penalty = 0`):

- `facebook/wmt19-en-de`: beam 4 → 64, BLEU 48.61 → 43.28, empty 0 → 8.75%, length ratio 1.011 → 0.845;
- `google/gemma-3-12b-it`: beam 4 → 64, BLEU 45.91 → 46.12, empty 0 → 0%, length ratio 0.998 → 0.995.

Following the classic system to beam 512 yields BLEU 3.67, 54.43% empty outputs, length ratio 0.253. Therefore the modern flat curve is **not** explained away by modern length-normalized beam defaults.

### C2 — intrinsic uncertainty is not the useful explanatory axis for the sentence-level collapse

The original L36 premise is dead. On the classic system the catastrophic beam damage is larger in the *low*-uncertainty quartile even through beam 512. In the collapse model, frozen human-reference uncertainty contributes essentially nothing once stopping competitiveness is included.

This is a correction to the project, not the new paper identity.

### C3 — classic and modern systems occupy sharply different termination regimes

Measured before beam search:

- classic `facebook/wmt19-en-de`: `log p(stop immediately | x) ≈ -9.31`;
- `gemma-3-12b-it` chat: about `-35.33` under the current stop-event measurement.

On the classic system, stop competitiveness strongly predicts which sentences collapse; intrinsic uncertainty does not.

**Important measurement rule:** for modern chat models, `stop` must mean the probability mass of the model's actual legal generation terminators, not an arbitrary tokenizer EOS id. Audit `generation_config.eos_token_id`, turn terminators, and any multiple-stop-token contract per model.

### C4 — selective movement of termination geometry can reintroduce beam-amplified degeneration

The preregistered Gemma stop-logit intervention shows a dose response: +13 is effectively null; around +26 produces shortening/empty outputs and a large BLEU drop; +39 destroys generation. With step-0 +26, empty rate rises from 4.0% at greedy to 8.5% at beam 64.

This supports **causal sufficiency of moving the model toward the classic termination regime**. It does **not** yet justify saying that the exact classic beam-curse signature has been fully reconstructed, because the +26 intervention already damages greedy decoding.

## 4. Closest ownership and the novelty boundary

Old work owns the pathology:

- Murray & Chiang (2018): the beam problem and brevity bias are tightly linked;
- Stahlberg & Byrne (2019): exact search often finds the empty translation as the model mode;
- Shi, Xiao & Knight (2020): analyzes why classic NMT assigns high probability to empty outputs and directly measures first-step EOS probability; changing EOS design can eliminate empty preferences.

Modern work supplies the mother phenomenon:

- Pang et al. (TACL 2025): reports that the classic beam-search challenge may no longer apply to LLM-based MT.

Therefore L36 must **not** claim discovery of the EOS mechanism. The novelty is the **cross-regime explanation**:

> old literature explains why classic NMT can live in a pathological termination regime; modern literature observes that the beam curse largely disappears; L36 identifies and causally tests the model-side quantity whose historical shift connects these two regimes.

Reviewer compression to survive:

> “Old papers already showed that empty hypotheses cause the beam curse; modern chat models simply do not output empty strings.”

The answer cannot be rhetoric. It must be empirical: matched raw scoring, cross-era quantitative separation, a selective reversible intervention, and ideally same-weights/interface isolation.

## 5. Current paper claim stack

### Claim A — regime shift

> **Modern instruction-tuned LLM translation remains stable under wide raw-score beam search in a setting where classic NMT catastrophically shortens and collapses.**

This is already supported on the current matched substrate, but needs breadth and semantic metrics for a paper.

### Claim B — termination geometry explains the difference

> **The classic/modern difference is localized to termination competitiveness rather than to the original intrinsic-uncertainty account or to length-normalization defaults.**

Use `stop-now` competitiveness, EOS/turn-termination rank, and a score margin against viable nonempty hypotheses. Do not make pseudo-R² itself the headline.

### Claim C — the regime is causally movable

> **Moving only termination competitiveness toward the classic regime recreates beam-amplified degeneration; moving the classic system away from that regime should rescue it.**

Current evidence supports the first direction imperfectly. The reverse rescue is now a priority experiment.

### Claim D — optional ceiling-raising claim

> **The termination regime is determined substantially by post-training / generation interface rather than by model scale or architecture alone.**

This claim is **not yet established**. The Qwen few-shot behavioral test is void, not negative. It must be rerun with a beam search that enforces string-level stopping correctly.

## 6. Required next experiments — paper-scale authorization

L36 is no longer restricted to a one-cell pilot. The following are authorized as a coherent paper program.

### E1 — reverse causal rescue on classic NMT

Lower immediate-stop competitiveness in the frozen classic model without otherwise changing token scores. Prefer a local operation at step 0. Test whether wide-beam shortening/empty collapse disappears while greedy/small-beam translation remains materially intact.

**Payoff:** bidirectional causal closure. This is more informative than another regression.

### E2 — margin/rank-calibrated modern intervention

Replace the crude “match mean log p(EOS)” intervention with a calibration that matches the classic **rank or score margin** of the legal stop event at step 0 while keeping stop below greedy argmax on most items.

Target signature:

- greedy remains mostly clean;
- small beam remains mostly clean;
- wide beam increasingly exposes the stop-now candidate;
- output shortening / empty collapse grows with beam width.

This is the cleanest test of the search-exposure story.

### E3 — same-weights / interface isolation

Redo the base/instruct or plain/chat comparison with the **actual stop contract enforced inside beam search**. Newline post-truncation is invalid. If a stop condition is a string rather than one token, implement string-level stopping in the search state.

Best possible result:

> same or tightly matched model family, same translation task, interface/post-training condition changes termination geometry and switches the beam pathology.

Do not claim this until the behavioral experiment is valid.

### E4 — breadth needed for Findings credibility

Replicate the matched raw-score result on approximately:

- 3–4 modern checkpoints from at least two model families;
- 3–4 translation directions / language pairs where practical;
- at least one classic NMT baseline per direction when available.

This is replication breadth, not a benchmark paper. The object remains the regime-shift mechanism.

### E5 — semantic-quality audit

Add COMET or another established semantic MT metric alongside BLEU/chrF, with bootstrap uncertainty. Pang et al. reported different behavior for surface and semantic metrics; the paper must show whether the termination pathology is merely surface shortening or genuinely harms translation adequacy.

## 7. What not to spend time on

Do not:

- revive the `beam × intrinsic uncertainty` law as the main story;
- build a new uncertainty benchmark;
- add a generic model zoo without causal purpose;
- turn this into a decoder-method paper;
- claim novelty from `p(EOS)` alone;
- run more elaborate regressions before completing the two-direction intervention;
- treat the void Qwen few-shot run as evidence;
- silently use one tokenizer EOS id when the model's generation contract has multiple legal stopping tokens.

## 8. Decision rule for continuation

This is now an **active project**, so ordinary negative cells do not automatically kill it. The core can survive some failed extensions because C1–C4 already constitute a coherent Findings-scale story.

The project should be stopped only if one of the following becomes true:

1. matched RAW replication shows the modern non-collapse was Gemma-specific rather than a meaningful modern regime;
2. after correct stop-event measurement, termination geometry does not separate classic and modern systems;
3. selective termination interventions cannot move wide-beam pathology without merely destroying generation in all decoding regimes;
4. a direct prior owner is found that already establishes the same classic→modern regime shift plus the same causal explanation.

Otherwise continue toward a Findings submission.

## 9. Current verdict

```yaml
status: ACTIVE_SUSTAINED_PROJECT
paper_identity: CLASSIC_TO_LLM_TERMINATION_REGIME_SHIFT
primary_target: ACL_EMNLP_NAACL_FINDINGS
main_ceiling: OPEN_BUT_NOT_REQUIRED
original_uncertainty_identity: RETIRED
core_regime_shift: SUPPORTED_ON_CURRENT_MATCHED_SETTING
termination_explanation: SUPPORTED_BUT_NEEDS_BETTER_MARGIN_MEASURE_AND_BREADTH
forward_intervention: SUPPORTED_WITH_GREEDY_DAMAGE_CAVEAT
reverse_rescue: TODO
same_model_interface_claim: UNTESTED
trivial_claim_filter: PASS_ONLY_FOR_REGIME_SHIFT_VERSION
continue: YES
```

### One-sentence project identity

> **Classic NMT and modern instruction-tuned LLM translation occupy different termination regimes: under the same raw MAP search, the former exposes a cheap stop-now mode and collapses as beam widens, while the latter suppresses that mode and remains stable; L36 asks what moved the model across that boundary and whether moving it back and forth causally switches the curse.**
