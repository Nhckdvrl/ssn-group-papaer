# E69进度报告：同图任务、人设效应与完成后的继续行动

2026-10-15；接续[E67/E68完整报告](PROGRESS_REPORT_2026-10-15_RULE_EXECUTION.md)。主配对2760条＋适应性控制144条全部完成，27519次新增本地调用、2.828GPUh（含启动/最后关闭日志），0API，GPU已释放。论文正文继续暂缓。

## 1. 先看研究判断

**同一NPC、物品、请求者和原世界下，当前指定任务确实调节人物效应；但审计期待的“Equip负、Duty-Give正”的完整反转没有跨模型成立，也不能由此确定特质—动词神经启动。** Gemma的8步任务人物交互为+4.17pp [0.00,8.33]，32B为+6.25pp [2.08,10.71]。32B在Equip下Agreeable任务完成更低、请求交付更多；Duty-Give下两人设却都近99%完成，并且物品几乎全部交给职责对象A而非索要者B。**本轮的职责Give与接收者选择得到保留，不能由goal交互直接推出无差别Give动词启动；任务用途、接收者与行动时间要分别测。**

三个原审计引用案例补齐共同8步后仍没有任何双事件完成，排除了仅由旧提前终止造成缺失这一解释。单句机制事实使32B的5/36条分支恢复了先装备再交付，完成说明没有恢复任何分支；Gemma则有17/36条真实卸下目标物、仍未新增交付。这提供了普通环境知识可部分解释的正向证据与明确的模型差异，不能统一判成深层人格失效。详见第4节。

C04/C05继续限定范围L2、I04保持PROMISING、全局PROPOSED不变。新同图干预发生在已知源世界，不冒称新的独立holdout。没有启动训练、patch网格或新语义标注项目。

## 2. 怎样读、怎样入手

先看本报告第3节的配对主表和[效果图](results/E69_figures/E69_matched_task_effects.png)，再看第4节的三个源案例。要逐项复核时，使用[实验卡](experiments/E69-matched-task-and-motivation-window.md)、[审计回应](knowledge/persona-behavior/TASK_MOTIVATION_AUDIT_2026-10-15.md)、[Gemma完整结果](results/E69_gemma_matched.json)与[32B完整结果](results/E69_32b_matched.json)。原始完整输入/输出/状态在`/home/xiang/.cache/game-npc-research/runs/e69_*`，不把大型rollout放Git。

采用新审计的同图任务对照；同时纠正四个跳跃：原计划未完成goal不代表每步非法；执行器原本直接看得到goal，恢复不是从无信息中创造目标；block的物理作用不能单独证明词汇启动；动机与timeline步骤不同不自动等于脏标注。LIGHT的wield是装备、并不自动攻击，remove是卸下、并不移出库存。

重读Dragon的动机/时间线采集协议，以及ACL2025 PANDA的任务—人物兼容性分析后，已有ownership与本轮增量更新在[定位表](knowledge/persona-behavior/TASK_COOPERATION_POSITIONING_2026-10-15.md)。没有把“性格与任务相容”或“动作不等于动机”重新命名成首次发现。

## 3. Panel B：112个同世界任务配对，2688条主分支

[CPU资格](results/E69_native_task_qualification.json)覆盖全部309源图。112图在同一初态允许同一物品Equip、Give给第三角色A、Give给索要者B，A≠B；其余197图不补人/物品。源give85、原equip27；confirm69、旧reserve43。原世界/人物背景/动机固定，当前任务指定为Equip或Duty-Give，全模块任务与人设一致；两模型×两traits×三固定seed6901–6903。每条均观察8步，不因任务成功提前终止，死亡/协议失败仍保留。

任务明确称研究者指定，不能称两支都是作者原任务。两支统一追加game-master当前任务说明，因此也不是旧E68措辞/种子的严格复现。主读数在首调用前登记；源任务层和confirm/reserve层完整公开，按图平均三seed，再做4000次配对图簇bootstrap，以下为点态95%区间。

| 模型 / 指定任务 | Firm任务事件 | Agreeable任务事件 | A−F，pp及95%区间 | 首步A−F，pp及区间 |
|---|---:|---:|---:|---:|
| Gemma Equip | 88.39% | 85.42% | −2.98 [−7.14,0.89] | −5.95 [−11.01,−1.19] |
| Gemma Duty-Give给A | 97.92% | 99.11% | +1.19 [0.30,2.38] | +2.38 [−2.08,6.85] |
| 32B Equip | 91.67% | 84.82% | −6.85 [−11.31,−2.68] | −2.38 [−7.44,2.68] |
| 32B Duty-Give给A | 99.40% | 98.81% | −0.60 [−2.08,0.89] | +2.38 [−1.49,6.25] |

最终对全部2904条分支做[独立物理状态读回](results/E69_native_state_readback.json)：5条命令级goal成功使用了同名替代物（Gemma4、32B1，3源图），最初绑定物品已给别的角色。原主指标与这些合法轨迹保持；POST-HOC严格固定初始item_id时，Equip人物差为Gemma−3.57pp [−7.74,0.30]、32B−6.55 [−11.01,−2.38]，goal交互为+4.76 [0.60,8.93] / +5.95 [1.79,10.42]。任务调节的判断保持，但固定物品主张须使用该敏感性，不能把命令级成功冒充原物品保有。图展示原登记口径。

人物×任务交互定义为`(A−F)Duty-Give − (A−F)Equip`。8步为Gemma +4.17pp [0.00,8.33]、32B +6.25pp [2.08,10.71]；首步为+8.33 [1.19,15.77] / +4.76 [−1.49,10.71]。Gemma首步差较突出，但32B仍有八步完成损失，不能统一解释成仅启动延迟。Duty-Give接近天花板也限制了可见人物差的幅度。

| 模型 / 任务 | 交给请求者B：F/A | 目标物品任何Give：F/A | 首个Give给职责A：F/A |
|---|---:|---:|---:|
| Gemma Equip | 0.00 / 1.49% | 6.25 / 8.63% | 6.25 / 7.14% |
| Gemma Duty-Give | 0.00 / 0.00% | 97.92 / 99.11% | 97.92 / 99.11% |
| 32B Equip | 2.38 / 9.52% | 6.85 / 14.88% | 4.46 / 5.65% |
| 32B Duty-Give | 0.30 / 0.60% | 99.70 / 99.40% | 99.40 / 98.81% |

32B在Equip下的人物请求转移效应+7.14pp [3.57,11.01]，Duty-Give下+0.30 [−0.60,1.49]。任何目标物Give的人物交互Gemma −1.19pp [−4.46,1.79]、32B −8.33 [−13.10,−4.17]；故不能把goal交互直接解释成Give动词族被一致启动。

原Give85图下，两模型改派Equip后（下述任务事件沿用预注册的原命令当前解析口径），任务与原作者Give事件均完成仅约0.4%–0.8%；原Give事件Gemma F/A 8.24/9.41%、32B 5.88/7.45%。保持Duty-Give则原Give事件约98%–100%。[POST-HOC物理见证](results/E69_sequential_native_witness_POST_HOC.json)确认112/112图均可合法完成Equip→remove→给A的三步路径，缺少双事件不是引擎强制互斥。它仍不是角色完整效用的金标，事件完成与最终状态分别记录。

[旧同子集核对，POST-HOC](results/E69_prior_subset_POST_HOC.json)：相同43个旧reserve图中，31原Give图的旧Gemma人物goal差仍为+7.53pp，12装备图−2.78pp。因而新旧差缩小不能全部归于换了世界；任务框架和seed也变了，旧新差不用于各自因果归因。

## 4. Panel A及适应性控制：完成后到底发生了什么

109源reserve图中，严格来源支持当前请求Give、原子goal为装备的全部3图为：女子（woman）wield food后给狗、顾客wear bag of herbs后给骑士、侍僧（acolyte）wield bible后给园丁。CPU均找到原goal→remove→Give的三步路径；未来timeline支持一种作者写过的可能路径，不表示角色必须在当前8步立刻照做。

两人设×G/B两规则×原seed6801–6803×两模型，共72条。精确复用E68原对话/更新/执行前缀，并逐字段校验；原子goal后继续至共同8步。每格9轨迹，来自3世界，不能当9独立世界。

| 模型 / 人设 / 规则 | 原子goal旧→新 | 请求Give旧→新 | 新窗口两事件均完成 |
|---|---:|---:|---:|
| Gemma Firm G | 3→3 | 4→4 | 0/9 |
| Gemma Firm B | 7→7 | 0→0 | 0/9 |
| Gemma Agreeable G | 2→2 | 7→7 | 0/9 |
| Gemma Agreeable B | 6→6 | 3→3 | 0/9 |
| 32B Firm G | 4→4 | 5→5 | 0/9 |
| 32B Firm B | 4→4 | 5→5 | 0/9 |
| 32B Agreeable G | 6→6 | 3→3 | 0/9 |
| 32B Agreeable B | 3→3 | 6→6 | 0/9 |

在看到该结果后登记两个适应性控制，只在同一个原生goal已执行后出现：(a)任务已完成，请依据原动机与请求决定下一步；(b)装备物须先remove才能Give的真实机制。每模型72条，合计144；goal之前的历史与基线必须完全一致。不称初始预注册或独立验证，也不追加组合网格。

**控制全部完成。** 共同8步基线和“任务已完成”说明下，两模型的双事件完成均为0；机制事实后的计数如下，每格9轨迹/3世界：

| 模型 / 机制事实 | Firm G | Firm B | Agreeable G | Agreeable B | 总新增双事件 |
|---|---:|---:|---:|---:|---:|
| Gemma | 0/9 | 0/9 | 0/9 | 0/9 | 0/36 |
| 32B | 1/9 | 1/9 | 3/9 | 0/9 | 5/36 |

32B恢复涉及女子4条、侍僧1条，原goal前历史逐字段不变；如同一条旧轨迹`wield food → 给篮子 → reward/表情`，加入真实机制后变为`wield food → remove food → give food to dogs`。这证明普通环境知识能恢复部分真实顺序行为，不能把此前全部缺失归成人设/动机压制。它是2个源世界中的5条分支，不是5个独立成功场景。

机制事实下Gemma 17/36条真实remove目标物、6/36条drop，32B 9/36条remove、0条drop；完成说明两模型均0条remove。动作前提变化与最终交付不同，Gemma不是完全忽视提示。原规则允许不交付，因此不把剩余不交付直接判成能力缺陷；三个世界不用于总体频率推断。[Gemma完整控制](results/E69_gemma_completion_controls.json)、[32B完整控制及全部恢复轨迹](results/E69_32b_completion_controls.json)。

## 5. 对话、计划、动作怎样一起读

这部分是看到Gemma主结果后新增的只读POST-HOC分析，不改主读数、无新模型调用。直接使用结构化stance和原生菜单的精确计划命令，不做语义打标。[Gemma](results/E69_gemma_structured_stages_POST_HOC.json)、[32B](results/E69_32b_structured_stages_POST_HOC.json)。

Agreeable相对Firm的对话`accept`字段在Equip/Duty-Give下：Gemma +24.11pp [17.26,30.96] / +23.81 [17.56,30.36]；32B +11.31 [6.85,16.37] / +3.57 [1.19,6.25]。Duty-Give下实体请求转移却仍约0%。accept不是无条件承诺：部分回复是先履责、稍后帮助；这可以是合理角色表达，不能拿字段差直接证明言行失信。

计划包含当前任务与实际任务执行也不相同。Gemma Equip下有11.61%/13.39%分支在计划未列当前任务时仍执行它，32B为1.49%/1.79%。这是行为层描述；执行器一直可见直接goal，不能据此声称从无信息找回目标或识别了充分中介。与E67/E68的阶段交叉结果共同看，合理问题是各阶段怎样使用可见信息与目标，而不是把几条接口路径当新机制。

## 6. 数据覆盖、成本和复算

全部309图保留源记录。严格短期自由文本命令解析只有1/309可作直接原生见证，不把其余硬贴动机一致/不一致金标。未来timeline在152图提供某个当前合法事件，其中9图匹配请求Give，reserve为上述3图。[覆盖表](results/E69_source_coverage.json)。E61旧support_claim标的是请求文字是否声称支持动机，不是客观步骤—动机一致性。

1344项全链输入检查、336项动作对象/接收者检查通过。两模型主队列各1380条，全部keyset齐全、0解析失败。主队列原生拒绝Gemma709/32B121，其中重复block460/80；随机动作失败217/135，全部保留。没有把零解析错误等同于零原生失败。

主分支2760＋适应性144；Gemma成本profile另执行12条，其输出精确复用于主队列，不增加独立样本。[完整成本账本](results/E69_resource_account.json)：27519次新增调用，prompt 34533858 tokens、completion 1864468 tokens，解析失败0。记录的模型载入＋推理为2.66807GPUh；从每个单卡job启动到最后关闭日志的完整观察占用为2.82804GPUh，含Python/依赖启动。profile120调用只计一次，旧E68缓存不计新推理。全程本地单卡，峰值4卡，0云API/训练/activation干预。七个job和队列/分析watcher均已退出，fvcrc21四卡均15MiB/0%。

原始资产为`~/.cache/game-npc-research/runs/e69_native_task_qualification/`、`e69_{gemma,32b}_matched_s{0,1}`、`e69_{gemma,32b}_completion_controls`及profile。配对数据SHA `53bcf71bde517cf12a2626a894fb0aeffd20a2088d73eea2022a127db39b453a`，窗口数据SHA `6c75bf573fe2969ffa8019453088d79ad73167a78dabb50c65d5aac60c5b8c1b`。原始输入、模型版本、脚本hash与每次实际调用均保存在各manifest/log。

复算主结果使用`scripts/native_matched_task_report.py --runs <同模型两分片> --data <资格目录> --out <JSON>`；案例控制使用`native_task_completion_report.py`，阶段只读使用`native_matched_stage_readout.py`，成本使用`native_matched_resource_report.py`。科学图保留PNG/PDF/SVG，已视觉核对。

## 7. 当前研究推进到哪里

E69把审计中的强故事拆成了可实测关系：同图指定任务调节人物效应，接收者并未被Give词语无差别替代；表达、计划、首步推进和八步实际后果不具有统一的角色效应。旧提前终止确实不能拿来判后续行为，但补窗后案例没有自行完成两事件；单句机制知识在32B恢复了部分真实后续交付，在Gemma只改变中间物理动作；这是目前比“统一动机压制”更具体、可复核的解释边界。

中心问题仍是NPC怎样把自身任务、角色动机与社会请求落实到真实后果。本轮提供了更明确的可操纵边界和后续问题，没有自动锁定词汇神经机制或论文四幕剧，也没有因为某个预期反转不完整就丢掉整条研究。下一判断应从任务框架、背景动机与后续行动之间的具体矛盾出发，优先能预测新实际后果的研究动作；不继续盲目扫措辞/层/seed。论文正文保持暂缓。
