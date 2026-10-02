# E31：原知识条件可识别性在现代强模型上的边界

- **状态：** RUNNING
- **对应：** C02/P02；E29不是scientific finding，知识控制必须先可识别
- **问题（一句话）：** E29的完整知识恢复但部分知识恶化、正负问不一致，在Qwen3更强端点是否消失？
- **设置：** E28已锁定8B/14B两个checkpoint SHA与下载完整marker；原EPITOME40item/360knowledge九条件，完全沿用E29四变体bare/common-chat，FP32/noTF32/thinkingFalse。4B E29为较小端点，原14B Qwen1.5只作不同代anchor。每模型四variant shard分别一GPU，共8独立槽，每shard720reads，无新prompt/换gold/挑item。
- **读数：** 原parent knowledge norm、部分/完整access联合报告；polarity agreement和归一P、support mass、role/access-only paired Δ与item40cluster2000bootstrapseed0；不合并readout、不report SDT/假称latent知识。从强模型没有错误不能反推小模型representational failure。
- **阳性对照：** 全360原题与1440变体CPU预检；所有shard唯一(key,variant,interface)，整合2880；各首末batch1/8 prob/mass<.001门槛；原题源SHA与E29完全一致，Q3词表token IDs应逐项核查。不用不完整checkpoint。
- **噪声地板 + MIE：** deterministic、无训练seed，CI仅item；保持原.001数值门槛。新run与原数字协议一致而无同checkpoint历史不冒称精确复现旧cache。
- **混杂审计：** 规模不是纯因果，training/data可能不同；role澄清改变指令/回答先验；负问有一般否定难度，不能所有归语用。只看full correct会掩盖partial错误；部分知识仍许可对某些候选推断，不把parent knowledge norm当inference许可。两入口不作两个独立模型。
- **决策表（跑之前写）：** A强模型联合正确/极性一致→小模型lead降级，仍需条件证据主问题；B全知识改善而partial/极性持续脆弱→知识测量存在边界，先semantic/control验证，不能讲scale不会pragmatics；C唯prompt/模板变化→留仪器，停止局部救分；D数值/输入失败→隔离。任何结果不自行关线或升claim。
- **算力预算：** 8卡共≤2GPU时，复用E28下载；等待已有GPU锁释放，绝不重复下载/占空卡做伪实验；无training/API/子agent。

## 结果
先卡后run，资产E31-knowledge-Qwen3-{8B,14B}-{variant}，每shard720，不覆盖E29。
