# 2026-09-15 — WALL-U / Why Does an External Scratchpad Increase Transformer Capability?

**Mode:** external-memory / recurrent-computation ancestry → Transformer expressivity theory → direct-owner audit  
**Outcome:** **EXHAUSTED AS A CURRENT TOPIC GENERATOR — NO NEW L-SERIES — NO PILOT**

# Mother problem

> When a fixed-parameter sequence model is allowed to emit intermediate symbols and read them back before answering, does this merely make an existing computation easier to learn, or does it fundamentally increase the computation the architecture can realize?

The question is older than CoT: external tapes/scratchpads/recurrent computation are classical ways to trade time and external state for computational power.

# Direct modern owners

Merrill & Sabharwal, ICLR 2024, *The Expressive Power of Transformers with Chain of Thought*, directly prove that intermediate generation fundamentally changes decoder-only Transformer expressive power, with the increase depending on scratchpad length.

Li et al., ICLR 2024, *Chain of Thought Empowers Transformers to Solve Inherently Serial Problems*, independently formalize CoT as serial computation unavailable to shallow/constant-depth parallel Transformer computation.

Amiri Bavandpour et al., ICML 2025, then derive lower bounds on the number of CoT steps required for different algorithmic problems, showing that even problems in apparently favorable circuit classes may need substantial scratchpad length.

Representative sources:
- https://proceedings.iclr.cc/paper_files/paper/2024/hash/1f59721c106ea80f613299039112f651-Abstract-Conference.html
- https://proceedings.iclr.cc/paper_files/paper/2024/hash/3309b4112c9f04a993f2bbdd0274bba1-Abstract-Conference.html
- https://proceedings.mlr.press/v267/bavandpour25a.html

# Decision

The attractive distinctions — `memory vs depth`, `elicitation vs new computational capacity`, `how many steps are necessary`, `parallel padding/looping vs tokenized CoT` — are already an active formal-theory program.

A new empirical LLM paper would reviewer-compress to theory validation / another algorithmic task, while a new theorem would require genuinely new formal ownership rather than an NLP Main question.

**WALL-U exhausted as current generator.**

No L-series is created.