# Born to Copy, Taught to Trust: What Is Innate in a Language Model — code and results

Anonymous submission. This archive contains the code for every experiment in the paper, the per-model measurements
and analysis outputs they produced, and the scripts that draw every figure and table from those outputs.

```
code/      analysis and training scripts (Python)
results/   per-model measurements (JSON) and analysis outputs used by the paper
cache/     small inputs we created (lists of the DataDecide models used); other inputs are downloaded, see below
outputs/   figures and tables regenerated from results/ by figs_acl.py and tables_acl.py
```

## Quick start: reproduce all figures and tables (CPU, no downloads)

```bash
pip install -r requirements.txt
cd code
python figs_acl.py      # -> outputs/figures/*.pdf
python tables_acl.py    # -> outputs/tables/*.tex (identical to the tables in the paper)
```

The analysis scripts also run on CPU from the included measurements, e.g. `python e35_verified.py`,
`python e59_analyze.py`, `python e61_seed_id.py`, `python e60_corpus_distance.py analyze`, `python e64_function_words.py`
(the last three also need the corpus samples described below).

## Re-running the measurements (GPU)

Measurements are forward passes over public checkpoints; controlled pretraining trains small models from scratch.
Set `MECHPOP_CACHE` to a directory for downloads (default: `./cache`). Models are fetched from the Hugging Face Hub
on first use (`prefetch.py` downloads job lists in advance).

* `python prepare_data.py probes` — natural-text probe material (2,000 windows of `NeelNanda/pile-10k`).
* `python prepare_data.py corpora` — 400M-token prefixes of single DataDecide source files for controlled pretraining.
* `$MECHPOP_CACHE/datadecide/named_data_mixes.py` — the recipe definitions of DataDecide, from the `DataDecide`
  branch of github.com/allenai/OLMo (`olmo/data/named_data_mixes.py`, Apache-2.0); needed by the corpus-statistics
  scripts (`e23_corpus_stats.py stats` downloads and caches the corpus samples).
* `$MECHPOP_CACHE/datadecide/evals/data/macro_avg-00000-of-00001.parquet` — DataDecide's released benchmark results
  (dataset `allenai/DataDecide-eval-results`), used by `e51_benchmarks.py`.

Head-role maps of any model: `python census.py --family dd --repo allenai/DataDecide-c4-1B --rev step69369-seed-default --out e35 --name c4-1B__default`
(`--family hf` for Pythia / OLMo 2). Controlled pretraining: see the usage block at the top of `e46_train.py`.

## Scripts by section of the paper

Experiment numbers (E##) are internal IDs; file names keep them so that results and code match.

| Paper | Scripts |
|---|---|
| §2 head-role maps, which-head agreement, App. B | `census.py`, `e59_roles.py` (five more roles, incl. the weight-only OV score), `fastsim.py`, `mp_common.py`, `dd_common.py` |
| §2 / App. A audits of the suites | `audit_init_start.py`, `audit_init_start2.py`, `audit_step0_all.py`, `r0_tensor_audit.py`, `audit_weight_retention.py` |
| §3 Finding 1, Fig. 1, Table 1 | `e35_census.py`, `e35_verified.py`, `e59_analyze.py`, `e45_analyze.py`, `e45_top1.py`, `e44_analyze.py`, `e58_analyze.py` |
| §3 Finding 2, Fig. 2b | `e61_seed_id.py`, `e61_early.py`, `e57_analyze.py` |
| §3 Finding 3, Fig. 2c | `e43_basis.py`, `audit_weight_retention.py` |
| §3 universal algorithm | `e55_algorithm.py` |
| §4 Finding 4, Table 2, App. G | `e35_census.py` (strength), `e54_timing.py` (onset, controlled runs), `e51_benchmarks.py`, `e36_init_behaviour.py` |
| §4.1 template habit, Fig. 4, Tables 3, 9, 10 | `e18_trait.py`, `e20_recipe.py`, `e26_factorial.py`, `e28_gating.py`, `e29_timecourse.py`, `e30_wild.py`, `e31_nocontext.py`, `e32_cues.py`, `e34_popqa.py`, `e47_flan_scale.py`, `e48_cueswap.py`, `e49_nqswap.py`, `e50_switch_attribution.py`, `infgram_counts.py` |
| §5 critical period, Fig. 3, Table 6 | `e46_train.py`, `e46_analyze.py`, `e37_analyze.py`, `e40_lockin.py`, `e39_init_predictors.py`, `e41_init_gradients.py` |
| §5 SGD temperature, App. F, Table 7 | `e46_train.py --bs/--lr`, `e62_analyze.py` |
| §6 corpus content, Fig. 5, Table 5 | `e23_corpus_stats.py`, `e60_corpus_distance.py`, `e60_disjoint.py`, `e64_function_words.py` |
| §8 transfer of component findings | `e42_causal.py` |
| Figures and tables | `figs_acl.py`, `tables_acl.py` |
| Shared utilities | `mp_common.py`, `dd_common.py`, `fastsim.py`, `prefetch.py`, `prepare_data.py`, `e13_arbitration.py`, `e21_e22_corpus.py` |

## Third-party artifacts and licences

The code downloads and uses, without redistributing them: DataDecide models (Apache-2.0), DataDecide data recipes and
evaluation results (ODC-BY), Pythia and PolyPythias (Apache-2.0), OLMo 2 and OLMo-1B-0724 (Apache-2.0), Qwen2.5-1.5B,
SmolLM2-1.7B and Gemma-2-2B (their respective licences), ParaConflict (Apache-2.0), NQ-Swap (MIT), PopQA (as released
by its authors), NeelNanda/pile-10k, and the infini-gram API. `results/` contains only numbers derived from these
artifacts (attention-based scores, log-probabilities, item indices and counts); `results/corpus_counts/` lists the
country / capital pairs of ParaConflict's World Capital relation with their corpus counts.

## Environment

Python 3.12; see `requirements.txt` (versions used for the paper). GPUs: NVIDIA A100 80GB.

## AI assistance

An AI coding assistant helped write and refactor parts of this code; all code was checked and run by the authors.
