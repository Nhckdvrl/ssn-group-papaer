# Which Head Takes Which Role? Initialization Leaves a Trace in Attention-Head Specialization — code and results

Anonymous submission. This archive contains the code for the experiments in the paper, the per-model measurements and
analysis outputs they produced, and the scripts that draw every figure and table from those outputs.

```
code/      measurement, training and analysis scripts (Python)
results/   per-model measurements (JSON) and analysis outputs used in the paper
cache/     lists of the DataDecide models and checkpoints used; other inputs are downloaded (see below)
```

## Reproduce the figures and tables (CPU, no downloads)

```bash
pip install -r requirements.txt
cd code
python make_figures.py    # -> outputs/figures/*.pdf
python make_tables.py     # -> outputs/tables/*.tex
```

The analyses run on CPU from the included measurements, for example `python crossing_1b_verified.py`,
`python more_roles_analyze.py`, `python strongest_head.py`, `python seed_identification.py`, `python critical_period.py`,
`python warmup_window.py`, `python sgd_temperature.py`, `python lockin_pythia.py`, `python flan_layout.py --analyze`.

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
(`--family hf` for Pythia and OLMo 2; `download.py` fetches a job list in advance). The DataDecide checkpoint used at
each size is listed in `cache/datadecide/datadecide_plan.json` and in the paper's size table.

Controlled pretraining: see the usage block of `controlled_pretraining.py`. The early-window experiments are branches
of a parent run that saves its state (`--save-branch-states`), e.g. noise as large as the weights at step 250
(`--branch 250 --eps 1`), a switch of corpus (`--branch 250 --to-corpus code --to-order 1250`), a longer warm-up
(`--warm 1000`) and a fresh optimizer at the branch point (`--reset-opt`).

Initialization baselines: `python identification_baselines.py --worker 0` stores, per model, a weight sample and a
SeedPrints fingerprint (about 2.4 GB in total for the 761 models, not included here); `--analyze` then writes
`results/identification_baselines/analysis.json`, which is included. `python audit_all_sizes.py` reads single weight
tensors of the public checkpoints by HTTP range request (no GPU).

## Scripts by section of the paper

| Paper | Scripts |
|---|---|
| §2 head-role maps, agreement, chance baseline (App. B, C) | `head_roles.py`, `more_roles.py`, `similarity.py` |
| §2, App. A: initialization audit at every size | `audit_step0.py`, `audit_training_start.py`, `audit_unlisted_init.py`, `audit_all_sizes.py`, `audit_pythia_step0.py` |
| §3 heads follow the initialization, Fig. 1, Fig. 2a, Table 1, App. B, D (Table 6) | `crossing_1b.py`, `crossing_1b_verified.py`, `more_roles_analyze.py`, `crossing_sizes.py`, `top_head.py`, `strongest_head.py`, `pythia_small.py`, `pythia_large.py` |
| §3 identifying the initialization, Fig. 2b, App. E (Table 7) | `seed_identification.py`, `seed_identification_early.py`, `identification_baselines.py` |
| §3 what carries the trace, Fig. 2c | `coordinates_vs_content.py`, `weight_retention.py`, `copying_algorithm.py` |
| §4 when the assignment is fixed, Fig. 3, Table 2, App. F, G (Fig. 6) | `controlled_pretraining.py`, `critical_period.py`, `warmup_window.py`, `lockin_datadecide.py`, `early_checkpoints.py`, `pythia_checkpoints.py`, `lockin_pythia.py`, `init_predictors.py`, `init_gradients.py` |
| §5 corpus similarity, Fig. 4 | `corpus_samples.py`, `corpus_distance.py`, `corpus_distance_disjoint.py`, `content_vs_function_words.py` |
| §5 gradient noise, App. H (Fig. 7, Table 8) | `controlled_pretraining.py --bs / --lr`, `sgd_temperature.py` |
| §6 behaviour follows the corpus, Table 3, App. I (Table 9) | `crossing_1b.py` (circuit strength), `induction_onset.py`, `no_lucky_seeds.py`, `context_trust_1b.py`, `seed_effect_behaviour.py` |
| §6.1 Flan and the `Question:` template, Fig. 5, Table 4, App. J (Fig. 8, Tables 10, 11) | `habit_format.py`, `habit_templates.py`, `flan_layout.py`, `habit_sizes.py`, `habit_pretraining.py`, `habit_popqa.py`, `habit_nqswap.py`, `habit_olmo2_public.py`, `habit_continued_pretraining.py` |
| §8 transfer of head-level findings; App. B ablation-defined roles | `ablation_transfer.py` |
| Figures and tables | `make_figures.py`, `make_tables.py` |
| Shared code | `common.py`, `datadecide.py`, `prompts.py`, `similarity.py`, `download.py`, `prepare_data.py` |

## Third-party artifacts and licences

The code downloads and uses, without redistributing them: DataDecide models (Apache-2.0), DataDecide data recipes and
evaluation results (ODC-BY), Pythia and PolyPythias (Apache-2.0), OLMo 2 and OLMo-1B-0724 (Apache-2.0), Qwen2.5-1.5B,
SmolLM2-1.7B and Gemma-2-2B (their respective licences), ParaConflict (Apache-2.0), NQ-Swap (MIT), PopQA (as released
by its authors) and NeelNanda/pile-10k. Template-marker counts in Dolma 1.7 come from the public infini-gram API.
`results/` contains only numbers derived from these artifacts (attention-based scores, log-probabilities, item
indices, weight correlations, corpus statistics).

## Environment

Python 3.12; package versions in `requirements.txt`. GPUs: NVIDIA A100 80GB.

## AI assistance

An AI coding assistant helped write and refactor parts of this code; all code was checked and run by the authors.
