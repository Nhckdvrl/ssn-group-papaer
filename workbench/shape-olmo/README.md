# ShapeLab — Workbench

**状态：PAUSED WORKBENCH / KNOWLEDGE ASSET。没有当前 paper candidate；今天测试的几条线均按当时规则排除，结论与经验保留在下方和 `docs/RESEARCH_LOG.md`。**
详细记录：`docs/RESEARCH_LOG.md`（按时间顺序，含每次预注册的 kill 规则）· `docs/P0_RESULTS.md`（OLMo 7B 对比）· `docs/READING_NOTES.md`（blog 与文献精读）

## 历史探索目标（2026-09-28）
结合 Alex Zhang 的 *Shape* blog（模型的计算 contract 应适配 harness；hybrid 各组件性质不同、组合方式重要）与本项目已有实验（CT05–CT09、ShapeLab），找到一个**有深度、新颖、有前景**的研究问题。门槛（全部满足才注册）：①建立在我们自己验证过的现象上；②关于组件如何**组合**，不是调 recipe；③最近邻 prior 已查、未被占；④我们的规模有因果操纵手段；⑤能通过事前写好的 kill 规则。

## 目前结论（按可信度）
| # | 结论 | 状态 |
|---|---|---|
| 1 | 论文里的 token 级 "hybrid 签名"（内容词 > 功能词、首次出现 token 优势大、重复 token 优势→0）在**只差架构**的 Pile 三联体上，和"模型变大 / 训练更久"产生的轮廓**形状完全一样**（novel ≈ 2×、rep≥4 ≈ 0.13×）→ 不能作为"递归层做状态追踪"的证据 | 已确认 |
| 2 | 唯一穿过所有对照的架构特异现象：Pile 三联体上，在**首次出现的 token** 上，hybrid 比两个父架构都好约 0.05 nats，而 Transformer ≈ Mamba-2。实验 A 显示：这个优势**不来自远处历史**（只保留最近 32 token 时优势依旧），是局部的 → "长程 discourse state" 解释被否定；按事前规则此线 kill | 现象确认；远程解释已 kill |
| 3 | OLMo-Hybrid 最终版在重复/闭括号/代码上变差，**是 DroPE 长上下文阶段中逐步产生的**，不是预训练架构性质；损失在"选哪个前文候选"（within-class），且随候选数增加而变大 | 已确认 |
| 4 | "无位置编码的 hybrid 会读旧值（primacy）"：DroPE 后的 OLMo-Hybrid 很明显（注意力直接从偏向最新 → 偏向最早）；但**从头就不用位置编码训练的 Granite-4.0-H / Nemotron-H 追踪最新值和 RoPE hybrid 一样好** → 按事前规则，**宽泛版本已死**；只剩窄版本"DroPE 事后改造的问题" | 宽泛版已 kill；窄版放弃（Llama 对照无效，且不满足"组件组合"门槛） |

## 已完成 / 正在跑
- **实验 A（已完成，已 kill）：各架构到底用远处历史的什么？**（Khandelwal 2018 *Sharp Nearby, Fuzzy Far Away* 的现代复刻；与 blog "近处精细看、远处粗略即可" 直接对应；loss 级别的 SSM/hybrid 版本未查到先例）。对远于 d 的上下文做 删除 / 32-token 块打乱 / 逐 token 打乱，比较 Transformer++ / Mamba-2-Attn / Mamba-2（只差架构）与 Pythia、Mamba-2 放大对照。**Kill 规则**：若 hybrid 多用的远程上下文相对其总差距，落在"放大模型"的范围内 → 只是"更好的模型"，此线死。结果：`results/ctx/`，分析 `src/analyze_ctx.py`。
- **实验 B（已完成，无效）：Llama-2-7B 原版 vs Sakana DroPE 版**。DroPE 版在内容对照题上就是随机水平，普通文本 NLL 也比原版差 0.58 → 该 checkpoint 在我们环境里没复现方法，结果不可用。窄线放弃。

## 已排除 / 已纠正（诚实记录）
- CT05 lineage 误读 blog：blog 说"粗略历史够用，因为 agent 可以再去取"，从没说递归能替代精确 KV。
- 7B 对（Olmo-3 vs Olmo-Hybrid）不是"只差架构"：数据配比、LR、头数、长上下文 recipe 都不同。
- 我事前以为 reuse 缺陷在 stage-1 就存在 → **错**（stage-1 时论文签名完全复现）。
- 我以为"递归通道存了变量的当前值（binding）" → **错**（只存无绑定的"最近"信号）。
- 工具陷阱：transformers 5.x 对 Olmo-3 的 YaRN 实现错误；Pythia 某些 step 分支的 safetensors 是 main 的。

## 1B 三联体 / Hybrid-YaRN checkpoint
论文说已发布但查不到公开地址。作者请求草稿：`docs/AUTHOR_REQUEST_DRAFT.md`（未发送，由用户决定）。

## 若重启：未决探索方向（不是候选论文；2026-09-28 13:55）
今天用事前规则 kill 了三条线（reuse gate、无位置编码 hybrid 读旧值（宽泛版）、hybrid 远程上下文优势）。"hybrid 在首次出现 token 上胜过双亲" 被定位为**局部**建模优势，且轮廓与"更大的模型"同形，因此我不再把它当作机制线索。剩下的思路：

1. **DroPE × hybrid 的 primacy（窄线，等 Llama 对照）**：若 Llama-2 DroPE 也出现 primacy → 是 DroPE 自身的性质（干净、有实际意义，但不满足"组件组合"这条门槛）；若 Llama 不出现 → 是"事后改造的 hybrid"特有，属于组合问题，但很窄。
2. **blog 的核心前提本身："粗略历史 + 再去取"**：递归/压缩通道能否保留"去哪里取"（地址 / 存在性），即使无法复现内容？可以用已有的通道分离工具在公开 hybrid 上测。风险：可能只是复现 2609.04434（特征保留、绑定丢失）。
3. **blog 的另一条轴："并行流 vs 纵向 hybrid"、"历史与当前观测分开处理"**：没有公开的匹配模型，需要小规模训练。**但 blog 提的这种架构（注意力管近期窗口 + 记忆模块管长历史）已经有人做了：Titans（Google，NeurIPS 2025）、Infini-attention、RMT 等**，所以这条的新颖性很低。
4. 如果 1–3 都不成立：建议暂停用"公开预训练 hybrid"做 Shape 这条路，转向需要训练的 shape 设计问题，或者换母问题。
