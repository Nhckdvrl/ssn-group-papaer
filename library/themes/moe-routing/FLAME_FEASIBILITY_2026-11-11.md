# FLAME-MoE 中间 checkpoint → E186/E189 转存：可行性探测（2026-11-11）

**结论：可行，约 3–4 小时写代码 + 自检（290M 起步）；推荐路径 (iii) 映射到 HF `Qwen2MoeForCausalLM`。** 已实测：不装 Megatron，用 HTTP range 只下 bf16 模型权重（290M iter_540 2.6 GB / 18.2 GB，跳过优化器状态，3 分 47 秒），`torch.distributed.checkpoint` 在 CPU 上 4.2 秒读出 81 个张量（1.30B 参数，全非零），路由器权重与 pre-MLP RMSNorm 增益已定位。0 GPU；未做前向。

**两条与文献不一致的事实（来自 checkpoint 内 `common.pt` 的训练 args，三个尺度一致）：** (1) **top-k = 6，不是 8**（`moe_router_topk=6`；README / 正文写 top-8，论文卡已记的"附录图注 top-6"才是对的）；(2) **第 0 层是稠密 MLP**（`moe_layer_freq=[0,1,…]`），MoE 层只有 1..L−1。

| 尺度 | 层（MoE 层） | d_model | 头（GQA 否） | 稠密 FFN | 专家 FFN | 共享 FFN（=2×专家） | 专家 / top-k | WSD 衰减起点 |
|---|---|---|---|---|---|---|---|---|
| 290M-1.3B | 9（8） | 1024 | 16 MHA，hd 64 | 5472 | 704 | 1408 | 64 / 6 | iter 4926 |
| 721M-3.8B | 12（11） | 1536 | 16 MHA | 8208 | 1056 | 2112 | 64 / 6 | iter 7934 |
| 1.7B-10.3B | 18（17） | 2048 | 16 MHA | 10944 | 1408 | 2816 | 64 / 6 | iter 9927 |

共同：RMSNorm eps 1e-6、无 bias、无 qk-norm、RoPE base 1e4 全维非交错、SwiGLU、词嵌入与输出不共享；路由器 softmax（pre-softmax，先对 64 个专家 softmax 再取 top-6，不重归一化），路由器 fp32；aux loss 0.01 + z-loss 0.001，无专家偏置；共享专家无门控（直接相加）；分词器 `EleutherAI/pythia-12b`（GPT-NeoX，padded vocab 50304）；数据 DCLM；lr 3e-4→3e-5，warmup 1%，最后 10% iter 指数衰减。

**10 个 checkpoint 的 token 数** = iter × global batch 1024 × seq 2048 = iter × 2.097M（来源：`common.pt` args；`consumed_train_samples` = iter × 1024 在 540 / 880 / 1100 三处核对相符）。
- 290M：iter 540, 1080, …, 4860（每 540）, 5473 → 1.13, 2.26, 3.40, 4.53, 5.66, 6.79, 7.93, 9.06, 10.19, **11.48B**
- 721M：iter 880, …, 7920（每 880）, 8815 → 1.85, 3.69, 5.54, 7.38, 9.23, 11.07, 12.92, 14.76, 16.61, **18.49B**
- 1.7B：iter 1100, …, 9900（每 1100）, 11029 → 2.31, 4.61, 6.92, 9.23, 11.53, 13.84, 16.15, 18.45, 20.76, **23.13B**
- 每个尺度只有终点在 WSD 衰减段之后，倒数第二点是"衰减前终点"（对应 E189 的 5.1T vs 发布版）。无 iter 0 / 初始化点。

**三条路径的工程量**
- (i) DCP 读 state dict + 自写最小前向：读权重已打通（0.5 h 已花）；前向 3–5 h。坑：Megatron fused qkv 的行顺序按头交错 [q_h,k_h,v_h]×16；fc1 = [gate; up] 拼接；layer 0 的 norm 融在 `linear_fc1.layer_norm_weight`。无比 (iii) 更好的地方。
- (ii) 装 Megatron（作者 fork yuzc19/Megatron-LM@cbaf684 + apex + TransformerEngine v1.11 源码编译，torch 2.6/cu124）：≥ 1 天，且原样只存 top-k（`moe_layer.py` 里 `EACT_SAVE` 存 (values, indices)），要改 fork 加隐状态 hook、把 FLORES 预处理成 Megatron indexed 数据、EP=8→1 重切分未验证。不推荐。
- (iii) 写 Megatron→HF 映射到 Qwen2MoE（transformers 4.57 已核：`qkv_bias=False`、`mlp_only_layers=[0]`、`norm_topk_prob=False`、`num_experts_per_tok=6`、`shared_expert_intermediate_size`；共享门 `sigmoid(W·h)` 无偏置 → 门权重置 0 得 0.5、共享 down_proj ×2，bf16 下精确）：转换 1–1.5 h + 阳性对照 1–2 h；之后 E186 的 `mlp.gate` 输入 hook 管线基本原样可用。**推荐。** Megatron 仓库 `tools/checkpoint` 没有 GPT/MoE 的 HF saver（只有 llava），HF 上也无第三方转换版。
- 阳性对照（必须）：转换后在英语留出文本上的 LM loss 应接近 FLAME 报的验证 loss（未核对其数值来源）；qkv 顺序错时 loss 会接近均匀；fp32 路由器（Megatron）vs bf16 gate（HF）的 top-6 平局翻转需报。

**下载**：HF 支持 range 请求；只取模型权重每点 290M 2.6 GB、721M 7.7 GB、1.7B 20.6 GB（由 `.metadata` 偏移算出），实测 ≈ 11 MB/s（12 路并发）→ 290M 十点约 40 分钟、721M 约 2 h、1.7B 约 5.5 h；1.7B 需"下一点→转存→删"流水（fvcrc20 /tmp 剩 82 GB）。`.metadata` 反序列化要给 `megatron...MCoreSavePlan` 打桩（自定义 Unpickler）。

**风险**
1. top-6 vs OLMoE top-8：一致率的偶遇基线、负载乘积期望不同，跨模型只比形状。
2. 共享专家：路由器输入定义与 OLMoE 相同（pre-MLP RMSNorm 输出 = Qwen2MoE 的 post_attention_layernorm 输出），但残差流每层恒加共享专家输出，路由器只为 routed 部分得梯度——"几何"不全由路由塑造，与 OLMoE 不可等同。
3. 分词器不同（Pythia/NeoX vs OLMoE 的 dolma 版 NeoX）：toksub_meta 须按 E186 规则重抽，(src, sid, pos, inp) 与 OLMoE 不能逐 token 对齐；E189 第 5 项的 H(e∣id) 表需重建。
4. DCLM 以英语为主，小模型上 FLORES 非英语 token 离分布；建议主用英语 + UD 视图。
5. 第一点已是 1.1–2.3B token，最早 ~1B token 仍删失；无初始化 checkpoint（seed 1234 但复现需 Megatron 同并行布局，未核对）。
6. 三个尺度只有 3 个点、≤ 23B token、WSD + DCLM 配方，与 OLMoE（5T、cosine/退火）不同；能回答"最早期是否也路由器先定"，不能单独回答尺度律。
7. `e186_hidden.py` 不在仓库 `division/scripts/`（未核对节点副本），转存格式按 E189 卡与任务描述理解。

**资产（节点本地 fvcrc20）**：`/tmp/xiang_flame/290m/iter_0000540/`（稀疏文件，仅模型权重区段有效）、`/tmp/xiang_flame/290m/router_norm_540.pt`（路由器 + 全部 norm 增益）、三尺度 `common.pt` / `.metadata` / range 表、脚本 `/tmp/xiang_flame/scripts/{meta,common,ranges,fetch,load}.py`。未 commit。
