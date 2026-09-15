# WALL-AL — Causal vs anticausal learning asymmetry in language

Date: 2026-09-15
Status: EXHAUSTED / DIRECTLY OWNED

## Mother question
Classical causal-learning theory predicts an asymmetry between learning effects from causes and learning causes from effects under the Independence of Cause and Mechanism (ICM) principle. Could paired language directions such as meaning/intention -> utterance versus utterance -> meaning expose different transfer/sample-efficiency behavior, and does pretraining erase that asymmetry?

## Direct-owner assassination
Jin et al., EMNLP 2021, *Causal Direction of Data Collection Matters: Implications of Causal and Anticausal Learning for NLP*, already imports Schölkopf-style causal/anticausal learning into NLP as its central scientific object. The paper:
- categorizes NLP tasks by causal direction;
- derives different expectations for semi-supervised learning and domain adaptation under ICM;
- uses MDL to test ICM-related assumptions on text;
- meta-analyzes more than 100 SSL studies and 30 domain-adaptation studies and reports patterns consistent with the causal-direction predictions.

Thus 'causal versus anticausal transfer in NLP' is already a direct framework, not an unowned bridge.

## Additional identification problem
Treating a clean latent 'meaning/intention' as the cause of an utterance is itself not generally identified. Utterances are jointly shaped by speaker, discourse context, pragmatic goals, style, world state, and other variables. A production/comprehension pair would therefore require a contentious causal graph before the causal-learning theorem could even be applied.

## Verdict
No L-series. A production/comprehension instantiation would reviewer-compress to Jin et al. 2021 + a new task pair, with an additional causal-identification problem.

## Anti-resurrection
Do not revive as:
- production versus comprehension transfer asymmetry;
- ICM applied to a new NLP task family;
- SSL/domain-adaptation causal-direction replication with foundation models;
- 'pretraining erases causal/anticausal asymmetry' without an independent older unresolved question;
- treating semantics/intention -> text as an unquestioned causal graph.
