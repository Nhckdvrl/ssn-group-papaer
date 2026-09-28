# Mind the (DH) Gap

Code and data for the paper [*Mind the (DH) Gap! A Contrast in Risky Choices Between Reasoning and Conversational LLMs*](https://arxiv.org/abs/2602.15173), to appear at ACL 2026.

Affiliation: Washington University in St. Louis.

## What's in this repo

```
data/        Processed LLM choice data (4 CSVs covering closed/open
             models × explicit/implicit prospect representations).
             Human subject data is not included per IRB.

code/        Two fitting scripts:
               fit_dual_beta.py    — dual-beta prospect theory model
                                     (primary model in the paper)
               fit_standard_pt.py  — standard prospect theory model
                                     and three alternative variants
                                     (reported in the appendix)

results/     Fitted parameters and bootstrap confidence intervals for
             both models, organized by model type and dataset.
```

## Running the code

Install dependencies:

```bash
pip install -r requirements.txt
```

Both fitting scripts read a CSV from `data/` and write fitted parameters to `results/`. To run a different dataset, change the `INPUT_FILE` variable at the top of the script.

```bash
python code/fit_dual_beta.py
python code/fit_standard_pt.py
```

Each run also produces a log file and uses checkpoints, so interrupted runs can be resumed by re-running the same script.

## Citation

```bibtex
@misc{ge2026minddhgapcontrast,
    title={Mind the (DH) Gap! A Contrast in Risky Choices Between Reasoning and Conversational LLMs},
    author={Luise Ge and Yongyan Zhang and Yevgeniy Vorobeychik},
    year={2026},
    eprint={2602.15173},
    archivePrefix={arXiv},
    primaryClass={cs.AI},
    url={https://arxiv.org/abs/2602.15173},
}
```
