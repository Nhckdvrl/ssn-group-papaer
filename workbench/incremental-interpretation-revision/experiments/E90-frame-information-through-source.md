# E90：正确frame信息能否经源解释迁移，而不是留在答题提示中？（2026-10-08）

- **状态：** RUNNING；生成器E431在任何forward/科学效应前改E90。
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
