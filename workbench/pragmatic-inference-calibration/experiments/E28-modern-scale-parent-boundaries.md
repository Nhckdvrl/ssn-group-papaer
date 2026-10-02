# E28：较强现代同family端点的parent边界（2026-10-03）

- **状态：** RUNNING
- **类型：** REPRO / D1–D4，不是扩benchmark或新方法
- **对应：** C01/C02/P02；小模型结果不足支撑领域判断，原14B Qwen1.5是复现anchor
- **问题（一句话）：** 原自然语用、人类分布与取消更新的不同读数，在较强Qwen3端点是否同时改善，或其条件结构仍不同？
- **设置：** Qwen3-8B @b968826d9c46dd6066d109eabc6255188de91218 / Qwen3-14B @40c069824f4251a91eefaf281ebe4c544efd3e18，官方公开权重非gated；与E21/E16/E03的Qwen3-4B @1cfa9a7208912126459214e8b04321603b3df60c对照。每模型Hu1365 bare/chat各一、ImplicatureX271×6×2order×parent/format、Wave100/50conceptpairs。均FP32/noTF32/explicit thinkingFalse，同各parent协议；Wave完整21个answer completion含EOS，禁止换数字token捷径。
- **读数：** Hu按phenomenon与item cluster原correct/prob；ImplicatureX按四类initial、cancel、joint、continuous cancel-minus-irrelevant/support mass/position boundary；Wave原human均值MAE、Wasserstein、Pearson及pair CI。所有尺度分开，不相加榜单，不造SDT或把Approx当falsealarm。
- **阳性对照：** 下载完整marker与SHA，首末batch1/8数值gate<.001；原source/token/score/EOS完整。不同规模tokenizer实际接口hash核对。Hu raw不用generation penalty，不把未生成reasoning的thinking prefix当CoT；失败隔离。
- **噪声地板 + MIE：** deterministic/每训练checkpoint一个seed，不伪造training独立样本；item cluster2000bootstrap seed0。无预设MIE/结果方向，小delta sign保留原.001界限。FP3214B约60GB单卡可行，OOM则停止并记录，不临时降precision救故事。
- **混杂审计：** size checkpoints不同training可比性有限，不是纯scale因果。parent cache的nativeBF16 rounding风险见E24；新结果不冒称exact cached parity。不同readout与human norm不是同一construct。不能从only4B anomaly说LM一般缺陷；强模型胜出也照报。
- **决策表（跑之前写）：** A三个parent各层指标均明显改善→小模型lead降级，回到条件证据主问题，不用新metric重复大模型更好；B均值改善而证据类型/取消边界持续→明确boundary后跨family验证；C只一任务/一入口有差→记录局部结果，不能缩claim救novelty；D numeric/资产失败→技术不可比，隔离。无论哪种结果都不自行关territory。
- **算力预算：** 8独立GPU槽，两模型各HuBare/HuChat/Impli/Wave。已有8B/14B的权重下载并行，完整后自动锁排程，不抢占E27。预计≤4GPU时，no training/API/子agent。

## 结果
先卡后运行。权重manifest写入外置models/qwen3-scale-manifest.json；结果E28-*不覆盖已有run。

开跑前静态校对发现原脚本numerical-gate只支持Hu。原队列尚无GPU作业，停止等待协调进程，保留两下载子进程及原日志/队列源码；r2队列使用独立run_scale_readout.py，为Wave加入原首末全21completion batch1/8门控，再运行100题。未修改任何已执行脚本或预测。
