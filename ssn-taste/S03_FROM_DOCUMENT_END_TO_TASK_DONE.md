# S03 — From Document End to Task Done

**Status:** SELECTED — PILOT-AUTHORIZED  
**Registered:** 2026-09-17  
**Target venues:** ACL / EMNLP / NAACL Main  
**Scientific type:** capability acquisition / post-training dynamics + controlled parameter intervention

## 1. Stable parent question

A pretrained language model already learns when a text or document ends. An assistant, however, should stop when the **user's requested task is complete**, even when the exact same response prefix could legitimately continue under a different request.

The stable parent question is:

> **How does post-training turn pretrained document/text-ending behavior into goal-relative assistant stopping?**

More specifically:

> **Is the information needed for goal-relative stopping already present in pretrained states and post-training mainly changes the stop readout, or must post-training change internal state/computation before user-goal completion can control termination?**

This is the scientific object. Do not broaden the paper into generic instruction following, response-length planning, goal-satisfaction representation, EOS interpretability, or a universal stopping circuit.

## 2. Why this is a real question

Pretraining and assistant use impose two different completion criteria:

- **textual/document completion:** does this sequence look like it should end here?
- **task completion:** relative to the user's current request, has the requested job already been completed?

The distinction is identifiable because the **assistant prefix can be held token-for-token identical while only the user goal changes**. For example, the same three-item answer should stop if the user requested three items, but should continue if the user requested four.

The paper is therefore not about whether EOS correlates with semantic completeness. It is about **how goal information becomes connected to the stopping action during post-training**.

## 3. Claim boundary

The contribution is allowed to claim only what the experiments directly identify:

> **where the information→stop mapping is acquired between pretraining and post-training, after separating textual closure from goal completion and intervening on which parameters are allowed to change.**

Do **not** claim any of the following as the main novelty:

- that LLMs contain a generic goal-satisfaction representation;
- that instruction tuning creates response-length planning;
- that there is one universal instruction-following mechanism;
- that we discovered a unique natural EOS circuit;
- that task completion affects EOS at all;
- that a new benchmark measures stopping better.

A good reviewer compression is:

> *The paper asks how pretrained document-ending behavior becomes goal-relative assistant stopping, traces when the transition appears across post-training, and uses controlled parameter interventions to determine whether the change is primarily in the stop readout, internal computation, or their interaction.*

If the eventual project is more naturally summarized as “EOS analysis”, “stopping benchmark”, “we found a completion direction”, or “one more instruction-following probe”, the topic has drifted.

## 4. Nearest-prior ownership boundary

The nearby literature constrains the claim but does not currently own the same parent question.

- **Yue et al., ACL 2024 Main — _Less is More: Mitigating Multimodal Hallucination from an EOS Decision Perspective_.** Owns the finding that EOS in multimodal generation can reflect sequence completeness relative to the input. Does not study base→post-training acquisition or document-end→user-goal-end transition.
- **Hewitt et al. — _Instruction Following without Instruction Tuning_.** Shows broad instruction-following behavior can emerge from response-only/narrow tuning and that simple output-side changes can matter. This kills the old paired-vs-response-only identification idea, but does not isolate goal-relative stopping acquisition.
- **Potraghloo et al., 2026 — _One Token Away from Collapse_.** Occupies post-training-induced response-length/planning structure. S03 must not sell “instruction tuning creates planning/completion representation”.
- **Rocchetti & Ferrara, 2026 — _How LLMs Follow Instructions: Skillful Coordination, Not a Universal Mechanism_.** Occupies dynamic/task-specific monitoring of instruction satisfaction. S03 must not sell the mere existence of goal/constraint-satisfaction information.
- **PCCG / PCCG-2.** Shows an engineered learned gate can causally control continuation/EOS while separating content generation from permission to stop. This raises the bar for causal identification, but it does not explain how ordinary post-training naturally acquires goal-relative stopping.
- **OpenChat / modern chat templates.** Structurally motivate the distinction between pretraining EOS and turn/task termination, but do not answer the acquisition question.

The novelty survives only if the project continues to center on **acquisition of the information→stop mapping**.

## 5. Recommended natural model family: OLMo 2

OLMo 2 is the preferred first family because it exposes the training chain and keeps the stopping interface unusually clean for this question.

Recommended 1B trajectory:

- `allenai/OLMo-2-0425-1B` — Base
- `allenai/OLMo-2-0425-1B-SFT` — SFT
- `allenai/OLMo-2-0425-1B-DPO` — DPO
- `allenai/OLMo-2-0425-1B-Instruct` — final post-training / RLVR

Why this family is attractive:

1. Ai2 releases model weights, training details, data recipes, and stage checkpoints for scientific study.
2. The OLMo 2 1B chat template ends assistant responses with the same native `<|endoftext|>` token rather than introducing a separate chat-only EOT action. This makes the scientific question especially clean: the **same stop action** is reused from pretraining into assistant behavior.
3. `tie_word_embeddings=false`, so an EOS output-row intervention can be implemented without automatically changing the EOS input embedding.
4. 1B is small enough for repeated controlled SFT experiments while still belonging to a modern open post-training stack.

OLMo is a **recommended implementation**, not part of the frozen claim. If an implementation issue makes another same-family base→post-training stack cleaner, the local agent may switch models while preserving the scientific identification requirements below.

## 6. Three-layer empirical program

The paper should ideally contain three complementary layers. They answer different questions and should not be conflated.

### Layer A — Natural phenomenon: exact-prefix goal intervention

Question:

> Does a normal assistant's native stopping decision respond to **goal completion itself**, when response length, wording, punctuation, and generated prefix are held fixed?

For every matched pair, hold the assistant prefix token-for-token identical and modify only the user's requested completion condition.

#### Family A — bounded quantity

Example:

- Goal complete: “Return the first **3** entries.”
- Goal incomplete: “Return the first **4** entries.”
- Replay the exact same prefix containing entries 1–3.

#### Family B — semantic requirement set

Example:

- Goal complete: request `name + occupation`.
- Goal incomplete: request `name + occupation + country`.
- Replay the exact same prefix containing `name + occupation`.

The second family must not merely be another disguised counting task.

Primary quantity:

`stop_margin = logit(stop_token) - logit(correct_next_missing_token)`

The key estimand is the within-prefix shift caused only by changing whether the requested goal is already complete.

Required control:

- In the incomplete condition, verify **continuation awareness**: the correct missing continuation must itself be plausible/high-ranked. Otherwise failure to continue is ambiguous.

### Layer B — Natural post-training trajectory

Use released same-family checkpoints to ask **when** goal-relative stopping appears under a real post-training pipeline.

Preferred first trajectory:

`Base → SFT → DPO → Instruct/RLVR`

For every stage, run the same exact-prefix identification instrument and estimate a goal-relative stopping effect such as:

`Δ_goal(stage) = stop_margin_complete - stop_margin_incomplete`

This is observational evidence about acquisition timing, not a causal decomposition. Different stages change objectives and data, so the paper must not infer necessity from the checkpoint curve alone.

Useful possible patterns include:

- effect appears sharply at SFT → SFT is the main natural acquisition stage;
- effect is weak after SFT but strengthens after DPO/RLVR → preference/reward optimization contributes materially;
- base already has a nontrivial effect → much of the mapping predates explicit assistant post-training;
- effect increases gradually → acquisition is distributed rather than stage-localized.

If released intermediate revisions/checkpoints are convenient, the local agent may add a finer curve inside the stage where the largest change occurs. This is optional and should be driven by observed structure, not precommitted for completeness.

### Layer C — Controlled causal source: parameter-locus intervention

Checkpoint curves answer **when**. The causal experiment asks **what part of the model has to change**.

Start from one small open base checkpoint and use the same native stop token across all arms.

Let the model be conceptually separated into internal state/computation `h_θ` and the native EOS output row/readout `w_EOS`.

#### Arm 0 — Base

No adaptation.

Purpose: measure the pretrained document/text-ending baseline and any pre-existing goal-relative stop mapping.

#### Arm R — Readout-only

Freeze the transformer and every non-EOS output row. Train only the native EOS output row (plus EOS bias if one exists).

Question:

> Are pretrained hidden states already sufficient for goal-relative stopping, such that post-training mainly has to learn how to read this information as a stop action?

If this arm succeeds while Base is weak, that strongly supports **latent information + acquired readout**.

#### Arm S — State-only

Freeze the native pretrained EOS output row. Allow internal model parameters to adapt on the same ordinary instruction-response data.

Question:

> Must post-training reorganize internal state/computation before the old document-end action can respond to user-goal completion?

If State-only succeeds while Readout-only is weak, that supports **state/computation acquisition with reuse of the old stop readout**.

#### Arm F — Full SFT

Adapt both internal parameters and EOS readout on the same corpus.

Purpose: positive control and interaction ceiling.

If neither constrained arm reproduces the Full effect, the scientifically interesting result is that state and readout adaptation are **jointly load-bearing**; do not force a simplistic reuse-vs-new dichotomy.

## 7. Stronger 2×2 behavioral identification, if useful

A useful extension is to independently vary:

- **goal completion**: complete / incomplete
- **textual closure**: surface form looks closed / surface form looks open

This creates a conceptual 2×2 in which textual closure and task completion can disagree.

The central developmental hypothesis is not that one particular crossing must appear, but that post-training may change the relative dependence of the stop decision on these two quantities.

A compelling summary figure, if supported by data, would trace how sensitivity to textual closure and goal completion changes across:

`Base → SFT → DPO → RLVR`

Do not manufacture awkward examples merely to complete the 2×2. If exact-prefix pairs plus continuous base-EOS closure already identify the distinction cleanly, keep the design simpler.

## 8. Data policy

### 8.1 Training data

Do **not** create a special stopping-training benchmark.

Use ordinary public instruction-response data. Preferred first source is an OLMo/Tülu 3 SFT mixture or a small clean subset of it.

Pilot scale can be on the order of a few thousand to low tens of thousands of ordinary instruction-response pairs, depending on how quickly the controlled arms learn a healthy response boundary behavior.

The same examples, formatting, ordering, and optimization setup should be shared across `R / S / F` as far as possible.

Why ordinary SFT is important:

- each response naturally supplies many `continue` positions and one response boundary;
- the model is not explicitly trained on the exact E01 contrast;
- this prevents the paper from becoming “we trained models to solve our own stopping test”.

### 8.2 Identification stimuli

E01 stimuli are **controlled identification instruments, not a benchmark contribution**.

Initial scout can be only tens of matched pairs. If the phenomenon is clean, expand to roughly low hundreds across at least two non-isomorphic operation families.

Possible sources/content can use simple public records, lists, passages, or factual tables. The scientific value is in the exact-prefix intervention, not in dataset size.

Avoid large annotation projects and avoid presenting the stimuli as a new benchmark.

## 9. OLMo-specific implementation advantages to verify locally

The current recommended setup relies on implementation facts that the local agent should verify directly before training:

- the chosen OLMo base/SFT/DPO/Instruct checkpoints are truly aligned to the intended training stages;
- the chat template uses the native `<|endoftext|>` token as assistant termination in the selected release;
- the EOS output row can be isolated cleanly;
- output embeddings are untied from input embeddings in the chosen config;
- padding, ignored labels, and generation stop configuration do not accidentally remove or duplicate EOS supervision;
- the same prompt serialization can be made meaningful for the base and post-trained models.

Any mismatch here is an implementation confound, not a scientific result.

## 10. Interpretable outcomes

The project is not anomaly gambling. Several outcomes answer the same mother question.

1. **Goal-relative stopping is already substantial in Base.**  
   Interpretation: much of the information→stop mapping predates explicit post-training; the assistant transition may mainly calibrate or stabilize an existing capability.

2. **Readout-only succeeds; Base is weak.**  
   Interpretation: goal-relevant information is already present in pretrained states, but pretraining EOS does not use it appropriately. Post-training can acquire task stopping largely through readout adaptation.

3. **State-only succeeds; Readout-only is weak.**  
   Interpretation: the pretrained stop action is reusable, but post-training must alter internal computation so user-goal completion becomes visible to that action.

4. **Both constrained arms partly work; Full is strongest.**  
   Interpretation: hybrid acquisition.

5. **Only Full succeeds.**  
   Interpretation: coordinated state/readout adaptation is necessary; a binary “reuse vs new representation” story is too simple.

6. **Natural checkpoint curve localizes the transition to SFT / DPO / RLVR.**  
   Interpretation: this identifies when the capability emerges under a real recipe and guides which objective/data transition deserves deeper follow-up.

7. **No robust exact-prefix goal effect despite continuation awareness.**  
   Interpretation: assistant stopping may remain much more dominated by textual/surface closure than the intuitive “task done” framing suggests. Reassess Main scope rather than forcing a mechanism story.

## 11. Execution order — current default, not a rigid script

Current high-information order:

1. **E01 scout** on one same-family base/instruct pair with a small exact-prefix set.
2. If E01 is clean, run the **released natural trajectory** `Base → SFT → DPO → Instruct/RLVR` on the same instrument.
3. Run **Readout-only** first because it is the cheapest controlled acquisition test.
4. Then run **State-only** and **Full SFT** on the identical ordinary instruction corpus.
5. Only after a stable acquisition pattern exists should we add finer intermediate checkpoints, another model family, activation analysis, row/state swaps, or mechanistic localization.

This order is recommended because it maximizes information per GPU-hour. It is **not** a contractual sequence.

## 12. Local-agent autonomy: frozen science vs flexible execution

The local experimental agent should **not blindly execute this document as a fixed checklist**. The exact experiments must adapt to what is learned during implementation and pilot runs.

### Frozen unless explicitly re-audited

The following are the scientific commitments of S03:

- the mother question: document/text ending → goal-relative task stopping;
- the scientific object: acquisition of the information→stop mapping;
- the distinction between textual closure and user-goal completion;
- the need for at least one exact-prefix intervention where the generated response prefix is held fixed;
- the need to separate observational checkpoint timing from causal acquisition claims;
- the causal interpretation of Readout-only / State-only / Full-style parameter-locus interventions;
- the prohibition against turning the project into a stopping benchmark, model leaderboard, or generic instruction-following paper;
- claim width must follow the actual evidence.

Changing one of these requires a deliberate research-level re-audit, not an implementation convenience.

### Flexible and should be adapted by the local agent

The local agent may change, reorder, add, or drop the following according to actual progress:

- exact model size and OLMo release;
- whether OLMo remains the cleanest family after implementation checks;
- number of matched E01 pairs;
- exact task families used for bounded and semantic completion;
- exact metric form (`EOS logit`, stop margin, calibrated probability, rank) as long as the causal contrast is preserved;
- amount and composition of Tülu/instruction data;
- optimizer, LR, batch size, LoRA/full-parameter choice where compatible with the intended parameter freeze;
- number of seeds after the scout stage;
- whether a 2×2 textual-closure design is necessary or redundant;
- whether DPO/RLVR intermediate checkpoints are worth finer analysis;
- whether a second model family is needed for generalization;
- whether later representation/activation analysis is scientifically informative;
- exact experiment order when an earlier result makes a later experiment redundant or suggests a better discriminating test.

The agent should choose the **next experiment that maximally reduces uncertainty about the parent question**, not mechanically complete every prewritten experiment.

### Required behavior when the plan changes

When changing the plan, record:

1. what was observed;
2. which competing explanation remains ambiguous;
3. why the proposed next experiment distinguishes those explanations better than the old step;
4. whether the change affects only execution or also the scientific claim.

Do not silently move the goalposts after seeing results.

## 13. Pilot gates and stop rules

The local agent should use evidence gates rather than a predetermined experiment count.

### Gate A — phenomenon exists

Proceed only if exact-prefix goal completion produces a stable stopping shift in at least two meaningfully different operation families, with continuation awareness intact.

### Gate B — natural trajectory is interpretable

Checkpoint analysis should reveal either a stage-localized change, a gradual change, or strong pre-existing Base behavior. Any of these is useful; a noisy model-dependent curve may be insufficient for a central claim.

### Gate C — causal locus can be implemented cleanly

Readout-only and State-only must correspond to genuinely different parameter freedoms. If architecture/tooling makes the freeze porous or token tying confounds the manipulation, fix the implementation or switch model family before interpreting results.

### Gate D — Main-level scientific object remains intact

Continue only while the main conclusion remains about **how stopping capability is acquired**, not about which model scores best on a custom set.

## 14. What the main paper should eventually look like

A strong paper would have this narrative:

1. **Puzzle:** pretraining teaches when text ends; assistants need to know when the task is done.
2. **Identification:** identical response prefix, different user goal → isolate goal-relative stopping from surface closure.
3. **Natural acquisition trajectory:** trace the transition through real post-training stages.
4. **Causal source:** determine whether stop-readout adaptation, internal-state adaptation, or their interaction is sufficient.
5. **Conclusion:** characterize what post-training actually changes when a text continuer becomes a goal-directed assistant.

The main result should be a learning/acquisition law or decomposition, not `model × dataset × score`.

## 15. Current operational summary

- **Selected:** yes.
- **Recommended first family:** OLMo 2 1B.
- **Training data:** ordinary public instruction-response data; Tülu 3 / OLMo-specific mixture preferred.
- **Evaluation object:** exact-prefix causal identification stimuli, not a benchmark.
- **Natural trajectory:** Base → SFT → DPO → Instruct/RLVR.
- **Controlled causal test:** Base / Readout-only / State-only / Full.
- **Agent policy:** keep the mother question and identification logic fixed; adapt concrete experiments aggressively according to actual evidence, compute cost, and implementation reality.

The experiment plan is intentionally a **research scaffold rather than a frozen recipe**.