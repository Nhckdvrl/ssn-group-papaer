# Draft request to the authors (for the user to send; not sent)

To: Yanhong Li <yanhongl@allenai.org>, William Merrill <willm@allenai.org>
(addresses from the 2606.20936 title page)

Subject: Checkpoints behind "Comparing Transformers and Hybrid Models at the Token Level" (§6) and the Olmo Hybrid YaRN branch

Dear Yanhong and Will,

We are building on *Comparing Transformers and Hybrid Models at the Token Level* (arXiv 2606.20936)
and *Olmo Hybrid* (2604.03444). We reproduce your natural-token analysis on the released 7B pair and
would like to separate the architecture contribution from recipe differences. Your 1B ladder is the
only setting where "the only difference between runs is the architecture itself", so it is the
natural control. We could not locate the following and would be grateful for pointers:

1. The **1B Transformer / Hybrid / Pure-GDN development runs** used for Fig. 7 (WSD-annealed
   checkpoints): a URI or HF revision per run (`olmo-checkpoints.org` paths would be ideal). The
   paper states they are released under Apache 2.0, but we could not find them on the HF hub or in
   OLMo-core (the `linear-rnns/1b/*` scripts only give the configs, not the run names).
2. The exact **config / run names** for those three runs.
3. The **natural-token evaluation manifest** (document IDs or sampling code for PG-19, CC-News,
   Wikipedia, ArXiv, Python, HTML, LaTeX) and the preprocessing / tagger code, so that our
   numbers are comparable with yours.
4. If possible, the **Olmo Hybrid + YaRN long-context checkpoint** (the 64K RULER 76.9 result,
   compared with DroPE 85.0), to compare positional treatments within the same architecture.

One question that affects how we read our 7B numbers: which inference stack did you use to score
Olmo 3 7B? In transformers 5.x (up to 5.12.1, with the released `rope_scaling` config), YaRN is also
applied to the sliding-window layers. In our runs this raises NLL steeply with position; 4.57.6
does not have the issue (cf. transformers #45945 / #48392).

Thank you very much for the work and for any help.

Best regards,
<name, affiliation>
