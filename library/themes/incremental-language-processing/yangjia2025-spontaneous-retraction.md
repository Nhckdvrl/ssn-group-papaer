# When Do LLMs Admit Their Mistakes?（Yang & Jia，2025 v1）[证据级别：部分正文]

来源：[arXiv v1](https://arxiv.org/html/2505.16170v1)。读§2、§3.1–3.2与摘要；§4–6 probe/steering仅定位，未细读/执行；不声称已接收。

1. 论文形态：模型主动承认自身生成错误及其解释。
2. 压力：知道相关事实不保证主动撤回错误答案。
3. 前提：retraction定义为即时承认错误，不等于之后给出正确答案。
4. idea来源（DOCUMENTED）：由自动self-correction的启动问题提出。
5. 距离：将主动承认与外部verification prompting区分。
6. 方法：三个模型、Wikidata/Celebrity模型专属continuation；保留能在单独验证题中指出冲突的错误答案；LLM judge算precision/recall。
7. 边界：这是经过筛选的可纠错知识设定；我们未核查mechanistic/SFT证据。
8. 可迁移动作：分别测能够查到事实、是否主动承认、实际后续使用，避免混读。
9. 对我们：泛化“知道却不修订”已有owner；外部报告被撤回后的角色预测不是自发retraction，不能靠换术语注册增量。
