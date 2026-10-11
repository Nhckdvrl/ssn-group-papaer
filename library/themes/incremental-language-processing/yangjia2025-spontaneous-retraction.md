# When Do LLMs Admit Their Mistakes?（Yang & Jia，2025 v1）[旧v1部分正文；最新v4完整主文见补充]

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


## 2026-10-07：最新v4完整精读补充

[作者v4（2026-08-06）](https://arxiv.org/html/2505.16170v4)主文§1–8完整、AppA/B、C1/C2/C6–9文本/表格；C3–5未深读。SHA262e9a2b6fdb5c0f35dabb6a85137734f024ea44faf2701fe30e57a20e2e464b。arXiv作者备注COLM2026，正式会议稿/评审未另核对。原v1阅读范围保留，本次才升级到MAIN_TEXT_READ。

- **idea生长（RECONSTRUCTED）：** CoVe/Attention Satisfies/反转诅咒提供已知事实却错答的实际场景；把最终答对改成不要求正确替代答案的自发撤回；再问旧truthfulness probe到底代表客观truth还是生成当下的判断。三个模型专属testbed→外部probe预测→双向因果控制→W/V分解→SFT后复用旧方向。贡献在操作定义与机制连贯，不在新probe算法。
- **数据：** 原Wikidata重建2000/1160问题、Celebrity1584/800。保留独立verification可识别冲突的错误回答；正确集不足时用已知gold补充，不是全部自然自生成。测试Llama1202/826、Qwen1072/1142、OLMo1260/1209；后两Celebrity不平衡、无训练集。UTQA为NQ/TriviaQA/SciQ各800、真假均衡，false由GPT4turbo生成；不是retraction标签训练probe。模型专属筛选不宜用裸召回作总体能力排名。
- **核心结果：** 三族Wiki撤回recall25.79/11.19/13.17%，Celebrity14.77/2.90/1.50%。最后answer token的true−false均值方向正/负steering控制继续生成和撤回，负向跨全体常超过70%撤回，但连正确回答一起撤回、precision常约.5。不能称70%事实修复。
- **高信息量机制分解：** Llama is-appended Wiki baseline recall.574，patchW .594、patchV .9784、fullsteer .9717；Celebrity .1429/.1574/.5569/.8232。K48 salient W heads vs所有层最后token V的干预范围不匹配，不是等规模每维效果竞赛；但排除仅立即停止这个解释有价值。OLMo is-appended需要alpha从1.5改5.0，不能叫完全同参三族机制强度一致。
- **训练与迁移：** LoRA2epoch/1e-4/batch8、单A6000，固定is (not) the correct answer目标；旧probe/steer在SFT后仍有效。它说明原可操控子空间被保留，不证明训练只有belief校准一项改变。条件steer使用另一个ID正确性probe(.819 accuracy)，LlamaWiki recall.7421/precision.8051/F1.7723 vsSFT .8453/.7815/.8121，是实用增量但没有认证OOD方法收益。
- **最新数学例子的边界：** 188个原greedy错例，强judge标首错；实际steer首错加前9个token、layers0–18，不是只改首错token。负/正恢复37.77/17.55%；main“20%”与表中两方向差约20.22pp相合，不能混成负向绝对恢复20%。原正确prefix也被改动，不能用它认证保留正确前文的局部机制。
- **对我们：** 一般知道却不自发更新、当下判断影响后续行为、V比W重要均有近邻。E71完整切P1消费只定位该路径，不单独认证语法或真值因子。真正可借动作是先确定研究对象，再用独立任务构造可操控信号，分解它如何产生行为，最后看训练是否沿用；不是对GP直接套一个belief方向就声称新方法。
