# Selected Topics — Sasano-Taste Search

Started: 2026-09-16

Purpose: record only questions that survive real nearest-prior novelty checking, fit Sasano/Main scientific taste, and whose **actual experiment is itself scientific rather than mainly an evaluation exercise**.

## Admission rule

A topic can enter this file only when all of the following are true:

1. **Worth asking:** the question is understandable without elaborate framing and there is a natural reason a reviewer would want to know the answer.
2. **Real difference:** nearest prior work does not already answer the same parent question; the difference is not merely a new model, dataset, language, condition, or exact experimental cell.
3. **Correct scientific width:** the parent RQ, claim scope, and Related Work neighborhood are calibrated against ACL / EMNLP / NAACL Main and Sasano-approved work.
4. **Scientific experiment, not evaluation disguised as science:** after stripping away the Introduction rhetoric, the main experiment must study a phenomenon, learning/representation/behavioral law, causal relation, trade-off, or natural process. If the work reduces to constructing a dataset and comparing methods/metrics/robustness/leaderboards, do not select it.
5. **Data path is natural and realistic:** do not require large synthetic benchmark construction, hard-to-obtain ground truth, or an artificial dataset merely to make the question measurable.
6. **Exploratory rather than anomaly gambling:** several plausible outcomes should remain scientifically interpretable, but this alone is not sufficient for selection.
7. **Feasible:** there is a cheap initial experiment that directly reduces uncertainty without large pretraining or a massive annotation campaign.

Mechanistic depth, surprising results, large model sweeps, and complex methods are not admission requirements.

---

## Current selections

### S03 — From Document End to Task Done: What Does Post-Training Teach a Model About When to Stop?

**Status:** SELECTED — PILOT REQUIRED BEFORE PAPER-MAINLINE PROMOTION  
**Registered:** 2026-09-17

**Research question.** Pretraining teaches an autoregressive LM when a document or text sequence ends. Instruction tuning requires a different decision: whether the assistant has satisfied the user's current goal and should end its turn. Does post-training mainly **reuse/retune the pretrained document-completion computation**, or does it learn a **new goal-conditioned task-completion signal** that can dissociate from ordinary textual closure and response-length priors?

**Why this is a natural Sasano-style question.** The puzzle exists independently of any one recent paper. Modern model families explicitly distinguish pretraining document-end markers from post-training end-of-turn markers: e.g. Qwen documents `<|endoftext|>` as end-of-document and `<|im_end|>` as end-of-turn; Llama 3.3 documents `<|end_of_text|>` for base-model text termination and `<|eot_id|>` for when the model judges that it has finished interacting with the initiating user message. The scientific object is therefore not a token-format quirk but a changed learning problem: a text continuer becomes an assistant that must decide when a goal has been completed.

**Competing explanations.**

1. **Reuse / retuning.** Post-training largely reuses the pretrained notion of sequence/document completion, perhaps changing only its readout or calibration. Apparent semantic stopping follows textual closure, response shape, and length priors already latent in the base model.
2. **New task-completion computation.** Instruction-response training creates a goal-relative completion signal: with the generated prefix held fixed, whether the user-requested quantity has been satisfied causally changes the stop decision, beyond textual closure and length.
3. **Hybrid.** Pretrained closure machinery supplies a reusable substrate, while post-training adds a goal-conditioned component that becomes decisive only for assistant-turn termination.

**Nearest-prior audit.** The parent question is not currently owned by the nearest work found through 2026-09-17.

- Yue et al. (ACL 2024 Main), *Less is More: Mitigating Multimodal Hallucination from an EOS Decision Perspective*, shows that an LMM's EOS decision can reflect completeness by comparing generated text with an image. It owns semantic EOS/completeness in a multimodal hallucination setting, but does not study the pretraining-to-instruction-tuning transition or document-end versus user-goal completion.
- Hewitt et al. (2024), *Instruction Following without Instruction Tuning*, shows that response-only and single-task tuning can induce broad instruction following and gives a rule-based adapter whose ingredients include gradually increasing EOS probability. It shows that simple distributional changes can elicit assistant-like behavior, but does not identify what teaches a model that a particular user goal is complete or whether that signal reuses pretrained document-end computation.
- Pal (2026), *Prerequisite-Conditioned Causal Continuation Gating in a Language Model* / PCCG-2, engineers a condition-dependent continuation/EOS gate and causally flips GO versus EOS. The released work explicitly bounds itself as an engineered gate rather than a discovered natural circuit in stock Qwen; it demonstrates that continuation control can be separated from content, not how ordinary instruction post-training naturally acquires task-relative termination.
- 2026 work on response-length planning / over-expansion shows that instruction tuning can create response-length or planning structure and stopping pathologies. That occupies generic post-training length planning, not the distinction between textual/document closure and goal satisfaction.
- LIMA and modern model-format specifications provide structural motivation by separating conversation end-of-turn from pretrained sequence-end semantics, but do not answer the scientific question.

**Reviewer compression that must remain true.** The paper must be describable as:

> *This work asks how post-training changes the meaning of completion in a language model, and uses matched and causal interventions to distinguish reuse of pretrained document-ending computation from newly learned goal-conditioned task completion.*

If the work later compresses to “an EOS/EOT analysis on newer chat models”, “ACL-2024 completeness but text-only”, or “a stopping benchmark”, revoke selection.

**Minimum E01 — identify goal-relative stopping without changing the response prefix.** Construct small matched families in which the assistant prefix is token-for-token identical but the user goal differs only in whether that prefix already satisfies it. Example: “output the first 3 items” versus “output the first 4 items”, replaying the same three-item assistant prefix. Measure the native end-of-turn token against the correct next-content token. Include a continuation-awareness check: the incomplete-goal condition must assign strong probability to the specific missing item, so a null EOT effect cannot be blamed on failure to understand the instruction.

E01 must cross at least two non-isomorphic operations (e.g. bounded list extraction and multi-part question answering / constrained copying), with length, punctuation, lexical suffix, and assistant-prefix tokens exactly matched inside each pair. The purpose is identification, not creation of a benchmark.

**E01 gate.** Continue only if there is a robust within-prefix goal-completion effect on native turn termination while continuation-awareness is present. A pure length/punctuation/textual-closure account, or an effect that disappears under minimal paraphrase / second operation family, is a STOP or reformulation trigger.

**Minimum E02 — identify the learning source / reuse question.** Use a small open base model with a matched post-trained derivative or perform bounded SFT from one base checkpoint. The experiment must include controls that separate goal-conditioned acquisition from generic response-distribution adaptation. A preferred design is a shared-response training comparison with: (a) normal instruction-response pairing, (b) response-only tuning with the same responses and termination targets, and (c) mismatched/shuffled instruction-response pairing, followed by the frozen-prefix goal-completion test. In parallel, compare the pretrained document-end signal with the post-trained turn-end signal using same-family checkpoints and a causal/representation-transfer test only if the transfer is interpretable.

This design distinguishes whether task-relative stopping requires learning the instruction-response relation or can emerge from marginal response-shape / generic EOS calibration alone. Do not claim “reuse” versus “new circuit” from representational similarity alone.

**Data and cost.** No large annotation or synthetic benchmark is required. Controlled matched examples are an identification instrument and can be instantiated from simple natural lists, existing QA/extraction data, or public instruction-response corpora. E01 is inference-only. E02 can use a 0.5B–4B open model and a small SFT corpus; the first decision should fit within a modest local-GPU budget.

**Why this is not evaluation-centric.** The manipulated quantity is whether the user goal has been satisfied while the generated response prefix is held fixed, and the scientific target is how post-training changes the model's termination computation. The central result should be a causal/learning-source decomposition, not `model × benchmark × score`.

**Interpretable outcomes.**

- Strong goal effect only after paired instruction-response training → evidence that task-relative completion is genuinely acquired from the conditional relation, not merely response style or length.
- Similar goal effect after response-only / mismatched tuning → evidence that stopping is largely inherited or induced by generic response-distribution adaptation; the “new task-completion computation” account weakens.
- Base document-end signal causally transfers to post-trained turn-end decisions → evidence for reuse/retuning.
- Goal-relative effect is present but causal transfer is weak → evidence for a post-training-specific component.
- No robust goal-relative effect despite correct continuation awareness → important negative result: assistant stopping is much more dominated by textual/length priors than natural interaction suggests; reassess Main scope after E01.

**Kill conditions.** Kill or demote if a newly found paper directly owns the pretraining document-end → post-training task-end acquisition question; if the only surviving result is generic EOS probability/response-length behavior; if E01 requires model-shopping or prompt-search to appear; if E02 cannot distinguish paired goal learning from generic response adaptation; or if the central output becomes a stopping benchmark or method comparison.

**Current selected topic count = 1.**

### Explicitly cancelled registrations

- **S01 — Omission ≠ Neutrality / effective default semantics in tool calls:** cancelled/demoted. It is already recorded as F06 in `FAILED_TOPICS.md`; the Main-level parent compresses to underspecified tool intent / argument completion, leaving only an exact API-default subcase.
- **S02 / C2 — AI Rewrite ≠ Semantic Change:** registration cancelled. The high-level framing looked scientific, but the actual experimental object collapses into synthetic rewrite-data construction + semantic-preservation validation + comparison of LSC methods/metrics/robustness. Real post-LLM corpora lack clean semantic-change ground truth; synthetic paired rewrites provide ground truth only by making the central data artificial. This is precisely the evaluation/benchmark/metric-validity direction the search should avoid.

Do **not** revive either topic by adding more models, more datasets, more metrics, or broader rhetoric.
