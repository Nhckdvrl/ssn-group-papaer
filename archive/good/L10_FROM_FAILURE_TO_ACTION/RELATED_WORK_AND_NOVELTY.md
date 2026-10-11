# L10 — Related Work and Open Scientific Space

**Freshness:** 2026-09-09

# 1. Established starting point

**ImplicitMemBench** (ACL 2026 Best Resource Paper) establishes a large gap between preference adaptation and inhibition across 17 models.

**Fission-GRPO** (ACL 2026) independently shows a related natural tool-use failure: models can repeat invalid calls after execution errors instead of recovering.

Together they make the behavioral object real enough to study directly.

# 2. What nearby work mainly asks

Reflection, mistake notebooks, negative-experience replay, corrective supervision, and learned reflectors largely ask:

> **How can we make failure experience useful?**

They show that failure contains usable information.

L10 asks:

> **When failure is already available in context, where does the conversion from experience to future action break?**

# 3. Open scientific space

The distinctive chain is:

> outcome retained  
> → responsible action identified  
> → replacement policy available  
> → actual action follows or violates that policy

L10's contribution is to locate the missing transition and causally complete it.

The central object is therefore the **experience→action transformation**, not a new memory architecture and not another failure benchmark.

# 4. Negative constraints as one boundary

Work on explicit negative constraints matters if the bottleneck turns out to be late behavioral inhibition.

That is one possible explanation of the final transition, not the starting story.

# 5. Current novelty judgment

The natural question remains open:

> **Why can a model remember a failure yet fail to act differently because of it?**

Refresh the literature if the winning stage changes the central explanation.
