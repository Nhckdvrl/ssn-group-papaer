# E107：交换后的共同标准记忆，能否经原生推理约束私人判断？（2026-10-11）

- **状态：** DONE-PILOT
- **类型：** PILOT / 内部memory interchange的自由续写
- **对应：** I04、C16/C20、P17。
- **问题：** E105直接结束thinking并读取Answer logits的接口，是否漏掉了后续计算对criterion信息的使用？

## 为什么现在做

E105标准16/16正确，但交换后在直接评分处会输出EOS（after13/128、before17/128、explicit25/128），并非大小写parser问题。opposite mixed after37.5→56.25%、margin+0.442nats有部分作用，显式Rec对照却不可靠。这不支持稳定criterion程序，也不应从关闭thinking的读数判它不能用于原生推理。本项只让同一记忆自由继续，不换来源、材料、层、标签、cue或alpha。对应Thought Anchors的干预后自由续写思想，而非再设计提示提升分数。

## 设置（运行前冻结）

沿E105全部4context和16完整teacher原生标准轨迹，不按成败选择；E95匿名input-label相同、来源分组确定共同criterion。Owner只有Dana的concordant例子，自己的p_R从原始labels推断，teacher始终无future Review。Teacher private p_T=-p_R，两方向p_R都覆盖；这是最有区分力的opposite-p子任务，same-p不执行也不外推其表现。

E105的prefix、before/after/explicit真实历史、Rec+conv交换全部保持。唯一消费者改变：去掉人为追加的关闭think与Answer前缀，让未来assistant在原生thinking开头自由生成。它不提供额外criterion或私人偏好，receiver的KV、Own原文与newActor信息仍不变。Rec可能含teacher事实，不能称teacher完全缺席。

BF16/SDPA原生生成，同checkpoint/openslime+vendor，greedy，1024 token；所有截断均用实际混合cache继续2048，绝不从纯Owner raw prompt重放而丢失干预。generate cache可能少最后生成token，续写必须以cache实际seq_len与完整已生成IDs消费尚未缓存token。FP32 E105与BF16 E107不直接作数值差的因果解释，比较E107内部匹配before/after。

每context：Own8、full cue Owner16；Rec before/after/explicit各16（p_R×c×4新输入、p_T=-p_R）。4固定分片各一个context，总288请求，所有invalid/仍截断保留。额外self-copy重复不纳入主要288分母。

## 读数、阳性对照、噪声地板 + MIE

完整生成的最终yes/no，使用原E95 parser；读CoT只作线索，不以其文字当忠实电路。主要opposite mixed after−before、各条件全部/同向/mixed准确率、完整四输入函数、c双向profile、teacher整函数、EOS/unknown与截断率。

- 完整Owner cue应可靠；Rec explicit作为自然消费者下的同接口参照，不设必须满分的新门槛。
- source cache指纹不变，KV精确来自Owner；48linear真实消费initial_state。自copy重复整生成序列必须一致，首step logits max≤.001。
- 第一条cued Owner cached manual suffix与generate实际首step对照，核对真实prefix/cache消费；uncached/full首step差报告，BF16不据微小margin升级。
- MIE是criterion×Owner-private-p完整功能profile与匹配after−before，而非next-token文字改变。

## 混杂审计

自由thinking可以新增计算，阳性证明恢复状态对后续算法有作用，不证明在E105时完整程序已存在。不同长度的Rec与Owner KV组合可能离开原生分布；before/after整历史同时变了目标、CoT、答案词，仍不定位某一步推断必要性。same-p未运行，结论限定opposite-p；但两个p方向、四输入和两criterion world可排除整teacher函数与常数输出。未知与截断不删除，不能只在合规subset报告高准确率。

## 决策表（跑之前写）

| 结果 | 更新 |
|---|---|
| after出现稳定criterion×Owner-p而before弱 | 后续原生计算能利用标准推断历史中的共享信息；下一步未选新材料确认并与E106形成机制综合，不继续接口搜索 |
| before与after都可靠 | 原始示例状态已有可用共享信息，不支持必须先报告标准；问题转向消费者何时调用 |
| after/explicit仍弱或主要EOS/teacher函数 | 这个跨记忆接口不足以给原生共享标准提供可靠解释；结束其consumer扩展，保留有限效应，回到完整示例中的形成与应用 |
| 三者仅改善同向、mixed不随c | 主要私人映射/输出校准作用，不能叫criterion运输 |
| carry/数值失败 | 保存失败并修同执行，不变科学变量 |

- **算力预算：** ≤4GPU·时，4独立单卡固定分片；实际待记录。
- **资产：** results/e107/，原始token/JSONL/cache本地，小analysis/run/audit入git。
- **状态边界：** 正式I04/ACTIVE、C16/C20不改。E105保留全部原读数，不事后重定义其准确率。

## 结果（运行后追加）

主要480/480＋extra self controls4，0未知，8分片正常结束，共4.48472 GPU·时。16完整Teacher标准轨迹全部保留。完整Owner cue64/64；rec before mixed33/64=51.56%[50,54.69]，after36/64=56.25%[51.56,60.94]，explicit39/64=60.94%[50,71.88]。after−before +4.69[0,9.375]pp，explicit−before +9.375[−3.125,21.875]pp。same/opposite与完整profile全部见analysis；opposite after−before仍0[−9.375,9.375]pp。

三种Rec条件同向输入均64/64保留Own私人映射。固定teacher、翻Own p的192对tensor检查全部通过：Teacher Rec逐字节同，Own KV不同；两p均正确率before68.75%、after70.31%、explicit73.44%（含同向输入），答案翻转率约84–86%。Own证据确实参与，不能只用复制Teacher C解释全部输出；但这不构成独立criterion子空间，也不排除校准/选择teacher整个函数。

生成consumer的cached manual与generate首step精确一致、自copy整轨迹和logits0；48linear恢复状态消费检查通过、pristine caches不变。BF16 full/split首step词表差.787–1.289nats、首argmax相同，数值限制完整报告；这里只比较匹配cached路径，不与FP32 E105当同一路径数值等价。Private p两world跨同GPU重复Teacher缓存hash精确一致。

更新：自由推理消除了E105的EOS，但仍没有可靠criterion执行；主动标准报告没有形成显著的before/after转换。保留有限正作用与私人映射证据，按照决策表结束此consumer/Rec运输扩展，不扫更多site或Goal。这个阴性限制接口，不证明全模型不存在规则信息或不能共享。C16/C20与I04正式状态不变。

results/e107/merged/{analysis,completeness_audit}.json；每part/same的numeric_audit/carry_audit/run保留，小文件入git、原始CoT/JSONL本地。

### 解读结果前的配置补充：私人偏好必须独立于teacher状态

原opposite-p设计有明确替代解释：teacher三人中C的完整函数为−p_T*x[c_T]，它恰好等于所有opposite Owner的目标。两个p方向不能排除复制C整体函数，故原卡“排除整teacher函数”的措辞不足。当前仅看运行进度/unknown，未查看Rec正确率或选择world。原288结果保留。

补充全部same-p condition：在每个固定teacher c_T/p_T/阶段，另用p_R=p_T的Own KV，与原p_R=−p_T比较。teacher Rec+conv的真实tensor hash必须跨两次运行相同，Own KV必须不同。所有ctx/四输入不筛；新same-p三阶段共192请求，另每part一条self-copy校对（额外4，不进主要分母）。合起来主要480＝原288＋same192，teacher p与Own p完整2×2，额外self controls4。

在原GPU同checkpoint/软件/precision上顺序跑supplement以避免硬件与private关系共线，比较原/补的teacher tensor指纹。若固定teacher而Own p翻转，完整函数也按Own p翻转，才支持Own证据真实参与；仍可能通过选择/校准teacher整函数组合，不称独立criterion子空间。预先补读数：每ctx/teacher c,pT下Own p两world都正确、四query函数均正确，以及混合输入c两world都正确；全部unknown保留。

代码scripts/e107_same_private.py另冻结，原正在运行代码不变。same补充后必须整体评价，不只用opposite成功作新主张。总预算增至≤6GPU·时；不增加Goal、layer、cue、alpha。此补充服务于原问题中“保留自己的私人映射”，不是完美机制的新关卡。
