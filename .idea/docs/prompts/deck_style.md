# Deck style file (shared by Presentation Prompt 1 and Presentation Prompt 2)

Attach this file together with either presentation prompt. In those prompts, **"Appendix A"** means the stylesheet below and **"Appendix B"** means the HTML patterns below. There is one copy, so the design-review deck and the final deck cannot drift apart. If you edit the style, edit it here only.

If this file is not attached, ask for it before building. Do not rewrite the style from memory.

## Tool-neutral spec (use when the tool is not the Claude Slides HTML artifact)

The HTML elements `x-shape`, `x-connector` and `x-icon`, and the CSS grid recipes, work only in the Claude Slides artifact. In PowerPoint, Keynote or Google Slides, build the same layout from native objects:

| Recipe element | Native object |
|---|---|
| Card, row card, layer box, flow node | Rounded rectangle, 1 px border `#D9DEEA`, fill as in the CSS |
| Pill | Rounded rectangle with the largest corner radius; the word inside is mandatory |
| `x-shape kind="diamond"` | Diamond shape, 260 × 160 px, 2 px blue border; label in a separate text box on top |
| `x-shape kind="arrow-right"` or `"arrow-down"` | Block arrow shape in `#0F5FDC` |
| `x-connector` | Straight arrow connector, 3 px blue; dashed grey 2 px for loop-backs and "what a step can end with" |
| Slanted data box | Parallelogram shape, 2 px blue border, white fill; label in a separate text box |
| Phase host | Rounded rectangle, 2 px dashed `#8A8FA8` border, fill `#F5F7FB`, no text |
| Grid row (`grid3`, `grid4`, `gridf`, `gridr`, `gridv`) | Native table, one row per card, column widths from the table below |
| Screenshot frame | Picture cropped to 533 × 372 px with a 1 px border |

Units: the canvas is 1920 × 1080 px. In PowerPoint and Keynote the slide is 13.333 × 7.5 in, so **1 px = 0.5 pt**. Content width is 1664 px (1920 minus 128 on each side).

**Column widths for the grid recipes** (px, computed from the CSS for a row card with 28 px side padding and the stated gaps; accurate to about 1 px):

| Recipe | Columns, left to right |
|---|---|
| `grid4` (ADR) | 120 · 468 · 511 · 425 |
| `grid3` (stack) | 340 · 582 · 631 |
| `gridf` (features) | 297 · 557 · 520 · 150 |
| `gridr` (results) | 577 · 385 · 385 · 190 |
| `gridv` (problem stats) | 590 · 394 · 40 · 512 |

**Fonts.** SF Pro exists only on Apple devices. When it is not available, use Arial (PowerPoint, Google Slides) and Courier New or Roboto Mono for tech lines. **Plan every text box with Arial widths**: about **13 px per character at 24 px** and about 15 px per character at 28 px. The fixed boxes in the recipes (flow nodes 232 px wide, diamonds 260 px wide, 533 px frames) were sized with this rule. Say in the hand-over which font was used.

---

## Appendix A: Complete stylesheet (use exactly)

```css
/* FraudShield design deck. Apple system fonts, one blue accent, pale blue-grey panels. */
:root {
  --ink: #14142B;
  --blue: #0F5FDC;
  --panel: #E6EBF5;
  --soft: #F5F7FB;
  --line: #D9DEEA;
  --muted: #5B5E73;
}

/* Reset: the recipes' heights assume no default browser margins. */
h1, h2, h3, p, ul { margin: 0; }

body { font-family: 'SF Pro Display', 'SF Pro Text', -apple-system, 'Helvetica Neue', Arial, sans-serif; color: #14142B; }

section {
  background: #FFFFFF;
  color: #14142B;
  font-family: 'SF Pro Display', 'SF Pro Text', -apple-system, 'Helvetica Neue', Arial, sans-serif;
  padding: 112px 128px 150px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  counter-increment: page;
}
section.dark { background: linear-gradient(135deg, #14142B, #1B2A6B); color: #FFFFFF; }

h1 { font-size: 120px; font-weight: 600; line-height: 1.02; letter-spacing: -2px; }
h2 { font-size: 60px; font-weight: 400; line-height: 1.1; letter-spacing: -1px; }
h3 { font-size: 30px; font-weight: 600; line-height: 1.15; }

.eyebrow { font-size: 24px; font-weight: 600; letter-spacing: 1.5px; line-height: 1.1; color: #0F5FDC; border-left: 6px solid #0F5FDC; padding-left: 16px; }
.dark .eyebrow { color: #8DB4FF; border-left: 6px solid #8DB4FF; }
.lede { font-size: 28px; line-height: 1.4; color: #5B5E73; }
.dark .lede { font-size: 36px; line-height: 1.3; color: #D5DDF2; }
.note { font-size: 24px; line-height: 1.35; color: #5B5E73; }
.dark .note { color: #AEB8D6; }
.mono { font-family: 'SF Mono', Menlo, 'Courier New', monospace; font-size: 24px; line-height: 1.3; color: #0F5FDC; }

/* Footer band */
.foot, .pg { position: absolute; bottom: 56px; font-size: 24px; color: #5B5E73; }
.dark .foot, .dark .pg { color: #AEB8D6; }
.foot { left: 128px; width: 1200px; }
.pg { left: 1664px; width: 128px; text-align: right; }
.pg::before { content: counter(page); }

/* Layout helpers */
.row { display: flex; gap: 24px; }
.col { display: flex; flex-direction: column; gap: 16px; }
.stack { display: flex; flex-direction: column; gap: 14px; }
.coverrow { display: flex; gap: 48px; align-items: center; flex: 1; }
.coverleft { display: flex; flex-direction: column; gap: 28px; width: 764px; }

/* Cards */
.card { background: #F5F7FB; border: 1px solid #D9DEEA; border-radius: 20px; padding: 26px 28px; display: flex; flex-direction: column; gap: 10px; flex: 1; }
.card.panel { background: #E6EBF5; border-color: #E6EBF5; }
.card h3 { font-size: 30px; }
.card p { font-size: 26px; line-height: 1.35; color: #5B5E73; }
.card .mono { font-size: 24px; color: #0F5FDC; }
.card .sub { font-size: 24px; line-height: 1.3; color: #5B5E73; }
.card .tag { font-size: 24px; font-weight: 600; color: #0F5FDC; }
.card .big { font-size: 96px; font-weight: 600; line-height: 1; letter-spacing: -2px; color: #14142B; }
.card ul { font-size: 26px; line-height: 1.3; color: #5B5E73; display: flex; flex-direction: column; gap: 8px; }

/* Outcome pills: always carry a word, never colour alone */
.pill { align-self: flex-start; font-size: 24px; font-weight: 600; padding: 6px 18px; border-radius: 999px; }
.pill.ok, .card .pill.ok { background: #E3F3EA; color: #1E6B43; }
.pill.ask, .card .pill.ask { background: #FFF1D6; color: #7A4B00; }
.pill.stop, .card .pill.stop { background: #FBE3E1; color: #8A1F17; }
.pill.info, .card .pill.info { background: #E6EBF5; color: #14142B; }
.card .pill { font-size: 24px; }

/* Row tables made of grids */
.grid4 { display: grid; grid-template-columns: 120px 1.1fr 1.2fr 1fr; gap: 28px; align-items: center; }
.grid3 { display: grid; grid-template-columns: 0.7fr 1.2fr 1.3fr; gap: 28px; align-items: center; }
.gridv { display: grid; grid-template-columns: 1.5fr 1fr 40px 1.3fr; gap: 24px; align-items: center; }
.gridf { display: grid; grid-template-columns: 0.8fr 1.5fr 1.4fr 150px; gap: 28px; align-items: center; }
.head { padding: 0 28px; }
.head p { font-size: 24px; font-weight: 600; color: #5B5E73; }
.rowcard { background: #F5F7FB; border: 1px solid #D9DEEA; border-radius: 18px; padding: 18px 28px; }
.rowcard h3 { font-size: 28px; }
.rowcard p { font-size: 26px; line-height: 1.3; color: #5B5E73; }
.rowcard .id { font-size: 26px; font-weight: 600; color: #0F5FDC; }
.rowcard .mono { font-size: 24px; color: #0F5FDC; }
.rowcard .val { font-size: 40px; font-weight: 600; line-height: 1.1; letter-spacing: -0.5px; color: #5B5E73; }
.rowcard .goal { font-size: 40px; font-weight: 600; line-height: 1.1; letter-spacing: -0.5px; color: #0F5FDC; }
.rowcard .arrow { font-size: 36px; color: #0F5FDC; text-align: center; }
.rowcard .pill { font-size: 24px; }
.rowcard .pill.info { background: #E6EBF5; color: #14142B; }

/* File tree (file architecture slide) */
.tree p { font-family: 'SF Mono', Menlo, 'Courier New', monospace; font-size: 24px; line-height: 1.3; color: #14142B; }
.tree .f { color: #0F5FDC; font-weight: 600; }
.tree .c { color: #5B5E73; }

/* Layered system diagram */
.band { background: #E6EBF5; border-radius: 20px; padding: 12px 20px; display: flex; flex-direction: column; gap: 8px; }
.band.ink { background: #14142B; }
.band .lbl { font-size: 24px; font-weight: 600; color: #0F5FDC; }
.band.ink .lbl { color: #8DB4FF; }
.box { background: #FFFFFF; border: 1px solid #D9DEEA; border-radius: 14px; padding: 10px 16px; flex: 1; display: flex; flex-direction: column; gap: 2px; }
.box h3 { font-size: 28px; }
.box p { font-size: 24px; line-height: 1.25; color: #5B5E73; }
.box .mono { font-size: 24px; color: #0F5FDC; }
.link { display: flex; align-items: center; justify-content: center; gap: 16px; }
.link p { font-size: 24px; color: #5B5E73; }

/* Pinned flow diagram (LLD) */
.node { position: absolute; box-sizing: border-box; width: 232px; border-radius: 16px; padding: 14px 16px; display: flex; flex-direction: column; gap: 6px; }
.node.main { height: 180px; background: #E6EBF5; border: 1px solid #E6EBF5; }
.node.drop { height: 170px; background: #FFFFFF; border: 1px solid #D9DEEA; }
.node h3 { font-size: 28px; }
.node p { font-size: 24px; line-height: 1.25; color: #5B5E73; }
.node .step { font-size: 24px; font-weight: 600; color: #0F5FDC; }

/* Process flowchart (shapes are pinned inside a phase host) */
.phase { position: relative; box-sizing: border-box; border: 2px dashed #8A8FA8; border-radius: 20px; background: #F5F7FB; }
.fterm { position: absolute; box-sizing: border-box; width: 160px; height: 56px; border-radius: 999px; background: #14142B; display: flex; align-items: center; justify-content: center; }
.fterm p { font-size: 24px; font-weight: 600; color: #FFFFFF; }
.fnode { position: absolute; box-sizing: border-box; border-radius: 12px; background: #E6EBF5; display: flex; align-items: center; justify-content: center; padding: 8px; }
.fnode p { font-size: 24px; line-height: 1.2; text-align: center; color: #14142B; }
.fdata { position: absolute; box-sizing: border-box; width: 220px; height: 72px; background: #FFFFFF; border: 2px solid #0F5FDC; transform: skewX(-14deg); }
.fdia { position: absolute; width: 260px; height: 160px; background: #FFFFFF; border: 2px solid #0F5FDC; }
.ftext { position: absolute; font-size: 24px; line-height: 1.2; text-align: center; color: #14142B; }
.flab { position: absolute; font-size: 24px; font-weight: 600; color: #0F5FDC; }
.plabel { font-size: 24px; font-weight: 600; text-align: center; color: #14142B; }

/* Score bar */
.bar { display: flex; gap: 6px; }
.seg { padding: 14px 18px; font-size: 24px; font-weight: 600; border-radius: 12px; }
.seg.ok { background: #E3F3EA; color: #1E6B43; }
.seg.ask { background: #FFF1D6; color: #7A4B00; }
.seg.stop { background: #FBE3E1; color: #8A1F17; }

/* Cover concept graphic */
.hero { width: 852px; height: 532px; box-sizing: border-box; border-radius: 24px; background: #1F2F7A; border: 1px solid #3A4A8C; padding: 40px; display: flex; flex-direction: column; justify-content: center; gap: 16px; }
.hstep { background: #FFFFFF; border-radius: 18px; padding: 22px 28px; display: flex; flex-direction: column; gap: 4px; }
.hstep.blue { background: #0F5FDC; }
.hstep h3 { font-size: 32px; color: #14142B; }
.hstep.blue h3 { color: #FFFFFF; }
.hstep p { font-size: 24px; line-height: 1.3; color: #5B5E73; }
.hstep.blue p { color: #DCE7FF; }

/* Concept wireframes (low fidelity, made of native shapes) */
.wf { width: 533px; height: 372px; box-sizing: border-box; border: 1px solid #D9DEEA; border-radius: 16px; background: #FFFFFF; overflow: hidden; display: flex; flex-direction: column; }
.wbar { background: #E6EBF5; padding: 8px 16px; font-size: 24px; font-weight: 600; color: #14142B; }
.wbody { padding: 16px; display: flex; flex-direction: column; gap: 12px; flex: 1; }
.wpanel { background: #F5F7FB; border: 1px solid #D9DEEA; border-radius: 12px; padding: 14px; display: flex; flex-direction: column; gap: 10px; }
.wpanel.ask { background: #FFF1D6; border: 1px solid #FFF1D6; }
.wt { font-size: 26px; font-weight: 600; color: #14142B; }
.wl { height: 14px; border-radius: 7px; background: #D9DEEA; }
.wpanel.ask .wl { background: #F1D99A; }
.wfield { font-size: 24px; color: #5B5E73; border: 1px solid #BFC6D8; background: #FFFFFF; border-radius: 10px; padding: 8px 14px; }
.wbtn { font-size: 24px; font-weight: 600; color: #FFFFFF; background: #0F5FDC; border-radius: 10px; padding: 8px 14px; }
.wbtn.ghost { background: #FFFFFF; color: #8A1F17; border: 1px solid #8A1F17; }
.wtag { font-size: 24px; font-weight: 600; padding: 2px 12px; border-radius: 999px; }
.wtag.stop { background: #FBE3E1; color: #8A1F17; }
.wtag.ask { background: #FFF1D6; color: #7A4B00; }
.wrow { display: flex; align-items: center; gap: 10px; }
.wtile { flex: 1; background: #F5F7FB; border: 1px solid #D9DEEA; border-radius: 12px; padding: 10px 12px; display: flex; flex-direction: column; gap: 8px; }
.wk { font-size: 24px; color: #5B5E73; }

/* Results table (final deck) */
.gridr { display: grid; grid-template-columns: 1.5fr 1fr 1fr 190px; gap: 24px; align-items: center; }

/* Screenshot frame (final deck, real screenshots only) */
.shot { width: 533px; height: 372px; box-sizing: border-box; border: 1px solid #D9DEEA; border-radius: 16px; overflow: hidden; background: #FFFFFF; }
.shot img { width: 533px; height: 372px; object-fit: cover; }
```

## Appendix B: HTML patterns

Content slide frame (every content slide):

```html
<section id="SLIDE_ID">
<p class="eyebrow">SECTION · LABEL</p>
<h2>Plain phrase, <b>bold key phrase.</b></h2>
<!-- body -->
<p class="foot">Footer text</p><p class="pg"></p>
<aside>Two to four plain-English sentences for the presenter.</aside>
</section>
```

Row table row:

```html
<div class="rowcard grid4"><p class="id">ADR-1</p>
<div class="col" style="gap:4px"><h3>Decision in plain words</h3><p class="mono">technical mechanism</p></div>
<p>Why, in one sentence.</p><p>The rejected alternative.</p></div>
```

Process flowchart (one phase host; shapes are pinned, so the host needs a size):

```html
<div class="col" style="width:512px; gap:12px">
<div class="phase" style="width:512px; height:560px">
<div class="fterm" style="left:70px; top:24px"><p>Start</p></div>
<x-connector x1="150" y1="80" x2="150" y2="108" style="color:#0F5FDC; border-width:3px"></x-connector>
<div class="fdata" style="left:40px; top:108px"></div>
<p class="ftext" style="left:40px; top:130px; width:220px">Payment data</p>
<x-connector x1="150" y1="180" x2="150" y2="208" style="color:#0F5FDC; border-width:3px"></x-connector>
<x-shape kind="diamond" class="fdia" style="left:20px; top:208px"></x-shape>
<p class="ftext" style="left:50px; top:273px; width:200px">Valid input?</p>
<x-connector x1="150" y1="368" x2="150" y2="408" style="color:#0F5FDC; border-width:3px"></x-connector>
<p class="flab" style="left:160px; top:372px">YES</p>
<div class="fnode" style="left:40px; top:408px; width:220px; height:80px"><p>Compute features</p></div>
<x-connector x1="280" y1="288" x2="330" y2="288" style="color:#0F5FDC; border-width:3px"></x-connector>
<p class="flab" style="left:284px; top:252px">NO</p>
<div class="fnode" style="left:330px; top:248px; width:160px; height:80px"><p>Reject: HTTP 422</p></div>
</div>
<p class="plabel">1 Validate · validation module</p>
</div>
```

Stat row:

```html
<div class="rowcard gridv"><h3>Measure</h3><p class="val">Today value</p><p class="arrow">→</p><p class="goal">Target value</p></div>
```

Flow nodes and connectors (inside a `position:relative` host, 1664 × 520):

```html
<div class="node main" style="left:0px; top:0px; height:220px"><h3>1 Step name</h3><p>One short line</p></div>
<div class="node drop" style="left:0px; top:300px; height:210px"><p class="pill stop">Reject</p><p>What this step can end with</p></div>
<x-connector x1="232" y1="110" x2="286" y2="110" style="color:#0F5FDC; border-width:3px"></x-connector>
<x-connector x1="116" y1="220" x2="116" y2="300" style="color:#8A8FA8; border-width:2px; border-style:dashed"></x-connector>
```

Layer band and link row:

```html
<div class="band"><p class="lbl">Who talks to it</p><div class="row" style="gap:16px">
<div class="box"><h3>Name</h3><p>One line</p></div></div></div>
<div class="link"><x-shape kind="arrow-down" style="width:30px; height:26px; background:#0F5FDC; flex:none"></x-shape><p>Protocol · credential per caller</p></div>
```


Feature status row (granular features slide):

```html
<div class="rowcard gridf"><p class="id">Analyst</p>
<div class="col" style="gap:4px"><h3>Queue · claim · close</h3><p class="mono">test_workflows.py</p></div>
<p>What the user gets, in two lines at most.</p><p class="pill ok">Done</p></div>
```

Results row (results slide):

```html
<div class="rowcard gridr"><div class="col" style="gap:4px"><h3>Fraud-model quality</h3><p class="mono">output/evaluation_report.md</p></div>
<p class="val">2× baseline</p><p class="goal">1.81×</p><p class="pill stop">Missed</p></div>
```

(Add `.gridr { display: grid; grid-template-columns: 1.5fr 1fr 1fr 190px; gap: 24px; align-items: center; }` to the stylesheet; it is listed in Appendix A.)

File tree card (file architecture slide), one paragraph per line, indentation with non-breaking spaces:

```html
<div class="card"><div class="tree">
<p><span class="f">project/</span></p>
<p>├─ <span class="f">backend/app/</span>&#160;&#160;&#160;<span class="c"># rules, decision, API</span></p>
</div></div>
```

Screenshot frame (screens slide):

```html
<div class="shot"><img src="…" alt="Analyst review queue with one alert open" width="533" height="372"></div>
<h3>Fraud analyst</h3><p class="note">Works the riskiest alert first.</p><p class="mono">frontend/src/Analyst.jsx</p>
```


### Extra patterns used by Prompt 1 only

Feature row (granular features slide):

```html
<div class="rowcard gridf"><p class="id">Analyst</p>
<div class="col" style="gap:4px"><h3>Review queue · claim · close</h3><p class="mono">alerts, claim, close_alert</p></div>
<p>What the user gets, in two lines at most.</p><p class="pill info">Goal 1</p></div>
```

Wireframe frame:

```html
<div class="wf"><p class="wbar">Role</p><div class="wbody">
<div class="wpanel ask"><p class="wt">Key question?</p><div class="wl" style="width:85%"></div>
<div class="row" style="gap:10px"><p class="wfield">Input</p><p class="wbtn">Action</p></div></div></div></div>
```
