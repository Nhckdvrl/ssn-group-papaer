# E08：同题字母概率与选项文本似然（2026-10-02）

- **状态：** DONE
- **类型：** REPRO / measurement control
- **对应：** C01、P03，E06/E07的elicitation替代解释。
- **问题（一句话）：** 同一道自然MCQ上，生成、字母概率、完整选项似然是否给出一致选择？
- **解释与设置：** A符号/生成绑定loss；B任务prompt影响选择；C选项长短/copy likelihood产生排序差。Qwen2.5-3B-Instruct与Qwen3-4B各1,200原题，在native user文本及仅追加E06格式指令两种prompt上获取下一token ABCDE条件概率；原MCQ模板下逐选项完整文本likelihood（累计与per-token均记录）。Flan-T5-XL英语300题提供另一family，原encoder文本无chat。模型revision沿用E02/E03/E04；Qwen enable_thinking=False。逐选项文本从原(A)…(E)边界解析，逐条断言无缺选项。
- **读数：** native/format letter accuracy与distribution，text累计/per-token accuracy；每项原始logprob/长度/选择、原生及format生成对应选择（若有）。前12项batch1/16概率校对阈值1e-3；不比较概率总值与generation accuracy当同构量。
- **阳性对照：** 1200个源prompt每个5选项解析断言；字母one-token断言；teacherforcing严格assistant prefix；前12例batch parity、parent game评分与oracle controls。
- **噪声地板 + MIE：** deterministic/frozen，按item bootstrap2000 draw seed0。option length/copy是待审混杂，均不能解释为知识增强。无FPR/SDT与能力MIE。
- **混杂审计：** 原MCQ含所有候选，text likelihood可受copy/length影响，不叫Hu&Levy意义的direct knowledge。只比较同题同模型的readout；tokenizer/endtokens/prompt/scriptSHA冻结。先检查parser/label平衡/截断/顺序，再解释任何逆转。
- **决策表（跑之前写）：** A字母与生成一致、text不同 → scoring/copy/length先审；B native/format字母变化 → elicitation，不归representation；C所有一致 → 暂削弱这套readout混杂，不预设必有anomaly；D解析/parity失败 → VOID并修复，不能解释科学现象。
- **算力预算：** GPU6/7两Qwen并行，GPU4 Flan英语；≤0.5GPU·时；有界单卡独立。实际待记录。

## 结果
子agent请求重连没有落盘/进程，root接管。本卡先于运行；不覆盖E02–E07。

### 数值控制失败，先审bug
两Qwen的BF16 batch1/16 option cumulative logprob误差分别max0.8547、4.6246，未通过原卡1e-3阈值；这些text likelihood选择不能解释为能力/criterion。先按已定义numerical controls固定首末项检查FP32/关闭TF32、原generate与forward、padding与token对齐，不改阈值救结果。概率差异来源待查，全部raw保留。

### 修复路径冻结
固定首末题FP32且关闭TF32：Qwen3的batch cumulative delta .000206/.000153，Qwen2.5 .000080/.000126，均通过原1e-3阈值；该控制支持数值精度/计算路径是主要替代解释，不是语用finding。完整1200两model按相同prompt/metric重跑FP32，保留所有旧BF16为VOID text evidence；仍做前12项batch控制，失败不改阈值。原生成与intrinsic logits还可能不同：Qwen2.5默认repetition_penalty需独立核对，不把二者等同。

### 补充校验，先冻结后运行
FP32重跑同时补齐字母概率首12+末1题的batch1/13 padding对照（native/format均测，prob delta阈值仍1e-3）；Flan英语首末题逐选项batch1/5累计似然对照（阈值1e-3）。失败则相应readout不进入解释。E04首末题额外固定repetition_penalty=1，检验Hu raw logits与generate概率差是否由继承的generation policy造成；这只是实现校验，不修改已保存的原读数。

### Flan decoder padding校对
补充首末控制发现T5 text batch parity未过阈值。代码继承encoder左padding到decoder labels；shift_right后前置pad decoder步数依其他选项长度变化。修正为target right padding，并保留原T5累计/per-token读数为VOID；固定首末逐选项控制通过后才用相同英语300题重跑。字母概率独立控制通过，不据decoder修复重写字母历史。
