# 2026-09-13 — Access-Conditioned Knowledge Encoding — Selection Audit

**Working lead:** Does Future Access Shape What an LLM Learns?  
**Status:** **HOLD — OWNER + SUBSTRATE/RESOLUTION BLOCKER**  
**Compute:** **NO COMPUTE AUTHORIZED**

This is the full Selection audit for the new lead registered in `2026-09-13_PROVENANCE_BATCH_SEARCH_XXII.md`.

---

# 1. RQ, mother, importance

## Plain-language RQ

> **Do language models preferentially learn the information they expect to be asked about later?**

More precise:

> **Before a model encounters new information, can the distribution of access demands it has learned selectively determine which parts/views of the same later information become easy to retrieve and retain?**

This is a mechanism / model-learning question, not a new benchmark.

## Mother phenomenon

Jiang et al., ACL 2024, *Instruction-tuned Language Models are Better Knowledge Learners* reports that the standard order `new documents -> instruction tuning` can produce low document perplexity yet poor factual QA. Reversing the order—pre-instruction-tuning (PIT), then training on documents—substantially improves new-knowledge QA (reported +17.8% over standard instruction tuning). The paper explicitly hypothesizes that exposure to how knowledge will later be accessed through questions helps the model encode complex documents in an access-aware way.

Source: https://aclanthology.org/2024.acl-long.296/

**Mother verdict:** `PASS` for a mechanism audit. We are not betting the project on first finding that pre-access instruction affects knowledge learning.

## Why the question matters

The parent establishes a useful *overall* intervention. It does not establish whether parameterized knowledge acquisition is **access-neutral** or **prospective/selective**.

If access demand selectively changes what the model subsequently learns from identical text, then instruction/post-training does more than teach how to answer: it changes the model's future **learning filter**. That would revise the usual picture in which new factual text supplies learning signal independently of how the model expects the information to be queried later.

---

# 2. Candidate accounts

## A — prospective / access-conditioned encoding

The model's learned access demand acts as a prior over what information deserves representational/parametric investment. Prior access regime A versus B therefore changes which *subsequently encountered* information is preferentially learned.

Signature: a selective A↔B crossover that is materially stronger on knowledge learned **after** the access manipulation than on old/control knowledge.

## B — generic learnability

Pre-instruction exposure mainly produces a better learner / instruction follower. The model absorbs later documents better broadly; access A versus B does not strongly determine what is learned.

Signature: new knowledge improves across access views without a selective A↔B crossover.

## C — retrieval-policy / query-skill specialization

The manipulation only makes one access/query family easier. It does not change later encoding.

Signature: A/B specialization is already present to a similar extent on old/control knowledge and does not interact specifically with knowledge learned after the manipulation.

---

# 3. Ownership and reviewer compression

## Closest owner

Jiang et al. 2024 already owns:

> `pre-access instruction/QA exposure -> later document knowledge learning improves`

and explicitly states the hypothesis that the model encodes complex documents in light of how the knowledge is accessed through questions.

Therefore the phrase **“future access shapes encoding” is not itself novel**.

## Strongest reviewer compression

> `Jiang et al. already propose access-aware encoding as the explanation for PIT; the new experiment is just the missing control proving their mechanism.`

That compression wins if the project only shows:

- PIT > standard instruction tuning again;
- PIT-A is best on the exact A prompt/interface;
- activation/probe differences;
- one relation/query family transfers better after being practiced.

## Surviving candidate contribution

The stronger statement not entailed by the parent's overall PIT gain is:

> **Changing only the expected access demand before new information arrives selectively changes which information is learned from a later, otherwise identical experience.**

This is a **conditional/selective learning law**, not merely an explanation for why PIT raises mean QA accuracy.

## Ownership verdict

# `UNRESOLVED NOVELTY`

Internal anti-resurrection passed: no existing recent project route in the repository owns this selective-access × later-learning interaction. The external 2024–2026 successor audit was started and did not surface an exact owner, but public-search tool limits were reached before a sufficiently exhaustive citation/successor sweep was completed. Absence of a hit is not novelty evidence.

**Blocker 1:** finish direct-owner audit before any pilot.

---

# 4. SAME-QUANTITY and identifying operation

A/B must not be two unrelated QA tasks or mere prompt paraphrases.

The strongest current design principle is:

1. begin from the same base checkpoint;
2. during the access-manipulation stage, expose both A and B arms to **matched semantic material**;
3. differ mainly in **which information is repeatedly required for successful access/use**, counterbalanced across relation labels/views;
4. then train both arms on the **exact same later documents** containing both kinds of new information with matched tokens, objective, steps and optimizer schedule;
5. evaluate both access views on new facts and on old/control facts;
6. include at least one neutral/paraphrastic probe not identical to the practiced access interface.

This yields the primary estimand:

`pre-access demand (A/B) × test access/view (A/B) × knowledge status (new/old)`.

The critical evidence for Account A is a materially stronger crossover for **new** knowledge than for old/control knowledge.

## Why the stage-1 matching matters

If A-model simply sees more A semantics/tokens than B-model, a later A advantage can be ordinary feature/relation familiarity. The pre-access stage should therefore equalize semantic exposure as much as possible while changing which relation/view is made **behaviorally task-relevant**.

Example shape only, not frozen design:

- each stage-1 item exposes both relation A and relation B information;
- A arm is repeatedly required to answer/use A while B is incidental;
- B arm gets the symmetric treatment;
- relation identities/mappings are counterbalanced so one inherently easier relation cannot explain the result.

The final experimental substrate is **not authorized** by this file.

**Identification verdict:** `PLAUSIBLE, NOT YET PILOT-READY`.

---

# 5. Successful-result chain

Strongest desired observation:

> Same later documents + same learning budget, but prior A-vs-B access demand produces a large counterbalanced crossover on newly learned information; old/control knowledge shows little corresponding crossover; the effect survives neutral/paraphrastic access and is larger under information competition than under trivial single-fact exposure.

Inference chain:

`new-only selective crossover`
→ `prior access demand changes later acquisition beyond generic query skill`
→ `knowledge learning is access-conditioned rather than fully access-neutral`
→ `instruction/post-training history can selectively bias what future text becomes parameterized knowledge`.

The last arrow is Main-worthy only if the result survives counterbalancing and a nontrivial generalization probe. One exact prompt interface is insufficient.

**Successful-result verdict:** `PASS IN PRINCIPLE`.

---

# 6. Pre-result outcome map

## Outcome A — new-only A↔B crossover

Supports prospective/access-conditioned encoding, subject to the old-knowledge and neutral-interface controls.

Return to Selection for C2/C3; do not immediately scale.

## Outcome B — PIT/global improvement but little selective crossover

Supports a generic-learnability account over selective prospective encoding. This would constrain the parent's explanation but may be Findings-scale rather than Main by itself.

Do **not** mutate the project into generic PIT optimization.

## Outcome C — similar A↔B specialization on old and new knowledge

Supports retrieval/query-policy specialization. This weakens the claim that encoding of later information is selectively changed.

Likely `HOLD / NO-GO` for the current paper identity unless an independently pre-specified consequence is large.

## Outcome D — no stable PIT/access effect on the chosen checkpoint

Mother-transfer / resolution failure. Stop; no model shopping.

## Heterogeneity

Only interpretable under a conditioning variable declared in advance (e.g. document information competition/complexity). Do not mine relation types post hoc until one works.

---

# 7. Resolution / feasibility

Known prior signal:

- Jiang et al. report a large overall PIT advantage (+17.8% over standard IT in their setup), suggesting the parent effect is not intrinsically tiny.

Unknown load-bearing signal:

- the proposed selective A↔B interaction may be much smaller than the overall PIT gain;
- no resolution estimate exists yet for a pre-specified tractable open checkpoint;
- parent code/data were not recovered through the available public GitHub index during this round;
- rebuilding a large factual-learning corpus/pipeline would be a major negative prior and could change the task into data engineering.

The first compute authorization, if ownership and substrate clear, must therefore be a **bounded resolution/mother-transfer audit**, not a full C1 experiment.

Before that authorization we need:

1. a concrete public/clean substrate with minimal reconstruction;
2. one pre-specified model family/checkpoint;
3. an expected parent-effect floor or pilot gate;
4. independent units and seed plan;
5. an estimate of whether the three-way interaction can be resolved without parent-scale training.

**Resolution verdict:** `HOLD — SUBSTRATE/RESOLUTION`.

---

# 8. Main-level growth path

If C1 is real and identified:

## C1 — Does expected access select later learning?

Counterbalanced selective crossover under identical later document exposure.

## C2 — Hidden condition: information competition

The ACL-2024 parent motivates a concrete boundary: QA access is simple while documents contain many interwoven facts. Predeclare the prediction that access-conditioned selectivity is small when a document carries one easy fact but increases when multiple facts compete under a fixed update budget.

This would turn a parent explanation into a conditional law rather than a one-off PIT mechanism.

## C3 — Does the favored information become genuinely easier to retain/use?

Use neutral paraphrases and a matched later-interference/retention test to separate interface-specific retrieval from stronger acquisition priority.

If the effect disappears outside the trained interface, the strong encoding claim is not supported.

Possible final statement:

> **Language models do not absorb new text in an access-neutral way: instruction history creates prospective learning priorities that determine which information in the same later experience becomes parameterized and durable.**

This statement is large enough for Main only if it is established beyond one synthetic query codebook.

---

# 9. Final verdict

# **HOLD — OWNER + SUBSTRATE/RESOLUTION BLOCKER**

The RQ, mother, competing accounts, identification shape, successful-result chain and Main-level upper bound are strong enough to keep.

The candidate is **not pilot-authorized** because two load-bearing prerequisites remain unresolved:

1. complete the external successor/direct-owner audit for selective access-conditioned knowledge acquisition;
2. secure a tractable, non-data-engineering substrate and show the selective interaction is resolvable on a pre-specified open checkpoint.

No GPU work is authorized by this record.
