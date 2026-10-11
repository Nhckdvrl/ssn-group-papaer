# SADA：内部对齐与输出蒸馏的证据链

- 主来源：[ACL2026 Main1046](https://aclanthology.org/2026.acl-long.1046/)，[正式PDF](https://aclanthology.org/2026.acl-long.1046.pdf)。2026-10-12读§3–4.4及Table3；未复跑作者代码。
- idea来源（论文论证重构）：上下文→参数方法深层状态偏离full-context oracle，拆成映射输入接口与监督信号。单层局部线性化支持attention-output接口，不宣称整个多层模型线性。
- 实验链：共享mapping/训练配置比较输入feature；固定StageI/architecture/20-shot/压缩政策，仅移除StageII hidden-state loss或LM loss；最后concept/QA和summarization揭露压缩作用范围。所有改动是辅助模块学习，不是完整native电路逆向。
- 方法学习：同最终分数可能内部状态不同，但MSE匹配本身不是反推原生算法。理论motivated接口与干预/实际功能验证接上，不只探针相关。
- ICES距离：不做context→weights/训练修复，也不能首次泛称信息存在但不可deploy。形成监督的来源、输出身份、公共关系与joint私人规则部署的反事实是当前具体对象；E126whole-cache交互未识别独立ID结构。已有形成阳性不因相似“state alignment”词自动撤回。
