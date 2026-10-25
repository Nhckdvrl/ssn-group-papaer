# MoE 受控重现性：补充论文卡（2026-10-25）

本轮只核对以下注明的正文，不冒充全篇证明复核。应用报告见 `workbench/mechanism-population-dynamics/knowledge/research/MOE_INDEPENDENT_AUDIT_2026-10-25.md`。

## On Linear Mode Connectivity of Mixture-of-Experts Architectures（NeurIPS 2025 Oral）`[证据级别：正文相关章节与附录实验，证明未独立复核]`

[原文 v2](https://arxiv.org/html/2509.11348v2)；本轮阅读 §2–6、附录 E/F、G.2。

1. **形态：** 理论 + 受控实验。
2. **压力：** MoE 带门控和专家排列，普通神经元匹配不能直接发现低壁垒。
3. **改变的前提：** 先匹配专家顺序，再匹配专家内神经元。
4. **来源 DOCUMENTED：** 从 dense LMC / weight matching 延伸到 MoE。
5. **距离：** 相对 dense LMC 增加 MoE 对称性与匹配；相对我们的 X2，它已经冻结预训练骨干、插随机 MoE、独立初始化训练，我们增加的是职责证据。
6. **实验：** GPT-2 / ViT，多种数据；3 个初始化；主 SMoE 为 top-2；对齐后测插值路径损失。
7. **短板：** 低壁垒不等于专家职责相同；附录 E 说明部分层本来不敏感。理论含强可辨识假设，主 SMoE top-k 内归一化。
8. **动作：** 用共享骨干固定接口；先量层的重要性。
9. **对我们：** 直接复用为平台先验，不能认领平台新颖性；不借理论断言有限数据上的近似解只有置换。

## RouterInterp: Understanding Superposed Specialisation in Mixture of Experts Routing（2026-10 预印本；会议信息本卡不另推断）`[证据级别：正文 §3–5、7]`

[原文](https://arxiv.org/html/2610.11775)。

1. **形态：** 构念与解释方法。
2. **压力：** 一个专家一个领域的假设解释不了路由。
3. **改变的前提：** 专家可接收多个不相干微特征。
4. **来源 DOCUMENTED：** 特征叠加、干扰最小化与负载均衡。
5. **距离：** 相对 token n-gram 解释用 SAE 特征；相对 Expert Strikes Back，它重点解释被路由的条件，未把解释准确率变成反事实职责。
6. **实验：** OLMoE / gpt-oss，自动解释与预测；不含独立预训练种子对比。
7. **短板：** SAE 与解释器质量限制；§7 明确把“为何是这些特征组合、输入相似还是功能相似”留作开放问题。
8. **动作：** 用微特征组合提出可检验预测，不再依赖 noun/verb 单标签。
9. **对我们：** 有最接近的开放问题表述；增量必须是独立训练与实际计算效用。

## GaP-MoE: Explicit Expert Specialization via Orthogonal Gradient Accumulation and Projection（2026-10-21 预印本）`[证据级别：正文 §3–4 与附录配置；理论未验算]`

[原文](https://arxiv.org/html/2610.29355)。

1. **形态：** 优化方法 + 小规模实证。
2. **压力：** 专家表示趋同，路由/相似性正则可能干扰训练。
3. **改变的前提：** 直接改变 follower 梯度，按 leader 历史梯度子空间投影。
4. **来源 DOCUMENTED：** 不同专家梯度重叠导致输出趋同的诊断。
5. **距离：** 相对改 router 或加 orthogonality loss，改梯度；相对我们的测量问题，输出夹角只作为分化指标。
6. **实验：** 4 experts / top-2，BERT GLUE 与 GPT-2 预训练；3 seeds 汇报性能，另有随机路由；输出图部分为单 seed / 单序列。
7. **短板：** 没测跨 seed 的职责对应；输出差异不自动说明语言计算分工。
8. **动作：** 路由和专家更新可分开；可作未来受控扰动，当前不必加方法。
9. **对我们：** 最新近邻说明输出夹角本身不新；不据未经复核的理论把该方法当确定机制。
