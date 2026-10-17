# E21：原生对话与行动机会的协议控制（2026-10-14）

- **状态：** DONE
- **类型：** REPRO / 强基线协议校准；非新方法。
- **对应：** C01 / P07 / E20。
- **问题（一句话）：** E20几乎没有对话，是NPC没有交涉倾向，还是一次say占用一个物理行动机会的当前task binding抑制了交涉？
- **设置：** LIGHT pin71a06ca…、E20原6图/12人物/独立原goals、Qwen3.5-27B不变。原Dragon base/environments/envs.py step先处理initiator utterance、partner utterance，再partner physical act；此分解已属Dragon贡献。我们的双自治角色任务只借其speech/action分离，不冒称原RL/partner复现。每物理round先首动角色原生say，再对手原生say，随后按同一首动顺序各选择一次原物理动作（全部原speech事件不再作为该阶段候选）；资源进VOID终止，最多6round/12物理动作，seed2001/2002/2003与2种首动顺序。非model脚本fallback，私有目标不共享，NPC可在公开speech选择透露。首个gate只跑固定6图×2顺序×seed2001，不筛角色；若真实交涉改变研究判断再另外2seed，若基本全是机械消费则停止扩矩阵。
- **读数：** 每阶段公开speech/合法事件/实际行动、物品归属、双方goal事件执行、消费者。speech只作合法观测交流，原graph/parser/probability/收益不改。E20结果完整保留，因interaction scheduler有差异不能把差异直接解释为persona效应。自己说过的话进入后续行动历史，存在已知同会话priming；必要时后续独立实验分解self vs partner，不偷当独立意图预测。表达与意图探针仍为影子；实际言语是行为，不当抽象trait分数。
- **阳性对照：** CPU原生say正确带payload、所有视角收到对应原生text且material state完全不变；随后原get/eat仍能改变同一物品，不造新分割、交易或消耗规则；非法动作state不变。两角色仍保有source goals/可见native observation。
- **噪声地板 + MIE：** E20原概率失败/全部三seed保留，本gate为一world seed不算总体CI。出现真实转让或协商改变物理路线才扩其他固定seed；说话措辞变化但动作仍相同→承认旧factorization/priors解释，不称增量。不会因出现共享建议就预设NPC必须自私，也不会假定食物可分。
- **混杂审计：** 强制speech阶段本身改变表达机会/LLM预算/自我历史，明确协议控制而非公平性能优化；不重写E20读数。native world物理、目标及角色规范固定，source canonical speech模板由E14payload修复。其他角色仍无Soul自动动作、6图便利样本、人类demo0，限制继承E20。Persona具体utility无唯一gold。
- **决策表（跑之前写）：** gate有交涉及物理路线变化→检查竞争解释并完成预定另2seed；对话无实质变化→停止扩矩阵记负结果；差异只是own-speech priming/普通强提示→承认已有解释；adapter/source事件问题→报失败修复，不作为新idea。
- **算力预算：** 单卡gate≤1小时，只有改变判断才其余seed≤2小时；现有fgvd+deps，0云API，07:00后项目≤8卡。raw在cache。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
尚未运行。

首gate完成：CPU12episodes，28/28 speech合法且无material变化，21/21物理动作合法，全部共享资源消费；0.363秒/0model。Qwen首seed12episodes均完成，loop197.78秒/0API。出现角色物理路线变化：p14908鸟put worm on nests并称safe，fox之后直接get并eat；原作者source短目标worm自用/中目标nut给幼鸟，两个独立目标不应混成唯一trait gold。按预定分支扩另外seed2002/2003全部原6图/2顺序，保留所有结果；P08/I01/E22先做最小竞争解释，不宣称新的gap。

三seed全36episodes完成：78/78物理动作、102/102speech合法，36个消费事件/72角色机会，310本地calls、609.99秒。放worm不跨seed稳定：seed2002鸟有put后steal回收/eat，seed2003主要直接eat。原生成功、失败、取舍均保留，[结果](../results/E21_native_dialogue_summary.json)；无总体CI/新机制主张。
