# WALL-AA — Why self-consistency majority voting works

Date: 2026-09-15
Status: KILLED / EXHAUSTED

## Tempting mother question
Why does majority voting over many reasoning samples from the same LM improve accuracy despite the samples sharing the same model and biases? Is improvement controlled by error decorrelation as in classical ensemble/Condorcet arguments?

## Theoretical correction
For a fixed prompt and fixed sampling distribution, independently generated completions are IID draws from the model's terminal answer distribution. The central asymptotic question is therefore not generic pairwise 'error correlation' among independently sampled runs. Plurality/self-consistency converges to the modal answer of that distribution.

The decisive quantity is the probability gap between the correct answer and the highest-probability competing answer. If the correct answer is modal, more samples estimate it increasingly reliably; if a wrong answer is modal, additional voting amplifies the wrong answer.

Recent self-consistency theory explicitly treats the method as mode estimation/voting and derives sample-efficiency/scaling guarantees. Recent empirical work also shows majority vote can systematically hurt on difficult problems when confidence/agreement tracks an incorrect modal answer.

## Verdict
Do not create a mechanism project around 'correlated reasoning errors explain self-consistency'. The statistically correct core object is already probability-gap/mode estimation and is an active theory program.

## Anti-resurrection
No:
- measuring pairwise chain similarity/correlation and calling it the mechanism;
- Condorcet theorem mechanically applied to IID LM samples;
- 'more diversity -> better voting' without a distinct theory-predicted quantity;
- majority-vote scaling curves on more models/tasks;
- confidence/agreement as a new generic self-consistency mechanism.
