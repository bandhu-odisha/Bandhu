Status: BUILT 2026-10-29 — A1, B1–B3, C1 done; reviews r1 NEEDS_CHANGES → r2 APPROVED (opus), end pass APPROVED (fable); Ran 762 tests OK (expected failures=10).
Status: 2026-10-29 correction — Q2 (arrows): match Gallery, so no arrow buttons and auto-scroll always runs (no reduced-motion gate). Changes B1, B3 and the B2/B3 confirm lines.
# Ankurayan home: image tiles keep each photo's natural shape

Status: reconstructed 2026-10-29 from `plan.md` (same folder). Build from this file.

## Original request
> In the Ankurayana home page, (check the screenshot) all tiles with images should take each photo's natural aspect ratio instead of a forced square crop like Gallery tiles.
> ref comit hash: a0472897b2ddca0e5bcab925ccbc176fd55955e3
>
> show me the mocks before building it

## Questions I asked
- **Q1 (ANSWERED → B1–B3).** Decision: which layout the "Running Ankurayans" cards use. Options: (1) Same as Gallery — every card 270px tall, width follows the photo clamped 200–720px, Glide replaced by a side-scrolling strip with arrows + auto-scroll, phones one card per screen; (2) same width, height follows photo — Glide stays, 370px wide, titles stop lining up; (3) same box, whole photo fits — Glide stays, 370×270 box with `object-fit: contain` and tint. In all three the hero switches to its natural shape. Recommended: (1), evidence: it is the a0472897 pattern the user cited (`git show a0472897 -- frontend/src/components/Gallery.jsx`). A: "1. Same as Gallery (Recommended)". Label: PROVIDED (planning session cdda5d83, AskUserQuestion answer).

- **Q2 (ANSWERED → B1, B3).** Decision: how users move through the strip, given `css/custom.css:527-531` hides every `.glide__arrows` site-wide ("auto-scroll only, no arrows or dots (match landing page)") so the planned arrows never show, and under reduced motion auto-scroll was off. Options: (1) show arrows on this strip always (recommended at the time: matches Q1 wording "keeps the arrows"); (2) arrows only when reduced motion is on; (3) thin scrollbar instead. Evidence: both r1 reviewers (`scratch/briefs/u1-r1-*-verdict.md`), `css/custom.css:528`. A: "Match the behavior of other carousels on the side like Gallery". Label: PROVIDED. Meaning (orchestrator): copy Gallery (`frontend/src/components/Gallery.jsx:128-151`): no arrows, hidden scrollbar, auto-scroll always on, pause on hover/focus.

## Confirm these changes
Approved together with the plan via ExitPlanMode (PROVIDED, planning session cdda5d83):
- A1: hero image box follows its photo instead of a square. Evidence: `css/ankurayan.css:152`, `:196` force `aspect-ratio: 1 / 1`.
- B1: the 17→15 Glide bullets and the (already hidden) arrow buttons go away. Evidence: bullets at `ankurayan.html:224-228` index fixed-width slides; a variable-width strip has no slide index.
- B2: on phones each card image is 225px tall, whole photo shown on a tint (`contain`), instead of a cropped box. Evidence: `css/custom.css:1176-1178` sets 225px under 1199px today.
- B2: on desktop, space beside a clamped photo (banners over 720px wide) shows a `#e6f0f1` tint, as in the Q1 option-1 preview ("thin tint bands" for the 2019 banner). Evidence: 2019 ratio 3.48 → 940px > 720px cap.
- B2: the strip's scrollbar is hidden and there are no arrow buttons, as in Gallery (`Gallery.jsx:203` `scrollbar-hide`, no arrows) and as today (arrows hidden by `css/custom.css:528`). Per Q2.
- B1: a card whose logo has no responsive rendition (2021 locally) gets a 360px-wide tile. Evidence: `responsive_image()` returned None for 2021.
- B3: auto-scroll always runs every 2s (like Glide `autoplay: 2000` today and Gallery, neither checks reduced motion); it pauses while the strip is hovered or has keyboard focus. Per Q2.

## My reading of the request
"All tiles with images" on `/ankurayan/` = the hero card and every "Running Ankurayans" card. "Like Gallery" = the a0472897 recipe: fixed height, width from the photo's ratio clamped 200–720px, `object-fit: contain`, per-tile `sizes`, auto-scroll by real `offsetLeft`. Out of scope: the detail page (`ankurayan_detail.html`) and every other page that uses `.glide .card img`.

## Objectives and Outcome ledger
| Objective | Metric that shows it met | Record | Writer |
| --- | --- | --- | --- |
| Hero not cropped | hero box width/height ≈ img naturalWidth/naturalHeight (±2%) at 1280px and 390px | E2E notes in this folder `e2e.md` | dev-workflow Phase 4 E2E run (chrome-devtools-axi) |
| Cards not cropped | every card img box 270px tall on desktop, width ≈ clamp(200, 270×ratio, 720) (±2px), `object-fit: contain` | `e2e.md` | dev-workflow Phase 4 E2E run |
| Strip still moves | auto-scroll advances, wraps to 0, pauses on hover/focus | `e2e.md` | dev-workflow Phase 4 E2E run |
| Nothing else breaks | `Ran 762 tests ... OK (expected failures=10)` | test log in this folder | dev-workflow Phase 4 / orchestrator run |

New artifacts: 0 files (one inline `<script>` block replaces the Glide mount; `e2e.md` is a record, not code).

## Verification summary
| Claim | Status | Citation |
| --- | --- | --- |
| Hero forced square at desktop and ≤768px | CONFIRMED | `css/ankurayan.css:152`, `:196`; img `height:100%; object-fit:cover` `:159-164` |
| Square came from redesign merge 24c49db, no stated reason | CONFIRMED | `git blame -L 152,152` / `-L 196,196` → 24c49db |
| Card img 270px via `.glide .card img` | CONFIRMED (+ 225px under 1199px) | `css/custom.css:1171-1178` |
| `max-width: 24rem` card cap only under `.glide__slide` | CONFIRMED | `css/bandhu.css:190-193` (`.glide-carousel-custom .glide__slide .card`) |
| Photo ratios 0.75–3.48 | CONFIRMED locally (15 records, not 17; 2021 has no rendition) | `responsive_image()` over `Ankurayan.objects.all()`: 2018=0.75, 2019=3.48, 2021=None |
| Hero photo 960×672 | NOT FOUND locally (file missing in local media); claim from the planning screenshot | `HomePage.picture` path exists=False |
| `responsive_img` gives width/height of the mid rendition (ratio preserved) | CONFIRMED | `bandhuapp/helpers.py:44,76` |
| Carousel from 2020 (758f5c7) | CONFIRMED | `git log -1 758f5c7` "Ankurayan index page ready" |
| Detail page untouched by scoping to `body.ankurayan-page` | CONFIRMED | detail body class is `ankurayan-detail` (`ankurayan_detail.html:10`) |
| `ankurayan.css` loaded with `?v=14` | CONFIRMED on BOTH pages | `ankurayan.html:14`, `ankurayan_detail.html:15` |
| `css/` and `static/css/` copies identical and both tracked | CONFIRMED | `cmp` → same; `git ls-files static/css/ankurayan.css` |
| Arrow look comes from `.glide__arrow` theme + `#ankurayans .glide__arrow i` | CONFIRMED; theme positions arrows `absolute` against the nearest positioned ancestor (was `.glide`) | `css/ankurayan.css:467-478`, `templates/base.html:50` (glide.theme) |
| No view test asserts Glide markup | CONFIRMED | `grep glide applications/ankurayan/tests/test_views.py` → none |
| Target files have no hook/deny guard | CONFIRMED | grep of `.claude/settings*.json`, `~/.claude/settings.json` deny list |

## Priority order
Visual-only change, no data at risk. Order: A1 (hero, smallest) → B1+B2+B3 (strip markup, CSS, JS; one unit) → C1 (cache bust). Operating policy: none needed (no ranking by value).

## A. Hero
**A1.** Today: hero box is square and the photo is cropped, `css/ankurayan.css:152` and `:196` (`aspect-ratio: 1 / 1`), img `height:100%; object-fit:cover` (`:159-164`). CONFIRMED.
Change: add rules scoped `body.ankurayan-page .pillar-overlay-cards .pillar-overlay-card--image { aspect-ratio: auto; }` and `... img { height: auto; }` at desktop and inside the ≤768px block. No markup change.
Test that fails today: at 1280px and 390px, hero box ratio ≠ img natural ratio (square).
existing path checked: `grep -n "aspect-ratio" css/ankurayan.css` — only the square rules and detail-page `unset` rules exist; no home-page override.

## B. Running Ankurayans strip
**B1 (markup).** Today: `ankurayan.html:189-229` renders `.glide.ankurayans` with equal-width slides, arrows and bullets; `sizes="(max-width: 600px) 92vw, 300px"` (`:197`). CONFIRMED.
Change: drop the Bootstrap `div.row` wrapper around the strip (a flex parent would let the nowrap strip grow to full width, so it never scrolls); give `.ankurayan-strip-wrap` `width:100%; min-width:0`. Keep `section#ankurayans.glide-carousel-custom.page-section` (white-background rules at `css/ankurayan.css:274` key on it). Replace the `.glide` block with `div.ankurayan-strip-wrap` (position: relative, holds arrows) → `div.ankurayan-strip` (scroller, `tabindex="0"`, `aria-label`) → `ul.ankurayan-strip-row` → `li.ankurayan-strip-item` per record → existing `.card.page-card.ankurayan-year-card`. With a rendition: `{% widthratio ankur_logo_img.width ankur_logo_img.height 270 as tile_w %}`, `<li ... style="--tile-w: {{ tile_w }}px">`, img `sizes="(max-width: 767px) 92vw, {{ tile_w }}px"`. Without one: no `--tile-w` (CSS default 360px), no `sizes`. `sizes` is not clamped to 720 (template has no clamp): only 2019 exceeds (940px), and with renditions 480/960/1600 (`bandhuapp/helpers.py:11`) both 720 and 940 pick 960 at 1x and 1600 at 2x, so the pick is the same. Drop the arrow buttons and the bullets (Q2: match Gallery; arrows were hidden site-wide anyway). Scroller gets `role="region"` so its `aria-label` is read. Remove page-local `<style>` rules on `#ankurayans .glide__slide…` (`:52-78`) and `#ankurayans .glide.ankurayans` (`:88-90`); keep the theme 2-line clamp on `.ankurayan-strip-item .ankurayan-year-theme` and the 2.2rem top margin on `.ankurayan-strip-wrap`.
Test that fails today (exactly one new test method; suite becomes 762, bump CLAUDE.md 761→762 and 679→680): rendered HTML has no `.ankurayan-strip-item` with `--tile-w`; add a view test asserting the strip markup and one `--tile-w` value for a record with a known logo size (see Phase 4 note on how `responsive_img` behaves in tests).
existing path checked: `grep -rn "ankurayan-strip\|tile-w" applications css templates` → none; Gallery's equivalent lives only in React (`frontend/src/components/Gallery.jsx`), not reusable in a Django template.

**B2 (CSS).** Today: card image box set by `css/custom.css:1171-1178` and `css/ankurayan.css:411-417` (`min-height:380px` on `#ankurayans .glide__slide .card`). CONFIRMED.
Change, in `css/ankurayan.css` (copy byte-identical to `static/css/ankurayan.css`), all scoped `body.ankurayan-page`:
- `.ankurayan-strip { overflow-x:auto; scroll-snap-type:x mandatory; scrollbar-width:none; scroll-behavior:smooth }` (+ `::-webkit-scrollbar{display:none}`); `.ankurayan-strip-row { display:flex; gap:30px; list-style:none; margin:0; padding:.5rem 0 }`; item `scroll-snap-align:start; display:flex`.
- ≥768px: item `flex:0 0 auto; width:clamp(200px, var(--tile-w, 360px), 720px)`; card `min-width:0; width:100%`; img `height:270px; width:100%; object-fit:contain; background:#e6f0f1`.
- <768px: item `flex:0 0 100%; min-width:100%`; img `width:100%; height:225px; object-fit:contain; background:#e6f0f1`.
- prefers-reduced-motion → `scroll-behavior:auto` (jumps instead of smooth glides).
- Update `.ankurayan-list-page #ankurayans … .glide__slide …` selectors at `:283-304` to the new class names. Leave `.ankurayan-detail` and unscoped `#ankurayans .glide__slide` rules (`:407-417`, `:445-450`) alone — the detail page still uses Glide.
Test that fails today: at 1280px and 390px `strip.scrollWidth > strip.clientWidth` and `document.documentElement.scrollWidth === innerWidth`; at 1280px every card img box height = 270 and width ≈ clamp(200, 270×ratio, 720) ±2px (2018 → ~202px, 2019 → 720px); today all are equal width.
existing path checked: `grep -n "ankurayan-strip" css/*.css` → none; extends existing `css/ankurayan.css`.

**B3 (JS).** Today: `new Glide('.ankurayans', {...autoplay: 2000...}).mount()` at `ankurayan.html:345-360`. CONFIRMED.
Change: replace with ~25 lines of plain JS (IIFE, guard if no `.ankurayan-strip`): `step()` = Gallery's algorithm (`git show a0472897 -- frontend/src/components/Gallery.jsx`, lines `items.find(pos > scrollLeft+1)`, `target = min(pos, maxScroll)`, `scrollLeft = target > scrollLeft+1 ? target : 0`); `setInterval(step, 2000)` always (Q2: like Gallery and today's Glide); paused while hovered OR focused (two flags, so leaving one does not resume while the other holds); no arrow handlers. Positions measured as `item.offsetLeft - row.offsetLeft`.
Test that fails today: in browser, `scrollLeft` of `.ankurayan-strip` changes over 2.5s; reaches max then returns to 0; stays still while hovered or focused; runs under prefers-reduced-motion too.
existing path checked: `grep -rln scrollLeft js applications/*/templates` → `js/gallery-auto-scroll.js` (loaded site-wide from `templates/base.html`) auto-scrolls `[data-gallery-scroll]` strips, but steps by the FIRST card's width (`advance()`: `card.offsetWidth + gap`) — the uniform-width bug a0472897 fixed — and has no arrows or reduced-motion guard. Changing it would alter every gallery strip on detail pages (out of scope). So B3 stays inline, and the new markup must NOT carry `data-gallery-scroll` / `data-gallery-card`, or that helper would also drive the strip.

## C. Cache bust
**C1.** Today: `css/ankurayan.css?v=14` on `ankurayan.html:14` and `ankurayan_detail.html:15`. CONFIRMED. Change: bump both to `?v=15` (the detail page loads the same file; leaving it at 14 lets browsers keep a stale copy keyed on the old URL). No visible change on detail.
existing path checked: CLAUDE.md gotcha "bump the number when the file changes".

## Rule decisions
None (no trading logic).

## Completeness sweep
Specified: `--tile-w` (B1/B2), `.ankurayan-strip*` classes (B1/B2), `data-strip-dir` (B1/B3). Referenced-only: 0. Nonexistent: 0. Note: 2021 record has no rendition → fallback width 360px, `sizes` omitted. Hero file missing in local media → E2E checks the hero rule by pointing the hero `<img>` at a local static image (`img/our_mission1.jpg`) in devtools and comparing ratios.

## Requirement trace
| User's words | Item | Match |
| --- | --- | --- |
| "all tiles with images should take each photo's natural aspect ratio" | A1 (hero), B1–B2 (cards) | verbatim |
| "instead of a forced square crop like Gallery tiles" / ref a0472897 | B1–B3 copy a0472897's recipe | verbatim |
| "show me the mocks before building it" | done in planning session (Q1 previews) | verbatim |
| Phones: 225px uniform height, not natural ratio | B2 phone rule | narrowed — mirrors a0472897, which kept phones uniform; approved with the plan |

## Deferred
- Hero 960×672 ratio check against the real production photo — NO EVIDENCE locally (file not in local media). Reopen when: the cPanel media zip is restored locally or the change is live.

## Summary of this pass
Evidence harvested: transcript cdda5d83 (request, Q1 answer), a0472897 diff, local DB ratios. Mandate-first item: none at risk (visual only). Assumptions: 14 — CONFIRMED 12, NOT FOUND 1 (hero 960×672 locally), corrected 1 (17 cards → 15 locally). New findings: detail page also loads `ankurayan.css?v=14` (C1), arrows need a positioned wrapper once `.glide` is gone (B1), `.glide .card img` drops to 225px under 1199px today. Strategist: N/A. grill-me: Q1 resolved from existing context.

Item status table:
| ID | Status | file:line |
| --- | --- | --- |
| A1 | CONFIRMED | css/ankurayan.css:152 |
| B1 | CONFIRMED | applications/ankurayan/templates/ankurayan.html:189 |
| B2 | CONFIRMED | css/custom.css:1171 |
| B3 | CONFIRMED | applications/ankurayan/templates/ankurayan.html:345 |
| C1 | CONFIRMED | applications/ankurayan/templates/ankurayan_detail.html:15 |

Question decision table:
| ID | Decisions | Count |
| --- | --- | --- |
| Q1 | card layout option | 1 |

Fresh-reader pass: 4 found (count 4: B1/B2/B3 visible details; count 7: B4 ref, B3/B2 label), 4 fixed.

Counts: 1) 0 2) 0 3) 0 4) 0 5) 0 6) 0 7) 0.

Steps run / steps skipped (reason): 0 run, 0b run, 1 run, 2 run, 3 run (ratios measured from local DB; no other numbers), 4 skipped (N/A: no trading rule, threshold or strategy logic), 5 run (resolved from existing context, Q1), 6 run, 7 run, 8 run.
