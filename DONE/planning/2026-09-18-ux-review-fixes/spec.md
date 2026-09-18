# UX review fixes (from live audit of bandhuodisha.in, 2026-09-18)

Branch `ux-review-fixes`, baseline `c5e62c5`. Commit locally, never push.
Audience: Android phones, 360px wide, slow 4G, India. Mobile first.
Out of scope: inner-page menu parity, the two 500 pages, empty `staff-experiences.html`, `/classic/`, program content.

## Ground rules
- Python 3.8 venv at `./venv`; Django 2.2, Pillow 6, easy-thumbnails 2.6 are pinned. Add no dependency.
- `css/custom.css` and `static/css/custom.css` are identical tracked copies (same for `ankurayan.css`). `static/` is first in `STATICFILES_DIRS`, so it wins. Edit BOTH, keep them byte-identical (`diff -q`).
- Templates reference CSS with `?v=NNN`; bump it on every changed CSS file. New templates need `git add -f`.
- No `print()` in app code. On-page admin checks use `{% if user|is_admin %}`.
- Full suite must end `Ran 742 tests ... OK (expected failures=10)`; if tests are added, the number rises and `CLAUDE.md` (two places: the "Check the test count" paragraph) is bumped to match. Run `python manage.py test 2>err.log >/dev/null; tail -5 err.log`.

## Deliverables — Track A (Django templates, CSS, Python)

A1. **Serve resized WebP photos on inner pages (review item 1).** Do NOT resize in `save()` and do NOT rewrite originals — the repo already has the mechanism: `bandhuapp/helpers.py::responsive_image(field)` (easy-thumbnails aliases `landing_480/960/1600`, WebP, never raises, returns `{src, srcset, width, height}` or `None`). Add one template tag/filter in `bandhuapp/templatetags/` that wraps it, and use it for content photos in: people list + staff profile, publications list, `templates/initiative_program/*.html`, ankurayan, anandakendra, ashram (bandhughar), charitywork, sevavrata/patriotism/prasantaraktadan index+detail, pillar pages not already covered. Fallback when it returns `None`: the original `.url`, exactly as today. Add `sizes` suited to the layout (e.g. `(max-width: 600px) 92vw, 600px`). Lightbox/zoom links keep pointing at the original file.
A2. **Warm-up command covers the new pages.** `bandhuapp/management/commands/warm_landing_thumbnails.py` currently warms home-page fields only. Extend it (or add a sibling command reusing its loop) to warm every image field rendered through the A1 tag, so production never generates thumbnails inside a visitor request. Update README line ~201 deploy step.
A3. **Lazy loading (item 2).** Every below-the-fold content `<img>` in the templates above gets `loading="lazy"` plus `width`/`height` (from the A1 data when available). The first/hero image on a page stays eager.
A4. **Floating "Be a Bandhu" button (item 4).** `templates/base.html:124`, class `.bandhu-fab-cta`. At `max-width: 600px` it becomes a slim full-width bottom bar (about 48px tall), and `body` gets matching `padding-bottom` so it never covers the footer or content.
A5. **Ankurayan year links (item 5).** `.ankurayan-years-track` in `ankurayan.css` + `applications/ankurayan/templates/ankurayan.html`: remove the auto-scroll animation and any duplicated link set that existed only to loop the marquee; render a static `flex-wrap` row; each link min 44px tall with padding.
A6. **Banner + People density (item 7).** Inner-page title banner: at `max-width: 600px` cut its height to roughly a third of today's. People list: two cards per row at 360px (smaller avatar, name, role, keep "View Profile" tappable at 44px).
A7. **WhatsApp + sign-up sentence (item 9).** Footer in `templates/base.html` (and the auth/footer partials if separate): add a WhatsApp link `https://wa.me/919437439371` next to the phone number, text "WhatsApp", `rel="noopener"`, 44px tap height. Under the "Sign Up" heading on the signup page and the signup modal add exactly: "Do you like to work for a social cause? You are welcome to join our team as a volunteer."
A8. **Clean-ups (item 11).**
  - `<img src="">` rendered on `/people/<id>/`, `/swaraj/`, `/swabalamban/`: find the template branch that emits an img when the field is empty and guard it with `{% if field %}`.
  - `<label for>` pointing at missing ids in the hidden on-page admin forms (counts seen live: ankurayan 8-10, anandakendra 6-11, bandhughar detail 14, other_activities 4-7). Make each `for` match a real input `id`, or drop `for` and wrap the input.
  - Ankurayan: 16 links with no accessible name — add `aria-label` or visible text.
  - Inner pages lacking an `<h1>`: make the banner title the `h1` (one per page). Keep visual size via the existing class.
  - Swabalamban: 10 `href="#"` links — give them real targets or turn them into `<button type="button">`/plain text.
  - `sitemap.xml`: use `django.contrib.sitemaps` (stdlib of Django, already installed). Static public routes + pillar pages + initiative index pages + published detail pages + publications. Add `Sitemap:` line to the robots.txt source if it is served from the repo. `django.contrib.sites` is NOT required if you pass absolute URLs via the request-aware `sitemap` view; check `INSTALLED_APPS` first and do not add a migration-bearing app unless unavoidable — report if it is.
A9. **Tests.** Template tag (returns srcset for a real image via `TempMediaMixin`, falls back to `.url` for missing file); warm command touches a non-landing field; sitemap returns 200 + contains `/people/`; one render test per cleaned template asserting no `src=""` and an `<h1>`. Helpers: `bandhuapp/tests/support.py`. Isolate every media write with `TempMediaMixin`.

## Deliverables — Track B (React home page)

B1. **Header tap targets (item 10).** Home header in `frontend/src` (find the Login / Updates buttons and carousel dots): Login and Updates min-height 44px, label text >= 13px; carousel dots get a 44px hit area (padding or pseudo-element) without changing dot visuals.
B2. **Gallery alt text (item 11).** Home gallery tiles: 13 share the accessible name "Ankurayan 2021". Make names unique, e.g. "Ankurayan 2021, photo 3 of 13", computed in the component from index within same-title group. No backend change.
B3. **WhatsApp link** in the home footer/contact block: same URL and label as A7.
B4. Rebuild: `cd frontend && npm install && npm run build` (writes `static/frontend/assets/index.{js,css}`, committed). Bump `?v=` for both assets in `templates/landing_react.html`.

Track B must not touch `templates/base.html`, any `*.css` outside `frontend/`, or any Python. Track A must not touch `frontend/`, `static/frontend/`, or `templates/landing_react.html`.

## Verification (Phase 4)
Run `python manage.py runserver` on sqlite with local media, then with chrome-devtools-axi at `emulate --viewport "360x800x2.625,mobile,touch"` (restate all flags on every emulate call; read back `innerWidth` = 360):
- People / Ankurayan / Publications: `document.images` — count with `loading=lazy`, count whose `currentSrc` ends `.webp`; no `img[src=""]`; exactly one `h1`.
- `.bandhu-fab-cta` rect: full width, bottom 0; `getComputedStyle(body).paddingBottom` >= its height.
- Ankurayan year links: no CSS animation on the track (`getComputedStyle(...).animationName === 'none'`), each link height >= 44, all within 0..360 horizontally.
- Home: Login/Updates height >= 44; gallery button names unique; WhatsApp link href exact.
- `/sitemap.xml` 200.

## Added by user during the run (2026-09-18)
A10. **Shrink the shared placeholder hero photo.** `static/img/our_mission1.jpg` and its tracked twin `img/our_mission1.jpg` were 5.9 MB (3264x2176). It is the fallback hero on the blood-donation, patriotism, sevavrata, bandhughar, ankurayan and anandakendra index pages and is used by `frontend/src/components/{Hero,Mission}.jsx`. Re-saved in place at 1600x1067, JPEG q80 progressive = 373 KB. Same filename, no template change. The original stays in git history.
- Also: move this plan folder to `DONE/planning/` at Phase 5.
- Also: record the browser walk-through as a video for the user to review.

## Status — DONE 2026-09-18 (branch `ux-review-fixes`, not pushed)
Checklist: [x] A1 [x] A2 [x] A3 [x] A4 [x] A5 [x] A6 [x] A7 [x] A8 [x] A9 [x] A10 [x] B1 [x] B2 [x] B3 [x] B4

Tests: `Ran 760 tests ... OK (expected failures=10)` (742 baseline + 18 new).
Reviews: two fix cycles on the main diff, then approved. One more review on the phone-banner CSS fix found two Important points: cache-buster collisions (fixed — each changed CSS file now has one number above any value ever seen in git history) and Ankurayan pills applying on desktop too (confirmed intended, by screenshot).
Browser check: 19 routes at 360x800 (no sideways scroll, one h1 each, no `src=""`, no bad labels, no duplicate label-target ids) plus 5 at 1366px. Walk-through video: `/tmp/bandhu-e2e/bandhu-ux-walkthrough.mp4`.

### Deviations from the original wording
- A1: reused `responsive_image()` and the easy-thumbnails WebP aliases instead of resizing in `save()`. Originals are never rewritten, so production media needs no clean-up. New uploads are still stored full size (disk only; visitors get thumbnails).
- A4 fix: `position: sticky` was not usable (`html`/`body` carry `overflow-x: clip`), so `<body>` gets `has-fab-cta` under the same condition that renders the button.
- A6 grew: the 150px phone banner needed the pull-up negative margins zeroed at `max-width: 600px` in 7 CSS files plus `pillar_page.html`, and banner titles re-anchored. Desktop rules untouched.
- A5: pills show the year only; the full name is kept in `aria-label`.
- A8 sitemap: `django.contrib.sitemaps` added to `INSTALLED_APPS` (no models, no migration). `django.contrib.sites` NOT added. The repo has no robots.txt, so no `Sitemap:` line was added.

### Deferred (found, not fixed) — reopen when someone touches these files
- `ankurayan_detail.html`: duplicate ids `exampleModalLongTitle` (modal titles) and `mission-carousel`. Not label targets, admin-only.
- Responsive images not applied to photos inside click-to-open modals, admin approval grids, staff "share experience" galleries, guest avatars.
- Desktop floating "Be a Bandhu" pill overlaps card text on `/publications/` at 1366px (pre-existing; item 4 was phone-only).
- Long banner titles truncate on phones (`white-space: nowrap`), e.g. Bandhughar detail.
- Dead CSS left by this change: `.ankurayan-year-sep` and `@keyframes ankurayanYearsScroll` remnants; the shadowed flex-end block at `css/custom.css` ~797-806; per-file margin overrides shadowed by `initiative-program-year.css`. One `--inner-banner-overlap` variable would replace them.
- `accounts_base.html` links `custom.css` with no `?v=`.
- `templates/landing_page.html` (`/classic/`) still has `id="inputGroupFile04"`; that page was out of scope.
- Review items not taken: 3 (inner-page menu parity), 6 (two 500 pages, empty `staff-experiences.html`, `/anandakendra/detail/slug/` placeholder), 8 (`/classic/` redirect), 6b content for the blood-donation and patriotism pages (only their shared placeholder photo was shrunk).
