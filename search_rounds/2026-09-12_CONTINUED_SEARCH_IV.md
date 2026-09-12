# 2026-09-12 — Continued Topic Search IV

**Target:** ACL / EMNLP / NAACL Main  
**Search mode:** continue after L29; no survivor quota; mechanism-first; owner assassination before promotion.  
**Repository state at round start:** `main` = `805df8b786943682f47773910a846165ec2ec0b5`.

This round continued searching rather than stopping at L29. It deliberately avoided data / benchmark / RAG / metric / workflow questions and focused on stable post-training anomalies, representation→causal-use gaps, SAME-QUANTITY tensions, and old empirical assumptions under modern reasoning regimes.

## Hard stop requested by user

### Temporal Forgetting — DO NOT RESURRECT

The user explicitly reports that this route has already been attempted and is not workable for this project. Treat the whole parent as a prior failed route. Do **not** reopen it as:
- forgotten ≠ erased;
- earlier-checkpoint ability vs final-checkpoint suppression;
- old-prefix / checkpoint rescue;
- capability-shift explanation;
- temporal sampling mechanism;
- another renamed checkpoint-forgetting question.

This is a search-space hard ban for current open-ended search, not a request for a new K-ID.

## Hooks investigated and rejected

### 1. Instruction tuning creates a strong prior that harms in-context override

**Hook:** Why can post-training improve instruction following while reducing the ability to override the model through new context/examples?

**Why not:** Findings 2024 work already links instruction tuning to loss of ICL / catastrophic forgetting; EMNLP 2025 studies partial adaptation; ICLR 2026 Spectrum Tuning centralizes the strong-post-training-prior / reduced-context-override phenomenon. The mechanism parent is occupied.

**Verdict:** DROP.

### 2. Warmth / empathy post-training lowers factual accuracy

**Hook:** Why can a style/personality-oriented post-training intervention alter factual judgment and increase agreement with a user's false premise?

**Mother:** 2026 Nature work finds robust factual-accuracy degradation after warmth/empathy tuning across multiple model scales.

**Why not:** Persona Vectors and subsequent persona steering already connect fine-tuning to predictable movement along sycophancy / hallucination / personality directions. A mechanism follow-up would reviewer-compress to the Nature phenotype plus persona-vector steering.

**Verdict:** DROP.

### 3. Multi-question stress / failure to reset between independent problems

**Hook:** Why can a strong single-problem reasoner collapse when several independent problems are packed into one reasoning episode, and why can reasoning post-training amplify the collapse?

**Why not:** duplicates the project's already-rejected `Many inputs: learning signal or processing burden?` parent. Multi-instance processing, set-size/working-memory, and multi-problem evaluation already occupy the main explanatory space.

**Verdict:** DROP / anti-resurrection.

### 4. RL exploration disappears at the final layer but remains in intermediate layers

**Hook:** Does reasoning post-training erase strategy exploration, or merely suppress its readout into the final policy?

**Why not:** current 2026 work already directly contrasts final entropy with intermediate-layer posterior entropy and recovers exploration by latent decoding; semantic/strategy entropy versus token entropy is also a direct current research object. This duplicates the project's rejected RLVR entropy/exploration neighborhood.

**Verdict:** DROP.

### 5. Generation–evaluation / production–verification gap

**Hook:** Why can a model generate a correct solution yet evaluate/verify related solutions poorly?

**Why not:** 2025–2026 work directly centralizes the generation/evaluation gap, answer-confirmation bias, hidden-state probes and causal interventions. The old “verification is easier than generation” assumption is already under active direct revision.

**Verdict:** DROP.

### 6. SFT teaches reasoning format rather than reasoning

**Why not:** direct EMNLP/ACL-era owner papers already make format imitation / reasoning imitation the main scientific statement.

**Verdict:** DROP.

### 7. High SFT competence makes a worse RL starting point

**Hook:** Why can a checkpoint with better supervised performance have lower later RL learnability?

**Why not:** 2026 work already explains this neighborhood using loss of plasticity, overconfidence, sharper landscapes, and plasticity ceilings. The mechanistic parent is no longer open enough.

**Verdict:** DROP.

### 8. Test-time exposure bias / off-trajectory reasoning fragility

**Why not:** current reasoning-distillation and on-policy work directly studies off-policy / on-policy exposure, backtracking and recovery. Remaining cells are training-method details, not a new scientific parent.

**Verdict:** DROP.

### 9. Composition of already learned skills

**Hook:** Why can a model learn A and B yet fail A∘B / A+B?

**Why not:** ICLR 2026 work directly localizes two-stage compositional circuits after CoT training and RL work explicitly studies composition of existing skills. The old compositional-generalization parent is occupied at the desired mechanism level.

**Verdict:** DROP.

### 10. Stronger reasoning resists direct persuasion but is vulnerable to curated truthful evidence

**Hook:** Why might reasoning act as a defense against an externally asserted conclusion but as an attack surface when the model constructs the conclusion itself from selected true fragments?

**Pressure:** AAAI/2026 reasoning-disagreement work reports greater resistance to persuasion; ACL 2026 Outstanding *Lying with Truths* reports greater susceptibility of reasoning-specialized models to selectively presented truthful evidence.

**Blocker:** the published studies are not SAME-QUANTITY: tasks, evidence structure and estimands differ. A matched same-question / same-evidence intervention would be required before claiming a contradiction.

**Owner risk:** 2026 *The Self-Correction Illusion* already holds a wrong claim byte-identical and shows very large own-thought vs user/tool/memory correction asymmetries. Source/provenance/self-commitment alone is therefore not an open mechanism.

**Verdict:** MAYBE only if a qualitatively distinct evidence→self-constructed-bridge computation can be identified; otherwise DROP. Not candidate-worthy now.

### 11. Explicit corrective rationale helps under SFT but hurts in-context learning

**Pressure:** Findings EMNLP 2024 shows mistake explanations can help supervised reasoning training; EMNLP 2025 Main *No Need for Explanations* shows explicit corrective rationales can hurt in-context learning compared with letting the model infer the correction.

**Tempting RQ:** Why does the same kind of corrective information help when written into weights but over-constrain when left in context?

**Why not promoted:** the two papers do not establish a SAME-QUANTITY sign reversal under matched supervision/model conditions. ICLR/ACL 2026 work also directly compares ICL versus fine-tuning learning dynamics / inductive biases. A matched experiment risks reviewer compression to those three ingredients.

**Verdict:** MAYBE-BUT-NOT-SERIOUS.

### 12. Same capability, different source of compute: parameter scale vs test-time reasoning

**Mother pressure:** *Monitoring Monitorability* finds that, at approximately matched capability, a smaller model at higher reasoning effort can be easier to monitor than a larger model at low reasoning effort.

**Tempting RQ:** Does the same behavioral capability arise through systematically different computational routes when obtained by parameter scaling versus externalized test-time reasoning?

**Why not promoted:** the mother already frames the model-size / reasoning-effort distinction; September 2026 work on opaque serial depth now explicitly centralizes where cognition can occur outside textual bottlenecks. Additional work on internal CoT and latent reasoning further crowds the proposed mechanism. The obvious study reviewer-compresses to `Monitoring Monitorability + Opaque Serial Depth + causal interventions`.

**Verdict:** MAYBE at most; currently insufficient independent contribution.

### 13. Generic post-training mechanism/circuit rerouting

**Hook:** Can two behaviorally similar checkpoints implement the same capability through different causal circuits after SFT/DPO/RL?

**Why not:** ACL 2026 *Patches of Nonlinearity* studies SFT/DPO instruction representations and circuit selection; ICML 2026 work directly compares RL vs SFT circuit preservation/reorganization; 2026 ARM→masked-diffusion work studies task-dependent mechanism shift. Generic circuit rerouting is no longer an open parent.

**Verdict:** DROP broad parent.

## Round status so far

No new SERIOUS candidate beyond existing L29. Two ideas remain only as weak MAYBEs (corrective-rationale substrate flip; parameter-scale vs test-time-compute mechanism difference), neither strong enough for `RESEARCH_TOPIC_SELECTION.md`.

Continue searching. Do not lower the bar and do not reopen Temporal Forgetting.