# Deep Open-Artifact Archive

> **2026-09-30：** 素材库已按题材重组（`../../README.md`）。本目录保留长篇原文；每个题材页（`../../themes/<题材>/README.md` §4）列出了本目录中与该题材相关的章节。单一题材的文件已移入对应题材目录。


Open models, checkpoints, code, Hugging Face/startup artifacts, and lineage notes.

Primary use: artifact archaeology before compute. Availability of an artifact is not itself a research idea.

## Interpretability / model-science artifacts

Detailed current map: [`INTERPRETABILITY_TOOLING_2026.md`](../../themes/interpretability-representation/INTERPRETABILITY_TOOLING_2026.md)（已移入题材目录）.

Use the map to choose an instrument from the scientific claim (localization, causal-variable intervention, sparse decomposition, model diffing, abstraction validity), not to choose a trendy tool first and then manufacture a question.


## Game NPC / interactive-character artifacts

| Artifact | Status checked 2026-09-28 | Use |
|---|---|---|
| https://github.com/microsoft/interactive-minecraft-npcs | public prototype | historical dialogue→code/action NPC |
| https://github.com/microsoft/collaborative-quest-completion | public gameplay logs/recordings | human–NPC collaboration evidence |
| https://github.com/Augustus2011/sony-cpdc-2025-starter-kit | public data + harness | cheap persona + task/function-calling substrate |
| https://github.com/MahammadNuriyev62/CPDC-challenge-2025-solution | code + Qwen3 1.7B/14B LoRAs | strong CPDC implementation baseline |
| https://github.com/INV-WZQ/ReactiveGWM | inference/training + model/data links | open game-world-model NPC baseline |
| https://github.com/JunseoKim0103/Lies-We-Can-See | Docker + VLM harness + data/logs | embodied verbal/non-verbal social behavior |
| https://github.com/altera-al/project-sid | public report/repo | large-scale Minecraft agent society |
| https://github.com/yoosunghong/pcsp | unusually complete research + UE5 artifact; code, envs, persona splits, training/eval scripts, results and later self-audits | strongest current substrate for testing whether free-form persona semantics actually ground into NPC action policy; later independent-behavior audit is especially valuable |
| https://github.com/carrotoxic/mario-personas | CoG 2026 code + checkpoints + PCG levels + human demonstrations | explicit behavioral-persona comparator (runner/killer/collector) with concrete action/outcome metrics |
| NCP-Bench project/repo | public code/data/prompts; verify current canonical repo before cloning | long-horizon narrative commitments |
| https://github.com/DilanRG/ai-murder-mystery-v2 | full Python/JS game engine, offline authored fixtures, strict truth/evidence/knowledge schemas, deterministic replay, authorized lies, 400+ tests | strongest current open substrate for controlled detective-NPC deception / deductive-fairness experiments |
| https://github.com/jiangaoMartin/F21CA-Games3-Minecraft-Murder-Mystery | Minecraft world + prompts + evaluation material | open free-form voice/NPC detective baseline; much looser state control than Ashwick |

**Artifact warning:** WorldMind was a frontier prior when checked, but should not be treated as the reproduction baseline until its promised code/weights are actually available. Proact-VL also had incomplete release components when checked.
