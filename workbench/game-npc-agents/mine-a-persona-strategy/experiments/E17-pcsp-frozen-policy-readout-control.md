# E17：PCSP 冻结政策的独立读出训练控制（2026-10-14）

- **状态：** DONE
- **类型：** REPRO / 机制校准（P06；不是重新发现作者internal/external差异）
- **对应：** E08 / E13 / C01 / P06。
- **问题（一句话）：** 作者InfoNCE消融的persona检索下降，有多少需要实际NPC政策改变，有多少仅需要轨迹encoder学会匹配既有persona projection？
- **设置：** 官方PCSP pin5420f7b…，公开v3-large full/no_consist seed42/43/44及原500 Qwen embedding。先seed42完整native episode核load/成本；policy与shared projection完全冻结，只训练原TrajectoryEncoder读取no_consist原生轨迹匹配该固定projection。政策原train400；读出训练320、校准80，test100只最终使用（沿作者独立probe拆分），自然原world/reward不改。每人2train/val episodes与3test episodes，原200cycles/32agents/batched-before-cycle actor选择，native完整轨迹CPU生成。固定训练seed171717，Adam原traj_lr、原InfoNCE温度，batch32不同persona，1000updates；每100updates用校准80检索选checkpoint，全部迭代保存train/val读数。先seed42；若会改变研究判断再43/44确认，不能只保留最好seed。
- **读数：** 原full与no_consist encoder、no_consist冻结政策+校准encoder的100候选top1/3与按persona簇bootstrap95%；φ/θ参数与native obs/actions byte hash前后严格相同，外部行为/任务reward因此不应改变。原行为评估的trait构念diff属于作者，本文不冒领。成本/失败记录。匹配projection的检索仍不是独立人物效度。
- **阳性对照：** 公开weights/embedding严格load，原native actor→AEC→needs/reward episode与精确重放；encoder训练loss可下降且φ/θ无grad/无weight变化；原full encoder应明显超过100候选随机1%，否则先报告资产/协议不匹配。
- **噪声地板 + MIE：** 冻结no_consist原encoder为读取基线、full为正控制；固定subset/seed/selection规则，不以test挑epochs。若readout-only实质恢复100角色检索（≥full一半且高于1%chance），说明metric改善可不伴随NPC决策改变，后续做更强因果路径分解；若恢复不明显，保留shared projection/policy变化解释，不宣判InfoNCE无效。精确identity、trait/原型识别、utility任务表现分开。
- **混杂审计：** full/no_consist投影空间不同，分别用各自原φ目标，不交叉错误空间；η只在320拟合。current native env与历史训练reward版本仍有E08阅读债，不声称整篇全部复现。trajectory观测可携带persona定义的needs-decay/social环境信息，因此高检索未必来自action；恢复后必须排除body/state vspolicy路径，不能只给新loss名字。不同decoder训练机会/额外离线预算全报告；此控制是解释论文指标，不把它自动当新科学创新。
- **决策表（跑之前写）：** readout-only恢复→独立定位“可恢复性”与“政策形成”，设计排除state-body路径的最小实验；未恢复→保留InfoNCE共享projection的实质因果作用；full正控制失败→先修复asset/protocol，不偷偷换checkpoint；结果已由作者trained audits充分覆盖→承认ownership，仅更新baseline认识。
- **算力预算：** CPU轨迹≤30分钟；单GPUdecoder≤1小时，优先fgvd+overlay，07:00起本项目≤8卡，0付费API；原始模型/轨迹在cache不进Git。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
尚未运行。

首个训练前发现protocol单位差异：原consistency helper把32同人物agent的AEC帧顺序拼为一个trajectory，再截前200；原trainer按单actor储200步。E18先做原helper逐byte正控制与focal/peer因果归因，避免E17拿不同观测单位作不公平readout复现。E17仍未做decoder训练、未见test结果；补充为训练/校准native数据按预定seed随机混合cohort，避免固定persona排列提供新的索引shortcut，原protocol单列控制。

首个native成本gate核验修正：当前v3-large源码N_AGENTS实际为16，非预估32；原helper200-cycle产生3200帧，截前200约12.5 cycles。上面的32数字是运行前估计，实际manifest/所有物理执行以未改源码16为准。E18 all-A与原helper全部obs/action逐byte一致；首个A=f401的own200正确识别401，joint前200识别同原型另一职业412。固定f401/peer427后，own识别同原型409，joint识别488。此时不支持“角色控制丧失”；单位/职业粒度/群体内容必须分开解释，尚无新科学claim。

seed42首个控制完成：original full reader own200的100-ID top1 .0667/top3 .1467；no_consist原reader .0100/.0333；只训练η .0367/.1200（top1 persona簇95%[.0167,.0600]），1000update/val80选checkpoint，train320/test100没有用于调参。φ/θ hash前后d625c380…相同；native rollout与reward不变。reader恢复部分，不足以证明全是读出解释。训练/评价单位与原joint-prefix不同，原指标完整保留E18。seed43/44确认已启动，故当前仅seed42，不宣称跨训练种子。

全部三公开种子完成：seed42/43/44 原full top1=6.67/3.67/2.33%；原no_consist=1.00/2.00/1.67%；冻结θ/φ仅训练η=3.67/4.67/4.67%。各自模型hash前后相同，三份native cache不改，selection固定val80而非test。结果见results/E17_readout_only_seed42.json、43.json、44.json；读出可学习解释部分指标，仍不能证明人格语义有效或InfoNCE政策路径没有作用。C01 L1，新科学增量0。
