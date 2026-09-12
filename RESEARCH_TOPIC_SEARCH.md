# Research Topic Search — Find the Right Scientific Question

Updated: 2026-09-12. Target: ACL / EMNLP / NAACL Main.

This file governs **where and how to search**. It does not decide whether a concrete candidate passes selection, and it does not prescribe experiments.

- Search direction and rough-lead generation: **this file**
- Optional generators: [TOPIC_SEARCH_PLAYBOOK.md](TOPIC_SEARCH_PLAYBOOK.md)
- Candidate gates and pilot authorization: [RESEARCH_TOPIC_SELECTION.md](RESEARCH_TOPIC_SELECTION.md)
- Work after authorization: [RESEARCH_EXECUTION.md](RESEARCH_EXECUTION.md)
- Current portfolio and temporary taste: [CURRENT_SEARCH.md](CURRENT_SEARCH.md)

The target intellectual shape is:

> **easy to understand, hard to answer**
>
> **question first → stable phenomenon or real scientific tension → explanation second → method last**

---

## 1. Current Search Taste: What We Actually Want

Open-ended search is **not topic-neutral**. Current priority is model science: questions about why modern language models behave, learn, reason, represent, or change the way they do.

### Primary search space

Spend most search budget on:

1. **Stable model anomaly → unresolved mechanism**
   - a strong, replicated behavior already exists;
   - the parent owns the phenomenon, not the explanation;
   - two or more plausible computational accounts make different predictions;
   - a causal or discriminating operation can separate them.

2. **Training / post-training dynamics**
   - pretraining → SFT → preference/RL/RLVR changes a capability or behavior in a surprising way;
   - ask whether information is learned, selected, suppressed, rerouted, overwritten, or merely read out differently;
   - prefer matched checkpoints, controlled training stages, or other designs that identify the transition.

3. **Reasoning / inference-time computation**
   - when is a decision formed;
   - what causes revision, commitment, recovery, overthinking, or failure to use available information;
   - reasoning vs non-reasoning / base vs instruct differences are useful only when they expose a deeper computational condition.

4. **Representation → computation → behavior**
   - distinguish absent information from inaccessible, suppressed, misread, or policy-overridden information;
   - probes alone are not the target; causal use is.

5. **Old empirical law / challenge → modern computational re-explanation**
   - revisit 2018–2023 claims that genuinely guided research effort;
   - modern models must change a load-bearing premise, not merely improve the score;
   - ideal outcome is a new conditional law, bottleneck migration, or explanation of why the old result held.

6. **Two strong results that conflict on the same scientific quantity**
   - same object, unit, gold/observable, estimand, and intervention meaning;
   - the paper should explain the hidden condition that makes both results true, not rerun a horse race.

### Strong negative search priors

Unless a question is unusually compelling and clearly transcends the area, **do not spend normal search budget** on:

- RAG, retrieval, search, evidence retrieval;
- benchmark construction, benchmark auditing, benchmark contamination;
- metric/evaluator papers, generic evaluation-protocol fixes;
- annotation, adjudication, labeling workflow, dataset-quality or dataset-bias papers;
- data-first reverse search where the dataset field creates the question;
- systematic review / evidence-synthesis infrastructure;
- generic Agent / long-term-memory / RL / judge / harness questions;
- new speech/audio topics;
- pure linguistic competence tests;
- generic bias, calibration, hallucination, prompt-sensitivity surveys.

These are **taste priors, not claims that the areas are scientifically invalid**. A genuinely exceptional question can override them, but “clean gold” or “easy data” is not enough.

### Taste test before deep search

Ask:

> If the dataset name, benchmark name, metric name, and system label disappeared, would I still urgently want to know the answer?

and:

> Is the exciting part “why does the model work this way?”, or merely “the current data/evaluation pipeline is imperfect?”

For current search, strongly prefer the former.

---

## 2. Mandatory Refresh and Anti-Resurrection

Before generating or naming a lead:

1. read `CURRENT_SEARCH.md`;
2. inspect `failed/KILLED_LEDGER.md`;
3. inspect recent `search_rounds/`;
4. inspect nearby archived candidates;
5. for mechanistic ideas, check relevant `Nhckdvrl/Interpretability-try` history.

Search old failures by **scientific object + estimand + decisive operation + synonyms**, not by title.

If a lead resembles KXXX, it must state:

> **Not KXXX because ...**

The reason must be qualitatively new scientific leverage. A new model, dataset, prompt, benchmark, domain, narrower mechanism, or prettier diagnostic does not reopen a dead parent.

Duplicate hits keep the old kill ID.

---

## 3. Generate from Scientific Pressure, Not from Available Tools

A good lead should have an origin that exists before our proposed experiment.

Good origins include:

- a replicated anomaly whose explanation is weak;
- a model-family or training-stage split that existing theory does not explain;
- a strong causal claim supported only by correlational/local evidence;
- an old empirical law whose premise has changed in the foundation-model regime;
- two strong papers that disagree on the **same quantity**;
- a widely used mechanistic explanation that has never survived a decisive intervention;
- a destructive or matched control that reveals a surprising computational invariance or dependency.

Bad origins include:

- “we have activation patching; what can we patch?”;
- “this dataset has an interesting field”;
- “nobody tested model X on task Y”;
- “X is not Y” followed by a search for somewhere to instantiate the distinction;
- a single odd table cell with no evidence that the mother phenomenon is stable.

Methods can reveal questions, but the question must survive without the method name.

---

## 4. Mine Strong Papers for Topic Provenance

Read ACL / EMNLP / NAACL Main and award work for **where the question came from**.

For a useful paper, record a compact Topic Provenance Card:

- **Scientific ancestry:** old problem, empirical law, computational claim, or model behavior.
- **Immediate pressure:** anomaly, contradiction, weak causal evidence, changed model regime, or unexplained transition.
- **Why now:** what modern model/training/intervention makes the old question newly answerable.
- **First decisive operation:** the cheapest observation that could have changed the authors’ belief.
- **Growth path:** how the paper grows from first result to explanation, boundary, consequence, or intervention.
- **Transferable generator:** the discovery move, not the subject matter.

Do not copy titles, topics, or section structures. Transfer the **origin mechanism**.

For the current taste, especially study strong papers with shapes like:

> stable behavior → computational account → causal discrimination → boundary/consequence

or

> old empirical claim → new model regime → matched test → revised law/explanation

---

## 5. Rough Lead Card — Keep It Small

Before deep literature work, write only:

### Hook
One plain-language scientific question.

### Origin
Which stable phenomenon, old empirical claim, training transition, or contradiction caused it?

### Why care
What understanding of model learning/computation would change if the answer differs?

### Mother phenomenon
Is it already credible, or are we secretly betting the paper on discovering it?

### Candidate accounts
What are the smallest live explanations? Do not invent three accounts merely to fill a form.

### Decisive operation
What observation/intervention would actually distinguish the accounts?

### Closest dead route
KXXX / archived candidate / none. If similar: `Not KXXX because ...`.

### Immediate owner risk
Who may already own the question or decisive operation?

### Verdict
Only:
- `NO`
- `MAYBE — blocker`
- `SERIOUS — selection audit required`

Do not create a full candidate package for a rough lead.

---

## 6. SAME-QUANTITY Check Before Claiming a Reversal or Contradiction

When connecting old and modern work, verify:

- same scientific object;
- same unit;
- same observable/gold when applicable;
- same estimand;
- same intervention meaning.

If one side measures NER mentions and the other coreference markables, or one measures consistency and the other correctness, that is not a contradiction until the bridge is independently justified.

Shared terminology is not shared quantity.

---

## 7. Bounded Owner Search

For any `MAYBE` or better lead, search at least:

- exact RQ and close paraphrases;
- parent scientific object;
- decisive intervention/operation;
- same conclusion;
- closest older paper;
- 2024–2026 successors;
- “revisiting / rethinking / does X still / LLM era” variants;
- relevant ACL / EMNLP / NAACL / TACL and, when technical ownership matters, ICLR / ICML / NeurIPS;
- current arXiv when material.

Distinguish:

- **direct collision** — the core answer and consequence are already owned;
- **component overlap** — ingredients are known but the new inference is not;
- **insufficient significance** — technically open but too small;
- **genuine open parent** — important unresolved statement plus a credible way to answer it.

Do not keep refining wording just to escape a neighbor.

---

## 8. Search Stops Before Selection

Search should answer only:

> Is this a natural question in the right search space, with a credible unresolved scientific gap and a plausible discriminating operation?

It should **not** perform every authorization gate itself.

Once a lead reaches `SERIOUS`, hand it to `RESEARCH_TOPIC_SELECTION.md` for:

- identification / construct validity;
- successful-result inference;
- outcome interpretation;
- feasibility and noise floor;
- paper-scale contribution;
- pilot authorization.

This separation is intentional. Search should generate the **right kind of question**; selection should kill weak realizations of it.

---

## 9. Round Discipline

A normal round is:

> **refresh → anti-resurrection → provenance mining → generate → SAME-QUANTITY → owner search → kill or hand off**

Record seriously investigated dead hooks in the dated `search_rounds/` record so the next round does not rediscover them.

No survivor quota. Zero survivors is valid.

But do not confuse aggressive filtering with search quality: repeatedly generating the wrong class of safe data/evaluation topics and then killing them is not progress.

> **The goal is not to find the easiest question to validate. The goal is to find a model-science question worth spending months understanding.**
