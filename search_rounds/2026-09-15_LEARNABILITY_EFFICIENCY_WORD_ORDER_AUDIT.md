# 2026-09-15 — Learnability vs Communicative Efficiency in Word Order

**Target:** ACL / EMNLP / NAACL Main, calibrated against TACL / ICLR / ICML / NeurIPS.

## Question

> Are typologically preferred word orders easier to learn because they are communicatively / information-theoretically efficient, or are learnability and communicative efficiency independent pressures that happen to favor the same language types?

**Final verdict:** `ARCHIVED / NO-GO — DIRECT SUCCESSOR / NO ESTABLISHED CONTRADICTION`. No L-series. No pilot.

## Why the question looked strong

TACL 2026, *Can Language Models Learn Typologically Implausible Languages?*, finds that minimally manipulated counter-Greenbergian English/Japanese variants are typically learned more slowly than matched natural/harmonic variants. The paper frames this as evidence that domain-general learners can exhibit typologically aligned learning preferences.

Separately, Hahn et al. (PNAS 2020) and Clark et al. (TACL 2023) argue that Greenberg-style word-order patterns reflect communicative / information-theoretic efficiency, using counterfactual grammars and UID/locality-style quantities.

Thus two major explanatory traditions bear on the same typological object:

- `learning bias / learnability`;
- `communicative / information efficiency`.

At first glance, connecting them could yield a stronger account of why harmonic word-order universals emerge.

## Why the A+B bridge does not survive owner audit

The broad connection is already explicit in the literature.

1. **Hahn et al. 2020** already show that optimizing communicative efficiency yields Greenberg word-order correlations.
2. **Kuribayashi et al. ACL 2024**, *Emergent Word Order Universals from Cognitively-Motivated Language Models*, show that typologically typical word orders tend to have lower perplexity under LMs with syntactic, parsing and memory biases; the paper explicitly connects cognitive bias, predictability and word-order universals.
3. **Someya et al. ACL 2025**, *Information Locality as an Inductive Bias for Neural Language Models*, directly show that languages with higher `m`-local entropy are more difficult for Transformer and LSTM LMs to learn. Thus an information-theoretic property associated with efficient/local prediction is already a predictor of neural learnability.
4. **Xu et al. TACL 2026** explicitly cite information-theoretic constraints as a possible source of harmonic learning bias and, in their discussion, state that communicative pressures are another mechanism explaining the same typological correlations. They specifically note that Hahn/Clark efficiency measures can be straightforwardly applied to their new counterfactual corpora as future work.

Therefore the obvious experiment

> compute UID / dependency-locality / information-locality measures on the TACL 2026 counterfactuals and correlate them with training difficulty

is directly legible as the parent's named next experiment.

## What would have made the combination substantial

A successful A+B paper would need a new falsifiable statement not already licensed by the components, for example an **established conflict**:

> the same counterfactual language is systematically *harder to learn* but *more communicatively efficient* (or vice versa), forcing a revision of single-pressure accounts.

No such mother phenomenon is currently established for the TACL 2026 variants.

Searching for such reversals by running the experiment would make paper value contingent on discovering them. If the rankings align, the result largely validates the existing bridge; if they do not, only then does a larger story appear. This is a `BET-THE-PHENOMENON` shape.

## Strongest reviewer compression

> Hahn 2020 says Greenberg universals can emerge from efficiency + ACL 2025 says information locality predicts LM learnability + TACL 2026 finds harmonic variants easier and explicitly proposes applying efficiency metrics to the same corpora = run the named follow-up.

Nothing in the current design escapes this compression.

## Reopen only if

Reconsider only if independent evidence first establishes at least one of:

1. a robust learnability–efficiency **ranking conflict** on the same word-order variants;
2. a formal result showing the two pressures are equivalent only under a nontrivial condition that natural languages systematically violate or satisfy;
3. a natural typological pattern where learnability and communicative-efficiency accounts make opposite preregisterable predictions on the same quantity.

Do not reopen by merely adding more efficiency metrics, more LM architectures, or more counterfactual word-order variants.

## Searcher lesson

> A+B is not a kill by itself. But when A already predicts B's quantity, B already cites A as a candidate mechanism, and the parent explicitly names the combined experiment as future work, the bridge needs an independent contradiction or theorem to become a new paper rather than a successor experiment.
