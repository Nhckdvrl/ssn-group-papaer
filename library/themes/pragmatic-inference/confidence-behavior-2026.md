# Causal Evidence that Language Models use Confidence to Drive Behavior（Nature Machine Intelligence2026）

[原文章](https://www.nature.com/articles/s42256-026-01293-x)；正文访问后转身份验证，不绕过；[作者公开v3](https://arxiv.org/abs/2603.22161v3)明确标最终DOI。**阅读范围：** v3引言、Methods pp4–12、Results主线pp12–20、Discussion pp21–24；统计/图表文字已读，图未逐像素核对、补充pp27–57与代码未读/未复现。

1. **idea来源 DOCUMENTED：** 动物confidence-guided meta-decision＋人类confidence formation/action policy两阶段理论；LLM已有外部calibrator与abstention训练，却缺模型原生使用信心的证据。改变的是“输出里能测信心”→“信心是否在行为控制里起作用”，并非首次发现不确定。
2. **研究动作：** 无abstain的Phase1先测LP/另调用VC，再同题加abstain；steer方向；最后明确阈值0–100。初期读数在行为指令前形成，避免用已含决策的Phase4概率解释决策。两种干预分别瞄准representation与policy；四模型/替代difficulty、RAG、embedding而非一个相关性。
3. **近邻ownership：** 自身回答是否提交的信心/阈值分离与steering已拥有；generic“criterion会移动”不足。文章说明是computational层架构，未声称transformer单forward的两个物理模块。E43的他人责任/意图归因是不同目标。
4. **需要保留的短板：** 原Llama70B因仅4%abstain未纳主分析；Gemma原阈值prompt不成功，20paraphrases选最高终点响应，迁移需预先固定并保留首版。不能在我们项目重复挑最佳恢复prompt。M2由same-task决策曲线拟合，mediation需要no-unmeasured-confounding，不能照搬百分比作因果模块分配。
5. **可借与不可借：** 同item、先测再决定、明确操纵成本/目标、held-out steering与cluster bootstrap值得借。群模型阈值差不证明RLHF原因；改变后还需要原理解成功与其它目标共同报告。claim是行为因果证据，不是任意概率差就是confidence。
6. **如何发展 RECONSTRUCTED：** 我们的未知是source/partner的信息选择过程如何进入具体解释与社会判断；未来要把来源证据与行动代价分开，让干预对两类解释给出不同预测。当前E49尚为文本parent驻留，不注册新方法或论文claim。
