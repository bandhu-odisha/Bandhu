Status: BUILT 2026-10-29 — D1–D3 done; r1 opus+fable APPROVED (Minor 1 logo-selector specificity fixed: `.ankurayan-detail .pillar-overlay-card--image .ankurayan-detail-logo-img`), end fable APPROVED; Ran 762 tests OK (expected failures=10). Accepted: logo fallback <img> without width/height may shift layout briefly.
# Ankurayan detail pages: photo tiles show the whole photo

Status: reconstructed 2026-10-29. Build from this file.

## Original request
> Let's apply same to the tiles in individual ankurayana pages like https://bandhuodisha.in/ankurayan/detail/2025/
>
> check the image

(The image was a capture of the live 2025 detail page: the logo card at top left, square, with the logo's left and right edges cut off.)

## Questions I asked
- **Q1 (ANSWERED → D2).** Decision: how the sidebar gallery photo (under the schedule) handles photos of different shapes. The logo-card fix was the same in every option. Options: (A) same 4:3 box, whole photo inside it on a soft tint, so the box doesn't change size when several photos rotate; (B) box takes each photo's shape, so the box changes height each slide and the page below moves; (Logo only) keep the gallery's 4:3 crop. Recommended: A. Evidence: real captures of local `/ankurayan/detail/2022/` (portrait 400×476 photo) at 1280 and 390, in `scratch/detail-{before,A,B}-*.png`; the gallery is a Bootstrap carousel when there are 2+ photos (`ankurayan_detail.html:1444-1475`). A: "A. Same box, whole photo (Recommended)". Label: PROVIDED.

## Confirm these changes
- D1: the logo card shows the whole logo in its own shape instead of a square. Evidence: `css/ankurayan.css:215-226` (`aspect-ratio: 1 / 1`, img `height:100%; object-fit:cover`); local 2022 logo 600×480 drawn in a 290×290 box. Same change the user approved for the home hero (commit ba6ea51).
- D2: covered by Q1.

## My reading of the request
"Same" = what ba6ea51 did on the home page: no photo tile crops its photo. On a detail page the photo tiles are the logo card and the sidebar gallery photo. Not photo tiles, left alone: guest avatars (round by design, `ankurayan_detail.html:705-715`), activity cards (all use the static placeholder `img/pimg6.jpg`, `:1675`), the commented-out carousel images. The same gallery classes under `.initiative-year-detail` in `css/initiative-program-year.css:328-344` belong to other initiative pages; that file is not loaded on this page (its `<link>` list is `:14-15`); out of scope.

## Objectives and Outcome ledger
| Objective | Metric that shows it met | Record | Writer |
| --- | --- | --- | --- |
| Logo not cropped | logo box width/height ≈ naturalWidth/naturalHeight (±2%) at 1280 and 390 | `e2e.md` in this folder | dev-workflow Phase 4 E2E run |
| Gallery photo not cropped | gallery link box stays 4:3; img computed `object-fit: contain` at 1280 and 390 | `e2e.md` | dev-workflow Phase 4 E2E run |
| Nothing else breaks | `Ran 762 tests ... OK (expected failures=10)` | test log in `scratch/` | dev-workflow Phase 4 / orchestrator run |

New artifacts: 0.

## Verification summary
| Claim | Status | Citation |
| --- | --- | --- |
| Logo box forced square, img cover | CONFIRMED | `css/ankurayan.css:215-226`; measured 290×290 box, natural 600×480 (2022, local) |
| Gallery link 4:3, img cover | CONFIRMED | `ankurayan_detail.html:1046-1059` (page-local `<style>`); measured 266.6×200, natural 400×476 |
| No other stylesheet on this page targets these classes | CONFIRMED | grep: only `css/initiative-program-year.css:328-344` (scoped `.initiative-year-detail`, not loaded here) |
| Square logo came from redesign 24c49db with no stated reason | CONFIRMED | `git blame -L 214,226 css/ankurayan.css` → 24c49db (same commit as the home square, checked in ba6ea51's spec) |
| `ankurayan.css` is loaded by both ankurayan pages at `?v=15` | CONFIRMED | `ankurayan.html:14`, `ankurayan_detail.html:15` |
| No view test asserts these classes' CSS | CONFIRMED | `grep -n "photo-wrap\|sidebar-gallery" applications/ankurayan/tests/` → none |

## Priority order
Visual only, no data at risk. D1 → D2 → D3.

## D. Detail page tiles
**D1.** Today: logo box is square and the logo is cropped, `css/ankurayan.css:218` `aspect-ratio: 1 / 1`, `:223-225` img `height:100%; object-fit:cover`. CONFIRMED.
Change: in those same rules set `aspect-ratio: auto` on `.ankurayan-detail .ankurayan-detail-photo-wrap` and `height: auto` on `.ankurayan-detail .ankurayan-detail-logo-img` (edit in place; the rules are already detail-only). Copy to `static/css/ankurayan.css` byte-identical.
Test that fails today: at 1280 and 390, logo box ratio ≠ natural ratio (1.0 vs 1.25 on 2022).
existing path checked: `grep -n "detail-photo-wrap\|detail-logo-img" css/*.css applications/ankurayan/templates/*.html` → only `css/ankurayan.css:215,222` and the markup.

**D2.** Today: gallery photo cropped to 4:3, `ankurayan_detail.html:1054-1058` `object-fit: cover`. CONFIRMED.
Change: `object-fit: contain; background: #e6f0f1` on `.ankurayan-sidebar-gallery__img` (same tint as the home strip). Keep the 4:3 box on `.ankurayan-sidebar-gallery__link`.
Test that fails today: computed `object-fit` of `.ankurayan-sidebar-gallery__img` is `cover`; whole portrait photo not visible.
existing path checked: grep above; edits the existing page-local rule.

**D3.** Today: `css/ankurayan.css?v=15` on both pages. CONFIRMED. Change: bump both to `?v=16` (the CSS file changes). No visible change.
existing path checked: CLAUDE.md gotcha "bump the number when the file changes".

## Rule decisions
None.

## Completeness sweep
Referenced-only: 0. Nonexistent: 0. Logo without a rendition (`:1428` fallback, no width/height attrs) also gets `height:auto`, so it follows the loaded image. Detail-page `.pillar-overlay-card--image.ankurayan-detail-photo-card` already has `aspect-ratio: unset` (`css/ankurayan.css:199-206`).

## Requirement trace
| User's words | Item | Match |
| --- | --- | --- |
| "apply same to the tiles in individual ankurayana pages" | D1, D2 | verbatim for photo tiles; guest avatars and placeholder activity cards excluded (not photos of different shapes) — see My reading |
| "check the image" (logo cropped) | D1 | verbatim |

## Deferred
- Live 2025 logo check — local 2025 logo exists (ratio 1.43) so E2E covers it; real production photos differ. Reopen when: deployed; open `/ankurayan/detail/2025/` and confirm the whole logo shows.

## Summary of this pass
Evidence: live capture (user), local measurements, mocks. Assumptions 6, CONFIRMED 6. Strategist N/A. grill-me: Q1 asked live with real captures.

Item status table:
| ID | Status | file:line |
| --- | --- | --- |
| D1 | CONFIRMED | css/ankurayan.css:218 |
| D2 | CONFIRMED | applications/ankurayan/templates/ankurayan_detail.html:1057 |
| D3 | CONFIRMED | applications/ankurayan/templates/ankurayan_detail.html:15 |

Question decision table:
| ID | Decisions | Count |
| --- | --- | --- |
| Q1 | gallery box behaviour | 1 |

Counts: 1) 0 2) 0 3) 0 4) 0 5) 0 6) 0 7) 0. Fresh-reader pass: not run (3-item visual spec; recount done by orchestrator from the tables above).

Steps run / steps skipped (reason): 0 run, 0b run, 1 run (inline inventory), 2 run, 3 run (ratios measured), 4 skipped (N/A: no trading logic), 5 run (Q1 live), 6 run, 7 run, 8 run.
