# E22：第二条真实Base/Instruct谱系的matched原任务（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D2–D4 stage boundary，非新method
- **对应：** C02/P02；ALTPRAG×PaCE压力，需要同题同模板、不预设criterion
- **问题（一句话）：** 同Qwen2.5-3B Base→Instruct在Hu与ImplicatureX原任务中，变化属于初始候选endorsement还是对后续证据的条件更新；这种差别是否依赖bare/common-chat入口？
- **设置：** Base Qwen/Qwen2.5-3B SHA3aab1f1954e9cc14eb9509a215f9e5ca08227a9b；Instruct SHAaa8e72537993ba99e69dfaafa59ed015b17504d1。原Hu1365、E21 canonical271×6states×2orders。Hu bare与chat各一（raw-no-special；共用Instruct官方template），ImplicatureX bare与common chat入口各parent/一句format。统一FP32/TF32关闭、batch8；Base无chat原生入口，common template是控制，不称native接口。无thinking/training/API。E21已有Instruct common-chat parent/format分片可复用，须逐item prompt/token parity；不把不同card命名当不同协议。
- **读数：** Hu gold/human endorsement与order，ImplicatureX原recognition/cancel/joint及连续cancel-minus-irrelevant delta，按4类分报paired item-cluster2000 bootstrap seed0。两种入口比较stage差的交互；无SDT gold/FPR/d′，不把Base/Instruct变化归因单独RLHF。
- **阳性对照：** 模型manifest、完整shard后才加载；Base与Instruct vocab/tokenizer对原同prompt所有token-ID一致；common template源固定Instruct。各run首末batch1/8阈值.001，不通过隔离。Hu旧Instruct bare generate包含repetition processor，不能直接复用，需raw matched重跑；chat可与E16对照。E21 canonical旧双否定剔除记录一致。
- **噪声地板 + MIE：** deterministic读数、没有independent training seed，CI只含item不含training变异。微小cancel sign并列.001数值边界；不设方向或paper MIE。
- **混杂审计：** Base/Instruct同时改变数据/目标，不是干净SFT→DPO；后者看OLMoE E12/E16。prior问题字串不同、Approx控制无human norm，遵循E21限制。不把same input IDs等同相同模型表征。
- **决策表（跑之前写）：** A两入口stage条件更新差一致→跨谱系边界可追，仍需OLMoE；B仅common chat或bare有差→入口交互，先审elicitation；C只initial endorsement变/continuous条件差不变→待测policy解释、不自动叫criterion；D方向随phenomenon相反→保留条件结构，不能维持统一推断倾向；E数值/tokenizer失败→技术失败，隔离。
- **算力预算：** Base约6GB下载；GPU0 Base独立队列、GPU1 Instruct待E21释放；各Hu两读数、ImplicatureX入口两×format两，≤2GPU·时，no multiGPU。OLMoE仍GPU5/6/7；无抢占无杀他人进程。

## 结果
跑前冻结。当前准备完整Base资产；不称stage实验已完成。

### 2026-10-03结果更新
已完成本卡原运行；后续stage输入差异见E27，旧raw保留。派生数字见results/E21-E23-implicaturex-stage-summary.json与results/E22-E26-stage-controls.json。未升级C01/C02；技术/任务描述不当能力finding。
