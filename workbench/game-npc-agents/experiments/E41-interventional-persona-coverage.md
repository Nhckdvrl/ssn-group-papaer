# E41：干预覆盖与普通等义增强的等预算控制（2026-10-14）

- **状态：** RUNNING；执行／编码资格完成，六个等预算300轮任务已启动。
- **类型：** EXPLORE；I03的研究动作，不预设新loss。
- **对应：** I03／P10，衔接E34/37/39/40。
- **问题：** 单C功能控制与文字稳健性需要哪种经验：普通等义表述，还是独立变化C与其他特质／身体的干预覆盖？
- **比较：** 原E34 NoInfoNCE为baseline；新增surface-only NoInfoNCE与C-intervention NoInfoNCE，三固定seed42/43/44、原300iterations／每轮25600transitions／所有PPO及diversity设置不变，从同初始化训练。先NoInfoNCE避免1200变体造成contrastive候选数量／false negative差异；不把读出提高当控制效果。
- **surface设置：** 每原episode选择相同16背景／body／goal；用独立augmentation RNG对每NPC选原canonical或E26整句顺序翻转，episode内固定。既有正确编码，不调用LLM生成。原400canonical保持逐byte，diversity reference pool仍原400。
- **intervention设置：** 同原sampler的16 base角色，将其原C值在这16人之间随机置换，因而每episode C边际完全相同；不改其他四traits／年龄／职业／身体需求衰减／preferred_actions。只更新原persona.big_five.C及作者模板文字，源style／social奖励照原函数计算。该训练配置干预不是修改世界规则或评价。最多400×3=1200 C输入，原C编码仍直接用E34原数组；新800及canonical数值重复用同本地.6B／正确pool编码。
- **split：** 原20训练非C背景与5测试非C背景完全独立，所有编辑后的held背景仍不入训练；职业／年龄的源切分按原协议，不宣称新职业独立。只读取held metadata核对隔离，不能据test结果选训练。
- **执行资格：** augmentation=none必须复现原E34初始参数及first rollout全部obs/actions/reward；surface保留所有body/goal；C干预逐episode C计数同一且body/prefs逐项同一。独立augmentation RNG不消耗原sampler RNG。新编码保存文本／hash／token长度和canonical-repeat误差。
- **读数：** 固定E34 native mixed utility／needs、E32等义与跨角色响应、E33完整利益四格、E37同状态同幅度利益方向；300轮为完整预算，30/100只描述形成，不挑最佳checkpoint。保留成功与负结果；若简单增强解释充分，承认而不造方法。首批不以η未训练分数判能力。
- **阳性对照：** 上述逐byte重放、参数／source reward路径资格；canonical original输入精确不换码，C相同的变体精确复用；原作者动作空间与合法执行闭环。
- **噪声地板 + MIE：** 三训练seed／原三world全部保留，数值重复与采样方差分别记录；不设MIE、通过率或科学淘汰bar。
- **混杂审计：** C重排同时改变多NPC偏好配置，允许真实social反馈；边际与body保持但不能把全部长期效应归单一actor。source C的心理构念不独立验证，使用的是作者明确的utility参数。普通surface增强是已有方法对照，C干预也可能只是一般数据增强；新颖性须靠形成机制和跨任务预测继续建立。
- **决策表（跑之前写）：** 读完整轨迹／指标后区分表述覆盖、属性组合覆盖和形成路径；充分考虑普通解释。任何结果都更新认识而非按bar舍弃。必要时再研究训练机制，不先规定损失。
- **算力预算：** .6B数据编码一张已有空闲GPU，白天总≤8；训练先精确CPU单update计时，沿E34同小MLP CPU更快的事实，最多6独立单core CPU任务、每task完整300轮约1.5小时（以实际为准），不新建env，0付费API。raw既有cache/runs/e41_*。

## 结果
none路径与E34相同初始policy及25600首轮obs/actions/reward逐byte相同（21.50秒）；1200 C输入的400原canonical完全复用，800编辑与400重复编码共9.17秒，重复cos最小.99999105。20训练／5held非C背景交集0。六个source300轮训练任务在既有CPU环境运行，保存30/100/300全部checkpoint；原生CNN评测使用八GPU，训练小MLP沿实测更快的CPU路径。结果未完成，不提前判方法。
