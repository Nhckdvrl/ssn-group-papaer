# 构念与测量：不要让指标偷偷决定科学问题

## 0. 指标必须写清“它观察的是什么”

| 观察 | 直接估计对象 | 不能独自认证 |
|---|---|---|
| critical-token surprisal / human RT | 当前词在前缀下意外程度/人类加工时间 | 读完的正确事件图；内存里有无旧关系 |
| yes/no “old role?” | 在特定问题合同下的回答偏好 | 旧事件从世界中被逻辑否定；新的正确关系已形成 |
| 正确新论元自由叙述 | 某一输出接口上显式声明的关系 | 所有接口中都可提取、在新任务会被使用 |
| forced-choice候选logP | 给定候选字符串的相对生成偏好 | 不加提示能自然产生候选、语义真值 |
| probe/SAE读出 | 被选仪器可读取、可编辑的信号 | 它在原生任务中承担选择性因果中介 |
| source residual patch | 换入这组向量影响输出的总效应 | 唯一语言因子、原生长程传播或记忆痕迹 |
| 重建观察得分 | 在设定的生成模型/上下文下观测的条件概率 | 完整关系为真；action更正确；grader训练一定失败 |
| QA正确率 | 满足答案合同 | 内部关系来源、更新因果、旧错误是否仍可被其他问法触发 |

## 1. 不被一个GoldNo掩盖的四值区分

固定事实来源S，对目标关系 R(a,b)：
- **ENTAILED**：S明确支持R（含允许的指代/语义等价，不要求逐字复述）。
- **CONTRADICTED**：S支持 not R；与无法从S推导R不同。
- **UNDETERMINED**：S既未支持R也未支持not R。
- **PRESUPPOSITION / PRAGMATIC**：要依赖世界知识、问题习惯或语用推断才给默认答案。

对 “While the man hunted the deer ran into the woods”，文本支持 deer ran；**不支持** hunter hunted deer，同时**未排除**猎人实际上猎了鹿。把回答“No”解释成“源文不肯定此角色关系”可以是任务约定；若解释成“世界中此事为假”，则推理已经越权。NP/S和reduced-relative其他问句也需逐题审核，不能因这里举例就断言每个GoldNo都错。

对更新实验还需标注 **what changed**：原初关系 h0 是源中许可的竞争解析，还是外部背景的事实？晚cue是否与它矛盾、只变更范围、增补前提、还是没有新信息？“删掉旧话、写出新话”在不同情形不等价。

## 2. 内容编码先于模型输出，防止事后移动靶心

每个新样本拥有一张最小“关系契约”，至少写：
- 给定源、独立源ID、构式；用语法/语义说明 **晚cue在哪里**，它改变哪条依赖。
- 旧暂时依赖，例如 dress(agent=Mary, patient=baby)；新的明确依赖，例如 fell(agent=baby) 和 dress(patient=unspecified/self under interpretation)。句子未断言Mary是否在其他时空给孩子穿衣，不能把世界否定塞入gold。
- 哪些信息必须显式产生才叫“完整替代关系”，哪些可以合理隐含；独立用途的答案从哪个关系推导。
- 哪些变化只涉及标点、长度、世界 plausibility、选项排列、解码/推理预算；它们可能是confound。
- 原生输出和**外加oracle**的来源：同源生成、外部正确答案提示或人工编写候选必须分开。

开放输出可编码 `EXPLICIT_CORRECT_COMPLETE`、`EXPLICIT_WRONG_OLD`、`CORRECT_BUT_INCOMPLETE`、`AMBIGUOUS_OR_UNBOUND`、`INCONSISTENT_MIXED`、`REFUSAL_UNKNOWN`，允许多标签但要定义覆盖与互斥维度。一个 “someone/something” 不因和gold没有明确矛盾就等于新关系已恢复；也不能把所有省略自动标成模型误解。

## 3. 正测量和反测量必须对称但不必同一界面

同一源的以下问题不等价：
- 旧绑定是否成立？（negative evidence / lingering）
- 新绑定具体是什么？（positive reconstruction）
- 其他正确关系是否保持？（collateral preservation）
- 一个未提前告知的后续用途能否依赖它？（functional transfer）
- 模型生成/选择/真正使用同一解释吗？（availability vs choice vs consumption）

Slattery 2013 用的是不同性质的反身约束和下句干扰，而不只是同源两题。Ceháková 2023 的open-ended error types解决了二元题识别不了的混合结果。我们过去E103表面“correct roles”升分，E107再检查实际完整依赖，就是**先定义了错误角色，后补定义成功**的成本案例。今后先确定成功语义对象；旧数据可事后重新分析，但必须标POST-HOC和未覆盖范围。

## 4. 因果历史：分块KV不是一种可独立操纵的“经历”

对同一个确定性causal transformer、相同tokens、position、mask与参数，正确的incremental KV-cache与一次完整prefill应实现同一个函数（允许数值/实现误差）。在全部输入相同的情况下，说“分两次读过因此旧理解固化”，缺少不同的有效处理组。后到token可在自身新状态中读取前文并重新组织意义，尽管前文旧token向量不被原地重写。

要检验**历史路径依赖**，真正的操纵必须在信息环境/外化承诺/任务目标/中间产物/采样时序等处产生可区分历史；控制最终信息是否等价、检索路径、计算预算与对齐位置。若加入一条“你以前回答过X”就改变行为，结果可能是承诺一致性压力而非解析算法，需并列这种解释。

## 5. Likelihood分解：算术身份不等于原因

`log p(x,y|H) = log p(x|H)+log p(y|x,H)`；两候选之差也满足该恒等式。

若早段x本来在正确H下不常见、晚段y要求修订，一个完全合理的概率模型就可得早段Δ<0、晚段Δ>0且整体Δ<0；这既不证明score错，也不证明模型保留了旧误解析。ABBEL Eq6还减去了此前证据的prior，观测分数的目标未必是最终语义posterior最大化。要证明“错误credit”，应有：
1. 固定语义关系的正确/错误候选，而且长度与措辞分布可对比；
2. 真正的晚到语义证据与不要求修订对照；
3. 原生候选池覆盖率和固定score选择（oracle与native分开）；
4. 独立有后果的后续用途，并能检验score所优化的原始目标；
5. 对词面/位置/先验改变的敏感性报告。

相同分数换截断位置本身不能确立因果机制。

## 6. 统计对象、校验与停止

- primary n 是**独立源/材料cluster**而不是candidate/问答/patch层数。若同source多候选、多问句，先聚合/配对到source层；公开覆盖分母与eligible subset。零可比较对≠零能力。
- 每个标注矩阵检查唯一键、总数量、审计状态、hash与许可的缺失。两次同一模型的审计裁决不是两位人类独立复核；不确定类别应保留区间。
- all predetermined controls 先报告；用看到结果后创造的新切分注明POST-HOC；漂亮局部不能升级为总体主张。
- preflight要求实际可解析、有效stop、正确调用模式，且与gold独立；E93旧重复tokens的预检没做到这一点。入口：[CPU修复与边界](../AUDIT_2026-10-12.md)。
- 一次负结果只限制该操作覆盖，不证明所有语义机制不存在；一次正patch只识别输入向量的total effect，不证明唯一因子。

**记账格式**：问题→语义对象→读数→这个量可能由哪些竞争过程生成→能区分它们的对照→主要结论/反例→适用范围→未读取/未运行。数值在历史实验卡与原始分片，不从本页凭空生产。