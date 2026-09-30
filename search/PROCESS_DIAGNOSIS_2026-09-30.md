# 选题流程诊断与顶会校准（2026-09-30）

> 本文回答两个问题：**(1) 为什么 25 天、1,420 次提交、约 255 个被杀题目、14 个 workbench 之后，candidate 仍然是 0？(2) 应该怎样改？**
> 结论与新流程分别落实在 `search/README.md`、`workbench/README.md`、`failed/REAUDIT_2026-09-30.md` 与 `tools/venue_corpus/`。
> 本文所有数字都可以用 `tools/venue_corpus/`（顶会接收/拒稿语料库）和本仓库的 git 历史复现。

---

## 0. 一页结论

**问题不在于执行不够努力或不够严谨，而在于流程在结构上把“顶会最常接收的论文类型”过滤掉了，只留下最稀有的一类。**

我们的流程（包括 9/28 重置后的 territory → workbench 版本）实际上在寻找这样一种论文：
> 一个**没有近邻**、**出人意料**、**无需方法**、**一次诊断实验就能说清楚**的科学发现。

顶会确实接收这类论文，但它们是少数、方差极大。顶会最常接收的是另外几类：
- **在强开源系统上做出来的“痛点 → 修复”型方法论文**（附分析）；
- **把另一个领域的成熟构念（construct）引入并大规模测量**的分析论文；
- **理论 + 受控实验**；
- **暴露能力缺口的 benchmark / 评测协议**。

而我们的规则恰好把这几类都挡在了门外：
1. **新颖性判据错位**：把“同一研究 program 里已经有人发表”当成撞车。约 91% 的 kill 的主因是 `NOVELTY_PARENT_COLLISION` 或 `CROWDED_PARENT`。可是被这样杀掉的 parent，顶会在同一周期里继续大量接收（例：K215 attention sink 被判“已成 program”，ICLR 2026 接收了 14 篇，切片接收率 47%，全会基准 27%）。
2. **论文形态错位**：“入场不许有方法”，只追求“发现”。可 ICLR 2026 被接收的多智能体 LLM 论文里，90% 的摘要是 “we propose / introduce / present” 型，“we find / show” 型只占 17%。
3. **时间尺度错位**：门槛要么在没有任何证据时执行（14 个 workbench 中 7 个**一个脚本都没跑**就被降级），要么在只有几小时证据时执行（两个实时方向 workbench 的寿命分别约 11 小时和 20 小时）。真实的论文是以“周—月”为单位的建设过程。

**应保留的优点**：强基线纪律、效应量 vs 噪声地板检查（L19 教训）、一阶工具有效性检查（L29 教训）、算力匹配比较、诚实记录负结果、谱系式读论文。这些应当成为我们**做出论文的比较优势**，而不是**杀题的工具**。

---

## 1. 我们到底做了什么（事实）

| 项 | 数量 / 事实 | 出处 |
|---|---|---|
| 时间跨度 | 2026-09-06 → 2026-09-30（25 天） | `git log` |
| 提交数 | 1,420（约 57 次/天，基本由 agent 驱动） | `git log --oneline \| wc -l` |
| kill ID | 约 255 个（K001–K253 + 续篇），其中 **K193–K195 被分配了两次**（批次文件与续篇指向不同题目） | `failed/` |
| 历史候选 | L01–L45、S01–S12、CT01–CT09 | `archive/` |
| workbench | 9/28–9/30 三天内开了 14 个 | `workbench/` |
| 当前 candidate | 0 | `candidates/README.md` |

### 1.1 kill 的原因分布
- 索引表中 125 行里，**114 行（91%）** 的主因是 `NOVELTY_PARENT_COLLISION`（73）或 `CROWDED_PARENT`（41）。
- K061–K161 的详细记录中，141 个标题里有 **101 个是 “X ≠ Y” 模板**（如 “Event Mention ≠ Event Occurrence”），其中 86 个死于 `NOVELTY_PARENT_COLLISION`。
- 287 条 kill 记录中，18 条的“拥有者”只有 arXiv 预印本或笼统的 “2026 work”，没有任何同行评审出处。

### 1.2 workbench 的寿命与实验量

| workbench | 开 → 关（09 月，git 时间） | 脚本数 | 结局 |
|---|---|---:|---|
| ai4quant | 28 19:20 → 29 13:34 | 0 | 降级 |
| hybrid-adaptation | 28 19:20 → 29 13:34 | 0 | 降级 |
| moe-route-preference | 28 19:20 → 29 13:34 | 0（继承旧结果） | 关闭 |
| model-diffing-measurement | 29 17:58 → 29 18:17 | 0 | 降级（约 20 分钟） |
| npc-deception-investigability | 29 01:24 → 29 13:34 | 0 | 降级 |
| npc-persona-behavior-grounding | 29 11:19 → 29 13:34 | 0 | 冻结 |
| mechanism-population-dynamics | 29 23:18 | 0 | 未开始 |
| cross-lingual-acquisition-regimes | 30 21:20 | 0 | 未开始 |
| realtime-agent-capability-transition | 29 15:21 → 30 02:35 | 16 | 关闭（约 11 小时） |
| realtime-computation-boundaries | 30 00:09 → 30 19:58 | 20 | 冻结（约 20 小时） |
| omni-recon | 30 17:09 → 30 19:57 | 13 | 侦察中，多条线当天降级 |
| scoped-context-state | 29 14:15 → | 5 | 仅生成数据 |
| shape-olmo | 28 | 39 | 暂停（继承 CT05–09） |
| **video-world-model-temporal-interfaces** | 28 23:29 → 持续 | **34** | **唯一存活**，并且是唯一写了“论文形态卡”（CVPR 计划）的一条线 |

---

## 2. 旧流程（“猜现象 → 赌博 → 实验”）为什么必然低产

**2.1 想法的生成器决定了命中率。** 旧流程的想法主要来自：概念二分（“A 和 B 在理论上不同，问 LLM 会不会区分”）、“X ≠ Y” 测量有效性模板、“旧定律在 LLM 上重新解释”、单篇论文的 anomaly、多篇论文之间的张力。这些生成器都是**从文献的邻域里采样**，所以几乎必然有近邻——于是被新颖性规则杀掉。

**2.2 即使通过了新颖性，实验本身的期望收益也很低。** 因为想法是“猜”的，现象要么不存在（L15：两个模型用 CoT 时几乎精确地算出后验，预设的“能力—整合分离”不存在），要么不稳定（L11：梯度差异在三个种子上方向互相矛盾；L45：完全内化终点在种子间崩溃），要么随训练配方而变（S03），要么需要超出预算的算力才能分辨（L19：预期效应 2.7pp，低于评测噪声地板）。

**2.3 “价值判断”发生在实验之后。** L36、L13 都做出了干净、可复现的结果，然后才发现“母问题不够重要”或“每次扩写都被成熟 parent 吸收”。这说明重要性不是在选题时由数据回答的，而是在投入之后由同一个 agent 事后判定的。

这三点是结构性的：换更好的 prompt、更严的规则都不会改变“从文献邻域采样 + 猜现象 + 事后判重要性”的低期望值。

---

## 3. 当前流程（territory → workbench）仍然存在的问题

9/28 的重置把“先起题再实验”改成“先进入领域、复现强基线、再让问题浮现”，方向是对的。但实际运行暴露出以下问题：

### 3.1 仍然是“找现象”，只是换了名字
workbench 章程的目标是“发现一个真实、可复现、新颖的研究对象”，入口禁止方法（“No method at entry”；方法只有在 Failure → Bottleneck → Action → Outcome 每一环都有证据后才被允许）。这等于**要求 workbench 先中一次“意外发现”彩票，才允许做任何建设性的工作**。实时语音两条线的轨迹就是例子：找到“失败”→ 发现是提示词默认值（一句指令恢复：abstention 1/39 → 39/40；clarification 4/20 → 18/20）→ 冻结。没有任何“建设性后备路径”（例如在该系统上做一个方法或评测协议）。

### 3.2 门槛执行得太早，而且在桌面上执行
“顶会天花板门槛”、“最坏审稿压缩”、“最近邻拥有者审计”都在任何实验之前执行。**在没有证据的时候，任何想法都能被压缩成“X 在 Y 上”**，所以桌面审计几乎总是得出“降级”。结果：7 个 workbench 零脚本被降级（NPC 两条、可解释性 model-diffing、hybrid、ai4quant、MoE……），其中恰好包括用户偏好里的**游戏 NPC**和**可解释性**。

### 3.3 “驻留”名不副实，并行过多
章程写的是“baseline residency 先于一切”，但实际寿命以小时计，3 天开了 14 个 workbench。规则里“null 结果只杀解释，不杀领域”“冻结领域需要覆盖证据”都写了，但没有最短驻留时间和并行上限来保证它们被执行。

### 3.4 主要测量工具脆弱
大量探针是“对已部署聊天模型做 prompt 行为测试”。这类工具对系统提示、解码方式、默认策略极其敏感，产出的“现象”常常是默认值而非能力（见 3.1）。流程没有对“工具可靠性”设门槛，却对“题目新颖性”设了很多门槛——顺序反了。

### 3.5 自己提出、自己判死：审稿模拟器没有校准
“reviewer compression（你不就是 ___ 吗？）”由提出想法的同一个 agent 在想法阶段执行，天然偏悲观：在一年十几万篇 arXiv 里总能找到一个近邻。而真实审稿噪声很大：**ICLR 2026 被拒/撤稿的论文里，约 840 篇以相同标题出现在 ICML 2026 接收名单中（约占 ICML 2026 接收论文的 13%）**，其中包括与我们方向相关的 “Investigating the Link Between Representational Similarity and Model Interactions”（ICLR 2026 拒，5.5 分 → ICML 2026 接收）。想法阶段的“想象审稿人”不可能可靠地预测这种结果。

### 3.6 没有论文形态与 deadline 锚定
流程从不问：这篇论文的贡献列表长什么样？主表是什么？和哪些基线比？投哪个会、哪天截稿？唯一写了这些（`video-world-model-temporal-interfaces/CVPR_ASSESSMENT.md`：3 个贡献、4 条摘要主张、5 张主图、证据标准、风险登记、10/15 关口）的那条线，恰好是唯一存活的线。

### 3.7 规则与文档本身成为负担
每个 workbench 有数百行的合同式 README，kill ledger 约 200KB，外加大量“Do not reopen by …”条款。这些反复活规则让可探索空间**单调收缩**——而第 4 节说明，很多被禁止的区域恰恰是顶会仍在大量接收的区域。

### 3.8 题材选择缺少量化依据
territory 来自博客（Shape）、单篇论文（PCSP、ProofGrid/ChronoScope）或产品新闻（GPT-Live），没有测量过热度、接收率、增长速度、是否被资源雄厚的团队主导、我们是否有可运行的强开源基线。

---

## 4. 与顶会对齐：校准数据

语料：ICLR 2025/2026（**含 22k 篇拒稿/撤稿及审稿均分**）、ICML 2025/2026、NeurIPS 2024/2025、ACL 2025/2026 main、EMNLP 2024/2025 main、NAACL 2025 main、CVPR/ICCV 2025，共 65,716 条。按组内规定**排除 EACL 与所有 Findings**。NeurIPS 2026 名单尚未公开，另用作者自报补充。

### 4.1 被判“已有 program / 已被拥有”的 parent，顶会仍在大量接收
（`python3 tools/venue_corpus/audit_kills.py`；正则只求精确，行数是下限）

| kill | 被杀的 parent | ACL25 | EMNLP25 | NeurIPS25 | ICLR26 | ICML26 | ACL26 | ICLR26 切片接收率（基准 27%） |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| K215 | attention sink 为何存在 / 是否必要 | 2 | 2 | 4 | 14 | 16 | 5 | **47%** (n=30) |
| K216 | 策略改进使评估器失效（reward hacking / 过优化） | 5 | 1 | 19 | 35 | 50 | 12 | 34% (n=104) |
| K204 | 涌现 / 训练中的相变 | 3 | 0 | 13 | 17 | 13 | 5 | 31% (n=55) |
| K201 | weak-to-strong 成功条件 | 6 | 2 | 6 | 7 | 9 | 3 | 30% (n=23) |
| K177 | LLM 如何对待冲突证据 | 7 | 7 | 8 | 7 | 7 | 8 | 30% (n=23) |
| K218 | 多语言诅咒 / 迁移规律 | 11 | 14 | 3 | 1 | 1 | 10 | 9% (n=11) |

具体例子：
- K215 被杀的理由是“现象→形成→功能→必要性这条链已经成了一个 program”。同一周期，ACL 2026 main 接收了 *Attention Sinks Are Provably Necessary in Softmax Transformers* 和 *A Mechanistic Account of Attention Sinks in GPT-2*。
- K217（口头置信度 vs 内部置信度的形成原因）被杀；ICML 2026 接收了 *How do LLMs Compute Verbal Confidence?*。
- K189（softmax bottleneck）被杀；ICLR 2026 接收了 *The Softmax Bottleneck Does Not Limit the Probabilities of the Most Likely Tokens*。
- K225（多智能体中的 hidden profile）被杀时引用的“拥有者” HiddenBench 当时是 2025 年预印本；它本身在 ICML 2026 才被接收。

**含义：**“有人做过”“已经成了 program”不是顶会的拒稿理由。顶会判断的是**这一篇的具体 claim、证据与方法相对近邻的增量是否清楚、是否扎实**。一个活跃的 program 反而说明审稿人关心这个问题。K218 这一行也说明另一件事：同一个 parent 在 *CL 会议持续被接收、在 ICLR 却很难——**热度要按目标 venue 看**。

### 4.2 被接收的论文长什么样（摘要线索，accepted vs rejected）
（`python3 tools/venue_corpus/query.py shapes <pattern>`）

| 切片（ICLR 2025+2026） | 接收 n | method | finding | theory | benchmark | failure-mode 语言 | 均分 接收 / 拒 |
|---|---:|---:|---:|---:|---:|---:|---|
| 多智能体 LLM | 115 | **90%** | 17% | 10% | 70% | **36%**（拒 28%，撤 22%） | 5.53 / 4.20 |
| 机制可解释性 / SAE / steering | 187 | 70% | **42%** | **18%** | 40% | 25% | 5.93 / 4.17 |
| 统一多模态（理解+生成） | 97 | 86% | 15% | 5% | 64% | 22% | 5.92 / 4.33 |
| LLM 游戏智能体 | 40 | 85% | 40% | 15% | 52% | 18% | 5.63 / 4.48 |

读法：
- **不同领域的“可接收形态”不同。** 多智能体与统一多模态几乎全是方法/框架论文；可解释性里“发现型”和理论型比例明显更高。选题时必须先看目标领域的形态分布，而不是默认“我们做分析论文”。
- **“先识别失败模式，再提出方法”是被接收论文的共同特征**（多智能体切片中 failure-mode 语言：接收 36% > 拒稿 28% > 撤稿 22%；可解释性切片 25% > 21% > 19%）。这正是“Failure → Bottleneck → Action → Outcome”——但它是**一篇论文的叙事结构**，不是“入场许可”。

### 4.3 顶会多智能体论文的真实生长方式（摘要级精读，ICLR/ICML 2026）
- **引入成熟构念并大规模测量**：*Multi-Agent Teams Hold Experts Back*（组织心理学的 strong synergy → LLM 团队达不到专家水平，瓶颈在“利用”而非“识别”专家，机制是折中式共识）；*Representational Similarity and Model Behavior in Multi-Agent Interaction*（神经科学中“神经相似性预测合作”→ 276 对模型 × 8 个游戏）；*HiddenBench*（社会心理学 hidden profile）；*Emergent Coordination in Multi-Agent LMs*（部分信息分解）。按我们的旧规则，这些都会被判为“把已知构念搬到 LLM 上，没有新 parent”。
- **在强系统上发现命名失败模式 + 修复**：*Lazy Agents → Deliberation*（多智能体 RL 推理中的“懒惰智能体”→ 因果影响度量 + 可验证奖励）；*Dr. MAS*（NeurIPS 2026：多智能体 LLM RL 训练不稳定 → agent-wise normalization）。
- **理论 + 受控实验**：*Benefits and Limitations of Communication in Multi-Agent Reasoning*。
- **方法 + 效率**：LatentMAS（ICML 2026 spotlight）、Cache-to-Cache、KVComm（ICLR 2026）。

### 4.4 低接收率切片的提示
ICLR 2026 上：ToM × 多智能体 0/13、社交推理游戏 0/11、合作游戏 LLM 2/14、“白盒”多智能体 1/11，远低于 27% 基准；而 ACL/EMNLP main 在同类题目上有接收。**用户偏好里的游戏 NPC / 社会推理方向，如果投 ML 会，贡献必须做成 ML 审稿人认可的形态（方法 + 严格评测），否则应以 ACL 系为目标。**

---

## 5. 改革原则（落实到新文档）

| 原来 | 改为 | 落实位置 |
|---|---|---|
| 新颖性 = 父问题无人触碰；有 program 即杀 | 新颖性 = **可陈述的增量**：对最近的 10 篇接收论文 + 近期 arXiv 写定位表；只有“同一 claim + 同一类证据 + 同一设定”才算撞车，撞车时先改 delta | `search/README.md` §3，`tools/venue_corpus nearest` |
| 题材来自博客/单篇论文/产品新闻 | 偏好 × **量化热度**（接收数、切片接收率、arXiv 增长）× **可运行的强开源基线** × **该领域的可接收形态** | `search/README.md` §2 |
| 入场禁止方法；先找意外现象 | **驻留 = 建设**：跑通强基线、建可复用 harness、记录痛点日志；从第一周起允许针对**已观察到的痛点**做方法 | `workbench/README.md` §2–3 |
| 桌面 kill；数小时即冻结 | 至少 **2–3 周驻留**并交付物齐全后才能关闭；桌面 kill 只允许“精确撞车”或“算力不可行” | `workbench/README.md` §5 |
| 同时开很多 workbench | **1 个主线 + 至多 1 个探索线**；每周人审“论文形态卡” | `workbench/README.md` §1 |
| 无 venue / deadline | 每条主线绑定一个 **目标会议与截稿日**，倒排里程碑 | `workbench/README.md` §4 |
| agent 自己压缩自己 | 用真实接收/拒稿数据校准；重投是常态（ICLR→ICML 约 13%） | `tools/venue_corpus/` |
| 反复活规则单调收缩空间 | kill ledger 再审：桌面新颖性 kill 改为“可带 delta 重开” | `failed/REAUDIT_2026-09-30.md` |
| 文档合同化 | workbench README 固定模板、≤200 行；过程日志放 log | `workbench/README.md` §6 |

**保留并强化**（它们是我们的比较优势）：
- 强基线、算力匹配比较（很多多智能体论文不做算力匹配——这正是我们能做得比别人扎实的地方）；
- 效应量 vs 噪声地板（L19）、一阶工具有效性（L29）、多种子、同一输入指纹断言（S03）；
- 谱系式读论文与 paper-rewind 练习（现在加上“与最近邻的距离”分析）。

---

## 6. 对 Sasano 口味通道的定位
Sasano 通道（自然、清楚、一个 RQ 对应一个 finding、避免“そうだよね”）作为 **ACL 系论文的叙事与判断标准**依然有价值。需要改变的是它的**生成方式**：不再用概念二分或“X ≠ Y”模板去生成题目（那正是 K061–K161 大批阵亡的来源），而是在驻留中观察到稳定现象后，用 Sasano 标准来判断和打磨叙事。

---

## 7. 复现本文数字

```bash
cd tools/venue_corpus && ./fetch.sh && python3 build.py
python3 audit_kills.py                                  # §4.1
python3 query.py shapes "multi[- ]agent" "\b(LLMs?|language models?)\b"   # §4.2
python3 query.py density "attention sinks?" --show 5
git log --format="%ad" --date=short | sort | uniq -c    # §1
```
