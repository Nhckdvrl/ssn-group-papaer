# Research Execution: Developing a Contribution, Not an Experiment Collection

Updated: 2026-09-11. Target: ACL / EMNLP / NAACL Main.

This governs selected projects. [Selection](RESEARCH_TOPIC_SELECTION.md) evaluates the question, idea, and contribution separately. Execution learns which answer is true and whether the evolving contribution merits a full paper. Neither document can guarantee acceptance.

## 1. Scope and Sources of Truth

Fetch the current remote main and inspect divergence and dirty files before work. Integrate without discarding concurrent changes. Ordinary execution edits only the concrete candidate directory. Root workflow maintenance requires an explicit workflow task, as authorized for this revision.

A candidate's latest README, claims, novelty audit, and experiment ledger are authoritative for its status. Root indexes are dated navigation, not independent authorization to rerun old experiments. Resolve contradictions before compute; do not follow an obsolete handoff command.

Keep only useful files. Every load-bearing result must be traceable:

**claim -> experiment -> config/code -> data -> raw result -> summary -> conclusion**

Root rules are durable procedures, not a place to prescribe one candidate's next experiment.

## 2. Keep Four Judgments Separate

| Judgment | Question |
|---|---|
| RQ value | Is this a natural, important question? |
| Contribution | Is our current answer/operation independently worth knowing after prior work? |
| Evidence | Do these data and operations support that answer rather than a weaker alternative? |
| Maturity | Is the depth, breadth, and consequence sufficient for the intended paper scope? |

A project can pass one and fail another. Large effects do not establish novelty. Complete logs do not establish construct validity. A novel title does not establish a new inference. A rigorous local result does not establish Main-level maturity.

State current RQ, proposed takeaway, supported vs hypothetical claims, and the largest unresolved contribution/evidence gap. Use as many headline claims as the argument needs, not a mandatory C1/C2/C3 count.

## 3. Stage Gates: Small Discovery, Adequate Full Study

| Stage | Work | Exit condition |
|---|---|---|
| Discovery | Parent/data audit and bounded high-information experiments | A credible phenomenon or operation, with its meaning understood |
| Contribution gate | Current novelty and successful-result test | An important unresolved statement the proposed evidence can establish |
| Explanation/development | Distinguish live accounts; test predictions or consequential implications | The paper advances beyond its first observation |
| Breadth/consequence | Independent units and meaningful external axes; test scope and consequence | The proposed scope has support rather than a collection of nearby examples |
| Manuscript review | Assemble argument, results, related work, and explicit gap-to-comparators review | No missing load-bearing work; defensible contribution and appropriately scoped conclusions |
| Archive | Preserve assets and explain the failed route | No active experiment queue without a new reason |

Stages can loop. A newly discovered phenomenon can justify reconstruction. Do not force all projects through probes, patching, or a method-improvement section.

**The smallest decisive pilot is the beginning of a study, not its completion criterion.** Once a contribution deserves investment, carry out the necessary full-study program. "Avoid model zoo" must not become an excuse to omit external validation that the claim requires.

Use scoped decisions: GO-to-discovery, GO-to-full-study, HOLD, RECONSTRUCT, ARCHIVED/NO-GO, or READY-for-manuscript-review. An unqualified "GO" must not be read as "already Main-level."

## 4. Claim Mutation = Mandatory Novelty Reset

Reset approval when the RQ, major explanation, central claim, paper identity, or reviewer takeaway materially changes. This includes supporting findings becoming headlines, null results producing reinterpretations, and new literature changing ownership. Cosmetic wording edits are not mutations.

Reset the **novelty judgment**, not the existence of usable evidence or code.

Write a Claim Novelty Delta in the existing claim/related-work record:

1. Old claim and paper identity.
2. New claim and paper identity.
3. Why it changed, including which observations motivated it.
4. The new scientific statement, not just a new name.
5. Closest primary sources, versions, and what each actually establishes.
6. Strongest reviewer compression AND strongest surviving contribution.
7. Successful-result test and Main-level depth/width burden.
8. PASS / HOLD / RECONSTRUCT / NO-GO, with explicitly authorized next work.

Before this passes, pause broad confirmation, model expansion, and layer scans. A bounded diagnostic needed to understand the candidate claim is allowed, with a stopping point. Do not accumulate weeks of evidence for a claim whose contribution remains undefined.

## 5. Novelty Review Must Be Two-Sided

Try the strongest honest compression:

> Prior Work A + B + C = our paper.

Then test it. Does the cited work actually establish our proposed relationship, explanation, or consequence? Or does it merely supply familiar ingredients?

- Shared components do not automatically kill a paper.
- Connecting components does not automatically make a paper.
- A meaningful new relation, explanation, operation, or consequence can be the contribution.
- No exact duplicate does not imply Main-level significance.
- Calling a narrow result a general principle does not enlarge the evidence.
- Precise claims are desirable; an identity consisting only of incidental dataset/model/layer restrictions is not.

Distinguish direct collision, insufficient contribution, and unresolved novelty. Do not claim a proven whole-paper collision when only component overlap was verified. Do not require every supporting claim to be unprecedented.

The width test is not "remove every concrete noun." Ask whether readers would learn something consequential beyond the experimental cell, and whether that scope can be supported. Some excellent papers study a specific domain deeply.

## 6. Main Calibration Must Change the Next Decision

At each new load-bearing claim or major expansion, revisit relevant strong ACL/EMNLP/NAACL work. Normally maintain three complementary anchors, chosen for problem, inferential operation, and development; refresh them when the identity changes. Technical top-ML neighbors also matter for ownership.

In existing project documents record:

| Dimension | Required comparison |
|---|---|
| Contribution | Their actual intellectual advance; ours; what remains derivative |
| Inference | Their decisive discrimination; ours; which alternative still survives |
| Depth | How they progressed beyond the first result; what deeper question we still owe |
| Breadth | Independent scientific units and genuinely distinct axes, not sample/model counts alone |
| Consequence | Prediction, explanation, intervention, resource utility, or changed practice; not a cosmetic extra benchmark |
| Decision | The largest gap and the next work that closes it, or why to stop |

Read methods/results and relevant appendices for quantitative workload comparisons. An abstract supports orientation, not a claim of full evidence parity. Record source sections/tables when asserting exact breadth or controls.

A paper with hypothesis, probe, patch, and intervention is not necessarily comparable to another with those headings. Compare what each step establishes.

Do not declare the project "Main-ready" because two experiments look clean. Conversely, do not force extra claims to match a paper's section count. Completion requires an argument-level review, not a number-of-runs threshold.

## 7. Design for an Inference, Not Merely an Effect

Before each substantive experiment, record its ID, linked claim, alternatives, data/model revisions, independent unit, primary outcome, sampling/seeds, exclusion rules, controls, and interpretation/stop conditions.

First ask:

> If the strongest expected effect occurs, what will still be unexplained?

Choose operations that resolve that gap. Common pitfalls include:

- probe accuracy substituted for causal use;
- whole-state answer transfer substituted for identification of the computation;
- same-answer no-change substituted for active causal interchangeability;
- behavior change and internal change placed side by side without testing their relationship;
- a model-family contrast called a training intervention;
- an obvious consequence promoted into an independent headline claim.

These are warnings, not a requirement for dozens of defensive controls. Test the strongest plausible alternatives. A control needed to protect the central inference is necessary work, even if it does not create a new headline.

After running, record command/config, environment, raw pointers, summary, uncertainty, failed/invalid cases, interpretation, and claim changes. Execution audit PASS means the specified run was executed, not that the scientific interpretation is correct.

## 8. Data Must Match the Proposed Distinction

Document provenance/version, independent units, gold, transformations, filtering, splits, leakage, missingness, and reproduction. Prefer existing natural data when it fits; use minimal controlled construction when it better identifies the question. Do not manufacture complicated worlds to produce the desired sign.

List everything a manipulation changes. In particular:

- One generating distribution and a finite sample from it are not identical evidence.
- A sequence and its frequency summary preserve a payoff multiset, but not necessarily order information. State the decision assumptions under which order is irrelevant.
- Fresh histories from previously analyzed problems are new observations, not a new problem-level holdout.
- Displayed option identity, underlying action identity, and gold direction must stay aligned.
- Invalid outputs may differ by regime; report coverage and the effect of handling them.
- Repeated generations improve Monte Carlo precision, not the number of independent scientific units.

Use paired estimates and uncertainty at the relevant unit. Separate exploratory findings from subsequent confirmation. A post-hoc explanation can motivate a better experiment without becoming a confirmed result by narration.

Keep construct validity, estimator validity, implementation validity, and scope validity distinct. Do not repair an interpretive mismatch by silently changing the metric after observing results.

## 9. Explore Flexibly Without Protecting a Story

When a hypothesis loses, investigate implementation, power/measurement, a competing account, or a meaningful boundary as appropriate. Do not conclude failure from one null; do not assume every null is an implementation bug.

Allocate bounded exploratory work to promising unexpected structure. It can change the question, operation, or narrative. Record the sequence of discovery and selection; novelty reset applies to the new idea.

Prefer a deeper discriminating question over many variants of a control that has already answered its purpose. But broaden substantially when the claim's scope requires it. Evidence economy means choosing valuable work, not doing the least work.

If the best remaining result is trivial, crowded, or uninterpretable, stop. A productive failure need not be salvaged into a paper.

## 10. Full-Study Completion and Stop Rules

Before manuscript readiness, answer:

1. Is the central contribution independently valuable after the strongest literature comparison?
2. Does the evidence distinguish the central explanation from its strongest live alternative?
3. Do the headline claims form an advancing argument rather than unrelated observations?
4. Do independent units and external axes support the claimed scope?
5. Is there a meaningful deeper explanation or consequence beyond the initial effect?
6. Have the largest gaps to comparable Main papers been closed or honestly shown unnecessary?
7. Are negative, invalid, and heterogeneous results integrated without selective reporting?

No universal number of claims, models, domains, or experiments substitutes for these answers. A mechanism claim need not establish every detail, but it must establish the mechanism it actually sells.

HOLD must name the blocker and the next bounded decision. After that review, expand only with a credible contribution path. Otherwise reconstruct with a substantive new reason or archive. Do not rotate through increasingly abstract titles indefinitely.

Archive the route, not the data. Record what remains usable, what failed, and what genuinely new evidence/idea would justify reopening. Synchronize project status and portfolio pointers; remove obsolete next-run instructions. An archive judgment is not a theorem that the RQ can never yield a paper.

## 11. Reproduction and Resource Hygiene

Maintain code/config/data/raw-summary provenance; do not manually alter results. Reuse compatible local environments and model caches. Record model/template/decoding differences relevant to interpretation.

Commit scoped code and compact documents/results frequently. Keep large raw outputs/checkpoints outside git with manifests, hashes, and retrieval/reproduction notes. Inspect the **entire outgoing commit history**, not only staged files, before pushing main. Do not publish unrelated local work.

Clean up only experiment processes started for the task and confirmed no longer needed. Do not kill other users' jobs or claim cleanup/revalidation that was not performed. A documentation revision does not imply experiments were rerun.

## 12. L12 Retrospective: What the Workflow Missed

This is a retrospective of our research decisions, not certainty about conference reviewers, a fresh numerical audit, or a new archive decision for the candidate. Consult [L12's current package](good/L12_REASONING_DECISION_INVARIANCE/README.md) for evidence and status.

| Turning point | What was too readily treated as enough | Missing question / earlier decision |
|---|---|---|
| Initial reasoning-invariance RQ | Natural phenomenon plus an open "why" meant a viable paper idea | Which answer would be independently valuable, and what operation could distinguish it? |
| E07/E08 trajectory and state effects | Strong causal perturbation meant a new explanatory mechanism | What is learned beyond trace causality or transfer of an already formed answer? Reset novelty before scaling. |
| E09 and later branch/control comparisons | Several linked positive results meant a mechanism-behavior explanation | Does a matched comparison connect route change to the phenomenon, or merely juxtapose them? |
| E17/E18 held-out behavior | A null required either narrowing the story or rescuing its sign | Was the purported presentation manipulation also changing observed evidence? Audit the construct first. |
| E20-E22 form/evidence direction | A better decomposition and new effects automatically supplied a wider identity | Which principle was already known, and what new explanation did our intervention establish? |
| Invariance-causality alignment proposal | A stronger abstraction upgraded the existing evidence | Could the proposed transfer result distinguish alignment from answer transfer or a no-op? |
| Late novelty rejection | Several component owners necessarily owned the entire synthesis | Separate a true collision from inadequate contribution and unresolved identification. |

### Why experiment volume did not settle the Main-level question

**Contribution:** the project repeatedly moved from a good question to a plausible description of results without establishing that the description supplied a new explanatory idea. The selection approval incorrectly persisted across those changes.

**Depth:** phenotype, representation, trajectory, and state results can each be useful without jointly identifying the causal computation explaining the phenotype. More locations or models do not repair a missing inferential connection.

**Breadth:** checkpoint breadth, model-family breadth, independent decision breadth, and domain breadth support different scopes. Neither three discovery prospects nor many resamplings suffice for a general principle. Conversely, breadth is valuable after the central inference is worth testing.

**Consequence:** renaming invariance as selective sensitivity or route control can clarify the question, but clarification is not automatically a new mechanism or a publishable generalization. The better formulation needs its own ownership and successful-result test.

**Management:** root instructions continued to prescribe old experiments. Positive local gates were too easily described as project-level success; later caution risked narrowing the paper to whatever survived. Both obscure the actual investment decision.

The lesson is not "be less accurate" or "make every claim smaller." It is to pursue a substantial answer with an operation capable of supporting it. If that operation is missing, design it or stop; do not substitute stronger prose or endless defensive ablations.

### Concrete comparison anchors, not a universal recipe

- [Racing Thoughts, NAACL 2025](https://aclanthology.org/2025.naacl-long.155/) proposes a specific token-dependency account of contextualization errors, then supplies correlational/causal support and inference-time interventions. The transferable lesson is a discriminating computational hypothesis, not the sequence of method names.
- [The LLM Language Network, NAACL 2025](https://aclanthology.org/2025.naacl-long.544/) links identified units to task-relevant causal function. Localization must advance an explanation; merely locating an effective patch is not equivalent.
- [What Makes a Good Reasoning Chain?, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.329/) makes reasoning-chain structure the object of study. Learn how a structural finding develops into explanatory/practical value, rather than borrowing an experiment count.
- [Stolfo et al., ACL 2023](https://aclanthology.org/2023.acl-long.32/) already separates robustness to irrelevant changes from sensitivity to relevant mathematical changes. A later form/evidence story must identify its additional contribution, not sell the distinction alone.

These illustrate the calibration questions, not a completed methods-level parity audit for L12. Future projects must choose their own current neighbors and examine the relevant full-text evidence.

**A selected topic is not grandfathered into novelty. Every materially new claim must re-earn the right to be the paper. Strong evidence and strong contribution are complementary requirements, not substitutes.**
