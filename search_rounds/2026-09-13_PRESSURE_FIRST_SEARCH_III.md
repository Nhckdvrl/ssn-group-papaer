# 2026-09-13 — Pressure-First Search III

Continuation of `2026-09-13_PRESSURE_FIRST_SEARCH.md` / `_II.md` under the corrected doctrine:

> **scientific pressure first → decisive matched/stress test → phenomenon second**

Only a fully selected `PILOT-AUTHORIZED — E01 ONLY` topic counts as a survivor. The entries below are anti-resurrection records, not candidates.

---

## Hook P7 — Does the hidden grammaticality signal actually control language-model behavior?

**Status:** `DROP / NEW PROPERTY + OLD CAUSAL-PROBING INSTRUMENT`

### Pressure

ACL 2026 reports a striking representation/output gap: sequence probability is not a clean grammaticality classifier, while hidden states contain a linearly decodable grammaticality signal that generalizes across benchmarks and languages. A tempting follow-up is to ask whether this signal is causally used or merely decodable.

### Why it dies

That exact inferential move is old. TACL 2021 *Amnesic Probing* was explicitly designed to distinguish `information is decodable` from `the LM uses it`: remove POS/dependency information from representations and measure downstream language-model behavior. TACL 2023 naturalistic causal probing extends the same logic to morphosyntax. ACL 2025 also documents a grammar knowledge–use gap behaviorally.

Therefore `ACL-2026 grammaticality direction + remove/steer the direction` is reviewer-compressible as a new linguistic property plugged into an established causal-probing instrument. It does not explain why the hidden grammaticality/probability gap exists.

### Anti-resurrection

Do not reopen as `probe ≠ use for grammaticality`, `erase the grammaticality direction`, or `steer grammaticality` unless a new estimand explains the systematic representation/output separation rather than merely establishing causal relevance.

---

## Hook P8 — Why do explicit rules beat demonstrations for novel-rule learning?

**Status:** `DROP / REPRESENTATION-MECHANISM SPACE ALREADY OWNED`

### Pressure

EMNLP 2026 reports a rule-vs-example asymmetry for learning novel tasks in context. The attractive mechanism question is whether explicit instructions and demonstrations create qualitatively different task representations.

### Why it dies

NeurIPS 2025 already directly compares instruction-induced and demonstration-induced function/task representations and finds distinct but partially overlapping internal structures. ACL/ICLR 2026 work further decomposes how demonstrations aggregate into local/global task vectors and where task-vector representations are functional.

Thus `rules > examples → compare task vectors / attention heads / patch the representations` is exactly the prohibited `new mother + existing instrument/representation story` composition.

### Anti-resurrection

Do not reopen as `why rules are better than examples`, `instruction vector vs demonstration vector`, or `explicit rules form cleaner task representations` without a different scientific quantity that current task-vector work cannot imply.

---

## Hook P9 — Are decoded long-horizon plans actually causally used?

**Status:** `DROP / DIRECT 2026 CAUSAL SUCCESSORS`

### Pressure

ICML 2026 work can decode future planning information from hidden states well before the eventual action. The obvious identification question is whether this future information is causally used rather than merely present.

### Why it dies

2026 follow-up work already perturbs/prunes chain-of-thought planning structure and measures downstream actions, while ICLR-2026 work independently studies hidden-state planning horizon and branch awareness. The simple `probe → causal-use` gap is therefore already active and no longer a fresh parent.

### Anti-resurrection

Do not reopen as `does the model really use its decoded future plan`, `planning probe vs intervention`, or `hidden planning horizon causes action` absent a qualitatively new contradiction.

---

## Hook P10 — Does reasoning rescue syntactic complexity by maintaining structure early, or by repairing semantic shortcuts late?

**Status:** `DROP / PREDICTABLE ACCOUNT + NO SELECTIVE FIRST OPERATION`

### Pressure

EACL 2026 CenterBench finds that as center-embedding complexity grows, LMs increasingly substitute semantic plausibility for syntactic structure; reasoning models improve accuracy, but their traces still show semantic shortcuts, overthinking and refusals. ACL 2026 independently shows that adding a concurrent cognitive load pushes strong LMs toward plausibility-based sentence comprehension.

This suggests an initially attractive question:

> **When reasoning helps a syntactically difficult sentence, did the model maintain the structural analysis more strongly from the start, or did it first follow the semantic shortcut and repair it later?**

### Why it dies

The most natural explanation is already heavily constrained by adjacent evidence: load-dependent LLM working-memory failures have been mechanistically tied to interference among overlapping in-context representations, and reasoning/CoT is already widely understood as providing extra external computation/state. `CenterBench + resource-load result + working-memory interference + extra reasoning computation` makes a memory/control or late-repair account unsurprising.

More importantly, no cheap selective E01 was found that distinguishes **early structural maintenance** from **late repair** without either (a) reading CoT text correlationally, or (b) patching/injecting a state that risks directly carrying the answer. Under the L29 first-stage lesson, that is not enough to authorize compute.

Primary sources:

- EACL 2026 CenterBench: https://aclanthology.org/2026.eacl-long.19/
- ACL 2026 dual-task comprehension: https://aclanthology.org/2026.acl-long.552/
- *In-context superposition: human-like working memory interference in large language models*: https://arxiv.org/abs/2604.09670

### Anti-resurrection

Do not reopen as `reasoning gives syntax more working memory`, `reasoning repairs center embeddings`, `CoT suppresses plausibility bias`, or `early parse vs late repair` unless a genuinely selective same-checkpoint operation is found that does not inject the correct parse/answer.

---

## Hook P11 — Does a language model internally maintain both readings of a scope ambiguity, and do those readings causally determine resolution?

**Status:** `DROP / DIRECT EMNLP-2026 OWNER`

### Pressure

Scope ambiguity is a clean semantic object because one surface sentence supports multiple logical readings and context can favor one without changing the sentence itself. TACL 2024 established behavioral sensitivity, leaving an apparent representation/mechanism gap.

### Why it dies

EMNLP 2026 *Do Language Models Understand Implicit Logical Meaning? A Case Study of Scope Ambiguity Resolution in Context* closes the attractive gap directly. Its SCOPEX setup places disambiguating evidence before the ambiguous sentence, analyzes layerwise representations, probes scope specificity, and uses **activation patching** to test whether those internal encodings causally affect behavior. The paper explicitly contrasts itself with the earlier behavior-only setup.

Sources:

- publication listing: https://nlp.unist.ac.kr/publication.html
- public manuscript: https://openreview.net/pdf?id=XgOewsKw4h

### Reviewer compression

> `TACL-2024 behavioral scope ambiguity + EMNLP-2026 internal encoding and causal activation patching = the representation/use mechanism program.`

### Anti-resurrection

Do not reopen as `where are scope readings represented`, `does context causally select inverse vs surface scope`, or `patch scope representations`.

---

## Current semantic-track lesson

The semantic/interpretability lane is worth keeping, but it is especially easy to generate false novelty of the form:

> `new semantic phenomenon/property + probing/steering/patching = paper`.

That is not enough. A viable semantic Main question should instead expose a **load-bearing computational distinction** whose competing accounts make different predictions under a selective operation, or rewrite a classic semantic law under a genuinely changed reasoning/post-training regime.

No new `PILOT-AUTHORIZED` topic is produced by this log.

---

# Batch provenance continuation — corrected `Explore → batch-generate → assassinate` mode

This continuation explicitly avoids the prior low-throughput loop `one paper → one neighbor hook → deep search`. Strong ACL/EMNLP/NAACL and adjacent award papers are mined first for their **minimal inferential move**, then that move is transferred across independent scientific objects. Strong-researcher problem-selection material is used only to constrain the generator: expand surface area before committing; ask whether the best-case result is itself exciting; prefer goal-driven questions over paper-driven +10% continuations; and do not confuse a method/property bridge with a contribution.

## Hook P12 — Scalar implicature: direct stronger-alternative access or broad activation → narrowing?

**Status:** `HOLD — IDENTIFICATION`

### Pressure

Recent human processing work separates at least two stages in scalar inference: alternative activation and subsequent alternative exclusion / pragmatic inference. A live account predicts broad semantic activation followed by grammar/context-sensitive narrowing; a rival predicts more direct access to the relevant stronger alternative. Recent negation experiments support broad activation but still leave the timing of suppression unresolved.

ACL 2026 *Continuous Interpretive Steering for Scalar Diversity* already shows that activation steering can manipulate final pragmatic interpretations. Therefore `scalar implicature + probe/steer/patch` is not enough.

### Blocker

No selective same-model operation has yet been found that distinguishes **direct stronger-alternative access** from **broad activation followed by rapid narrowing** without collapsing to layerwise probing/patching. Do not authorize compute until the intervention itself identifies the processing accounts.

---

## Hook P13 — Contextual diversity: acquisition speed vs decontextualized generalization

**Status:** `DROP / KEY TRADEOFF ALREADY OWNED NEARBY`

### Pressure

TACL 2024 reports that, frequency-controlled, tokens seen in more diverse contexts can be learned later / less stably, while controlled human studies show a familiar-context vs novel-context reversal: narrow exposure can aid early/familiar-context learning while diverse exposure improves transfer to new contexts. This initially suggested a clean split between acquisition speed and decontextualized generalization.

### Why it dies

2025 *Facts in Stats* already demonstrates in controlled LM pretraining that contextual diversity can delay in-distribution factual acquisition while being necessary for some forms of out-of-distribution recall, and traces the effect to embedding/unembedding bottlenecks. Moving the same speed↔OOD tradeoff from factual associations to lexical semantics is too reviewer-compressible as domain transfer.

Do not resurrect by replacing facts with words, pseudo-words, or another lexical dataset unless a qualitatively different scientific quantity emerges.

---

## Hook P14 — Does anticipated future access selectively shape parametric knowledge encoding?

**Status:** `SERIOUS — HAND TO SELECTION AUDIT; NOT PILOT-AUTHORIZED`

### One-line RQ

> **When a language model learns identical new facts, does prior experience with how those facts will later be queried selectively shape how the facts are encoded, or does pre-instruction-tuning merely improve generic learnability / retrieval policy?**

### Provenance

ACL 2024 *Instruction-tuned Language Models are Better Knowledge Learners* shows that exposing a model to QA before continued pretraining substantially improves later learning from new documents. The authors explicitly hypothesize that learning how knowledge is accessed before document learning changes subsequent knowledge absorption. Their ablations reject simple post-hoc elicitation, forgetting, and answer-token upweighting explanations; PIT also generalizes across domains and to real-user question forms.

What remains unidentified is stronger than the method claim: does **anticipated future access selectively shape the encoding of facts that arrive later**?

Primary source: https://aclanthology.org/2024.acl-long.296/

### Three accounts

- **A — prospective encoding:** access specialization learned before a fact arrives selectively changes how that later fact is encoded. A/B access specialization should produce a larger A↔B crossover for facts learned **after** specialization than for facts learned before it.
- **B — generic learnability:** PIT creates a generally better document learner. New facts improve across access views without a selective A↔B crossover.
- **C — retrieval-policy specialization:** PIT mainly specializes how queries are answered. The A↔B preference should appear similarly for facts learned before and after specialization.

### Decisive estimand

Do not use uncontrolled pretraining facts as `OLD`. Use a controlled temporal factorial:

1. inject an identical set of novel `OLD` facts into every arm;
2. train access specialization `A` vs `B` on separate auxiliary content;
3. inject an identical set of novel `NEW` facts into every arm;
4. evaluate both OLD and NEW facts under matched A/B query views.

Primary signature:

`(PIT-A − PIT-B) × (query-A − query-B) × (NEW − OLD)`.

This removes the obvious `A/B is merely query-format practice` confound: a pure retrieval-policy change affects OLD and NEW similarly, whereas prospective encoding predicts extra selectivity only for knowledge encoded after the access policy exists.

### Selection blockers

1. A/B access views must be isomorphic enough that a three-way interaction cannot be reduced to relation-specific extraction difficulty, output-space imbalance, or the Reversal Curse parent.
2. The best A/B construction should target a meaningful **access operation**, not superficial prompt formatting. Candidate constructions should be compared before any run; no prompt search after results.
3. Resolution must be established with a small modern open-weight model before expensive scale-up; no model zoo.
4. Bounded owner search found PIT descendants and query-conditioned adaptation methods, but no direct owner of the temporal A/B × query-view × old/new interaction. This remains a bounded-search conclusion, not proof of novelty.

### Successful-result upper bound

A strong three-way crossover would show that parametric knowledge acquisition is not query-neutral: before the model has even seen a fact, prior learning about **how information will later be used** can selectively determine how that fact becomes retrievable. This is materially stronger than `PIT gives +X QA accuracy` and has a direct cognitive analogue in transfer-appropriate processing / encoding–retrieval interactions.

---

## Hook P15 — What computational mechanism creates the spacing benefit in LM training?

**Status:** `SERIOUS — SELECTION AUDIT REQUIRED; HIGH SUCCESSOR PRESSURE`

### Pressure

Spacing is one of the oldest and most robust learning laws. Human memory theory still entertains competing accounts including deficient processing, study-phase retrieval / reinstatement, and encoding/state variability. In 2026 the object became directly relevant to machine learning: *Spacing effect improves generalization in biological and artificial systems* reports spacing/variation benefits in artificial networks, and *When to Review: Spaced Repetition for Continual Pre-Training of Language Models* applies adaptive spaced repetition to LMs and reports large retention gains.

Sources:

- https://doi.org/10.1016/j.patter.2026.101564
- https://arxiv.org/abs/2608.17530

### Candidate accounts in SGD terms

- **A — deficient processing / update collapse:** adjacent repetitions become easy immediately, so later massed presentations have tiny loss / effective gradient and contribute little new learning.
- **B — state-dependent re-encoding / reinstatement:** intervening training moves the model into a different parameter/representation state; recomputing the same example later yields complementary update directions, not merely larger updates.
- **C — adaptive selection rather than classical spacing:** recent LM gains may be driven mainly by reviewing examples when their recall signal deteriorates, rather than by spacing per se.

### Identification direction

A naive `match massed gradient norm to spaced gradient norm` experiment is not yet sufficient, because rescaling itself changes the optimizer trajectory. A more selective chain should be sought before authorization, e.g.:

- normalize/equalize per-presentation update magnitude in **both** massed and spaced schedules, asking whether spacing survives when magnitude collapse is removed;
- if it survives, hold update magnitude fixed and compare recomputed later gradients against a matched cached/first-gradient direction control to ask whether state-dependent gradient direction is necessary;
- include an adaptive-scheduling control so a null classical spacing effect can still distinguish `spacing` from `review-at-forgetting` rather than merely fail.

### Why not yet pilot

The mother is credible in artificial systems and adaptive LM replay, but a clean fixed-exposure massed-vs-spaced law in language-model factual learning is not yet as well established as the human mother. The paper must remain interpretable if the pure spacing component is small. High successor pressure from the August 2026 SRT paper also raises the novelty bar.

---

## Hook P16 — Are local morphological exemplars causally used online for analogical generalization?

**Status:** `DROP / DATA-ATTRIBUTION BRIDGE + IDENTIFICATION RISK`

### Pressure

PNAS 2025 *Derivational Morphology Reveals Analogical Generalization in Large Language Models* fits rule-based vs exemplar-based cognitive models to training-data statistics and finds GPT-J nonce-word behavior much better matched by analogy, motivating the claim that similarity operations over stored exemplars underlie linguistic generalization.

Primary source: https://doi.org/10.1073/pnas.2423232122

### Why it dies

The obvious causal follow-up is to remove/downweight a probe's nearest training exemplars while preserving aggregate suffix statistics and ask whether the local nonce decision moves. But 2026 mechanistic data-attribution work already establishes the broader `training examples → mechanism/behavior` causal program. On GPT-J, approximate unlearning also does not identify what true training-data absence would have done; retraining from scratch on a controlled lexicon weakens the original-model claim.

This is therefore likely reviewer-compressible as `new linguistic object + established training-data attribution instrument`, with an additional construct-validity problem.

---

## Hook P17 — Prediction surprise vs structural repair in garden paths

**Status:** `DROP / CROWDED 2025–2026 SUCCESSORS`

### Pressure

PNAS 2026 human evidence reports that LM surprisal predicts early forward-reading garden-path slowdown but not later regressions/rereading, motivating a tempting distinction between generic prediction error and a separate structural repair process.

### Why it dies

COLING 2025 already augments surprisal with LLM-derived structural signals for reanalysis; ACL 2026 Main directly revisits whether neural LM surprisal explains garden paths; ACL 2026 work also studies recovery dynamics and layerwise hidden-state divergence. `matched surprisal + hidden-state repair signal` is therefore too close to an active successor cluster unless a qualitatively new causal identification operation appears.

Do not reopen as generic garden-path representation/recovery probing.

---

## Hook P18 — Neg-raising: syntactic/semantic derivation or pragmatic reconstruction?

**Status:** `HOLD — IDENTIFICATION`

The semantics/pragmatics dispute remains live in 2026, including new analyses of `I don't think p` vs `I think not p`. This is scientifically attractive because competing accounts already exist independently of LLMs. However, no operation has yet been found that distinguishes the accounts in a model without reducing to contextual behavioral tests plus layerwise probing/patching. Do not promote on theory elegance alone.

---

## Updated batch verdict

Current new-search state from this batch:

- **P14 prospective-access-conditioned encoding:** `SERIOUS — Selection audit required`; strongest current lead from this batch.
- **P15 spacing mechanism in LM training:** `SERIOUS — Selection audit required`, but with higher successor/mother-phenomenon risk.
- **P12 scalar implicature processing:** `HOLD — IDENTIFICATION`.
- **P18 neg-raising:** `HOLD — IDENTIFICATION`.
- P13 contextual diversity, P16 analogical morphology, P17 garden-path repair: dropped for owner/reviewer-compression reasons.

None is `PILOT-AUTHORIZED`; approved paper mainline remains unchanged.
