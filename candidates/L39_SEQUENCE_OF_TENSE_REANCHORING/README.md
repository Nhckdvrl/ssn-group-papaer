# L39 — Past Is Not Always Before

**Internal name:** Sequence of Tense / Contextual Temporal Re-Anchoring  
**Status:** `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`  
**Date registered:** 2026-09-14  
**Target:** ACL / EMNLP / NAACL Main  
**Style anchors:** *The Imperfective Paradox in Large Language Models*; *The Flexibility Trap: Rethinking the Value of Arbitrary Order in Diffusion Language Models*

---

## 1. Locked scientific question

> **Can language models re-anchor temporal meaning compositionally when surface tense morphology conflicts with the correct discourse/reference-time interpretation?**

The decisive linguistic instrument is English **Sequence of Tense (SOT)** in past-under-past attitude/speech reports.

Canonical example:

> John said that Mary was sick.

English permits a reading on which Mary's sickness overlaps John's saying time. Therefore the embedded past **does not force semantic anteriority relative to the matrix attitude time**.

Short form:

> **Does an LLM treat embedded past as a context-relative temporal relation, or fall back to the surface heuristic `PAST => BEFORE`?**

This is **not** a project whose contribution is `LLMs know/do not know SOT`. SOT is the identifying instrument for a broader question about whether temporal reasoning uses context-relative compositional representations or surface/default cue priors.

---

## 2. Why this is scientifically interesting

The project is motivated by a form–meaning dissociation:

- ordinary past morphology strongly cues temporal anteriority;
- in English past-under-past attitude complements, that cue is not a valid entailment;
- the embedded past can support a simultaneous interpretation with the matrix attitude time.

A model can therefore succeed on ordinary tense recognition and temporal ordering while still failing the compositional computation that matters here.

This makes SOT analogous in research shape, but not scientific object, to the imperfective paradox:

- recognizing an aspectual/temporal category is weaker than using its semantic consequences correctly;
- a small, classic linguistic distinction can expose a broader reasoning policy;
- the useful result is a dissociation, not merely a low benchmark score.

The strongest potential conclusion is:

> **A model can possess explicit tense/SOT knowledge and ordinary temporal competence while failing to deploy the correct reference frame when surface morphology conflicts with compositional interpretation.**

If supported, the paper is about **knowledge deployment and temporal reference-frame computation**, not about collecting another linguistic benchmark.

---

## 3. Traditional empirical substrate — do not build a dataset first

The E01 core must start from published human experimental materials.

### Primary source

Anne Mucha, Agata Renans & Jacopo Romoli. *Sequence of tense and cessation implicatures: evidence from Polish.* Natural Language & Linguistic Theory 41, 267–346 (2023). DOI: 10.1007/s11049-022-09545-2.

Why it is unusually useful:

- Experiment 1 directly tests the availability of simultaneous readings for past-under-past attitude complements;
- it includes **33 native British English participants** in the English arm;
- it uses **24 target lexicalizations + 36 fillers**, with a Latin-square design;
- the four target conditions cross source-context tense (shifted vs simultaneous) with indirect-report tense (past vs present);
- the full target materials are printed in **Appendix A**;
- the article is published under **CC BY 4.0**, permitting reuse/adaptation with attribution and indication of changes;
- the paper reports that simultaneous past-under-past readings are available in English and more available than in Polish.

The critical traditional form is:

- source/direct speech establishes a simultaneous state using present tense;
- the indirect report uses embedded past;
- humans judge whether the indirect report accurately preserves the source report.

This gives us independently established human materials and an empirical interpretation target. We should not replace this with free-form LLM-generated examples.

### Possible later external substrate

Elena Marx & Eva Wittenberg. *Event structure predicts temporal interpretation of English and German past-under-past relative clauses* (CogSci 2022), with critical linguistic/visual materials and preregistration linked through OSF (`osf.io/6ae5m`).

This is **not E01** because it studies a different syntactic environment. It may become an external-environment test only if the broader contextual re-anchoring claim survives the core SOT pilot.

---

## 4. Critical identification warning

**Past-under-past is ambiguous / multiply licensed. Never create a dataset that assigns `John said Mary was sick` the single gold label SIMULTANEOUS.**

The core empirical facts we are entitled to test are:

1. a simultaneous reading is **licensed / compatible** in English SOT contexts;
2. simple embedded past **does not entail** that the embedded state is anterior to the matrix attitude time;
3. a context that establishes simultaneity can be faithfully reported with past-under-past.

Therefore valid observables are:

- report accuracy / meaning preservation in a context that forces simultaneity;
- compatibility with an explicitly simultaneous world;
- non-entailment of anteriority;
- paired behavior under contexts that change the intended temporal relation while the report string is held fixed.

Invalid main observables include:

- `What time did it happen?` with one author-assigned answer;
- treating the bare SOT sentence as unambiguously simultaneous;
- scoring a model wrong merely for choosing a backward-shifted reading when the context leaves both open.

This distinction is load-bearing. If it cannot be preserved in the implementation, stop the pilot.

---

## 5. E01 — Human-validated SOT core

**Authorization:** E01 only. No E02/E03 execution is authorized by this registration.

### E01-A — Reproduce the traditional report-accuracy task

Recover the 24 English target lexicalizations and their four conditions from Mucha et al. Experiment 1 / Appendix A.

Preserve:

- original item ID;
- original condition;
- direct-speech/source context;
- indirect report;
- matrix verb;
- embedded stative predicate;
- source citation and license provenance.

Ask the model to judge the accuracy / possible faithfulness of the indirect report to the source context. Prefer a fixed scale or forced response that can be mapped transparently to the human task; do not optimize prompt wording after seeing the critical effect.

The most diagnostic condition is **simultaneous source + embedded past report**.

E01-A establishes whether the human-licensed SOT reading transfers to the model task at all.

### E01-B — Consequence-sensitive inference

Using the same lexical material, construct a minimal inference view that asks the scientific quantity more directly.

Examples of valid questions:

- Is the indirect past report compatible with the embedded state holding at the matrix saying/thinking time?
- Does the indirect past report require the embedded state to be earlier than the matrix attitude time?

The gold must test **compatibility / non-entailment**, not select one reading for an ambiguous sentence.

For a subset, make the world explicitly simultaneous while holding the indirect past report fixed. A clean version may state or imply that the stative condition holds at the matrix speech time and ask whether the report is compatible with that world.

### E01-C — Controls

At minimum include:

1. **ordinary temporal comprehension control** — the model must handle explicit before/after relations;
2. **explicit anteriority control** — e.g. past perfect or an overt earlier-time adverb, where anteriority really is required;
3. **source/report-content control** — obvious faithful and unfaithful report pairs, ideally retaining the published fillers where useful;
4. **label/polarity balancing** — the target answer must not be recoverable from answer position or global yes/no frequency.

A failure is not SOT-specific if the model cannot pass these controls.

### E01-D — Declarative knowledge control

Separately ask whether English past-under-past under a past attitude/speech verb can receive a simultaneous reading, and optionally ask for a brief explanation.

This is **not** the main task.

Its value is to test a possible knowledge–deployment dissociation:

> the model can state the rule correctly but fails to use it when judging concrete reports/inferences.

---

## 6. E01 models and run discipline

Use only **2–3 strong model families that are already accessible**. Record exact model/checkpoint/API names, dates and decoding settings.

Main run should be deterministic or low-temperature. Do not create a model zoo.

Freeze before the first critical full run:

- item extraction and inclusion rules;
- prompt templates;
- answer parser;
- the primary contrasts;
- control definitions;
- any threshold used for the go/no-go decision.

A tiny implementation smoke test is allowed, but do not inspect enough critical outputs to redesign the task around the desired result.

---

## 7. Primary quantities

Report at least:

- accuracy/acceptance on the traditional **simultaneous-context + embedded-past** condition;
- matched shifted-context performance;
- false-anteriority rate on the consequence-sensitive task;
- simultaneous-compatibility rate;
- explicit-anteriority control accuracy;
- ordinary temporal-control accuracy;
- if E01-D is run, a **knowledge–deployment gap** between metalinguistic rule knowledge and contextual inference/use.

Prefer paired item analyses because the strongest design holds lexical content and/or the indirect report fixed while changing the reference-time context.

Do not make aggregate `SOT accuracy` the only observable.

---

## 8. Frozen E01 decision rule

### Kill / close L39

Close the candidate without rescue if any of the following is true:

- strong current models robustly license the simultaneous reading and avoid false anteriority on the consequence-sensitive task;
- apparent failure disappears under a trivial, non-leading reformulation of the same task;
- failures are explained by generic report-reading, temporal, label, or instruction errors exposed by controls;
- only a weak/outdated model fails while stronger families do not;
- the human materials cannot be transferred without making author-created temporal labels load-bearing;
- a direct 2025–2026 owner is found that already asks the same parent question: whether LLMs deploy SOT/context-relative embedded tense in downstream inference.

**Do not rescue a failed E01** by multilingual expansion, changing to relative clauses, adding chain-of-thought, model-shopping, fine-tuning, activation patching, or inventing a new tense construction.

### Promote to a development decision

E01 is worth developing only if **at least two strong model families** show a stable, item-level specific failure on simultaneous SOT / false anteriority while the explicit-anteriority and ordinary temporal controls are strong.

The strongest version is:

> the same models can explicitly state the SOT rule but systematically fail to deploy it in contextual report/inference judgments.

No fixed effect-size number is treated as scientifically magical. The result must be large enough that the paper headline is about a robust computation, not a statistically detectable benchmark delta.

---

## 9. Development path — only after E01 survives

### E02 — Controlled lexical robustness

Goal: establish that the E01 result is not an artifact of the 24 published lexicalizations.

Use small, theory-controlled expansion only:

- curated English stative predicates;
- programmatic substitution of names/times/predicates;
- approximately 50–100 additional items is enough if power/robustness requires it;
- manually audit every generated template family;
- no free-form LLM paraphrase corpus.

Diversity should be **scientifically meaningful**, not benchmark-style surface diversity.

### E03 — Rule reminder and conditional deployment

Give a concise explicit reminder that English past-under-past can have a simultaneous interpretation, then rerun locked critical/control items.

Three outcomes are scientifically distinguishable:

1. **selective recovery:** simultaneous SOT improves while true-anteriority controls stay intact — suggests a default inference-policy/cue prior that explicit rule access can override;
2. **no recovery:** the model can receive the rule but still fails to deploy it — stronger surface/default-prior failure;
3. **nonselective overcorrection:** simultaneous cases improve but genuinely anterior cases are now misread as simultaneous — strongest evidence that instruction swaps one heuristic for another instead of inducing conditional semantic reasoning.

E03 should only be run after E01 establishes the mother phenomenon.

### E04 — External environment / boundary, only if needed

Only after the broader claim is supported, test whether contextual temporal anchoring generalizes to an independently published past-under-past paradigm (e.g. relative-clause materials from Marx & Wittenberg), or test a linguistically pre-specified boundary.

This is not permission to add multilingual breadth, a model zoo, or arbitrary tense constructions.

---

## 10. Potential Main-level paper shape

A successful paper should not be narrated as `we introduce an SOT benchmark`.

Desired claim stack:

### C1 — competence/control

Strong LLMs recognize ordinary tense and solve explicit temporal relations.

### C2 — critical dissociation

When simple past morphology conflicts with the correct context-relative interpretation, models systematically over-infer anteriority or fail to license the human-established simultaneous report.

### C3 — knowledge deployment

If E01-D/E03 support it, models may explicitly know the SOT rule yet fail to apply it conditionally; a rule reminder may either selectively fix the computation or trigger heuristic overcorrection.

Potential scientific conclusion:

> **LLM temporal reasoning can be dominated by surface/default temporal cues rather than robust context-relative re-anchoring, producing a gap between declarative linguistic knowledge and consequence-sensitive semantic inference.**

That is the paper. SOT is the decisive instrument.

---

## 11. Strongest reviewer compression and defense

### Compression

> This is another `does the LLM know a linguistic phenomenon?` paper using a small set of formal-semantics examples.

### Required defense

The project survives only if the actual result supports:

> **The model succeeds on tense knowledge and ordinary temporal reasoning but fails specifically when semantic interpretation requires changing the reference frame despite misleading surface morphology.**

The traditional SOT materials are not the contribution. They provide a human-established diagnostic that lets us identify a broader knowledge-deployment / cue-prior failure.

If E01 cannot establish this specificity, the reviewer compression wins and L39 should be killed.

---

## 12. Novelty state as of registration

Exact searches on 2026-09-14 included variants of:

- `"sequence of tense" "large language models"`
- `"sequence of tense" LLM temporal reasoning`
- `"past-under-past" LLM`
- `"embedded tense" "large language model"`
- `"double access" LLM tense`
- `"sequence-of-tense" transformer language model`

No direct modern LLM owner was found in this bounded search.

Nearby work exists on:

- generic temporal ordering/reasoning;
- tense representation/probing;
- the traditional formal semantics of SOT and double access;
- human/cross-linguistic SOT experiments.

This is **provisional novelty**, not a guarantee. The local agent must perform one bounded exact-owner sanity check before executing E01 and stop if a direct parent collision appears.

---

## 13. Explicit prohibitions

Before E01 survives, do **not**:

- build a benchmark;
- generate hundreds/thousands of synthetic examples;
- fine-tune a model;
- run activation patching / SAEs / representation atlases;
- add multilingual experiments for breadth;
- tune prompts until the effect appears;
- change the parent claim after seeing results;
- turn a null E01 into `maybe another model/construction fails`.

The authorized work is deliberately small:

> **published human materials -> exact SOT inference task -> strong-model controls -> binary go/no-go.**

---

## 14. Current authorization

**L39 is `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`.**

The local agent may:

- verify/recover the Mucha et al. English materials and license;
- build a provenance-preserving machine-readable E01 set;
- preregister/freeze task prompts, scoring and controls;
- run E01 on 2–3 accessible strong model families;
- write an E01 report and a promote/kill recommendation.

The local agent may **not** automatically continue to E02/E03/E04.

The next decision is:

> **Do strong models that otherwise understand tense and temporal order specifically fail to license/use English SOT when surface past morphology conflicts with context-relative temporal interpretation?**

If no: close L39.  
If yes: return to Selection before expanding the project.
