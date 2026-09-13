# 2026-09-13 — Pressure-First Search XIII

Continuation after `PRESSURE_FIRST_SEARCH_XII.md`. This batch broadens into lexical/phrase composition, morphology, causal interpretability assumptions, human prediction theory, normalization defaults, negation, and noisy-channel comprehension. Only `PILOT-AUTHORIZED — E01 ONLY` counts as a survivor.

---

## P63 — Idiom comprehension: whole-expression retrieval vs online literal composition

**Status:** `DROP / DIRECT MODERN MECHANISTIC OWNER`

### Pressure
Classic psycholinguistic theories distinguish direct lexical/whole-expression access from compositional analysis for idioms. Decoder LMs make this computationally attractive: does a figurative meaning arrive through a stored phrase-level route while literal composition proceeds separately?

### Why dead
EACL 2026 *Tug-of-war between idioms' figurative and literal interpretations in LLMs* already studies the internal competition mechanistically. It reports early attention/MLP contributions to figurative meaning, attention heads that boost figurative while suppressing literal interpretations, and a parallel literal route that remains available. EMNLP 2025 and TACL/ACL work already surround memorization, reasoning and controlled idiomaticity. `retrieval vs composition / coexistence of literal and figurative routes` is therefore occupied.

**Anti-resurrection:** do not reopen as direct-access-vs-composition, two-route idiom processing, or figurative retrieval vs literal bypass with a different model/phrase set.

---

## P64 — English past tense: symbolic rule + lexical exceptions vs a single associative mechanism

**Status:** `PRESSURE ONLY — IDENTIFICATION BLOCKER — NO COMPUTE`

### Pressure
This is a genuine decades-old scientific A/B with an intuitive question: does a model form regular past tense by a productive rule while retrieving irregulars from lexical memory, or can one associative mechanism generate both? AACL 2022 shows Transformers reproduce some regular/irregular frequency dissociations, but only behaviorally. Classic denominal diagnostics (e.g. denominal `ringed` despite lexical `rang`) were designed to separate routes.

### Identification failure of the obvious experiment
A causal dissociation inside an LLM would still not identify the dual-route theory. Westermann & Jones (2021) deliberately construct a neural network with a **known single associative mechanism** and show that it nevertheless develops double internal dissociations for regular and irregular past tense; frequency, phonological neighborhood and complexity are enough. Earlier single-system connectionist work also reproduces denominal regularization. Therefore neither `different subcircuits` nor `denominal -> regular` rules out a one-system account.

### Blocker
Need an operation/prediction that a graded single associative mechanism cannot reproduce by emergent modularity/statistics. Until such an identifying contrast exists, this is a classic but non-identifiable pressure, not a candidate.

**Anti-resurrection:** do not promote on the basis of a tense direction, separate heads/MLPs, Wug accuracy, regular/irregular lesion dissociation, or denominal regularization alone.

Sources: AACL 2022 Transformer past tense; Westermann & Jones 2021 *Origins of Dissociations in the English Past Tense*; Plunkett & Juola 1999 single-system model.

---

## P65 — Decodable direction = writable/steerable causal variable?

**Status:** `DROP / 2026 ACTIVE IDENTIFICATION PROGRAM`

### Pressure
Interpretability frequently discovers a linearly decodable concept and then treats that direction as a manipulable semantic variable. The attractive question is whether `read direction` and `write/control direction` are actually the same causal object.

### Why dead
By 2026 this assumption is already directly under attack: EACL 2026 formalizes activation steering through causal mediation and searches sparse causal mediators; multiple recent papers distinguish decodability from causal salience and document steering side effects / KV-cache contamination / prompt-activation duality. A generic `can decode but cannot steer` result would join an active program rather than own a new parent.

**Anti-resurrection:** do not reopen generic probe-vs-steer, read-vs-write representation, or decodable≠causal without a narrower identifying theorem/quantity.

---

## P66 — Prediction vs integration in decoder LMs

**Status:** `DROP / ANSWER TOO STRONGLY IMPLIED BY OBJECTIVE`

### Pressure
Human psycholinguistics has a long debate: does contextual facilitation reflect pre-activation before the word occurs or easier integration after it arrives?

### Why dead
For an autoregressive next-token LM, target-conditioned prediction before the target is not an optional mechanism: the architecture/objective explicitly produces a next-token distribution at the pre-target state. A study could localize which layers/features support that prediction, but the core A/B is not hard to answer in this computational regime. Human work itself continues to debate what neural pre-onset signals identify, but that does not create an LLM mechanism gap.

**Anti-resurrection:** do not transfer the human N400 prediction-vs-integration debate mechanically into decoder LMs unless a different computational variable makes both accounts genuinely viable.

---

## P67 — Pre-Norm as a default: optimization necessity or historical convention?

**Status:** `DROP / OWNER DENSITY TOO HIGH`

### Pressure
Pre-Norm is a ubiquitous modern LLM default and superficially fits the `structural default -> scientific variable` generator.

### Why dead
Normalization placement is already a dense 2025–2026 research program: ICML 2025 Peri-LN gives analytical large-scale training dynamics; NeurIPS 2025 studies memorization/generalization; ICML 2026 SiameseNorm explicitly addresses the Pre/Post tradeoff; AISTATS 2026 derives initialization effects; August 2026 directly tests a changed training regime where the Pre/Post ranking flips under curriculum depth growth. This is not under-examined.

**Anti-resurrection:** do not reopen generic why-Pre-LN, Pre-vs-Post under modern LLMs, representation-collapse vs stability, or normalization placement with another training recipe.

---

## P68 — Negation: suppression of the positive concept vs construction of a negative semantic state

**Status:** `DROP / DIRECT ICML 2026 MECHANISM OWNER`

### Pressure
Negation admits an intuitive computational A/B: suppress what `X` would normally activate, or construct a new representation for `not X`.

### Why dead
ICML 2026 *How Language Models Process Negation* asks essentially this exact mechanistic question and uses observational plus causal interventions on Mistral-7B and Llama-3.1-8B. It finds both suppression and constructive mechanisms, with construction more prominent, and also identifies late shortcut attention that causes errors. Additional 2026 work targets causal negation features/circuits. The parent is directly owned.

**Anti-resurrection:** do not reopen suppression-vs-construction, negation operator features, or `negation known internally but shortcut wins` with a new model or task.

---

## P69 — Does an LLM that “mentally corrects” noisy language actually model the error channel?

**Status:** `SERIOUS-LOOKING PRESSURE — UNRESOLVED NOVELTY — NO COMPUTE`

### One-line RQ
> **When an LLM reinterprets an implausible/malformed sentence as what the speaker probably meant, does it actually combine a language/world prior with a model of which errors are likely, or is the behavior explainable by plausibility alone?**

### Scientific pressure
Human noisy-channel comprehension makes a specific decomposition:

`P(intended | observed) ∝ P(intended) × P(observed | intended)`.

The second term is not cosmetic. Human experiments show that comprehenders track deletion/insertion/exchange likelihoods and adapt the noise model to the recent environment. CMCL 2024 reports that ChatGPT can show the same surface pattern of nonliteral interpretation on implausible sentences, which has been discussed as human-like noisy-channel behavior.

Crucially, EMNLP 2025 *Resource-Rational Noisy-Channel Language Processing* explicitly states that it remains unclear whether ordinary next-word LMs are themselves the right model of this behavior: humans can explicitly model error operations, whereas their computational model uses the LM only as the language prior and adds a separate error model plus inference algorithm. Thus the load-bearing unresolved quantity is not `can the LLM correct?`; it is whether a vanilla LM contributes an **implicit channel-likelihood term beyond its linguistic prior**.

### Candidate accounts
- **A — implicit channel model:** correction/reinterpretation is sensitive to error-operation likelihood even when intended-message plausibility is controlled; this channel estimate may adapt when the local error process changes.
- **B — prior-only plausibility repair:** the model chooses a more probable/plausible intended sentence, and apparent deletion/insertion asymmetries are reducible to sentence priors/surface likelihoods rather than a separate error model.

### Potential identifying move
A promising design is to vary **error-channel evidence independently of intended-message prior** on the same checkpoint. Strongest version: hold the candidate intended sentence fixed while changing the observed corruption operation, then independently manipulate recent exposure to a particular corruption family without explicitly instructing the model what rule to use. Measure implicit comprehension/correction choices on held-out ambiguous items. A channel account predicts operation-specific adaptation; a static prior-only account does not.

This is only a design sketch, not authorization. Surface fluency of the corrupted string, generic ICL/pattern matching, and explicit task-following are serious alternative explanations and need matched controls.

### Closest owners / current blocker
- CMCL 2024: establishes LLM nonliteral reinterpretation behavior, not prior-vs-channel identification.
- EMNLP 2025: supplies an explicit external error model and explicitly says ordinary next-word LMs may not implement noisy-channel inference themselves.
- Ryskin et al. 2018 / subsequent human work: proves context-specific error-model adaptation in humans.
- **Ownership risk:** Gawel & Ryskin list a 2025 poster titled *Noisy Channel Inference in Large Language Models* at the California Meetup on Psycholinguistics. Public search currently surfaces the title/listing but not an abstract, paper, or preprint. Because its exact estimand is unknown, novelty cannot be declared clear.

### Current verdict
`UNRESOLVED NOVELTY`, not Selection-ready. Do not GPU. Promotion requires either obtaining enough information about the Gawel/Ryskin work to show it does not own prior-vs-channel/error-type adaptation, or reframing to a scientifically distinct estimand. If that ownership clears, this is worth a full Selection audit because both positive and negative outcomes revise an explicit current claim about whether next-token LMs implement noisy-channel comprehension.

Sources: Ryskin et al. 2018 *Comprehenders model the nature of noise in the environment*; Cai et al. CMCL 2024; Clark et al. EMNLP 2025 *Resource-Rational Noisy-Channel Language Processing*; Gawel & Ryskin 2025 poster listing.

---

## Round checkpoint

**New survivor: 0.**

P69 is the strongest new pressure in this batch but is blocked by unresolved ownership and identification controls. It is explicitly **not** `PILOT-AUTHORIZED` and must not monopolize the next search. Continue switching scientific objects.