# pythia-410m-seed3 / seed4: weights are reset to their own step0 initialization mid-training (step75000→76000 and step122000→123000)

**Summary.** In the PolyPythias 410M runs `seed3` and `seed4`, the published checkpoints immediately after the reported "outlier" events are essentially the run's own **step0 initialization**, not a continuation of the previous checkpoint. This looks like a resume-from-the-wrong-checkpoint (or a re-initialization) during training rather than a loss spike / training instability. All later checkpoints of these two runs are therefore models trained from initialization for only ~67k (seed3) / ~20k (seed4) further steps, at an already decayed learning rate.

**Evidence** (cosine similarity of flattened weights, float64, from the published `pytorch_model.bin` of each branch; tensors: `embed_in`, layer-5 `query_key_value`, layer-12 `dense_h_to_4h`, layer-20 `attention.dense`, `embed_out`):

| run | cos(step before, step after) | cos(step after, step0) | cos(step before, step0) |
|---|---|---|---|
| seed3, 75000 → 76000 | 0.125 / 0.181 / 0.303 / 0.018 / 0.218 | **0.929 / 0.982 / 0.990** / 0.533 / 0.705 | 0.089 / 0.184 / 0.302 / 0.025 / 0.066 |
| seed4, 122000 → 123000 | 0.100 / 0.147 / 0.278 / 0.025 / 0.132 | **0.984 / 0.995 / 0.999 / 0.965** / 0.897 | 0.077 / 0.145 / 0.277 / 0.023 / 0.060 |
| seed1 (control), 75000 → 76000 | 0.995 / 0.997 / 0.997 / 0.995 / 0.996 | 0.089 / 0.204 / 0.306 / 0.027 / 0.066 | 0.089 / 0.204 / 0.307 / 0.027 / 0.066 |

- Weight norms also drop at the event (step-after / step-before norm ratio for seed3: 0.65 / 0.66 / 0.73 / 0.17 / 0.92; seed4: 0.76 / 0.74 / 0.82 / 0.11 / 0.85), while the control seed stays at 1.00.
- Final checkpoints (step143000) vs. their own step0: normal 410M seeds give cos ≈ 0.075–0.079 (embedding), 0.17–0.18 (layer-0 QKV), 0.25–0.28 (layer-12 MLP); seed3 gives 0.49 / 0.61 / 0.71 and seed4 0.89 / 0.94 / 0.97, consistent with only ~67k / ~20k steps of training after the reset. No other size (14M–160M, 40 runs) shows a late reset by this end-point test.

**Why it matters.** The PolyPythias paper (Section 3/5, Appendix A) identifies 410M seed3 and seed4 as the only outlier runs and attributes them to loss spikes / training instability. If the weights were reset to initialization, the outlier behaviour (loss jump, degraded representations, poor final performance) is explained by the reset itself, and analyses of these two seeds as "unstable training runs" would need to be revisited. Anyone using `pythia-410m-seed3` (≥ step76000) or `pythia-410m-seed4` (≥ step123000) as an ordinary seed is affected.

**Reproduce** (downloads 2 × 3 checkpoints of ~0.9 GB):
```python
import torch
from huggingface_hub import hf_hub_download
def load(repo, rev):
    return torch.load(hf_hub_download(f"EleutherAI/{repo}", "pytorch_model.bin", revision=rev), map_location="cpu", weights_only=True)
k = "gpt_neox.layers.5.attention.query_key_value.weight"
cos = lambda a, b: torch.nn.functional.cosine_similarity(a[k].double().flatten(), b[k].double().flatten(), 0).item()
s0, a, b = (load("pythia-410m-seed4", r) for r in ("step0", "step122000", "step123000"))
print(cos(a, b), cos(b, s0), cos(a, s0))   # ≈ 0.147, 0.995, 0.145
```

Related but distinct: #203 (decoupled 160M weight-seed runs not continuing from their own step0).
