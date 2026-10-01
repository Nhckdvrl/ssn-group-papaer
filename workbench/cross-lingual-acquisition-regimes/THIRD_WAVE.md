# Third Wave: Evidence Binding Versus Answer Realization

Status: exploratory; candidate gate not passed. No training authorized by this wave.

## Scientific Decision

The first two waves did not establish preferential reasoning gains in weak languages. Matched nominal JGP checkpoints also removed the large native-language loss gap seen in publication-selected exports. Do not rescue either explanation with prompt optimization.

This wave asks whether adding bilingual documents changes **selecting an answer using supplied evidence** differently from **realizing that answer in another language**. These are fact-retrieval diagnostics, not proofs of logical reasoning or a novel benchmark contribution.

## Fixed Pilot, Before Outcome Analysis

- Family: official German MONOWEB and MONOWEB+PARALLEL, nominal step 34,000. Same immutable model revision and tokenizer.
- Dataset: XQuAD English/German, revision `51adfef1c1287aab1d2d91b5bead9bcfb9c68583`.
- One pair of different questions per paragraph, with the same two candidate answers held fixed. Both questions have real annotations. No synthetic contradictory evidence.
- First 50 eligible paragraph pairs; five other, shortest eligible paragraphs supply demonstrations. Selection depends on annotations and length, not model outcomes.
- Dataset-order convenience pilot, with clustered article topics; not a representative estimate of XQuAD or a full reproduction of MONOWEB.
- Eight cells: context language x question language x answer language, each English/German. Two questions per pair. Exclude entire pairs across all cells if any prompt exceeds the context limit; no truncation.
- Raw conditional log likelihood for both answers with the full target paragraph and with that paragraph removed. Question-only still includes the same five demonstration contexts.
- Fixed-choice question binding averages the two oppositely signed gold margins. An additive answer preference cancels; question-type guessing does not, hence the question-only control.
- Greedy generation, 64-token cap, newline stop; preserve raw answers and score first-line EM/F1. Answer language is indicated by demonstration answers, not an explicit instruction. This changes demonstration content, so the answer-language contrast is not a pure generation-cost intervention.
- Separate pairs with different English/German answer strings from pairs with invariant strings (often numbers or unchanged names). Invariance is a lexical diagnostic, not a perfect semantic taxonomy.
- Resample paragraph pairs jointly across questions and cells. Exploratory 95% intervals, no familywise correction, one training seed per condition.

Data validation found five English answers in one paragraph with offsets shifted by one character. Exclude those IDs in **both** languages; record IDs, offsets and strings in run metadata. Do not silently repair annotations. Two initial attempts failed before scoring; they are not experiments or evidence.

## Gates

1. Validate generation and binding readouts away from format-induced floors. Inspect raw predictions; no outcome-driven prompt search.
2. If late-stage parallel gains concentrate in output-language-sensitive answers but not evidence binding, this would be consistent with an interface account, already partly owned by MONOWEB. Not sufficient novelty.
3. If evidence contribution differs, distinguish higher useful full-context performance from worse question-only performance. A positive interaction alone is insufficient.
4. A nominal 8,000-step comparison may test training-time dependence, but English and German acquisition, optimization and bilingual dose all co-vary. It cannot identify target-language acquisition as the cause.
5. Only a stable, non-floor interaction merits independent language/family confirmation and a mechanistic intervention. Otherwise close this branch and reconsider the scientific object. P4 remains closed.

## Ownership Expansion

- [XOR QA, NAACL 2021](https://aclanthology.org/2021.naacl-main.46.pdf), primary methods read: distinguishes retrieval, English answer-span selection, and target-language full answers. Extraction-versus-answer-translation decomposition is owned.
- [Cross-Lingual QA Attribution, EMNLP 2023](https://aclanthology.org/2023.emnlp-main.10.pdf), primary setup and attribution results read: gold-answer correctness need not imply support by retrieved evidence. Correctness-versus-grounding is owned; annotation measures attribution, not necessarily causal use.
- [Cross-Lingual BrowseComp-Plus, June 2026](https://arxiv.org/html/2606.15345v1), primary setup, oracle analysis and Appendix F read: supplied gold evidence does not remove the cross-language performance deficit; translating instructions into the target language can worsen oracle answers. Evidence-language-versus-instruction-language effects are owned. These are post-trained agents, not controlled bilingual-pretraining interventions; differences in setup do not alone guarantee novelty.

The potentially useful missing link is a **replicable intervention-conditioned dissociation**, not another report of cross-language QA difficulty. No claim that this missing link is unoccupied until a focused literature audit and independent-family test establish it.

### Further Acquisition And CPT Constraints

- [Second Language Acquisition of Neural Language Models, Findings ACL 2023](https://aclanthology.org/2023.findings-acl.856.pdf), primary training setup and Section 3 read: 18M masked LMs, four seeds, L1 pretraining then English L2. Translation-paired inputs underperform nonparallel pairs on BLiMP; alternating source-side removal does best. Authors propose lexical shortcuts as an explanation, not an established mechanism. Therefore neither grammar acquisition gains nor removing scaffolding is a new generic hypothesis. This is not decoder-only reasoning evidence.
- [PreAlign](https://arxiv.org/html/2407.16222v2), primary method, controlled synthetic setup and ablations read: alignment initialization and input-only codeswitching improve language modeling and synthetic cross-language factual application differently; dictionary coverage and timing are already studied. Source-trained factual transfer is distinct from using a passage supplied at inference. Do not relabel either distinction as novel.
- [EMMA-500 / MaLA, Findings ACL 2026](https://aclanthology.org/2026.findings-acl.937.pdf), primary mixture, Table 2 and deterministic-task appendix read: released monolingual/bilingual Llama 3/3.1 CPT families are a possible independent substrate. However, the monolingual mix trains 419B tokens and the bilingual mix 671B, with different warmup schedules and mixture proportions. Final-checkpoint contrasts cannot isolate explicit bilingual correspondence. Published resource-group gains are not measurements of initial language competence.

These readings motivate a **capability-type x objective x training-state** decomposition, but that decomposition itself is not a contribution. A paper needs an unexpected, replicated conditional effect plus an intervention that distinguishes its mechanism from data quality, supervision/readout, cumulative exposure and optimization history. More benchmark scores alone will not meet that gate.

- [Parallel Structures in Pre-training Data Yield In-Context Learning, ACL 2024](https://aclanthology.org/2024.acl-long.465.pdf), primary definition and ablation setup read: shared-template phrases in one context contribute to ICL, with gradient-based detection and token ablation. These are not necessarily bilingual translations. Nonetheless, a generic claim that repeated semantic structures teach context conditioning/ICL is already owned; multilingual instantiation needs a distinct intervention and prediction.

## Outcomes

### Late Stage Complete

Both nominal 34,000-step runs completed: 50 paragraph pairs, 100 questions, eight language cells, 800 rows per model. Zero oversized pairs. 41 pairs have language-sensitive answer strings; only nine are invariant. Raw generations are nonempty except one treated cell. Generation EM ranges 18-34%, so this is not a label-format floor.

Order below is context/question/answer language. Accuracy is fixed-choice raw likelihood; EM is greedy free generation. Changes are MONOWEB+PARALLEL minus MONOWEB in percentage points.

| Cell | Choice accuracy MWB -> MWB+P | Accuracy change | Generation EM MWB -> MWB+P | EM change |
| --- | --- | --- | --- | --- |
| en/en/en | 85 -> 87 | +2 | 34 -> 29 | -5 |
| en/en/de | 70 -> 70 | 0 | 23 -> 18 | -5 |
| en/de/en | 79 -> 78 | -1 | 27 -> 31 | +4 |
| en/de/de | 75 -> 76 | +1 | 20 -> 24 | +4 |
| de/en/en | 78 -> 79 | +1 | 23 -> 27 | +4 |
| de/en/de | 82 -> 71 | -11 | 29 -> 25 | -4 |
| de/de/en | 69 -> 70 | +1 | 24 -> 18 | -6 |
| de/de/de | 83 -> 80 | -3 | 31 -> 33 | +2 |

No general restoration of German output emerges. Nor do these noisy changes establish equivalence. The de/en/de accuracy change has exploratory pair-bootstrap CI [-18, -4] pp; both-questions-correct falls 66% -> 46%, CI [-32, -8] pp. This is one cell in a small convenience pilot, not yet a replicated harm claim.

**Do not mistake larger context contribution for better useful performance.** In de/en/de, full-context binding margin changes -0.217 nats, but question-only margin changes -0.921 nats. Consequently context contribution rises +0.704 nats, CI [0.209, 1.198], despite worse full-task accuracy. In de/en/en, the full-context margin does improve +0.450 nats, CI [0.017, 0.897], but choice accuracy changes only +1 pp and EM +4 pp, both uncertain. Both full scores and controls must accompany an interaction.

The answer-language EM interaction even changes sign with question language under German context: +8 pp for German questions, -8 pp for English questions. It is not a uniform target-language-generation benefit. Five-demo content and output-language compliance are remaining confounds; do not explain this by semantic acquisition yet.

Machine-readable estimates: `results/p2_qa_binding_34k.json`. No hypothesis promotion based on isolated uncorrected intervals.

### Early Stage

Nominal 8,000-step MONOWEB and MONOWEB+PARALLEL completed the same 50-pair likelihood assay, without free generation. Both match the late-stage actual prompt hash. Compare training-time interactions only on shared fixed-choice metrics; no early-generation result exists.

| Cell | Early choice accuracy MWB -> MWB+P | Early parallel effect | Late-minus-early effect, pp [exploratory 95% CI] |
| --- | --- | --- | --- |
| en/en/en | 80 -> 79 | -1 | +3 [-3, 10] |
| en/en/de | 65 -> 65 | 0 | 0 [-6, 6] |
| en/de/en | 72 -> 74 | +2 | -3 [-13, 7] |
| en/de/de | 67 -> 64 | -3 | +4 [-3, 10] |
| de/en/en | 70 -> 68 | -2 | +3 [-6, 12] |
| de/en/de | 72 -> 70 | -2 | -9 [-18, 0] |
| de/de/en | 67 -> 63 | -4 | +5 [-3, 13] |
| de/de/de | 75 -> 69 | -6 | +3 [-5, 11] |

No broad early-stage positive parallel effect appears. The early de/de/de accuracy change is -6 pp [-11, -1], another exploratory deficit, not an independently replicated result. MONOWEB early accuracy is already 65-80%; this is not an independently established weak-language regime. The de/en/en binding-margin interaction is +0.530 nats [0.019, 1.044], but context-contribution interaction remains uncertain; en/en/en context-contribution interaction is +0.712 nats [0.107, 1.319], not a selective cross-language improvement. These isolated intervals do not establish a training-state mechanism. Acquisition, learning-rate history and cumulative parallel dose remain inseparable.

Machine-readable estimates: `results/p2_qa_binding_8k.json` and `results/p2_qa_binding_time_interaction.json`.

## Decision After This Wave

**Do not promote the current QA dissociation or acquisition-regime account.** Useful readouts were obtained, but no consistent useful-performance interaction passed the gate. Lower the priority of expanding this assay to more German checkpoints or prompts. No P3 replication claim; no P4 training.

The late de/en/de deficit is a possible independent-confirmation target, not an established finding. To pursue it, require held-out article topics and another controlled language/family, check actual output-language compliance and lexical-overlap shortcuts, and distinguish useful full-context behavior from degraded controls. Do not scale solely to make an isolated interval significant.

At the field level, stop treating all parent outcomes as one scalar "reasoning" capability. Next scientific decisions should distinguish target-language grammar/semantic acquisition, parametric knowledge access, inference-time evidence binding, task/readout supervision and output transduction. Existing papers own generic versions of these distinctions. A defensible idea must add a falsifiable **intervention-conditioned mechanism**, not a taxonomy or another resource curve. The four-parent tension remains worth examining, but the current simple explanation has not survived these tests.

## Verification And Accounting

- Four new complete QA runs: 3,200 item-cell rows, only 50 paragraph pairs/100 questions reused across conditions. 1,600 free generations at late stage only.
- Total frozen/QA inventory: 31 runs, 88,716 item-cell rows, including corrupted-context and invalid-readout diagnostics. Independent text-loss measurements remain a separate 7,808 scores, not added to the QA inventory.
- Actual item hashes, completeness, key uniqueness and finite likelihoods checked. Pair-cluster bootstrap; no model-seed replication or multiplicity adjustment.
- Analyzer sanity test: a constant preference added to one answer cancels in opposite-question binding margin but still harms both-correct accuracy. Keep the two metrics separate.
- Python compilation and tracked diff whitespace checks passed. All inference/download sessions completed; no training launched. Model files remain in the standard HF cache, environment is existing `openslime` conda, GPUs are fvcrc10's previously idle cards.
- Post-run GPU check: our QA/scoring processes exited. Another user's 32B OLMo process now occupies fvcrc10's four GPUs; it was not interrupted. Re-inventory authorized machines before the next launch.
