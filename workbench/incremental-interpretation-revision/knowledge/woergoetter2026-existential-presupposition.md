# There Is No Spoon: Existential Presupposition in Large Language Models（LREC 2026）

**证据范围：** primary引言/related/background、模型/预检、主要结果、context实验与结论；刺激构造细节及附录未完整阅读。[原文](https://aclanthology.org/2026.lrec-1.161.pdf)。暂停前阅读补记。

1. 形态：语义/语用现象的受控NLI测量。
2. 压力：existential inference受embedding、determiner、context影响；字面重叠/negation heuristic会伪装理解。
3. 前提：先匹配affirmative/negative NLI pretest，再比较projection/gradience/context modulation。
4. 来源（DOCUMENTED）：IMPPRES/NOPE/PROPRES和理论existential projection。
5. 距离：强弱quantifier与context交叉，比较DeBERTa、LLaMA/Gemma instruction及NLI-finetuned版本。
6. 实验：1600预检，context实验12000pairs；zero/few-shot波动大，NLI监督后的模式更一致。
7. 短板：模板与任务的归因，transfer不能自动证明未提问internal belief；本文entailment概率也明确不当calibrated confidence。
8. 动作：验证读数算子和语义，再解释理论构念；不能拿简单任务失败直接讲能力或新机制。
9. 对我们：广泛presupposition sensitivity、prompt susceptibility、task scaffolding均有owner；与E51不同角色/同一实体尚非精确撞车，也不能因为不同就认证novelty。
