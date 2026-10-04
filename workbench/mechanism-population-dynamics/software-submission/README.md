# Born to Copy, Taught to Trust: What Is Innate in a Language Model — code and results

Anonymous submission. This archive contains the code for the experiments in the paper, the per-model measurements and
analysis outputs they produced, and the scripts that draw every figure and table from those outputs.

```
code/      measurement, training and analysis scripts (Python)
results/   per-model measurements (JSON) and analysis outputs used in the paper
cache/     lists of the DataDecide models used; other inputs are downloaded (see below)
```

## Reproduce the figures and tables (CPU, no downloads)

```bash
pip install -r requirements.txt
cd code
python make_figures.py    # -> outputs/figures/*.pdf
python make_tables.py     # -> outputs/tables/*.tex
```

The analyses run on CPU from the included measurements, for example `python crossing_1b_verified.py`,
`python more_roles_analyze.py`, `python seed_identification.py`, `python critical_period.py`,
`python sgd_temperature.py`, `python lockin_pythia.py`, `python seed_effect_behaviour.py`.

## Re-run the measurements (GPU)

All measurements are forward passes over public checkpoints, which are downloaded from the Hugging Face Hub on first
use; the controlled experiments train small models from scratch. Set `MECHPOP_CACHE` to a download directory
(default `./cache`).

1. `python prepare_data.py probes` — natural-text probe material (2,000 windows of `NeelNanda/pile-10k`).
2. `python prepare_data.py corpora` — 400M-token prefixes of single DataDecide source files (web text, code, papers,
   books, Flan) for controlled and continued pretraining.
3. For the corpus statistics, place DataDecide's recipe definitions (`olmo/data/named_data_mixes.py` from the
   `DataDecide` branch of github.com/allenai/OLMo, Apache-2.0) in `$MECHPOP_CACHE/datadecide/` and run
   `python corpus_samples.py stats`.
4. For the benchmark analysis, place DataDecide's evaluation results (`allenai/DataDecide-eval-results`,
   `macro_avg` table) in `$MECHPOP_CACHE/datadecide/evals/data/`.

Head-role maps of one model:
`python head_roles.py --family dd --repo allenai/DataDecide-c4-1B --rev step69369-seed-default --out crossing_1b --name c4-1B__default`
(`--family hf` for Pythia and OLMo 2; `download.py` fetches a job list in advance). Controlled pretraining: see the
usage block of `controlled_pretraining.py`.

## Scripts by section of the paper

| Paper | Scripts |
|---|---|
| §2 head-role maps, which-head agreement (App. B) | `head_roles.py`, `more_roles.py`, `similarity.py` |
| §2, App. A: auditing the suites | `audit_step0.py`, `audit_training_start.py`, `audit_unlisted_init.py`, `audit_pythia_step0.py`, `weight_retention.py` |
| §3 Finding 1, Fig. 1, Table 1 | `crossing_1b.py`, `crossing_1b_verified.py`, `more_roles_analyze.py`, `crossing_sizes.py`, `top_head.py`, `pythia_small.py`, `pythia_large.py` |
| §3 Finding 2, Fig. 2b | `seed_identification.py`, `seed_identification_early.py`, `early_checkpoints.py` |
| §3 Finding 3, Fig. 2c | `coordinates_vs_content.py`, `weight_retention.py` |
| §3 shared copying algorithm | `copying_algorithm.py` |
| §4 Finding 4, Table 2, App. G | `crossing_1b.py` (circuit strength), `induction_onset.py`, `no_lucky_seeds.py`, `context_trust_1b.py`, `seed_effect_behaviour.py` |
| §4.1 the `Question:` habit, Fig. 4, Tables 3, 9, 10 | `habit_format.py`, `habit_templates.py`, `habit_sizes.py`, `habit_pretraining.py`, `habit_popqa.py`, `habit_nqswap.py`, `habit_olmo2_public.py`, `habit_continued_pretraining.py`, `habit_heads.py` |
| §5 critical period, Fig. 3, Table 6 | `controlled_pretraining.py`, `critical_period.py`, `lockin_datadecide.py`, `pythia_checkpoints.py`, `lockin_pythia.py`, `init_predictors.py`, `init_gradients.py` |
| §5 SGD temperature, App. F, Table 7 | `controlled_pretraining.py --bs / --lr`, `sgd_temperature.py` |
| §6 corpus content, Fig. 5, Table 5 | `corpus_samples.py`, `corpus_distance.py`, `corpus_distance_disjoint.py`, `content_vs_function_words.py` |
| §8 transfer of component findings | `ablation_transfer.py` |
| Figures and tables | `make_figures.py`, `make_tables.py` |
| Shared code | `common.py`, `datadecide.py`, `prompts.py`, `similarity.py`, `download.py`, `prepare_data.py` |

## Third-party artifacts and licences

The code downloads and uses, without redistributing them: DataDecide models (Apache-2.0), DataDecide data recipes and
evaluation results (ODC-BY), Pythia and PolyPythias (Apache-2.0), OLMo 2 and OLMo-1B-0724 (Apache-2.0), Qwen2.5-1.5B,
SmolLM2-1.7B and Gemma-2-2B (their respective licences), ParaConflict (Apache-2.0), NQ-Swap (MIT), PopQA (as released
by its authors) and NeelNanda/pile-10k. `results/` contains only numbers derived from these artifacts
(attention-based scores, log-probabilities, item indices, corpus statistics).

## Environment

Python 3.12; package versions in `requirements.txt`. GPUs: NVIDIA A100 80GB.

## AI assistance

An AI coding assistant helped write and refactor parts of this code; all code was checked and run by the authors.
