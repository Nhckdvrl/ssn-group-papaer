# Principled Personas（EMNLP2025 Main，全文相关部分）

主源：[正式正文](https://aclanthology.org/2025.emnlp-main.1364.pdf)、[HTML](https://arxiv.org/html/2508.19764)、[作者代码](https://github.com/peluz/principled-personas)。核读§2–6、Table1–2、AppendixB提示与结果/回归入口；仓库README已核，未逐文件审计或复现。

**DOCUMENTED：** 9模型/27可客观判分任务，区分专家优势、不相关persona的稳健性、相关属性忠实度。名字/颜色会影响准确率，能力随persona变化不是新认识。Instruction/Refine/组合控制已做；先无persona回答再按persona改写也已有明确先例，不能把这种分离直接包装成新算法。

**RECONSTRUCTED idea来源：** 不再只问persona是否提高分数，而是先定义什么应该改变、什么应保持，再由真实任务检验。局限是规范性相关/不相关划分与QA正确性，不直接提供有自身目标的NPC该向谁交付的金标。

**对本项目：** 原生物理后果是可判真的对象，私有目标取舍与性格表达须另测。E74若发现性格影响物理预测，只是该文任务稳健性问题的游戏实例；增量要落在对角色行动选择/任务表现的可操纵解释与跨任务预测上。不能靠给技术误差起新名字立题。

资产cache/papers/principled_personas_emnlp2025.pdf，SHA256 `4f4489e5eedcdb7cf1d951c5bed51ca37d5987c3caae7f5346a587e2489bd1d6`。
