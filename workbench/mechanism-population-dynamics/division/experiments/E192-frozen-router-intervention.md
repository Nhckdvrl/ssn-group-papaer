# E192：干预（因果腿）——FLAME-MoE-290M 从公开早期 checkpoint 续训，路由器自由 / 冻结 / 重置（2026-11-17）

- **状态：** RUNNING（11-17 19:45 八臂已在 fvcrc20/21 启动，主会话 19:57 核对全部在跑；以下登记内容写于续训之前：11-17 写定臂、读数、阳性对照、地板、"会改变读法的结果"，在任何续训之前；之前只做过：checkpoint 的 args / 优化器键检查、数据下载与分词、冒烟（加载 + 评估 + 5 iter 计时）。跑后不改，事后新加的读数标 POST-HOC）
- **类型：** EXPLORE → 主线 N4 的因果腿（DIRECTION §26 "留给人决定的事"第 2 条；用户 11-17 批准并要求"多用几个 GPU、fvcrc20/21 都能用、不限时间、跑扎实"）。不写二元判决表；不推进主张等级（C28 的升级由主会话在结果后按 EXECUTION §3 处理）。
- **对应：** 主张 C28（路由器先于隐状态定型，L1）、C29（上下文路由的功能价值）；叙事 N4（DIRECTION §23–§26）。
- **问题（一句话）：** E189/E191 观察到路由器的决策函数先于它读的隐状态定型（FLAME-290M：到 n = .8 路由器 3.79B vs 隐状态 6.39B token，2.26B 起每个点 R > H）；**如果在 2.26B 处把路由器冻住（或重置）再继续训练，模型损失和路由会怎样**——早定的路由器够不够用，之后的那 1 − R ≈ .25 漂移有没有功能，路由器的"来源记忆"是不是可有可无？

## 起点与已知（登记前已看过，视为已知量）
- 模型：HF `CMU-FLAME/FLAME-MoE-290M-1.3B`（Megatron torch_dist）。起点 **S = iter 1080（2.26B token）**；次要起点 iter 540（1.13B，R ≈ H）。官方相邻公开点 iter 1620（3.40B）、2160（4.53B）为锚点。
- 训练配置（来自 checkpoint `common.pt` args，iter 1080）：global batch 1024 × seq 2048（= 2.10M token / iter），micro batch 8（DP 32、EP 8、TP 1），Adam β = (0.9, **0.999**)、eps 1e-8、weight decay 0.01（1 维参数 wd_mult 0）、clip 1.0、lr 3e-4（WSD：warmup 1% ≈ 55 iter，iter 4926 起指数衰减到 3e-5；**本卡所有续训段都在常数段，lr 恒为 3e-4**）、dropout 0、bf16 + fp32 主权重 + fp32 梯度累积、aux loss（Switch，micro batch 级）0.01、z-loss 0.001、router fp32、pre-softmax 取 top-6 不重归一、dropless（capacity None）、`reset_attention_mask=False`、`eod_mask_loss=False`、init std 0.02、seed 1234。
- **优化器状态可读：** checkpoint 里有分布式优化器的 fp32 主权重 + Adam exp_avg / exp_avg_sq（`chained_0` = 非专家 65 个张量，`chained_1` = 专家 16 个张量，扁平存储），step = 1080（iter 540 处 = 540）。β2 = .999 时偏差校正在 step 1080 仍有 1/(1 − .999^1080) ≈ 1.5 倍，所以 step 一并恢复。
- **官方训练数据**：`data_path` = DCLM-baseline 的 global-shard_03 下 local-shard 1/3/6/8/9 共 1395 个分片。**本卡的训练池与评估集取自 global-shard_10 / local-shard_9，与官方训练文件不相交**（按文件名；文档级去重未做）。
- E191 全部结果（含 iter 1080 的英语 loss：FLORES eng 4.2066、UD 4.1569，HF Qwen2Moe 映射 bf16 前向）。

## 实现
- **模型**：`division/scripts/e192_train.py` 用纯 PyTorch 重写 FLAME-290M，**参数名与 Megatron-core fqn 逐字相同**，官方 checkpoint（含优化器状态）一对一映射；fused qkv 按头 [q;k;v] 交错、fc1 = [gate; up]、第 0 层稠密、MoE 层 1–8：64 专家 top-6 + 共享专家（1408，无门控，直接相加）。不经过 HF Qwen2Moe（因此 E191 的"共享门权重 0、down_proj × 2"等价处理在这里不需要——直接按 Megatron 语义相加，所有臂一致）。RMSNorm 在 fp32 里算；RoPE fp32；SDPA 因果注意力；router logits fp32；专家按 token 排序后逐专家矩阵乘；LM 交叉熵 fp32。
- **损失**：LM + Σ_层（aux + z），aux 按 Megatron `switch_load_balancing_loss_func`（全 softmax 分数 × 每专家 token 数，E·coeff/(n²K)），**按官方 micro batch（8 条序列）分组计算再平均**，与 DP 下每个 rank 每个 micro batch 各算一次等价；z = mean(logsumexp²) × 0.001。
- **精度与优化器**：fp32 主权重，bf16 autocast 前向，fp32 梯度跨 micro batch 累积，torch fused AdamW（解耦 wd、按参数 step 的偏差校正，与 apex FusedAdam adam_w_mode 同式），全局范数裁剪 1.0（冻结的参数不参与范数）。批大小 1024 × 2048 用梯度累积实现（我们的 micro batch = 16 条序列，64 次累积；只影响显存，不改数学，aux 仍按 8 条一组算）。
- **优化器状态**：从官方 checkpoint 读入 fp32 主权重与 Adam 动量（HTTP range 取 `chained_*` 张量），检查 fp32 主权重舍入到 bf16 后与模型张量**逐位相等**（不等即停）；step 恢复为起点 iter。冻结臂不建优化器状态；重置臂的路由器 Adam 状态清零、step 从 0 计（全新参数的标准偏差校正）。
- **数据**（`e192_data.py`）：DCLM-baseline global-shard_10/local-shard_9 的 shard 00–23（jsonl.zst），pythia-12b 分词（add_special_tokens=False），每个文档后接 EOD（id 0；Megatron `--append-eod` 惯例，FLAME 的预处理未核对）。shard 23 的前 2,097,153 token = **DCLM 留出评估流**（1024 个 2048 窗口），任何臂都不训练；训练池 P1 = shard 00 起的前 540 × 1024 × 2048 + 1 token，P2 = 接下来同样多。训练序列 = 池内第 j 个 2049 窗口（跨文档打包、因果注意力跨文档、EOD 不屏蔽 loss，与官方 args 一致）；窗口顺序 = `default_rng(1000 + 数据种子)` 的置换。**同一数据种子的所有臂逐 iter 看到完全相同的序列**。wikitext-103-raw test（HF parquet，按原文行拼接，285,831 token）作第二评估集。
- **转存**：每 54 iter 在 E191 的同一批 token（FLORES 20 语 + UD，N = 21,500，主视图英语 12,000）上存各 MoE 层路由器输入（`toksub.npy` fp16 [8, N, 1024]、`toksub_meta.npz`、`router.npz`、`topk_fp32.npy`、`meta.json`，格式同 E191；这里的 top-6 是 fp32 router 在 bf16 隐状态上算的，与 Megatron 一致）+ 路由器权重与 pre-MLP 增益 + 两个留出集的逐 token NLL（fp16）+ E191 英语文本 loss；每 270 iter 存 bf16 完整权重；每 27 iter 存续跑状态（模型 + 优化器，原子替换）；每 iter 记训练 loss / aux / z / 梯度范数 / router 哈希 / 第一个 micro batch 的 top-6 概率和与最大负载。
- 官方锚点 iter 1080 / 1620 / 2160（与 540）用同一代码评估与转存（`e192_eval.py`，bf16 权重）。

## 臂（每臂 1 卡；第一轮 8 卡并行）
| 臂 | 起点 | 路由器 | aux / z | 数据种子 | 续训到 |
|---|---|---|---|---|---|
| A1 / A2 | 1080 | 自由（对照） | 开 | 1 / 2 | 1620（阶段 1），之后 2160（阶段 2） |
| B1 / B2 | 1080 | **冻结**（8 层 router.weight 不更新、不进优化器；pre-MLP 增益与其余参数照训） | 开 | 1 / 2（与 A 配对） | 同上 |
| C1 / C2 | 1080 | **重置**（router.weight ~ N(0, 0.02)，初始化种子 101 / 102；专家与其余参数不动） | 开 | 1 / 2（与 A 配对） | 同上 |
| D | 540 | 冻结 | 开 | 1 | 1080 |
| E | 540 | 自由 | 开 | 1 | 1080 |
| F（次要，卡空出后） | 1080 | **只训路由器**，其余全冻结 | 开 | 1 | 1620 |
| G（次要，卡空出后） | 1080 | 冻结 | **关** | 1 | 1620 |
阶段 2 用池 P2（新数据，不重复 P1）。C1/C2 用不同的初始化种子（否则 C1 vs C2 的一致会混入同一初始化）。

## 读数（写死）
1. **评估损失**：各臂每个保存点在 DCLM 留出流与 wikitext-103 test 上的平均 NLL；CI = 按 2048 窗口配对自助 1000 次。锚点 = 官方 iter 1080 / 1620 / 2160 权重在同一评估集上的 NLL。主对比 **B − A、C − A（同种子配对）**；**噪声地板** = |A1 − A2|（数据顺序）以及 A 与官方同 token 数权重之差（续训忠实度）。D − E 同口径。
2. **路由**（E191 的 R 口径：同一输入 x̂ 上 top-6 重合 / top-1 一致，主口径增益归属同 E191）：
   (a) A 终点路由器与官方 iter 1620 路由器在同一输入上的一致率，以及 A1 vs A2 的一致率——路由器后续漂移跨数据顺序是否重现；
   (b) C 的重学路由器随 iter 与 S 的原路由器、与 A 终点路由器的一致率曲线（专家匈牙利配对后与恒等两种都报）——回到原分配还是去了别处；
   (c) B 中有效路由器 W·diag(g) 的漂移（冻结的是 W，增益 g 仍在训）；
   (d) 各臂的 O / H / R 对各自终点与对官方终点，用 `e191_decomp.py` 的口径。
3. **几何**：B 与 A（同种子）的路由器输入在同一 token 上的相似度（读出子空间内 / 外的逐 token 余弦与 CKA，读出子空间取 A 终点有效路由器的行空间）；负载分布（每专家份额）与 top-6 概率和。
4. **token 类**：B − A、C − A 的逐 token NLL 差按位置 0 / 词片段（无前导空格）/ 频率五分位 / H(e∣id)（由 A 终点在 DCLM 留出流上算）分层。
5. **原始样例**：B − A 最大 / 最小各 20 个 token 带上下文（DCLM 留出流）。

## 阳性对照
- (p1) 加载 S（iter 1080）后在 E191 英语文本上的 loss 与 E191 记录一致（FLORES eng 4.2066、UD 4.1569，±.01；E191 用 HF Qwen2Moe 映射，这里是独立重写的前向）。
- (p2) fp32 主权重舍入到 bf16 后与 checkpoint 的 bf16 模型张量逐位相等（检验扁平优化器状态的重排）。
- (p3) A 续训前 54 iter 的训练 loss 不出现 > .05 的跳变（优化器状态恢复后不应有重启瞬态；超了就查并记录）。
- (p4) 冻结臂的 router.weight 逐 iter 哈希不变（日志 `router_unchanged`）。
- (p5) 重置臂在续训第 0 点的路由与原路由一致率 ≈ 偶遇水平（top-6 重合 ≈ 6/64）。
- (p6) A 到 iter 1620 时的评估 NLL 与官方 iter 1620 之差必须报出（"我们的续训是否忠实"的刻度，不设通过线）。

## 噪声地板
A1 vs A2（只差数据顺序）的 NLL 差与路由一致率；A 与官方同 iter 的 NLL 差；随机专家置换（200 次）与 E191 的三族随机路由器地板；配对自助 CI。只有 2 个数据种子：种子方差只有一个自由度，地板写成"观察到的 |A1 − A2|"，不当成方差估计。

## 最强先验（写进卡，不是判决）
- StableMoE（蒸馏后冻结路由器 PPL 19.48 → 19.28，不降反升）、Hash Layers（固定哈希路由不差）、Why Routers Freeze（路由器权重更新本来就会冻结）⇒ **冻结几乎无代价**。
- 反向：E191 显示 S 之后路由器仍有 1 − R ≈ .25 的漂移（到 iter 1620 R .794 对终点），若这部分漂移有功能，B − A > 噪声地板。

## 会改变读法的结果（不写二元判决表；每种写放弃什么）
1. **B − A 在地板内**（两个配对都是）→ 路由器在 2.26B 时已足够，之后的漂移功能上可有可无；放弃"后续路由器漂移是学习的一部分"的说法，N4 写成"早定且已足够"（只限此配方 / 此尺度 / 1.1B token 的续训窗口）。
2. **B − A 显著为正**（CI 不含 0 且 > |A1 − A2|）→ 后续漂移有功能，N4 的"先定型"要加限定（定型 ≠ 完成）；放弃"冻结早期路由器无代价"在此配方上的外推，StableMoE 先验不成立于 softmax top-k + aux 的配方。看差是否随 iter 增长（持续增长 = 路由器持续承担学习；稳定 = 一次性缺口）。
3. **C 很快回到原分配**（与 S 原路由器的一致率远高于偶遇并趋近 A1–A2 的水平）→ 分配由专家 + 几何决定；"路由器携带来源记忆"改写为"专家–路由器配对是吸引子"，放弃"路由器本身存储历史"的措辞。
4. **C 去了别处且 NLL 追平** → 存在多个等价分配，路由器历史决定落在哪个；"来源记忆"保留但改为"功能上中性的记忆"。
5. **C 的 NLL 长期追不平** → 专家已与原路由器共适应，早期路由决定了专家分工；放弃"路由器可随时替换"的读法。
6. **D − E 与 B − A 的对比**：D − E 明显大于 B − A → 1.13B 太早，"够早"的点在 1.13–2.26B 之间；两者相近 → 冻结代价与起点无关（在这两个点上）。
7. 次要臂：F 的路由器在几何固定时的漂移方向是否与 A 的路由器漂移相同（A 的路由器漂移是否只是追随几何）；G − B：aux / z 经 logits 推几何的效应量。

## 混杂审计（EXECUTION §4）
- **续训 ≠ 原训练**：数据分片不同（不相交）、数据顺序不同、我们的实现不是 Megatron（核算子、bf16 舍入路径、aux 的数值细节）——用 (p1)(p6) 与 A vs 官方的差标出刻度；所有臂共用同一实现，B − A 的对比不受影响。
- **优化器状态**：已恢复（若 (p2) 失败则改为全新 AdamW + 短 warmup，所有臂同样处理，并在此注明）。
- **冻结的是 W 不是有效路由器**：pre-MLP 增益 g 仍在训，读数 2c 单独报；若要"有效路由器完全冻结"需另一臂（未登记）。
- **aux / z-loss 在冻结臂仍经 logits 把梯度传给隐状态**：G 臂分开这一项。
- **种子数 2**：地板只有一个自由度（见上）。
- **wikitext 与 DCLM 不同分布**；主读 DCLM 留出流。
- **单尺度、单配方**（290M，WSD 常数段，softmax top-6 + 共享专家）。

## 算力
8 臂 × 540 iter × 2.10M token = 每臂 1.13B token。冒烟实测（RTX PRO 6000 Blackwell Max-Q 单卡，micro batch 16，torch.compile 只融合 RMSNorm / RoPE / SwiGLU 逐元素核，CE 分块重算）：**约 60k token/s ≈ 35 s / iter，显存 61 GB**；每臂阶段 1 ≈ 5.3 h 训练 + 11 次评估 / 转存（每次约 1 分钟）+ 续跑存盘 ≈ **5.5–6 h 墙钟**。阶段 1 合计 ≈ 8 × 6 = 48 GPU h；阶段 2（A/B/C 6 臂）再约 36 GPU h；F、G 各约 6 GPU h。只做不改数学的提速（专家权重一次转 bf16 + unbind，避免逐专家索引的全尺寸零梯度；逐元素核融合；分块 CE）；批大小 / 学习率 / micro batch 分组的 aux 都未改。

## 执行记录（11-17，写在启动前后；结果另写）
- 环境：两节点各建 `/tmp/xiang_e192/env`（`e192_mkenv.sh`）；节点没有 Python.h，triton 编译时用 uv 装的 CPython 3.12.16 头文件（`C_INCLUDE_PATH`），第一次 8 臂启动因此在第一个编译核处崩溃，清空目录后重启（无训练步发生）。
- **(p1) 通过**：独立重写的前向在 iter 1080 上 FLORES eng 4.2061 / UD 4.1569（E191：4.2066 / 4.1569）；DCLM 留出 NLL 3.5830、wikitext 3.9225（官方 1080，fp32 主权重口径；bf16 口径待 `e192_eval.py` 跑锚点时一并报）。
- **(p2) 通过**：81/81 个张量的 fp32 主权重舍入到 bf16 后与模型张量逐位相等（最大差 0）——**优化器状态按官方恢复**（fp32 主权重 + Adam 一 / 二阶矩，step 1080；冻结臂 73 个可训张量全部带状态；重置臂 8 个路由器张量状态清零、step 0）。
- 冒烟（A 配置 5 iter，GPU 0 fvcrc20）：训练 loss 3.574 / 3.542 / 3.575 / 3.558 / 3.546（起点 DCLM 留出 3.583，无跳变），aux 合计 .0813（8 层 × ≈ .010，均衡值）、z .0007、梯度范数 .18 → .27（前 5 iter 缓升，持续观察，(p3) 在 54 iter 处判断）。
- **启动（11-17 19:25 / 19:45）**：fvcrc20 GPU0–3 = A1 / B1 / C1 / D，fvcrc21 GPU0–3 = A2 / B2 / C2 / E；目录 `/tmp/xiang_e192/arms/<臂>/`，结束时写 `DONE_0540`。实测 34–35 s/iter；预计 1080 起点的 6 臂 11-18 约 00:45 到 iter 1620，D / E 约 01:10 到 iter 1080。iter 540 起点 (p1) 同样通过：FLORES eng 4.6211（E191 4.6212），DCLM 留出 3.9482。官方锚点 1620 / 2160 只下了 bf16 模型张量，评估与转存（`e192_eval.py`）留到卡空时跑。F / G 未启动（无空卡）。阶段 2 = 同一行 launch 命令把 n-iter 改为 1080 即从 resume.pt 接着跑（P2 已在两节点）。
- **(p3) 通过**：前 54 iter 训练 loss 相邻跳变最大 .033（A1/B1）/ .028（A2/B2），1–10 iter 均值 3.558 / 3.561 → 45–54 iter 3.521 / 3.516；A2 在续训 54 iter 时 DCLM 留出 NLL 3.5349（起点 3.5830）。续跑状态（15.6 GB）与 54 iter 的评估 / 转存路径已实际走通。
- 启动后第一点：A/B 两种子在续训第 0 点 NLL 一致（3.5830）；B 的 `router_unchanged` = True；C 重置后第 0 点 DCLM NLL 4.846 / 4.842（比 S 高 1.26 nat），z-loss .151（随机路由器的 logsumexp ≈ 4.4，官方路由器的 logits 被 z-loss 压到 lse ≈ 0.3）。

## 产出
`division/scripts/e192_{data,fetch,inspect,train,eval,dump,analyze}.py`、`e192_mkenv.sh`；`division/results/e192/`（表、json、图，< 5 MB）。大文件只在节点本地（见资产位置）。

## 资产位置（节点本地，重启即失）
- fvcrc20 与 fvcrc21（192.168.0.37）：`/tmp/xiang_e192/{env,scripts,data,tok,dclm,ckpt,official,arms/<臂>}`；环境 `e192_mkenv.sh`（torch 2.8.0+cu128、transformers 4.57.6、numpy 1.26.4、zstandard、pyarrow<16）。
- 每臂目录：`train_log.jsonl`、`run_info.json`、`resume.pt`（续跑）、`routers_cXXXX.npz`、`nll_cXXXX.npz`、`dump_cXXXX/`、`full_cXXXX.pt`、`DONE_XXXX`、`stdout.log`。

## 结果（跑完后填写；上面内容不改，修改需注明日期）
