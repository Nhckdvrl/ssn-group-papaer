# E18｜Utility-Gated Recovery：更新、反馈、重规划还是保持不动？

- **状态：** RUNNING；两任务四response与扩六response均完成；接续恢复能力探索，不训练router。
- **对应：** I11 / R5。
- **来源：** S19–S20；这是第二波方法线。
- **阳性对照：** no-shift / in-distribution条件下HOLD应有竞争力；明显shift下至少一种干预应优于HOLD，否则recovery set本身无效。
- **噪声地板：** deployment start/state、shift instance、train seed、router split分开；同一fork使用common random numbers或尽量相同随机性。
- **决策表（跑之前写）：** utility router优于固定策略→扩task/shift；某固定策略统治→保留简化结论；fork labels噪声过大→增加重复或缩小intervention set；未来信息泄漏→作废该router。

## 核心问题

world model出现异常时，哪种intervention真的提高未来closed-loop utility，而不只是降低instant prediction error？

## Stage 0｜Fork ledger

在可重置环境选择预注册decision points。对同一个model checkpoint与environment state建立matched continuations：

- `HOLD`：不更新，按原planner继续；
- `FEEDBACK`：只更新latent feedback / observer state，不改参数；
- `SHORT-UPDATE`：用最近真实transition做1–K步轻量梯度更新；
- `EXTRA-REPLAN`：不改模型，只增加candidate/horizon/replanning compute；
- `FALLBACK`：若已有简单policy/short-horizon controller则加入。

每个fork记录未来H_eval steps / episode return / success / failure，并计算相对HOLD的 `ΔU`。

第一轮只需HOLD + 2种最容易实现干预，不要求全五类。

## Router features：只允许部署时可见

### 2026-10-02 无训练fork pilot（运行前）

动机：E13在两任务远goal上的self-consistency refinement没有收益；E16固定bank的regret也未支持“排序修正”解释。下一步改变**反馈/重规划设计**，不再局部调selector。

复用E13 A2锁定的75-step goal anchors，各task前32个预定episode，不按失败或结果筛选。使用同released Fast checkpoint、β=0、native macro rollout(3×25steps)与CEM N300/K30/30，先规划完整75动作，执行共同25步prefix。fork点在step25；若此前已成功，完整保留并标无需干预。

同fork比较HOLD（原剩余50动作）、FEEDBACK（真实当前pixel替换预测state，重新规划2×25剩余动作，N300）、EXTRA-REPLAN（同feedback，N900）；三者不改参数，剩余environment budget均50。这是feedback+replan组合，不把差值单独归因observer correction；首轮不训练router、不称新颖feedback方法。追加一种对照 PREDICTED-REPLAN（用预测step25 latent重新规划N300，不使用真实当前pixel），分开搜索更新与真实反馈。

跨两个conditions：no-shift action gain1.0与共同prefix第10步起gain0.7（fork前已有可见作用）；PushT使用relative action接口才允许action gain，否则拒绝此shift。所有干预面对相同gain/同prefix commands；selector/features不可输入真实gain或future utility。每task32×2conditions×4continuations，环境最多约25,600steps+prefix重放controls；模型不训练，单GPU。

公共prefix在fresh reset/public setter后执行；各continuation用同reset seed+完整prefix replay恢复fork的完整**本次生成**physics memory，state/pixel一致性需控制。不能声称恢复原dataset完整memory。部署features：step25 prediction/observation latent residual、可见goal progress、初始elite margin；future utility与特权state只用于离线标签。对已成功prefix与所有失败均保留。

主读数：native success、剩余50步的native task distance/return、对HOLD的配对help/harm与episode bootstrap CI；condition/task分开。另报重规划calls/candidates和fork replay开销，GPU非独占则降级timing。native-cached cost需H1/H2/H3一致性控制；动作长度必须75=3×25、remaining50=2×25。若fixed FEEDBACK普遍更好，先沿固定策略发展；若compute/feedback只在部分state值得，再扩ledger/shift或utility controller。不能因为firstpilot无utility异质性而关闭R5。

候选：
- recent prediction residual；
- ensemble / bootstrap disagreement；
- CEM elite margin；
- candidate rank instability；
- goal progress / stagnation counter；
- support/OOD proxy；
- previous intervention response；
- remaining compute / interaction budget。

禁止：
- fork未来return；
- privileged hidden state；
- “哪种干预后来最好”的真实标签直接在线输入。

## Baselines

1. ALWAYS-HOLD；
2. ALWAYS-FEEDBACK；
3. ALWAYS-UPDATE；
4. ERROR-THRESHOLD；
5. CHANGEPOINT detector（适用时）；
6. ORACLE-FORK（只作上界）；
7. learned / rule-based utility router。

## 训练方式

先把fork ledger当监督集：
- binary：best intervention vs hold；
- 或multi-class：HOLD/FEEDBACK/UPDATE/REPLAN；
- 或直接回归每种intervention的 `ΔU`。

第一版优先浅层模型，避免router本身成为主要算力/容量来源。

## 主读数

- closed-loop success / task cost；
- intervention count；
- extra model calls / gradient steps / wall-clock；
- real-environment extra transitions；
- utility gain per intervention；
- false-positive update cost：本来HOLD更好却触发干预；
- false-negative cost：需要干预却没触发。

## 确认范围

至少包含：
- no-shift ID；
- 一个dynamics shift（friction/action scale/layout等）；
- 一个model-error/stagnation自然失败子集。

如果router只在人工shift有效、自然失败不泛化，就明确限制，不包装成通用trust mechanism。

## 最近邻压力

- Feedback WM已经证明feedback-state correction有价值；
- WorldAgen / AdaJEPA类工作已做test-time update；
- CAWM做shift detection + replay forgetting；
- Counterfactual Utility Protocol已经证明“update本身可能伤return”，并提供update-vs-hold fork measurement。

因此E18的潜在新点是**从fork utility学习intervention selection**，而不是再证明某一种adaptation有用。

## 结果
首轮四response与扩六response均已运行，见下方记录；无科学主张升级。

2026-10-02首轮native cost正控因missing candidate axis在模型接口处停止，尚未执行fork/candidate银行；failure与源码留存。修复直接native scoring的显式candidate axis，保持全部seed/inputs/主读数，以s0-retry1重跑。该接口失败不是科学null，不覆盖原run。

### 2026-10-02 recovery set扩充（运行前）

首轮两task×32goals×2gains×4interventions已完成：no-shift TwoRoom HOLD12/32→FEEDBACK16/32，PushT4→7、EXTRA9；gain0.7时TwoRoom6→7，PushT1→0。全部40,696执行/重放steps，fork state/pixel error0。不能从这组方法推断“恢复不可能”；尤其面对未知动力学变化，单纯换成真实当前state没有改变错误transition。

接续同一64锁定goal/相同initial75-step plans/同step10 shift onset，不增加新goal、不按结果挑任务。扩 **SHORT-HEAD**（只更新action encoder）与 **SHORT-DYNAMICS**（action encoder+predictor，encoder/projectors冻结）；均使用fork前最后3段5-step真实pixel transitions与名义commands，frozen encoder target，16 AdamW updates/lr5e-5/WD1e-3/clip1、native prefix MSE，无privileged state/gain/reward输入，不读取fork未来。仅有3个新样本，可能过拟合，失败也全部保留；这是固定response的探索，不宣称新训练配方或普适update增益。

六方法同batch比较HOLD/PREDICTED-REPLAN/FEEDBACK/EXTRA/SHORT-HEAD/SHORT-DYNAMICS；每fork重新clone原权重、params更新不跨episode/condition污染。adapted dynamics在原latent坐标规划剩50steps，N300，与FEEDBACK额外search一致；单列16 gradient steps/更新参数数、所有policy总计算和physical steps。原基线HOLD/FEEDBACK同初始plan重算作控制。目标是比较**信息反馈 vs transition update vs search**三个设计，不先训练router，也不只研究一个gain值的阈值。后续确认需自然错误、别种dynamics shift、原任务保留与独立checkpoint。

### 六response实测（2026-10-02）

[完整summary/config/hash](../results/E18_20261002_short_updates_seed0.json)，768 continuations、59,459执行/恢复steps，fork state/pixel差0。顺序HOLD/PRED/FEEDBACK/EXTRA/HEAD/DYNAMICS，每组32：TwoRoom nominal12/13/16/15/12/12，gain0.7为6/6/7/7/9/6；PushT nominal4/6/7/9/6/4，gain0.7为1/1/0/0/1/0。HEAD对FEEDBACK在nominal导航help0/harm4（−12.5pp CI[−25,−3.125]），shift导航help2/harm0（+6.25pp [0,15.625]）；不是跨seed稳定增益。

HEAD更新1,802,848参数，DYNAMICS更新10,826,272参数；均16steps/3 prefork transitions。导航shift的prefork fitting MSE中位0.06331→HEAD0.00504/DYNAMICS0.00474；这只拟合已有3样本，不是held-out预测证据，更不证明长期任务效用。当前短适配没有强恢复signal，不增加router复杂度。

RTX重算512条旧baseline的success全部相同，但4条重规划的完成步数及部分distance不同（max15.39）；HOLD步数全一致、距离差≤2.3e−13。prefork latent特征跨GPU也有差异，不能写成逐轨迹/特征完全数值复现，或混A100/RTX时间。新增方法的配对判断用本次同RTX baseline。保留全部原始输出、同initial plans与public-setter限制。


### 2026-10-02 P08/R5 连续适配pilot（运行前）

从AdaJEPA的recent-history/one-step-per-MPC/reset策略与adaptive MPC借方法，不称完整AdaJEPA复现。旧短更新只训练5-step前缀并一次fork；新比较预测模块/表示readout在持续真实反馈中的效用。不先造router，不先按短loss判update有益。

两released Fast，各锁g25前16；nominal、driver gain0.7、task-specific physics（TwoRoom每command加[.15,0]再native clip，无滤波记忆；PushT block moment×2、mass不变，reset恢复），shift onset0。模型看issued nominalcommand，不看shift/真实物理参数。3methods：FROZEN / DENSE25-PREDLAST / DENSE25-PREDLAST+PROJECTOR；PREDLAST为transition_stack最后层/norm/output_proj及pred_proj，PROJECTOR为MLP readout，不是ViT最后层。记录模块名/参数数。共288episodes，总budget≤50；common nominalH25/N300 plan首5步在条件下真执行并完整重放一致，absorbing首5成功保留。

此后每5steps同N300/K30/30/H25重新规划，执行首5。更新用最近≤25真实commands和每5步raw image，对所有合法source→已观测future directprefix等权MSE、target detach，无padding/future标签。t5/10/15/20/25共有1/3/6/10/15pair，**只有t≥25存在真实25step目标**。每决策1 fresh AdamW update/lr5e-5/WD1e-3/clip1，evalmode BN固定；每episode完整clone/reset参数+buffers，projector变后重encode全部buffer/current/goal，不缓存旧latent。t50无未来执行不更新。

主读数为每task/condition成功、vs frozen help/harm/paired episode CI；距离、pre-update fitting loss、updates、encoding/gradient/search时间分别报告，不能把训练误差降低当效用。各method每决策同env/CEM预算，adaptation额外compute不称equal-wallclock；native wrapperallclose、source不变、BN固定、prefixtarget count和5step重放为正控。只一releasedmodel/task，16episode CI条件于该model；普通条件可能成功ceiling/更新机会少，报告机会数。源25动作在各条件下factual replay只作诊断、特权状态仅恢复，不进部署feature。

决策表：适配跨physics类改善且ID无显著伤害→独立head/episode确认与跨goal冻结复用、第二任务/新shift；局部fit改善但future弱→比较低维系统辨识/action-map、数据激励或cost/proposal，不连续调lr；readout有益但不能保留原任务→明确reuse问题。raw `20261002-E18-continuous-adaptation-RTX-s0`、单授权空RTX，完成自动复制durable。


连续pilot运行前物理干预校对：原PushT mass+moment同比例×2在锁定16 factual25轨迹的10D状态逐步差全0（15/16实际接触），构成无效transition干预；未用于任何GPU适配比较。CPU1200steps对比发现moment-only×2在15/16改变轨迹，故运行前修订为moment-only。这是按是否真实改变transition的干预正控，不是按适配效益选择shift；全部16保留。原实现/轨迹/诊断保存，[校对](../results/E18_20261002_physics_preflight.json)。E18等待queue仅在未运行时停止，修订完成后重启。


### 连续适配全288episodes（2026-10-03 JST）

[config/hash/summary/controls](../results/E18_20261002_continuous_adaptation.json)，14,313执行/诊断/重放steps，common prefix state/pixel误差0。FROZEN/PREDLAST/PREDLAST+PROJECTOR顺序、各16：TwoRoom nominal10/10/9、gain.7=8/8/9、wind=8/8/9；PushT nominal5/4/3、gain.7=3/4/3、moment×2=3/2/3。没有稳定成功增益，不能转成update普遍无效或完整AdaJEPA反驳。Pusht更新有distance退化；success与distance分开汇报，fitting loss不作utility。

此前E17 sameg25前16整25执行ZERO300为导航13/16、操作14/16，本次每5反馈FROZEN10/5，但两次plannerseed不同（68000/78000），**不能直接归因feedback**。新增共同初始plan、commit5/10/25和shift-warm控制已先写E13卡；若差由cold optimizerrestart解释，先加强MPC baseline，再研究update；如果仍有差，继续分辨预测对象、执行承诺、隐藏速度/反馈state替换，不预选narrative。
