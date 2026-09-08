# L09 — RLVR Disagreement: Erased or Suppressed?

**Status:** SERIOUS CANDIDATE / A-  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Canonical research package:** this directory  
**Last audited:** 2026-09-08

> **Plain-language thesis:** RLVR-style reasoning models become worse at reproducing real human disagreement. The open question is whether training actually removes alternative interpretations from the model, or merely suppresses them at the final output.

---

## 1. One-sentence research question

> When RLVR-style reasoning collapses a human disagreement distribution toward one answer, are the alternative human interpretations **erased from the model's internal representation**, or are they still represented but no longer expressed by the final decision/readout?

Plain version:

> **The model used to know that reasonable people disagree. After reasoning training it gives one confident answer. Did it forget the alternatives, or just stop saying them?**

## 2. Established phenomenon

Ni et al., EACL 2026, **“Can Reasoning Help Large Language Models Capture Human Annotator Disagreement?”**:
- evaluates RLHF, CoT, and RLVR-style reasoning settings;
- 60 experimental setups;
- 3 task families;
- finds RLVR-style reasoning degrades disagreement modeling while naive CoT can improve RLHF models.

Source:
- https://aclanthology.org/2026.eacl-long.3/

The accompanying repository exposes data/prompts for:
- Gab Hate Corpus;
- HelpSteer2;
- GoEmotions positive / negative / ambiguous subsets;
- sampled-distribution and verbalized-distribution settings;
- HighVar and random subsets.

Therefore this project does not need to discover the behavioral degradation.

## 3. Why ACL / NLP cares

Human disagreement often carries real information:
- ambiguity;
- subjectivity;
- value differences;
- borderline categories.

If RLVR improves single-answer reasoning while destroying this information, there are two scientifically different possibilities:

1. **representation loss** — post-training removes the alternatives;
2. **policy/readout collapse** — alternatives remain internally available but are not expressed.

These imply very different remedies:
- retraining/data objectives if erased;
- decoding/readout/intervention if preserved but suppressed.

## 4. Competing accounts

### Account A — Representation erasure

After RLVR, hidden states no longer support recovery of the human label distribution or ambiguity signal.

Predictions:
- probes trained on pre-RLVR representations lose decodability after RLVR;
- representation patching from pre-RLVR to post-RLVR restores disagreement behavior;
- output-only steering is insufficient.

### Account B — Readout/policy suppression

Human variation remains decodable internally, but final logits/decision policy collapse toward one label.

Predictions:
- hidden-state probes retain human-distribution information;
- causal steering/patching near later layers can restore calibrated disagreement without retraining the model;
- early representations remain similar while final readout changes.

### Account C — Selective erasure

Different disagreement sources behave differently:
- lexical/semantic ambiguity preserved;
- subjective preference or social/value disagreement suppressed;
- or vice versa.

This creates a task/type × layer × training-regime map.

### Account D — Behavioral degradation is mostly expression-format/calibration

The model still represents and can verbalize alternatives, but the evaluation distribution is distorted by confidence/temperature.

Prediction:
- alternative elicitation and calibrated decoding recover much of the human distribution without hidden-state intervention.

This is a required falsification route.

## 5. Outcome robustness

All outcomes support a scientific conclusion:

- erasure → RLVR changes representational content;
- suppression → information survives but is disconnected from action/readout;
- selective change → RLVR reshapes which kinds of human uncertainty are preserved;
- calibration-only → the apparent information-loss interpretation is wrong.

The paper is explanation-first, not effect-hunting.

## 6. Paper identity

**Primary identity:** post-training representation / behavior mechanism.

**Not the identity:**
- another disagreement benchmark;
- “RLVR hurts disagreement”;
- generic probing;
- generic uncertainty calibration;
- an RLVR method paper.

## 7. Planned C1 → C2 → C3

### C1 — Where did the disagreement information go?
Measure human-distribution information across layers before/after RLVR-style training.

### C2 — Causal attribution
Use:
- cross-model probes;
- activation patching;
- representation steering;
- readout/logit interventions;
- controlled RLVR training pairs.

Separate erasure from suppression.

### C3 — Consequence
Determine whether recovering plural human interpretations requires:
- new training;
- a different readout/decoding rule;
- or task-specific treatment.

## 8. Five hard gates

| Gate | Verdict | Why |
|---|---|---|
| REAL OBJECT | **YES** | Human annotator distributions are real repeated-label observations. |
| SCIENTIFIC TENSION | **YES** | Erasure and suppression are both plausible and imply different fixes. |
| GOOD DATA | **YES** | Existing datasets provide human label distributions; EACL repo is reproducible. |
| PAPER-LEVEL NOVELTY | **YES, current audit** | EACL 2026 establishes behavior but does not decompose internal preservation vs output suppression. |
| OUTCOME-ROBUST DECISIVENESS | **YES** | All major accounts yield distinct scientific conclusions. |

## 9. Main danger

Reviewer compression:

> **“This is the EACL 2026 disagreement paper plus probes.”**

That attack wins if the contribution is only:
- train a classifier on hidden states;
- report probe accuracy.

The paper survives only with a causal chain:
> behavior gap → layerwise information localization → causal restoration or erasure test → consequence for post-training.

## 10. Directory map

- [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md)
- [DATA_AND_GOLD.md](DATA_AND_GOLD.md)
- [RESEARCH_PLAN.md](RESEARCH_PLAN.md)
