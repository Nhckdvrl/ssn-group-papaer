# E89：正确动词框架要在读句前知道，还是读完也能重建？（2026-10-07）

- **状态：** DONE；生成器E431科学效果前改E89。
- **对应：** I06 / P19 / C06–C09。E88名词可见性帮助解除旧附着，但反身/互指正关系未共同补出；动词可见性null不能证明不存在frame瓶颈。本块唯一第二追问，不扫更多mask。
- **问题：** 提供同一正确谓词语法框架，放在Source前（改变形成）或Source后（只允许后续重建），是否不同？Hint不含实体名、Q、答案或答案倾向，只含原句目标词及intransitive/passive-relative/clausal-complement类信息。
- **数据：** E88全部151发表GP组/784QA，两种Source均保留；回原E82相同item/S/Q/Gold/analysis字段，原语法parse类别按发表构式与对照形式生成：NPZ早期V不带直接宾语，MVRR早期V为passive relative participle，NPS早期V带finite clause complement。原word位置机械复用E88，不新增S/Q/语义金标、不重审，0API。是有语法信息的oracle，不假装普通无辅输入任务。
- **条件：** EARLY_FRAME和LATE_FRAME相同Hint文字，只变S前/后；原native零shotG2任务/word答案/two mappings。3当下族Qwen3.8/Gemma4/Ministral3，784×2timing×2mapping×3=9408真实greedy输出。原native actual QA_STRICT/QA_RECOVER来自E87完整缓存，作为无hint与一句恢复对照（R8），不再跑。
- **生成与解析：** 复用E87已验证actual32tokens/greedy/nonthinking/native入口；Yes/No、A/B、A/B. Yes/No按冻结显式语义解析，冲突/含混仍UNKNOWN；cap独立、上下界保留。E87最初literal格式读数另存，不借格式错误造新能力结论。
- **主读数：** actual正确率下/上界，EARLY−LATE、各自相对无hint和一句恢复；初始/最终/原完整Q joint。三族/三构式/GP-cue/原GoldYes-No及input源frame分别完整报告，冻结Source→lexical cluster bootstrap10000/seed89，不筛baseline正确条目。
- **阳性对照：** 原cue/原Recovery actual完整复用；Hint机械不含Q/Gold/entity；全prompt同task/Gold，LATE原Source及可见之前prefix与E82逐字相同；只有新增Hint信息，不能把有无Hint差等同同信息计算变化。两timing token总量记录，不冒称BPE边界/hidden数值全相同。
- **噪声地板：** 两mapping实际语义差与cluster CI；无温度、格式、词首空格校准网格。原Min cue初始反身关系弱，不用弱控制推一般能力。
- **混杂审计：** Hint是语法oracle而非全义项/全事件role答案；仍可能触发一般显式语法推理。EARLY改变编码prefix，LATE加入Task附近信息，时机差不能独自认证特定神经变量。非因果mask null与自然Hint正不冲突；不把已存在的人类partial-reanalysis重新命名独占novelty。
- **决策表（跑之前写）：** EARLY明显强于LATE且真正正关系与其它角色保持→源形成/论元框架重算值得探索，下一最直接源中介；两者相当且均恢复→后续frame检索可修，旧token不改不是必要瓶颈；只No变化/GoldYes不恢复→未重建论元，改解释对象；两者均不帮→本框架oracle未定位痛点，更新假说表与意义判断，不继续提示/时机网格。当前目标是选出值得追的idea，不要求当夜完成成稿证据。
- **算力预算：** ≤3GPU·h，8独立H20 Q3/G3/M2，现有国内下载/离线资产，0新API；每任务检查人定deadline，08:55提前释放、09:00绝不占卡。

CPU三族3136条件/族，完整晚Hint原Source-prefix/原Task字节预检通过，784原S/Q/Gold全相同。data SHAb33d4a494833c310cfade0beff3a233616c0210233c9813c61dbb74926cdb422，8卡PID以外置runner-pids-v1.json记录为准，9408生成0API；完成全图前不读partial。

## 完整结果与自审

9408真实输出全部闭合，.626489GPU·h，0API，unknown/cap全0。完整4860主/分层面板、324joint、72mapping noise见外置`E89/predicate-frame-timing-map-v1.json`，SHA76ac3f99f5f1ca71bc0fe5923ebbef0a403d306f07b29765fa5ccab93d0bf8f4；[小摘要](../results/E89-predicate-frame-timing-summary.json)。已读全部族/构式GP-cue主图、initial/final Gold与frame层及joint/noise，未逐格手读4860全部组合，不把正cell冒充全图。

- NPZ GP joint（native→EARLY/LATE）Q32.0→65.7/51.7%，G53.9→91.0/77.5%，M13.5→12.4/14.6%；EARLY−LATE Q+14.0[8.4,20.2]、G+13.5[5.6,21.9]pp，M−2.2[−6.2,1.7]。三个族的总体上涨不能概括为共同重建。
- 真正正initial关系NPZ17组：Q/M native、EARLY、LATE均0；G0→100/73.5%，EARLY−LATE+26.5[5.9,47.1]。MVRR15组：G10→80/70%，EARLY−native+70[46.7,90]，timing差CI含0；Q0→0/1.7、M6.7→0/0。NPS正initial只有1组，不作跨材料结论。
- Q/Min很多initial收益来自GoldNo；例如NPZ GoldNo Q41.9→100/98.3%，M91.6→98.3/98.9%，而上述正角色不恢复。Min NPS final GoldYes58→16/24%，不能藏在平均数里。
- G NPZ正initial cue70.6→29.4/47.1%，EARLY−native−41.2[−76.5,−2.9]pp；提示会改变任务解释或信息使用，不能把提示当普遍无损解析器。G NPZ final GoldNo native100/EARLY100/LATE45.8%；Q NPZ final GoldYes72.7→75.6/56.8%，部分joint timing差来自保持损伤。
- 两mapping不一致：G NPZ gp EARLY2.7/LATE.9%、M NPS native21.4/EARLY8.6/LATE20%；全部效果按原mapping平均，非挑映射。Hint是外给语法信息；没有认证native神经valence变量或框架时机的单一原因。

**探索结论：** I06已有值得追的现象：拒绝旧关系与建立替代关系有区别，Gemma的框架信息能改变后者。停止本块时机/mask/措辞扩展。下一应问这份正确frame信息能否被编译成不依赖答题时显式hint的源解释，并作用于未指定问题；不是为了候选门槛补一堆控制。人最新要求先找探索idea，§0成稿标准仅用于未来候选，不能变成今晚行动门槛。C06–08L0/C09限定L1不变。
