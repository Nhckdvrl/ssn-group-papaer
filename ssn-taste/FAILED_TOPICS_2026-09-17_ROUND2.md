# Failed Topics — 2026-09-17 Next-Round Search

**Status:** durable kill ledger. Read together with every other `FAILED_TOPICS*` file before generating new topics. These are negative/process evidence only, never positive taste exemplars.

---

## F75 — When does fine-tuning turn a represented feature into a causally used computation?

**Question.** Suppose a pretrained model already contains information about a task-relevant variable in a decodable latent representation, but its behavior does not depend on that variable. When supervised fine-tuning makes behavior depend on the variable, what changed: the representation itself, downstream routing/transformation, or only the final readout? In other words, how does information become computationally usable?

**Why it looked promising.** The scientific pressure is stronger than ordinary probing: `encoded` and `used` are different claims, yet adaptation must somehow connect available information to behavior. The question supports a Zhao/Cho-style chain from representation structure to transformation/routing to components to causal intervention. Several outcomes are meaningful: pre-existing representation + new routing, representation restructuring, readout-only acquisition, or a hybrid.

**Nearest prior.**
- Lepori et al., ACL 2026 Main, *Language Models Struggle to Use Representations Learned In-Context*, explicitly separates encoding novel semantics in latent representations from deploying those representations in behavior.
- Tucker et al., NAACL 2022 Main, *When Does Syntax Mediate Neural Language Model Performance?*, distinguishes decodable syntactic information from causal use and uses causal probes/interventions to establish mediation.
- 2026 work such as *Dissociating Decodability and Causal Use in Bracket-Sequence Transformers* makes `decodable representation versus causal computation` the central object under controlled interventions.
- Galichin et al., EACL Findings 2026, *Feature Drift: How Fine-Tuning Repurposes Representations in LLMs*, directly studies how fine-tuning repurposes existing features and causally links drifted base-model features to newly acquired refusal behavior.
- Older fine-tuning/probing work already asks how fine-tuning changes encoded linguistic knowledge, and recent model-diffing work broadens this to representation reuse versus new-feature formation.

**Failure reason.** The exact learning-dynamics wording initially looks fresher than a static probe-vs-causality question, but a Main reviewer can compress it to the intersection of two established parents: `(1) decodability does not imply causal use` and `(2) fine-tuning repurposes/reorganizes pretrained representations to support new behavior`. A controlled task tracing the transition from decodable-but-unused to used would be a clean and potentially useful mechanism study, but it is not yet an independently owned mother question. Its novelty currently comes mainly from combining two active literatures and following the acquisition trajectory more finely.

**Remove-the-trigger-paper test.** The question does arise independently from the conceptual distinction between representation and computation, so it passes this test. It fails instead on reviewer-level parent ownership.

**Growth lesson.** The promising part is not `probe before/after fine-tuning`. A genuinely new topic in this neighborhood would need a **new computational transition law** that forces competing explanations to make different predictions—for example, a case where a feature is already causally used for one operation but must change computational role for another, or where representation and routing can be independently manipulated and exhibit a nontrivial constraint. Merely tracing `decodable -> causal` over checkpoints is too close to existing work.

**Revival condition.** Find an independently motivated behavior in which the same latent variable must undergo a qualitatively new transformation whose necessity is not captured by generic feature reuse/drift or decodability-vs-causality. The intervention must distinguish representation change, routing change, and readout change with opposing predictions, rather than only localize when causal use appears.

---

## Search-process note

Fresh calibration this round reinforced two constraints:

1. Sasano's recent feedback emphasizes that a top-conference paper should make an average reviewer both accept the motivation and find the central result interesting; a merely decodable structure is weak if the surprising/meaningful finding lies elsewhere. Unexpected results remain valuable when they answer the same RQ.
2. Recent ACL 2026 interpretability papers already move beyond static probes toward representation/behavior/causal-use distinctions. Therefore `find a representation -> patch it` is no longer a fresh question generator by itself. The next generator should start from a behavior/computation whose possible worlds are scientifically distinct before choosing interpretability tools.

**Round verdict:** 0 survivor from this generator. Do not lower the bar; rotate search surface rather than manufacture exact-cell novelty.
