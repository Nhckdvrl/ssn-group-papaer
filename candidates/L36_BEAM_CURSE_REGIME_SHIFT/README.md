# L36 — Where Did the Beam-Search Curse Go?

**Status:** **ACTIVE — sustained Findings-target project**  
**Primary target:** ACL / EMNLP / NAACL Findings  
**Main ceiling:** open, but not required  
**Date:** 2026-09-14

Current authoritative project definition: [`ACTIVE_PROJECT.md`](ACTIVE_PROJECT.md)  
Original selection and audit trail: [`SELECTION.md`](SELECTION.md)  
E00 verdict: [`results/e00/E00_VERDICT.md`](results/e00/E00_VERDICT.md)  
Ceiling probe / completed extension evidence: [`results/ext/CEILING_ASSESSMENT.md`](results/ext/CEILING_ASSESSMENT.md)

## Current research question

> **Why does raw wide-beam MAP decoding catastrophically shorten classic NMT, yet remain stable for modern instruction-tuned LLM translation? What changed in the learned generation distribution?**

The active story is a **classic-NMT → modern-LLM termination-regime shift**.

The project no longer claims that intrinsic human-reference uncertainty explains sentence-level beam damage. That original identity is retired: the classic system shows the opposite within-MT uncertainty ordering even at beam 512, and uncertainty adds essentially no information once termination competitiveness is included.

## What is new enough to pursue

Old literature already owns the facts that classic NMT can prefer short/empty hypotheses and that EOS/length bias is central. L36 therefore does **not** claim “EOS causes the beam curse.”

The surviving scientific claim is broader and newer:

> **The disappearance of the beam-search curse in modern LLM translation reflects a measurable shift in termination geometry, not merely a change in beam-search normalization; classic and modern systems occupy different search regimes under matched raw scoring, and moving termination competitiveness can move the pathology.**

This passes the project's triviality filter only in this regime-shift form. The following are explicitly too trivial / too old to serve as the paper identity:

- EOS probability affects stopping;
- classic NMT sometimes prefers the empty string;
- modern chat models usually do not emit empty answers;
- adding a positive EOS bias makes outputs shorter.

## Evidence already in hand

On the same En→De substrate with raw cumulative sequence scores (`length_penalty = 0`):

- `facebook/wmt19-en-de`: beam 4 → 64, BLEU 48.61 → 43.28; empty 0 → 8.75%; length ratio 1.011 → 0.845;
- `google/gemma-3-12b-it`: beam 4 → 64, BLEU 45.91 → 46.12; empty 0 → 0%; length ratio 0.998 → 0.995.

The classic system continues to collapse through beam 512 (BLEU 3.67; 54.43% empty; length ratio 0.253). The modern non-collapse therefore survives the exact raw-scoring semantics under which the classic system fails.

The model-side contrast is also large: the measured immediate-stop log probability is about -9.31 for the classic system and -35.33 for Gemma under the current stop-event definition. A preregistered stop-logit intervention on Gemma shows a dose response and brings back beam-amplified shortening/empty outputs, although the current +26 step-0 intervention also damages greedy decoding and therefore only partially reconstructs the clean classical signature.

For modern chat models, every future measurement must define `stop` from the **actual generation contract** (all legal EOS/EOT/turn terminators), not from one arbitrary tokenizer EOS id.

## Why the project is promoted now

The previous `HOLD / finding-level at best` language was written under the old requirement that L36 had to become a revised uncertainty law and plausibly grow to Main. That is no longer the acceptance criterion.

Under the current criterion — a credible, non-trivial scientific story that can support a strong Findings paper even if the Main ceiling is uncertain — L36 clears the bar:

1. the modern non-collapse is a real matched-regime phenomenon, not a length-normalization artifact;
2. the old uncertainty identity has been falsified rather than post-hoc rescued;
3. termination geometry supplies a coherent cross-era explanation with an existing causal intervention;
4. no owner found in the audit already establishes the same classic→modern regime shift plus the same causal account;
5. the remaining work is paper-building work, not phenomenon gambling.

## Authorized next work

L36 is no longer restricted to one bounded pilot. The active paper program is:

1. **Reverse rescue:** selectively reduce step-0 stopping competitiveness in classic NMT and test whether the wide-beam collapse disappears without damaging greedy/small-beam quality.
2. **Cleaner forward intervention:** match the classic stop **rank / score margin**, not just mean log probability, so greedy remains mostly clean while wider beams increasingly expose the stop-now candidate.
3. **Same-weights / interface isolation:** redo the void Qwen plain/chat or base/instruct test with string-level stopping enforced inside beam search. The previous newline post-truncation run remains void / untested.
4. **Breadth:** replicate across several modern checkpoints/families and several translation directions, without turning the work into a benchmark.
5. **Semantic metric:** add COMET or another established semantic metric plus bootstrap uncertainty alongside BLEU/chrF.

Full claim stack, novelty boundary, kill conditions, and experiment details are in [`ACTIVE_PROJECT.md`](ACTIVE_PROJECT.md).

## Current verdict

```yaml
status: ACTIVE_SUSTAINED_PROJECT
paper_identity: CLASSIC_TO_LLM_TERMINATION_REGIME_SHIFT
primary_target: ACL_EMNLP_NAACL_FINDINGS
main_ceiling: OPEN_BUT_NOT_REQUIRED
original_uncertainty_identity: RETIRED
core_regime_shift: SUPPORTED_ON_CURRENT_MATCHED_SETTING
forward_intervention: SUPPORTED_WITH_GREEDY_DAMAGE_CAVEAT
reverse_rescue: TODO
same_model_interface_claim: UNTESTED
continue: YES
```

### One-sentence identity

> **Classic NMT and modern instruction-tuned LLM translation occupy different termination regimes: under the same raw MAP search, the former exposes a cheap stop-now mode and collapses as beam widens, while the latter suppresses that mode and remains stable; L36 asks what moved the model across that boundary and whether moving it back and forth causally switches the curse.**
