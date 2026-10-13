# E13：作者公开的 PCSP 已训练政策原生闭环（2026-10-14）

- **状态：** DONE
- **类型：** REPRO（D1–D4；不是新idea）
- **对应：** E06 / E08 / C01。
- **问题（一句话）：** 不从随机FiLM梯度或作者表格推断行为，直接恢复公开已训练v3 policy的角色→观测→action→needs/reward闭环，检查内部检索与原生行为的解释范围。
- **设置：** PCSP@5420f7b…；公开research/results/pcsp_v3/full/policy.pt及persona_embeddings_300.npy，作者test_60_v3前4条，原MiniInzoiV3Env，每episode40cycles，seed801/802/803；torch CPU/原policy权重/原env。推理期间不改变persona配置、奖励、动作语义。必要反事实仅同state更换policy输入embedding（不执行改动世界的对照）；作者已有shared-state KL，所以这只作恢复阳性对照。
- **读数：** 每NPC raw obs/logits/chosen action/native state pre-post/reward/时间；persona preferred_actions及style条款单列；饥饿等8needs不叫人格效度。原policy参数完全load严格核；embedding/weights/text/split hash；完整失败保留。
- **阳性对照：** weights不是LFS指针且严格load；固定seed重复action/world一致；确有action改变needs/位置；同state persona KL只证明policy输入有因果作用，不独占新颖性。
- **噪声地板 + MIE：** 3seed全保留；n=4角色的prototype只作baseline资格，不给总体persona–utility结论；标准v3已有0.5偏好和style reward不能当独立一致性gold。
- **混杂审计：** 公开300 embedding与300 policy对应，不拿500 policy随意配300编码；与v3-large官方独立behavior table条件不同。无模型训练、无API、无LLM裁判。其他agent与环境feedback会影响轨迹，不能把trajectory分类归因直接policy文本。
- **决策表（跑之前写）：** 闭环成功且persona影响明确→承认persona到行为可有效；内部/外部测量差异→先对齐协议，不发明gap；不可load或资产不齐→报告未复现，不替换随机policy冒充作者。
- **算力预算：** CPU≤10分钟，GPU0；所有公开权重/rawtrace保存在研究cache不进Git。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
尚未运行。

运行前核验补充：公开v3/full目录只有indist60评价，不是zeroshot checkpoint；选取test_60文件的前4条仅固定角色选择，**不声称这4条未参与该权重训练**。

已跑通3×160=480原生动作（另160精确重放），全部通过原AEC动作空间；seed801行动/世界trace SHA完全重现，CPU推理loop0.332秒、0GPU/API。原state下改embedding的平均KL为4.886/6.595/6.049；作者已有shared-state KL，所以这不是新发现。241角色以社交为主，242工作为主，243/244更多样；人物条件确实可强烈控制行为，不能预设persona只有表达效果。40cycle仍未到严重need耗竭，此刻不能声称缺乏长程needs管理。与作者500-persona独立probe/UE5/MeltingPot条件不同。
