# L13 — Data audit against Main-conference standards (2026-09-11)

Written because the entire empirical basis now rests on **one construction**: E12 tested
two other non-veridical constructions on the same 40 bases and both are handled
correctly (`about_to` 0.150; `purpose` 0.125–0.275; `before_modal` 0.025–0.250, against
`before_neutral` 0.425–1.000). The data therefore has to be unimpeachable on `before`
itself.

## 1. Size

| | |
|---|---|
| independent scenarios (unit of statistics) | **40** |
| core items | 200 |
| extension items | 120 |

**Verdict: the item count is fine; the number of independent scenarios is thin.**
Every CI in the study is bootstrapped over 40 units. Diagnostic sets in strong analysis
papers sit at roughly 100–500 items over 50–200 independent scenarios. We are at the
bottom of that range. Going to **80 bases / 400 core items** is the right target: enough
to halve the CI widths, not so much that the paper turns into a benchmark contribution.

## 2. Over-construction

**Verdict: too templatic in one specific and fixable way.**

All 40 `before_neutral` items are the *fronted* subordinate order:

> `Before <target>, <main>.`

English overwhelmingly prefers the **post-posed** order, and our own Pile scan confirms
it: of 4,615 natural sentences containing " before ", only 255 have the fronted,
comma-marked form. **We tested the minority word order.** If the effect is specific to
the fronted order it is a surface artifact, and the paper does not survive.

This is now the highest-value single test in the study, and it has a second payoff: the
post-posed form

> `The portal closed before Maya submitted the application.`

is the exact minimal pair of the already-collected `before_modal`

> `The portal closed before Maya could submit the application.`

differing in **one word**. That is the tightest possible isolation of "is
non-veridicality marked or carried by the connective alone", which is the study's
central scope claim.

Added as condition `before_post` (E16).

## 3. Binding between the data and the scientific question

The question is whether the connective's non-veridicality survives into an emitted
structure. Each design decision is either load-bearing for that or a declared control:

| feature | why it is there | what it would confound if removed |
|---|---|---|
| main clause is a plausible **blocker** | without it, `before X` is pragmatically near-veridical and the item has no open reading to lose | the estimand disappears |
| `after` with the *same* clauses | veridicality ceiling; differs from `before_neutral` in one word | — |
| `nontemporal_neutral` | middle-label availability | a low `NOT DETERMINED` rate could be label avoidance |
| `about_to` / `purpose` (same blocker, same proposition) | isolates the **connective** from the blocker and from open status in general | without these, the blocker itself could be the cause |
| `before_modal` | isolates **marking** | — |
| `before_post` (new) | isolates **word order** | a fronted-order artifact would masquerade as a semantic effect |

The blocker is a deliberate confound with `before`, and `about_to` / `purpose` are
precisely what unconfounds it: same blocker, same proposition, same open status,
different construction, and the effect vanishes. That comparison, not the raw rate, is
what binds the data to the question.

## 4. Known defects, carried forward

1. Two `after` items have naturalness < 4 (b16, b33); repair recorded, leave-out check
   shows no change (`data/GOLD_AUDIT_v1.md`).
2. Domain coverage is narrow: 40 everyday administrative/physical scenarios. The
   expansion should widen it deliberately rather than clone the frame.
3. Gold is author annotation. Blocking for submission.

## 5. Actions

- **E16** — `before_post` on all bases. Decisive for the surface-order objection.
- **Expansion** — 40 new bases (b41–b80) across wider domains and varied clause lengths,
  authored to the same contract, then re-run the core comparisons on all 80.

---

## 6. Expansion executed — `stimuli_v2` (2026-09-11)

| | v1 (frozen) | **v2** |
|---|---|---|
| independent scenarios | 40 | **80** |
| core items (5 conditions) | 200 | **400** |
| extension items (4 conditions) | 160 | **320** |

`stimuli_v1` stays frozen so the already-recorded runs keep corresponding to it.
`L13_STIMULI_VERSION=stimuli_v2 scripts/build_stimuli.py` produces v2; v1 is the first
40 bases of the same source, so the two are nested rather than divergent.

### Domain widening

The 40 new bases (b41–b80) were written to leave the administrative/everyday frame of
v1: instrumentation and laboratory work, sport, court proceedings, tunnel rescue,
currency exchange, restaurant service, software release, teaching, trading, family
conversation, roofing, photojournalism, veterinary work, a siege, a concert, retail
refunds, parcel delivery, wildlife management, archaeology, publishing, aircraft
maintenance, titration, hospital discharge, immigration, a wedding, fishing, an election
count, theatre, dentistry, mountain rescue, conservation, patents, disaster relief,
astronomy, gardening, key rotation, athletics, port logistics, film production and a
vaccination campaign.

Clause lengths vary (6–17 words in the subordinate clause) rather than holding the v1
frame constant.

### Naturalness audit of the new bases

All 40 new `after`/`before_neutral` minimal pairs were read and adjudicated. One defect,
of the same class as v1's:

- **b69**: *"After the dentist fitted the crown, the lab sent the wrong shade."* — the
  lab sends the crown before it is fitted, so the `after` reading is incoherent.
  **Repaired before any model was run**: the main clause is now *"the practice was
  flooded"*, which reads naturally in both orders and is a plausible blocker.

Defect rate 1/40, against 2/40 in v1. No other item required repair. Four
`nontemporal_neutral` sentences were reworded to remove incidental `before`/`after`
tokens flagged by the structural validator.

### Conditions now in the design

| condition | n (v2) | gold | role |
|---|---|---|---|
| `before_neutral` | 80 | NOT_DETERMINED | the estimand |
| `after` | 80 | YES | veridicality ceiling, one-word minimal pair |
| `before_confirm` / `before_cancel` | 160 | YES / NO | resolution anchors |
| `nontemporal_neutral` | 80 | NOT_DETERMINED | middle-label availability |
| `about_to` | 80 | NOT_DETERMINED | aspectually marked control |
| `purpose` | 80 | NOT_DETERMINED | unmarked non-temporal control |
| `before_modal` | 80 | NO | modally marked control |
| **`before_post`** | 80 | NOT_DETERMINED | **word-order control; one-word minimal pair with `before_modal`** |

Eight conditions over 80 scenarios, 720 items. That is a diagnostic set, not a
benchmark: every condition exists to remove one specific alternative explanation, and
none exists to raise the item count.

### Audit of the new `before_post` condition

A random 18 of the 80 post-posed items were read and adjudicated. All read as natural
English and all are genuinely `NOT_DETERMINED` — post-posing is truth-conditionally
equivalent to the fronted order, and no item acquired an odd reading under the
transformation. No defects found.

Examples: *"The doors locked before Daniel boarded the train."*, *"A competitor
published the design before the founders filed the patent."*, *"Preservation status was
granted before the council demolished the old mill."*

### What the data now is

720 items over 80 hand-written scenarios in eight conditions, every condition traceable
to one alternative explanation it removes. No LLM wrote, selected or labelled any item.
Gold follows from the construction and was verified 200/200 against a blinded pass on
v1; the v2 expansion uses the identical contract, and its authored prose was audited
item by item (one defect, repaired pre-run).

---

## 7. Second expansion and reconciliation — `stimuli_v2` final (2026-09-11)

The core set had drifted to 100 bases while the extension conditions still covered only
80, and one model run had been interrupted, so results and data were no longer in
correspondence. Both were rebuilt and every model re-run on the final set.

**Final `stimuli_v2`: 100 scenarios × 9 conditions = 900 items.**

| condition | n | gold | role |
|---|---|---|---|
| `before_neutral` (fronted) | 100 | NOT_DETERMINED | v1-compatible form |
| **`before_post`** (post-posed) | 100 | NOT_DETERMINED | **the ordinary English order; primary estimand** |
| `after` | 100 | YES | veridicality ceiling, one-word minimal pair |
| `before_confirm` / `before_cancel` | 200 | YES / NO | resolution anchors |
| `nontemporal_neutral` | 100 | NOT_DETERMINED | middle-label availability |
| `about_to` | 100 | NOT_DETERMINED | aspectually marked control |
| `purpose` | 100 | NOT_DETERMINED | unmarked non-`before` control |
| `before_modal` | 100 | NO | modally marked control, one word from `before_post` |

### Defects found in this pass and what was done

1. **Extension conditions covered only 80 of 100 bases.** Decompositions written for
   b81–b100; all 100 now carry all nine conditions.
2. **Subject–verb agreement.** `b98` ("the volunteers") produced *"The volunteers was
   about to …"*. Fixed. A structural check for this class is now in
   `scripts/validate_stimuli.py`, and a regex sweep over the rebuilt file returns clean.
3. **`purpose` frame naturalness.** *"X was there to VP when Y"* presupposes a located
   action. For 15 of 100 bases the subject is an institution performing a non-located
   act (*"The company was there to pay the fine"*), and the item reads marginally. These
   are **flagged, not deleted**: items carry `purpose_natural`, and `purpose` is reported
   both on all 100 and on the natural 85. The other 85 read naturally, and the
   domain-widened bases b41–b80 — mostly physically situated work — are natural
   throughout.

### Standing defect

`before_neutral` uses the minority fronted order. It is retained only for continuity
with the v1 runs; `before_post` is the primary estimand and is the form the natural
corpus overwhelmingly uses.
