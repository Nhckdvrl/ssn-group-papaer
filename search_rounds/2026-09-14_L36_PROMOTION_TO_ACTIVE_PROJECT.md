# L36 Promotion Decision — 2026-09-14

## Decision

**PROMOTE L36 to an active sustained project.**

New status:

```yaml
status: ACTIVE_SUSTAINED_PROJECT
primary_target: ACL_EMNLP_NAACL_FINDINGS
main_ceiling: OPEN_BUT_NOT_REQUIRED
paper_identity: CLASSIC_TO_LLM_TERMINATION_REGIME_SHIFT
continue: YES
```

Authoritative current project definition:

- `candidates/L36_BEAM_CURSE_REGIME_SHIFT/ACTIVE_PROJECT.md`
- `candidates/L36_BEAM_CURSE_REGIME_SHIFT/README.md`

The old `SELECTION.md`, E00 preregistration, E00 verdict, and extension ceiling report remain preserved as the audit trail. They document how the original intrinsic-uncertainty identity failed and how the current termination-regime story emerged.

## Why the decision changed

The previous ceiling decision was evaluated against a stricter and now-unnecessary requirement: L36 had to become a new uncertainty law and plausibly justify an ACL/EMNLP/NAACL Main paper. Under that requirement, the original identity was correctly declared dead.

The current acceptance bar is different:

> a topic may proceed if it has a credible, non-trivial, defensible scientific story that can sustain a strong Findings paper, even when its Main ceiling is uncertain.

This is **not** permission to save weak topics by shrinking claims. The promoted L36 story survives only because the *larger* regime-shift claim remains meaningful.

## Claim-compression audit

### Claims that are already owned / trivial and therefore forbidden as the paper identity

1. Classic NMT can prefer short or empty translations.
2. EOS / length bias contributes to the classic beam-search curse.
3. Higher EOS logits make generation stop earlier.
4. Instruction-tuned chat models generally do not answer with empty strings.

Murray & Chiang (2018), Stahlberg & Byrne (2019), and Shi, Xiao & Knight (2020) substantially own the first two. The latter two are not scientifically sufficient claims.

### Claim that survives

> **The disappearance of the beam-search curse across the classic-NMT → modern instruction-tuned-LLM transition is a real model-distribution regime shift: it survives matched raw sequence scoring, is associated with a very large change in termination competitiveness, and can be causally moved by selectively changing that termination geometry.**

This is not identical to the old EOS story. The old literature explains why classic NMT can occupy a bad termination regime. Pang et al. (TACL 2025) observes that the classic beam challenge may no longer apply to LLM translation. L36's object is the missing cross-era explanation: **what changed so that the same wide raw MAP search stopped exposing the pathology?**

## Triviality audit

A reasonable reader may initially compress the result to:

> “Classic NMT has an empty-hypothesis problem; modern chat models do not.”

That compression would kill the topic if all we had were empty-output rates.

It does **not** fully explain the current evidence because:

1. the modern non-collapse survives **matched unnormalized RAW scoring**, ruling out the easy “modern beam search just uses normalization” explanation;
2. the classic and modern systems show a very large quantitative separation in immediate-stop competitiveness under the same translation substrate;
3. a preregistered selective stop-logit intervention moves the modern model toward the classic failure regime with a dose response;
4. the next decisive tests are bidirectional rescue and rank/margin calibration, which can show a search-exposure boundary rather than the tautology “more EOS → more stopping”;
5. the strongest pending test asks whether the regime follows **post-training / generation interface rather than architecture or scale**, using a correct in-beam stop contract.

Therefore the project passes the triviality filter **only** if it stays centered on the regime transition and the causal boundary. If it degrades into an EOS-probability correlation paper, it should be stopped.

## Current evidential backbone

### Historical contrast under matched RAW scoring

On the same En→De substrate:

- classic `facebook/wmt19-en-de`, beam 4 → 64: BLEU 48.61 → 43.28; empty 0 → 8.75%; length ratio 1.011 → 0.845;
- modern `google/gemma-3-12b-it`, beam 4 → 64: BLEU 45.91 → 46.12; empty 0 → 0%; length ratio 0.998 → 0.995.

The classic model continues to beam 512: BLEU 3.67, 54.43% empty, length ratio 0.253.

### Original uncertainty story is rejected

The classic deterioration is not stronger on the high human-reference-uncertainty quartile; it is stronger on the low-uncertainty quartile even in the catastrophic beam range. Once termination competitiveness is included, the frozen uncertainty score adds essentially no collapse-prediction information.

This result should be reported as the project history / correction, not inflated into the paper's main contribution.

### Termination-regime separation

Current measurement gives roughly:

- classic: `log p(stop immediately | x) = -9.31`;
- Gemma instruction/chat: `-35.33`.

Future measurements must aggregate the model's **actual legal generation terminators**. Modern chat models can use EOS, EOT, end-of-turn, or multiple legal stop ids; one tokenizer EOS id is not automatically the scientific stop event.

### Forward causal movement

The preregistered Gemma intervention has a monotone dose response. The +26 step-0 intervention restores substantial shortening/empty behavior and beam amplification, but also hurts greedy decoding, so it is evidence for causal movement toward the classic regime, not yet a perfect reconstruction of the classical curse.

## Paper-scale next steps

Priority order:

1. **Classic reverse rescue** — lower step-0 stop competitiveness and test whether wide-beam collapse disappears while greedy/small-beam output remains intact.
2. **Rank/margin-calibrated modern intervention** — match the classic stop rank or score margin while keeping stop below greedy argmax on most examples. The desired signature is clean greedy + worsening wide beam.
3. **Correct same-weights/interface test** — implement string-level stopping inside beam search for the Qwen/plain-text condition. The prior newline-token experiment remains void and must never be treated as negative evidence.
4. **Breadth** — several modern checkpoints/families and several translation directions; enough to establish a regime rather than a Gemma anecdote.
5. **Semantic metric** — COMET or another established semantic MT metric alongside BLEU/chrF with uncertainty estimates.

## Promotion logic

The project is now in ordinary sustained-project mode rather than bounded-pilot mode. This means:

- one failed extension no longer automatically kills the topic;
- breadth and causal closure are authorized;
- the team should optimize for a coherent paper, not continually re-litigate whether E01 was allowed;
- the topic should still be stopped if the cross-model replication collapses, the termination separation disappears under correct stop-event accounting, interventions only cause generic destruction, or a direct prior owner is found for the same classic→modern causal regime-shift result.

## Final project identity

> **Classic NMT and modern instruction-tuned LLM translation occupy different termination regimes: under the same raw MAP search, the former exposes a cheap stop-now mode and collapses as beam widens, while the latter suppresses that mode and remains stable; L36 studies what moved the model across that boundary and whether moving it back and forth causally switches the curse.**
