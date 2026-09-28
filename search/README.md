# Search

This directory contains **topic-search philosophies**.

A search lane answers:

> **Which problem territory is important enough to enter and explore deeply?**

It does **not** need to predict the final paper idea, method, mechanism, or result.

The output of search is a handoff into `../workbench/<territory>/`, not a candidate ID.

Current lanes:
- `sasano-taste/` — governed by Sasano's research taste.
- `our-taste/` — our own broad search lane.

## What search should produce

A useful search result is closer to:

> “This scientific object / problem is important, not obviously exhausted, and worth spending weeks understanding. Here is the strongest baseline / parent work / data / artifact to start from, and here are the main unknowns.”

It is **not**:

> “Here is a beautiful paper title, expected finding, mechanism, and method; now run an experiment to prove it.”

The expected result may be wrong. That is normal.

## Read papers for idea genesis, not only for final ideas

Do not read a strong paper only as:

> problem → final method → benchmark gain.

Reconstruct the path that could plausibly have produced the work.

For an important paper / lineage, ask:

1. **Parent state:** What was the strongest prior method / baseline / accepted belief before this paper?
2. **Pressure:** What concrete failure, inefficiency, contradiction, scaling problem, or awkward design choice made the parent unsatisfactory?
3. **Changed premise:** Which assumption did the paper stop accepting?
4. **Earliest revealing experiment:** What small analysis or baseline comparison could have exposed the pressure before the final method existed?
5. **Exploration path:** What alternative explanations or directions would a reasonable researcher have tested?
6. **Crystallization:** At what point does a real RQ / bottleneck / method become justified by evidence?
7. **Related-work boundary:** Why is the final contribution not merely “prior A + prior B”, a new model, a new dataset, or an obvious future-work cell?
8. **What to imitate:** Is the reusable move baseline strengthening, decomposition, re-attribution, representation redesign, changed optimization object, causal intervention, etc.?

### Important epistemic rule

A paper's Introduction is a polished scientific narrative. It is **not automatically the authors' historical brainstorming process**.

Keep two notions separate:

- **documented genesis** — explicitly supported by author blog, talk, appendix, repo history, or retrospective;
- **scientific genealogy reconstruction** — our reasoned reconstruction of how one could naturally move from the parent literature to the final work.

The second is extremely useful for learning how to find research questions, but must not be presented as biographical fact.

## Do not mine one paper for a “gap”

Prefer a **small lineage** over a single paper:

> parent → successor → strongest current baseline → failure / changed assumption.

A future-work sentence or one published anomaly is only a lead. Often the original authors or immediate follow-ups already own the obvious next step.

The goal is to understand **where the field's problem representation changed**, and which important difficulty remains visible after strong baselines.

## Handoff to workbench

Before opening a workbench, search should provide only:

- why the territory matters;
- why it is suitable for this search lane;
- strongest practical baseline / parent implementation;
- relevant data / public artifacts;
- nearest important lineage;
- 3–6 **uncertain diagnostic questions**;
- major feasibility / ownership risks.

Do **not** require:
- an expected sign;
- a final RQ;
- a paper title;
- a method;
- a candidate ID.

Rules:
- no experiments under `search/`;
- no topic-specific subdirectories under `search/`;
- no candidate IDs here;
- detailed taste criteria live inside each lane.
