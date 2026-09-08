# What would a valid L02 support target require?

This is a measurement specification, not new annotation or an executed study.
It follows the SemEval guide §3.2, UCCA revisions, Roit ACL 2024's candidate
entailment formulation, and the limitations identified in DUST / RefNLI / REGen.

## Distinguish the quantities

For natural document d, target event mention e and role r:

- I(d,e,r): the interpretation of the omission (source-native categories).
- L(d,e,r): whether the release records a textual filler link.
- S(d,e,r,a): whether a particular answer a is supported in this event's scope.
- G(a): the specificity/granularity of the answer (type, set, particular referent,
  event/proposition, attribution or modal qualification).

S depends on **the proposed answer**, not only on a role's interpretation flag.
INI permits existential interpretation without requiring ignorance in every
context. DNI permits deictic reference without an in-document mention. An answer
may be a supported type description, a location, or a scoped hypothetical actor.
Neither I nor L alone determines all candidate-specific S values.

The 11 linked INIs are an audit trigger, not 11 independently proven semantic
counterexamples. Some have uncertain interpretation or suspect links. The case
against the blanket mapping additionally rests on the meaning of the labels and
on the difference between requiring an identifiable referent and having contextual
information. Do not replace an overconfident initial mapping with overconfident
claims about annotation errors.

## Resource admission matrix

| Resource | Natural input | Independent labels actually provided | Missing for this mainline |
|---|---|---|---|
| SemEval Task 10 recovered train | Full fiction story | Omission interpretation, annotated filler links | Candidate-specific negative support; complete equivalent-link validation; broader independent documents |
| UCCA revised 2021 | 116 natural reviews / 393 segments | Fine-grained implicit participant type in semantic graphs | Frame-specific role identities; candidate support; role↔node alignment for mixed scenes |
| TNE / Roit ACL 2024 | Multi-sentence documents | Preposition-mediated relation judgments / detection evaluation | The stricter support target is not its typical-reader-inference instruction; no omission-interpretation axis |
| CLAIRE | wikiHow revision contexts | Human plausibility of original and generated alternatives | Plausibility does not entail original-text support; no DNI/INI labels |
| DUST | Mixed source sentence pairs, including CLAIRE | Underspecification and specified counterparts | Not a natural full-discourse candidate-support corpus; occupied detection/interpretation narrative |
| RefNLI | Retrieved claim/evidence pairs | Reference ambiguity plus entailment relation | Different reference object; no event-role omission interpretation |

## Minimal substantive redesign

1. Retain natural full documents; split at source document level before sampling.
   Use SemEval only for development. UCCA can provide an additional review source,
   but role names must be newly annotated, not read off a type label or node ID.
2. Independent annotators first identify target event, role and attribution/modal
   scope, without model predictions or proposed method names. Preserve ambiguity
   and exclusions with reasons; do not force agreement on bad items.
3. Independently judge concrete candidate answers against the complete document:
   supported / contradicted / merely compatible / unresolved; record minimal
   evidence and specificity. Merely compatible is not supported. If reliable
   annotation cannot distinguish these, revise the scientific target instead of
   forcing binary gold.
4. Candidate pools must include published links, natural discourse entities and
   outputs from several frozen systems; blind source identity and randomize order.
   Audit pool coverage. This is additional annotation, not pre-existing gold;
   randomly pairing arbitrary names with roles is not an acceptable main dataset.
5. Match direct, status-first, generic verification and candidate-entailment
   conditions on evidence, output options and resources. A two-call win alone is
   not factorization evidence. Do not hard-gate all INIs to null.
6. Measure supported recovery jointly with unsupported specificity and report
   document-level uncertainty, annotator disagreement, and abstention behavior.
   Use a separate development set for margins and sample-size planning. Require a
   robust method/selection consequence, not simply an extra error category.

No independent humans have completed this annotation in the present project.
Codex review notes and model agreement cannot be substituted for it. These steps
are a new data-and-study design, not a missing script that makes the old pilot valid.
