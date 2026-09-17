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

### S03 — From Document End to Task Done: How Does Post-Training Acquire Goal-Relative Stopping?

**Status:** SELECTED — PILOT-AUTHORIZED; CLAIM FROZEN BEFORE RUNS  
**Registered:** 2026-09-17  
**Re-audited:** 2026-09-17

**One-sentence parent question.** A pretrained language model already has a learned action for “this text/document ends here.” When it becomes an assistant, how is information about **the user's goal being complete** connected to that stopping action: was the needed information already present and post-training mainly changes the readout, or must post-training change the model's internal state/computation before goal completion can control termination?

This is the parent. Do not broaden it to “how instruction following works”, “whether models represent goal satisfaction”, “how models plan response length”, or “what the EOS circuit is”.

**Why the question exists independently of any trigger paper.** Pretraining and assistant use impose different completion criteria. A pretrained LM predicts boundaries in text/documents; an assistant should stop when the current requested job is done, even when the same response prefix could legitimately continue under a different request. Modern chat systems often make this distinction explicit with a separate end-of-turn token. OpenChat even motivates a distinct end-of-turn token as avoiding confusion with the EOS meaning learned during pretraining. The scientific problem therefore exists even if all recent interpretability papers disappeared: what changed between “text ends” and “task is done” when a continuer becomes an assistant?

## Claim boundary: what S03 is and is not allowed to claim

S03 does **not** claim to discover a generic goal-satisfaction representation, a universal instruction-following mechanism, a new EOS circuit, or the fact that post-training creates response-length planning. Those parent claims are already occupied or too close to existing work.

The only defensible contribution is:

> **identify where goal-relative stopping is acquired between pretraining and post-training, by separating pretrained textual-closure propensity from user-goal completion and by intervening on the parameter locus that can change the stop action.**

A reviewer should be able to compress the paper to:

> *The paper asks how a pretrained document-ending behavior becomes goal-relative assistant stopping, and distinguishes readout reuse from post-training-induced state/computation change under matched stopping decisions.*

If the eventual paper instead compresses to “an EOS analysis”, “a stopping benchmark”, “instruction tuning creates a completion representation”, or “we found a stopping direction”, revoke selection.

## Nearest-prior audit and exact ownership boundary

The strongest nearby papers do not currently own this acquisition question, but they sharply constrain the claim.

1. **Yue et al., ACL 2024 Main — _Less is More: Mitigating Multimodal Hallucination from an EOS Decision Perspective_.** They show that an LMM's EOS decision reflects sequence completeness relative to an image and use this to mitigate hallucination. They own semantic completeness influencing EOS in a multimodal model. They do **not** study the pretraining → instruction/post-training transition, document-end versus user-goal completion, or which part of the model must change for task completion to control stopping.

2. **Hewitt et al., 2024 — _Instruction Following without Instruction Tuning_.** Response-only tuning and narrow-domain tuning can elicit broad instruction following; their constructive rule-based adapter also includes gradually increasing EOS probability. Therefore S03 must **not** use “paired instruction-response supervision is necessary” as its central identification claim, and the old paired-vs-response-only E02 is rejected. This work does not isolate goal-relative termination or decompose whether stopping is inherited in pretrained states versus acquired through state/readout changes.

3. **Potraghloo et al., 2026 — _One Token Away from Collapse: The Fragility of Instruction-Tuned Helpfulness_.** They report prompt-level response-length/planning structure in instruction-tuned models that is absent in their base-model probes. Therefore S03 cannot claim novelty from “post-training creates a planning/completion representation”. Their object is constraint-induced response collapse and response-length planning, not acquisition of the stop action from pretrained document closure.

4. **Rocchetti & Ferrara, 2026 — _How LLMs Follow Instructions: Skillful Coordination, Not a Universal Mechanism_.** They find task-specific, temporally dynamic constraint monitoring rather than one universal compliance mechanism. Therefore S03 cannot claim novelty from merely detecting goal/constraint-satisfaction information during generation. They do not study termination as the dependent action or the base → post-training acquisition locus of that action.

5. **Pal, 2026 — PCCG / PCCG-2.** These works causally engineer prerequisite-conditioned continuation control and, in PCCG-2, alter native EOS while frozen content logits remain unchanged. They establish that stopping/continuation can be separated from content and controlled by a small learned gate. The released work explicitly bounds itself as an **engineered** continuation gate rather than a naturally discovered circuit in stock Qwen. It does not answer how ordinary post-training transforms pretrained text-ending behavior into goal-relative stopping.

6. **Instruct Vectors, 2026.** A frozen base model can be pushed toward assistant-like behavior, including proper EOS use, with learned low-dimensional steering parameters. This is important adjacent evidence that much assistant behavior may already be latent in the base model. It strengthens the need for S03's readout-vs-state identification but does not isolate goal-relative stopping or textual closure versus task completion.

7. **OpenChat, ICLR 2024.** It uses a distinct end-of-turn token that functions like EOS while avoiding confusion with EOS semantics learned during pretraining. This is structural motivation for the scientific distinction, not an answer to the acquisition question.

**Novelty verdict as of 2026-09-17:** no located paper directly owns the parent question “how does pretrained text/document completion become goal-relative assistant termination, and is the required change primarily in the stop readout or in internal state/computation?” S03 survives, but only under this narrow parent.

---

## E01 — Establish the natural phenomenon with an exact-prefix goal intervention

The first experiment must show that an ordinary instruction-tuned model's native end-of-turn decision is genuinely **goal-relative**, not merely correlated with response length, punctuation, or textual closure.

For each item, hold the assistant prefix **token-for-token identical** and change only the user's requested stopping condition.

Example family A — bounded extraction:

- complete goal: “Return the first **3** entries.”
- incomplete goal: “Return the first **4** entries.”
- replay the exact same assistant prefix containing entries 1–3.

Example family B — semantic slot completion:

- complete goal: request fields A and B.
- incomplete goal: request fields A, B, and C.
- replay the exact same assistant prefix containing correct A and B.

The second family must not reduce to another counting/list-length task.

**Primary stop quantity.** For each exact-prefix pair, compare the native stop token against the first correct missing continuation token from the incomplete condition:

`stop_margin = logit(EOT) - logit(next_missing_token)`

Use the same competitor token inside the pair. The key estimand is the within-prefix change in `stop_margin` caused by changing only whether the user goal is already satisfied.

**Continuation-awareness control.** In the incomplete condition, the model must assign substantial probability/rank to the correct missing continuation. Otherwise a low stop rate could be uninterpretable because the model simply does not know how to continue.

**Textual-closure control.** Record the corresponding base model's native EOS propensity on the same response prefix under a neutral/plain continuation format. Use that as a continuous pretrained textual-closure score. E01 must contain prefixes spanning both high and low base-EOS closure. The decisive pattern is a goal effect inside exact-prefix pairs that cannot be reduced to this pretrained closure propensity.

**E01 gate.** Continue if the goal-completion intervention reliably shifts native stop margin in at least two non-isomorphic operation families, with correct continuation awareness and without prompt/model shopping. Kill or reformulate if the effect exists only in one counting-style family, disappears under minimal paraphrase, or is explained almost entirely by base textual-closure propensity.

---

## E02 — Minimal acquisition-locus experiment

The old E02 (`paired instruction-response vs response-only vs shuffled`) is **retired**. Hewitt makes that decomposition too easy to compress into generic implicit instruction tuning, and it still does not identify whether the stopping computation itself is inherited or newly formed.

The replacement is a matched parameter-locus intervention from one small open base checkpoint. Use the **same native EOS token in every controlled arm** so token identity cannot masquerade as a scientific result. Train/evaluate all arms on the same plain instruction-response format and the same small corpus.

Let the model be conceptually split into internal computation/state `h_θ` and the native EOS output row/readout `w_EOS`.

### Arm 0 — Native base

No adaptation. Measure whether pretrained EOS already shows any goal-relative stop effect under the exact-prefix E01 instrument.

This is the actual “document/text ending” baseline.

### Arm R — Readout-only

Freeze the entire transformer and every non-EOS output row. Train only the native EOS output row (and EOS bias if the architecture has one) to distinguish response-internal continuation positions from true assistant-response boundaries.

This asks:

> **Are pretrained hidden states already sufficient for goal-relative stopping, such that post-training only needs to attach/recalibrate a stop readout?**

Because all non-EOS logits and all hidden states are frozen, success cannot be attributed to newly learned internal goal computation.

### Arm S — State-only

Freeze the native EOS output row at its pretrained value. Adapt the model's internal parameters on the same instruction-response data while keeping the stop readout fixed.

This asks:

> **Can post-training make goal completion drive the old document-end action by changing internal state/computation alone?**

This arm is the one missing from the previous three-stage design. Without it, `readout-only fails; full SFT succeeds` would not identify where the extra learning occurred.

### Arm F — Full SFT

Adapt both the internal model and the EOS readout on the same data. This is the unconstrained positive-control/interaction ceiling and should recover ordinary assistant stopping if the setup is healthy.

### Why the four arms are the minimum identified design

The pattern across `Base / Readout-only / State-only / Full` directly distinguishes parameter-locus explanations:

- **Base already goal-relative:** much of the information→stop mapping predates post-training; post-training mainly calibrates or changes interaction format.
- **Readout-only succeeds, Base weak:** base representations already contain the needed goal information, but pretrained EOS does not read it out appropriately.
- **State-only succeeds, Readout-only weak:** post-training must reorganize internal state so the old EOS readout can act on user-goal completion.
- **Both constrained arms partly succeed, Full strongest:** hybrid acquisition; stopping uses both inherited information/readout structure and post-training state/readout adaptation.
- **Only Full succeeds:** interaction between state and readout changes is load-bearing; simple “reuse” versus “new representation” is false.

The claim is about **sufficiency under controlled parameter interventions**, not metaphysical proof that a unique natural circuit exists.

### Optional secondary analysis — paired released base/instruct checkpoints

Only after E02 works, use a real same-family base/instruct pair as ecological validation. Compare their exact-prefix goal effects and, if hidden-state geometry is stable enough to make it interpretable, attempt stop-row/state swaps or limited causal transfer. This is **not** required for the first pilot and representational similarity alone is not evidence for reuse.

---

## Data, scale, and feasibility

No benchmark construction is required. The controlled items are identification instruments, not the paper's contribution.

- **E01:** tens to low hundreds of exact-prefix matched pairs across two operation families; inference only.
- **E02:** one 0.5B–1.7B base model for the first pilot, one small public instruction corpus or a few thousand ordinary instruction-response examples, and three lightweight adaptation runs beyond the base (`R`, `S`, `F`).
- Use one seed to decide whether the phenomenon/design works; add seeds/models only after the effect and identification are real.
- Do not start with a model zoo, benchmark suite, or mechanistic circuit hunt.

## Interpretable outcomes

Every major E02 pattern answers the same scientific question, so this is exploratory rather than anomaly gambling.

1. **Mostly readout acquisition** — goal information is already accessible in pretrained states; post-training mainly learns when that information should trigger termination.
2. **Mostly state/computation acquisition** — document-end readout is reusable, but post-training must transform internal state so task completion becomes visible to it.
3. **Hybrid acquisition** — both state and stop readout change, with neither alone reproducing full goal-relative stopping.
4. **Little post-training acquisition** — base models already exhibit a substantial goal-relative EOS mapping in plain instruction contexts; the scientific story shifts toward calibration/formatting rather than new completion semantics.
5. **No robust goal effect despite continuation awareness** — assistant stopping is more dominated by surface/textual closure than the intuitive “task done” story suggests; reassess Main scope after E01 rather than forcing a mechanism paper.

## Kill conditions

Kill or demote S03 if any of the following occurs:

- a newly located paper directly owns the base-document-end → post-training goal-end acquisition question;
- E01 requires prompt search/model shopping or survives only in one artificial counting family;
- the result is explainable by token-format/configuration errors (wrong EOS/EOT wiring, padding/EOS masking, generation stop-list differences);
- E02 cannot maintain the parameter freezes cleanly enough to support the readout-vs-state inference;
- the project drifts into “find a stopping direction/circuit” without first establishing the acquisition law;
- the main output becomes a benchmark/model comparison rather than a learning-source result.

## Pilot order

1. **E01 first** on one same-family base/instruct pair. If exact-prefix goal-relative stopping is not clean, stop.
2. If E01 passes, run **Arm R** on a ≤1.7B base model. This is the cheapest high-information test.
3. Then run **Arm S** and **Arm F** using the identical corpus/setup.
4. Only after the four-arm pattern is clear should we add a second model family or mechanistic localization.

**Current selected topic count = 1.**

### Explicitly cancelled registrations

- **S01 — Omission ≠ Neutrality / effective default semantics in tool calls:** cancelled/demoted. It is already recorded as F06 in `FAILED_TOPICS.md`; the Main-level parent compresses to underspecified tool intent / argument completion, leaving only an exact API-default subcase.
- **S02 / C2 — AI Rewrite ≠ Semantic Change:** registration cancelled. The high-level framing looked scientific, but the actual experimental object collapses into synthetic rewrite-data construction + semantic-preservation validation + comparison of LSC methods/metrics/robustness. Real post-LLM corpora lack clean semantic-change ground truth; synthetic paired rewrites provide ground truth only by making the central data artificial. This is precisely the evaluation/benchmark/metric-validity direction the search should avoid.

Do **not** revive either topic by adding more models, more datasets, more metrics, or broader rhetoric.
