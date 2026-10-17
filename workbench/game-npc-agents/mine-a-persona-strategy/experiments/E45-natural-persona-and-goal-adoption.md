# E45：人物指令是否改变新增教学承诺与后续真实行程

- **状态：** DONE；10个新完整后缀与2个复用格全部归档、独立回放一致。
- **类型：** 原生机制探索／普通强基线；不预定新方法。
- **对应：** P11；围绕人物设定、具体社会目标与实际选择，不新建工作台或先挂论文claim。
- **问题：** E44只改上下文，不能证明人物因果效应。本次只干预教授对话阶段的角色描述，观察它是否改变自发／接受的教学承诺，以及这个效应是否依赖已有责任可见。
- **竞争解释：** H1对话中的角色规范影响新增目标；H2缺失的时钟／原责任主导而非该角色描述；H3已有个人经历、其他组件的人设或输出预算／fallback影响。允许原人设很有效，也允许普通事实解释充分。
- **设置：** 复用E35三个既有自然episodes；每个取10:00以后第一次Professor Tanaka structured speak：3501/turn834/prefix79responses，3502/turn787/77，3503/turn754/67。选择只看作者时间与调用类型，不按失败或新结果选state。原地图／schedule／事件／关系／parser／时钟与全部prefix保持，后缀到1200原结束。
- **干预单位：** 仅教授本次及以后对话消息中的`precise and warm with students`改为`precise and reserved with students`；profession／age／解释宇宙的兴趣等保持。世界原角色配置、planner／decider以及已有经历都保留原状。这是同状态／同历史下conversation组件的人物指令干预，不能称完整人格变换或独立Big Five心理构念。没有唯一正确动作／必须拒绝学生的gold。
- **四格：** original/reserved角色指令 × native/clock_and_duty事实输入。两事实句沿E44，并完整覆盖structured speak与原自由文本fallback。3502两个original格已由E44完成；3501/3503各原native source保留，并补fresh native续跑检查A/A层次。共10个新完整后缀，不为整齐扩角色矩阵。
- **读数：** 真实逐句表达／提出或接受的具体活动、outcome里的immediate/scheduled/未变计划、原生成计划与之后实际地点／活动／物品变化，逐actor来源。目标生成与执行分开。语句较短／JSON更易解析、call数量与采样seed的后续分化显式记录，不将parser差归为纯人物战略。lecture/sketch活动不等于物理作品或教学完成。
- **阳性对照：** 三个prefix逐frame/source request一致；原生LLMAgent.converse强制tool=None的CPU检查，确保角色句和事实在两个路径都生效，其他角色／非对话不变；原E44 fresh native三人位置与活动全1200frame同一，文字部分有采样差；完成分支零模型cassette独立验证。编码／实现资格只防错，不是科学bar。
- **噪声地板 + MIE：** 三个固定自然状态、同作者教授、同本地27B，不推跨角色总体或估population CI。seed沿各source seed+prefix call index，未来call数可不同，不冒称整条共同随机数。全部格／case保留，无MIE／比例／去留门槛。
- **混杂审计：** 修改一个描述词可能影响多个语言属性；历史仍带原温暖经历，属于条件性组件效应。goal facts是额外信息。原预算128导致speak失败后的chat redraw是重要替代解释。无新世界规则、奖励或评价阈值；source相同但hardware浮点／采样可能变化，A/A如实记录。当前不以旧研究重叠关闭探索。
- **决策表（跑之前写）：** 角色改变新增承诺而执行随之变→读中介链及信息条件；只变表达→保留正向表达与行为稳定；仅parse/fallback变化→先校正归因；普通已有责任吸收效应→承认context解释。无论方向都不自动提新loss或讲gap。
- **算力预算：** 既有fgvd/deps和27B缓存；初批8个独立单卡workers（21/20各4，均已空闲），两个original worker随后同模型补native对照；最多8物理卡、无跨节点同步、0API／云fallback。复用E44单后缀273秒量级，启动与实际token成本另记；远程采用已核对vLLM eager加载，只有读取方式改变。raw cache/runs/e45_*，不入Git。

## 结果
10个新后缀均完成原1200帧，704次新增本地调用；与E44复用两格合计12格／820次后缀调用。全部新后缀独立零模型回放1200帧一致，原始失败均保留。结果见 `results/E45_complete_persona_context_factorial.json` 与 `results/E45_all_ten_new_branches_independent_replay.json`。

三case方向不一致：3501 reserved两信息条件继续原讲座，original加事实后转向新个别教学任务；3502原人物／信息四格出现交叉，不能用“reserved必然少帮助”概括；3503 original两条件持续讲座，而reserved接受新地点／任务。这里是局部conversation角色指令与整条交互后缀的条件效应，不能单凭一次后缀差推总体因果大小。

POST-HOC原输入重复核对：3501三人位置／活动1200帧相同；3502已由E44核对为1200相同；3503为1095/1200帧三人位置与活动相同，教授活动1170/1200相同。保留采样／数值造成的后缀变异，详见 `E45_fresh_native_nondeterminism_POSTHOC.json`。不估人格总体CI，不升科学claim；E46/47继续区分真实进度与输出协议解释。

运行前资格已完成：3501/3502/3503精确前缀834/787/754frame与79/77/67responses；首次新请求与原source逐消息相同。四格的上游真实LLMAgent.converse强制fallback均验证角色句／事实两路一致，其他角色消息不变，0模型/API。已启动8独立单卡任务；两个original worker随后同一已载入模型补fresh native对照。代码冻结、eager仅改变权重读取，raw启动清单e45_launch_manifest.json。
