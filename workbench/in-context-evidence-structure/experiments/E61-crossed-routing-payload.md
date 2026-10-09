# E61：来源key与标签value是否真正组合（2026-10-10）

- **状态：** DONE（2026-10-10；发现、预定独立确认及有界复现完成）
- **类型：** PILOT（检验推理桥梁：分别定位两种影响≠证明二者组合）
- **对应：** I04、C12/C13；E59 的 source-name K / label-anchor V 位置分离。
- **问题（一句话）：** 来源名字K交换和标签V翻转各自改变答案后，同时实施两种操作会恢复原映射，还是只是两个独立效应相加？
- **为什么现在做：** 若默认模型已经通过分布在不同位置的两条通路组合了source与mapping，则不能继续把“未能组合绑定与ICL”当作已证事实。可用双翻转的非加性交互对这一新候选解释作正面检验；这不是新head搜索，也不把非线性本身当novelty。
- **设置：** Qwen3-8B，无训练。base/source-swap/label-flip 四种语义关系中，两次翻转在理想任务下保持原函数。移植全部source_name K自source-swap缓存，全部label_anchor V自label-flip缓存：2×2干预(base,K,V,K+V)；再用label-anchor KV代替V检查label-key信息必要性；自然的source+label双翻转作保持函数的阳性对照；no-op重复。
  - discovery：64synthetic animals/fruits yes/no seed61001；48real E56 train-pool seed61002。
  - confirmation：64synthetic occupations/vehicles toxic/safe seed161001；48real E56 test-pool seed161002。
  - 每个context输入/次序/label频率配对等同，source/label均single token，query恒定。预定全部层同移植，不挑最佳层。
- **读数：** 以base真值计算m00,m10,m01,m11的mean source-correct margin；交互J=m11−m10−m01+m00，context-bootstrap95%CI；恢复差m11−m00、准确率；所有raw值与自然双翻转基线报告。加性路径在这套干预下J=0；理想双翻转近m11≈m00>m10,m01。恢复不要求“比分”超过base。
- **阳性对照：** donor source与label各自翻转应有可测作用；natural double应保持函数；no-op=base；缓存position一致；label V/KV两个版本避免对纯V可用性的过强假设。默认混合能力弱时只谈可测的计算信号，不靠相对小效应的比值包装成功。
- **噪声地板 + MIE：** 既有repeat=0nats；J>0.2nats且CI不跨0，双翻转距base≤完整单翻转效应的30%且明显好于两个单翻转，为进入下一机制实验的线索；未过阈值亦报告。不按结果更换指标。
- **混杂审计：** 配对所有词频/位置/内容；无训练、不提供query正确标签；自然joint donor确保task定义正确；发现/确认材料独立；raw bootstrap而非挑头；未控制：hybrid缓存引入非自然组合；J可由一般attention/MLP非线性产生，不能直接宣称新计算构件或精确串行head路径。
- **决策表（跑之前写）：**
  - 双翻转恢复、J明显，独立材料确认 → 默认已有来源与映射影响的可组合计算，否定“普遍不组合”的简单版本；转向组合强度/表示部署边界。
  - 单翻转有效、双翻转不恢复 → 分别有作用不证明可独立操作的composition；检验协作/耦合或干预失配。
  - 纯V失败但KV恢复 → 标签key亦承载关系，不能把mapping简化为value-only payload。
  - natural double不保持模型行为 → 词汇/材料/次序影响强，固定函数不保证相同程序；明确识别限制。
- **算力预算：** ≤0.3GPU·时；**实际：** 0.054 GPU·时（单卡进程墙时折算，含加载，非积分利用率）。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 独立synthetic确认：交互J，K_source×V_label为2.259[1.880,2.660]nats；K_source×KV_label为3.655[3.239,4.063]；后者双翻转仍低于base0.411nats，非完美恢复。
- 独立真实评论确认：纯V双翻转相对base−0.375[−0.485,−0.274]，加入label-K后仅−0.089[−0.168,−0.007]；J=1.201[0.979,1.449]。纯payload说法不足，联合key/value关系重要。
- 结果：`results/e61/*/analysis.json`。C15增加协作证据；不能由非加性直接命名新构件/精确串行电路，也不能说native两种能力普遍无法组合。
