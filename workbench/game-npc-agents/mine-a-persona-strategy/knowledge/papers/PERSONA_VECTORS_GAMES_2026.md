# Persona Vectors in Games（2026 arXiv）

证据：[正文](https://arxiv.org/abs/2603.21398)§3–6、AppendixE/F与Figures3/4/7；[作者代码](https://github.com/johnathansun/persona-vector-agents)generate_vec.py、activation_steer.py、judge.py/eval入口已审；未执行其云judge/生成脚本。

- **DOCUMENTED / idea来源：** 提示人设不说明内部可控特质；把对比激活差扩展到利他、宽恕、对他人预期，干预Qwen2.5-7B的layer20。50dilemmas×5正/5负前缀；response-token均值差，经GPT trait≥50/<50与coherence过滤。Beta范围[-5,5]，宽恕限制|beta|≤3。
- **实际评价：** 六类利他博弈和宽恕5类/8vignettes，数值/二元选择由GPT提取，trait与coherence也由GPT评；叙事包含历史不等于环境长期闭环。高beta可强化语言却逆向改变宽恕策略，是它的已有结果。
- **代码/版本限制：** README生成teacher写Claude3.7，论文写Sonnet4.5；code还有coherence过滤，论文主定义先写trait阈值，需明确快照。公开hook支持prompt/response/all，不自动等于相同因果问题。
- **对我们：** “首次用steering影响策略”“人格与策略向量分离”均不可冒领。若以后做内部干预，须先有NPC原生利益/合法动作条件的新可预测现象，同时用规则解析实际执行，避免同源judge构念循环。
