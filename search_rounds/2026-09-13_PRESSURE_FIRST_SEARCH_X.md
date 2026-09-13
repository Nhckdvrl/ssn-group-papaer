# 2026-09-13 — Pressure-First Search X

Continuation after `PRESSURE_FIRST_SEARCH_IX.md`. This file records the first cross-pool owner-assassination batch of the new conversation. It deliberately does **not** continue the Neg-raising / gradable-adjective leads as the primary search axis.

Only `PILOT-AUTHORIZED — E01 ONLY` counts as a survivor. No portfolio promotion is made in this file.

Search doctrine:

> **scientific pressure first → decisive matched/stress test → phenomenon second**

This batch sampled independent objects from psycholinguistic structure/semantics, reasoning order, factual relation learning, tokenization, multilingual scaling, and finetuning dynamics. The point is to record why attractive hooks die so they are not rediscovered after a network/session interruption.

---

## Hook P41 — Center embedding: structure lost, or structure present but overridden by semantic plausibility?

**Status:** `DROP / NEIGHBORING INTERNAL EVIDENCE ALREADY PREDICTS THE STRONGEST RESULT`

### Pressure

EACL 2026 *The Dog the Cat Chased Stumped the Model* (CenterBench) establishes a clean behavioral mother: as center-embedded sentences become harder, the plausible-vs-implausible performance gap widens, which the paper interprets as models abandoning structure for semantic associations.

The tempting mechanistic RQ is:

> **On an incorrect implausible trial, has the structural relation itself failed to form, or is a usable structural state still present and later overridden by semantic plausibility?**

This initially looked like a mature `representation/state vs selection/readout` distinction rather than another competence benchmark.

### Why it dies

The strongest likely mechanistic answer is already substantially predicted by nearby 2026 work:

- McGee, Zhang & Blank, *Evidence Against Syntactic Encapsulation in Large Language Models* (Cognitive Science 2026), directly reports that semantic implausibility changes the behavior of attention heads selected for syntactic dependency tracking rather than leaving a clean autonomous syntax module untouched.
- Aljaafari et al., *Emergence and Localisation of Semantic Role Circuits in LLMs* (ACL Findings 2026), already identifies causally functional, compact semantic-role circuits with edge attribution and training-time tracking.

Together these owners make a generic `syntax is there but the output merely ignores it` paper difficult to own. Conversely, a result that semantic plausibility degrades the structural/role state itself is already strongly foreshadowed by the Cognitive Science result.

### Reviewer compression

> `CenterBench establishes semantics-vs-structure behavioral failure + syntax-specialized heads are themselves modulated by semantic plausibility + causal semantic-role circuits already exist = a new state-vs-override localization is a refinement, not a fresh parent.`

### Anti-resurrection

Do not reopen as `does the model secretly parse the implausible sentence`, `structure present but semantic shortcut wins`, or generic CenterBench activation patching unless a genuinely new estimand appears that the syntactic-encapsulation and semantic-role-circuit work cannot already predict.

Sources:

- https://aclanthology.org/2026.eacl-long.19/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12973484/
- https://aclanthology.org/2026.findings-acl.1964/

---

## Hook P42 — Presentation order vs utilization order: is the dependency graph missing, or merely executed in the wrong order?

**Status:** `DROP / PROBLEM FAMILY ALREADY EXPANDED INTO ORDER-AND-STRUCTURE PROGRAM`

### Pressure

A clean deployment-style mismatch exists: the same information can be presented in an order different from the order in which it should be used. Earlier work already found premise-order effects, and EACL 2026 *The Curse of Verbalization* shows that reasoning degrades when presentation order and utilization order diverge.

The tempting mechanistic question was:

> **Does the model fail because it never constructs the task dependency structure, or because it represents that structure but autoregressive reasoning still serializes it in presentation order?**

### Why it dies

By 2025–2026, presentation/utilization order is no longer an isolated behavioral anomaly. The literature already contains premise-order studies, graph/dependency-order studies, explicit order augmentation, and the EACL 2026 verbalization account. A new internal localization would be compressed as a mechanistic refinement inside an already explicit `presentation order → reasoning order` research program.

The obvious intervention is also not selective: changing/patching intermediate order can itself supply the correct execution sequence, making it hard to distinguish `dependency graph absent` from `graph present but serialization biased` without injecting the answer.

### Reviewer compression

> `premise-order mother + graph/order successors + Curse of Verbalization = the core law and its proposed explanation are already active; patching the execution order is not an independent scientific parent.`

### Anti-resurrection

Do not reopen generic `reasoning follows input order`, `dependency graph represented but not followed`, or `presentation order vs reasoning order mechanism` unless a new selective operation identifies one account without directly giving the correct order.

Source:

- https://aclanthology.org/2026.findings-eacl.218/

---

## Hook P43 — Reversal Curse: wrong direction stored, or correct relation available but unbound to the queried direction?

**Status:** `DROP / SUCCESSOR PROGRAM HAS ALREADY DECOMPOSED DIRECTION, BINDING, IDENTITY, AND RELATION FACTORS`

### Pressure

The original Reversal Curse was a strong old-law-style anomaly: training `A is B` does not reliably yield `B is A` even when the inverse follows trivially. A tempting causal RQ is whether reverse failure reflects absent inverse knowledge versus a binding/readout failure.

### Why it dies

The 2024–2026 successor literature is already unusually deep: work has separated root word-order effects, causes of reversal, recall/reversal training interventions, structured binding, identity bridges, and entity/relation contributions. The scientific parent is no longer merely `why can’t the model reverse a relation?`; the natural explanatory axes have already become the topic of multiple successor papers.

A new `inverse fact exists but is misbound` paper is therefore not independent enough, even if implemented with a clean patch.

### Anti-resurrection

Do not reopen `reversal = storage vs retrieval`, `binding vs direction`, or `inverse relation latent but unread` through a new model/patch/dataset. A future return requires a scientific quantity not already covered by the reversal/binding successor program.

---

## Hook P44 — Non-canonical tokenization: does the LM reconstruct canonical words first, or compute directly over arbitrary fragments?

**Status:** `DROP / DIRECT CAUSAL MECHANISM OWNER`

### Pressure

NeurIPS 2025 Spotlight *Broken Tokens? Your Language Model can Secretly Handle Non-Canonical Tokenizations* establishes a striking mother: instruction-tuned models retain up to 93.4% of canonical performance under random non-canonical tokenization and 90.8% under character-level tokenization, despite such segmentations being unseen during training.

The intuitive mechanism question is:

> **Does the model first reassemble arbitrary fragments into a canonical whole-word lexical state and then compute normally, or can downstream computation remain distributed over the fragments without a canonicalization stage?**

This initially looked independent of the killed `tokenizer bottleneck for multilingual competence` parent because the estimand is internal recovery of lexical identity, not downstream multilingual capacity.

### Why it dies

ICLR 2025 *From Tokens to Words: On the Inner Lexicon of LLMs* already directly owns the answer. It proposes **intrinsic detokenization**: subword information is integrated into a whole-word representation at the final fragment, mostly in early/middle layers. Crucially, the result is robust to arbitrary splits, typos, and OOV words, and the paper causally ablates FFN contributions that construct the whole-word state; destroying those updates sharply harms both word recovery and downstream country→capital behavior.

Thus extending the same mechanism to the more extreme NeurIPS 2025 mother is application/confirmation, not a fresh Main-level question.

### Reviewer compression

> `Broken Tokens establishes extreme non-canonical robustness + From Tokens to Words already shows arbitrary splits are causally detokenized into whole-word states = canonicalize-vs-distributed is already answered.`

### Anti-resurrection

Do not reopen as `how do LMs understand character tokenization`, `canonicalization vs segmentation invariance`, `where broken tokens get repaired`, or `does the last fragment store the word` unless a causal quantity beyond intrinsic detokenization is identified.

Sources:

- https://proceedings.neurips.cc/paper_files/paper/2025/hash/2b5c5689fae6fa9a4883e73e511d52c8-Abstract-Conference.html
- https://proceedings.iclr.cc/paper_files/paper/2025/hash/aef75887979ae1287b5deb54a1e3cbda-Abstract-Conference.html

---

## Hook P45 — Does MoE erase the classic curse of multilinguality by isolating languages into experts?

**Status:** `DROP / CHANGED-REGIME RETEST ALREADY OWNED`

### Pressure

The classic curse of multilinguality says that finite shared capacity creates interference as one model covers more languages. Modern sparse MoE architecture appears to change the load-bearing premise because total parameter capacity can grow while active compute remains bounded.

A natural Type-B/C question is:

> **Did sparse experts actually remove the old interference law, or merely relocate multilingual competition into routing/shared components?**

### Why it dies

Recent multilingual-MoE work already explicitly uses MoE to address negative transfer/capacity competition, analyzes language-related expert routing, and studies how language groups share or specialize experts. The architecture change has already been used to revisit the old multilinguality premise directly. A fresh model family sweep would be another routing/capacity paper, not a new model-science law.

### Anti-resurrection

Do not reopen generic `curse of multilinguality under MoE`, `language-specific experts fix interference`, or `where multilingual interference moves in MoE` without a same-quantity contradiction that existing multilingual-MoE studies cannot explain.

---

## Hook P46 — Catastrophic overtraining: why does more pretraining reduce downstream plasticity?

**Status:** `DROP / 2026 SUCCESSOR ALREADY PROVIDES THE OPTIMIZATION MECHANISM`

### Pressure

ICML 2025 *Overtrained Language Models Are Harder to Fine-Tune* challenges the default monotonic assumption `better/longer pretraining → better downstream adaptation`: longer pretraining can make SFT outcomes worse, accompanied by broader parameter sensitivity.

The obvious scientific question is why continued pretraining reduces plasticity — e.g. whether the model becomes intrinsically sharp/fragile versus whether SFT simply uses the wrong step scale for the later checkpoint.

### Why it dies

April 2026 *\(How\) Learning Rates Regulate Catastrophic Overtraining* directly links the phenomenon to optimization geometry: pretraining learning-rate decay increases pretrained sharpness, which exacerbates catastrophic forgetting during SFT; different finetuning learning rates converge to qualitatively different models even at matched SFT loss.

That successor already performs the mechanistic rewrite the pressure-first search would want.

### Reviewer compression

> `ICML 2025 establishes catastrophic overtraining + 2026 successor links LR decay → sharpness → SFT forgetting = generic plasticity/sharpness mechanism is owned.`

### Anti-resurrection

Do not reopen as `why overtraining hurts SFT`, `sharpness causes loss of plasticity`, or `later checkpoints need different SFT learning rates` unless a new same-quantity result contradicts the 2026 mechanism.

Sources:

- https://proceedings.mlr.press/v267/springer25a.html
- https://arxiv.org/abs/2604.13627

---

## Hook P47 — Why does narrow finetuning leave a readable domain signal on completely unrelated text?

**Status:** `PRESSURE ONLY — NOT SELECTION / NO COMPUTE`

### Pressure

ICLR 2026 *Narrow Finetuning Leaves Clearly Readable Traces in Activation Differences* finds that the base→finetuned activation difference on the **first few tokens of unrelated/random text** can reveal the format and semantic content of the finetuning domain; steering with that difference can reproduce the domain. The effect spans architectures/scales and shrinks when unrelated/pretraining data are mixed into the finetune.

The interesting scientific question is not `can we detect the finetune?`, but:

> **Why does domain-specific training create a domain-readable shift before the current input contains domain evidence? Is narrow finetuning writing an approximately prompt-independent global bias into the residual computation, or are nominally unrelated states repeatedly activating changed features in an input-dependent way?**

### Why it is not promoted

This is close to a live owner program, and the proposed explanation risks becoming algebraically predictable. The ICLR parent already averages activation differences and shows that the average itself steers domain-like generation; August 2026 *Diff Mining* further finds finetuning fingerprints in output-logit differences on unrelated text. ICML 2026 *Weight Updates as Activation Shifts* gives a first-order theoretical bridge between weight updates and activation shifts.

A simple `mean shift vs residual shift` decomposition would therefore be descriptive, and `ΔW h` already makes an average input-independent component unsurprising when hidden states have a nonzero mean. We currently lack a selective operation whose two outcomes would establish a deeper law about narrow finetuning rather than explain why ADL works.

### Blocker

Need a scientific A/B that is **not** already implied by `weight update ↔ activation shift`, and a manipulation that can selectively remove the putative global prior while preserving the learned task. Until then: no Selection and no GPU.

### Anti-resurrection

Do not promote generic `why ADL works`, `finetuning leaves a global activation bias`, or `mean activation difference is causal`. A future return needs a new invariant/estimand beyond detecting or steering the finetuning objective.

Sources:

- https://proceedings.iclr.cc/paper_files/paper/2026/hash/3b939edfdf9c1211fb764a888078f13d-Abstract-Conference.html
- https://arxiv.org/abs/2608.26462
- https://arxiv.org/abs/2603.00425

---

## Hook P48 — Syntactic-domain shortcut learning: intended task missing, or present but overridden by the spurious syntax cue?

**Status:** `DROP / TOO CLOSE TO ACTIVE SHORTCUT-MECHANISM + L33/CENTERBENCH SHAPE`

### Pressure

NeurIPS 2025 work on syntactic-domain spurious correlations shows that models can learn a syntactic cue that overrides intended task semantics. The natural mechanistic A/B is again `task representation corrupted/never formed` versus `task representation preserved but spurious cue wins downstream`.

### Why it dies

Even before exhaustive implementation design, this is the wrong direction for the current search. It mechanically instantiates the same `state distortion vs downstream selection` skeleton already represented by L33 and P41, but with a new shortcut phenotype. That violates the instruction to search independent scientific objects rather than manufacture neighboring interference papers.

The broader shortcut/spurious-correlation literature also already treats representation and shortcut reliance as causal objects. A new syntax-domain patching study would be owner-adjacent and would add portfolio redundancy rather than scientific breadth.

### Anti-resurrection

Do not reopen via a different spurious feature, domain token, training corruption, or patching target. A new shortcut paper would need a genuinely different scientific distinction, not another `correct signal exists but shortcut wins` variant.

---

# Round checkpoint

**New survivor so far: 0.**

This is **not** a closeout. The search continues across new pools. In particular, this batch intentionally kills multiple initially attractive mothers instead of using their cleanliness as a reason to authorize compute.

The strongest unresolved item in this file is P47, but it remains only `PRESSURE ONLY / NO COMPUTE` and should not dominate the next search batch.
