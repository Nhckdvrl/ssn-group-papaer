# L10 — Success Teaches, Failure Doesn't? Why Is Behavioral Inhibition Hard for LLMs?

**Status:** SERIOUS CANDIDATE / A-  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Canonical research package:** this directory  
**Last audited:** 2026-09-08

> **Plain-language thesis:** Current LLMs can quickly form a positive behavioral preference from experience, yet often fail to learn the symmetric lesson “do not do that again” from a failed experience.

---

## 1. One-sentence research question

> Why do LLMs adapt much more readily to **successful experience** than to **failed experience**—does the negative side break at outcome memory, credit assignment, policy formation, or behavioral inhibition?

Plain version:

> **Why can a model learn “use A again” after success, but still repeat B after B just failed?**

## 2. Established phenomenon

### ImplicitMemBench — ACL 2026

Qin et al. introduce a 300-item Learning/Priming–Interfere–Test benchmark over 17 models.

The paper reports a dramatic asymmetry:
- preference adaptation: **75.0%**;
- inhibition: **17.6%**.

Source:
- https://aclanthology.org/2026.acl-long.1301/

Therefore we do not need to discover that inhibition is weak.

### Natural interactive corroboration — EscapeBench

ACL 2025 EscapeBench categorizes **Useless Repetition**:
- model takes an action;
- environment replies “Nothing happens”;
- model immediately repeats the same failed action.

The paper reports this error across all tested models.

Source:
- https://aclanthology.org/2025.acl-long.39/

This supports ecological relevance beyond one memory benchmark.

## 3. Why ACL / NLP cares

Interactive LLM systems receive experience continuously:
- tool succeeds/fails;
- user accepts/rejects;
- environment gives feedback;
- actions cause outcomes.

A system that stores successful patterns but cannot convert failure into future inhibition will:
- repeat failed tool calls;
- reintroduce rejected behaviors;
- waste interaction budget;
- make memory systems look better on recall than on actual behavior.

The scientific object is the **experience → future action transformation**.

## 4. Competing accounts

### Account A — Negative outcome memory is weak

The model simply fails to retain:
> B failed.

Prediction:
- after interference/delay, explicit outcome recall is also poor.

### Account B — Credit assignment fails

The model remembers that the episode failed but cannot bind failure to the responsible action/choice.

Prediction:
- episode-level recall good;
- causal attribution to B poor;
- providing explicit attribution repairs future behavior.

### Account C — Policy knowledge exists but inhibition fails

The model can say:
> B failed; avoid B.

Yet its first real action still chooses B.

Prediction:
- explicit policy query correct;
- action behavior wrong;
- action/readout intervention or positive replacement framing repairs behavior.

### Account D — Negative specification itself is hard

The model struggles with “do not B” but handles an equivalent positive alternative:
> use A instead.

Prediction:
- recoding failure as positive replacement sharply improves behavior.

### Account E — Failure lessons decay faster

The model initially inhibits B but loses the lesson under interference/context growth faster than it loses positive preference.

Prediction:
- valence × delay/interference interaction.

## 5. Outcome robustness

Every account gives a publishable scientific result:

- memory bottleneck → fix retention;
- credit assignment → store cause, not just failure;
- inhibition bottleneck → memory is present but disconnected from behavior;
- negative-specification bottleneck → represent lessons as positive alternatives;
- decay asymmetry → memory consolidation/interference mechanism.

Even if modern models improve over ImplicitMemBench, a matched success-vs-failure decomposition remains informative.

## 6. Paper identity

**Primary identity:** behavioral adaptation mechanism / experience-to-action decomposition.

**Not the identity:**
- another agent memory benchmark;
- “LLMs repeat mistakes”;
- reflection prompting;
- self-evolving agents;
- negative instruction following;
- cognitive-science imitation.

## 7. Planned C1 → C2 → C3

### C1 — Locate the asymmetry
Match positive and negative experiences and measure:
1. outcome memory;
2. causal attribution;
3. policy knowledge;
4. actual first action.

### C2 — Mechanism / boundary
Cross:
- success vs failure;
- raw failure vs explicit attribution;
- “avoid B” vs “use A instead”;
- delay/interference;
- feedback strength;
- task type.

### C3 — Consequence
Determine what an LLM memory/experience system should store:
- outcome;
- causal attribution;
- prohibition;
- positive replacement action.

## 8. Five hard gates

| Gate | Verdict | Why |
|---|---|---|
| REAL OBJECT | **YES** | Repeated action after explicit failure is natural in interactive LLM use. |
| SCIENTIFIC TENSION | **YES** | Multiple stages can explain the positive/negative asymmetry. |
| GOOD DATA | **YES** | ImplicitMemBench establishes matched behavioral constructs; EscapeBench supplies natural trajectories. |
| PAPER-LEVEL NOVELTY | **YES, current audit** | Prior work measures failure learning/reflection or negative constraints, but not the matched success-vs-failure stage decomposition. |
| OUTCOME-ROBUST DECISIVENESS | **YES** | Every stage/boundary outcome changes how experience should be represented. |

## 9. Main danger

Reviewer compression:

> **“This is ImplicitMemBench plus mechanistic probing.”**

That attack wins if we only inspect hidden states or add another benchmark.

The paper survives only if it performs:
> **matched positive/negative experiences → stage-wise behavioral decomposition → targeted intervention that repairs the identified bottleneck → natural interactive validation.**

## 10. Directory map

- [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md)
- [DATA_AND_GOLD.md](DATA_AND_GOLD.md)
- [RESEARCH_PLAN.md](RESEARCH_PLAN.md)
