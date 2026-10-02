# Addressing the Binning Problem in Calibration Assessment through Scalar Annotations — TACL2024

[论文](https://aclanthology.org/2024.tacl-1.7/)

- 阅读：正文§1–7完整；附录证明/implementation未完整读，code/scalar raw未取得，原训练不复现。不能标全文。
- 来源DOCUMENTED：ECE分箱影响model排序；human多标签与直接scalar annotations如何降低观测成本而支持instance-level评价。UNLI/ChaosNLI既有资产先验证scoring function，再给下界和新标注，不从新metric直接宣称知识。
- 方法ownership：expected label scoring、calibration下界、ranking风险与regression、scalar/distributed映射、scalar联合训练；已经直接应用pragmatics CIRCA，不可claim首次human uncertainty校准语用。
- 关键限制：scalar不是完整probability vector，ranking invariant to constant shift；正文建议能回归就回归。UNLI f(ENT,NEU,CON)=(1,.2,0)有主观解释和任务假设，理论下界不是模型latent sensitivity。
- Circa：stratified300原8类别（排Other）、3-way annotation，先5题qualification/heldout correlation>.6；同批近邻score辅助校准。BERTbase/large、GPTNeo1.3/2.7经Circa训练；MAE .183/.179/.167/.155，而ECE-5/.100排序不稳定。Cond mapped .6、Unsure/NA mapped .5，不能把这个映射当唯一语用规范。
- 可迁移动作：把所需semantic event先写清，已有human数据优先；防止annotation protocol/label collapse把“speaker意思有多强”与“预测正确率”混为一谈；多维情况保留分布而非强压一scalar。
- 对我们：E33/E34是instrument/boundary probes，不能靠Brier/MAE/JSD新榜单成为paper。值得追问的是证据来源与真实stage如何改变合适推断的条件结构，需自然同对象证据和跨family才可能超越该ownership。
