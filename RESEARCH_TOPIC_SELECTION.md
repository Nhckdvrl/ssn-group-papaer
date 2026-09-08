# Research Topic Selection — Final Compact Standard

**Target:** ACL / EMNLP / NAACL Main  
**Aspirational bar:** Best / Outstanding / Best Theme  
**North star:** **Easy to understand, hard to answer. Question first, method second.**

This is the authoritative topic-selection workflow. Keep it short.  
New historical lessons should normally update the kill ledger, **not create new gates**.

---

# 0. What we are looking for

A strong topic should be expressible as:

> **There is an important NLP problem/object X. Existing understanding leaves a real uncertainty Y. We can obtain credible evidence Z that resolves or reframes Y. The resulting paper has a genuinely new identity and changes how NLP understands, measures, models, or solves X.**

The problem must exist before our proposed solution. It may be:
- a natural language / NLP phenomenon;
- a mature modeling or system decision;
- a measurement/evaluation problem;
- a methodological limitation;
- a model-computation question with a concrete consequence.

Do not require every topic to have the same paper shape.

Use Sasano-lab work to calibrate **naturalness and question style**, not as the quality ceiling.  
Use ACL / EMNLP / NAACL Main and relevant top ML papers as the external scientific bar.

No quota. Zero survivors in a round is acceptable.

---


# 1. Topic-Space Prior — Sasano-Lab / Advisor / User Calibrated

The gates above decide **whether a topic is good**. This section decides **where we should spend search effort**.

It is a search prior, not a permanent whitelist: an exceptional topic outside these regions may survive, but search should not repeatedly drift into areas the advisor/user do not want.

## What Sasano-lab topics tell us

Use the lab to calibrate the **kind of object and question that feels natural to the advisor**, not to copy topics or set the quality bar.

Representative patterns seen in the group include:

- **Hamdi:** concrete LLM behaviors such as fictional-entity representation and random-choice mechanisms; move from a clear behavior/question to internal explanation, causal intervention, and a meaningful consequence.
- **Kisako:** internal organization of language/thought in LLMs; representation/compression questions such as sentence-embedding dimensionality reduction and quantization.
- **Sato:** how LLMs acquire character information, using controlled pretraining conditions to answer a concrete mechanism question.
- **Yoda:** practical scientific-document NLP—finding relevant scientific papers and extracting structured experimental/material information from real papers, including text/PDF/image representations.
- **Oshika:** scholarly-document processing such as citation-related paper placement, related-work generation, and scientific-text processing.
- **Yano / Tsujimoto:** semantic-frame / FrameNet / FrameBench-style research. These confirm that classical linguistic/NLP objects are acceptable in the lab, but **this particular project should not follow that branch because of the user's topic preference**.

The useful common pattern is:

> **concrete object → easy-to-state RQ → non-obvious scientific question → appropriate evidence/method**

not:

> **hot technology → search for a place to apply it**

## High-priority search regions for this project

Spend most search effort in:

1. **Model behavior / computation with a concrete NLP consequence**
   - stable, interpretable model behavior;
   - internal computation/representation when it answers a natural RQ;
   - causal/mechanistic work only after the behavior/question is already interesting.

2. **Representation and information encoding**
   - what information representations preserve/lose;
   - when an explicit representation remains necessary or becomes obsolete;
   - compression/organization/readout questions tied to meaningful NLP behavior.

3. **Classic or mature NLP decisions revisited under modern models**
   - old modeling choices whose assumptions have genuinely changed;
   - task formulation, output representation, supervision, inference, or evaluation decisions;
   - prefer broad decision problems over another benchmark comparison.

4. **Documents / scientific and scholarly text**
   - scientific-paper understanding;
   - evidence, claims, results, citations, tables, structured extraction;
   - document-level QA/IE and scholarly communication;
   - natural real documents and externally grounded structure are especially attractive.

5. **Measurement / evaluation / task-definition questions**
   - cases where a standard metric/output unit/task abstraction may erase a scientifically meaningful quantity;
   - only when changing the measurement can change a real NLP conclusion.

6. **Other clean NLP objects with obvious real meaning**
   - IE, QA, knowledge use, structured prediction, generation, retrieval/representation, etc.;
   - allowed whenever the RQ is natural, non-trivial, and not crowded.

## Strong negative prior / default do-not-search regions

### User preference: avoid strongly linguistic topics

Do not proactively search for:
- FrameNet / frame semantics / FrameBench;
- formal semantics-heavy questions;
- syntax-heavy phenomena;
- morphology-heavy topics;
- typology/dialect-focused work;
- garden-path or specialized psycholinguistic phenomena;
- topics requiring a long linguistic lecture before the RQ becomes interesting.

A language phenomenon is still allowed when its distinction is **immediately understandable in ordinary language** and the scientific importance is obvious.

### Advisor/search preference: do not chase hot crowded areas

Do not default to:
- generic Agent / agentic workflow topics;
- generic RAG;
- prompt engineering;
- generic RL/post-training races;
- generic Speech / SpeechLLM;
- generic VLA/robotics;
- API/tool-use/harness trends;
- LLM-as-judge / LLM-as-annotator;
- whatever happens to be fashionable this month.

This is **not a theorem that these fields can never contain a good topic**. It means they carry a strong search penalty because:
- the literature moves too fast;
- parent questions are crowded;
- novelty often collapses to implementation differences;
- paper identity ages quickly.

Only enter a hot area when the RQ is independently natural/durable and novelty remains strong **after removing the fashionable technology label**.

## Search balance

A normal search round should therefore draw rough leads from several of:

- model behavior/computation;
- representation;
- classic NLP decisions;
- document/scientific-text NLP;
- measurement/evaluation;
- other mature natural NLP objects.

Do not make all leads linguistic.
Do not make all leads document NLP.
Do not make all leads mechanistic.
Do not make all leads variants of one generator.

The goal is not topical diversity for its own sake. The goal is to avoid search fixation and keep finding **natural, advisor-compatible Main-level questions**.

---

# Stage A — Broad Search

Search broadly across multiple mother domains. Do not spend a whole round generating variants of one structural template or one recently mentioned hot area.

Useful generators include:
- unresolved natural NLP questions;
- classic decisions revisited under changed model capabilities;
- factors previously conflated;
- questionable measurement/task assumptions;
- data-first opportunities;
- established findings with unresolved explanations;
- new scientific operations that make an old question testable.

These are **idea generators only**.

For each rough lead write only:
1. one-sentence RQ;
2. one plain example;
3. why it matters;
4. plausible data/evidence;
5. obvious closest collision.

Quickly discard obviously trivial, artificial, crowded, or data-impossible ideas.  
No GPU and no long Candidate Card yet.

---

# Stage B — Four Hard Gates

The **gates are strict; the route through them is flexible**.

## Gate 1 — Is the research question worth a Main paper?

Ask:
- Is the underlying problem/object natural, important, and durable?
- Can a simple example make the interest visible?
- Is there genuine uncertainty, tension, or a consequential decision—not an answer that is obvious in advance?
- Would the result change understanding, measurement, modeling, or practice rather than merely report model competence?

Common failure:
> “A known distinction exists; does an LLM know it?”

Also reject claims whose likely reviewer reaction is:
> “Of course. Why was this experiment necessary?”

**Competing Account A/B is a useful default, not a universal requirement.**  
Measurement or methodology papers may instead have a contested quantity, broken assumption, or consequential design choice.

### Continuous conference check
At this gate, compare the **RQ scale and scientific interest** with strong papers of the same identity.

---

## Gate 2 — Can credible data/evidence actually answer the RQ?

Data is part of the science.

Existing natural datasets are preferred **when they fit**, but they are not mandatory.

Allowed evidence includes:
- existing corpora/resources;
- real logs/records/system states;
- published human materials;
- carefully constructed controlled stimuli/data;
- causal interventions or new measurements when direct labels do not exist.

For the load-bearing claim, state the identification chain:

> **data / observation / manipulation / intervention → scientific quantity → claim**

The chain must be scientifically defensible and must not rely on an unexplained proxy.

If constructing data:
- construction must be necessary;
- keep it minimal and interpretable;
- preserve natural language/task properties;
- avoid elaborate synthetic worlds or hypothesis-shaped ontologies;
- validate labels/manipulations independently where needed;
- audit artifacts, leakage, and ecological validity;
- align construction quality with strong papers of the same research type.

The question is **not “is there an existing gold dataset?”**  
The question is:

> **Do we have the simplest high-quality evidence that can genuinely identify the claim?**

### Continuous conference check
At this gate, compare the **data/experimental identification standard** with strong papers of the same identity.

---

## Gate 3 — Does the paper have a genuinely new identity?

Novelty does **not** mean every ingredient is untouched.

Prior work may already contain:
- the object;
- dataset;
- distinction;
- method component;
- one subclaim;
- neighboring experiments.

What must remain distinctly ours is the load-bearing paper identity:

> **new framing/narrative + new idea or decisive operation + new central claim/conclusion**

The exact form varies by paper type.

Mandatory novelty assassination:
- search classic parent work;
- search recent ACL / EMNLP / NAACL, especially 2024–2026;
- use PaperNotes / ACL Anthology / arXiv / OpenReview;
- search relevant ICLR / ICML / NeurIPS when appropriate;
- inspect the closest direct papers, not only surveys.

Mandatory reviewer compression:

> **“This is just ______.”**

If existing work can accurately compress the whole proposed story, **KILL**.

A new model, dataset, language, prompt, scale, cleaner control, or extra mechanism does not by itself create a new paper identity.

### Continuous conference check
At this gate, ask whether our paper would sit beside the closest Main papers as a **new paper**, not as their extension cell.

---

## Gate 4 — Is there enough scientific depth for a Main paper?

Do not bet the project on one fragile favorable result.

The topic should contain a **crisp center plus enough natural depth** to develop without padding.

Depending on paper identity, depth may come from:
- mechanism / attribution;
- boundary / heterogeneity;
- measurement validation;
- theory;
- generalization;
- robustness;
- decision map;
- causal analysis;
- practical consequence;
- a principled method derived from the diagnosis.

Do **not** mechanically require exactly three subquestions.

For scientific/measurement questions, multiple plausible outcomes should remain informative.  
For methodology papers, the diagnosis/problem must be independently important and the paper must contain more than “our trick improves one score.”

Before pilot, the paper should have a plausible claim architecture, often:

- **C1 — Core answer / contribution**
- **C2 — Why, when, or validation**
- **C3 — Consequence / what changes**

This is a heuristic, not a mandatory universal template.

### Continuous conference check
At this gate, compare the **paper depth, evidence breadth, and consequence** with structurally similar Main/Outstanding papers.

---

# Stage C — Deep Audit and Pilot Authorization

Only the strongest leads reach this stage.

Complete the compact Candidate Card:
1. RQ + plain example;
2. why it matters / what is genuinely uncertain;
3. data/evidence and identification chain;
4. closest literature + reviewer compression;
5. our new paper identity;
6. scientific depth / outcome routes;
7. expected claim architecture;
8. smallest decisive pilot;
9. exact kill conditions;
10. dynamic top-conference alignment.

Then:

# PILOT-AUTHORIZED

does **not** mean mainline-approved.

Run the smallest experiment that can materially change the decision.

After the pilot, re-check:
- identification/data validity;
- novelty;
- interpretation;
- paper depth;
- current top-conference alignment.

Kill without sunk-cost protection if the scientific case collapses.

---

# What past failures teach us

Do not add more gates. Remember four failure families:

### 1. Weak question
Known distinction / competence test / obvious conclusion.

### 2. Weak identification
Proxy gold, overconstructed data, or a long uncertain chain between data and claim.

### 3. Weak novelty
The parent narrative or decisive conclusion is already owned.

### 4. Weak paper
One-effect gamble, narrow cell, or no natural route to a full Main-level story.

Almost every historical failure is a version or combination of these four.

---

# Strict vs Flexible

## Strict
- the RQ must be worth asking;
- the evidence must genuinely support the claim;
- paper-level identity must survive serious novelty attack;
- the project must have Main-level scientific depth;
- every stage must be calibrated against relevant strong conference work.

## Flexible
- existing vs constructed data;
- external gold vs controlled identification vs causal intervention;
- whether there are explicit Account A/B;
- exact number of subquestions;
- C2/C3 form;
- model/dataset/reference-paper count;
- behavioral vs mechanistic vs measurement vs methodology paper shape.

Do not turn useful heuristics into universal laws.

---

# Five-line final test

Before spending compute, ask only:

1. **Is this genuinely worth knowing?**
2. **Can our evidence really answer it?**
3. **Is the resulting paper identity genuinely ours?**
4. **Can it grow into a strong paper without depending on one lucky effect?**
5. **Does it hold up beside the most relevant ACL/EMNLP/NAACL Main work?**

If any answer is materially NO, do not promote.

> **Search broadly. Judge simply. Audit novelty deeply. Use evidence that actually answers the question.**
