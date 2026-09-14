# 2026-09-15 — WALL-K / Advance Planning in Autoregressive Generation — Exhaustion Audit

**Target:** ACL / EMNLP / NAACL Main, calibrated against TACL / ICLR / ICML / NeurIPS / AAAI  
**Mode:** classic production-planning dispute → neural generation ancestry → current direct-owner / identifying-operation audit  
**Outcome:** **WALL-K EXHAUSTED AS A CURRENT TOPIC GENERATOR — NO NEW L-SERIES — NO PILOT**

> The old scientific problem is real: sequential behavior may be executed one unit at a time while being planned at a larger structural scope. But the straightforward LM descendant (`does an autoregressive Transformer plan future tokens before emitting them?`) is already directly owned by COLM 2024, and the attractive `word vs phrase / hierarchical planning scope in LMs` descendant has no independent model-science theory that makes phrase boundaries the load-bearing quantity. It reviewer-compresses to psycholinguistic planning scope × an existing LM planning instrument.

---

# 0. Mother scientific problem

> **How much of a sequential linguistic action is planned in advance before the current production unit is executed?**

This is older than neural language models. Speech production is incremental, but incrementality does not imply that only the next word is planned. A producer can execute sequentially while preparing a larger phrase, clause, semantic relation, or action structure in advance.

The durable tension is:

- **minimal / highly incremental planning:** prepare little beyond the next lexical unit;
- **phrasal / hierarchical planning:** prepare a larger structurally meaningful unit before onset;
- **adaptive planning:** scope changes with task, structure, accessibility, experience and resource pressure.

The scientific object is the **scope and organization of advance planning**, not whether an output sequence happens to be coherent.

---

# 1. Classic sentence-production dispute

## 1.1 Phrase vs word as planning scope

Martin et al. (Cognition 2010), **Planning in sentence production: evidence for the phrase as a default planning scope**, explicitly frame a controversy over the scope of advance lexical planning.

Sources:
- https://pubmed.ncbi.nlm.nih.gov/20501338/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC2930890/

Their experiments control alternative explanations involving retrieval fluency and visual grouping and repeatedly find longer speech-onset latency when the initial phrase contains more nouns. They interpret this as evidence that speakers often plan at least the initial phrase before speech onset.

The important scientific point is not the latency effect itself. It is that **sequential realization can be preceded by preparation at a larger grammatical unit**.

## 1.2 Planning scope is not fixed

A broad psycholinguistic lineage subsequently shows that planning scope varies with:

- lexical accessibility;
- structural complexity;
- production experience;
- message formulation;
- task demands;
- cognitive/resource pressure.

This weakens any universal `one phrase is always planned` law. The mature question becomes what determines planning scope and whether the scope follows meaningful grammatical / conceptual structure rather than a fixed token horizon.

The human literature therefore gives a real old scientific problem, but it does **not** automatically make a Transformer experiment evidence about humans; the repo's exhausted WALL-F already forbids that linking leap without an independent model-system theory.

---

# 2. Neural language generation had explicit planning long before current LLMs

Classic and neural NLG systems have repeatedly separated **content / structure planning** from surface realization.

Examples include explicit sentence / document planning and later latent planning architectures. Neural work such as:

- Shu & Nakayama 2018, **Discrete Structural Planning for Neural Machine Translation**: https://arxiv.org/abs/1808.04525
- Hu et al. ACL 2022, **PLANET: Dynamic Content Planning in Autoregressive Transformers for Long-form Text Generation**: https://aclanthology.org/2022.acl-long.163/

adds explicit latent or discrete planning states to improve structure and coherence.

These papers do not answer whether a *vanilla* autoregressive LM spontaneously plans ahead, but they remove one weak novelty claim:

> `language generation benefits from a higher-level plan before / during word realization`

is already a mature engineering and modeling idea.

---

# 3. Direct modern owner: Wu, Morris & Levine, COLM 2024

**Do Language Models Plan Ahead for Future Tokens?** asks almost the exact vanilla-model question.

Sources:
- https://arxiv.org/abs/2404.00859
- https://openreview.net/forum?id=BaOAvPUyBO

They distinguish two explanations for hidden-state features at time `t` that help inference at future times `t+τ`:

### Pre-caching

Training causes the model to compute features at the current timestep that are not needed for the current next-token prediction but are useful for later timesteps.

### Breadcrumbs

Features needed now happen also to be useful later; apparent foresight therefore need not reflect extra computation devoted specifically to the future.

The paper supplies an unusually strong identifying operation: **myopic training**, which removes gradient propagation from future losses into earlier hidden-state computations.

Findings:

- clear pre-caching in a constructed synthetic setting;
- natural-language modeling is more consistent with breadcrumbs at smaller scales;
- evidence for pre-caching grows with model scale.

This is not merely `probe the hidden state for future tokens`. It directly asks whether training allocates computation now for future inference and supplies a counterfactual learning intervention.

Therefore the obvious descendant:

> **Does a standard autoregressive LM really plan ahead?**

is directly occupied.

---

# 4. The surrounding 2024–2026 program is already dense

## 4.1 Planning from autoregressive learning itself

Wang et al. 2024, **ALPINE: Unveiling the Planning Capability of Autoregressive Learning in Language Models**, develops a theory of how next-token learning can acquire path-finding representations and studies the learned adjacency / reachability structure.

Source:
- https://arxiv.org/abs/2405.09220

This directly occupies another tempting route:

> `derive when next-token prediction can create planning computation`.

## 4.2 Myopic decoding / explicit lookahead is an active method program

Ma et al., ICLR 2025, **Non-Myopic Generation of Language Models for Reasoning and Planning**, formalize ordinary autoregressive decoding as myopic decision making and introduce predictive decoding based on model-predictive-control-style foresight.

Source:
- https://openreview.net/forum?id=OoNazl6T7D

Noci et al. 2026, **Thinking into the Future: Latent Lookahead Training for Transformers**, explicitly gives the model multiple latent lookahead steps before token commitment.

Source:
- https://arxiv.org/abs/2603.20219

Current latent-prediction / multi-token-prediction work further studies higher-level or longer-horizon representations.

Thus `NTP is too myopic; add lookahead / hierarchy` is a crowded method parent, not a fresh scientific question.

## 4.3 Internal future-use signals are already being reported in current ACL work

ACL 2026 **Retrieval Heads are Dynamic** finds that retrieval heads change over autoregressive timesteps and that current hidden states contain predictive signal about future retrieval-head patterns; the authors interpret this as evidence of internal planning.

Source:
- https://aclanthology.org/2026.acl-long.715/

Whatever one thinks of that interpretation, it increases owner density for generic `future computation is already represented now` analyses.

---

# 5. Strongest residual: planning **scope**, not existence

The most attractive way to avoid the direct owner is to return to the classic psycholinguistic dispute:

> **If an autoregressive LM prepares future material, is the unit of advance preparation a fixed token horizon, or a structural unit such as a phrase / clause / semantic subgoal?**

At first glance this is appealing:

- old scientific ancestry;
- both answers matter;
- token-level autoregression and grammatical hierarchy make opposite intuitions plausible;
- hidden-state / training interventions could in principle quantify future influence across structural boundaries.

It still does **not** survive promotion.

---

# 6. Why `word vs phrase planning scope in LMs` fails

## 6.1 The phrase boundary is motivated for human production, not independently for Transformer computation

In human production, phrase boundaries are theoretically privileged because conceptual / grammatical formulation and motor execution have an established processing architecture.

For a decoder-only LM, importing `phrase` as the natural planning unit needs its own theory. Otherwise the experiment is:

> classic psycholinguistic variable × Transformer hidden state.

That is exactly the banned generator shape.

## 6.2 Human evidence cannot supply the missing theory automatically

One might claim:

> if LMs also plan by phrase, they illuminate human sentence production.

But WALL-F has already established why behavioral / mechanistic similarity between LM and human production requires a separate linking hypothesis. Using humans to motivate the unit and then treating agreement as evidence of shared mechanism is invalid.

## 6.3 Wu et al.'s intervention already owns the generic future-computation distinction

Any experiment that removes future-loss influence, measures current features useful for future tokens, or compares myopic vs standard training starts from Wu et al.'s central estimand.

Adding syntax-conditioned bins does not create a new parent unless an independent theory predicts a **qualitative crossover at a structural boundary** that the existing work cannot derive.

No such unowned model-science theory was found.

## 6.4 Fixed-horizon vs hierarchical planning easily becomes metric engineering

One could define `planning horizon`, `future-information radius`, or `structural foresight index`. But without a theory that privileges one notion, these are measurements of a phenomenon whose interpretation remains ambiguous:

- future token predictability;
- shared features / breadcrumbs;
- explicit pre-caching;
- long-range dependency;
- semantic coherence;
- actual action commitment.

A new scalar does not identify which computation is taking place.

## 6.5 Planning is already overloaded across neighboring literatures

Current papers use `planning` to mean at least:

- pre-computing future-useful representations;
- search / path finding;
- long-horizon action selection;
- explicit subgoal decomposition;
- latent future prediction;
- document content organization;
- anticipatory retrieval.

A paper that exploits the shared word `planning` without SAME-QUANTITY alignment risks building the scientific bridge after seeing the literature.

---

# 7. Reviewer-compression tests

### K1 — `Do LMs plan future tokens?`

Compression:

> Wu, Morris & Levine 2024 already ask exactly this with a direct training intervention.

**KILL — DIRECT OWNER.**

### K2 — `Is LM planning word-sized or phrase-sized?`

Compression:

> Martin / sentence-production planning-scope theory + Wu-style LM future-token instrument.

No independent LM theory makes phrase the decisive unit.

**KILL — PSYCHOLINGUISTIC PHENOMENON × LM / MECHANISTIC TOOL.**

### K3 — `Does scale create more lookahead?`

Wu et al. already report pre-caching increases with model scale.

**KILL — DIRECT RESULT / MODEL-ZOO DESCENDANT.**

### K4 — `Does reasoning require non-myopic generation?`

ICLR 2025 predictive decoding and 2024–2026 planning / latent-lookahead work directly occupy this family.

**KILL — CROWDED METHOD PARENT.**

### K5 — `Hierarchical plan latent emerges under NTP`

ALPINE and current latent-prediction work occupy representation / learning-theory versions; a probe-only result would be weaker.

**KILL — ACTIVE PROGRAM / WEAK IDENTIFICATION.**

---

# 8. Anti-resurrection additions

Do not regenerate via:

- another probe for future-token information in current hidden states;
- `planning horizon` / `future token radius` as a new metric;
- phrase vs clause vs sentence bins without an independent causal theory;
- Wu et al. myopic training on a newer / larger model;
- `scale increases planning`;
- natural-language syntax inserted into path-finding / maze planning;
- psycholinguistic planning-scope task applied to LMs as evidence about human production;
- reasoning benchmark comparisons of standard vs explicit lookahead as the scientific contribution;
- retrieval-head / attention-head prediction treated as proof of planning.

A future reopening requires one of two things:

1. a **model-native theory** that independently predicts a particular structural planning unit and an opposite result under a matched intervention; or
2. a genuinely new operation that distinguishes **future-specific computation** from ordinary shared features / breadcrumbs in a regime not already covered by myopic training.

Merely changing structure, model scale, hidden-state tool or downstream task is insufficient.

---

# 9. Wall verdict

The classic advance-planning question is scientifically excellent, but the bridge to a new LM-science project fails:

- existence of future-specific LM computation is directly owned;
- explicit non-myopic generation is an active method program;
- human phrase-level planning does not automatically define the model's natural causal unit;
- importing the human dispute gives a prohibited `old psycholinguistic theory × LLM` project.

**Decision: WALL-K exhausted as a current generator. No new L-series. No pilot.**
