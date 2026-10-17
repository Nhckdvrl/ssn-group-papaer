# E40：文字偏好控制与真实需求反馈（2026-10-14）

- **状态：** DONE；三个完整300轮种子的540个原生episode完成。
- **类型：** EXPLORE／原生机制控制；不新增训练，不预设persona失效。
- **对应：** I02／P06；E27证明文字与身体信息并存，E37/39显示功能方向随人物／训练不同。
- **问题：** 单C文字编辑的原生作用，是否取决于角色身体工作需求的真实反馈？普通C值标注能解释多少？
- **竞争解释：** H1，背景依赖的文本／projection绑定；H2，训练中C与工作需求衰减相关，政策还依据实际需求轨迹；H3，两个目标本就常兼容或行为有替代性。三者可并存。
- **设置：** 沿用E33原五held背景／15固定同伴／3固定world33011–13、200cycles、source20合法动作及双原生reward环境。E34三seed42/43/44的Full/No完整300轮，默认plain+原body已在E34评价。增加：plain+工作decay取作者C_low值；plain+工作decay取作者C_high值；clarified+原body。不是自造映射：从原test/train JSON核对C→work decay唯一值，原值low=.7／mid=1／high=1.3。只改persona已有body参数，世界规则／实际收益函数／其余属性／preferred_actions／同伴不变。
- **普通说明控制：** 复用E33已编码的原句“In this game, the character’s Conscientiousness (C) is high/low.”，准确称C状态标注，不冒称已给了最优动作或完整收益信息。plain／clarified均保留；不因少于几个人物“过线”自动触发。
- **原生闭环：** 每input在同body、目标C_H/C_L的两个source环境执行同一实际动作tape，逐步核物理相同，得到两text×两reward完整四格；不同body的世界允许按真实反馈自然分叉。记录needs／positions／obs／all actions／native rewards。
- **阳性对照：** 初始观测不包含body参数，两个body在相同seed下的首focal obs与首cycle动作应逐byte相同；差异只能在需求更新之后出现。新body值恰等于原body的四种背景，必须恢复E34原plain轨迹，逐字段核对。源双reward物理parity继续保留。实现核对不等于科学bar。
- **读数：** 全部四格return／need后果／实际action变化、首观测和动作分叉时间、文字效应随body改变的差；逐人物／训练seed／world呈现。clarified作用与body反馈分开，不以DD正向替代总utility受益。
- **噪声地板 + MIE：** exact replay／首cycle控制及全部3seed×3world变异；不设MIE或比例通过率，不筛成功种子。
- **混杂审计：** C-only的body反事实不叫新正常人格或心理效度；游戏作者BF既影响style奖励又影响需求衰减，分开机制正是问题。source身体参数干预可影响未来能力／状态，不能把return变化全部归给语言偏好。先看原生成功、失败与利益相容的情况，不强制唯一动作。
- **决策表（跑之前写）：** 依据文字×身体的完整交互解释H1/H2/H3；普通标注若足以解释则接受；若body通道解释，讨论游戏反馈怎样参与角色形成；若仍有跨背景可预测的错位，再考虑机制或训练。没有科学淘汰条件。
- **算力预算：** 三CPU任务各顺序三条件、180episodes，预计约3分钟/seed；0新GPU/API。原E34评价harness保持原文件，不在运行中修改；新wrapper只在本进程persona配置入口注入body参数。raw既有cache/runs/e40_*。

## 结果
全部540个原生episode完成，结果见 `results/E40_need_dynamics_i300.json`。真实身体反馈与原C标注作用存在背景／种子异质性，没有一个通用恢复结论；不据此淘汰研究线或升级能力主张。
