# L12 Next Decisive Experiment Card

**Experiment:** L12-E12
**Status:** RUNNABLE; WAITING FOR CHECKPOINT AVAILABILITY

## Scientific question

> Does the causal-control reorganization found at the sibling SFT split persist through the documented DPO continuation of both branches?

This is checkpoint breadth, not another search for a local interpretability effect.

## Design

Use the same 222 matched stripped-trajectory pairs from E10 and score the same prompt-frame x trajectory-frame factorial on:

- `allenai/Olmo-3-7B-Instruct-DPO`
- `allenai/Olmo-3-7B-Think-DPO`

The SFT results are frozen comparators. Official model metadata states:

- Instruct-SFT -> Instruct-DPO
- Think-SFT -> Think-DPO

## Primary evidence

> Think-DPO minus Instruct-DPO trajectory-minus-prompt control.

The base-decision bootstrap interval must exclude zero and direction should be broadly consistent across the 36 independent decisions.

Within-branch DPO-minus-SFT changes are secondary and descriptive. This experiment cannot identify DPO as the origin of the original branch divergence.

## Execution state

Exact revisions, scripts, and summary code are complete. The first run was stopped before model loading because Hugging Face checkpoint transfer remained below 0.1 MB/s with and without `hf_transfer`.

Runnable:

- `configs/checkpoint_validation.json`
- `scripts/run_checkpoint_control.py`
- `scripts/summarize_checkpoint_control.py`
- `scripts/run_checkpoint_control.sh`
