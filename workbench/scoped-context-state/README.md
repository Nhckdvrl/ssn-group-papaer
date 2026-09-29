# Scoped Context State — Workbench

**Lane:** sasano-taste  
**Stage:** ACTIVE EXPLORATORY WORKBENCH — **not a candidate**  
**Target ceiling:** ACL / ICLR / NeurIPS main-track scale.  
**Core discipline:** discover the real research object; do not optimize a local probe into a paper.

---

## 0. Why this workbench exists

A basic reasoning operation is to temporarily enter a local world, reason inside it, and then leave it.

Examples:

- “Assume A. Under that assumption, what follows? Now discharge A.”
- “Suppose Alice lived in Paris. ... Return to the actual situation.”
- “Simulate plan A. Return to the current state. Now simulate plan B.”
- “In 2010, ...” followed by later turns that inherit, switch, or leave the temporal frame.
- nested mathematical or logical subproofs whose assumptions must not leak outside their scopes.

The natural question is:

> **Can an LLM maintain temporary, scoped context and correctly return to the surrounding context when the scope ends?**

The first experimental target is **not** to prove that LLMs have a special “scope module”, nor to build a new benchmark.

The workbench exists because two strong neighboring lines expose related pressure without yet establishing one shared object:

- **ProofGrid** evaluates formal reasoning with hierarchical proofs and nested assumptions. Its NDL supports explicit assumption / lemma scopes, and invalid use of conclusions outside the current assumption base is a substantive reasoning error.
- **ChronoScope (ACL 2026)** studies temporal scope stability in multi-turn QA and finds that models can know the underlying fact yet drift away from an implicitly maintained temporal frame, especially over longer interactions.

These are important parents, not empty gaps. The workbench asks whether their failures are task-specific or manifestations of a more general difficulty with **entering, maintaining, switching, and exiting temporary contextual states**.

---

## 1. Top-conference ceiling contract

This workbench is authorized only under the following scope ladder:

> **matched failures under temporary-context transitions**  
> → **a general property of how LLMs represent and manage reversible/scoped reasoning state**  
> → **consequences for reasoning, planning, counterfactual simulation, multi-turn interaction, or architectures/interfaces that rely on multiple temporary worlds**

The local substrate may be formal proof, natural-language hypotheticals, temporal frames, planning, or another clean setting.

No single substrate is the scientific contribution.

### The workbench loses authorization if

- the effect is only a ProofGrid/NDL syntax issue;
- the effect is only temporal QA already owned by ChronoScope;
- the effect is ordinary long-context degradation after length-matched controls;
- the effect appears only in weak/small models and disappears in strong current models;
- explicit prompting such as “END ASSUMPTION” trivially removes the effect and no natural setting still exposes a meaningful failure;
- the remaining contribution can fairly be summarized as “another benchmark of hypothetical reasoning”;
- the workbench needs increasingly artificial controls merely to keep the phenomenon alive.

If any of these become the best remaining story, **stop and demote**. Do not rescue it by local optimization.

---

## 2. Nearest-prior ownership: overlap is allowed; narrative theft is not

A serious problem will overlap with prior work. **Novelty does not require isolation from every neighboring paper.**

The goal is not to find an untouched keyword. The goal is to own a scientific statement that the nearest prior does not already own.

### Already owned / do not claim

#### ProofGrid
Already owns:
- formal proof reasoning with nested assumptions;
- hierarchical subproofs;
- explicit assumption scopes;
- errors where an inference does not follow from the current assumption base;
- the broader fact that frontier models still fail on some structured proof reasoning.

Therefore we cannot claim:

> “LLMs sometimes violate assumption scope in formal proofs.”

That is too close to existing evidence.

#### ChronoScope
Already owns:
- temporal scope stability in multi-turn factual QA;
- implicit carryover, explicit temporal switching, cross-entity transfer, long temporal trajectories;
- present-day drift despite correct underlying knowledge.

Therefore we cannot claim:

> “LLMs sometimes lose an implicit temporal frame over dialogue.”

That is already a strong ACL paper.

### What may still be ours if earned

A broader or different object may remain open if experiments show that:

> **the same reasoning content is handled correctly in a flat representation but degrades specifically when it must cross temporary-context boundaries, and this transition-specific failure recurs across genuinely different substrates.**

The novel story would then be about **scoped-state transition / reversible contextual state**, not about one benchmark's error category.

This is only a working ownership hypothesis. The agent must continuously search for work that could invalidate it.

---

## 3. Agent mission

The local research agent is the default executor.

Its objective is **not**:

> maximize performance on the current benchmark, accumulate many experiments, or make the initial hypothesis survive.

Its objective is:

> **use baselines, perturbations, prior search, failures, and cross-substrate tests to discover whether there is a simple, important, novel scientific object with top-conference ceiling.**

The agent is authorized to:
- reproduce baselines;
- inspect source code / prompts / datasets / model outputs;
- design and run diagnostic experiments;
- read new related work continuously;
- change the working explanation;
- abandon an experimental instrument that is uninformative;
- replace one substrate with another if the broader object remains the same;
- conclude that the workbench should be killed;
- discover a different, stronger question than the one written here.

The agent is **not** authorized to:
- protect the initial “scoped context” story;
- keep adding prompt tricks until a desired effect appears;
- turn every null result into a narrower special case;
- spend many runs optimizing a local score before establishing scientific meaning;
- invent a method before a stable bottleneck exists;
- build a large benchmark merely because small probes are noisy;
- claim novelty because no paper uses our exact terminology;
- reject useful neighboring prior merely because it overlaps with us;
- mechanically execute a fixed experiment list after the scientific question has changed.

---

## 4. Anti-local-optimization rule

This rule is mandatory.

After **every meaningful experiment block**, the agent must stop local iteration and answer:

1. **What did this result change in our understanding?**
2. **Which explanation became less plausible?**
3. **Does the broader object become clearer, weaker, or unchanged?**
4. **What is the strongest nearest-prior compression now?**
5. **Can a reviewer summarize us as an existing paper + new setting?**
6. **What experiment has the highest information gain about the scientific object?**
7. **Should we continue, pivot within the territory, freeze, or kill?**

Do not run another hyperparameter/prompt sweep unless its result would distinguish two substantive explanations.

### Bad loop

> scope effect exists  
> → tune prompt  
> → add another template  
> → tune threshold  
> → add more models  
> → make a bigger benchmark  
> → write paper

### Required loop

> reproduce a parent capability  
> → create a matched contrast  
> → inspect the failure  
> → test alternative explanations  
> → search nearest prior again  
> → decide whether the **problem representation** changed  
> → choose the next highest-information intervention

The workbench is successful even if it dies quickly.

---

## 5. Research-navigation objective

The agent should actively search for **idea growth**, not merely validate a preregistered hypothesis.

Useful discoveries may look like:

- scoped transitions are genuinely harder than equivalent flat reasoning;
- only **exit/discharge** fails while enter/maintain is intact;
- only **nested/sibling** scopes fail;
- explicit formal scopes work but natural-language scopes fail;
- temporal and logical scope failures share no mechanism at all;
- reasoning models repair one type but worsen another;
- scope errors are actually caused by recency, positional bias, answer priors, or context length;
- the current “scope” abstraction is wrong, but experiments expose a more important state-management bottleneck.

Any of these may redirect the paper identity.

Do not force all substrates to agree.

---

## 6. First baseline residency

Before building anything large, understand the nearest parents.

### A. ProofGrid

Use released prompts/results and, when available, checker code.

Identify:
- which tasks actually require nested assumptions / discharge;
- concrete examples of “not in current assumption base” failures;
- whether the same local inference is accepted in isolation but used incorrectly in a larger proof;
- which strong current models fail vs pass.

Do not reproduce all 15 tasks.

The goal is to understand **what ProofGrid already establishes** and extract minimal matched cases.

### B. ChronoScope

Use the released dataset/evaluation.

Understand:
- implicit scope carryover;
- explicit scope switching;
- oracle-context setting;
- length dependence;
- present-day drift.

Again, do not rerun the full 1.4M-chain benchmark initially.

The goal is to understand whether temporal failures look like:
- maintenance failure;
- switching failure;
- default-state attraction;
- or something unrelated to logical assumption discharge.

### C. Strong-model prerequisite check

Before interpreting any failure:
- verify the model solves the underlying flat reasoning/content task;
- verify it understands explicit scope markers in simple cases;
- use multiple strong open models before spending on frontier APIs;
- include at least one strong reasoning model if accessible.

If prerequisite competence is absent, the item is not evidence about scoped state.

---

## 7. Earliest revealing experiment: matched scope transformation

The first new instrument should be **small and matched**.

Construct content-equivalent variants where possible.

### Flat

All premises remain globally active.

### Enter / maintain

A temporary assumption is introduced and queried while still active.

### Exit / discharge

The same temporary assumption is no longer active when the target judgment is made.

### Switch

Move from temporary world A to world B.

### Nested

Base → A → B → exit B → remain in A → exit A.

### Sibling

Base → A → exit → B → exit.

The key comparison is not raw task accuracy.

It is whether **the same underlying reasoning operation changes when only contextual scope structure changes**.

Control:
- token length;
- premise order;
- recency;
- surface wording;
- answer label distribution;
- difficulty of the underlying inference.

Keep the first set small enough for manual inspection.

---

## 8. Error decomposition

Do not report one “scope accuracy”.

At minimum separate:

- **leakage:** information/assumptions remain active after exit;
- **premature forgetting:** active local assumptions are ignored before exit;
- **switch failure:** old scope contaminates a new sibling scope;
- **base-state corruption:** temporary reasoning changes later judgments that should depend only on the base context;
- **default attraction:** model exits toward a pretrained/default world instead of the explicitly restored base state;
- **nesting error:** inner and outer assumptions are confused.

These categories are diagnostics, not guaranteed paper constructs.

If another decomposition better explains the data, replace them.

---

## 9. Alternative explanations that must be attacked early

Before saying “scoped state”, test:

- ordinary recency bias;
- longer-context degradation;
- lost-in-the-middle effects;
- instruction-following failure;
- lexical/coreference ambiguity;
- answer-position bias;
- inability to solve the base reasoning task;
- prompt-format sensitivity;
- world-knowledge conflict;
- self-conditioning from earlier model outputs;
- generic multi-turn error accumulation.

A good workbench result should survive **simple explanations before complex mechanism work**.

---

## 10. Cross-substrate expansion is evidence, not decoration

Do not start with five datasets.

First earn one clean transition effect.

Only then ask whether the **same abstract intervention** transfers to a second substrate.

Potential substrates, in increasing order of cost:

1. minimal logical assumptions / conditional proof;
2. ordinary natural-language hypotheticals;
3. temporal frames;
4. small counterfactual planning/state simulation;
5. other domains only if they expose the same scope operation naturally.

Cross-substrate evidence is useful only if it tests the same scientific abstraction.

Do not add datasets merely to claim generality.

---

## 11. Mechanistic work: only after behavioral object is stable

Mechanistic analysis is optional, not the entry ticket.

Only after a robust transition-specific effect exists, investigate possibilities such as:

- representation of active scope identity across layers;
- whether temporary facts remain linearly/readably encoded after exit;
- whether model computation still causally uses them;
- attention/KV persistence across scope boundaries;
- whether explicit delimiters create sharper state separation;
- whether reasoning training changes state separation or merely improves output correction.

Do not run SAEs/probes merely because interpretability tools are available.

The mechanism must explain a behavioral regularity that already matters.

---

## 12. Method permission

No method at entry.

A method becomes justified only after:

> **scope-specific failure → localized bottleneck → controllable state/interface → simple intervention → broader outcome**

Possible intervention classes are intentionally unspecified.

A prompt delimiter is a baseline, not a paper method.

A method that only fixes one synthetic probe without improving another natural substrate is insufficient.

---

## 13. Novelty narrative discipline

The workbench must maintain a live **ownership map**, not a fake “no one has done this” claim.

For every important nearest prior, record:

- what exact scientific statement it owns;
- what evidence supports that statement;
- where our evidence overlaps;
- what our current distinct statement would be;
- what new result would collapse our distinction.

Overlap is normal.

### Good novelty relation

> Prior A proves temporal scope drift.  
> Prior B exposes assumption-scope errors in proof reasoning.  
> Our matched interventions show that both are instances of a transition-specific failure that appears even when flat-equivalent reasoning is intact, and we identify which scope operations are load-bearing.

This would be novel **only if experiments actually establish it**.

### Bad novelty relation

> ProofGrid used formal proofs; we use natural language.

or

> ChronoScope studied time; we study hypothetical worlds.

Those are setting changes, not enough.

---

## 14. Venue-scale evidence runway

A candidate paper should eventually have several **independent** evidence types, not just more examples:

- strong-model matched behavioral contrast;
- controls eliminating simpler explanations;
- at least one independent substrate if generality is claimed;
- decomposition of enter / maintain / switch / exit operations;
- a causal or diagnostic intervention that changes the relevant failure;
- downstream consequence for reasoning/planning if the broad claim reaches that far;
- optional mechanism/method only if earned.

Do not check boxes mechanically. The final paper should become simpler as evidence accumulates.

---

## 15. Hard kill / pivot conditions

### Kill

Stop the line if:
- matched flat/scoped variants show no robust gap;
- failures vanish under strong baseline prompting/model choice;
- only formal notation produces the effect;
- nearest prior is found that already owns the transition-specific cross-substrate conclusion;
- the effect is fully explained by generic length/recency/instruction effects;
- months of work would be needed just to build an instrument before knowing whether the object exists.

### Pivot within the workbench

A pivot is allowed if experiments reveal a stronger object such as:
- exit/discharge specifically, not scope generally;
- default-state attraction after local simulation;
- inability to isolate sibling hypothetical worlds;
- representation-use dissociation across scope boundaries;
- another state-management bottleneck that naturally subsumes the original question.

A pivot must **simplify or deepen** the scientific story.

It must not merely make the original claim harder to falsify.

---

## 16. Execution cadence for the local agent

The agent may execute autonomously, but in **research blocks**, not endless micro-iterations.

A block should usually contain:

1. one literature/ownership update;
2. one baseline or matched experiment;
3. one alternative-explanation test;
4. one integrated interpretation;
5. one explicit continue/pivot/kill decision.

After each block, update this README or a concise result note with:

- exact artifact/model/version;
- experiment;
- result;
- what assumption changed;
- nearest-prior impact;
- current scope ladder;
- next highest-information action.

Do **not** create many process documents.

Use:
- this README as the scientific contract;
- `experiments/` for harness/code;
- `results/` for raw outputs and concise analyses;
- `BASELINE.md` only if setup details become too large.

---

## 17. Immediate first block

Do **not** start with a large benchmark.

### P0 — Parent audit
- inspect ProofGrid's scope-relevant prompts/results;
- inspect ChronoScope's switch/carryover/oracle settings;
- write a precise ownership table;
- identify the smallest examples where prerequisite reasoning is clearly present.

### P1 — Matched pilot
Build a hand-audited set of roughly tens, not thousands, of examples covering:
- flat;
- active temporary assumption;
- discharged temporary assumption;
- one nested/sibling condition.

Run several strong open models.

### P2 — Earliest controls
Only if P1 reveals a nontrivial effect:
- length-match;
- reorder;
- explicit markers;
- paraphrase;
- prerequisite flat competence.

### Decision
After P0–P2, the agent must choose exactly one:

- **CONTINUE:** scope-transition object strengthened;
- **PIVOT:** a simpler/better object emerged;
- **KILL:** no top-conference object remains.

Do not begin representation analysis, training, or method development before this decision.

---

## 18. Primary references

- **Stress-Testing the Reasoning Competence of Language Models With Formal Proofs** — Findings of EMNLP 2025  
  https://aclanthology.org/2025.findings-emnlp.661/

- **Stress-Testing the Reasoning Competence of LLMs With Proofs Under Minimal Formalism / ProofGrid** — 2026 extended report  
  https://arxiv.org/abs/2605.12524  
  https://github.com/System-2-Labs/ProofGrid

- **Evaluating Temporal Consistency in Multi-Turn Language Models / ChronoScope** — ACL 2026  
  https://aclanthology.org/2026.acl-long.2133/  
  https://github.com/yashkumaratri/ChronoScope

---

## 19. Current paper identity

**None.**

The current working scientific territory is:

> **reversible / scoped contextual state in LLM reasoning**

This wording is intentionally broader than “assumption discharge” and narrower than generic “context management”.

The workbench earns a candidate only if experiments discover a simple, robust, novel statement whose importance survives removal of the first benchmark and whose best-case consequence is genuinely top-conference scale.
