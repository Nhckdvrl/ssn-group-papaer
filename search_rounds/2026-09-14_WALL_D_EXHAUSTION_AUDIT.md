# 2026-09-14 — WALL-D Exhaustion Audit

**Wall:** WALL-D / IP04 — structure from resource constraints  
**Mode:** lineage saturation + direct-owner assassination + anti-resurrection  
**Candidate generation:** OFF until the audit is complete  
**Outcome:** **WALL-D EXHAUSTED FOR THE CURRENT SEARCH — NO NEW L-SERIES**  

> `EXHAUSTED` does **not** mean the standing scientific problem is solved. It means that, after following the main mature lineages and their 2024–2026 updates, the currently visible paper-sized descendants either (i) are already owned, (ii) do not instantiate genuine rival explanations, or (iii) survive only by narrowing into an A+B / old-debate×LM cell.

This file is intentionally written without assigning new K numbers. The repository currently contains numbering state beyond the stale header of `failed/KILLED_LEDGER.md`; polluting that sequence would be worse than recording these killed routes here. The routes below are nevertheless **anti-resurrection state** and must be checked before reopening WALL-D descendants.

---

# 1. Standing problem

The durable scientific question remains:

> **What useful representation or computation emerges specifically because a learner is resource constrained?**

The attraction of this wall is that a resource limit can be a **constructive cause**, not merely damage. The mature resource-rational program asks what information a bounded learner should preserve, at what precision, and for what downstream objective.

The search therefore did **not** ask whether `a smaller context window improves BLiMP` or whether `a bottleneck helps`. It asked whether the literature leaves an unresolved, theory-discriminating quantity for which modern neural learners supply qualitatively new identification.

---

# 2. Branch A — What is limited memory optimizing?

## Initial pressure

Resource-rational theories do not uniquely determine a learner until both the **resource** and the **objective served by that resource** are specified.

Two prominent formulations appear different:

- predictive / lossy-context accounts allocate memory to support future prediction;
- Strategic Resource Allocation (SRA) derives precision allocation from reconstructability / retrieval error over past material.

A tempting candidate was therefore:

> **Does bounded linguistic memory preserve what is hard to reconstruct, or what is useful for future prediction?**

## Why this does not survive

The rival-account premise is false in its simple form.

Xu & Futrell explicitly describe SRA and lossy-context/predictive memory as compatible rather than mutually exclusive. High-surprisal units can receive greater precision inside a predictive distortion model; the two principles need not make opposite predictions.

Meanwhile the future-predictive side has become a direct 2026 research program:

- Kajikawa, Isono & Wilcox, **Information-Theoretic Storage Cost in Sentence Comprehension** (CoNLL 2026): storage cost is formalized by how much information the past carries about future context.
- Isono & Kajikawa, **Syntactically-guided Information Maintenance in Sentence Comprehension** (CoNLL 2026): rational comprehenders selectively maintain information important for future prediction, guided by syntax.

Sources:
- https://www.sciencedirect.com/science/article/pii/S0749596X25000993
- https://aclanthology.org/2026.conll-main.2/
- https://aclanthology.org/2026.conll-main.5/

### Verdict

**KILL CURRENT DESCENDANT.**

Do not reopen as `reconstruction vs prediction` unless a future theory supplies a naturally crossed case in which the two accounts make **opposite predictions for the same memory observable**. Merely comparing the two losses/objectives in a Transformer is an A+B experiment.

---

# 3. Branch B — Encoding quality vs retrieval / maintenance

## Initial pressure

Resource effects in sentence processing can arise because:

1. the stored representation itself is noisy/compressed;
2. retrieval is competitive/locality-limited;
3. information is selectively maintained over time.

ACL 2026 Best, **Memory efficiency and resource-rational encoding in sentence processing**, is particularly important because it makes encoding precision itself a constructive cause of compressed/categorical representations.

This looked like modern leverage for an old question:

> **Are locality/interference effects consequences of what was encoded, or of how otherwise intact information is retrieved?**

## Why this does not survive as our paper parent

The scientific split is old and directly theorized in psycholinguistics. Representation-distortion and cue-based retrieval accounts have long been quantitatively contrasted, including hybrid explanations.

Modern NLP has also already entered the exact neighborhood. ACL 2025 **If Attention Serves as a Cognitive Model of Human Memory Retrieval, What is the Plausible Memory Representation?** explicitly separates retrieval algorithm from memory representation.

Therefore a project whose novelty is `use a modern LM intervention to distinguish encoding from retrieval` reviewer-compresses to:

> **old psycholinguistic debate × mechanistic LM**.

The ACL 2026 encoding work raises the evidence standard but does not by itself create a new unowned question.

### Verdict

**KILL CURRENT DESCENDANT.**

Reopen only if a specific old empirical law is simultaneously explained by two mature accounts and a new operation changes an inference that the human experiments genuinely could not identify. `Noise the representation and patch attention` is not enough.

---

# 4. Branch C — Less Is More / Starting Small

This was the deepest historical audit in this WALL.

## 4.1 The original dispute

Newport / Elman proposed that immature processing capacity might aid language learning because the learner initially processes smaller/local pieces and later combines them. Elman (1993) reported a recurrent-network regime in which adult-like full memory failed whereas a gradually expanding window succeeded.

Rohde & Plaut (1999) obtained a qualitatively different result. As the miniature language became more English-like and semantically constrained, starting small ceased to help and could hurt. A key reason is structural: intervening material can itself remain predictive of the distant dependency, so retaining longer context supplies useful local learning signal rather than merely distracting the learner.

Brooks & Kempe (2019) later separated three often-conflated stories:

1. limited cognitive capacity;
2. reduced interference / less prior knowledge;
3. simplified input.

They conclude that direct evidence for **limited capacity itself** benefiting language acquisition is weak, while prior knowledge and input structure provide more plausible routes.

Perfors (2012) supplies an especially important negative result: seven adult high-load experiments did not produce stronger regularization. Her computational analysis shows that memory limitation yields regularization only when it distorts the experienced data in the right way and when an appropriate prior bias already exists.

Rafferty & Griffiths (2010) sharpen the levels-of-analysis problem: for an ideal Bayesian learner, the best training examples for a complex language should be representative rather than artificially simple. If starting small helps, the explanation therefore lies in an **algorithmic / implementation limitation**, not in simple input being computationally more informative in general.

Sources:
- Elman (1993), Cognition, *Learning and development in neural networks: the importance of starting small*.
- Rohde & Plaut (1999), Cognition, *Language acquisition in the absence of explicit negative evidence: how important is starting small?*
- https://onlinelibrary.wiley.com/doi/full/10.1111/lang.12320
- https://www.sciencedirect.com/science/article/abs/pii/S0749596X12000800
- https://sites.socsci.uci.edu/~lpearl/courses/readings/RaffertyGriffiths2010_StartingSmall.pdf

## 4.2 Why modern Transformers do not automatically reopen it

Mita, Yoshida & Oseki (ACL 2025), **Developmentally-plausible Working Memory Shapes a Critical Period for Language Acquisition**, introduce an early memory limitation that is progressively relaxed and report improved targeted syntactic learning.

Madhyastha & Adamcová (Findings ACL 2026), **Working Memory Constraints Scaffold Learning in Transformers under Data Scarcity**, compare fixed-window and temporal-decay attention constraints and find gains especially under scarce training data.

These papers make the old question live in a modern model system, but they do not create a clean new parent for us.

The central identification problem is that attention/window-style `working-memory constraints` also alter the **effective evidence available to the learner**: they change the conditioning information used to predict the next token. This is precisely the old Less-Is-More ambiguity between an internal resource limitation and a learning environment/intake that has been selectively filtered.

However, that ambiguity itself is already old. Work before the LLM era explicitly distinguishes internal cognitive limitation from external simplified input and prior-knowledge/entrenchment effects. A modern `internal constraint × external curriculum` factorial would therefore be cleaner evidence, but not a new scientific parent.

Sources:
- https://aclanthology.org/2025.acl-long.462/
- https://aclanthology.org/2026.findings-acl.2133/

### Verdict

**STARTING-SMALL LINEAGE EXHAUSTED FOR CURRENT SEARCH.**

Forbidden reopenings:

- `Does limited WM help a Transformer learn syntax?`
- `dynamic vs static WM constraint`;
- `WM constraint helps more under low data`;
- `internal WM constraint vs simple-to-complex curriculum`;
- `capacity vs L1 entrenchment / prior knowledge`;
- `use ACL 2026 precision noise instead of ACL 2025 ALiBi and rerun acquisition`.

The last one is particularly dangerous: it is **ACL25 + ACL26**, not a question with independent provenance.

---

# 5. Branch D — Does limited capacity induce compositional / reusable units?

## Initial pressure

The strongest reading of Newport's original idea is not simply `low capacity improves accuracy` but:

> **processing less at once may force the learner away from holistic sequence memorization and toward smaller reusable form–meaning / constituent units.**

This is scientifically much more interesting than a BLiMP gain. It asks whether a resource limit changes the **granularity of learned representation**.

## Why this descendant is already crowded

This mechanism has substantial ancestry in human chunk-size / implicit-learning work, and modern work now directly connects memory/load to representational or compositional structure.

Most decisively, Futrell & Hahn, **Linguistic structure from a bottleneck on sequential information processing** (Nature Human Behaviour 2026), show that systematic word/phrase-like structure can arise from a predictive-information bottleneck. The paper's scientific object is already:

> **a sequential information-processing bottleneck as a constructive cause of systematic linguistic structure.**

ACL 2026 resource-rational encoding further shows precision constraints creating more compressed/categorical neural representations.

Source:
- https://www.nature.com/articles/s41562-025-02336-w

### Verdict

**KILL CURRENT DESCENDANT.**

`Limited working memory causes more compositional representations in LMs` is not an unoccupied parent. A new project would need a qualitatively different structural law, not another bottleneck and another systematicity metric.

---

# 6. Branch E — Resource amount vs resource allocation

## Initial pressure

Perhaps the important variable is not how much memory exists but **how a fixed budget is allocated**.

This is a natural scientific distinction: a uniformly noisy bounded learner and a strategically selective bounded learner can have the same total capacity yet preserve different information.

## Why the obvious version is already the current program

SRA is explicitly an allocation theory: under a fixed resource budget, surprising information receives greater precision. Predictive-maintenance work allocates storage according to future utility / syntax. The resource-rational program has already moved from `finite capacity` to `which information gets the capacity`.

Thus:

> `fixed budget, different allocation policies`

is not itself a new question. It is the defining move of the current literature.

### Verdict

**KILL GENERIC FORM.**

Reopen only if a mature linguistic dispute provides two independently motivated allocation policies that make opposite predictions on the same natural material. Do not invent allocation policies merely because they are easy to optimize.

---

# 7. Branch F — Bounded computation / inference

## Initial pressure

`Resource` need not mean memory. Limited inference/search compute can change the algorithm a bounded comprehender or reasoner executes.

This is theoretically attractive because it moves from `what is stored` to `what computation is performed under a budget`.

## Why there is no clean current entry

Clark et al., EMNLP 2025 **Resource-Rational Noisy-Channel Language Processing**, already instantiate bounded computation through sequential Monte Carlo and model human-like noisy-channel inference as a function of computational resources.

In the current reasoning literature, adaptive test-time compute, overthinking/diminishing returns, difficulty-conditioned allocation, and shared-budget reasoning are rapidly becoming their own active program.

Therefore generic questions such as:

- `which reasoning steps deserve more compute?`
- `does finite compute make the model use a different algorithm?`
- `can adaptive allocation outperform uniform thinking under the same budget?`

are already active method/science parents rather than unoccupied WALL-D descendants.

### Verdict

**KILL GENERIC FORM.**

A future reopening would need an older substantive theory that predicts *which* algorithm a bounded system should adopt, not simply a new compute scheduler.

---

# 8. Branch G — Resource constraint shapes the language/code itself

The final anti-miss branch asks whether cognitive constraints shape not the learner's internal representation but the **external communication system**.

This is an exceptionally strong scientific lineage, but it is not open enough for us to enter generically. Futrell & Hahn (2026) already make the bottleneck→systematic-language-structure link a central claim, while classic iterated-learning / communicative-efficiency traditions study how learning and transmission pressures shape language structure.

### Verdict

**NO GENERIC ENTRY.**

Do not propose `resource-constrained agents evolve more compositional language`, `LM iterated learning under context bottlenecks`, or `bottleneck X yields typological universal Y` without a specific unresolved historical disagreement that survives the mature cultural-evolution/efficiency literature.

---

# 9. Exhaustion judgment

The main natural descendants of WALL-D have now been checked:

| branch | current state |
|---|---|
| memory objective: reconstruction vs prediction | **not a clean rivalry + 2026 owners** |
| encoding vs retrieval / maintenance | **mature old dispute + modern owners** |
| Starting Small / Less Is More | **deep historical dispute, but obvious modern descendants compress to old debate × Transformer** |
| resource constraint → compositional/systematic representation | **directly occupied by bottleneck/systematicity program** |
| resource amount vs strategic allocation | **already the defining move of SRA/predictive-maintenance work** |
| bounded inference / reasoning compute | **active resource-rational + test-time-compute program** |
| resource bottleneck → language/code structure | **mature efficiency/cultural-evolution program + 2026 direct owner** |

No route leaves a paper-sized scientific remainder that simultaneously satisfies:

- independent old ancestry;
- genuine mature rival accounts;
- same-quantity opposing predictions;
- modern identification unavailable to the old literature;
- high consequence;
- reviewer compression resistance.

Therefore:

> **WALL-D is EXHAUSTED FOR THIS SEARCH ROUND.**

No L-series is registered. No pilot is authorized.

---

# 10. What this WALL taught us — scientific state, not a project

Several durable updates should be retained:

1. **`resource limitation` is not one causal variable.** Amount, access, encoding precision, retrieval, maintenance, prior knowledge, and inference compute are different objects.
2. **A beneficial bottleneck result does not identify why the bottleneck helped.** A window/attention constraint can simultaneously alter resource availability and the effective evidence stream.
3. **Resource rationality requires an objective.** `bounded` alone cannot predict what should be retained or computed.
4. **Capacity and allocation are distinct.** Modern theories increasingly treat selective allocation, not scalar capacity, as the central object.
5. **Constructive resource effects are real and scientifically important**, but many obvious modern descendants are now active programs rather than fresh questions.
6. **Less-Is-More should not be resurrected by swapping in a Transformer.** Its major alternative explanations were already separated long before foundation models.

These updates may later constrain another WALL. They are not themselves a paper proposal.

---

# 11. Reopen condition

WALL-D remains a standing important problem and may be reopened only when one of the following occurs:

1. a mature resource theory makes a **failed prediction** that a rival theory gets right on the same natural quantity;
2. a new operation allows an old unresolved resource dispute to be identified without changing the scientific object;
3. a new regime invalidates a load-bearing assumption of the old resource theory, rather than merely providing another implementation of a bottleneck;
4. a natural anomaly appears for which resource amount, allocation, encoding, retrieval and compute accounts make **pre-existing divergent predictions**.

A new bottleneck, attention mask, curriculum, precision noise model, or benchmark is not sufficient.
