# Rough idea

## Original request (verbatim, planning session cdda5d83, 2026-10-29)
In the Ankurayana home page, (check the screenshot) all tiles with images should take each photo's natural aspect ratio instead of a forced square crop like Gallery tiles. 
ref comit hash: a0472897b2ddca0e5bcab925ccbc176fd55955e3

show me the mocks before building it

## Answers (recorded by the orchestrator; only A: lines are the user's words)
Q (orchestrator): Which layout should the 17 'Running Ankurayans' cards use? Today each photo is cropped to the same 370×270 box. Option 1 copies the Gallery fix exactly but replaces the Glide carousel. Option 2 is only CSS, but cards end up different heights. Option 3 is also only CSS: nothing gets cropped, but each photo is shrunk to fit inside one fixed box. In all three, the hero image switches to its natural shape.
Options (orchestrator):
- 1. Same as Gallery (Recommended): every card 270px tall, width follows the photo (clamped 200–720px); Glide replaced on desktop by a side-scrolling strip that keeps arrows and auto-scroll; phones one card per screen.
- 2. Same width, height follows photo: Glide stays, cards 370px wide, image height follows photo; titles won't line up.
- 3. Same box, whole photo fits: Glide stays, 370×270 box, whole photo shown with object-fit: contain on a tint.
A: "1. Same as Gallery (Recommended)"
Meaning (orchestrator): build spec.md items A1, B1–B3, C1 (Gallery recipe from a0472897).

## Follow-ups (2026-10-29)
/re-construct planning/2026-10-29-ankurayan-natural-tiles/plan.md (run by dev-workflow Reconstruct Gate after plan approval: "Implement the following plan: # Ankurayan home: image tiles keep each photo's natural shape ...")

## Answer 2 (2026-10-29, after r1 review; only A: is the user's words)
Q (orchestrator): The prev/next arrows on the Ankurayan home card strip are hidden by a site-wide 'no arrows, auto-scroll only' rule. Without them, a mouse user whose computer turns off animation can't reach most cards. How should the strip let people move through the cards?
Options (orchestrator):
- Show arrows always (Recommended): arrows show on this strip only, on every desktop; matches option 1 wording 'keeps the arrows and auto-scroll'; other carousels keep hiding theirs.
- Arrows only if motion off: arrows show only when auto-scroll is off because of the motion setting.
- Thin scrollbar instead: no arrows, a thin scrollbar under the strip on desktop.
A: "Match the behavior of other carousels on the side like Gallery "
Meaning (orchestrator): spec Q2 — no arrow buttons, hidden scrollbar, auto-scroll always runs (Gallery.jsx:128-151 has no reduced-motion check), pause on hover/focus. Changes spec B1, B3.
