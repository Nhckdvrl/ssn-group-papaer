# SimpleToM（ICLR2026，全文相关部分）

主源：[正式PDF](https://openreview.net/pdf?id=iE2JmbRJow)、[全文v2](https://arxiv.org/html/2410.13648)、[作者代码](https://github.com/yulinggu-cs/SimpleToM)。OpenReview网页本轮遇challenge；PDF/HTML可读，PDF页首确认ICLR2026。实际核读§2–5、Table1–2/Fig3及AppendixK.1–K.3；未运行作者模型。

**DOCUMENTED：** 1147人审故事/3441问题，21模型；分开问信息意识、行为预测、行为判断。三人一致过滤原3600故事；并非游戏引擎执行。提醒此前信念答案、系统提示与CoT均已有消融，改善不稳定；“能说对却不会用”及提醒修复已有ownership。

**RECONSTRUCTED idea来源：** 将同一故事上的推断链拆为能相互核查的不同任务，揭示传统显式ToM分数遗漏的应用困难。不是因模型回答不一致就推测神经模块缺失。

**对本项目：** E74自身行动物理后果由native事件给真值，接收者选择没有唯一性格金标；要测预测质量替换如何改变实体行为。仅展示预测正确但没Give不构成独立增量。分叉预测不等读取内部信念，测量进入决策本身也会改变可用路径。

资产cache/papers/simpletom_iclr2026.pdf，SHA256 `fccc26632150c04b3b8a792b9f9dc999367486d5f1804df5af4da303329644ed`。
