# E109：共同输出怎样让外来源信息进入本来源的标签证据？（2026-10-11）

- **状态：** RUNNING-CONFIRMATION
- **类型：** PILOT / 形成机制的竞争反事实
- **对应：** I04、P17、C16/C20。
- **问题（一句话）：** namespace改变本Source标签证据，主要通过过去外Source的答案载体，还是过去外Source的输入/来源编码？答案载体起作用时，是K选择还是V消息？
- **设置：** E91/E106同任务、Qwen3-8B固定revision、FP32/eager，16新contexts seed109001、8query/context。B shared/far × aligned/conflict全部保留；A raw文本、姓名、答案相同。冻结原生far prefix各层B K/V。shared prefill仅在**A label token作为attention query**时，使用far的某一B消息族；其它attention receiver用原生计算，后继状态自然演化。不搜索头、层、强度。最终仅将重算A label KV送给pristine shared cache，全部query位置禁读B。
- **读数：** 各context B-rule有符号差与绝对幅度，10,000 context bootstrap；与直接far-label interface比较绝对减弱、signed差和逐context效果。shared gate、far gate、full-A、far-label、B-answer-KV、B-prelabel-KV、all-B-KV、B-answer-K、B-answer-V、instruction共10条件×2world×8query×16＝2560评分。预先同时保存原生A-label接收B答案的概率、label-match/输入class-match读数，作为辅助观察，不拿attention alone证明机制。
- **阳性对照：** full-A重建far gate；shared B KV在相同edge自交换后全词表margin≤.001、自cache max≤.001；直接far label接口有效。插入far消息的每层/receiver调用计数，未改raw token，源cache fingerprint不变。
- **噪声地板 + MIE：** 全float32；native重建与edge self重建比科学效应小。若消息族恢复与完整label作用方向一致并清楚分叉，同源脚本32新contexts seed109101确认。若完整all-B接口也不恢复，接受该edge解释不足，不为它加更多位置/层。
- **混杂审计：** B答案载体定义为答案word及其尾部换行；B prelabel是其余完整Comment/Annotator/Label冒号区域。两组覆盖全B并不等大，不以效应除token数称特异性。K干预能改变attention分配，V能经后继反馈再改变读取，故不把它们称完全独立语义模块。far B状态已上下文化，不等于静态标签embedding；肯定答案载体作用也不能单凭它证明抽象prototype或纯标签词先验。所有其它receiver未直接交换，允许因果后继变化；输出端只接收A label的改变。
- **决策表（跑之前写）：**

| 结果 | 对主解释的更新 |
|---|---|
| B答案KV恢复，而B prelabel弱 | 过去外Source答案载体→本Source label是具体形成机制；继续检验传递的是学到的输入标签关联还是仅label身份 |
| B prelabel恢复，而答案弱 | 历史输入/来源状态直接参与label形成；不能讲输出label pooling |
| 两者都有、all-B更强 | 支持组合消息路径，不能宣布单一label机制；用新的关系反事实检验功能内容 |
| K单独恢复，V保持shared | 输出身份通过形成时的检索选择起作用，不只是最终query地址；已有QK机制上新增发生阶段和来源依赖 |
| V单独恢复，K保持shared | 固定上游选择也能转移namespace效应，内容改变是功能环节；仍不声称V独立存整条规则 |
| all-B接口仍弱/不一致 | 构造性edge解释不足，不继续扫组件；回到完整形成计算和文献 |

- **算力预算：** discovery＋可能确认≤1 GPU·时；单卡。**实际：** 待记录。

## 与文献的距离

Wang2023已解释label anchors，Cho2025已有forerunner→label合并/denoising，CTA2025已有y_i→y_j contextualization边；How Few-Shot Examples Add Up2026已有QK/V分解。这项不争这些所有权。具体竞争问题是：合法私人规则共用输出词时，先前外Source的哪些关系消息改变A自身标签证据，以至随后Source正确寻址不能恢复信息边界。若能建立功能内容与新的反事实预测，才构成机制增量。E108尚在独立确认，E109仅在其label强/完整prelabel恢复不足的结果保持时运行。

## 结果（运行后追加）

待运行。raw JSONL/context本地；analysis/run/audit/preflight入git。

### 执行校对失败（先于科学结果）

初版 qwen3_discovery 在首context self-cache门槛失败（max .0022783），0科学记录。原因是只重算8个ALabel receiver行改变GEMM形状，累积FP32差；不放宽门槛。改为完整原生矩阵形状重算，只替换目标行。失败目录保留，正式同seed/n重跑 qwen3_discovery_fixed；变量、读数、样本不改。

### 数值修复后的Discovery与独立确认冻结

16全部2560评分：shared gate B-rule幅度.897，far label .245；直接label减少.652[.290,1.050]。B答案KV只在A label形成时替换，减少.631[.315,.979]；B prelabel KV仅.0011[−.0133,.0164]，all-B .630[.314,.981]。答案K单独减少.648[.320,.997]；V单独.193[−.112,.468]。因此是过去答案载体的**形成时检索选择**这一候选，而非当前完整输入编码或只在最终query选择来源。

同配置、同源代码32新context seed109101确认，未扫描receiver/head/layer。消息本身包含far答案身份，尚不能说传递了完整规则；E110固定label stream的关系反事实已写运行前设计，以排除静态答案词解释。

计数偏差：源引擎额外保留shared/far ungated native两条件，所以实际每world12条件、合计3072（非卡写2560）。全部保存，主对比不变；确认固定全部24条件/每context。self edge max0、整段/分段margin差9.54e−6，原cache不变；.0514 GPU·时。冻结源SHA 1ee41052abd31d517a6ac93a5db065db9cf95a9cc004d106ea5e46a5f3ea0d10。

### 探索后、确认结果查看前冻结的辅助预测

不拟合系数。对每个query/world用形成边干预的Δmargin（相对shared gate）以系数1预测完整far-label KV的Δmargin；全部answer K/KV/V、prelabel KV、all-B KV都报RMSE/correlation与零预测基线。此为discovery后新增的辅助分析，确认原始评分虽然正在生成，但尚未查看；protocol文件明确时点。它预测的是已定义干预的功能效果，不是假称无需donor激活的通用行为模型。

同一确认查看前，还冻结rule double-contrast预测：[(mode aligned−conflict)−(shared aligned−conflict)]，target为far-label。这样消掉与B私人规则无关的共同alias输出偏移；必须与单world namespace差同时报，避免raw correlation只反映标签先验。仍全部5预测器、系数1、无拟合。
