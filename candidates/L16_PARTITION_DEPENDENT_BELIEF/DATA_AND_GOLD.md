# L16 — Data and Gold Contract

**Freeze date:** 2026-09-11, before model outputs.  
**Purpose:** define what is manipulated, what is held fixed, the independent unit, and what counts as gold before E01/E02.

---

## 1. Scientific object

L16 is not a factual-QA benchmark. It tests an **invariance relation** over subjective credence.

For one base scenario, define nine atomic hypotheses:

`H1, H2, ..., H9`

They are stated to be mutually exclusive and exhaustive. The target is always `H1`.

Across matched prompts we keep fixed:

- the scenario;
- all nine atomic hypotheses;
- their order of first mention;
- the target proposition (`H1`);
- all world evidence;
- the requested probability scale;
- the reasoning instruction;
- generation settings.

We manipulate only the **displayed partition** over the same atomic set.

Primary partitions:

- `M2`: `{H1} | {H2,H3,H4,H5,H6,H7,H8,H9}`
- `M3a`: `{H1} | {H2,H3,H4,H5} | {H6,H7,H8,H9}`
- `M3b`: `{H1} | {H2,H3,H6,H7} | {H4,H5,H8,H9}`
- `M9`: `{H1}|{H2}|{H3}|{H4}|{H5}|{H6}|{H7}|{H8}|{H9}`
- `FLAT`: identical atomic list and target question, without an additional grouping line; diagnostic baseline only.

`M3a` and `M3b` are precommitted arbitrary regroupings. They diagnose whether the count of salient partition cells matters or whether a specific semantic grouping is driving the result.

The atomic strings themselves must not be added, omitted, duplicated, or reordered across `M2/M3a/M3b/M9/FLAT`.

---

## 2. Gold

### 2.1 Primary gold: extensional partition invariance

The gold relation is exact:

> **Changing only an arbitrary grouping of an unchanged exhaustive atomic hypothesis space adds no information about which atomic hypothesis is true. Therefore the credence in the same target proposition should not change merely because the other atoms are packed or unpacked.**

For any matched base scenario:

`P(H1 | E, partition=M2) = P(H1 | E, partition=M3a) = P(H1 | E, partition=M3b) = P(H1 | E, partition=M9)`

This is the core evaluation target. It does **not** require us to know the objectively correct absolute value of `P(H1|E)`.

### 2.2 Mechanism prediction, not normative gold

Classic partition-dependence work predicts an **ignorance prior** over salient cells:

- `M2 -> 1/2`
- `M3 -> 1/3`
- `M9 -> 1/9`

If LLM confidence is pulled toward this representation-induced prior, then with the target kept as a singleton:

`P_M2(H1) > P_M3(H1) > P_M9(H1)`

under weak information, with the effect attenuating when stronger evidence dominates the ignorance prior.

This direction is a preregistered account prediction. It is not itself the normative probability gold.

### 2.3 Equivalence-awareness gold

For E02, ask a separate question:

> Do the two displayed groupings contain different atomic possibilities or different evidence about which atomic possibility occurs?

For matched L16 pairs, gold is **NO**.

This probe is deliberately separate from the confidence query. It is used to test whether a model can know that two partitions are informationally equivalent while nevertheless assigning different credence.

---

## 3. Data tiers

### Tier A — published human anchor materials

Use publicly accessible / reproducible materials from the classic partition-priming line where licensing/access allows:

- Fox & Rottenstreich (2003), especially the Sunday-hottest case/class pair;
- Ding & Feldman (2025) Registered Report replication/extension, public project `https://osf.io/g9czs/`.

These items establish continuity with the classic phenomenon. They are **not** the primary causal estimate because original case/class formulations alter wording, not only an explicit partition map.

### Tier B — primary content-matched LLM diagnostic grid

Create **48 base scenarios** before any model output is inspected.

Four domains, 12 independent bases each:

1. **forecast / competition** — mutually exclusive future winners, days, locations, categories;
2. **troubleshooting / diagnosis (non-medical in the primary set)** — one of nine exclusive causes or fault states;
3. **classification / provenance** — one of nine exclusive classes/sources;
4. **everyday uncertainty / planning** — one of nine exclusive outcomes or destinations.

The domain labels are for breadth, not separate hypotheses. The scientific unit is the base scenario.

### Why 9 atoms?

Nine allows a large, simple partition contrast (`1/2` versus `1/9`) while retaining two balanced four-atom residual groups for the `M3` condition.

---

## 4. Base-scenario construction rules

Each base must satisfy all of the following before it enters the run:

1. Exactly nine atomic hypotheses are mutually exclusive and jointly exhaustive **by explicit task stipulation**, not by an LLM's world knowledge.
2. `H1` is the target in every partition condition.
3. Atomic hypotheses are short, natural, and comparable in linguistic complexity.
4. No atomic label may semantically contain another.
5. No evidence sentence may mention the grouping or group labels.
6. The prompt must not imply that group membership is itself causal or diagnostic.
7. The target must be explicitly named after the partition display in every condition so target salience is not unique to `M2`.
8. The atom list appears in the same order before the grouping map in every condition.
9. No condition may omit or repeat an atom.
10. The same base text is reused byte-for-byte except for the partition map field.

A validation script must enforce atom identity/count/order and hash all non-partition fields.

---

## 5. Prompt skeleton

Primary E01 uses natural reasoning and does **not** tell the model that grouping is irrelevant; that recognition is tested later in E02.

```text
Consider this uncertain situation:
{scenario}

There are exactly nine mutually exclusive and exhaustive possibilities, listed in this order:
1. {H1}
2. {H2}
...
9. {H9}

For organization, they are shown in the following groups:
{partition_map}

Target proposition: {H1} is the true outcome.
{evidence_if_any}

What probability from 0% to 100% do you assign to the target proposition?
Think through the uncertainty normally, then end with: PROBABILITY: <number>%
```

`FLAT` omits only the grouping paragraph and is diagnostic, not a required primary contrast.

### E02 explicit-equivalence condition

If E01 survives, add before the probability query:

```text
The grouping above is only a display convention. It does not add, remove, or change any atomic possibility or any evidence.
```

This is not part of E01 because telling the model the answer to the representational question could erase the phenomenon we are trying to measure.

---

## 6. Evidence conditions

### E01 primary: weak-information condition

Use scenarios with little or no diagnostic evidence beyond the stated possibility space. The purpose is to maximize sensitivity to the hypothesized ignorance prior, matching the classic parent.

Do **not** treat `1/9` as gold solely because information is weak. The gold is cross-partition invariance.

### E02 mechanism: stronger-evidence attenuation subset

Only if E01 survives, preconstruct a stronger-evidence counterpart for 24 bases. The same evidence sentence appears in every partition condition for that base and is chosen so it clearly favors `H1` without deterministically identifying it.

The claim tested is relative:

> a partition-prior effect should be smaller when evidence about `H1` is stronger.

The absolute posterior is not scored against an author-invented numeric gold.

---

## 7. Readouts

### Primary readout

Parsed verbal probability in `[0,1]`.

Parsing rule is frozen before outputs:

1. Prefer the final `PROBABILITY: <number>%` pattern.
2. If absent, mark parse failure; do not search arbitrary numbers in the chain of thought.
3. Clamp is forbidden; values outside `[0,100]` are invalid.

### E02 readout robustness

If supported by the local inference stack, obtain a separate fixed binary readout:

```text
A = target proposition is true
B = target proposition is not true
```

Use the normalized first-token logit mass over the prevalidated single-token labels `A/B` (or another prevalidated two-token pair if tokenizer constraints require it). The partition effect is evaluated **relatively**; this is not claimed to be a calibrated probability.

A result confined to verbal numeric reporting is insufficient for the broad word **belief** and triggers re-selection.

---

## 8. Independent units and statistics

- Independent unit: **base scenario**, not prompt cell.
- All confidence intervals bootstrap base scenarios, preserving all matched partition cells within a resampled scenario.
- Report domain-stratified effects descriptively; domains are not independent replications by themselves.
- `M3a/M3b` belong to the same scenario and are never treated as independent samples.

Primary contrast:

`Delta_29 = P_M2(H1) - P_M9(H1)`

Additional preregistered quantities:

- `P_M3 = mean(P_M3a, P_M3b)`;
- monotonic signature: `P_M2 > P_M3 > P_M9`;
- partition spread: `max(P_M2,P_M3a,P_M3b,P_M9) - min(...)`;
- M3 regrouping sensitivity: `|P_M3a-P_M3b|`;
- signed ignorance pull relative to FLAT, exploratory/diagnostic: whether each `M` condition moves toward `1/M`.

No cell-level pseudo-replication.

---

## 9. Data leakage / provenance notes

Classic human items may be in model pretraining and are therefore anchors only. The primary clean grid uses new surface scenarios but tests a relation whose truth is independent of model output.

Construction may use scripts/templates for consistency, but **the model being evaluated must not generate or judge its own gold**. All 48 bases require human audit before the run.

Publication-scale claims must not rest solely on these 48 diagnostic bases. A positive pilot triggers re-selection and a fresh decision about natural/external validation; it does not automatically authorize synthetic scaling.

---

# Contract summary

The data contract is designed so that a positive effect cannot be explained by adding/removing alternatives, changing evidence, changing target identity, or using LLM-generated gold. What changes is the explicit **partition map over an otherwise identical state space**.