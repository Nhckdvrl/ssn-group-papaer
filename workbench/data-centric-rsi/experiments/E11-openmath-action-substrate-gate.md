# E11 — 公开强教师数据能否提供实质不同且有效的数据动作（2026-10-02）

- **状态：** PLANNED，**执行搁置**；截至 2026-10-02 未下载 OpenMath 数据、未运行脚本或 GPU。下文是运行前原设计，保留供审计，不表示下一项要执行的实验。
- **执行前结构复核（未见任何 E11 数据/学生结果）：** 用户指出连续局部路线没有产生 data improver 的科学证据。复核确认本卡只比较两种公开**静态**数据替换；即使 S/Q 优于金标静态，也无法测反馈是否改善行动、动态更新是否必要、改进器能否迁移。当前对最终目标的信息收益低于先审计一个有可信生成/策展动作与强基线的 substrate。因此暂不按下文资格门下载或开卡；若以后恢复，应在跑前重写它与新的科学问题、反馈闭环和强对照的关系，并保留这份原设计。此处不改变 workbench/idea 状态，也不把未执行卡记作 null 实验。
- **类型/对应：** D1/D2 的 substrate gate；P03/P04，I01/I02 的必要实验空间，不升级 C01–C04。
- **对应：** 原草案对应 P03/P04；运行前结构复核对应 P06。没有运行，不构成任何 C# 的证据。
- **问题与两个解释：** E10 将同一金标静态集从 120 扩到 960 后，学生未更强，错误检索动作仍 110/120 相同。可能当前短程 Gemma2/MATH loop 对更多同类金标题不敏感；也可能真正有效的数据操作是更强教师的**不同解答**或**新问题**，而非扩同类题目。用 ICLR 2025 OpenMathInstruct-2 已发布的 405B 教师数据，把行动拆成“原 120 题换解答”和“换 120 个新题”；两臂都与现成金标静态120比较真实训练后收益。这不是在当前状态自适应生成，不能当 RSI 证据。
- **论文/源码边界：** [P39 全文](https://arxiv.org/html/2410.01560)、[官方数据卡](https://huggingface.co/datasets/nvidia/OpenMathInstruct-2)、[NeMo Skills 数据构建命令](https://github.com/NVIDIA-NeMo/Skills/blob/main/docs/releases/openmathinstruct2/dataset.md)已核。只**使用发布数据**和已审过的本地 `e00_student.py`，不执行/宣称复现其 405B teacher、NeMo full-SFT 或原论文绝对分数。数据 revision 在准备时锁 SHA，记录每个 parquet LFS SHA 与本地文件 SHA。复用 venv `/home/xiang/.venvs/data-centric-rsi`，不新装训练框架。

## 数据资格门（看任何 E11 学生结果前冻结）

1. 从 `nvidia/OpenMathInstruct-2@469216e3f46f4dacf476b382e192485ea51a143e` 的 `train` parquet 分片按编号 00000 起读取，最多四片，预计每片约 237 MB；不足样本则停止，**不临时改到其他数据源/生成教师**。每片全部原始行数、四种 `problem_source` 计数、源文件哈希记录，不下载 12.6 GB 全库。`math` 是原 MATH 题多答案，`augmented_math` 是新题＋多数答案；`gsm8k`/`augmented_gsm8k` 不用于本卡。
2. **换解答臂 S：** 以冻结 `static_120.jsonl` 的前 120 行题面为唯一题目。对每题从 `problem_source=math` 找与原题题面规范化 hash 完全相同且 `expected_answer` 与原金标在官方 math equivalence scorer 下等价的候选。要求每题至少一个完整候选；过滤生成解答在 Gemma tokenizer 下使总训练长度 >1024 的候选，或无法识别最终答案的候选。每题选择与原金标答案 token 长度最接近的一条，平局按 `SHA256(generated_solution)`；保留原题、原预期答案，`response` 由原样生成解答和固定原金标 final-answer footer 组成。若四 shard 后任何题无合格候选，**停止 S**，不以模糊匹配偷偷换题。
3. **新题臂 Q：** 从读到的 `augmented_math` 取题面 hash 唯一、与冻结 MATH train pool/dev1740/test5000 题面精确 hash 不重合、生成解答与其发布 `expected_answer` 末答案一致、Gemma 总长度≤1024 的候选。对 dev1740 再做 char 3–5 gram TF-IDF 最近邻：若最大余弦≥0.80，排除并记录最近邻；对 test 只用事先封存的题面 hash，不读取其成绩/按 test 选方法。剩余候选以 `SHA256("20261002"+problem)` 固定排序取前 5000 个为抽样框，从中按旧静态120逐题的监督 token 长度最近邻无放回选 120，平局按上述稳定哈希；要求两臂总监督 token 与旧静态120相差≤10%，否则该臂不训练。`response` 保留原样生成解答并追加固定发布 expected-answer footer；题面来源/生成解答/expected_answer 原文与 hash 全保留，不因后验学生表现换例子。
4. **数学质量 gate：** 从每臂确定的 120 条里按稳定 ID 排序取前 20 条，逐题查题设是否自洽、完整解答是否真推出最后答案；答案正确但推理错误算不合格，无法核对单独列出而非默认通过。每臂至少 **16/20** 完整可训练才启动该臂 GPU；如果两臂均未过，不跑学生。对于 Q 多数答案本身不是真值验证，不能把 `generated_solution` 与 `expected_answer` 一致误称独立数学正确性证明。审核表在学生评估前锁定，所有失败样本保留。

## 学生训练与读数

- **固定训练：** 每个合格臂从 `google/gemma-2-2b-it@299a8560bedf22ed1c72a8a11e7dce4a7f9f51f8` 原父模型独立 reset optimizer；同 `e00_student.py` 的 LoRA r16/alpha32/dropout0.05、3 epoch、effective batch16、LR1e-4 cosine/warmup0.1、cutoff1024、seed17、120 例＝24 optimizer steps。先不继承 static120 或 static960 checkpoint；原金标 static120 seed17 已存在且未选后验 checkpoint。每例原文、训练 token、是否截断、数据 SHA、配置、源码 git SHA、GPU/CPU/API/wall 全记录。
- **评估主读数：** 只在相同 fvcrc10 A100 GPU0、相同 DataEnvGym 官方 scorer、zero-shot＋显式格式、vLLM eager＋V1 multiprocessing 0、temperature0/max350/full dev1740 上比较；主指标排除预先冻结 72 反馈题后的 heldout1668 逐题准确率。若环境及模型 revision 未变，复用 E10 的同卡 base320/1668、static120 seed17 391/1668 原始预测作为并行基线；新分支完整1740 ID/hash/评分摘要必须验证。报告配对差与题级 bootstrap CI、格式遵守、训练 token/题长、每次成本。不碰封存 test、不用 test 挑配方。
- **阳性对照：** E10 同卡金标 static120 相对 base +71/1668；源 `math` 匹配 120/120、数据各臂无 exact train/dev/test 污染、审核 gate 通过、学生训练和 1740 评估完成。若这些失败，停止解释，保存资产。
- **噪声地板 + MIE：** E08 金标120 三 seed 相对 base +3.66–4.20pp；同卡 eager base 重复文本 SHA 一致，但 E11 的新监督单 seed 方差未知。对 S/Q 相对金标120 的 **≥2pp（34/1668）**、且配对题级 CI 下界>0，才触发固定 seed29/43 两个重复训练与全评；低于此只用于决定动作空间是否有希望，不讲论文方法。重复时要求同方向且报告所有种子，不以最佳 seed 塑造结论。
- **最强混杂：** Q 相对金标换了题、教师、难度/领域分布；S 则固定题但解答形式与可能推理质量变，匹配监督 token 也不是 token 逐一相同。两者均用原父模型、相同训练步、同样例数/提示/evaluator/seed，token 总量控制±10%；此卡只能筛行动空间，不能把 Q−S 解释成“题目多样性因果效应”。作者对公开 MATH test 的去污染不包含我们的 train-derived dev，须重新查本地 dev；0.80 TF-IDF 只能排明显近重，人工审核剩余风险。没有新生成调用，**生成原始成本由公开资产摊销**，不能宣称零生成成本的在线方法。
- **决策表（跑之前写）：** S ≥2pp 且复种子仍胜 → 答案/解答行动值得继续，下一步必须纳入 P38 的强 teacher/response-selection baseline，追问状态改变时真实终端效用而非再改局部概率；Q ≥2pp 且 S 不胜 → 重点转到新问题生成/选择的实质动作，并以 P39 的强静态多样性/teacher 作为基线；两者都胜 → 比同等成本组合/强静态，先测更简单配方是否吸收；两者均不胜或 gate 失败 → 本 Gemma2 短 SFT 设定并非寻找顶会 data improver 问题的优先槽位，审计一次基本训练/格式后转向更成熟的学生/任务，而不围绕这里的微弱差异调参。若只有单 seed 1–2pp 或 CI 跨零，标不确定但不自动扩局部网格。
- **资源上限：** 数据最多约 1GB 下载、CPU 过滤/审核；GPU 初筛至多两条 120 例训练＋两次 full dev 评估，约 0.25 A100·时，若两个均触发复种子最多再四条训练/评估约 0.5 A100·时；总 cap **0.8 A100 GPU·时**，API 0；只用空闲单卡，不跨节点同步。若任一单次训练 >0.3 GPU·时或显存/输出异常，停并保留失败。CPU wall 另计，实际填结果。

## 结果（运行后追加，不回改上文）

- 待数据资格审计。
