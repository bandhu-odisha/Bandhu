# Gallery tiles take the photo's own shape instead of a forced square crop

## Objective

Every photo in the `#gallery` carousel — across all category tabs — shows its full subject
on desktop: no cropping, no letterbox bars, tiles still read as an orderly row.

**Outcome ledger**: measured by the browser-console ratio check in Verification §7 below.
It compares each tile's rendered box ratio against the photo's natural ratio; a passing run
prints zero mismatches outside the nine tiles that hit the 720px width clamp (Deferred #1).
No file logs this automatically — it is a manual DevTools check run against the live/local
page, recorded by whoever runs Verification.

## Problem

`Photo.objects.filter(approved=True, picture__startswith='bandhuapp/gallery/')`
(`bandhuapp/views.py:435-441`) feeds the single `#gallery` carousel. Every category tab
(ALL, ANKURAYAN, ANANDAKENDRA, BANDHUGHAR, ACTIVITIES, OTHER) filters the same list
client-side (`frontend/src/components/Gallery.jsx`, `filtered` derived from `photos` and
`filter` state) — one render path draws every tile regardless of tab.

The 53 gallery photos span aspect ratio **0.56 to 3.48** (tall portrait to ultra-wide
banner). The prior render forced every tile into a fixed `aspect-square` box with
`object-fit: cover`: tall photos lost heads/feet, wide banners lost most of their width. A
banner at ratio 2.67 (`Logo2013.jpeg`, 960×360) had ~63% of its width cropped away — the
Odia text on it was cut off both edges.

A per-image `object-fit` threshold cannot fix this: banners and ordinary landscape photos
occupy the same ratio band. `Logo2016.jpeg` (a banner needing no crop) is ratio 1.786;
`Bandhughara.jpeg` (an ordinary photo that crops fine) is 1.778. No cutoff separates them.

## Design

The carousel is a horizontal scroller with `snap-x` — it has no columns to keep visually
aligned, only a shared top/bottom edge. Variable tile *width* costs nothing structurally
there; the fixed square was inherited from grid layout this component isn't. Desktop tiles
now share a fixed **height** and take their **width from the photo's own ratio** — order
comes from the shared baseline, not a shared shape. Mobile is unaffected: it already shows
one uniform full-width tile per screen (`frontend/src/index.css:357-371`,
`@media (max-width: 639px)`), which the new desktop-only rule (`@media (min-width: 640px)`)
does not touch — the two media queries are mutually exclusive at the same selector
specificity, so neither cascades over the other.

This needed no backend or database change: `bandhuapp/views.py:410-412` already attaches
exact `width`/`height` to every photo via `responsive_image()`
(`bandhuapp/helpers.py:43-88`), and 0 of 53 live photos are missing it.

## What shipped

**`frontend/src/components/Gallery.jsx`** — the tile map (`filtered.map`):

- Computes `ratio = width/height` per photo (from `picture_responsive`, falling back to
  `1` — today's square — when that field is absent) and passes it to CSS via an inline
  `style={{ '--tile-ratio': ratio }}` custom property, since the ratio must apply only
  above the mobile breakpoint and an inline style can't be scoped to a media query.
- Button: dropped the fixed `sm:w-[380px]` (width now comes from the CSS rule below);
  `bg-white` → `bg-slate-50` (a visible backdrop under the still-letterboxed clamped
  tiles, and under the mobile square).
- Image: `object-cover` → `object-contain`; dropped `group-hover:scale-105` — under
  `cover` that 5% zoom was invisible because the image already overflowed the box; under
  `contain` it would grow the image past the tile and `overflow-hidden` would shear ~2.5%
  off each edge, cutting the very text this change exists to reveal. The button's existing
  `hover:shadow-[var(--card-shadow-hover)]` remains as the hover affordance.
- `sizes` attribute now tracks the per-tile rendered width instead of the old flat
  `380px` hint: `tileWidth = Math.round(Math.min(720, Math.max(200, 380 * ratio)))` (the
  same clamp the CSS rule below applies) feeds `sizes={'(min-width: 640px) ${tileWidth}px, 100vw'}`.
  A flat `720px` bound was tried and reviewed off — it over-fetches the majority of tiles
  that render narrower than the clamp, picking an unnecessarily large `srcset` candidate
  on every tile instead of just the nine wide ones that actually need it.
- Auto-scroll timer (`useEffect` reading `[data-gallery-card]`): previously stepped by
  `firstCard.offsetWidth + gap`, exact only when every tile was the same width. Replaced
  with a scan to the next card's actual `offsetLeft` past the current scroll position:
  `target = next ? Math.min(pos(next), maxScroll) : 0`, then
  `el.scrollLeft = target > el.scrollLeft + 1 ? target : 0` — the second clamp is load-
  bearing, not decorative. An earlier version of this fix (`target` assigned straight to
  `el.scrollLeft`) got permanently stuck at `scrollLeft = 0` whenever the next tile's
  offset exceeded `maxScroll` (few/narrow tiles on some category tabs); clamping to
  `maxScroll` alone then got stuck at `maxScroll` instead, because the same "next" tile
  kept being found on every subsequent tick. The `target > el.scrollLeft + 1` progress
  check is what makes the two-state cycle (`0 ↔ maxScroll`) actually alternate rather than
  freeze at either end. Verified live against the real DOM on both a 3-tile and a 10-tile
  category tab — see the observation this spec's implementation left behind for the exact
  traces. Removes the `getComputedStyle` gap-parsing the old step arithmetic depended on.

**`frontend/src/index.css`** — new rule at `@media (min-width: 640px) { #gallery
.gallery-card-shell { height: 380px; width: auto; aspect-ratio: var(--tile-ratio, 1);
max-width: 720px; min-width: 200px; } }`:

- `height: 380px` matches the prior tile height exactly, so the carousel row height and
  everything below it is unchanged.
- `max-width: 720px` — backtested against the 53 live photo ratios: exactly 9 tiles exceed
  it (`Logo2019` 3.48, `Logo2013` 2.67, `Paika_Ananda_kendra` 2.24, `GC_Meeting_3` 2.24,
  `GC_Metting_1` 2.17, `GC_Meeting_111` 2.06, `GC_Meeting_4` 2.06, `Logo2012` 2.00,
  `Ankurayan_8` 2.00). Those nine are letterboxed on `bg-slate-50` inside the clamp — see
  Deferred #1.
- `min-width: 200px` — the tallest live photo (0.56) renders 213px wide at height 380, so
  nothing currently hits this floor; it guards against a future extreme upload.

**Rebuilt and committed**: `static/frontend/assets/index.{js,css}` regenerated via
`cd frontend && npm run build`; `templates/landing_react.html` cache-buster bumped
306 → 307 on both asset tags.

## Explicitly out of scope

- No Django/database change — `bandhuapp/models.py`, `views.py`, `admin.py`,
  `helpers.py`, and the thumbnail aliases in `bandhu/settings.py:242-252` are untouched.
- Lightbox (`Gallery.jsx`, the portal-rendered full view) was already `object-contain`.
  Unchanged.
- `frontend/src/components/Videos.jsx` (`video-card-shell`) — thumbnails there are
  uniformly 16:9, so variable width buys nothing. Left as-is.
- The classic Jinja landing at `/classic/` (`templates/landing_page.html`) reads `Photo`
  rows directly through a separate template. Not part of this change.

## Verification

1. `cd frontend && npm run build` — succeeds, no JSX errors.
2. `python manage.py test` — must print `Ran 736 tests ... OK (expected failures=10)`.
   Frontend-only change; any other count is a discovery failure, not a pass.
3. `python manage.py runserver`, open `/`, scroll to `#gallery`.
4. **ANKURAYAN tab**: banner tiles render wide and short with full Odia text visible;
   `Logo2019` (3.48) is letterboxed inside the 720px clamp on the grey backdrop.
5. **BANDHUGHAR tab**: 16:9 photos fill their tiles edge to edge, no bars, no crop. Tall
   portraits elsewhere render as narrow tall tiles with heads and feet intact.
6. All tiles share a common top/bottom edge; row height unchanged from before (380px).
7. In DevTools console on `#gallery`:

   ```js
   [...document.querySelectorAll('#gallery [data-gallery-card]')].map(b => {
     const im = b.querySelector('img'), r = b.getBoundingClientRect()
     return { src: im.currentSrc.split('/').pop(),
              tile: +(r.width / r.height).toFixed(2),
              img: +(im.naturalWidth / im.naturalHeight).toFixed(2) }
   })
   ```

   Every row's `tile` must equal its `img` ratio, except the nine clamped banners (where
   `tile` reads the clamp's own ratio, lower than `img`).
8. Auto-scroll: watch several unattended 3-second ticks. Each step lands a tile flush at
   the left edge — never mid-tile — and wraps to the start after the last one. Hover
   pauses it (existing `mouseenter`/`focusin` handlers, untouched).
9. Switch tabs repeatedly: track resets to `scrollLeft = 0` on filter change (existing
   effect, untouched); the step-timer effect re-binds on `filtered`.
10. Narrow viewport (~390px): one uniform square tile per screen, whole image shown, snap
    still works, no horizontal page scroll.

## Deferred

- **Nine tiles (ratio > 1.895 at height 380px) still show letterbox bars inside the 720px
  clamp** rather than a fully bar-free layout. Removing the clamp entirely would let
  `Logo2019` (3.48) render as a 1322px-wide tile, breaking the carousel's row rhythm on
  desktop. `Reopen when`: human call — if a wider clamp or a different treatment for
  extreme banners (e.g. a distinct "wide-banner" style) is wanted, that's a design
  decision, not a bug.
- **No automated check ties the Outcome ledger metric to CI.** Verification §7 is a manual
  DevTools script, run by hand. `Reopen when`: human call — if this component gets visual
  regression testing (e.g. Playwright) added generally, fold this check in then; not
  worth a bespoke harness for one component today.
