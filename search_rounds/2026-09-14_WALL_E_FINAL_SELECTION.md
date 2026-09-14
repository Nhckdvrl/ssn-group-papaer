# 2026-09-14 — WALL-E Final Selection

**Wall:** WALL-E — developmental state / path dependence  
**Mode:** QUESTION SELECTION AFTER LINEAGE + DISAGREEMENT + OWNER AUDIT  
**New wall:** **FORBIDDEN / NONE CREATED**  
**Outcome:** one question survives selection and may enter the L-series; all broader WALL-E formulations remain closed as candidate generators.

---

# 0. Decision

After pushing WALL-E through old learning theory, metaplasticity/plasticity, critical-period theory, SLA learned-attention work, 2025–2026 LM language-acquisition work, recent replication disputes, crosslinguistic-transfer work, and direct owner search, one paper-sized question survives:

> **When prior language experience changes how readily a learner acquires a new morphological cue, is the persistent learning bias attached to morphology as a formal cue class, or to the particular grammatical function for which morphology was previously predictive?**

Short form:

> **What is the unit of learned attention: a form class, or a form–function relation?**

This question is registered separately as **L39 — The Unit of Learned Attention**.

No other WALL is opened.

---

# 1. How WALL-E was compressed to this question

The starting WALL-E problem was deliberately broad:

> Is current behavior/function a sufficient description of a learner for predicting what it will learn next, or can history leave a latent developmental state that only future learning reveals?

Several tempting descendants were killed before selection.

## Killed branch A — generic path dependence

`different history -> same current behavior -> different future learning` is not a fresh NLP claim. Classical learning theory already treats path dependence this way, and Ger & Barak (2026) give a modern neural-theory instance in which functionally invisible state records training history and is exposed by subsequent learning.

Therefore a Transformer/NLP demonstration of the bare phenomenon would be `old result × new model`.

## Killed branch B — L34-style training order / prospective encoding

The L34 post-mortem already established that generic non-commutativity of neural training order is insufficient. WALL-E cannot revive `access -> document` vs `document -> access`, NEW/OLD subtraction, arbitrary curricula, or relation-specific transfer.

## Killed branch C — global critical-period / language-similarity story

Constantinescu et al. (TACL 2025) already test whether delayed L2 exposure and L1–L2 similarity generate human-like critical-period effects in neural LMs. Ordinary training does not reproduce the full human pattern; explicit plasticity reduction via EWC does much better. Coarse `language similarity determines entrenchment` is therefore already tested and empirically inadequate.

## Killed branch D — selective blocking as a new phenomenon

Ellis, Sagarra, MacWhinney and the wider Competition Model / learned-attention literature have studied cue competition and blocking in adult L2 learning for decades. Reproducing `an old cue blocks a later cue` in a Transformer would add little.

## Killed branch E — second-order associability itself

General associative-learning work already demonstrates that cue history can alter future learning of a *new* outcome, rather than merely current response. Beesley & Le Pelley (2011) provide a particularly clean Stage-3 test: a previously blocked cue later acquires a novel outcome more slowly than a matched control cue.

Thus `blocking changes future learnability` is also not the novelty.

## Killed branch F — item vs cue dimension

Ellis-line SLA work explicitly claims generalization at the level of cue dimensions rather than individual lexical items; later work extends learned attention to new/future temporal cues. The item-vs-morphology-class contrast is therefore not open enough.

---

# 2. The native theoretical disagreement that remains

The surviving question does not come from combining two unrelated literatures. It appears **inside the learned-attention / usage-based SLA program itself**.

### Cue-dimension reading

The learned-attention literature often describes prior experience as creating persistent attention to a **cue dimension** — for example, lexical/adverbial cues versus verbal morphology. Long-term L1 effects are interpreted as a processing bias that affects subsequent learning of morphological cues.

Representative sources:

- Ellis (2006), *Selective Attention and Transfer Phenomena in L2 Acquisition*  
  https://doi.org/10.1093/applin/aml015
- Ellis & Sagarra (2010/2011), learned attention / blocking in temporal reference  
  https://doi.org/10.1111/j.1467-9922.2010.00602.x  
  https://doi.org/10.1017/S0272263111000325
- Ellis et al. (2014), eye-tracking study of learned attention  
  https://doi.org/10.1017/S0142716412000501

### Form–function reading

The same broader usage-based theory says that linguistic knowledge is learned as **constructions / form–function mappings**, and that contingency between a form and its meaning is load-bearing. A persistent learning bias may therefore be tied not to `morphology` globally, but to *morphology used for a particular grammatical function*.

Representative source:

- Ellis (2022), *Second language learning of morphology*  
  https://doi.org/10.22599/jesla.85

### Associative-learning constraint

The general theory that learned-attention accounts invoke does not guarantee a global cue salience. Learned-predictiveness work has shown that transfer can depend on the outcome/outcome class, and later work distinguishes learning-rate effects from performance/integration effects.

Representative sources:

- Le Pelley et al. — outcome specificity / learned predictiveness literature
- Beesley & Le Pelley (2011), blocking changes later associability
- Don et al. (2009), learned predictiveness can affect both learning and performance

The result is a real theory-level ambiguity:

> **When language history makes morphology easier or harder to learn, what exactly has become easier or harder to learn?**

A formal dimension? Or a relation between that formal dimension and a grammatical function?

---

# 3. Why this ambiguity is now scientifically live

## 3.1 A flagship blocking effect is no longer stable under close replication

McManus et al. (Language Learning 2026), *Revisiting Blocking Effects in Second Language Learning: A Close Replication of Ellis and Sagarra (2010b)*, reproduce the strong adverb-pretraining effect but do **not** find the corresponding verb/morphology-pretraining effect. They argue that pretraining on a cue dimension alone is insufficient; cue linguistic properties, prior experience, and cue competition matter.

Source:

- https://doi.org/10.1111/lang.70005

This directly weakens the strongest `dimension alone -> persistent attention to that dimension` reading.

## 3.2 Current cross-L1 evidence cannot identify the state variable

Zhu et al. (SSLA 2025), *Learning morphology from cross-situational statistics*, explicitly contrast **wholesale morphological transfer** with **feature-by-feature transfer** using tense, number and agreement morphology in English-, German- and Mandarin-speaking learners.

Source:

- https://doi.org/10.1017/S027226312510106X

Their results are informative but not causally identifying for WALL-E:

- L1 is not randomized;
- German and Mandarin groups broadly have additional-language experience while many English participants are monolingual;
- the authors note that the study cannot categorically determine whether the artificial markers were represented as inflections rather than adverb-like indicators;
- participant groups differ in multiple demographic / language-history variables.

Thus the study asks an adjacent theoretical question but cannot say **which latent learning state a controlled history installed**.

## 3.3 Neural-LM L2/CLI work establishes transfer but not its unit

Relevant NLP work now makes prior language history a serious causal object:

- Oba et al. (Findings ACL 2023), *Second Language Acquisition of Neural Language Models*  
  https://aclanthology.org/2023.findings-acl.856/
- Hu et al. (ACL 2025 Outstanding), *Between Circuits and Chomsky*  
  https://aclanthology.org/2025.acl-long.478/
- Constantinescu et al. (TACL 2025), critical-period experiments  
  https://aclanthology.org/2025.tacl-1.5/
- Issam et al. (2026), controlled LM crosslinguistic influence  
  https://arxiv.org/abs/2601.21587

These works establish that prior training, structural relation, timing/dominance, and reusable circuitry affect later language learning. None of the closest work found in the audit uses a controlled **same-current-state -> identical-new-update** design to distinguish cue-class-wide from grammatical-function-specific future learnability.

---

# 4. The decisive experiment — designed before seeing the sign

The experiment must instantiate the classical WALL-E logic:

> randomized history -> matched current observable state -> identical future treatment -> divergent / non-divergent learning

while also making the two linguistic theories disagree.

## 4.1 Two cue classes and two grammatical functions

Use a small, controlled semi-artificial language with:

- cue classes: **bound morphology (M)** and a **free lexical/function cue (L)**;
- grammatical functions: **TENSE (T)** and **NUMBER (N)**.

The semantic contrasts, cue frequencies, cue entropy, surface frequency, stem inventory, number of predictive events, optimization steps and target-token exposure must be balanced/counterbalanced.

The stimuli should be adapted from established artificial/semi-artificial language paradigms rather than sold as a new benchmark.

## 4.2 Randomized history phase

Four histories provide a factorial decomposition:

| history | TENSE predictive cue | NUMBER predictive cue |
|---|---|---|
| `MM` | morphology | morphology |
| `ML` | morphology | lexical/free cue |
| `LM` | lexical/free cue | morphology |
| `LL` | lexical/free cue | lexical/free cue |

Non-predictive cue types remain present at matched frequency, so `predictive history` rather than raw token exposure is manipulated.

The strongest comparison is **ML vs LM**: they have exactly the same amount of morphological experience, lexical-cue experience, predictive relations, training steps and grammatical functions; only the *form–function pairing* differs.

## 4.3 Common-state / equalization phase

All histories then receive the **same common language experience** for a fixed, preregistered number of steps.

The common phase is calibrated on separate development seeds **using only current-state equivalence criteria**, never using the future-learning result.

Before challenge, the critical histories must be equivalent within prespecified margins on:

1. held-out TENSE competence;
2. held-out NUMBER competence;
3. isolated morphology-only cue use;
4. isolated free-cue use;
5. morphology-vs-free-cue conflict preference;
6. initial loss/probability on all later challenge items;
7. ordinary LM loss on matched common-language data.

If this equivalence gate fails, the experiment does **not** identify a latent learning state. Stop rather than residualize it away.

## 4.4 Identical future-learning challenge

Clone each checkpoint into fixed challenge branches. All models assigned to a branch receive **byte-identical new training examples in the same order**.

Use entirely new cue tokens and new lexical items to eliminate exact-item savings.

Branches:

- novel `M -> T` mapping;
- novel `M -> N` mapping;
- mirror `L -> T` and `L -> N` mappings;
- one unrelated new-relation control to diagnose generic plasticity.

The primary quantity is **future update response**, not endpoint test accuracy:

```text
G(H, F) = L_F(theta_H) - L_F(U_DF(theta_H))
```

where `H` is randomized history, `F` is a future cue×function relation, and `U_DF` is the same short fixed training update for that future relation.

Use one-step / very-early learning gain and a short preregistered early-learning AUC; do not wait until every condition saturates.

---

# 5. Rival predictions

## Account A — cue-class-wide learned attention

History creates a reusable state such as `morphology is worth attending to / easy to learn`.

Prediction:

- `MM` should acquire new morphology faster than `LL` for **both T and N**;
- any advantage should mainly track the amount of prior predictive morphology, not whether morphology previously expressed the same function;
- in the perfectly balanced `ML` vs `LM` comparison, there should be little or no crossover tied to T vs N.

## Account B — form × function-specific learning state

History changes future learning mainly for the particular relation that was predictive.

Prediction:

- after current behavior has been matched, `ML` should still learn novel `M -> T` faster than `LM`;
- `LM` should learn novel `M -> N` faster than `ML`;
- the mirror pattern should hold for free cues;
- this **history × cue class × grammatical function crossover** is the decisive signature.

## Account C — current preference / stored-use account

The apparent learned-attention effect is adequately described by current cue use; there is no additional persistent learning-state effect.

Prediction:

- once isolated cue use, conflict preference and current task behavior are actually equivalent, the future-learning differences should disappear.

This is a scientifically informative null: it directly weakens a strong latent-associability interpretation of learned attention.

## Account D — generic plasticity / optimization-state account

History leaves one learner globally easier/harder to update.

Prediction:

- learning differences should generalize across morphology, free cues and the unrelated new relation rather than show the pre-specified cue×function crossover.

This outcome **kills the linguistic claim**. It cannot be rescued as a generic plasticity paper.

---

# 6. Why the mixed-history crossover is unusually useful

The `ML` vs `LM` pair is the core instrument.

Both have:

- one function learned through morphology;
- one function learned through a free cue;
- equal numbers of predictive mappings;
- equal total morphology exposure;
- equal total lexical/free-cue exposure;
- equal training duration;
- the same two grammatical functions.

Therefore a global claim such as:

> `history ML simply made the network more plastic`  
> `history ML simply gave it more morphology`  
> `one model simply trained longer`  
> `morphology is globally easier than particles`

cannot predict the **direction reversal across TENSE and NUMBER**.

This is the identifying gain that was missing in the earlier WALL-E branches.

---

# 7. Strongest reviewer compressions

## Compression 1 — “Zhu et al. already test wholesale vs feature-by-feature morphology transfer.”

**Remainder:** Zhu et al. compare naturally different human L1 populations and measure acquisition outcomes. L39 randomizes the relevant language history, forces current cue use to an equivalent baseline, applies an identical new update, and measures the causal unit of **future learnability**. It asks what state history installed, not merely which L1 group transfers better.

If our study degenerates into another final-accuracy comparison across different histories, this compression wins and L39 dies.

## Compression 2 — “Associative-learning research already shows outcome-specific learned predictiveness.”

**Remainder:** learned-attention accounts of adult SLA explicitly inherit associative-learning theory but operationalize a durable linguistic `cue dimension` and use it to explain L1->L2 morphological difficulty. Usage-based language theory simultaneously treats the learned units as form–function mappings, and the flagship dimension-only blocking result is now unstable under close replication. L39 audits a **load-bearing ambiguity inside the language theory**, not merely imports an associative-learning effect into NLP.

If the paper is framed as `we reproduce outcome specificity with language tokens`, it fails selection.

## Compression 3 — “Neural L2 work already shows prior language changes later acquisition.”

**Remainder:** Oba/Hu/Constantinescu/Issam establish history effects, not the state variable's granularity after present behavior is matched. L39's estimand is the cue-class-vs-form×function structure of the **learning operator**.

## Compression 4 — “This is generic path dependence.”

**Remainder:** generic path dependence predicts that histories may differ. It does not predict the pre-registered **ML-vs-LM grammatical-function crossover** after current behavior and initial challenge loss are matched. The theory-specific interaction is the claim.

---

# 8. Main-level successful-result test

All three theory-facing outcomes are useful.

### Result 1 — form–function-specific crossover

Headline-level inference:

> **Adult-like learned attention is not a global preference for morphology; language history changes future learnability at the level of form–function relations.**

This would explain why simple morphology pretraining need not replicate symmetrically and would constrain how L1 experience is allowed to explain L2 difficulty.

### Result 2 — cue-class-wide transfer survives current-state matching

Headline-level inference:

> **Predictive experience with morphology creates a reusable morphology-level learning state that generalizes across grammatical functions, even after current cue use has converged.**

This would provide much stronger causal evidence for the classic `cue dimension` interpretation than natural L1 comparisons currently provide.

### Result 3 — no future-learning difference after current-state matching

Headline-level inference:

> **Once current cue use is matched, linguistic history no longer predicts how new morphology is learned; the strong latent-associability reading of learned attention is unnecessary.**

Given the 2026 failed close replication, this is a genuine correction to a long-standing explanatory story, not an uninteresting null.

### Non-result / kill

A broad difference that also appears on unrelated learning, without the cue×function structure, compresses to generic plasticity/path dependence. Kill the candidate under its linguistic identity.

---

# 9. Why this belongs at ACL / EMNLP / NAACL Main

This is not a benchmark paper and not `human effect X on Transformer Y`.

The modern neural learner supplies an **identifying operation unavailable in natural L1 cohorts**:

- randomize the entire relevant linguistic history;
- checkpoint exact developmental states;
- apply byte-identical future evidence;
- require matched current behavior before future treatment;
- measure the immediate learning operator rather than only final proficiency.

Recent ACL/TACL work already treats controlled neural learners as scientific model systems for inductive bias, second-language acquisition and critical-period questions. L39 uses that leverage to answer a long-standing language-learning question whose human evidence is intrinsically confounded by lifelong language history.

The contribution is an explanatory law about **what linguistic experience makes easier to learn next**, not a better multilingual model.

---

# 10. Feasibility / bounded E01

A first experiment does not require a large LLM.

A small decoder-only Transformer trained from scratch on a semi-artificial grammar is preferable because:

- histories must be randomly assigned from the same initialization distribution;
- cue frequencies and contingencies must be exactly controlled;
- many independent seeds are more scientifically valuable than one large model;
- the claim is about learning dynamics, not pretrained world knowledge.

### E01 gates

1. Both cue classes and both grammatical functions are learned reliably.
2. `ML` and `LM` histories are balanced in total task difficulty before the common phase.
3. A common phase can achieve prespecified current-state equivalence **without consulting future-learning results**.
4. Challenge cues are novel and initial challenge loss is equivalent across histories.
5. Same branch data are byte-identical across histories.
6. The primary mixed-history crossover and global-history contrast are preregistered before confirmation seeds.
7. The unrelated-control branch rules out a broad trainability shift.

Failure of Gates 1–5 is an **instrument failure**, not evidence against the scientific question.

---

# 11. Search/ownership record

The audit explicitly covered:

- classical SLA learned attention / cue competition / blocking;
- close replications of Ellis–Sagarra;
- outcome-specific learned predictiveness and second-order associability;
- usage-based form–function learning;
- wholesale vs property-by-property transfer in L2/L3;
- cross-situational morphology learning across English/German/Mandarin L1 groups;
- neural models of prior experience and category/grammar learning;
- NLP neural second-language acquisition;
- critical-period experiments with LMs;
- formal-language pre-pretraining and transferred inductive bias;
- 2026 controlled LM crosslinguistic influence / dominance work;
- generic neural path dependence / hidden training-state theory.

No direct owner was found for the exact estimand:

> **after randomized linguistic histories are brought to equivalent current cue use, does response to identical novel cue learning transfer at the level of a formal cue class or at the level of a form–grammatical-function relation?**

This is a novelty judgment as of 2026-09-14, not a proof that no unpublished/concurrent work exists.

---

# 12. Selection verdict

| gate | verdict |
|---|---|
| durable question independent of one frontier paper | **PASS** |
| native theoretical disagreement | **PASS** |
| not generic path dependence | **PASS** |
| not L34 resurrection | **PASS** |
| mature rival accounts make opposite predictions | **PASS** |
| current owner leaves a real estimand remainder | **PASS** |
| both major signs scientifically interpretable | **PASS** |
| controlled small-model identification route | **PASS ON PAPER** |
| ACL/EMNLP/NAACL Main consequence | **PASS** |
| data/RAG/benchmark as intellectual center | **NO** |

**Decision: REGISTER L39.**

No new WALL is opened. WALL-E remains the only active wall for this selection pass.