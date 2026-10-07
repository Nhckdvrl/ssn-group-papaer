# E66：提前目标经源编码还是直接参与作答？（2026-10-07）

- **状态：** DONE；先卡后代码/科学运行。
- **对应：** I03/I04、C06/C09；E65完整矩阵产生的POST-HOC选题，E66效应尚未产生。与先前解释修订关系：提前关注初始误读的真假能否改变可供其他关系复用的源信息。
- **核心区分：** E65原生提前Q可能通过S编码，也可能被后续Task/answer直接读到。E66在全部decoder层切断提前目标区间→全部source结束后token的注意力边，保留提前目标→S及S→后续消费者，因果上提前Q的内容只能经S传递。原生源逐层hidden必须与未切版本一致。
- **条件：** 原NONE/INITIAL/FINAL原prompt不改；每个只运行SOURCE_ONLY新路由，原native科学分数复用完整E65。切断区间自Reading goal标记起到S首token之前的全部token，包括可能传播goal的Sentence标记；NONE对应Sentence标记前缀区间。区间前token未见目标，不能传播其内容。源token不改任何入边/hidden，postsource保留源的全部入边，Task与answer保留原生自回归入边。不删source、不开未来边、不扫层窗口、不做bank跨位置移植。
- **数据/规模：** 完整E65 892QA/356源/178clusters，SHA45137a88328224095c3d8bf1dc969f63eed7822a4f1ef4412949528c935b406b；四构式GP/cue全部保留，3预定族各10704评分，总32112新评分。原S/Q/gold/目标/两option mapping、words/letters不改。无新构造文本，可信数据不重审；Step角色纠错独立继续。
- **读数：** 完整goal×eval-target×GP/cue×构式×三族正确率/p_correct；source-only INITIAL−NONE/FINAL−NONE与native同差的对比，源内全Q共同正确率，两mapping平均前求joint，exact同题与other分别输出。与E65相同unit→S→lexical cluster加权/bootstrap10k、seed66，原gold相同层与全量层均保留。后续初始错误修复/正确最终关系损伤同时看，不把联合收益等同独一parse。
- **阳性对照：** NONE匹配路由测量切前缀自身损伤，完整cue判断任务是否仍可答；
- **噪声地板：** 只做输入排序首四source小仪器：4D原native与独立E65单token分数差<.001，所有层source hidden绝对<.001或相对L2<1e−5，只移除预定边、不加未来边，原科学分数配置SHA核验。不能把路由消融的null自动说成无源表征，因为分布变化仍可能存在；NONE/cue地板严重受损则不可作机制证据。
- **决策表（跑之前写）：** INITIAL NPZ/NPS跨关系收益在source-only仍在且cue保持→源介导目标入口，下一步用自然用途修订/角色而非仅QA；只同题收益保留→特定问题信息经源携带，非完整解析；native收益消失但NONE/cue尚好→直接目标消费主贡献，回作答组装/检索问题；地板崩溃→该路由不够辨别，不以null否定源编码，改别的核心问题。各族方向不一致就保留机制地图，不挑Llama独立推进。
- **算力：** FP32/eager/pinned local模型，seed66，3独立单卡，预算≤2GPU·h/族；GPU4/5服务不动。无HF直连，无现金API。
- **定位/尺度：** Ask Twice已区分Q-first编码与echo读取；BindingIDs以冻结源控制功能路径。这里追“撤销旧关系”目标与“确认最终关系”目标对同句其他事实的迁移及因果路径；仅证明一般目标经源影响回答仍不是合格idea，不靠别人的空白做自动novelty判断。E65→E66为这个目标异常的第1次局部追问。

## 结果
完整32112新评分及原生对比已完成；三族0.22951/0.36250/0.27098 GPU·h，总0.86299。C06–C09 L0，注册状态不变。

- 三族小仪器全部通过；原E65 prompt/token/任务数/模型manifest逐项相同，后续目标边按全层屏蔽，源hidden不变。仪器摘要：{"Meta-Llama-3.1-8B-Instruct": {"max_LP": 0.00011682510375976562, "max_source_abs": 0, "max_source_relative": 0}, "Qwen3-8B": {"max_LP": 0.00041747093200683594, "max_source_abs": 0, "max_source_relative": 0}, "gemma-3-12b-it": {"max_LP": 0.0002275705337524414, "max_source_abs": 0, "max_source_relative": 0}}。完整32112新评分开跑，尚未读取路由科学效应。

### POST-HOC目标语义命名校对（P16）

原question_target≠预期更新操作：NPZ有17初始目标源支持Yes，MVRR有19最终目标源支持No；完整原条件/数据/读数保留，不将其整体命名撤销/建立。另以input-only initialNo_finalYes、initialYes、finalNo全部层及evalGold拆分已有输出，先保留全图再限定解释。拆分晚于E65全效应、早于E66全效应与E67角色效应，非事前主分析；没有补跑提示/重新逐条审原数据。

### 完整自审：修订假说发生变化

- 外置完整地图goal SHAa83857a10b83e054f7f40531929a4a9c92baabbc948c18e82d4b92317801e5e3，route SHA32a5405eb4c4339780416d662753f3b32d4b78130454fc7e7a2ab20ba4471791；小摘要results/E66-goal-path-summary.json。三族四构式/GP与cue/两目标/words与letters/p_correct全部看，不按正效应筛。
- NPZ INITIAL联合收益原生Q/G/L+15.17/+11.24/+28.09pp，source-only−10.67 [−17.42,−5.06]/−11.24 [−19.66,−3.37]/−17.42 [−26.40,−8.99]；source-only减native目标效应−25.84 [−34.27,−17.42]/−22.47 [−32.02,−13.48]/−45.51 [−55.06,−36.52]pp，89clusters。
- NPZ初始问题source-only INITIAL−NONE−8.43/−10.67/−18.54pp，words三族CI负；letters Q−5.34 CI到0/G−13.76 CI负/L−3.37 CI含0，不能说所有读数都负；native对比的损失方向一致。
- NPS INITIAL source-only联合+4.17/−2.78/0，与native相比−27.78 [−41.67,−15.28]/−9.72 [−19.44,−2.78]/−45.83 [−58.33,−33.33]pp；初始letters仍有局部小收益，绝不说源路径完全无信息。
- 无提前Q基线Q/G基本保持；Llama NPZ INITIAL目标基线初始−7.87 [−12.92,−3.37]、final+7.10 [3.69,10.80]，因此不能称三族baseline全不变。cue初始损伤/收益、低能力NPS面板全部保留。
- FINAL目标source-only Llama NPZ联合+12.36 [5.06,20.22]、与native目标效应差+30.90 [21.91,40.45]；NPS final+42.31 [21.15,63.46]但initial−32.86 [−48.57,−18.57]，联合未恢复。不是选择FINAL就共同修好。
- 当前三句故事：提前问题的答题收益大量需要后续消费者直接访问该问题；保留原生目标条件源表征并不足保留收益。NPZ甚至出现源路径受限读数劣于无目标，而原生更好；这提示路径可能相互抵消，也可能源信息需直接目标才能正确读取。此时不能把它认证成已修好的可复用源解释。
- 什么会推翻：E68若仅允许目标直达作答、禁止目标进入S编码后收益消失，说明joint编码依然必要，而非目标只作后续补偿；若更好，则更支持两路径有相反功能效应。E67检验原生正确答案是否同时转成正确自由角色。
- 自审与研究价值：E65→E66假说已从“源介导关系修订”转向“编码/作答用途相反或依赖”，有具体可分辨预期，不需要再扫prompt。成功回答可能掩盖更难复用的源状态，比一般Q-first涨分更值得解释；Ask Twice/Lens已拥有普通编码/读取改善，增量尚需自然关系的功能性结果。E67是原目标的第2次追问，仍在跑；这里先更新表后只做一个对称路径E68，检验新的相反路径机制，不无限绕原收益。
