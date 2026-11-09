# E182：文字切换代价的词表载体与语言距离标尺——塞尔维亚语 + 乌兹别克语双文字，字母 / 无字母 token 分开（2026-11-09）

- **状态：** PLANNED（11-09 写定"设置 / 读数 / 决策表"，在任何 E182 采集之前；跑后不改；结果见末节，事后分析标 POST-HOC）
- **类型：** CLAIM-确认（E180 两条 POST-HOC 线索的预登记确认运行；[DIRECTION](../DIRECTION_2026-11-06.md) §17.1 的决定）
- **对应：** CLAIMS C25（语言专属路由跟文字，L1）的两个待确认限定：(L1) 训练路由器超出几何零模型的部分偏向文字；(L2) 文字效应由带字母的 token 携带。另把"文字切换代价"放到语言距离标尺上（E180 hin↔urd 语言身份胜、塞语文字胜，需要分级而不是二元）。
- **问题（一句话）：** 在多语 MoE 里，"同一语言换文字"造成的路由差异是否只出现在带字母的 token 上（无字母 token——数字、标点、空白、符号——上同语异文反而更近），训练路由器超出零模型的那部分是否也只在字母 token 上；以及一次文字切换的路由代价相当于把塞尔维亚语换成哪一种语言。
- **对手假设：** H-词表载体：文字效应 = 词表身份；字母 token 上 Δ > 0、无字母 token 上中层 Δ ≤ 0，T 超出 N_B 的部分只在字母 token 上。H-非词表：无字母 token 上 Δ 也处处 > 0（文字效应不由词表携带，进入了上下文表示）。

## 设置
- **模型（单卡 bf16，fvcrc11 A100 80GB，transformers 4.57.6，同 E180 加载方式）：** `Qwen/Qwen3-30B-A3B`（E180 的同一 checkpoint，后训练版，下称 Instruct；48 层，128 选 8）、**`Qwen/Qwen3-30B-A3B-Base`**（新下载，同架构，检验指令微调 / 后训练是否改变结果）、`openai/gpt-oss-20b`（24 层，32 选 4，带偏置，eager）、`allenai/OLMoE-1B-7B-0125-Instruct`（16 层，64 选 8）。四个模型都**重新采集**：E180 只存了 T / N_A0 / N_B0 的逐 token top-k，8 个 draws 只有按句聚合的计数、没有按 token 类别分开，R1–R4 的零模型读数无法从 E180 数组重算。E180 数组用于辅读数 A1（见下）。
- **数据（留出）：** **FLORES-200 devtest 全部 1012 句**作测量（E180 用的是 dev，devtest 对塞语配对是留出数据）；校准集 = 22 个语侧 **dev** 前 25 句（与测量不重叠）。每句单独一条序列，不加模板，`add_special_tokens=False`。22 个语侧分三组：
  - **S 塞语组（主配对）：** srp_Cyrl；srp_Latn = E180 转写器（`scripts/e180_translit.py`，devtest 输出已在 `~/mechpop_cache/e180/srp_Latn/devtest/`）；西里尔 mkd、bul（最近亲）、rus、ukr（较远）；拉丁 hrv（几乎同一语言）、slv、ces、pol。
  - **U 乌兹别克组（第二个同文本双文字配对）：** uzn_Latn（FLORES 原文）；**uzn_Cyrl = 确定性转写**（`scripts/e182_translit_uz.py`，规则见下）；西里尔对照 kaz、kir；拉丁对照 tur、azj。
  - **H 印地组（次要，不同译文）：** hin_Deva ↔ urd_Arab；对照 npi、mar（天城文）、snd、pes（阿拉伯字母）。FLORES 两份是独立翻译，不是同一文本换文字。
- **乌兹别克 拉丁→西里尔转写（跑前已写好并单测）：** 单字母 a а, b б, d д, f ф, g г, h ҳ, i и, j ж, k к, l л, m м, n н, o о, p п, q қ, r р, s с, t т, u у, v в, x х, y й, z з；二合 oʻ→ў、gʻ→ғ（o/g 后任一撇号变体 ' ʻ ʼ ‘ ’ `；FLORES 原文几乎全用 ASCII '）、sh→ш、ch→ч、yo→ё、yu→ю、ya→я。**有歧义、按规则定的：** (1) e / ye：词首或元音后 "ye"→е、"e"→э，辅音后 "e"→е、"ye"→йе（西里尔正字法里俄语借词会写 ъе，如 объект，无法恢复）；(2) 撇号不在 o/g 后且夹在两个字母之间 → ъ（tutuq belgisi，如 maʼno→маъно），否则当标点原样保留。**不可恢复、原样处理：** 俄语借词的 ц 在拉丁里写 s / ts（保留 с / тс）、拉丁里丢掉的 ь / ъ、外文字母 c→ц、w→в（有损）。往返检查：西里尔→拉丁逆规则后与原文（撇号统一成 '）逐词比较。跑前结果（`results/e182/translit_uz_report.json`）：devtest 18,190 个纯 ASCII 拉丁词往返一致 .9991（失败 15 种：w 有损、AQSH / YaIM 这类大小写混排缩写），整行一致 .984；规则触发数 e 词首/元音后 572、ye 词首/元音后 172、ye 辅音后 7、撇号→ъ 331、ts 保留 124、外文 c 41 / w 14；转写后无残留拉丁字母；21 个单测全过。
- **token 类别（由 `tok.decode([id])` 定，与被测变量无关，只依赖分词器；`scripts/e182_common.py::token_class`）：** **LET** = 含任何 Unicode 字母或组合符（L*/M*）；**NON** = 非空、不含字母 / 组合符、不含替换符 U+FFFD、不含撇号类字符（数字、标点、空白、符号）；**frag** = 含 U+FFFD（UTF-8 字节片段，几乎都来自多字节字母，但单个 token 无法判类）——两类都不计；**apos** = 无字母但含撇号类字符——两类都不计（乌兹别克拉丁的 oʻ / gʻ / tutuq 与土耳其语专名后缀的撇号是词内成分，若算作 NON 会让 U 组的 NON 类不对称）。跑前分词统计（devtest）：NON 占 3–11%；frag 在 Qwen3 印地组达 51–58%、OLMoE 斯拉夫西里尔 1–9%、OLMoE 乌兹别克西里尔 15%；apos 在乌兹别克拉丁 2–3.4%。
- **采集（`scripts/e182_capture.py`，以 e180_capture.py 为底，不改 e180 脚本）：** 每个 MoE 层路由器挂 forward hook 取输入 h；路由器 T、**N_A**（W·R，Haar O(d)，8 draws；GPT-OSS 保留训练偏置）、**N_B**（N1：W_c V Q Vᵀ，偏置在校准集上重拟合到 T 的负载，8 draws）。随机数：每层 `torch.Generator().manual_seed(182000 + l)`（与 E180 不同的新 draws），抽取顺序 N_A → N_B。
- **逐句、逐类别均衡（种子 182，与模型无关）：** 对组 g、句 s、类别 c：n_{s,c} = 组内各语侧该句 c 类 token 数的最小值，每个语侧在该句 c 类位置里无放回均匀抽 n_{s,c} 个。四种计数类别：**ALL**（E180 式，所有 token，含 frag / apos）、**LET**、**NON**、**NONtm**（NON 的类型匹配版：对每个无字母 token 类型 t，n_{s,t} = 组内各语侧该句 t 出现数的最小值，抽这么多——各语侧在每一句里的无字母 token 多重集完全相同，去掉"不同译文标点 / 引号风格不同"这一混杂）。
- **存：** 每层 × 每（语侧, 句）× 17 路由器（T + 8 N_A + 8 N_B）× 4 类别的专家计数（ALL / LET uint16，NON / NONtm uint8，溢出断言）；全部 token 的 T top-k、输入 id、预测下一个 token id、类别、四个选中标记。原始数组 `~/mechpop_cache/e182/<model>/`（不进 git）。

## 读数（跑前固定；层号 0 起）
- **D(A, B; c)**：第 l 层，两侧 c 类被抽中 token 的专家使用分布（top-k 计数归一）之间的 JSD（底 2）。**句子配对 bootstrap** 1000 次（种子 182；句 id 在所有语侧一起重抽）给 95% 区间；零模型族 = 每个重抽对 8 draws 取均值。
- **配对：**
  - S：**P1** = srp_Cyrl ↔ srp_Latn；**P2n**（最近亲，主比较对象，同 E180）= mean{srp_Cyrl ↔ mkd, srp_Cyrl ↔ bul}；梯级 **hrv(0)** = srp_Latn ↔ hrv（同文字、几乎同一语言）、**mkd/bul** = P2n、**rus/ukr** = mean{srp_Cyrl ↔ rus, ↔ ukr}；拉丁副梯级 slv = srp_Latn ↔ slv、ces/pol = mean{srp_Latn ↔ ces, ↔ pol}。
  - U：**P1U** = uzn_Latn ↔ uzn_Cyrl；**P2U** = mean{uzn_Latn ↔ tur, uzn_Latn ↔ azj, uzn_Cyrl ↔ kaz, uzn_Cyrl ↔ kir}（两种文字各取同文字的两个突厥语；乌兹别克语属葛逻禄语支，哈萨克 / 吉尔吉斯属钦察、土耳其 / 阿塞拜疆属乌古斯，没有哪一边是明显的近亲，所以两侧对称平均，不挑"最近"）；梯级 **kaz/kir** = mean{uzn_Cyrl ↔ kaz, ↔ kir}、**tur/azj** = mean{uzn_Latn ↔ tur, ↔ azj}。
  - H：**P1H** = hin ↔ urd；**P2H** = mean{hin ↔ npi, hin ↔ mar, urd ↔ snd, urd ↔ pes}（同 E180）。
  - **P0**（逐类别 split-half 地板）：srp_Cyrl、uzn_Latn、hin_Deva 的句子按固定置换（种子 182）分两半，D(半 A, 半 B; c)。
- **R1 Δ_letter(l)** = D(P1; LET) − D(P2; LET)，T、N_A、N_B 各算（P2 = P2n / P2U / P2H）。
- **R2 Δ_nonletter(l)** = D(P1; NON) − D(P2; NON)。同时报 **R2-tm**（NONtm 类别，类型匹配，混杂对照）。
- **R3 文字切换代价的语言距离标尺：** 每层、每类别（ALL 为标题，LET、NON 同报）：
  - S：在梯级 {hrv(0), mkd/bul, rus/ukr} 中取与 D(P1) 绝对差最小的那一级 X → "一次文字切换的路由代价相当于把塞尔维亚语换成 X"；另给**标尺坐标** x：分段线性，D_hrv → 0、D_mkd/bul → 1、D_rus/ukr → 2，两端用相邻段斜率外推；仅当该层梯级有序（D_hrv < D_mkd/bul < D_rus/ukr）时定义，否则记"梯级无序"；x 的 bootstrap 95% 区间。拉丁副梯级 {hrv, slv, ces/pol} 同样报最近级。
  - U：在 {kaz/kir, tur/azj} 中取最近级，并报 D(P1U) / D(级) 两个比值（U 没有"同一语言"的零级，不定义坐标）。
  - 跨配对共同尺度：**r = D(P1) / D(P2)**（S、U、H 各一，T 与零模型族均值），r > 1 = 换文字比换成同文字的对照语言更远。
  - 按层段汇总（E179 / E180 层段：Qwen3 edge 0–3 ∪ 44–47 / middle 7–34；GPT-OSS 0–1 ∪ 22–23 / 4–17；OLMoE 0–1 ∪ 14–15 / 2–11；其余层记 "other"）：每段报众数最近级与 x 的中位。
- **R4 超出零模型的部分，逐类别：** excess_c(l) = Δ_c,T(l) − mean_j Δ_c,N_B,j(l)（同一 bootstrap 重抽给 95% 区间），c ∈ {LET, NON}；对 N_A 同样算、同报。
- **辅读数（不进判决）：** A1 dev 复现：用 E180 数组（dev 997 句，T 的逐 token top-k + 输入 id）按同一类别定义、同一逐句逐类别均衡（S 组 10 个语侧）重算 T 的 Δ_letter / Δ_nonletter（Qwen3 Instruct、GPT-OSS、OLMoE）；A2 ALL 类别的 Δ（E180 主统计量在留出 devtest 上、并扩到 U 组 / Base）。

## 决策表（跑前写死；用户给定的条文照录，括号内为操作化）
主配对 = S（Δ = D(P1) − D(P2n)），逐模型判，然后跨模型合并：
- **(i) H-lexical-carrier confirmed:** for T on all models, Δ_letter > 0 on ≥ 90% of layers AND Δ_nonletter ≤ 0 (CI upper bound < 0 or overlapping 0) on a contiguous middle band of ≥ 1/3 of layers, AND the excess over N_B is positive on letter tokens and ≈ 0 on non-letter tokens → "MoE language-specific routing is vocabulary identity; the residual stream carries script-invariant language identity that the router does not use".
  - 操作化（逐模型 m，三条都满足记 (i-m)）：**C1** Δ_letter 的 95% 区间下界 > 0 的层数 ≥ 0.9 L。**C2** 在层 [2, L−3] 内存在一段连续层，长度 ≥ ⌈L/3⌉（Qwen3 16、GPT-OSS 8、OLMoE 6），每层 Δ_nonletter 的区间下界 ≤ 0（即不显著 > 0）；取最长的一段为带 B（并列取最早）。**C3** (a) excess_LET 区间下界 > 0 的层数 ≥ 0.5 L，且 (b) 在带 B 上 mean excess_LET > 0 且 |mean_B excess_NON| ≤ 0.25 × mean_B excess_LET（"≈ 0"按相对字母类效应定，不按区间是否含 0——NON 类 token 少、区间宽，用区间会偏向判 ≈ 0）。另报带内 Δ_nonletter 显著 < 0（区间上界 < 0）的层，不进判决。
- **(ii)** Δ_nonletter > 0 everywhere too → the script effect is not lexical; the lead is dead, report.（操作化：Δ_nonletter 区间下界 > 0 的层数 ≥ 0.9 L，记 (ii-m)；所有模型都是 (ii-m) 才记全局 (ii)。）
- **(iii)** holds on some models not others → report per model and say which property (Base vs Instruct, expert count, model) separates them, as a which-models statement.（操作化：既不是全部 (i-m) 也不是全部 (ii-m)；逐模型报 (i-m) / (ii-m) / 部分（列出 C1 / C2 / C3 哪条不满足），并对照 Qwen3 Instruct vs Base（后训练）、E = 128 / 32 / 64 与 k = 8 / 4 / 8（专家数）、模型族。）
- **(iv)** Uzbek disagrees with Serbian → the Serbian result is pair-specific; report.（操作化：同一套 C1–C3 / (ii-m) 规则用于 U 组（Δ = D(P1U) − D(P2U)）；某模型上 U 的分支 ≠ S 的分支，即对该模型记 (iv)。）
- **混杂对照条款：** 若某模型用 R2-tm（NONtm）替换 R2 后 C2 或 C3 的结论翻转，分支仍按 R2 记，但该模型的结论注明"受无字母 token 类型组成影响"。
- H 组（hin↔urd）用同一规则报分支，不进判决（不同译文）。
- 以上都不是开线 / 关线条件；结果交主会话，立题由人定（R2）。

## 阳性对照与 sanity
- 转写往返：塞语（E180 转写器在 devtest 上重报，预期 1.0）；乌兹别克（上面的 .9991 / 失败清单）。
- 两次前向 top-k 完全一致率（预期 1.0）；hook fp32 重算 vs 模型选择、T logits vs 模型选择（预期 ≈ 1 / 1.0）。
- **N_B 负载 TV 均值 ≤ .01**：若 GPT-OSS 再次略超，用更大的校准集（dev 前 100 句）重跑 GPT-OSS 一次，两套都报（判决用哪套：两套分支一致则无所谓；不一致则两套都报、不选边）。
- 均衡核对：逐句逐类别被抽 token 数在组内各语侧相等（差 0）；NONtm 逐句类型多重集相等（差 0）；T 的逐 token top-k 重新计数 = 存的 T 计数。
- 逐类别 split-half 地板 P0（LET、NON 各报 D(P0) 与 D(P1)、D(P2) 之比）；E180 的教训：P0 是"不同句子、半数 token"，偏大；符号判定靠配对 bootstrap，不靠 P0。

## 噪声地板 + MIE
- T 的地板 = 句子配对 bootstrap 区间；零模型族 = 8-draw 均值的 bootstrap 区间 + draws 范围；P0 = 换句子距离。判决是逐层区间是否越过 0（二元）；90% / ⌈L/3⌉ / 0.25 / 0.5 是用户给定或本卡操作化的 pilot heuristic（R12），不是自动科学判决。

## 混杂审计（EXECUTION §4）
- **无字母 token 的类型组成随语言变**（P2 是独立译文，标点 / 引号风格不同；"«»" vs "„“"）：会让 D(P2; NON) 偏大、偏向 H-词表载体 → NONtm 类型匹配对照（已控制，按上面条款报）。
- **无字母 token 的上下文本身随文字变**：这正是被测量（无字母 token 的路由是否还带文字），不是混杂。
- **乌兹别克拉丁撇号**是词内成分 → apos 类两类都不计（已控制）。
- **字节片段 token**（frag）在 Qwen3 印地 / OLMoE 西里尔占比高 → 两类都不计，报占比（部分控制：LET 类在这些语侧只剩完整字母 token）。
- **转写文本不自然**：srp_Latn 与真实拉丁塞语一致（一一映射）；uzn_Cyrl 在俄语借词（ц、ь、ъе）处与真实西里尔乌兹别克语不同（未控制，影响限于借词）。
- **翻译差异**：P1 两侧逐词对应，P2 是独立翻译；同 E180，部分由 hrv(0) 梯级与 NONtm 控制。
- **深层按预测 token 路由**：末层 Δ 可能被输出文字主导（E180 已见）；C2 只在 [2, L−3] 内找带。
- **零模型族翻转**：N_A、N_B 同报；判决只用 N_B（用户条文），N_A 结果同表报。
- **分词器不同**：只比各模型内部的层集合 / 符号 / 比值，不比绝对 JSD。
- **E180 POST-HOC 线索 → 本卡判决**：数据换成 devtest（留出）、draws 换新种子、乌兹别克是新配对；读数在本卡写死，跑后不改（R5）。

## 算力预算
估计：每模型约 1.4M token（22 语侧 × 1012 句）；Qwen3 Instruct / Base 各约 15 分钟、GPT-OSS 约 10 分钟（可能再加一次大校准集重跑）、OLMoE 约 5 分钟，加冒烟 ≈ 1 GPU h（上限 2 GPU h，并发 ≤ 2 卡，fvcrc11 GPU 0–1）。分析在 fvcrc20 CPU。日志 `results/e182/_logs/`。**实际：**（跑后填）

## 结果（跑完后填写；上面内容不改，修改需注明日期）
