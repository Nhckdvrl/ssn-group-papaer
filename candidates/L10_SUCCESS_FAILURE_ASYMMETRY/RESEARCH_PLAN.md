# L10 — Research Plan

**Candidate:** Success Teaches, Failure Doesn't?

---

## 1. Minimum decisive pilot

### Pilot set
Build or adapt ~100–200 matched positive/negative experience pairs.

Keep:
- same task structure;
- same options;
- same interference;
- same feedback strength.

Counterbalance which option succeeds/fails.

### Models
Two open model families.

### Required outputs
For every item:
1. outcome recall;
2. causal attribution;
3. policy knowledge;
4. actual first action.

### Primary plot
A four-stage funnel for:
- positive experience;
- negative experience.

Question:
> at which transition does the gap first appear?

## 2. Pilot outcome routes

### Route A — Memory gap
Negative outcome recall already weak.

Next:
- retention/interference curve;
- memory encoding analysis.

### Route B — Attribution gap
Outcome remembered, responsible action not identified.

Next:
- attribution hints;
- ambiguity controls;
- credit-assignment analysis.

### Route C — Inhibition gap
Memory + attribution + policy knowledge correct, action still repeats failure.

Next:
- positive replacement;
- logit/readout inspection;
- action-selection intervention.

### Route D — Negative-language gap
“Use A instead” fixes behavior while “don’t use B” fails.

Next:
- distinguish experiential learning from explicit negative-constraint mechanism.

### Route E — No matched asymmetry
If properly matched success/failure are similar:
> ImplicitMemBench headline asymmetry may be driven by task construction rather than a general valence mechanism.

This is scientifically useful but may require a measurement-reassessment framing.

## 3. Phase 2 — Interference and retention

Vary:
- 0;
- short;
- medium;
- long interference.

Measure whether:
> negative lessons decay faster than positive preferences.

Keep token count and topic controlled.

## 4. Phase 3 — Causal repair

For the identified bottleneck, apply the smallest intervention.

Examples:
- attribution sentence;
- structured failure record;
- positive replacement memory;
- explicit policy state;
- action logit/readout steering if warranted.

Strong result:
> selectively repair failure learning while leaving success learning unchanged.

## 5. Phase 4 — Natural interactive replication

Use EscapeBench trajectories.

Identify episodes:
- action fails unambiguously;
- same action is available again;
- model repeats or avoids it.

Before the next action, query the four stages where possible.

Ask:
> does the controlled bottleneck predict natural useless repetition?

This prevents the paper from remaining a toy memory experiment.

## 6. Planned C1 → C2 → C3

### C1
Where does success/failure learning become asymmetric?

### C2
Is the bottleneck memory, credit assignment, policy formation, inhibition, or retention?

### C3
How should LLM systems represent failed experience so it changes future behavior?

## 7. Kill conditions

KILL if:
- matched controls eliminate the asymmetry across models and there is no broader measurement conclusion;
- the result is fully explained by known explicit negative-constraint priming with no experiential component;
- stage labels require subjective annotation;
- intervention cannot causally move behavior;
- natural interactive replication does not transfer.

## 8. Main-level requirements

Before mainline approval:
- matched positive/negative design;
- ≥2 model families;
- stage-wise decomposition;
- at least one causal repair;
- interference/boundary analysis;
- one natural interactive validation;
- novelty re-audit against new self-evolving-agent work.

## 9. Paper skeleton

1. Established success/failure asymmetry.
2. Four-stage behavioral pipeline.
3. Matched positive/negative experiment.
4. Locate the divergence.
5. Targeted repair.
6. Interference/boundaries.
7. EscapeBench natural validation.
8. Implication for memory representation.

## Final pilot verdict

**SERIOUS / PILOT-WORTHY after exact dataset/code availability check.**
