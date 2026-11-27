# 相关工作与定位（D5 初稿，2026-11-27）

**完整文献地图：** [`library/themes/training-post-training/SUBLIMINAL_LEARNING_MAP_2026-11-26.md`](../../library/themes/training-post-training/SUBLIMINAL_LEARNING_MAP_2026-11-26.md)，约 50 篇，标注了阅读深度与核对状态。本页只列与 M1–M3 直接相关的近邻。
**更新规则：** 主旨改变、主张升到 L2、进入候选前，都要重扫近邻（AGENTS.md §3）。

## 1. 定位表
| 近邻 | 状态 | 它的 claim | 设定 | 与我们的关系 / 增量 | 压缩风险 |
|---|---|---|---|---|---|
| Dubiński et al., *Beyond Owls*（2610.10657） | 预印本 | 能力、后门、黑客倾向能经 SL 传递（存在性证明） | Qwen3.x；LoRA；多为 logit；单一教师 | 我们沿用它的后门设置作为阳性起点，但改为**反事实析因教师 + 种子地板**，问的是“传递的是身份、成分还是功能”；它自己写明“we leave a systematic study of when such transfer occurs to future work” | 中：如果我们只报告“后门也能在别的语言上传”，就会被压缩成它的扩展 |
| Chen et al.（2610.04907） | 预印本 | 硬标签的样本复杂度来自 Fisher 逆与采样噪声 | 单 steering 向量；SGD；动物偏好 | M3 直接检验它的预测能否外推到条件规则与新知识；M1/M2 不依赖它 | M3 高；M1/M2 低 |
| Feng et al.（2611.10397） | 预印本 | 正则放大迁移；最优正则取决于特质复杂度 | 偏好为主，附录 L 有计数与后门 | 我们的 I06 回答它点名的未解问题（单教师无法区分知识复杂度与教师 rank）；M1/M2 是不同的问题 | I06 中高；M1/M2 低 |
| *Base Models Can Detect Hidden Intentions*（2610.36202） | 预印本 | base 模型似然（PHLE）能解码 SL 信号；prompted 分类器不行 | OLMo / Qwen；偏好与 secret-harm | 它展示了“可解码”与“学生弱迁移”的落差，但**没有用反事实知识内容测学生按成分得到什么**。M1 把这个落差变成系统测量 | M1 中：必须超出“能解码 ≠ 能学到”这一句，给出成分级的读数与跨通道、跨模型的规律 |
| Zhao & Zhong, *Cross-Trait Transfer*（2610.04260） | 预印本 | 跨特质迁移矩阵；学生学到相近而非相同的特质；动态从“广泛”到“特异” | 偏好簇 | 我们的对象有独立真值（规则成分），而不是偏好相似度 | 低 |
| Amjith et al., *Crosses Modalities*（2611.31870） | 预印本 | 图像表征偏移不区分情感；weight lens 能读出情感 | Qwen3-VL-8B；硬标签；prompt 教师 | “吸收了但没表达”的现成例子，支持三层读数；我们在可控规则上系统化 | 低 |
| Blank et al.（2606.00995） | NeurIPS 2026 | SL 是 steering vector 蒸馏 | prompt 教师；偏好 | 规则型知识是否超出单向量（Beyond Owls 显示部分超出） | 低 |
| Schrodi et al.（2509.23886） | ICLR 2026 | divergence tokens 承载信号 | 偏好 | 编码层读数与之相关（似然差） | 低 |
| Behrens & Zdeborová（2506.14457） | ICLR 2026 | 软标签能泄露教师记忆的留出知识 | 随机数据；GPT-2 实验用的是教师训练数据的子集 | 如果我们的结论只剩“软标签能传随机知识”，就会被它压缩；我们的输入是语义无关载体，问的是成分与绑定 | 中（只对软标签结论） |
| Stanton et al.（2106.05945）；2505.15442 | NeurIPS 2021；ACL Findings 2025 | 蒸馏后学生性能与 fidelity 不同步 | 普通 KD | SL 是 fidelity 问题的极端、可控情形；可作为论文的更大背景 | 低 |

## 2. 理论与方法近邻（Stage 3 或讨论时用）
- **Li et al., ghost kernel（2609.23260，NeurIPS 2026 workshop）：** 跨任务核，但没有在 LLM 上测过。
- **Malladi et al.（ICML 2023）：** 早期 Adam ≈ SignGD 核。
- **ICML 2026 *What Makes a Strong Model?*（2606.01292）：** 知识迁移的统一谱分析；学生输入与教师数据同分布，不覆盖“载体 ≠ 评测”。
- **Nagarajan et al.（NeurIPS 2023）：** KD 夸大 GD 沿主特征方向的隐式偏置。
- **Saxe et al.（PNAS 2019）：** 逐模式学习。
- **Xu et al., V-information（ICLR 2020）；Hewitt & Liang（EMNLP 2019）；Voita & Titov（EMNLP 2020）；Hewitt et al., conditional probing（EMNLP 2021）：** 区分“信息存在”与“信息可用”，探针结论要配对照。
- **Physics of LM 3.1 / 3.2：** 存储 ≠ 提取 ≠ 操作。组合类任务必须先过直接学习门控。

## 3. 撞车警戒
- 任何新出现的“用反事实 / 析因教师测 SL 迁移成分”的工作，都是直接竞争。每次人审前用 `python3 tools/venue_corpus/query.py nearest "<主旨>"` 加 arXiv 关键词（subliminal + counterfactual / factorial / component / identity）重扫一次。
