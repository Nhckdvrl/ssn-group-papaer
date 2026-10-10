
# PAIN_LOG — In-Context Evidence Structure

| ID | 日期 | 痛点 / 压力 | 影响 | 下一动作 |
|---|---|---|---|---|
| P00 | 2026-10-05 | order sensitivity 已有大量文献；ICLR 2025 已直接提出 invariant ICL | 不能把 permutation variance 当 paper object | 仅作 stationary calibration |
| P01 | 2026-10-05 | ICLR 2026 / regime-change work 已占 nonstationary recency/change-point | 不能写“LLM 应该忘旧规则”作为 novelty | 与 exchangeable/noise 条件交叉，研究 adaptive structure inference |
| P02 | 2026-10-05 | sequential-correlations work 已占 effective context length | correlation 只能作为后续 pressure family | E02 先做 noise-vs-change |
| P03 | 2026-10-05 | Jiao 2026 已占 single corrupted demo + internal conflict mechanism | isolated conflict/position heads 不是我们的 lead | 用其 task 只做外部 calibration |
| P04 | 2026-10-05 | 最大 reviewer compression 风险是“InvICL + nonstationary ICL 拼表” | 必须形成一个结构选择量或 predictive account | E02 直接比较 four accounts 与 exact meta oracle |
| P05 | 2026-10-05 | NFS 读权重约 40 MB/s，32B 首次加载 ~25 分钟 | 32B 实验排队变慢 | 小模型暂存到 `/tmp/xiang_hf/hub`（`scripts/stage_model.sh`）；32B 依赖页缓存 |
| P06 | 2026-10-05 | StepFun 先误用现金账户接口（`/v1`），额度耗尽 | 审计中断、产生现金费用 | 改用 Step Plan（Credit）接口 `api.stepfun.com/step_plan/v1`；只审计真正构造的数据 |
| P07 | 2026-10-05 | 自然标签词的置换/翻转映射难学（semantic anchors） | K 类置换 allA 准确率仅 0.16–0.34 | E25 只作方向性证据；二分类用 base 间平衡的翻转 |
| P08 | 2026-10-06 | 同一张卡放两条排队脚本，交接时两个 32B 同时加载 → OOM | 两个 32B 任务失败重跑 | 同一张卡只放一条队列 |
| P09 | 2026-10-06 | 远程命令中 `pkill -f <模式>` 匹配到自身 shell，把新启动的任务一起杀掉 | E37 一次重跑实际未执行 | 不在同一命令里先 pkill 再启动；按 pid 停 |
| P10 | 2026-10-06 | 锚点 value 投影初版乘了每次运行的 1/rms | 跨提示比较被缩放污染，初版数字作废 | 投影方向只乘 norm 权重，rms 另存（健全性检查：旧锚点逐位相同） |
| P11 | 2026-10-06 | 真实多标注者数据（DICES）评分者噪声大 | 交互泄漏无法与“无交互可学”区分 | 暂不做真实标注者版本；需结构更清楚的 perspectivist 数据 |

| P12 | 2026-10-10 | E56逐层query模块超过single-source参照、E56c同时换任务与词表 | “只修好source路由”与“证明纯词表依赖”归因不成立 | E58/E59拆表示与因果中介，E60固定任务与词表操纵，E61交叉K/KV |
| P13 | 2026-10-10 | 来源影响主要由答案前query位置的消息传递；只看末位label attention漏掉约41–61%的源交换效应 | E55“native默认不用来源”诊断范围不充分 | E63/E64逐步扩展干预scope，阳性控制逐位重建；精确path待核对 |
| P14 | 2026-10-10 | 外部float32 QK重算虽平均误差小，最坏SDPA重建相对RMS=7.2% | E63首轮组件干预VOID | 改原生eager attention weights/V，全重建RMS=0；同seed重跑，作废目录保留 |

| P15 | 2026-10-10 | E66 bf16整段/分段推理评分差可达1.625nats；mask泄漏为0仍不足 | 切KV缓存的科学归因会混入分段精度变化 | 首轮VOID，同seed全float32校对；发现max差4.01e-5，任何后续都先过no-op，精度范围明确 |
| P16 | 2026-10-10 | E72 direct短预算在single/entity也截断；E73严格parser漏掉加粗最终答案 | 生成低分混合了未完成、格式与判断错误，不能定位绑定能力 | 共同采样轨迹预算核对48次全一致；保留strict结果，装饰校正标POST-HOC，独立确认前冻结parser |
| P17 | 2026-10-10 | 正确词从其它来源读入，不必等价于借用其它来源的映射关系 | E48的foreign-label贡献能否单独证明rule leakage仍需任务条件 | E74缺失Source×category组合，枚举函数约束、owner-only与foreign-only反事实；正控有效后才拆word/relationship来源 |
| P18 | 2026-10-10 | E76 unseen query恒为demo中点，且x+b没有Source-specific Input斜率；正确Source响应可由Source label均值产生 | 不能将Source方向阳性称完整Input×Source程序；确认高accuracy亦未过门槛 | E77用copy/9−x、每Source相同label边缘与全0..9 queries，区分seen/interpolation/extrapolation、Single/Mixed/Direct |
| P19 | 2026-10-10 | E78交换定义块，mixed subtract插值96.1%→25.0%，single亦有强偏好变化；规则识别/执行部分gate失败 | E77的函数类别不对称不能当稳定Source组成机制；中间code涨分已有直接COLM2024近邻 | 不铺本组“知道却不用”patch；先把private函数参数与共享输出词典的证据角色分开，E79仅先behavior有效性 |
| P20 | 2026-10-10 | 人审计后的核对：旧D0 prefix读数实际为Mark；output Source排名只测contrast符号；公共偏移可以减少平均mass | 不能把“码更显眼”或accuracy/ranking分离直接当访问/选择机制 | E81按actual码位置对齐，全query钳制m/pi，固定kind翻Source；64新contexts确认carrier外读取有独立效果，保持C20 L1 |

E90对P13/P20的更新：Source组内读取与rule信息的功能依赖不是同一读数；signed平均影响为0也可掩盖context间正负抵消。原24→48方向没有确认，之后新增幅度观测在32新contexts冻结确认，原结果完整保留。single上的同一模块+27.6点说明Source排除不能唯一解释E56。后续不为这项区别继续拆mask矩阵，回到共享Task信息与私有输出映射的内容解释。
