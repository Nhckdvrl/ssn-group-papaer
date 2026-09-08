# Success–Failure Asymmetry — Minimum Decisive Pilot

## Pilot question

> In matched positive and negative experience, where does the pathway from experience to future action first diverge?

## 1. Minimal data

Start with a controlled subset of ImplicitMemBench emphasizing preference/inhibition pairs with clean action-outcome structure.

Target 100–200 paired cases if available; otherwise use the entire clean paired subset.

## 2. Models

Two strong open models from different families are enough for the first pilot. Prefer one model with strong preference adaptation but weak inhibition, matching the parent result.

## 3. Four-stage protocol

For each experience pair:
1. expose model to success or failure;
2. add matched interference;
3. in separate diagnostic branches, measure:
   - outcome memory;
   - causal attribution;
   - policy knowledge;
4. in a clean branch without preceding diagnostics, score actual first action.

Use separate conversations/rollouts so diagnostics do not teach the answer before the behavioral test.

## 4. Primary comparison

At each stage compute:

`positive success rate - negative success rate`

and identify the earliest stage where a reliable gap appears.

Then estimate conditional transition rates:
- P(attribution correct | outcome remembered);
- P(policy correct | attribution correct);
- P(action correct | policy known).

## 5. Causal repair

Choose intervention based on the identified bottleneck:

### If encoding/retention fails
Store/restate outcome compactly after experience.

### If attribution fails
Provide a causal binding between failed action and outcome without prescribing the future action.

### If policy formation fails
Provide a derived policy.

### If action inhibition fails
Compare:
- “do not B”;
- “use A instead”;
- equivalent positive replacement.

The strongest evidence is selective repair of Stage 4 without changing irrelevant cases.

## 6. Outcome branches

### A — Knowledge–action gap
Strong Main route: model explicitly knows failure/cause/policy but behavior repeats. Investigate action-selection/readout mechanism and replacement intervention.

### B — Credit-assignment gap
Strong route if failure memory is intact but action-cause binding breaks under negative experience.

### C — Encoding/retention gap
Still viable if robust and asymmetric after matched controls; connect to implicit vs explicit memory.

### D — Positive replacement fully repairs
Potentially strong conclusion: LLMs encode failure but struggle to implement suppressive policies; memory systems should store replacement actions rather than prohibitions.

### E — Asymmetry vanishes under matched controls
KILL or substantially revise. This would imply the benchmark-level gap was due to task/feedback asymmetry rather than a general mechanism.

## 7. Natural replication

Only after controlled pilot survives, test the diagnosed mechanism on EscapeBench-like interactions with explicit failure feedback and repeated opportunities.

## 8. Promotion condition

Promote only if the pilot locates a stable bottleneck and an intervention selectively changes future behavior.

Do not promote a result consisting only of:
- preference 75 vs inhibition 18 replication;
- explicit recall correlations;
- linear probes with no behavioral consequence.