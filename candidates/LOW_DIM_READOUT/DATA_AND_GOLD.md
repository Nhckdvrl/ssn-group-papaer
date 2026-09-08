# Low-Dimensional Readout — Data and Gold

## 1. Load-bearing quantities

No proxy labels are required. The decisive quantities are directly measurable:
- task correctness under controlled readout interventions;
- token-level next-step likelihood / rank / margin;
- divergence between full-readout and truncated-readout token distributions;
- trajectory deviation under free generation;
- recovery under teacher forcing.

## 2. Primary tasks

Use at least three capability families:

### Knowledge / classification
- MMLU or equivalent direct-answer benchmark.

### Reading / extraction
- SQuAD-style answer extraction or QA.

### Multi-step reasoning
- GSM8K plus at least one second reasoning family (e.g. MATH/MuSiQue/BBH subset) to avoid a GSM8K-only story.

Add a **long non-reasoning generation control** so reasoning is not confounded with output length.

## 3. Models

Minimum pilot:
- one Qwen-family causal LM;
- one Llama/Mistral-family causal LM.

Prefer models close enough to the EMNLP 2025 setup for replication plus one newer reasoning-tuned model for boundary analysis.

## 4. Interventions

### A. Coordinate truncation
Remove a fixed fraction of hidden dimensions immediately before LM-head readout.

### B. Random projection / subspace-preserving compression
Keep dimensional budget comparable while avoiding coordinate-selection artifacts.

### C. Teacher-forced truncation
Feed the gold previous reasoning tokens while applying the same readout intervention at each next-token step.

### D. Local-step truncation
Apply truncation only at selected reasoning steps, then restore full readout.

### E. Answer-only vs rationale-only truncation
Apply the intervention only while generating intermediate reasoning or only at final answer tokens.

All interventions must preserve the underlying Transformer computation unless explicitly testing a second hypothesis.

## 5. Primary metrics

- exact task accuracy;
- token log-probability of gold next token;
- rank/margin of gold next token;
- KL divergence full vs truncated readout;
- first divergence position in free generation;
- downstream recovery after restoring full readout;
- accuracy under teacher forcing;
- performance as a function of output length.

## 6. Critical identification tests

### Autoregressive accumulation test
If teacher forcing restores most reasoning performance while per-step gold-token probability remains high, the free-generation collapse is largely accumulation.

### Intrinsic next-step bottleneck test
If teacher forcing still shows severe next-step degradation, reasoning genuinely requires more fragile/richer readout information.

### Geometry test
If random projection preserves reasoning substantially better than deleting arbitrary coordinates at the same dimensionality, coordinate geometry matters.

## 7. Negative controls

- long-form copying or constrained generation matched in token count;
- easy arithmetic requiring long output but little inference;
- short hard questions requiring strong reasoning but few generated tokens;
- truncation rates below/above 50%.

## 8. Data validity

Standard benchmark gold is sufficient because the scientific variable is the intervention, not an inferred semantic label.

KILL/demote if:
- original phenomenon fails to replicate across accessible models;
- GSM8K collapse disappears after correcting implementation details;
- all effects reduce to sequence length with no reasoning-specific residual;
- results vary chaotically across random masks with no interpretable account;
- the only conclusion is “more dimensions are better.”
