# E67：证据分开取决于最终标签身份，还是答案前缀的检索线索？（2026-10-10）

- **状态：** DONE
- **类型：** PILOT
- **对应：** C09/C15，P12，I04；E31/E46换词、E60词表差异、E65读出混杂。
- **问题：** 不改变最终标签、答案候选、信息量或token频率，只把source code从独立字段移到答案前缀，会不会改变来源条件化；若改变，是否经label-anchor K选择而非V读出？
- **为什么现在：** 独立label vocabulary同时改变输出身份、格式、任务标识和读出几何；旧现象不能唯一定位output indexing。E66未提供source-specific可复用程序。现在直接竞争label identity/readout与prefix-address retrieval，两者对本设计给出不同预测。
- **近邻与compression risk：** Cho2410.04468§3–5已有forerunner merge/induction/shortcut，Olsson prefix matching、Wang label anchors、Bai PCT已有模板汇聚；成功不代表新head/新induction原理。潜在增量仅为在**同信息、同最终输出**下，来源条件化的编码边界及K/V causal transfer；需独立预测，不把任意格式差叫普遍定律。
- **设置：** Qwen3-8B冻结bf16/eager，同E65 revision/conda，无训练。先32-context发现seed67001，animals/fruits yes/no；16demo，source×label严格4/cell，query两个类别词均未见且分别给两个source。code assignment每context随机Alex/Sam置换、独立于规则orientation，避免代码词直接等于来源身份。
  - **D0/Q0（code在字段）：** `Item: x\nSource: Alex\nTag: <code>\nLabel: Mark yes`。
  - **D1/Q1（code在答案prefix）：** `Item: x\nSource: Alex\nTag: Mark\nLabel: <code> yes`。
  - 标签yes/no与其频率完全不变；两layout每demo/query token多重集、长度、source/code/marker位置及label anchor位置逐位assert。字段名与标点完全相同，唯一移动是Tag值与Label前缀值互换。Tag不是删除信息，而是另一来源编码位置。
  - code words与marker均一个leading token，跨source的code频率平衡；query prefix teacher-forced不含gold label，只含已知source code。结果是归一化后的同一source-conditioned二元判断。
  - **D×Q完整2×2：** prefix编码需同时demo/query匹配的假说预测交互；query-only收益更支持额外cue/读出/计算位置；D-only收益更支持representation改变。四项均跑，不只看一致格式。
  - **native输出前缀对照：** query算至`Label:`，报告所需prefix在Mark/Alex/Sam三选一中的准确率及概率，不以teacher forcing成功声称原生端到端能力；不放宽最终答案空间。
  - **因果cache：** 两D缓存长度/RoPE完全匹配。以D0为recipient、D1为donor，分别移植label-anchor K、V、KV和整个cache；对Q0与Q1均做。再反向D1←D0的label K/V。全层全head、无头选择；recipient最终标签words/candidates/所有其它cache值不变。加入完整交换=no-donor、self-copy=no-op。
  - native attention按全部query位置记录label-anchor读取分布对requested-source demos的比率；只作key操作后的路由读数，不能单独用attention宣布能力。全层平均＋逐层完整保存，不事后挑峰。
  - 一句指令对D0Q0和D1Q1；single-source同编码与同候选参照，防止任务不可识别/通用变差。
- **读数：** source-correct margin、准确率、同input的来源排序正确率、D×Q accuracy/margin交互、native prefix三选一；key/value transfer相对native格式差（gap≤0.2nats不报告比例）、requested-source label读取的变化。按context bootstrap4000。
- **阳性对照：** 两layout多重集/offset/token数相同；完整KV donor输出=no-donor，self-copy=no-op≤0.10nats（预期0）；donor规则labels频率平衡；query source信息不含gold；prefix候选概率＋single＋一句指令。score batch左padding与显式position_ids。
- **噪声地板 + MIE：** 既有同scope no-op=0；D1Q1−D0Q0≥0.10accuracy或≥0.3nats且CI不跨0，且source排序不恶化，才继续确认编码效应。K-only迁移≥格式margin gap的50%且CI不跨0、同时source读取改变，才支持routing线索；V-only迁移/偏置变化更强→读出解释。若仅平均margin增加、accuracy/排序不增，则拒绝来源选择改善的当前版本。
- **混杂审计：** 同triples、词频、token数、label space、示例位置、输出label anchor、code assignment、seed配对；未控制：code从输入字段变成输出prefix会改变语法/前训练关系，正是研究操纵，不可偷换为一般能力；teacher forcing不等于model自己生成正确prefix，单独测；hybrid K/V非自然组合，不把比例当可加份额；单来源非上界。
- **决策表（跑之前写）：**
  - D1Q1明显改善、D×Q交互、K-transfer路由与行为都成立 → 相同最终标签不是充分失效条件，进一步独立编码验证prefix-address参与。
  - V-transfer占主导，attention未有选择性改善 → 沿E48 readout separation/校准解释，不称修路由。
  - query-only普遍改善，D变化作用小 → 更多cue/位置计算，不能用demo indexing作解释。
  - 只有mismatch差、两个matched差不大 → 常规模板一致性，不支持新中心问题。
  - 无改善/仅margin↑/single失败/数值失败 → 分别保留negative、收窄判断/修harness，不继续盲铺。
  - 若超过MIE且对照有效：64-context seed167001 occupations/vehicles toxic/safe独立确认；有界Mistral同发现材料复现用于模型边界。未达到阈值则不自动追加。
- **算力预算：** pilot≤0.3GPU·时；确认/复现≤0.6；实际待填。独立单卡，本地/fvcrc20可用，conda优先。

## 结果
待运行。

### 结果（2026-10-10）
- 预定发现32/独立确认64 Qwen、同发现32 Mistral完成；token多重集/位置/长度相等，self/full donor误差0。最终label vocabulary一致，**完整输出语法仍不同**（source code是前缀的一部分），不能说全输出身份完全相同或已消除所有任务分离解释。
- Qwen发现matched D1Q1−D0Q0 accuracy+0.141[0.070,0.211]，确认+0.074[0.047,0.105]（0.508→0.582）；确认source排序+0.109[0.055,0.172]（0.805→0.914），margin+0.645[0.552,0.741]。满足margin-MIE，但准确率未达到完全恢复。D×Q确认interaction margin1.119[0.965,1.270]，两mismatch不构成公平独立编码任务，只限定互操作/模板匹配。
- Qwen确认D0Q1←D1 label K fraction−0.003[-0.063,0.055]，V0.015[-0.021,0.049]，KV0.083[0.026,0.141]；ratio分母是固定Q的D差，不是matched总体gap。K改变Source attention约+0.015但没有行为恢复，拒绝仅凭attention判修路由。原生prefix三候选准确率matched0.996/1.000，仅三选一，不是全词表greedy端到端准确率。
- Mistralmatched accuracy+0.031[-0.039,0.102]、margin+0.178[0.133,0.223]，未达到预定MIE；有编码交互，但强matched收益非普遍。按原规则不追加更多Mistral确认。
- 单来源/一句指令：Qwen确认single D0/D1 accuracy0.633/0.648；指令0.520/0.566。代码位置收益不是一般single-source性能上涨或指令完全修复。
- **判断更新：** 相同最终label word不是失效的充分条件，但source-code prefix收益未由label-anchor K/V充分定位。C17新增L1、原C09有界结果保留；E68检验其它carrier与history，不称新induction原理。
- 资产`results/e67/*/{run,analysis}.json`，raw contexts/scores/attention/layout本地；实际273.10秒=0.076单GPU进程墙时折算小时（非积分利用率）。
