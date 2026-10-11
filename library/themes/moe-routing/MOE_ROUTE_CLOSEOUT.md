# MoE 路由偏好与实际 Top-K：负结果

原 `workbench/moe-route-preference/` 已 CLOSED 并从当前树删除。旧测量及所依附 CT03 的文件如需核实，从 [清理前历史](https://github.com/Nhckdvrl/ssn-group-papaer/tree/81e319fdc3414b7b6d16c8950f0046646d198cb1/workbench/moe-route-preference) 和 [CT03 快照](https://github.com/Nhckdvrl/ssn-group-papaer/tree/81e319fdc3414b7b6d16c8950f0046646d198cb1/archive/candidates/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING) 读取。

在固定 target 的探针中：pairwise preference accuracy = **0.947**；preferred-route overlap 从 **3.77/8 降至 1.05/8**；exact preferred route adoption 为 **0**；被执行的 slot 中 **80.8%** 不属于偏好或被拒路由。这说明**双路偏好目标的拟合不是竞争环境下确定性 Top-K 执行的可靠代理**。

该方向的广泛“路由反事实比较及最小改动”已有 *When Are Experts Misrouted? Counterfactual Routing Analysis in Mixture-of-Experts Language Models*（2026）等强近邻，旧项目没有独立 paper 贡献；不要以“换个 ranking loss”恢复研究。
