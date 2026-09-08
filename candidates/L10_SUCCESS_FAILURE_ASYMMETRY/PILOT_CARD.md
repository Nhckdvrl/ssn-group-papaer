# L10 — Minimum Decisive Pilot Card

**Candidate:** Success Teaches, Failure Doesn't?  
**Status:** SERIOUS / A-  
**Goal:** Locate where success/failure experience becomes behaviorally asymmetric.

## Established phenomenon
ACL 2026 ImplicitMemBench reports a large preference-vs-inhibition gap (about 75.0% vs 17.6%). EscapeBench supplies natural examples of repeating actions after explicit failure.

We do **not** need to rediscover “models repeat mistakes.”

## Matched pilot design
Build/adapt **100–200 matched positive/negative experience pairs**.

For each item hold fixed:
- task;
- options/actions;
- context length;
- interference;
- feedback strength;
- lexical framing as much as possible.

Counterbalance which action succeeds or fails.

## Four-stage funnel
After experience + interference, evaluate separately:

1. **Outcome memory**  
   Did A/B succeed or fail?

2. **Causal attribution**  
   Which action/choice caused the outcome?

3. **Policy knowledge**  
   What should be done next / what should be avoided?

4. **Actual first action**  
   What does the model really choose when acting?

The first stage where positive and negative trajectories diverge is the primary scientific quantity.

## Conditions
- successful experience;
- failed experience;
- failed experience + explicit causal attribution;
- “avoid B” representation;
- semantically equivalent “use A instead” representation;
- multiple interference lengths.

Use at least two open model families.

## Informative outcomes
### A — Memory bottleneck
Negative outcome recall is already weak.

### B — Credit assignment bottleneck
Failure remembered, responsible action misidentified.

### C — Inhibition bottleneck
Memory + attribution + policy knowledge correct, but actual action repeats B.

### D — Negative-specification bottleneck
“Use A instead” repairs behavior while “avoid B” fails.

### E — Retention asymmetry
Negative lessons decay faster under interference.

### F — Matched controls remove the gap
Then ImplicitMemBench's headline asymmetry may partly reflect task construction; this can support a measurement-reassessment route if broad and decisive.

## Phase 2 — Targeted repair
Apply the smallest intervention at the identified bottleneck:
- structured failure memory;
- causal-attribution record;
- positive replacement;
- explicit policy state;
- action/readout intervention only if warranted.

Strong result:
> repair failure learning selectively without degrading success learning.

## Natural validation
Replicate the diagnosed bottleneck on EscapeBench useless-repetition trajectories.

## Kill conditions
Kill if:
- matched controls remove the asymmetry and no broader measurement conclusion survives;
- results reduce entirely to known explicit negative-instruction effects;
- stage labels require subjective annotation;
- intervention cannot causally move actual behavior;
- natural interactive validation does not transfer.
