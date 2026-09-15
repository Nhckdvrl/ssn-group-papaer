# WALL-AX — Softmax gauge / raw-logit energy under conditional likelihood

Date: 2026-09-15
Status: KILLED FOR MAIN-LEVEL TOPIC; KEEP AS IMPORTANT CONCEPTUAL CORRECTION

## Mother question considered
Cross-entropy / next-token likelihood identifies conditional probabilities, but softmax logits are only defined up to a context-dependent common additive offset. Why, then, do absolute-logit quantities such as log-sum-exp / 'energy' often correlate with OOD inputs, uncertainty, hallucinations, or sequence errors? Does conditional training somehow recover input/context density beyond what its objective identifies?

## Old ancestry
This is a classical identifiability issue in multinomial logistic regression and conditional modeling. Only score differences determine the softmax distribution. Adding the same score to every class/token leaves all probabilities and cross-entropy unchanged. Classical models therefore fix a reference class, impose a sum-to-zero constraint, or use regularization to choose one representative from an equivalence class.

JEM / classifier-as-EBM work (ICLR 2020) explicitly notes that a discriminative classifier possesses an extra logit degree of freedom if one wishes to reinterpret its logits as a joint energy; JEM adds a generative p(x) objective to make the input-density interpretation meaningful.

## Modern LLM trigger
ICLR 2026 *Spilled Energy in Large Language Models* interprets token logits and next-step log-sum-exp values as energies that should agree across autoregressive steps and reports that their mismatch predicts hallucinations/errors. Vaishnavh Nagarajan's 2026 note *What does a language model model?* independently notices the same conceptual issue: NTP determines next-token probabilities, while the absolute logit level is underdetermined, and asks whether optimization's implicit bias nevertheless makes logits track joint/context probability.

## Decisive gauge fact
For z = W h + b followed by softmax, any common shift z -> z + c(h) 1 preserves the complete next-token distribution. In linear softmax regression, L2/minimum-norm conventions simply select a centered representative; this is representation choice, not extra probabilistic identification.

Stollenwerk et al. (2026), *Output Embedding Centering for Stable LLM Pretraining*, provides an especially direct LM intervention. Let the mean output embedding be μ = (1/V) sum_i e_i. They show mean logit = μ·h and propose subtracting μ from every output embedding. This makes mean logits zero while preserving softmax probabilities and LM loss exactly. Therefore raw-logit / log-sum-exp energy can change under a behaviorally and probabilistically equivalent reparameterization.

Training recipes can also explicitly choose the gauge: z-loss penalizes logsumexp(logits)^2 and is used in PaLM/OLMo/Chameleon-style training, while logit soft-capping and output-embedding centering impose other absolute-logit conventions.

## Stronger decomposition
If logits are approximately mean-centered, their log-sum-exp is not independent evidence for p(context). For canonical zero-mean logits corresponding to a probability vector p,

    logsumexp(z) = - mean_v log p_v.

Thus a large fraction of the apparent raw-energy signal can reduce to a coordinate representation of the *shape of the conditional next-token distribution* (confidence/peakedness/geometric-mean probability) rather than a separately learned joint density.

## Why this does NOT become L41
The cleanest publishable operation would be to apply gauge-preserving reparameterizations (e.g. output-embedding centering or an explicit common-logit gauge head), show that LM probabilities/generation are exactly unchanged while raw-energy hallucination scores move, then reinterpret why the metric works.

That is scientifically useful, but the reviewer-compression is too easy:

> classical softmax translation non-identifiability / classifier-energy caveat + ICLR-2026 Spilled Energy.

The topic would become primarily a correction/reinterpretation of a frontier metric rather than an independently inherited Main-level scientific question. The old question ('what does conditional likelihood identify?') is real, but the modern operation mainly critiques a particular gauge-dependent observable.

## Anti-resurrection
Do not revive as:
- 'spilled energy is not gauge invariant';
- arbitrary common-logit shift as a paper by itself;
- energy-vs-softmax hallucination benchmark;
- logit centering as a new hallucination detector;
- z-loss effects on spilled-energy scores;
- 'do logits represent joint or conditional probability?' unless a new independent theory supplies a model-intrinsic, gauge-invariant quantity and a question larger than the 2026 energy papers.

## Useful conceptual lesson
Any scientific interpretation of raw logits must first separate:
1. quantities identified by the predictive distribution;
2. the arbitrary/regularized gauge chosen by parameterization and optimizer;
3. genuinely additional training objectives that constrain absolute logits.

A model-intrinsic explanatory quantity should normally be invariant under exact reparameterizations that preserve the entire predictive distribution, unless the gauge itself is the scientific object.
