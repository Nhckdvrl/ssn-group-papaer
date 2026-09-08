# Success Teaches, Failure Doesn't? Why Is Behavioral Inhibition Hard for LLMs?

**Status:** SERIOUS CANDIDATE / A-  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Last audited:** 2026-09-08

> **Plain-language thesis:** LLMs readily learn “do this again” from successful experience but often fail to learn “don’t do this again” from failure. The scientific question is where that asymmetry enters the experience-to-action pipeline.

## 1. One-sentence RQ

> **Why can LLMs quickly form behavioral preferences from successful experience, yet struggle to turn failed experience into future action inhibition?**

## 2. Established phenomenon

ACL 2026 ImplicitMemBench evaluates 17 models and reports a dramatic asymmetry:
- preference adaptation: 75.0%;
- inhibition: 17.6%.

Source: https://aclanthology.org/2026.acl-long.1301/

ACL 2025 EscapeBench independently observes repeated ineffective actions even after explicit environment feedback that nothing happened.

Therefore the project does not depend on discovering failure-learning weakness.

## 3. Natural scientific tension

A failed action can fail to influence later behavior for multiple reasons:

### Account A — Outcome encoding / retention failure
The model does not reliably retain that action B failed.

### Account B — Causal/credit-assignment failure
The model remembers the failure but does not bind it to the responsible action/parameter/context.

### Account C — Knowledge–action gap
The model can state “B failed; avoid B” yet still chooses B when acting.

### Account D — Suppression-format bottleneck
Models have difficulty implementing negative policies (“do not B”) but can use a positively specified replacement (“use A instead”).

These accounts have different interventions and practical consequences.

## 4. Why ACL / NLP cares

Interactive LLMs increasingly learn from user/environment experience without retraining. If negative experience does not automatically guide future behavior, memory quality cannot be assessed by explicit recall alone.

The paper asks what information has to be stored after failure:
- outcome;
- causal explanation;
- explicit prohibition;
- or replacement action.

This matters for personalization, memory systems, dialogue agents, and tool-using systems without becoming a generic agent-method paper.

## 5. Outcome robustness

- failure itself forgotten -> encoding/retention bottleneck;
- failure remembered, cause wrong -> credit assignment;
- cause/policy stated correctly, action repeats -> knowledge–action inhibition gap;
- positive replacement repairs behavior -> negative-specification bottleneck;
- delay/interference boundary -> memory consolidation boundary.

All major outcomes support a scientific story.

## 6. Paper identity

**Primary identity:** mechanism of asymmetric experiential behavioral adaptation.

**Not:**
- another memory benchmark;
- another reflection agent;
- “LLMs cannot learn from feedback”;
- generic negative prompting;
- a method for agent self-improvement.

## 7. C1 → C2 → C3

### C1
Establish matched positive-vs-negative experiential adaptation under equivalent information/action structure.

### C2
Decompose experience→behavior into:
`outcome memory -> causal attribution -> policy knowledge -> actual first action`.

### C3
Intervene at the identified bottleneck and determine the minimal representation of failure that produces reliable future avoidance.

## 8. Five gates

| Gate | Verdict | Why |
|---|---|---|
| REAL OBJECT | **YES** | The asymmetry is established across many models and interactive tasks. |
| SCIENTIFIC TENSION | **YES** | Four plausible mechanisms make distinct predictions. |
| GOOD DATA | **YES** | ImplicitMemBench provides controlled experiences/outcomes; environment feedback is direct. |
| NOVELTY | **PROVISIONAL YES** | Parent benchmark establishes asymmetry but does not stage-wise causally explain it. |
| OUTCOME ROBUST | **YES** | Every bottleneck location yields a useful conclusion/intervention. |

## 9. Main danger

> **“This is just ImplicitMemBench + mechanistic probing.”**

Fatal if the work ends at recall/probe correlations. It must perform stage-wise behavioral interventions that selectively repair the discovered bottleneck.

## 10. Directory map
- `DATA_AND_GOLD.md`
- `RELATED_WORK_AND_NOVELTY.md`
- `PILOT_CARD.md`
