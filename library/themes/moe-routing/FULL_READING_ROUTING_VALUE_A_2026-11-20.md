# 全文精读（路由价值 A）：学习路由何时胜过固定路由——Hash Layers 与 Clark Unified Scaling（2026-11-20）

**用途**：division 线的问题。我们自训的小 MoE（12 层、d768、64 专家 top-8、Dolma 800M token）里，冻结随机路由器（路由权重固定在初始化，只训练负载均衡 bias）的留出损失与学习路由器持平（3.519/3.531 vs 3.525/3.508）；但学习路由器的 token 分区部分跨 seed 可复现，冻结随机的不可复现。要回答的是：学习到的分工能复现，是因为任务需要它（那么可复现性应出现在学习路由胜过固定路由的地方），还是任务并不需要它。本文件收集两篇论文里"学习路由何时胜过固定（hash / 随机 / 冻结）路由"的证据，按专家数、模型规模、训练 token、层位置、top-k 分开整理。

**阅读方式**：PDF 用 `pdftotext -layout` 转成文本逐段读（正文、所有表格、图注、附录）；图里的数字把页面渲染成 PNG（110–300 dpi）后读取，标"≈图读"，误差约 ±0.01 loss / ±0.02 PPL；arXiv HTML 与 PDF 是同一版本（v3 / v2），逐句抽查一致。凡是我用论文给的系数自己算出来的数，标【自算】（脚本放在 scratchpad，没有进仓库）。

---

## 卡 1　Roller, Sukhbaatar, Szlam, Weston, "Hash Layers For Large Sparse Models"（NeurIPS 2021，arXiv 2106.04426）

**读的来源**：https://arxiv.org/pdf/2106.04426（v3，2021-07-20，16 页）；https://arxiv.org/html/2106.04426（v3，抽查与 PDF 一致）；NeurIPS camera-ready https://proceedings.neurips.cc/paper_files/paper/2021/file/92bf5e6240737e0326ea59846a83e076-Paper.pdf（12 页）与 Supplemental（3 页，等于 arXiv 附录 A–D）。camera-ready 与 v3 逐句比对：只有参考文献编号不同（多引了 product keys 和 hashing trick 两篇），**没有新增实验或数字**。
**读的范围（全文）**：Abstract；§1 Introduction；§2 Background；§3 Method（3.1 Hash Functions，含 Clustered / Dispersed；3.2 MultiHash）；§4 Related Work；§5.1 Tasks；§5.2 Experimental Setup（Seq2Seq / BASE Comparison）；§5.3.1–5.3.4；§6 Conclusion；表 1–9；图 1–4（图 2、图 3 渲染后读数）；附录 A（表 7–9）、B.1 / B.2 超参表、C 算力、D 社会影响。
**论文没给的**：图 3 只有图，没有数值（已读图）；Reddit 实验的总训练 token 数没报（只给 100k updates、batch 40、context 128 / label 128）；Switch 的容量因子和丢 token 策略没报；**全文没有 seed 重复，也没有误差条**；没有任何路由一致性或可复现性分析。

### 设置
- **主分析（pushshift.io Reddit）**：ParlAI encoder–decoder，2 个编码层 + 11 个解码层，d=1024，D=4096，16 头，稠密基线 222M。MoE **只替换一个解码层**的 FFN（默认第 7 层），**top-1**（Hash 和 Switch 都是每个 token 只走一个专家）。专家数 16 / 32 / 64 / 128（记作 1x16 … 1x128），另有 5x16（隔层放 5 个路由层，每层 16 个专家）。同参数稠密对照：Wider（D=6144，755M）、Deeper（22 层，755M）。100k updates，Adam，LR 0.002，InvSqrt，预热 10k 步。8×V100 约 20 小时（128 专家和大稠密模型用 16 卡）。
- **其他数据**：RoBERTa+cc100en（约 100B token，GPT-2 词表 51200）；Wikitext-103（标准词表 267k 与 BB 词表 8k 两种切分）；BST 下游微调。
- **BASE 比较（唯一的大尺寸）**：用 fairseq 的 BASE 代码，纯语言模型，25 层（24 个共享层），d=2048，D=8192；32 个专家，每个专家 = 3 个堆叠的 FFN，放在中间一层；总参数 4.5B（共享 1.31B，每专家 100.7M）。"3x Hash" 变体：3 个路由层均匀分布、每专家 1 个 FFN，总参数同为 4.5B。每 update 512k token，训练到 40k 步（≈20B token【自算】；超参表的 max steps 写的是 62,500）。只换路由方法，其余全同。32×V100 约 2 天。
- **比较的路由方法**：Balanced hash（按训练集频率贪心，把高频 token 放进最空的桶）；Fixed random hash；Token clustering（基线 Transformer 词嵌入做 k-means）；Dispersed hash（同一簇的 token 均匀分到各桶）；Position hash；Bigram；Previous token；Predicted future token（基线模型预测的下一词）；Oracle future token；5x16 下"每层同一 hash"与"每层不同 hash"；MultiHash（N 个 hash，各选一段宽 D/N 的 FFN 片段再拼接）；Switch（隐状态 softmax top-1 + load_bal，系数在验证集上调）；**Token Switch**（学习路由器，但输入换成当前 token 的查表嵌入）；BASE（线性分配）。
- **没有做的**：top-k>1 的学习路由；多个基座尺寸（Reddit 只有 222M 一个基座，BASE 比较只有 4.5B 一个尺寸）；多 seed。

### 学习路由 vs 固定路由：全部对比
PPL 为验证集（表 1 另有 test）。括号里是 ln(学习 PPL / Hash PPL)，即每 token 的 nats 差【自算】，**正值 = Hash 更好**。

| 设置（表 / 图） | 学习路由 | Hash | 差（nats） |
|---|---|---|---|
| Reddit 1x16，第 7 层（图 3 左、表 7） | Switch 24.00 | 24.01 | −0.000 |
| 1x32（表 5 / 7） | Switch 23.79 | 23.58 | +0.009 |
| 1x64（表 1） | Switch 23.65（test 23.73） | 23.16（23.23） | +0.021 |
| 1x128（表 1） | Switch 23.52（23.58） | 22.89（22.95） | +0.027 |
| 5x16，load_bal 0.1（表 1） | Switch **23.00**（22.93） | 23.21（23.27） | −0.009（Switch 更好） |
| 5x16，load_bal 0.01（表 1） | Switch 23.19（23.25） | 23.21 | −0.001 |
| RoBERTa+cc100en 1x64（表 2） | Switch 27.41 | 26.99 | +0.015 |
| Wikitext-103 1x16，标准词表 267k（表 4） | Switch **31.76** | 32.32 | −0.018（Switch 更好） |
| Wikitext-103 1x16，BB 词表 8k（表 4） | Switch 11.67 | 11.58 | +0.008 |
| Token Switch 1x64（表 6） | 23.43（test 23.43） | 23.16 | +0.012 |
| Token Switch 1x128（表 6） | 23.26（23.32） | 22.89 | +0.016 |
| 4.5B，BASE vs Hash（图 2 右，≈图读） | 10k 步 ≈14.1；20k ≈12.2；30k ≈11.55；40k ≈11.45 | ≈13.8；≈11.8；≈10.85；≈10.2 | ≈+0.02 → +0.03 → +0.06 → +0.12 |

- **相对稠密基线（24.90）的路由收益**【自算，nats】：E=16：Switch 0.037 / Hash 0.036；E=32：0.046 / 0.055；E=64：0.052 / 0.072；E=128：0.057 / 0.084。Switch 收益占 Hash 收益的比例：1.01、0.84、0.71、0.68。也就是说，在这个设置里专家越多，学习路由越落后于固定 hash。
- **Hash 层的位置**（图 3 右，只测了 Hash，1x64，≈图读）：第 1 层 ≈23.70，第 3 层 ≈23.42，第 5 层 ≈23.30，第 7 层 23.16，第 9 层 ≈23.21。原文："even the worst performing choice (layer 1) is still performing well compared to other baselines: as good as Switch Transformers using later layers in fact"。**学习路由在不同层的价值没有测。**
- **hash 函数比较**（表 3，1x64，valid / test）：balanced 23.16 / 23.23；fixed random 23.22 / 23.27；**token clustering 23.90 / 23.99**；dispersed 23.17 / 23.22；position 25.07 / 25.14（比稠密 24.90 还差）；bigram 24.19 / 24.28；previous token 24.16 / 24.22；predicted future token 25.02 / 25.09；oracle future token 1.97 / 1.97；5x16 每层同一 hash 23.74 / 23.81，每层不同 hash 23.21 / 23.27。
- **MultiHash**（表 5、7，参数不变）：1x16：Switch 24.00，Hash 24.01，hashes=2/4/8：23.88 / 23.73 / 23.83；1x32：Switch 23.79，Hash 23.58，hashes=2/4/8：23.48 / 23.38 / **23.28**。8 段固定 hash（32 专家）比 Switch 1x32 好 0.022 nats，比单个 hash 好 0.013 nats。
- **Switch 对负载均衡系数的依赖**（表 9，1x64）：load_bal 0 → 24.80（几乎等于稠密 24.90）；0.01 → 23.95；0.05 → 23.68；0.1 → 23.65；0.5 → 23.68。
- **同参数稠密模型**（表 1）：Wider 23.32，Deeper **22.72**——Deeper 比所有同参数 MoE 都好；作者的说法是稀疏模型的优势在同速度（同计算）下，而不是同参数下。
- **下游微调**（表 8，BST valid）：Baseline 14.21，Wider 12.48，Deeper 12.83，Switch 1x64 13.67（router 冻结 13.61），Hash 1x64 13.45；冻结稀疏部分基本无害，只调稀疏部分有害。

### 作者对"何时需要学习路由"的说法（原文）
- §5.3.1："for small numbers of modules Hash and Switch perform similarly, but the gap grows larger as the number of modules increases. For small numbers of modules, we hypothesize that learning to route, as Switch does, would be more important to be performant with those choices, but with larger numbers of modules many routing choices could work."
- 5x16："Given the results of Figure 3 (left), the small number of modules in this case may make performance close."
- 聚类："if the goal of conditional computation is to make fine distinctions, then those distinctions are more likely to appear between tokens within the same cluster, hence they should be in different hashes"；"learn-to-route methods such as Switch Transformers and BASE use simple functions of the hidden state to perform routing, which generally provide clustered expert modules [10], which could hence be a disadvantage for those methods."
- 隐状态作为路由输入："the hidden representations in layers of the Transformer, being biased towards the predictions of the model, may be suboptimal for routing."
- BASE："During early parts of training, Hash would presumably have an advantage in being able to specialize expert modules earlier, while BASE must learn membership for each of the expert modules. Later in training, BASE becomes mildly unstable presumably as expert assignments shift"。
- 结论："given that our routing approach is learning free, our results perhaps suggest that none of the current approaches are routing particularly well."

### 路由器学到了什么 / 可复现性
- 没有分析路由器本身。唯一涉及"学到的划分是什么形状"的是转引 BASE 论文（学习路由给出按聚类划分的专家），加上表 3 的间接证据：按词嵌入聚类的划分（23.90）明显差于随机（23.22），把同簇 token 分散开（23.17）就恢复。**在这个设置里，语义上成团的划分不仅不是必需的，还有害。**
- 没有 seed 重复，没有稳定性测量。与路由稳定性有关的只有 BASE "mildly unstable presumably as expert assignments shift" 这一句推测。

### 局限（作者自述）
- "While our experiments scale up to 4.5B parameters, we do not reach the scales of large industrial works such as [8]"。没有其他自述局限。

### 我的评估
1. **学习路由的代表偏弱**：主对比是单层、top-1 的 Switch 加辅助损失。表 9 显示 Switch 对 load_bal 很敏感，Clark B.2.1 也说 Switch 对 balancing 超参敏感、S-BASE 更稳。专家越多，每个专家每批分到的 token 越少，top-1 路由的梯度越稀疏、越难平衡。所以"差距随 E 变大"有一部分可能是 Switch 自身随 E 变差（Switch 从 64 到 128 只降 0.13 PPL，Hash 降 0.27），不一定说明"大 E 下不需要学习路由"。
2. **单 seed，没有噪声地板**：0.2–0.6 PPL 相当于 0.01–0.03 nats。参考 Clark 的 seed 散布（≤0.01 nats），1x16、1x32、5x16 的差都落在噪声量级内。
3. **只路由一层**：Clark D.4 恰好发现单个路由层时学习路由和 hash 没有差别。Roller 的大部分结论都出自这个学习路由最没有用武之地的配置。
4. **两个因素混在一起**：Hash 用 token id（无上下文），Switch 用隐状态（有上下文）。Token Switch 部分拆开了这两个因素：对 Switch 来说去掉上下文反而更好（+0.009 / +0.011 nats）；在相同的 token 输入下，学习路由（Token Switch 23.43）仍不如固定随机（23.16）。
5. **BASE 的 0.12 nats** 主要来自 BASE 在 20k 步之后进入平台、出现不稳定，不能当作"固定路由普遍更好"的幅度。
6. **算力匹配**：参数和 FLOPs 匹配（Hash 少一个路由矩阵：751,159,296 vs 751,224,896），updates 和 batch 相同。调参预算不对称：Switch 的 load_bal 在验证集上调过，Hash 没有超参。这种不对称偏向 Switch，但 Switch 仍然输。

### 与我们问题的关系
- **专家数**：top-1、单层设置下，学习路由的优势在 E=16 时为 0，E 越大越落后于 hash（ln 差从 0 到 +0.027）。这是"大 E 时学习路由变得不必要"的唯一直接证据，但混有 Switch 自身退化的因素。
- **模型规模**：没有数据（只有一个尺寸）。
- **层**：只测了 hash 的层位置（后层更好）。多层时（5x16）Switch 小胜 0.009 nats，与 Clark "多个路由层时学习路由才显出优势"方向一致。
- **训练长度**：BASE 曲线显示 hash 在训练早期就领先（10k 步 ≈+0.02 nats，约 5B token）。我们的 800M token 远早于这个点。
- **top-k**：没有 top-k>1 的学习路由对照。MultiHash（多段固定 hash，相当于细粒度、多激活的固定路由）进一步拉大了与学习路由的差距。我们的 64 选 8 更接近这种情形。
- **冻结随机的隐状态路由器**：这篇没有测。它的 "random" 是 token→专家的随机查表。最接近的两个条件：Position hash（不看内容，无收益，25.07）和 predicted-future-token hash（看基线模型的预测，25.02，不如基线）。由此看，路由需要依赖输入内容，但依赖方式不必是学出来的。
- **对"任务需要"假设的意义**：这篇说明任务对**具体用哪种划分**几乎不挑（random ≈ balanced ≈ dispersed，聚类反而差），这站在"学习路由分区的可复现性不是损失所需"一边。但它没有测分区可复现性，也没有多层、多 seed 的噪声地板。

---

## 卡 2　Clark, de las Casas, Guy, Mensch, et al., "Unified Scaling Laws for Routed Language Models"（ICML 2022，arXiv 2202.01169）

**读的来源**：https://arxiv.org/pdf/2202.01169（v2，2022-02-09，31 页；pdftotext 报一次 xref 错误后自动重建，31 页文本完整，页码连续）；https://arxiv.org/html/2202.01169（v2，抽查与 PDF 一致）。
**读的范围（全文）**：Abstract；§1（含 Key contributions）；§2（Language modelling / Scaling laws / 2.1 Routing Networks / Routed Transformers / Model size and inference cost / Training Details）；§3.1–3.3；§4.1–4.4；§5.1–5.3（含给实践者的 6 条建议）；§6 Related Work；§7 Conclusion；附录 A（架构、表 4、seed 方差图 7）；B（B.1 balancing loss；B.2 S-BASE；B.2.1 Sinkhorn；B.2.2 打乱；B.3 RL-R 三个变体、图 8、表 5；B.4 HASH、图 9）；C（C.1 expert parallelism；C.2 load balancing / capacity）；D（D.1 超参敏感性 图 10；D.2 routing frequency 图 11；D.3 routing policy 图 12；D.4 单层路由 图 13；D.5 K 图 14）；E（zero-shot，图 15–16、表 9）；F（F.1–F.3，图 17–18）；G（大规模，图 19）；H（表 6–8、图 20–26）。图 2、3、7、10、11、12、13、17 渲染后读数。
**论文没给的**：168 个模型的原始 loss 只有图，没有数值表（图读 ±0.01）。表 9 的 "Validation Set" 行（Eq. 7 系数）与表 7 略有出入（如 S-BASE b 0.088 vs −0.092），论文没有解释。

### 设置
- 仅解码器 Transformer（GPT-2 式，相对位置编码），SentencePiece 32k，MassiveText（Gopher 的数据，数万亿 token）；seq 2048 × batch 256 × 250k 步 = **130B token，所有尺寸都一样**；AdamW，cosine 衰减，1500 步预热到 2e-4；参数 bf16，路由器 softmax 用 fp32。
- 7 个尺寸（表 4）：15M（d512，6 层）、25M（512，8）、55M（640，10）、130M（896，12）、370M（1536，12）、870M（2048，16）、1.3B（2048，24）。主扫描用其中 6 个（不含 870M）× E∈{2,4,8,16,32,64,128,256,512} × 3 种方法，加上稠密基线，共 168 个模型。
- 路由：**每隔一层 FFN 路由（R=0.5），K=1**，专家是单个 FFW，容量因子 C=2（训练时溢出就丢 token，评估时不丢），每个设备放 4–8 个专家。
- 三种方法：**S-BASE**（线性路由器 + Sinkhorn 再平衡 + 跨 worker 打乱 + balancing loss，etol=1e-2）；**RL-R**（REINFORCE + 学习的 baseline + 负熵正则 + balancing，贪心 top-K；图 8 比较三个变体）；**HASH**（token id mod E，**不是** Roller 的 balanced hash）。图 9：E=64 时 modulo 溢出 5.0%（greedy 0.8%，random 7.2%）；E=512 时 21.5%（greedy 18.9%，random 23.4%）。
- 变体扫描：K∈{1,2,4} 与 R∈{0.25,0.5,1.0}，E∈{8,64,256}，N∈{15M,370M,870M}，**只做了 S-BASE**（图 5、24–26）。Routing frequency R∈{1/L,1/4,1/2,1}：S-BASE vs HASH，8/64/256 专家，55M/370M/870M（图 11），单层时放在倒数第二层。共享路由决策、按层置换的 hash：25M，64/256 专家（图 12）。单层路由：L−1 位置，55M/370M/870M，E∈{1,8,64,256}（图 13a）；L/2 处 3 个堆叠 FFW vs 3 个交错路由层，32 专家 1.3B（图 13b）。
- seed（附录 A、图 7）：130M，1 / 8 / 256 专家，三种方法各 3 个 seed，100k 步，分歧 "no more than 0.01"；脚注 2：作者把 0.02 当作显著性门槛。
- 额外实验：15M HASH，1/64/128/512 专家，训 75k / 250k / 1M 步（图 17）；RL-R 64 专家 7B（d4096、32 层、batch 1024、100k 步 ≈100B token）对比稠密 7B（图 19）。

### 拟合的标度律与系数
- Eq. (1)：log L = a log N + b log Ê + c log N log Ê + d（log 以 10 为底；L 是验证 NLL）。Ê 是饱和变换：Ê(1)=E_start，E→∞ 时 Ê→E_max。
- **表 3（Eq. 1 的解）**：

| | a | b | c | d | E_start | E_max |
|---|---|---|---|---|---|---|
| S-BASE | −0.082 | −0.108 | 0.009 | 1.104 | 1.847 | 314.478 |
| RL-R | −0.083 | −0.126 | 0.012 | 1.111 | 1.880 | 469.982 |
| HASH | −0.087 | −0.136 | 0.012 | 1.157 | 4.175 | 477.741 |

- **表 7（Eq. 7 的拟合，不带饱和项，表中符号已翻正）**：S-BASE a 0.079 / b 0.088 / c 0.007 / d 1.072；RL-R 0.080 / 0.105 / 0.010 / 1.076；HASH 0.081 / 0.097 / 0.009 / 1.086。
- **表 6（每个 N 单独拟合的专家斜率 b(N)，括号是留出 RMSE）**：

| | 15M | 25M | 130M | 370M | 1.3B |
|---|---|---|---|---|---|
| S-BASE | −0.035 | −0.031 | −0.029 | −0.024 | −0.019 |
| RL-R | −0.033 | −0.031 | −0.027 | −0.022 | −0.016 |
| HASH | −0.031 | −0.029 | −0.025 | −0.021 | −0.015 |

  在每个 N 上，S-BASE 的斜率都比 HASH 陡 0.002–0.004（log10 L 每十倍专家）。
- **表 8（a(E)，即 N 方向的斜率）**：E=4：0.077 / 0.075 / 0.077；E=64：0.066 / 0.063 / 0.066；E=512：0.060 / 0.053 / 0.056（S-BASE / RL-R / HASH）。专家越多，加大 N 的收益越小。
- **表 1（留一法 RMSLE）**：可分离形式 80–90e-4；双线性 57–60e-4；双线性 + 饱和 56–58e-4；每个 N 单独拟合（下界）19–46e-4。**表 2**：稠密 α_N 0.078（Kaplan 0.076）。
- **解释（§4.2，原文）**："when c is positive, the expert improvement slope b(N) reduces with model size N. All three routing techniques considered therefore predict diminishing improvements from routing when increasing scale. However, the scaling of S-BASE is predicted (and seen) to be substantially better." "A clear goal for future work in routing techniques should be to find a method with scaling coefficient c ≈ 0."
- **有效参数量（EPC，§5.1）**：N̄ 定义为损失与该路由模型相同的稠密模型大小（Eq. 11），所有稠密和路由模型在 N̄ 上落在同一条幂律上（图 1c）。例子（§4.3）："a model with N = 5M and E = 128 equals the performance of a model with N = 55M and E = 1"。【自算，Eq. 11 + 表 3】N=130M、E=64：S-BASE ≈572M，HASH ≈470M，RL-R ≈443M；N=1.3B、E=64：3.91B / 3.15B / 2.65B。
- **N_cutoff（§5.2）**：超过这个 N，路由就不再带来收益，log N_cutoff = −b/c。论文给出 S-BASE 937B、RL-R 85B、HASH 83B；"These values are highly dependent on the number of tokens seen, and N_cutoff is expected to increase with increased numbers of tokens"。附录 G："error in the second decimal place shifts predicted values by orders of magnitude"，RL-R 的 b 只要小 0.01，N_cutoff 就降到 9B；但 7B 的 RL-R 64 专家模型仍明显好于稠密 7B（图 19）。【自算】用表 3 四舍五入后的系数算 10^(−b/c)，得到 1.0T / 32B / 215B，仅舍入就让 RL-R 和 HASH 偏了 2–3 倍，**所以 N_cutoff 本身不稳健**。
- **§5.3 的比较结论（原文）**："S-BASE consistently outperforms RL-R and HASH, though RL-R is very competitive at smaller N." "All routing techniques suffer from reducing efficacy as N increases. Amongst the three techniques, S-BASE scales best: the fitted parameter c is lowest." "For small N, RL-R and S-BASE scale similarly with expert count and better than HASH." "HASH and RL-R maintain power-law behavior for longer than S-BASE (larger E_max). However they suffer from more interference (c)." "HASH has large initial overhead (bigger E_start), clearly visible as a more obvious curvature at small E."
- **建议**（§5.3）：N ≤ 1.3B 都应使用路由；S-BASE 作默认；E 取 64–128；K=1，0.5 ≤ R ≤ 1；"New routing techniques must be validated at multiple values of N and E when comparing with prior work. Results on single sizes cannot be extrapolated."

### 学习 vs 固定：由系数推出的差距【自算，Eq. 1 + 表 3】
各方法的拟合在 E=1 处给出的损失相差最多 0.017（拟合时没有强制稠密等价），所以这里比较的是**每种方法相对自己 E=1 的路由收益** L(1) − L(E)（nats），括号是 HASH 收益占 S-BASE 收益的比例。

| N | E=8：S-BASE / HASH | E=64 | E=512 |
|---|---|---|---|
| 15M | 0.206 / 0.149（72%） | 0.435 / 0.393（90%） | 0.584 / 0.585（100%） |
| 130M | 0.141 / 0.098（70%） | 0.299 / 0.260（87%） | 0.404 / 0.390（97%） |
| 1.3B | 0.088 / 0.056（64%） | 0.188 / 0.152（81%） | 0.255 / 0.229（90%） |

- 绝对差（S-BASE 收益 − HASH 收益）：15M 0.057 / 0.042 / −0.001；130M 0.043 / 0.039 / 0.014；1.3B 0.032 / 0.036 / 0.026（E=8 / 64 / 512）。
- 读法：学习路由多出的收益，绝对值在 E≈8–64 时最大（约 0.03–0.06 nats）；E=512 时 HASH 追上来，原因是 HASH 的 E_max 更大（478 vs 314），S-BASE 先饱和。**HASH 拿到的收益比例随 E 上升、随 N 下降。**只看每个 N 单独的纯幂律拟合（表 6）则是另一幅图：差距随 log E 线性变大，且基本与 N 无关。两种读法在 E≥256 处分歧，取决于饱和项拟合得准不准。
- 图 2(d) 的比较面板（≈图读）：15M、25M 时 HASH 曲线在 E≈512 附近碰到 S-BASE；370M、1.3B 时 HASH 一直在 S-BASE 上方。与上表一致。

### 直接从图读的学习 vs 固定差距（≈图读，loss 单位 nats）
- **图 10（55M，512 专家，R=0.5，训练过程）**：50k 步 HASH ≈2.76 vs S-BASE ≈2.72；100k ≈2.675 vs 2.63；250k ≈2.53 vs 2.48。**差距随训练从约 0.04 增大到约 0.05。**最好的 RL-R ≈ S-BASE，RL-R 的超参区间上沿到 ≈2.61。
- **图 11（routing frequency；格式：HASH − S-BASE，依次为 R=1/L、0.25、0.5、1.0）**：

| | 55M | 370M | 870M |
|---|---|---|---|
| 8 专家 | 0.01 / 0.03 / 0.05 / 0.09 | 0.01 / 0.02 / 0.045 / 0.085 | 0.00 / 0.015 / — / 0.085 |
| 64 专家 | 0.01 / 0.04 / 0.06 / 0.09 | 0.00 / 0.035 / 0.06 / 0.10 | 0.00 / 0.025 / — / 0.105 |
| 256 专家 | 0.01 / 0.03 / 0.055 / 0.08 | 0.00 / 0.025 / 0.055 / 0.09 | 0.00 / 0.025 / — / 0.085 |

  （870M 的 R=0.5 点图上没有。）规律：单个路由层时两者相同；路由层越多差距越大；**R=1 时差距约 0.08–0.10，在 8/64/256 专家、55M–870M 之间几乎不变。**差距大的主要原因是 HASH 从 R=0.25 到 R=1 基本不再变好，有时还变差（如 370M 64 专家：2.27 → 2.285；256 专家：2.21 → 2.235），而 S-BASE 一直在改进。原文："S-BASE scales well with routing frequency, but HASH degrades in performance … At a single routed layer, HASH has the lowest validation loss across model sizes."
- **图 12（25M，共享路由决策）**：64 专家，R=0.125 / 0.25 / 0.5 / 1.0：S-BASE ≈2.855 / 2.745 / 2.645 / 2.575；HASH ≈2.865 / 2.78 / 2.705 / 2.665；Shared S-BASE（在第一个路由层学习决策，之后各层沿用）≈2.86 / 2.755 / 2.69 / 2.66。256 专家：S-BASE ≈2.775 / 2.63 / 2.525 / 2.465；HASH ≈2.785 / 2.66 / 2.585 / 2.555；Shared ≈2.78 / 2.645 / 2.575 / 2.56。**共享决策的 S-BASE ≈ HASH。**按层置换的 hash（每层用不同的静态 token 置换）："performance was unchanged"（只有文字，没有图）。作者结论："methods which can adapt to each expert layer will outperform static policies."
- **图 13a（单层，放在 L−1）**：55M / 370M / 870M，E=1/8/64/256，S-BASE 与 HASH 的曲线重合（差 ≤0.01）。
- **图 13b（32 专家，1.3B）**：L/2 处单层、每专家 3 个 FFW：S-BASE ≈ HASH；3 个交错路由层："S-BASE performance is improved for interleaving"（≈图读，约 100k 步时低 0.02–0.03）；3x HASH 与单层 HASH 几乎相同。
- **图 17（只有 HASH，15M）**：专家斜率 b 在训练过程中越来越陡。75k 步那组结束时约 −0.026，250k 步那组结束时低于 −0.03。同一 token 数下，b 还取决于学习率调度走到了哪里（1M 步那组在相同 token 处只有约 −0.024）。原文："15M with no routing … training for 4x longer further reduces the validation loss by 0.05 … the same model with E = 512 gets a 0.07 reduction in loss from 4x more tokens."
- **K（图 5、14、25）**：只有 S-BASE。K 越大，每步损失越低，但 K=1 始终在 FLOP 帕累托前沿上。换成 (F, B) 变量后 K 和 R 几乎不改变标度律（R=0.25 略有偏离）。**没有 K>1 时的 HASH 对照。**

### 路由器学到了什么 / 稳定性
- 没有分析路由器内容：没有 token 聚类、专精，也没有跨 seed 的路由一致性。
- 与稳定性有关的只有三处：图 7 的 seed 间 loss 分歧 ≤0.01；B.2.2 的打乱步骤用来防止大模型通过再分配"side channel"让验证损失发散（作者明说是假设，没有证实）；D.1：RL-R 对超参高度敏感，S-BASE 对 balancing weight 在 1e-3 到 1 之间鲁棒，不加 balancing loss 也有竞争力但训练不稳。

### 局限（作者自述）
- 所有数值只在 130B token 下成立（§5、附录 F）；"convergence is not a proper criteria"；标度系数还取决于学习率调度的位置，不只取决于 token 数（F.2）。
- N_cutoff 对 b 极其敏感（附录 G）；受算力所限，没有扫更大的 E 和 N。
- 每个配置只有一个 seed（附录 A）。
- R=1/L 和 R=0.25 偏离拟合（D.4，作者归因于第一个路由层表现欠佳）。
- 下游任务的系数各不相同，单一验证集代表不了（附录 E，表 9：例如 N=110M、E=32 时，验证集上的 EPC 是 370M，LAMBADA 上 284M，Pile 上 535M）。

### 我的评估
1. **不全是"学习 vs 不学习"**：HASH 用 token id mod E，C=2 时 E=512 约有 21.5% 的 token 溢出（按边际频率模拟），训练时被丢掉；S-BASE 有 Sinkhorn 再平衡。差距中有一部分来自负载平衡而不是学习。（Roller 在单层设置里发现 random ≈ balanced，但他的丢 token 机制和这里不同。）
2. **HASH 的所有路由层用的是同一个 token 划分**。D.3 说按层置换也不变；但 Roller 表 3 的 5x16 中，"每层同一 hash"比"每层不同 hash"差 0.023 nats。两篇在这点上不一致，配置也不同。
3. **算力匹配**：N、token 数、步数相同；S-BASE 每步多 1–3% 开销（B.2.1），没有计入。RL-R 和 S-BASE 调过参（表 5、图 10），HASH 没有超参可调。
4. **关键混杂**：S-BASE 的路由输入是隐状态（含上下文），HASH 是 token id。论文没有"固定但依赖隐状态"的对照（例如冻结的随机线性路由器）。所以多层时 S-BASE 的优势，分不清来自"学习"还是来自"每层按上下文路由"。Shared S-BASE ≈ HASH 只能说明优势需要每层各自做决策，仍然没有把学习和上下文依赖分开。
5. **单 seed + 0.02 门槛**：单层、R=1/L、小 E 的许多 S-BASE vs HASH 单点差距都落在这个门槛以内。
6. **外推很脆**："N 越大，学习路由的相对优势越大"建立在 c_HASH − c_S-BASE = 0.003 这么小的差上，只能算弱证据。

### 与我们问题的关系
- **专家数**（K=1，R=0.5，130B token）：学习路由多出的收益，绝对值在 E≈8–64 时最大（约 0.03–0.06 nats），按饱和拟合在 512 时缩小。HASH 拿到的收益比例：E=8 时 64–72%，E=64 时 81–90%，E=512 时 90–100%。**学习的相对价值随 E 下降。**在 R=1 时则看不到这种下降（图 11：8/64/256 专家的差距都约 0.08–0.10）。
- **模型规模**：所有方法的路由收益都随 N 缩小；HASH 缩得更快（c 更大），所以学习路由占的收益份额随 N 上升；绝对差距大致不变（E=64、15M–1.3B 之间约 0.036–0.042）。
- **层**：学习路由的优势几乎全部来自"有多个路由层、每层独立决策"。单层约为 0；共享决策约为 0；R=1 时最大（约 0.08–0.10）。
- **训练长度**：差距随训练变大（图 10：50k → 250k 步，约 26B → 130B token，差距 0.04 → 0.05）；HASH 自身的专家收益也随 token 增长。我们的 800M token 约等于 Clark 的 1.5k 步，**和他们的预热长度差不多**。文献里没有这个训练长度下学习 vs 固定的数据点。
- **top-k**：K 只扫了 S-BASE，没有 K>1 的 HASH 对照。
- **冻结随机的隐状态路由器**：Clark 没有这个条件。我们的 FRZ（每层一个不同的随机线性投影、依赖隐状态、只学 bias）正好落在 Clark 没覆盖的格子里：它和 S-BASE 一样"每层不同、依赖上下文"，又和 HASH 一样"不学习"。如果在长训练和 R=1 下 FRZ 仍 ≈ 学习路由，那么 Clark D.3 的结论"能按层自适应的方法胜过静态策略"就该改写为"依赖每层隐状态的路由胜过按 token 的静态路由，不需要学习"。两篇论文都没有回答这个问题。

---

## 两篇合起来看：学习路由何时胜过固定路由

1. **随专家数**：两篇里，学习路由在固定路由之上多出的收益份额都**随 E 缩小**。Roller（top-1 单层 Switch）只有 E=16 时 Switch ≈ Hash，E 越大 Hash 越领先；Clark（K=1，R=0.5）中 HASH 拿到的份额从 E=8 的约 2/3 升到 E=512 的 90–100%。绝对差：Clark 在 E=8–64 时约 0.03–0.06 nats，E=512 时约 0–0.03。例外是 Clark 的 R=1：差距约 0.08–0.10，基本与 E 无关。
2. **随模型规模**：只有 Clark 有数据。绝对差距大致不变；相对份额随 N 上升（弱证据，依赖 Δc=0.003）。Roller 只有单一尺寸。
3. **在哪里起作用**：在有多个路由层、每层独立路由的模型里。R=1 时差距最大（130B token 下约 0.1 nats）；单个路由层（无论放在 L−1 还是 L/2）差距为 0；各层共享第一层的决策也为 0。Roller 的层位置实验只测了 hash（后层更好）。
4. **随训练长度**：差距随训练变大（Clark 图 10）。小于约 10B token 时没有学习 vs 固定的数据，只有 Roller 的 BASE 曲线早期段（Hash 领先 ≈0.02 nats）。
5. **top-k>1**：两篇都没有学习 vs 固定的数据。最接近的是 Roller 的 MultiHash：多段固定路由比 Switch top-1 更好。
6. **路由器学到什么、可复现性**：两篇都没有测。Roller 表 3 表明语义成团的划分对损失有害、随机划分就够了；Clark 只报告了 seed 间 loss 分歧 ≤0.01。

### 对我们问题的含义
- **我们的零结果和文献相容**：FRZ 与学习路由的平均差约 0.0085 nats，在 seed 散布以内。我们的条件（800M token，12 层 d768 大致相当于 Clark 的 130M 档（d896、12 层；激活参数量未核对），64 专家）正是文献预期差距最小的区间：训练极短；E=64 时固定路由在 K=1 下已能拿到约 87% 的收益。**但文献不支持"学习路由普遍不必要"**：Clark 在 R=1、130B token 时有约 0.1 nats 的清楚差距。
- **一个可以检验的反向关系**：我们自训模型的分区可复现度随专家数上升（16 / 64 / 256 专家：.13 / ≈.5 / .81），而文献显示，学习路由相对固定路由的价值随 E **下降**（R=0.5 时）。如果在我们自己的设置里，FRZ 与学习路由的损失差距也随 E 缩小（需要 16 和 256 专家下 FRZ vs 学习路由的损失；我没有核对现有运行里是否有这些数），那么可复现性就不是跟着"任务需要"走的，支持"任务不需要"这一边。跨设置推断有三个保留：K=1 vs top-8；token hash vs 隐状态随机路由器；130B vs 800M token。
- **文献指向的、能打开学习 vs 固定差距的两个轴**：路由层的数量（每层独立路由）和训练长度。专家数和规模的效应更弱，而且方向依赖设置。（这里只记录文献指向什么，不是提议新训练；按目前的约定，不新开训练。）
- **两篇都没有覆盖、正好是我们 FRZ 条件能回答的问题**：在多层路由中，学习路由胜过 token hash 的那部分优势，来自"学习"还是来自"每层依赖隐状态"？

### 不确定 / 未核对
- Roller 的 Reddit 总 token 数、Switch 的容量因子：论文没报。
- 所有"≈图读"的数，误差 ±0.01 loss / ±0.02 PPL；图 11 中 870M 的 R=0.5 点图上没有。
- 【自算】的差距和 EPC 用的是表 3 四舍五入后的系数；N_cutoff 与论文不一致，正是这个原因。
- Clark 表 7 与表 9 "Validation Set" 行的系数出入，论文没有解释。
- Clark 只用文字报告了"按层置换的 hash 无变化"，没有给出配置和数字。
