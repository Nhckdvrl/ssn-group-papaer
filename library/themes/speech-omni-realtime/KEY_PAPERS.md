# Key Papers — 语音、全模态与实时交互（Speech / omni / realtime）

从 `library/KEY_PAPERS.md` 按题材拆出（2026-09-30），ID 与内容保持不变。标签含义见 `../../KEY_PAPERS.md`。


## Omni / speech

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| VO01 | **Moshi: a speech-text foundation model for real-time dialogue** (2024) | ANCHOR / ARTIFACT | Full duplex as a modeling problem; parallel user/system streams and physical-time constraints. | https://arxiv.org/abs/2410.00037 |
| VO02 | **Qwen2.5-Omni Technical Report** (2025) | ANCHOR / ARTIFACT | Thinker–Talker separation, streaming multimodal input, text/speech co-generation; useful architecture reference. | https://arxiv.org/abs/2503.20215 |
| VO03 | **τ-Voice: Benchmarking Full-Duplex Voice Agents on Real-World Domains** (ICML 2026) | PARENT / BENCHMARK / ARTIFACT | Direct grounded-task comparison between strong text/half-duplex agents and full-duplex voice agents; establishes a substantial capability transition rather than a pure ASR problem. | https://arxiv.org/abs/2603.13686 |
| VO04 | **Stream RAG: Instant and Accurate Spoken Dialogue Systems with Streaming Tool Usage** (ICML 2026) | PARENT / METHOD | Starts retrieval/tool preparation before the user finishes speaking; important parent for overlapping perception and action. | https://arxiv.org/abs/2510.02044 |
| VO05 | **Hierarchical Acoustic-Semantic Modeling / Lychee-FD** (ACL 2026 Outstanding) | PARENT / ARTIFACT | Finds acoustic–semantic gradient conflict in native full-duplex SpeechLM training and separates parameters hierarchically. | https://aclanthology.org/2026.acl-long.419/ |
| VO06 | **Full-Duplex-Bench v3** (2026) | FRONTIER / BENCHMARK / ARTIFACT | Real-human disfluency plus multi-step tool use; useful diagnostic substrate for interaction failures without requiring us to invent a new benchmark. | https://arxiv.org/abs/2604.04847 |
| VO07 | **Speech-Hands** (ACL 2026) | PARENT / ROUTING | Shows naive integration of noisy speech hypotheses can hurt and studies when an Omni model should rely on specialist audio perception. | https://aclanthology.org/2026.acl-long.1997/ |
| VO08 | **OmniInteract** (2026) | FRONTIER / BENCHMARK | Tests native online audiovisual interaction and exposes a gap between offline capability and streaming interaction. | https://arxiv.org/abs/2605.26485 |
| VO09 | **NemotronLabs VoiceChat** (2026) | FRONTIER / ARTIFACT | Open 11B full-duplex speech-to-speech model with a parallel structured function-call stream; practical model-level foothold. | https://arxiv.org/abs/2609.21967 |
| VO10 | **Qwen-Audio-Agent Technical Report** (2026) | FRONTIER / ARTIFACT | Foreground dialogue plus background delegated agents, explicit task state, cancellation/modification, result delivery, and persistent memory; practical asynchronous-runtime foothold. | https://arxiv.org/abs/2609.25195 |
| VO11 | **How Should LLMs Listen While Speaking?** (2026) | FRONTIER / ARCHITECTURE | Contrasts direct channel fusion with cross-attention routing and exposes grounding-vs-context-corruption pressure under overlapping speech. | https://arxiv.org/abs/2605.10199 |
| VO12 | **Full-Duplex Speech Models Take the Floor When Asked, Not When Needed** (2026) | FRONTIER / BEHAVIOR | Separates turn opportunity from semantic need to intervene; important ownership boundary for proactive-speaking research. | https://arxiv.org/abs/2609.19596 |
| VO13 | **Speaking While Listening: Full-Duplex Survey and Empirical Audit** (EMNLP 2026 Main) | SURVEY / FIELD MAP | L0–L3 architecture hierarchy, T×I×R ontology, state machine, and the crucial empirical result that architecture levels are not a progress ladder; use before making any full-duplex frontier claim. | https://arxiv.org/abs/2606.19453 |
| VO14 | **DuplexCascade** (2026) | PARENT / ARTIFACT | Important counterexample to “native end-to-end is necessary”: VAD-free cascaded ASR–LLM–TTS with micro-turns preserves strong text-LLM intelligence while supporting duplex interaction. | https://arxiv.org/abs/2603.09180 |
| VO15 | **Realtime-Venus** (2026) | FRONTIER / ARTIFACT | Open 9B full-duplex frontend plus asynchronous Harness; request-time context capture, background work, private feedback, freshness and playback-aware delivery make computational boundaries directly instrumentable. | https://arxiv.org/abs/2609.13814 |
| VO16 | **A frontend-backend architecture for tool calls in full-duplex speech models** (2026) | FRONTIER / ARCHITECTURE | NVIDIA design: streaming duplex frontend delegates transcript to a text backend and reinjects results; strong evidence for 2026 foreground/backend convergence. | https://arxiv.org/abs/2609.19334 |
| VO17 | **Unified Audio Intelligence Without Regressing on Text Intelligence (Audex)** (2026) | COUNTEREXAMPLE / FRONTIER | Large-scale unified audio-text decoder reports strong audio capability with little text regression; prevents overclaiming that separation/modularity is inherently necessary. | https://arxiv.org/abs/2607.05196 |
| VO18 | **The Latent Bridge: A Continuous Slow-Fast Channel for Real-Time Game Agents** (2026) | CROSS-DOMAIN / ARTIFACT | Fast reactive + slow reasoning models with communication as the load-bearing variable; text/latent bridge results and channel interference are a direct cross-domain ownership boundary. | https://arxiv.org/abs/2606.24470 |
