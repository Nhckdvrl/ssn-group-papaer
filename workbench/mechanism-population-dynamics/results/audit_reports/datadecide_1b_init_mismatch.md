# DataDecide 1B: six runs do not start from the initialization shared by their seed label

**Summary.** For the 1B DataDecide models, 69 of the 75 (recipe × seed) runs share their seed's initialization across recipes (published `step0-seed-<seed>` is identical to the same seed's `c4` step0). Six runs do not. They form three pairs, each pair sharing an identical but otherwise unregistered initialization:

| pair | seed label |
|---|---|
| `dclm-baseline-qc-7p-fw2`, `dclm-baseline-qc-7p-fw3` | `default` |
| `dolma1_7-no-math-code`, `dolma1_7-no-reddit` | `default` |
| `falcon-and-cc-qc-orig-10p`, `falcon-and-cc-qc-tulu-10p` | `large-aux-3` |

**Evidence** (Pearson correlation of `model.transformer.blocks.5.att_proj.weight`, read from the published safetensors by HTTP range request):
- Published `step0` of each of the six runs vs. the `c4` step0 of *each* of the three seeds: |r| ≤ 0.0004. (Ordinary recipes, e.g. `dolma1_7` and `dclm-baseline`, give r = 1.0 with their own seed's `c4` step0.)
- Within each pair, the published step0 tensors are identical (r = 1.0); across pairs r ≈ 0.
- The six runs do train from their own published step0: step2500 vs. own step0 r = 0.23–0.24, the same as ordinary runs (0.23).

**Why it matters.** The seed labels are naturally read as "same initialization across recipes" (and this holds for 69/75 runs), which is what seed × data analyses rely on. For these six runs the seed label does not identify the initialization. It may be intended (the card does not promise shared initialization across recipes), but it would help to document it, or to state which initialization these runs used. We only checked the 1B size.

**Reproduce:** read one tensor per checkpoint via `huggingface_hub.hf_hub_url(..., revision="step0-seed-default")` with an HTTP `Range` request on the safetensors shard (header length in the first 8 bytes, then `data_offsets` from the JSON header).
