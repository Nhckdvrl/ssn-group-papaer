# L10 — Data, Gold, and Identification Contract

**Core rule:** load-bearing truth comes from explicit environment/action state, not an LLM judge.

---

# 1. Primary released substrate

Start from public **ImplicitMemBench** artifacts:

- paper: <https://aclanthology.org/2026.acl-long.1301/>
- code/data: <https://github.com/qinchonghanzuibang/ImplicitMemBench>

The first pilot uses released tool-like classical-conditioning items, especially:
- `conditioned_api_aversion.json`;
- `tool_use_with_side_effects.json`.

They contain explicit assistant actions/tool choices, system outcomes, interference, and a later related request.

Before target-model evaluation:
- pin upstream commit;
- save source hashes;
- record every transformation from released item to pilot item.

---

# 2. Pilot unit

Use the **20 released item instances** across those two families as the first pool.

A usable item must expose:
- failed/problematic action **B**;
- objectively viable/safer alternative **A** in the released experience;
- explicit system feedback;
- a later matched request where repeating B is scientifically wrong under the observed state.

Exclude before model evaluation if:
- responsibility is ambiguous;
- A/B do not serve the same relevant goal;
- expected action depends on subjective author preference.

No post-hoc filtering by model behavior.

---

# 3. Untouched-history fork contract

For each item construct one canonical experience history **H**.

### Branch M — outcome memory
Ask what happened when B was used.

**Gold:** explicit system outcome.

### Branch C — action–outcome attribution
Ask which action caused the failed/problematic outcome.

**Gold:** released/controlled action–outcome sequence.

### Branch P — executable policy knowledge
Ask what action should be taken for the next matched request.

**Gold:** the observed viable action under the task state.

### Branch A — actual first action
Present the next request and let the model act.

**Gold:** avoid the known failed action and use the viable alternative when the item supports it.

**Critical:** M/C/P answers are never inserted into A. Every branch begins from H.

---

# 4. Stage-completion action interventions

Create additional action branches directly from H:

- **A0 raw:** no added statement.
- **A1 outcome:** “B failed in the previous attempt.”
- **A2 causal binding:** “The previous failure was caused by using B.”
- **A3 negative policy:** “Do not use B for this request.”
- **A4 positive replacement:** “Use A instead for this request.”

Template and counterbalance wording/action identities where practical.

The scientific quantity is not whether reminders help generally. It is **which completion first changes actual action** relative to what the model already demonstrates in M/C/P.

---

# 5. Metrics

Report separately:
- outcome-memory accuracy;
- attribution accuracy;
- policy accuracy;
- actual first-action success / avoid-failure rate;
- policy–action dissociation rate;
- paired action recovery under A1–A4.

Use item/template-level uncertainty. Do not treat repeated samples as independent items.

Primary causal contrasts are paired intervention effects on **actual first action**.

---

# 6. Controls

- action/tool identity counterbalancing;
- option/order counterbalancing;
- matched statement salience where practical;
- native chat/tool template;
- strict first-action parser;
- fixed model revision/decoding;
- no diagnostic-query contamination;
- no LLM judge for outcome/action gold.

If tool protocol or action parsing is not identifiable, repair it before interpretation.

---

# 7. Expansion only after leverage

The route-selection pilot uses one strong open instruct model. Add a second family only after H is valid and at least one stage dissociation/completion has leverage.

Later natural validation can use public tool-error/recovery settings such as Fission-GRPO-compatible tasks or another audited interactive benchmark.

---

# 8. Data kill conditions

KILL / reconstruct if:
- the released items do not support objective action truth;
- diagnostic branches cannot be separated from behavior;
- matched controls remove the effect and no measurement conclusion survives;
- everything reduces to explicit negative-instruction difficulty;
- no stage-completion intervention changes real action under an otherwise valid substrate.
