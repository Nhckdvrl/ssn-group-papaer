# E15：自然NPC意图—行动差异的采样噪声校准（2026-10-14）

- **状态：** DONE
- **类型：** REPRO（P04 measurement资格；不是新idea/人格缺陷证据）
- **对应：** C01 / E14 / P04。
- **问题（一句话）：** E14独立shadow意图与实际行动不完全一致，是两个随机样本/等价动作的自然噪声，还是意图问法使策略分布改变？
- **设置：** 原E14 seed901前12不同graph，固定step0与step3（若源episode不足4则用最后step，全部保留），共24自然frozen snapshots。每个snapshot保持同persona/作者goals、观察、原legal menu/已执行event状态；意图使用原E14独立hypothetical问法，行动使用原E14执行问法。32独立action draws（A1/A2各16）与16意图draws（I），固定seed150000+snapshot_index*1000+draw_index，128token/.7/nonthinking，原JSON schema。I不写入行为线程。完整prompt/hash/token/raw均缓存，不能按结果挑states。
- **读数：** exact action-template pair agreement仅是粗粒度；离散选择分布JS(I,A1)与JS(A2,A1)配对差、总变差及speech-vs-material action类型；全部JSON失败率。每个actual action draw在CPU原图原命令重放至同snapshot后fork一次原事件，检查合法/native世界Δ及随机失败，不将prompt选择当世界后果。speech payload填入原模板并保留。研究判断以snapshot/graph为单位，不把1152calls当独立scene。
- **阳性对照：** 原真实轨迹逐步CPU重放与material state一致；每个model action经同原parser/execute，不改规则；I/A同合法schema与预算。A1/A2同prompt但独立seed给抽样基线；若32draw皆一动作JS噪声=0，不能用随机猜测mismatch解释。
- **噪声地板 + MIE：** A1/A2 paired floor；graph cluster bootstrap95% CI（预定2000rep/seed151515），仅3seed来源中的1seed discovery快照，绝不升L2。跨24states的I/A差若不超本层A/A，则E14差异归于抽样；若超过，先归意图question/framing，Rethinking已拥有measurement-context解释，需另一问法/模型后才考虑更深现象。
- **混杂审计：** 48draw/snapshot batch使调度与原sequential不同，但两层同batch规则；random seed显式隔离。postgoal event提示是本地task binding中已有字段，不将它冒称作者机制。canonical菜单自身有parse mismatch，native gate失败按原样记录；action class/template相同不保证utterance相同或利益等价。
- **决策表（跑之前写）：** 纯采样差→取消“intent gap”线索，分析真实目标/后果条件；I/A分布差→量化question敏感性，承认近邻解释；nativefork不一致→停止行为分析先修回放，不补造世界；若仅speech差/合法goal行为一致→不发战略utilitygap结论。
- **算力预算：** 24×48=1152本地短call，1GPU≤1小时，CPU fork≤10分钟；先2snapshot成本gate再展开，零API，现有fgvd；07:00起全项目≤8GPU。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
尚未运行。

DONE：24自然snapshots逐步native replay/clone全部匹配，1152个本地独立短call，0JSON失败；768实际action forks753合法。JS(I,A1)−JS(A2,A1)按图均值−0.01125，graph-bootstrap95%[−0.03103,0.01020]，不支持intent/action差超过同层抽样地板。实际loop300.64秒+模型加载。按预先决策表取消本批“intent gap”线索，不用原单draw不一致证明战略脱节；genuine交互影响/utility问题需另找。
