# Follow-up ownership and data alignment

This supersedes optimistic novelty judgments in the inherited proposal. PDFs and
text are stored alongside this file; `manifest_followup_20260908.json` and
`manifest_claire_20260908.json` pin retrieved bytes. Full text, not search snippets,
supports the comparisons below. No assertion of exhaustive novelty search is made.

| Work / inspected section | Already established | Remaining room for L02 |
|---|---|---|
| [DUST, Findings ACL 2024](https://aclanthology.org/2024.findings-acl.572/), §§3–6, Table 1 | Separately tests detecting underspecification and interpreting it; finds detection can coexist with overly definite/default interpretations. Includes 216 implicit-reference pairs sourced from CLAIRE and varies prompt order. | “Knows the distinction but still commits” is not a new narrative by itself. Natural full-discourse **supported-recovery versus unsupported-specificity** behavior and a selection/method consequence would have to add the contribution. Stronger models alone do not supply novelty. |
| [RefNLI, Findings NAACL 2025](https://aclanthology.org/2025.findings-naacl.450/), §§2–4, Tables 1–2 | Expert labels for reference/context ambiguity in 1,143 retrieved claim/evidence pairs; evaluates downstream consequences of reference-determinacy assumptions in NLI. | “Check reference before entailment” and “reference mistakes corrupt verification” are occupied. Their problem is cross-text context identity, not omitted-role interpretation. Do not relabel RefNLI as DNI/INI to manufacture replication. |
| [Cui & Hershcovich, IWPT 2021](https://aclanthology.org/2021.iwpt-1.7/), §§2–3, Table 2 | Re-annotates six implicit-participant categories; native semantic graphs and parsing metrics already distinguish them. | Provides natural review text and a source taxonomy, not candidate-specific filler-support labels. E000b reproduces 391 typed participants over 393 segments / 116 review IDs. |
| [Cui & Hershcovich, DMR 2020](https://aclanthology.org/2020.dmr-1.5/), taxonomy and examples | Fine-grained types and differences from other implicit-argument schemes. | Typology is prior art. Use the 2021 revision for any inventory, not the superseded 2020 counts. |
| [CLAIRE, LREC 2022](https://aclanthology.org/2022.lrec-1.354/), §§3.1–3.5, Tables 1–3 | Natural wikiHow revisions with generated alternatives and independent human plausibility scores; several incompatible fillers can be plausible. | Useful for plausibility / multiple interpretation studies. Its annotation explicitly asks plausibility, not entailment or uniquely licensed specificity. An original editor insertion also need not be entailed by the earlier text. It cannot silently supply strict support gold. |
| [NAACL 2025 relative-clause ambiguity](https://aclanthology.org/2025.naacl-long.177/), abstract/introduction | Studies ambiguity resolution and world-knowledge biases across six languages. | Scope/breadth comparator; not a direct omitted-role or filler-grounding dataset. No experimental details beyond inspected portions are asserted here. |

The earlier seven-paper alignment remains relevant: Roit et al. already use
entailment for document-level implicit argument detection; DiscourseEE already
permits null; REGen already treats contextual grounding and specificity. These
collisions are cumulative constraints, not proof that one paper owns every possible
version of L02.

## Source correction

The first follow-up acquisition mistakenly included `2020.dmr-1.3.pdf`, which is
*Building Korean Abstract Meaning Representation Corpus*. Its transport and PDF
format are valid, but it is **not** the intended UCCA source and is not used as
evidence. The correct `2020.dmr-1.5.pdf` was separately retrieved and inspected.
The original acquisition manifest is preserved rather than rewritten.

## Searches and boundary

2026-09-08 queries covered implicit arguments / reference / specificity; semantic
underspecification and unwarranted disambiguation; extraction abstention; 2025–2026
implicit arguments; and targeted DUST, RefNLI, UCCA and CLAIRE searches. Argument
mining (premise/warrant reconstruction) and programming-task underspecification
were excluded as different objects. No exact licensing-conditioned frontier paper
was located. That is limited search evidence, not an unconditional novelty pass.

## What would actually constitute a new story?

A defensible candidate is an **evidence-selection consequence**: additional natural
discourse can help locate a participant while causing a system to commit to a
specific interpretation the discourse does not license; explicit interpretation
changes this trade-off beyond a candidate-level entailment check and matched
generic caution. This requires independent support judgments on the same items,
not just classification changes or an INI-null rule. At present it is a hypothesis.

A competing, potentially useful result is that source-native interpretation adds
no predictive or intervention value once candidate support is measured. A prompt
tie with 42 cases cannot establish that result; it would need an adequately precise
comparison with a stated practical margin and multiple independent documents.
