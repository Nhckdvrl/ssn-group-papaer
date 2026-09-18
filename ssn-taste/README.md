# ssn-taste

This directory is the working ledger for Sasano-taste-driven NLP/LLM research-question search.

Target venues: **ACL / EMNLP / NAACL Main**. TACL / ICLR / ICML / NeurIPS are secondary calibration. EACL / AACL / Findings / workshops / arXiv may be used aggressively for novelty collision, but not as the main positive taste signal.

Current selected topics: **4**.

## Current selection

- **S03 — From Document End to Task Done: How Does Post-Training Acquire Goal-Relative Stopping?** Selected / pilot-authorized on 2026-09-17. The parent question is where the information→stopping mapping is acquired when a pretrained document continuer becomes an assistant: pretrained/native stop mapping, stop-readout adaptation, internal-state adaptation, or their interaction.
- **S04 — How Do Language Models Update Situation Models Across Event Boundaries?** Selected / pilot-authorized on 2026-09-18. The parent question is how an LM transforms its active situation representation when one event becomes another: local editing, broader reconstruction, selective reactivation/rebinding, or another discovered update primitive.
- **S05 — When Does Reading Become Learning?** Selected / pilot-authorized on 2026-09-18. The parent question is the boundary between transient conditioning and persistent parameter learning under ordinary response-only SFT: which prompt-side information is merely used, which task-sufficient information is retained, and which details are durably written into parameters.
- **S06 — What Does Deliberation Do to Evidence?** Selected / pilot-authorized on 2026-09-18. The parent question is whether reasoning computes over a stable evidence state or endogenously changes the causal influence of fixed external evidence as deliberation unfolds.

See `SELECTED_TOPICS.md` for the frozen parent questions, novelty boundaries, and detailed registration files.

## Governing taste

The search is not trying to find the most fashionable technical gap. It is trying to find a scientific question that Sasano and a Main-conference reviewer would naturally consider worth asking.

The stable pattern from Sasano's feedback is:

> **easy-to-understand puzzle or scientific pressure -> clear scientific object -> real difference from nearest prior -> direct experiment -> claims no wider than evidence.**

Important anchors:

- **Sato:** strongest positive pattern — simple puzzle, natural competing explanations, controlled experiments that distinguish them.
- **Guo:** strongest negative reminder — 「先行研究との差が小さい。」 Old question + new model/language/dataset/condition is usually not enough.
- **Hamdi:** average reviewers need both “納得できる” and “面白い”; unexpected outcomes can still be findings; mechanism is not mandatory.
- **Utami:** a real technological/social change can create a new language question when one changed premise leads to one interpretable consequence.
- **Kisako / Tsukagoshi:** a systematic trade-off or interaction between mature operations around one natural quantity can be Main-sized without deep mechanism.
- **Oshika:** an independently necessary middle decision that a mature workflow still treats as human/gold/oracle can itself be a research object.
- **Youchi / Yano:** nearby prior does not automatically kill an idea if a load-bearing structural defect changes the inference/object/capability when fixed.

## Hard preference: no evaluation-centric topics

The user does **not** want benchmark/evaluation research as the primary contribution.

Do not select topics whose actual work reduces to:

- building a new benchmark, challenge set, or synthetic test suite;
- auditing a metric or comparing metrics;
- evaluating robustness under perturbation X;
- comparing method A/B/C across a new condition;
- constructing large synthetic data mainly to obtain ground truth;
- contamination detection or dataset-quality auditing;
- producing a leaderboard as the central result.

Evaluation can be an **instrument** inside a scientific experiment. It must not be the main scientific object.

The decisive sanity check is:

> **After deleting all benchmark names, metric names, and method names, what new fact does the paper learn about language, models, learning, training, representation, behavior, interaction, or a real-world process?**

If there is no clear answer, reject the topic.

### Why this rule was added

C2/S02 (“AI Rewrite ≠ Semantic Change”) looked strong at the framing level: a changed text-production regime and a clean distinction between meaning change and contextual redistribution. But the actual experiment collapsed into synthetic rewrite construction + semantic-preservation validation + LSC method/metric robustness comparison, while natural real-world data lacked clean ground truth. It was therefore cancelled. This is the canonical example of **scientific framing being stronger than the experimental object**.

## Exploratory does not mean evaluation

The search prefers **exploratory rather than gambling** questions: several natural outcomes should remain scientifically interpretable.

But this is only a necessary property, not a sufficient one. A benchmark paper can also have multiple interpretable outcomes. A real exploratory topic must study a scientific phenomenon or process itself.

Good targets include:

- what a model has learned when two theoretically different quantities are behaviorally confounded;
- where a capability/representation comes from;
- how a training operation changes learning dynamics, representation, or generalization;
- a natural trade-off between two mature operations around one resource/quantity;
- a hidden independent decision in an established workflow;
- a real language/behavior process changed by a new technological or social premise;
- an old scientific debate newly identifiable through a modern controlled intervention;
- a cross-lineage collision that creates a genuinely new quantity or prediction.

## Do not mine paper edges by default

The default generator must not be:

> recent Main paper finds phenomenon X -> it did not fully explain why/source/mechanism/boundary -> we study that missing piece.

Apply the **remove-the-trigger-paper test**:

> If the trigger paper disappeared, would this research question still arise naturally from theory, a real-world change, a workflow defect, a learning problem, a structural contradiction, or another independent source?

If not, it is probably a follow-up.

Successor work is allowed only when the predecessor has a **load-bearing assumption or structural defect** whose correction changes the scientific inference, object, or capability. “Cleaner experiment”, “more models”, “newer model”, and “one more boundary” are not enough.

## Reviewer-level novelty, not exact-gap novelty

For every serious seed, identify the parent literature a reviewer will use to compress the contribution.

Ask:

- What parent RQ does nearest prior already own?
- Would a reviewer describe our work as one more model/language/dataset/condition/cell inside that parent?
- Is our novelty sentence stated at the same abstraction level as nearby ACL/EMNLP/NAACL Main papers?
- Are we inflating a narrow experiment into a broader parent rhetorically?

Main scope is calibrated empirically by reading actual Introduction + Related Work sections, not by intuition.

## Mandatory experiment-grounding audit before promotion

Before a seed can become serious, answer plainly:

1. **Where is the data?** Existing natural data, cheap controlled examples, or a large synthetic/annotation project?
2. **What variable is actually manipulated or observed?** A scientific quantity/process, or merely a benchmark condition?
3. **What will the main result look like?** If it is primarily `method × dataset/perturbation × score`, be suspicious.
4. **What is learned if all benchmark/metric names are removed?** There must still be a substantive scientific conclusion.
5. **Who is the grammatical subject of the paper?** Prefer language/model/training/representation/behavior/process, not metric/benchmark/method.

Do this **before** registration, not after writing a beautiful story.

## Search workflow

1. **Recalibrate first.** Re-read real Sasano feedback/projects and several recent ordinary-strong ACL/EMNLP/NAACL Main papers. Learn how their questions arise, not only what topics they cover.
2. **Search for scientific pressure.** Natural puzzles, competing explanations, learning sources, representation distinctions, training effects, trade-offs, hidden decisions, real changed premises, old debates with new identifying operations.
3. **Lock one promising seed at a time.** Do not surface a large pile of half-ideas. Once one seed is promising, deep-audit it to a yes/no decision before switching.
4. **Read nearest papers, not abstracts only.** At minimum understand Introduction + Related Work and the actual experimental claim.
5. **Do reviewer compression early.** Kill exact-cell novelty inside an occupied parent.
6. **Do the experiment-grounding audit immediately after novelty.** This prevents another C2 failure.
7. **Only then design the minimum pilot.** Prefer natural/available data and a cheap experiment that directly distinguishes explanations or reveals structure. Do not begin by constructing a benchmark.
8. **Register only after all of the above.** Selected = 0 is fully acceptable.

## Drift audit

Every ~8–12 serious seeds, or whenever several seeds come from the same literature, stop and check:

- Are we again mining recent-paper mechanisms/future work?
- Are RL/agents/tool-use trends dominating because they are searchable rather than because they fit Sasano?
- Are we relying on exact gaps rather than parent novelty?
- Are evaluation, metric validity, robustness, benchmark construction, or synthetic data becoming the center again?
- Is the data path becoming artificial or expensive?
- Are Main papers being used only to kill ideas rather than positively teach question formation?
- Are Sasano examples becoming slogans instead of reasoning patterns?

If many seeds die for the same reason, change the **idea generator/scientific object**, not the novelty threshold.

## Current cancelled registrations

- **S01 / F06 — optional tool default / effective action semantics:** cancelled. Reviewer-level parent compresses to underspecified tool intent / argument completion; the default-value case is too narrow.
- **S02 / C2 — AI Rewrite ≠ Semantic Change:** cancelled. Actual execution is evaluation-centric and data/ground-truth awkward.

Do not revive them by adding more models, datasets, metrics, or rhetoric.

Files:

- `FAILED_TOPICS.md` and dated continuations — serious ideas that died; do not revive without evidence resolving the recorded failure.
- `RE_AUDIT_2026-09-18_NOVELTY_CALIBRATION.md` — overlay correcting overly strict old novelty reasoning.
- `SELECTED_TOPICS.md` — only genuinely selected questions. Current count: **4**.
- `S03_FROM_DOCUMENT_END_TO_TASK_DONE.md`, `S04_EVENT_BOUNDARY_SITUATION_MODEL_UPDATING.md`, `S05_WHEN_DOES_READING_BECOME_LEARNING.md`, `S06_DELIBERATION_EVIDENCE_REWEIGHTING.md` — detailed registrations.
- `NEXT_ROUND_PROMPT_ZH.md` — current operational search procedure; treat it as scaffolding rather than constitution.
