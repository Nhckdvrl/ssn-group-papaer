# chasing trends

这是 `Nhckdvrl/ssn-group-papaer` 中用于重新校准科研选题 taste 的独立工作区。

建立日期：2026-09-19

> **当前阶段：大量读论文、重建 paper genealogy、归纳问题是怎样从 literature 中长出来的。**
>
> **2026-09-19：用户已明确认可 genealogy-first 的阅读/校准方法。当前继续做纵向 literature study；在用户明确要求开始找题以前，不启动 CT01 / S10，不注册 candidate，不做 pilot。**

---

# 1. 这不是“某一种方法论文”的搜题目录

最初版本曾把用户举的一个喜欢的结构：

> failure → diagnosis → mechanism → method → benchmark → ablation

写成了 chasing-trends 的主范式。

**这个版本已经被否定。**

用户真正要求的是：

> 大量阅读 ACL / EMNLP / NAACL / ICLR / ICML / NeurIPS / AAAI / CVPR / ICCV / ECCV 等真实优秀论文，
> 不只看摘要，而是追 Introduction、Related Work、关键实验/理论、方法由来和 nearest prior，
> 研究 idea 为什么会被看到、它从哪些 parent work 长出来、作者真正改变了什么问题坐标，
> 然后从大量不同论文的 genealogy 中归纳多种 question-forming / paper-growing paradigms。

所以：

> **范式必须从论文中归纳出来，不能先写模板再往里面找题。**

---

# 2. 当前最重要文件

启动顺序：

1. **RESEARCH_TASTE_RECALIBRATION_2026-09-19.md**  
   本轮最重要的纠偏。说明为什么“机制→方法”只能是一个 archetype，并深拆第一批不同 genealogy。

2. **PAPER_GENEALOGY_GUIDE.md**  
   深读一篇 paper 时具体怎么向下追 parent、siblings、related work、assumption、changed premise、decisive experiment。

3. **LONGITUDINAL_GENEALOGIES_01_2026-09-19.md**  
   第一批真正纵向 lineage reconstruction：RLVR learning signal、test-time scaling、ICL mechanism、diffusion fast sampling、robot/VLA action representation。重点记录 primitive 如何移动、成功 abstraction 如何制造下一代问题，而不是逐篇摘要。

4. **LITERATURE_MAP_2026-09-19.md**  
   跨会议 breadth map；用于判断 field density、saturated axes 和值得纵向追的 lineage。

5. **PAPER_AUTOPSIES_2026-09-19.md**  
   第一轮 paper notes。旧版有明显 method-paper bias，因此只能作为原始阅读记录；以新的 genealogy 文件为上位解释。

6. **LESSONS_FROM_SSN_TASTE.md**  
   保留旧搜索真正有用的 process lesson：repo restore、nearest-prior audit、reviewer compression、data/compute gate、anti-resurrection、execution risk。

7. **SEARCH_GUIDE_ZH.md**  
   当前 canonical 工作流。重点已经从固定 topic template 改为：
   **field map → lineage reconstruction → genealogy induction → pressure mining → candidate audit**。

---

# 3. Repo 当前事实

截至 2026-09-19，`ssn-taste/` 最新正式状态：

仍为 **SELECTED — PILOT-AUTHORIZED**：

- S04 — How Do Language Models Update Situation Models Across Event Boundaries?
- S05 — When Does Reading Become Learning?
- S06 — What Does Deliberation Do to Evidence?
- S07 — Where Does Surprise Go?
- S08 — Is Metacognitive Control Shared?

已正式 KILL / registration cancelled：

- S03 — From Document End to Task Done
- S09 — Same Recall, Different Stability?

这些自有题都不是 positive taste exemplar。

只用于：

- anti-duplication；
- execution-risk；
- failure-process learning；
- data/compute calibration。

---

# 4. Positive taste 从哪里来

只从：

1. **Sasano 的真实判断与真实指导记录**
2. **真实强论文及其 immediate related work lineage**

不能从：

> “我们以前 S06 过线，所以新题应该像 S06。”

也不能从：

> “StepFlow 很好，所以以后都找 failure→method。”

正确方式是：

> **论文 A 为什么成立？**
>
> **它在 A 出现以前的 literature 中究竟看到了什么别人没当成问题的东西？**
>
> **如果只读它的 method，我们会错过什么？**
>
> **如果换一个领域，真正能迁移的是哪一种 question-forming move？**

---

# 5. 当前第一批观察到的 genealogy

注意：这些是从论文中**观察到的**，不是以后机械套用的 generator。

目前已经深拆：

- successful objective → **decompose hidden learning signals**  
  例：Negative Reinforcement in RLVR

- mature algorithm → **deployment variable was never part of policy state**  
  例：Budget-Guided MCTS

- fragmented related work → **unified design space → dominant bottleneck**  
  例：TORS

- known final failure → **change the attribution unit / causal coordinate**  
  例：StepFlow、GUARD

- crowded scientific object → **change explanatory decomposition**  
  例：ICL information removal

- strong prior theorem → **audit a load-bearing assumption**  
  例：A Little Depth Goes a Long Way

- known phenomenon → **remove an artificial premise in prior evidence**  
  例：CoT faithfulness in the wild

- mature heuristic family → **search for a common success invariant**  
  例：DC-Merge

未来还会继续扩充、合并、删改。

---

# 6. PaperNotes 怎么用

PaperNotes（https://papernotes.org/）非常适合做：

> **breadth scan / taxonomy / cross-conference discovery。**

例如快速看到：

- ACL 2026 reasoning / interpretability；
- ICLR 2026 reasoning / interpretability；
- ICML 2026 reasoning / optimization；
- NeurIPS 2025 reasoning / optimization；
- CVPR 2026 image generation / multimodal / optimization；
- ECCV 2026 image/video generation；
- AAAI 2026 reasoning。

但它不能替代 deep read。

任何真正进入 taste calibration 或 candidate audit 的 core paper，都必须尽量回到：

- ACL Anthology
- OpenReview / official proceedings
- PMLR
- NeurIPS proceedings
- CVF / ECCV official
- arXiv full paper

并至少读到：

> **Introduction + Related Work + decisive section + method derivation + main ablation / limitations。**

---

# 7. 当前硬停止线

现在仍然：

> **不开始 CT01。**

先继续建立足够厚的 genealogy library：

- 不同会议；
- 不同领域；
- 不同 paper type；
- 普通但强的 Main，不只 Best/Outstanding；
- method paper；
- pure science / analysis paper；
- theory paper；
- negative / limits paper；
- cross-domain generation / multimodal / optimization；
- 同一 lineage 连续多篇论文。

最终目标不是得到十条“好题公式”。

而是形成一种能力：

> **看到一个 literature cluster 时，能判断它现在真正拥挤在哪些轴、哪些 assumption 被默认固定、哪些 relation 尚未被解释、哪个新系统改变了 premise、什么小 observation 有可能长成 Main-sized question。**

这才是 chasing trends 当前真正要训练的东西。
