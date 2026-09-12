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

## Additional audited rejections — continuation

- **Primary-outcome switching in scientific synthesis.**  
  **Question:** Does an LLM treat a post-hoc/secondary positive outcome as equivalent evidence to a preregistered primary outcome?  
  **Why not:** outcome-switching detection from trial registries is already directly studied, while assigning a unique normative synthesis weight to preregistration status is not independently identified. The strong version lacks clean gold for the downstream weighting rule.

- **Pairwise preferences imply a global scalar utility.**  
  **Question:** Can local pairwise LLM/human preferences be treated as observations of one transitive global ranking?  
  **Why not:** non-transitivity in LLM-as-a-Judge and preference fine-tuning under cyclic/multi-objective preferences are already direct modern parents.

- **Training-path access diversity as the cause of factual recall.**  
  **Question:** Is factual recall determined by exposure count or by the diversity of contexts/access paths in which the fact appeared?  
  **Why not:** controlled pretraining work already independently manipulates factual contextual diversity and measures recall/generalization; a natural-corpus replication would compress to that parent.

- **K008 reopen with executable world-state gold.**  
  **Question:** Is an instructed action merely one feasible route to a goal or necessary across all successful plans?  
  **Why not:** new embodied planning datasets improve gold, but the operational quantity collapses to classical planning landmarks / step essentiality. **NO REOPEN K008.**

- **Grammar-constrained decoding preserves semantic preference.**  
  **Question:** Does token-level masking/renormalization preserve the model's distribution over semantic structured outputs?  
  **Why not:** Grammar-Aligned Decoding and later constrained-decoding work directly establish distribution distortion / projection tax and semantic errors caused by naive constraint masking.

- **Deduplication removes bad repetition without damaging contextual learning.**  
  **Question:** Are within-context repetitions useful learning signals while cross-sample repetitions are merely memorization-inducing duplicates?  
  **Why not:** recent induction/sparse-attention work directly distinguishes in-context from cross-sample repetition and measures their effects on emergent copying/induction. The proposed repetition-topology axis is occupied.

- **Diffusion LMs reopen autoregressive error accumulation.**  
  **Question:** Does iterative denoising reveal which reasoning failures are caused specifically by irreversible left-to-right commitment?  
  **Why not:** diffusion-CoT/error-correction and denoising-trajectory reasoning work already make revisability of earlier tokens a central advantage/analysis axis.

- **Cross-model replication count vs independent model evidence.**  
  **Question:** Does replication across many model checkpoints/fine-tunes provide independent evidence for a universal LLM behavior?  
  **Why not:** model-lineage / genealogy work already shows shared lineage predicts benchmark behavior and breaks naive independence; a paper-level audit alone is insufficient.

- **Hallucination corpus-presence taxonomy vs causal training source.**  
  **Question:** Does finding a correct/incorrect fact in pretraining-like corpora identify the causal source of a hallucination?  
  **Why not:** TrackStar-style training-data influence work already shows textual attribution/entailment and causal influence diverge, including analyses of model errors. Applying that result to HALoGEN plus expensive retraining interventions is too compressed.

- **Curriculum / data order as hidden cause of final linguistic bias.**  
  **Question:** Holding the training-data multiset fixed, can order alone determine persistent downstream inductive bias?  
  **Why not:** 2026 pretraining-order and data-scheduling work already isolates order/path dependence under fixed data/model settings.

- **Correct internal number representation but wrong numerical answer.**  
  **Question:** Are arithmetic/comparison failures caused by damaged numerical representation or by readout/verbalization?  
  **Why not:** EACL 2026 *LLMs Know More About Numbers than They Can Say* directly demonstrates strong hidden numerical representations with weaker explicit outputs and links representation improvement to verbalized accuracy.

- **Long-context success depends on compressibility into a task statistic.**  
  **Question:** Why do many-shot demonstrations benefit from long context while instance-specific evidence reasoning degrades—can the former be compressed into a low-dimensional task vector?  
  **Why not:** 2026 task-vector work directly studies when demonstrations can be compressed into static task vectors versus requiring query-conditioned/distributed information.

- **Locally correct NLI judgments form a globally coherent theory.**  
  **Question:** Can individually accurate entailment decisions be mutually inconsistent under transitivity/logical constraints?  
  **Why not:** transitive NLI self-consistency and earlier global-consistency/factor-graph methods directly own the local-to-global coherence parent.

- **RLVR selects existing reasoning or invents new reasoning.**  
  **Question:** What initial conditions decide whether RLVR merely reweights base-policy strategies or expands the reachable reasoning boundary?  
  **Why not:** this is already an explicit 2026 debate with direct papers on sparse policy selection, high-entropy fork tokens, and reasoning-boundary expansion. Remaining conditions are cells inside an active parent.

- **Program test agreement vs semantic equivalence.**  
  **Question:** Can code models distinguish programs that pass the same examples from programs that are functionally equivalent?  
  **Why not:** EquiBench and subsequent formal/code-equivalence benchmarks directly evaluate semantic program equivalence with high-confidence formal gold.

- **Same cohort reused across papers as independent evidence.**  
  **Question:** Do multiple analyses of an overlapping participant cohort constitute multiple independent evidence units?  
  **Why not:** duplicate of K010/L06 dependent-evidence / study-identity parents; meta-analysis already treats overlapping samples as dependent evidence.

- **LoRA rank-direction importance is an identifiable scientific quantity.**  
  **Question:** Do claims that specific LoRA rank directions encode/drive a skill survive gauge transformations that leave the exact weight update unchanged?  
  **Why not:** LoRA factor gauge non-identifiability is already explicit in recent work, and the scientific identity duplicates L22's broader function-preserving-basis identifiability question. Use as an L22 extension, not a new candidate.

- **Aggregate social-science effect prediction implies a valid population simulator.**  
  **Question:** Can a model predict average treatment effects while failing to reproduce the underlying response distribution?  
  **Why not:** 2026 work directly separates effect replication from full response-distribution fidelity and population-level statistical realism.

- **Self-consistency votes as independent evidence.**  
  **Question:** Do 32 reasoning samples from one policy provide 32 independent pieces of epistemic evidence?  
  **Why not:** duplicate of K049's dependence-aware aggregation parent; correlated-error and self-consistency-confidence work already studies non-independent samples.

- **Compilable autoformalization vs semantic equivalence.**  
  **Question:** Does a natural-language-to-formal translation that typechecks preserve the source statement's meaning?  
  **Why not:** FormalAlign, bidirectional-equivalence evaluation, and 2025 reliable autoformalization evaluation directly own syntactic validity versus semantic equivalence.

- **Adaptive benchmark scores remain comparable across different item sets.**  
  **Question:** If different models receive different dynamically generated questions, can their raw scores still be compared?  
  **Why not:** CAT/IRT/ATLAS-style adaptive LLM evaluation already introduces item calibration/equating specifically for this problem.

- **Benchmark item parameters are invariant across model families.**  
  **Question:** Is a single item-difficulty/discrimination scale valid across architecture families, or do items exhibit model-family DIF that can alter rankings?  
  **Why not:** very recent work directly performs family-DIF-guided benchmark recomposition and measures rank reversals among near-tied cross-family models. The intended measurement-invariance paper identity is now occupied.

- **One scalar quality score under pluralistic preferences.**  
  **Question:** Is annotator disagreement noise around one answer-quality scalar, or evidence for legitimate context/user-specific preference modes?  
  **Why not:** personalized judges, Personalized RewardBench, and preference-aware rubric learning already make evaluator personalization/pluralism a direct modern parent.

- **Behavioral equivalence does not imply equal future learnability.**  
  **Question:** Can two currently similar models react very differently to the same future fine-tuning because of hidden training-history/plasticity state?  
  **Why not:** LM plasticity work already shows equal/similar pretraining loss does not imply equal downstream adaptability, and 2026 work directly studies plasticity preservation/loss in LLMs.

- **Replication prediction vs temporal leakage.**  
  **Question:** Are LLMs forecasting whether studies will replicate or recalling later replication/publication signals from training data?  
  **Why not:** the Nature 2026 experiment-forecasting paper already performs post-cutoff/unpublished checks, and 2026 temporal-leakage work provides matched-clean-control backtesting methods.

- **Local alignment resistance as an item-level pretraining statistic.**  
  **Question:** Which pretraining statistic predicts whether a particular behavior will resist later SFT/alignment?  
  **Why not:** ACL 2025 alignment-elasticity work already ties resistance to pretraining depth/scale, while ACL 2026 compatibility-aware fine-tuning defines sample-level demonstration–policy compatibility. The remaining item-level predictor is too close to a local extension of these parents.

- **Dynamic-benchmark generator identity changes who looks best.**  
  **Question:** If an LLM generates the test set, does its identity/family systematically favor itself or related models and change evaluated rankings?  
  **Why not:** 2025 work directly deconstructs self-bias in LLM-generated test sets, including generator-side bias. Moving the same test to another benchmark domain is not a new parent.

- **Retrieval relevance vs evidence directness / transportability.**  
  **Question:** Does a retrieved study that is topically relevant to a target question necessarily provide direct evidence for the target population/intervention/comparator/outcome?  
  **Why not:** recent work explicitly constructs GRADE-PICO indirectness mismatches and tests whether retrieval/evidence agents detect and penalize them. The broad relevance-versus-directness parent is occupied.

## Portfolio after this pass

No new candidate promoted. Current portfolio remains **L16 / L17 / L22 bounded pilots**, with **L21 serious but blocked before compute**. Continue broad search rather than lowering the bar. New topic search should avoid speech/audio per current user preference.