# E001 — development pilot design, NOT FROZEN / NOT RUN

## Question and comparison papers

Can explicit interpretation decisions improve the trade-off between context-supported argument recovery and unsupported specificity beyond generic caution, formatting, and extra computation? Compare to Roit et al. ACL 2024's evidence checking, DiscourseEE EMNLP 2024's generation with null slots, and REGen Findings EMNLP 2025's context-grounded evaluation; see `literature/ALIGNMENT_20260908.md`.

The original INI-as-unlicensed-filler estimand failed E000's gold-contract audit. This draft does not authorize relabeling the source. No model outputs informed it.

## Available and missing gold

Released interpretation flags and positive source links are distinct fields. Preserve six uncertain interpretation items and the uncertain antecedent flags for review. A source-link miss is not automatically an incorrect answer: coreference alternatives must be audited. INI and absent fenodes do not supply independent negative-support labels. A role supplied in the prompt cannot establish independent role knowledge.

Before primary model experiments:

1. Align source-native interpretation with recoverability using the released guide §§3.2/3.5 and classical literature. Separate presupposed identifiability, recoverable discourse information and absent annotation.
2. Review every linked INI and uncertain NI. Codex source-review notes are not independent human gold adjudication.
3. Secure an independently annotated natural negative set for a particular candidate filler, or a verified existing resource with explicit non-relation labels. Roit et al.'s resource is a lead, not an admitted substitute; it must preserve the scientific question without invented DNI/INI labels.
4. Audit complete coreference equivalents, multiple-node expressions and full-context rendering. Freeze exact sample IDs before outputs.
5. If negative gold is unavailable, a positive-link/interpretation feasibility pilot may run after its own protocol review, but cannot establish H01 or a hallucination rate. Merely removing 11 linked INIs does not validate the remaining 266 as negatives.

## Controlled comparison once ready

Give identical passages, targets, role definitions, abstention options and final output fields. Compare one-call answer-first versus interpretation-first; compare explicit two-stage decisions against generic two-stage evidence verification. Match token ceilings and record actual tokens/calls/time. Allow context-supported INI fillers; do not hard-gate all INIs to null.

Full natural context is primary. Shortened windows are separately labeled evidence conditions and cannot change an INI/DNI label. Keep development on the original training story and later evaluation on untouched independently verified material. Include frame-role and no-discourse diagnostics. Do not tune prompts on test chapters.

Cached Qwen3-32B is an initial serious open-model candidate; before broad conclusions use another model family in the 24B–70B range. These are inventory choices, not performance claims. Recheck local runtime and GPU occupancy immediately before execution; leave other GPU jobs alone. E000's local .venv is standard-library-only; no model has been loaded for this audit.

Freeze support definition, positive/negative gold, equivalence classes, denominators, malformed-output handling, paired contrasts and practical effect thresholds before model execution. Exploratory pilot results cannot stand in for a powered confirmatory comparison. One author's stories cannot justify genre-wide uncertainty intervals.

Candidate narrative: a system may learn to recover more content without learning when specificity is warranted. This is a hypothesis. It must lead to a new relation or decision consequence beyond DNI/INI classification, not just a prompt win or a restatement of a classical distinction.
