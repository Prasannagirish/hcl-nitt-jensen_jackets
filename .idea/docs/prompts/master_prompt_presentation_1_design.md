# Master Presentation Prompt 1 of 2: Design Review Deck (Before Coding)

Paste this prompt into your slide tool, then attach the hackathon problem statement. It produces a concise, editable design-review deck in one fixed visual style, tailored to the problem of the day. The reference deck for this style is the FraudShield design presentation (Appendix C); it shows the style and the tone only, so never reuse its names, numbers, rules or outcomes for another problem. **Attach `deck_style.md` with this prompt**: it holds Appendix A (the stylesheet) and Appendix B (the HTML patterns), shared with Prompt 2. Use this prompt **before any code exists**, to present how the solution will be designed and implemented. After the solution is built, use Prompt 2 (the final presentation), which is checked against the code.

---

## 0. Inputs

| Input | Value |
|---|---|
| PROBLEM_STATEMENT | Attached document (read all of it, including tables, roles, rules and the technology appendix) |
| TEAM and DATE | `[Team name]`, `[Date]` (leave bracketed placeholders if not given; never invent names) |
| STAGE | `DESIGN_REVIEW` (default): no code exists yet |
| TOOL | The tool you are running in (see section 8) |

## 1. Role and goal

Act as a presentation designer and solution architect. Produce a deck of **at most 14 slides** that covers the eight sections the panel expects at design review (section 4a): intro, understanding the problem, proposed solution, system architecture, tech stack, data flow (request to response), granular features, and scalability, security and future scope. It also carries the architecture decisions, the low-level design and a process flowchart of the core logic. File architecture is deliberately not part of this review: it is decided when coding starts and appears in the final presentation (Prompt 2). The audience is a panel that mixes technical and non-technical members. The deck must be concise, crisp and tailored to this problem statement, in exactly the visual style defined in section 5.

## 2. Audience and tone

- Every slide must make sense to a non-technical reader from its **headline and first line alone**. Technical detail sits in a secondary line (the monospace "tech line") that a non-technical reader can skip and an engineer will value.
- Plain words. No jargon without a one-phrase explanation. Short sentences. Active voice.
- One idea per slide. A diagram or a table beats a paragraph.
- Never verbose: aim for at most about 45 words of body text per slide, not counting diagram labels. Slides 12 (features) and 14 (scale, security, future) may use up to about 70 words because they are tables and cards of short lines.

## 3. Hard constraints

1. **At most 14 slides.** Use the blueprint in section 4. If the problem does not need a slide, merge it; do not add slides. Never drop one of the eight required sections (section 4a) to save a slide; merge other content instead.
2. **No images of any kind.** No photographs, no screenshots, no clip-art, no SVG, no AI-generated pictures. Every visual (diagrams, wireframes, charts, icons-as-shapes) is built from native, editable elements: text boxes, rectangles, rounded rectangles, arrows, connectors, tables. The user must be able to click and edit every element.
3. **Design-stage truthfulness (STAGE = DESIGN_REVIEW).** The solution does not exist yet. Never write "built", "tested", "working", "running", "passes", a measured result, a test count or a screenshot. Use "proposed", "planned", "target", "will". ADR status is "Proposed". Metrics appear only as **targets taken from the problem statement**. Wireframes are labelled "Concept wireframes, not final designs".
4. **Everything traces to the problem statement.** Every number, role, rule and technology named must come from the statement or be a clearly labelled proposal. Never invent a statistic or a quote. Scalability and speed numbers come only from the statement's non-functional section; if it gives none, write "target to be set" instead of a number.
5. **Minimum text size 24 px** (12 pt) on the 1920×1080 canvas. If text does not fit, split the content, shorten it or merge slides. Never shrink text.
6. **Content must stay above y = 920 px** on every slide (the footer band owns y = 982 to 1016).
7. **Speaker notes on every slide:** 2 to 4 plain-English sentences, at most 70 words, that a non-expert presenter can read aloud.
8. **Colour is never the only signal.** Every status colour (green, amber, red) carries a word taken from this problem's own outcomes (for example "Approve", "Ask the customer", "Block" in a payments case; use the statement's words in any other case).
9. **Full coverage.** All eight required sections (section 4a) appear in the deck, each on the slide named there, in the order the panel expects: intro, problem, solution, architecture, tech stack, data flow, features, scale, security and future scope. Do not show a folder tree or file names: that is for the final presentation.

## 4. Slide blueprint (14 slides)

Fill each slide from the problem statement using the extraction worksheet in section 7.

| # | id | Purpose | Required content | Layout recipe |
|---|---|---|---|---|
| 1 | cover | Name and promise | Product name; one-sentence promise; section list; team/date footer | Dark gradient. Left: eyebrow, H1, lede, section list. Right: **concept graphic** (the idea in three steps: input, decision, outcomes) built from shapes |
| 2 | problem | Problem and goal | Plain statement of today's pain; 3 to 4 measures from the statement's "success measures" with Today → Target | Stat rows (recipe 6.2). Footnote defines any abbreviation |
| 3 | approach | Approach and users | 3 principles (each with a tech line); the roles from the statement (one line each) | Left stack of 3 principle cards; right column of role cards |
| 4 | tour | Proposed screens | One low-fidelity wireframe per role (up to 3), each with a title, a one-line purpose and a tech line | Three wireframes (recipe 6.5). Footer: "Concept wireframes to show intent, not final designs" |
| 5 | adr-a | ADR 1 to 4 | Decisions about how the core business decision is made | Row table (recipe 6.1) |
| 6 | adr-b | ADR 5 to 8 | Decisions about intelligence/AI, configuration, audit, integration | Row table (recipe 6.1) |
| 7 | hld | System architecture (high-level design) | Three layers: who talks to it; the service and its modules; where it remembers. Name the credential for each caller type | Layered bands (recipe 6.3) |
| 8 | stack | Technology stack | 5 to 6 layers: Layer, Technology, Why (one short line). Prefer technologies from the statement's appendix; label each as proposed | Row table, 3 columns (recipe 6.1) |
| 9 | lld-flow | Data flow: request to response | One request followed from the caller to the stored record and back: the pipeline as a **flow diagram** of up to 6 steps, what each step can end with, and the request-in and response-out line (fields and status codes) | Pinned flow diagram plus request-to-response line (recipe 6.4) |
| 10 | flowchart | Process flowchart | The core decision or workflow end to end **in flowchart notation**: Start, the input, 8 to 12 steps grouped into 3 phases (the statement's stages), up to 5 decisions (at most 2 per phase) with YES and NO branches, any loop back, End. Do not repeat slide 9 (the request path): show the logic, its branches and its loops | Phase containers holding flowchart shapes (recipe 6.10) |
| 11 | lld-data | Low-level design: data | Entity chain with key fields; supporting tables; status lifecycles | Cards with arrows plus two lifecycle lines (recipe 6.6) |
| 12 | features | Granular features | Four to five areas (each role or module), each with up to three concrete features, what the user gets, and when it ships (Goal 1, Next or Later). Footer: the "done when" line for Goal 1 | Feature table (recipe 6.8) |
| 13 | core | The core intelligence | The use case's AI/ML or rules intelligence: inputs, method, outputs, how it changes decisions, success target (not results), guardrails | Left: 3-step chain plus second-opinion card plus decision bar; right: target card plus guardrails |
| 14 | plan | Scalability, security and future scope | Scalability (how it grows; targets only from the statement); Security (who may do what, what is never stored, what is audited); Future scope (Next, if time permits; Later, scale-up); one line of risks to manage | Three cards plus a risks line (recipe 6.9) |

**Adapting slide 13:** if the problem is an ML model, use the structure above. If it is a retrieval/LLM assistant, show retrieval, generation and guardrails. If it is rules plus workflow only, show the decision tables and how exceptions are handled. Keep the same layout.

**ADR content:** derive eight decisions from the statement's constraints. Each row has an ID (ADR-1 to ADR-8), the decision with a tech line, why (one sentence), and "instead of" (the rejected alternative). Typical candidates: where decisions are made (rules versus model); how doubtful cases are handled (ask, hold or reject); one engine for every entry point; the database and concurrency approach; how intelligence is integrated and what happens when it fails; where settings live; how history is protected; how external systems are simulated or integrated.

## 4a. Coverage checklist (the panel's eight sections)

The panel expects these eight sections at design review, in this order. Each must be visibly present; check the table in step 5 of section 8 before handing over. **File architecture is not a section of this deck.** It belongs to the final presentation, once the code exists.

| # | Panel section | Slide(s) | What must be on it |
|---|---|---|---|
| 1 | Intro | 1 cover | Product name, one-sentence promise, concept graphic (input, decision, outcomes) |
| 2 | Understanding the problem | 2 problem (roles on 3) | Today's pain in numbers, who is affected, success measures as Today → Target |
| 3 | Proposed solution | 3 approach, 4 tour, 5 and 6 ADRs | Principles, screens per role, eight decisions each with the rejected alternative |
| 4 | System architecture | 7 hld | Three layers, protocol and credential per caller type |
| 5 | Tech stack | 8 stack | Layer, technology, one-line reason; every item proposed |
| 6 | Data flow (request to response) | 9 lld-flow and 10 flowchart, with 11 lld-data for what is stored | Entry points, one engine, pipeline steps and their outcomes, the logic with its branches and loops, record written, response fields and status codes |
| 7 | Granular features | 12 features (with 4 and 13) | Features per role or module, what the user gets, Goal 1 / Next / Later, Goal 1 "done when" |
| 8 | Scalability, security and future scope | 14 plan | How it grows, controls and what is never stored, Next and Later, risks |

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

- **Eyebrow:** section label such as `ADR · ARCHITECTURE DECISION RECORDS · PROPOSED (1 OF 2)`, `HLD · SYSTEM ARCHITECTURE`, `LLD · DATA FLOW · REQUEST TO RESPONSE`, `LLD · PROCESS FLOWCHART`, `LLD · DATA MODEL`, `FEATURES · GRANULAR FEATURES BY ROLE`, `THE PLAN · SCALE, SECURITY AND FUTURE SCOPE`.
- **Tech line:** monospace 24 px, blue, under a plain-language line (function names, tables, status values, mechanisms).
- **Pill:** 24 px, weight 600, padding 6 × 18; the word is mandatory.
- **Score bar:** a row of coloured segments with labels, widths in proportion.
- **Arrows:** block arrows or connectors in blue `#0F5FDC`; dashed grey `#8A8FA8` for "what a step can end with".

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

### 6.5 Concept wireframes (screens slide)
Three frames, 533 × 372 px, gap 32, each: a pale title bar (role name, 24 px, bold), then simple blocks. Use grey rounded bars for placeholder lines, real 24 px labels only for key controls (for example the role's key question and its main action), blue buttons, one status panel. Under each frame: H3 title, a 24 px muted line, a tech line.

### 6.6 Data slide
A chain of entity cards joined by 36 × 28 block arrows (key field names in tech lines), supporting tables in a row of three panel cards, and one card holding two lifecycle lines in monospace (`STATE → STATE | STATE`). The footer states the cardinality in words.

### 6.7 Cover concept graphic
An 852 × 532 rounded panel (fill `#1F2F7A`, 1 px `#3A4A8C`, radius 24, padding 40) holding: a white step card, a down arrow, a blue step card, a down arrow, a row of the three outcome pills. It illustrates input → decision → outcomes for this problem.

### 6.8 Feature table (granular features slide)
A row table like 6.1 with columns `0.8fr 1.5fr 1.4fr 150px`, gap 28: Area (blue, bold; a role or module) | Features (H3 plus a tech line; up to three features separated by ` · `) | What the user gets (at most two lines) | When (a pill: `Goal 1`, `Next` or `Later`; the word is mandatory). Four to five rows. If the lowest row ends below y = 920, drop to four rows and put the rest in the speaker notes. Cover every role from the statement and at least one back-office or system module (rules, audit, settings, integration). Footer: `Goal 1 is done when: <one line>` with the demo-worthy baseline.

### 6.9 Scale, security and future scope slide
Three equal cards in a row (gap 24) and a one-line risks note below.
- **Scalability** (H3, then three short lines of at most 8 words): how it grows (for example a service with no local state, so more copies can run; one lock per entity keeps counts correct); the speed or volume targets taken from the statement, or "target to be set"; the first scale-up step. Everything is labelled "proposed".
- **Security** (H3, then three short lines): who may do what (roles; which credential each caller type uses); what is never stored or shown (for example full card numbers, model internals); what is recorded (an audit trail that cannot be edited). Add one line on responsible AI if the solution has an AI part (it may only tighten a decision; a person reviews high-impact ones).
- **Future scope** (H3, two labelled blocks): a pill `Next` with one line (if time permits), a pill `Later` with one line (scale-up and bonus ideas from the statement).
- Risks note (24 px, muted): `Risks to manage: <risk 1>; <risk 2>; <risk 3>.`

### 6.10 Process flowchart slide
A landscape flowchart in the classic notation, grouped into **phases** like the swim-bands of a process diagram. It shows the logic of the core process (decisions, branches, loops), not the request path of slide 9.

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
- Footer key (24 px): "Pill = start or end · slanted box = data · box = step · diamond = decision. Proposed flow."

## 7. Extraction worksheet (fill this first, then build)

Before designing any slide, produce this table from the problem statement and show it to the user in the chat.

| Item | Source in statement | Value |
|---|---|---|
| Product name | Title or use case | |
| One-sentence promise | Objective | |
| Today's pain (3 to 4 numbers) | Business scenario | |
| Success measures (Measure, Today, Target) | Success-measures table | |
| Roles and what each can do | Users and roles | |
| Core decision or workflow and its rule stages | Business rules | |
| Outcomes (up to 3) | Outputs and decisions | |
| Core data entities and key fields | Input data pack | |
| Status lifecycles | Lifecycle table | |
| Process stages, decisions and loops (for the flowchart) | Business rules, workflow, lifecycle | |
| Core intelligence and its success target | AI/ML module | |
| Non-functional targets (speed, volume, availability, audit) | NFR section | |
| Entry points and the request and response shape (key fields, status codes) | Input and output specification, API section | |
| Features per role or module, with priority (Goal 1, Next, Later) | Functional requirements, priority table | |
| Security requirements (roles, credentials, data never stored, audit) | NFR and security sections | |
| Scalability expectations (volume, growth, peak load) | NFR section; otherwise `[missing]`, never invented | |
| Suggested technologies | Technology appendix | |
| Deliverables, future scope and bonus ideas | Deliverables, out of scope | |
| Ambiguities and the assumption chosen | Anywhere | |

Mark any row you could not fill as `[missing]` and ask about it (section 9). Never guess.

## 8. Build and quality procedure

1. Fill the worksheet (section 7) and show it to the user. If the user has not answered, proceed with the stated defaults and list them as assumptions (do not wait).
2. Write all slide text first; check the word budget (about 45 words of body text per slide) and the headline grammar (plain phrase, bold key phrase).
3. Build slides with the exact stylesheet (Appendix A) and recipes (section 6).
4. **Measure every slide:** the lowest content element must end at or above y = 920 on the 1920 × 1080 canvas; no text may overflow its box; no flex-shrunk arrows. Fix by trimming words, never by reducing font size.
5. Check the coverage checklist (section 4a) row by row: each of the eight panel sections sits on its named slide, in order, with the content listed. Then check the constraint list in section 3 one by one: at most 14 slides, no images, no built/tested/measured claims, text at least 24 px, notes on every slide, status colours always with words.
6. Re-read every number against the problem statement.
7. Hand over with a short list of what is a placeholder and what is an assumption.

### Tool mapping

- **HTML slide tool (such as Claude's Slides artifact):** use Appendix A as the shared stylesheet and Appendix B snippets as patterns; canvas 1920 × 1080; elements: headings, paragraphs, lists, divs (flex or grid), `x-shape`, `x-connector`, `x-icon`, tables.
- **PowerPoint or Keynote:** use the tool-neutral spec in `deck_style.md` (object mapping, column widths in px, the Arial width rule). Slide size 13.333 × 7.5 in. Convert px to pt by multiplying by 0.5 (1 px = 0.5 pt; 144 px per inch). Margins: top 0.78 in, sides 0.89 in, bottom 1.04 in. Use native shapes, connectors and tables; no pictures. Set fonts to SF Pro Display (headings and body) and SF Mono, with Arial and Courier New as fallbacks.
- **Google Slides:** same as PowerPoint; use Arial and Roboto Mono if SF Pro is unavailable and say so.

## 9. Questions to ask before building

Ask these (briefly, in one message) only if the answer is not already in the inputs:
1. Which tool will this deck live in (so the right build path is used)?
2. Is this the design-review stage (no code), or a later stage where results may be shown?
3. Team name and date for the cover and footer?
4. Does the evaluation rubric require any section not in the blueprint (for example cost or a demo plan)? The eight panel sections in 4a, including tech stack, features, scalability and security, are already covered; file architecture is left for the final presentation. If a further section is needed, which slide should give way?
5. Which part of the solution is its core intelligence (ML model, retrieval/LLM, rules only), so slide 13 is tailored?
6. Any mandatory technology the panel expects to see?

If the user does not answer, proceed with the defaults stated here and list them as assumptions.

## 10. Hand-off to coding (after the deck)

The deck shows the idea. The panel and the team also need the exact plan for building it. After the deck, give the user one **implementation brief** in the chat, in plain text, so coding can start without re-deciding anything:

1. **Build order:** milestones in the order they will be built, each with a "done when" line (Goal 1 first).
2. **Decision function:** its inputs, its outputs, the ordered pipeline steps and the decisions and loops, as on the data-flow and flowchart slides.
3. **Data model:** every table with its key fields and status values, as on the data slide.
4. **Interfaces:** the endpoints or entry points, who may call each one, and the request and response fields.
5. **Configuration:** every threshold, window, list and setting that must live in data, not code.
6. **Acceptance tests:** the statement's worked examples and sample files, each mapped to the check that will prove it.
7. **Assumptions and risks:** every interpretation of an ambiguous requirement, and the main risks with a mitigation.
8. **Left open on purpose:** the folder layout and library versions, decided at the start of coding and shown in the final presentation (Prompt 2).

Everything in the brief is labelled proposed; nothing is claimed as built or tested.

---

## Appendix A and B: the stylesheet and the HTML patterns

These live in the shared file `deck_style.md` (attach it with this prompt). "Appendix A" is its stylesheet and "Appendix B" is its HTML patterns.

---

## Appendix C: Reference deck (FraudShield, card fraud detection)

1. **Cover:** "FraudShield. Real-time card fraud detection that protects customers without getting in their way." Concept graphic: payment → decision → Approve / Ask the customer / Block.
2. **Problem:** "Fraud is found late. **Genuine customers pay for it.**" Stat rows: fraud loss 9 bps → 5 bps; false positives 25 : 1 → 10 : 1; time to analyst 6 h → 30 min / 4 h; decisions batch → under 300 ms and audited.
3. **Approach:** "Simple, explainable, **end to end first.**" Principles: rules decide and AI advises; ask before blocking; explain and record everything. Four roles.
4. **Proposed screens:** "Three roles, **three screens.**" Wireframes: cardholder, analyst, manager.
5. **ADR 1 to 4:** "How payments are **decided.**" Rules decide and AI only tightens; ask the customer before declining; one decision engine for every entry point; PostgreSQL with a lock per card.
6. **ADR 5 to 8:** "The AI, the settings and **the audit trail.**" Model in the service with a 150 ms cap; XGBoost with SHAP and an Isolation Forest; settings in the database; audit locked by the database.
7. **System architecture (HLD):** "One service, **three layers.**" Clients; service; storage. Credentials: apps use a bearer token, the gateway uses a service API key.
8. **Technology stack:** "Proven tools, **chosen for a reason.**" Frontend, API, data, AI/ML, security, delivery.
9. **Data flow, request to response (LLD):** "One payment in, **one decision out.**" Validate, features, hard stops, hard blocks, soft rules, AI check; each with what it can end with. Line: gateway, screen or batch file in → one decision function → decision, reasons and status codes out.
10. **Process flowchart (LLD):** "The decision logic, **branch by branch.**" Three phases. *Validate:* Start → payment data → "Valid input?" (NO: reject, HTTP 422) → "Seen before?" (YES: return the original answer). *Decide:* "Hard stop or hard block?" (YES: Block) → soft rules → "Three or more flags?" (YES: Block; NO: Step-up or Approve). *Check and record:* "Model answers in 150 ms?" (NO: keep the rules decision) → tighten one step if the score is high → save decision and audit row → End.11. **LLD data:** "The data model **and lifecycles.**" Customer, card, transaction, step-up, alert; audit log, rule config, reference tables; status lifecycles.
12. **Granular features:** "Every role gets **a clear job.**" Rows: cardholder (confirm or deny), analyst (queue, claim, close), manager (settings, reports), decision engine (rules, explanations), integration (gateway, batch replay); each with Goal 1, Next or Later. Footer: Goal 1 is done when a payment is decided end to end and recorded.
13. **Core intelligence:** "A second opinion that **can only tighten.**" Signals, model, decision; second detector; score bar; target 2× the baseline (target, not result); guardrails.
14. **Scale, security and future scope:** "Room to grow, **safe by design.**" Scalability: no local state in the service, one lock per card, decision-time target from the statement. Security: roles and credentials per caller, no full card numbers stored, audit trail that cannot be edited. Future scope: Next and Later; risks to manage.
