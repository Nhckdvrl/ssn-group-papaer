# S05 — When Does Reading Become Learning?

**Status:** SELECTED — PILOT-AUTHORIZED  
**Registered:** 2026-09-18  

## One-sentence parent question

In standard response-only supervised fine-tuning, prompt/context tokens are read by the model but receive no direct prediction loss. **What determines whether information used only as a conditioning variable remains transiently used for the supervised response, is compressed into only the task-sufficient information needed for that response, or becomes persistent parameter memory?**

Short form:

> **When does information the model reads during training become information the model learns into its parameters?**

This is the parent question. Do **not** narrow S05 to prompt-loss tuning, privacy extraction, one specific fact type, or a method for context distillation.

---

## Scientific pressure

Ordinary response-only SFT minimizes a conditional objective of the form

`-log p_theta(y | x)`

where the prompt/context `x` participates fully in the forward computation but prompt tokens themselves contribute zero direct token loss. Therefore the model must often **use** information in `x` to predict `y`, but the objective does not explicitly say which information in `x` should become durable parameter memory.

This creates a natural distinction among three different notions of learning:

1. information is **read / represented transiently** while processing the training example;
2. information is **causally necessary for predicting the supervised response**;
3. information becomes **persistently recoverable from parameters after the original prompt is absent**.

These are not logically equivalent.

The question exists independently of any one recent anomaly. It follows directly from the semantics of conditional training.

---

## Competing worlds

### H1 — Task-sufficient bottleneck

Response-only SFT writes mainly the information required to predict the supervised response. Rich prompt-side details may be processed transiently but only a lower-dimensional task-relevant property becomes persistent.

Example: the prompt contains an 8-digit code but the response only depends on its parity. The model may learn the parity-relevant computation/property without memorizing the complete code.

**Prediction:** matched prompt exposure produces substantially stronger persistent traces for response-relevant information than for response-irrelevant details, and full-detail recovery remains weak even when the relevant statistic is learned.

### H2 — Incidental write-through

Information can leave durable parameter traces simply because it repeatedly participates in the computation that produces supervised responses, even when the response does not require that information.

**Prediction:** response-irrelevant prompt details can become persistently recoverable under matched exposure, despite zero direct prompt-token loss.

### H3 — Staged consolidation

Early training first acquires the response-sufficient computation, while continued optimization later begins consolidating instance-specific or response-irrelevant prompt information.

**Prediction:** task performance saturates before prompt-detail parameter traces emerge or sharply increase across checkpoints.

Hybrid regimes are allowed; the goal is to identify the law governing the transition from conditioning to persistent learning.

---

## Nearest-prior audit

### Prompt-loss work

**Huerta-Enochian & Ko, EMNLP 2024, _Instruction Fine-Tuning: Does Prompt Loss Matter?_** studies prompt-loss weight and downstream performance. The decisive unknown is whether/how much direct loss should be placed on prompt tokens, especially across response lengths.

**Shi et al., NeurIPS 2024, _Instruction Tuning With Loss Over Instructions_** adds loss over instructions/prompts and studies when this improves instruction tuning, with gains attributed largely to reduced overfitting in particular data regimes.

These papers establish that prompt-side loss changes learning, but they do not identify what ordinary response-only SFT selectively writes from its conditioning variables.

### Context / prompt distillation

**Snell et al., _Learning by Distilling Context_** and later context-parameterization work deliberately construct training procedures whose purpose is to internalize context into parameters. Very recent work such as **_Towards Evolving Context Parameterization for Large Language Models_ (2026-09)** continues this method/capability line.

These works ask how to intentionally transfer context into weights. S05 asks what standard response-only conditional training does **without** a dedicated context-distillation objective.

### Fine-tuning data extraction / memorization

Existing extraction work reports that prompt-side sensitive strings can leave detectable traces even under completion-only loss, especially with more training. This is important proof-of-existence: loss masking is not necessarily an information firewall.

However, the decisive unknown remains open: **what determines which conditioning-only information is written, which is only transiently used, and whether response relevance changes that writeability under matched exposure?**

### Reviewer compression to avoid

Do not allow S05 to be summarized as any of the following:

- `Does prompt loss matter?`
- `Can fine-tuning memorize private prompt data?`
- `Can we distill context into parameters?`
- `Do more epochs increase memorization?`

The registered parent is **the boundary between conditioning and parametric learning under ordinary conditional SFT**.

---

## Knowledge delta / novelty sentence

> Prior work studies whether prompt tokens should receive direct loss, shows that some loss-masked prompt content can nevertheless leave detectable traces after fine-tuning, and develops methods that deliberately internalize context into parameters. **What remains unknown is the causal boundary between conditioning and learning under ordinary response-only SFT: which information that a model reads from the prompt becomes persistent parameter memory, and what determines that transition?**

A useful conceptual sentence is:

> **Response-only SFT specifies what the model should predict from its inputs, but does not explicitly specify what from those inputs should become durable memory.**

---

## Identification logic

The minimum design must vary **causal relevance to the supervised response while matching exposure**.

Construct controlled examples containing multiple independently manipulable prompt-side fields. A target field appears with the same token frequency, entity frequency, prompt position, formatting, and number of optimizer exposures across conditions.

### Relevant condition

The supervised response depends on a low-dimensional property of the target field without copying the full field.

Example: prompt contains an 8-digit code; response requires only parity / a bucket / a deterministic low-dimensional function.

### Irrelevant condition

The same target field is present with matched exposure, but the response is determined by another independent field.

This creates the decisive intervention:

> **same information exposure, different necessity for predicting supervised outputs.**

Measure persistent parameter traces only after removing the original training prompt/context.

---

## Minimum pilot E01

Use one small open model (roughly 1B–3B is enough initially) and a small controlled micro-world.

1. Create fictitious entities with several independent fields.
2. Match field exposure exactly across relevant and irrelevant conditions.
3. Train with standard response-only / assistant-only loss.
4. Save several checkpoints through training.
5. Measure separately:
   - supervised task performance;
   - recovery/use of the **task-sufficient property**;
   - recovery/use of the **full prompt-side detail** under a novel query format;
   - likelihood discrimination of true values versus matched decoys.
6. Include a full-sequence-loss positive control to verify that the memory measurement can detect prompt-side learning when it is directly supervised.
7. Include a relevance-swap control in which the same field is response-relevant for one group and response-irrelevant for another.

The pilot should not require a benchmark, large annotation effort, judge model, or large-scale training.

---

## Informative outcomes

### Outcome A — selective task-sufficient writing

Response relevance strongly affects durable learning, but full irrelevant details remain weakly recoverable.

**Meaning:** ordinary conditional SFT behaves like an implicit information bottleneck: what survives into parameters is constrained by what is useful for predicting the target.

### Outcome B — broad incidental write-through

Matched response-irrelevant details become persistently recoverable nearly as strongly as relevant details.

**Meaning:** loss masking does not prevent conditioning information from becoming parameter memory; direct token supervision is not necessary for durable write-through.

### Outcome C — staged consolidation

Task performance/property learning saturates early, while full-detail or irrelevant-information traces rise later.

**Meaning:** the semantic content of a demonstration changes over training time: early optimization learns the task-sufficient computation, later optimization increasingly consolidates conditioning context itself.

### Outcome D — weak/no persistent prompt-side trace

Even relevant prompt-side details do not become recoverable once the original context is removed, except when directly supervised.

**Meaning:** standard response-only SFT may largely learn mappings/computations without internalizing instance-specific conditioning content; this sharply distinguishes ordinary conditional learning from deliberate context distillation.

All four outcomes answer the same mother question.

---

## Main-width argument

S05 is not a privacy paper and not a prompt-loss recipe paper. Its scientific object is **conditional learning**.

After removing model, dataset, metric, and method names, the intended knowledge statement remains:

> **Information can participate in training by being read, by being necessary for prediction, and by being consolidated into parameters; standard conditional training does not make these three notions equivalent.**

If a robust law links response relevance and training stage to persistent writeability, it changes how we interpret demonstrations in instruction tuning, tool/environment supervision, profile-conditioned training, and other conditional-learning settings without requiring those domains to become benchmark suites.

---

## Kill / demotion conditions

Kill or demote S05 if any of the following becomes true:

- a current prior already performs a matched-exposure intervention on **response relevance** under ordinary response-only SFT and measures persistent prompt-side parameter memory;
- apparent memory reduces to a training-example likelihood fingerprint and disappears under novel queries / functional transfer, leaving no broader learning distinction;
- response relevance has no reproducible relation to writeability and the only stable result is the trivial law `more epochs -> more memorization`;
- the effect requires extreme repeated overfitting that no longer resembles meaningful SFT;
- the project devolves into privacy attack accuracy, prompt-loss hyperparameter tuning, or a context-distillation method;
- the controlled task cannot separate task-sufficient information from full-detail memorization;
- the paper's conclusion becomes specific to codes, entities, or one synthetic format rather than a general conditional-learning law.

---

## Registration verdict

**SELECTED — PILOT-AUTHORIZED.**

Registered parent question:

> **Under ordinary response-only SFT, what determines whether information used as conditioning remains transient, is compressed into task-sufficient knowledge, or becomes persistent parameter memory?**


---

## Rescinded re-audit — former KILL (2026-09-19)

**RESCINDED:** this kill decision was withdrawn after a fresh prior/feasibility audit. S05 remains experiment-authorized.

### Why it is killed

The decisive problem is not that prompt-side learning is impossible. It is that the scientifically interesting version is unlikely to remain stable outside a heavily controlled memorization regime.

1. **The natural null is already unsurprising.** Context-distillation work exists precisely because contextual gains often disappear when the context is removed. If ordinary response-only SFT leaves little persistent prompt-side memory, that is no longer a strong Main-level surprise.

2. **Broad incidental write-through is already occupied.** EACL 2026, *Unintended Memorization of Sensitive Information in Fine-Tuned Language Models*, directly studies information that appears only in fine-tuning inputs, not targets, including task-irrelevant input-only information, with synthetic and real data and analyses of task type, repetition, model size and other factors. This substantially narrows S05's remaining novelty to the matched causal effect of response relevance.

3. **The remaining interesting effect is likely dose/recipe dependent.** To make persistent memory of arbitrary prompt-only details measurable, the experiment would likely require repeated exposure, stronger learning rates, or other memorization-amplifying choices. At that point the project risks answering “under this fine-tuning dose, this kind of input leaks into parameters” rather than identifying a stable law of conditional learning.

4. **The task-sufficient outcome is hard to separate from ordinary function learning.** If the response depends only on a low-dimensional property of the input and the model later retains that property, a reviewer can reasonably read the result as learning the input→output mapping rather than storing the original conditioning information.

5. **S04-style construct risk.** The clean causal contrast requires a synthetic micro-world; if native ordinary SFT produces too little persistent input-only memory, making the phenomenon visible would require increasingly artificial repetition/structure. That risks turning the identification instrument into the phenomenon itself.

### Final verdict

**KILL.**

Do not revive S05 by:
- adding more epochs until prompt memory appears;
- adding model families;
- turning the project into privacy/extraction;
- comparing prompt-loss weights;
- reframing a synthetic overfitting regime as a universal SFT law.

A future topic may reuse the broader distinction between transient conditioning and persistent learning only if a new natural phenomenon creates independent pressure and can be identified without relying on an artificial memorization regime.


---

## Restoration audit — KEEP / PILOT-AUTHORIZED (2026-09-19)

The previous kill was too aggressive and is formally rescinded.

### Why S05 survives the recipe-risk audit

1. **The decisive variable is within-run causal relevance, not training stage.** Relevant and irrelevant prompt-side facts can be exposed inside the same model, same optimizer state, same batches, and same SFT recipe. This differs materially from reconstructing a capability from incomparable post-training stages.

2. **EACL 2026 strengthens the scientific pressure rather than covering the question.** *Unintended Memorization of Sensitive Information in Fine-Tuned Language Models* directly establishes that input-only, target-absent information can be memorized and explicitly hypothesizes that textual context and utility to the downstream task matter. It does not perform the matched intervention S05 needs: hold the same information exposure fixed and change only whether that information is causally necessary for predicting the supervised response.

3. **The pilot need not manufacture memorization by extreme overfitting.** Use an ordinary short SFT dose ladder and a direct-supervision positive control. If no persistent prompt-side trace is detectable at reasonable doses, kill quickly rather than increasing epochs until an effect appears.

4. **Recipe variation is a robustness check, not the scientific variable.** The first decision can be made with one standard optimizer and two modest training doses. Only if a clean relevance effect appears is one confirmatory recipe variation needed; a full optimizer/model zoo is not required.

### Tightened pilot gate

- one small open model;
- ordinary response-only SFT;
- matched relevant vs irrelevant information in the **same run**;
- two modest doses, not a large sweep;
- direct-supervision positive control;
- measure task-sufficient property and full-detail memory separately;
- if the qualitative relevance effect changes sign across the two doses or only appears after obvious overfitting, **KILL**.

### Final status

**SELECTED — PILOT-AUTHORIZED.**

---

## 2026-09-19 execution-risk re-audit — KEEP / PILOT-AUTHORIZED

S05 survives the S03-informed recipe audit because its causal variable is **within-run response relevance under matched exposure**, not a post-hoc label for a training stage/history.

Relevant and irrelevant prompt-side information can coexist in the same batches, optimizer state and SFT run. Recipe therefore acts primarily as a nuisance variable.

### Tightened execution gate

- one small open model;
- one standard response-only SFT recipe;
- two modest training doses;
- relevant vs irrelevant fields mixed within the same run;
- direct-supervision positive control;
- measure task-sufficient property and full-detail memory separately.

**KILL immediately** if:
- the relevance effect changes qualitative direction across the two modest doses;
- persistent input-only memory appears only after obvious overfitting / aggressive LR;
- the only stable law is “more training produces more memorization”;
- the result collapses to ordinary function learning without persistent prompt-side information.

Do not expand to model/optimizer sweeps to rescue an unstable effect.

**Final status: KEEP — PILOT-AUTHORIZED.**

---

## 2026-09-19 data-path audit

**Data burden: LOW–MEDIUM.**

The core dataset should be generated deterministically from fictitious entities/fields. Ground truth is exact; no annotators or judge model are needed. Relevant/irrelevant conditions must be created by swapping which field controls the response while holding tokens/exposure matched.

A few thousand training examples and a few hundred evaluation queries are enough for the pilot.

**KILL on data grounds** if:
- natural-looking examples require large manual authoring;
- persistent memory can only be exposed by building a large extraction benchmark;
- the generator leaks relevance through surface templates;
- validating “memory” requires subjective judge-model scoring rather than exact/functional queries.

