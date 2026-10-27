# 几何、单专家预测与跨历史功能分工（2026-10-27）

## Myth of Expert Specialization（arXiv 2604.09780v1，31页全文）

1. 形态：表示几何测量与router理论。
2. 压力：usage与人类语义并不简单对应。
3. 前提：线性router把H的几何传到logits；生成阶段也需研究。
4. 来源（DOCUMENTED）：线性投影与共享方向/负载均衡。
5. 近邻：MoE Lens、CommitteeAudit、预训练报告；本轮未据这些引用自动判断增量。
6. 证据：5个预训练MoE的表示/路由，文本与轨迹比较、prefill剪枝损伤。
7. 条件：几何上界含主子空间余项；LB证明用简化损失、小logit及中心化噪声。
8. 动作：区分同题、生成文本、读出模型和权重来源，避免把usage直接当职责。
9. 对我们：几何与历史共同学习；母问题需因果函数和重用读数。Fig.6重放实现未明确，不代填。

## MoE Lens（arXiv 2603.05806v1，15页全文与notebook）

1. 形态：路由分布、局部读出、整网预测测量。
2. 压力：专家冗余与部署成本。
3. 前提：检验少数高门值专家是否保持输出。
4. 来源（DOCUMENTED）：LogitLens与残差中的专家增量。
5. 近邻：DeepSeekMoE/OLMoE、TunedLens；当前只核本篇及所用代码。
6. 证据：DeepSeekMoE主实验，附多架构路由图；top-k PPL整网前向保留shared/残差。
7. 条件：图按域内平均log PPL再min-max；历史HF revision未锁，未独立复现其数值。
8. 动作：把局部Lens与真正后续传播分开，并显式控制始终激活计算。
9. 对我们：E155区分R、S与D的任务依赖；E156问历史形成的配套如何实际重用。

原始PDF/文本与SHA在MoE阅读manifest，具体作者代码行号在reading_terra_code_check；不作贡献上限或开关线判断。
