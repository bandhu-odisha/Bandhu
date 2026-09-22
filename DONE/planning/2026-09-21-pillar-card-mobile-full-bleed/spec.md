# Swabalamban pillar page — full-bleed text card on phones + fix the clipped quote

## Status: implemented, verified on all three pillars

Both changes shipped in `bandhuapp/templates/pillar_page.html`. Verified in-browser
(chrome-devtools-axi) on `/swabalamban/`, `/sanskar/`, `/swaraj/` at phone (~500px, the
tool's floor), the 600-768px band (700px), and desktop (1280px). `python manage.py test`
green at 760/760 throughout.

**The "specificity trap" section below undersold the trap.** It documented one
`!important` collision (`#about.pillar-overlay-cards .container`, `anandakendra.css:738`).
Rendered testing found `css/anandakendra.css:767-786` carries a second, undocumented block
— "Force exact Sanskar card geometry on Anandakendra about cards" — that re-declares
`#about.pillar-overlay-cards .pillar-overlay-card--image` and `--text` with an `#about` ID
prefix *and* `!important` on width/max-width/padding/box-shadow. The plain-class overrides
this plan specified (`.pillar-overlay-cards .pillar-overlay-card--image { width: 100%; }`
etc., no ID, no `!important`) silently lost to it: the image card stayed at 92% width, its
padding stayed inset (photo not flush despite the card div reading full-bleed), and the
text card kept its shadow. Fixed by re-targeting those two rules through the `#about`
prefix with matching `!important` — see the code comment at `pillar_page.html:316-318`.
Lesson for next time: grep the loaded stylesheet for *every* class the plan's selectors
touch, not just the one collision spotted by inspection.

## Context

![Swabalamban pillar page on a phone, before the fix — the cream card occupies only the middle ~63% of the screen and the italic quote above it is cut off mid-sentence](screens/swabalamban-mobile-before.jpeg)

On a phone, the cream text card on `/swabalamban/` (the "Explore: SANSKAR / SWARAJ"
card with the Odia + English description) wastes about a third of the screen width.
The card is already 100% of its Bootstrap column — the narrow text comes from a stack of insets:

- `#about.pillar-overlay-cards .container` → `padding-left/right: 1.5rem` (24px)
- `.pillar-overlay-cards .pillar-overlay-card` → `padding: 1.5rem 1.75rem` (28px)

(Bootstrap 4's `.row` negative margin cancels the column's own 15px, so those two are
the whole story.) Net: ~52px of dead space per side on a 390px screen → text column
~286px, which is why "SWARAJ" wraps to its own line and the Odia paragraph breaks every three or four words.

The same screenshot shows a second, separate defect: the italic quote above the card
("Self-reliance is a way of life, a way that leads to prosperity and…") is cut off
mid-sentence. Its box `.pillar-image-caption.swabalamban-image-caption` is pinned to
`min-height: 2.35rem` (~38px, one line) while its two `.caption-line` children are
`position: absolute`, so the box cannot grow when the text wraps — the overflow slides
behind the opaque card below it. This affects Sanskar and Swaraj too (same absolute
pattern, `min-height: 4.25rem`), and the text comes from the database, so no fixed
height is safe.

Intended outcome: on screens ≤600px the text card and the logo card run edge to edge
(no side gutter, no rounded corners, no shadow), and the rotating quote box grows to
fit however many lines its database text wraps to, at every width.

## Decisions already made

- **Edge-to-edge**, not a small gutter — user's pick.
- **Phone-only** for the width change (`max-width: 600px`); desktop's two-column
  overlap layout is deliberately tuned and stays untouched.
- **Fix the clipped quote in the same change.**

## The specificity trap — read before editing

`css/anandakendra.css:738-752` already sets the container padding with `!important`:

```css
#about.pillar-overlay-cards .container {
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    ...
}
```

The template's own inline copy (`pillar_page.html:79-93`) is non-important and is
**losing** today. So the new mobile rule must use the selector
`#about.pillar-overlay-cards .container` **with `!important`**, or it will silently
do nothing.

## Where the edit goes

**One file: `bandhuapp/templates/pillar_page.html`** — its inline `<style>` block
(lines 16-580), which sits in `{% block style %}` and is therefore the last stylesheet
on the page (`templates/base.html:58`).

**All three pillars are affected, and that is intended.** `pillar_page.html` is a single
template shared by Sanskar, Swaraj and Swabalamban: the overlay-card section is gated on
`{% if page_title == 'Sanskar' or page_title == 'Swaraj' or page_title == 'Swabalamban' %}`
(line 666), so all three render the same `#about.pillar-overlay-cards` markup, the same
`.pillar-overlay-card--image` / `--text` pair, and the same `.pillar-image-caption`
rotating quote. Every rule below therefore lands on `/sanskar/`, `/swaraj/` and
`/swabalamban/` alike — full-bleed cards on phones on all three, and the quote-box fix on
all three. The generic `{% else %}` branch at line 758 (`.pillar-hero`, used by any other
page rendered through this template) is untouched.

Per-pillar differences to keep in mind while checking:

- **Sanskar** shows the Explore row via `related_links` (Anandakendra + Ankurayan,
  `bandhuapp/views.py:541-544`); **Swabalamban** uses the hardcoded Sanskar/Swaraj branch
  (lines 722-727); **Swaraj** renders no Explore row at all
  (`bandhuapp/pillar_pages.py:115-134` passes no `related_links`).
- Sanskar's caption box floor is `min-height: 4.25rem` (lines 145-151), Swabalamban's is
  `2.35rem` (line 233), and Swaraj has its own duplicate rule block with
  `width: 92%` (lines 189-196). All three need the Change 2 edits; only Swaraj needs the
  extra width override.

Why not `css/anandakendra.css`: that file is loaded by 15 templates
(ashram, ankurayan, anandakendra, charitywork, sevavrata, patriotism,
prasantaraktadan, `templates/initiative_program/*`). The inline block only exists in
`pillar_page.html`, so the blast radius is exactly the three pillar pages and nothing
else — which is the wanted scope.

Two consequences worth stating: **no `?v=NNN` bump is needed** (nothing in `css/`
changes; the inline block ships with the HTML), and **no `git add -f`** is needed
(`.gitignore` ignores `*.html` but this template is already tracked).

## Change 1 — full-bleed cards on phones

Extend the **existing** `@media (max-width: 600px)` block at `pillar_page.html:312-317`
rather than adding a new breakpoint. 600px is this page's phone line already — it is
where `--inner-banner-height` flips to 150px (`css/custom.css:599`) and where the
section pull-up is zeroed.

Add inside that block:

- `#about.pillar-overlay-cards .container` → `padding-left: 0 !important; padding-right: 0 !important;` (beats `anandakendra.css:738`)
- `.pillar-overlay-cards .pillar-overlay-card` → `padding: 1.5rem 1rem; border-radius: 0;`
- `.pillar-overlay-cards .pillar-overlay-card--text` → `box-shadow: none;`
  (this modifier carries its own four-layer shadow at lines 101-108; the base rule's
  shadow is separate and also needs clearing)
- `.pillar-overlay-cards .pillar-overlay-card--image` → `width: 100%; max-width: 100%; border-radius: 0;`
- `.pillar-overlay-cards .pillar-image-caption` → `padding-left: 1rem; padding-right: 1rem;`

That caption rule is not optional. The italic quote lives in the container but
**outside** any card (`pillar_page.html:701-706`, inside the `col-lg-4`), and it has no
padding of its own — its lines fill the box edge to edge. Zeroing the container padding
without this would push that text flush against both screen edges. Card padding does
not protect it.

Also drop the `width: 92%; max-width: 92%` from
`.pillar-image-caption.swaraj-image-caption` (lines 189-196) inside the phone query —
otherwise on Swaraj the caption ends up narrower than the now-100% logo card above it.

The logo card is the other easy thing to miss: it is `width: 92%; margin-left: 0`
(lines 129-137). Zeroing the container padding alone would leave it flush against the
left edge with an 8% gap on the right — visibly lopsided. Taking it to 100% makes both
cards full-bleed and consistent.

One matching markup edit goes with it: the hero `<img>` at line 674 declares
`sizes="(max-width: 600px) 92vw, 600px"`. Since the card becomes 100% wide on phones,
change `92vw` to `100vw` so `responsive_img`'s `srcset` picks a candidate that is not
undersized for the space it now fills.

Expected result: text column ~358px instead of ~286px on a 390px screen (+25%), and
"Explore: SANSKAR SWARAJ" fits on one line
(label ~60px + two pills ~195px + gaps ~13px ≈ 268px, well inside 358px).

## Change 2 — quote box grows to fit its text

Structural fix, no magic number: stack the two rotating `.caption-line` elements in a
single CSS grid cell instead of absolutely positioning them. Both children occupy
`grid-area: 1 / 1`, so they still overlap for the crossfade, but the container's height
becomes the height of the taller one and follows the wrapped text.

Edit the existing rules **in place** rather than layering overrides:

- `pillar_page.html:145-151` `.pillar-image-caption, .sanskar-image-caption` → add
  `display: grid;` (keep `min-height` as a floor, keep `text-align: center`)
- `pillar_page.html:152-163` `.caption-line` → replace
  `position: absolute; top: 0; left: 0; right: 0;` with `grid-area: 1 / 1;`
- `pillar_page.html:189-207` the `.swaraj-image-caption` duplicate → same two edits

`.swabalamban-image-caption` (lines 231-238) only overrides `margin-top`, `min-height`
and the animation, so it inherits the fix with no edit of its own.

This is applied at **all** widths, not just phones: the `min-height` values stay as
floors, so a one-line quote on desktop renders identically, and the bug class (database
text longer than a hardcoded box) disappears for all three pillars at once. The
`opacity`/`translateY` keyframe animations are unaffected by the position change.

## Pre-flight check (before touching anything)

`css/bandhu.css` and `static/css/bandhu.css` are byte-identical today (md5
`86d1eb8e882c28ef9c558e8f67b2250c`), and `bandhu/settings.py:268-275` lists
`BASE_DIR/static` before the `('css', BASE_DIR/'css')` prefix — so an edit to the wrong
copy would be silently ignored. This plan edits no `.css` file, so the trap cannot bite
the edit itself — but it can invalidate the reasoning. Run
`python manage.py findstatic css/anandakendra.css` **and diff the two copies**
(`diff css/anandakendra.css static/css/anandakendra.css`). Only `bandhu.css` was
md5-verified as identical; Change 1's whole `!important` premise rests on what the
*served* copy of `anandakendra.css` contains.

Also grep `css/anandakendra.css` for `caption-line` / `pillar-image-caption` before
Change 2 — if it defines those with `!important`, the in-place edits need matching
overrides in the inline block instead.

## Verification

Per observation 16 (a phone-only CSS change that passed tests and two reviews, then
failed on first look in a browser), the rendered check comes **before** review, not
after.

1. `source venv/bin/activate && python manage.py runserver`
2. Drive it with the `chrome-devtools-axi` skill (project memory: use the browser, not
   curl/lsof). **Observation 6 applies:** `resize`/`emulate` in this environment reports
   success but floors the viewport around 500x700, and can silently target a stale tab.
   So: run `pages` and `selectpage` on the right tab, then read back
   `window.innerWidth` and compare to the requested value. Report the **achieved**
   width, not the requested one.
3. Check all three pillar pages, since they share the template and Change 2 touches the
   shared caption rules: `/swabalamban/`, `/sanskar/`, `/swaraj/`.
   - Text card spans the full viewport with no side gutter, square corners, no shadow.
   - Logo card spans full width, not lopsided.
   - "Explore: SANSKAR SWARAJ" on one line (Swabalamban and Sanskar; Swaraj renders no
     Explore row — `bandhuapp/pillar_pages.py:115-134` passes no `related_links`).
   - The italic quote is fully readable, not clipped by the card, and the EN↔Odia
     crossfade still works without the layout jumping between the two.
4. Measure, don't eyeball: `document.querySelector('.pillar-overlay-card--text') .getBoundingClientRect().width` should equal `window.innerWidth`, and
   `.swabalamban-image-caption` `scrollHeight` should be ≤ its `clientHeight` (no
   overflow).
5. **Check the 600-768px band too (~700px).** It is a third distinct configuration and
   the one Change 2 disturbs most: between 768 and 992 the image column is `col-md-5`
   (~41% wide), so the quote wraps to 3-4 lines, and the grid conversion lets that box
   *grow* where it previously sat at a fixed 4.25rem — directly under the
   `margin-top: -100px !important` pull-up that was tuned against the old fixed height.
   That is exactly the failure shape observation 16 describes. The 500px viewport floor
   is a minimum, so 700px is reachable.
6. Confirm desktop is unchanged at ≥992px — same three pages, side-by-side cards with
   the `-280px` pull-up intact.
7. `python manage.py test 2>err.log >/dev/null; tail -20 err.log` — expect
   `Ran 760 tests ... OK (expected failures=10)`. Any other count is a discovery
   failure, not a pass. Tests cannot see layout; this run only proves nothing else
   broke.

## Files touched

- `bandhuapp/templates/pillar_page.html` — the only code file changed: the inline
  `<style>` block (the `@media (max-width: 600px)` query at 312-317, the caption rules at
  145-163, and the Swaraj caption duplicate at 189-207) plus the one `sizes` attribute on
  the hero `<img>` at line 674.
- `DONE/planning/2026-09-21-pillar-card-mobile-full-bleed/spec.md` and
  `screens/swabalamban-mobile-before.jpeg` — new, per Step 0.
