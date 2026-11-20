# 全文精读 B（路由价值）：冻结 / 随机 / 稳定路由与路由器–专家共同特化的四篇（2026-11-20）

服务的问题（division 11-20，不是主线）：自训小 MoE（12 层，d768，64 专家 top-8，Dolma，800M token）里，**冻结随机路由器**（权重固定在初始化，只训练平衡偏置）在 held-out loss 上追平学到的路由器；学到的路由器分区跨种子部分可复现；完全重跑（只差 GPU 非确定性）在前 ~50M token 内丢掉一半深层分区一致度后进入平台；跨种子共享分区在 ~25M token 时像体裁 / 位置，50M 时下降，之后出现按词性组织的共享分区。要问：(a) 学到的路由何时、为何胜过固定 / 随机路由；(b) 路由器与专家怎样共同特化（自组织 / 富者愈富）；(c) 已知的路由波动与早期定型。

**阅读方式**：四篇都从 arXiv 下载 PDF（`https://arxiv.org/pdf/<id>`），`pdftotext -layout` 转文本逐节读；所有表格从文本读；正文没有数字的图，把 PDF 页面渲染成图片目读，读出的值标"≈（读图）"，误差约为坐标轴最小刻度的一半。四个 arXiv 编号与题目都核对无误。2605.12476 读的是 v2（2026-11-11，NeurIPS 2026 camera-ready），并对照了 v1（2026-05-12）的改动。

---

## 一句话结论

- **Fan, Messmer & Jaggi（2402.13089）**：GPT-2 small 每层 MoE，但**只有 4 个专家、top-2**，单种子，约 6B token。冻结在初始化的路由器 vs 学到的路由器：token 级 9.810 vs 9.907（多语 Wiki），22.687 vs 22.632（OpenWebText），差距 ≤1%。"Random"是**每步重新随机初始化**路由器（没有稳定的分区），差了约 19%（11.752 / 26.879），和激活参数量相同的稠密基线一样差，甚至更差。作者对"冻结 ≈ 学到"的解释是"embedding layers adapt to a frozen router head"，也就是表征去迁就固定的路由器。他们只在 4 专家的条件下测过，在 64 专家 top-8 下没有证据。
- **StableMoE（2204.08396，ACL 2022）**：唯一给出路由波动数字的一篇：BASE Layer（32 专家 top-1，单个 MoE 层）有 40.9% 的验证 token 在训练进行到 20% 之后还换目标专家，29.1% 在 50% 之后还换，15.4% 在 80% 之后还换。方法分两段：前 10% 训练（约 3B token）把路由蒸馏到**只看词 ID 的词嵌入路由器**，然后冻结。结果 19.28，好于 Hash 19.63、Switch 19.79、BASE 20.04。**固定的随机词哈希（Hash）在 16 / 32 / 64 专家下都胜过学到但一直波动的 BASE**；StableMoE 相对 Hash 的优势随专家数从约 0.4 缩到约 0.15 ppl（读图）。把 BASE 的路由在 6K 步时冻结就降 0.63 ppl。被冻结的路由器把 token 按词性 / 词汇类别分给专家（附录 Table 9）。
- **THOR（2110.04260，ICLR 2022）**："gating ≈ 随机路由"的证据**全部来自 2 专家**的低资源 MT：门控平均置信度收敛到约 0.55–0.60，Switch(t) / Switch(s) / Switch(r) 的 BLEU 都约 33。THOR 的随机是**每个 batch 随机选一对专家，整个 batch 共用**，根本不形成 token 分区，靠一致性正则（双向 KL）让专家互为老师。消融显示：去掉正则后随机路由是 20.6–20.8 BLEU，和学到的 Switch 一样（20.6）；THOR 的 +1.8 BLEU 来自正则，不来自"随机"。它对数据充足的 LM 预训练和多专家分区几乎没有信息。
- **Routers Learn the Geometry of Their Experts（2605.12476，NeurIPS 2026）**：要点是一个梯度恒等式。对某个 token，被选专家的路由行 r_i 与该专家输入侧的行（W_up 的行，W_gate 同理）的梯度都 ∝ x，只差标量系数；所以二者累加的是同一段被路由 token 的历史，作者称为"geometric coupling"。经验证据：(1) 在三个公开 MoE 上，路由分数与被选专家的预激活范数单调相关；(2) 自训 1B loss-free 模型上这一相关在第一个检查点（约 2.4B token）就从 0 升到约 0.32，峰值约 0.42，之后回落到约 0.37（读图）；(3) 辅助均衡损失让路由行彼此的平均余弦从 0.13–0.32 升到 0.57–0.63；(4) 没有可学参数的 EMA 质心（K-Means）路由器只比学到的 loss-free 路由差 2.6% 训练 PPL，负载更均衡。**没有冻结随机路由器的基线，没有多种子，没有跨种子分区测量**。

---

## 合并回答 (a)(b)(c) 与 (i)(ii)(iii)

**(a) 学到的路由何时胜过固定 / 随机路由（四篇的数字放在一起）**

| 比较 | 设定 | 差距 | 出处 |
|---|---|---|---|
| 冻结在初始化 vs 学到 | GPT-2 small，N=4，top-2，约 6B token | token 级：−0.097 ppl（多语），+0.055 ppl（OWT），即 ≤1% | Fan Table 3 |
| 每步重新随机 vs 学到 | 同上 | +1.85 / +4.25 ppl（约 +19%） | Fan Table 3 |
| 固定随机词哈希 vs 学到的 BASE | 1 个 MoE 层，32 专家 top-1，约 31B token | Hash **好** 0.41 ppl（19.63 vs 20.04） | StableMoE Table 2 |
| 学到后冻结（词 ID 路由）vs Hash | 同上，N=16/32/64 | 学到后冻结好约 0.4 / 0.35 / 0.15 ppl（读图 / 表） | StableMoE Fig. 5、Table 2 |
| BASE 学到 + 在 10% 处冻结 vs 一直学 | 同上 | 冻结好 0.63 ppl | StableMoE Table 5 |
| 随机（每 batch，无正则）vs 学到的 Switch | 低资源 MT，2 专家 | 20.6–20.8 vs 20.6 BLEU（Cs-En） | THOR Table 1、4 |
| 推理时去掉训练好的门控（随机派发） | 同上 | 20.6 → 20.4 BLEU | THOR §5.5、Fig. 8 |
| 不可学的 EMA 质心 vs 学到的 loss-free | 1B，64 专家 top-6 + 2 共享，50B token | 质心差 +2.6% 训练 PPL（15.40 vs 15.01），C4 21.01 vs 20.40 | 2605.12476 Table 1 |

我从这张表读出的规律（这是推断，不是哪篇论文的结论）：在这些规模上，**token→专家映射是否稳定比它是否"学到"更重要**。不稳定的映射（每步重抽的随机路由、一直波动的 BASE）明显吃亏；固定的映射，不论随机的（Hash、冻结路由器）还是学到后冻结的（StableMoE），都至少不差。学到的内容本身只值约 0.1–0.4 ppl 或约 2–3%，而且随专家数上升而缩小（StableMoE Fig. 5）。我们在 64 专家 top-8 下看到冻结随机路由器 ≈ 学到的，与这个规律一致。区别在于：我们的冻结路由器作用在**上下文隐状态**上，不是词 ID 上，所以上游表征可以把 token "搬"到想去的专家（Fan 的解释）。这四篇都没有在多专家、多层、上下文路由的条件下测过冻结随机路由器，所以对我们的数字来说，它们是近邻，不是先例。

**(b) 共同特化的机制**
- 2605.12476 是唯一给出机制账的一篇：每个路由行和匹配专家的输入行只累加被选给该专家的 x（前提是归一化发生在 top-K 掩码之后，见卡 4 的批评）。被选中 → 两边都往 x 方向移 → 下次相似 token 分数更高、专家预激活更强，这是一个自强化的聚类过程；EMA 质心路由器把它显式写成在线 k-means。论文**没有**用"富者愈富"这个词，也没有讨论它推出的多解性 / 初值依赖性。
- 由它可以推出（我的推断，论文没说）：同样的梯度结构在**冻结**路由器下仍然成立于专家一侧。专家输入行累加的是被固定方向 r_i 选中的 x，被选中的 x 在 r_i 上的投影平均为正，所以专家行在统计上也会向 r_i 对齐，耦合可以只由"选择"产生，不需要路由器学习。若成立，2605.12476 的 Fig. 2 式相关在我们的冻结随机模型里也会出现，"耦合"就不能当作路由器学到东西的证据。这是一个便宜的诊断，见文末。
- Fan 与 StableMoE 的另一半机制：表征去迁就路由（Fan），路由退化为词 ID 的函数也不吃亏（StableMoE 的词嵌入路由器胜过 1–3 层 Transformer 路由器，Table 6）。

**(c) 波动与早期定型**
- StableMoE 只在 BASE Layer 上测"最后一次换专家的步"（相对最终步，每 500 步测一次），结果是大量 token 一直在换（数字见上）。但同一篇显示，在 10% 训练（约 3B token）时蒸馏并冻结的路由，比继续学到 25% / 50% 再冻结**更好**（19.28 / 19.34 / 19.41），即有用的路由结构很早就到位，后面的波动是单 token 层面的抖动。
- 2605.12476 Fig. 6：路由–专家相关在第一个检查点（约 1k 步 ≈ 2.4B token）已到约 0.32，在 5k–10k 步（约 12–24B token）达峰后回落；OLMoE 公开检查点上 gate 相关在 20k 步达峰后下降（Fig. 5）。时间分辨率比我们的 25–50M 窗口粗约两个数量级。
- THOR Fig. 3（MoE(tok)，2 专家，batch 64k token）：门控置信度约在 1000 步（≈64M token）升到约 0.9 的峰，到约 4000 步（≈256M token）落回约 0.52；MoE(dec) 约 200 步（≈13M token）内塌缩到一个专家。这是唯一与我们 25–50M 窗口量级相当的早期瞬态，但模型、任务、专家数都差太远，只能当弱类比。
- Fan Fig. 1 / 6（序列级，无均衡损失）：各专家负载在前约 200–500 步（≤0.5B token）分叉，部分层在 3000–4500 步（约 3–4.5B token）再分叉（"Experts exhibit the ability to recover from collapsing"）。这里测的是负载，不是分区。

**(i) 跨种子分区可复现、(ii) 路由价值与可复现性的联系、(iii) 早期定型窗口：四篇都没有直接预测。**
- (i) 四篇都**没有任何多种子实验**（Fan 明说因算力只跑单种子；StableMoE、THOR、2605.12476 都未报种子方差）。最接近的是 Fan Fig. 4：在 MMLU 六个类别上，学到的与冻结的路由给出"similar routing results"，比较的是**路由方式**之间（不是种子之间）的粗粒度类别直方图，而且只有 4 个专家。2605.12476 的在线 k-means 解读推出：分区是数据几何上的 k-means 不动点，强簇（对应强数据模式）应可复现，簇内切分依赖初值（这是我的推断）。这与 Kawata et al. 理论（见同日精读 B 卡 3）的结构一致。
- (ii) 没有任何一篇把"路由学到多少"与"分区多可复现"放在一起。StableMoE Table 9 显示，被冻结的词 ID 路由按**词性 / 词汇类别**分专家（物主代词 + 时间单位、介词 + 宾格、标点、数词、形容词、代词、连词、后缀），外加几个话题名词簇（科技、政治、日常）。这与我们晚期出现的按词性组织的共享分区方向一致，但这只是"学到的路由收敛到什么"的单种子快照。
- (iii) 只有 StableMoE（10% 就够）与 2605.12476（第一个检查点就耦合）间接支持"有用结构早出现"；没有一篇测量完全重跑之间的分歧何时产生、何时停止增长。我们"完全重跑在前 ~50M token 丢一半一致度后进入平台"的测量在这四篇里没有对应物。

---

## 卡 1　Fan, Messmer, Jaggi — Towards an empirical understanding of MoE design choices（arXiv 2402.13089v1，2024-02-20；EPFL；4 页正文 + 附录，像 workshop 短文，录用情况未核对）

**读取**：https://arxiv.org/pdf/2402.13089 。**全文已读**：§1 Introduction；§2 Related Works；§3 Experiments（3.1、3.1.1、3.1.2、3.2.1、3.2.2）；§4 Conclusion；附录 A.1 Experimental Details、A.2 On Router Choices、A.3 Expert Assignments、A.4 Layer-wise Expert Activation；Table 1–3；Fig. 1–8 全部渲染目读。

**设置**
- nanoGPT（LoRA 扩展版）上的 GPT-2 small（124M，12 层，d768），**每个 Transformer 块的 FFN 都换成 MoE**；路由器是 MLP（1 层或 2 层，A.2 / Fig. 3：两者验证曲线无差别）。
- **专家数 N=4**（Table 1 / 3 的所有实验）；Table 3 的 learned 数值（10.666 / 9.907）与 Table 1 的 top-2 行一致，因此 Table 3 是 top-2。Top-1 不设容量上限。可选均衡损失 λ=0.01；Table 3 的各行是否开了均衡损失，原文**未写**。
- 数据：多语 Wikipedia（英 / 德 / 法 / 意，17B token）与 OpenWebText（9B token）；GPT-2 tokenizer。
- 训练：6K 步，每步 1,048,576 token（≈6B token），lr 9.6e-4 → 9.6e-5，dropout 0.2，weight decay 0.5；单张 A100-40GB。**单种子**，报最后 100 步的平均（§3："to address the inability to conduct multiple runs with different seeds"）。
- 路由单位：token 级 vs 序列级；layer-wise（每层一个路由器）vs global（只在第一块路由，后面各层照抄）。

**比较的路由方式（§3.2.1）**
- Learned；**Frozen**：路由参数冻结在初始化（"conceptual similarity with hash routing. However, the routing result is embedding dependent instead of token id dependent"）；**Random**：路由参数"re-initialized randomly at each iteration"，即每步一个新随机路由器，没有跨步稳定的分区；Language：按语言硬编码（只在 global 序列级）。

**结果（Table 3，验证 PPL）**

| 数据 | 层级 | 方式 | 序列级 | token 级 |
|---|---|---|---|---|
| 多语 | Global | Language | 11.716 | – |
| 多语 | Global | Learned | 11.605 | – |
| 多语 | Layer-wise | Frozen | 10.601 | 9.810 |
| 多语 | Layer-wise | Random | 11.685 | 11.752 |
| 多语 | Layer-wise | Learned | 10.666 | 9.907 |
| OWT | Layer-wise | Frozen | 24.590 | 22.687 |
| OWT | Layer-wise | Random | 26.429 | 26.879 |
| OWT | Layer-wise | Learned | 24.980 | 22.632 |

- 冻结 − 学到：多语 token −0.097（冻结略好），序列 −0.065；OWT token +0.055，序列 −0.39。都在单种子噪声可能覆盖的范围内，作者没有给噪声地板。
- 每步随机 − 学到：token 级 +1.85（多语，+19%）、+4.25（OWT，+19%）。对照 Table 1 的稠密基线：1× FFN（124M）11.815 / 26.195，2× FFN（182M，与 top-2 激活参数相同）10.831 / 24.387。每步随机路由比激活参数相同的稠密模型差，大约只和 1× 稠密持平。
- Table 1（N=4）：只有 token 级 layer-wise top-2（9.907 / 22.632）追平总参数相同的 4× 稠密（10.071 / 22.700）。作者："the routing unit has the biggest impact"。
- Table 2（多语）：token 级更受益于 N：(2,2) 10.761 → (4,2) 9.907 → (6,2) 9.467；序列级更受益于 K：(4,1) 11.573 → (4,2) 10.667 → (4,3) 10.107。

**专家特化（§3.2.2、A.3）**
- 测法：在 MMLU 六类（global facts、abstract algebra、medical genetics、management、college biology、college chemistry）与 XNLI / X-stance 四种语言上，画第 0 / 5 / 11 层各专家的分配频率直方图（Fig. 2、4、5）。只是目视比较，没有统计量。
- 序列级：弱的话题特化（"weak expert specialization in topics"），分配与语言无关；中间层出现"一个公共专家 + 弱特化专家"（A.3，作者联系到 DeepSeekMoE 的共享专家）。
- token 级（Fig. 5 左）：话题上几乎均匀，"does not bring any expert specialization in topic domains"；语言上不均匀，作者归因于分词差异。
- **Fig. 4（OWT，序列级 top-2）：learned / frozen / random 三种路由在 MMLU 上的分配图，"Frozen routing and learned routing gave similar routing results"**，random 近似均匀。
- 全文没有 token 级词性 / 句法分析。

**动态（§3.1.1、A.4、Fig. 1 / 6–8）**：无均衡损失时早层与晚层更易塌缩，但验证 PPL 几乎不变（10.674 vs 10.667）；负载在前约 200–500 步分叉（读图），部分层在约 3000–4500 步再分叉，"Experts exhibit the ability to recover from collapsing"。

**作者陈述的局限**："our findings may not generalize to larger Language Model scales due to computing constraints"；单种子。

**我的评估**
- N=4 / top-2 时每层只有 6 种组合，路由器能学的东西很少，"冻结 ≈ 学到"在这里几乎是预期结果。它不能外推到 64 专家 top-8（每层约 4.4×10⁹ 种组合）。
- "Random"不是固定随机路由器，而是每步重抽，它测的是"没有稳定映射"的代价，不是"没学"的代价。这恰好分开了两个变量：Frozen ≈ Learned，而 Random ≫ 两者。
- 结论里的"achieving expert specialization during MoE training is attainable by simply initializing router weights randomly"只有直方图式证据支持。
- 作者把"冻结 ≈ 学到"与 Dikkala et al.（EMNLP 2023）联系起来，那篇我**未读**，不判断。

**与我们的关系**：这是"冻结路由器 ≈ 学到的路由器"最直接的前人结果，但只在 4 专家、单种子、无噪声地板的条件下。我们的增量（若成立）：64 专家 top-8、多层、有种子方差、有分区层面的测量。它的 Frozen / Random 二分可以作为我们冻结随机 vs 每步重抽对照的先例。

---

## 卡 2　Dai, Dong, Ma, Zheng, Sui, Chang, Wei — StableMoE: Stable Routing Strategy for Mixture of Experts（arXiv 2204.08396v1，ACL 2022 long）

**读取**：https://arxiv.org/pdf/2204.08396 。**全文已读**：Abstract；§1 Introduction（含 Fig. 1–2）；§2 Background；§3 Method（3.1–3.4）；§4 Experiments（4.1 Tasks、4.2 Setup、4.3.1 LM、4.3.2 MT、4.4.1 超参效应、4.4.2 固定路由效应、4.4.3 蒸馏路由器变体、4.4.4 波动分析）；§5 Related Work；§6 Conclusion；附录 A（Table 7）、B（Table 8）、C（Table 9）。Fig. 4、5、6、7 渲染目读。

**设置**
- LM：RoBERTa 语料 + CC100 英文（约 100B token），GPT-2 BPE。Base：12 层，d768，FFN 3072，**一个 MoE 层**插在中间块之后，**32 专家**，每个专家是 3 个堆叠的 FFN 子层（BASE Layer 式），top-1；60K 步 × 512K token ≈ 31B token（stage 1 为 6K 步 ≈ 3.1B token）。Large：24 层，d1024，64 专家，每专家 6 个子层。
- MT：WMT 10 语对 + 1.8 亿回译，32 专家，2 个 MoE 层（编码器第 3 块后、解码器第 3 块后），352K 步（stage 1 30K 步）。
- 方法：Stage 1 用贪心 top-1 + sigmoid 门 + 平衡损失（α=0.3）学路由，同时用交叉熵把路由蒸馏到"词嵌入 + 50 维质心"的轻量路由器（多 2.51M 参数）；Stage 2 冻结这个路由器，路由只看**词 ID**（D(X_t) 是词嵌入，与上下文无关），门值仍用原始分数 σ(s_{t,a_t}) 学习。
- **未报种子数与方差**。

**路由波动（§1 Fig. 2、§4.4.4 Fig. 7）**
- 测法：BASE Layer 训练中每 500 步记录验证集 token 的目标专家；"last fluctuation step" = 目标专家最后一次与最终步不同的步。
- 结果：40.9% 的 token 在 20% 训练后仍有波动；29.1% 在 50% 后；15.4% 在 80% 后。StableMoE 的 stage 2 为 0%（按构造）。
- 局限：只测 BASE（平衡线性指派，指派依赖整个 batch，天然更易波动）；只是单次运行内相对最终步的累积量，不区分"少数边界 token 一直抖"和"大块分区在移动"；没有 Switch 的对应数字；验证时 BASE 用什么指派规则没写。

**结果**
- Table 2（valid / test PPL）：Base：稠密 124M 23.02 / 22.58；更深 578M 17.93 / 17.63；更宽 578M 18.31 / 18.01；Switch 19.79 / 19.20；BASE 20.04 / 19.69；**Hash 19.63 / 19.25**；StableMoE 19.28 / 18.93。Large：稠密 18.86 / 18.19；Switch 16.62 / 16.21；BASE 16.36 / 15.75；Hash 16.37 / 15.79；StableMoE 16.22 / 15.59。
- Fig. 5（Base，专家数）≈（读图）：N=16：BASE 20.7，Hash 20.3，StableMoE 19.9；N=32：20.04 / 19.63 / 19.28；N=64：BASE 19.3，Hash 19.0，StableMoE 18.85。三种 N 下固定随机 Hash 都好于学到的 BASE；学到后冻结相对 Hash 的优势随 N 缩小。
- Table 5：BASE + 在 6K 步蒸馏并冻结 20.04 → 19.41（−0.63）；StableMoE 只有 stage 1 时 19.48，加 stage 2 后 19.28（−0.20）。
- Table 6：stage 1 长度 6K（10%）19.28，15K（25%）19.34，30K（50%）19.41；15K 时蒸馏路由器：词嵌入 19.34，CNN 19.39，1 层 Transformer 19.42，2 层 19.38，3 层 19.65。上下文更多的路由器并不更好。
- Table 4：MoE 层位置：顶 19.55，中 19.28，底 22.82，分散 20.56。Fig. 6：3 → 10 子层（454M → 1.51B 专家参数）各法都变好。
- Table 3（MT，X→En 平均 BLEU）：稠密 28.31，更大稠密 29.10，Switch 29.70，BASE 30.16，Hash 29.94，StableMoE 30.32。

**专家特化（附录 C、Table 9）**：冻结的路由下，验证集各专家最常见的 token：专家 5 物主代词 + 时间单位，6 介词 + 宾格，11 连词 + 标点，12 数词，13 科技名词，17 政治名词，22 形容词，27 日常名词，29 后缀，30 代词，31 连词。只列"有代表性的"专家，没有量化指标。

**作者陈述的局限**：基本没有；只在 §4.4.3 说 32 类蒸馏信号可能不足以训练复杂路由器。

**我的评估**
- 结论"稳定性带来增益"的直接证据是 Table 5（−0.63 / −0.20 ppl），单种子、无误差棒。
- 更重要的副产品是：路由退化为词 ID 的函数后反而更好，且固定随机哈希胜过学到但一直波动的 BASE。这说明在 32–64 专家、单个 MoE 层的设定下，**上下文路由的增量价值没有被证明**。
- 只有一个 MoE 层（每 token 一次路由），与多层 MoE 的层间组合不同。

**与我们的关系**：(a) 提供"稳定 > 学到"的旁证和"学到的价值随 N 缩小"的读图证据；(c) 提供唯一的波动数字，但是在 BASE 上、相对最终步、单次运行内测的，和我们"完全重跑之间的分歧"不是同一个量；(ii) Table 9 的词性 / 词类专家与我们晚期词性组织的共享分区方向一致。我们可以借用它的"last fluctuation step"作为单次运行内的稳定性读数，与跨重跑一致度并列报告。

---

## 卡 3　Zuo, Liu, Jiao, Kim, Hassan, Zhang, Zhao, Gao — Taming Sparsely Activated Transformer with Stochastic Experts（THOR；arXiv 2110.04260v3，ICLR 2022）

**读取**：https://arxiv.org/pdf/2110.04260 （v3，2022-02-03）。**全文已读**：Abstract；§1；§2 Background；§3 Analysis of SAMs（Fig. 1–4）；§4 THOR（Eq. 3，Fig. 5）；§5 Experiments（5.1–5.5，Table 1–5，Fig. 6–9）；§6；附录 A（A.1 训练细节、A.2 Fig. 10–13）、B（Table 6–7）、C（C.1–C.3）、D（Fig. 14，Table 8）。Fig. 1–4、7–9、14 渲染目读。

**"门控 ≈ 随机"的分析（§3、附录 A）**
- 设定：IWSLT De-En + Vi-En 多语翻译，batch 64k token，**专家数全部为 2**。模型：MoE(dec)、MoE(tok)（Shen et al. 2019 的混合模型，EM 训练），Switch(t)（token 级）、Switch(s)（句级）、Switch(r)（"routed randomly"，是每步随机还是固定哈希**原文未写**）。
- Fig. 1（读图）：Transformer / MoE(dec) / MoE(tok) 验证 loss ≈3.97 / 3.97 / 3.93，BLEU 都约 33。Fig. 4：Transformer 与 Switch(s)/(t)/(r) 的 loss ≈3.97–3.98，BLEU ≈32.8–33.0。
- Fig. 2：MoE(dec) 约 200 步后塌缩到专家 2（负载 → 1.0，置信度 → 1.0）。Fig. 3：MoE(tok) 置信度约 1000 步时达峰（≈0.9），约 4000 步后回到 ≈0.52，负载均衡；作者称之为"random routing"。
- 附录 A.2：Switch(s) / Switch(t) 无均衡损失时置信度收敛到 ≈0.60 / ≈0.55，负载 55% / 45%；加均衡损失后不均衡 <0.4% / <0.2%，置信度不变。作者结论："behavior of the gating mechanism is still random routing"。

**THOR 方法**：每层每个 batch 随机抽一对专家，整个 batch 都用这对；两次前向，loss = CE(p1) + CE(p2) + α·½(KL(p1‖p2) + KL(p2‖p1))；推理时随机派发（句级 / token 级）或集成。

**结果**
- Table 1（低资源 12 任务，2 专家）：Switch 平均 26.3 = Transformer 26.3；THOR 在全部 12 个任务上比 Switch 高 >1 BLEU（例：Vi-En 33.0 vs 29.5，Cs-En 22.4 vs 20.6）。
- Table 2（WMT，4 专家，Transformer-big）：En-De 30.4，En-Fr 43.8（BLEU）。Table 3（多语 10 语对，4 专家，300M）：Switch 22.4 → THOR 24.4，等于 Switch 32E / 5.5B 的 24.4。
- **Table 4（Cs-En 消融）**：CE1+CE2+CR 22.4；CE1+CR 22.2；CE1+CE2 20.8；CE1 20.6。对照 Table 1：Switch 20.6，Transformer 20.4。**去掉一致性正则后，随机路由 = 学到的门控。**
- Table 5：Dispatch(s) 22.4，Dispatch(t) 22.4，Ensemble 22.6。§5.5 / Fig. 8：推理时去掉 Switch 的训练门控 20.6 → 20.4；20 次随机推理的方差 THOR <0.002，Switch 0.008。
- Fig. 9（De-En）≈（读图）：THOR 2E → 8E 约 37.8 → 38.1；同参数量的宽 FFN Transformer 约 35.8 → 35.5（过拟合）。
- 附录 D Fig. 14（WMT16 En-De，小模型 48M；2 / 16 / 64 专家 = 55M / 143M / 456M）≈（读图）：Switch BLEU 25.1 / 25.4 / 25.5，Transformer 25.2，THOR 25.7 / 26.1 / 26.2；Switch 的训练 PPL 随专家数明显下降。

**作者陈述的局限**：只做 NMT；承认视觉上有相反结论（Riquelme et al. 2021），归因于"image classification ... belongs to a clearly-defined category"。

**我的评估**
- "门控不比随机好"的证据只在 2 专家、低资源条件下成立；平均最大置信度约 0.55 只说明门控分数差小，**不说明** argmax 指派是随机的（小差距下的 argmax 仍可能确定且依赖输入）。作者没有测指派的一致性。
- THOR 的增益来自双前向 + 一致性正则（类似 R-drop / 集成）；每 batch 共用专家 → 专家之间没有数据分工，被正则拉成近似副本。这是正则化论文，不是路由论文。
- 无训练种子方差，BLEU 差距无置信区间。
- 唯一有多专家的比较（附录 D）里没有"随机路由但不加正则"的一档，无法分离路由与正则。

**与我们的关系**：基本不预测 (i)–(iii)。可借鉴的一点：Fig. 3 的门控偏好在约 64M token 内先升后落，这是与我们 25–50M 窗口量级相当的早期瞬态，但模型、任务、专家数差太远，只能作为弱类比，不能引用为证据。"学到的路由 ≈ 随机"在文献中经常被引用，但它出自 2 专家 MT 的设定，与 64 专家 LM 预训练不可比；我们引用时要写清楚。

---

## 卡 4　Ahrac, Hochwald, Geva — Routers Learn the Geometry of Their Experts: Geometric Coupling in Sparse Mixture-of-Experts（arXiv 2605.12476v2，NeurIPS 2026 camera-ready，2026-11-11；Tel Aviv University）

**读取**：https://arxiv.org/pdf/2605.12476 （v2）；对照 https://arxiv.org/pdf/2605.12476v1 （2026-05-12）。**全文已读**：Abstract；§1；§2 SMoE architecture and training（Eq. 1–6）；§3 Router–expert geometric coupling（Eq. 7–8）；§4 Empirical evidence（Fig. 2，router-direction removal 段）；§5 Auxiliary load-balancing breaks coupling（Eq. 9–10，Fig. 3）；§6 Centroid tracking（Eq. 11–12，Table 1，Fig. 4，Discussion，"Where the perplexity gap comes from"）；§7 Related work；§8 Conclusion + Limitations；附录 A（A.1 符号表 Table 2、A.2 专家梯度、A.3 路由梯度、A.4 共享结构、A.5 AdamW）、B Resources、C（含 C.1 与 Table 3）、D（D.1 Fig. 5，D.2 Fig. 6）、E（Table 4）；NeurIPS checklist。Fig. 2–6 渲染目读。代码库（github.com/sagearc/router-expert-geometry）**未看**。

**理论主张（§3、附录 A）**
- 对路由到专家 i 的 token x：W_up 第 k 行的梯度 ∂L/∂u_k = δ_{i,k} x^T，其中 δ_{i,k} = ((W_down)^T p_i L_y)_k · g_{i,k}（Eq. 17）；路由行 ∂L/∂r_i = γ_i x，其中 γ_i = L_y^T E_i(x) · ∂p_i/∂z_i（Eq. 19）。二者方向相同，标量不同（A.4）。W_gate 的行也有 δx^T 的形式（Eq. 7），只是系数含激活导数。
- 未被选中的专家 p_j = 0，r_j 不从该 token 得到 LM 梯度，于是"each router weight vector therefore accumulates only the tokens routed to its expert"（§3）。
- 辅助均衡损失（Eq. 9）用的是**未掩码**的 softmax，所以对每个 token、每个专家 j 都有 ∇_{r_j} L_balance = β_j x（Eq. 10），即 Wang et al. 所说的"interference gradients"。隐状态不居中 → 所有路由行累积共同的均值分量 → 彼此靠拢。
- A.5 的让步："Shared input histories therefore motivate geometric coupling under AdamW without guaranteeing aligned router and expert weights."

**经验证据**
- §4 / Fig. 2（OLMoE 7B，DeepSeek-V4-Flash 284B，Qwen3-30B-A3B-Base；1,000 个 Wikipedia 标题的末 token，标题由 AI 辅助挑选、5 个领域各 200 个；分数与范数在每层 × 专家内标准化后分 8 个分位箱）：被选的 token–专家对中，路由分数越高，‖W_gate x‖ 与 ‖W_up x‖ 越大。OLMoE 中位数从约 −0.5 SD 升到约 +0.6 SD（读图）；DeepSeek、Qwen 斜率较小、低分段较平。
- 附录 C.1 / Table 3（被选减未被选的标准化预激活差，按层平均）：OLMoE gate +0.471 / up +0.292（16/16、16/16 层为正）；Qwen +0.166 / −0.014（48/48、13/48）；DeepSeek +0.008 / +0.281（22/40、39/40）。作者："higher preactivation norms among selected experts depend on the model, projection, and layer"。
- 附录 E / Table 4（OLMoE，在一层把被选专家输入中沿路由方向的分量去掉，选择与权重保持不变；对照为 32 个与路由方向正交、由 gate / up 权重导出的方向；176 条序列 × 512 个预测）：15/16 层路由方向的 ΔNLL 大于对照中位数，比值 1.6–54×。例：第 14 层 0.128 vs 0.0057（排名 1/33）；第 12 层 0.089 vs 0.0016；第 13 层 −0.0017 vs 0.0014（排名 33/33）；第 15 层 0.178 vs 0.112（1.6×）。
- 附录 D.1 / Fig. 5（OLMoE 11 个公开检查点，5k–1.22M 步）≈（读图）：gate 相关 0.35（5k）→ 峰值约 0.47（20k）→ 0.33（1.22M）；up 相关约 0.43（5k）→ 约 0.28（终点）。达峰后单调下降，作者没有解释为何下降。
- 附录 D.2 / Fig. 6（自训 loss-free 1B，6 个检查点 0 → 39.75k 步；末 token、1,024 个标题；平均 post-SiLU gate 激活）≈（读图）：routed 0.02（初始）→ 0.32（约 1k 步）→ 0.41（5k）→ 0.42（10k）→ 0.38（20k）→ 0.37（39.75k）；non-routed 从 0 缓升到约 0.17；置换配对对照约 1k 步时 0.15，之后降到约 0.05。v1 正文对这个模型报的是 ρ = 0.43，p = 1.2×10⁻⁸¹。
- §5 / Fig. 3（两个 1B，同初始化、同 token 数，只差均衡规则；Wang et al. 配置：9 个 SMoE 层，d=1024，64 路由专家 top-6，2 个共享专家，专家宽 512；OLMoE-mix-0924，约 50B token）：路由行两两余弦的非对角均值，辅助损失 + z-loss 为 0.63 / 0.63 / 0.57（第 0 / 4 / 8 层），仅偏置均衡为 0.32 / 0.18 / 0.13。
- §6 / Table 1（21k 步，2.36M token/步 ≈ 50B token；AdamW β=(0.9, 0.95)，lr 1e-3 → 1e-4，warmup 1k）：

| 方法 | 路由参数 | 训练 PPL | C4-en | Pile | MaxVio |
|---|---|---|---|---|---|
| Aux-Loss（load + z） | 0.59M | 15.09 | 20.54 | 11.82 | 0.526 |
| Loss-Free + Seq-Aux | 0.59M | 15.03 | 20.44 | 11.77 | 0.102 |
| Loss-Free | 0.59M | 15.01 | 20.40 | 11.76 | 0.084 |
| K-Means（EMA 质心，α=0.99，偏置 γ=1e-3） | 0 | 15.40 | 21.01 | 12.09 | 0.037 |

- PPL 差距来自哪里（§6，6.9M 个 held-out token）：最稀有的 10% 目标 token 上 NLL 差 +0.061，最常见的 token 上消失；层平均第 6 / 7 名分数间隔最窄的十分位 +0.044 vs 最宽 +0.016（2.7×）；按各自的间隔分箱，学到的路由器窄–宽差只有 +0.005，K-Means 为 +0.027。

**作者陈述的局限（§8）**：路由方法比较只在一个 1B 配置上做；均衡损失的分析只覆盖路由几何的一个方面；K-Means 是"a constructive test of the coupling view rather than a practical router"，它的 PPL 差距说明"learned routers use degrees of freedom beyond centroid position"。

**我的批评**
1. **"未选中专家不得梯度"依赖归一化顺序。** Eq. 1 把掩码放在非线性之前（先 top-K 掩码再 softmax / sigmoid）。若先对全部 N 个专家做 softmax 再取 top-K 且不重新归一化（据我所知 OLMoE 是这种做法，本文未核对），被选专家的 p_i 依赖所有 z_j，未选中的 r_j 每个 token 也会通过归一化项得到 ∝ x 的 LM 梯度。论文在 OLMoE 上做主要分析，却没讨论这一点。
2. **耦合不是路由学习独有的。** 专家一侧的 δx^T 累积只需要"被选中"。路由器冻结时，被固定方向 r_i 选中的 x 在 r_i 上投影偏正，专家行同样会向 r_i 统计对齐。论文**没有冻结 / 随机路由器对照**，所以 Fig. 2 / Table 3 的相关不能区分"路由器学到了专家的几何"与"专家学到了路由器的几何"。标题的因果方向（Routers learn ...）没有被检验。
3. **单种子、无误差棒。** checklist 把分位箱的 IQR 当作误差棒；Table 1 中 Loss-Free 与 Loss-Free + Seq-Aux 相差 0.02 PPL，K-Means 的 2.6% 差距是否超过种子噪声未知。
4. **内部不一致**：§6 说训练 21k 步（50B token），附录 D.2 说 loss-free 模型跟踪到 40k 步（"about 93.8 billion training tokens"）；摘要与引言仍写"In a 1B SMoE trained from scratch, higher router scores predict stronger expert neuron preactivations"，但 v2 的 §4 已改用三个公开模型，自训模型的证据只剩附录 D.2（v1 正文是自训模型）。Fig. 4 放大图里两个 loss-free 曲线在 21k 步约为 0.10，与表中 0.084 / 0.102 有出入（滚动均值 vs 最后一步，未说明）。
5. 预激活 L2 范数与路由分数可能共享 token 范数、频率等因素；按层 × 专家标准化去不掉 token 层面的共同因素。non-routed 相关从 0 升到约 0.17（Fig. 6），说明有一部分相关与"被谁路由"无关，作者没有讨论。
6. K-Means 的质心是未居中隐状态的均值，按余弦路由时可能被共同均值方向主导（与 §5 他们自己指出的"hidden states ... not centered"同一问题），PPL 代价有一部分可能来自这里而不是"失去学习自由度"，论文未分离。

**与我们的关系**
- (a)：它的 K-Means 是"方向会移动但不学"的路由器，代价 +2.6%；我们的冻结随机路由器是"方向固定、只学偏置"，在小模型上没有代价。这组对比本身值得记下：要么规模 / 训练长度改变结论，要么余弦打分（丢掉范数信息）才是 K-Means 的代价来源。不确定，未核对。
- (b)：提供了共同特化的梯度级机制与"在线 k-means"的读法；由 k-means 不动点可以推出分区依赖初值、强簇可复现，但这是我的推断，论文没有讨论种子。
- (c)：耦合在第一个检查点（约 2.4B token）就已建立，在 OLMoE 上 20k 步后下降。分辨率比我们的窗口粗约 100 倍，不能回答前 50M token 的事。
- 认领风险：它占有"路由行与专家输入行共享梯度方向 → 共同累积"这一表述，以及"辅助损失让路由行趋同（约 3×）"这个测量。它**没有**占有冻结 / 随机路由器、跨种子、分区可复现性、早期动态中的任何一项。

---

## 可做的便宜诊断（建议，不是决定；用我们已有的 checkpoint，不需要新训练）

1. **冻结随机模型上的耦合**：在冻结随机与学到的路由模型上，用 2605.12476 Fig. 2 / Table 3 的读数（路由分数 vs 被选专家的 ‖W_gate x‖、‖W_up x‖，被选减未被选的差，置换配对对照）。若冻结模型的相关与学到的一样强，"耦合"就是选择的产物，可以作为对 2605.12476 因果方向的直接补充。
2. **路由行几何**：学到的路由器各层路由行两两余弦的非对角均值（2605.12476 Fig. 3 的读数）。冻结随机路由器的这个值在初始化时约为 0（d768 下随机向量余弦 ≈ ±0.04），可以作为参照。还要核对我们学到的路由用的是辅助损失还是偏置，这决定该比哪一行。
3. **单次运行内的波动**：在已有检查点序列上算 StableMoE 式的"last fluctuation step"累积曲线，与"完全重跑之间的一致度"并列，区分"单 token 抖动"与"分区层面的分歧"。
4. **词 ID 可解释度**：每层分区里有多少可以由词 ID 单独预测（StableMoE 的词嵌入路由器就是这个读法），并分别对学到的与冻结的路由器计算。这可以和"跨种子共享分区按词性组织"的观察对接。

## 下一步该读（本次未读，不作判断）
- Roller et al. 2021, Hash Layers（NeurIPS 2021）：固定随机词哈希与学到路由的原始比较，StableMoE 复现了它。
- Dikkala et al. 2023, On the benefits of learning to route in MoE models（EMNLP 2023）：Fan 引用它支持"冻结 ≈ 学到"，2605.12476 引用它讨论聚类数据下的路由–专家对应。两种引法不一致，需要读全文。
- Wang et al. 2024, Auxiliary-loss-free load balancing（2408.15664）：我们的偏置均衡与 2605.12476 的 1B 配置都来自它。
- Lv et al. ICLR 2026, Coupling experts and routers via an auxiliary loss：库里已有 `ERC_FULL_READING_2026-10-29.md`，可与卡 4 对照。
