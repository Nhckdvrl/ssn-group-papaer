# S04 — How Do Language Models Update Situation Models Across Event Boundaries?

**Status:** SELECTED — PILOT-AUTHORIZED  
**Registered:** 2026-09-18  

## One-sentence parent question

When a narrative shifts from one event to the next, how does an autoregressive language model update its internal representation of the current situation: by locally editing only what changed, by reconstructing a broader active situation state, or by selectively reactivating/rebinding relevant past information?

This is the parent question. Do **not** narrow the project to proving one specific cognitive theory, one boundary token, one SAE feature, or one exact patching effect.

---

## Why this is worth asking

Narrative understanding requires more than detecting that an event boundary exists. A model must continue to use information that remains relevant, replace information that changed, and stop relying on information that is no longer part of the current situation.

Classical situation-model and event-segmentation theories distinguish different update mechanisms. A change may trigger a local/incremental edit, a broader reconstruction of the current situation model, or a selective reactivation/rebinding process at event boundaries.

This creates a natural mechanistic question for autoregressive LMs: their past token states remain in context and old KV states are not literally rewritten, yet downstream behavior can reflect an updated world state. What computation transforms a stream of text into an updated active situation representation?

The question exists independently of any one recent LLM anomaly.

---

## ACL/EMNLP width calibration

This topic is intentionally registered at the level of **situation-model updating in LMs**, not at the level of an ultra-narrow claim such as `global updating exists`.

Relevant ACL-family work shows that this width is appropriate:

1. **ACL 2026 Main — Injecting Context via Situation Working Memory for Logical Reasoning with LLMs.** This paper explicitly treats dynamically updated situation models (time, space, causality, intention, protagonist) as an NLP object and engineers an external situation memory. It does not characterize the native internal update computation of pretrained LMs.

2. **ACL 2026 Main — Action Boundary Blindness.** This paper imports Event Segmentation Theory to study action granularity/boundaries in LLM agents. It owns a behavioral/action-boundary problem, not internal narrative situation-state updating.

3. **EMNLP 2025 Main — Discursive Circuits.** It studies mechanisms of discourse understanding using controlled contrastive data and activation patching. This calibrates that a mature discourse phenomenon can support a Main mechanistic paper when the internal computation and causal story are new.

4. **ICLR 2026 — Priors in Time / Temporal Feature Analysis.** It shows that LM activations contain rich temporal dynamics and that Temporal SAE features delineate narrative event boundaries. It owns temporal-feature extraction and boundary-aligned representational structure; it does not ask what information is updated/reconstructed/reactivated at a boundary or which update computation causally supports later narrative understanding.

5. Existing cognitive/neuroscience work provides competing mechanisms rather than novelty blockers: incremental vs global situation-model updating, and selective reactivation of relevant past events at boundaries.

**Novelty boundary:** the contribution is not event-boundary detection and not merely showing that event structure is represented. The contribution is to characterize and causally distinguish how an LM transforms its active situation representation when event structure changes.

---

## Main competing explanations

### H1 — Incremental editing

Only dimensions that actually change are substantially updated. Unchanged information remains available mainly through the existing historical/contextual representation.

Prediction: representations/causal pathways for changed dimensions reorganize strongly at transitions, while unrelated unchanged dimensions show substantially weaker reinstatement/reorganization.

### H2 — Global reconstruction

A sufficiently strong event transition causes the model to construct a new active situation representation containing multiple currently relevant dimensions, including information that did not itself change.

Prediction: an event boundary induces coordinated reorganization/reinstatement of both changed and still-relevant unchanged information.

### H3 — Selective reactivation / rebinding

Boundaries trigger reactivation of information selected for relevance to the new event rather than a literal full reset of every dimension.

Prediction: changed and still-relevant past information are selectively reinstated/rebound, whereas obsolete or irrelevant past information is not.

These hypotheses organize the investigation. The paper does not need to prove that one classical cognitive theory transfers literally to LMs.

---

## Data strategy

No benchmark construction is the contribution.

Use two complementary sources:

### A. Small controlled narratives for identification

Generate tens to a few hundred short, natural micro-stories with independently manipulable situation dimensions such as:

- protagonist / active character;
- location;
- object/property;
- goal/action.

Create matched conditions such as:

- no meaningful shift / within-event continuation;
- one-dimension shift;
- multi-dimension/event shift;
- unchanged-but-still-relevant information;
- obsolete/irrelevant past information.

These items are **experimental instruments**, not a benchmark.

### B. Natural narratives for ecological validation

Use existing narrative/event-segmentation materials or publicly available stories with human/event-boundary annotations when practical. Natural data are secondary validation; the first pilot does not require a large annotation campaign.

---

## Pilot E01 — Is there boundary-linked reorganization of situation information?

Start with one open 7B–8B model and roughly 100–300 controlled micro-stories.

For each story, track 2–3 independent situation dimensions through a matched transition. At several layers/tokens, measure whether information about each dimension becomes more or less accessible around the transition.

The first pilot does **not** need a new interpretability method. Simple linear decoding / representational similarity / logit-based probes are acceptable as discovery tools, provided the final claim is not based only on probe accuracy.

The key comparison is not merely `boundary vs non-boundary`. It is:

- **changed information**;
- **unchanged but still relevant information**;
- **obsolete/irrelevant information**;

under matched within-event and event-transition conditions.

### Informative patterns

- Mostly changed dimensions reorganize -> supports an incremental-update story.
- Changed + relevant unchanged dimensions jointly reorganize -> supports broader reconstruction/reactivation.
- Relevant unchanged information is selectively reinstated while obsolete information is not -> supports selective reactivation/rebinding.
- No systematic distinction -> reassess whether native LMs maintain an event-level situation state at all.

E01 is exploratory. None of these outcomes is a failed pilot by definition.

---

## Pilot E02 — Causal test of the update computation

Only after E01 reveals a stable representational signature, perform causal intervention.

Preferred tools include activation patching, targeted ablation, attention-path intervention, or a temporary historical-access restriction.

A useful causal-bottleneck design is:

1. Let the transition region process the full prior context normally.
2. For a downstream query/continuation, restrict direct access to pre-transition tokens while preserving the transition/post-transition states.
3. Test which old information remains causally recoverable from the post-transition representation.

This can distinguish:

- selective/global carry-forward of active situation information;
- generic summarization of everything salient;
- pure direct retrieval from old tokens with little compact event-state transfer.

This bottleneck is a **strong causal experiment**, not a requirement for the very first run.

---

## Zhao-style mechanistic path

If E01 passes, the intended explanation chain is:

1. **Representation:** identify the geometry/content of the active situation state across time.
2. **Computation:** characterize the transformation at event transitions — local edit, reconstruction, selective reactivation/rebinding, or another discovered primitive.
3. **Implementation:** localize which layers/attention/MLP pathways implement the transformation only after the higher-level computation is clear.
4. **Causality:** intervene on that transformation/pathway and test downstream use of changed and unchanged information.
5. **Optional controllability:** only if justified, test whether manipulating the update computation changes narrative-state tracking.

Do not begin by hunting heads/SAEs and then invent the scientific question afterward.

---

## Why this is exploratory rather than anomaly gambling

Several qualitatively different outcomes answer the same parent question:

- LMs primarily edit changed dimensions;
- LMs reconstruct broad active situation states;
- LMs selectively reactivate only currently useful past information;
- different layers/timescales implement different mixtures;
- LMs rely mostly on direct retrieval and show little event-level state reconstruction.

The paper remains interpretable across these outcomes.

---

## Feasibility

- Initial data: tens to a few hundred short stories; trivial to generate and manually inspect.
- Initial model: one open 7B–8B checkpoint is enough.
- E01: inference + activation collection; cheap.
- E02: patching/masking on the same examples; still inference-only.
- No pretraining, large SFT run, judge model, or expensive annotation campaign is necessary for the first decision.

---

## Kill / demotion conditions

Kill or demote if:

- newly located prior work directly characterizes the same internal situation-update computation at event boundaries;
- the effect exists only for punctuation/sentence boundaries and disappears under semantic-boundary controls;
- `changed / relevant-unchanged / obsolete` information cannot be separated in a way that yields a coherent update story;
- the project devolves into event-boundary detection accuracy or a narrative benchmark;
- the contribution becomes merely `we found a feature/head correlated with boundaries`;
- causal intervention cannot connect the identified transformation to later use of situation information.

Do **not** kill merely because neighboring work studies event boundaries, situation models, narrative representations, or discourse circuits. Normal scientific overlap is expected; novelty is in the internal update computation and causal story.

---

## Registration verdict

**SELECTED — PILOT-AUTHORIZED.**

The registered question is deliberately broad enough for ACL/EMNLP/NAACL Main:

> **How do language models update their active situation representations when one narrative event becomes another?**

Incremental editing, global reconstruction, and selective reactivation are competing mechanistic explanations, not three separate topics and not an over-narrow novelty claim.

---

## 2026-09-19 execution-risk re-audit — KEEP / PILOT-AUTHORIZED

S04 survives the S03-informed feasibility audit because it does not reconstruct a training history. The main risk is instead **construct ambiguity**: probe accessibility alone cannot establish an update computation.

### Tightened execution gate

The first decisive experiment should prioritize a causal history-access bottleneck over broad probing:

- process a matched event transition normally;
- at a downstream query/continuation, block direct attention/access from the query region to pre-transition tokens while preserving post-transition states;
- compare changed, still-relevant-unchanged, and obsolete information.

Proceed to Zhao/Cho-style mechanistic localization only if post-transition states carry a reproducible, content-selective signature that causally supports later use.

**KILL immediately** if:
- probe effects are present but disappear under the causal bottleneck;
- the pattern reduces to generic recency/sentence-boundary effects;
- incremental vs reconstruction/reactivation cannot be distinguished without increasingly elaborate representational assumptions.

**Final status: KEEP — PILOT-AUTHORIZED.**
