# L39 — The Unit of Learned Attention

**Status:** `PILOT-AUTHORIZED — E01 ONLY`  
**Date registered:** 2026-09-14  
**Origin:** WALL-E — developmental state / path dependence  
**Target:** ACL / EMNLP / NAACL Main

---

## 1. Research question

> **When prior language experience changes how readily a learner acquires a new morphological cue, is the persistent learning bias attached to morphology as a formal cue class, or to the particular grammatical function for which morphology was previously predictive?**

Short form:

> **What is the unit of learned attention: a form class, or a form–function relation?**

This is a question about the **state left by learning history**, not about whether one curriculum obtains higher final accuracy.

---

## 2. Why this is scientifically important

A major family of explanations for adult second-language difficulty says that successful prior language learning changes what learners attend to later. Cues that were predictive in the first language become privileged; cues that were redundant or absent can be blocked when a later language is learned.

This idea has been influential for roughly two decades under labels such as:

- learned attention;
- cue competition;
- blocking;
- entrenchment;
- crosslinguistic transfer.

But the theory has a load-bearing ambiguity.

Some classic learned-attention work talks as though experience creates a durable bias toward a **cue dimension** such as verbal morphology. Under that reading, extensive predictive experience with morphology should make novel morphology easier to learn even when it expresses a different grammatical function.

The broader usage-based/construction-learning theory, however, treats linguistic knowledge as **form–function mappings** whose contingency matters. Under this reading, learning that morphology is predictive for TENSE need not make morphology especially learnable for NUMBER.

The distinction matters because these are different theories of what linguistic experience does to a learner:

> `morphology becomes learnable`  
> versus  
> `morphology-for-this-kind-of-meaning becomes learnable`.

They make different predictions about future learning after present behavior has been matched.

---

## 3. Why the pressure is live rather than textbook residue

### 3.1 The strongest cue-dimension blocking story is under replication pressure

McManus et al. (Language Learning 2026), a close replication of Ellis & Sagarra, reproduce the strong adverb-pretraining effect but do **not** obtain the corresponding verb/morphology-pretraining effect. They argue that pretraining on a cue dimension alone does not explain subsequent attention; prior knowledge, cue properties and competition are required.

- https://doi.org/10.1111/lang.70005

This means the old `train a cue dimension -> persistently attend that dimension` account cannot simply be assumed.

### 3.2 Human cross-L1 comparisons point both ways but do not identify the state

Zhu et al. (SSLA 2025) train English-, German- and Mandarin-speaking adults on artificial morphology for tense, number and agreement and explicitly contrast **wholesale morphological transfer** with **feature-by-feature transfer**.

- https://doi.org/10.1017/S027226312510106X

Their study is important evidence, but L1 history cannot be randomized. Language groups also differ in additional-language experience and other properties, and the paper notes that the artificial markers may not have been represented unambiguously as inflection rather than adverb-like cues.

Thus natural human groups cannot identify whether the persistent state is `morphology-wide`, function-specific, or something more generic.

### 3.3 Modern neural learners make the missing intervention possible

Recent NLP work already shows that prior language/training history causally changes later language acquisition:

- Oba et al. (Findings ACL 2023), neural second-language acquisition;
- Hu et al. (ACL 2025 Outstanding), formal-language pre-pretraining and persistent transferable circuitry;
- Constantinescu et al. (TACL 2025), critical-period experiments with controlled neural learners;
- Issam et al. (2026), controlled LM crosslinguistic influence and entrenchment.

But these papers do not identify the **granularity of the latent future-learning bias after current behavior has converged**.

This is the model-system leverage of L39.

---

## 4. What this question is NOT

L39 is not:

- `Does training order matter?`
- `Does morphology transfer from L1 to L2?`
- `Can a Transformer show blocking?`
- `Do morphologically rich languages help later morphology?`
- `Can prior training improve later sample efficiency?`
- `Where in the network is the morphology circuit?`
- a repaired version of L34 prospective encoding;
- an application of activation patching to SLA.

Bare path dependence, blocking, second-order associability, item-to-dimension transfer, and L1 morphological transfer all have mature owners.

The surviving quantity is the **unit of the history-conditioned learning operator**.

---

## 5. Competing scientific accounts

### Account A — cue-class-wide learned attention

Prior predictive experience changes the learner's general disposition toward a formal cue class.

After morphology has repeatedly been useful, novel morphology should become easier to learn **across grammatical functions**.

Conceptual state:

```text
A_M = associability / attention assigned to morphology
A_L = associability / attention assigned to free lexical cues
```

History modifies `A_M` or `A_L` largely independently of the grammatical function carried by that cue.

### Account B — form × function-specific learning state

Prior experience changes future learning primarily for a **relation** between a formal cue class and a grammatical function.

Conceptual state:

```text
A_(M,TENSE)
A_(M,NUMBER)
A_(L,TENSE)
A_(L,NUMBER)
```

Learning morphology for TENSE may therefore facilitate new morphology-for-TENSE without facilitating new morphology-for-NUMBER.

### Account C — current-use / no additional latent state

History changes present cue preference or current representations, but once current behavior and cue use are genuinely brought to the same observable state, no extra history-dependent learning bias remains.

Under this account, future learning is predicted by the learner's present state at the level we have matched.

### Account D — generic plasticity / optimization state

Different histories globally change trainability rather than a linguistic learning state.

This can produce different learning rates, but it does **not** predict the pre-specified cue-class × grammatical-function crossover.

If this account explains the result, the L39 linguistic claim fails.

---

## 6. Core experimental object

Use a controlled semi-artificial language with two surface cue classes and two grammatical functions:

- **M** = bound morphological cue;
- **L** = free lexical/function cue;
- **T** = TENSE;
- **N** = NUMBER.

The design must make grammatical function real: cue values covary with interpretable event properties such as temporal location and entity numerosity, not arbitrary class labels named `T` and `N`.

The surface realizations must be counterbalanced so that morphology vs free-cue identity is not synonymous with token frequency, marker length, entropy, vocabulary size, output position, or number of supervised events.

A character/byte-level or purpose-built tokenizer is preferred if ordinary subword tokenization would give one cue class an accidental representational advantage.

---

## 7. History manipulation

Four randomized histories:

| arm | TENSE predictive cue | NUMBER predictive cue |
|---|---|---|
| `MM` | morphology | morphology |
| `ML` | morphology | free cue |
| `LM` | free cue | morphology |
| `LL` | free cue | free cue |

Crucially, both cue classes should remain **present** in every arm. Predictiveness/contingency changes; raw exposure does not disappear.

The strongest pair is `ML` vs `LM`.

They contain:

- the same two functions;
- one morphology-predictive relation;
- one free-cue-predictive relation;
- the same total number of predictive contingencies;
- the same training steps;
- matched cue frequencies;
- matched numbers of morphology and free-cue tokens.

Only the **pairing between cue class and grammatical function** changes.

This symmetry is the main protection against generic plasticity and total-exposure explanations.

---

## 8. Common-state phase — mandatory WALL-E identification step

After different histories, every model receives **exactly the same common-language training** for a fixed number of steps.

The purpose is not to erase all internal history. The purpose is to make the histories observationally equivalent on the quantities that could otherwise trivially explain later learning.

The common-phase duration may be calibrated using separate development seeds, but calibration may use **only equivalence metrics**. Future-challenge results must remain hidden until the duration and equivalence margins are frozen.

### Required pre-challenge equivalence

For the confirmation models, `ML` and `LM` must fall within preregistered equivalence margins on all of:

1. TENSE accuracy / surprisal;
2. NUMBER accuracy / surprisal;
3. morphology-only TENSE use;
4. morphology-only NUMBER use;
5. free-cue-only TENSE use;
6. free-cue-only NUMBER use;
7. cue-conflict preference for both functions;
8. common-corpus language-model loss;
9. initial loss on each future challenge family before any challenge update.

The `MM` and `LL` comparison should satisfy the same gate if it is used for the global cue-class claim.

### Hard rule

If current-state equivalence cannot be achieved cleanly, E01 is **instrument failure**.

Do not use regression/residualization to claim a hidden state while large behavioral differences remain.

---

## 9. Future-learning challenge

After the equivalence gate, clone each checkpoint into independent future-learning branches.

Every history assigned to the same branch receives the **same examples, in the same order, with the same optimizer state and update count**.

The challenge uses:

- novel cue tokens / affixes;
- novel lexical stems where possible;
- the same grammatical functions TENSE and NUMBER;
- matched cue frequency and contingency.

Primary branches:

1. novel `M -> T`;
2. novel `M -> N`;
3. novel `L -> T`;
4. novel `L -> N`.

Add one **linguistically unrelated new-relation control** with matched training burden. Its only role is to detect a broad trainability shift.

---

## 10. Primary estimand

Do not make saturated endpoint accuracy primary.

For a history `H` and future relation `F`, define the early-learning response to a fixed update:

```text
G(H,F) = L_F(theta_H) - L_F(U_DF(theta_H))
```

where:

- `theta_H` is the matched pre-challenge checkpoint after history `H`;
- `D_F` is the fixed training batch / short curriculum for future relation `F`;
- `U_DF` is the identical update operation;
- `L_F` is held-out loss on unseen items from that same future relation.

Primary summaries:

- one-step / first-few-step held-out loss reduction;
- preregistered early-learning AUC before saturation.

### Decisive mixed-history crossover

For morphology, the form×function account predicts:

```text
G(ML, M->T) > G(LM, M->T)
G(ML, M->N) < G(LM, M->N)
```

The mirror prediction holds for free cues.

This reversal is the key interaction.

A global morphology preference cannot produce the reversal from total morphology exposure, because `ML` and `LM` have exactly the same amount of morphology history.

---

## 11. Full prediction table

### If Account A — cue-class-wide state

Expected pattern:

- `MM` faster than `LL` for both `M->T` and `M->N`;
- `LL` faster than `MM` for the mirror free-cue challenges;
- mixed histories `ML` and `LM` show little cue×function crossover once total predictive morphology is matched.

### If Account B — form×function-specific state

Expected pattern:

- `ML > LM` on novel `M->T`;
- `LM > ML` on novel `M->N`;
- reverse mirror on free-cue branches;
- the effect survives current-state equivalence and novel markers/stems.

### If Account C — current-state sufficiency

Expected pattern:

- after equivalence, history no longer predicts early learning on the challenge branches.

This is not an automatic candidate kill. It directly rejects the strong persistent-associability version of learned attention under the tested conditions.

### If Account D — generic plasticity

Expected pattern:

- one history learns many/all future relations faster, including the unrelated control;
- no theoretically predicted form×function crossover.

This **kills L39 under its current paper identity**.

Do not rebrand as a plasticity paper.

---

## 12. Why this is not just Zhu et al. with a model

The strongest reviewer compression is:

> Zhu et al. already compare wholesale and feature-by-feature morphological transfer; this paper just repeats the question in Transformers.

That compression is fatal unless the following difference remains central:

> **Zhu et al. compare naturally different learner populations and ask which groups acquire morphology better. L39 randomizes the relevant linguistic history, matches the learner's current cue use, then asks how an identical new learning event changes the model. The object is the causal unit of the latent learning state, not group-level transfer performance.**

The whole experiment is built around that difference.

If final figures become `history A has higher final accuracy than history B`, reject the paper identity.

---

## 13. Why this is not “psychology result + NLP”

General associative-learning work already shows learned predictiveness can be outcome-specific.

That fact is evidence **against novelty by analogy**, not our novelty claim.

The scientific reason L39 remains open is that the adult-SLA learned-attention program explicitly uses associative learning to explain durable L1->L2 cue biases, while simultaneously describing transfer at the level of linguistic cue dimensions. Usage-based theory gives a different natural unit — form–function mappings — and the key cue-dimension blocking result is now unstable under close replication.

Therefore L39 asks whether the **language theory has specified the correct state variable**.

A paper whose introduction says only `psychology found outcome specificity, so we test it in language` should be rejected before submission.

---

## 14. Why this is not generic path dependence

Generic path dependence says two histories may produce different future behavior.

It does not predict:

> after current behavior is matched, swapping which grammatical function was historically carried by morphology should reverse which future morphological relation is learned faster.

The `ML` vs `LM` crossover is a **linguistic theory prediction**, not a generic consequence of non-commutative gradient descent.

---

## 15. Main-level result space

### Result A — form×function-specific crossover

Inference:

> **The persistent effect of language history is relational: morphology becomes easier to learn for functions it previously carried, not globally as a cue dimension.**

Consequence:

- weakens the strongest global cue-dimension reading of learned attention;
- aligns adult-L2 entrenchment with a construction/form–function learning unit;
- explains why morphology pretraining need not transfer symmetrically across linguistic uses.

Potential headline:

> **Learned attention is a relation, not a cue class.**

### Result B — global cue-class transfer

Inference:

> **Predictive morphological experience creates a reusable morphology-level learning state that generalizes to new grammatical functions even after present cue use converges.**

Consequence:

- gives much stronger causal support to the classic cue-dimension account than natural L1 comparisons provide;
- establishes a true second-order acquired bias rather than a current-use difference.

Potential headline:

> **Language experience changes how morphology itself is learned next.**

### Result C — no latent history effect after equivalence

Inference:

> **Once present cue use is matched, past predictive history no longer changes acquisition of new morphology; a hidden persistent associability state is not needed to explain learned-attention behavior in this regime.**

Consequence:

- fits the recent replication pressure;
- moves explanation toward current competition/cue properties rather than a durable history-conditioned learning operator.

Potential headline:

> **Learned attention does not outlive the behavior that reveals it.**

### Result D — generic trainability only

Kill.

---

## 16. Anti-phenomenon-gambling rules

1. No model-family shopping after seeing the challenge effect.
2. No searching common-phase length for a history effect; common-phase selection sees only equivalence metrics.
3. No changing TENSE/NUMBER to another pair after the crossover is null.
4. No choosing marker realizations post hoc based on the sign.
5. No restricting to seeds that pass in the desired direction.
6. No mechanistic explanation before the behavioral learning-state quantity is established.
7. No rescue from generic plasticity by adding activation analysis.
8. Null after a valid equivalence gate is a legitimate answer to Account C.

---

## 17. E01 — bounded pilot

**Authorization: YES, E01 ONLY.**

The pilot has two strictly separated stages.

### E01-A — instrument construction / equivalence calibration

Allowed to inspect:

- whether both cue classes are learnable;
- whether both functions are learnable;
- whether history arms have matched exposure and expected behavior;
- current-state metrics only;
- whether a fixed common phase can satisfy equivalence margins.

Forbidden to inspect while tuning the instrument:

- future-challenge history effects;
- the decisive `ML` vs `LM` crossover.

Choose and freeze:

- grammar generator;
- tokenizer;
- model architecture;
- history token budget;
- common-phase duration;
- equivalence margins;
- future challenge batches;
- primary statistic.

### E01-B — untouched challenge test

After freezing E01-A, train fresh confirmation seeds and run the predetermined future challenge.

Primary decision:

> Does the history-conditioned early-learning response support cue-class-wide state, form×function-specific state, current-state sufficiency, or generic trainability?

No follow-up intervention is authorized automatically.

---

## 18. E01 kill conditions

Kill or return to selection if:

1. morphology and free cues cannot be made comparably learnable without unnatural task engineering;
2. current-state equivalence requires selecting checkpoints after seeing challenge outcomes;
3. `ML` vs `LM` retain large current cue preferences after the common phase;
4. novel challenge markers have unequal initial loss across histories that cannot be fixed by design;
5. the only history effect is a broad trainability difference visible on the unrelated control;
6. marker tokenization/surface frequency determines the result;
7. a fresh ownership audit finds a direct prior experiment with randomized linguistic history + matched current cue use + identical future update distinguishing cue-class vs form×function learning state;
8. the strongest successful result still compresses to `prior training helps related future learning`.

---

## 19. Ownership boundary

Directly covered / not claimable as novelty:

- blocking and learned attention in SLA;
- long-term L1 effects on morphology;
- second-order associability / learned predictiveness;
- outcome specificity of learned predictiveness;
- item-to-cue-dimension generalization;
- wholesale vs feature-by-feature L2/L3 transfer;
- neural L1->L2 transfer;
- critical-period effects in LMs;
- formal-language pre-pretraining creating linguistic bias;
- generic neural path dependence;
- mechanistic persistence of prior-training circuitry.

The only selected remainder is:

> **the causal granularity of the persistent future-learning state after linguistic histories have been randomized and current cue use has been matched.**

---

## 20. Current confidence

- **Q-confidence:** HIGH. The theory question remains important regardless of the pilot sign.
- **I-confidence:** MEDIUM-HIGH ON PAPER. The symmetric mixed histories plus current-state gate create a real identifying contrast, but feasibility must be demonstrated by E01-A.
- **Novelty confidence:** MEDIUM-HIGH after current audit; concurrent/unindexed work remains possible.
- **Main-level reward:** HIGH if the clean interaction/null survives multiple seeds and one principled replication family.

---

## 21. Current authorization

**PILOT-AUTHORIZED — E01 ONLY.**

Allowed next work:

- construct the balanced semi-artificial grammar;
- write the exact data/gold contract;
- calibrate the common-state phase using equivalence only;
- freeze the E01 challenge and statistic;
- run confirmation seeds.

Not yet authorized:

- mechanistic interpretability;
- large-model scaling;
- multilingual/natural-language expansion;
- human experiment;
- model zoo;
- paper writing around a generic transfer effect.

The scientific question is locked before the result:

> **Does learned attention persist at the level of a formal cue class, a form–function relation, or not beyond matched current cue use?**
