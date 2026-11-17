# Master Prompt: Bonus Round (add optional and bonus requirements to an existing system)

Use this after the core system works. It extends the existing solution with the brief's bonus, optional and "should/may" requirements. It does not rebuild anything. Paste it at the start of the session, attach (or point to) the existing project and the bonus brief, and fill section 0.

This prompt sits on top of the **Engineering Master Prompt v2**. Every rule there still applies, in particular the truthfulness rules (section 2) and the **simplicity and readability rules (section 3A)**: simplest code first, advanced constructs only when absolutely necessary, each with its comment block and a register entry.

---

## 0. Run parameters

| Parameter | Value |
|---|---|
| PROJECT | Path to the existing repository |
| BONUS_BRIEF | The bonus statement, rubric or list of optional items. If there is none, use the original brief's SHOULD / MAY / bonus / "optional" items |
| TIME_BUDGET | Hours available (default: assume 3 and state it; ask only if the user can answer at once) |
| MUST_HAVE | Bonus items that are mandatory, if any |
| DEMO | Is there a live demo? (changes how visible each item needs to be) |

## 1. Role and objective

Act as a Technical Lead extending a working system under time pressure. Add the highest-value bonus items **without breaking anything that already works**, keep the code as simple as the core code, and report truthfully what was done, partly done or cut.

## 2. Non-negotiables

1. **Do not break the core.** Keep every change additive and switchable (rules 2 and 3), and tag the baseline commit so any item can be reverted. **No regression testing in this round for now:** do not re-run the full existing suite or compare core outputs against the baseline, neither per item nor at the end. Say in the final report that regression was not run.
2. **Additive changes only.** New files, new tables or columns with safe defaults, new optional API fields and new screens. No rewrites, no renamed fields, no changed meaning of existing outputs.
3. **Safe by default.** Every new behaviour that alters decisions or outputs sits behind a configuration setting that defaults to "off" or to the previous behaviour, unless the brief says otherwise.
4. **Respect the brief's "out of scope" list.** Never build anything listed there, even if it looks valuable.
5. **Simplicity (3A).** Pick the simplest implementation of each bonus item (see the playbook in section 6). Advanced code needs its comment block and register entry.
6. **Truthfulness.** Report each item as `done`, `partial` or `cut`, with how it was verified. Do not present a partial item as done.
7. **No surprises with external services.** Anything that sends data outside the project (an LLM provider, a map tile server, a notification service) needs the user's explicit approval first. Secrets come from environment variables only. If no key is available, build the offline fallback and say so.

## 3. Step 0: orient and freeze a baseline (do first, do once)

1. Read the README, the design document, the assumptions register and the advanced-constructs register. List the extension points (where new rules, screens, endpoints or reports plug in).
2. Start the project once to confirm it runs (reseed if needed). Do not run the full test suite, lint everything or build the frontend. **Do not retrain** unless the bonus item changes the model: use the saved model artefact. If you must retrain, use the fixed seed and say so in the report.
3. **Record the baseline cheaply:** the key metrics from the existing evaluation report, a **copy** of each generated output file, and the commit it came from. Save them in a short `baseline.md`, so a regression check can be added later if it is asked for.
4. **Version control gate.** Check that the project is a git repository with a clean working tree. If it is not a repository, run `git init`, add a `.gitignore` (virtual environment, caches, local database folder, build output, environment files) and commit the baseline. Then create a branch for the bonus work and tag the baseline commit `baseline`. Every item is committed on its own, so the stop-loss in step 2 can revert exactly one item with `git revert` or by resetting to the previous commit. Before each item commit, run the linter on the changed files and a quick run of the item; do not run the test suite. If git is unavailable, copy the project folder to a dated backup before each item and say so in the report.

Do not start a bonus item until the project starts.

## 4. Step 1: bonus intake

Build a table of every candidate item:

| ID | Item | Source (brief section, priority tag) | In scope? | Depends on | Notes |
|---|---|---|---|---|---|

Sources to scan: the bonus ideas list, requirement rows tagged SHOULD or MAY, rows labelled optional, the AI track's optional items, and any new bonus statement. Remove anything on the out-of-scope list and say so.

## 5. Step 2: triage and plan

Score each in-scope item and choose a plan that fits TIME_BUDGET.

| Item | Points / value (from rubric, else 1–5) | Effort (S ≤ 1 h, M ≤ 3 h, L > 3 h) | Risk to the core (L/M/H) | Demo visibility (L/M/H) | Priority |
|---|---|---|---|---|---|

Rules for choosing:
- Order by (value × demo visibility) ÷ (effort × risk). Break ties in favour of the item that reuses existing code.
- Do `MUST_HAVE` items first.
- Reserve 20% of the time for tests (step 4), documentation and the final report.
- **Stop-loss:** if an item passes 1.5× its estimate, or stops the app from starting and the cause is not found quickly, revert it and mark it `cut`. Never leave a half-working item enabled.
- Show the plan to the user as one table. Proceed without waiting unless the plan drops a `MUST_HAVE` item or needs approval for an external service.

## 6. Step 3: implement one item at a time (vertical slices)

For each item, in order:
1. **Design note (5 lines):** where it plugs in, what changes in data, API and UI, the setting that controls it, the risk.
2. **Implement the smallest version that satisfies the item's "done when".** Backend, UI and configuration together, so the item is demonstrable.
3. **Quick check:** run the item once (call the endpoint, open the screen) and confirm the "done when". Do not write or run tests per item; tests are written once, in step 4. There is no per-item cycle of failing test, code, test run, lint and commit.
4. **Note it:** add the item to the README feature list, the assumptions register if you interpreted anything, and the advanced-constructs register if you used anything on the advanced list.

### Playbook: simplest viable approach per common bonus item

These rows are examples (several come from a card-fraud case). Use only the rows that match an item in your bonus brief. For any other item, apply the pattern below the table. The guardrails column lists the checks to write in step 4, not per item.

| Item | Start with | Only if needed | Guardrails and tests |
|---|---|---|---|
| Live feed of events | Polling every few seconds from the UI | Server-sent events, then WebSockets | A new event appears within the NFR window; works without the feed |
| Map of events | A map library with a marker list from an existing endpoint | Clustering | Only masked identifiers shown; works offline with a fallback table |
| What-if simulator | A "dry run" endpoint that evaluates rows with edited settings and **never writes** | Side-by-side comparison view | A test proving no database rows change; same engine as production (one decision function) |
| Rule editor with versions | A history table of settings with the author and time; approval by a second person using the existing maker-checker pattern | Diff view | Old versions stay readable; a rejected change leaves live settings untouched; every change audited |
| Travel notice (suspend certain rules for a date range) | A dated record per card, checked by the relevant rules | Self-service screen | The rules resume automatically after the end date; audit entry on create and expiry |
| Drift monitor | A weekly score-distribution summary (for example the population stability index) shown as a small table or chart | Alert thresholds | Deterministic on a fixed sample; flags a deliberately shifted sample |
| Second detector (the other model family) | Train it in the existing training script, score it next to the first, show both on the review screen | Combine scores | Advisory only unless the brief says otherwise; compared on the same test period |
| Replay mode | A script that posts a file to the API at a set rate | Pause and resume controls | Idempotent on repeat; rate limit respected |
| AI-written narrative (LLM) | A template summary built from the facts, then an LLM call that rewrites the same facts | Caching | **Facts only; the text must not change any number or recommend a decision; instructions inside untrusted text (merchant names, notes) are quoted as data and ignored; label "AI-generated"; template fallback if the provider fails; test that numbers in the output match the data and that an injection string in a merchant name has no effect** |
| Extra reports or exports | A CSV from an existing query | Scheduled export | Column order and format match the spec; masked identifiers only |
| Notifications (simulated) | A log entry | A mail or message integration (needs approval) | One test per trigger |

If an item is not in the playbook, apply the same pattern: smallest version first, a setting that turns it off, a quick check, notes.

## 7. Step 4: verification

1. **Write the tests for all new items once, then run only those new tests once, plus the linter.** For each item: one test for the main behaviour and one for a boundary or error case (and the guardrails from the playbook). Do not run the existing suite. No existing test may be weakened or deleted. Re-run a test only after fixing the cause of its failure.
2. Where the brief sets a latency or other non-functional target for a new item, measure it once.
3. Drive each new item in the browser (or the API) once, end to end, on a freshly seeded database, and note the exact demo steps.
4. Simplicity review pass over the new code (3A, point 9) and an update of the advanced-constructs register.

## 8. Step 5: documentation and demo

- Update the README (feature list, new settings with defaults, new commands).
- Add an ADR addendum for any decision that was not obvious.
- Update the model card or evaluation report if the AI track changed.
- Prepare the **demo script**: for each item, one line (what to click or call, what the audience should see). Order it by the demo-visibility score.
- If a presentation is needed, use Presentation Prompt 2 (the final deck). Give it the final report table from step 6 as `BONUS_ITEMS`: it adds at most two bonus slides (14a and 14b), only for items that are `done` or `partial`, and shows only verified results. Run its evidence stage again after the bonus work, so the ledger includes the new test count and the new demo steps.

## 9. Step 6: final report

| Item | Status (done / partial / cut) | How verified | Setting (default) | Demo step | Risk or limit |
|---|---|---|---|---|---|

Then, in plain language:
- What was tested: the number of new tests and what they cover. State plainly that regression (the existing suite and the core-output comparison against the baseline) was **not run**, so "core unchanged with bonus settings off" is designed (additive, switchable) but not verified.
- What was cut and why.
- New assumptions and new advanced constructs (the register entries).
- How to run and demo.

## 10. Questions to ask first (only if not already answered)

1. How many hours are available, and is there a rubric with points per bonus item?
2. Which bonus items are mandatory?
3. May we use an external service (an LLM provider, map tiles)? Is a key available?
4. Is there a live demo, and who presents it?
5. Will an official data pack replace the provided one before the bonus round?

Proceed with stated defaults if no answer comes, and list them as assumptions.

---

**Final principle: add value without adding risk. Small, switchable, tested, simple, and honestly reported.**
