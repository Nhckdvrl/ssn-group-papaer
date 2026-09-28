# Blogs, Reports & Source Feeds

**Last verified:** 2026-09-28

These are not citations of convenience. They are sources repeatedly useful for research taste, practical baselines, artifact discovery, or understanding how frontier labs frame problems.

---

## Research craft / experimental discipline

### B01 — Andrej Karpathy — A Recipe for Training Neural Networks
**Type:** CRAFT / evergreen  
**Why keep:** perhaps the best compact reminder that neural-net experiments fail silently; build the end-to-end skeleton, dumb baseline, overfit sanity checks, then add complexity.  
**Use when:** a new training project starts or results look mysteriously weak.  
https://karpathy.github.io/2019/04/25/recipe/

### B02 — Alex L. Zhang — Language Model “Shape” (2026)
**Type:** FRONTIER / architecture thought-piece  
**Why keep:** useful question-forming provocation: should the model’s computation contract change to fit the harness, rather than always adapting the harness to a decoder-only model?  
**Warning:** inspiration only; the repo’s ShapeLab already showed that blog intuition is not mother evidence.  
https://alexzhang13.github.io/blog/2026/shape/

### B03 — Anthropic — The engineering challenges of scaling interpretability
**Type:** CRAFT / research-engineering  
**Why keep:** explicitly describes scaling infrastructure **after** evidence accumulates, not before; useful counterweight to overbuilding.  
https://www.anthropic.com/research/engineering-challenges-interpretability

---

## Interpretability / model science

### B04 — Anthropic Interpretability research index
**Type:** FRONTIER source feed  
**Why keep:** concentrated stream of current large-model interpretability work; useful for checking whether a proposed model-science object is already active.  
https://www.anthropic.com/research/team/interpretability

### B05 — Anthropic — Open-sourcing circuit-tracing tools
**Type:** ARTIFACT  
**Why keep:** practical entry point when causal graph / attribution tooling matters; supports open-weight models.  
https://www.anthropic.com/research/open-source-circuit-tracing

---

## Post-training / reasoning

### B06 — Nathan Lambert / Interconnects — A recipe for frontier model post-training
**Type:** BRIDGE / practical synthesis  
**Why keep:** compact synthesis of modern post-training recipe evolution; useful before interpreting SFT/DPO/RL changes as novel mechanisms.  
https://www.interconnects.ai/p/a-recipe-for-frontier-model-post-19f

### B07 — Nathan Lambert / Interconnects — The state of post-training in 2025
**Type:** BRIDGE / field state  
**Why keep:** separates recipe components and open-vs-closed knowledge; useful historical baseline for later RLVR work.  
https://www.interconnects.ai/p/the-state-of-post-training-2025

### B08 — Nathan Lambert / Interconnects — A taxonomy for next-generation reasoning models
**Type:** BRIDGE / reasoning map  
**Why keep:** helps separate reasoning capability, calibration, strategy, abstraction, and agentic requirements rather than treating “reasoning model” as one object.  
https://www.interconnects.ai/p/next-gen-reasoners

### B09 — Nathan Lambert / Interconnects — 2025 year in review
**Type:** source map  
**Why keep:** useful index into the 2025 RL/reasoning discussion; do not cite as scientific evidence.  
https://www.interconnects.ai/p/2025-interconnects-year-in-review

### B10 — DAPO project page
**Type:** ARTIFACT / project report  
**Why keep:** code/data/model links plus the concrete engineering choices behind open large-scale RL.  
https://dapo-sia.github.io/

---

## Architecture / memory

### B11 — Google Research — Titans + MIRAS: Helping AI have long-term memory
**Type:** BRIDGE / official research explanation  
**Why keep:** clear synthesis of attention, recurrent memory, test-time memorization, and MIRAS design axes. Good for understanding the intended abstraction before reading details.  
https://research.google/blog/titans-miras-helping-ai-have-long-term-memory/

### B12 — state-spaces/mamba official repository
**Type:** ARTIFACT / lineage hub  
**Why keep:** one place tracking Mamba, Mamba-2 and Mamba-3 code/papers; check this before making claims about current SSM capability.  
https://github.com/state-spaces/mamba

---

## Agents / multimodal background

### B13 — Lilian Weng — LLM Powered Autonomous Agents
**Type:** ANCHOR / conceptual map  
**Why keep:** still a useful decomposition of planning, memory, and tool use; use as vocabulary/history, not frontier novelty evidence.  
https://lilianweng.github.io/posts/2023-06-23-agent/

### B14 — Lilian Weng — What are Diffusion Models?
**Type:** ANCHOR / cross-domain tutorial  
**Why keep:** broad, durable diffusion reference; especially useful when mining CV/generative-model research moves.  
https://lilianweng.github.io/posts/2021-07-11-diffusion-models/

### B15 — Lilian Weng — Diffusion Models for Video Generation
**Type:** BRIDGE / cross-domain tutorial  
**Why keep:** shows how temporal consistency, world knowledge, and long-horizon generation change the problem relative to images.  
https://lilianweng.github.io/posts/2024-04-12-diffusion-video/

---

## Frontier-lab research feeds

### B16 — DeepSeek Research & News
**Type:** FRONTIER feed  
**Why keep:** efficient place to track new architecture, long-context, memory, MoE, reasoning and systems reports from DeepSeek.  
**Rule:** read the actual technical report before using a release claim scientifically.  
https://www.deepseek.com/en/news/

### B17 — Qwen Research
**Type:** FRONTIER feed  
**Why keep:** current Qwen technical reports / open releases; the old qwenlm.github.io blog now points users here for latest research.  
https://qwen.ai/research

### B18 — Google Research Blog
**Type:** FRONTIER feed  
**Why keep:** architecture, memory, multimodal, robotics and theory posts with links to primary papers.  
https://research.google/blog/


---

## Game NPC / interactive-character industry evidence

### B19 — Ubisoft — NEO NPC
**Type:** INDUSTRY / boundary evidence  
**Why keep:** writer-authored character identity and constraints are combined with generative dialogue; useful production reference for the authoring-vs-model boundary.  
https://news.ubisoft.com/en-us/article/7Cm07zbBGy4Xml6WgYi25d/ubisoft-reveals-neo-npc

### B20 — Ubisoft — Teammates
**Type:** FRONTIER / industry prototype  
**Why keep:** moves generative characters from standing conversation into FPS-style voice-directed co-play, where tactical action and personality must coexist.  
https://news.ubisoft.com/en-us/article/3mWlITIuWuu0MoVuR6o8ps/ubisoft-reveals-teammates-an-ai-experiment-to-change-the-game

### B21 — NVIDIA ACE — autonomous game characters
**Type:** INDUSTRY / systems map  
**Why keep:** useful source for deployed constraints around local inference, perception, speech, reasoning and control; do not treat product claims as scientific evidence.  
https://developer.nvidia.com/ace

### B22 — NVIDIA / KRAFTON — How PUBG Ally was built
**Type:** INDUSTRY / architecture report  
**Why keep:** unusually concrete production decomposition: fast/reflexive behavior-tree control plus a small local LLM for deliberate coordination/reasoning/speech. Strong evidence that NPC control authority and timescale are practical design variables.  
https://developer.nvidia.com/blog/how-krafton-built-pubg-ally-a-co-playable-character-powered-by-nvidia-ace/

---

## Primary literature / proceedings fallbacks

When the curated library is insufficient, prefer these before generic search results:

- ACL Anthology — https://aclanthology.org/
- OpenReview — https://openreview.net/
- NeurIPS proceedings — https://proceedings.neurips.cc/
- PMLR — https://proceedings.mlr.press/
- arXiv — https://arxiv.org/

For a current claim:
1. verify the primary paper/report;
2. verify publication/release date;
3. distinguish public artifact availability from “coming soon”;
4. only then update this library.
