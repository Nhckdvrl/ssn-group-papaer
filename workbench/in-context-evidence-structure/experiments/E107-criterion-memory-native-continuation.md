# E107：交换后的共同标准记忆，能否经原生推理约束私人判断？（2026-10-11）

- **状态：** PLANNED
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

待运行。
