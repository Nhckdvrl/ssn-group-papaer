# 2026-09-13 — Related-Work Minimal-Move Search

**Purpose:** rolling anti-duplication log for the search style adopted after simplifying topic discovery: read a strong ACL/EMNLP/NAACL paper, isolate one surprising/load-bearing statement, trace its nearest 3–5 related works, and ask what one important sentence is still missing. Kill immediately when the answer is already naturally implied by nearby work.

**Reporting rule:** only a fully selected `PILOT-AUTHORIZED — E01 ONLY` topic is user-facing as a found topic. Everything below is dead/non-actionable.

---

## Hook A — Why later training makes LLMs harder to quantize

**Status:** `DROP — SUCCESSOR OWNS THE NEXT SENTENCE`

### Origin
ACL 2025, *Low-Bit Quantization Favors Undertrained LLMs*, reports a stable and counterintuitive effect across many checkpoints: undertrained/larger models can be more robust to low-bit post-training quantization than more fully trained models.

### Why it dies
The natural next question is whether quantization brittleness is caused simply by seeing more tokens or by a specific part of the optimization trajectory. ICLR 2026 *Training Dynamics Impact Post-Training Quantization Robustness* already moves directly onto this question, showing that learning-rate decay / training dynamics materially govern quantization robustness and using controlled training comparisons rather than leaving the effect as a descriptive token-count law.

### Reviewer compression
> ACL 2025 establishes the training-progress anomaly; ICLR 2026 already identifies training dynamics / LR decay as a load-bearing condition and intervenes on it.

**Anti-resurrection:** do not reopen as `why does more training hurt quantization?`, `token count causes quantization brittleness`, or a generic checkpoint-geometry explanation without a same-quantity contradiction to the ICLR-2026 account.

---

## Hook B — Train then revert beats freeze then train

**Status:** `DROP — GENERAL OPTIMIZATION PRINCIPLE TOO NATURAL`

### Origin
Independent work in cross-lingual/task-composition and 2026 multilingual continual pretraining reports a striking asymmetry: allowing parameters to update during adaptation and reverting selected changes afterward can outperform freezing those parameters from the beginning.

### Why it dies
The most natural interpretation is already supplied by a broad, mature optimization principle: temporary degrees of freedom can ease optimization / provide overparameterized scaffolding even when the corresponding final parameter changes are not needed. This is closely analogous to dense-train-then-prune / optimize-in-a-larger-space-then-constrain behavior.

The exact LLM implementation may be new, but the strongest successful result would compress to `extra train-time freedom helps find a better solution, then the extra coordinates can be removed` unless a more specific contradictory law is first established.

### Reviewer compression
> Known overparameterized/dense optimization advantage + post-hoc constraint/pruning = train-then-revert can beat freeze-then-train.

**Anti-resurrection:** do not reopen as `temporary parameter scaffolding`, `ephemeral weight updates`, or `reverted parameters still helped learning` without evidence that the phenomenon violates the generic optimization account.

---

## Hook C — Why wrong answers / negative reasoning trajectories can teach

**Status:** `DROP — 2025–2026 LINE ALREADY CENTRALIZES THE PHENOMENON`

### Origin
EMNLP 2025 *No Need for Explanations: LLMs can implicitly learn from mistakes in-context* reports that wrong-answer demonstrations can be useful and that adding corrective rationales may even overconstrain performance. ACL 2026 *Learning from Mistakes: Negative Reasoning Samples Enhance Out-of-Domain Generalization* shows negative reasoning samples can improve OOD reasoning and analyzes optimization/policy-entropy changes.

### Why it dies
The obvious next sentence — `why can incorrect/negative examples improve learning rather than merely inject noise?` — is already the center of this line. The 2026 work connects negative samples to slower loss descent / reduced overfitting and substantially higher policy entropy, then operationalizes the insight in a method.

### Reviewer compression
> EMNLP 2025 establishes useful mistakes without explicit correction; ACL 2026 establishes negative-trajectory OOD gains and a training-dynamics / exploration account.

**Anti-resurrection:** do not reopen generic `learning from mistakes`, `wrong rationales help`, `negative CoT increases diversity`, or `why bad examples regularize reasoning` without a genuinely incompatible quantity/result.

---

## Hook D — Which formal-language property makes pre-pretraining useful?

**Status:** `DROP — SUCCESSOR ALREADY BREAKS AND REPLACES THE 2025 EXPLANATION`

### Origin
ACL 2025 Outstanding *Between Circuits and Chomsky* argues that useful formal-language pre-pretraining depends on hierarchical dependency structure plus compatibility with the model's computational limitations, and reports downstream natural-language sample-efficiency gains.

### Why it dies
ACL 2026 *Language Acquisition Device in Large Language Models* provides exactly the human-paper move we would want to make: it constructs a formal-language setting that violates the earlier computational-bound story yet transfers better, then advances a different explanation based on dependency-resolution accessibility / functional landmarks. Later 2026 work also reports substantial seed/setup/language instability in pre-pretraining gains.

### Reviewer compression
> 2025 states the load-bearing explanation; 2026 already supplies the counterexample and replacement explanation.

**Anti-resurrection:** do not reopen as `what synthetic grammar is best`, `is C-RASP the right bound`, or generic `why formal-language pretraining transfers` unless a new stable contradiction survives the 2026 replacement account.

---

## Search lesson

These four kills reinforce the simplified search rule:

> **Strong prior paper → one strange/load-bearing sentence → nearest related work → only the next missing scientific sentence.**

Do not turn a dead local gap into a larger synthesis merely to preserve it. Exact-intervention novelty is not enough when the answer is already naturally entailed by the literature.
