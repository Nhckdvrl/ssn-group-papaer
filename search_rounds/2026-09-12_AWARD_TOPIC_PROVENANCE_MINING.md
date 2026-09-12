# 2026-09-12 — Award-Paper Topic Provenance Mining

**Target:** ACL / NAACL / EMNLP Main, calibrated especially on Best / Outstanding papers.  
**Purpose:** correct a search failure. Do not generate topics from abstract templates such as `X ≠ Y`, `proxy ≠ target`, or `same A ≠ same B` and then hunt for an application. Study where strong papers actually started.

## What strong papers actually start from

### 1. ACL 2026 Best — The Imperfective Paradox in Large Language Models

**Concrete starting point:** a textbook-clean semantic contrast with an immediate example: `was building a house` does not entail `built a house`, while `was running` does entail `ran`.

**Why it is a strong topic source:** the phenomenon existed independently for decades, has clean judgments, needs no invented benchmark story, and becomes newly interesting because LLMs are now claimed to reason compositionally. The larger teleological-bias story grows from the empirical result; it is not the starting abstraction.

**Search lesson:** look for a concrete, old, independently interesting phenomenon with simple natural cases and a modern capability claim that makes it newly diagnostic.

### 2. NAACL 2025 Outstanding — AdvScore

**Concrete starting point:** the field calls datasets `adversarial`, but as models improve those datasets become stale, and there was no standardized way to tell whether they are still genuinely adversarial relative to humans.

**Why it is a strong topic source:** it begins from an existing benchmark practice with a visible operational contradiction, not a philosophical distinction. Human responses already supply the natural external reference.

**Search lesson:** inspect important labels used by the field (`adversarial`, `hard`, `robust`, `faithful`, etc.) and ask whether current practice actually operationalizes the ordinary/field meaning of that label.

### 3. NAACL 2025 Outstanding — PeerQA

**Concrete starting point:** expert peer reviewers already ask hard, real scientific questions while reading papers. Instead of inventing QA questions, use those naturally occurring questions; ask original authors for answers.

**Why it is a strong topic source:** the task comes from a real professional workflow. Difficulty and relevance pre-exist the benchmark.

**Search lesson:** look for artifacts created naturally by experts while doing real work: reviewer questions, error reports, revision requests, support tickets, adjudication notes, analyst comments, etc. These can reveal tasks that benchmark designers would not think to synthesize.

### 4. TACL 2024 Best Paper / ACL 2025 award — Reading Subtext

**Concrete starting point:** short-story summarization has nuanced subtext and non-linear timelines, but automatic metrics and outsider annotators may not know what the story intended. The authors themselves do.

**Why it is a strong topic source:** the data/gold source is obvious once noticed: use unpublished stories and their writers. The paper then discovers >50% faithfulness problems and metric–author disagreement.

**Search lesson:** search for tasks where an unusually authoritative natural judge exists but standard NLP evaluation ignores them: original creator, decision-maker, domain expert, downstream user, or the person whose intent is being modeled.

### 5. ACL 2025 Outstanding — Rethinking GEC Evaluation Metrics

**Concrete starting point:** human GEC evaluation and automatic GEC evaluation aggregate sentence-level judgments differently. If both aim to rank systems according to human preference, why are their evaluation procedures different?

**Why it is a strong topic source:** the discrepancy is tiny, concrete, inspectable, and already embedded in a mature task. No new philosophical object or expensive data construction is needed.

**Search lesson:** compare actual pipelines step by step. Strong topics can come from a mundane procedural mismatch between what humans do and what automatic evaluation does.

### 6. ACL 2025 Outstanding — All That Glitters is Not Novel

**Concrete starting point:** research-agent papers increasingly claim to generate novel scientific ideas. Instead of building another novelty metric, manually inspect the outputs under a different question: are they actually borrowing existing ideas without attribution?

**Why it is a strong topic source:** it attacks a live, important community claim using direct expert inspection of real system outputs. The paper grows from an uncomfortable empirical observation, not from an abstract construct.

**Search lesson:** inspect the strongest claims made by fashionable systems and ask what obvious failure mode their published evaluation did not check. Prefer an audit that a skeptical human would naturally perform.

### 7. EMNLP 2025 Outstanding — Measuring CoT Faithfulness by Unlearning Reasoning Steps

**Concrete starting point:** models print chains of thought that are supposed to explain their answer, but prior work cannot establish whether those verbalized steps are actually tied to the model's parametric decision.

**Why it is a strong topic source:** the question grows from a direct mismatch between a widely used artifact (`reasoning trace`) and the causal claim people implicitly make about it. The method follows from the question: remove the claimed reasoning information and see whether the prediction changes.

**Search lesson:** find widely used artifacts whose interpretation makes a causal claim stronger than the measurement actually supports, then seek a decisive intervention rather than another correlation.

### 8. ACL 2026 Best — Characterizing Local Attention

**Concrete starting point:** local attention is usually sold as an efficiency restriction, yet empirical work sometimes finds that it improves model quality. Why can a restriction improve capability?

**Why it is a strong topic source:** it begins from a stable, counterintuitive engineering observation already reported by others. The paper explains the anomaly with theory and validates it experimentally.

**Search lesson:** search for robust `should hurt, but helps` / `should help, but hurts` observations in mature NLP practice that currently have no satisfying explanation.

### 9. ACL 2026 Best Theme — Mapping the Circumplex of Affect

**Concrete starting point:** psychology has a long-standing geometric model of emotion that NLP researchers often use interpretively, but its geometric assumptions had rarely been imposed and tested directly in language-model representations.

**Why it is a strong topic source:** a real external theory makes a concrete structural prediction; modern representation learning finally lets the prediction be tested, including a performance–interpretability trade-off.

**Search lesson:** external theories are useful only when they make a concrete, falsifiable prediction about an NLP object. Do not mine abstract concepts without such a prediction.

## Revised topic-generation rules

1. **Start from a concrete source, not an abstract distinction.** Every lead must name the actual paper practice, empirical anomaly, real workflow artifact, long-standing phenomenon, external theory prediction, or untested community claim that caused the question to exist.
2. **The one-sentence origin must sound natural before mentioning the proposed experiment.** If the question only becomes interesting after describing our manipulation/schema, kill it.
3. **Prefer cheap/natural evidence.** Strong exemplars often exploit data already created by the phenomenon: human responses, peer reviews, author judgments, real model outputs, existing benchmark procedures, or established natural contrasts.
4. **Do not reward data archaeology.** Needing multi-database linkage, bespoke ontology reconstruction, or extensive manual relabeling is a strong negative prior unless the scientific question is exceptional.
5. **Do not begin with `X ≠ Y`.** Such formulations may summarize a mature result later, but they are not a generator.
6. **Look for five concrete origin mechanisms:**
   - a textbook/simple phenomenon newly diagnostic of LLM claims;
   - an existing field label whose operationalization visibly contradicts its intended meaning;
   - real expert-workflow artifacts that naturally define a task/gold;
   - a robust, surprising empirical anomaly lacking an explanation;
   - a strong current system/community claim that omitted an obvious skeptical check.
7. **Only after finding the concrete origin** do novelty audit, successful-result test, data audit, and Main-level development-path analysis.

## Immediate correction

L27 and similar evidence-schema topics exposed the failure mode: a technically valid representation issue can still be a bad research topic when the motivating question is niche, construction-heavy, and data-hungry. Finding a natural witness does not rescue a weak topic.

Next search rounds should therefore spend substantially more effort mining **topic origins in award / outstanding papers and real NLP practice**, and substantially less effort enumerating classical distinctions from medicine, law, statistics, or philosophy and trying to attach them to LLMs.