# OLMo-2-0425-1B: `main` is not from the same training run as the published stage1/stage2 checkpoints (and is not the base of the Instruct model)

**Summary.** The model card says `main` is the final checkpoint and that fine-tuning can start from it, and that for the 1B model only stage-2 ingredient 3 is the real mid-training run. In the published weights, however, `main` is unrelated to every `stage1-*` / `stage2-ingredient*` branch, including `stage2-ingredient3-step23852-tokens51B`, while the `-Instruct` model descends from the stage-2 ingredient-3 branch. `main` looks like a model from a different training run (different initialization).

**Evidence** (Pearson correlation of flattened tensors, float64, read from the published safetensors):

| comparison | layer-5 q_proj | layer-5 v_proj | layer-5 mlp.down_proj | embed_tokens |
|---|---|---|---|---|
| `main` vs `stage2-ingredient3-step23852-tokens51B` | 0.0003 | 0.0002 | −0.0004 | 0.0058 |
| `main` vs `stage1-step1907359-tokens4001B` | 0.0004 | — | — | 0.0059 |
| `main` vs `stage1-step0-tokens0B` | 0.0001 | — | — | 0.0024 |
| `stage1-step1907359` vs `stage2-ingredient3-step23852` | 0.960 | 0.977 | 0.971 | 0.9996 |
| `OLMo-2-0425-1B-Instruct` vs `main` | — | — | −0.0004 | — |
| `OLMo-2-0425-1B-Instruct` vs `stage2-ingredient3-step23852` | — | — | 0.995 | — |

- The configs of `main` and the stage-2 branch are identical, so this is not a format difference. The near-zero correlation also holds for `v_proj`, `down_proj` and the embeddings, which a q/k RoPE permutation in conversion would not affect.
- Functionally, `main` and `stage2-ingredient3-step23852` give different next-token distributions (mean KL 0.21 nats/token, top-1 agreement 0.78 on three short prompts), i.e. they are different models, not the same weights stored differently.
- `stage1-step0-tokens0B` vs `stage1-step1907359` gives 0.005, as expected for a single run; `main` is equally far from all branches.

**Why it matters.** Work that treats `main` as the endpoint of the released stage1 → stage2 trajectory, or as the base model of `-SFT/-DPO/-Instruct` (e.g. base-vs-instruct comparisons, training-dynamics analyses that append `main` to the checkpoint series), compares unrelated models. Could you clarify which run `main` comes from, or point `main` to the intended final checkpoint?

**Reproduce:** read one tensor per revision via `huggingface_hub.hf_hub_url("allenai/OLMo-2-0425-1B", <shard>, revision=...)` with an HTTP `Range` request, e.g. `model.layers.5.mlp.down_proj.weight`, and compute the correlation.
