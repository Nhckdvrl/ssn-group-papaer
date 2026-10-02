# Pragmatic competence through discourse connectives — CoNLL2021

[原文](https://aclanthology.org/2021.conll-1.29/) · [原code](https://github.com/lalchand-pandia/Pragmatic-competence-in-PLM)。13页全文含AppendixTables9–12已读；代码/PDTB许可资产尚未核对，未复现。

- **来源 DOCUMENTED：** natural connective预测看起来好，但go-to and/shallow cues可能造成高分→原心理语言学minimal pairs隔离高层线索，再测reinforcement/cancellation与explicit and-then。先复现再controlled slice的历史典型。
- **方法/ownership：** 8BERT/RoBERTa/ALBERT maskedmodels、17476PDTB单词cloze/66候选；30causal/concessive pairs；160cancel/reinforce pairs，320implicit/explicit versions。把每侧accuracy与same-item pair correctness并列，早已拥有“偏好替代辨别”的核心教训，不能把此思想只归2026 SDT。
- **数字：** PDTB .42–.66，但causal/concessive pair0–.30，temporalcancel/reinforce pair.02–.20；同implicit/explicit敏感性≤.03除了RoBERTalarge强化.21。是旧模型结果，不能推到现在。
- **构念风险：** 他们承认部分cloze标准来自理论而非对当前items的人类选择；‘in fact’可取消但不必取消、after/before lexical/frequency cue与syntax intertwined。pair chance.25只是独立随机二选假设；和极低accuracy对比不自动证明能力。Masked读取后文不能直接改为causal prefix不给后文再称same task。
- **对我们：** implied versus explicitly encoded meaning的受控比较已存在，generic“自己脑补难撤回”不是新。可以借其语义/读数控制思想；没有natural human norm与现代stage边界前，不另铺全套新benchmark。
