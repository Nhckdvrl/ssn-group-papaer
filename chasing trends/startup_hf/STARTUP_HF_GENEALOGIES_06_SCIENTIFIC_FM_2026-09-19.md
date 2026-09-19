# Startup & Hugging Face Genealogies 06 — Scientific Foundation Models — 2026-09-19

> Status: literature / research-taste calibration only.
>
> NO formal CT candidate generation.
>
> This file extends the Startup/HF track into scientific foundation models.
>
> The purpose is not to chase "AI for Science" as a trend.
>
> It is to learn from domains where the scientific object is often more explicit than in general-purpose LLMs:
>
> - what is the natural token/unit?
> - what nuisance variables are known rather than latent?
> - what spatial/temporal/functional scale matters?
> - what should the pretraining objective preserve?
> - what makes a representation useful to the downstream scientific consumer?
>
> The most important finding from this batch:
>
> > **A domain foundation model becomes scientifically interesting when domain structure changes the tokenizer, objective, context, representation unit, or evaluation contract — not merely when the training corpus comes from a scientific field.**

---

# S59 — Genomic FM design exposes a three-way conflict: sequence length, supervision resolution, and biological function

Recent DNA/genomic models make a useful contrast because the raw alphabet is tiny but the meaningful structures span enormous scales.

A genomic model may need to represent:
- single-nucleotide variation;
- short motifs;
- genes;
- regulatory regions;
- multi-gene neighborhoods;
- whole-genome context.

One representation rarely optimizes all scales simultaneously.

---

# S60 — Carbon: coarse tokenization creates a supervision-resolution problem

Carbon is a fully open autoregressive genomic FM family from Hugging Face / collaborators.

Public artifacts include:
- Carbon-500M;
- Carbon-3B;
- Carbon-8B;
- pretraining corpus;
- Megatron-LM training fork;
- evaluation code;
- fine-tuning recipes.

This makes it unusually high instrument value.

---

## S60.1 Hybrid tokenizer is driven by throughput, not linguistic fashion

Carbon uses:
- ordinary BPE for English text;
- non-overlapping 6-mer tokens for DNA;
- a modality tag to switch tokenization.

A 6-mer compresses six base pairs into one model token.

Benefit:
> much longer biological sequence per transformer token.

But this creates a cost:

\`\`\`
compute efficiency ↑
→ nucleotide-level supervision resolution ↓.
\`\`\`

The tokenizer is therefore not a neutral preprocessing choice.

It changes what the loss can directly supervise.

---

## S60.2 FNS repairs information lost by coarse tokenization

Carbon's training fork includes **Factorized Nucleotide Supervision (FNS)**.

Rather than accepting only coarse 6-mer next-token loss, FNS provides base-pair-level supervision for DNA k-mer tokens.

The research structure is clean:

\`\`\`
coarse tokenization
→ better sequence-length economics
→ weaker nucleotide-resolution learning signal
→ factorized nucleotide supervision.
\`\`\`

This is an excellent example where:
> the method is derived from the representation's known information loss.

Not:
> append another auxiliary loss because benchmarks improve.

---

## S60.3 Tokenization and context length are coupled

Carbon's 8B release trains initially at an 8,192-token sequence length and later performs a long-context stage to 32,768 tokens.

With 6-mer tokens:
> the biological base-pair span is ~6× the token context.

Thus "context length" in genomics has at least two units:
- model tokens;
- biological base pairs.

Comparing only token context can therefore be misleading across tokenizers.

A model with shorter token context may still see more physical sequence.

This is directly analogous to the earlier Anthropic tokenizer-cost warning:
> a token is not a universal physical unit.

---

## S60.4 Carbon turns the small model into infrastructure for the large model

Carbon-500M is explicitly positioned as a speculative-decoding draft model.

This is important.

A model-size ladder is not necessarily:

\`\`\`
small
→ medium
→ large
\`\`\`

as independent accuracy points.

It can be:

\`\`\`
small model
→ computational component used to accelerate large model.
\`\`\`

So size variants can have different **roles**, not only different capability.

---

## S60.5 Evaluation is designed around biological counterfactuals

Carbon's open evaluation suite includes:
- sequence recovery;
- variant effect prediction;
- repeat insertion;
- synonymous codon substitution;
- long-context DNA retrieval.

Some tests modify sequence while preserving another property.

Example:
> synonymous codon substitution preserves amino-acid identity while changing nucleotide choice.

This is scientifically stronger than arbitrary text perturbation.

The perturbation has a biological invariant.

Research-taste lesson:

> **domain knowledge can make synthetic interventions more causal, not merely more realistic.**

---

# S61 — JEPA-DNA: token reconstruction may be the wrong semantic target

JEPA-DNA starts from a different genomic failure.

Its critique is not about context length or throughput.

It is about the **pretraining objective**.

---

## S61.1 MLM/NTP are locally informative but may not force functional abstraction

Masked-language or next-token objectives reward:
- nucleotide recovery;
- motifs;
- local syntax.

But downstream biological function may depend on broader region-level semantics.

Thus:

\`\`\`
predict exact token identity
\`\`\`

does not guarantee:

\`\`\`
represent functional meaning of the masked region.
\`\`\`

---

## S61.2 JEPA adds latent functional prediction while preserving generative/token objectives

JEPA-DNA adds a joint-embedding predictive objective:
- context encoder sees surrounding sequence;
- target encoder represents the masked region;
- predictor learns its latent representation;
- token-level/generative learning remains.

Primitive change:

\`\`\`
masked region target = nucleotide identities
→ masked region target = nucleotide identities + functional latent representation.
\`\`\`

The method tries to make the model predict:
> what the region *means in representation space*,
not only what characters are missing.

---

## S61.3 The matched-backbone release is more valuable than one headline score

The open project releases JEPA-augmented checkpoints for multiple backbone families, including:
- DNABERT-2;
- Nucleotide Transformer v3;
- HyenaDNA.

For each, the original pretrained backbone can serve as the baseline.

This creates a strong experimental structure:

\`\`\`
same underlying backbone family
→ add one continual-pretraining objective
→ compare representation behavior.
\`\`\`

If the effect appears across substantially different backbones:
> the claim is less likely to be one architecture artifact.

This is much more scientifically valuable than testing only one giant checkpoint.

---

## S61.4 Negative heterogeneity matters

JEPA-DNA is not uniformly better on every fine-grained task.

The reported benefits are more compelling on some global/regulatory-function tasks than on every local sequence task.

That is exactly what the mechanism would predict if:

> latent region prediction mainly improves broader functional abstraction.

A method whose gains concentrate where its hypothesized mechanism should matter is more informative than uniform benchmark gains with no structural pattern.

---

## S61.5 Optimization fragility is itself evidence

The public/reproduction materials indicate the JEPA continual-training setup has nontrivial optimization constraints.

This matters because:

> a semantically appealing objective can still be practically fragile.

For future topic work:
- objective quality;
- optimization stability

must be separated.

Do not interpret a failed run as immediate evidence against the scientific target.

But do not hide the optimization cost either.

---

# S62 — Carbon vs JEPA-DNA: two different answers to "what should DNA pretraining learn?"

Carbon emphasizes:
> preserve fine nucleotide information while making long-sequence autoregression computationally practical.

JEPA-DNA emphasizes:
> add a global/latent functional target beyond literal token recovery.

Their main pressure axes are different.

### Carbon
Representation granularity ↔ throughput ↔ supervision resolution.

### JEPA-DNA
Local token prediction ↔ global functional representation.

Both use DNA.

They are not one scientific lineage.

---

# S63 — NASA–IBM Lunar FM: known nuisance variables should not always be inferred from pixels

The Lunar Foundation Model provides one of the cleanest scientific examples of **explicit confound/context handling**.

---

## S63.1 Lunar imagery has a dominant observation confound

The appearance of lunar terrain changes strongly with:
- illumination angle;
- acquisition geometry;
- viewing/solar conditions.

Two visually different image patches may correspond to:
> very similar terrain under different illumination.

If the model receives only pixels,
it must spend capacity disentangling:
- physical terrain;
- observation geometry.

But acquisition geometry is already known metadata.

---

## S63.2 The model promotes acquisition geometry to explicit context

The NASA–IBM model tokenizes:
- illumination angles;
- solar-frame anchors;
- tile footprint

as encoder context.

Primitive:

\`\`\`
known acquisition variable hidden in image
→ known acquisition variable explicitly conditioned.
\`\`\`

This is a strong scientific design principle:

> **Do not force a model to infer a nuisance variable that the measurement process already records accurately.**

That is very different from:
> add metadata because multimodal models are fashionable.

---

## S63.3 Mixed-resolution pretraining treats physical scale as part of the task

The model jointly trains on:
- high-resolution NAC imagery around ~1 m/px;
- lower-resolution WAC imagery around ~100 m/px.

One set of weights therefore covers a ~100× spatial-scale gap.

The scientific issue is:
> whether the same physical/geological structure can be represented across observation scales.

This is not ordinary image resizing.

Spatial resolution changes:
- visible morphology;
- feature frequency;
- physical interpretation.

---

## S63.4 Modality-wise tokenization preserves sensor semantics

The release uses modality-specific tokenizers rather than immediately collapsing all sensor products into one homogeneous image representation.

This keeps:
> sensor identity / measurement type

visible to the model.

Again:
> multimodal unification does not require pretending modalities are identical.

---

## S63.5 The open artifact is reasonably accessible

Public:
- ViT-B scale backbone;
- tokenizers;
- fine-tuning code;
- pretraining dataset;
- model checkpoint.

Training from scratch still used substantial GPU compute.

But inference/fine-tuning experiments are relatively modest compared with frontier LLM work.

Instrument value:
> A/B.

---

# S64 — Genos-m: specialization changes the prior over biological diversity

Genos-m is a 4.7B-total / ~330M-active MoE specifically for human-associated microbial genomes.

Its key scientific decision is not simply:
> use a smaller active MoE.

It is:
> **change the training distribution to reflect one ecological/biological domain.**

---

## S64.1 General DNA FMs may underrepresent niche-specific structure

Human-associated microbial genomes contain:
- strain-level variation;
- niche-specific genes;
- phages;
- metagenome-assembled genomes;
- large ecological diversity.

A general genomic corpus may optimize for broad phylogenetic coverage but not this specific functional ecology.

Genos-m therefore constructs a curated microbial prior with strong human-associated coverage.

Primitive:

\`\`\`
one universal genomic prior
→ domain/ecology-conditioned genomic prior.
\`\`\`

---

## S64.2 Single-base tokenization makes a different resource trade-off than Carbon

Genos-m uses:
> single-nucleotide tokens.

Carbon uses:
> 6-mer tokens with factorized nucleotide supervision.

Therefore the models make opposite design choices:

### Genos-m
Preserve raw base resolution;
pay more sequence length / rely on sparse active compute.

### Carbon
Compress sequence into coarse k-mers;
restore finer supervision through the loss.

This is exactly the kind of matched conceptual contrast that can generate scientific questions.

Not:
> which model wins?

But:
> **where should biological resolution be preserved: representation or supervision?**

---

## S64.3 MoE capacity is used for biological heterogeneity

Genos-m:
- 32 experts;
- top-2 routing;
- ~4.7B total;
- ~330M active.

The authors frame expert expansion as a way to model diverse microbial sequence structure while keeping active compute modest.

Whether experts correspond to meaningful biology is not automatically established.

This creates a distinction:

\`\`\`
MoE improves capacity/efficiency
\`\`\`

vs

\`\`\`
experts specialize along biological factors.
\`\`\`

The latter needs explicit evidence.

---

## S64.4 SAE analysis asks whether learned units align with known genomic units

The project trains sparse autoencoders over hidden activations and reports sparse features associated with:
- ORFs;
- intergenic regions;
- tRNA;
- rRNA;
- strand direction.

This is useful because it asks:

> does the representation discover scientific structure that can be independently annotated?

That is a better mechanistic target than:
> "find interesting neurons."

The external scientific annotation gives a falsifiable semantic reference.

---

## S64.5 Cross-scale composition is another useful property

For whole-genome phenotype tasks, Genos-m chunks long genomes and aggregates chunk embeddings.

The reported success suggests:
> local/region representations retain enough information to compose into genome-level phenotype features.

That is a scientific representation question:

\`\`\`
local sequence embedding
→ composable whole-system representation?
\`\`\`

This matters beyond genomics.

---

# S65 — Botanic1: architecture should match the sequence process, not the dominant ML fashion

Botanic1 is a recent open plant-genomics FM family.

It uses:
- bidirectional Mamba-2;
- masked modeling;
- single-nucleotide tokens;
- data from hundreds of plant species.

The interesting scientific pressure is:
> long genomic sequence + exact base-level representation.

Rather than forcing standard quadratic attention over huge context,
the model uses a state-space architecture.

---

## S65.1 Domain specificity is not only data specialization

The plant-genome setting includes:
- very long sequence dependencies;
- species variation;
- regulatory patterns;
- coding/noncoding structure.

So the architecture/data/tokenization package is chosen around:
> the physical/statistical structure of genomic sequence.

This is more scientifically grounded than:
> use Mamba because Mamba is trending.

---

## S65.2 Family variants create another public instrument

The model family has multiple sizes.

Combined with:
- frozen embedding evaluation;
- LoRA;
- full fine-tuning;
- zero-shot variant scoring,

this makes it an accessible instrument for studying:
- scale;
- context;
- adaptation regime

within one domain family.

---

# S66 — Domain structure can enter at five distinct places

Across this batch, "use domain knowledge" decomposes cleanly.

## 1. Tokenization
Carbon:
> 6-mer DNA tokenization for sequence economics.

Genos-m/Botanic:
> single-nucleotide resolution.

## 2. Loss / objective
Carbon:
> factorized nucleotide supervision.

JEPA-DNA:
> latent functional prediction.

## 3. Training distribution / prior
Genos-m:
> human-associated microbial ecology.

Carbon:
> eukaryote-heavy genomic prior.

## 4. Context / metadata
Lunar FM:
> explicit acquisition geometry.

## 5. Architecture
Botanic:
> bidirectional state-space sequence model.

NASA Lunar:
> modality-wise tokens + flexible spatial scale.

This gives a much better question than:
> "Can we inject domain knowledge?"

Ask:
> **where in the learning system should the domain constraint live?**

---

# S67 — A useful scientific-FM pattern: known nuisance vs unknown signal

NASA Lunar FM provides a general decomposition.

Suppose observation x contains:

\`\`\`
x = signal(s) + nuisance(n).
\`\`\`

If n is:
- known from the acquisition process;
- measured reliably;
- causally affects x;

then making the model infer n from x may waste representation capacity and entangle the learned signal.

Explicitly condition on n.

By contrast, if n is unknown or noisy:
> hard-coding it can introduce bias.

This distinction appears across:
- remote sensing illumination;
- medical scanner settings;
- experimental batch effects;
- camera parameters;
- robot embodiment metadata;
- audio recording conditions.

This is a transferable scientific structure.

Not a method recipe.

---

# S68 — Another useful pattern: scientific tokenization is a claim about invariance

In language, tokenization is often treated as an engineering choice.

In scientific domains, the token may imply what transformations should preserve meaning.

Examples:

### DNA 6-mer
Assumes local chunks are useful compute units.

### Single nucleotide
Preserves exact mutation resolution.

### Lunar image patch
Represents spatial measurement region.

### Multi-sensor modality token
Preserves sensor identity.

Thus tokenizer design encodes:
> which local variations should be grouped together and which should remain distinguishable.

That is a scientific hypothesis.

---

# S69 — Research-instrument value is unusually high in scientific FMs

Several artifacts are immediately useful for cheap secondary science:

## JEPA-DNA
Very high:
- original backbone vs JEPA continual-pretraining versions;
- multiple backbone families;
- reproduction params;
- benchmark code.

## Carbon
High:
- 500M/3B/8B ladder;
- complete training/eval;
- 500M draft role;
- tokenizer/loss implementation;
- zero-shot perturbation tasks.

## NASA–IBM Lunar FM
High:
- public backbone/tokenizers/data/fine-tuning code;
- explicit geometry metadata.

## Genos-m
Medium/high:
- checkpoint and detailed evaluation;
- planned/partial SAE artifacts;
- ~330M active compute but 4.7B storage.

## Botanic1
High:
- multiple sizes;
- frozen/LoRA/full adaptation paths.

These may be better experimental substrates for representation/pretraining questions than re-training language models.

---

# S70 — Scientific FM anti-patterns

## Anti-pattern A — "domain-specific data" as the whole contribution

Not enough.

Need:
> why does the domain alter representation, objective, evaluation, or inference?

## Anti-pattern B — transfer an LLM tokenizer blindly

Scientific units may not align with text token boundaries.

## Anti-pattern C — performance-only domain specialization

If a specialized model is better,
ask whether the reason is:
- data distribution;
- tokenizer;
- architecture;
- scale;
- contamination;
- evaluation fit.

## Anti-pattern D — interpretability without external semantics

Scientific domains are valuable partly because they provide:
- annotations;
- known structures;
- causal variables.

Use them.

## Anti-pattern E — longer context as goal

Biological/physical sequence length matters only if:
> the downstream property depends on those scales and the model actually uses the information.

---

# S71 — Current conclusion

Scientific foundation models reinforce a broader lesson from the startup/HF scan:

> **The most interesting research often happens where the representation boundary is forced by the structure of the world rather than by the conventions of current ML architectures.**

Examples:
- one base vs one k-mer;
- local token vs region function;
- terrain vs illumination geometry;
- one microbial species vs ecological community;
- one spatial resolution vs multi-scale measurement.

This is especially valuable for our topic-search training because it forces us to ask:

> What is the real scientific object?
> What information is nuisance?
> What information must stay identifiable?
> What computation is required by the downstream consumer?

Still no formal candidate generation.
