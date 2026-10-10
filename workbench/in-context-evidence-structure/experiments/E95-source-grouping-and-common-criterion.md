# E95：输入和标签完全相同，来源分组如何决定共同标准？（2026-10-11）

- **状态：** PLANNED。
- **类型：** PILOT；一个有效世界对有效世界的反事实，不扫描激活位置。
- **对应：** I04 / C16 / C20 / P17。
- **问题：** 模型如何从私人判断中提取可共享的评判标准，而不是直接借用别人的标签？

## 为什么现在做

E93表明避免私人映射混入与合法借用标准不等价；E94整体来源状态能切换私人函数，但两个线性标准分量没有功能运输。继续在同一字段找层不能回答标准怎样形成。这里改变观测对象：把所有匿名input-label证据固定，让来源分组本身携带唯一的标准差别。

## 文献定位与设计来源

| 最强参照 | 已有解释 / 学习的实验动作 | 本实验检验什么，尚不能证明什么 |
|---|---|---|
| [Cho 2026](https://arxiv.org/html/2509.21012v4)，§3–4、unseen-label | 用普通标签复制无法覆盖的条件检验补充计算；不是首次信息过滤 | 固定整个匿名输入/标签集合，迫使来源关系起功能作用；不宣称已有过滤电路 |
| [Multi-Task Bayesian ICL](https://arxiv.org/html/2606.20538v1)，§5.2.2 | 固定target，用不同prefix区分prior inference与错误pooling | 此处连prefix匿名input-label都固定；多任务共享本身已有，不是ICES首次发现 |
| [Concept Subspace Learning](https://arxiv.org/html/2605.18830)，§3.4、5 | 已明确task-conditioned矩可识别共同子空间，而无条件均值可能为零；用投影/补空间/同rank对照做因果检验 | 私人函数反向时共享标准可保留，是已有数学；原生LLM怎样构造/部署才是后续问题 |
| CTA / Sun input-label mappings / local task vectors | 示例如有来源的上下文化表示，标签位置可以承载任务信息 | Source-aware retrieval与层次推断均可能通过本实验；行为阳性不能宣布新算法 |

Corpus nearest已执行，长句检索主要是词汇近邻，不能替代以上正文对照。新预印本的claim ownership明确保留，不因为读到它就缩减E90/E91已成立的因果事实，也不把相同数学改名为新机制。

## 任务与冻结配置

三位普通reviewer A/B/C，共同关注food spiciness或service pace，但私人偏好不同。每条review同时含spicy/mild、quick/leisurely两属性。设共同标准c∈{0,1}，私人函数f_s(x)=p_s*x_c；p_A、p_B±完整交叉，p_C=-p_B。没有直接告知c或私人偏好。

- A8例仅++/--，唯一确定p_A，却不区分c；A自身信息对预测不可替代。
- foreign16例：四属性格×两个重复措辞×yes/no两标签。每对相同review在两个不同人手里得到相反标签，是合法私人偏好，不是错误label corruption。
- 固定每行review、label、位置；当y=p_B*x_c时名字填B，否则C。换c**仅交换discordant行的B/C名称**；换p_B仅交换foreign所有B/C名称。
- 两个世界的匿名完整input-label序列、source-label边缘、source-input属性边缘、每Source频率严格相同。差别只在source×input×label关系；不能写成所有文本都相同，Source名字确实改变。
- 4个新context，seed95001。姓名/属性句序/foreign行顺序、A块在foreign前后独立随机；与E93同词池但新组合，不是独立自然数据确认。四query措辞未出现于demo；不筛模型正确项。
- Qwen3.5-27B真实qwen3_5_text，本地已验证revision，openslime+vendor tf5.12.1，冻结bf16/SDPA单卡。Direct所有4context；thinking固定前2context，不按direct结果筛选。

五个功能询问共用示例：native A判断；一条指令提醒从B/C推断共同标准并保持A私人偏好；explicit A criterion oracle；B自身判断；不提供新review时直接问共同标准（food/service）。每context direct136请求，共544。Thinking仅native/criterion/B-probe共72/context，两context144；medium greedy1024，所有截断保留原prefix续2048，不以未完成当negative。

## 竞争解释与可识别性

| 解释 | 成对世界预测 |
|---|---|
| 仅依匿名input-label证据的聚合 | 两世界相同预测，mixed A及criterion在两世界平均正确最多50%，成对同时答对为0；与正确推断分叉 |
| Source-conditioned exemplar + B私人偏好换算 | 可以全部正确；强替代解释，不能凭行为排除 |
| 先推断共同criterion，再结合A私人偏好 | 可以全部正确；不是行为唯一解释 |
| 从各来源私有函数的无向几何提取标准 | 可以全部正确；统计框架已有，不据此声称神经协方差运算 |

运行前静态枚举应证明两个世界均唯一可识别、A单独有两种criterion解、pool完全相同。程序/校正检索/无向metric反例均保存。普通reviewer名称不是人为class code；p_B全方向使某个名字固定绑定类别的捷径失效。

## 读数、阳性对照、噪声地板 + MIE

- **主读数：** A mixed准确率与两个世界同时答对的比例；concordant不变/正确；criterion准确率、c翻转响应、p_B翻转不变性。全词表argmax与候选二选一均报告。
- **次读数：** 当前A答案受p_B翻转影响率、c成对signed logit差；以context bootstrap 10000次95% CI，不把行当独立样本；thinking无效/截断全报。
- **阳性对照：** B自身四新输入；明确A criterion的oracle；一句指令恢复。它们分别测本地函数执行、给定规则执行、提示切换，不假定内部抽象criterion已存在。
- **噪声地板：** 首batch无操作重复误差≤.001nats；全部原始行、唯一键、single-token候选、加载无缺权重、模型身份核对。bf16小logit差不作精细因果判断。
- **MIE：** 成对世界正确与私人偏好保留的结构性模式会改变下一投资；不以一点logit非零或任意5点阈值自动判死。
- **混杂审计：** 姓名与私人偏好/criterion正交；匿名input-label、行位置、source频率及边缘固定；两世界都合法；四query齐报；语言池/小样本/私有函数lookup替代尚未排除。不声称全部内部机制已分离。

## 决策表（跑之前写）

| 结果 | 更新与下一动作 |
|---|---|
| criterion/B明确正确，A弱 | 从示例提取标准的能力与把标准用于私人判断在这个接口分离；随后围绕中间标准的功能部署设计因果竞争，不再找Reviewer字段 |
| 三项明确正确 | 有共享与私人保留的正确计算阳性；解释对象为正确行为，以来源重分组反事实研究其形成过程 |
| B正确，criterion弱 | 私人函数预测不足以支持抽象标准；进一步学习如何测量规则等价类，不以更多alpha/字段修补 |
| B/oracle也弱 | 任务执行尚不能支持上述归因；原始失败保留，回到样例/语言与文献，不无限扩大配置 |
| thinking恢复或改变模式 | 分清默认计算与显式策略；推理文本只是线索，不当内部电路证据 |

任何结果都不会自动证明完整criterion程序/输入过滤/新头；只有anonymous pooling是本实验能明确反驳的受限解释。正式C16/C20 L1、I04/ACTIVE状态不变。

- **算力：** 单卡≤1.2 GPU·时；不训练、不跨节点传大模型。
- **资产：** `scripts/e95_source_grouping.py`；`results/e95/qwen35_discovery`。raw prompts/contexts/行为本地，小audit/run/analysis入git。

## 结果（以后追加）

尚未运行。
