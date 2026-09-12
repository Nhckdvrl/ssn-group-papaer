# Research Execution — Develop the Selected Scientific Contribution

Updated: 2026-09-12. Target: ACL / EMNLP / NAACL Main.

This file governs work **after a candidate has explicit authorization**.

- Where to search: `RESEARCH_TOPIC_SEARCH.md`
- Whether a candidate deserves compute: `RESEARCH_TOPIC_SELECTION.md`
- How to develop an authorized project: **this file**

Execution is not permission to keep a story alive. It is a sequence of tests that determines which answer is true and whether that answer still deserves a paper.

---

## 1. Source of Truth and Scope

Before work:

- sync current `main`;
- inspect the concrete candidate’s latest README / claims / experiment ledger;
- resolve conflicts with root status documents;
- edit only the authorized candidate scope unless workflow maintenance is explicitly requested.

A candidate directory name such as `good/` or an old “GO” does not confer current authorization.

Every load-bearing result must remain traceable:

> **claim → experiment → config/code → data → raw result → summary → conclusion**

Keep large checkpoints/raw artifacts outside git when appropriate, with hashes/manifests/reproduction notes.

---

## 2. Keep Four Judgments Separate During Execution

At every major decision distinguish:

| Judgment | Question |
|---|---|
| **RQ value** | Is the question still worth answering? |
| **Contribution** | Is the current answer/account independently new and important? |
| **Evidence** | Do the experiments identify that answer rather than a weaker alternative? |
| **Maturity** | Is the depth/breadth/consequence sufficient for the claimed scope? |

A project may pass evidence and fail contribution. It may have a great RQ but an unresolvable effect. Strong local results do not automatically imply Main-level maturity.

---

## 3. Stage Gates

| Stage | Purpose | Exit condition |
|---|---|---|
| **Authorized pilot** | resolve one named uncertainty at minimum cost | specified decision can be made |
| **Contribution gate** | reassess novelty + successful-result inference using actual evidence | current paper identity still deserves investment |
| **Explanation** | distinguish live accounts and establish causal/structural relation | explanation advances beyond phenotype |
| **Breadth / boundary** | establish where the account holds/fails | scope is supported by independent axes |
| **Consequence / intervention** | test a prediction, repair, or implication when scientifically meaningful | contribution changes understanding or use |
| **Manuscript review** | audit argument as a whole | no load-bearing gap remains |
| **Archive** | preserve assets and stop sunk-cost drift | no unauthorized experiment queue remains |

The smallest decisive pilot is a gate, not a miniature paper.

Do not force every paper into phenotype → probe → patch → intervention. The stages serve the inference, not a template.

---

## 4. Pre-Run Resolution Check

Selection performs the first feasibility audit. Execution must refresh it whenever scale, metric, dataset size, model size, or expected effect changes.

Before an expensive run ask:

- What effect or difference must this experiment resolve?
- What is the current noise floor / minimum detectable effect?
- What is the independent scientific unit?
- Are repeated generations only reducing Monte Carlo noise, or adding true units?
- What training/seed variance matters?
- If the important conclusion is a null, is the planned interval tight enough to exclude the scientifically relevant effect?
- Is the compute/storage cost proportional to the information gained?

Do not run because a configuration exists.

The L19 lesson is durable:

> **A scientifically valid question can still be a bad executable project when the effect of interest is below attainable resolution.**

Resolution is part of experiment design, not an afterthought.

---

## 5. Design Each Experiment for an Inference

Before a substantive experiment record:

- experiment ID;
- linked claim/question;
- live alternative accounts;
- exact manipulation/comparison;
- what the manipulation changes besides the intended variable;
- primary observable/estimand;
- independent unit;
- seeds/sampling;
- controls;
- possible outcomes and their interpretation;
- stopping/reconstruction condition;
- expected resolution and cost when material.

Then ask:

> **If the strongest expected result occurs, what important alternative still survives?**

Choose the smallest operation that resolves that alternative.

Common inference failures:

- decodability substituted for causal use;
- state transplant substituted for identification of the computation that formed the state;
- a same-answer no-change intervention treated as proof despite being ineffective;
- behavior and representation changes shown separately without connecting them;
- model-family differences called training causality;
- output improvement treated as proof of the proposed internal mechanism.

Controls protect an inference; they do not need to become headline claims.

---

## 6. Mechanism Evidence: Observable → Intervention → Causal Claim

For mechanism/model-computation projects, keep three layers explicit:

1. **Phenotype / observable** — what behavior is stable?
2. **Candidate computational quantity** — what representation, route, state, strategy, or training change is proposed?
3. **Causal bridge** — what intervention shows that quantity controls the phenotype in the claimed way?

Do not let a clean behavioral benchmark substitute for the mechanistic bridge.

Useful designs may include probes, patching, steering, checkpoint comparison, controlled training, corruption/restoration, teacher forcing, trajectory analysis, or other tools. None is automatically causal by name.

The operation must discriminate accounts.

---

## 7. Data / Measurement Evidence: Gold Must Match the Quantity

For external-task/data projects, document:

- provenance and version;
- unit of analysis;
- gold/observable definition;
- transformations/filtering;
- train/test leakage;
- missingness;
- repeated/clustered units;
- whether the label directly supervises the claimed estimand.

A related label is not direct gold.

For all projects, list every scientifically relevant thing changed by the manipulation. Do not silently repair a construct mismatch after observing the result.

Use uncertainty at the correct unit. More generations increase precision; they do not automatically create more independent scientific cases.

---

## 8. Claim Mutation = Mandatory Re-Selection

If any of the following materially changes, previous paper-level approval expires:

- RQ;
- core explanation;
- central causal claim;
- paper identity / reviewer takeaway;
- a supporting result becomes the new headline;
- a null result motivates a different scientific story.

Evidence and code survive. **Authorization does not.**

Before broad confirmation of a mutated claim, write a compact Claim Novelty Delta in the candidate package:

1. old statement;
2. new statement;
3. evidence that motivated the change;
4. closest owners;
5. strongest reviewer compression;
6. surviving contribution;
7. new successful-result inference;
8. feasibility/resolution if compute changes;
9. `PASS / HOLD / RECONSTRUCT / NO-GO`.

A new story may be worth studying. It is simply a new selection decision.

This rule prevents L13/L15-style post-hoc paper growth.

---

## 9. Explore Unexpected Results Without Story Protection

Unexpected structure can be scientifically valuable.

Allowed:

- check implementation validity;
- check whether the measurement had enough power/resolution;
- test a pre-existing competing account;
- perform a bounded diagnostic to understand what failed;
- formulate a genuinely new candidate and restart selection.

Not allowed:

- repeatedly rename the paper until the existing experiments fit;
- add increasingly narrow mechanisms solely to preserve novelty;
- treat every null as an implementation bug;
- collect a large model/layer sweep before the contribution is defined.

A productive failure can remain a useful archived result.

---

## 10. Novelty Must Be Refreshed When the Scientific Statement Changes

For the current paper identity, test both:

> **Prior A + Prior B + Prior C = our paper**

and:

> **What substantial inference still remains after A/B/C?**

Distinguish:

- direct collision;
- component overlap;
- insufficient contribution;
- unresolved ownership;
- plausible independent contribution.

Do not kill because all ingredients are familiar. Do not survive because the exact sentence has never appeared.

---

## 11. Main-Level Calibration

Calibration should change the next research decision, not decorate a README.

Use relevant strong ACL / EMNLP / NAACL Main work and top-ML work when it owns the mechanism.

Compare:

- **intellectual advance** — what did readers learn?
- **decisive inference** — which alternative did the key experiment eliminate?
- **depth** — what moved the work beyond its first observation?
- **breadth** — which genuinely independent axes support the scope?
- **consequence** — what prediction, intervention, understanding, or practice changed?
- **work remaining** — what one gap most limits our current paper?

Do not imitate section counts, model counts, or method names.

A claim may require another training regime, model family, task family, or domain. Add breadth because the scope requires it, not because “Main papers test many models.”

---

## 12. Full-Study Completion Test

Before manuscript readiness answer:

1. Is the central answer independently valuable after current prior work?
2. Does the evidence distinguish the claimed explanation from its strongest live alternative?
3. Does the argument progress rather than accumulate disconnected experiments?
4. Does breadth match the scope actually claimed?
5. Is there a meaningful explanation, boundary, prediction, or consequence beyond the first effect?
6. Are null/negative/heterogeneous outcomes represented honestly?
7. Are all load-bearing effects resolvable and statistically defensible?
8. Have major claim mutations re-passed novelty/selection?

No fixed number of experiments, claims, datasets, models, or domains substitutes for these answers.

---

## 13. Stop / Hold / Archive

### HOLD
Use only when there is:

- one named blocker;
- one bounded way to resolve it;
- an explicit review point.

### RECONSTRUCT
Use when a substantively different account may be valuable. Restart selection before scale-up.

### ARCHIVED / NO-GO
Stop when:

- central answer is owned or too small;
- operation cannot identify the interesting claim;
- mother phenomenon is unstable;
- important effect cannot be resolved within available resources;
- project becomes infrastructure/benchmark work rather than the intended science;
- best remaining result is trivial or post-hoc.

Archive the route, not useful evidence.

Record:

- what was learned;
- why the route stopped;
- reusable code/data/results;
- what qualitatively new evidence would justify reopening.

Remove obsolete next-run instructions.

---

## 14. Reproduction and Resource Hygiene

Maintain exact commands/configs, model versions, templates, decoding settings, random seeds, data hashes, and result pointers when load-bearing.

Do not manually alter results.

Before pushing:

- inspect outgoing history, not only staged files;
- avoid committing unrelated work;
- preserve concurrent users’ processes/files;
- clean only jobs/artifacts known to belong to the project;
- delete massive regenerable checkpoints when archiving if results and reproduction paths are preserved.

A documentation update never implies an experiment was rerun.

---

## 15. Durable Failure Lessons — Compact, Not Candidate-Specific

Detailed retrospectives belong in the candidate/archive package, not in this root workflow.

The reusable lessons are:

- **L12:** a natural RQ and many strong local effects do not substitute for a discriminating explanatory idea; claim mutation must reset novelty.
- **K175-type failures:** related annotation is not direct supervision of the load-bearing scientific quantity.
- **K180-type failures:** if only a large reversal creates a paper, the candidate is outcome-fragile.
- **K181-type failures:** an unstable mother anomaly plus increasingly narrow mechanisms is a bad route.
- **L13-type failures:** strong evidence does not rescue a paper identity that grew post-hoc from successive falsifications.
- **L15-type failures:** when the preregistered dissociation fails, generic fallback observations are not the same paper.
- **L19/K184:** novelty and question value can survive while the project is infeasible because the effect of interest lies below the attainable noise floor.

These lessons constrain decisions without turning root workflow documents into historical candidate narratives.

> **Execution should make the scientific answer clearer and the paper identity more defensible. If experiments only make the story more complicated, stop and re-select.**
