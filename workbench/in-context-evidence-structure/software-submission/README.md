# Whose Rule Is It Anyway? — code and results

Anonymous submission. This archive contains the code of every experiment in the paper, the result files from which
all figures and appendix tables are drawn, and the scripts that draw them.

All experiments are forward passes over frozen public checkpoints (Qwen3, Mistral, Llama-3.1, Gemma-2; FP32, eager
attention); no model is trained. Each experiment script builds its prompts from public data, runs the attention
interventions and writes `contexts.jsonl`, `behavior.jsonl` (per-query logits and argmax tokens for every condition) and
`analysis.json` (prompt-level bootstrap intervals). `CODE_PROVENANCE.md` relates the code here to the versions that
produced the results.

```
code/      experiment engines, analysis and figure scripts
results/   confirmation-run outputs used by the figures and tables (same layout as written by the engines)
```

## Regenerate the figures and appendix tables (CPU, no model downloads)

```bash
pip install -r requirements.txt
python code/e125_swapped_minus_unrelated.py   # public word-set table contrasts
python code/flip_single_source.py             # per-query magnitudes, flip rates, single-source accuracy
python code/instruction_control.py            # instruction control
python code/paper_figures_v2.py               # -> outputs/figures/*.pdf, outputs/figures/numbers.json, outputs/tables/*.tex
```

## Re-run the experiments (GPU)

Download the checkpoints listed in Appendix A to `models/<name>`. SST-5 is read from the Hugging Face datasets
cache of `SetFit/sst5`; create it once with

```bash
python -c "import datasets; datasets.load_dataset('SetFit/sst5')"
```

and set `SST5_ARROW_DIR` to the Arrow directory if the cache lives elsewhere. Each engine takes `--model`, `--out`,
`--n` (16 development or 32 confirmation prompts), `--seed` and `--materials discovery|validation`; the seeds of all
reported runs are listed in Appendix A. For example:

```bash
python code/e123_natural_source_function_policy.py --model models/Qwen3-8B --out results/e123/qwen3_confirmation \
    --n 32 --seed 123101 --materials validation
python code/e132_cross_source_edges.py --model models/Qwen3-8B --out results/e132/qwen3_confirmation \
    --n 32 --seed 132101 --materials validation --shard 0/2     # shards can run on separate GPUs
python code/e132_merge.py results/e132/qwen3_confirmation         # after all shards
python code/run_gemma.py code/e123_natural_source_function_policy.py --model models/gemma-2-9b ...   # Gemma-2
```

`--large` (E132) and the `e131_*` engines place a model across all visible GPUs.

| Script | Paper |
|---|---|
| `e121_sst_materials.py` | SST-5 prompt construction (Appendix B) |
| `e123_natural_source_function_policy.py` | §3 (Figure 2), §5 (Table 2, Figure 4a) |
| `e121_natural_sentiment_mechanism.py` | §4.1 reconstruction (Figure 3), §4.3 association content |
| `e120_operation_necessity.py` (with `e115_llama_native_mechanism.py`) | §4.2 native operation on controlled reviews (Table 1) |
| `e132_cross_source_edges.py`, `e132_merge.py` | §3–§5 edge types, label-word swap, layer bands, attention mass (Figure 4b–c, Appendix I) |
| `e125_public_output_schema_coordination.py`, `e125_swapped_minus_unrelated.py` | §5 public word-set table (Figure 5) |
| `e127_shared_output_cache_composition.py` | §5 encodings formed together (Appendix H) |
| `e122_source_preserving_formation.py` (with `e118_mistral_materials.py`, `e119_criterion_scale.py`) | two-aspect reviews (Appendix G) |
| `e131_mechanism.py`, `e131_native.py`, `e131_function.py`, `e131_dispatch.py` | the same engines for Qwen3-32B and Llama-3.1-70B |
| `run_gemma.py` | runs any engine on Gemma-2, with the beginning-of-sequence token prepended to the prompt |
| `e123_wave_report.py`, `gemma_full_output.py` | full-vocabulary accuracy summaries of the policy runs |
| `flip_single_source.py`, `instruction_control.py` | analyses added after the confirmation runs (marked in the appendix) |
| `paper_figures_v2.py` | all figures and appendix tables |

The remaining files are shared helpers (prompt header and Measuring Hate Speech pools, bootstrap, reconstruction statistics).
