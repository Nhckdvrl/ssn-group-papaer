# Right for the Wrong Reasons: Diagnosing Syntactic Heuristics in Natural Language Inference（ACL 2019 Main；正文部分）

[主文](https://aclanthology.org/P19-1334/)。实际读引言/Table1、§2三heuristic与negation捷径讨论、§3模板设计；全部model结果/附录未完整核对。

- **来源/动作（DOCUMENTED）：** 高benchmark分数不证明推断依据正确；用lexical overlap/subsequence/constituent三个明确解释，各构造支持与违背的matched例子。HANS每heuristic10模板×1000，共30,000项，4种NLI模型。
- **已拥有：** hypothesis词在premise中、片段看似关系相同等，可让模型错误判entailment；negation还可能被单独作为contradiction捷径。不能把E28–E31分类在同V/换V时改变，直接叫我们首次发现event scope欠缺或新内部机制。
- **I01的定位：** 该分类现象仅辅助定位，普通lexical/polarity匹配仍竞争；候选主干是无需诊断题的角色信息对新活动患者相对预测反向、跨人物、谓词依赖，并以neutral及共同配置控制。相反用途本身也非novelty，须验证关系而非原词近邻/句型重复。
- **有用的研究技艺：** 控制要求反例改变解释的预测，不按成功题定义能力。邻居已有NLI捷径claim，不等同其已拥有本线正常predictive contrast，也不自动否定候选。

21页，288,756 bytes，SHA256 `c9c106161f40b6dc76ae5b6e50e0df6f4a8428498285e9ca9e88a960ffc2d0a6`；直接无代理下载，全文cache-only。不做其训练增广，不读出隐藏表示。
