# 2026-09-13 — Continued Search After L31 II

Continuation of `2026-09-13_CONTINUED_SEARCH_AFTER_L31.md`. Same persistence rule: log every nontrivial killed lead immediately; only report a topic to the user after full SEARCH+SELECT reaches `PILOT-AUTHORIZED — named bounded E01`.

## N. Parallel Attention+MLP as the root cause of small-Pythia late saturation — DROP

**Scientific object:** Why do small Pythia models become worse late in pretraining while closely matched small language models do not? Is Pythia's hardware-motivated parallel Attention+MLP block the load-bearing trigger, rather than an intrinsic softmax/output-rank capacity wall?

**Mother / same-quantity pressure:**
- COLM 2024 establishes late-training loss degradation / saturation in small Pythia models.
- PolyPythias (ICLR 2025) provides nine additional seeds across 14M–410M and reports highly consistent training dynamics across seeds/sizes; ICML 2026 explicitly cites Pythia/PolyPythias saturation for <=160M.
- ICML 2026 Spotlight `Disentangling Geometry, Performance, and Training in Language Models` trains an OLMo-14M that exactly matches Pythia-14M and states that the **sole architectural difference is sequential attention instead of Pythia's parallel variant**. Pythia shows late loss degradation and abrupt rank collapse; matched OLMo does not. The authors explicitly conjecture that parallel attention may contribute, while leaving the root cause open.
- PaLM previously reported a small-scale quality penalty for parallel Attention+MLP that shrinks/disappears at larger scale, giving independent architecture pressure rather than a Pythia-only observation.

**Closest mechanistic owners:**
- Aug-2026 `Feed-Forward Steering in Transformer Residual Dynamics` develops an attention-as-aggregation / FFN-as-local-steering account and defines a sequential-to-parallel defect. It shows that low-defect sequential layers can be parallelized with small loss while high-defect layers degrade sharply.
- Mar-2026 `Half the Nonlinearity Is Wasted` finds strong architecture dependence between sequential GPT-2 and parallel Pythia MLP behavior and explicitly discusses the sequential-vs-parallel trade-off.

**Tempting missing inference:** A causal training intervention could try to show that removing same-layer Attention→MLP dependence causes the late small-model failure, perhaps with a scale boundary and a growing FFN-steering/commutator defect.

**Strongest reviewer compression:**
> `Kulkarni et al.: matched Pythia-14M saturates while the otherwise matched sequential OLMo-14M does not, and parallel attention is explicitly proposed as the cause` + `Mudarisov et al.: we already know what computation is lost when a sequential block is parallelized and have a defect predicting its quality cost` + `PaLM / later architecture sweeps: parallel blocks already have a small-scale quality penalty` = `you confirmed an already strongly implied explanation`.

**Why this fails the successful-result test:**
Even a perfect same-code parallel-vs-sequential training result would mostly upgrade Kulkarni's near-controlled observation/conjecture to a cleaner causal replication. The likely mechanism—loss of current-layer attention-conditioned FFN steering—is already supplied by the Aug-2026 dynamics work. The exact late-training intervention is missing, but the strongest expected answer is substantially implied by the closest components.

**Identification / pilot problem:**
A cheap checkpoint surgery (switching a trained parallel Pythia checkpoint to sequential) changes the computation off the training manifold; positive rescue could be transient architectural perturbation, while a null would not rule out an architecture-induced training path. A clean from-scratch parallel-vs-sequential training comparison is identifiable, but ICML-2026 has already run almost that exact matched comparison. Thus the cleaner the experiment becomes, the more it collapses into a replication/confirmation of the closest owner.

**Verdict:** `DROP / DO NOT REGISTER AS L32`.

**Anti-resurrection:** do not reopen as `parallel residual causes saturation`, `same-layer Attention→MLP steering prevents saturation`, `commutator defect predicts Pythia saturation`, `serializing Pythia rescues late loss`, or another parallel-vs-sequential small-model sweep unless a qualitatively different stable quantity and inference appears.

---

_Continue search from here; append later killed leads in this file or a numbered continuation if the file becomes too large._
