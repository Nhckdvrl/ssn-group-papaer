# The Story Shapes the Agent（COLM 2026，作者正文标注）

证据：[正文](https://arxiv.org/html/2607.18566v1)§3–6、附录A–H/I与Tables4–16；未找到明确可clone的作者代码URL，未以摘要代替可复现性。原文将代码release用于full matrices，地址仍待核。

- **DOCUMENTED / idea来源：** 人设行为可能随领域故事而变；在调查游戏固定核心决策结构，改变medical/IT/crime背景。3模型10personas×7场景×3trial共1890session，温度.7；16行为特征。人物在单叙事内可显著影响行为，不能概括为“persona无用”。
- **强已有控制：** 两个persona去动作词；第四cooking叙事；source-only BCI选角色；去掉4比例特征；prompt长度/人工specificity；强动作比例指令（63session）与abstract action labels（21session）。后两项已经堵住简单的“加行为指令”“动作改名”增量。
- **需限定：** BCI相关性在每叙事内z-normalize后计算，不等同原始效用一致；Top5识别改善须区别类别数变少与实际可控性。AppendixA有5/7角色和12/15文档，作者称为packaging；没有代码验证资源级一一同构前，不把它写成完全同一MDP。此项是未核竞争解释，未推翻作者结论。
- **对我们：** 调查者属于任务行动agent，未直接测玩家请求与原生NPC自身作者目标冲突。不能仅换RPG外壳就声称新发现；需要不同的可预测条件或更独立的执行/因果证据。
