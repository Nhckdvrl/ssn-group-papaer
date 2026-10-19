# NPC研究的测量：对象、构念、因果与玩家价值

更新：2026-10-19。测量应与研究目的相配：动作控制、角色表达、作者工具、社会仿真和玩家体验各有合理证据。**实际游戏后果是声称改变游戏机制时的必要证据，但不是语言表达、角色认同和创作价值的唯一来源。** 本页是知识规范，不启动任何测量。

## 1. 把对象和评价单位写清楚

| 研究对象 | 合理指标举例 | 必须防止的外推 |
|---|---|---|
| 动作与技能 | 成功、轨迹、动作风格、响应时间、编辑保留 | 任务回报高就一定像人、动作自然或适合角色 |
| 对手与难度 | 挑战曲线、玩家学习、挫败、公平感、长期动机 | 固定50%胜率就等于最佳难度 |
| 合作伙伴 | 团队收益、贡献、等待／重复劳动、适应过程、人类偏好 | agent替玩家做完全部工作就一定是好队友 |
| 人物表达 | 知识边界、可辨识风格、场景适合度、作者人物约束 | LLM采访、括号动作或人格量表就证明真实行为 |
| 关系与情绪 | 事件来源、解释、更新、跨情境预测、玩家理解 | 所有变化都叫漂移，或所有正面语言都叫共情 |
| 叙事与选择 | 动机、连贯性、信息节奏、可达分支、表达和角色认同 | 只有结局改变才有agency；分支越多越好 |
| 作者工具 | 实际作品、修改任务、诊断正确性、时间和返工、长期使用 | 生成字数、演示截图或问卷偏好就代表制作成本降低 |
| 社会／经济仿真 | 个体拟合、制度干预、总体分布、外部验证 | 出现熟悉宏观现象就证明拟真人群或因果理论 |
| 安全与规则 | 合法完成、越权、误拒、实际副作用、适应攻击 | 什么都不做或不提供线索就叫完美安全 |

[评价综述](../../../library/themes/game-npc-social/papers/RPA_EVALUATION_SURVEY_2025.md)支持按属性和任务选择指标；[叙事选择研究](../../../library/themes/game-npc-social/papers/NARRATIVE_CHOICE2022.md)提示表达性选择也可能有价值；[DeepMimic](../../../library/themes/game-npc-social/papers/PENG_2018_DEEPMIMIC.md)、[FCP](../../../library/themes/game-npc-social/papers/STROUSE_2021_FCP.md)和[KNUDGE](papers/KNUDGE_2024.md)展示不同指标会得出不同判断。

## 2. 不同证据层能回答不同问题

1. **模型输出／文本评分**：可以研究人物风格、知识、对话和评价方法。需说明参考、评委、样本及人机一致性。
2. **交互轨迹**：可观察多个参与者与上下文变化。须区分真实玩家、固定脚本、模型模拟玩家和随机选择。
3. **独立状态／引擎行为**：支持动作执行、机械一致性和世界后果。叙述者声称门已开，不等于引擎验证门已开。
4. **真人与作者研究**：可发现体验、需求、解释和实际使用问题。短时便利样本、专家评文本、真正游玩和长期创作分别记录。
5. **生产和持续使用**：可支持部署、维护或长期关系主张。内部案例、评论、自选用户和对照实验各有选择偏差。

这些不是可机械排序的质量等级。质性访谈可以提出重要设计分类；小样本案例可以证明新的创作方式存在；但它们不估计整个玩家群体的平均效果。[Orchid-Creator](../../../library/themes/game-npc-social/papers/ORCHID_CREATOR2026.md)的六个月作者案例也不是六个月玩家关系研究。

## 3. 真值、角色所知与作者意图

游戏真值、NPC观察、玩家声称、别人转述、NPC回忆和作者规范应有不同来源。错误信念可以是合法叙事机制；[Sabre](../../../library/themes/game-npc-social/papers/SABRE_2021.md)和[Talk of the Town](../../../library/themes/game-npc-social/papers/TALK_OF_TOWN_2015.md)就显式研究误信／转述／说谎。不能把与全知世界不一致的角色信念一概算坏。

事实正确也不保证此刻该公开。[KNUDGE](papers/KNUDGE_2024.md)中的真实人物事实可能破坏披露节奏；安全任务则需定义谁在什么条件下有权知道什么。原任务没定义唯一规范时，保留多种合理选择或不可判定，不在看到输出后补答案。

规范性判断同样适用于目标与合作：已收到物品不一定形成有效承诺，某人亲自完成与目的被代办不同，计划失效与目的消失不同。局部任务可记录“场景→有效前史→可行机会→动作→后果”的漏斗，但这个漏斗不应成为所有NPC方向的统一任务模板。

## 4. 分母、拆分与独立性

| 常见计数 | 应实际报告 | 本轮可核例子 |
|---|---|---|
| 角色×场景×轮次×seed | 独立游戏／布局／场景／角色及重复分别列 | CharacterBox是10作品100场景；多轮不额外增加独立世界 |
| 判断次数 | 样本与标注员聚类，是否同一人多次评分 | MASCOT的多次评分不是同数量独立对话；同伴五角色组不能相加成人数 |
| 生成策略／分支 | 是否真可执行、是否由同一基础世界变形 | Player-Driven Emergence的53节点、43独特策略是玩家提出的策略，部分机制尚不支持 |
| 训练／测试 | 按人物、对话、任务、游戏或时间哪一级隔离 | CharacterEval按样本划分，不能称全对话或新人物隔离 |
| 不同设置的平均 | 共同分母、共同任务、宏观／微观权重 | VideoGameBench实时10游戏与Lite3游戏平均不能直接作倍数比较 |
| 前后提升 | 量表分值、百分比／百分点与相对增幅分开 | HER的22.86→53.12是100分扣分量表上的30.26分 |

参考记录：[CharacterBox](../../../library/themes/game-npc-social/papers/CHARACTERBOX_2024.md)、[MASCOT](papers/MASCOT_EMNLP2026.md)、[同伴研究](../../../library/themes/game-npc-social/papers/COMPANIONS_DISSERTATION2019.md)、[玩家策略](../../../library/themes/game-npc-social/papers/PLAYER_EMERGENCE2024.md)、[CharacterEval](../../../library/themes/game-npc-social/papers/CHARACTEREVAL_2024.md)、[VideoGameBench](../../../library/themes/game-npc-social/papers/VIDEOGAMEBENCH_2026.md)、[HER](../../../library/themes/game-npc-social/papers/HER_2026.md)。

自然游戏任务、作者设计的解释性对照和程序生成压力测试都可有价值，须说明各自用途。相同机制换物品、改名字、增轮次不自动扩大独立情境。训练／开发／选择／测试应隔离，不能以跑得多代替覆盖。

## 5. 模型裁判必须校准，而且不能跨协议拼榜

记录评委完整版本、提示、参考、匿名化、长度处理、评分量表、样本抽法和人机一致性。总体相关可能掩盖关键维度失效；一致性系数不等于构念有效，事后理由不等于模型内部机制。

[InCharacter](../../../library/themes/game-npc-social/papers/INCHARACTER_2024.md)的逐维与整个人格一致不同；[CharacterEval](../../../library/themes/game-npc-social/papers/CHARACTEREVAL_2024.md)总体奖励模型相关高于知识维；[RPGBench](../../../library/themes/game-npc-social/papers/RPGBENCH_2025.md)的趣味与人格评分人机一致性弱；[SOTOPIA-π](../../../library/themes/game-npc-social/papers/SOTOPIA_PI_2024.md)自动高分并未消除真人差距。[CoSER](papers/COSER_2025.md)、[HER](../../../library/themes/game-npc-social/papers/HER_2026.md)、[OpenCharacter](../../../library/themes/game-npc-social/papers/OPENCHARACTER_2025.md)还显示更换评委后绝对分不可互比。

设计独立校准可以用明确规则、人类双盲、不同来源评委和分层质量审查；选择取决于构念。用更强模型审所有数据不自动使答案成为真值。原文表格、算法和协议矛盾应保留为待澄清，而不是选择支持叙事的一处。

## 6. 公平对照与因果解释

[强基线](STRONG_BASELINES.md)应控制角色信息、历史、可见状态、工具、执行器、反馈、决策频率和合理推理预算。无历史对有历史，弱动作接口对可靠技能，训练特定伙伴对从未见伙伴，都不能无条件解释成方法能力差。

若声称某内部机制解释失败，需要干预／替换／反事实证据。能从表示解码地图，不证明行为使用它；生成认知文本，不证明采用对应心理机制；群体出现某种规范，不证明和人类同一过程。应先提出可区分的竞争解释，再选能更新判断的比较。

统计单位随问题确定：按玩家、场景、训练seed或任务簇处理相关性；报告失败、排除和事后切片。样本量依最小有意义效应、变异和推断范围决定，不机械指定统一n。高成本实验不自动比精心设计的小对照更有信息。

## 7. 玩家和作者的额外劳动要可见

分开自愿探索、表达和角色扮演，与为绕过错误被迫重复指令、补做队友工作、修复状态、搜索外部攻略。更长时间既可能是投入，也可能是摩擦。更少NPC发言既可能是高效，也可能使人物缺乏存在感。

[自由语音](../../../library/themes/game-npc-social/papers/VOICE_CONTROLLED2025.md)和[礼貌机制](../../../library/themes/game-npc-social/papers/ETIQUETTE2024.md)显示表达、认知投入和易用性可朝不同方向变化；[Vaudeville评论研究](../../../library/themes/game-npc-social/papers/VAUDEVILLE_FEEDBACK2024.md)与[VR语音研究](../../../library/themes/game-npc-social/papers/DIALOGS_GENAI2026.md)显示错误会改变玩家行为和归因。作者侧同样应区分生成、筛选、规范编写、调试、引擎接入、回归和多人交接成本，不能只测第一次生成耗时。

## 8. 四兴趣方向新增的测量约束

**按体验构念报告。** [PXI开发](../../../library/themes/game-npc-social/papers/PXI_2020.md)为通用性排除了专门社会/叙事构念；[1518人独立验证](../../../library/themes/game-npc-social/papers/PXI_VALIDATION_2024.md)支持分构念模型而非高阶总PX。选择自主、好奇、意义等应服从问题，补充角色关系/叙事过程；不能自行合为“整体好玩”，也不能把关联SEM当设计因果。

**允许人物和作者有依据地改变。** [ORIBA](../../../library/themes/game-npc-social/papers/ORIBA_2025.md)的作者会受互动启发而修订角色，[Bonsai](../../../library/themes/game-npc-social/papers/BONSAI_2026.md)则处理生成后的作者编辑。保留“符合先前明确意图”和“作者后来采纳新方向”两份记录；新的创作决定不反写旧评价gold。若规范本来允许多解，不要求玩家猜中隐藏心理的唯一解释。

**情绪至少有三个对象。** NPC内部状态、玩家所扮演人物的感受和实际玩家情绪不能混同。[OSSE](../../../library/themes/game-npc-social/papers/OSSE_SOCIOEMOTION_2009.md)还把内部与表达分开，[CoRE](../../../library/themes/game-npc-social/papers/CORE_EMOTION_CONCEPTS_2026.md)显示分类结构与人类差异，不等于NPC体验好坏。更积极、更信任玩家、情绪类别更确定不是统一成功。短互动、跨会话关系和实际留存各要相应时间证据。

**交互支持同时会改变模型输入。** 比较引导、确认、恢复时保留原始输入、模型理解、可用状态、回应/后果与玩家解释。相同后端不保证收到的意图和历史相同；固定意图回放只证明该表达下能力。将多种支持一起加入只能估计组合效果；两次体验只能观察重复暴露，不能直接分离新奇、学习和剧情熟悉。[E进入设计](../mine-e-player-agency/POSITIONING.md)

**归因、态度与实际行为分开。** [Imitation Game](../../../library/themes/game-npc-social/papers/IMITATION_GAME_2026.md)没有随机操纵来源标签，体验可能反过来影响来源猜测；[AI用途态度](../../../library/themes/game-npc-social/papers/PLAYERS_AI_ATTITUDES_2026.md)研究假想情境，不是实际游玩。不能据此主张隐藏AI改善体验，或未使用自由就证明玩家不需要。

**文献数不等于独立实证数。** [Dramamancer](../../../library/themes/game-npc-social/papers/DRAMAMANCER_2025.md)的demo/短稿合并，Drama Llama与其共享项目谱系且作者样本重叠未知；CoG开放对话与旧学位论文为同一研究家族。目录条目、独立样本、作品和复现分别统计，详见[身份与范围总账](READING_CATALOG.md#mines-2026-10-19)。
