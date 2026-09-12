# 2026-09-13 — Final-Layer Angular-Jump Assassination

**Target:** ACL / EMNLP / NAACL Main  
**Verdict:** **KILL — K192 — PARENT/MECHANISM COMPRESSION**  
**Rule:** do not reactivate by changing model family, angular metric, normalization variant, early-exit loss, or causal probe.

## Hook

EACL 2026 Findings, *Suppressing Final Layer Hidden State Jumps in Transformer Pretraining*, reports a striking and apparently stable phenomenon across multiple open-weight Transformer families: middle layers often make only small angular changes to hidden states, while the final or near-final layer produces an unusually large angular jump. The jump grows through pretraining; suppressing it with layer-weighted regularization can improve performance. Penalizing only the final layer can move the jump earlier rather than eliminate it.

Natural question:

> Why does a Transformer leave so much representational reorganization to the final few layers?

A tempting stronger question was whether the terminal jump is (A) compensatory work caused by underutilized deep/middle layers or (B) a necessary late context→prediction transformation induced by the next-token objective/readout.

## Closest owners

### Shibata et al., EACL 2026 Findings

Owns the mother phenomenon, its cross-model prevalence, growth during pretraining, layer-shift under final-only suppression, and a performance-improving regularizer.

Source: https://aclanthology.org/2026.findings-eacl.64/

### *The Curse of Depth in Large Language Models*, NeurIPS 2025

Explains the broad middle/deep-layer underutilization phenotype in Pre-LN Transformers through residual-path variance growth and increasingly identity-like deep blocks. Uses layer removal and angular-distance evidence and gives an architectural normalization intervention.

Source: https://proceedings.neurips.cc/paper_files/paper/2025/hash/eeb57fdf745eb31a3c7ef22c59a4661d-Abstract-Conference.html

### *Peri-LN*, ICML 2025

Shows that normalization placement changes hidden-state variance growth and angular redundancy; Peri-LN reduces the redundancy characteristic of Pre-LN and improves training behavior.

Source: https://proceedings.mlr.press/v267/kim25u.html

### LayerSkip, ACL 2024

Already supplies depth-distributed predictive supervision: depth-increasing layer dropout plus an early-exit language-model loss using the shared LM head. This is an existing natural intervention on where prediction pressure is applied across depth.

Source: https://aclanthology.org/2024.acl-long.681/

### *Depth-Wise Emergence of Prediction-Centric Geometry in Large Language Models*, 2026

Shows that late decoder layers undergo a transition from context processing toward prediction-forming geometry; late angular organization is causally related to next-token prediction. This directly occupies the attractive fallback explanation that late angular reorganization is a special prediction/readout phase rather than merely wasted compensatory work.

Source: https://arxiv.org/abs/2602.04931

## Reviewer compression

> `Curse of Depth / Peri-LN explain why many deep blocks become redundant` + `LayerSkip shows how intermediate predictive supervision redistributes depth-wise prediction pressure` + `prediction-centric geometry work explains why late angular reorganization is tied to token prediction` + `Shibata already establishes and regularizes the jump` = the proposed "why does the last layer jump?" study.

The exact matched intervention may still be absent, but the likely scientific answer is already heavily constrained by these components.

## Why this is not worth selection

1. **The broad cause is already owned.** Middle/deep underutilization in Pre-LN models is not an unexplained mother anymore; residual/normalization dynamics are a mature causal account.
2. **The interesting fallback is also occupied.** Late angular change as prediction formation is already an explicit 2026 mechanistic object.
3. **The obvious discriminator is not new enough.** Distributing LM loss across depth / early-exit supervision is already central to LayerSkip-style training. A matched baseline would be useful engineering/science but reviewer-compresses to known ingredients.
4. **SAME-QUANTITY bridge is weak.** Shibata's jump magnitude, Curse-of-Depth redundancy, early-exit predictiveness, and prediction-centric angular geometry are related but not identical quantities. A paper trying to unify them would first need to build a bridge rather than answer a clean pre-existing uncertainty.
5. **Strongest successful result is below the current Main bar.** Showing that reducing deep-layer redundancy or moving prediction supervision earlier reduces the final jump would largely confirm the combined existing account rather than create a new inference.

## Anti-resurrection

Do not revive as:

- `why does the final layer jump?` with another model family;
- final-layer jump caused by LM-head proximity;
- terminal-only supervision versus deep supervision;
- normalization placement explains the jump;
- final-layer jump as compensatory workload;
- final-layer jump as context→prediction conversion;
- another angular-distance / logit-lens / tuned-lens localization of the same phenomenon.

A future depth-wise-computation topic needs a qualitatively different stable phenotype and central estimand, not another explanation of the same final-layer jump.

## Durable lesson

A visually striking unexplained-looking anomaly can still be a bad topic when its apparent explanation is already distributed across several mature papers. Before promoting it, search both (i) the upstream cause of the surrounding phenotype and (ii) the downstream functional interpretation of the anomaly itself.
