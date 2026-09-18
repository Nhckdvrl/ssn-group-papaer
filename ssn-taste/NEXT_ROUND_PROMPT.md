# Next-Round Research-Question Search Prompt

Last synchronized: **2026-09-18**

This is the English handoff for `Nhckdvrl/ssn-group-papaer/ssn-taste`. The Chinese prompt `NEXT_ROUND_PROMPT_ZH.md` contains the fullest current operational state. Always restore the repository before trusting any handoff text.

## 0. Restore canonical state first

Read:

- `ssn-taste/README.md`
- `ssn-taste/SELECTED_TOPICS.md`
- every `ssn-taste/FAILED_TOPICS*.md`
- `ssn-taste/RE_AUDIT_2026-09-18_NOVELTY_CALIBRATION.md`
- the three selected-topic registration files
- recent commits / handoff changes

Repository state overrides this document.

### Current selected topics = 3

- **S03 — From Document End to Task Done: How Does Post-Training Acquire Goal-Relative Stopping?**
- **S04 — How Do Language Models Update Situation Models Across Event Boundaries?**
- **S05 — When Does Reading Become Learning?**

These are current unrefuted research hypotheses / selected projects, **not positive taste exemplars**.

## 1. Current active search state

### SERIOUS / NOT PILOT-AUTHORIZED

**Long-input ↔ Long-output directional transfer.**  
Question: why does long-input competence not automatically produce long-output ability, while some long-output RL appears to improve long-input reasoning? The scientific object is whether reading and writing share long-range computation and why transfer is directional. Main blocker: direction is still confounded with teacher-forced vs on-policy training. Keep only if a small factorial design can separate them.

**Belief or Source? — Epistemic Credit Assignment.**  
Question: when evidence conflicts with a current belief, does the model revise the world hypothesis, the source-reliability hypothesis, or both? Minimal identification should separately fix source reliability, fix world state, and leave both uncertain. The target is a credit-assignment law, not a source-reliability benchmark. Nearest-prior deep audit is still required.

**What Does Deliberation Do to Evidence?**  
Question: with the evidence set fixed, does deliberation change each piece of evidence's causal influence on the final decision? Competing worlds: normative reliability-weighted integration, generic dilution with longer self-generated context, or coherence/confirmation amplification. Keep only if evidence influence can be measured causally under matched evidence, prior, and reliability.

### ACTIVE AUDIT — not yet SERIOUS

**Multi-turn degradation: Fragmentation vs Self-Commitment.**  
Immediately check whether the ICLR 2026 Outstanding multi-turn degradation paper and nearest prior already separate:
- fragmented evidence without assistant commitment,
- fragmented evidence with neutral assistant turns,
- self-generated intermediate commitment,
- externally supplied identical commitment.

If they already make the decisive separation, kill. If not, the mother question is whether multi-turn failure comes from fragmented evidence or from premature self-generated commitments that later alter interpretation.

### OPEN-CONFLICT pressures only

- which ingredient of rationale supervision is actually useful;
- uncertainty as error signal vs reasoning resource;
- premature commitment under irreducible ambiguity;
- planning quality vs realization quality.

Do not promote these merely by giving them titles.

## 2. Target venues and taste

Primary targets: **ACL / EMNLP / NAACL Main**.  
Use **ICLR / ICML / NeurIPS / TACL** to calibrate scientific taste.  
Use CVPR / ICCV / ECCV, multimodal, speech/audio, robotics, general ML, optimization, cognitive science, neuroscience, statistics, information theory, control, dynamical systems, and statistical physics for **idea provenance**.

Do not mechanically transfer terminology. Transfer scientific pressure, competing explanations, identification logic, directed asymmetry, regime change, and paper-growth patterns.

Positive taste comes from:
1. Sasano's actual judgments and supervision style;
2. real strong Main papers and their mother-question growth.

User-generated S/L/F/Unring/selected topics are process evidence only.

## 3. Correct novelty standard

Do **not** kill a question merely because the broad parent has prior work.

Ask instead:

> Has nearest prior already answered the **same decisive unknown** with evidence that distinguishes the same scientifically meaningful competing worlds?

Overlap is normal. Thin novelty is not.

Still kill when:
- the same decisive unknown is directly answered;
- the proposed distinction is not identifiable;
- the tension disappears in the ideal-model limit;
- novelty is mainly a new model, dataset, modality, terminology, benchmark, or cleaner replication;
- mechanism is only another head/vector/subspace/circuit with no changed system-level explanation;
- the honest story is too narrow for Main.

Main-sized width should come from **explanatory reach**, not experiment count.

## 4. Search for open/conflicting components, then upgrade them into experiments

The preferred generator is now:

> Find an unresolved, conflicting, or poorly identified component/relation/law first; then ask whether a small decisive experiment can distinguish plausible worlds.

High-value pressure patterns include:
- two quantities usually treated as the same, but evidence suggests they differ;
- directed transfer asymmetry;
- a changed premise that invalidates the old explanation;
- a global label that hides heterogeneous local information utility;
- a constraint that forces a qualitatively different learned computation;
- several credible papers whose findings cannot be explained by one simple account.

Do not start by brainstorming 30 titles.

## 5. Minimum candidate requirements

A SERIOUS candidate should have:
- a natural one-sentence mother question;
- independent scientific pressure;
- at least 2–3 qualitatively different possible worlds;
- nearest prior that does not already close the decisive unknown;
- a clean identification path;
- Main-sized explanatory reach;
- no benchmark/data-construction center;
- a realistic cheap pilot.

PILOT-AUTHORIZED additionally requires:
- a minimum experiment that directly separates major worlds;
- clear interpretation for A/B/C outcomes;
- nearest-prior audit based on actual claims/experiments, not titles;
- no unresolved identifiability blocker;
- no need for a large benchmark or annotation effort;
- a one- or two-sentence reviewer-level novelty statement;
- scientific value even if the result is opposite the initial hypothesis.

Zero survivors is acceptable.

## 6. Immediate next actions

1. Audit **Multi-turn Fragmentation vs Self-Commitment** against the ICLR 2026 Outstanding paper and nearest work.
2. Resolve the **direction vs teacher-forced/on-policy** confound in Long-input ↔ Long-output with the smallest possible factorial design; kill if this requires experiment explosion.
3. Deep-audit **Belief or Source** against Bayesian belief update / source reliability / epistemic trust work.
4. Deep-audit **Deliberation → Evidence Reweighting**, focusing on causal influence of fixed evidence rather than generic confirmation bias.
5. In parallel, perform substantial fresh exploration across generation, understanding, and reasoning, with provenance from at least three distinct lineages.
6. After roughly 6–8 serious seeds, or repeated identical kill patterns, reset the generator rather than lowering the bar.

## 7. Hard anti-drift rules

Avoid:
- mechanism-first search;
- recent-paper edge mining;
- exact-cell novelty;
- architecture micro-puzzles without a natural mother question;
- benchmark / metric / evaluator / RAG / data-centric work;
- model-zoo studies;
- RLVR / agent hype chasing;
- complex linguistics;
- “new model re-tests old phenomenon”;
- “behavior exists, therefore do a mechanism paper”;
- using strong papers only as a kill database rather than learning how their questions grew.

The final goal is not to manufacture S06. It is to find a question worth asking **before the answer is known**, such that any major outcome changes our understanding of language-model learning, understanding, generation, or reasoning.
