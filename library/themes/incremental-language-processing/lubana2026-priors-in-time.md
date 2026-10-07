# Priors in Time（ICLR2026 accepted；作者v3主文精读）

证据：作者[arXiv v3](https://arxiv.org/html/2511.01836v3)（2025-11-24）§1–8完整、AppA1–7与B1；其余长附录未深读。[正式接收页](https://proceedings.iclr.cc/paper_files/paper/2026/hash/45f7d161845e402f69c8f8b4d04fa447-Abstract-Conference.html)仅摘要核对。最终PDF未成功取得，不能称正式全文已读；最终摘要称Temporal SAE，v3称Temporal Feature Analysis（TFA），作者列表亦有差别。外置HTML SHA dda8ce0df04ad1f4e77b1196b6c49b68cec4bdc8a767f9e7695b8430ce8516f2。

1. **形态：** 解释工具的前提诊断＋时间结构归纳偏置＋跨域示例，不是GP能力修复。
2. **压力：** 逐token独立稀疏编码很会重构，却可能拆碎时间上持续的事件/角色。高重构质量不回答解释对象的时间结构是否保留。
3. **改变前提：** 固定iid latent先验不适合非平稳激活；把可预测的持续成分与新残差拆开，仅对新成分施稀疏约束。
4. **idea来源（RECONSTRUCTED）：** sparse coding的MAP先验→神经表征的manifold/slow-feature观点→LM上下文自相关和有效维度测量→先验/数据错配→带历史attention的编码器。新意来自诊断旧工具隐含的统计前提，而不是多画一张UMAP。
5. **近邻距离：** 标准SAE iid稀疏方向，此文增加时间条件；Hanna的GP SAE可同时保留候选，此文尝试让工具显示时间一致的句法关系；Costa层次SAE改变特征组织，此文改变时间先验；Park in-context grid geometry已有，此文用分解后的code与干预展示；SFA/神经manifold提供观点，非LM-specific新理论。未读所有祖先全文，以上为本论文如何组织related work的重建。
6. **方法/材料：** TFA用共享dictionary、历史attention预测code及残差TopK/BatchTopK。1B预缓存Pile激活，Gemma2-2B layer12与Llama3.1-8B layer15，0-index，单H100；并非所有任务完整两模型矩阵。TinyStories及50个GPT5故事，50 GP/control（词汇或标点变化）；grid9节点/500步；Ultrachat1000对话。重构与ReLU/TopK/BatchTopK/Matryoshka SAE比较。
7. **强度/短板：** GP证据为phrase-mean cosine/层次聚类，未测试源支持QA、自然角色输出或GP任务因果恢复；grid换最后token的PCA成分只4/9节点成功。事件边界为GPT5标注，不是独立人类norm。predictive约80%norm不等于80%语义；U-stat有效rank依赖生成假设，不能直接叫概念数。训练双分支竞争、Llama TopK不稳改BatchTopK，深层表现不同；残差仍iid、auxiliary attention可能增加上下文处理而非忠实分解原计算。作者明示系统因果评价待做。
8. **可迁移动作：** 先问解释工具的前提是否隐藏了对象，再换可检验的前提；“几何匹配”与“可用于正确行为”分开。平滑不是功能充分性，后者应直接实验。
9. **对我们：** 自然cue源轨迹的因果作用不认证正确parse；E64局部正确与完整绑定应分开。不能仅用他们“GP正确parse”措辞认定题被覆盖，也不能把功能缺口自动当我们的novelty。应找有价值的关系修订规律，而非补一套工具评测。
