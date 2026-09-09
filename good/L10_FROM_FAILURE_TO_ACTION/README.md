# L10 — From Failure to Action

## Failure Is Remembered, But Why Isn't It Avoided?

**Status:** **A / PILOT-AUTHORIZED / Rank 1**  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Canonical research package:** this directory  
**Last audited:** 2026-09-09

> **Natural question:** Why can an LLM know that an action failed, know what it should do instead, and still repeat the failed action?

The scientific object is:

> **experienced outcome → action–outcome attribution → executable policy → future action**

---

# 1. Established phenomenon

ACL 2026 **ImplicitMemBench** evaluates 17 models with public artifacts and reports:
- preference adaptation: about **75.0%**;
- inhibition: about **17.6%**.

ACL 2026 **Fission-GRPO** independently reports repetitive invalid tool calls after execution errors.

L10 therefore does not need to discover that models sometimes repeat failures.

---

# 2. Core RQ

> **Where does failure experience stop becoming future action?**

### Stage 1 — Outcome retention
The model does not retain: **B failed**.

### Stage 2 — Action–outcome attribution
It remembers failure but does not bind it to B.

### Stage 3 — Executable policy formation
It knows B failed but does not form: **use A next time**.

### Stage 4 — Behavioral inhibition
It can explicitly state **B failed; use A next**, but its actual first action is B again.

Negative-language difficulty (“do not B”) is a boundary/control, not a pre-committed explanation.

---

# 3. Identification: untouched-history forks

For one experience history **H**, create independent branches:

- **M:** outcome-memory query;
- **C:** causal-attribution query;
- **P:** policy query;
- **A:** actual next action.

**Never feed M/C/P responses into A.**

Then create separate action branches from H with one matched completion:
- outcome reminder;
- causal binding;
- “do not B”;
- “use A instead.”

This turns the decomposition into a causal test rather than a questionnaire.

---

# 4. Paper identity

> **Established failure/inhibition gap**  
> → **where experience→action conversion breaks**  
> → **matched stage completion/repair**  
> → **natural interactive validation**  
> → **what an agent memory must store to actually change behavior**

Not the identity:
- ImplicitMemBench + probes;
- another reflection/memory benchmark;
- “LLMs repeat mistakes”;
- a new memory architecture;
- explicit negative-instruction following.

---

# 5. Why-space

Nearby work mainly asks:
> **How can failure be made useful?**

Corrective RL, reflection, mistake notebooks, negative-experience replay, and learned reflectors show that failure contains usable information.

They do not yet own:
> **when the same failure experience is already in context, which transformation from event to future action is missing?**

The RQ remains natural without naming a layer, metric, or interpretability method.

---

# 6. Outcome robustness

Any stable bottleneck is informative:
- Stage 1 → retention/consolidation;
- Stage 2 → credit assignment / causal binding;
- Stage 3 → fact-to-policy conversion;
- Stage 4 → knowledge/action dissociation;
- positive replacement beats prohibition → negative-specification boundary;
- matched controls erase the parent asymmetry → measurement/construct reassessment.

Hypothesis loss does not kill the RQ.

---

# 7. Current gates

| Gate | Verdict |
|---|---|
| Natural / important | **PASS++** |
| Scientific tension | **PASS++** |
| Data / identification | **PASS** |
| Paper-level novelty | **PASS** |
| Outcome robustness | **PASS++** |
| Main-level calibration | **PASS++** |
| Anomaly robustness | **PASS++** |
| Why-space / narrative-space | **PASS++** |

# 8. Immediate work

Run **L10-E01** exactly as defined in [PILOT_CARD.md](PILOT_CARD.md). Do not start with a model zoo or hidden-state probes.

See:
- [DATA_AND_GOLD.md](DATA_AND_GOLD.md)
- [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md)
- [RESEARCH_PLAN.md](RESEARCH_PLAN.md)
- [PILOT_CARD.md](PILOT_CARD.md)
