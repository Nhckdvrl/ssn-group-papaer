# Parent EPO — verbatim spec, checked against arXiv 2605.07260 on 2026-09-23

Fetched from `https://arxiv.org/html/2605.07260v1`. *When Are Experts Misrouted?
Counterfactual Routing Analysis in Mixture-of-Experts Language Models*, Yoon,
Wang, Chen, Ok. Recorded because every E11 claim is a claim about this object,
and until now the project had been working from a second-hand reading.

| item | parent (quoted) | E11 |
|---|---|---|
| `r⁻` | "let r⁻_t be the top-k route currently selected by π_θ" | same |
| candidates | "sample G alternative top-k routes from π_θ via Gumbel-top-k" | same |
| skip rule | improving route becomes `r⁺`, "otherwise the token contributes no gradient" | same |
| route log-prob | "We treat each route r as a sequence of experts and use the factorized log-probability log π(r\|x_t)=Σ_{e∈r} log π(e\|x_t)" | same |
| loss | `ℓ_t = −Δ_t log σ(β log π_θ(r⁺)/π_ref(r⁺) − β log π_θ(r⁻)/π_ref(r⁻))` | same |
| lr / β / batch / epochs | 3e-4 / 0.1 / 16 / 1 | same |
| G, τ | 32 for Qwen3, τ = 0.1 | 32, 0.1 |
| layer | "we update only the final-layer router while leaving every expert and every other router frozen" | **L47 = final layer of Qwen3-30B-A3B** |
| downstream | pass@K on AIME24+25, HMMT25, 160 completions/problem | not run (see below) |

Two consequences worth stating plainly.

**The parent is explicit that the factorized form is a chosen surrogate** — "we
treat each route as a sequence of experts and use the factorized
log-probability". So the mismatch E11 measures is not an error in their paper;
it is a property of a surrogate they define openly. Any write-up must say this.

**E11 reproduces the parent's setting including the layer.** The final-layer
router is not a convenience choice we made and the parent's own headline
setting; they coincide. That removes "you trained the wrong layer" as an
explanation for the E11 null.

The one thing E11 does not match is the downstream evaluation, which was
deliberately not run — see `results/RESULTS_E11_CORRECTED_L47.md`.
