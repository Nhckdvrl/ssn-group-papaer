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

## Top-conference ceiling gate

Search is not only deciding whether a territory is **researchable**. It is deciding whether the territory has enough scientific / technical headroom to justify aiming at **ICML / ICLR / NeurIPS / ACL / EMNLP / NAACL / CVPR-level main-track work**.

This does **not** mean the surface topic must be broad or require huge compute. A narrow experimental object can be excellent if it exposes or overturns a broad premise. What is not enough is a narrow object whose best plausible outcome remains a local follow-up.

Before opening a workbench, explicitly test the territory's **ceiling**:

1. **Parent-scale question:** What broader scientific/technical assumption, bottleneck, design principle, or capability does this object inform?
2. **Best-case consequence:** If the most interesting plausible outcome is true, what would the field understand or do differently?
3. **Worst reviewer compression:** Could a reviewer accurately dismiss the project as “X on one more model/dataset/language/domain”, “another slice”, or “a small fix for one benchmark”? If yes, do not open the workbench yet.
4. **Evidence runway:** Is there room for multiple independent kinds of evidence—strong baselines, cross-model/regime checks, causal/diagnostic analyses, downstream consequences, or a method naturally implied by the bottleneck—rather than one lucky experiment?
5. **Abstraction beyond substrate:** If the first substrate is removed, is there still a scientific object? The initial game, dataset, language, model family, or benchmark may be an instrument, but should not be the whole reason the problem matters.
6. **Venue fit:** Which top venue community would care, and which existing high-level conversation would the result enter? “No one has tried this exact combination” is not a venue fit.
7. **Growth room:** Can several months of baseline residency and exploration plausibly make the story **more general and simpler**, rather than forcing increasingly narrow controls?

A territory fails the gate when:

> even its best plausible outcome is only a correct but local observation, benchmark patch, model-specific quirk, or incremental variant.

Such a result can still be useful knowledge and belong in `library/`, but it should not automatically receive a workbench.

### Scope ladder

Before workbench admission, write a three-level ladder:

> **local observation / substrate**  
> → **broader scientific object**  
> → **top-conference-scale consequence**

If the arrow from local observation to broader object is speculative or purely rhetorical, keep searching.

The target is not “big topic” but **big consequence**.

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

## Paper rewind exercise

For especially strong papers, train the search process explicitly:

1. Read the parent papers / baseline and the beginning of the target paper's Introduction.
2. **Hide the final method and headline result.**
3. Write what you think the real pressure is.
4. Propose 3–5 analyses / baseline checks you would run before inventing a method.
5. Predict several plausible outcomes, not one desired outcome.
6. Only then read the rest of the paper.
7. Compare:
   - which pressure did the authors actually resolve?
   - what did they notice that you missed?
   - which of your analyses would have produced useful gradient?
   - did the final method follow naturally from a measured bottleneck, or from a conceptual derivation?
   - what part of the path is transferable to another territory?

The exercise is successful even when your hypothetical path differs from the paper. The goal is to improve **research navigation**, not to reverse-engineer the authors' private thoughts.

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
