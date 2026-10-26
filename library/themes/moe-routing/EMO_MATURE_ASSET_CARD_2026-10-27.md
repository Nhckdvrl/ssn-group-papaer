# EMO: Pretraining Mixture of Experts for Emergent Modularity（2026预印本，接收/评分未核对）`[阅读：正文§1–3、Appendix B.4、发布清单与代码]`

来源：[论文](https://allenai.org/papers/emo)、[作者仓库](https://github.com/allenai/EMO)、[实际模型集合](https://huggingface.co/collections/allenai/emo)。

1. **形态：** 训练方法 + 原生功能测量。
2. **压力：** 一般MoE的token路由会遍历许多专家，任务子集单独使用较难。
3. **改变前提：** 用文档共享pool约束训练，不预定义领域标签。
4. **Idea来源（DOCUMENTED）：** 同文档的语义关联提供弱组织信号；显式组织约束参与形成模块。
5. **近邻距离：** 文中比较ModuleFormer、BTX/FlexOlmo与常规MoE；本轮未重读这些原文。选择性部署和自模型内组合的ownership属于已有路线，不能重新命名成我们的新联盟发现。
6. **资产/基线：** 作者发布EMO与匹配标准MoE，以及标准预训练后改用pool退火的终点。训练规模和具体谱系以作者脚本及HF pins核验；不是多初始化套件。
7. **强度/短板：** 原生匹配模型且实际权重可下载。原始分叉起点hash、batch/optimizer链没有取得；不能冒充严格单因素干预。
8. **可迁移动作：** 利用成熟协议分支，直接交叉部件来源区分兼容边界；无须自行训练多个成熟模型。
9. **对我们：** 自模型内子集可用性与跨历史组件可重用性不同。E150将共享专家单列，检验源配套是否跨越始终激活计算；不是反驳作者未声称的跨模型可移植性。
