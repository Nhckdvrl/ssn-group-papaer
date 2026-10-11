# E24：把 regime 标在输入侧——映射通道能绑定“检索得到的上下文”，却绑定不了“时间”？（2026-10-05）

- **状态：** DONE（2026-10-06 整理时更新状态）
- **类型：** CLAIM
- **对应：** C02（concept drift 不被跟踪）、C05（nearest-not-newest / 检索机制）；与 E22（输出侧标记）、E23（时间戳）构成三联对照
- **问题（一句话）：** E22 中模型知道 regime 变了（会写大写），却不把新映射绑定到它；如果把同样完全耦合的 regime 标记放在**输入侧**，映射通道会按 query 的输入标记切换映射吗？切换是否与先后顺序无关？
- **设置：** 与 E22 同源的 base（数字 small/large、SST-5 两极 positive/negative），300 base/任务，新种子 SEED0=720000。B demo 的映射反转，标签保持小写（只有两个候选：A 映射标签 vs B 映射标签）。两种输入标记：
  - `annot`：每条 demo 在输入行后加一行 `Annotator: Alex`（A 段）/ `Annotator: Sam`（B 段）——自然情境：两位标注者约定相反。query 标记 ∈ {Alex, Sam, 省略}。
  - `case`：B 段输入键大写（`NUMBER: 37` / `REVIEW: ...`），A 段正常。query 标记 ∈ {A 式, B 式}。
  - 模式（7 个）：allA、suffix_4、disp_4、noise_2__suffix_3、suffix_8、prefix_8、block_start4。
  - 模型：Qwen3-8B、Qwen2.5-7B、Mistral-7B、Llama-2-7B、gemma-2-2b、Qwen3-14B（可行时加 32B）。脚本 `scripts/build_ctxmark.py` → `data/ctxmark`，`run_lm.py` 两候选打分。
- **读数（全部为 logit P(B 映射)，按 base 配对）：**
  1. 标记绑定：`bind = P(B|q 标 B) − P(B|q 标 A)`，在 suffix_8 与 prefix_8 分别计算；规范的“上下文条件”学习者两者都大且相等。
  2. 顺序对称性：同一 query 标记下 suffix_8 − prefix_8（检索假说：≈0；时间学习者：>0）。
  3. 无标记 query（仅 annot）：suffix_8 − prefix_8、suffix4−disp4、噪声方向检验（meta oracle +4.62 / +4.02 / −1.70）。
  4. 与 E22 的对比：同模型同任务，E22 映射通道 suffix_8 时 P(新映射|大写) vs 本实验 P(B|q 标 B)。
- **阳性对照：** allA 下 P(B) 很低（任务已学会）；E22 格式通道同一模型规范（已知有效应）。
- **噪声地板 + MIE：** 300 base 配对 bootstrap；E22 映射通道 CI 半宽 ~0.1–0.3 logit。bind > 1 logit 且两个顺序都 > 1 视为“绑定”；|suffix_8 − prefix_8| < 0.5 视为“与顺序无关”。这些只是解释阈值，不作为停止门槛。
- **混杂审计：**
  - 标记词本身的先验（Alex/Sam、大写键）：用 allA + q 标 B（上下文中没有 Sam 段）对照——此时 bind 应≈0，否则是标记词本身的偏置。已控制。
  - 位置：suffix_8 与 prefix_8 中 B 段位置相反，标记绑定在两种顺序下都测。已控制。
  - 检索相似度的混杂：query 的内容与 A/B 段的相似度在 suffix_8/prefix_8 间对称（同一组 demo、只换标签与标记），已控制。
- **决策表（跑之前写）：**
  - bind 大、两顺序对称、无标记 query 集合式 → “映射通道按检索到的上下文条件化，不按时间”——E22/E23/E24 三联成为论文机制节的核心（输出标记：不绑定；输入时间戳：不绑定；输入类别标记：绑定）。
  - bind 小（≈E22）→ 映射通道连显式输入上下文也不绑定，说明问题在“二阶上下文 × 映射”的组合（contextual ICL）而不在时间；改写 C05 的机制表述。
  - bind 大但 suffix_8 ≫ prefix_8 → 标记让时间可用（标记把 regime 变成可检索的单元），与 E22 不同的原因需要再追。
- **算力预算：** 21000 行 × 6 模型，每模型 ~10–20 分钟单卡。

## 结果（跑完后填写）

## 结果（2026-10-06）
- 6 个模型（Qwen3-1.7B/8B/14B、Qwen2.5-7B、Mistral-7B、gemma-2-2b）× 2 任务 × 2 种标记：带新 regime demo 时的“绑定”P(B|q 标 B)−P(B|q 标 A) 为 0.2–2.7 logit，**多数不超过 allA（上下文里根本没有 B 标记）时的值**，且 suffix_8 ≈ prefix_8（对顺序对称）。无标记 query：成簇 0–0.44、噪声 −0.11 到 +0.19、后8−前8 −0.10 到 +0.30（集合式）。
- **E24b 打乱标签对照（Qwen3-8B）：** 打乱时绑定≈0（−0.07 到 +0.11），说明读数干净。净绑定：数字 allA 2.20 → suffix_8 1.49、prefix_8 1.41；SST allA 2.41 → suffix_8 2.39、prefix_8 2.53。会利用标签的上下文 oracle：allA 4.4 → suffix_8 7.3。即 8 条新 regime 的 Sam demo **没有增加**按标注者的分流（oracle 应 +2.9）；“绑定”只是“没见过的标注者→降低信心”的新奇性效应。
- **按决策表：** 输入侧显式上下文标签也不被用来路由映射（8B 及以下）。E22（输出标记）、E23（时间戳）、E24（输入标记）三联：在 8B 规模，任何显式的 regime 标记都几乎不被绑定到映射上；32B 在输出标记上开始绑定（见 E22 规模趋势），32B 的输入标记结果待出。
