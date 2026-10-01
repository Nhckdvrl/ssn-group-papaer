# First experimental wave: correspondence, competence, and usable evidence

Status: active workbench, **not a candidate**. No new training. Repository synced
to `6cc0e50`; pre-existing unrelated untracked work left untouched.

## What was actually done

- Read methods, results and relevant appendices of JGP, MONOWEB, OpenSeal,
  TransWebEdu, False Friends, Macaroni, and Bilingual BabyLM. Source hashes and
  failed downloads are in `sources/manifest.json`; decomposition is in
  [P0_PARENT_AUDIT.md](P0_PARENT_AUDIT.md).
- Cached five JGP models and MONOWEB EN-DE FWB / MWB / MWB+P at 34K in the
  standard Hugging Face cache. Used existing `openslime` conda environment and
  free A100s on fvcrc10. No existing jobs were killed.
- Completed 15 frozen probes: seven XCOPA runs (481 common semantic items,
  four language cells each), five XNLI runs (500 items, four cells each), and
  three HellaSwag runs (500 items, four cells each): 29,468 item-cell scores.
  This count includes diagnostic formats and corrupted-context controls, not
  29,468 independent questions. Per-option likelihoods and metadata retained.
- Published-table reconstruction is separate from our inference. None of these
  pilots is presented as a complete reproduction of a parent's benchmark suite.

## Main results and decisions

All intervals below are exploratory paired item bootstrap 95% intervals, with
10,000 draws. They are **not multiplicity-adjusted**, and training seeds are not
replicated. Cross-language cells have connector/continuation-language confounds.

| Question | Observation | Decision |
|---|---|---|
| Do existing parents already support acquisition H1? | JGP adjacency gains are larger in ID than weaker ZH on shared tasks. OpenSeal XCOPA has no positive average gain; its 7B XNLI average is slightly negative. | Downweight the leading explanation. Neither two-language rank comparison nor change-vs-baseline regression identifies a competence threshold. |
| Does matched JGP adjacency clearly improve raw XCOPA? | Non-adjacent -> distributed: ID +2.49 pp [-0.83,6.03], ZH +1.04 [-2.49,4.57]. Cross-minus-mono interaction -2.70 [-5.61,0.10]. | No convincing raw-score or selective cross-language composition result. Baseline performance is near chance. |
| Does a choice-prior correction uncover evidence use? | Same contrast, prior-adjusted: ZH +8.32 pp [2.49,14.35]. But after swapping premise for an unrelated same-cause/effect premise, pairing-by-evidence interaction is only +4.99 [0.00,9.77], and gold-margin interaction +0.116 nats [-0.17,0.40]. | Not a validated reasoning gain. Do not promote the calibration-dependent headline. |
| Any remaining directional lead? | ID premise -> ZH choice: evidence interaction +5.61 pp [1.25,9.98] under prior correction; raw gold-margin interaction +0.447 nats [0.13,0.77]. ZH -> ID margin +0.022 [-0.28,0.32]. | A provisional directional evidence-uptake signal, not a paper claim. Requires a non-floor second task, held-out competence, and stronger semantic counterfactuals. Topic/lexical association remains an explanation. |
| Does MONOWEB pairing rescue German NLI? | Joint-score DE->DE +0.20 pp; token-normalized -0.80. EN->EN raw +5.40, with strong entailment prediction bias. Explicit English-label diagnostic predicts essentially all entailment (~33.4%). | Label format is invalid for this frozen model, not evidence of absent capability. Raw NLI shifts cannot support a mechanism claim. Stop prompt searching. |
| Does a non-floor second MONOWEB task show cross-language stress? | HellaSwag MWB->MWB+P character-normalized DE->DE 41.0->41.2% (+0.20 [-2.60,3.00]); cross-minus-mono +0.20 [-2.40,2.80]. Other readouts also lack a clear interaction. FWB contrast likewise has no clear interaction. | No rescue in this particular German pilot. This is not an equivalence test, and says nothing yet about weak languages or open-ended target-language generation. |

Machine-readable evidence:
[published](results/p1_published_summary.json),
[JGP pairing](results/p1_pairing_pilot.json),
[JGP evidence intervention](results/p1_pairing_evidence_control.json),
[NLI pairing](results/p2_pairing_pilot.json),
[invalid label diagnostic](results/p2_label_readout_pilot.json),
[HellaSwag pairing](results/p2_hellaswag_pairing.json),
[HellaSwag full bilingual](results/p2_hellaswag_full_bilingual.json).

## What this changes at research scale

The initial cross-paper tension cannot yet bear a two-regime narrative. Several
apparent conflicts mix target-side content, pairing, schedule, task type, and
readout. In particular, OpenSeal is not independent evidence of broad reasoning
acquisition through pairing. Translation-only gains and a matched-content
Standard-vs-Split decomposition are already owned by the parents and the direct
ICLR prior. Repeating them with another model is not enough.

The next discriminating question is narrower in causal definition, not merely in
benchmark scope: **does bilingual correspondence change sensitivity to relevant
evidence, independently of unconditional answer preferences and monolingual
competence?** This could matter for whether translation/alignment is a proxy for
usable multilingual knowledge. It is only an exploration branch. A score
calibration recipe, a direction-specific slice, or unrelated-context likelihood
sensitivity alone has insufficient novelty and cannot establish reasoning.

## Finite next gates

1. Measure target-language competence on held-out native text or disjoint items;
   compare within intervention families, not heterogeneous parent models.
   Different tokenizers require bytes/characters or matched within-tokenizer
   comparisons, not cross-model raw perplexity.
2. Test the provisional JGP evidence signal on one independent, above-chance task
   with a fixed readout. Use relevant-vs-irrelevant evidence and, if feasible,
   label-changing semantic counterfactuals while holding options fixed. Do not
   select prompts by treatment effect or claim a shuffle isolates inference.
3. MONOWEB: extend beyond German using a pre-specified language/task contrast,
   and existing early checkpoints if they permit a valid competence trajectory.
   A trajectory also changes optimization time: it is a diagnostic, not a clean
   factorial competence intervention. Include output-language burden only if
   separate from answering correctness; the parent already owns on-target rates.
4. P3 requires the **same qualitative interaction**, not separate attractive
   metrics, in an independent intervention family. Otherwise abandon this branch
   and reconsider task/content or retention objects at field scale.
5. P4 remains prohibited until existing substrates leave an identified causal
   ambiguity, the direct Standard/Split prior has been fully audited, and a small
   factorial intervention would resolve it. No expensive training to rescue H1.

P2 is **partial**: no independent competence diagnostic, weak-language stress, or
generation-burden experiment yet. P3 has not been executed. There is no verified
top-tier paper idea yet.

## Integrity and reproducibility

XCOPA: excluded 19 reannotated/incompatible ID/ZH items across all cells.
HellaSwag: joined semantic IDs and respected language-specific option
permutations and gold indices; five demos excluded from evaluation. No silent
context truncation or incomplete-run summaries. Model/dataset revisions, prompt
hashes, package versions, and expected item counts are saved with each run.
Legacy pickle loading is restricted to pinned official JGP checkpoints.

`verify_scorer.py` passed direct next-token cross-entropy, boundary and padding
checks in FP32 compute on the same BF16-rounded weights (maximum four-case
batch-vs-single discrepancy 1.53e-5 nats). BF16 batch-shape sensitivity reached
0.270 nats for one unconditional five-token choice. This small test does not
bound errors on the full dataset. **Prior-adjusted and near-boundary effects
require numerical replication before further interpretation.** It is not a
prompt-selection gate. Checks are in [scorer_verification.json](results/scorer_verification.json).
The complete local raw-output inventory is in
[run_inventory.json](results/run_inventory.json).

Run from the repository root with the existing conda interpreter:

```bash
PY=/home/xiang/miniconda3/envs/openslime/bin/python
W=workbench/cross-lingual-acquisition-regimes
$PY "$W/scripts/analyze_probe.py" "$W/artifacts/p2/mwb_hswag_s5.jsonl" \
  --treated "$W/artifacts/p2/mwbp_hswag_s5.jsonl" \
  --output "$W/results/p2_hellaswag_pairing.json"
$PY "$W/scripts/analyze_context_control.py" \
  "$W/artifacts/p1/jgp_nonadj_s0.jsonl" \
  "$W/artifacts/p1/jgp_nonadj_shuffled_s0.jsonl" \
  "$W/artifacts/p1/jgp_distributed_s0.jsonl" \
  "$W/artifacts/p1/jgp_distributed_shuffled_s0.jsonl" \
  --output "$W/results/p1_pairing_evidence_control.json"
```

Full-text limitation: the additional direct ICLR Standard/Split prior remains
behind OpenReview browser verification/403 in this execution. Its local-library
record and indexed primary abstract already establish a strong ownership warning;
neither is represented as a fresh full-text read. OpenSeal controlled checkpoints
were not found; model-family availability is not assumed from a paper promise.
