# L13 — Claim calibration against Main-conference standards

Date: 2026-09-11. Written against `RESEARCH_EXECUTION.md` §3 and
`RESEARCH_TOPIC_SELECTION.md` gates 4–6. Its purpose is to state each claim at the
scope the evidence actually licenses, and to name where the current write-up
over-claims.

---

## 1. Two over-claims in the current write-up, and their corrections

### Over-claim A — "timeline construction is not truth-preserving"

**Status: false as stated. Must be removed.**

E12 tested the same proposition with the same open status in two other temporal
constructions, on the same 40 bases:

| construction | example | instantiation rate |
|---|---|---|
| `before_neutral` | *Before Maya submitted the application, the portal closed.* | 0.425 – 1.000 |
| `about_to` | *Maya was about to submit the application when the portal closed.* | **0.150** (all three models) |
| `before_modal` | *The portal closed before Maya could submit the application.* | **0.025 – 0.250** |

Timeline construction **is** truth-preserving wherever English marks non-realization
aspectually or modally. The correct scope is: *the case where non-veridicality is
carried by nothing but the temporal connective's lexical semantics.*

### Over-claim B — using the plain-timeline rate as the error rate

**Status: not licensed. The headline number must change.**

The plain instruction says "list the events **described** in this passage". Listing a
described-but-unrealized event under that instruction is defensible, and a reviewer will
say so. Two quantities are error-by-construction and must carry the headline instead:

**(i) Under an instruction that explicitly excludes unresolved events** — *"list only the
events that actually happened … do not list events whose occurrence the passage leaves
open"*:

| model | `before_neutral` | `before_cancel` (same instruction, explicit negation) |
|---|---|---|
| Llama-3.1-8B | **1.000** | 0.425 |
| Gemma-3-12B | **0.775** | 0.250 |
| Olmo-3-7B | **0.625** | 0.150 |
| Qwen3-8B | **0.200** | 0.025 |

Three of four models violate an explicit prohibition for the unresolved case while
obeying it for the negated case. **Qwen3-8B substantially complies**, and the paper must
say so rather than averaging it away.

**(ii) Downstream propagation (E13)** — the model reads only its own timeline:
P(YES) on `before_neutral` rises +0.26 to +0.73, with `after` and the non-temporal
control preserved in both Qwen checkpoints. This is harm, not interpretation.

---

## 2. Control upgrade

`nontemporal_neutral` ("Maya **planned to** submit the application") introduces an
intention, not an event in progress, so omitting it is trivially correct. `about_to`
("was about to submit … when …") describes an event actually underway with the same open
outcome, and is therefore the **stronger matched control**. It should be promoted from a
scope test to a primary control in the paper; `nontemporal_neutral` stays as the
label-availability check it was designed to be.

---

## 3. The claims, at the scope the evidence licenses

> **C-A (dissociation).** Asked directly, LLMs judge the subordinate event of an
> unmarked `before`-clause as not guaranteed (P(NOT DETERMINED) 0.59–0.86 in 3 of 6
> families). Asked to emit an event structure from the same sentence — under an
> instruction that explicitly excludes unresolved events — three of four models emit it
> as realized at 0.63–1.00.

Licensed. State the Qwen3-8B exception in the same sentence.

> **C-B (the structure governs belief).** Emitting the structure raises the model's own
> realization commitment on identical text and an identical probe: +0.075 to +0.332
> across 9 checkpoints and 4 families against a form-matched paraphrase control, ~0 on
> the non-temporal passage. A non-generative ordering demand produces ≤0.07, so the
> effect requires the structure to be emitted.

Licensed.

> **C-C (order and realization are independent).** Enabling reasoning takes emitted
> chronological order from 0.34 to 1.00 correct and instantiation from 0.45 to 1.00
> (Qwen3-8B); across models the two are uncorrelated (Llama: order 0.15, instantiation
> 0.98).

Licensed. This is the strongest single result and should be the title claim.

> **C-D (scope).** The failure is confined to constructions where non-veridicality is
> carried by the connective alone. Aspectually marked (`was about to … when`) and
> modally marked (`before X could Y`) counterparts are handled correctly, in constructed
> (0.15; 0.025–0.25) and in natural text (0.14–0.32).

Licensed, and it must appear in the abstract, not only in a limitations section.

> **C-E (consequence).** A downstream reader consuming the model's own timeline inherits
> the false event (+0.26 to +0.73 on P(YES)), with matched controls preserved.

Licensed.

> **C-F (not repairable by prompting).** An explicit prohibition, an explicit three-state
> schema, and a status-first pipeline each nearly eliminate ghosting for explicitly
> negated events (0.35–0.90 → 0.00–0.08) and fail for unresolved ones.

Licensed. Do **not** state it as "cannot be fixed"; state it as "three natural
prompt-level repairs fail".

> **C-G (not plausibility, not scale-fragile).** No monotone dependence on item
> pragmatic bias; instantiation rises from Qwen3-8B (0.45) through 14B (0.98) to 32B
> (1.00) with the control flat at 0.10.

Licensed, with the n=4 caveat on `yes_leaning`.

---

## 4. Under-claiming risk, and the decision it forces

Stated only as "LLMs mishandle `before`-clauses", this is a narrow finding and a
reviewer will compress it to a construction study. The general statement the evidence
gestures at is:

> a model's explicit judgement about an event's status does not survive into the
> structure it emits, and the emitted structure then governs downstream belief.

**We currently have one construction where this happens and two matched constructions
where it does not.** That ratio licenses a *mechanism-with-a-boundary* paper, not a
general claim about structure building.

**This is the single biggest remaining gap.** Two honest ways to close it:

1. **Find a second positive construction.** Candidates where non-veridicality is lexical
   and unmarked are genuinely rare in English — `before` may be close to unique. If a
   second one exists (`until` under negation, `in time to`, some purpose adjuncts), the
   general claim becomes available.
2. **If `before` is unique, do not stretch the construction claim.** Take the generality
   from the *pipeline* instead: the finding is that a classical, well-understood
   semantic property is the one thing that does not survive structure extraction, and
   E13 shows what that costs any system built this way. That is a legitimate Main paper
   and it is what the current evidence supports.

Option 2 is the current default. Option 1 should be attempted once, cheaply, before the
framing is fixed.

---

## 5. Comparison to the calibration target

Against a single-construction award paper such as the imperfective-paradox line, the
comparison is:

| dimension | that shape | ours |
|---|---|---|
| one-sentence example | yes | yes |
| classical parent | yes | yes |
| systematic, not random, failure | yes | yes (6 families, 0.425–1.00 vs 0.10 control) |
| mechanism beyond an error rate | partial | yes (order/realization dissociation; emission requirement; three failed repairs) |
| consequence measured | no | yes (E13) |
| boundary established | contested afterwards | yes, in advance (E08, E12) |
| independent gold | yes | **no — author annotation only. Blocking.** |

Two dimensions where we are stronger than the target shape: the measured consequence and
the pre-established boundary. One dimension where we are strictly weaker and must fix:
independent annotation.
