# Understanding Cross-Layer Contributions to Mixture-of-Experts Routing in LLMs（ICLR 2026，poster；OpenReview BqyPLOkxFY；arXiv 未找到）`[证据级别：会议页摘要 + papernotes 二手笔记；正文未读]`

作者：Wengang Li、Lingqi Zhang、Toshio Endo（东京工业大学 / Science Tokyo）、Mohamed Wahib（RIKEN）。代码：github.com/wengangli/routing-contribution。

1. 论文形态：构念引入 + 测量（路由分数的加性分解方法）。
2. 背景与压力：以往路由分析只看路由结果（专家 × 领域 / token），不问路由由残差流中哪些上游组件决定。
3. 改变的前提：路由分数是残差流的线性读出，可按"词嵌入 + 各层注意力（到头、query、key）+ 各层 MoE 输出（到专家）"加性分解；RMSNorm 的非线性按比例分摊（近似）。
4. idea 来源（RECONSTRUCTED）：把稠密模型的 direct logit attribution / 残差流分解搬到路由器上，并递归跨层。
5. 与最近邻的距离：相对 Ye 2604.17837（按子空间分）是按组件分；相对 Routers Learn Geometry 2605.12476（训练动力学）是对已训练模型的推理时分解；相对 super-experts 2507.23279，作者称高范数专家与高影响专家不完全重合。无随机 / 几何零模型。
6. 方法 / 数据：OLMoE、DSV2-Lite、Qwen3-30B-A3B、Mixtral-8x7B；C4。影响 = 某组件对同层各专家分数的方差；正 / 负分数区分促进 / 抑制；AARV = 置零某组件后 top-K 排名变化。发现：MoE 输出影响 > 注意力；词嵌入影响前两层最高、随深度迅速下降；"promotion is local; inhibition is global"；OLMoE M1、M4 层形成跨层"条纹"，置零 M1E9 显著改变 M5 / M10 / M15 的 top-K；IOI 相关头分数方差高；"MoE entanglement"（相邻层 MoE 激活共现）。
7. 证据强度与短板：页面无原始数值；自述局限：只到专家级、RMSNorm 近似、无理论预测 hub 专家。评审意见未读。
8. 可迁移的研究动作：把输出端的归因分解搬到中间读出器（路由器）上，并跨层递归。
9. 对我们：OLMoE 第 0 层"前一 token 头 → 路由器"（RESIDUALS §2，能量 8.5×）正好落在它的分解框架里；它的"词嵌入影响前两层最高"预测第 0 层按当前 token，与我们的观察相反——可作 Part C 第 5 问的对手。它的 Qwen3-30B-A3B 逐层结论也受层复制影响（未核对是否依赖层间独立）。日本作者组，导师可能熟悉。
