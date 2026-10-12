# InT: Self-Proposed Interventions Enable Credit Assignment in LLM Reasoning（ICLR2026）

证据：[作者v1全文](https://arxiv.org/html/2601.14209v1)主文§1–7完整、AppC/D/E文本、F/G选段；[正式接收与稿件](https://proceedings.iclr.cc/paper_files/paper/2026/hash/89062e4d480c0c3a88d36c20c5694459-Abstract-Conference.html)已核对，正式主文§1–5完整、AppC原334结果选段，其他正式附录未全读，不冒充38页全部精读。正式PDF SHA f634d989e7ac32b7f49b6df640d9d9f3d2f76e369d0011821803fa12e9e53c8a。作者v1 SHA67f2aecbe80f06a570518922eee7637b42cde911de1c7e7dd5a69f269fcffd01。CMU/UIUC，Aviral Kumar组。

1. **问题与形态：** 方法题，从真实training痛点长出：困难题组全错使outcome RL advantage全零，整个失败轨迹又包含正确步骤，不能整体丢弃或同样惩罚。
2. **idea来源（RECONSTRUCTED）：** PRM估值与替代动作搜索都昂贵→验证给定解比从零解容易→用参考解让当前模型定位首错并给短替代步→保留on-policy正确prefix，SFT prefix+intervention，不克隆完整suffix→作为普通RL初始化。跨领域祖先是DAgger在自己访问状态上局部专家纠正，语言模型把专家动作部分转为给参考解的自验证。不是把“反思一下”当方法。
3. **操作与规模：** Qwen3-4B-Instruct2507主实验；Polaris/AceReason/OmniMath等约4500 hard pool，按原64/128次全错筛；1076 intervention在32次续写中至少一成功才保留。训练SFT4epoch、普通GRPO400steps/8rollout。参考解通常已有，部分由Gemini生成；“无强模型生成纠正”不等于整个数据全无外部监督。
4. **核心区别：** 334原pass128全错子集，再采32次，原题/正确prefix/原错误步/纠正后accuracy分别0.0984/0.0726/0.0713/1.56%；纠正覆盖80/334，原错步29/334。有限采样零成功不是理论不可解。prefix-only不是充分恢复。SFT同235子集prefix+intervention无suffix202覆盖/7.71%，加成功suffix111/2.31%，不训prefix162/2.87%。这是有后果的设计发现，不只给一张可读特征图。
5. **端到端边界：** 作者v1表四测试列混pass1（IMO/HMMT）与pass8（AMO/Apex），各由128rollout估计，不能统称pass1宏平均。InT+RL IMO25.62 vs普通RL23.46（+2.16pp），v1表Avg33.72含训练reward第五列，并非纯held-out四任务平均。主线只有一个模型族；附录e3-1.7B及更强纠正者扩展不作三族证据。NLL低与test收益相关，作者也承认不一定因果；不克隆suffix变更监督token/探索分布，没有证明通用“正确后缀有害”定律。
6. **近邻距离：** PRM已有credit对象、STaR/solution distillation已有参考解、hint-RL已有partial解前缀、critique已有重写，增量是自己的失败状态里短动作纠正及训练保留何部分。最高价值由方法能打开原无奖励区域并保留泛化提供，不靠找无人提过的名词。
7. **对我们：** 可借先局部辨错，再只干预会改变后续结果的步骤；E71具体关系消费与此不同，但不能将任意正确prefill失败包装为新意。当前不开数学/RL实验；若GP关系修订有稳定因果规律，才从这种痛点设计对应方法。
