# Disentangling Indirect Answers to Yes-No Questions in Real Conversations（NAACL2022 main）

**证据范围：正文§1–7/related work完整；附录A3 hyperparameter、A4/error、Tables5/6/11/12已读，A1及全组合Tables7–10未逐行核对。** 原repo源码仅README，未GPU复现；公开评审未核对。[论文](https://aclanthology.org/2022.naacl-main.345/)，[原repo](https://github.com/krishna-chaitanya-sanagavarapu/SwDA-IA)，clone SHA97e77c519e581ec53d14bdf1fb7e13404bb76838（2026-10-03）。

1. 形态：真实语料/构念与controlled measurement。原SwDA1155电话对话/2544间接问答，人工五类（Yes/PY/Middle/PN/No）；同题两批独立human分别只看QA或前后三轮，并在完整context条件标证据turns。不是从摘要宣称缺陷。
2. 压力：Circa是自然语言但**按设定众包**，与自然发生的对话不是一回事。真实对话会延迟回答、提出澄清、修正背景，QA两轮不够。例“within the state”在后续明确“not local”被解释No，前期Yes是当时可用证据下的合理解释，不是FPR。
3. 前提变化：让human gold随已提供的context变化，不给被遮挡的模型完整上下文gold当能力判决。提供有用turn annotations区别信息缺失与context利用。
4. idea来源DOCUMENTED：真实对话/早期yes-no理论与Circa取材对照，发现ground truth随上下文改；非怪prompt造bug。
5. 最近邻距离：deMarneffe2010真实gradable224项→广2544；Circa两轮/合成情境→自然多人持续上下文；传统NLI/BoolQ→交际解释；相关任务数据迁移有限，本身已owned，不可claim首次。
6. 实验：conversation不跨70/15/15split，RoBERTa(BERT/TOD-BERT差<.02)fine-tune多corpus组合，QA/full/annotator-selectedcontext；main最佳QA F1.46、full同组合.40、oracle-selected最佳.49。200MRDA跨domain最佳.38；论文调学习率3×epochs3×batch2并选dev，未见多训练seed统计，不自动当确定causal机制。
7. 证据限制：human7native，pilot200多标κ.80、后2annotators+adjudicationκ.81/.78；annotations含未来2–3轮，测offline理解，不能当前turn动作预测。原source只README写待发布；2024 IndirectQA也明说没取到。不能以原PDF6例当大样本、更不能模型补gold。
8. 可迁移动作：同utterance/candidate两种真实证据条件各自human norm；提供human证据turns作为oracle对照，将未给信息/给了不使用区分；按实际context变化而非单侧average分类。
9. 对我们：与最初推断边界更匹配，但资产当前不可运行。不是关闭对象，保留可重新驻留条件：取得author original两批labels/turns，校对human-key/speaker/timeline再跑。不能继续局部Circa选项偏差救故事。
