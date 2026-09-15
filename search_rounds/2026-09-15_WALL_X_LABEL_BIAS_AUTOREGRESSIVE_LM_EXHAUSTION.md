# WALL-X — Label bias vs autoregressive language modeling

Date: 2026-09-15
Status: KILLED — PREMISE MISMATCH

## Tempting mother question
Classic structured-prediction theory treats local normalization as vulnerable to label bias. Modern decoder-only LMs are locally normalized autoregressive models yet model long-range structure successfully. Why are they not crippled by label bias?

## Theoretical audit
This apparent contradiction is largely a premise mismatch.

Classic label bias is harmful when an incremental locally normalized model must commit before observing future input evidence; probability mass normalized away at earlier states cannot later be recovered. Globally normalized models can use evidence from the whole structured output/input configuration.

However, high-capacity neural sequence models that condition on the complete observed input can be representationally equivalent under local and global normalization (Goyal, Dyer, Berg-Kirkpatrick, NAACL 2019); remaining differences concern search-aware optimization and inexact search.

For an unconditional/prefix-conditional autoregressive LM, the true joint distribution itself admits the exact chain-rule factorization p(x_1:T)=prod_t p(x_t|x_<t). There is no missing future observed input that the current conditional ought to use. Therefore importing the MEMM/CRF label-bias theorem directly to next-token language modeling is not a valid old-theory-vs-modern-regime contradiction.

## Verdict
Do not promote. The attractive framing was conceptually wrong before novelty search.

## Anti-resurrection
Do not revive as:
- 'LLMs are locally normalized so why no label bias?'
- global vs local normalization for decoder-only LM without a precise missing-information condition;
- future-token evidence as if it were observed input at current decoding time;
- old CRF theorem mechanically transplanted to autoregressive language modeling.
