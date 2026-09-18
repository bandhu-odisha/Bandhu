# Desktop "Be a Bandhu" corner pill + dead CSS clean-up

Branch `ux-review-fixes`, baseline `11474f4`. Commit locally, never push.
Follow-up to `DONE/planning/2026-09-18-ux-review-fixes/spec.md` (its "Deferred" list).

## Ground rules
- `css/X.css` and `static/css/X.css` are tracked twins: edit both, keep byte-identical (`diff -q`).
- Cache-busters: templates write `{% static 'css/X.css' %}?v=N`. For every CSS file you change, set ONE new number = (highest N for that file anywhere in the working tree) + 1, in EVERY template that references it. Count substitutions and read back with grep; a script that reports success on zero matches is a bug.
- React home: build output `static/frontend/assets/index.{js,css}` is committed; after `cd frontend && npm run build`, bump both `?v=` in `templates/landing_react.html` (currently 309).
- `./venv/bin/python`; zsh default shell (quote globs, `/bin/bash` for scripts). No `print()` in app code.
- Suite must stay `Ran 760 tests ... OK (expected failures=10)`.
- Layout is verified on the RENDERED page with chrome-devtools-axi before returning, never by reading CSS. Restate all `emulate` flags on every call, run it after a first `open`, `open` again, read back `innerWidth`.

## D1. Desktop pill: small, tucked in the corner (user chose this option)
Problem: above 600px the inner-page pill (`.bandhu-fab-cta`, `css/custom.css` ~1025-1074, markup `templates/base.html` ~124) floats at `right: 1.75rem; bottom: 6rem` with `font-size: 1rem; padding: .625rem 2.25rem`, and covers card text (seen on `/publications/` at 1366px over the 5th card's title).
Change, for viewports wider than 600px only: `right: 1rem; bottom: 1rem`; smaller pill (about `font-size: .875rem; padding: .5rem 1.25rem`), still at least 40px tall and keyboard-focusable; keep colours, hover, and the `--on-dark` inversion. The phone bottom bar (`max-width: 600px` block) must not change.
React home page (`frontend/src/components/BeABandhuFab.jsx`, pill classes in `frontend/src/cta.js`): at `sm:` and up it already sits at `right-7 bottom-7`; make it match — 16px from the edges and the same smaller size — without changing the phone layout (`max-sm:` classes) or other users of `ctaPillClass`/`CTA_PILL_CLASS` (the Volunteer section button must keep its size; add a size modifier for the FAB only).
**User changes during the run (2026-09-19), these override the two paragraphs above where they conflict:**
1. Phones no longer use the full-width bottom bar. Remove the `max-width: 600px` bar block, `body.has-fab-cta { padding-bottom }`, and the `has-fab-cta` body class if nothing else uses it.
2. On phones the button is "like a circle": a 64px round button (68px max if needed) in the bottom-right corner, 16px from the edges with the safe-area inset respected, keeping the words as two centred lines "Be a / Bandhu" (not icon-only), text never below 11px, `aria-label` kept. Above 600px it is the small corner pill. Same on the React home page via `max-sm:` classes.
3. The phone circle shows a handshake icon instead of the words (overrides "not icon-only" in point 2). Font Awesome Free 5.13 `fas fa-handshake` is already loaded on inner pages and the React home, so no new dependency. Markup: `<i class="fas fa-handshake bandhu-fab-cta__icon" aria-hidden="true">` + `<span class="bandhu-fab-cta__label">Be a Bandhu</span>`; on phones the icon shows and the label is visually hidden with the clip pattern (never `display:none`); above 600px the icon is hidden and the words show. `aria-label` kept. Clicking the icon must still open the signup modal.
4. Under the icon the phone circle shows a small visible label "Join ବନ୍ଧୁ" with ବନ୍ଧୁ in bold (`<strong lang="or">`), one line, 11px minimum, fully inside the circle (68px, up to 72px if needed). It is `aria-hidden`; the anchor's `aria-label="Be a Bandhu — sign up"` stays the accessible name. This overrides "label visually hidden on phones" in point 3. Desktop pill: words "Be a Bandhu" only. Odia text stays literal UTF-8 in the template and the JSX; the built bundle must contain it.
5. FINAL label decision (overrides points 3-4 on wording and on which label shows where): one label on both desktop and phone — "Be a ବନ୍ଧୁ" with ବନ୍ଧୁ bold — plus the handshake icon on both. Desktop: small corner pill, icon left of the label. Phone: 68-72px circle, icon above the label. Single `__label` span (`aria-hidden`), anchor keeps `aria-label="Be a Bandhu — sign up"`. Only the floating button changes; the Volunteer section copy stays "Be a Bandhu".
Known trade-off accepted by the user: a floating button can sit over content again on phones; it is small, so it covers little.

Check first why inner pages used `bottom: 6rem` (something else in that corner? `#scroll-to-top` is `display:none !important`; grep for other fixed bottom-right elements, chat widgets, cookie bars). If something real lives there, keep clear of it and say so.

## D2. Dead CSS clean-up (only what is provably dead)
Candidates reported by review; treat each as a hypothesis and prove it before deleting:
1. `css/ankurayan.css`: leftovers of the removed auto-scrolling year strip — `.ankurayan-year-sep`, `@keyframes ankurayanYearsScroll`, any `.ankurayan-years-track` rule that only served the marquee (duplicate-track selectors, `animation`, `will-change`, pause-on-hover). Proof = grep of all templates/JS shows no element or class that the selector can match.
2. `css/custom.css` ~797-806: phone block setting `justify-content: flex-end !important; padding: 0 0 8px 0 !important` on `body.pillar-inner-page #top-section .slider-txt-container…`, reported as fully shadowed by the later-loading `css/pillar-inner-banner.css` (`padding-top: 88px` rule). Proof = every template that loads `custom.css` and renders that markup also loads `pillar-inner-banner.css` after it, AND the computed `justify-content`/`padding` on the element at 360px are identical with the block removed.
3. Per-file phone pull-up overrides (`margin-top: 0` at `max-width: 600px`) in `css/ashram.css` / `css/anandakendra.css` that are shadowed by identical-selector rules in the later-loading `css/initiative-program-year.css`. Only delete a rule if NO template loads that file without `initiative-program-year.css` (e.g. `ashram.html`/`ashram_detail.html` may load `ashram.css` alone — then the rule is live, keep it).
Anything not provable stays. Do not refactor to a shared variable; deletion only.

## Verification (do before returning)
Method for D2: BEFORE deleting anything, record at 360x800 and at 1366x768, for each page below, a JSON of computed styles — banner container `height`, `justify-content`, `padding`; h1 rect; first content block `margin-top`; year-pill track `display`/`flex-wrap`/`animation-name` — and a screenshot. AFTER deleting, record again and diff the JSON: it must be identical. Pages: `/people/`, `/sanskar/`, `/swabalamban/`, `/ankurayan/`, one ankurayan detail, `/anandakendra/`, one anandakendra detail, `/bandhughar/`, one bandhughar detail, `/other_activities/`, `/odisha-satabdi-sevavrata/`, `/prasanta-raktadan-shibir/`, `/publications/`.
For D1 at 1366x768 on `/publications/`, `/people/`, `/ankurayan/` and `/`: pill rect is within 16px (+-2) of the right and bottom edges, height >= 40; on `/publications/` `document.elementsFromPoint` at each visible card title's centre does not include the pill at scroll 0. At 360x800 the inner-page bar rect is unchanged: `[0, 752, 360, 48]`, `body` padding-bottom `48px`; home phone layout unchanged (screenshot).
Save evidence under `/tmp/bandhu-e2e/d/` and look at the screenshots.

## Orchestrator steps after review (user asked 2026-09-19)
- Record the browser walk-through as a video again once the work is done: reuse `/tmp/bandhu-e2e/record.sh` (frames + `.srt` captions stitched with ffmpeg, captions as a subtitle track), update captions for the round button, add frames that show the button over the footer on a phone and the corner pill on desktop. Send the MP4 to the user.
- Move this folder to `DONE/planning/` before the commit.

## Status — DONE 2026-09-19 (branch `ux-review-fixes`, not pushed)
Checklist: [x] D1 inner pages [x] D1 React home [x] D2 dead CSS [x] cache-busters [x] twins [x] rendered checks [x] video

Tests: `Ran 760 tests ... OK (expected failures=10)` (unchanged count). Review: one fix cycle, then approved.
Measured: phone 360x800 — 68x68 circle, 16-18px from right/bottom, no `body` padding, icon or label tap opens the signup modal, inverts to white over the dark footer, modal renders above it. React pill 44px tall at 640, 768 and 1366 wide. D2 before/after computed-style JSON identical on 13 pages x 2 viewports.
Video: `/tmp/bandhu-e2e/bandhu-ux-walkthrough-v2.mp4` (32 steps).

### What was decided along the way
- `bottom: 6rem` on the old pill avoided nothing — no other element lives in that corner.
- React button is positioned in px, not rem: the landing page's root font-size is responsive, so rem offsets drift.
- React home keeps the system font for the Odia word: that page loads no Odia font for any of its Odia text, and ~95 KB for one word is a bad trade on slow 4G. Inner pages use the existing `oriya` `@font-face`.
- D2 candidate 1 (Ankurayan marquee leftovers) did not exist — nothing to delete. Two look-alike rules were kept because pages that load only that stylesheet still match them (`.angular-ashram + .pillar-overlay-cards` for `ashram.html`; the `anandakendra.css` block for `anandkendra_detail.html`).

### Deferred
- A floating button can sit over content (seen: edge of the 5th card on `/publications/` at 1366px, the "Our Mission" heading on the phone home page). Accepted by the user when choosing the floating option.
- Visible label "Be a ବନ୍ଧୁ" vs accessible name "Be a Bandhu — sign up": reviewed, not a WCAG 2.5.3 failure; revisit if voice-control users report trouble.
- `accounts_base.html` still links `custom.css` with no `?v=`.
