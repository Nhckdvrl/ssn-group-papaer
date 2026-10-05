# Draft outline (agent, 2026-10-05) — working title

**In-Context Learners Notice When the Rule Changes — Unless the Rule Is a Mapping**
*(alt.: "Change Blindness in In-Context Classification"; "LLMs Track What to Do, Not Which Input Gets What")*

## Abstract (draft)
When a few demonstrations contradict the rest, a rational in-context learner must decide whether they are
noise or a sign that the rule has changed — and the answer is in *how the contradictions are organized in
time*: isolated contradictions in a noisy context are outliers, a persistent run at the end is a change.
We turn this cognitive-science distinction (change-point vs. oddball) into an exact test for LLMs, using
procedurally generated tasks with an exact hierarchical Bayesian oracle that jointly infers volatility and
noise. The oracle makes a direction-reversing prediction: adding *more* contradicting evidence early in the
context should make a late run of contradictions *less* believable. Across 13 open models (0.6B–32B, four
families, base and post-trained), the answer depends on what kind of rule the demonstrations express.
When the rule is a global function applied to every input — a label stream, a format transformation, an
arithmetic shift — models integrate evidence over time and move in the normative direction. When the rule
is an input-routed mapping — classification with natural or nonce labels, numeric or sentiment categories,
class-conditional transformations — the same models pool the evidence as an exchangeable set: clustered
and dispersed contradictions are equivalent, extra noise makes them *more* (not less) willing to follow late
contradictions, they cannot distinguish A→B from B→A even with 64 demonstrations, they adapt only for
inputs similar to the changed examples, and neither instructions nor chain-of-thought help. Mechanistically,
the temporal signature is already present in the task state carried at the query (patched task vectors
reproduce it, ρ=0.95 across formats), while mapping evidence is retrieved by content similarity. Training a
transformer from scratch on task-homogeneous sequences reproduces the dissociation, and briefly fine-tuning
an LLM on volatile classification streams partially transfers change-awareness to unseen natural
classification tasks — suggesting the blindness is learned from the statistics of pretraining contexts.

## 1 Introduction
- One-minute question; Fig. 1 paradigm (dispersed vs clustered contradictions; noise-prefix reversal).
- Tension in the literature: order sensitivity as a bug (Lu'22, Fang'25) vs recency as a feature under drift
  (Kossen'24, Qin'26, Dudley'26) vs exchangeable Bayesian ICL (Xie'22, Falck'24, Bigelow'25).
- Contribution list (measurement; phenomenon; boundary; mechanism; why/fix).

## 2 Measuring evidence structure in ICL
- Exact oracle (rule × volatility λ × noise ε; set / sequence / meta variants); three directional probes;
  normalized indices CSIn / NDIn; paired design; why accuracy alone is not informative.

## 3 Classification ICL is change-blind
- E02a/E16 across 13 models; E07/E13 SST; E15 numbers; condarith; E08 T=64 A→B vs B→A; E04 local update;
  E03 instructions; E09 CoT/thinking; implicit prior fit (λ=0, ε≈0.3).

## 4 The same models track change in global rules
- Label streams (incl. irrelevant inputs / unique ids, E06); case; arithmetic and FV task pairs (E11/E19);
  gradient in Fig. 2; implicit hazard λ≈0.02–0.05.

## 5 Where the difference lives
- Attention organisation (content similarity vs runs), run-head ablation (−73%), task-vector patching
  (E17/E17b: temporal signature carried by the task state; ρ=0.95).

## 6 Why: context statistics
- Toy transformers (E12): task-homogeneous training reproduces the dissociation; volatile classification
  partially removes it. LoRA (E18): volatile classification streams transfer partial change-awareness to SST /
  parity / magnitude.

## 7 Related work; 8 Implications (agents and continual ICL, evaluation of order effects, ICL theory)

## Rebuttal reserve (do not put in main text)
- nonce lexicon audit (step-5 quota); letter-shift exception; arithmetic strength varies by model;
  thinking-mode cost; LoRA dose response.
