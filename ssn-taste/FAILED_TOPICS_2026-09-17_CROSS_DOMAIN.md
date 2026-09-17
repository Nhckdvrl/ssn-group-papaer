# Failed Topics — 2026-09-17 Cross-Domain Search

**Status:** durable kill ledger. Read together with the other `FAILED_TOPICS*` files before generating new topics.

---

## F24 — Content memory versus source memory in parametric learning

**Question.** As a language model learns a proposition more strongly, does it lose the binding between that proposition and where it came from, analogous to human semanticization/source amnesia? Are content memory and provenance memory governed by different learning dynamics?

**Why it looked promising.** Human memory distinguishes item/content memory from source memory, and pretraining aggregates many documents into one next-token objective. Repetition across sources could strengthen proposition content while washing out source identity, creating a natural mechanism question rather than a citation benchmark.

**Nearest prior.** *Source-Aware Training Enables Knowledge Attribution in Language Models* (2024) directly begins from the observation that LMs acquire knowledge in pretraining while often remaining unaware of its source, and trains explicit source/document bindings. ICLR 2026 *Cite Pretrain* likewise makes persistent source↔fact binding during pretraining the central capability.

**Failure reason.** The mother question `can parametric factual knowledge remain bound to its source, and how should pretraining create that binding?` is already directly occupied. Reframing it with the cognitive-science term `source memory` would not change reviewer-level ownership.

**Revival condition.** A source-memory law or dissociation that cannot be reduced to source attribution/binding and that yields a qualitatively different causal intervention, not merely another citation/provenance setup.

---

## F25 — Does single-reference SFT treat one valid sample as an exclusive label?

**Question.** A natural-language response in an SFT corpus is typically one valid sample from a many-valid-output distribution. Cross-entropy nevertheless increases the observed continuation relative to unobserved alternatives. Does post-training therefore learn demonstrations as samples from a distribution or as effectively exclusive labels, and what happens to equally valid unseen responses?

**Why it looked promising.** The tension follows directly from the one-to-many nature of language and the token-level likelihood objective; it does not depend on a reported anomaly. It also suggests interpretable outcomes about support preservation, redistribution, and mode concentration.

**Nearest prior.** ICLR 2025 *Preserving Diversity in Supervised Fine-Tuning of Large Language Models* explicitly argues that conventional CE maximizes likelihood of observed responses without accounting for alternative possibilities and studies diversity loss. ACL 2026 Main *Learning Diverse Responses with Prefix-Conditioned SFT* studies optimization interference/diversity collapse with multiple valid responses to the same prompt. Findings ACL 2026 *ProFit* explicitly frames ordinary SFT as ignoring the one-to-many nature of language by forcing alignment with a single reference. Related 2026 work analyzes when finite-sample SFT produces under- or over-dispersion.

**Failure reason.** The central conflict `single observed gold response versus many valid outputs` and its consequence for output diversity/support are already active, explicit research objects. Calling it `exclusive-label semantics` would be a reframing rather than a new parent.

**Revival condition.** A non-diversity consequence of single-sample likelihood with a distinct theoretical prediction not covered by mode collapse/support preservation/one-to-many SFT.

---

## F26 — Lexical content versus prosodic/paralinguistic evidence in speech LMs

**Question.** When lexical content and prosody/paralinguistic cues conflict, which signal governs a speech-language model's interpretation, and does training create a lexical shortcut that suppresses acoustically expressed meaning?

**Why it looked promising.** CV/video research offers a recurring puzzle in which one modality or shortcut dominates another even when the weaker signal is causally relevant. Speech provides a natural same-transcript intervention that can isolate the acoustic contribution.

**Nearest prior.** ACL 2024 *Advancing Large Language Models to Capture Varied Speaking Styles and Respond Properly in Spoken Conversations* explicitly constructs identical transcripts with different speaking styles that should elicit different responses. EACL 2026 work on paralinguistic understanding explicitly identifies lexical shortcuts over paralinguistic cues, and ACL 2026 speech-to-speech evaluation/training work studies paralinguistic instruction following and ASR-centric suppression of non-lexical information.

**Failure reason.** The parent `speech LMs over-rely on lexical content and underuse paralinguistic/acoustic evidence` is already directly occupied. Borrowing shortcut-learning language from CV does not create a new scientific object.

**Revival condition.** A distinct acoustic-linguistic interaction with a causal prediction not reducible to lexical shortcutting or paralinguistic instruction following.

---

## F27 — Mutual exclusivity / fast mapping as a route to new-word learning in neural models

**Question.** When a learner encounters a novel word alongside familiar and unfamiliar referents, does it infer the new mapping by excluding already-named objects, and can this inductive bias explain rapid lexical acquisition in modern neural models?

**Why it looked promising.** Mutual exclusivity is a classic child-language-learning principle with a simple, interpretable intervention and direct connection to open-vocabulary learning; it looked like a promising example of importing a mature cognitive-science question rather than mining a recent LLM anomaly.

**Nearest prior.** NeurIPS 2020 *Mutual Exclusivity as a Challenge for Deep Neural Networks* directly studies this bias in deep networks. EMNLP 2022 uses mutual-exclusivity training to induce compositionality. ACL 2023 Outstanding *World-to-Words* studies grounded open-vocabulary acquisition via fast mapping, and TACL 2024 directly reports mutual-exclusivity bias in visually grounded speech models.

**Failure reason.** The cognitive-science parent itself has already been explicitly transported into neural and multimodal language learning. Applying it to a newer LLM/VLM family would be `old question + new model`, exactly the pattern to avoid.

**Revival condition.** A different language-acquisition principle whose neural-learning parent is not already occupied and whose identifying intervention produces genuinely new predictions.
