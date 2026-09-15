# WALL-AE — Input/output embedding weight tying and role conflict

Date: 2026-09-15
Status: EXHAUSTED / DIRECTLY OWNED

## Mother question
Classic weight tying shares the input token embedding and output classifier/unembedding, motivated by lexical-geometry sharing, parameter efficiency, and regularization. In modern decoder LMs the two roles are highly asymmetric. Is the shared representation scientifically justified, or does tying merely trade parameter savings/regularization against a conflict between input representation and output prediction?

## Lineage
Press & Wolf (EACL 2017) showed the output matrix itself forms a useful embedding and recommended tying; they already observed that the tied matrix evolves more like the output embedding than the untied input embedding.

## Direct-owner assassination
Lopardo et al., ACL Findings 2026, *Weight Tying Biases Token Embeddings Towards the Output Space*, directly studies this role conflict. They find the tied embedding aligns substantially more closely with the output/unembedding space than with input embeddings from comparable untied models. They trace the effect to output gradients dominating early training, show weaker contribution of early-layer computations, and causally mitigate the bias by scaling input gradients. The paper explicitly argues that tying can harm performance at scale because output optimization compromises input representation.

Thus the core scientific distinction—shared lexical representation versus gradient/role conflict—is already directly mechanistically studied.

## Verdict
No L-series. Larger models, more model families, or tied/untied scale sweeps would be direct follow-up engineering/replication.

## Anti-resurrection
No:
- tied vs untied perplexity scaling;
- Qwen/Llama model-family comparison;
- 'input and output embeddings do different jobs' as novelty;
- gradient-imbalance mechanism as a new claim;
- embedding geometry comparison without a new independently inherited theory.
