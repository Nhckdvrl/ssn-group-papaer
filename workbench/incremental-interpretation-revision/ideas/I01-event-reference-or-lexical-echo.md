# I01：被排除的参与者为什么在下一事件里更容易被预测？（2026-10-05）

- **状态：** PILOT；已收敛到有区分性实验支撑的候选主旨，未认定普遍机制或完成新颖性认证。
- **来源：** P10/P11；驻留E14–E25的事件/患者范围异常，E29方向拆分与E30/E31事前预测检验。研究对象始终是晚来语言证据如何改变角色关系及后续使用；不以GP存在/更多模型生成题目。
- **自然问题：** 旧活动里明确排除了一位参与者。下一次活动开始后，这条信息会让他更不被预测，还是反而成为一种关系备选？这个影响跟着事件、人物还是谓词走？
- **当前候选finding：** 固定Qwen3-8B，具名排他角色事实对患者相对预测的影响在旧event为正、同谓词新event为负；换人物仍负，换谓词后改变方向。中性实体提及不能解释全部结构。显式三类关系判读却容易按旧role方向外推，更受人物/谓词匹配影响，不能用这些不同用途证明一个统一未修订的old belief。
- **拟议论文形态：** 一个角色证据迁移的问题 → 事件/人物/谓词身份的区分性行为证据 → relational aftereffect的可预测边界。不是通用scope benchmark或representation/QA差值论文。

## 最小证据主干

D是“明确允许旧患者−明确排除旧患者”对同一患者相对另一患者的log-probability影响（bits）。负D表示排除条件反而更偏向该患者；它不是accuracy或绝对P变化。所有CI按12verb-family先两source平均再paired bootstrap，不把派生行当独立样本。

| 判别 | 已完成实验 | 主要数字 / 意义 |
|---|---|---|
| 源GP是否必要 | [E29](../experiments/E29-source-ablation-dual-readout.md) | 移除完整S1后，具名原event D+2.65 [1.58,3.65]、同actor新event−1.86 [−2.86,−.92]；scope分类迁移也保留，因此这部分不需GP |
| 一般entity accessibility | E29 POST-HOC完整cell拆分 + E30/E31事前控制 | 新event activity方向翻转，而neutral近0或小；matched-neutral后的主交互仍在。generic表现不同，不能泛称所有措辞 |
| separate字面触发 | [E30](../experiments/E30-event-boundary-versus-participant-contrast.md) | second边界同actor D−1.64 [−2.64,−.80]、换actor−2.11 [−2.90,−1.28]；明确另一event但不需exact separate词 |
| 谓词关联vs一般新事件对比 | [E31](../experiments/E31-predicate-match-versus-narrative-contrast.md) | 同aspect began，同actor同V D−1.36 [−2.33,−.45]→不同V+1.53 [.59,2.37]；扣neutral差+2.50 [1.47,3.68]；换actor差+2.89 [1.72,3.98]。strict9/无odd11同形 |
| 范围推断是否同方向 | E28–E31全映射/R8 | E31同actor正确U同V22.22%→不同V58.33%，paired+36.11 [19.10,52.08]pp；未完全恢复。matched named旧role carryover同V75.71→不同V33.04pp，与患者预测的同V反向作用不同 |

[主统计E31](../results/E31-summary.json)、[native表述分层](../results/E31-nli-wording-summary.json)、[E31图](../results/E31-predicate-transfer.png)。E29实际activity方向拆分、E30 native风格分层均明确标POST-HOC；其后E30/E31对应预测/控制跑前写入卡。完整不利和uncertain分项保留。

## 当前account及仍需区分的解释

| 解释 | 判别预测 | 目前结论 |
|---|---|---|
| 原事件关系未修订的单一信号 | 影响应特别对应旧event/actor，方向与旧关系相容 | 新event具名方向反转、跨actor、无源S1仍在；当前读数不能作为此归因的专属证据，未证明任何隐状态已删除 |
| 一般实体可及性 | activity与neutral响应平行，换V不应改变额外J | E29/E31 matched-neutral交互不支持充分解释 |
| 任意新事件都要换参与者的叙事对比 | 同/不同V都反向 | E31同aspect条件换V改变方向，解释不足 |
| 谓词依赖的关系aftereffect | 同V新event反向、换actor保留、换V减弱/变向 | 当前最匹配的行为account；不等同内部机制证明 |
| 原词/句型检索 vs语义关系记忆 | 换同一动作的自然释义时应有不同迁移 | 尚未区分：E31换V同时改变meaning/适配度，下一决定性测试 |
| only/focus alternative与显式否定形式 | 等价role证据的focus/否定实现应改变aftereffect | 仍竞争；不能将限定模板的结果说成一般语言修订算法 |

**下一最有信息量的动作：** 保持同一动作、actor、活动身份及角色真值，独立构造/审核自然释义，比较原词与释义的患者方向和scope use；配套旧event正/负控制。释义改变行动强度、范围或患者集合的项保留uncertain，不由执行者自判等价。不扩模型/提示词/同义词sweep。

## 与最近邻的距离

| 最近邻 / 已读范围见知识库 | 已拥有的claim | 本候选必须补出的精确增量 |
|---|---|---|
| Van Gompel2006、Slattery2013、Sturt2007、Huang/Ferreira2021、Ceháková2023/25 | GP后结构/semantic persistence、不同final表征、memory与reanalysis竞争 | 不能首次宣称跨句残留；需要晚来role证据在event/actor/predicate边界的方向及用途预测 |
| Sinclair TACL2022、Jumelet2024、Zhou/Frank/McCoy NAACL2025 | frozen LM结构priming、semantic-role预期、lexical boost/IFE | 不能把跨actor/谓词依赖泛泛叫新priming；本线测具体排他角色信息在新event的反向作用，及限定条件 |
| Mann2025、Zhou ICML2026、Lacina2026人类focus alternatives | 否定后词可及性、构造/抑制与捷径并存、备选激活后受context筛选 | 不能卖not-X rebound或双机制；须证明relation-specific而非entity-only，明确event/predicate依赖。focus account未排除 |
| McCoy/Pavlick/Linzen ACL2019 HANS | NLI lexical overlap、subsequence/constituent及negation shortcuts | 不能把native换谓词改善叫新scope机制；这是辅助读数，普通词/极性匹配仍竞争，主干在正常患者预测的scope/predicate方向结构 |
| Hu/Levy2023、Hanna/Mueller2025、Hassan2026 | probability/QA及encoding/access差异 | 相反读数本身不是增量；预测改变须来自同role信息的事件/谓词/人物干预，避免wording pooling伪影 |
| Xu BeliefTrack2026、Hase2024、Chen CMN2026 | 更新/保持/范围隔离、belief一致性、revision与elaboration结构区分 | 不做泛化scope benchmark；不把概率变化当graph rollback；对象是语言角色关系在新事件里如何迁移 |
| Britton et al.2024 discourse connectives | connectives可要求event expectations反转（目前仅primary摘要） | 不能宣称首次context contrast；本线role信息与predicate匹配的具体交互，全文方法仍待核对 |

venue-nearest已回查accepted主会及arXiv入口，仅作定位；检索不完整，没有新颖性证书。公开题材相近不自动关线。

## 证据边界 / 当前判断

- 当前是[C05](../CLAIMS.md) L1固定模型/协议测量。C04的GP历史×表述交互仍保留，与C05无S1的角色aftereffect不能强合为同一机制。
- 具名两个role世界同样提到患者NP及reference对象，避免generic中只有允许患者时才引入NP的巨大salience差；这也是E30/E31跑前选named主读数的理由。所有style全报，不从结果筛措辞。
- 具名与generic不同；源场景24词汇材料、12family不是任意自然语料。新V改动包含meaning/selection；第三审anchor与12个selection-odd意见全部留在预设敏感层。
- native label mapping波动大，definition/query可引发重分析；R8一句scope控制不稳定恢复，不证明一般能力欠缺或预问内部状态。
- E23实际续写错误证据未稳健成立。还需要自然功能用途/独立材料来判断现象的研究价值，不以其缺失桌面判死。
- 现在有具体值得人评估的候选叙事；不自动升PROMISING、改ACTIVE分配或宣称Sasano已认可。后续由区分性结果改进account与定位。
