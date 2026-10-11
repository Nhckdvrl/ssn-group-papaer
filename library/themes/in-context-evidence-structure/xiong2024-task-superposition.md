# Xiong et al. — Everything Everywhere All at Once

- 原文：[arXiv2410.05603v1](https://arxiv.org/html/2410.05603v1)，2024-10-08；未核正式venue，不把预印本冒称ACL。
- 本次阅读：全文§1–9、附录B/C实际评分与task-vector选择；§5/D只核构造的解释与假设，未独立证明全部定理。
- idea来源：混合不同任务的无来源例子，next-output分布可能同时支持多个任务；不是“一个答案必须混合”。从这一观察到单任务训练模型的能力、理论existence，再到内部任务向量/因果插值。
- 实验切口：§6用LDA观察混合状态，再用两个task vectors的凸组合移植，比较实际混合示例。两者都能改变任务答案概率；插值更多无关答案、关系更不线性，作者明确说充分构造不等于完整解释。
- 技术范围：附录C平均100条dummy-query最后delimiter特征，按100新query准确率选层；公开两任务集层14/19。不能拿LDA几何直接断言原生计算严格凸混合。§7比较top-K覆盖和分布校准，不是命名Source的正确条件选择。
- 与ICES距离：已有多任务并存、task-vector组合及更大模型改善的范围，不可称首次多规则计算/叠加。ICES来源身份要求在共享输出上选择合法标准，候选E129同名Cue在固定recipient历史下比较criterion×code方向；不会用向量移植本身宣称novelty。
- 设计启发：构造性干预能复现大趋势仍须对照它复现不了的功能，而非因为两个曲线相关就宣布同一机制。E128的code与criterion范围差异正应这样解释；E129全多层KV块不等于该论文一个task vector。
