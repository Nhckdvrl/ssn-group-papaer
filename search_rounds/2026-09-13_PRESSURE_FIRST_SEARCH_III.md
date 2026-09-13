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
