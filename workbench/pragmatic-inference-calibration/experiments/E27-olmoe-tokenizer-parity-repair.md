# E27：OLMoE tokenizer/BOS混杂修复（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / bug audit，不是novel method
- **对应：** C02/P04/P11；E21/E16/E19/E20的聊天stage归因被输入不一致阻断
- **问题（一句话）：** 固定完整tokenizer、逐token一致后，Base/SFT的条件证据读数是否仍改变，是否依赖BOS token？
- **设置：** E26先前两bare结果与E12 bare不变。OLMoE Base9b0c1aa87e34a20052389dce1f0cf01da783f654 / SFT6f7a5b02aa069fdcb8d0cb6b837b9905a3d995d7，完整固定SFT tokenizer（含special map）。原ImplicatureX两stage各运行官方SFT BOS50279与同输入首token替换Base已见IP token0两条件；原EPITOME atomic两个readout、原下注common-chat两个stage，Hu chat两个stage同完整SFT tokenizer。原题/评分/FP32/noTF32不变，首末数值gate<.001。
- **读数：** 沿用E21/E26连续条件效应、原指标、选项support mass、下注无效；paired item bootstrap2000 seed0，BOS交互与裸入口交互分报。固定SFT tokenizer是受控入口，Base不原生，不称pure能力或RLHF因果。DPO资产到齐后同协议补齐，先冻结，无新seed筛选。
- **阳性对照：** 三stage权重manifest；所有刺激按完整SFT tokenizer编码；两个BOS只允许首token差，余token逐项一致；新增token IDs不得超model embedding size。原source prompts SHA不变；bare普通词Base/SFT token-ID parity逐项审。先发现旧Base bos=None产生不同prefix而不是把结果审计错误改掉。
- **噪声地板 + MIE：** deterministic数值gate、item CI非training uncertainty，无paper MIE。tiny cancel符号按原.001边界报告。原不同tokenizer聊天读数只保留描述、不用于paired-stage claim。
- **混杂审计：** SFT更改special-token映射；50279对Base可能未训练，0对SFT语义可能重映射，所以需要两个BOS与bare三入口一致才支持稳定stage解释。统一tokenizer不声称所有训练差可消除。Approx缺human norm；generation invalid不作能力错。
- **决策表（跑之前写）：** A两BOS与bare的连续stage效应一致且候选support充分→继续跨现象证据来源；B只一个BOS/聊天入口成立→token/入口混杂，不升级；C两BOS均无有效候选support→原MCQ不适于Base能力归因，转原completion/行为norm；D原子与下注矛盾→readout边界，不能选择漂亮版本；E数值/token parity失败→隔离。
- **算力预算：** 八卡独立：0/1 Base/SFT ImplicatureX SFT-BOS；2/3 Base/SFT base-BOS；4/5 Base/SFT EPITOME atomic；6/7 Base/SFT下注，后接Hu chat。DPO随后任一空卡顺序执行。≤3GPU时；无训练/子agent/API judge。

## 结果
先卡后运行。历史raw不覆盖；旧Base聊天token差异已单列，不解释为语用能力。

完成：全部队列exit0，三阶段同actual token SHA核对通过。SFT→DPO natural baseline聊天bos50279 Δ−.04625 CI[−.05350,−.03894]、bos0 Δ−.03201[−.03800,−.02631]；裸 Δ+.00641[+.00364,+.00963]但选项support极弱。不要合并成criterion；完整结果results/E27-token-matched-stage-summary.json。下注valid Base0/SFT40/DPO4（各760），不能把invalid当能力。
