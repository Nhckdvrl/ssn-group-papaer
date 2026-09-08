# Success–Failure Asymmetry — Data and Gold

## 1. Load-bearing quantities

No proxy label is needed. The experiment directly observes:
- which action was taken;
- whether the environment marked it successful/failed;
- whether the model later recalls that outcome;
- whether it attributes the outcome to the right action;
- what policy it states;
- what first action it actually takes later.

## 2. Primary substrate — ImplicitMemBench

ACL 2026 ImplicitMemBench provides a Learning/Priming–Interfere–Test protocol with first-attempt scoring and explicitly measures behavioral adaptation after prior experience.

Key established result:
- inhibition 17.6%;
- preference 75.0%.

Source: https://aclanthology.org/2026.acl-long.1301/

This is ideal for the first causal decomposition because the experience and outcome are externally controlled.

## 3. Natural replication

Use an interactive environment such as EscapeBench or another released task with explicit environment feedback and repeated action opportunities.

Natural example:
`click X -> environment says Nothing happens -> later opportunity -> click X again`

The replication is not the primary gold; it tests whether the mechanism transfers beyond the controlled benchmark.

## 4. Matched positive/negative design

Construct pairs where information structure is as symmetric as possible:

### Positive experience
`choose A -> success`
Later choose between A/B.

### Negative experience
`choose B -> failure`
Later choose between A/B.

Match:
- action salience;
- number of exposures;
- delay/interference;
- alternatives;
- outcome wording/informativeness.

Do not confound “negative experience” with longer or more ambiguous feedback.

## 5. Stage-wise diagnostic outputs

After experience and interference, independently query:

### Stage 1 — Outcome memory
“What happened when action B was tried?”

### Stage 2 — Causal attribution
“Which action/choice caused the failure?”

### Stage 3 — Policy knowledge
“What should you do/avoid next time?”

### Stage 4 — Actual behavior
Give the natural task again and score the **first action**, without reminding the model of its stated policy.

The separation is crucial: explicit answers are diagnostics, not substitutes for actual behavior.

## 6. Intervention conditions

- RAW FAILURE: preserve original environment feedback only;
- EXPLICIT NEGATIVE: “Do not use B”;
- POSITIVE REPLACEMENT: “Use A instead”;
- CAUSAL LESSON: “B failed because X; use A under this condition”;
- OUTCOME ONLY: “B failed” with no policy;
- DELAY/INTERFERENCE levels.

## 7. Primary metrics

- positive adaptation first-action rate;
- negative inhibition first-action rate;
- Stage 1–4 accuracy;
- transition failure rates between consecutive stages;
- effect of each intervention on actual behavior;
- delay/interference decay;
- transfer to related but non-identical contexts.

## 8. Identification logic

### Encoding failure
Low Stage 1 negative recall relative to positive.

### Credit-assignment failure
Stage 1 correct, Stage 2 poor.

### Policy formation failure
Stages 1–2 correct, Stage 3 poor.

### Knowledge–action gap
Stages 1–3 correct, Stage 4 poor.

### Negative-specification bottleneck
Explicit negative remains weak, positive replacement repairs Stage 4.

## 9. Data-validity kill conditions

KILL/demote if:
- positive and negative conditions are not information-matched;
- failure feedback is ambiguous about the responsible action;
- explicit diagnostic questions themselves alter the later behavioral test without clean separation;
- the asymmetry disappears under basic matched controls;
- results are entirely explained by one benchmark's wording/template;
- natural replication provides no evidence the mechanism transfers.
