# L13 — Research Note

Last updated 2026-09-11. All numbers are final on `stimuli_v2` (100 scenarios) and the
adjudicated natural set (176 sentences). Full provenance in `PILOT_REPORT.md`; claim
scoping in `CLAIM_CALIBRATION.md`; data contract in `DATA_AND_GOLD.md` + `DATA_AUDIT.md`.

---

## 1. The core question

English `before` is **non-veridical**: *"The portal closed before Maya submitted the
application"* does not entail that Maya submitted it. `after` is veridical. This is
classical, uncontroversial semantics.

> **When an LLM is asked to extract the events of such a sentence, does the connective's
> non-veridicality survive into the extracted representation?**

The question is not whether models *know* the semantics — they largely do. It is whether
that knowledge survives the act of producing a structured event representation, which is
what every event-extraction, timeline, and agent-state pipeline asks a model to do.

## 2. Related work and what is ours

**Classical parents (assets, not competitors).** Non-veridicality of `before` vs `after`
(Anscombe; Heinämäki; Beaver & Condoravdi). Psycholinguistic processing of `before`/`after`
with item-level veridicality norming (Politzer-Ahles et al., PLOS ONE 2017). Richer Event
Description annotation guidelines already forbid putting hypothetical events on the actual
timeline — the applied statement of the same concern.

**Nearest modern neighbours and what they own.**

| work | owns | does not own |
|---|---|---|
| *Are LLMs Temporally Grounded?* and the temporal-ordering line | ordering, duration, self-consistency of **given** events | whether a construction licenses believing a relatum exists |
| Temporal-mechanism work on before/after ordering (2026) | internal machinery of **ordering** | realization as a separate quantity |
| MAVEN-FACT (Findings EMNLP 2024) | large-scale event factuality labels, LLM benchmark | any manipulation of construction or of the extraction demand |
| TReMu (Findings ACL 2025) | temporal anchoring, unanswerable time questions | whether the event exists at all |
| Belief-R (EMNLP 2024) | defeasible belief revision in general | whether the construction manufactured the belief |

**Ours.** Not a factuality benchmark and not a temporal-reasoning benchmark. The object is
a **dissociation between judgement and extraction**, established by manipulating the
construction and the extraction demand while holding the proposition fixed, plus the
downstream cost of that dissociation. The killed-ledger entry K064 ("event mention ≠ event
occurrence") is cleared in `PARENT_AUDIT.md`: the estimand here is a relation between two
computations, not a label.

## 3. Experiments run

| id | question | verdict |
|---|---|---|
| **E01** | direct judgement profile across conditions | models mostly judge correctly |
| **E02** | does emitting a structure change the model's own belief? | yes, +0.06 to +0.38 |
| **E04** | does an explicit prohibition stop it? | no for unresolved, yes for negated |
| **E05** | does a *non-generative* temporal demand do it? | no (≤0.07) — emission required |
| **E06** | does an explicit three-state schema repair it? | no in 4 of 5 checkpoints |
| **E07** | scale ladder, Qwen3 0.6B–32B | rises with scale; control flat |
| **E08** | natural `before`-clauses from the Pile | replicates on unmarked items |
| **E09** | reasoning mode during extraction | order → 1.00, instantiation → 1.00 |
| **E10** | status-first pipeline repair | fixes negated, fails unresolved |
| **E11** | is it item plausibility? | no |
| **E12** | other non-veridical constructions | handled correctly |
| **E13** | downstream reader consuming the model's own list | inherits the false event |
| **E14** | two further families (Mistral-Small-24B, Phi-4-mini) | replicates |
| **E15** | purpose infinitives | handled correctly |
| **E16** | remove the ordering requirement | failure persists — it is **enumeration**, not ordering |

## 4. Setup

**Controlled materials.** 100 hand-authored scenarios × 9 conditions = **900 items**.
Each scenario is one agent, one target event `E`, one main event `M` that is a plausible
blocker of `E` and reads naturally in both orders. All conditions share the lexical
content, so contrasts are minimal pairs.

| condition | example | gold |
|---|---|---|
| **`before_post`** (primary) | *The portal closed before Maya submitted the application.* | NOT_DETERMINED |
| `before_neutral` (fronted) | *Before Maya submitted the application, the portal closed.* | NOT_DETERMINED |
| `after` | *After Maya submitted the application, the portal closed.* | YES |
| `before_confirm` / `before_cancel` | + *"…she sent it by email that evening."* / *"…it was never submitted."* | YES / NO |
| `nontemporal_neutral` | *Maya planned to submit the application. The portal closed at midnight.* | NOT_DETERMINED |
| `about_to` | *Maya was about to submit the application when the portal closed.* | NOT_DETERMINED |
| `purpose` | *Maya was there to submit the application when the portal closed.* | NOT_DETERMINED |
| `before_modal` | *The portal closed before Maya could submit the application.* | NO |

`before_post` and `before_modal` differ by one word (`could`); `before_post` and `after`
differ by one word (the connective).

**Natural materials.** 1,943 Pile sentences containing a `before`-clause → 471 in scope
under an explicit written construction definition (`src/before_scope.py`; PP, forensic,
generic, deontic, imperative and irrealis uses excluded) → **211 hand-adjudicated** →
**176 kept**, each with a written target proposition and a realization judgement.

**Measurement.**
- *Judgement:* "Based only on the passage, is the statement true?" → YES / NO / NOT
  DETERMINED, scored from label-token log-probabilities over **all 6 option permutations**
  and averaged, removing position and letter bias. A separate 1–5 likelihood probe keeps
  strict entailment and pragmatic expectation apart.
- *Extraction:* the model emits an event list; the target counts as instantiated only if
  the proposition occupies a **main clause** with no negation or hedge, so copying
  `Before X, Y` is not counted. The rule was validated against 160 hand-adjudicated
  generations (159/160; the single error is a false negative, so rates are lower bounds).
- *Controls:* a **paraphrase-first** arm (same "the model generated something first"),
  a **non-temporal** arm (label availability), and an **unordered** arm (E16).
- *Statistics:* paired bootstrap over scenarios, 10,000 resamples, 95% percentile CI.

**Models.** Qwen3 (0.6B, 1.7B, 4B, 8B, 14B, 32B), Llama-3.1-8B-Instruct,
Gemma-3-12B-IT, Olmo-3-7B-Instruct-DPO, Mistral-Small-24B-Instruct, Phi-4-mini —
6 families, 11 checkpoints. Local GPUs, existing environment, cached weights, no
downloads, greedy decoding for the one generation step, log-prob scoring elsewhere.

## 5. Core claims

**C1 — Dissociation.** Asked directly, models judge the subordinate event of an unmarked
`before`-clause as not guaranteed (P(NOT DETERMINED) 0.54–0.66 on `before_post` for
Qwen3-8B, Llama-3.1-8B, Gemma-3-12B). Asked to enumerate the events of the same sentence,
they emit it as a realized event at **0.87–1.00**, against ~0.14 for a matched
non-temporal open proposition.

**C2 — The emitted inventory governs the model's own belief.** On identical text and an
identical probe, having emitted the list raises P(YES) by **+0.06 to +0.38** against a
form-matched paraphrase control. A non-generative temporal demand moves it ≤0.07, so the
effect requires the structure to be emitted.

**C3 — The trigger is enumeration, not ordering.** Removing the chronological requirement
("in any order") leaves the failure intact and slightly worse (0.775–1.000 vs 0.450–0.975).

**C4 — Order and realization are independent.** Enabling reasoning takes emitted
chronological order from 0.34 to **1.00** correct and instantiation from 0.45 to **1.00**
(Qwen3-8B). Across models the two are uncorrelated (Llama: order 0.15, instantiation 0.98).

**C5 — Scope.** The failure is confined to constructions where non-veridicality is carried
by **nothing but the connective**. Marked counterparts are handled: `about_to` 0.21–0.22,
`purpose` 0.18–0.35 (0.18–0.35 on the natural 85 subset), `before_modal` 0.03–0.27 —
against `before_post` 0.87–1.00. One word (`could`) moves Qwen3-8B from 1.00 to 0.04.

**C6 — It replicates on natural text.** On hand-adjudicated Pile sentences, unmarked
non-veridical `before`-clauses are instantiated at **0.44–0.81** while marked ones sit at
**0.00–0.18**, and the direct probe on the same sentences gives P(YES) 0.006–0.255.

**C7 — It propagates.** A reader consuming only the model's own emitted list raises P(YES)
by **+0.26 to +0.73**, with the `after` and non-temporal controls preserved.

**C8 — Prompt-level repair fails selectively.** An explicit prohibition, an explicit
three-state schema and a status-first pipeline each nearly eliminate instantiation of
**explicitly negated** events (0.35–0.90 → 0.00–0.08) and fail for **unresolved** ones.

**C9 — Not plausibility, not scale-fragile.** No monotone dependence on item pragmatic
bias; instantiation rises across the Qwen3 ladder (0.45 → 0.98 → 1.00) with the control
flat at ~0.10 in all six checkpoints.

**Rejected along the way:** that models over-commit when asked directly (C1-original);
that the connective's representation contaminates factuality without generation (E05);
that timeline *ordering* is the mechanism (E16); that natural text does not replicate
(superseded sampling artifact).

## 6. Conclusion

A model can read a sentence correctly, be asked what events it contains, answer with an
inventory that contains an event the sentence never asserted, and then believe its own
inventory. The knowledge is present at the judgement interface and absent at the
extraction interface. Extraction is where a classical semantic property is discarded, and
the discarded belief then propagates to whatever consumes the extracted structure.

Reasoning does not help: it makes the temporal order perfect and the event ontology worse.
Three natural prompt-level repairs recover events the text *negates* and none recovers
events the text *leaves open* — there is no room for `unresolved` in what the model emits.

## 7. Boundaries and limitations

1. **Construction-specific.** One positive construction (`before`), three matched negative
   ones. Whatever marks non-realization — modal `could`, aspectual `was about to` — is
   respected. The general statement ("judgement does not survive extraction") is supported
   by one construction and must be stated as such.
2. **Prevalence.** 12.3% of adjudicated natural plain-past `before`-clauses are
   non-veridical, so the affected cell is real but uncommon; that is also why the natural
   critical cell is n=16 and why a controlled set is necessary rather than optional.
3. **Qwen3-32B is not a dissociation case on the primary form.** It answers the direct
   probe with P(YES)=0.54 on `before_post`, i.e. it over-commits before any extraction.
   C1 holds for 3 of 4 checkpoints on that form; the extraction failure holds for all 4.
4. **The instantiation measure is a validated rule, not a human label** (159/160 against
   hand adjudication, conservative). Rates are lower bounds.
5. **Gold and the natural adjudication are author judgements** under a written, blinded
   protocol with published raw responses.
6. **English only; one connective family; `purpose` is marginal on 15 of 100 items**
   (flagged, reported both ways).
7. **The mechanism is characterised at the level of emitted structure.** E05 rules out a
   representation-level coupling that needs no generation; it does not localise where in
   generation the collapse happens.
