# 2026-09-12 — Continued Topic Search II

**Target:** ACL / EMNLP / NAACL Main  
**Rule:** anti-resurrection first; combine multiple reliable results into scientific pressure; no survivor quota.  
**Record style:** only the core question and the reason it cannot currently support a new Main-level paper.

## Rejections

- **Many inputs: learning signal or processing burden?**  
  **Question:** Why can many-shot demonstrations keep helping while multi-instance prediction degrades as more instances are packed into one call?  
  **Why not:** multi-instance processing, multi-problem evaluation, and latent-state / working-memory set-size work already occupy the main processing-burden explanation. The remainder compresses to a synthesis of those parents rather than a new scientific relation.

- **Reasoning strength vs validity gate.**  
  **Question:** Does reasoning post-training improve object-level solving while weakening the decision of whether the problem should be solved at all?  
  **Why not:** tool hallucination, abstention under insufficient information, and overthinking are now directly studied; recent work already connects these failures to objective mismatch / persistent test-taking behavior. Cross-domain unification alone is not enough.

- **Multi-turn persistence: stale history or failed belief update?**  
  **Question:** When a model becomes worse across turns, is it mainly polluted by its own history or unable to revise an earlier commitment?  
  **Why not:** multi-turn failure, belief-revision, repair, and multi-turn RL work already separate persistence, update, and recovery. Remaining mechanism cells are too crowded.

- **Agent limit-awareness: absent state or unused state?**  
  **Question:** Does an agent fail to abstain because it does not represent that action is invalid, or because that state fails to control the action policy?  
  **Why not:** When2Tool-style latent tool-necessity probes, AgentAbstain-style action failures, latent abstention probes, and hidden-state control already occupy the latent-awareness-to-policy gap.

- **Evaluation repetitions vs independent scientific units.**  
  **Question:** Do repeated generations or benchmark items create the independent units implied by common confidence intervals and significance tests?  
  **Why not:** modern NLP evaluation work already models cluster dependence, data/model uncertainty, and ranking uncertainty. A field-practice audit alone is not a new Main-level scientific object.

- **Sampling noise vs real study heterogeneity in evidence synthesis.**  
  **Question:** Can an LLM distinguish disagreement caused by sampling noise from genuine effect heterogeneity that should alter pooling or subgroup conclusions?  
  **Why not:** as a direct test this is mostly statistical competence; as an end-to-end consequence, recent systematic-review work already propagates extraction errors into pooled effects and heterogeneity estimates.

- **Belief stability vs correct belief revision.**  
  **Question:** Does higher cross-step consistency mean better logical-state maintenance or simply stronger commitment to an earlier answer?  
  **Why not:** recent belief-consistency, Belief-R, and choice-supportive / opposing-evidence work jointly own the preserve-versus-update trade-off.

- **Repeated / correlated evidence counted as independent support.**  
  **Question:** Does seeing the same originating evidence through many correlated sources make the model treat it as many independent observations?  
  **Why not:** duplicate of the K010 scientific parent; 2026 RAG / grouped-evidence work directly studies dependent evidence inflating support. Do not assign a new K ID.

- **One paper is not one study.**  
  **Question:** In scientific synthesis, does an LLM double-count multiple reports from the same underlying study?  
  **Why not:** duplicate hit on archived L06. Systematic-review work already warns against paper-level over-weighting and clusters multiple reports by study before extraction/synthesis. Do not reopen L06.

- **Benchmark overlap: association or causal score inflation?**  
  **Question:** Does training on benchmark-like examples causally create the apparent capability increase attributed to contamination?  
  **Why not:** controlled contamination-injection work already manipulates timing, amount, and format and measures causal score inflation; newer work studies re-emergence after post-training.

- **Rubric reasoning vs the judge's actual scoring policy.**  
  **Question:** Are criterion-level judgments the causes of an LLM judge's final score, or merely explanations produced alongside it?  
  **Why not:** rubric interference, criterion-level meta-evaluation, and rubric dependency/redundancy already occupy the core object.

- **SAE features: stable mechanisms or arbitrary decompositions?**  
  **Question:** Are named SAE features reproducible properties of the representation, or seed/basis-dependent decompositions of a more stable subspace?  
  **Why not:** 2026 work directly studies feature consistency across seeds and finds unstable features with more reproducible subspaces. The intended identifiability question is already occupied.

- **Generation destroys an already-good decision structure.**  
  **Question:** When does autoregressive generation systematically damage a ranking / decision structure that is already present before generation?  
  **Why not:** generation–discrimination gap is an established parent, now studied across classification, preference, safety, and self-guided optimization. This also collapses into previously rejected capability/readout and latent-to-policy gaps.

- **Circuit overlap as an identifiable mechanism claim.**  
  **Question:** If two tasks are said to share a circuit, is that overlap a property of the model function or an artifact of one parameterization/component decomposition?  
  **Why not:** 2026 circuit-consistency/specificity and explicit mechanistic-identifiability work already study circuit overlap, uniqueness, and non-uniqueness.

- **RLVR token entropy vs actual exploration.**  
  **Question:** Does token-level entropy collapse mean the reasoning policy truly loses strategy diversity?  
  **Why not:** recent work directly shows token entropy can collapse while semantic/strategy entropy remains high and proposes semantic entropy as the better exploration quantity. A tokenizer-invariance refinement is too narrow.

- **MCQ recognition vs free recall.**  
  **Question:** Do answer options merely read out knowledge already accessible to the model, or provide the cue that makes otherwise inaccessible knowledge retrievable?  
  **Why not:** *Empty Shelves or Lost Keys?* explicitly profiles encoding / recognition / recall and uses multiple-choice recognition to show that many reverse-question errors are recall failures; MCQ mechanistic work further localizes answer-selection computation. The remaining cue mechanism is too narrow for a new parent.

## Portfolio after this pass

No new candidate promoted. Current portfolio remains **L16 / L17 / L22 bounded pilots**, with **L21 serious but blocked before compute**. Continue broad search rather than lowering the bar.
