# 2026-09-14 — WALL-E Final Selection

**Wall:** WALL-E — developmental state / path dependence  
**Mode:** QUESTION SELECTION AFTER LINEAGE + DISAGREEMENT + OWNER AUDIT  
**New wall:** **FORBIDDEN / NONE CREATED**  
**Outcome:** one question survives selection and is registered as **L40 — The Unit of Learned Attention**.

> **Numbering correction:** an earlier edit accidentally called this question L39. `L39` was already occupied. The only valid candidate identity for this WALL-E result is **L40**. Any `L39_LEARNED_ATTENTION_UNIT` path is a tombstone only.

---

# 0. Final question

> **When prior language experience changes how readily a learner acquires a new morphological cue, is the persistent learning bias attached to morphology as a formal cue class, or to the particular grammatical function for which morphology was previously predictive?**

Short form:

> **What is the unit of learned attention: a form class, or a form–function relation?**

Canonical candidate:

- `candidates/L40_LEARNED_ATTENTION_UNIT/README.md`
- `candidates/L40_LEARNED_ATTENTION_UNIT/PILOT_CARD.md`

Status: **PILOT-AUTHORIZED — E01 ONLY**.

---

# 1. Why this survived WALL-E while broader versions died

The starting WALL-E problem was:

> Is current behavior/function a sufficient description of a learner for predicting what it will learn next, or can history leave a latent developmental state that only future learning reveals?

The following broader routes were explicitly killed before selection:

1. **Generic path dependence.** Old learning theory and modern neural theory already show that different histories can be hidden by current behavior and revealed by later learning. A Transformer replication is not enough.
2. **L34-style training-order effects.** Generic neural non-commutativity is not a Main-level scientific claim.
3. **Global critical-period / language-similarity story.** Constantinescu et al. (TACL 2025) already test this family and show ordinary experience alone does not reproduce the full human pattern.
4. **Blocking itself.** SLA learned-attention / Competition Model work has studied cue competition for decades.
5. **Second-order associability itself.** Associative-learning research already shows that cue history can change future learning of a new outcome.
6. **Item vs cue dimension.** Ellis-line SLA work already argues for transfer at the cue-dimension level.

The remaining unresolved quantity is therefore narrower and more theoretically diagnostic:

> **What is the granularity of the history-conditioned learning state in language: cue class, form–function relation, or no latent state beyond present cue use?**

---

# 2. Native theoretical disagreement

The question arises inside the learned-attention / usage-based SLA program itself.

### Cue-dimension reading

Classic learned-attention work often describes prior experience as creating persistent attention to a **cue dimension**, such as verbal morphology versus lexical/adverbial cues.

### Form–function reading

Usage-based/construction-learning theory treats linguistic knowledge as **form–function mappings**, making contingency between a form and the grammatical meaning it expresses load-bearing.

These descriptions are not equivalent.

If history changes morphology globally, predictive morphology for TENSE should facilitate later morphology for NUMBER.

If history changes a form–function relation, morphology-for-TENSE need not facilitate morphology-for-NUMBER.

---

# 3. Why the dispute is scientifically live

- **McManus et al., Language Learning 2026** closely replicate Ellis & Sagarra and recover the strong adverb-pretraining effect but not the corresponding morphology-pretraining effect, weakening a simple `cue dimension alone -> persistent attention` account.
- **Zhu et al., SSLA 2025** explicitly compare wholesale morphological transfer against feature-by-feature transfer across English-, German- and Mandarin-speaking learners, but natural L1 history cannot be randomized and language groups differ in other experience.
- **Oba et al. 2023; Hu et al. ACL 2025 Outstanding; Constantinescu et al. TACL 2025; Issam et al. 2026** establish that prior neural language history changes later acquisition, but do not identify the causal granularity of the latent future-learning state after current behavior is matched.

So the open scientific quantity is not whether transfer exists. It is **what state variable carries that transfer forward**.

---

# 4. Identifying experiment

Use two cue classes and two grammatical functions:

- `M` = bound morphology;
- `L` = free lexical/function cue;
- `T` = TENSE;
- `N` = NUMBER.

Randomized histories:

| history | TENSE predictive cue | NUMBER predictive cue |
|---|---|---|
| `MM` | morphology | morphology |
| `ML` | morphology | free cue |
| `LM` | free cue | morphology |
| `LL` | free cue | free cue |

The critical pair is `ML` vs `LM`: same total morphology exposure, same total lexical-cue exposure, same functions, same steps, same number of predictive relations; only the **form–function pairing** differs.

After history, all models receive the same common-language phase. That phase is calibrated using **current-state equivalence only**, never future challenge outcomes.

Before challenge, `ML` and `LM` must be equivalent on current TENSE/NUMBER competence, isolated cue use, cue-conflict preference, common-language loss, and initial challenge loss.

Then apply identical future updates with wholly novel markers/stems:

- `M -> T`;
- `M -> N`;
- `L -> T`;
- `L -> N`;
- unrelated new-relation control.

Primary quantity is early learning response, not saturated final accuracy.

---

# 5. Rival predictions

### A — cue-class-wide state

`MM` should acquire novel morphology faster than `LL` across both functions; `ML` vs `LM` should show little function-specific reversal once total predictive morphology is matched.

### B — form×function-specific state

The decisive crossover is:

```text
G(ML, M->T) > G(LM, M->T)
G(ML, M->N) < G(LM, M->N)
```

with the mirror pattern for free cues.

### C — present-state sufficiency

After current cue use is genuinely matched, history no longer predicts future learning.

This is a valid scientific null: the strong latent-associability reading of learned attention is unnecessary under the tested regime.

### D — generic plasticity

One history is simply easier to train across all branches, including the unrelated control, without the theory-specific crossover.

This **kills L40 under its linguistic identity**.

---

# 6. Reviewer-compression gate

L40 survives only if the paper remains about the **unit of the history-conditioned learning operator**.

It dies if compressed to any of:

- `Zhu et al. but with Transformers`;
- `psychology outcome specificity but with language tokens`;
- `prior training helps related future learning`;
- `different training order changes later accuracy`;
- `neural L2 transfer exists`.

The selected remainder is:

> **Randomize linguistic history, match present cue use, apply identical novel learning, and identify whether future learnability transfers at the cue-class level or the form–grammatical-function level.**

---

# 7. Selection verdict

| gate | verdict |
|---|---|
| durable question independent of one frontier paper | **PASS** |
| native theoretical disagreement | **PASS** |
| not generic path dependence | **PASS** |
| not L34 resurrection | **PASS** |
| mature rival accounts make opposite predictions | **PASS** |
| owner audit leaves a real estimand remainder | **PASS** |
| positive / opposite / null outcomes interpretable | **PASS** |
| controlled identification route | **PASS ON PAPER** |
| ACL/EMNLP/NAACL Main consequence | **PASS** |
| data/RAG/benchmark as intellectual center | **NO** |

**Decision: REGISTER L40.**

No new WALL is opened.