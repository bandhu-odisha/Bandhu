# Ankurayan home: image tiles keep each photo's natural shape

## Context
On `/ankurayan/`, every photo is cropped:
- **Hero card** (top left) is forced square (`aspect-ratio: 1 / 1` in `css/ankurayan.css:152`, plus the mobile rule at `:196`). Its 960×672 photo loses its sides.
- **"Running Ankurayans" cards**: 17 photos with ratios from 0.75 (portrait) to 3.48 (wide banner). They all go into a 370×270 `object-fit: cover` box, because of the site-wide `.glide .card img { height: 270px }` rule (`css/custom.css:1171`) and Glide's equal-width slides.

The user picked **option 1, "Same as Gallery"**: copy the fix from commit a0472897 (React Gallery). Every tile has the same height, and its width follows the photo, clamped to 200–720px. On desktop, Glide is replaced by a side-scrolling strip. Phones keep one card per screen.
History check: the square hero comes from the big redesign merge 24c49db (#97). That commit gives no reason for the square, so changing it does not undo any stated intent. The carousel is from 2020 (758f5c7).

## Scope
Home page only (`body.ankurayan-page`). The detail page (`ankurayan_detail.html`, `.ankurayan-detail` rules) and other pages that use `.glide .card img` stay as they are.

## Changes

### 1. `applications/ankurayan/templates/ankurayan.html`
- **Hero:** no markup change (the `<img>` already has width/height attributes).
- **Cards:** replace the Glide markup (`.glide.ankurayans` / `__track` / `__slides` / `__slide` / bullets) with:
  - `div.ankurayan-strip` (scroller), then `ul.ankurayan-strip-row`, then `li.ankurayan-strip-item`, then the existing `.card.page-card.ankurayan-year-card`.
  - Set each item's width from its photo: `{% widthratio ankur_logo_img.width ankur_logo_img.height 270 as tile_w %}`, then `<li style="--tile-w: {{ tile_w }}px">`. CSS clamps it to 200–720px. The width goes on the `li`, not on the image box. Otherwise the long unwrapped theme text would decide the card width.
  - When there is no responsive rendition, there are no dimensions, so use a fixed fallback (`--tile-w` defaults to 360px in CSS).
  - Image gets `object-fit: contain` (whole photo shown, never cropped, the same as Gallery). `sizes="(max-width: 767px) 92vw, {{ tile_w }}px"` uses each tile's real width. A flat 720px would download bigger images than needed, which is what a0472897 fixed.
  - Wide banners hit the 720px cap. They show with thin tint bands above and below (see the 2019 tile in the mock).
  - Keep the prev/next arrow buttons (same `slider_arrow` classes for the same look). Drop the 17 bullets: they don't fit a variable-width strip. Phones swipe.
- Remove the page-local `<style>` rules that target `#ankurayans .glide__slide` (lines 52–78). Move the theme line clamp onto the new class names.
- **Script:** replace `new Glide('.ankurayans', …)` with about 25 lines of plain JS, ported from Gallery's auto-scroll:
  - Every 2s, advance to the next item's real `offsetLeft`, clamped to `maxScroll`. Wrap to 0 at the end. The progress-check clamp from a0472897 stops the scroll getting stuck at 0 or at max.
  - Pause on hover/focus. Don't start under `prefers-reduced-motion`.
  - Arrows move by one item (the next or previous offset).

### 2. `css/ankurayan.css` (and the identical tracked copy `static/css/ankurayan.css`)
- Hero, scoped to `body.ankurayan-page`: `.pillar-overlay-card--image { aspect-ratio: auto; }` and `img { height: auto; }`. Do this at both desktop and ≤768px, so the hero follows its photo.
- Strip:
  - `.ankurayan-strip { overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; }`, with the row as `display:flex; gap:30px`.
  - Desktop (≥768px):
    - `li { flex: 0 0 auto; width: clamp(200px, var(--tile-w, 360px), 720px); }`
    - card `min-width: 0` so text wraps.
    - img `height: 270px; width: 100%; object-fit: contain; background: #e6f0f1`.
    - Titles line up because every image is the same height.
    - The `max-width: 24rem` rule at `css/bandhu.css:190` only targets `.glide__slide .card`, so it stops applying once the Glide markup is gone. Same for `.glide .card img` in `custom.css`.
  - Phone (<768px): item `min-width: 100%`, media `width: 100%; height: 225px` (`contain` + tint). This mirrors Gallery, which kept phones uniform.
- Update the `.ankurayan-list-page #ankurayans … glide…` selectors (about lines 283–300) to the new class names. Leave the `.ankurayan-detail` rules alone.

### 3. `templates/…` cache-bust
Bump `css/ankurayan.css?v=14` to `?v=15` in `ankurayan.html`.

## Verification
- `python manage.py test applications.ankurayan`, then the full run. It must report `Ran 761 tests … OK (expected failures=10)`. Log goes to a file.
- `runserver`. Then check with chrome-devtools-axi on `/ankurayan/` at 1280px and at 390px (read `innerWidth` back after resizing):
  - The hero box ratio matches 960/672.
  - Every card image box is 270px tall, and its width ≈ clamp(200, 270×ratio, 720). Check the 0.75 and 3.48 photos.
  - Auto-scroll advances, wraps at the end, and pauses on hover. Arrows work.
  - Phone: one card per screen, swipe works, no horizontal page overflow.
  - Screenshots of desktop + phone sent to the user.
- Build via /dev-workflow (implement, review, fix, commit locally, no push).
