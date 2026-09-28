# L02 experiment log

## 2026-09-08 — E000

Selected L02; all writes scoped to this directory. Recovered the original Task 10 training package via its archived official download page, pinned paper/data provenance, and parsed source-native NI flags and links. No changes to L03 belong to this work.

Executed `runs/E000_20260908_v1`. Reproduced the central published NI/frame/sentence counts. Found 11 linked INIs, 58 unlinked DNIs, and lexical-prior leverage in a within-story diagnostic. These findings require a measurement revision; they are not an LLM failure result. See `experiments/E000_data_audit/RESULTS.md`.

Read and aligned seven paper PDFs, including direct ACL/EMNLP task neighbors and NAACL/EMNLP scientific-shape references. Corrected collisions: DiscourseEE already permits null slots; REGen already addresses grounding and specificity.

Created a subproject-only Python 3.12.3 .venv for the standard-library audit. Eight parser integrity tests passed. Source re-extraction and offline reproducibility verification are recorded separately when completed. Original run snapshots and raw responses remain immutable. No GPU/model experiment run; E001 remains a draft because its original negative-gold mapping is invalid.

## 2026-09-08 — E000b and second ownership audit

Pinned and audited the authors' revised UCCA repository at
`432bac16527299b389a0f964e34abf040e000f7c`. Reproduced all six type counts
(391 total) across 393 graph segments / 116 document IDs. Found 82 parent scenes
with differently typed implicit participants sharing generic Participant edges.
No frame-specific role identities or candidate-support labels were invented.
See `experiments/E000b_ucca_audit/RESULTS.md` and `data/SUPPORT_CONTRACT.md`.

Inspected DUST, RefNLI and CLAIRE in addition to the earlier direct extraction
neighbors. DUST materially narrows the novelty of detection-versus-interpretation
claims; RefNLI already gives reference assumptions a verification consequence;
CLAIRE annotates plausibility, not strict support. These are substantive ownership
and data-contract constraints, not merely publication-date comparisons.

Eight parser tests passed again; the E000b verification record includes 395 UCCA
file hashes, 26 reference/source checks and equality with earlier UCCA downloads.

## 2026-09-08 — E001a execution initiated

Frozen 42-example, 21-stratum interpretation challenge; 168 likelihood evaluations
per model, crossing sentence/full context and A/B label order. Started Qwen3-32B
on GPU 0 and Mistral-Small-24B-Instruct-2501 on GPU 2 using an existing local conda
environment read-only. BF16, no prompt truncation, no Qwen thinking. All caches,
scripts, rendered prompts and records are within L02. Other GPU processes left alone.
See `experiments/E001a_interpretation/EXECUTION_NOTES.md` for the tokenizer fix,
lexical-control limitation and shared-storage loading mitigation. Completion and
results must be logged after all frozen jobs finish; loading is not a result.

## 2026-09-08 — E000c source-coreference audit during model loading

Preserved 1,198 source Coreference edges over 1,328 mention spans / 142 classes.
178/256 NI link spans exactly match this graph. 14 linked records have a nonlocal
original span but a globally equivalent mention in the target sentence. The
source guide explicitly merges identities established later in the story; these
14 cases are not automatically locally recoverable. No new candidate-support
labels or heuristic equivalences were created. See E000c results and raw edge ledger.

## 2026-09-08 — E001a Mistral completion; exploratory E001b format validation

Mistral completed all 168 frozen jobs. Its raw argmax is A on every job: all
42 examples disagree across label orders in each context. The prespecified
order-averaged score is 23/42 sentence, 22/42 full, but this extreme format
sensitivity makes an interpretation-capability reading unsafe. Preserve the
raw outputs and `mistral_completed_analysis.json`; do not use this as evidence
against the scientific phenomenon.

Freeze E001b as a measurement check on the **same 42 items** in both contexts.
Remove the arbitrary A/B mapping and directly generate DNI/INI, greedily with
an eight-token ceiling. Keep definitions, context and role information unchanged.
No few-shot examples, sample exclusions or repeated prompt search. Exact native
labels only are valid; all invalid responses count in the all-42 denominator.
This is exploratory and triggered by E001a, not a preregistered method comparison.
The original E001a protocol and runs remain intact.

E001a both-model completion: 336/336 frozen records. Qwen order-averaged
accuracy is 20/42 sentence, 22/42 full, with 16/42 and 9/42 order disagreements.
Both models' full-context predictions strongly favor DNI. Full results and
limitations are in `experiments/E001a_interpretation/RESULTS.md`.

E001b Mistral completed 84/84 jobs with no invalid responses: 24/42 sentence,
20/42 full; 41/42 full-context responses are DNI. Native-label generation removes
the arbitrary letter mapping but does not yield a strong discriminative signal
on this fixed development selection. Qwen E001b is running under the same frozen
protocol; no prompt adjustment follows the Mistral result.

## 2026-09-08 — Completed validation and route verdict

E001b Qwen completed all 84 jobs with no invalid responses: 20/42 sentence and
20/42 full, with 41/42 full-context DNI predictions. Both native-label model
results are recorded in E001b RESULTS.md and analysis.json. No prompt search or
new exclusions followed either result.

Four-run verification passed: 504 prediction records, 42 identical source sample
IDs, matching protocol/script/input/output hashes, and exact E001b preservation
of context, roles and definitions. Both GPUs were released. Four E000b/E000c
artifacts reproduced byte-for-byte in separate replay directories.

Decision: NO-GO for the current Main research route. The reason is the invalid
candidate-support mapping plus lack of a distinctive extraction/selection
consequence beyond close work, not low model accuracy. H01–H03 are untested.
See RESEARCH_VERDICT.md for the reviewed alternatives and reopening conditions.
