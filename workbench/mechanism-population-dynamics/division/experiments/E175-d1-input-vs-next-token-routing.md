# E175：d1-input-vs-next-token-routing（2026-11-06）

- **状态：** DONE（2026-11-06；预注册部分纯 CPU、只用 E167 路由缓存 + 分词器；POST-HOC A 在 CPU 上做了终点前向（200 段），B 用 hidden 缓存；不再追加）
- **类型：** PILOT（D1 的最便宜决定性试探；不是论文实验，产出给主会话判断"值不值得继续"）
- **对应：** [READOUT_CATALOGUE](../../../../library/themes/moe-routing/READOUT_CATALOGUE_AND_SEED_ROBUSTNESS_2026-11-06.md) §5 的 D1；表 1 的 #4（OLMoE §5.4）与 #7（OpenMoE §4.1–4.2）
- **问题（一句话）：** 我们的自训 MoE 里，深层路由更多由"当前输入 token"决定，还是由"真实下一 token"决定；若沿训练有从前者到后者的转换，发生在训练哪一段、哪些层，三个 init seed 是否一致？

## 两篇原文（读数定义与原话；PDF 在会话 scratchpad，未进仓库）
- **OpenMoE（Xue 等，arXiv 2402.01739v2）§4.1–4.2 `[节]`**
  - 读数：单模型（第 3 个 MoE 层为默认，"we did not observe significant differences across layers"）；按 token ID 画各专家的路由比例（图 10、附录 E 的路由标准差）；各专家 top-10 偏好 token 表（表 9）；不同中间 checkpoint（200B–1T token）上同一批 token ID 的路由比例叠画（图 11）。无数值指标、无随机基线。
  - 原话："All these tokens show a very strong specialization on only a few experts. … That means, MoE simply routes based on the Token ID instead of high-level semantics. We name this observation as Context-independent Specialization"（§4.1，p.12）。"the tokens with the same Token ID are always routed to the same expert no matter what the context is"（§4.2）。"We can see that the expert preferences are almost totally overlapped for different checkpoints, which means that the model has started to fix its routing at the very early stage of training. … Therefore, the routing probably has been learned at the warmup stage or so, and kept throughout the whole following training stage."（§4.2，p.13）。摘要："Token ID routing specialization is established early in pre-training and remains largely fixed"。
- **OLMoE（Muennighoff 等，arXiv 2409.02060）§5.4 `[节]`，式 (8)，图 23（k=1）、附录 G 图 30（k=8）**
  - 读数：Vocabulary specialization(E_i, x) = N^(k)_{x,E_i} / N_x，"the proportion of tokens with a token ID x … that are routed to one particular expert E_i out of all experts in that layer"；x 取输入 token ID、真实下一 token ID 或模型预测的下一 token ID；层值 = "we average the specialization of each expert in that layer"。**原文没写对 x 怎样聚合成一个专家的值**，下面读数 A 的聚合是我们的选择。终点单模型，无随机基线（定性）。
  - 原话："Later layers also specialize more on predicted output token IDs rather than input token IDs, i.e., the routing is decided more by the token the model is about to predict rather than the original input token. This is intuitive as in earlier layers there is more uncertainty about which token the model will predict."（p.22）。注意：这句话说的是**预测**的下一 token；真实下一 token 在图 23 中是第三条线，正文没单独下结论。
- **两者的关系：** OpenMoE 看的是输入 token ID、沿训练的中间 checkpoint；OLMoE 比较输入 / 输出 token ID、只看终点。没人把"输入 vs 下一 token"放在训练轴上。本卡只能测**真实下一 token**（预测下一 token 需前向，标为"需前向，待定"）。

## 设置
- **数据（核对过）：** `~/mechpop_cache/e167_analysis/routing/<run>__ckpt_<t>.npz` 的 `S{l}`（29,551 × 8，`torch.topk` 默认降序，`S[:,0]` = top-1 专家）。锚点 = `pairs.npz` 的 `anchor_word`（`results/e167/passages.json` 的词索引）。**抽样方式**（`scripts/ud_passages.py`、`capture_routing.py`）：UD EWT test + 前 4000 句 train 的整篇文档切成 ≤400 词的段；锚点 = 出现 ≥6 次的（小写）词形、每词形最多 40 个（固定种子）、共 1,827 个词形；每个词取**覆盖其最后一个字符的 token**（44 个 token 越过词尾的无效锚点已删）；前面加 EOS 整段前向。所以 `S` 是"词末 token 位置"的路由，**不是连续 token**。
- **词形与下一词：** 缓存里没有 token ID；`ud_annotations.json` 有 `form`、`upos`、`next_upos`（逐词，与 `passages.json` words 同索引）。**输入 token ID / 真实下一 token ID**：用同一分词器（`~/mechpop_cache/hf_olmo_dense/main`，OLMo）对段落文本重新分词，按 `capture_routing.word_token_index` 的同一规则定位：输入 token = `ids[pos−1]`，真实下一 token = `ids[pos]`（段末无下一 token 的锚点删去）。重算位置与缓存的有效锚点集逐一核对一致后才用。**输入词形 / 下一词形**：`passages.json` 中该词与同段下一个词的 `form` 小写（段末删去；多词 token 如 "don't" 的组成部分不在词表里，下一词因此可能跳过——记为已知小误差）。不需要回 conllu。
- **run 与 checkpoint：** 主分析 I0D0、I1D0、I2D0（只换初始化、同数据顺序），各 10 个 checkpoint：0 / 25M / 50M / 100M / 200M / 400M / 800M / 1.6B / 3.2B / 终点 3,999,793,152。重跑参照 I4D0 / I4D0R（0–3.2B，9 个）。其余 run（I3D0、I5D0、I0D1、I1D1）顺带算出存进 json，不进主图。warmup = 2000 步 × 262,144 = 5.24 亿 token，即 ≤ 4 亿的 checkpoint 都在 warmup 内。
- **脚本：** `scripts/e175_input_vs_next.py`（读数）、`scripts/e175_figure.py`（图）；结果 `results/e175/`。

## 读数（看到结果之前固定）
x 有 6 种：**in_tok**（输入 token ID）、**next_tok**（真实下一 token ID）、**in_form**、**next_form**（小写词形）、**in_upos**、**next_upos**。主读数用 token ID 版（与 OLMoE 定义一致），词形版作复核。所有读数在同一组锚点（有下一 token 的锚点）上算，每层、每 checkpoint、每 run。
- **读数 B（主，可预测性）：** e = top-1 专家（`S[:,0]`）。plug-in 互信息 I(e; x)（bit）。**地板** = 把 x 在锚点间随机打乱后的 plug-in 互信息，20 次打乱取均值（保持 x 与 e 的边缘分布，正好吃掉稀疏 x 的上偏）；**主量 = 超额互信息 ΔI = I − 地板均值**。**上限** = ΔI(e; in_tok ∧ next_tok)（二元组当一个 x）。另报 H(e)。
  - **增量信息（关键）：** 条件互信息 I(e; next_tok | in_tok) 与 I(e; in_tok | next_tok)，地板 = 在条件变量的每个值内部打乱另一个变量（20 次），同样取超额。含义：知道输入 token 之后，下一 token 还额外告诉了多少路由信息；反之亦然。
  - top-8 版（复核）：把 8 个槽都当作 (token, e) 样本（OLMoE 的 k=8），同样算 ΔI。
- **读数 A（OLMoE 式词表专精，复核）：** k=1 与 k=8。对每个 x 值，spec(E_i, x) = N^(k)_{x,E_i} / N^(k)_x。**专家值（我们的聚合）** = 路由到 E_i 的样本上 spec(E_i, x) 的样本加权平均 = Σ_x (N_{x,Ei}/N_{Ei})·(N_{x,Ei}/N_x)；**层值** = 64 个专家的平均（OLMoE 的层聚合）。只纳入在锚点集中 N_x ≥ 6 的 x（对两种 x 同一门槛，限制小样本上偏）；地板 = 打乱 x 后同一量（20 次均值），报原值与超额。
- **深层 / 浅层：** 深层 = L6–11，浅层 = L0–5（沿用 FINDINGS）；另单报 L11。
- **需前向，待定：** 预测下一 token（logit lens / 模型输出）版本——本卡不做。

## 对手假设与预测（写死）
- **H_in（OpenMoE）：** ΔI(e; in_tok) 从 warmup 起就高且此后平坦——定义为 **8 亿 token（warmup 结束后第一个 checkpoint）处的值 ≥ 3.2B 处值的 90%**；ΔI(e; next_tok) 在所有层、所有 checkpoint 都 < ΔI(e; in_tok)；增量 ΔI(e; next | in) 接近地板（< ΔI(e; in_tok) 的 10%）。
- **H_out（OLMoE）：** 深层的 ΔI(e; next_tok) 随训练上升（3.2B 值 > 1 亿值），且在 3.2B / 终点处 **≥ 或接近**（≥ 90%）ΔI(e; in_tok)；增量 ΔI(e; next | in) 在深层随训练上升。
- 两者不互斥（可浅层 H_in、深层 H_out）；按层判。

## 阳性对照与地板
- **阳性对照：** 未训练 checkpoint（step 0）第 0 层：路由 = 输入 embedding 的随机投影，ΔI(e; in_tok) 应明显 > 0、ΔI(e; next | in) ≈ 0——同时这就是"0 是什么"：**训练之前，输入 token 决定路由已经是默认状态**，所以"输入 token 互信息高"本身不是训练学到的。上限 ΔI(e; in∧next) 应 ≥ 两个单变量。
- **噪声地板：** 打乱地板（每个读数自带）；3 个 init seed 的范围；I4D0 vs I4D0R 之差作重跑参照。
- **MIE：** 交叉判定以 3 个 seed 都满足为准；next − in 的差小于 3 seed 极差时写"分不开"。不设通过线。

## 混杂审计
- **词频（高频词既是常见输入也是常见下一 token）：** 部分控制——(1) UPOS 版 x（17 类，无稀疏上偏）作对照；(2) 频率子集：只取输入 token 与下一 token 在锚点集中都出现 ≥ 20 次的锚点，两种 x 在**同一子集**上重算 ΔI；(3) 条件互信息本身扣掉了另一变量。
- **抽样不对称：** 锚点按输入词形每型 ≤ 40 抽样，输入分布被压平、下一 token 分布是自然长尾——H(x) 不同、稀疏度不同。打乱地板校正上偏，但不校正上限不同；故并报 ΔI / H(e) 与频率子集结果。绝对值不能与 OLMoE 的全 token 结果直接比。
- **只看词末 token：** 词中子词位置（下一 token 由词内决定，几乎确定）不在样本里，这对 next_tok 是保守的（去掉了最容易预测的情形），对 in_tok 也去掉了词内子词。未控制，记录。
- **下一 token 与输入 token 相关（如 "of the"）：** 由条件互信息处理。
- **专家编号跨 run 不对应：** 本卡所有读数都是单模型内的，跨 run 只比较数值，不需要配对。

## 决策表（跑之前写）
- **深层（L6–11 多数层，≥4/6）在 3 个 seed 上都出现 ΔI(next_tok) ≥ ΔI(in_tok) 的交叉，且交叉 checkpoint 在 seed 间相差 ≤ 1 个 checkpoint** → OLMoE 现象在我们的小模型里沿训练出现、有可定位的时点 → 报主会话：D1 的"何时、哪些层"有一条可画的曲线，值得继续（下一步是预测词版需前向、跨 seed 是否同一批 token 换边）。
- **无交叉，但深层 ΔI(next_tok)/ΔI(in_tok) 随训练单调上升、增量 ΔI(next | in) 明显高于地板** → 部分支持 H_out（方向在、没到交叉）；记录比值曲线与平台位置，报主会话。
- **无交叉、比值平坦、增量接近地板，且 8 亿处 in_tok 已达 3.2B 的 90%** → 支持 H_in；D1 的冲突在本设置下归于模型差异（OLMoE 规模 / 预测词 vs 真实词），报主会话，不继续追 D1 的训练轴。
- **3 个 seed 不一致（有的交叉有的不交叉，或交叉点相差 > 1 个 checkpoint）** → seed 依赖本身是一条信息；与重跑对差异并列报告。
- **token 版与词形 / UPOS 版结论不同** → 报告不同处，不选一个。
- 以上都不是关线条件。

- **算力预算：** 0 GPU；CPU 约 30 分钟。**实际：** 0 GPU；CPU 约 1.5 小时墙钟（NFS 慢、机器负载高；计算本身每 checkpoint 约 40 秒）。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

**数据核对：** 重新分词得到的有效锚点与缓存 `pairs.npz` 逐一相同（29,551）；段末无下一词 / 下一 token 的 80 个删去，用 29,471 个。输入 token 3,073 种（大小写、前导空格分开计，故多于 1,827 个词形），下一 token 4,998 种；H(in_tok) 10.9 bit，H(next_tok) 9.1 bit。

**一句话：** 所有 12 层、所有 checkpoint、3 个 init seed（加重跑对）上，路由专家与**输入 token** 的信息都高于与**真实下一 token** 的信息，**没有任何层出现交叉**（预注册 plug-in 读数、POST-HOC 交叉拟合读数、词形 / UPOS / 频率子集 / top-8 / OLMoE 式词表专精各版本一致）。但深层（L9–11）两者之比随训练持续上升、到 16 亿后走平；输入 token 信息在 2 亿 token（warmup 内）达峰后回落，下一 token 信息继续上升；"已知输入后下一 token 的增量"始终很小（≈ .07 bit）。

**主表（3 个 seed 均值 [最小, 最大]；bit；POST-HOC 交叉拟合估计；plug-in 预注册读数方向相同，见 `results/e175/e175_summary.json`）**

| 读数 | 层 | step 0 | 1 亿 | 2 亿 | 8 亿 | 32 亿 | 终点 |
|---|---|---|---|---|---|---|---|
| G(e; 输入 token) | L11 | −.01 | 1.62 [1.60, 1.64] | 1.64 [1.57, 1.68] | 1.43 [1.34, 1.50] | 1.41 [1.27, 1.49] | 1.42 [1.29, 1.50] |
| G(e; 下一 token) | L11 | −.09 | .50 [.49, .52] | .65 [.62, .70] | .70 [.68, .76] | .75 [.68, .81] | .76 [.70, .81] |
| 下一 ÷ 输入 | L11 | — | .31 | .40 | .49 | .53 [.51, .54] | .53 |
| 下一 ÷ 输入 | L6–11 均值 | — | .27 | .32 | .35 | .36 | .36 |
| 下一 ÷ 输入 | L0–5 均值 | — | .14 | .14 | .12 | .13 | .13 |
| G(e; 下一 \| 输入) | L11 | −.02 | .05 | .06 | .06 | .07 | .07 |
| G(e; 输入 \| 下一) | L11 | .06 | 1.17 | 1.05 | .79 | .73 [.65, .78] | .74 |
| G(e; 下一词 UPOS \| 输入 token) | L11 | −.11 | .08 | .10 | .09 | .10 | .10 |
| 下一词 UPOS ÷ 输入 UPOS | L11 | — | .50 | .64 | .75 | .81 [.77, .86] | .81 |
| 频率子集 下一 ÷ 输入（token） | L11 | — | .38 | .49 | .60 | .65 | .64 |

- **预注册 plug-in 读数（ΔI = I − 打乱地板）：** L11 32 亿处 ΔI(输入 token) 1.38 [1.28, 1.43]、ΔI(下一 token) .90 [.83, .96]，比值 .65；L6–11 均值 1.69 / .79（.48）。交叉：token / 词形 / UPOS / 频率子集四个版本、12 层 × 3 seed 全部"无"。H_in 的"平坦"判据（8 亿值 ÷ 32 亿值 ≥ .90）：12 层全部满足（.93–1.09）。H_in 的"增量 < 输入的 10%"：12 层全部满足（ΔI(下一 \| 输入) ÷ ΔI(输入) .003–.081，L11 最高）。H_out 的"深层下一 token 随训练上升（32 亿 > 1 亿）"：L0、L3–11 满足（L1、L2 不满足，下一 token 信息先升后降）；"终点 ≥ 输入的 90%"：任何层都不满足。
- **OLMoE 式词表专精（读数 A，k=1，N_x ≥ 6）：** L11 输入 .27 vs 下一 .15（打乱地板 .08 / .04）；k=8 同向。无交叉。
- **噪声：** 3 个 init seed 的范围在 L6–8 较窄（32 亿处 ≤ .07 bit），L9–11 较宽（输入 token .16–.27 bit），但不改变排序：任何层、任何 ≥ 2500 万的 checkpoint、任何 seed 上"输入 − 下一"的最小值都 ≥ .14 bit（L1），深层 ≥ .15。重跑对 I4D0 / I4D0R：L6–11 逐层差 ≤ .04 bit（输入）/ .03（下一）/ .004（增量），小于 seed 范围。
- **阳性对照：** 未训练模型第 0 层：G(输入 token) 2.30 bit，G(下一 \| 输入) .03——估计器能测到"按 token ID 路由"，且这在训练前就是默认状态（随机路由器 × 输入 embedding）。深层未训练 ≈ 0。
- **结果文件：** `results/e175/e175_summary.json`（3 seed 汇总 + 交叉点 + 重跑对，两种估计）、`e175_readouts.json`（预注册 plug-in，逐 run × checkpoint × 层）、`crossfit_<run>.json`（POST-HOC，9 个 run）、图 `e175_input_vs_next.png`（预注册）与 **`e175_crossfit.png`（主图）**；`e175_rows.json`（逐锚点 token ID，2 MB）留在本地不进 git，由 `scripts/e175_rows.py` 重建。
- **按决策表执行了什么：** 第一行（深层交叉）不成立。结果落在第二行与第三行之间：无交叉、增量小（第三行的条件"增量接近地板、8 亿处已达 90%"成立），但深层比值随训练单调上升到 16 亿后走平（第二行的条件"比值上升"也成立；"增量明显高于地板"只勉强成立：.07 bit，未训练 −.02）。3 个 seed 一致，不触发第四行。token 版与词形 / UPOS 版结论一致，不触发第五行。按表：报主会话，**不下方向性结论**。
- **主张变化：** 无（PILOT）。

**POST-HOC（看到预注册读数之后才加的，单独标注）：**
1. **预注册上限读数失效。** plug-in 的 ΔI(e; 输入∧下一) 在 L11 只有 .40 bit，**低于** ΔI(e; 输入) 1.43——稀疏 x（20,548 个二元组、多数只出现一次）的 plug-in 互信息与其打乱地板都饱和到 H(e) 附近，差值被压扁；打乱地板本身 1.9 bit，比多数信号大。预注册的条件互信息 ΔI(下一 \| 输入) 同样被压（这一项的数值只能当下界）。
2. **改用交叉拟合预测信息**（`scripts/e175_crossfit.py`）：一半锚点估 p(e|x)（向边缘分布平滑，A = 8，只试了这一个值），另一半算对数损失下降，交换取均值；二元组向输入 token 表回退。稀疏只会让估计变低、不会变高；打乱 x 的对照为负（输入 −.46、下一 −.28 bit），即两者都是保守下界，且对输入 token 的惩罚更重——**不利于输入 token 的偏差方向下，输入仍然更高**。条件量取 G(下一 \| 输入) = G(联合) − G(输入)、G(输入 \| 下一) = G(联合) − G(下一)。
3. **加了 G(e; 下一词 UPOS \| 输入 token)**（问"下一词的语法类在输入 token 之外是否还带路由信息"）：深层 .10–.13 bit，2 亿后平坦；浅层 L0 反而最高（.20）。L0 的原因未查。
4. **观察（解释不确定）：** 深层"下一 ÷ 输入"比值上升，不是因为增量 G(下一 \| 输入) 上升（.05 → .07），而是因为 G(输入 \| 下一) 下降（L11 1.17 → .73）而 G(下一) 上升：路由保留的输入 token 信息里，"与下一 token 无关的那部分"在 2 亿之后被丢掉、"与下一 token 共享的那部分"在增加。一种读法是深层专家把**预测相同后续的输入 token** 归到一起；这只是对分解的一种读法，没有单独检验。
5. 只看了词末 token、真实下一 token；OLMoE 的原话针对的是**预测**下一 token，那一版需前向，待定。

**这张图支持哪个对手、哪里不确定（≤ 15 行）：**
- 支持 H_in 的部分：输入 token 是各层、各阶段路由的主要决定因素；8 亿 token 时（warmup 刚结束）各层输入 token 信息已达 32 亿值的 93–109%；没有任何层交叉；知道输入之后，真实下一 token 只再给 ≈ .07 bit。OpenMoE 的"warmup 定下 token ID 路由"在我们的 run 上重现，且 3 个 seed + 重跑对一致。
- 支持 H_out 的部分：深层（L9–11，不是 L6–8）下一 token 信息在 warmup 之后继续上升，输入 token 信息在 2 亿后回落，比值 L11 从 .31 升到 .53（UPOS 版 .50 → .81），到 16 亿走平。方向与 OLMoE"later layers specialize more on output"一致，但幅度不到交叉。
- 不确定 1：OLMoE 的结论是关于**预测**下一 token；真实下一 token 未交叉不能否定那句话（需前向，待定）。
- 不确定 2：锚点是按输入词形每型 ≤ 40 抽的词末 token，不是自然 token 流；输入分布被压平。绝对值不能与 OLMoE 比，比值也可能受抽样影响。用 hidden 缓存（终点 + 未训练，113k 连续 token）可在终点处做自然流复核，CPU 可做。
- 不确定 3：估计器换过一次（POST-HOC），A 只试了 8；plug-in 与交叉拟合方向一致，但"增量 .07 bit"的绝对值依赖估计器。
- 不确定 4：比值上升发生在 1 亿–16 亿之间，主要在 warmup 末到 8 亿；我们的 checkpoint 在这一段只有 4 个点，"何时"只能粗定位到这一段。
- 不确定 5：观察 4（深层把预测相同后续的输入 token 归组）是对信息分解的一种读法，没有检验；若要追，是一个"同输入不同后续 / 不同输入同后续"的对比，CPU 可做。

## POST-HOC 补充 A / B（2026-11-06 后加；看到上面结果之后、应主会话要求才加，用来堵上面的"不确定 1 / 2"；不改预注册读数）
估计器与上文交叉拟合相同（2 折、种子 175、平滑 A = 8）。脚本：`scripts/e175_posthoc_ab.py`、`scripts/e175_predict_cpu.py`、`scripts/e175_posthoc_figure.py`；汇总 `results/e175/e175_posthoc_summary.json`、`posthoc_B.json`；图 `results/e175/e175_posthoc_AB.png`。

**B. 自然词流复核（做完）。** 用 hidden 缓存的 H_l、W_l、b_l 重算路由（top-1 = argmax(H W^T + b)），覆盖全部有效 UD 词的词末 token（112,262 个，有下一 token 的；不按词形抽样、不压平；输入 token 11,773 种、下一 token 11,238 种）。重算与路由缓存 S_l[:,0] 在锚点上的一致率：终点各层 .986–.999，未训练 .992–.997（差异来自 fp16 存储 vs bf16 采集）。终点，3 个 init seed（均值 [最小, 最大]，bit）：

| 层 | G(输入) | G(真实下一) | 下一 ÷ 输入 | 抽样版比值（上文） | G(下一 \| 输入) | 重跑对比值 I4D0 / I4D0R（32 亿） |
|---|---|---|---|---|---|---|
| L0 | 4.31 [4.24, 4.35] | .40 | .09 | .02 | .04 | .10 / .09 |
| L3 | 2.97 | .69 | .23 [.22, .25] | .17 | .06 | .24 / .24 |
| L6 | 2.47 | .72 | .29 [.28, .31] | .23 | .08 | .30 / .30 |
| L8 | 2.25 | .87 | .39 [.39, .39] | .31 | .09 | .37 / .36 |
| L9 | 2.09 | .93 | .44 [.42, .47] | .36 | .10 | .45 / .44 |
| L10 | 1.95 | 1.02 | .52 [.52, .52] | .46 | .10 | .56 / .57 |
| L11 | 1.74 [1.59, 1.85] | 1.05 [1.00, 1.11] | .60 [.59, .63] | .53 | .10 | .58 / .57 |
| L0–5 均值 | | | .19 | .13 | | |
| L6–11 均值 | | | .43 | .36 | | |

- 未训练（I0D0、I1D0 的 step 0）：L0 G(输入) 2.43 / 2.47，深层 ≈ 0；G(下一) 各层 −.02 到 −.15（估计器的稀疏惩罚，见上文 POST-HOC 2）。
- 结论（只对两条复核问题）："输入 > 下一"在自然词流上 12 层 × 3 seed 全部保持；深层比值在自然流上**略高**于抽样版（L11 .60 对 .53，L6–11 均值 .43 对 .36，每层高 .05–.08），即按词形压平的抽样略微低估了下一 token 的相对份额，但不改变"无交叉、L11 约 .5–.6"。只有终点与未训练两个时点（hidden 缓存只存了这两个），训练轴上的复核没有做。

**A. 预测下一 token——第一次尝试（全文，停掉）。** CPU 前向（flash-attn 在 CPU 上不可用，换成 PyTorch SDPA，数学等价）。空闲时测得约 130 token/秒（8 线程）；实跑时机器负载 30（其他用户），3 个进程各约 35 token/秒；全文 856 段约 22 万 token → **每个 checkpoint 约 1.75 小时**，"终点 + 2 亿"× 3 seed 约 3.5 小时墙钟，超过主会话给的 2 小时上限，按要求在第 50 段时停下，没有输出文件。可选：（一）只取锚点所在段的子集（如 200 段、约 5 万 token），每 checkpoint 约 25 分钟；（二）GPU 上同一脚本几分钟一个 checkpoint；（三）不做。主会话选（一）并再缩为只做终点。

**A（缩减版，2026-11-06 做完）：预测下一 token，终点 × 3 个 init seed，锚点段子集。** 从含缓存锚点的段里按种子 175 抽 200 段（4.1 万 token），保留这些段的全部有效词（34,456 个有下一 token 的词，输入 token 6,354 种、下一 token 6,085 种）；单进程 8 线程依次跑，每个 seed 约 5 分钟。预测 = 词末 token 位置的 argmax 下一 token。CPU fp32 前向的 top-1 路由与 GPU bf16 采集的 hidden 重算 top-1 一致率 .977–.999。top-1 预测与真实下一 token 一致率 **.327 [.326, .327]**（预测 token 3,738–3,770 种）。G 的单位 bit，3 个 seed 均值 [最小, 最大]：

| 层 | G(输入) | G(真实下一) | **G(预测下一)** | 预测 ÷ 输入 | 真实 ÷ 输入 | G(预测 \| 输入) | G(真实 \| 输入) | G(真实 \| 预测) |
|---|---|---|---|---|---|---|---|---|
| L0 | 3.79 | .31 | .65 | .17 | .08 | .08 | .05 | −.09 |
| L3 | 2.54 | .59 | 1.02 | .40 | .23 | .09 | .06 | −.05 |
| L6 | 2.09 | .60 | 1.04 | .50 [.47, .52] | .29 | .11 | .07 | −.04 |
| L8 | 1.88 | .72 | 1.23 | .65 [.65, .66] | .38 | .13 | .07 | −.02 |
| L9 | 1.75 | .76 | 1.29 | .74 [.70, .78] | .43 | .14 | .07 | −.02 |
| L10 | 1.65 | .85 | 1.40 | .85 [.84, .86] | .51 | .13 | .07 | −.02 |
| L11 | 1.47 [1.36, 1.58] | .87 [.82, .93] | **1.40 [1.34, 1.49]** | **.95 [.93, .99]** | .59 | .14 | .07 | −.02 |
| L0–5 均值 | | | | .33 | .18 | | | |
| L6–11 均值 | | | | .71 | .42 | | | |

- 预测下一 token 在每一层都比真实下一 token 带更多路由信息，且比值随深度单调上升；**L11 几乎追平输入 token（.95），但 3 个 seed 都仍略低（预测 − 输入最大 −.015 bit）**，即预测版也没有交叉，差距落在 seed 范围内。
- 知道输入之后，预测 token 再多给 .14 bit（L11），是真实下一 token 的 2 倍；知道预测 token 之后，真实下一 token 不再多给信息（下界 ≈ −.02，即 0）。由联合量推得：知道预测之后输入还多给的信息约 .21 bit（= 1.47 + .14 − 1.40），知道真实下一之后输入还多给约 .67 bit——深层路由在输入 token 之外的那部分，几乎都能用模型自己的预测解释。
- 和 OLMoE 原话的关系：OLMoE 说深层"specialize more on predicted output token IDs rather than input token IDs"。我们这里深层预测版追平而没有反超；方向一致、幅度在 4B token 的 12 层小模型上停在约 .95。真实下一 token 版（.59）与预测版（.95）的差距主要由预测准确率（.33）造成。
- 局限：只有终点（主会话决定不做 2 亿 / 8 亿）；200 段子集（不是全文）；pred 的 argmax 只取 top-1；G(预测 | 真实) 一列（向真实下一 token 回退）是弱下界（L11 .04），未列入表。

