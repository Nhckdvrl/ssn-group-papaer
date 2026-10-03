# E57：source-exposure-response（2026-10-03）

- **状态：DONE。** 协议与全量CPU gate冻结后八独立作业入队。
- **类型：REPRO。** parent公开证据干预的现代端点迁移；不是I01决定性pilot。
- **对应：C02 / P02。**
- **问题：** 待解释的原句和问题固定时，原clean/noisy句库能否改变解释？变化是否与literal任务目标分离，而无歧义理解保持？
- **设置：** E56前四alternation×20items×4条件=320原critical；完整48原filler作为仅含句子的exposure（18实际改动）。clean/noisy×两固定排列(seed20261003/20261004)×default/literal目标。原48 active/passive变体作共享语义控制（12item clusters），每model2944回答，8model23552；同E55八固定revision。只共同chat入口（Base用同family Instr tokenizer/template），Q3关闭thinking，FP32/eager，不裁切，不训练。
- **任务措辞：** 原Cai2024 yes/no comprehension要求统一用于所有cells。exposure仅显示原句，无question/response/答案或错误标签。default目标句前无额外解读指令；literal一句沿E55冻结指令。二者都是同一exposure内比较，不把措辞变化叫内在能力改变。
- **读数：** 原生成config greedy max_new_tokens=8；主要严格完整EOS的Yes/No(允许大小写/单句点或叹号/首尾空白)，其它与非EOS全部invalid，保留raw及IDs。每源implausible/plausible的noise−clean literal-rate及literal-goal−default配对效应，全部item为分母，invalid的上下界同时报告，禁止筛双方有效项或事后改parser。5000次seed20261003按source/Item cluster，两个排列分别报并报预定平均。无SDT或人为正确gold。
- **阳性对照：** plausible160句及独立12-item/48变体active/passive控理解；质量/invalid按context×goal×排列分别报。首末每cell独立完整forward的raw首token概率与generate output_logits比较LP<.001、raw argmax同、生成重复IDs同/token score差<.001；全部gate通过才科学预测。保留原processed与raw logprob，不混native repetition penalties。
- **噪声地板 + MIE：** 两个原句库排列检查history敏感性，不筛seed。10pp源内配对效应且bounds/cluster CI不含零可改变下一source选择；不是自动finding门槛。模型基本控制≥.95仅协议适用heuristic，未过也保存所有结果，不按控制表现筛item。20独立items/源不足小效应估计，后续规模需独立场景与人类规范支持。
- **混杂审计：** 原release仅18改动，与论文30不符；不补造。blocked句库不是人类随机interleaving，且source变化不唯一隔离channel noise，不能机制归因。两排列clean/noisy同slot顺序，完整history/prefix hash核对；源词汇/长度变化保留。共同chat与native generation config造成stage差须独立校对，不做训练因果。噪声句上下文仍为受控人类实验材料，不称自然会话。问题/候选/解码预算固定，0API judge。
- **决策表（跑之前写）：** A控制可用且两个排列同方向响应→跨独立speaker-knowledge/source材料测是否出现来源特有关系，不将本parent效应当novelty；B目标指令主导或context×排列变化→区分回答规范与证据使用，不追加prompt救分；C无歧义控制/invalid bounds不可用→该入口只报未识别，退回独立自然材料/数据构造，主问题不缩成格式bug。任一结果不自动关闭territory。
- **算力预算：** 8独立H20，有限锁队列，预计总8–24 GPU·时；E51已在占用时让其完成、实际显存<10GiB才进。**实际：** 成功八作业合计4.0555 GPU·时；此前Q3 r1作废时间另留raw，不计科学有效预算。

## 结果
- 跑前全8 source/backend/输入通过，最长700–830tokens，无裁切；`results/E57-source-preflight.json`。严格parser6阳/9阴/6非EOS控制全通过，`results/E57-parser-controls.json`。两对Base/Instruct实际inputs指纹相同。队列外置`E57-queue.log`，锁与E51协调；失败留档。
- 23,552/23,552完成；完整source/IDs/prefix/解析/EOS/数值校对通过，[原summary](../results/E57-exposure-summary.json)。技术gate通过不等于semantic controls通过。
- 每端点2944，invalid分别Q25Base2931、Q25Instr0、MistralBase2944、MistralInstr470、OLMoE SFT0、Q3-4/8/14均0；Base生成入口不能用于stage能力差。严格missing bounds保留，没有筛joint-valid或改parser。
- 所有control cell最差literal-rate下界：Q25Instr.9583，Q3-8 .9583，Q3-14 1.000；但critical plausible各cell最低为.800/.600/.750；其它端点理解/输出更弱。没有一个端点全材料同时越过预设.95 heuristic，不能自动解释为领域能力缺陷。
- 在E3 for-dative的implausible源内，default下noise−clean的预定两排列平均为Q25Instr−.1125，cluster CI[−.2250,−.0250]；两排列−.100/−.125。Q3-8 +.0625[.0125,.1250]，两排列+.075/+.050；Q3-14−.0125[−.0875,.0500]。这是预定多切片中的描述，不作multiple-comparison后的发现，源内20clusters也不足建立跨域统一解释。
- literal目标对上述Q25Instr clean/noisy的作用−.0125[−.0875,.0625]/+.0500[0,.1125]，并非统一恢复；不能把一种指令命名为能力校准。
- 决策表B/C：没有跨端点同方向channel响应，材料/入口规范仍须识别；不添加prompt保护局部效应。E58盲态语义审计区分event-role回答、world entailment与修复；回独立原source，不直接展开这一source的机制拟合。
- 主张：C02仍L0；I01仍SEED。
- POST-HOC：无。

2026-10-03执行修订：generation_config false被Transformers≥4.50 fallback为Q3默认true。8/14重复性gate失败，0科学预测；4B的受影响partial隔离并停止，未汇总。其他五端点配置回退规则需CPU完整核对后才允许科学汇总。保持原greedy协议不变，r2显式do_sample=False/use_model_defaults=False并逐token断言processed argmax；三端点新目录重跑，不改原输入/seed/parser/gate/MIE。原失败见results/E57-decoding-failure-audit.json，非科学异常。

补充核对：installed GenerationMixin._prepare_generation_config以各native pinned config与实际请求config重建，五个原endpoint所有非metadata字段完全一致，do_sample=False/max_new_tokens8/num_beams1；results/E57-effective-config-audit.json。Q3-4B受影响2175条全部隔离，8/14为0条。r2三端点完整16重复/独立raw gate全通过，逐生成token实际processed argmax断言生效，输入与原协议不变。
