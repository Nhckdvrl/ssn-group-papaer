# N4（路由器先定型、携带来源记忆）与 E190（推理时查表 / 同 id 替换）的 claim ownership 核查（2026-11-11）

**只写定位，不写判决（R6）；不判死（R1）；不改叙事 / DIRECTION / CLAIMS（主会话改）。** 对象：`workbench/mechanism-population-dynamics/division/MAINLINE_NARRATIVE_2026-11-11.md` §4 N4 行、§5 "相关工作为什么没有"一段、§6 E190。
**不重做：** FIELD_MAP（代号 FM）、HIST、SURV、BR、CL、NA 已覆盖的条目只引用。2609.32821 只用已有卡（未抓原文）。
**证据标签**（同 FM）：`[HTML]` 本次读了 arXiv HTML（经抓取工具转述）/ `[PDF]` 本次 pdftotext 读了正文 / `[页]` 会议页或 GitHub/HF 页 / `[摘要]` arXiv API 摘要 / `[检索]` 只来自检索摘录 / `[旧]` 旧笔记 / `[记忆]` 执行者已知文献、本次未取原文 / "未核对"。
**检索：** venue corpus `nearest` 6 句（路由器先于表示收敛；路由波动与冻结路由器；路由变化拆成参数 vs 输入；推理时 token-id 查表的困惑度代价；按 token id 预测专家做预取；早期训练哪些结构先形成）+ 8 条 `show`；Web 检索 15 组；arXiv API 7 篇摘要；WebFetch 读 FLAME-MoE / OLMoE §5.1 / OpenMoE §4 / StableMoE / Grouter / Mixtral §5 / Hash Layers / Thérien CPT / Semantic Parallelism 的 HTML；HF API 列了 FLAME-MoE 仓库文件；pdftotext 读 Router Prior Bias 正文。**未覆盖：** OpenReview 未挂 arXiv 的 2026 投稿正文、引用链、中文社区。

---

## Part A — 四个问题的定位表

### A1. 路由器先于表示定型

| 项 | 内容 |
|---|---|
| 最近邻与 ownership | **(i) 只看分配的"早饱和"**：OLMoE 2409.02060 §5.1 `[HTML]`——饱和 = 中间 ckpt 与终点逐 token top-k 交集 / k，0.5% C4 验证集，1/10/20/40% 四个 ckpt，1% 处"up to ∼60%"、40% 处 ∼80%，深层先饱和、L0 最慢；基线只有解析随机 12.5%；**不比路由器权重与隐状态，无固定路由器**；原因未解释（只引"prior work"）。**FLAME-MoE 2505.20225 §6.3** `[HTML]`：同一公式（k=1,2,4,8），7 个尺度，"rises sharply within the first few thousand steps"、中点多数层 >70%、深层先饱和、大模型浅层更慢；**无随机路由器、无隐状态稳定性**。OpenMoE 2402.01739 §4.2 `[HTML]`：只画 "ed"/"an" 两个 token 的专家比例，"almost totally overlapped"，解释为"learned at the warmup stage or so"——**它给了机制猜测**：把 token 送去不熟的专家会升损失、把它推回原专家（即路由由专家侧的适应锁住）。Thérien 等 TMLR'25 2503.05029 §5.3 `[HTML]`：持续预训练中的饱和与词表专精，不拆参数 / 输入。Output Dilution 2608.25231 `[摘要]`：11 个 OLMoE ckpt，探针精度几千步饱和、路由对噪声稳定。**(ii) 路由波动**：StableMoE ACL'22 2204.08396 `[HTML]`——BASE Layer 上 20% 训练时 40.9% token 的"最后一次换专家"仍在后面（50% 处 29.1%，80% 处 15.4%）→ 蒸馏 + 冻结路由器；这是"路由器**不**早定"的反向证据（BASE 分配、6 万步小模型）。**(iii) 理论 / 工程说法**：Why Routers Freeze（Dhir、Cevher、Vankadara；NeurIPS'26 poster OpenReview TccaEvFVmc，另有 ICML'26 *High Dimensional Learning Dynamics* workshop 版 OpenReview AhwB471ARJ；**无 arXiv**，OpenReview 正文被验证页挡住）`[页]`——Tensor Programs、固定专家数、宽度 → ∞、SGD 与 Adam：**标准参数化（SP）下路由器 logits 在一步特征学习后发散，softmax / sigmoid 门饱和、路由器梯度消失**（NeurIPS 版措辞 "router updates freeze after one step"，soft 与 top-k 都如此；作为辅助损失 / z-loss 必要性的部分解释）；µP-MoE 恢复稳定但 soft 路由对称、专家同分布不专精；top-k 下即使 logits 收敛到对称极限，**选哪个专家由有限宽涨落决定**（隐式对称破缺）；实验只说"验证了标度律与 µP-MoE 超参迁移"，模型 / 数据未核对。**它说的是路由器 logits / 梯度的冻结，不涉及隐状态几何，也不预测"路由器相对几何先定"**；top-k 分配由有限宽涨落决定这一点反而预测分配对初始化敏感；Motif 3 技术报告 2608.09119 `[检索]`："early router lock-in"，用衰减路由噪声对抗；Grouter ICML'26 2603.06626 `[HTML]`——称路由"remains highly unstable even after extensive training"（§1）而附录 B 又说趋于稳态（自相矛盾），用从 Qwen3-30B-A3B 蒸馏的固定路由器加速训练；Routers Learn Geometry 2605.12476 `[旧]`：路由器与专家输入权重耦合、"路由器塑造几何"。Three Phases 2604.04230 `[摘要/旧]`：只看负载 γ_eff |
| 我们的增量 | 第一次在公开训练轨迹上把"饱和"拆成**路由器分量**（训练路由器 t 对终点）与**几何分量**（同一固定随机路由器在 h_t 与 h_T 上），给出 20B token 时 .42 vs .17；并在第 0 层前一 token 方向上给出"路由器先于几何约 5000 亿 token"的时间点 |
| 压缩风险 | **中**。一句"OLMoE 早就说路由早饱和、Why Routers Freeze 证明路由器会冻结"可把 N4 压成已知；能抵抗的是：(a) 已有文献没有一篇把分配稳定拆成路由器 vs 几何；(b) "路由器先于被它读的几何定型"是相对次序，现有论断都只是绝对"早" |
| 最强先验预测什么 | **不是单向的**（与叙事 §4 "Myth 与 Routing Drift 都预测反面"不同）：Myth / Ye 的几何说 ⇒ 路由稳定 = 几何稳定（同步）；Why Routers Freeze（SP 无限宽：logits 一步后发散、梯度消失）+ OpenMoE 的"warmup 定"+ Motif 3 lock-in ⇒ 路由器权重先停（**部分预测 N4 方向**：只预测路由器停，不预测相对几何的次序；OLMoE 是有限宽、带 z-loss 的配方，SP 极限结论能否迁移未知）；StableMoE ⇒ 学习型路由长期波动（反向）；Grouter §1 ⇒ 路由长期不稳（反向） |
| 谁依赖答案 | 冻结 / 蒸馏路由器的方法（StableMoE、Grouter）、post-training 不训路由器的工程默认（Unsloth 冻结路由层，见 RPB 引言）、Why Routers Freeze 的有限宽验证、OLMoE / FLAME 饱和曲线的读法（BR B3） |
| 诚实分级 | 子社区关心（MoE 训练动力学 + 分析方法学）；若与 Why Routers Freeze 的预测对接，可变成"理论预测在 7B 公开模型上的检验"，读者面扩到理论组 |

**相邻领域（一两句，`[记忆]`，页码未核对）：** 稠密网络"谁先定型"有成熟文献：Raghu 等 SVCCA（NeurIPS'17）显示表示自底向上收敛并据此提出 freeze training；Chen 等 ICLR'23 *Which Layer is Learning Faster?* 浅层收敛更快；Frankle 等 *Linear Mode Connectivity and the LTH*（ICML'20）与 *The Early Phase of NN Training*（ICLR'20）显示对 SGD 噪声的稳定性在训练很早出现（可 rewinding 到早期点）；Achille 等 *Critical Learning Periods*（ICLR'19）与 Jastrzebski 等 *Break-Even Point*（ICLR'20）把早期阶段定为决定性窗口；Hoffer 等 *Fix your classifier*（ICLR'18）显示**固定随机读出头**几乎不损失精度——**稠密侧其实有"可替换读出器"这一把手**（固定随机头），只是读出器在网络末端、不是逐层门控。神经科学：表征漂移（Driscoll 2017 Cell；Rule 等 2019 *Causes and consequences of representational drift*）讨论"表征在漂、读出 / 行为稳定"——方向与 N4 相反（它是表征先动、读出补偿），可借作对比概念"稳定读出 × 漂移表征"。

**A1 补核表（11-11 协调者追加）：可用训练轨迹与 E186 管线的兼容性** `[页]`（HF API / GitHub API 逐仓库核；FLAME 每 iter token = global batch 1024 × seq 2048 ≈ 2.10M）

| 轨迹 | 结构 | 中间 ckpt（token） | 格式 / 加载 | 与 E186 转存管线 |
|---|---|---|---|---|
| OLMoE-1B-7B-0924 | 16 层、64 专家 top-8、5T token | 每 5000 步（≈ 20B） | HF | 现用 |
| FLAME-MoE-1.7B-10.3B | 18 层、64 专家 top-8 + 2 共享、23.1B token | iter 1100…11029，每 1100 iter ≈ 2.3B（10 点） | Megatron-LM torch_dist `.distcp`（单点约 20+ GB 分片）；**仓库无 HF 转换脚本**，HF 搜索无第三方 HF 版；仓库自带 `scripts/empirical_analysis/capture-*.sh`、`router_saturation_step*`（基于其 Megatron 子模块，从 GCS 拉权重） | **不能零改动**；需写 Megatron → HF 映射（含共享专家）或在 Megatron 内转存 |
| FLAME-MoE-721M-3.8B | 12 层，同上，18.4B token | iter 880…8815，每 880 ≈ 1.85B（10 点） | 同上 | 同上 |
| FLAME-MoE-290M-1.3B | 9 层，同上，11.4B token | iter 540…5473，每 540 ≈ 1.13B（10 点） | 同上 | 同上 |
| FLAME-MoE-419M-2.2B | 15 层，11.9B token | iter 2000 / 4000 / 5685（3 点） | 同上 | 同上 |
| FLAME-MoE-38M / 98M / 115M | 9 / 9 / 12 层，4.4–8.7B token | **只有终点** | 同上 | 无训练轴 |
| OpenMoE-8B | 24 层、**每 6 层一个 MoE 层**（共 4 个）、32 专家 **top-2**、容量因子丢 token（eval 2.0）、词表 256k、fp32 | HF 独立仓库 `openmoe-8b-200B / 400B / 600B / 800B / 890B / 1T`（6 点；主仓库 openmoe-8b 为最终） | HF PyTorch `.bin` + `modeling_openmoe.py`（trust_remote_code，transformers 4.34 时代；是否依赖 ColossalAI 内核未核对） | 需为自定义类写 hook；top-2 + 丢 token 与 OLMoE 读数不直接可比 |

一句话：**没有一条能零改动套 E186（HF transformers）管线**；OpenMoE 最接近（HF 格式但自定义类），FLAME 需要格式转换。FLAME 的总训练量（≤ 23B token）约等于 OLMoE 的第一个公开 ckpt（20B），所以它覆盖的恰是 OLMoE 左删失之前那段——对早期次序可能有信息，但配方（WSD 调度、DCLM 数据、小规模）不同。

### A2. 路由器携带来源记忆 / 路由器漂移 vs 输入漂移

| 项 | 内容 |
|---|---|
| 最近邻与 ownership | **Routing Drift 2609.32821**（已有卡，`[摘要]`）：合并 MoE（DeepSeekMoE / OLMoE / Qwen3-MoE）上交叉套用源 / 合并的路由器输入与参数，"多数重分配来自输入漂移"——**交叉套用 2×2 的唯一已知先例**。**Router Prior Bias**（Lee 等，NAVER，Findings EMNLP 2026，2026.findings-emnlp.2339）`[PDF]`：post-training 后与 base 路由器的**逐 token top-k 重合**（三层：利用率、top-k 重合、共激活社区 NMI），Moonlight-16B-A3B 与 Qwen3-30B-A3B-Base，math / code SFT，表 15 重合约 .39–.48；**用各自模型的隐状态，不拆路由器 vs 输入**；引言称 Unsloth 默认不训练路由层。**Thérien 等 2503.05029（TMLR'25）**`[HTML]`：持续预训练（含 / 不含回放）中饱和比回放低 10–15%、L0–4 词表专精下降；**不拆、不比重置路由器**。SAME ICML'26 / PASs-MoE ACL'26（corpus）：持续指令调优中"router drift / co-drift"作为方法动机，不做交叉套用。RSPO 2510.23027（ACL'26）`[摘要]`：RL 中的"router shift"，用路由器 logits 重加权。升级类：Sparse Upcycling / Drop-Upcycling 路由器随机初始化，Expert Upcycling 2604.19835 复制路由器行（CL 已核，均不测分化）；Qwen1.5-MoE 博客只说"upcycling"自 1.8B，**路由器初始化未公开**（未核对 Qwen2-57B 报告） |
| 我们的增量 | 把交叉套用从"合并后同层"换到"同一初始化、不同深度、各自完整预训练到终点"的自然实验，并给出**拷贝特异**的分量（R .53 vs 非拷贝 .15，H ≈ R 不特异）；Base vs Instruct 21% 是 post-training 的同类读数，但我们能拆 |
| 压缩风险 | 方法 **中–高**（Routing Drift 同构）；"post-training 改了多少路由"本身 **高**（RPB 已在 Qwen3-30B-A3B-Base 上报 top-k 重合，且 Base=Instruct 这一读数不新） |
| 最强先验预测什么 | Routing Drift ⇒ 输入漂移为主；我们 E187 读数 H ≈ R、仅 R 拷贝特异——**与 Routing Drift 的结论不同但场景不同**（同层短程合并 vs 跨深度长程训练），不能直接说"推翻" |
| 谁依赖答案 | 合并 / 修复路由的方法（HARC、SRR）；post-training 冻 / 锚路由器的默认（RPB、Unsloth）；升级时路由器复制 vs 重置的选择 |
| 诚实分级 | 子社区关心；单独成文的空间小，作 N4 的第二条轴有用 |

### A3. 推理时 token-id 查表 / 同 id 替换训练路由器的 NLL 代价（E190）

| 项 | 内容 |
|---|---|
| 最近邻与 ownership | **训练时用 token-id 路由**（不回答"训练好的上下文路由器换掉后多贵"，但给出强先验）：Hash Layers 2106.04426（NeurIPS'21）`[HTML]` 表 6 **Token Switch**（路由器输入 = 当前 token 的查表）23.43 vs Switch 23.73 test PPL（64 专家），作者假设隐状态"may be suboptimal for routing"；表 3 前一 token 哈希 24.16、bigram 24.19 劣于当前 token 23.22；StableMoE `[HTML]`：蒸馏路由器**以词嵌入为输入**（上下文无关）并冻结，PPL 19.48 → 19.28；MoLE ICML'25 Oral 2503.15798 `[摘要/检索]`：专家输入取嵌入层输出，推理时重参数化为按 id 的查表。**推理时用预测 / 静态表代替或预测路由**：SiDA-MoE MLSys'24 2310.18859 `[HTML]`：预测器 = **词嵌入序列 → 2 层 LSTM + 自注意力（SparseMax）+ FC**（§3.3–3.4，**带上下文**，不是 token id 查表），离线用真实路由 top-30 logits 蒸馏训练；推理时**真的替换路由器**（§3.1 "routers … do not participate in the forward pass"，§4.4 "We replace the router function with its approximation"）；模型 Switch-base-8/64/128/256（encoder-decoder，非 decoder LLM）；质量：微调后 SST2 / MRPC / MultiRC 保真度 base-8 为 97.5–99%、base-128 为 92.6–93%（表 4；摘要 "down to 1%" 只对应最好情况，§4.5 "up to 96%" 与表 4 不一致）；**预训练模型 C4 PPL 6.68 → 18.49（base-8）、4.86 → 11.73（128）、4.59 → 8.11（256）**（表 3）；命中率只报 top-3（90.5–99%，表 5），无 top-1、无分层。**这是在训练好的 MoE 上推理时用近似路由代替原路由并报 PPL 的先例**；与 E190 的距离：它的替代物是上下文模型的近似（不分离 token 身份与上下文）、Switch 小专家数、不分层不分 token 类，E190 的同 id 打乱 / 逐 id 查表问的正是它没问的"上下文那部分值多少"；它的 PPL 涨幅（×1.8–2.8）给出"近似路由代价可以很大"的先验；Semantic Parallelism 2503.04398 §3.2 `[HTML]`："Context-Independent Token Activation Prediction"，按 token id 计数的专家表，DSV2-Lite 上静态 top-k 预测 precision 96.3%、F1 78.8%（附录 A.2），**不改路由、不测质量**；ExpertFlow / Fate / Pre-gated / MoE-Infinity 报预取命中率（91–99%），但用的是隐状态或跨层门控，不是纯 id `[检索]`。**训练好模型上换路由测损失**：Misrouting 2605.07260（已有卡）等算力替代路由；How Modular 2606.25092 随机专家集；Expert Strikes Back 随机专家（FM B2）；Grouter `[HTML]` 论证"static lookup table eliminates contextual sensitivity"但**无实验**。**反向证据**：2606.22798 *Does the Same Token Mean the Same State?* `[摘要]`——固定输出 token id 后专家仍分离任务上下文、轨迹历史与推理模式（gpt-oss、Qwen3-MoE）；Mixtral §5 `[HTML]` 只有相邻 token 同专家率（L0 13.6–14.9% ≈ 随机 12.5%，L15 23.6–28.4%），**没有 token-id 路由的说法，也没换路由测 PPL**；OpenMoE §4 "routes based on the Token ID"（定性） |
| 我们的增量 | 在公开大模型上、不重训，直接量"上下文依赖"那部分路由的功能价值（同 id 打乱 vs 逐 id 查表 vs 原路由），并按层 / token 类 / 前一 token 恢复拆开；**未找到精确撞车**（SiDA 是最近邻：推理时替换 + PPL，但替代物是带上下文的近似、Switch 模型、无层 / token 类分解） |
| 压缩风险 | **中**：若代价 ≈ 0，会被读成 Hash Layers / StableMoE / OpenMoE 早已说过"token 路由就够"；若代价大，会被读成 Grouter 那句论证的实证。SiDA 已核：推理时替换确有先例且代价不小（PPL ×1.8–2.8），E190 须引它，并把增量放在"id 内打乱 vs id 查表"的分解与大模型分层上 |
| 最强先验预测什么 | 训练时文献 ⇒ 若从头用 id 路由，损失几乎不变；但**对已训练成上下文路由的模型**，专家已适应上下文路由，先验是"有可见代价、集中在深层与 fragile token"（Misrouting、2606.22798、OLMoE §5.4 深层按预测 token）。两类先验方向相反，E190 有信息 |
| 谁依赖答案 | 预取 / 卸载系统（静态 id 表能否直接执行而非仅预取）、MoLE 类查表架构、N1 的"路由器 = 几何读出 × 词表锐化"是否需要功能腿 |
| 诚实分级 | 子社区关心（MoE 分析 + 推理系统两个社区都能用这个数） |

### A4. Qwen3-30B-A3B 层复制是否有正式文献 / 12 层周期

| 项 | 内容 |
|---|---|
| 最近邻与 ownership | 本次复查（Web 4 组）**仍未找到正式文献或官方说明**；只有 CL 已列的 Kilian X 帖（负载级，12/24 层后同编号专家重现）与 Epstein LessWrong 短帖（Qwen3-32B 稠密，推测 8–31 层复制）`[检索]`。社区"层手术"帖（Qwen3-30B-A3B 复制 18–21 层最好、50–56% 深度危险区）`[检索]` 是推理时复制，不是证据。ai-muninn 博客 2026-09 的 12 次重复是 Qwen3.8-Flash-Next 的层类型，与权重无关 `[页]`。**逐层分析图中出现周期的出处：未找到**；FM Part C 第 1 问已列应受影响的 ≥7 篇（Bandarkar、Chen、Zheng、Li、Ye、Standing Committee、Misrouting），本次没有逐图核对页码 |
| 我们的增量 / 压缩风险 / 分级 | 同 CL：复制事实本身压缩风险高、不该作贡献；作测量样本是增量 |

---

## Part B — "相关工作为什么没有"的诚实版本

| 叙事里的理由 | 实况 | 类别 |
|---|---|---|
| 训练轴需要密集公开 checkpoint，只有 OLMoE-0924 | **不成立，但幅度比初报小**。FLAME-MoE 只有 3 个尺度有 10 个点（1.7B、721M、290M），419M 有 3 个点，38M / 98M / 115M 只有终点（HF API 逐仓库核）；格式是 Megatron torch_dist（`.distcp`），**仓库无 HF 转换脚本、HF 上无转换版**；训练只有 4.4–23.1B token（见 A1 补核表）`[页]`；论文 §6.3 已在其上画饱和曲线；OpenMoE-8B 公开 5 个中间 ckpt（每 200B token）`[HTML]`，Three Phases 已用 6 个；Output Dilution 用了 11 个 OLMoE ckpt | 有人做过一半（饱和曲线有三家，拆分没人做） |
| 还需逐 token 路由器输入转存 + 同一隐状态上的随机路由器 | 成立为"我们的工具"，但不是别人做不到的理由：转存是一次前向。真正的原因更可能是**问题没被提出**——各家把饱和直接读成"路由早定"（OLMoE、FLAME、OpenMoE 解释均如此），没人把它当成复合量 | 只是没人问（我们的搜索范围内） |
| MoE "早饱和"文献只看分配不拆路由器 / 几何 | **成立**（OLMoE §5.1、FLAME §6.3、Thérien §5.3、OpenMoE §4.2 均已核）。但要补：StableMoE 量过路由波动（反向结论）；Why Routers Freeze 从理论上预测路由器权重冻结；Grouter 做了路由扰动；这些都触及"路由器何时定"，都没有几何对照 | 真空白（拆分），周边有人 |
| 层复制先要发现复制本身（无正式文献） | 成立（复查仍无） | 真空白（正式文献层面） |
| Routing Drift 只问合并失败 | 成立；但 post-training 的"路由保留"已被 RPB（Findings EMNLP'26，Qwen3-30B-A3B-Base）、持续预训练的被 Thérien（TMLR'25）量过，都不拆 | 有人做过一半 |
| 稠密侧早期训练文献没有"可替换的读出器"这个把手 | **要改**：稠密侧有固定随机读出头（Hoffer ICLR'18）、freeze training（SVCCA）、逐层收敛速度（Chen ICLR'23）。差别在于 MoE 路由器是**逐层、离散、决定计算路径**的读出器，且可在同一隐状态上换成随机路由器做对照——这个把手是 MoE 特有的，但"读出器可替换"不是 | 措辞过强 |
| （E190）推理时查表的代价没人量过 | 训练好的公开 LLM 上**未找到**；但 SiDA-MoE 可能在 Switch 上做过"嵌入哈希代替路由、推理掉点 ~1%"（未核对正文），Hash/StableMoE/MoLE 在训练时给出强先验 | 只是我们没找到精确先例；半个先例待核 |

## Part C — 对 MAINLINE_NARRATIVE §5（及相关句）"未核对"文字的逐句核对

| 原句（§） | 结果 | 依据 / 建议改法 |
|---|---|---|
| §5 "训练轴需要密集公开 checkpoint（只有 OLMoE-0924）" | **要改**（初报"撤回"过强） | 改为"OLMoE-0924 是唯一 HF 格式、5T token、每 5000 步的密集轨迹；FLAME-MoE 3 个尺度各 10 点（Megatron 格式、≤ 23B token）与 OpenMoE-8B 6 点（HF + 自定义代码、top-2、每 6 层一个 MoE 层、200B 间隔）是可用但需转换、配方差异大的轨迹"（见 A1 补核表） |
| §4 N4 行"第二个训练轨迹（没有公开的）"、§7 第 5 条"没有公开的，只能自训" | **撤回"没有公开的"** | 公开的有，但不是零改动：FLAME 需写 Megatron → HF 转换（或用其仓库自带的 Megatron capture 脚本），OpenMoE 需 trust_remote_code 的自定义模型类。规模轴只剩 290M / 721M / 1.7B 三点 |
| §5 "+ 逐 token 路由器输入转存 + 同一隐状态上的随机路由器三者同时在手" | **要改** | 作为"我们怎么做"成立；作为"为什么别人没做"过强。改为"已有饱和曲线（OLMoE、FLAME、OpenMoE）都把分配稳定直接读成路由早定，没人把它拆成路由器与几何两部分" |
| §5 "层复制先要发现复制本身（无正式文献）" | 成立 | 本次复查仍无 |
| §5 "Routing Drift 只问合并失败" | 成立，**要补** | 补"post-training 保留（RPB, Findings EMNLP'26）与持续预训练（Thérien, TMLR'25）量过路由变化但不拆" |
| §5 "MoE 的'早饱和'文献只看分配不拆路由器 / 几何" | 成立 | 4 篇已核；补 StableMoE（反向）、Why Routers Freeze（理论预测路由器冻结） |
| §5 "稠密侧的早期训练文献（lottery ticket rewinding、critical period）没有'可替换的读出器'这个把手" | **要改** | 稠密侧有固定随机读出头（Hoffer '18）；改为"读出器只在网络末端、不逐层决定计算路径；MoE 路由器是逐层的离散读出器，能在同一隐状态上换成随机路由器" |
| §5 "与 Routers Learn Geometry 同向但那是 1B 自训、无零模型" | 成立，**要补** | 再补 Why Routers Freeze（理论，SP 下路由器一步冻结）与 Motif 3 lock-in——它们与 N4 同向，是先验而非对手 |
| §4 N4 行"Myth 与 Routing Drift 都预测反面" | **要改** | 先验分裂：几何说预测同步、Routing Drift 预测输入为主；Why Routers Freeze / OpenMoE / Motif 3 预测路由器先停；StableMoE / Grouter §1 预测路由器长期波动。N4 的"反直觉"应落在**相对次序 + 来源记忆**，不是"与所有先验相反" |
| §5 会杀死 N4 的结果 (iv)"有人已在公开 checkpoint 上做过路由器 vs 几何的先后" | 本次范围内**未发现** | 最近：OLMoE §5.1、FLAME §6.3（只看分配） |
| §6 E190 "代价 ≈ 0 → 路由器 ≈ 查表" | 要补先验 | Hash Layers Token Switch ≥ Switch、StableMoE 词嵌入路由器冻结后更好、Semantic Parallelism 静态 id 表 precision 96.3%——"≈ 查表"有强先验，结果若 ≈ 0 需写成"对这些训练时结论的推理时确认"；若 > 0 则与 Grouter 的论证、2606.22798 同向 |

## Part D — 未核对清单

- SiDA-MoE 正文 11-11 已核（见 A3）。仍未核：表 3 PPL 的路由 k、是否所有 MoE 层都替换；预测器训练语料与 C4 评测是否同分布。
- Why Routers Freeze 正文：无 arXiv；两个 OpenReview 论坛（TccaEvFVmc、AhwB471ARJ）均被验证页挡住，只读到 NeurIPS / ICML 会议页摘要。未核：SP 的具体宽度标度、有限宽实验的模型规模与数据、是否测路由分配（而非 logits / 梯度）。
- Motif 3 "router lock-in" 原句与节号（只检索摘录）。
- FLAME-MoE：token 数与格式已核（A1 补核表）；未核：Megatron ckpt 的层命名、能否用 Megatron 官方转换工具导出 HF；论文 §6.3 用的是否就是这些公开点。OpenMoE 自定义模型类的依赖未核。
- Router Prior Bias 表 15 的 top-k 重合是否归一化到 k、各行对应模型 / 数据；Qwen3-30B-A3B-Base 上 SFT 的重合具体值。
- Qwen2-57B-A14B / Qwen1.5-MoE 技术报告中路由器初始化原文。
- 相邻领域各条（SVCCA、Chen ICLR'23、Frankle、Achille、Jastrzebski、Hoffer、Driscoll、Rule）只凭记忆，未取原文核对页码与措辞。
- Qwen3 逐层分析图中的 12 层周期：Bandarkar、Chen、Zheng、Li、Ye、Standing Committee、Misrouting 的 Qwen3 逐层图未逐一查看。
- 2606.22798 只读摘要；MoLE 只读摘要与检索摘录；Pre-gated / ExpertFlow / MoE-Infinity 命中率只来自检索。
- Thérien 2503.05029 后半（10 万字后）未读。
