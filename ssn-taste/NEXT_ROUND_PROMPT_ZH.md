# 下一轮 Sasano-Taste 搜索启动提示词（Observation-First）

你现在接手 `Nhckdvrl/ssn-group-papaer/ssn-taste`。

唯一 canonical 方法文件：`SEARCH_GUIDE_ZH.md`。

开局按顺序读：

1. `SEARCH_GUIDE_ZH.md`
2. `README.md`
3. `OBSERVATION_PORTFOLIO.md`
4. `INSTRUMENT_PREFLIGHT_TEMPLATE.md`
5. `SELECTED_TOPICS.md`
6. recent commits

repo 最新状态是唯一正式状态源。

## 当前状态

- selected = 0；
- S01–S12 全部 KILL / cancelled；
- 不允许直接创建 S13；
- 本轮首要任务不是 brainstorm RQ，而是建立 Observation Portfolio。

## 本轮唯一目标

> 找到已经存在、自然、稳定、结果本身有意思，而且原作者尚未把关键 why 做完的 empirical finding。

不要优化用户个人 method-paper / benchmark-gain 偏好；这个文件夹只优化 Sasano taste。

## 严禁开局做的事情

- 不许先想 A/B/C theory worlds；
- 不许先想 mechanism；
- 不许从 old psychology / linguistics debate 直接生题；
- 不许从 future work 生题；
- 不许从 synthetic micro-world 生题；
- 不许因为 exact contrast 没人做就叫 novelty；
- 不许把“两个结果都有故事”当 significance；
- 不许创建 Sxx。

## 第一步：只收 Observation Cards

每张必须写：

1. source；
2. exact result / numbers；
3. natural setting；
4. baseline expectation 及其来源；
5. stability evidence；
6. source author 已解释到哪里；
7. 还剩哪个具体 unresolved point。

优先找：

- 与事前自然预期方向相反；
- direct prior 说 X 关键，新结果说 X 不关键/方向反转；
- strong vs weak / more vs less 出现真正 reversal；
- 两篇真正可比工作结果冲突；
- natural subset 出现 sharp reversal；
- clear capacity / information surprise。

## 第二步：先复现 observation

把所有发现先写入 `OBSERVATION_PORTFOLIO.md`，不要写 Sxx。

候选进入 RQ 之前，默认必须由我们自己用尽可能接近 source 的设置复现。只有原 artifact 已不可获得且有至少两个独立可比来源重复同一结果，才允许把 multi-source evidence 当作替代，并必须显式记录例外原因。

复现不稳定，直接 KILL。

不要把“为什么复现不了”自动改成新题。

## 第三步：才形成 RQ

只允许：

> Observation O 与 baseline B 冲突；我们问哪个自然因素解释 O，或 O 在什么真实条件下反转。

RQ 必须一对一对应 finding。

## 第四步：查 explanation ownership

必须读 source main text、appendix、follow-up。

如果原作者已经完成 observation → explanation → decisive test，KILL。

## 第五步：Instrument Preflight

严格按 `INSTRUMENT_PREFLIGHT_TEMPLATE.md` 建 candidate-specific preflight record。

在 selected 前先证明：

- manipulation 有效；
- readout prerequisite 可完成；
- 等价问法稳定；
- positive/negative controls 通过；
- scorer/parser/ground truth 正确；
- 不需要 prompt sweep。

Preflight 过不了，不允许注册，也不允许先创建 Sxx 再标成“preflight pending”。

## 最终状态

只有真正经过：

> finding → reproduction → surprise audit → ownership audit → RQ → preflight

之后，才允许：

> PILOT-AUTHORIZED

否则全部 KILL。

允许整轮 0 survivor。
