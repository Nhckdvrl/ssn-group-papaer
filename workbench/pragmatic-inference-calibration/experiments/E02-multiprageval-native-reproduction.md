# E02：MultiPragEval 原生任务复现与本地运行（2026-10-02）

- **状态：** DONE
- **类型：** REPRO
- **对应：** C01、P01；P02 待 E01 确认
- **问题（一句话）：** 保持原始数据、prompt 和 accuracy scoring，公开强基线能否复现，现代 open weights 能否稳定跑通？
- **设置：** E01 后开跑前冻结完整数据、prompt、模型/revision、解码配置、seed。优先官方 Qwen1.5-14B-Chat；受阻写失败；现代模型只算 contemporary reproduction。最多 GPU 0–7，各独立单卡。
- **读数：** 语言/类别 exact-choice accuracy、无效答案率、原始输出、时长、显存、data/prompt hash，95% Wilson CI。保留所有 seed 与失败。option logprob 是额外读数，不替代 generation；不从正确率自动造 FPR/d′。
- **阳性对照：** E01 oracle parser；同模型/同配置才与官方数字对照。上下文/options 不变，字母解析歧义拒绝。
- **噪声地板 + MIE：** 论文 greedy 协议时 seed 0/1/2 重跑，确定性相同不冒充独立样本重复；抽样 CI 与计算重复分开。官方偏差超出原论文/本地 CI 或无效率 >1% → 先查 protocol/implementation，非 finding 阈值。
- **混杂审计：** 固定数据/问法、不开 CoT、记录 chat template/prompt 字节、审计 imbalance/parse/truncation；训练污染未知；缺 inference 脚本/温度时标不完整复现；base/instruct 不足以归因 RLHF。
- **决策表（跑之前写）：** A 同模型接近官方且 scorer 通过 → D1 anchor；B 巨大偏差 → parsing/prompt/config 排查后有界复测；C 只有现代模型跑通 → D2/smoke 完成，D1 官方数字待办；不确定 → 一次原配置重跑，不为故事改读数。
- **算力预算：** 第一轮上限 4 GPU·时，先测一个模型再铺其余卡。**实际：** 待记录。

## 运行前冻结配置
2026-10-02 开跑前核对 §3.3 与附录 B：论文 temperature=0.5，三次 sampled trial，原始 CSV prompt；本卡上文提及 greedy 只是审计前的条件分支，不适用于该 parent。官方表 5 是每语言 240 个 maxim items（不含 literal），另报 literal/None 分数，不能用 300 项整体分数对表 5。

- 原始强 baseline：Qwen/Qwen1.5-14B-Chat @9492b22871f43e975435455f5c616c77fe7a50ec；权重下载中。
- 现代技术 baseline：Qwen/Qwen2.5-3B-Instruct @aa8e72537993ba99e69dfaafa59ed015b17504d1。
- T=0.5、top_p=1、top_k=0、max_new_tokens=256、BF16/SDPA、单条 user 消息使用原始 tokenizer chat template。未加“只答字母”或任何 literal 引导。
- seed=0/1/2；每语言 300 项，所有项保留；按语言拆成独立单卡任务，8 卡授权已覆盖。现代模型 batch=32，原始 14B batch=16。
- 首先现代模型英语原始首 12 项/seed0 做吞吐与 parser smoke（只算技术验证，不进入科学比较）；通过后跑全量。
- 论文未公开 generation 代码/system message/top_p/top_k/max_tokens/seed；上述明确写作本地 protocol reconstruction，不能声称 bitwise reproduction。
- 若 parse 无效率或 truncation >1%，按原始原输出审计后注册有界修复，不偷偷改题或删项。

## 结果
待运行。

### 2026-10-02 技术修复，第二轮开跑前
原生 smoke 首12项：12/12 parser invalid、10/12 达 max256（输出完成标记），8.72 秒。不能作为行为证据；保留原始输出与旧 scorer hash。按预先决策 B 修复显式最终选择解析（不使用 gold），max_new_tokens 增至1024。问法、temperature、原数据保持不变。先原12项/seed0复测，通过后启动全量现代模型四语言×三seed；每语言独立一张卡。后续未提前预见的读数均标 POST-HOC。

2026-10-02 全量开跑前：第二轮 smoke 无截断，3 条 invalid 来自末尾 LaTeX boxed 字母；追加 boxed 解析 fixture 后12/12 可解析。此重算为技术 POST-HOC，旧输出不覆盖。冻结全量 max1024、batch32、原始4语言、seed0/1/2；GPU0–3各一语言，未添加指令。

### 原14B anchor执行配置（下载完成前冻结）
Qwen/Qwen1.5-14B-Chat revision9492b22871f43e975435455f5c616c77fe7a50ec；全部8 shard与DOWNLOAD_COMPLETE存在后运行。四语言各300题×seeds0/1/2，独立GPU0/1/2/4，BF16、batch16、max1024、T=.5/top_p1/top_k0、原user prompt。继承的generation_defaults完整保存，不把未公开参数冒充论文原配置；客观解析/invalid上下界/item-cluster CI，分别240maxim与60literal。与Table5/Figure1仅比走势；若不一致先核对协议与解析，不能宣称parent错。单GPU峰值预算≤90GB、总≤2GPU·时；每语言单卡，不使用张量并行。
