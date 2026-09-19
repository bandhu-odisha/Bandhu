# Consistent navbar brand (logo + "Bandhu") across the site

Status: done (2026-09-19)

## Problem

The Bandhu brand is drawn three different ways, so the logo jumps around between pages:

| Page(s) | Where the brand is today (measured at 1440px with chrome-devtools-axi) |
| --- | --- |
| Inner pages (`templates/snippets/navbar_landing.html`, used by `templates/base.html` and `accounts/templates/accounts_base.html`): /sanskar/, /swaraj/, /swabalamban/, /anandakendra/, /bandhughar/, /people/, /odisha-satabdi-sevavrata/, /classic/ | Logo only, 86x86 at (36,9); 63x63 at phone width. No "Bandhu" word. |
| Auth pages (`templates/snippets/navbar_auth.html`, used by `templates/registration/login.html`, `accounts/templates/signup.html`) | Logo only, 59x59 at (18,12). |
| Home `/` (React: `frontend/src/components/Navbar.jsx`, `Hero.jsx`) | No logo in the navbar at all. Navbar starts with the Updates button. The logo + big "Bandhu" h2 sit inside the hero slide (`Hero.jsx` ~lines 155-172, the `logoUrl` row, and its duplicate in the other layout branch if any). |

## Decisions (made by the user)

1. One brand lockup — logo image + the word "Bandhu" to its right — at the top-left of the navbar on **every** page (home, inner pages, auth pages).
2. **Remove** the logo + "Bandhu" h2 row from the home hero slide. The hero keeps its slide title (h1), subtitle and photo.
3. On home, the **Updates button sits right after the brand** (brand first, then Updates, nav links stay centered, Login/Logout stays right).

## Changes

1. Inner pages — `templates/snippets/navbar_landing.html`: inside `a.navbar-brand.navbar-brand-emblem`, add a text span "Bandhu" next to the `img.navbar-logo`. Style it in `css/custom.css` (and the identical copy `static/css/custom.css` — both dirs are served; keep them byte-identical). An unused `.navbar .navbar-brand .navbar-title` rule already exists (white text, meant for a dark bar) — reuse/rename it rather than adding a parallel rule; color must be the brand teal used for headings (e.g. `#005E66` / `var(--brand-primary)`), heavy weight, Inter. The emblem link currently has `line-height: 0` and `display:inline-block` — switch to an inline-flex row with the logo and word vertically centered and a small gap.
2. Auth pages — `templates/snippets/navbar_auth.html`: same lockup (logo + "Bandhu"), styled in `css/accounts-auth-landing.css` (+ `static/css/` copy) so size/position match the inner pages as closely as the auth header allows.
3. Home — `frontend/src/components/Navbar.jsx` (~line 545-600): render the brand lockup (link to `/`, logo from `data.logo_url` with the same fallback the hero used, plus "Bandhu") as the first item, then `<CurrentUpdates data={data} inline />`. Match the inner-page size: logo ~86px tall on desktop, ~63px on phone widths, word "Bandhu" in brand teal, black/heavy weight.
4. Home — `frontend/src/components/Hero.jsx`: delete the logo + "Bandhu" h2 row (and the now-unused `logoUrl` variable if nothing else uses it). Keep everything else in the slide.
5. Rebuild the React bundle (`cd frontend && npm run build`) — output in `static/frontend/assets/` is committed.
6. Cache-busting: bump `?v=` on every edited stylesheet/bundle reference in templates (`templates/landing_react.html` index.js/index.css currently `?v=312`; `custom.css` `?v=308` in `templates/base.html` and `accounts/templates/accounts_base.html`; `accounts-auth-landing.css` `?v=289` wherever referenced). Keep every reference to the same file on the same number.

## Constraints

- Django 2.2 templates; `.gitignore` ignores `*.html` but these templates are already tracked (no `git add -f` needed unless a new template is created — avoid creating one).
- Do not change nav links, menus, the mobile menu behaviour, or anything outside the brand/Updates placement.
- No `print()`; no new dependencies.
- Keep the logo image asset (`static/img/bandhu-logo-navbar.webp`) as is.

## Verification

- `python manage.py test` → `Ran 760 tests ... OK (expected failures=10)` (count must be exactly 760 unless a test is deliberately added; if added, state the new count).
- In chrome-devtools-axi at 1440x900 and at phone width (the browser's minimum is ~500px): on `/`, `/sanskar/`, `/anandakendra/`, `/people/`, `/accounts/login/` the navbar shows the logo with the word "Bandhu" to its right; the logo's left/top and size match across `/` and the inner pages (within a few px); the home hero no longer shows the logo/"Bandhu" row; Updates button sits right after the brand on home. Take screenshots of `/` and `/sanskar/` at both widths.
- No horizontal page scroll at phone width on those pages (`document.documentElement.scrollWidth <= innerWidth`).

## Checklist

- [x] Inner-page navbar lockup
- [x] Auth navbar lockup
- [x] Home navbar lockup + Updates after brand
- [x] Hero logo row removed
- [x] Bundle rebuilt, ?v bumped
- [x] Tests 760 OK, browser checks done
- [x] Reviewed (cr)
- [x] Committed

## Outcome

- Brand lockup (logo + "Bandhu") at the same place on every page: logo left/top 36px, 9px; 86px logo + 24px word on desktop, 63px + 18px below 640px; 8px gap. All in fixed px so the differing root font-sizes (React landing vs Django pages) don't shift it.
- Measured with chrome-devtools-axi (emulated viewports) on /, /sanskar/, /anandakendra/, /people/, /accounts/login/, /accounts/signup/ at 360, 1440, 1920 and 2560px: identical at every width.
- Home: hero logo + "Bandhu" row removed; Updates button follows the brand and is icon-only below 640px so the row fits at 360px.
- Review cycle 2 raised two items. (1) "inner-page offset is rem-based and drifts" — measured, does not reproduce (Django pages resolve root to 18px at all tested widths), left as is. (2) auth header capped at 80rem and centred, logo at 276px/596px at 1920/2560 — confirmed and fixed by dropping the cap.
- Tests: Ran 760 tests, OK (expected failures=10).
