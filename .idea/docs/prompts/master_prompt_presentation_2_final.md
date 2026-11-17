# Master Presentation Prompt 2 of 2: Final Presentation (Checked Against the Code)

Run the evidence stage first (section 0a) in a tool that can run commands and a browser, then paste this prompt into your slide tool with the problem statement and the `evidence_ledger.md` it produced. It produces a concise, editable final deck in one fixed visual style, in which **every fact about the solution has been checked against the code and against output the agent actually ran**. Use Prompt 1 (the design review deck) before coding starts; use this prompt once the solution exists. The reference deck for this style is the FraudShield final presentation (Appendix C); it shows the style and the tone only, so never reuse its names, numbers, rules or outcomes for another problem. **Attach `deck_style.md` with this prompt** (Stage D): it holds Appendix A (the stylesheet) and Appendix B (the HTML patterns), shared with Prompt 1.

---

## 0. Inputs

| Input | Value |
|---|---|
| PROBLEM_STATEMENT | Attached document (read all of it, including tables, roles, rules and the technology appendix) |
| CODE_ROOT | Path to the finished repository. Read it and run it (section 7) |
| DESIGN_DECK | Optional: the design review deck made with Prompt 1, used to show what changed |
| TEAM and DATE | `[Team name]`, `[Date]` (leave bracketed placeholders if not given; never invent names) |
| STAGE | `FINAL`: the solution exists, so built, tested and measured claims are allowed **with evidence** |
| EVIDENCE_LEDGER | Path to `evidence_ledger.md` from the evidence stage (section 0a). Required when you cannot run commands or open a browser |
| BONUS_ITEMS | Optional: the bonus items that are `done` or `partial`, from the Bonus Round final report, each with its demo step. Adds up to two slides (section 3, point 1) |
| TOOL | The tool you are running in (see section 8) |

## 0a. Two-stage use (read first)

This prompt has two stages. They need different tools, so run them in different places.

- **Stage E, evidence.** Needs a shell and a browser (for example Claude Code). Do sections 7.1 to 7.7: inventory, run, compare, screenshots, ledger, worksheet. **Output:** `evidence_ledger.md` (the 7.6 table, the 7.3 traceability table, the 7.7 worksheet, the list of what was not run) and the screenshot files, saved next to the repository. Stop there. Do not build slides in this stage.
- **Stage D, deck.** Runs in the slide tool. Input: the problem statement, `EVIDENCE_LEDGER`, the screenshot files and, optionally, `DESIGN_DECK` and `BONUS_ITEMS`. **Do not run commands, open the app or read the repository in this stage.** Every claim, number and name on a slide must come from a ledger row. A ledger row counts as verified evidence for sections 3 and 7.
- **If you can do both** (one session with a shell, a browser and a slide tool), run Stage E first, write the ledger file, then continue to Stage D in the same session.
- **If you are in Stage D and no ledger was given, stop.** Say that the evidence stage has not been run and list what is needed. Never invent a result, a test count, a version or a screenshot. A claim with no ledger row is written as "not measured" or left out.

---

## 1. Role and goal

Act as a presentation designer, solution architect and independent auditor. Produce a deck of **at most 16 slides** (plus up to two optional bonus slides when `BONUS_ITEMS` is given, section 3 point 1) that covers the nine sections the panel expects at the final presentation (section 4a): intro, understanding the problem, proposed solution, system architecture, file architecture, tech stack, data flow (request to response), granular features, and scalability, security and future scope. It also carries the architecture decisions, a process flowchart of the core logic, the data model, the core intelligence and a results slide. The audience is a panel that mixes technical and non-technical members. The deck must be concise, crisp and tailored to this problem statement, in exactly the visual style defined in section 5.

## 2. Audience and tone

- Every slide must make sense to a non-technical reader from its **headline and first line alone**. Technical detail sits in a secondary line (the monospace "tech line") that a non-technical reader can skip and an engineer will value.
- Plain words. No jargon without a one-phrase explanation. Short sentences. Active voice.
- One idea per slide. A diagram or a table beats a paragraph.
- Never verbose: aim for at most about 45 words of body text per slide, not counting diagram labels. Slides 13 (features), 15 (results) and 16 (scale, security, future) may use up to about 70 words because they are tables and cards of short lines.
- **Say limits and misses in plain words.** An honest "missed, here is why" is stronger than a vague success.

## 3. Hard constraints

1. **At most 16 slides, or 18 when `BONUS_ITEMS` is given.** Use the blueprint in section 4. If the problem does not need a slide, merge it; do not add slides. The only allowed additions are the two optional bonus slides **14a** and **14b**, inserted after slide 14 and only for bonus items that are `done` or `partial` in the Bonus Round report: one item per slide (what it is, the setting that turns it on, the demo step, how it was verified, its status pill). A `cut` item gets no slide; list it on slide 15 under "not built". Without `BONUS_ITEMS`, the cap is 16. Never drop one of the nine required sections (section 4a) to save a slide; merge other content instead.
2. **Pictures: real screenshots only, on slide 4 only.** Up to three screenshots of the **running app**, captured in the evidence stage and listed in the ledger, showing synthetic data only (recipe 6.5). Everything else (diagrams, tables, charts, icons-as-shapes) is built from native, editable elements: text boxes, rectangles, rounded rectangles, arrows, connectors, tables. No photographs, stock images, clip-art, SVG or AI-generated pictures. If the app cannot be run, use labelled concept wireframes instead (built from shapes, as in Prompt 1) and say so.
3. **Evidence-based truthfulness (STAGE = FINAL).** Keep four states apart: **designed, built, tested, measured.** Say only what you verified in this session, and name how:
   - *Built*: you found the file, function or table in the repository (cite the path).
   - *Tested*: you ran the test command and saw the result (cite the command and the count).
   - *Measured*: the number comes from an output file or a command you ran or read now (cite the file or command).
   - A figure copied from a README, report or earlier chat that you did not re-run or re-read against the current outputs is **not measured**: either confirm it or label it "from `<file>` dated `<date>`, not re-run".
4. **Report misses plainly.** If a target is missed (for example a model reaches 1.8× of a required 2×), show target and result side by side with the verdict word "Missed" and the likely cause. Never tune on the test set, weaken the baseline or redefine a metric to look better.
5. **Label provenance.** If the data is synthetic or a substitute for an official pack, say so on every slide that shows a result. Never call results "official validation" unless they are.
6. **Everything traces to the statement or the code.** Every number, role, rule and technology named must come from the statement, from the repository or from output you ran. Never invent a statistic or a quote. Keep the Evidence Ledger (section 7.6); every number on a slide appears in it.
7. **List what you did not run or build** (for example a container build when no container daemon was available; features the statement asks for that are missing). They appear on slides 13 and 15 and in the hand-over.
8. **No secrets and no real personal data on slides.** Never show passwords, keys, tokens or connection strings, even demo ones. Screenshots show synthetic data only.
9. **Minimum text size 24 px** (12 pt) on the 1920×1080 canvas. If text does not fit, split the content, shorten it or merge slides. Never shrink text.
10. **Content must stay above y = 920 px** on every slide (the footer band owns y = 982 to 1016).
11. **Speaker notes on every slide:** 2 to 4 plain-English sentences, at most 70 words, that a non-expert presenter can read aloud, then one line starting `Evidence:` (at most 25 words) naming the files, commands or screenshots the slide rests on.
12. **Colour is never the only signal.** Every status colour carries a word: outcome pills with this problem's own outcome words (for example "Approve", "Ask the customer", "Block" in a payments case), status pills ("Done", "Partial", "Not built") and verdict pills ("Met", "Missed", "Not measured").
13. **Full coverage.** All nine required sections (section 4a) appear in the deck, each on the slide named there, in the order the panel expects: intro, problem, solution, architecture, files, tech stack, data flow, features, scale, security and future scope.

## 4. Slide blueprint (16 slides)

Fill each slide from the problem statement, the repository and the ledger (section 7).

| # | id | Purpose | Required content | Layout recipe |
|---|---|---|---|---|
| 1 | cover | Name and promise | Product name; one-sentence promise; section list; "Final presentation"; team/date footer | Dark gradient. Left: eyebrow, H1, lede, section list. Right: **concept graphic** (input, decision, outcomes) built from shapes (recipe 6.7) |
| 2 | problem | Problem and goal | Plain statement of today's pain; 3 to 4 measures from the statement's "success measures", Today → Target. Results go on slide 15, not here | Stat rows (recipe 6.2). Footnote defines any abbreviation |
| 3 | approach | Proposed solution | 3 principles **as implemented**, each with a tech line naming a real function, table or file you verified; the roles from the statement (one line each) | Left stack of 3 principle cards; right column of role cards |
| 4 | tour | Screens | One real screenshot per role (up to 3), each with a title, a one-line purpose and a tech line (the route or component file) | Three screenshot frames (recipe 6.5). Footer: "Screenshots of the running app, [date]; data is synthetic" |
| 5 | adr-a | ADR 1 to 4 | The decisions about how the core business decision is made, **as taken**. Status word per row: Implemented, Changed or Dropped | Row table (recipe 6.1) |
| 6 | adr-b | ADR 5 to 8 | Decisions about intelligence/AI, configuration, audit, integration, as taken, with the same status words | Row table (recipe 6.1) |
| 7 | hld | System architecture | Three layers **as built**: who talks to it; the service and its real modules; where it remembers. Name the credential for each caller type, as found in the code | Layered bands (recipe 6.3) |
| 8 | files | File architecture | The real folder tree of CODE_ROOT, top two levels, at most 14 lines; one purpose per folder; where the rules, the intelligence, the settings and the tests live; the test count | Tree card plus three "where is it?" cards (recipe 6.8) |
| 9 | stack | Tech stack | 5 to 6 layers: Layer, Technology **with the version read from the dependency files**, Why (one short line) | Row table, 3 columns (recipe 6.1) |
| 10 | lld-flow | Data flow: request to response | One real request followed from the entry point to the stored record and back: the steps of the real decision function (up to 6), what each can end with, and the request-in and response-out line with the real field names and status codes, confirmed by running one request | Pinned flow diagram plus request-to-response line (recipe 6.4) |
| 11 | flowchart | Process flowchart, as built | The core decision or workflow end to end **in flowchart notation**, drawn from the real code: Start, the input, 8 to 12 steps in 3 phases, up to 5 decisions (at most 2 per phase) with YES and NO branches, any loop back, End. Every step and decision must exist in the code (name the function in the notes). Do not repeat slide 10 (the request path) | Phase containers holding flowchart shapes (recipe 6.12) |
| 12 | lld-data | Data model | Entity chain with key fields, supporting tables and status lifecycles, all read from the real models and status values | Cards with arrows plus two lifecycle lines (recipe 6.6) |
| 13 | features | Granular features | Four to five areas (each role or module), each with up to three features and a status: Done, Partial or Not built. Status needs evidence (a passing test or a run this session). Footer: how many required items are Done | Feature status table (recipe 6.9) |
| 14 | core | The core intelligence, as built | The method, inputs, outputs and guardrails as implemented; **target versus result** from the evaluation output; misses stated plainly; data provenance | Left: 3-step chain plus second-opinion card plus decision bar; right: target-versus-result card plus guardrails |
| 15 | results | Results against targets | 4 to 5 rows: Measure, Target, Result, Verdict (Met, Missed, Not measured), each with its source file or command; test count; a line listing what was not run or not built | Results table (recipe 6.10) |
| 16 | plan | Scalability, security and future scope | Scalability: what the code does today and any measured speed; Security: the controls found in the code **and the honest gaps**; Future scope: Next and Later, taken from what is Not built and the statement's bonus ideas; one line of risks | Three cards plus a risks line (recipe 6.11) |

**Optional bonus slides 14a and 14b (only with `BONUS_ITEMS`):** eyebrow `BONUS · ADDED ON TOP OF THE CORE`; headline names the item in plain words; body is a row card (recipe 6.1 style, one row) with: item, setting and its default, demo step, how it was verified (ledger row), and a status pill (`Done` or `Partial`). Footer: "Core outputs are unchanged with the setting off" only if the Bonus Round report confirms it. Group two small items on one slide if that saves a slide.

**Adapting slide 14:** if the problem is an ML model, use the structure above. If it is a retrieval/LLM assistant, show retrieval, generation and guardrails with their measured quality. If it is rules plus workflow only, show the decision tables, how exceptions are handled and the reproduction of the statement's worked examples. Keep the same layout.

**ADR content:** reuse the eight decisions of the design review (DESIGN_DECK) if it exists, otherwise derive them from the statement's constraints and the code. Each row has an ID (ADR-1 to ADR-8), the decision with a tech line, why (one sentence), "instead of" (the rejected alternative) and a status word. When a decision changed or was dropped, say why in the speaker notes.

## 4a. Coverage checklist (the panel's nine sections)

The panel expects these nine sections at the final presentation, in this order. Each must be visibly present and backed by the code; check the table in step 5 of section 8 before handing over.

| # | Panel section | Slide(s) | What must be on it, and how it is checked |
|---|---|---|---|
| 1 | Intro | 1 cover | Product name, one-sentence promise, concept graphic |
| 2 | Understanding the problem | 2 problem (roles on 3) | Today's pain in numbers, who is affected, success measures as Today → Target, all from the statement |
| 3 | Proposed solution | 3 approach, 4 tour, 5 and 6 ADRs | Principles and decisions as implemented, real screenshots; each ADR carries a status word checked against the code |
| 4 | System architecture | 7 hld | Layers and modules as built; credential per caller type read from the security code |
| 5 | File architecture | 8 files | The real tree (from a directory listing), one purpose per folder, where rules, AI, settings and tests live |
| 6 | Tech stack | 9 stack | Technologies and versions read from the dependency files |
| 7 | Data flow (request to response) | 10 lld-flow and 11 flowchart, with 12 lld-data for what is stored | A real request traced through the code and confirmed by running it; real fields and status codes; the logic with its branches and loops, each present in the code |
| 8 | Granular features | 13 features (with 4 and 14) | Each feature marked Done, Partial or Not built with its evidence |
| 9 | Scalability, security and future scope | 16 plan (with 15 results for measured speed) | What the code does today, measured numbers, real controls, honest gaps, Next and Later, risks |

## 5. Design system (exact)

Canvas **1920 × 1080 px** (16:9). The complete stylesheet is in Appendix A; reproduce it exactly. Summary:

### 5.1 Palette (use only these)

| Token | Hex | Use |
|---|---|---|
| ink | `#14142B` | Text, dark slide base |
| blue | `#0F5FDC` | The single accent: eyebrow, numbers, tech lines, arrows, buttons |
| panel | `#E6EBF5` | Pale blue-grey panels and bands |
| soft | `#F5F7FB` | Card fill |
| line | `#D9DEEA` | 1 px borders |
| muted | `#5B5E73` | Secondary text |
| white | `#FFFFFF` | Slide background |
| cover gradient | `linear-gradient(135deg, #14142B, #1B2A6B)` | Cover only |
| on-dark accent | `#8DB4FF` | Eyebrow and arrows on the cover |
| on-dark text | `#D5DDF2` lede, `#AEB8D6` notes | Cover text |
| Positive outcome (green) | fill `#E3F3EA`, text `#1E6B43` | Outcome label only; the word is this problem's own (for example Approve) |
| Caution outcome (amber) | fill `#FFF1D6`, text `#7A4B00` | Outcome label only; the word is this problem's own (for example Ask the customer) |
| Negative outcome (red) | fill `#FBE3E1`, text `#8A1F17` | Outcome label only; the word is this problem's own (for example Block) |

Rules: one accent colour only; status colours appear only on small labels and bars, never as large fills; no gradients except the cover; no shadows; no decorative colour.

### 5.2 Fonts

- Text and headings: **Apple system font stack** `'SF Pro Display', 'SF Pro Text', -apple-system, 'Helvetica Neue', Arial, sans-serif` (SF Pro on Apple devices; Arial elsewhere).
- Technical lines: `'SF Mono', Menlo, 'Courier New', monospace`.
- Do not load web fonts. Do not mix other typefaces.

### 5.3 Type scale (px on the 1920 canvas; pt = px × 0.5)

| Role | px | pt | Weight | Notes |
|---|---|---|---|---|
| Cover title (H1) | 120 | 60 | 600 | letter-spacing −2 px, line height 1.02 |
| Slide headline (H2) | 60 | 30 | 400 | letter-spacing −1 px, line height 1.1; the **key phrase is bold** |
| Card or row title (H3) | 30 (28 in rows and nodes) | 15 (14) | 600 | |
| Lede | 28 (36 on cover) | 14 (18) | 400 | muted; cover lede `#D5DDF2` |
| Body in cards | 26 | 13 | 400 | line height 1.35, muted |
| Eyebrow, captions, footers, tech lines, labels | 24 | 12 | 600 for eyebrow and tags, else 400 | eyebrow letter-spacing 1.5 px |
| Row values (stat rows) | 40 | 20 | 600 | tracking −0.5 px |
| Big number | 96 | 48 | 600 | tracking −2 px |

### 5.3a Weights, tracking and case
Headlines are regular weight with one bold key phrase. Type eyebrows in UPPERCASE (do not rely on a case transform). Use weights 400 and 600 only for UI text.

### 5.4 Spacing, shape and rhythm

- Slide padding: top 112, sides 128, bottom 150. Default vertical gap 24 (20 on dense slides).
- Card: padding 26 × 28, radius 20, border 1 px `#D9DEEA`, fill `#F5F7FB`; panel variant fill `#E6EBF5`, no visible border.
- Row card: radius 18, padding 18 × 28. Layer box: radius 14. Flow node: radius 16. Pills: fully rounded.
- Footer: one 24 px line at bottom 56 px, left (what the slide is, or a truthfulness note); page number at the right.
- Headline pattern on every content slide: **eyebrow** (UPPERCASE, blue, with a 6 px blue left rule and 16 px padding), then **H2**, then content. The heading sits at the same height on every slide.
- White space is a feature: slides fill about 70% to 90% of the content area; never crowd.

### 5.5 Components

- **Eyebrow:** section label such as `ADR · ARCHITECTURE DECISION RECORDS · PROPOSED (1 OF 2)`, `HLD · SYSTEM ARCHITECTURE`, `LLD · DATA FLOW · REQUEST TO RESPONSE`, `LLD · DATA MODEL`, `FEATURES · GRANULAR FEATURES BY ROLE`, `THE PLAN · SCALE, SECURITY AND FUTURE SCOPE`.
- **Tech line:** monospace 24 px, blue, under a plain-language line (function names, tables, status values, mechanisms).
- **Pill:** 24 px, weight 600, padding 6 × 18; the word is mandatory.
- **Score bar:** a row of coloured segments with labels, widths in proportion.
- **Arrows:** block arrows or connectors in blue `#0F5FDC`; dashed grey `#8A8FA8` for "what a step can end with".


### 5.6 Additions for the final deck

- **More eyebrows:** `FILES · FILE ARCHITECTURE · AS BUILT`, `LLD · PROCESS FLOWCHART · AS BUILT`, `STACK · TECHNOLOGY · AS BUILT`, `FEATURES · WHAT IS DONE`, `THE CORE · AS BUILT`, `RESULTS · AGAINST TARGETS`.
- **Status pill** (features): `Done` (green), `Partial` (amber), `Not built` (red). **Verdict pill** (results): `Met` (green), `Missed` (red), `Not measured` (amber). Same pill style as outcome pills; the word is mandatory. Status colours stay on small labels, never large fills.
- **Screenshot frame:** 533 × 372 px, 1 px `#D9DEEA` border, radius 16, picture inside with `object-fit: cover`. No shadows, no device frames.

## 6. Layout recipes (numbers are exact)

### 6.1 Row table (ADR and stack slides)
A header row of 24 px labels (muted, weight 600), then 4 rows (6 on the stack slide). Each row is a row card.
- ADR columns: `120px 1.1fr 1.2fr 1fr`, gap 28: ID | Decision (H3 + tech line) | Why | Instead of.
- Stack columns: `0.7fr 1.2fr 1.3fr`, gap 28: Layer (blue, bold) | Technology (H3) | Why (one line, at most about 40 characters).
- Keep each cell to two lines. The slide gap is 20.

### 6.2 Stat rows (problem slide)
Columns `1.5fr 1fr 40px 1.3fr`, gap 24: Measure (H3) | Today (40 px, muted) | → (36 px, blue) | Target (40 px, blue). Four rows. A one-line lede above and a 24 px footnote below.

### 6.3 Layered bands (HLD slide)
Three bands separated by two link rows. Band 1 ("Who talks to it") and band 3 ("Where it remembers") use the pale panel; band 2 (the service) uses ink with a light-blue label. Each band holds 3 to 4 equal boxes (white, 1 px border, radius 14, padding 10 × 16, title 28 px, line 24 px). A link row is a 30 × 26 down arrow plus a 24 px caption: put the protocol and **the credential per caller type** here.

### 6.4 Pinned flow diagram (LLD flow slide)
A host box 1664 × 520 px. Six main nodes, 232 px wide, 220 px tall, at lefts 0, 286, 572, 858, 1144, 1430 and top 0. Six outcome nodes below at top 300, height 210, same lefts. Main nodes have the panel fill; outcome nodes are white with a border. Main connectors are solid blue, 3 px, from (left + 232, 110) to the next left, 110. Drop connectors are dashed grey, 2 px, from (left + 116, 220) to (left + 116, 300). Each main node: step number and name (28 px) and one 24 px line (at most 40 characters, so that it stays within three lines of a 232 px node even in Arial). Each outcome node: a pill carrying one of this problem's own outcome words (for example Reject, Block, Ask) and one line (at most 40 characters). **The headline of this slide must fit on one line (up to about 55 characters at 60 px; a 60-character headline fitted in the test).** Measured by rendering the recipe: with a one-line headline the diagram, the request line and the pills end at y = 894 (26 px below the y = 920 limit); with a two-line headline they end at y = 961, which breaks the limit by 41 px. Below the host: one request-to-response line (24 px, at most 110 characters, for example `Request in: <entry points, key fields>  →  one decision function  →  Response out: <fields>, 200 / 409 / 422`) plus the three outcome pills. The line names every entry point (API, screen form, batch file) so the panel sees they all share one pipeline. Total pinned elements must stay at or below 24, counting every node, connector and label (the full layout is 6 + 6 nodes and 5 + 6 connectors = 23).

### 6.5 Screenshot frames (screens slide)
Three frames, 533 × 372 px, gap 32, each holding one real screenshot of the running app: one role's main screen. Under each frame: H3 role, a 24 px muted line, a tech line (route or component file). Capture rules:
- Run the app from CODE_ROOT (section 7.2) and sign in as each role with the seeded demo accounts. Never show a password, token or key on screen.
- Synthetic data only. If anything looks like real personal data, do not use the screenshot.
- **Legibility maths (a full 1440 px page shrunk into a 533 px frame is about 0.37 scale, so 16 px interface text becomes about 6 px and cannot be read).** Capture with the browser window about 1000 px wide, **browser zoom at 125%** and a device pixel ratio of 2. Then **crop a region of at most 700 × 490 px** (ratio 1.43:1) around the single useful part of the screen (the open alert, the step-up question, the settings table), never the whole page. At 700 → 533 the scale is about 0.76. Work from the app's **smallest text that matters**: read its stylesheet (for the FraudShield app, table text is about 13.5 px and body text 15 px). At 125% zoom 13.5 px becomes about 17 px, and after the 0.76 scale about 13 px, which passes the 12 px test below. At 100% zoom it would be about 10 px and fail.
- **Capture in light mode.** The deck is light (white slides and a fixed light palette). Before capturing, set the operating system or the browser to light, or emulate `prefers-color-scheme: light` in the browser tools, and check that the page really is light. A screenshot of a dark theme on a white slide breaks the palette rule. If the app has no light theme, use that screenshot anyway only if it is legible, and say in the footer that the app theme is dark.
- **Legibility test, run on the finished slide:** the key labels and numbers that the slide's tech line or caption refers to must be at least 12 px high on the 1920 canvas, and the rest of the picture may be unreadable detail. If they are not, crop tighter. If one role's screen cannot be cropped to a single useful part, use a labelled concept wireframe for that role instead (as in Prompt 1) and say so in the footer.
- Give each picture a plain `alt` text describing the screen. Insert as a picture in editable tools; keep the crop editable.
- Footer: "Screenshots of the running app, [date]; data is synthetic." If a screenshot cannot be captured, use a labelled concept wireframe for that role and say which.

### 6.6 Data slide
A chain of entity cards joined by 36 × 28 block arrows (key field names in tech lines), supporting tables in a row of three panel cards, and one card holding two lifecycle lines in monospace (`STATE → STATE | STATE`). The footer states the cardinality in words.

### 6.7 Cover concept graphic
An 852 × 532 rounded panel (fill `#1F2F7A`, 1 px `#3A4A8C`, radius 24, padding 40) holding: a white step card, a down arrow, a blue step card, a down arrow, a row of the three outcome pills. It illustrates input → decision → outcomes for this problem.

### 6.8 File architecture slide (as built)
Two columns, gap 24. Left (flex 1.4): one soft card holding the folder tree in monospace (class `.tree`, 24 px, at most 14 lines, folder names in blue, a short grey comment of at most 30 characters after each, such as `backend/app/rules/   # hard stops, soft rules`). **Build the tree from a real directory listing** of CODE_ROOT (top two levels, skipping dependency, cache and build folders), and write each comment after reading what the folder holds, never from a guess. Right (flex 1): three stacked cards, each an H3 question and one 24 px line with a real path: "Where do the rules live?", "Where does the AI live?", "Where do the settings and tests live?". Put the test count in one of them ("N tests in M files", from the run in section 7.2). Footer: "As built. Source: directory listing of the repository, [date]."

### 6.9 Feature status table (granular features slide)
A row table like 6.1 with columns `0.8fr 1.5fr 1.4fr 150px`, gap 28: Area (blue, bold; a role or module) | Features (H3 plus a tech line naming the test or file that proves it; up to three features separated by ` · `) | What the user gets (at most two lines) | Status (a pill: `Done`, `Partial` or `Not built`; the word is mandatory). Four to five rows. If the lowest row ends below y = 920, drop to four rows and put the rest in the speaker notes. **Rules for the status:** Done only if a passing test or a run in this session shows it works; Partial if part of it works (name the missing part in the notes); Not built if no code exists for it. Cover every role from the statement and at least one back-office or system module. Footer: `N of M required requirements are Done; the rest are listed in the notes.` (counts from the traceability table, section 7.3).

### 6.10 Results table (results slide)
Columns `1.5fr 1fr 1fr 190px`, gap 24, each row a row card; a header row of 24 px muted labels: Measure (H3 plus a tech line with the source file or command) | Target (40 px, muted) | Result (40 px, blue) | Verdict (a pill: `Met`, `Missed` or `Not measured`). Four to five rows, always including the test result (`N passed of N run`) and the main quality or speed targets from the statement. A missed target is shown with its real number, never rounded up. Below the table, one 24 px line: `Not run or not built: <short list>.` Footer: the provenance label (for example "Synthetic data pack; not official validation").

### 6.11 Scale, security and future scope slide (as built)
Three equal cards in a row (gap 24) and a one-line risks note below.
- **Scalability** (H3, then three short lines of at most 8 words): what the code does today that helps it grow or stay correct (for example no local state in the service, one lock per entity); a measured speed or volume figure with its source, or "not measured"; the first scale-up step (labelled "proposed").
- **Security** (H3, then three or four short lines): who may do what (the roles and the credential for each caller type, as found in the code); what is never stored or shown; what is audited; and **one line of honest gaps** (for example "demo-grade: no TLS or rate limits") taken from the code, the README or the statement's caveats.
- **Future scope** (H3, two labelled blocks): a pill `Next` with one line, a pill `Later` with one line, taken from the Not built list and the statement's bonus ideas.
- Risks note (24 px, muted): `Risks to manage: <risk 1>; <risk 2>; <risk 3>.`

### 6.12 Process flowchart slide (as built)
A landscape flowchart in the classic notation, grouped into **phases** like the swim-bands of a process diagram. It shows the logic of the core process (decisions, branches, loops), not the request path of slide 10.

**Shape language (always with words, never colour alone):**
- **Start and End:** pill, ink fill, white 24 px text.
- **Input or output:** slanted box (a skewed painted box with a 2 px blue border and white fill; the label is a separate centred text box on top, because skewed text would lean).
- **Step:** rounded rectangle, panel fill `#E6EBF5`, 24 px text, at most 2 lines of about 15 characters (a 220 px box has 204 px of text width, which holds about 15 characters of 24 px text; measured: "Step-up or Approve" wraps to two lines).
- **Decision:** diamond (`x-shape`), white fill, 2 px blue border, 260 × 160 px, label (at most 2 lines of 14 characters, about 28 in all; at 13 px per character that is 182 px in a 200 px text box) in a separate centred text box on top. Every decision has two labelled exits, `YES` and `NO` (24 px, bold, blue), each a word, not just an arrow.
- **Arrows:** solid blue `#0F5FDC`, 3 px, with an arrowhead. A **loop back** is dashed grey `#8A8FA8`, 2 px, with a 24 px label ("repeat", "retry"). A branch that ends the process goes to an End pill or a step labelled with the outcome (Reject, Block, Ask).

**Composition:**
- A row of **three phase columns** (four only if each holds at most 3 shapes and is 368 px wide), each column holding a **phase host** and, below it, a 24 px bold centred label (`Phase name · module`). The phase host is a `position:relative` box, 512 px wide and 560 px tall, with a 2 px dashed `#8A8FA8` border, radius 20 and fill `#F5F7FB`. Its shapes are pinned inside it; keep each host at **24 pinned elements or fewer, counting every element you pin: each shape, each text box, each connector and each YES / NO label** (a diamond with its label counts as two, a slanted box with its label as two). If a phase is over 24, show the main path and move the minor branch to the speaker notes, or split the phase. Hosts are siblings in the flow, never nested, so each keeps its own count.
- Between the hosts: a blue `arrow-right` shape, 48 × 34 px, as a flow child (8 px gap each side) at mid-height of the host (`margin-top` about 260 px). The row spans 1664 px (three 512 px hosts plus two 64 px links).
- Put Start at the top of the first phase and End at the bottom of the last. Place the main path down the left of each host (centre x of about 150 px) and side exits to the right (boxes 160 px wide: 80 px tall holds two lines of about 10 characters, 104 px tall holds three; "Return original answer" needs 104 px). Two stacked diamonds leave only about 68 px at the bottom of a 560 px host, so the box under the second one holds one line of at most 15 characters (for example "Ask or approve").
- At most **12 steps and 5 decisions** on the slide, with at most 2 decisions in one phase. If the logic is bigger, show the main path and move the rest to the notes. (Checked by rendering the reference flowchart: 12 steps, 5 decisions, pinned elements 18, 17 and 12 per host, readable.)
- **Keep the headline to one line.** Measured: with a one-line headline the content ends at about y = 854; a two-line headline moves it to about 920, which leaves no slack.
- Footer key (24 px): "Pill = start or end · slanted box = data · box = step · diamond = decision. As built; every step and decision exists in the code."

**Final-stage rules:**
- Draw the flow from the **real code** (the decision function and the functions it calls), not from the design review. Each step and each decision diamond must match a real function or condition; name them in the speaker notes and in the `Evidence:` line.
- Exercise both branches of every decision where you can (a test or a real run) and cite it. A branch you could not exercise is stated in the notes.
- If the built logic differs from the design review's flowchart, show the built one and say what changed in the notes.
- No invented steps. If the code does something the diagram would need a step for, add the step; if a planned step does not exist, leave it out.

## 7. Evidence procedure (Stage E: do this before designing any slide)

The deck is only as honest as its evidence. **This section is Stage E (section 0a) and needs a shell and a browser.** In Stage D, skip 7.1 to 7.5 and read the ledger instead. Work through these steps, write `evidence_ledger.md`, then show the ledger (7.6) to the user in the chat before building.

### 7.1 Inventory the repository
List the tree (top two levels, skipping dependency, cache and build folders), the dependency files (for example `requirements.txt`, `package.json`, lock files), the container files, the README and any design or model documents. Count files and tests. Note every claim the README makes about results; treat each as a **claim to check**, not a fact.

### 7.2 Run it
- Probe the environment first: language versions, a database server, a container daemon, the Node toolchain. Record what is missing.
- Use a project-local database on a non-default port; never search for, guess or reuse credentials, and never touch another database.
- Start the app the way the README says. Seed it. Run the full test suite. Run the batch or evaluation commands the statement requires. Send one real request to the main endpoint and keep the request and response.
- Never run destructive commands, never modify the code to make a result look better, and never skip a failing test: a failure is a finding.
- If something cannot be run, say exactly what and why; its numbers become "not measured" or "from `<file>` dated `<date>`, not re-run".

### 7.3 Compare with the statement
Build the traceability table with the statement's own IDs: ID | requirement | Done / Partial / Not built | evidence (test name, file or run). Use it for the features slide and its footer count.

### 7.4 Compare with the design review (if DESIGN_DECK exists)
For each ADR: Implemented, Changed or Dropped, with the reason in one sentence. Note anything built that the design review did not promise, and flag it as an addition.

### 7.5 Capture the screenshots
Up to three, one per role, following recipe 6.5.

### 7.6 The Evidence Ledger
Show this table in the chat before building. Every number, name and claim on a slide must have a row.

| # | Claim for the slide | Evidence (file and line, command output, screenshot) | Run in this session? | Slide |
|---|---|---|---|---|
| | | | Yes / No (file dated …) | |

### 7.7 Extraction worksheet (from the statement)
Also fill this from the statement, and mark any row you could not fill as `[missing]` and ask about it (section 9). Never guess.

| Item | Source in statement | Value |
|---|---|---|
| Product name | Title or use case | |
| One-sentence promise | Objective | |
| Today's pain (3 to 4 numbers) | Business scenario | |
| Success measures (Measure, Today, Target) | Success-measures table | |
| Roles and what each can do | Users and roles | |
| Core decision or workflow and its rule stages | Business rules | |
| Outcomes (up to 3) | Outputs and decisions | |
| Status lifecycles | Lifecycle table | |
| Process stages, decisions and loops (for the flowchart) | Business rules, workflow, lifecycle | |
| Core intelligence and its success targets | AI/ML module | |
| Non-functional targets (speed, volume, availability, security, audit) | NFR section | |
| Suggested technologies | Technology appendix | |
| Deliverables, future scope and bonus ideas | Deliverables, out of scope | |
| Ambiguities and the assumption chosen | Anywhere | |

## 8. Build and quality procedure

1. Stage E: complete section 7 and write `evidence_ledger.md`. Stage D: read the ledger. In both, show the ledger and the worksheet to the user; if the user has not answered, proceed with the stated defaults and list them as assumptions (do not wait).
2. Write all slide text first; check the word budget (about 45 words of body text per slide) and the headline grammar (plain phrase, bold key phrase).
3. Build slides with the exact stylesheet (Appendix A) and recipes (section 6).
4. **Measure every slide:** the lowest content element must end at or above y = 920 on the 1920 × 1080 canvas; no text may overflow its box; no flex-shrunk arrows. Fix by trimming words, never by reducing font size.
5. Check the coverage checklist (section 4a) row by row: each of the nine panel sections sits on its named slide, in order, with the content listed. Then check the constraint list in section 3 one by one: at most 16 slides (18 with bonus slides), pictures only on slide 4 and only real screenshots that pass the legibility test in 6.5, no claim without a ledger row, text at least 24 px, notes with an `Evidence:` line on every slide, status colours always with words, no secrets or real personal data.
6. **Reconcile every number** on every slide against the ledger and the statement. Re-run or re-read anything you doubt.
7. Hand over with a short list of: what is a placeholder, what is an assumption, what was **not run**, what is **not built**, and which figures are "not re-run".

### Tool mapping

- **HTML slide tool (such as Claude's Slides artifact):** use Appendix A as the shared stylesheet and Appendix B snippets as patterns; canvas 1920 × 1080; elements: headings, paragraphs, lists, divs (flex or grid), `x-shape`, `x-connector`, `x-icon`, tables, and `img` for the screenshots only. Indent the file tree with non-breaking spaces, one paragraph per line.
- **PowerPoint or Keynote:** use the tool-neutral spec in `deck_style.md` (object mapping, column widths in px, the Arial width rule). Slide size 13.333 × 7.5 in. Convert px to pt by multiplying by 0.5 (1 px = 0.5 pt; 144 px per inch). Margins: top 0.78 in, sides 0.89 in, bottom 1.04 in. Use native shapes, connectors and tables; pictures only for the screenshots. Set fonts to SF Pro Display (headings and body) and SF Mono, with Arial and Courier New as fallbacks.
- **Google Slides:** same as PowerPoint; use Arial and Roboto Mono if SF Pro is unavailable and say so.

## 9. Questions to ask before building

Ask these (briefly, in one message) only if the answer is not already in the inputs:
1. Where is the repository (CODE_ROOT), and how is it started (the README command, ports, demo accounts)?
2. Can the app and the tests be run here (database, Node, Python, containers)? If not, which existing outputs may be used as evidence?
3. Which tool will this deck live in (so the right build path is used)?
4. Team name and date for the cover and footer?
5. Is there a design review deck (DESIGN_DECK) to compare against?
6. Does the evaluation rubric require any section not in the blueprint (for example cost or a demo plan)? If so, which slide should give way?

If the user does not answer, proceed with the defaults stated here and list them as assumptions.

---

## Appendix A and B: the stylesheet and the HTML patterns

These live in the shared file `deck_style.md` (attach it with this prompt). "Appendix A" is its stylesheet and "Appendix B" is its HTML patterns.

---

## Appendix C: Reference deck (FraudShield, final presentation)

Illustrates the structure and the tone, including how a miss is reported. **Example only: never copy a name, rule, number or outcome from it into a deck for a different problem.** **The numbers below were read from the project README when this prompt was written; every figure must be re-verified against the current code and outputs before it is used.**

1. **Cover:** "FraudShield. Real-time card fraud detection that protects customers without getting in their way." Final presentation; concept graphic: payment → decision → Approve / Ask the customer / Block.
2. **Problem:** "Fraud is found late. **Genuine customers pay for it.**" Stat rows from the statement: fraud loss 9 bps → 5 bps; false positives 25 : 1 → 10 : 1; time to analyst 6 h → 30 min / 4 h; decisions batch → under 300 ms and audited.
3. **Approach:** "Simple, explainable, **end to end first.**" Principles as implemented: rules decide and the model only tightens; ask before blocking; explain and record everything. Roles: cardholder, analyst, risk manager, gateway.
4. **Screens:** "Three roles, **three real screens.**" Screenshots of the cardholder, analyst and manager screens; footer: synthetic data.
5. **ADR 1 to 4:** "How payments are **decided.**" Each with a status word, for example "PostgreSQL with a lock per card: Implemented; a Redis counter store: not added".
6. **ADR 5 to 8:** "The AI, the settings and **the audit trail.**" Model with a 150 ms cap; XGBoost with SHAP and an Isolation Forest; settings in the database; audit locked by a database trigger.
7. **System architecture:** "One service, **three layers.**" React UI and gateway; FastAPI service; PostgreSQL. Credentials: bearer token for people, service key for the gateway.
8. **File architecture:** "One folder per job, **easy to find.**" `backend/app/` (rules, decision), `backend/ml/`, `backend/tests/`, `frontend/`, `scripts/`, `data/pack/`, `output/`; the real test count.
9. **Tech stack:** "Proven tools, **with their versions.**" Versions read from `requirements.txt` and `package.json`.
10. **Data flow:** "One payment in, **one decision out.**" The steps of `authorise()`; a real request and response with their fields and HTTP codes.
11. **Process flowchart, as built:** "The decision logic, **branch by branch.**" Three phases drawn from `authorise()`. *Validate:* Start → payment data → "Valid input?" (NO: reject, HTTP 422) → "Seen before?" (YES: return the original answer). *Decide:* "Hard stop or hard block?" (YES: Block) → soft rules → "Three or more flags?" (YES: Block; NO: Step-up or Approve). *Check and record:* "Model answers in 150 ms?" (NO: keep the rules decision) → tighten one step if the score is high → save decision and audit row → End. Each branch tied to a test or a run.12. **Data model:** "The data model **and lifecycles.**" Customers, cards, transactions, step-ups, alerts, audit log, rule settings; the real status values.
13. **Features:** "What is **done, and what is not.**" Done and tested: rules R1–R13, step-up, alerts, maker-checker, audit, dashboard. Not built: alert narrative by an LLM, live feed, rule editor with versions, what-if simulator, drift monitor. Footer: counts from the traceability table.
14. **Core intelligence:** "A second opinion that **can only tighten.**" Target 2× the baseline; result about 1.81× (PR-AUC 0.787 against 0.435), shown as **Missed**, with the cause (simulated labels) and the provenance label.
15. **Results:** "Results **against targets.**" Rows such as: sample file reproduced (900 of 900 cells: Met); tests (N passed of N run); model quality (Missed); container build (Not measured: no daemon). Line: not run or not built.
16. **Scale, security and future scope:** "Room to grow, **honest about gaps.**" Scalability: per-card lock and a measured batch time; Security: token and service-key credentials, salted hash and last four digits only, append-only audit, and the honest gap (demo-grade, no TLS or rate limits); Future: Next and Later from the Not built list; risks.
