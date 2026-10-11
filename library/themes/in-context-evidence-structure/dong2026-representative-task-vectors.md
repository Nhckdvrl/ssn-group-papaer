# Dong et al. 2026：Task vectors作为代表性示例

- 来源：[ICLR2026正式全文](https://proceedings.iclr.cc/paper_files/paper/2026/file/20dcab0f14046a5c6b02b61da9f13229-Paper-Conference.pdf)。本轮读取§3–4理论结构与bijection反事实、相关主文图表；未穷尽36页证明/代码。
- **idea来源：** 不预设task vector就是抽象程序；比较pair/triplet格式的linear-transformer优化，提出其为示例加权组合。由这个结构推导single-vector注入的rank-one限制，再用方向任务与双向bijection让完整ICL和task-vector预测分叉。
- **设计学习：** 先提出被移植信号的计算角色，再找正常行为等价、反事实不等价的任务。注入成功只证明该接口有用；失败也需对照完整ICL，不直接否定全模型能力。
- **证据边界：** rank-one推导有特定linear-attention/注入假设；实用LLM的saliency与行为相符不等于证明全网络都遵循该算法。
- **与ICES最近邻：** “一个状态可能是代表性证据而非完整规则”早已有解释。E93的metric、完整私人规则、B-verdict换算均能行为全对；需来源偏好及recipient证据竞争，不能靠一次before-input patch就宣称通用程序。

## 2026-10-12 再读与E129定位

- **来源/阅读：** [ICLR2026正式PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/20dcab0f14046a5c6b02b61da9f13229-Paper-Conference.pdf)。官方作者repo同camera-ready PDF读§1–7，含线性模型结构假设、pair/triplet/GD阶段、saliency、bijection与multi-vector；附录完整证明未独立校验、未运行代码。
- **idea/实验链：** 从TaskV有效但机制不明提出“单代表性demo”，用简化理论推出输入格式/有效rank，再构造单向任务均可做、合成双向难的对照，继而改多vector注入。对照揭露特定解释的表达能力，非只扩大benchmark。
- **范围审计：** 线性attention、结构化参数与特定prompt支撑推导；LLM saliency/失败形态是吻合证据，非所有高维多层task状态必然rank1。作者limitations承认简化模型与未给收敛/样本保证。
- **ICES距离：** 不把同sentiment＋private remapping或输入独立cue运输称新task vector。多Source selector的criterion/code功能内容与Source地址的区分可借其方向/能力审计，但整块多层KV不符合其单向量rank假设，不能机械套定理。E129候选应与Hendel conflicting-task实验、JIT实际scope共同对齐，不靠这些题材字面不同认定novelty。
