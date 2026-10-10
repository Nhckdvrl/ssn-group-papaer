# Task Schema and Binding: A Double Dissociation Study of In-Context Learning（2025预印本）

[v1正文](https://arxiv.org/html/2512.17325)，Chaeha Kim。2026-10-11读§3、4.1–4.2；其余主张/代码未完整核对，接受状态未核对。

- **问题与idea来源（RECONSTRUCTED）：** 任意映射学习与事实覆盖表现不同，尝试区分任务类别和具体对应关系的运输。
- **实验把手：** MLP输出交换、整残差交换；前者测输出类别概率，后者测具体答案top1。任务类型与输入输出绑定的宽泛分解已有直接近邻，不能由ICES重新命名。
- **方法审计：** 两个不同运输接口、不同读数得到不同成功率，本身不充分建立严格的双向机制分离；Source confidence、target prior也影响运输。论文效果超过原baseline的比例不等于精确恢复原计算。
- **ICES设计启发：** 下一步在相同food/service答案空间比较不同Source范围的等价标准问题，另测仅传递criterion后的私人判断。让功能区别落在明确反事实上，不拿类别概率与个体答案正确率的差异冒充同一测量。
- **定位：** 此文不直接测试从多人的反向私人判断推断同一标准，也不覆盖E91的Source历史形成路径；这只是具体范围区别，不自动给ICES novelty结论。
