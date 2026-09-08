# RLVR Disagreement — Related Work and Novelty

## 1. What the parent paper owns

Ni et al., EACL 2026 owns:
- the question of whether reasoning helps model human annotator disagreement;
- systematic evaluation across RLVR/RLHF reasoning settings;
- the finding that RLVR-style reasoning degrades disagreement modeling;
- task/model-size/expression/steering comparisons.

Source: https://aclanthology.org/2026.eacl-long.3/

We therefore cannot claim:
- RLVR hurts disagreement modeling;
- disagreement matters in NLP;
- prompting/steering can affect expressed disagreement.

## 2. Neighboring mechanism work

Recent work studies:
- hidden-state representations of uncertainty/ambiguity;
- neurons/subspaces associated with ambiguity;
- RLVR calibration and confidence shifts;
- post-training-induced distribution changes.

These establish that hidden-state analysis is plausible, but do not kill the candidate unless they already decompose the same human-disagreement loss into representation erasure vs output suppression in matched RLVR models.

## 3. Surviving scientific axis

The new question is causal:

> **Where did the missing human variation go?**

Behavioral collapse can result from:
1. erased internal alternatives;
2. preserved alternatives with output suppression;
3. selective preservation by task/type/layer.

The paper must connect behavioral distributions to internal information and then to a causal intervention.

## 4. Reviewer compression

### Attack A
> “EACL 2026 plus probes.”

Fatal if the paper ends at hidden-state decodability.

Required rebuttal:
- matched checkpoints;
- layerwise localization;
- intervention/patching/readout recovery;
- a conclusion about whether retraining or readout repair is needed.

### Attack B
> “RLVR calibration work.”

Calibration asks whether confidence matches correctness. Human disagreement asks whether the model preserves **population-level alternative interpretations** even when one answer may be majority-correct.

### Attack C
> “Ambiguity neurons on another model.”

General ambiguity representation does not answer what RLVR specifically destroys or suppresses relative to a matched pre-RLVR state.

## 5. Exact novelty claim

Potentially defensible:

> “RLVR-induced collapse of human disagreement is caused primarily by representation erasure / output suppression / a task-dependent mixture, established by matched hidden-state and causal intervention evidence.”

## 6. Kill-level collision

KILL if prior work already compares matched RLHF/RLVR checkpoints on human label distributions and causally shows whether alternative interpretations remain internally represented and recoverable.

## 7. Current verdict

**NOVELTY: PASS, current audit; mechanism standard must be high.**