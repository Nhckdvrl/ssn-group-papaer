# Router Prior Bias: Preserving Base Routing Structure in MoE Post-Training（Findings of EMNLP 2026，2026.findings-emnlp.2339；Lee, Kim, Han, Yun, Choi, Yoo，NAVER）`[证据级别：PDF 正文（pdftotext），表格列名未逐列核对]`

注：Findings 论文，按 R10 不作投稿目标，但可作 claim owner 引用。

1. 论文形态：受控比较（post-training 路由目标）+ 方法（软锚定）+ 诊断（三层路由保留）。
2. 背景与压力：post-training 重新施加均衡损失（LBL）会抹平 base 路由器已有的非均匀共激活结构；工程默认在两端（不约束 / 完全冻结，Unsloth 默认不训练路由层）。
3. 改变的前提：继承来的路由应"软持有"——均匀化与硬冻结都有代价。
4. idea 来源（RECONSTRUCTED）：把 base 路由器当先验（逐样本、逐 span 的平均门控概率），以零均值 log 偏置加到 logits；再用"打乱先验内容 × 软 / 硬执行"的 2×2 分开"内容"与"执行强度"。
5. 与最近邻的距离：相对 Routing Drift 2609.32821（交叉套用拆输入 / 参数），它**不拆**，只量 post-trained 与 base 路由器在各自隐状态上的保留；相对 Thérien 2503.05029（持续预训练饱和），它针对 post-training 并连到下游；相对 StableMoE（冻结），它说硬冻结有害。
6. 方法 / 数据：Moonlight-16B-A3B（主）、Qwen3-30B-A3B-Base（第二家族）、DSV2-Lite（附录）；math20k / coding20k / OpenR1-Math-220k；三种子。保留三层：利用率（TVD/JSD）、逐 token top-k 重合、共激活 Louvain 社区 NMI。表 15 中 top-k 重合约 .39–.48（SFT .469/.482，LBL .420/.391；列与模型对应未逐列核对）。RPB 在 Moonlight 数学上 45.77 vs LBL 31.91 vs 不锚 29.44。
7. 证据强度与短板：重合用各自模型的隐状态，路由器变化与输入变化混在一起；对不锚 SFT 的优势模型依赖。
8. 可迁移的研究动作："先验内容 × 执行强度"的 2×2 干预分离；把路由保留分三层量。
9. 对我们：(a) 我们 Base vs Instruct 同层路由差 21%（即重合约 .79）是同类读数——"post-training 改了多少路由"已有 owner（Qwen3-30B-A3B-Base 上），我们能补的是交叉套用拆分；(b) 它把"base 路由结构被继承"当前提并给功能证据，与 N4 的"路由器携带来源记忆"同向。
