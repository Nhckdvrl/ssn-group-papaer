# L10 — Related Work and Paper-Level Novelty

**Freshness:** 2026-09-09  
**Novelty standard:** full paper identity.

---

# 1. ImplicitMemBench — direct parent

Qin et al., ACL 2026  
<https://aclanthology.org/2026.acl-long.1301/>

Owns:
- implicit behavioral adaptation evaluation;
- Learning/Priming–Interfere–Test;
- first-attempt scoring;
- 300 items / 17 models;
- inhibition 17.6% vs preference 75.0%.

L10 cannot claim inhibition is weak, failure adaptation is under-evaluated, or first-action behavior is new.

It does **not** localize where an experienced failure stops becoming changed action.

---

# 2. Fission-GRPO — natural tool-error corroboration

Zhang et al., ACL 2026  
<https://aclanthology.org/2026.acl-long.1880/>

Owns:
- repeated invalid tool calls after execution errors;
- converting errors into on-policy corrective supervision.

It does not own a frozen/in-context decomposition of:
> outcome retention → causal attribution → policy formation → actual action.

---

# 3. Failure-learning / memory methods

### Mistake Notebook Learning — Findings of ACL 2026
<https://aclanthology.org/2026.findings-acl.719/>

Builds structured mistake notes from clustered failures for training-free adaptation.

### BenchTrace — 2026
Studies failure diagnosis/reflection and whether experience becomes avoidance.

### Training Language Agents to Learn from Experience — 2026
Trains reflector models to extract reusable lessons.

These works own important **ways to make failure useful**. They do not identify which conversion stage is missing in the original model.

---

# 4. Explicit negative-constraint neighbor

**Semantic Gravity Wells: Why Negative Constraints Backfire** studies explicit “do not X” instructions and mechanistic failure modes.

This becomes fatal only if L10 collapses to prohibition following.

L10 begins earlier:
> action happened → environment returned a negative outcome → model must convert that experience into future behavior.

“Do not B” vs “use A” is a boundary/control, not the paper identity.

---

# 5. What can still be ours

The paper must own:

1. externally established failure/inhibition gap;
2. one fixed experience history;
3. independent forks for outcome memory, attribution, policy, and action;
4. matched completion of candidate stages;
5. causal change in actual action;
6. natural interactive validation;
7. implication for what experience memory must represent.

No located paper owns this full chain.

---

# 6. Reviewer compression

### “ImplicitMemBench + probes”
Wins if we only ask diagnostics or decode hidden states.

### “BenchTrace with a positive control”
Wins if the paper becomes another failure-diagnosis benchmark.

### “Fission-GRPO without training”
Wins if we only show repeated calls and a prompting fix.

### “Semantic Gravity Wells in agents”
Wins if the mechanism is only explicit negative language.

The defense is the **untouched-history causal stage-completion design**, not wording.

---

# 7. Why-space verdict

**PASS.**

After the failure-memory/reflection/corrective-training ecosystem is laid out, the natural question remains broad:

> **Why does available failure experience fail to become changed action, and which transformation is missing?**

Refresh before mainline promotion and whenever the load-bearing explanation changes.
