# E66：提前目标经源编码还是直接参与作答？（2026-10-07）

- **状态：** RUNNING；先卡后代码/科学运行。
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
尚未运行。C06–C09 L0，注册状态不变。

- 三族小仪器全部通过；原E65 prompt/token/任务数/模型manifest逐项相同，后续目标边按全层屏蔽，源hidden不变。仪器摘要：{"Meta-Llama-3.1-8B-Instruct": {"max_LP": 0.00011682510375976562, "max_source_abs": 0, "max_source_relative": 0}, "Qwen3-8B": {"max_LP": 0.00041747093200683594, "max_source_abs": 0, "max_source_relative": 0}, "gemma-3-12b-it": {"max_LP": 0.0002275705337524414, "max_source_abs": 0, "max_source_relative": 0}}。完整32112新评分开跑，尚未读取路由科学效应。
