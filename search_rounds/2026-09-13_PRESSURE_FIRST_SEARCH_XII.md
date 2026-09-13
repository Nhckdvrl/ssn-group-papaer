# 2026-09-13 — Pressure-First Search XII

Continuation after `PRESSURE_FIRST_SEARCH_XI.md`. This batch mines explanatory claims and identifying assumptions across generation, psycholinguistics, semantics, post-training defaults, and mechanistic interpretability. Only `PILOT-AUTHORIZED — E01 ONLY` counts as a survivor.

---

## P56 — Contextual entrainment under scale: semantic filtering route vs mechanical copying route

**Status:** `DROP / CAUSAL ROUTE ALREADY SUBSTANTIALLY OWNED`

### Pressure
ACL 2025 Outstanding *Llama See, Llama Do* shows that merely seeing a token in context mechanically raises its later probability, even when the token is random or counterfactual. ACL 2026 then reports an intriguing scaling split: larger models become more resistant to semantic misinformation while becoming more prone to copying arbitrary tokens. This tempts a two-route RQ: does scale separate semantic filtering from a low-level entrainment/copy pathway?

### Why dead
The 2025 parent already uses differentiable masking to identify causal entrainment attention heads. A 2026 sentence-level successor finds that only about 2–4% of attention heads are sufficient to mediate the effect and that masking shared heads can nearly eliminate entrainment without broadly damaging performance. Thus `mechanical copying has a separable sparse causal route` is already much more than a conjecture. A new semantic-vs-copy head decomposition would be a natural successor/refinement of this program, not a fresh Main-level parent.

**Anti-resurrection:** do not reopen as `why larger models copy nonsense more`, `semantic resistance vs token copying circuits`, or `entrainment is low-level while misinformation is high-level` unless a distinct estimand exists beyond localizing/separating the already-owned entrainment route.

Sources: ACL 2025 Outstanding *Llama See, Llama Do*; ACL 2026 *Better and Worse with Scale*; 2026 *Sentence-Level Contextual Entrainment in Large Language Models*.

---

## P57 — Imperfective paradox: event completion state encoded correctly but overridden at decoding?

**Status:** `DROP / MOTHER PHENOMENON DESTABILIZED BY 2026 BENCHMARK REBUTTAL`

### Pressure
ACL 2026 Best Paper *The Imperfective Paradox in Large Language Models* reports a Teleological Bias: models infer completion for accomplishments even when imperfective morphology should not entail culmination. Its representational analysis argues that process/result information is internally distinguished while output is dominated by a goal prior. This initially looked like a weakly identified `encoding knows vs decoding overrides` explanation worth causal stress-testing.

### Why dead
An August 2026 rebuttal, *The Imperfective Paradox Is Not Necessarily in Large Language Models: A Benchmark Failure Before a Model Failure*, directly audits the mother and finds that a large fraction of the supposedly non-culminating examples fail to explicitly rule out culmination; native speakers also report substantial alternate interpretations. A mechanistic paper should not spend its identity repairing an unstable behavioral mother, especially when the attractive explanation is already stated by the Best Paper itself.

**Anti-resurrection:** do not reopen `teleological prior overrides aspect representation`, `encoding vs decoding of culmination`, or mechanistic patching of this benchmark unless an independently validated mother is first established outside the disputed item logic.

---

## P58 — Why is response-only loss masking the default in SFT?

**Status:** `DROP / STRUCTURAL DEFAULT ALREADY DIRECTLY TESTED`

### Pressure
Instruction tuning conventionally masks prompt tokens and trains only on assistant responses. This looks like a classic `ubiquitous default → scientific variable` generator: does response-only loss preserve prompt understanding, or throw away useful modeling signal?

### Why dead
EMNLP 2024 *Instruction Fine-Tuning: Does Prompt Loss Matter?* directly tests prompt-loss choices, and TACL 2025 *On the Effect of Instruction Tuning Loss on Generalization* systematically varies prompt loss weight and finds that non-zero prompt loss can improve generalization/robustness. The default is no longer scientifically unexamined.

**Anti-resurrection:** do not reopen `mask prompt vs train prompt`, `why response-only SFT`, or prompt-loss weighting with a new model/dataset unless a qualitatively new causal quantity—not another generalization recipe—is identified.

---

## P59 — Why do larger/lower-perplexity LMs predict human reading times worse?

**Status:** `DROP / MATURE MULTI-YEAR EXPLANATION PROGRAM`

### Pressure
A striking old-law violation is now well established: better language modeling does not monotonically imply better psycholinguistic fit; beyond moderate scale, surprisal often predicts human reading times worse.

### Why dead
This is no longer an underexplained single anomaly. TACL 2023 established the inverse-scaling pattern and lexical residuals; ACL 2024 tested calibration/temperature explanations; ACL Findings 2025 ruled out data leakage; EACL 2026 extends inverse scaling to fMRI; ACL 2026 studies early-vs-late layer alignment and provides a garden-path surprisal existence proof. Reader-experience matching and token-granularity work further decompose the gap. There is active ownership over the plausible explanation axes.

**Reviewer compression:** `inverse scaling mother + calibration + leakage + experience + layer + brain-data successors = an active mature program, not an empty why.`

**Anti-resurrection:** do not reopen generic `why bigger LMs are less human-like`, `memorization causes psycholinguistic mismatch`, or `which layer is most human-like` without a new scientific variable not already in this chain.

---

## P60 — What does activation patching actually identify: a mediator path or mediator–bypass interaction?

**Status:** `DROP / DIRECT 2026 THEORY + EMPIRICAL OWNER`

### Pressure
Activation patching is routinely interpreted as measuring the causal contribution of a component. Transformer residual connections, however, create bypass paths around every local mediator, raising an identifying-assumption question rather than a mere tooling issue.

### Why dead
June 2026 *The Curse of Multiple Mediators: Hidden Interaction Effects in Activation Patching* directly owns this pressure. It re-derives patching as causal mediation, proves that the common noising/NIE estimand contains mediator–bypass interaction effects, shows noising and denoising estimate distinct quantities, explains backup compensation and prompt instability, and demonstrates that single-component rankings can miss mechanisms that only combinatorial search reveals. This is exactly the kind of identifying-assumption paper we want to imitate in provenance, but its topic is occupied.

**Durable provenance lesson:** find a widely used scientific instrument; state the causal estimand people think it measures; identify a structural property of modern Transformers that violates the required identification condition; predict and explain multiple observed pathologies.

**Anti-resurrection:** do not reopen generic `activation patching is off-manifold`, `patching does not prove mechanism`, `self-repair hides causal heads`, or `noising vs denoising` unless a different estimand/assumption survives the 2026 interaction theory.

---

## P61 — Garden-path recovery: rebuild a corrected parse or retain/select among multiple interpretations?

**Status:** `DROP / DIRECT MECHANISM OWNER`

### Pressure
Decoder-only models cannot revise hidden states at earlier token positions, making syntactic reanalysis a conceptually interesting changed-computational-regime question. One could ask whether a disambiguator causes the later state to build a new corrected parse, retain both analyses, or repair the initially preferred representation.

### Why dead
NAACL 2025 *Incremental Sentence Processing Mechanisms in Autoregressive Transformer Language Models* explicitly asks whether LMs use syntactic features vs shallow heuristics, represent one vs multiple interpretations, and reanalyze/repair initial incorrect representations, using SAEs to study internal mechanisms. ACL 2026/SRW work further compares garden-path recovery dynamics in causal and masked LMs, while ACL 2026 has multiple garden-path/surprisal studies. The natural mechanistic question is already directly owned.

**Anti-resurrection:** do not reopen as `forward-only repair`, `two parses vs overwrite`, `where reanalysis happens`, or causal-vs-masked garden path recovery with a different model/intervention.

---

## P62 — LM-head gradient bottleneck: does the output projection discard task-relevant learning signal or mostly unrealizable/irrelevant gradient components?

**Status:** `PRESSURE ONLY — NOT SELECTION — NO COMPUTE`

### Pressure
March 2026 *Lost in Backpropagation: The LM Head is a Gradient Bottleneck* argues that projecting vocabulary-dimensional loss gradients through a hidden dimension `D << V` suppresses 95–99% of gradient norm, produces suboptimal update directions, and can make trivial pretraining patterns unlearnable. At the same time, ICLR 2026 *The Softmax Bottleneck Does Not Limit the Probabilities of the Most Likely Tokens* argues that the classical expressivity bottleneck is much less consequential for likely tokens than rank-counting intuitions suggest.

Potential scientific question:
> **Is the enormous gradient norm removed by the LM head actually information the hidden state needed in order to learn, or is norm loss a misleading quantity because most removed vocabulary-space directions are not behaviorally realizable/relevant through the shared hidden representation anyway?**

### Why not promoted
This is a real identifying-pressure tension, but the current decisive experiment is not cheap or obvious. The gradient-bottleneck paper already supplies theory plus controlled pretraining failures, so merely decomposing gradients at a fixed checkpoint cannot overturn its training claim. A fair test likely requires matched alternative heads or controlled training while holding output expressivity/top-token support fixed, which pushes cost upward and risks becoming architecture-method work. It also sits near output-head/weight-tying families already heavily studied.

**Blocker:** find a same-training-state or small controlled task intervention that distinguishes `lost norm = lost learnable signal` from `lost norm = irrelevant null-space energy` without training a new architecture at scale. Until then: no Selection and no GPU.

---

## Round checkpoint

**New survivor: 0.**

P62 is only a pressure, not a candidate. Search must continue into independent objects rather than centering the next round on output heads.