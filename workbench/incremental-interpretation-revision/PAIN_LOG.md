# PAIN_LOG — Incremental Interpretation & Revision

| ID | 日期 | 痛点 / 异常 | 复现条件 | 影响 | 下一动作 |
|---|---|---|---|---|---|
| P00 | 2026-10-05 | 直接近邻很强：ACL 2025/2026 已覆盖 GP 难度/人机比较；ACL SRW 2026 已覆盖 recovery dynamics；Findings ACL 2026 已覆盖 delayed lexical disambiguation mechanism | 文献定位 | generic GP/ambiguity story 会被立即压缩 | 把 GP 固定为 calibration；novelty 必须来自 revision structure / condition / consequence / account |
| P01 | 2026-10-05 | E00 question-type 与答案极性完全混杂（simple 全 Yes、GP question 全 No） | 276 upstream QA / 69 sets | simple>GP 不能单独证明 GP-specific 能力损失 | 主检验同题 GP/nonGP 配对；E01 构造要检查极性与语义判定 |
| P02 | 2026-10-05 | Jurayj 实际 43/19/28；blocker 与 verb substitution 不是统一的同义操作，部分 MV/RR passive 不自然 | pinned TSV 全量 audit | 自动生成会误标 gold 或把语义变化当修订响应 | 逐条审计 canonical variants，报告词汇和结构条件，保留排除记录 |

| P03 | 2026-10-05 | E00 同模型 GP effect 随 reg/rev 反向；16-prefix pooled −2.81 pp，prompt range 65.22 pp；repeat probability drift 0.0865 | 全量 E00、原协议/原生 chat/一句恢复对照 | positive control 不稳定；用户已取消以此停步的gate | E03 已确认FP32下反转；E01测这种顺序差异是否改变具体语言证据的作用 |

| P04 | 2026-10-05 | 1.7B 重现正方向 +19.84 pp，但 nonGP lingering accuracy=30.71%；raw specificity DiD CI 跨 0；No 的含义/输出标签/语用补全未区分 | E04 全量固定 protocol | 方向复现不等于 GP-specific interpretation instrument 已有效 | E05 改 response label/明确 assertion meaning，原题/gold 不变 |

| P05 | 2026-10-05 | Amouyal hyp5_14 simple 题写 tomato 而句子 tomatoes；hyp5_18 题问 floor 但句子 road；Jurayj 原句 had rode / burglers / boooks，部分构造主动诊断缺论元 | 逐条输入校对，全部在对应新推理之前发现 | 发布数据也不能当作 gold oracle；旧复现保留字节/标签，不能事后悄改 | E06 全69 + 事前登记67-set source-question clean；Jurayj 对称 quarantine / 不可用诊断标记；raw留cache |

| P06 | 2026-10-05 | E06 GP main-subject角色控制0–5.80%，object No题最高100%；nonGP两角色正确且event初始Yes组合31.88–47.83% | 全69 sets、两order×一句恢复；67 clean同结论 | 单个role-No/event-No不能当revision proxy；问句任务影响与语用补全仍竞争 | 用户要求继续系统观察；E01实际VP锚定+native boundary，全部配置报告，不选prompt赢家 |

| P07 | 2026-10-05 | 去掉prefill/示例仍保留巨大顺序交互；题先GP拒绝initial更多，但simple final回答更差 | E07完整4416评估，69/67sets | “拒绝初始命题”可能是回答默认值/任务影响，不能单独等同修订 | E08固定最终目标题，相关/极性对应无关focus×before/after区分reading goal与回答启动 |

| P08 | 2026-10-05 | E01无歧义NPZ extension也降低原短NP角色支持（NPZ:1 blocked约1→.040、nonGP约1→.119），final semantic约1保持 | 独立free外审snapshot1、neutral/reg/base，gold=null | 不能把role下降直接归为digging-in；短NP引用与完整subject、一般NP复杂度竞争 | E11先外审head/full-span与isolated控制；三源组pilot，不把测量修复称novelty |

| P09 | 2026-10-05 | E12 earlyQ sourceGP−cue disamb交互+1.47 bits，但主要cue词更易预测−2.22；原cue答案反而下降，aggregate/逐项不等价 | E10同prompt源word概率+原QA，24clusters、base/repair | 不可把GP差值变大叫承诺加深；也不可用易预测当已正确理解 | 下一步没有诊断Q的自然后文功能依赖，区分question reactivation与input-history影响，先用已发表原材料 |


| P10 | 2026-10-05 | 初始事件常未assert但未exclude；Slattery原22字面ref后文仅7明确episode，11generic/4modal | 独立Luna关系/temporal scope审核，任何E14推理前 | initial Yes及后文surprisal不能直接等于同一事件未改绑；extra event/semantic expectation仍竞争 | E14普通叙事same/separate activity×患者continuation，预先报告episode与全source分项 |

| P11 | 2026-10-05 | E23 free continuation的首NP不一定是活动患者，后面可能又有finite verb；明确否定/纠正也不能只按首词判角色 | 224 greedy、匿名完整二审：首审10→次审6contradiction、12label disagreement，unknown84/88；48token cap全体 | 不从首NP/单一teacher错误率升级false belief，功能读数不足给C04加能力结论 | 两套审计及bounds均保存；E24用独立source检验C04概率预测，另需合格的角色使用场景，不扩sampling找错误 |

- 2026-10-06 / P11追加：E43/44普通名字语言transport未支持普遍角色反转，neutral subtraction在old也负；原模板描述/报告frame、possessive重绑定与正常叙事偏好仍竞争。E45只改指称NP，必须先逐条whole-input审核，不以more-model或subset显著来避开反证。

- 2026-10-06 / P11追加：E50列表joint41.41%、anchored普通复述98.05%，同patient列表特别差，但原two names/entities可诱发distinctness预设。E51固定全部facts，比较neutral joint/role-keyed/count与repeat恢复，不能先称内部role失效。

| P12 | 2026-10-06 | Step Plan批量完整JSON协议未能稳定完成：E51每批24回答，39/192批完整；108 max_tokens、45 schema/覆盖失败；E01亦61/626未完整 | 原请求/响应/manifest全保留，无新调用 | 未完成不是semantic通过；成功批不能代表总体，E51不能给最终语义结论 | 用户暂停，不重试；恢复后先解决批大小/协议完成性，不能以无脑更大token重跑替代原因分析 |

- P11暂停补记：E51去two-names仍有literal同patient劣势，但正确description与错误Name格式、count的name-string解读必须分开；外部全量审核未完成。当前不扩大sweep、不升级能力/novelty。

| P13 | 2026-10-06，2026-10-07纠正 | Amouyal部分GP命题只是未被断言；原问答将non-entailment记No，不能把这直接换成世界矛盾，也不能据此否定源理解错误 | D0及E59完整三族源支持测量；原公开数据审计保留 | 撤回原“约一半GP错误不是GP效应”的推断，比例没有对应因果比较；MVRR明确源支持/文字答案后仍有37.1–63.8pp配对差距 | 同时报世界E/C/N与源支持；继续研究关系修订的跨用途与选择性，不收窄到两个literal-C组 |
| P14 | 2026-10-06 | E24–E51 共 28 个实验复用同一批 24 句（12 族），只用 Qwen3-8B；而 Qwen3-8B 在反身 Subj/Obj 上几乎没有 GP 差距（47.7% 对 51.8%） | 实验卡与公开结果审计 | 设计空间被压成一个点，每条主张只有 4–12 个 cluster | EXECUTION_BRIEF §6：≥3 族、≥2 构式，禁止单模型连锁实验和旧模板扰动 |

| P15 | 2026-10-06 | 取消客户端请求后Step服务端仍占并发，后续请求429；旧driver把429当semantic失败立即拆单扇出 | E52 step-full-v2/v3 raw/request与interrupted.json | 总本地并发≤8不保证服务端已释放取消请求；429不是标签 | E52 v4有界传输退避、保存每次response、暂用4并发；不给429消耗语义重试或通过计数 |

### P15：语法voice被误当语义agent（2026-10-07）

E63完整T4固定顺序抽查中，department was merged→department merged被第三遍仅凭主动形态判施事；inchoative merge仍可描述patient经历合并。不是原始可信benchmark要逐条重审，而是新输出的role判定存在具体shortcut。v1保存；E63/E64所有MVRR packet按role-v2澄清双遍重审，E53随后同规则处理；非MVRR既有完全相同packet复用。未改类别定义、模型输出或QA；语义角色必须由实际词义/论元赋值决定，模糊情况OTHER。MVRR旧role数字在v2前暂定，QA不受影响。


## P16：原question_target不是预期修订操作标签（2026-10-07）

- E65后完整输入核对发现：INITIAL GP目标NPZ72No/17Yes，NPS35No/1Yes，MVRR27No，NPVP26No；FINAL GP目标NPZ88Yes/1No，NPS26Yes/10No，MVRR8Yes/19No，NPVP23Yes/3No。cue对应数量同样。原initial/final只是位置/关系标签，不能自动命名“撤销旧关系/建立正确关系”。科学输入资格/原gold/Step标签无改动，不是要重审成熟数据。
- POST-HOC的输入定义分析：完整all之外同时输出initialNo_finalYes、initialYes、finalNo，并按eval gold Yes/No拆开；保留原完整主结果。首次拆分晚于E65效果，早于E66完整效果和E67角色效果，明确不冒充事前层。不是按成功效应筛样本。
- 收紧的是解释命名：某个问题涉及早期关系未必就是初始误读，对最终区域提问也未必确认正确关系。只有实际问题内容/源支持模式相符才可检验对应入口假说；输入定义层依旧不能把prompt语义当内部状态。

## P17：完整角色正确率不能定位部分修复（2026-10-07）

E64-v2所有两用途结果闭合后，以输入排序首2 MVRR源核对三族四bank文本：某些输出已经改对V1受事/被动关系，仍把V2附着到错误内层NP。旧CORRECT_ROLES要求全部源关系，作为联合读数没有错；但用它的null断言“哪个角色完全没改”不成立。保留全部T4-v2、原S/Q/gold、模型输出和原主图。后续E70以前向模型效果后登记的POST-HOC测量，用原公开多问题投影自由表达中的具体源断言，分别报告恢复/未断言/多断言，不拿全部No当关系恢复，不改旧资格、不选择修补成功文本。V1语义patient与主动语法形态的P15澄清仍适用。

## P18：共同关系回答增加正确关系与源未支持关系的断言（2026-10-07）

E72现成175对/350源三族四构式，NPZ No/Yes65组中initial正确概率−16.22/−9.99/−25.21pp、final+12.78/+3.36/+20.62，所有六CI分离0。cue亦有损伤，其它構式/真假模式异质；不能叫GP专用机制/内部解析。真实痛点是共同用途没有实现共同修订，可能是首答案串联，也可能joint问题/一般Yes启动。E73以同任务正确首答案prefill、唯一首label消费cut区分；0API/不改原数据，完整图和卡是证据。
