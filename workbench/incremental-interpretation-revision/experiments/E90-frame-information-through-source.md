# E90：正确frame信息能否经源解释迁移，而不是留在答题提示中？（2026-10-08）

- **状态：** DONE；生成器E431在任何forward/科学效应前改E90。
- **对应：** I06 / P19 / C06–C09；完成E88/E89后先[尺度对齐](../REASSESSMENT_2026-10-07_2355.md)，退出Hint时机/词位mask局部块。此处唯一源中介pilot，不是论文完整控制链。
- **问题：** E89的EARLY框架语法信息能否在Q未知的Source计算里形成可供原全部问题使用的影响？答题时不提供Hint原文。Gemma两构式正关系改善是已知探索线索，不挑Gemma或挑baseline错的条目。
- **数据：** E89完整151发表组/302源/784QA，原S/Q/Gold不变、三当下族/两words mappings，0新数据/0API。
- **条件：** NATIVE_BANK、FRAME_BANK；对每Source在无Q原生prefix/同一EARLY Hint原生prefix计算，记录每层Source残差输出。两个条件的回答prompt均为原无Hint native；每层仅将Source位置输出替换为对应缓存，其余位置不变、不跨位置移植。FRAME供给来自相同原S、有正确frame信息的源计算；NATIVE_BANK控制源冻结与prefix数值布局。Q未知、没有Q/Gold进入缓存。E87实际NATIVE及E89实际EARLY作为外置完整参照，不把不同layout参照当主因果差。
- **范围：** 全源残差bank是功能通道干预，并非单一valence语义因子。Gemma共享KV/Ministry native系统/Qwen混合循环结构保持，早期attention/recurrent cache不是完整donor，不能称整网完全正确parse。Source位置顺序/相同token IDs逐条验，Hint绝不出现在回答prompt；位置prefix长度变化可能含通用提示作用。
- **主读数：** 实际greedy32token正确率下/上界，FRAME_BANK−NATIVE_BANK、各自相对既有native/early；初始/最终/原全部Q joint。构式/GP-cue/GoldYes-No全部族分别报。与E89相同Source→lexical cluster/bootstrap10000 seed90；不是按成功条目筛cohort。正角色与既有正确其它角色一起读，未指定QA而非新的语义金标。
- **阳性对照：** 每族输入ID固定首个source完整小仪器：没有hook的native两次输出完全相同；同一full prompt捕捉Source再放回的SELF_BANK输出token逐字同native，Source替换及非Source不变逐层assert。prefix-bank与原native的数值/答案差单列，不隐瞒BF16布局漂移。原cue全量为任务地板，FRAME的已有EARLY用于解释外部信息上界。
- **噪声地板：** 两mapping实际语义分歧、cluster CI、NATIVE_BANK−原native全图；若基线冻结严重改变正关系/正确其它关系，不能用FRAME null否定源解释。未知/cap全量上下界，不添加空格/温度校准网格。固定单任务/greedy布局，科学效果前不选择模型/层。
- **决策表（跑之前写）：** 无答题Hint仍有正关系恢复且其它关系基本保持→可携带源影响值得挖，下一从具体frame转换后果发展解释与方法；只GoldNo变化→源通道仍只是解除/断言收缩，下一由自由角色确定替代解释对象；全局收益只在显式EARLY存在→答题策略/直接Hint消费提高优先级；baseline或cue显著崩溃→此pilot不能判源机制，保留结果，回真实错误内容，不延展Source层/边网格。探索先选idea，不要求今晚达L2/论文标准。
- **算力：** ≤3GPU·h，8独立H20，Q3/G3/M2，BF16/eager/local offline镜像资产；每任务deadline guard，08:55自动TERM/KILL/删除剩余weights，09:00不得再占卡。

CPU三族全部3136条件/族、302源的Source原token IDs与无Q prefix逐条一致，8卡Q3/G3/M2已启动。先八分片小仪器全部通过再开放实际科学输出；不以partial判断。prefix截断按完整tokenization切至最后Source token，包含固定标点/换行不含Task/Q；初版按字符串末尾编码的BPE合并错误在任何GPU之前发现并修正。

## 完整结果与自审

9408实际输出/.701904GPU·h/0API，unknown/cap0，完整4860主/分层面板＋324joint，map SHA2b0252326f1dbbf46f974931f9d2a3c9015615a942053f28dac4b662157e3b5e。[摘要](../results/E90-frame-source-bank-summary.json)。全族/构式GP-cue主图、Goldinitial/final、GP frame与mapping噪声已读；没有逐格手读4860全部组合。

- 基线prefix-bank与原native大多接近；G NPS final−4.3[−11.4,0]、Q MVRR initial+1.9[0,4.9]pp等异质数值差同报。不能称full-prefix hidden逐字相同；主因果差为匹配FRAME_BANK−NATIVE_BANK。
- NPZ GP initial+33.1[24.4,41.9]/+12.6[6.2,19.7]/+5.3[2.5,8.4]pp，final+1.7[−4.2,7.6]/0[−6.5,5.6]/−8.4[−13.5,−3.9]。GP joint+27.5[18.0,37.1]/+5.6[−2.2,13.5]/−7.3[−12.4,−2.8]；不是共同完整重建。
- NPZ正initial17组Q/Min两banks都0，G0→5.9[0,17.6]%，远未传递E89 EARLY100%的正恢复。GoldNo Q41.3→78.1、G75.3→91、Min92.7→99.4；改善大多拒绝旧关系。
- MVRR G initial GoldYes15组10→33.3，差23.3[0,46.7]；final GoldYes24组52.1→81.2，差29.2[12.5,45.9]；GP joint+13[1.9,27.8]。Q/M initial GoldYes无恢复，Q final Yes−12.5[−25,−2.1]，未认证普遍角色规律。
- NPS Q joint+14.3[1.4,27.1]；Min initial+11.4[2.9,21.4]但final−22.9[−41.4,−4.3]，final GoldYes58→10%、GoldNo60→100%。G唯一正initial被损伤，只有1组不泛化。
- mapping不一致完整保留，Min NPS bank4.3%vsnative21.4%、G NPZ bank5.9%vsnative6.8%。低映射噪声不等于能力恢复。

**POST-HOC既有数据对齐（0新生成/0API）：** 回E87完整实际输出按本151发表cohort原Gold拆初始Yes（不改原读数/Gold，不按结果筛），详外置`E87-posthoc-positive-role-task-strata.json`。G普通QA NPZ cue94.1%/GP0%，Q76.5/5.9、M44.1/0；MVRR Q cue100/GP16.7、G100/26.7、M56.7/10。一般指令可以改善cue，不能把GP零分全归于strict明确性，但Min控制仍弱。

**改变假说：** 外给正确frame能强烈改变答题时的正关系，却未普遍形成可携带的源解释；Source只传部分抑制/部分MVRR正角色影响。源bank不覆盖全部KV/recurrent/hint信息，null不能证明没有源状态。退出本frame/source局部块，不追加层位/边/措辞修补；下一由实际遗漏内容与独立知识库对象发问。I06仍探索种子，先寻找有价值预测，不要求成稿；C06–08L0/C09限定L1不变。资源到期仍按08:55早停/删模型、09:00硬停，不以实验结果改人定截止。
