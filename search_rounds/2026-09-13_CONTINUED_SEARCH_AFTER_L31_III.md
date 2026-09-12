# 2026-09-13 — Continued Search After L31 III

Continuation of `2026-09-13_CONTINUED_SEARCH_AFTER_L31_II.md`. Same persistence rule: every nontrivial kill is written immediately; only topics that fully pass SEARCH + SELECT and reach `PILOT-AUTHORIZED — named bounded E01` are reported as candidates to do.

## S. Punctuation / filler tokens as hidden context-memory carriers — DROP broad parent

**Scientific object:** Why do seemingly low-content tokens such as punctuation, articles, and stopwords carry disproportionate contextual information, and are they computational memory hubs rather than mere syntax markers?

**Mother:** Findings NAACL 2025 `LLM-Microscope: Uncovering the Hidden Role of Punctuation in Context Memory of Transformers` reports that punctuation/determiners/stopwords carry surprisingly high contextualization and that removing them degrades MMLU and BABILong even when they appear irrelevant.

**Direct successor / owner:** Findings EACL 2026 `Punctuations and Predicates in Language Models` explicitly begins from that anomaly and applies intervention-based necessity/sufficiency tests across layers and models. It finds punctuation both necessary and sufficient in multiple GPT-2 layers, much less so in DeepSeek, and not at all in Gemma, then extends the analysis to static summaries versus dynamic propagation and reasoning rules.

**Related pressure:** 2026 punctuation-aware sparse-attention work already operationalizes punctuation as semantic-boundary anchors for long-context retrieval, so the broad `punctuation is a hidden context carrier` observation is also becoming methodologically exploited.

**Reviewer compression:** `LLM-Microscope punctuation-context anomaly + EACL-2026 causal necessity/sufficiency across models = punctuation-memory mechanism is already the direct successor line`.

**Kill reason:** the obvious mechanism question is no longer open. A new punctuation mark, task, layer intervention, or model family would be a cell. The cross-model heterogeneity (`GPT-2 yes, DeepSeek partial, Gemma no`) is interesting but currently comes from one direct successor and does not yet establish a stable same-quantity law whose hidden condition is independently pressured; promoting it now would repeat the L31 mistake of turning one paper's model-family heterogeneity into a route-selection project.

**Anti-resurrection:** do not reopen as `why commas store context`, `filler tokens are memory hubs`, punctuation necessity/sufficiency, punctuation as static summaries, or model-family punctuation differences unless independent work first establishes the same cross-model computational split and a non-obvious causal axis.

---

_Continue appending killed leads here._
