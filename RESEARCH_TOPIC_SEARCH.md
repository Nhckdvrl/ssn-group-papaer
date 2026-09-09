# Research Topic Search — Authoritative Search Workflow

**Target:** NAACL Main  
**External bar:** ACL / EMNLP / NAACL Main, with Best / Outstanding / Best Theme / other unusually strong-paper-identity work as high-end calibration.  
**North star:** **Easy to understand, hard to answer. Question first, method second.**

This file governs **how we search for research questions**. It does not decide whether a concrete candidate deserves a pilot; that belongs to **RESEARCH_TOPIC_SELECTION.md**.

---

# 1. Document boundaries

The topic side has only three conceptual layers:

- **RESEARCH_TOPIC_SEARCH.md** — hard search discipline: how to search, what not to do, advisor/user constraints, per-round process.
- **TOPIC_SEARCH_PLAYBOOK.md** — non-authoritative inspiration library: anomaly mining, contradictory papers, Old Problem / New Method, data-first, lab-style seeds, etc.
- **RESEARCH_TOPIC_SELECTION.md** — once a concrete RQ exists, formally judge it and decide PASS / HOLD / KILL / PILOT-AUTHORIZED.

Supporting state:
- **CURRENT_SEARCH.md** records current portfolio/status only.
- **failed/KILLED_LEDGER.md** prevents accidental resurrection of dead parents.
- **RESEARCH_EXECUTION.md** governs projects only after a topic enters execution.

**A useful search generator must never silently become a hard gate.**

---

# 2. What we are searching for

We are not searching for:
- an untouched benchmark cell;
- a strange failure that may or may not exist;
- a method looking for a problem;
- a dataset simply because it can be built;
- a topic that is merely “publishable.”

We are searching for:

> **a natural and important NLP/LLM question whose answer is genuinely non-obvious, for which credible evidence can resolve a real uncertainty, and which can become a paper with its own Main-level identity.**

The problem should exist independently of our proposed method.

A good rough lead should make another NLP researcher think:

> “Yes, that is a real question.”

but not:

> “Isn’t the answer obvious?”

---

# 3. Hard search rules

## 3.1 Question first

Search for the scientific question before choosing:
- activation patching;
- probing;
- steering;
- GRPO / RLVR;
- a benchmark;
- a model family;
- a particular dataset.

A method is valuable only when it gives new leverage on a worthwhile question.

## 3.2 No quota pressure

A search round may produce zero survivors.

Never lower naturalness, data quality, novelty, or Main-level scale to fill a target count.

Correctly killing weak ideas is successful search work.

## 3.3 Multi-track search is mandatory

A normal round must inspect several genuinely different mother domains and/or generators.

Do not spend the whole round on:
- one recently successful generator;
- one task family;
- one “X ≠ Y” template;
- one representation trick;
- one annotation schema.

There is no numerical quota per track. The goal is to prevent search fixation.

## 3.4 Naturalness before cleverness

Prefer:
- a real NLP object;
- a plain-language example;
- obvious scientific or practical meaning;
- little setup before the tension is visible.

Strong negative search prior:
- formal-semantics-heavy;
- FrameNet/frame-semantics-heavy;
- syntax-heavy;
- morphology-heavy;
- typology-heavy;
- specialized psycholinguistics-heavy;
- any topic requiring a long linguistic lecture before the RQ becomes interesting.

This is a search prior, not an absolute ban. A language problem can survive when it is immediately understandable and important.

## 3.5 Data/evidence feasibility enters early

Do not postpone the data question until after becoming attached to the idea.

For every serious rough lead, ask:

> **What observation, gold, controlled manipulation, or intervention could actually identify the scientific quantity?**

Prefer:
- natural existing data;
- official/provider-defined state;
- real human behavior;
- published experimental materials;
- benchmark-native gold when it truly matches the estimand;
- naturally occurring interventions.

Controlled constructed data are allowed when necessary, but must be:
- minimal;
- natural;
- interpretable;
- independently defensible;
- directly tied to the scientific variable.

Never build an elaborate synthetic world merely to manufacture an effect.

## 3.6 Do not gamble on one unverified phenomenon

Default suspicion:

> “If failure X appears, we have a paper; if X disappears, the project dies.”

Prefer research spaces where several plausible outcomes remain informative.

The current highest-priority shape is:

> **established anomaly → unresolved mechanism / boundary / consequence**

because the phenomenon already exists.

But this is a priority track, **not the only valid search philosophy**.

## 3.7 Old parent problems are allowed

Do not kill a topic because its parent question is old.

Classic NLP questions can be excellent when modern models create genuinely new leverage:
- causal intervention;
- long-context reading;
- end-to-end collapse of old pipeline boundaries;
- representation inspection;
- controlled post-training;
- changed supervision/inference regimes;
- ability to test an old assumption at scale.

The novelty question is:

> **Has the modernized scientific question and its decisive story already been done?**

not:

> “Was this parent discussed 20 years ago?”

## 3.8 Novelty is paper-level

The object, dataset, distinction, method component, or one subclaim may already exist.

What must remain ours is the load-bearing paper identity:
- framing/narrative;
- decisive scientific operation or idea;
- central claim/conclusion;
- consequence.

Mandatory reviewer-compression test:

> **“This is just ______.”**

If one or a few prior papers can accurately fill the blank and compress the whole proposed paper, stop.

## 3.9 Literature must be current

Before a rough lead becomes serious:
- search classic parent work;
- search recent ACL / EMNLP / NAACL;
- inspect the closest direct papers, not only surveys;
- use relevant ICLR / ICML / NeurIPS for mechanistic, causal, representation, measurement, or methodology identities;
- refresh novelty whenever the central claim/narrative changes.

Do not make permanent novelty decisions from a stale literature snapshot.

## 3.10 Main-level alignment is continuous

At search time already compare:
- RQ scale;
- naturalness;
- scientific tension;
- likely evidence standard;
- likely paper identity;
- likely consequence.

Use structurally relevant strong papers. Award papers are high-end anchors, not mandatory templates.

The local candidate pool is never the quality ceiling.

---

# 4. Advisor/user constraints

Advisor discussion should be preserved without accidentally turning every comment into a universal law.

## Durable constraints

Carry these into search unless newer advisor guidance supersedes them:

- do not assume a behavioral phenomenon is real merely because one setup seems to show it;
- comparison conditions must be scientifically meaningful and fair;
- reason from a reviewer’s perspective, especially whether the distinction really changes the conclusion;
- do not lock the project to one domain when the scientific question does not require it.

## Recurring concerns, not universal gates

Apply extra scrutiny when relevant:

- probability-based evidence can be easy to overinterpret;
- model-family differences can break a seemingly general story;
- forgetting/unlearning or other neighboring mechanisms may be necessary comparison points when they are the obvious alternative explanation;
- legal, biomedical, linguistic, or any other domain should not be preserved simply because an early version started there.

Future advisor notes should be classified as either:
- **HARD REQUIREMENT**, or
- **CONCERN / SEARCH PRIOR**.

Do not turn a one-off discussion remark into a permanent gate without evidence that this was intended.

---

# 5. Search priors

Spend most attention across several of:
- model behavior/computation with a concrete NLP consequence;
- representation and information organization;
- post-training effects when the question is durable and not a generic RL race;
- classic/mature NLP decisions reopened by foundation models;
- scientific/scholarly document understanding;
- evidence synthesis and structured information;
- tables and structured observations;
- measurement/evaluation/task-definition;
- retrieval/generation/IE/QA when the RQ is natural and not a benchmark cell;
- strong recent areas with unresolved assumptions but without heavy crowding.

Strong negative prior:
- generic Agent;
- generic RAG;
- generic RL/post-training;
- generic VLA/robotics;
- generic Speech/SpeechLLM;
- prompt engineering;
- LLM-as-judge / LLM-as-annotator;
- generic hallucination;
- generic bias;
- generic calibration;
- generic “does the LLM know X?”;
- benchmark creation as the main contribution.

A hot area is acceptable only when the question remains natural and durable after removing the fashionable technology label.

---

# 6. Per-round workflow

## S0 — Refresh state

Before searching:
1. read the top of **CURRENT_SEARCH.md**;
2. inspect the active candidate registry;
3. inspect **failed/KILLED_LEDGER.md** for nearby dead parents;
4. use the current date for literature novelty;
5. sample strong recent Main papers for calibration.

Do not resurrect a killed route without a qualitatively new reason.

## S1 — Calibrate with strong papers

Look for:
- natural RQ scale;
- what makes the question non-trivial;
- evidence/identification standard;
- how the paper develops beyond C1;
- unresolved findings, contradictions, or assumptions.

## S2 — Generate rough leads across multiple tracks

Use **TOPIC_SEARCH_PLAYBOOK.md** as a menu, never as a checklist.

For each rough lead write only:
1. one-sentence RQ;
2. one plain example;
3. why it matters / what is not obvious;
4. plausible data or intervention;
5. obvious closest collision.

Do not create a full candidate package yet.

Do not spend target-model GPU just to discover whether a topic exists.

## S3 — Cheap assassination

Immediately discard when:
- the question is artificial or trivial;
- the likely answer is obvious;
- the data cannot plausibly identify the claim;
- the story already compresses to prior work;
- the topic exists only if one fragile phenomenon appears;
- novelty is only a model/dataset/prompt/language change;
- the likely contribution is just another benchmark result.

If uncertain, keep it as a rough lead rather than promoting prematurely.

## S4 — Hand off to formal selection

A lead enters **RESEARCH_TOPIC_SELECTION.md** only when:
- the RQ is clear and natural;
- there is real scientific uncertainty or a consequential contested decision;
- a credible evidence path exists;
- no immediate fatal collision is known;
- the topic appears capable of surviving more than one lucky effect.

## S5 — Record only what belongs where

- live search/portfolio status → **CURRENT_SEARCH.md**
- serious killed parents → **failed/KILLED_LEDGER.md**
- reusable generators → **TOPIC_SEARCH_PLAYBOOK.md**
- candidate evaluation rules → **RESEARCH_TOPIC_SELECTION.md**

Do not create a new root document for every lesson.

---

# 7. Extra discipline for anomaly search

Anomaly search is high priority because it lowers phenomenon risk.

Good sources:
- Main/Award paper reports a stable large effect;
- an appendix/table contains a large unexplained gap;
- capability ordering reverses;
- scaling behaves unexpectedly;
- one intervention preserves A but destroys B;
- authors say “surprisingly,” “unclear why,” “remains unexplained,” or leave the mechanism open;
- two strong papers suggest incompatible explanations.

Before promotion:
- confirm the effect is not a tiny single-setting fluctuation;
- require a natural consequential object;
- identify at least two plausible explanations or a meaningful unresolved mechanism;
- identify a decisive intervention;
- check follow-up literature has not already consumed the explanation space.

Do not confuse systematic anomaly mining with random setting search.

---

# 8. One-page search test

Before formal candidate evaluation, ask:

1. Can I explain the question in one or two sentences?
2. Would an NLP researcher agree the object matters?
3. Is the answer genuinely uncertain or consequential?
4. Do I already see a credible data/intervention path?
5. If the first expected effect is absent, is there still a scientific question?
6. Can the whole paper still plausibly be ours after current literature search?
7. Have I searched outside the generator that worked last time?
8. Does the question look capable of sitting beside strong ACL/EMNLP/NAACL Main work?

If several answers are NO, keep searching.

> **Search broadly. Use generators lightly. Promote slowly. Never let a good search trick become the project’s only philosophy.**
