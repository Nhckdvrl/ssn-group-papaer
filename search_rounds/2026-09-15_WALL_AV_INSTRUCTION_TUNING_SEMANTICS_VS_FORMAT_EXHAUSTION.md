# WALL-AV — Instruction tuning: task semantics vs format/protocol/elicitation

Date: 2026-09-15
Status: EXHAUSTED / DIRECTLY OWNED

## Mother question
Why does instruction tuning transform a base LM into an instruction-following assistant? Candidate explanations include: (1) learning to interpret natural-language instructions as compositional task descriptions; (2) learning a common response/chat/output-format protocol; and (3) eliciting task capabilities and semantic priors already present from pretraining.

## Direct-owner audit
This decomposition is already a longstanding instruction-tuning analysis axis.

- Kung & Peng, ACL 2023, *Do Models Really Learn to Follow Instructions?*, directly trains models with altered/simplified task definitions that remove semantic components while retaining output-space information, and with delusive examples containing incorrect mappings. These variants can perform comparably to original instructions; the paper explicitly concludes that substantial apparent IT gains can come from output format/superficial patterns rather than task understanding.
- FLAN-style ablations compare natural instructions against dataset/task names and no-template multi-task fine-tuning.
- Symbol Tuning removes instructions and replaces semantic labels with arbitrary symbols specifically to force reliance on demonstrations rather than natural-language task priors.
- Work on instruction tuning and ICL shows instruction tuning both improves arbitrary input-label mapping and strengthens semantic-prior reliance.
- Format-consistency work studies the contribution of unified instruction formatting itself.

## Verdict
No L-series. Natural instruction semantics versus arbitrary task identifiers/output protocol is already directly tested. Repeating with current chat LMs would be scale/model-family follow-up.

## Anti-resurrection
Do not revive as:
- natural instructions vs task IDs/random labels;
- semantic instructions vs simplified output-space descriptions;
- chat template/role-token ablations as mechanism;
- 'instruction tuning mostly teaches format' as novelty;
- larger instruction-tuned models on the same semantic-vs-format distinction.
