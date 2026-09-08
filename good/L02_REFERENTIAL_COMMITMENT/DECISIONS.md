# Research decisions

## 2026-09-08 — Select L02 and tighten the scientific target

User authorized choosing and beginning one good project and permits evidence-led
departures from speculative planning. All writes for this work stay in this directory.
Existing untracked L03 work was present before this session and is not ours.

Selection: L02 has the clearest correspondence between naturally occurring language,
pre-LLM expert annotation, and a consequential generation decision. L03 is promising
but has existing separate work and provider-access issues; L04 has a closer published
set-valued morphology parent and language/resource concentration. This is a judgment
about where to start, not a claim that the other projects are invalid.

Working narrative: **Recovering more of an event is not necessarily recovering more
of what the discourse commits to.** Investigate the frontier between licensed filler
recovery and unlicensed specificity, and whether explicit licensing changes it beyond
generic caution. This is a research narrative, not a result. Natural context may help
find a referent while leaving the decision to posit that referent unchanged; that
interaction would deepen the main question, but must be tested rather than assumed.

The inherited phrase “factorization is necessary” is too strong for a prompt comparison.
An advantage of two calls can reflect additional compute, deliberation, formatting or
abstention cues. Keep an identical-schema one-call order comparison, a generic
verification control, and explicit resource accounting. Report operational effects
under tested conditions, not architectural impossibility for direct generation.

## Data corrections before compute

1. DNI is definite interpretation, not automatically a recoverable textual filler.
   Preserve interpretation and link availability separately. A missing link is neither
   an INI label nor proof that no conceivable inference is available.
2. “No specific referent” does not assert that no participant exists. INI may license
   an existential/type description; only unsupported *specificity* is the target.
3. DNI fillers may be event/proposition spans, discontinuous expressions, or several
   equivalent mentions. Retain source token IDs and graph structure; do not restrict
   gold to named entities or pick one canonical string.
4. Frame/role and licensor may predict NI type. A frame-role majority baseline is
   required; test-only labels cannot inform it. A no-discourse diagnostic must precede
   any claim of discourse-sensitive understanding.
5. Full chapters are natural context. A shortened window creates a separate evidence
   condition: re-evaluate which gold links are visible; never relabel a cropped DNI
   as INI. Exclude unresolved source links from filler scoring, not from the audit.
6. SemEval has one train story and two test chapters from another story, all Doyle.
   Hundreds of roles are not hundreds of independent documents. No genre-wide CI
   from a naive item bootstrap; no context-transfer or modern real-world IE claim yet.
7. Famous public fiction creates potential pretraining exposure. Reading passages is
   still a meaningful task, but do not describe the corpus as contamination-free.
8. A pipeline given the role cannot establish role knowledge by repeating that role.
   An independent role probe needs a separate, validated task; defer rather than leak gold.

## Acquisition

Original Saarland documentation remains available. Its FBK dynamic download entry
returns 404. Internet Archive CDX and the preserved Task 10 training page provide a
traceable original-package route. DKPro supplies a separately pinned single-sentence
sample with provenance; it is useful for parser checks only, not a pilot corpus.
Archive payload validity and published counts remain to be checked.

## 2026-09-08 — Post-acquisition measurement revision

Training source recovered; E000 central counts match the paper. 11 linked INIs,
including two interpretation-uncertain items, contradict using the inherited
label-to-action mapping without review. One link targets an isolated determiner;
other cases include role descriptions, quoted/figurative or hypothetical events.
Do not count all 11 as semantically adjudicated counterexamples. This is an input
contract problem, not evidence to kill the question or a new paper-level claim.

All 580 NI observations remain in the ledger. Specific-filler licensing is unknown
rather than inferred. E001 remains a draft until its unsupported-specificity gold
is independently justified. A positive-link feasibility study is allowed only with
its limited estimand explicitly documented. No GPU run is scientifically justified
merely to produce a number on the invalid error metric.

## 2026-09-08 — Final current-route decision

NO-GO for advancing the current L02 design as a NAACL Main mainline. E000b
confirmed a natural alternative corpus but not the missing support target;
E000c clarified source-global coreference; E001a/E001b completed on 32B and
24B models and supplied development-level interpretation findings only. DUST,
RefNLI, Roit, DiscourseEE and REGen materially constrain an easy reframe.

This is an evidence-based research-design decision, not a claim that no future
paper on the phenomenon is possible and not a statistical rejection of H01–H03.
The strongest reopening route requires independent candidate-support/scope
annotation and an extraction or system-selection consequence beyond generic
verification. Preserve sources, failures, frozen protocols and all model outputs.
Do not switch to or alter another subproject as part of this conclusion.
