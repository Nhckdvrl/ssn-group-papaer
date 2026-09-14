# WALL-AT — Test-time compute: breadth versus depth

Date: 2026-09-15
Status: EXHAUSTED / ACTIVE CORE PROGRAM

## Mother question
Under a fixed inference-compute budget, should a reasoning system spend compute on exploring more independent candidate trajectories (breadth) or on extending/refining a smaller number of trajectories (depth)? Classical search/value-of-computation theory suggests this allocation should depend on problem structure rather than be universally fixed.

## Direct-owner audit
This allocation question is already central to test-time scaling research.

- Snell et al., ICLR 2025, explicitly asks how a fixed nontrivial inference budget should be allocated and develops compute-optimal scaling; the best strategy varies strongly with prompt difficulty.
- PaCoRe, ACL 2026 Main, scales test-time compute through massive parallel breadth plus multi-round coordination and explicitly argues coordinated parallel exploration can outperform simply extending a single chain.
- 2026 *Refining Over Resampling* directly frames the problem as breadth versus depth and combines independent sampling with iterative refinement.
- Other 2025–2026 work develops adaptive Best-of-N, beam/BoN hybrids, recurrent-depth reasoning, and budget-rationing strategies.

## Verdict
No L-series. Breadth-vs-depth is now a core test-time-compute axis. Without an independently inherited structural variable that predicts a qualitative crossover, another budget-allocation study is method work.

## Anti-resurrection
Do not revive as:
- Best-of-N vs longer CoT;
- sampling breadth vs self-refinement depth;
- compute-allocation sweeps across difficulty;
- adaptive breadth/depth routing;
- value-of-computation applied generically to reasoning unless a new old-theory quantity supplies a nontrivial prediction.
