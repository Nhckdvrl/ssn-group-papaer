# I04：In-context learners index evidence by output——看得见“用哪些输出”的变化，看不见“输出重新分配给输入”的变化

- **状态：** 主 idea（2026-10-06 人决定）；暂停推进，留作之后主推的 candidate。机制证据为 L2（2 个 Qwen 模型，相关 + 因果修补）。
- **来源（必填；优先高质量来源但不是白名单）：** 稳定测量异常——exact Bayes oracle 的方向相反检验在分类式 ICL 上 13 个模型方向都错（E02a、E16）；逐个排除竞争解释后收敛（见 §2、§5）。
- **研究动作：** 定位 + 分解测量 + 引入成熟构念（virtual vs real drift；outcome density vs contingency；main effect vs interaction）+ 建设性预测（E32）+ 机制（E36–E38）。
- **工作标题（英文）：** *In-Context Learners Index Evidence by Output: Why LLMs Detect Output Drift but Miss Concept Drift*

## 1. 一句话
冻结 LLM 在上下文里把输入-输出证据**按输出标签存放**：某个输出得到多少支持，来自带这个输出的 demo 的、按输入相似度加权的汇总——这份汇总在**时间**和**上下文**（例如标注者）上是可交换的。因此，改变“用哪些输出”的漂移（标签流、格式、输出语言、换了新词的新 regime）被追踪，而把**已有输出重新分配给不同输入**的漂移（concept drift、因人而异的映射）被混在一起；混合程度随新旧输出标签的语义相似度单调增加。

## 2. 从哪里来
稳定异常：exact Bayes oracle 预测“前缀里零散的反例会让模型**更不**相信后缀的变化”，而所有分类式 ICL 的方向都相反（E02a 起，13 个模型）。随后用实验逐个排除竞争解释（见 §5），剩下唯一一致的描述是本卡。概念来源：数据流学习中的 virtual vs real drift（Gama et al. 2014）、联想学习中的 outcome density vs contingency、统计中的 main effect vs interaction、样例分类模型（Nosofsky GCM）。

## 3. 主张（两层）
**行为层**
1. **输出侧变化被追踪**：标签流、输出格式、输出语言、作用于全部输入的变换（±k、大小写↔反转）的变化，方向与 exact Bayes 一致（噪声检验为负）——13/13 模型（标签流），格式通道 16/16（E22），规模越大越强（32B）。
2. **条件结构被可交换地汇总**：类别→标签的映射变化在 13 个模型、0.6B–32B、自然语言、K=4/6 多类、任务切换、thinking（2 万 token）、指令、时间戳、输入侧标注者标签下都没有规范的变化推断；预测由“query 像哪一半 demo”决定、与新旧无关（E21，32B 仍对称）；变化后旧证据不被重置（E26）。
3. **证据按输出身份分开**：能分开关联证据的只有输出身份与（部分地）输入内容——分隔阶梯：不同输出词 0.00 ≪ 不同输入领域 0.42–0.49 < 显式上下文标签 0.51–0.91 < 时间（完全合并）（E31/E35/E30/E21）。泄漏与两套标签词的语义相似度相关 ρ=0.75–0.96（E33，5 模型）。
4. **建设性预测成立**：新 regime 换成新输出词后，concept drift 被规范追踪（E32，6 模型 11/12 格，含 1.7B/2B）。

**机制层（Qwen3-8B、Qwen2.5-7B）**
5. 输出由一族晚层**读标签头**读出（逐头 DLA 重建 r=0.9997）：从答案位置读 demo 的标签锚点；注意力按内容相似度（同类 ×2–69）≫ 上下文标签（×1.5–2.6）≫ 位置（≈0）；读出标签身份（E36）。
6. 时间盲的原因：因果掩码使旧锚点在变化后不可改写；新 regime 的锚点不携带“变化”信号（成串的新锚点反而更弱，E37）；读取不偏向新锚点 → 条件证据只能可交换地汇总。
7. 方向错误的噪声效应 = 晚层直接读取噪声锚点（替换噪声锚点在读取层之前完全恢复、之后无效；阳性对照精确，E38）。偏置成分的规范符号部分来自噪声之后的旧 regime 锚点在 ~L16 编码的标签流状态（恢复 0.4–1.0，E38c），以及注意力被更多同标签锚点分走（E37）。

## 4. 预测 → 实验 → 结果
| 预测 | 实验 | 结果 |
|---|---|---|
| 类别不均衡时翻转映射，时间结构只落在“偏向新多数输出”的成分上；少数类 query 被拉向错误答案 | E28/E29 | 条件成分噪声方向错 12/12（6 模型）；Qwen3-8B 少数类 后8−前8 −0.96；关系型输出（±2）同样成立 |
| 同一答案内：格式通道重置、映射通道不重置 | E26 | 格式通道旧 demo 支持度为负 8/8 且与输入内容无关；映射通道为正 16/16 且同类主导 |
| 上下文主效应比上下文×输入交互更易绑定 | E30 | 交互溢出 > 主效应溢出 14/14（7 模型）；Qwen3-32B 主效应溢出 ≈0、交互 0.8（行为层面成立；机制层面见 §3.7 的修正） |
| 换输出词 → 不泄漏 | E31 | nonce 词表溢出 0.00（10/10） |
| 泄漏 ∝ 标签语义相似度 | E33 | ρ=0.75–0.96（10/10 格） |
| 新 regime 换新词 → concept drift 可追踪 | E32 | 噪声方向规范 11/12 |
| 输入领域只部分分开 | E35 | 0.36–0.49 vs 混合 0.79–0.91 |

## 5. 被实验否定的解释（按时间）
表层 vs 潜在（E11b）· 单条 demo 可识别 regime（E13）· “可复制标签”（condarith）· 任务识别 vs 任务学习 TR/TL（E27）· 输出标记即可绑定（E22，8B 不行、32B 部分）· 时间写进内容（E23，到 32B 仍无效）· 输入侧标签分流（E24/E24b）· 主效应来自相邻 token 统计（E34）· 映射与主效应由两组头承载（E36）· 新锚点是运行滤波器（E37）· “Label:” 预测位置存放运行估计（E38b）· E10 游程头 = 边缘通道（E28b）。

## 6. 最近邻与增量
| 近邻 | 它的 claim | 我们的增量 |
|---|---|---|
| Wang et al. EMNLP'23（Label words are anchors） | demo 信息汇聚到标签词锚点，再被读出 | 锚点机制对非平稳/多上下文证据的后果（concept drift 盲、交互泄漏、语义相似度定律）；锚点读取不看位置、旧锚点不可改写的因果解释 |
| Zhao et al. ICML'21 | 多数/近因标签偏置需校准 | 标签流上的“偏置”方向近似 Bayes；真正的缺陷在条件结构 |
| Kossen et al. ICLR'24 | ICL 学标签关系但不像常规学习 | 方向相反检验把“近因”与“结构推断”分开；给出可预测的失效边界与修复 |
| Falck et al. ICML'24 | ICL 违反 martingale | 输出侧近似 Bayes、条件结构近似可交换（set oracle r≈0.98），两者在同一答案内可分 |
| Xiong et al. ICLR'25 | 任务叠加：输出是任务混合 | 混合权重按相似度与输出身份，不按时间/上下文 |
| Dudley ICML'26 / Qin ICLR'26 | 训练的 transformer 能做 in-context 变化检测 | 预训练 LLM 只在输出侧做；条件结构上 13 模型、32B、thinking 都没有 |
| Cho et al. ICLR'25 / Yang-Cho-Inoue ICLR'26 | ICL 检索电路、TR/TL 头 | 行为与机制证据：读标签头按内容检索、不看位置；TR/TL 不是时间性的分界 |
- **Compression risk：** “ICL = kNN + 标签偏置”。load-bearing 差异：(1) 方向相反检验下输出侧近似 Bayes、条件侧可交换，同一答案内分开测量（E22/E26）；(2) 可证伪的符号预测被验证（E28 少数类被拉错）；(3) 定量的语义泄漏定律（E33）与建设性修复（E32）；(4) 因果机制（E38）。

## 7. 预期论文形态
C（理论 + 受控）+ B（测量）：exact oracle 与方向相反检验 → 输出漂移 vs concept drift 的普遍地图 → “按输出存放证据”的说明 → 分隔阶梯与语义定律 → 建设性修复 → 机制。两套叙事并行：ICML/ICLR（ICL 理论与机制）与 ACL/EMNLP（标签语义、标注者视角、非平稳 NLP 场景）。

## 8. 恢复推进时的开放问题（按信息量排序）
1. 读标签头的消融：映射效应与泄漏应同时消失（因果确认）。
2. 非 Qwen 模型的机制复现（需单 token 标签，例如 Llama-3 系列）。
3. 为什么：预训练数据中“同一输出被重新分配给不同输入”有多罕见；toy 中易变数据推不动（E12 v3）。
4. 后果：真实的非平稳 NLP 场景（内容审核政策更新、标注规范变化、多用户个性化）；DICES 真实评分者噪声过大（kappa 中位 0.19），需结构更清楚的数据。

## 9. 修订记录
- 2026-10-05：I01“表层时间、潜在集合”→ 多次修正为“输出漂移 vs concept drift”。
- 2026-10-06 凌晨：I02（TR/TL）被 E27 否定；I03（边缘统计）被 E28/E29 支持；推广为“主效应 vs 交互”（E30）。
- 2026-10-06 晨：E31/E32 表明交互可学（换输出词），定稿为“按输出存放证据”；E33–E35 给出语义定律与分隔阶梯。
- 2026-10-06 下午：机制 E36–E38；“可按上下文条件化的独立先验通路”在读取机制层面不存在（主效应的行为绑定来自 query 自己标注者锚点的反证）。

## 2026-10-10：定位与解释收窄（原结果完整保留）

工作标题是候选计算描述，不是已建立的普遍定律。C09/C10/C13的有界现象可靠，但E58–E64检出可迁移来源差分、native来源name-key中介，以及整个query的来源条件化label消息；因此“信息在但默认不用”和“唯一按输出存放”不能替代完整机制。

| 近邻 | 已拥有的认识 / compression risk | 本线仍开放的可检验问题 |
|---|---|---|
| Cho ICLR2025 | label retrieval + input encoding +旁路；找到额外token/head只是已有框架的实例 | metadata-conditioned计算在整个query何处完成，最终label复制对它的作用 |
| Cho ICLR2026 / NAACL2025 | task-verbalization subspace、过滤、token读出边界 | 不能用adapter成功或换词涨分直接定位source机制 |
| Feng/Steinhardt与Mixing Mechanisms | binding IDs、跨任务子空间、多种机制组合 | demo诱导来源特定函数与显式fact binding的同/不同程序，尚待直接对照 |
| CBR ACL2026 | entity×relation cells；双键binding不是空白 | 规则推断×来源条件化如何组合，不能把来源分类简单改名 |
| Lepori ACL2026；2609.38866/2609.31401 | 表示可读出≠部署、保留但选择失败、probe/native/logit信息区分 | 可读出source方向为何未通过所测label-anchor路径承担source effect |
| Test, then Route 2608.04183 | predicate先在query输入位置计算再传至末位；router与label pair绑定 | metadata-conditioned消息的scope、source→query→label具体链条；“早期有计算”本身不新 |
| Few-Shot Examples Add Up 2605.16591 | QK/V因果分解与context-dependent weighting | full-query条件化与末位attribution的对应关系及其可靠边界 |

扫描记录：venue corpus三次nearest（2026-10-10）；awesome入口main返回404、master读取；DailyArXiv镜像读取至10月7日条目并过滤ICL/binding（无新相关记录据此作结论）；随后回到上述arXiv/会议原文。**没有exact-collision判决，也没有“空白双键问题”的novelty声明。** 近邻压力是研究对象需要更具体，不是关闭项目的理由。

### E65/E66进一步限制（2026-10-10）
E65原生sender-edge显示Qwen marker接力与Mistral source字段接力的边界；删direct标签不稳定改善accuracy，平均source×input交互↑甚至可伴随source排序↓。E66 input前source KV缓存在single/mixed均未部署规则，input后query KV仅保留规则相关logit，独立确认accuracy收益低于MIE。两者不是新shortcut、可复用task-vector或普遍composition障碍的证明；参照Bai PCT、Li just-in-time状态、Cho过滤/旁路。下一关键切口需对信息等价编码提出竞争预测，不能以继续定位token填补意义缺口。证据见两卡、`results/e65_e66_summary.json`与10-10复盘，L1范围保持。
