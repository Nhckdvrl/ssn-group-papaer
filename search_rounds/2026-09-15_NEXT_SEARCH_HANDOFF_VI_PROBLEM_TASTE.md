# Next Search Handoff VI — Problem Taste, Scientific Intimacy, Exploration

**Date:** 2026-09-15  
**Primary target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS  

This is a compact control document for the next open-ended topic-search session. It is **not a constitution**. If fresh evidence from excellent papers, strong author lineages, talks/blogs, or the actual search process contradicts it, **change the search process** rather than obeying this file mechanically.

---

# 0. Current state

- Open-ended search remains **ACTIVE**.
- **L42 — Does Scale Reward Syntax?**: `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`.
- **L43 — Do Counterfactual Alternatives Predict Endogenous Route Selection?**: reconstructed from the earlier natural-backup formulation; `PILOT-AUTHORIZED — E01R ONLY; NOT MAINLINE`.
- Do **not** generate L42/L43 sequels during open search.
- Search Rounds V–VII were deep-zero rounds. Round VIII produced L43. Read their dead walls before reviving anything.
- Current preference is stronger toward **mechanistic interpretability / model science**, but this is not an exclusive assignment. Good foundation-model questions in training/post-training, reasoning/inference, architecture/inductive bias, or theory remain welcome.
- Low priority: benchmark/dataset, RAG, evaluator, data-centric, generic model-zoo, and questions whose importance requires large amounts of specialist linguistics exposition.

---

# 1. Main diagnosis: why good topics are still rare

The search process has improved substantially. The main failure is **no longer** `paper -> limitation -> gap`.

We can now generate many genuinely important mother questions. The remaining bottleneck is a combination of **landscape scarcity** and several searcher biases.

## A. Frontier-proximity bias

We read excellent 2025–26 papers to calibrate taste, but then unconsciously use those same papers as the main source of standing problems. This produces strong questions in exactly the places where strong groups are already working, so owner density is naturally extreme.

**Correction:**

- Use recent strong papers primarily as a **leverage bank** and taste calibration.
- Source standing problems more longitudinally: classic papers repeatedly cited years later, unresolved debates, open-problem syntheses, strong-author lineages, recurring empirical annoyances, old assumptions that modern work still invokes, and failures that multiple papers work around without resolving.

Do not confuse “read current frontier” with “generate next to current frontier”.

## B. Candidateization happens too early

We still often see one pressure and immediately formulate a candidate. That encourages successor-paper thinking and shallow novelty checks.

**Correction:** maintain roughly **10–20 standing important problems** in memory and a separate **new-leverage bank**. Keep only 2–4 pressure pools in deep study at a time. Candidateize only when a new clue genuinely changes what can be answered.

## C. Owner anxiety can become anti-creativity

An exact owner should kill a claim. But nearby strong work is not itself a defect.

The L43 reconstruction gave an important lesson: several strong neighboring papers can be an advantage if their intersection creates a **new scientific statement that none of the parents entails**.

Do not optimize for “distance from prior work”. Optimize for **independent paper identity**.

`A + B + C` is weak when it merely combines methods or datasets. It can be excellent when the combination exposes a new contradiction, quantity, law, or causal question.

## D. Instrument-first leakage

Once we see a powerful new method, it is easy to let the method manufacture the question: `we can now measure X, so X must matter`.

A method is valuable when it **unlocks an old important distinction**. It should not create the importance.

Before naming the method, ask whether the question would still sound important.

## E. Gambling disguised as two-way science

A project can claim “both outcomes are interesting” while still being a gamble if a negative result is easily dismissed as `the trigger was wrong`, `the stress was too weak`, or `the phenomenon did not activate`.

We strongly prefer **exploration over gambling**.

Prefer designs that estimate a relationship, law, map, causal quantity, or structural alternative over designs waiting for one lucky reversal/anomaly.

Good shape:

> natural quantity varies -> measure how another causal quantity changes -> positive / zero / negative relationships are all identified.

Bad shape:

> choose one intervention or prompt family -> hope an exciting effect appears.

A precise null is valuable only when the instrument actually covers the scientific question.

## F. Breadth without intimacy, or intimacy inside a saturated wall

Rapidly switching walls prevents understanding what a field considers its real unsolved bones. But deep-diving a saturated frontier can waste the whole round.

**Correction:** combine breadth with intimacy.

- Keep a broad problem bank.
- Pick a few less-saturated pools for longitudinal study.
- If owner density becomes obviously extreme, stop searching ever-finer residual claims and move to another standing problem.

## G. The process has become slightly over-constitutional

Many past gates are useful diagnostics, but too many rigid rules can make the searcher optimize the prompt rather than science.

The prompt is a **current belief state**, not a constitution.

Strong papers are diverse. If excellent evidence contradicts the process, modify the process.

---

# 2. What “good topic” means now

The core is not a long checklist. A truly strong candidate should satisfy most of the following at a high level.

## 1. High reward upper bound

Before feasibility, ask:

> **If the cleanest possible answer were published tomorrow by another top group, would this be a paper we would be genuinely excited to read?**

The best-case conclusion must matter beyond a narrow subcommunity or one tool. A low-upper-bound topic is not rescued by low risk.

Prefer questions that are **simple, general, and likely to remain meaningful after the current model generation changes**.

## 2. Independent importance

The question must matter before introducing our SAE, probe, patching method, metric, dataset, architecture trick, or special experimental instrument.

A knowledgeable reader should understand why the question matters in one or two sentences.

## 3. Scientific consequence

Be able to state:

> **Which meaningful belief changes if answer A is true? What changes if answer B is true?**

The strongest papers change how we think about a model capability, learning process, architecture, mechanism, scaling law, or interpretation of prior evidence.

`X affects Y` is usually not enough.

## 4. Genuine uncertainty

The answer must not be derivable from standard theory plus two parent papers.

Aim for:

> **easy to understand, hard to answer.**

A good question often has knowledgeable people making different predictions for principled reasons.

## 5. Why now / new leverage

Ask why this question is answerable **now** when it was not before.

Useful leverage includes:

- a newly controllable model family or architecture;
- a causal intervention that isolates a formerly confounded quantity;
- a theorem that changes the expected relationship;
- matched checkpoints / training regimes;
- a new natural phenomenon;
- a new way to vary one causal factor while holding behavior approximately fixed;
- several independent results whose intersection creates a previously untestable contradiction.

Recent papers should often be searched for **this**, not merely as owner checks.

## 6. Exploratory, decisive attack

Strong preference:

> **exploration > gambling.**

The experiment should map a relationship, discriminate explanations, or identify a causal quantity without requiring one lucky phenomenon.

A good E01 should maximize **information gain**, not probability of a pretty figure.

## 7. Sufficient scientific space

Do not equate nearby papers with lack of novelty.

Instead ask:

> Does the proposed paper have a scientific statement that the closest papers cannot honestly put in their own abstract without doing our experiment/theory?

If yes, several neighboring parent papers can be healthy provenance.

If the only difference is a new model, dataset, stressor, metric, or stronger probe, the space is probably too small.

---

# 3. How to search next

Do **not** follow a rigid conveyor belt. Use the following as a flexible loop.

## A. Maintain two independent banks

### Standing important problems

Prefer sources such as:

- durable / classic papers repeatedly cited by modern work;
- TACL and old ACL/EMNLP/NAACL work with unresolved conclusions;
- strong-author research lineages across years;
- field open-problem syntheses;
- talks, interviews, research statements, lab blogs;
- repeated empirical contradictions or annoying failures;
- assumptions everyone uses but whose scientific status remains unclear.

### New leverage

Continuously collect 2025–26 developments that alter identifiability:

- new causal tools;
- model families / architectures;
- post-training regimes;
- matched checkpoints;
- controllable sparsity / routing / depth / precision / feedback;
- formal results;
- newly public weights or intermediate checkpoints;
- surprising results from another scientific school.

Then ask:

> **Which new leverage suddenly bears on which standing problem?**

Do not autocomplete a limitation from the leverage paper.

## B. Build scientific intimacy before candidateizing

For a promising pool, reconstruct:

> classic question -> major answers -> repeated unresolved friction -> what researchers currently disagree about -> what was previously unidentifiable -> what changed recently.

Do not candidateize every pressure you see.

## C. Once a question becomes SERIOUS, finish the audit

Judge together:

- independent importance;
- scientific consequence;
- genuine uncertainty;
- exact / mother / adjacent owners;
- why-now leverage;
- exploratory vs gambling nature;
- identification;
- feasibility;
- reward upper bound / best-case paper identity.

Do not half-audit and jump away.

## D. Preserve a small fragile-idea budget

Keep 1–2 strange/high-upside ideas long enough for one cheap falsification, literature check, or toy calculation if the mother question is genuinely important.

Do not optimize all originality away before gathering any information.

---

# 4. Strong-paper calibration: use taste, not templates

Regularly recalibrate against diverse excellent work from **different research schools**.

Recent examples illustrate very different strong-paper identities:

- ICML 2026 Outstanding **The Flexibility Trap**: challenges a dominant supposed advantage and exposes a non-obvious failure mode.
- ACL 2026 Best **Characterizing the Expressivity of Local Attention in Transformers**: explains a real empirical puzzle by moving to theory and showing complementary expressivity.
- EMNLP 2025 Outstanding **Generative or Discriminative?**: revives a durable classical question under modern assumptions rather than inventing a micro-gap.
- ICLR 2026 **Addressing divergent representations from causal interventions**: questions whether a standard scientific instrument measures the natural model at all.
- ICML 2026 **All Circuits Lead to Rome** and TMLR 2026 **Many Circuits, One Mechanism**: challenge implicit assumptions about what a “circuit” means rather than merely discovering one more circuit.

Do **not** convert these into templates like `challenge assumption`, `old law + new regime`, or `wrong quantity`.

Instead use **predict-before-reading**:

1. From the prior literature alone, what question would I have asked?
2. What answer would I have predicted?
3. What experiment/theory would I have thought sufficient?
4. What did the actual authors notice that I missed?
5. What existing knowledge made their move possible?
6. Is my next generated idea coming from the scientific object, or am I copying the rhetorical move?

If 2–3 consecutive ideas share the same generator shape, **stop and recalibrate on another school**.

Also periodically read research-taste sources, not only papers. Useful persistent lessons:

- Hamming / Marco Ribeiro: keep ~10–20 important problems and notice when new ideas bear on them.
- Marco Ribeiro: do not accept the first `good enough` project; reject projects with a low reward upper bound.
- Chris Olah: actively train taste; compare your predicted ideas with what strong researchers actually did; beware rushing to execute as soon as an idea becomes tractable.
- Jason Wei: topic selection is a huge multiplier; prefer simple, general, durable questions and avoid narrow topics whose best-case impact is capped.
- Michael Nielsen: survey the landscape for larger patterns; “messes” may hide missing simplifying concepts.

---

# 5. Interpretability-specific guidance for the next search

The user currently wants **more interpretability**, but avoid saturated micro-frontiers.

Do not default to:

- `find another circuit`;
- `SAE feature X for behavior Y`;
- `post-training changes these heads/features`;
- `cross-prompt / cross-model stability`;
- `better attribution / patching metric`;
- generic steering / probing.

Many of these spaces are already dense.

Prefer deeper scientific questions such as:

- what an intervention-defined mechanism actually tells us about natural computation;
- when multiple causal realizations correspond to genuinely different algorithms versus equivalent representations;
- what computation is shared, substituted, recomposed, or selected endogenously;
- whether apparent modularity / redundancy / sparsity has functional consequences;
- what interpretability evidence can and cannot identify about learning or generalization;
- longstanding open problems from the 2025 TMLR **Open Problems in Mechanistic Interpretability** review, but only when a new leverage makes one of them newly attackable.

Again: these are **pressure examples, not assigned directions**.

---

# 6. Anti-resurrection / current portfolio

Before searching, sync latest `main` and read at least:

- `search_rounds/2026-09-15_SEARCHER_HANDOFF_V_RECALIBRATED.md`
- `search_rounds/2026-09-15_SEARCH_ROUND_VI_ZERO_SURVIVOR.md`
- `search_rounds/2026-09-15_SEARCH_ROUND_VII_STANDING_PROBLEM_NEW_LEVERAGE.md`
- `search_rounds/2026-09-15_SEARCH_ROUND_VIII_INTERPRETABILITY.md`
- `search_rounds/2026-09-15_L43_RECONSTRUCTION_COUNTERFACTUAL_TO_ENDOGENOUS.md`
- `failed/KILLED_LEDGER.md`
- L42 and L43 selection files.

Do not cosmetically resurrect dead walls.

In particular, recent searches already found heavy ownership around:

- RLVR `new skill vs sharpening`;
- CoT semantic-content vs extra-compute;
- optimizer / Muon implicit bias;
- QK-Norm roles;
- KV-sharing / GQA/MLA redundancy;
- attention-vs-MLP division of labor;
- pretraining-loss / plasticity sufficiency;
- AR-vs-diffusion inductive bias;
- SFT-vs-RL on-policy state distribution;
- generic circuit stability / post-training circuit evolution / simple cross-seed universality.

Only return to one of these if genuinely new evidence changes the scientific object, not merely the instrument or model scale.

---

# 7. Searcher heartbeat — mandatory self-correction

The next LLM must **not completely trust this prompt**.

Every ~1–2 serious candidate audits, or whenever the generator starts repeating itself:

1. stop generating;
2. read fresh strong papers from another conference / research school;
3. read at least one author talk/blog/interview/research statement when useful;
4. compare the current search style with how those researchers actually found / framed their problems;
5. ask whether the searcher is drifting into successor-paper search, novelty hair-splitting, tool-driven questions, or gambling;
6. change the search procedure if necessary.

The goal is **alignment with strong scientific practice**, not compliance with a static prompt.

---

# 8. Two questions to repeat constantly

> **Would excellent researchers have wanted this answer before seeing our method?**

and

> **Why is this question newly answerable now — and are we exploring a real unknown relationship, or merely betting that one exciting phenomenon appears?**

One final check:

> **If another top group published the best version tomorrow, would we wish we had done it?**

If not, keep searching.

---

# 9. Immediate next task

Do **not** spend the next session editing this process.

Use it as a prior, sync the repository, recalibrate on fresh excellent work, then **continue finding new topics**.

A final `0 survivor` is allowed after a genuinely broad/deep search. A shallow `read a few recent papers -> generate obvious questions -> exact-owner kill -> stop` is not.
