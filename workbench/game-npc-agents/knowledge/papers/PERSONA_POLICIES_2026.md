# Persona Policies（2026预印本；会场未核实）`[证据：正文/关键附录/作者代码]`

来源：[论文](https://arxiv.org/html/2605.12894v1)、[作者代码](https://github.com/harshita-chopra/persona-policies)，本地pin85e5286667。已读§3–5、A/B/C/D/E/F/G/H关键协议；未复现付费模型搜索。

1. 形态：人格生成方法＋人类轨迹与下游训练验证。
2. 压力：默认用户模拟器过于配合。DOCUMENTED来源是人类交流分布与一般行为维度，转为可执行的披露/节奏等指令。
3. 方法：OpenEvolve搜索Python生成器，RF人类概率＋双向Chamfer覆盖；任务目标/私人事实固定。最优验证checkpoint，最多70次搜索；三个模拟模型、retail/airline。
4. 证据：16标注者/87对话。等48步LoRA训练，retail挑战均值.213→.250；airline.400→.413，全部表格保留异质性。19个regex特征的分类器不等于语义/效用评价。
5. 代码事实：injection.py明确保留原目标；fitness主要优化human-likeness/coverage，runner另记原任务reward（含自然语言assertions与失败重试）。指令保证与独立目标保持证据须分开；没有审计每个生成任务的目标语义。
6. 增量/迁移：已有“同目标不同风格”和数据增强训练owner。我们研究原生利益属性编辑与状态机会中的控制形成，不能将保持任务的人格多样性重新命名；普通增强先作为解释与强基线。
