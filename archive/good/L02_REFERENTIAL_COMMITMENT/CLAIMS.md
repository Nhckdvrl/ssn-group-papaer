# L02 claim ledger

Updated 2026-09-08. Current route: NO-GO for NAACL Main; see `RESEARCH_VERDICT.md`. Hypotheses,
published facts, extraction results, and model findings are different evidence types.

| ID | Claim and scope | Evidence / planned test | Current status | What would undermine it |
|---|---|---|---|---|
| D01 | SemEval distinguishes interpretation from discourse recoverability. | S10-1008 §§2–4, Table 1; E000 raw XML audit. | Published; corpus reproduction pending. | Released annotation cannot support the distinction per item. |
| D02 | Some linked omissions have non-NP fillers or multiple equivalent mentions. | S10-1008 §4; E000 graph and coreference audit. | Published; occurrence counts pending. | Parser cannot faithfully represent the links. |
| D03 | Our acquired release supports a development pilot. | E000 source identity, counts, exclusions, context and rendering review. | Pending. | Only a sample or unreconciled version is available. |
| H01 | Output organization changes the trade-off between recovering licensed fillers and committing to unlicensed specific referents, beyond generic answer suppression. | E001 then E002: paired answer-first/status-first, identical schema, evidence and token ceiling; separate two-call and generic verification controls. | Hypothesis; no model evidence. | Gains vanish against matched controls, or all reductions in commitment are explained by losing licensed recovery. |
| H02 | Discourse evidence improves recovery without equally improving referential licensing; explicit licensing may condition the benefit of additional context. | E002: native full context vs fixed local windows, complete-link support indicators; frame/role prior baseline and natural within-stratum analysis. | Hypothesis. | Adequate evidence improves both uniformly; effect is solely truncation, lexical priors, or one frame. |
| H03 | Selecting systems using positive filler recovery alone can select a different operating point than jointly measuring recovery and independently judged unsupported specificity. | E003: same frozen predictions; compare explicitly named selection rules on held-out material. | Hypothesis; requires new support gold. | Conclusions remain equivalent within justified margins; only the score scale differs. |
| A01 | Explicit status staging adds no practically meaningful benefit in specified conditions. | Equivalence/non-inferiority design after independent variance and power analysis. | Alternative hypothesis. | Intervals exclude the preregistered margin. Non-significance alone is insufficient. |

Forbidden conclusions: discovering DNI/INI; first abstention in EAE; first grounded
generation metric; all implicit arguments are people/entities; absent link implies
INI; one prompt win proves representation necessary; a role supplied in the prompt
counts as independent role knowledge; training-set pilot estimates generalize to
other genres or model families.

Each future claim must link its literature comparison, immutable protocol, input
hashes, executed code, raw outputs, exact denominator, exclusions and uncertainty.
Claims are promoted only after evidence exists; software checks are not experiments
on language-model behavior.

## Evidence update after E000 (2026-09-08)

D01: central training NI counts reproduced in `runs/E000_20260908_v1/report.json`.
D02: source IDs and multi-node/cross-sentence spans retained; full coreference
alternatives still unvalidated. D03: raw training access and parser feasibility
established, but original model-gold readiness **not established**.

| ID | Executed finding | Scope / limitation |
|---|---|---|
| D04 | 11/277 INIs contain source fenode links; 58/303 DNIs have none. | XML annotation properties. Not all 11 links have been independently semantically validated. Missing links do not define negative gold. |
| D05 | Frame-role majority predicts 418/574 interpretation labels versus 300/574 for fold-global majority. | Five contiguous folds within one training story; excludes six uncertain interpretation labels. Does not establish discourse or genre generalization. |
| D06 | Two released XML variants agree on NI targets, links and flags; graph audit has no missing node/cycle issues. | Syntactic integrity is not semantic correctness. Published overt-FE count remains unresolved. |

H01/H02/H03 remain untested. H01's original blanket INI error definition is withdrawn;
E001 must obtain independent negative-support gold or state a narrower estimand.
The task is active and not killed. Software tests do not promote scientific claims.

## Evidence update after E000b and follow-up literature review

| ID | Executed finding | Scope / limitation |
|---|---|---|
| D07 | Revised UCCA six-type counts reproduce IWPT 2021 Table 2: 391 participants / 393 segments / 116 review IDs. | Native inventory; 28 additional unrefined/other implicit nodes preserved separately. |
| D08 | 82 UCCA parent scenes have differently typed implicit participants with broad Participant edges. | These edges do not independently provide role names or candidate-support gold for L02. |

DUST already tests recognizing versus interpreting underspecification, including
implicit-reference examples. RefNLI already studies downstream errors caused by
reference-determinacy assumptions. See `literature/FOLLOWUP_ALIGNMENT_20260908.md`.
H01–H03 require more than modern-model reproduction of either existing narrative.
E001a is explicitly a native-label diagnostic and cannot promote those hypotheses.

## Final evidence and route decision

| ID | Finding | Exact scope |
|---|---|---|
| D09 | 1,198 coreference edges form 142 classes over 1,328 mention spans; 14 linked NIs have a global equivalent in the target sentence despite a nonlocal original span. | E000c. Global equivalence does not establish local support. |
| R01 | E001a Mistral argmax is A on all 168 jobs; order averaging gives 23/42 sentence, 22/42 full accuracy. | Format-sensitive elicitation; not a robust capability or grounding claim. |
| R02 | E001a Qwen scores 20/42 sentence, 22/42 full with 16/42 and 9/42 order disagreements. | Same 42-item development challenge. |
| R03 | E001b gives Qwen 20/42 → 20/42, Mistral 24/42 → 20/42; both predict DNI on 41/42 full-context items, with zero invalid outputs. | Exploratory format check, not filler support. Aggregate context harm is not replicated across both models. |

H01/H02/H03/A01 remain untested. The current route is not promoted: the original
support mapping fails and native-label findings do not establish the distinctive
extraction/selection narrative needed beyond prior work. This is a design
decision, not a statistical rejection of those hypotheses.
