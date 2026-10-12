# Time-Reversal Provides Unsupervised Feedback to LLMs（NeurIPS2024 spotlight，所读作者v2）

`[证据级别：主文精读＋指定附录]` [原文](https://arxiv.org/abs/2412.02626v2)。本地缓存 `papers/reassessment-2026-10-07/yerram2024-time-reversal.pdf`（外置项目根目录），23页，SHA5878db6370ceddf213771083ffed3d6a381401b7eebaa3cda765588b6f8f21e2。2026-10-08核作者arXiv接收声明及PDF页脚；当前v3存在，未精读v3，不混称最终稿。

1. **问题/形态：** 无额外偏好监督的生成反馈→逆向条件评分及反向预训练→多个用途的重排。Google DeepMind/IISc；不是仅提出一个评分公式。
2. **idea来源（RECONSTRUCTED）：** 自我批判需强instruction-following且串行；从“答案正确是否也能解释为什么会问这个问题”转成response→query条件预测，再把反向token序训练引入模型。核心轴是反馈方向与模型训练方向，连接生成、检索与安全。
3. **近邻距离：** Self-refine依靠口头评价；Bayes/MI重排已有条件关系；这里训练逆序token模型、提供具体反馈系统。一般inverse reconstruction及best-of-N已有明确owner，不能作为我们的创新。
4. **方法：** Fo是普通模型用反向任务提示；Ba是逆序token预训练并FLAN微调；FoBa两种方向。重排16个固定温度候选；不是把同一forward LM的两个条件式当保证一致的Bayes joint。
5. **规模：** PaLM2-Otter私有骨干；reverse pretrain两TPUv5e pods约两周、FLAN约一天；Gemini/Mixtral proposal。AlpacaEval805、CNN/DM citation及检索、NF-Corpus/TREC-COVID/SciFact、JailbreakBench安全。不能把该模型默认当可下载低成本baseline。
6. **结果/边界：** LC Alpaca约32.44(Ba)对27.05(self-score)/24.38(single)；各检索集不都Ba最佳，NF-Corpus普通Fo/FoBa约48 NDCG而Ba约43。citation的Gecko/TF-IDF/ROUGE并非逐条人类引用正确率，不把“44%相似度提高”改写成44%忠实率。没有本文方法的RL训练收益实验。
7. **理论：** 重排分布为forward分布乘inverse conditional的幂；示意双部图/Hamming半径邻域假设下减少hallucination。近query对应answer集合须满足特定分离，不是自然语义或所有高inverse分都忠实的定理。
8. **阅读范围：** main1–7 pp1–10全部；AppA theorem/B算法pp15–16全部，C1提示p17全部/C2指定表8/9 p18，D/E部分pp18–20，G compute p22全部；H license仅部分。剩余安全逐项案例/最终代码未核。
9. **对I07：** 一般inverse feedback失败不够新。可辨别的增量是重建完整歧义观察时，早先片段与后来的关系修订产生相反credit，以及同原观察候选选择的后果。E103不是reverse-trained Ba实验，不能把结果当本文方法被证伪；也不能因为它已有inverse评分就在桌面关闭I07。
