# Selected Topics — Sasano-Taste Search

Started: 2026-09-16

Purpose: record only questions that survive a real nearest-prior novelty check and are worth concrete pilot design or execution.

## Admission rule

A topic can enter this file when all three are true:

1. **Worth asking:** the question is understandable without elaborate framing and there is a natural reason a reviewer would want to know the answer.
2. **Real difference:** recent nearest prior work does not already answer the same question; the distinction is substantive rather than merely “newer model / larger model / another benchmark”.
3. **Testable:** there is a realistic clean experiment that can reduce uncertainty without requiring unreasonable data construction or compute.

Mechanistic depth, surprising pilot results, broad cross-model robustness, and complex methods are valuable when they help, but they are not admission requirements.

For each selected topic, record the question, scientific pressure, nearest-prior gap, minimal experiment, expected resource cost, Sasano-fit rationale, and remaining risks.

---

## Current selections

### S01 — Omission ≠ Neutrality: Do LLM Agents Understand Effective Default Semantics?

**Status:** SERIOUS CANDIDATE — PILOT-WORTHY; novelty survives current search, paper-scale still needs evidence.

**Plain-language question.** When an LLM agent omits an optional tool argument, does it understand that the omission is not “no decision” but resolves to a concrete runtime default? More importantly, when that default conflicts with the user's requested outcome, will the model actively override it, or will it produce a syntactically valid but behaviorally wrong call?

**Why this is scientifically interesting.** Tool-calling evaluation usually focuses on whether the model selects the right function and emits legal arguments. But optional arguments introduce a semantic distinction between the **surface call** and the **effective call** actually executed by the program. A missing field is not an empty semantic slot: the runtime substitutes a specific value and therefore a specific behavior. This creates a clean possible dissociation: `argument omitted` can look conservative or neutral in language while committing the system to a concrete policy in execution.

A simple example is a tool `search(..., include_archived=false)` or `send(..., notify=true)`. If the user explicitly asks for archived items or asks not to notify, omission is behaviorally equivalent to choosing the wrong value even though the JSON is schema-valid. The scientific object is therefore not optional-argument accuracy; it is whether the model represents **effective action semantics after default resolution**.

**Nearest-prior check and current gap.**

- BFCL-compatible evaluation was explicitly updated in July 2026 so that an omitted optional parameter and an explicitly supplied schema-default value are treated as the same call. This is correct at the API execution level, but it also shows that prevailing tool-call scoring collapses the two surface forms into one effective-call equivalence class rather than asking whether the model reasons about the consequences of the default.
- MultiCAT-Bench (2026) systematically varies the fraction of parameters with default values and likewise does not penalize omission versus explicit default when the effective call is equivalent. Its object is function-calling difficulty/accuracy, not whether an agent knows when a default must be overridden to satisfy user intent.
- Recent ACL/EMNLP tool-use work studies when to call tools, tool preference, schema/documentation quality, sequential/nested calls, dynamic schema evolution, missing required parameters, and robustness to tool-output perturbations. In the current search, no direct owner was found for **default-consequence reasoning under matched user intent**.
- Engineering guidance increasingly warns that optional parameters and defaults affect agent reliability, which supplies external pressure, but these sources do not answer the model-side scientific question.

**Important boundary.** This topic is **not** “benchmark optional parameters,” “models sometimes omit arguments,” or “defaults are bad.” Those versions are weak or already covered. The proposed parent is the distinction between **surface omission** and **effective behavior after runtime default resolution**, tested by holding the user goal and backend semantics fixed while changing only whether satisfying the goal requires accepting versus overriding a default.

**Minimal clean pilot.** No large dataset is needed.

Construct 20–50 tiny deterministic tool schemas, each with one optional parameter whose default has an observable consequence. For every semantic task create matched conditions:

1. **Default-consistent:** the user's goal is satisfied by omitting the optional field.
2. **Default-conflicting:** the same user goal structure requires explicitly overriding the default.
3. **Default-flipped:** identical tool/name/task wording, but the schema default is swapped; the correct surface action must therefore flip.
4. **Explicit-equivalent control:** replace omission with the explicit default value to verify that the model treats the two calls as behaviorally equivalent once the value is made explicit.

Score the **effective executed call**, not raw JSON equality. Before the call, optionally ask the model to predict the resulting state; this separates failure to understand the default from failure to realize that the user goal requires overriding it.

A strong first result would be a systematic asymmetry in which models perform well when the desired behavior coincides with the default but fail disproportionately when satisfying the same kind of request requires overriding it. A null result is still informative for deciding whether the parent has leverage, but would probably not justify a full paper without a second source of pressure.

**Cheap follow-ups only if the pilot has leverage.**

- Put the same default in the structured schema versus natural-language description to localize where the semantics is acquired.
- Rename the parameter while preserving its behavior to separate lexical priors from schema reasoning.
- Compare explicit `null` / omitted / explicit default only where the host language/API gives them genuinely different semantics.
- Test whether a short intermediate question (“what value will the runtime use if omitted?”) repairs the error, distinguishing missing knowledge from action-selection failure.
- Inspect open tool-calling training data only after a phenomenon exists, asking whether training/evaluation conventions systematically reward omission/default equivalence and therefore fail to teach override conditions.

**Resource cost.** LOW. Pure inference is enough for the first pilot; deterministic local tools can execute calls and verify outcomes. No human annotation, large benchmark construction, or training run is required initially.

**Why it fits Sasano's taste.**

- The distinction is understandable in one sentence.
- It starts from a real property of the interface rather than an invented benchmark taxonomy.
- The clean experiment changes one thing at a time and can eliminate simple explanations.
- The nearest-prior difference can be stated concretely: existing work evaluates optional/default parameters as a tool-calling property; this asks whether the model represents the **runtime consequence of omission** and overrides it when needed.
- It does not require a complicated new method or heavy linguistic theory.

**Main risks.**

1. **Paper-scale risk (largest):** if frontier models simply resolve defaults correctly across all matched conditions, the question may close cleanly but not grow into a Main paper.
2. **Reviewer-compression risk:** reviewers could still describe it as “a focused optional-parameter/tool-calling robustness study.” The paper must make effective-call semantics, not benchmark accuracy, the central object.
3. **Documentation confound:** failures may reduce to models not reading the schema. The default-flip and pre-call state-prediction controls are essential.
4. **Artificial-tool risk:** toy APIs are ideal for identification but need a small natural-API validation set if the phenomenon survives.

**Current decision.** Run the minimal pilot before adding mechanisms, large datasets, or training. Do not expand this into a broad tool-use benchmark.