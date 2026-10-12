# (QA)²: Question Answering with Questionable Assumptions（ACL 2023）

**证据范围：** primary PDF主文§1–6及部分§7；附录未读。[原文](https://aclanthology.org/2023.acl-long.472.pdf)。本次只补记暂停前已完成阅读，不新增实验。

1. 论文形态：自然问题诊断数据＋测量。
2. 压力：问题本身含false/unverifiable assumptions时，正常wh答案可能默许错误；不是只有模型不知道事实。
3. 改变前提：把完整回答、assumption detection和oracle assumption verification分开，不靠单一Gold字符串裁定自由答案。
4. idea来源（DOCUMENTED）：自然Google查询与已知unanswerability解释不足。
5. 增量：602自然问题，570 evaluation/32 adaptation；false与unverifiable区分，genuine presupposition与epistemic bias不强行一刀切。
6. 实验：QA专门模型与通用LM，zero/few-shot/ICL，完整答案100题×5human raters；最佳E2E acceptability56%，verification与实际回答并非一回事。
7. 短板：旧模型、开放世界知识/时间边界、少量人工E2E；未核对公开评分。
8. 可迁移动作：拆问句隐藏假设、事实验证和完整答法；外部审计不能把“理所当然”Gold当oracle。
9. 对我们：generic false-premise处理和识别/回答gap已有owner。E50“two names”可能是question expectation，不等于role memory lost；E51无该措辞是区分，仍没有natural transport或novelty认证。
