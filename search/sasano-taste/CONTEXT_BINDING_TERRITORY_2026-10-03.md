# Territory：上下文中的情境理解与信息组织

日期：2026-10-03；Sasano-first候选；主会对象可为ACL/EMNLP、ICLR/ICML/NeurIPS，取决于最后证据。此卡提出驻留领域，不注册预期finding、不新建workbench。

**自然问题：读完一段描述后，模型怎样记住“谁和什么有关、发生了什么变化、现在到底是什么情况”？** 对象涵盖人物/物体与属性、关系、事件更新及信息干扰。表格和盒子任务是已存在的可控入口，不能把整个领域缩成“某种提示里的一个token”。可解释性是回答实际理解问题的工具。

## 热度与近期接收

运行 `density 'entity bind|relational bind|entity track|binding.*language|language.*binding'`：ICLR2026接收9/35（26%，全会27%），ACL2026为5，ICML2026为15；但人工抽查发现视觉/蛋白binding误命中，**这些数仍高估纯文本邻域，不能当精确领域规模**。更宽的`binding|entity tracking|state tracking|table understanding`同时包含视觉/表格benchmark和蛋白，ICLR2026为29/70，故不采用41%作为选题背书。

最新已核主会核心：

| 论文 | 当前已经拥有的内容 |
|---|---|
| [Mixing Mechanisms，ICLR2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/2eeff35664016c7f0f8aa704f0d9a83e-Abstract-Conference.html) | 位置信息之外，词汇与反身指针共同检索绑定实体；跨模型/任务及干预分布建模 |
| [Do Language Models Track Entities Across State Changes?，ICML2026](https://proceedings.mlr.press/v306/tang26ah.html) | 动态操作、按query整合、全局移除tag及它预测的行为失败 |
| [Cell-Based Representation，ACL2026](https://aclanthology.org/2026.acl-long.2194/) | entity×relation的低维cell组织、跨context平移、干预改变关系判断 |
| [Representational Analysis of Binding，EMNLP2024](https://aclanthology.org/2024.emnlp-main.967/) | binding order ID子空间与可控编辑；明确的parent |
| [How Do LMs Bind Entities in Context?，ICLR2024](https://openreview.net/forum?id=zb3b6oKO77) | 绑定问题的机制起点，按后继论文回溯，不冒充最新论文 |

NeurIPS2026目录新增 *How Do Language Models Understand Tables?*（[全文](https://arxiv.org/html/2602.08548v1)）、*Do LLMs Bind Episodes?*（仅目录，全文未取得）；前者已分析单元格定位三阶段与列索引，不是可再命名为新意的空白。后者不可仅凭题目推断实验或开源资产。

## 谱系卡

1. **绑定实体 → 定位binding ID → 混合检索机制。** 早期短上下文位置解释在更复杂输入失准，ICLR2026通过反事实设计拆开替代机制，并拟合干预后的输出分布；增量来自推翻解释的适用范围。
2. **静态状态 → 动态更新 → 机制预测新失败。** ICML2026不只加操作数，而是研究新增/删除/移动如何被执行，再构造原benchmark遗漏的情况检验预测。
3. **一对实体与属性 → 多关系绑定 → 结构化读取。** ACL2026把关系轴加入表征组织；表格工作进一步连接二维结构与一维序列。接下来不能简单声称“有低维网格”。
4. **长输入准确率 → 位置、干扰和记忆组织。** [Unable to Forget](https://arxiv.org/abs/2506.08184)已经把前摄干扰与长度分开；本地有ICLR2026 Reject4.50旧记录，其他最终会场未核，不把检索聚合页的会议标签当事实。

## 形态卡：为什么有主会资质

已有范例的证据组合是：**自然理解问题 → 能区别解释的行为测量 → 因果干预 → 对新输入的可验证预测**，或**已有表示理论的适用边界 → 更准确的解释模型**。它们没有要求预训练更大模型，也不靠小模型刷数学分数来成立。

本轮`shapes`宽切片有分数accepted40，method78%、finding45%、benchmark57%，标签重叠且混入非目标；只支持该邻域存在组合形态。尚未补齐纯文本同邻域10篇接收、5篇高分拒稿与评审全文；不根据分数猜拒稿原因。

## 立足点卡

**首入口：[mixing-mechs](https://github.com/yoavgur/mixing-mechs)里的Gemma-2-2B-it官方示例。** 已核有`example.ipynb`、`tasks/dist.py`、任务grammar、因果模型及patching依赖代码。README说明仍在整理，但并非占位仓库。先复现一个公开干预图与行为对照，再扩家族和输入；本轮尚未安装或实跑。

**独立窗口：[entity-tracking-mi](https://github.com/PootieT/entity-tracking-mi)。** 有生成器、原数据入口、行为评测、probe/path-patching脚本。原文主分析CodeLlama13B，补充Gemma2-2B与Llama3.1-70B；从能完成前置任务的小模型开始，不能用2B失败代表70B相同机制。官方README把`environment.yaml`写成`.yml`，配置需核，70B有远程NDIF路径，不能假定全部脚本默认本地。

基础LM冻结；probe与解释模型可能有小规模拟合，明确区分“LLM不训练”和“完全不训练任何参数”。短文本、目标位置activation和输出分布适合独立单卡缓存；完整逐头patching仍可能慢，不能首次就铺模型×所有token×所有层。

## 压力清单

| 压力 | 来源 | 可发展的研究动作（尚非我们的idea或发现） |
|---|---|---|
| 一种检索机制只在简单输入成立 | Mixing Mechanisms §3–5 | 让替代解释给出不同预测，再干预而非只看attention |
| 结构相同却有不同信息来源/定位方式 | Mixing Mechanisms反事实与padding | 标准输入变化及信息组织测量；“lost in middle”本身已知 |
| 正确完成旧benchmark仍可能使用脆弱更新规则 | State Changes §4.4 | 由机制预言自然失败，再独立验证；其三个remove场景已占 |
| probe读不到全局状态不足以证明没有任何状态表示 | State Changes §3的线性读出范围 | 改测量位置、读出族与表示单位，联系行为后果，避免纯probe竞赛 |
| 实体身份、关系和表面token容易混为一体 | ACL2026 CBR及跨context干预 | 关系保留/迁移的可回答性与干预效度；低维cell主张已占 |
| 状态操作与普通回忆有不同前置能力 | State Changes多模型差异及few-shot附录 | 原配置复现、单句恢复、基础执行阳性对照 |
| 受控生成语料到实际文本仍有外部效度距离 | Mixing §5仅entity-less filler；State Changes盒子任务 | 回真实记录/程序描述/多轮交流检验同一机制；不能只换名词 |

## 驻留顺序与仓库分工

原示例复现与时延/显存测量 → 固定数据/反事实/评分协议 → 普通成功与失败一起记录 → 标准输入与强提示控制 → 用近邻更新定位 → 人审后决定研究动作。没有指定要“发现哪个异常”。

与当前`mechanism-population-dynamics`的交集是内部干预工具；那条线现在已有预训练语料与“复制上文/回忆知识”仲裁测量，本领域不能再把仲裁当自己的新问题。`latent-world-model-planning`已有状态/记忆/不确定性分支，旧CT05也有exact binding资产；正式进入前需人决定复用/归属。此卡研究语言输入里的情境组织，不自动重复建设新环境或恢复旧线。

风险不是“有人做过所以关掉”，而是只把最近邻换模型/实体名；需要由复现观察确定改变哪条解释、对什么理解行为产生后果。主会潜力由上述接收形态支持，尚无本仓库新结果。
