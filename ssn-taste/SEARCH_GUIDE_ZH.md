# ssn-taste 科研选题搜索指南（Canonical v2）

最后系统重构：2026-09-26

这个文件夹只做一件事：

> 找到 Sasano 会认为清楚、自然、结果本身有意思、值得知道，并具有 ACL / EMNLP / NAACL Main 潜力的问题。

这里不优化用户个人更喜欢的 method paper / benchmark gain / training / mechanism 题型。那些偏好属于别的搜索线，不能反过来定义 Sasano taste。

当前正式状态：S01–S12 全部 KILL，selected = 0。

---

# 1. 这次为什么整池失败

根本错误不是“实验没调好”，而是选题对象选错了。

旧流程实际上经常是：

> 先想一个漂亮 distinction → 写 A/B/C worlds → 设计 synthetic assay → 再问这个结果会不会有意义。

这会系统性产出“概念上漂亮、实验一碰就碎”的题。

S11 / S12 只是把问题暴露得最清楚：

- S11：value vs measurement precision 很漂亮，但真正 readout 连显式 interval 上的 certification 都不稳定。
- S12：definition vs world fact 很漂亮，但 natural discourse role 根本不能稳定操纵 scope；加强 scope 后又变成提示词本身在起作用。

所以以后第一原则改成：

> 不是先找 question，而是先找已经存在的 finding。

只有 finding 本身先站住，才允许形成 RQ。

---

# 2. Sasano taste 的正确理解：finding-first，不是 distinction-first

根据 Sasano 2026 年真实反馈，最稳定的信号是：

1. 平均 reviewer 必须很快看懂哪里有意思。
2. 技术上干净但结果理所当然，不够强。
3. 事前预期被真实实验打脸，本身可能很有意思；下一步应换几个自然 setting 验证，而不是立刻发明复杂机制。
4. 直接先行把某个因素说成关键，而新实验发现这个因素作用有限，也值得，因为它直接修改了一个 live claim。
5. 结果与 RQ 应尽量一对一。
6. 输出类似但内部理解不同，可以作为有价值的 deeper finding，但未必足以单独成为主线。
7. 几何/机制指标如果不知道和实际知识或行为有什么关系，很难说明到底学到了什么。

因此，Sasano-style seed 的起点应当更像：

> “这个已经观察到的结果为什么和最自然预期不一样？”

或：

> “直接先行认为 X 很关键，但这里 X 居然不关键/方向相反，为什么？”

而不是：

> “A 和 B 理论上不同，LLM 会不会区分？”

---

# 3. 新流程总览

正式流程只有七步：

> Evidence Harvest → Anchor Reproduction → Surprise/Claim Audit → Explanation Ownership → RQ Formation → Instrument Preflight → PILOT-AUTHORIZED

任何一步失败，直接 KILL；不进入 Sxx。

**特别重要：在 Instrument Preflight 通过之前，不允许创建新的 Sxx registration。**

---

# 4. Stage A — Evidence Harvest：只收结果，不许想题

搜索开始时，禁止 brainstorm 标题、RQ、mechanism。

只建立 Observation Cards。

每张卡必须包含：

1. Source：论文 / Slack / 我们已有真实实验的具体来源。
2. Exact observation：具体数值、表格、figure 或稳定行为，不接受抽象总结。
3. Natural setting：结果是否来自正常任务/数据/模型使用，而不是为了这个题专门造的 micro-world。
4. Expected baseline：在看到结果之前，一个知情 reviewer 为什么会预期相反/不同？这个预期必须来自 direct prior、常用假设、明确方法 claim 或非常直接的 capacity/logic argument，而不是我们自己的直觉。
5. Stability evidence：至少说明是否跨 seed / context / model / subset 稳定；如果 source 只给一个点，明确标红。
6. Author explanation：原作者到底解释到了哪一步？
7. Why unresolved：还有什么具体 unknown 没被 source paper / appendix / follow-up 吃掉？

Observation Card 还不是 seed。

## 4.1 允许进入 portfolio 的 observation

优先级最高：

- 事前自然预期与真实结果方向相反；
- stronger / more / larger 条件反而更差，且不是明显 trade-off；
- 直接先行 claim X 是关键，新结果显示 X 不关键或方向反转；
- 两篇强工作在真正可比的对象上得到相反结论；
- 一个自然 subset 出现 sharp reversal / discontinuity；
- 一个本来应该受 context / evidence / supervision 影响的行为几乎不受影响，且结果跨自然 setting 稳定；
- 一个显然受 capacity / information bound 约束的系统表现远超自然预期。

## 4.2 立即拒绝的 observation

- 只是“模型做错了”；
- 只是 benchmark 某一项掉分；
- surprise 只来自我们的主观直觉；
- effect 只在一个 prompt / 一个 model / 一个 seed；
- perturbation 两边强度根本不可比；
- source paper 已经把 observation、why 和 decisive test 都做完；
- 为了让 phenomenon 出现必须先造 custom synthetic task。

---

# 5. Stage B — Anchor Reproduction：先复现 finding，再形成问题

这是旧流程缺失的关键门。

任何 observation 想进入下一步，必须先证明 anchor 本身可靠。

优先直接复现 source setting：

- 原 benchmark / 原 dataset / 原 prompt family；
- 原公开 model 或可合理替代的同类 model；
- 原 metric；
- 尽量不加我们的新 construct。

最低要求：

**默认必须由我们自己做 anchor reproduction。** 只有原模型/API/数据已不可获得、且至少两个独立来源已经在可比设置下重复同一 finding 时，才允许用 multi-source replication evidence 替代；必须在 Observation Card 中显式说明为什么无法自行复现。

1. finding 方向能复现；
2. effect 不是 parser / scoring / prompt accident；
3. 若 claim 很 broad，至少在第二个自然 setting 或第二个合理 model family 上不立即反转；
4. 如果原 observation 本身只在一个狭窄 cell 成立，就把 claim 限到那个 cell，不能先写大 mother question。

如果 anchor 不稳定：

> KILL observation。

不允许先解释“为什么复现不了”再把复现失败改成新题。

---

# 6. Stage C — Surprise / Direct-Claim Audit：结果本身到底值不值得？

复现后，用一句普通话写：

> “本来根据 X，我们会预期 Y；但实际稳定看到 Z。”

其中 X 必须是 live baseline，而不是事后编出来的 strawman。

合格的 X 可以是：

- direct prior 明确 claim；
- 社区真实使用的方法 assumption；
- 清楚的 monotonic expectation；
- 明确的信息/容量/逻辑限制；
- 多篇工作共同依赖的 premise。

不合格：

- “我们觉得应该这样”；
- “人类会这样，所以模型也应该”；
- “更多信息一般更好”；
- “更自然的 perturbation 应该更简单”这类未经控制的修辞。

如果 Z 其实由最简单 baseline 就能解释，KILL。

这一步对应 Sasano 对 manifold-steering 的反馈：

> curved method 比粗糙 straight line 更准，如果本来就应该如此，就没有足够 surprise。

---

# 7. Stage D — Explanation Ownership：原作者到底还剩什么给我们？

旧流程经常犯的错误是：看到一个漂亮 anomaly，就默认“作者只发现现象，我们补 why”。

现在必须把 ownership 拆开检查：

1. Observation ownership：谁先报告 finding？
2. Explanation ownership：source 是否已经提出原因？
3. Evidence ownership：source 是否已经用实验支持这个原因？
4. Decisive-contrast ownership：source / follow-up 是否已经区分了最主要 competing explanations？

只有以下情况允许继续：

- source 只给猜测，没有直接 test；
- source 做了部分 analysis，但至少两个重要解释仍然给出不同可检验 prediction；
- 两篇工作对同一个 finding 给出互不兼容解释；
- direct prior claim 与新 observation 冲突，但没有工作解释冲突为什么出现。

如果 source 已经完成 finding → explanation → decisive intervention，KILL。

**secondary finding 不等于 free novelty。appendix、follow-up、同组后续都要查。**

---

# 8. Stage E — RQ Formation：到这里才允许问问题

RQ 必须从一个已经复现的 finding 长出来。

标准模板：

> Observation O 与 baseline B 冲突；我们问哪个因素解释 O，或 O 在什么自然条件下发生反转。

要求：

- 一条主 finding 对一条主 RQ；
- 不允许凭空新加漂亮 taxonomy；
- competing explanations 最多保留 2–3 个真正自然的；
- 每个 explanation 必须来自 existing result / prior / known property，而不是为了让实验像 science 临时发明；
- 如果删掉 anchor finding，RQ 就不再值得问，说明这条 RQ 至少 provenance 正确。

禁止重新出现：

- typed vs untyped；
- state vs retrieval；
- source vs rule；
- pre-verbal vs verbal；
- shared vs separate；
- A/B/C worlds；

除非这些 distinction 是被已经复现的 finding 强迫出来的解释，而不是 seed 来源。

---

# 9. Stage F — Natural Contrast First

诊断 finding 时，优先从已有自然 variation 里找 contrast：

- source 已有 subset；
- model family / scale；
- clean vs naturally occurring condition；
- direct prior 中已存在的 factor；
- 一个真实 ablation；
- 原任务中自然存在的 context / data regime。

只有自然 contrast 不足以区分解释时，才允许 synthetic diagnostic。

synthetic diagnostic 的角色只能是：

> 解释一个已经独立存在的自然 finding。

它不能负责：

- 创造 phenomenon；
- 定义 construct；
- 同时当 ground truth、manipulation 和 evidence。

如果删掉 synthetic assay，整个项目就没有 empirical pressure：KILL。

---

# 10. Stage G — Instrument Preflight：通过前不能 selected

这是新的硬门。

Preflight 不看我们最终想要的主结论，只验证 diagnostic instrument 是否有资格回答问题。

必须全部满足：

1. Manipulation validity：scientific variable 确实被操纵，而不是 wording / difficulty / length / format 顺便改变。
2. Readout validity：最强显式版本下，模型有能力完成 readout 所需的 prerequisite reasoning。
3. Symmetry stability：逻辑等价 / polarity 对称 / answer-order 等价改写不能出现灾难性翻转。
4. Positive / negative controls：两端都能工作。
5. Exact ground truth：若有程序性真值，generator/scorer/parser 全部测试通过。
6. No prompt search：不能通过扫几十个 prompt 挑一个 effect 最大的版本。
7. Control budget：如果为了让结果可解释必须不断加第 4、第 5、第 6 层控制，默认 KILL；这通常表示 construct 不自然。

S11 / S12 如果按这个门执行，都不会进入 selected。

---

# 11. PILOT-AUTHORIZED 的新定义

一个题只有同时满足以下条件，才允许创建新的 Sxx registration：

1. 有一个已经存在的、具体的 natural finding；
2. finding 已被我们复现或有等价级别的多源强证据；
3. finding 本身对普通 reviewer 一句话就有 surprise / direct-prior relevance；
4. source paper 没有把主要 why 做完；
5. RQ 只解释这个 finding，不先扩成宏大 mother question；
6. nearest prior 没有 same decisive contrast；
7. 第一刀 diagnosis 来自 natural contrast 或已经通过 preflight 的 instrument；
8. instrument validity 已经通过；
9. 不需要先做 model zoo / evaluator / benchmark / mechanism 才能回答；
10. 结果如果符合最简单 baseline，不会被包装成“也有意义”强行续命。

PILOT-AUTHORIZED 现在表示：

> finding 是真的，问题是真的，工具也真的能测；现在才值得花算力回答 why / when。

不是“这个想法值得试试看”。

---

# 12. Pilot 后仍然允许 RQ 改变，但必须守住 discovery / validation 边界

主 pilot 冻结后：

- 可以仔细看 unexpected structure；
- 如果出现更有意思的新 finding，可以改 RQ；
- 但新 hypothesis 必须用 held-out data / new seed / new natural setting 验证；
- 不允许在同一批 discovery data 上调 prompt / metric / subset 后宣称验证。

如果 original RQ 被结果否定：

> 先 KILL original RQ。

不要先想怎么救。

---

# 13. 搜索时真正应该找什么

下一轮搜索不再维护抽象 Pressure Portfolio。

改成维护 Observation Portfolio，建议 5–8 张卡。

优先搜索：

- strong paper 的 result / ablation / error analysis；
- “contrary to prior work / unexpectedly / surprisingly” 后面的具体结果，但必须自行判断是不是 rhetorical surprise；
- direct prior 把某因素称为 critical / necessary / key，而后续自然实验发现不是；
- 同一 task / construct 上真正可比的 cross-paper reversal；
- Sasano Slack 里明确说“和事前预想不同，但结果有意思”的现象形状；
- source paper 的 secondary finding，但要确认 authors 没继续把 why 做完。

不要从以下地方生成 seed：

- future work；
- 心理学现象列表；
- mechanism 名词；
- architecture component；
- exact-cell literature gap；
- synthetic benchmark idea；
- “old debate + new intervention”本身。

强论文 autopsy 仍然可以做，但只用于：

> 判断一个 finding 为什么是强 finding、作者如何从真实结果长出问题。

不能再作为抽象 generator。

---

# 14. Sasano calibration：只记 finding 形状，不复制题材

正向形状：

- 未知名字放进 factual context，模型仍极度 skeptical；与事前预测相反。Sasano 认为结果本身有意思，并建议换 obituary / politics / sports 等自然 context 验证。
- direct prior 强调 one-word limitation 很关键，但新设置中效果有限；即使结果不戏剧化，因为它直接修改先行 claim，也值得报告。
- 2D 1-bit representation 居然还能有很高分类性能；Sasano 第一反应是问“这么少状态怎么还能 85%？”，说明清楚的 capacity surprise 本身能驱动问题。

负向形状：

- curved approximation 比粗 straight line 好：结果本身不够惊讶。
- curvature / isometry 等指标如果难以连接到实际知识/行为，就很难说学到了什么。
- 输出类似但内部 representation 不同可以很有意思，但可能更适合作为 discussion/depth，而不是自动成为主线。

---

# 15. Anti-resurrection 与 Global Reset

FAILED_TOPICS 只在 observation/RQ 已经形成后定向查重。

如果连续 2–3 个 Observation Card 因同一种原因死亡，换来源/lineage，不要在同一论文族里找缝。

强制 Global Reset 的信号：

- 开始讨论“怎么让这个题成立”；
- controls 越来越多；
- novelty 依赖 wording；
- finding 本身越来越不重要，只剩 mechanism；
- surprise 只能靠我们自己解释；
- source paper 已经做完 why，却还在找一个小缺口。

Reset 时只问：

> “现在手里哪个已经存在的 finding，本身最值得知道？”

如果没有，就允许 0 survivor。

---

# 16. 当前正式状态

截至 2026-09-26：

> Selected topics = 0.

S01–S12 全部是历史失败 / anti-resurrection 记录。

下一轮禁止直接创建 S13。

执行文件流：

`OBSERVATION_PORTFOLIO.md`
→ Anchor Reproduction / Surprise Audit / Explanation Ownership
→ RQ Formation
→ `INSTRUMENT_PREFLIGHT_TEMPLATE.md`
→ 通过后才能创建 Sxx registration
→ `SELECTED_TOPICS.md`

任何候选必须经过 Anchor Reproduction 和 Instrument Preflight 后，才允许进入 SELECTED_TOPICS。

---

# 17. 最后只记住八句话

> 先找 finding，不先找 question。
> surprise 必须来自真实 baseline，不来自我们的修辞。
> finding 先复现，再问 why。
> source paper 做完 why，就别捡。
> RQ 只能解释一个真实 finding，不凭空长 taxonomy。
> synthetic task 只能诊断，不能创造研究对象。
> preflight 过不了，永远不许 selected。
> Sasano taste 看的是“结果本身有没有意思”，不是我们能不能把 A/B/C 讲漂亮。
