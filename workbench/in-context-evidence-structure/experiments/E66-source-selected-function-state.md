# E66：在看到新输入前，来源字段是否选出了可复用的规则？（2026-10-10）

- **状态：** DONE
- **类型：** PILOT
- **对应：** C16 / P13 / I04；不是另开workbench。
- **问题：** E65的query接力传的是这个输入的答案，还是能在输入出现前按来源选出一个任务状态、供新输入使用？
- **为什么现在：** E65确认Label标记→末位承担大量source效应；但标记已看到输入，可能只是已知shortcut/answer induction。FV和task-vector文献也已有跨输入迁移。本卡把输入的可见性与原始demo访问切开，不以“某位置有信息”命名新机制。
- **近邻：** Hendel/Todd（可迁移任务状态）、Xiong2410.05603§6/附录C（混合任务向量、但未做显式来源选择）、Cho2509.21012§3（干预后切断追加context信息），Bai2401.11323v3（模板token汇聚）、Wang标签锚点压缩。成功仅为此source-first缓存接口的充分性；失败不是没有任务向量。
- **设置：** frozen Qwen3-8B，同revision/conda，bf16/eager。沿用E58平衡16demo，每来源每类4条、相反规则，随机orientation/order；demos仍Item→Source→Label，query改Source→Item→Label（一句指令与single-source参照）。24发现contexts seed66001 animals/fruits yes/no；条件有效后才按下述预定确认。所有query词都未出现在demo；不给gold或排除错误答复。
  - 先仅处理query的`Source: Alex\n`或Sam，**此时尚无query input**，收集全层KV。随后处理`Item: x\nLabel:`，全层屏蔽所有demo，只允许读取这个source clause和suffix自身。保留原position_ids/RoPE与cache长度，不压缩重定位。
  - capsule接口：保留source clause全部token vs仅来源name token；同source clause在生成时就屏蔽demo的null capsule，比较context带来的信息而非raw名字。每个source clause缓存被重复用于两个类别的新输入，严禁每个input生成不同capsule。
  - **rule donor：** demo标签全翻转，source clause文本/位置不变；只将clause KV替成rule-flip donor。未来输入仍完全相同。若有可部署规则，输出应按同一函数的翻转变化，不只是名字偏置。全prefix rule-flip作阳性。
  - **单来源接口对照：** 只保留对应来源8demo，source clause的full/null、rule-flip同操作；若连单来源均失败，不能把混合失败归因source选择。
  - **答案接力阳性：** 原始Input→Source→Label完整query先算到末位冒号前，再仅允许该query KV供冒号读取（全部demo屏蔽）。这时状态看过输入；用于判断cache接口能否部署已经形成的判断，不能混作可复用task state。
  - native source-first、original-order、instruction、single-source均报告；source-first/no-op整段与分段推理的最大差≤0.10nats，所有屏蔽条件demo attention质量精确0，无padding误入capsule；prefix/source-clause token布局写JSON。
- **读数：** source-correct margin和二元候选accuracy；full−null capsule的paired rule部署收益；rule donor翻转效应（base−flip的gold方向margin）；分别按source与input类别聚合并保留all contexts。ratio仅native rule效应>0.2nats时使用。context bootstrap4000，accuracy/margin必须同时看。
- **阳性对照：** native分段=no-op；native翻转确有作用；已看到input的query relay capsule；single-source capsule。缓存容量全层多token，不称“一个task vector”或小模块。
- **噪声地板 + MIE：** 控制≤0.10nats；full clause−null部署≥0.20nats、accuracy≥0.05且CI不跨0；rule donor效应≥0.20nats且CI不跨0；两类输入方向一致，才作为可复用来源规则线索。未达阈值/阳性失败→有限negative或接口失败，不包装成新瓶颈。
- **混杂：** 所有triples、频率、orientation平衡；native改query字段顺序，不能与E65直接解释为同程序；屏蔽重归一化与接口分布移位未消除，null与single/answer对照约束；原始prefix绝不能经未来token再读入；tokenizer/name长度assert。全层KV可能含高容量示例压缩，不能证明抽象规则唯一解释。
- **决策表（跑之前写）：**
  - 混合capsule在输入前成功、rule翻转且跨新input → 下一步用真正独立的新规则/因果交换区分可复用程序与记忆压缩。
  - single成功而mixed失败、answer relay成功 → 来源选择与输入相关检索可能有接口差异；需恢复原始demo路径/匹配模板，尚不证明本质composition failure。
  - single与mixed均失败、answer relay成功 → 当前interface主要支持input-dependent判断传递，撤回“source clause已选出function”；考虑先解读native时序，不再盲扫capsule位置。
  - 所有capsule均失败或no-op不精确 → harness/接口没有判别力，停止科学归因。
  - 若发现主要对照有效且有≥MIE线索：预定64独立contexts seed166001 occupations/vehicles toxic/safe确认；真实评论不自动追加。
- **算力：** pilot≤0.3单GPU·时；确认≤0.5；实际待填。独立材料不和发现复用。先发现，再确认，不盲铺后续分支。

## 结果
待运行。

### 数值校对后的协议修正（2026-10-10，重跑前）
首轮24contexts完成，但native整段vs分段推理max差1.625nats（source-first max0.25，original拆至末位max1.625），超过0.10；mask attention质量0不挽救此对照。该运行VOID，保留`qwen3_discovery_invalid_chunking_bf16`，未读取其它条件作为科学结果。先改全模型float32重跑同seed/n，仍执行原0.10阈值，不用放宽阈值绕过控制。float32的正负结果均不能直接等同原bf16程序；后续需匹配原生精度边界。

### float32有效运行与独立确认（2026-10-10）
- 有效发现24 contexts、独立确认64 contexts（新词库与标签词）；所有query均未出现在demo，capsule严格在input出现前形成并复用于两类别。max分段no-op差发现4.01e-5、确认3.62e-5nats；所有被屏蔽demo attention质量0。
- **确认来源字段缓存：** native source-first accuracy0.523[0.508,0.543]；full-source-clause缓存0.484[0.441,0.523]，null0.500；deployment margin差-0.109[-0.202,-0.010]，accuracy差-0.016[-0.059,0.023]。rule-flip donor影响-0.026[-0.089,0.033]nats，没有部署证据。一句指令capsule0.508，无明确恢复；name-only0.500。
- **单来源接口同样失败：** accuracy0.500，full−null margin-0.035[-0.128,0.057]，rule donor效应-0.034[-0.127,0.053]；native单来源rule-flip阳性2.360[2.181,2.544]nats。不能把mixed failure归因特有source-composition缺陷。
- **看过input的query缓存：** 确认base−null margin+1.109[0.861,1.369]、rule-flip效应1.919[1.521,2.287]，说明input-dependent规则相关logit可经query缓存保留；accuracy仅0.543 vs0.504，gain0.039[0.008,0.078]，**低于预定0.05 MIE**。发现accuracy gain0.188不在独立材料中同幅复现；不称稳定高能力/完整答案状态。
- **决策执行：** 按single/mixed同时失败分支，撤回source clause已选出可部署function的候选解释；该接口对input-dependent logit有判别力，但没证明模型没有可复用function。拒绝从失败包装出新的组合瓶颈，不盲扫全部token/layer。
- **范围：** 全层KV、多token、高容量；有效推断为float32而非原bf16程序。native改query字段顺序、有mask重归一化和接口移位，结果只限定本缓存接口。未提升C16等级，不新增强机制主张。
- **资产：** `results/e66/qwen3_{discovery,confirmation}/{run,analysis}.json`；VOID的`control_failure.json`，原始JSONL本地。有效进程墙时406.18秒=0.113GPU·时；bf16 VOID运行未写完成计时，日志末次20/24 context66.2秒，不冒充精确总算力。conda优先、无训练。
