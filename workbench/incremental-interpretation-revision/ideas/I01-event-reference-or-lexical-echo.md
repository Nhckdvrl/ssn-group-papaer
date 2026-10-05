# I01：角色证据何时反向影响下一事件的参与者预测？（2026-10-05）

- **状态：** PILOT；2026-10-06更新，E43–44反驳普通场景的普遍反转；继续定位必要变量，未找到可确认的顶会主旨。
- **来源：** P10/P11；驻留E14–E25的事件/患者范围异常，E29方向拆分与E30/E31事前预测检验。研究对象始终是晚来语言证据如何改变角色关系及后续使用；不以GP存在/更多模型生成题目。
- **自然问题：** 旧活动里明确排除了一位参与者。下一次活动开始后，这条信息会让他更不被预测，还是反而成为一种关系备选？这个影响跟着事件、人物还是谓词走？
- **当前候选finding：** 固定Qwen3-8B，具名排他角色事实对患者相对预测的影响在旧event为正、同谓词新event为负；换人物仍负。E31原词序下换谓词变正，E32交换事实词序后未普遍变正，更稳的是换谓词使matched-neutral后的预测作用向正方向移动。普通实体可及性解释一部分绝对反向，不能解释全部谓词结构。显式三类关系判读却容易按旧role方向外推，更受人物/谓词匹配影响，不能用这些不同用途证明一个统一未修订的old belief。
- **最具体的当前发现：** 独立同基本动作8family，释义旧event角色作用J+3.93 [3.00,4.91]bits，而换actor新event两fact orders为−2.17 [−3.54,−.95]/−2.14 [−3.88,−.30]。sameActor释义J不确定，但两actor的释义均与不同动作区分。这个行为结构跟着动作意义迁移并受词汇boost/焦点/actor条件影响，不能只称词面echo，也不是单一old truth的沿用。
- **拟议论文形态：** 一个角色证据迁移的问题 → 事件/人物/谓词身份的区分性行为证据 → relational aftereffect的可预测边界。不是通用scope benchmark或representation/QA差值论文。


## 2026-10-06 当前解释优先于以下历史候选
E38独立新选择已知/未知/概率QA可用，不能说功能scope一律失败。E39反身非必要，E40 only/显式not非必要，E41物理再参与条件解除仍反向，E42 native conditional continuation仍反向，均局限描述/报告frame。E43只给一个名字时曝光主导，old J也负；E44普通在场句平衡曝光后old D有效、新other方向不稳定，ready转正。此前“被排除者”并不适用于非排他E40，改称未明确陈述的角色备选。

目前未分清描述NP的语义属性/指称绑定与整段人工frame。原their nephew/brother在新actor下可能另指，不能把字符串一致当实体一致。E45固定E40frame只替换全部候选与target为E43冻结名字，保持actor、event、报告/identity scaffold、两order。其结果决定追referential realization还是frame，不预先制造全局allocation机制。以下E29–33文字是历史候选及保留的局部证据，**不是普通语言transport已经成立的结论**。

## 最小证据主干

D是“明确允许旧患者−明确排除旧患者”对同一患者相对另一患者的log-probability影响（bits）。负D表示排除条件反而更偏向该患者；它不是accuracy或绝对P变化。所有CI按12verb-family先两source平均再paired bootstrap，不把派生行当独立样本。

| 判别 | 已完成实验 | 主要数字 / 意义 |
|---|---|---|
| 源GP是否必要 | [E29](../experiments/E29-source-ablation-dual-readout.md) | 移除完整S1后，具名原event D+2.65 [1.58,3.65]、同actor新event−1.86 [−2.86,−.92]；scope分类迁移也保留，因此这部分不需GP |
| 一般entity accessibility | E29 POST-HOC完整cell拆分 + E30/E31事前控制 | 新event activity方向翻转，而neutral近0或小；matched-neutral后的主交互仍在。generic表现不同，不能泛称所有措辞 |
| separate字面触发 | [E30](../experiments/E30-event-boundary-versus-participant-contrast.md) | second边界同actor D−1.64 [−2.64,−.80]、换actor−2.11 [−2.90,−1.28]；明确另一event但不需exact separate词 |
| 谓词关联vs一般新事件对比 | [E31](../experiments/E31-predicate-match-versus-narrative-contrast.md) | 同aspect began，同actor同V D−1.36 [−2.33,−.45]→不同V+1.53 [.59,2.37]；扣neutral差+2.50 [1.47,3.68]；换actor差+2.89 [1.72,3.98]。strict9/无odd11同形 |
| 近V位置/事实词序 | [E32](../experiments/E32-fact-order-versus-predicate-transfer.md) | 同词袋交换affirm/negate位置，绝对反向更强但neutral也变，sameActor关系特异J不确定；different−same J差仍+1.94 [1.04,2.84]/+2.36 [1.44,3.36]。绝对换V变正并不跨order保持 |
| 原stem还是动作意义 | [E33](../experiments/E33-same-action-paraphrase-transfer.md) | 审计basic clear8的新event otherActor释义J两order−2.17/−2.14bits，较原词减弱+.59/.83；sameActor J CI跨0，但para−不同动作两order−1.70/−1.75bits，皆有paired CI。old event释义控制正、96 unchanged控制drift0 |
| 范围推断是否同方向 | E28–E31全映射/R8 | E31同actor正确U同V22.22%→不同V58.33%，paired+36.11 [19.10,52.08]pp；未完全恢复。matched named旧role carryover同V75.71→不同V33.04pp，与患者预测的同V反向作用不同 |

[主统计E33](../results/E33-summary.json)/[清晰动作图](../results/E33-action-transfer.png)、[主统计E31](../results/E31-summary.json)、[native表述分层](../results/E31-nli-wording-summary.json)、[E31图](../results/E31-predicate-transfer.png)。E29实际activity方向拆分、E30 native风格分层均明确标POST-HOC；其后E30/E31对应预测/控制跑前写入卡。完整不利和uncertain分项保留。

## 当前account及仍需区分的解释

| 解释 | 判别预测 | 目前结论 |
|---|---|---|
| 原事件关系未修订的单一信号 | 影响应特别对应旧event/actor，方向与旧关系相容 | 新event具名方向反转、跨actor、无源S1仍在；当前读数不能作为此归因的专属证据，未证明任何隐状态已删除 |
| 一般实体可及性 | activity与neutral响应平行，换V不应改变额外J | E29/E31 matched-neutral交互不支持充分解释 |
| 任意新事件都要换参与者的叙事对比 | 同/不同V都反向 | E31同aspect条件换V改变方向，解释不足 |
| 谓词依赖的关系aftereffect | 同V新event反向、换actor保留、换V减弱/变向 | 谓词依赖的相对作用获得E31/E32支持，绝对极性随order改变；不等同内部机制证明 |
| 狭义原词重复 vs动作意义相关aftereffect | 换同一基本动作释义，与原词及不同动作分别比较 | E33原stem未复现但otherActor反向及para−不同动作区分保留，exact repetition-only不足；lexical boost、semantic association/contrast仍竞争，未证明内部关系memory |
| only/focus alternative与显式否定形式 | 等价role证据的focus/否定实现应改变aftereffect | 仍竞争；不能将限定模板的结果说成一般语言修订算法 |

E31 POST-HOC具名J的actor匹配差同V+1.81 [1.11,2.53]bits、不同V+1.42 [.34,2.46]，与谓词匹配的负向差并不平行；这提示不能用单一旧关系信号概括，但未证明可加性或内部因子分解。[完整统计](../results/E31-posthoc-identity-contrasts.json)。

**已检验的具体混杂：** E32交换`not X but only Y`为`only Y but not X`，词袋与角色真值相同。同V新event反向保留，故近V的否定对象不是必要条件；但neutral显著改变，differentV绝对方向不跨order保持，不能把词序或focus排除。更稳的证据是各order内different−same的matched-neutral作用差。

**下一最有信息量的动作：** 停止继续改同义词/问答标签，加入真正的解释修订历史。在相同final角色事实下交叉preliminary role（与final一致/矛盾）及其证据状态（事件报道/明确假设性描述），并保留原event final读数、new-event预测和neutral。若new作用只由最后fact模板/普通cooccurrence决定，撤回history和词句匹配的假设性描述应近同；若被撤回关系作为备选被保留，其影响应依赖旧证据状态及对final的冲突，同时old-event final作用可保持。需要pre-update角色读数核对原证据确实可影响模型；不把报道内容直接标成事实、likelihood当belief。新材料先独立审，先写下一卡和互相区分的预测，不扩模型sweep。这是同一个I01的下一科学区分，不是新开generic belief benchmark。


## 与最近邻的距离

| 最近邻 / 已读范围见知识库 | 已拥有的claim | 本候选必须补出的精确增量 |
|---|---|---|
| Van Gompel2006、Slattery2013、Sturt2007、Huang/Ferreira2021、Ceháková2023/25 | GP后结构/semantic persistence、不同final表征、memory与reanalysis竞争 | 不能首次宣称跨句残留；需要晚来role证据在event/actor/predicate边界的方向及用途预测 |
| Sinclair TACL2022、Jumelet2024、Zhou/Frank/McCoy NAACL2025 | frozen LM结构priming、semantic-role预期、lexical boost/IFE | 不能把跨actor/谓词依赖泛泛叫新priming；本线测具体排他角色信息在新event的反向作用，及限定条件 |
| Pucci/Li/Sinclair2026-09 production priming | 结构priming与lexical/semantic alignment共同作用、coherence增强生成复用 | 普通semantic transfer或后续生成作用不是增量；须保留角色证据方向/事件身份的具体问题 |
| Capuano2023 conversational negation alternatives | 语境/合理备选影响否定后的相对activation | 不能首次宣称修正激活备选；source-free C05尚不是真正先错后改的history测试 |
| Mann2025、Zhou ICML2026、Lacina2026人类focus alternatives | 否定后词可及性、构造/抑制与捷径并存、备选激活后受context筛选 | 不能卖not-X rebound或双机制；须证明relation-specific而非entity-only，明确event/predicate依赖。focus account未排除 |
| McCoy/Pavlick/Linzen ACL2019 HANS | NLI lexical overlap、subsequence/constituent及negation shortcuts | 不能把native换谓词改善叫新scope机制；这是辅助读数，普通词/极性匹配仍竞争，主干在正常患者预测的scope/predicate方向结构 |
| Hu/Levy2023、Hanna/Mueller2025、Hassan2026 | probability/QA及encoding/access差异 | 相反读数本身不是增量；预测改变须来自同role信息的事件/谓词/人物干预，避免wording pooling伪影 |
| Xu BeliefTrack2026、Hase2024、Chen CMN2026 | 更新/保持/范围隔离、belief一致性、revision与elaboration结构区分 | 不做泛化scope benchmark；不把概率变化当graph rollback；对象是语言角色关系在新事件里如何迁移 |
| Britton et al.2024 discourse connectives | connectives可要求event expectations反转（目前仅primary摘要） | 不能宣称首次context contrast；本线role信息与predicate匹配的具体交互，全文方法仍待核对 |

venue-nearest已回查accepted主会及arXiv入口，仅作定位；检索不完整，没有新颖性证书。公开题材相近不自动关线。

## 证据边界 / 当前判断

- source-free C05没有asserted initial错误事实，属于首次角色约束的后续使用；它不能单独建立“纠正后的旧关系残留”。下一具体方向是同final角色证据下匹配consistent/被撤回的preliminary report，区分修订history与仅最后fact的focus/priming；不是换研究对象或泛化belief benchmark。
- 当前是[C05](../CLAIMS.md) L1固定模型/协议测量。C04的GP历史×表述交互仍保留，与C05无S1的角色aftereffect不能强合为同一机制。
- 具名两个role世界同样提到患者NP及reference对象，避免generic中只有允许患者时才引入NP的巨大salience差；这也是E30/E31跑前选named主读数的理由。所有style全报，不从结果筛措辞。
- 具名与generic不同；源场景24词汇材料、12family不是任意自然语料。新V改动包含meaning/selection；E33八family是场景内basic动作匹配，不是无条件严格同义，4个related family也全部评分；第三审anchor与12个selection-odd意见全部留在预设敏感层。
- native label mapping波动大，definition/query可引发重分析；R8一句scope控制不稳定恢复，不证明一般能力欠缺或预问内部状态。
- E23实际续写错误证据未稳健成立。还需要自然功能用途/独立材料来判断现象的研究价值，不以其缺失桌面判死。
- 现在有具体值得人评估的候选叙事；不自动升PROMISING、改ACTIVE分配或宣称Sasano已认可。后续由区分性结果改进account与定位。

## E45–47 当前实验解释（优先于历史主旨）

E45 propernames在固定frame仍newother D−13.545/−12.625bits，但old absolute D近0/负，不能直接叫old正/new负。E46 8cells找到了具体调节成分：identity主newSame D−6.556 [−7.935,−5.254]、identity×event−3.335 [−4.091,−2.500]，identity对new−old J−4.357 [−6.206,−2.434]；unused report非必要，E44/E45重复2304target drift0。还不知道身份断言地位、词串还是额外entity/actor曝光驱动它。E47冻结asserted/unverified exact quote/name inventory/absent，两event表达、两order全部测；先修复引用标点并全量外审v2，未按结果调整材料。一般global suppression已有Tang ICML2026 owner，一般next-mention/discourse preference已有Upadhye等owner；这仍是候选精确语言条件，非已认证好idea。GUM现成natural identity/reference资产已审，下一自然材料是检验同一个问题，不能因为有了新数据就换对象。
