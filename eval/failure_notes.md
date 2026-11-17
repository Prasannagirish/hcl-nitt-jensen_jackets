Two runs are reported. **Run 1** is the first evaluation (saved in `eval/run1_baseline/`). **Run 2** is the current one, after one change to the evidence gate described in failure 1. By the rule-based checks both runs score 15 of 21 correct; citation accuracy went from 15 to 16 of 21; grounded stayed at 21 of 21. The rules were not changed between runs. Because run 2 followed a look at the run 1 failures, it is **not a blind result**.

### Failure 1: the evidence gate rejected answerable questions (q07, q17)

- **What happened.** In run 1 both questions returned "No answer found", although the right evidence had been retrieved. The best rerank scores were 0.681 (q07, limitations of the safety paper) and 0.807 (q17, techniques across the whole collection). The gate threshold was 0.869.
- **Cause.** The threshold was calibrated on seven narrow, specific dev questions, where answerable questions score 0.95 or more. Broad questions score much lower with a reranker, because no single passage answers them. The earlier "answerable and unanswerable questions separate" result was an artefact of having no broad questions in the dev set.
- **What was changed.** Ten more dev questions were added (six broad answerable, four near-topic unanswerable), none of them from the evaluation set. On the 23 dev questions the two groups overlap heavily (answerable 0.04 to 0.99, unanswerable up to 0.81), so a score cannot tell them apart. The gate became a coarse off-topic filter (threshold 0.0185, half the lowest answerable score) and the model's own "no supporting claims" answer does the fine-grained work. End to end on the dev set: 13 of 13 answerable questions answered and 10 of 10 unanswerable ones abstained, including six near-topic ones. Ten unanswerable questions is a small sample.
- **Result.** Both questions now answer, but neither passes the correctness rule (see failure 3 and 4). The headline did not move. The lower gate is a real risk: a near-topic question with a misleading premise could now reach the model, and only the dev set and the evaluation's two unsupported questions (both abstained correctly) show it holds.

### Failure 2: a cross-paper question lost the tables it needed (q08)

- **What happened.** "Which tasks do ENGINE, StructZO and the Riemannian paper all report on OPT models, and which baseline do they share?" returned only "all three compare against MeZO and LOZO". The task names (SST-2, RTE, BoolQ, WiC, CB) appeared only in the evidence-gaps note, not in the answer. It cited paper-003 page 9 through a figure crop and never retrieved the results tables.
- **Cause.** Comparison questions search each paper separately and keep three pieces per paper. Three pieces were too few to include a results table next to the text that discusses it, and the figure crop on page 9 ranked above Table 2. This is a retrieval-depth and ranking problem, not a model problem.
- **Not fixed.** Raising the per-paper quota would be the first thing to try, and it was not tried, so as to avoid tuning on the evaluation set. Recorded as a known failure.

### Failure 3: the answer was incomplete (q15, q17)

- **q15** (figure on peak memory) correctly said LoRA and LongLoRA run out of memory at 32K, but left out that Jenga still runs, which the question implied. The key-fact rule needed "Jenga".
- **q17** (whole-collection synthesis) covered pooling, zeroth-order methods and KV-cache quantisation, but missed SMELL's sparsity technique. It cited SMELL's page 2, which is background text on LoRA, and mixed techniques the papers only mention as related work (GaLore, Adafactor) with techniques they contribute. Telling a paper's own method from background it describes is not something the system does; this is a real weakness for synthesis questions.

### Failure 4: the evaluation set itself was too strict or ambiguous (q01, q07, q09, q11)

These four are not system errors in my reading, but they count as failures under the rules, and the reading is the builder's, not an independent reviewer's.

- **q01 (AdamPM).** The answer says only the second moment is compressed, which is more precise than my expected answer ("first and second moments"). It failed because it never uses the word "pool" and cites pages 4 and 5, not page 1.
- **q07 (limitations).** The answer lists five real limitations from the paper's limitations section. It failed because the rule demanded the word "purity" or "irrelevant".
- **q09 (MeZO on OPT-13B RTE).** The Riemannian paper reports MeZO twice: 68.2 in its Table 1 (copied from another study) and 60.4 in its own controlled Table 3. The question did not say which. The system compared ENGINE's 59.0 with 60.4, which is a defensible answer; my label expected 68.2.
- **q11 (AdamPM vs StructZO).** The content is right. It failed citation_ok because it cited StructZO pages 7 and 8 instead of page 1.

**Reading the numbers.** Counting only genuine system failures (q08, q15, q17, with q08 the clearest), about 18 of 21 answers were substantively acceptable. That count is my judgement, so treat the rule-based 15 of 21 as the reported result and the rest as an informed caveat.

### A finding about retrieval, not a failure

At k=8, plain rank fusion (recall 0.785) scored below dense search alone (0.833) on this set. Fusion plus reranking was clearly best (0.943). With 19 questions this is a hint, not a conclusion.
