# Whose Rule Is It? — code

Anonymous submission. This archive contains the code for all experiments in the paper and the script that draws the
main-text figures and appendix tables from their outputs.

All experiments are forward passes over frozen public checkpoints (Qwen3, Mistral, Llama-3.1, Gemma-2; FP32, eager attention); no model is trained.
Each experiment script builds its prompts from public data, runs the attention interventions and writes
`contexts.jsonl`, `behavior.jsonl` (per-query logits and argmax tokens for every condition) and `analysis.json`
(prompt-level bootstrap intervals).

## Scripts and paper sections

| Script | Paper |
|---|---|
| `e121_sst_materials.py` | SST-5 prompt construction (Appendix B) |
| `e123_natural_source_function_policy.py` | §3 (Figure 2), §5 (Table 2, Figures 4, 5a) |
| `e121_natural_sentiment_mechanism.py` | §4.1 reconstruction (Figure 3), §4.3 association content |
| `e120_operation_necessity.py` | §4.2 native operation on controlled reviews (Table 1) |
| `e132_cross_source_edges.py` | §4–5 edge-type isolation, label-word role swap, layer bands, attention mass |
| `e125_public_output_schema_coordination.py` | §5 public word-set table (Figure 5b) |
| `e127_shared_output_cache_composition.py` | §5 encodings formed together (Appendix H) |
| `e122_source_preserving_formation.py` | two-aspect reviews (Appendix G) |
| `e131_mechanism.py`, `e131_native.py`, `e131_function.py`, `e131_dispatch.py` | the same engines for Qwen3-32B and Llama-3.1-70B (multi-GPU) |
| `e132_merge.py` | merges runs split over several GPUs (`--shard k/n`) and runs the analysis |
| `run_gemma.py` | runs any engine on Gemma-2 with the beginning-of-sequence token prepended to the prompt |
| `e123_wave_report.py`, `gemma_full_output.py` | full-vocabulary accuracy summaries of the policy runs |
| `flip_single_source.py`, `instruction_control.py` | per-query magnitudes, flip rates, single-source accuracy and the instruction control |
| `paper_figures_v2.py` | figures and appendix tables from the outputs |

The remaining files are shared helpers (prompt header, bootstrap, reconstruction statistics).

## Running

```bash
pip install -r requirements.txt
# models: download the checkpoints listed in Appendix A to models/<name>
python code/e123_natural_source_function_policy.py --model models/Qwen3-8B --out results/e123/qwen3_confirmation \
    --n 32 --seed 123101 --materials validation
python code/e132_cross_source_edges.py --model models/Qwen3-8B --out results/e132/qwen3_confirmation \
    --n 32 --seed 132101 --materials validation
python code/paper_figures_v2.py
```

`--materials discovery` builds development prompts (validation split queries) and `--materials validation` builds
confirmation prompts (test split queries). SST-5 is read from the Hugging Face datasets cache of `SetFit/sst5`; set
`SST5_ARROW_DIR` to its Arrow directory if it is elsewhere. The seeds of every reported run are given in the paper's
appendix. Large models use `device_map="auto"` across the visible GPUs.
