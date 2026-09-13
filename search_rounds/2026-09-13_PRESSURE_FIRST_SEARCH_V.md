# 2026-09-13 — Pressure-First Search V

Continuation of the pressure-first search after `_IV.md`. This log persists dead routes from the round that produced L33 so they are not rediscovered merely because the final round had one survivor.

Only `PILOT-AUTHORIZED — E01 ONLY` counts as a survivor.

---

## Hook P13 — Why do sentence-boundary delimiter / pause tokens help reasoning: persistent memory anchor or boundary-triggered computation?

**Status:** `DROP / DIRECT 2026 BOUNDARY-TOKEN MECHANISM WORK`

### Pressure

ACL 2026 *Think in Sentences* reports large gains from inserting a special delimiter at sentence boundaries and shows sentence boundaries beat equally many random/fixed-chunk delimiters. A tempting same-checkpoint experiment would deny already-passed boundary tokens later KV access to distinguish a persistent sentence-memory anchor from a one-time boundary computation trigger.

### Why it dies

September-2026 pause-token mechanism work already studies boundary-adjacent pause tokens as a training/computation object rather than a generic dummy-token trick. It reports that boundary pauses alter representation/training dynamics, reduce mode overwrite under matched adaptation, and encode additional downstream-step information, with masked boundary-pause variants used as mechanism-guided interventions.

Therefore `Think in Sentences + causal KV masking` is too compressible as a causal refinement inside an already active boundary-token mechanism program.

### Anti-resurrection

Do not reopen as `sentence delimiter is a memory token`, `past boundary-token KV is necessary`, or `boundary anchor vs transient pause` unless a qualitatively different same-quantity contradiction appears.

---

## Hook P14 — Does memorized exception behavior compete with or reuse general reasoning computation?

**Status:** `DROP / MEMORIZATION–REASONING MECHANISM PARENT CROWDED`

### Pressure

Recent work shows memorized exceptions can still recruit computation associated with general reasoning. The natural next question is how a model arbitrates when both a learned rule and a memorized exception are available.

### Why it dies

2026 work on the `knowing–using` gap and adjacent memorization/reasoning localization already studies the transition from stored knowledge to usable reasoning computation. A noisy-label / exception-arbitration version is a narrow successor inside that mature parent rather than an independent Main-level question.

### Anti-resurrection

Do not reopen as `rule vs rote arbitration`, `memorized exception overrides reasoning`, or `when does stored knowledge enter the reasoning circuit` without a genuinely new causal quantity.

---

## Hook P15 — Are lexical boost and persistent structural priming two mechanisms or one contextual-memory mechanism?

**Status:** `DROP / STRONG THEORY REVIEW ALREADY OWNS THE CORE CONCLUSION`

### Pressure

Structural-priming theory traditionally distinguishes short-lived lexical boost from longer-lived abstract structural persistence. Modern language models offer a way to ask whether the two behavioral signatures arise from one contextual representation mechanism or genuinely separate computations.

### Why it dies

The 2025 *Trends in Cognitive Sciences* `context—not grammar` account directly challenges the standard dual-mechanism interpretation, reviews the decay and lexical evidence, and explicitly argues that a single contextual representation account — including neural language models — can generate lexical boost without postulating a separate mechanism. 2026 human work further shows priming of non-constituent linear structure.

A causal-interchange or activation-patching study would therefore mainly mechanistically confirm a conclusion already strongly articulated by the theory literature.

### Anti-resurrection

Do not reopen as `lexical boost vs abstract syntax`, `single vs dual structural-priming mechanism`, or `LLM structural priming is contextual memory`.

---

## Hook P16 — Which tokens should receive loss during instruction / reasoning fine-tuning?

**Status:** `DROP / DIRECT STRUCTURAL-DEFAULT OWNERS`

### Pressure

Several ubiquitous training defaults initially looked like under-examined scientific variables: response-only loss versus loss on instruction tokens; all assistant turns versus only the final turn; equal weighting of rationale and answer tokens.

### Why it dies / does not promote

- NeurIPS 2024 *Instruction Tuning With Loss Over Instructions* already directly turns instruction-token loss into a scientific variable and identifies conditions under which it helps.
- ACL 2026 reasoning-SFT work already attacks uniform token-level CE / rationale-vs-answer misallocation with adaptive weighting.
- `all assistant turns vs final turn only` remains a real engineering switch, but no nontrivial model-science law was found beyond trajectory/data reweighting; it risks becoming a recipe/Agent-training result.

### Anti-resurrection

Do not reopen response-only loss masking or rationale/answer uniform weighting as new parents. A future multi-turn-loss question needs a specific scientific quantity beyond recipe performance.

---

## Hook P17 — Why does self-consistency work: independent-path variance reduction or something else?

**Status:** `DROP / CLASSIC INTUITION ALREADY REWRITTEN AS CONDITIONAL LAW`

### Pressure

The ICLR-2023 self-consistency intuition is that sampling multiple diverse reasoning paths and voting can recover an answer that is consistent across paths. Modern reasoning models, however, can have strongly correlated samples and systematic biases.

### Why it dies

TACL 2026 already shows self-consistency changes character with context length: it can help in shorter settings but amplify positional/systematic biases in long context. ACL-2025 work also analyzes self-consistency through changes in latent answer distributions rather than a simple independent-path vote story.

Thus the unconditional `diverse independent paths reduce variance` intuition has already been converted into a conditional modern law.

### Anti-resurrection

Do not reopen as `sample correlation breaks self-consistency`, `why SC still works in reasoning models`, or `SC is not independent voting` absent a new same-quantity contradiction.

---

## Hook P18 — When is descriptive sampling pulled toward normative ideals: pretraining or post-training?

**Status:** `DROP / DIRECT BASE–ALIGNED OWNERS`

### Pressure

ACL-2025 Best Paper work on response sampling shows models do not simply sample typical real-world values; outputs can be pulled toward prescriptive ideals. A natural training-origin question is whether this shift exists in pretraining or is amplified/created by instruction/preference alignment.

### Why it dies

The parent work already reports stronger prescriptive pull with instruction tuning / RLHF and scale. 2026 *Alignment Makes Language Models Normative, Not Descriptive* then compares a large collection of matched base/aligned models against human behavior and directly identifies alignment-induced normative bias.

### Anti-resurrection

Do not reopen as `base vs instruct normative bias`, `when prescriptive sampling emerges`, or `alignment turns descriptive models normative`.

---

## Hook P19 — Teacher-forced mechanism evidence vs free-running causal computation

**Status:** `DROP CURRENT FORM / CLASSIC EXPOSURE-BIAS PARENT + MEASUREMENT-AUDIT RISK`

### Pressure

Many autoregressive mechanism studies intervene on fixed/gold trajectories even though deployment is free-running. Teacher forcing and free running can induce different hidden-state dynamics.

### Why current form does not promote

The underlying mismatch is the classic exposure-bias / Professor-Forcing problem. Merely showing that a teacher-forced activation effect changes under generation would be a measurement-validity audit unless a specific influential mechanism conclusion is shown to reverse and the reversal exposes a new computation.

### Anti-resurrection

Do not register generic `teacher-forced patching may not transfer to generation` as a topic. A future candidate needs a concrete owned scientific object and a consequential reversal.

---

## Hook P20 — Representation similarity implies shared / swappable computation

**Status:** `DROP / DIRECT FUNCTIONAL-ALIGNMENT CAUSAL WORK`

### Pressure

Cross-model representational similarity is frequently treated as evidence of convergent computation. The hidden identifying assumption is that aligned states are functionally interchangeable.

### Why it dies

ICML-2025 functional-alignment / model-stitching work already shows functional alignment can coexist with differences in represented information, and 2026 LLM cross-model activation-transfer work directly tests end-to-end causal transfer and finds that similar hidden alignment does not imply universal functional interchangeability.

### Anti-resurrection

Do not reopen generic `representation similarity ≠ causal equivalence` or `CCA/linear alignment does not prove shared computation`.

---

# Survivor from this round: L33

## L33 — Where Does Agreement Go Wrong?

**Status:** `PILOT-AUTHORIZED — E01 ONLY`

Package:

- `candidates/L33_AGREEMENT_ATTRACTION_MECHANISM/README.md`
- `search_rounds/2026-09-13_AGREEMENT_ATTRACTION_SELECTION.md`

RQ:

> **When a distractor noun pulls a language model toward the wrong subject–verb agreement, is the controller-number state already corrupted before verb prediction, or does the correct controller information survive and lose only when the model reads it out?**

Why it survived where the hooks above did not:

1. stable published mother phenomenon;
2. long-standing live theoretical distinction (`state distortion` vs `retrieval/access competition`), not a competence test;
3. closest LLM owners either use behavioral/attention proxies or analyze successful agreement circuits, not causal origin of attraction errors;
4. decoder causal masking plus the published attractor→neutral-adverb→verb structure creates a genuinely selective path decomposition;
5. a cheap first-stage mother gate and an explicit instrument-completeness gate can kill the route before broad compute;
6. positive state/access/hybrid outcomes all deepen the same scientific identity rather than requiring a post-hoc pivot.

This log does not authorize any experiment beyond L33 E01.