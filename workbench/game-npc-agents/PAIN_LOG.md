# 本地痛点与意外现象

## P01 · 2026-10-14 · 本地依赖/运行路径恢复（工程痛点，不是科学增量）
ActionCastle首次导入缺prompty/aiofiles：现有Conda fgvd加隔离依赖overlay后CPU闭环8/8通过。PCSP原测试在PettingZoo1.24.3因AgentSelector导入失败；改用1.25.0后重试，原失败日志保留。
Qwen3-32B单GPU权重成功加载61.03 GiB，但vLLM0.23.0/flashinfer采样kernel warmup找不到PATH中的ninja，尚未发生模型推理。需完整Conda激活，或明确使用已有非flashinfer采样器。工程失败不能当“persona行为失败”。版本、log与资产见E07/E08。

## P02 · 2026-10-14 · 作者目标动作与当前地点/执行后果错位（单seed发现性观察）
E07 Qwen3-32B non-thinking、原生pureReAct seed101，20次NPC决策，11/20合法执行，4次NPC动作有material变化；未启script fallback。troll在已经位于Drawbridge时说“return to my post”却执行go west离开，guard离开Courtyard后该处阻挡解除；ghost离开Dungeon后因黑暗连续返回失败（1/9动作成功），其目标性理由没有消失。全部失败保留。
不是已证明persona失效：竞争解释H1为NPC原生观测/动作语法/后果信息不足，H2为地名与自我位置整合或叙事prior导致目标型语言先于当前state；H3为non-thinking/128token/采样的运行模式影响策略；H4为多NPC/未在场全局Game narration与history使目标对象错位。最小下一动作：在同一自然snapshot分别测无历史的当前位置、原版action、一个明确核当前地点的提示和信息等价structured state；先定位，再谈新机制。CPU自动吃鱼事实仍仅为执行归因。

## P03 · 2026-10-14 · 位置probe与原生动作contract不同（E09）
Gemma3-12B在发现性snapshot原版location9/9，却action合法3/9；单句/viewer/neutral能保持location但动作变0/9，raw输出包含不在场target等失败。Qwen32部分位置literal失败是前缀格式而非知识。位置原文、probe格式/语义、动作参数/对象scope必须分开；不能由“模型知道当前位置”或“问卷正确”自动判断execution能力，亦不能强行把位置提示改善称策略改善。下一步先作者per-action descriptions/scoped tool arguments与可靠格式，不加训练。
