# 有限重建验收：没有获得论文项目通过证据（2026-10-03）

> 关闭后保留的历史证据：2026-10-03用户决定终止；原始输出、数据和实验runner现已删除。文中local raw路径为历史定位，不能再逐条重算；最终汇总保留。代码可从关闭前Git快照51a578c1追溯。

**建议冻结本项目的继续自动投入，保留核心复现、数据与输出，交人决定正式状态。** PROPOSED未擅改；没有训练、新数据生成、API judge或邻接题材扩展。本轮E65–E68全部完成，新推理合计 **0.3822 GPU·小时**，未以占满八卡当进展。

原自然问题没有被证明无效：同一候选含义随语境变化，有原人类评分，也有可用模型入口。**但“可以测”与“找到值得投稿的结构”是两件事。** 本轮没有找到能排除一般答案变化、跨有效读数/独立材料迁移、超出parent解释的条件规律。

## 1. E59收尾：不是已有发现只差包装

只用原150 development项目、68 Source组；65 evaluation未使用；两固定5fold来源划分、三表述、两个入口/完整和内容读数全部保留。小映射只拟合DPO软分布，没用human标签拟合。

| 聊天/full表述 | 实际human距离增量 | global偏置+尖锐程度对identity的OOF预测误差减少 | 残余距离增量及来源CI |
|---|---:|---:|---|
| W0 | +.3128 | 96.25% | +.0040 [−.0044,.0124] |
| W1 | +.3419 | 93.23% | +.0078 [−.0276,.0793] |
| W2 | +.3771 | 90.92% | +.0189 [−.0274,.1173] |

第二split对应96.25%/93.20%/90.96%；预定六项资源验收全部满足。CI条件于固定OOF fit、不含refit或训练种子；不宣布残余等价零。

**支持：** 一个跨未拟合来源的低维全局响应映射足以预测主要阶段差，不能把距离均值恶化直接解释为语用能力下降。
**不支持：** DPO完全忽视对话、只改一个固定类别偏好，或拟合参数等于内部criterion。constant参考比直接沿用SFT更差；pure bias只减少40–62%误差，sharpness在W0/W1尤其强。映射仍依赖SFT每题的对话分布。

C03原任务观察保留L1；**语用论文线索优先级降级并收尾**，不再复杂拟合救叙事。[E65卡](../experiments/E65-global-answer-transport.md) · [全量结果](../results/E65-global-transport-summary.json)

## 2. 现成人类条件桥梁存在，但不是许可gold

原ImplicatureX 271项目：scalar46、discourse31、synthetic144、natural50。原过滤逐项精确复现 **2285评分、76保留参与者**；542 item-condition格各3–5评分。重复item-condition-worker=0，同worker见同一item两条件=0；不是人类within-worker配对。

公开raw attention记录88人，论文招募数90；不伪造两人。Likert 1–7原量尺、individual z、人类人口分歧与模型候选概率分开，不线性换成true probability。

仅去除显示标签/标题、scalar单说者前缀后，243项q/场景两侧presentation-normalized匹配；28项版本/拼写/标点差异逐条保留。**进一步UI检查发现其中16项的`<laughter>`/`<noise>`等注释模型看到字面token，但人类innerHTML可能隐藏cue名；243不是完整视觉刺激等价证明。** 保留原冻结243cohort，另报227无此风险的技术敏感性；不是根据模型效果筛项。见[UI风险](../results/E66-ui-render-risk.json)。

原human取消评分均值下降：scalar −2.648、discourse −1.741、synthetic −3.091、natural −1.586（原1–7尺度）；255项下降、14上升、2相同全部保留，不能只留“取消成功”项。

32项固定source-stratified语义pilot由root盲于E67输出审读。存在事实反驳、撤回依据、范围例外、主观判断、说者belief/commitment、计划变化；不该硬混成unlicensed/not-q。**这不是独立人类裁决**；三态gold与全量语义层次仍未裁决。baseline/cancel有原human norm，derived prior/negation/strengthen/irrelevant没有相应norm。[E66卡](../experiments/E66-canonical-human-condition-audit.md) · [覆盖/过滤/文本汇总](../results/E66-canonical-human-audit.json) · [语义pilot](../results/E66-semantic-pilot.json)

## 3. 同一阶段pair的条件检验：没有识别能力归因

补跑与E59相同OLMo2-13B SFT/DPO，canonical baseline/cancel、两order、parent/一句format恢复，原common tokenizer/template/FP32；八独立shard共4848预测、0.3619GPU·小时，源/token/数值gate通过。

| format端点 | 明确affirm/deny控制 | natural候选mass | median order差 | 预定综合gate |
|---|---:|---:|---:|---|
| SFT | 114/128（89.1%） | .926 | .259 | 失败 |
| DPO | 97/128（75.8%） | .969 | .147 | 失败 |

对错误先作实现检查：完整唯一key、p_true逐项label反转、概率和/FP32 padding/source/token parity均过；没有生成parser。DPO控制失败集中在明确affirm：两order13/32和20/32正确，deny两order均32/32；这提示偏向/任务解释仍混杂，**不能把控制失败讲成语用能力或新角色问题**。

243冻结cohort的OOF global映射对identity误差减少80.84%/80.80%；添加cancel字段未改善，human变化特征相对global只改善1.95%/2.30%（相对加cancel模型为2.64%/3.06%，不能混分母）。按order分别是约63.6%/86.6%，human特征order1相对加cancel模型改善约6.0–6.7%，order2反而恶化。**没有跨order稳定的证据结构；gate已失败，不能越过它宣称能力不变/criterion shift。**

CPU r1发现WSJ同文章片段不能按item当独立group，r2按article整组修复；unknown article统一组。r1保留隔离，原输入/读数不变。r3补UI风险敏感性，原243与271均保留；r4补齐原约定KL与相对global分母，fit不变。单source现象不报退化CI，共享human raters额外不确定性仍未计。[E67卡](../experiments/E67-canonical-stage-response.md) · [完整r4结果](../results/E67-canonical-stage-summary.json)

## 4. 正常端点存在，不等于本轮有novelty

复用原Qwen3-8B/14B自然输出，仅补512缺失控制预测（0.0203GPU·小时，E68标POST-HOC于E67），不换natural提示、不加模型/数据。

格式控制8B **128/128**、14B **127/128**；mass>.999999、order median差<2e−7。原入口控制并不全过且候选mass很低，仍保留。已有natural format语境响应均值8B −.2739、14B −.3446，human raw相关rho=.254/.282（243冻结cohort；不把相关叫机制）。227 UI风险敏感性为−.2765/−.3624，rho=.252/.253，不能替换主结果。227的stage global误差减少81.11%/81.13%，human相对global仅2.42%/3.37%改善，没改变受限结论。

这支持“同一q对原有语境变化有可描述响应”，反对“整个territory无法测量”。它不提供阶段算法归因或二分类规范；普通撤回、prior、现象差异已属ImplicatureX等parent对象，**目前没有改变其科学解释的增量**。[E68卡](../experiments/E68-cached-endpoint-controls.md) · [完整结果](../results/E68-cached-endpoint-controls.json)

## 5. 验收与停止条件

- E59竞争解释完成收尾；不保住能力下降故事。
- 核心条件桥梁已实际核对/测量，不再笼统以“没有human数据”拖延。
- 原正常端点可测，但新阶段pair未满足归因gate，且没有稳定的新条件预测结构。
- 未识别必须补某类新材料才能区分的稳定竞争解释，因此本轮没有启动生成/新human规范。
- 不新增训练、SAE、角色/信任/社会评价/噪声修复，也不继续调提示直到gate通过。

**建议：冻结本项目的后续自动投入。** 这是有限可行性检验的投入判断提议，不是agent用“有人做过/天花板不够”自动关闭territory。原自然问题仍有意义，现有资产仍可复核，但当前没有成熟论文idea/叙事；正式冻结/重开由人决定。重开应有具体的新证据或能排除现有竞争解释的自然对照，不以换模型、换metric或更多调用量为条件。

核心raw审计和推理在`/data1/xiangding/work/pragmatic-inference-calibration`，不进git；脚本/冻结卡/小汇总进入main。没有恢复已删除的额外扩展数据。
