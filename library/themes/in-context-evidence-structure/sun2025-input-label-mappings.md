# Sun et al. 2025：通过输入—标签映射解释ICL

- 来源：[ACL2025 Main原文](https://aclanthology.org/2025.acl-long.196.pdf)。本轮读取主文§3–5及方法Algorithm1/2；未穷尽23页附录/代码。
- **idea来源：** 标签改成任意词后，直接hidden-state logit lens不易看到任务语义，作者改用跨样本PCA再观察其词表投影；随后沿选出的PC做扰动，追踪相关attention heads并做mean ablation。不是先发现异常head再命名。
- **认识增量：** 将任务相关表示、使用该表示的组件和输入到标签的行为串起；关键heads参与匹配demo label位置。
- **设计学习：** 观察方式可随具体失败改进；PC patching提供文本反事实之外的构造性干预，但本项目已有能保持文字不变的正交标签反事实，不必为了模仿新方法先加PCA。
- **证据边界：** 任务词投影高或PC改变预测，不能单独证明完整输入—标签函数；选PC的语义与输出方向可能耦合。其relative-logit分母不能直接套在小gap上。
- **与ICES最近邻：** 任务子空间、label matching、少数heads干预均有所有权。E93候选是标准与个人偏好如何从不同Source组合；若有功能状态，再检验对私人映射/新输入的迁移，不能以PC本身称novelty。
