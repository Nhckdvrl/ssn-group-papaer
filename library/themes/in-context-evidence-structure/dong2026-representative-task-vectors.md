# Dong et al. 2026：Task vectors作为代表性示例

- 来源：[ICLR2026正式全文](https://proceedings.iclr.cc/paper_files/paper/2026/file/20dcab0f14046a5c6b02b61da9f13229-Paper-Conference.pdf)。本轮读取§3–4理论结构与bijection反事实、相关主文图表；未穷尽36页证明/代码。
- **idea来源：** 不预设task vector就是抽象程序；比较pair/triplet格式的linear-transformer优化，提出其为示例加权组合。由这个结构推导single-vector注入的rank-one限制，再用方向任务与双向bijection让完整ICL和task-vector预测分叉。
- **设计学习：** 先提出被移植信号的计算角色，再找正常行为等价、反事实不等价的任务。注入成功只证明该接口有用；失败也需对照完整ICL，不直接否定全模型能力。
- **证据边界：** rank-one推导有特定linear-attention/注入假设；实用LLM的saliency与行为相符不等于证明全网络都遵循该算法。
- **与ICES最近邻：** “一个状态可能是代表性证据而非完整规则”早已有解释。E93的metric、完整私人规则、B-verdict换算均能行为全对；需来源偏好及recipient证据竞争，不能靠一次before-input patch就宣称通用程序。
