# S12 — Does In-Context Learning Distinguish Definitions from Facts?

**Status:** CANCELLED — CURRENT DESIGN KILLED AFTER E03 (mother question unresolved)  
**Registered:** 2026-09-25  
**Target venues:** ACL / EMNLP / NAACL Main  
**Scientific type:** in-context learning / semantic vs world knowledge / typed contextual updating

## Parent question

When the same relation is introduced in context, does a language model track **what kind of thing is being updated**?

Concretely:

> **Does an LM distinguish a relation that defines what a new term means from an extensionally identical relation that merely describes what is true in the current world?**

A compact example is:

- **Definition role:** in the current language, an object is a `dax` iff it is a red triangle.
- **World-fact role:** in World A, an object is a `dax` iff it is a red triangle.

The core relation can be literally identical, and the observed extension in World A can be identical. But the two statements have different scopes. If we move to World B while keeping the language fixed, the lexical definition should continue to constrain `dax`; the contingent World-A fact need not.

The scientific object is therefore not whether the model can read the phrase “by definition.” It is whether **in-context adaptation is typed by semantic role**—for example, meaning/terminology versus world state—or whether both are reduced to an undifferentiated association between tokens and properties.

## 30-second why-care

LLMs are routinely taught new vocabulary, schemas, labels, APIs, rules, and world facts inside a prompt.

A model can appear to have “learned a new concept” on seen cases even if it only learned that two predicates currently co-occur. Those two possibilities make different predictions when the world changes.

So the basic question is:

> **When we teach an LM something in context, does it know whether we changed the language or changed the world?**

If it does, contextual learning supports functionally distinct update roles. If it does not, success on ordinary definition-learning tasks may overstate what “learning a new meaning” amounts to.

## Scientific pressure

There is a longstanding distinction between **word/lexical knowledge** and **world/encyclopedic knowledge**: knowing what an expression means is not the same thing as knowing facts that happen to hold of its referents.

Modern LMs make this distinction especially consequential because both kinds of information are delivered through the same mechanism at deployment: token context. A single frozen transformer is expected to absorb a temporary definition, a schema rule, and a fact about the current environment through ordinary conditioning.

Nearby work establishes the ingredients:

1. LMs can follow factual and counterfactual concept definitions to some degree.
2. LMs can induce representations of novel semantics in context, while often struggling to deploy them flexibly.
3. Linguistic cues can teach LMs new world information about novel entities.
4. Recent semantic work distinguishes intensional structure from extensional reference.

What remains unresolved is whether the model uses **the status of a contextual statement** to determine how that information should persist when the surrounding world changes.

## Knowledge-delta statement

**Prior knows:** LMs can process definitions, learn novel contextual representations, and update/infer facts about artificial worlds.

**Still unknown:** whether an extensionally matched relation is treated differently depending on whether it is **constitutive of a term’s meaning** or **contingent on the current world**.

**Why prior does not answer it:** existing definition-following work asks whether models obey supplied definitions; novel-semantics work asks whether representations are encoded and usable; world-inference work asks what facts are inferred from discourse. None of these requires the model to distinguish two contexts with the same core relation and same current extension but different update scope.

**Our experiment first separates:**

- a **typed-update world**, where definition-like information and world-state information have different persistence;
- an **untyped-association world**, where the same relation is treated similarly regardless of its contextual role;
- a **surface-role heuristic**, where a difference appears only under explicit labels such as “Definition:” but does not survive natural discourse-role paraphrases.

## Why this is not “old linguistics + new LLM”

The contribution is not to re-test a human lexical-semantic effect.

The modern changed regime is **in-context adaptation**: the same frozen autoregressive model is used as a temporary learner of both interface semantics and environment state, with no separate symbol table, ontology store, or world-state module.

The question is therefore model-native:

> **Is contextual conditioning functionally typed by what the prompt is updating, or is it one generic association mechanism whose apparent semantics come only from the surface sequence?**

The old lexical/world distinction supplies the scientific pressure; the object under test is how modern LMs perform contextual updating.

## Main possible worlds

### World A — typed contextual update

The model tracks that a definition has language/terminology scope while a fact has world scope.

Predictions:
- a definitional relation transfers to a new world when the language is held fixed;
- a World-A relation does not automatically transfer to World B;
- a World-B observation that violates the old relation is contradictory under the definition condition but coherent under the World-A-fact condition;
- the difference survives several natural ways of establishing the discourse role.

This would show that identical relational content can be stored/used according to different functional roles during in-context adaptation.

### World B — untyped relational association

The model mainly learns the `dax ↔ red-triangle` association and does not preserve whether it came from a definition or a world description.

Predictions:
- both conditions generalize similarly across worlds, or both fail similarly;
- changing the role while holding the core proposition fixed has little systematic effect;
- seen-case success therefore does not identify lexical-semantic learning versus ordinary contextual association.

This would weaken common interpretations of successful “novel meaning learning” from prompt behavior.

### World C — explicit-cue following without role generalization

The model differentiates conditions only when the prompt contains highly explicit metalinguistic markers such as “definition,” “means,” or “dictionary,” but the distinction collapses when the same role is established through ordinary discourse context.

This would imply that apparent type-sensitive updating is primarily instruction/cue following rather than a robust distinction in contextual information use.

World C is diagnostic, not a separate paper claim.

## Nearest-prior boundary

### Fonseca & Cohen — Can Large Language Models Follow Concept Annotation Guidelines? (Findings ACL 2024)

This work evaluates factual and counterfactual concept definitions in annotation guidelines. It establishes that models can sometimes follow remapped definitions.

It does **not** compare a definition with an extensionally identical contingent fact, nor ask whether their information should persist differently after a world change.

### Lepori et al. — Language Models Struggle to Use Representations Learned In-Context (ACL 2026 Main)

This work shows that models may encode novel semantics presented in context yet fail to deploy those representations flexibly.

S12 asks a different question: when the relational content is held fixed, does the model distinguish **what role that information has** in the contextual state?

### Brubaker et al. — Wugnectives (EACL 2026 Main)

Wugnectives studies whether discourse connectives allow LMs to infer attributes of novel entities—that is, how language cues update world knowledge.

It does not contrast world updating with meaning/definition updating under matched relational content.

### Evelo et al. — Language Models Can Resolve Reference Compositionally, But It’s Not Their Native Strength (TACL 2026)

This work distinguishes intensional interpretation from extensional reference in a compositional reference task.

S12 is not an intensional-versus-extensional performance comparison. It studies the **scope/persistence of a contextual update** when the same extension is initially compatible with two different information roles.

### Belief / knowledge / fact work

Recent work such as KaBLE establishes that LMs have difficulty with epistemic distinctions among belief, knowledge, and fact.

Those are attitudes toward propositions. S12 instead contrasts a proposition that **constitutes a temporary vocabulary rule** with one that **describes a temporary world**.

## Minimum decisive pilot

No training, probe, LLM judge, human annotation, or large benchmark is required.

### 1. Generate tiny synthetic micro-worlds

Each item contains:
- one nonce predicate such as `dax`, `wug`, or `kef`;
- one programmatically generated property such as `red ∧ triangle`;
- a small World A whose objects make the relation extensionally true.

Avoid real-word category priors.

### 2. Hold the core proposition fixed

Use the same sentence in both conditions, for example:

> “An object is a dax if and only if it is red and triangular.”

Only its discourse role changes.

**Definition condition:** the sentence is presented as a glossary / terminology / language-use entry.

**World-fact condition:** the sentence is presented as a field report / survey result / description of World A.

The core proposition, nonce word, property, and World-A extension remain matched.

### 3. Move to World B while preserving the language

World B creates cases where the two roles diverge.

#### Readout A — contradiction under an exception

State that a World-B object is a blue `dax`.

Ask a forced-choice consistency question.

- definition condition → inconsistent with the unchanged lexical rule;
- World-A-fact condition → coherent, because the World-A regularity need not hold in World B.

#### Readout B — transfer to a new instance

Give a new red triangle in World B without specifying whether it is a `dax`.

Ask whether `dax` is entailed.

- definition condition → yes;
- World-A-fact condition → not entailed.

Use exact categorical scoring.

### 4. Surface-role diagnostic

Use a small fixed set of natural role framings rather than one keyword:

Definition-like:
- glossary entry;
- terminology convention;
- “for this discussion, use the word …”;
- dictionary/manual entry.

World-fact-like:
- field report;
- census/observation summary;
- “in World A …”;
- environment description.

Crucially, keep the **core relation sentence unchanged** within matched pairs.

The purpose is not a prompt sweep. It is only to rule out a single literal-marker explanation.

## Primary statistic

The primary quantity is the **role × transfer interaction**.

For matched items, measure how much changing only the contextual role changes correct behavior in World B.

Do not make raw benchmark accuracy the contribution.

A typed-update account predicts a strong crossed pattern:
- definition transfers across worlds;
- World-A facts do not.

An untyped account predicts substantially weaker differentiation.

## Why the pilot directly answers the science

The manipulated variable is the **status/scope of the same contextual relation**.

The decisive outcome is what happens when the original world changes.

There is no intermediate requirement to:
- discover a probe;
- invent a latent metric;
- train a classifier;
- validate a judge;
- collect natural-language annotations;
- fine-tune a model;
- run a model zoo.

The first batch already asks the mother question.

## Execution discipline

Start with one strong open instruct model and roughly 100–200 matched items.

Use:
- random nonce predicates;
- several primitive property combinations;
- 3–4 pre-fixed role formulations;
- deterministic decoding or a small fixed sampling protocol.

Only after a clean qualitative result:
- replicate on one second model family;
- optionally add one non-lexical schema case to test whether the effect generalizes beyond nonce nouns.

Do not initially expand into:
- broad ontology benchmarks;
- API/tool-use evaluation;
- many linguistic constructions;
- human experiments;
- hidden-state analysis;
- dozens of prompt variants.

## Kill conditions

Kill S12 if any of the following occurs:

1. A nearest prior is found that already holds relational content/current extension fixed and directly contrasts **definition/meaning scope vs contingent world scope**.
2. The matched design cannot separate knowledge status from a simpler logical-form difference.
3. The effect exists only for literal labels like `Definition:` versus `Fact:` and disappears when role is conveyed through ordinary discourse context.
4. The only defensible contribution becomes “models follow definitions better/worse than facts,” rather than differential persistence under world change.
5. Interpreting the result requires hidden-state probes or a learned evaluator because the behavioral interaction is weak.
6. The project naturally expands into a large lexical/world-knowledge benchmark or a model/prompt matrix before the mother question is answerable.

A robust null is **not** itself a kill condition. If the matched contexts genuinely produce no role-sensitive transfer while the model succeeds on the within-World-A controls, that directly supports the untyped-association world and is scientifically meaningful.

## Claim boundary

Do **not** claim:
- that LMs possess human-like lexical semantics;
- that this resolves the philosophical analytic/synthetic distinction;
- that a behavioral difference proves separate internal modules;
- that nonce-word behavior automatically generalizes to all ontology or API learning.

The defensible claim is:

> **S12 tests whether in-context learning uses the contextual status of information—definition versus world fact—to control how an otherwise matched relation persists when the world changes.**

Mechanistic work is optional later depth only after the behavioral law is established.

## Final pilot adjudication — 2026-09-26

E01–E03 were executed and the registered design is **KILLED**.

Final E03 used a fresh held-out batch with 360 matched main prompts and 216 controls. Controls were 216/216 correct and all final answers parsed exactly.

Key result (correct / 60):

| Condition | Positive transfer | Exception / coexistence |
|---|---:|---:|
| Definition | 60/60 | 60/60 |
| Fact-natural | 1/60 | 0/60 |
| Fact-explicit | 60/60 | 26/60 |

Within Fact-explicit exception items, question form produced a predeclared split: 26/30 correct for the “impossible” wording versus 0/30 for the logically complementary “can both be true” wording.

Interpretation:
- natural report framing did not localize the bare biconditional;
- explicit World-A-only scope can repair positive transfer, showing that the model can use world scope when it is stated strongly enough;
- the exception readout remains unstable and highly wording-sensitive even after explicit scope;
- therefore the current instrument does not cleanly identify a robust natural discourse-role distinction between definition updating and world-fact updating.

This triggers the registration's own kill criterion: the effect does not survive natural discourse-role framing and requires stronger explicit scope manipulation, while one main readout remains question-form dependent.

**Verdict:** KILL current S12 design. The broader language-update-vs-world-update mother question remains unadjudicated.

Do not revive by:
- adding stronger scope prompts;
- sweeping many phrasings;
- adding model families;
- moving directly to hidden-state/mechanistic analysis;
- treating the E03 polarity split as a new finding without independent novelty checking and held-out validation.

A future revival would require a new scientific rationale and a newly frozen instrument that separates definition/meaning status from world-state status without making explicit scope wording itself the operative variable.

See `experiments/S12_E03/RESEARCH_LOG.md` and commit `7e04161`.

## Promotion status

**CANCELLED from current selection.**

S12 survives because:
- the why-care is understandable in one sentence;
- the pressure concerns a native deployment property of modern LMs, not merely a transplanted human effect;
- nearest work separately studies definitions, novel semantic representations, and world inference but does not own the same decisive unknown;
- the project does not depend on a surprising anomaly;
- both typed and untyped outcomes revise a meaningful interpretation of in-context learning;
- a tiny programmatic experiment directly separates the worlds;
- the core proposition and current extension can be matched across conditions;
- the scoring is analytic and exact;
- no training recipe, evaluator, probe, or benchmark construction is required before answering the scientific question.
