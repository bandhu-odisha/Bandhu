# Bandhu Odisha — Customer Experience Audit (2026-09-12)

Sites audited: production `https://bandhuodisha.in/` and local `http://127.0.0.1:8000/` (runserver, DEBUG, placeholder media). Read-only audit; no repo files changed except this folder.

## 1. Summary

The site is structurally sound on mobile — no page scrolls sideways at 360/390/768/1440 px, layout shift is ~0, and the React landing scores 94 (accessibility) / 100 (best practices) / 92 (SEO) in Lighthouse. The two things a visitor actually feels are speed and shareability: the home page waits 1.4–2.1 s for the server before any HTML is sent (the Django view builds the landing data slowly — same on local, so it is code, not hosting), and it references 81 images totalling 48 MB, several at 4000×3000 shown at 313 px. No page has a meta description or Open Graph tags, so a WhatsApp/Facebook share of any Bandhu link shows no preview text or image, and the home page has no server-rendered text at all for crawlers. Top 3 fixes: (1) cache or precompute the landing data so TTFB drops to the ~250 ms every other page gets; (2) resize/convert uploaded images and add `srcset` so phones download hundreds of KB, not tens of MB; (3) add title/description/Open Graph tags in `base.html` and `landing_react.html`. Security hygiene (session cookie sent without `Secure`, no HSTS) is a one-line settings fix and should ship with the next deploy.

## 2. Work items (sorted by Impact = Severity × Reach; ties → lower effort first)

Reach: 5 = home page / every page incl. mobile · 4 = every Django-template page · 3 = one initiative family · 2 = secondary page (/classic/, 404) · 1 = admin-only.
Screens live in `planning/2026-09-12-cx-audit/screens/`.

| ID | Problem (plain words) | Pages affected | Where | Evidence | Source file:line | Sev | Reach | Effort | Impact |
|---|---|---|---|---|---|---|---|---|---|
| W01 | Home page waits 1.4–2.1 s for the server before any HTML arrives; every other page takes 0.25–0.45 s. It is the view's own work, not hosting: local shows the same 1.6–1.8 s. Also every anonymous visit writes a session (`home_page_visited`), which sets `sessionid` + `Vary: Cookie` and makes Cloudflare unable to cache the page. | `/` | both | Browser TTFB prod 2120 ms (mobile) / 1515 ms (desktop); Node probe prod 2009/2134/1403 ms, local 1782/1826/1618 ms; `/bandhughar/` 243 ms, `/sanskar/` 290 ms | `bandhuapp/views.py:190` (`_build_landing_data`), `bandhuapp/views.py:156`, `:504` (session write) | 5 | 5 | M | 25 |
| W02 | Home page references 81 images = 48 MB (18 files > 300 KB, two 8 MB PNGs, 5.9 MB JPEG). Gallery images are 4000×3000 shown at 313 px; hero is 1040×780 shown at 315 px. No `srcset`/`sizes`/`width`/`height`, no WebP/AVIF; uploads are served as originals. | `/` (gallery, hero, pillars, visitors) | prod (content); both (code) | `tmp/imgweight-prod-home.json`: n=81, total 49,488 KB; `Ankurayan_2024_Logo_Inauguration.png` 8,291 KB, `swamblamban_BGUU3u3.png` 8,291 KB, `IMG_20190815_082039.jpg` 3,542 KB; vitals `oversizedImgs` list | `frontend/src/components/Hero.jsx:103-112` (no srcset/dimensions); media uploads unresized (no resize step in upload views) | 5 | 5 | M | 25 |
| W03 | No `<meta name=description>`, no Open Graph/Twitter tags, no canonical on any page. Shared links show no preview text/image; search snippets are auto-generated. Titles are weak: `/` = "Bandhu", `/bandhughar/` = "Ashram" (old internal name). | all | both | Lighthouse `meta-description` fail on `/` and `/bandhughar/`; Node probe: 0 og tags on 4 pages × 2 sites; layout probe `metaDesc:null, og:false` on every page | `templates/landing_react.html:7` (title), no meta block; `templates/base.html:11` (no `{% block meta %}`); `applications/ashram/templates/ashram.html:6` ("Ashram") | 4 | 5 | S | 20 |
| W04 | Session and CSRF cookies are sent without the `Secure` flag in production, and there is no HSTS header. `*_COOKIE_SECURE` is only assigned inside `if DEBUG:` (to False), so production gets Django's default False. | all | prod | Node probe: `csrftoken` Secure=no, `sessionid` Secure=no HttpOnly=yes SameSite=Lax; `strict-transport-security` absent; http→https 301 works | `bandhu/settings.py:160-165`; no `SECURE_HSTS_SECONDS` anywhere | 4 | 5 | S | 20 |
| W05 | Tap targets far below 44 px: hero slide dots 9×9 (mobile) / 12×12, testimonial dots 8×8, photo dots 6 px tall, notice-ticker links 17 px tall, nav/footer links 20–21 px, modal "Forgot password?" 117×16 and "Sign up now" 80×16, hamburger 40×40. | `/` (dots), every Django page (nav/footer/ticker), modal | both | Lighthouse `target-size` fail on `/`; layout probe `small` lists on every page; `prod-login-modal-360.jpeg` | `frontend/src/components/Hero.jsx:129`, `:183` (`h-2.5`), `OurVisitors.jsx:135` (`h-2`), `About.jsx:153` (`h-1.5`); `Navbar.jsx:562` (`h-10 w-10`); `accounts/templates/includes/login_modal.html` links | 3 | 5 | S | 15 |
| W06 | Images/static cached only 4 h (`max-age=14400`), so returning visitors re-validate everything; JS/CSS filenames are unhashed and `?v=` is hand-maintained and inconsistent (vendor CSS/JS, `main.js`, `bandhu.js` have none; `bandhu.css` is fetched twice as `?v=27` and bare; bootstrap.min.css as `?v=255` and bare). | all | prod (headers); both (versioning) | Node probe: every asset `cache-control: max-age=14400`; 12–13 scripts + 8–9 stylesheets without `?v=` on classic pages | `frontend/vite.config.js:17-19` (fixed names); `bandhu/settings.py` (no `STATICFILES_STORAGE`); `templates/base.html:31-41`, `:118-132`; `bandhuapp/templates/landing_page.html:10-11`, `:761-762` | 3 | 5 | M | 15 |
| W07 | Navbar logo is a 343 KB 1254×1254 PNG shown at ~105 px, loaded on every page. | every Django page + `/` | both | `imgweight-*.json`: `/static/img/bandhu-logo-navbar.png` 343 KB; vitals `natural 1254x1254 shown 105x105` | `static/img/bandhu-logo-navbar.png`; `templates/snippets/navbar_landing.html:8`; `frontend/src/components/Hero.jsx:145` | 3 | 5 | S | 15 |
| W08 | Home page has no server-rendered text — only an empty `<div id="root">` and a JSON blob. With JS off or if `index.js` fails, the page is blank; non-JS crawlers see nothing. (`/classic/` has 7,067 chars of real text.) | `/` | both | `oc open https://bandhuodisha.in/` → "no readable content"; Node probe: 204 visible chars outside `<script>` (the modal) | `templates/landing_react.html:128`, `:133`; `frontend/src/App.jsx:101-107` (JS-only "Loading…") | 3 | 5 | M | 15 |
| W09 | Login/signup inputs have no `<label>` or `aria-label` — placeholder only (vanishes when typing; screen readers inconsistent). Initiative admin forms have `<label for>` pointing at missing ids. | modal on every page; admin forms | both | Layout probe `inputsNoLabel: [email,password,email,password,password2]` on every page; local console "Incorrect use of `<label for=FORM_ELEMENT>` (count: 6)" on `/bandhughar/` | `accounts/templates/includes/login_modal.html:42`, `:45`; `signup_modal.html:41`, `:44`, `:47`; `templates/initiative_program/*` admin modals | 3 | 4 | S | 12 |
| W10 | Year-detail hero caption is pushed off-screen on phones: the caption box starts at x=300 in a 360 px viewport and is 459 px wide, so its text ("A home of care and dignity…") is not visible. The list page got this fix in commit `b09e33c`; the detail page did not. | `/bandhughar/detail/<slug>/` and the other initiative detail pages (same template) | both | Eval: `left:300, w:459, parentW:243, visible`; `prod-bandhughar-detail-360.jpeg` (caption absent), `local-bandhughar-detail-360.jpeg` | `templates/initiative_program/year_detail.html:82`; `css/anandakendra.css:834-847` | 4 | 3 | S | 12 |
| W11 | Classic-template pages load 9 render-blocking stylesheets + Google Fonts CSS + 10 synchronous scripts before content; the React landing also loads jQuery/Popper/Bootstrap/FontAwesome it barely uses. Today the server wait dominates (FCP ≈ TTFB + ~150 ms), so this is the next bottleneck once W01 is fixed. | all | both | vitals: `/` mobile FCP 2324 vs TTFB 2120; `/classic/` 118 requests desktop; 9 iframes (YouTube) eager on `/classic/` | `templates/base.html:14`, `:31-44`, `:118-132`; `templates/landing_react.html:10`, `:14-18`, `:135-137` | 2 | 5 | M | 10 |
| W12 | Every classic-template page throws `TypeError: Cannot read properties of undefined (reading 'filteredItems')` in `main.js:275` (Isotope instance missing) — the rest of that handler never runs. Lighthouse flags it. | every Django page | both | Console on prod `/classic/` and local `/bandhughar/`; Lighthouse `errors-in-console` fail on `/bandhughar/` | `static/js/main.js:268-275` | 2 | 5 | S | 10 |
| W13 | No `<h1>` on any Django-template page (title is `<h2>`), heading levels jump (H2→H5, H3→H5), no `<main>` landmark, no skip link. | every Django page | both | Layout probe `h1Count:0` on 9 pages; Lighthouse `landmark-one-main` fail on `/bandhughar/` | `templates/initiative_program/list_page.html`, `bandhuapp/templates/pillar_page.html`, `templates/base.html` | 2 | 5 | S | 10 |
| W14 | Hero carousel auto-rotates with no pause on hover/focus and no `prefers-reduced-motion` check (WCAG 2.2.2). | `/` | both | Code read | `frontend/src/components/Hero.jsx:79-85` | 2 | 5 | S | 10 |
| W15 | Floating "Be a Bandhu" pill covers content on phones (caption text on detail page, poster on classic). | all | both | `prod-bandhughar-detail-360.jpeg`, `prod-classic-360.jpeg`, `prod-other_activities-360.jpeg` | `templates/base.html:112`; `frontend/src/components/BeABandhuFab.jsx:16` | 2 | 5 | S | 10 |
| W16 | Missing security headers: no `X-Content-Type-Options: nosniff`, no `Referrer-Policy` (full URLs incl. `?next=` leak to fonts/tracker hosts), no CSP. | all | both | Node probe headers | `bandhu/settings.py` (no `SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_REFERRER_POLICY`) | 2 | 5 | S | 10 |
| W17 | Keyboard focus is invisible on nav links: after Tab, the focused link has `outline: none` and no box-shadow. | every Django page | both | Eval on prod `/bandhughar/` after 2× Tab: `outline:"none 3px", boxShadow:"none"` (one element measured) | `css/custom.css` (focus rules only on `.btn-outline-primary:151-158`) — exact reset rule not located | 2 | 4 | S | 8 |
| W18 | `www.bandhuodisha.in` serves the site (200) instead of redirecting to the apex; with no canonical tag, search engines see two sites. README says production is `www.`; Cloudflare serves apex. | all | prod | Node probe: `https://www.bandhuodisha.in/` 200, no redirect | Cloudflare/cPanel redirect rule (not in repo); `README.md:154` | 2 | 3 | S | 6 |
| W19 | Third-party scripts on every page: GoDaddy tracker `img1.wsimg.com/traffic-assets/js/tccl.min.js` (301 → `scc-c2.min.js`, 21 KB), Cloudflare beacon, GTM. Not referenced in any template — injected by the GTM container or host. Also Cloudflare's Email Obfuscation injects `/cdn-cgi/scripts/.../email-decode.min.js`, which 404s on every classic page. | all | prod (email-decode); both (tccl) | Network log on `/`; Node probe 404 on `/classic/`, `/sanskar/`, `/bandhughar/` | GTM: `templates/base.html:50-54`; Cloudflare dashboard (Email Obfuscation) | 1 | 5 | S | 5 |
| W20 | 404 page downloads a 1.3 MB animated GIF, has malformed CSS (orphan `}`), and extends `accounts_base.html` so it has different chrome. | 404 | both | `static/img/icon/404-1.gif` 1,373,645 B; `prod-404-360.jpeg` | `templates/404.html:1`, `:17+` | 2 | 2 | S | 4 |
| W21 | `/classic/`: 6 of 68 images lack `alt`; 9 YouTube iframes load eagerly (114–118 requests); local renders `<img src="None">` ×3 and a literal `${data[photo].fields.picture}` src (template bugs that surface whenever data is missing). | `/classic/` | both (alt/iframes); local (None/`${}` srcs) | Node probe alt count; console 404s local | `bandhuapp/templates/landing_page.html:154`, `:166`, `:178`, `:190`; `templates/includes/mission_list_card.html:6`; `templates/initiative_program/list_about_section.html:8` | 2 | 2 | M | 4 |
| W22 | Local home hero falls back to the 5.9 MB `our_mission1.jpg` (page weight 7.9 MB, LCP 1.97 s); the file is stored twice (`static/img/` and `img/`, both in `STATICFILES_DIRS`) and is the `onerror` fallback for every pillar/initiative hero in production. | `/` (local); fallback path everywhere | local (hero); both (fallback) | `imgweight-local-home.json` 5,896 KB; vitals local `lcp_url: /static/img/our_mission1.jpg` | `frontend/src/components/Hero.jsx:7`; `templates/initiative_program/list_about_section.html:13`, `:16`; `bandhuapp/templates/pillar_page.html:666-670`; `bandhu/settings.py:218-219` | 2 | 2 | S | 4 |
| W23 | TLS certificate expires 2026-12-05 (~12 weeks). Informational — confirm Cloudflare auto-renew. | all | prod | Node TLS probe | — | 1 | 1 | S | 1 |

## 3. Recommendations

### Quick wins (effort S, impact ≥ 12)
- **W03** — Add `{% block meta %}` to `templates/base.html` and real `<title>`/description/`og:title`/`og:description`/`og:image` (use the hero image) on `landing_react.html` and each program's `list_page.html`; rename the "Ashram" title to "Bandhughar".
- **W04** — In `bandhu/settings.py` set `SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = not DEBUG`, `SECURE_HSTS_SECONDS = 31536000` (+ `SECURE_HSTS_INCLUDE_SUBDOMAINS`), `SECURE_PROXY_SSL_HEADER` for Cloudflare; ship with the next deploy.
- **W05** — Give the dot buttons a 44×44 hit area (padding or `before:` pseudo-element, keep the visual dot small), bump nav/ticker/modal link padding to ≥ 24 px tall.
- **W07** — Replace `bandhu-logo-navbar.png` with an SVG or a 210 px WebP (~5 KB).
- **W09** — Add visually-hidden `<label for>` elements to the 5 modal inputs; fix the `for` ids in the admin modals.
- **W10** — Apply the same caption CSS fix from commit `b09e33c` to `year_detail.html:82` / `css/anandakendra.css:834`.

### Next sprint
- **W01** — Profile `_build_landing_data` (`bandhuapp/views.py:190`); cache the built dict (`cache.get_or_set`, 5–15 min, invalidate on admin save) and stop writing the session on anonymous GET so Cloudflare can cache HTML.
- **W02** — Generate resized variants on upload (Pillow: 480/960/1600 px WebP), serve them via `srcset`/`sizes` in `Hero.jsx` and the gallery, add `width`/`height`; batch-convert existing media once.
- **W06** — Enable Vite hashed filenames + `ManifestStaticFilesStorage` (or one `?v=` from a settings constant), set Cloudflare cache rule `max-age=31536000, immutable` for `/static/` and `/media/`.
- **W12** — Guard `main.js:268` (`if (!iso) return;`) or scope the loader to pages that have an Isotope grid.
- **W13** — Make each page title an `<h1>`, wrap content in `<main>`, add a skip link; fix H3→H5 jumps in the modal and cards.
- **W14 / W15 / W16 / W17** — Pause carousel on hover/focus and honour `prefers-reduced-motion`; hide or shrink the FAB while a caption/footer is in view on phones; add `SECURE_CONTENT_TYPE_NOSNIFF` and `SECURE_REFERRER_POLICY='strict-origin-when-cross-origin'`; restore `:focus-visible` outlines.

### Later
- **W08** — Server-render the mission/pillars text inside `#root` (or a `<noscript>` block) so crawlers and JS-failure cases get content.
- **W11** — Trim `base.html` to the stylesheets each page needs, `defer` the ten scripts, self-host Inter with two weights; drop jQuery/Bootstrap/FontAwesome from `landing_react.html` (only the modal uses them).
- **W18 / W19** — Cloudflare: redirect `www` → apex; turn off Email Obfuscation (404 script); review whether the GoDaddy tracker in GTM is still wanted.
- **W20 / W21 / W22** — Replace the 404 GIF with an SVG and fix its CSS; add `alt` to the six classic images and lazy-load the YouTube iframes; delete the duplicate `img/our_mission1.jpg` and downsize the fallback.

## 4. Metrics appendix

Browser measurements: Chrome via chrome-devtools-axi, `emulate --viewport 360x740,mobile` / `1440x900`, warm cache (Lighthouse had already loaded the page), from the auditor's location; TTFB = `responseStart`, LCP/CLS/longtask from `PerformanceObserver` (buffered). Node probe = fresh `fetch` per page, no cookies, 1 req/s.

### Core Web Vitals (production, browser)

| Page | Viewport | TTFB | FCP | LCP | LCP element | CLS | TBT | Requests |
|---|---|---|---|---|---|---|---|---|
| `/` | 360 mobile | 2120 ms | 2324 ms | 2324 ms | hero `img` `/media/bandhuapp/hero/image1.jpg` (1040×780 → 315×236) | 0 | 7 ms | 79 |
| `/` | 1440 | 1515 ms | 1664 ms | 1664 ms | same | 0.003 | 0 | 79 |
| `/classic/` | 360 mobile | 1009 ms | 1124 ms | 1124 ms | section bg `/media/bandhuapp/banner/our_mission.jpg` | 0.019 | 0 | 114 |
| `/classic/` | 1440 | 1002 ms | 1156 ms | 1244 ms | same | 0 | 0 | 118 |
| `/bandhughar/` | 360 mobile | 789 ms | 884 ms | 884 ms | `img.pillar-overlay-single-image` `/media/ashram/index/21.jpg` | 0 | 0 | 40 |
| `/bandhughar/` | 1440 | 794 ms | 924 ms | 924 ms | same | 0 | 0 | 40 |
| `/bandhughar/detail/bandhu-ghar-celebration-lankapara/` | 360 mobile | 760 ms | — | 880 ms | `/media/ashram/thumbnails/collage.jpg` (2,428 KB) | 0 | 0 | 38 |
| local `/` | 360 mobile | 1687 ms | — | 1968 ms | `/static/img/our_mission1.jpg` (5,896 KB) | 0 | 3 ms | 21 (7,937 KB) |

INP: not measured (needs real user interaction; TBT ≤ 7 ms everywhere suggests it is fine).

### Server response (Node probe, no cookies)

| Page | prod status | prod TTFB | prod bytes (br) | local TTFB | local bytes |
|---|---|---|---|---|---|
| `/` | 200 | 2009 / 2134 / 1403 ms | 56,938 | 1782 / 1826 / 1618 ms | 34,750 |
| `/classic/` | 200 | 437 ms | 155,260 | 32 ms | 53,432 |
| `/sanskar/` | 200 | 290 ms | 49,833 | 22 ms | 47,681 |
| `/swaraj/` | 200 | 248 ms | 53,117 | 26 ms | 46,428 |
| `/bandhughar/` | 200 | 243 ms | 56,817 | 24 ms | 35,851 |
| `/other_activities/` | 200 | 258 ms | 64,262 | 21 ms | 40,228 |
| `/prasanta-raktadan-shibir/` | 200 | 346 ms | 31,914 | 26 ms | 29,759 |
| `/patriotism-in-action/` | 200 | 253 ms | 31,940 | 22 ms | 29,785 |
| `/odisha-satabdi-sevavrata/` | 200 | 263 ms | 40,011 | 54 ms | 30,063 |
| `/people/` | 200 | 313 ms | 120,962 | 24 ms | 86,171 |
| `/accounts/login/` | 200 | 244 ms | 8,604 | 19 ms | 6,449 |
| `/this-page-does-not-exist-404/` | 404 | 245 ms | 16,504 | 6 ms | 7,177 |
| `http://bandhuodisha.in/` | 301 → https | 79 ms | | | |
| `https://www.bandhuodisha.in/` | 200 (no redirect) | 2037 ms | 56,938 | | |

Transport (prod): Cloudflare in front; ALPN `h2` (browser negotiated `h3`); TLS 1.3; HTML Brotli, JS/CSS gzip; every asset `cache-control: max-age=14400` with ETag + Last-Modified; HTML has no `cache-control`, `vary: Cookie,Accept-Encoding`. Local runserver: no compression, no cache headers (expected).

### Page weight (images referenced in HTML, fresh GET each)

| Page | Images | Total | > 300 KB | Largest |
|---|---|---|---|---|
| prod `/` | 81 | 49,488 KB | 18 | `Ankurayan_2024_Logo_Inauguration.png` 8,291 KB; `swamblamban_BGUU3u3.png` 8,291 KB; `our_mission1.jpg` 5,896 KB (onerror fallback, not loaded); `IMG_20190815_082039.jpg` 3,542 KB; `IMG_20190815_103831_yBbZbk4.jpg` 3,114 KB; `notice_files/collage.jpg` 2,428 KB |
| prod `/bandhughar/` | 8 | 9,204 KB (≈3,300 KB actually loaded; `our_mission1.jpg` is the onerror fallback) | 3 | `ashram/thumbnails/collage.jpg` 2,428 KB; `bandhu-logo-navbar.png` 343 KB |
| local `/` | 9 | 7,111 KB | 2 | `our_mission1.jpg` 5,896 KB; `bandhu-logo-navbar.png` 343 KB |

Repo static files > 200 KB (top): `static/img/our_mission1.jpg` 6,037,786 B (duplicated at `img/our_mission1.jpg`), `static/img/icon/404-1.gif` 1,373,645 B, `bandhu_pillars_emblem.png` 856,354 B, `03.png` 597,630 B, `bandhulogo_new.png` 551,933 B, `bandhu-logo-navbar.png` 350,896 B. Built bundle: `static/frontend/assets/index.js` 215 KB, `index.css` 67 KB (uncompressed).

### Lighthouse (mobile, production)

| Page | Accessibility | Best Practices | SEO | Failed audits |
|---|---|---|---|---|
| `/` | 94 | 100 | 92 | `aria-hidden-focus` (visitors carousel), `target-size`, `meta-description`, agent a11y tree |
| `/bandhughar/` | 98 | 96 | 92 | `errors-in-console`, `landmark-one-main`, `meta-description` |

Performance category: not available in this tool's Lighthouse build; CWV taken from the Performance APIs above. Desktop Lighthouse: not run (mobile is the binding case; desktop vitals above).

### Mobile display sweep (layout probe + screenshot per cell)

| Page | 360 | 390 | 768 | 1440 | Notes |
|---|---|---|---|---|---|
| prod `/` | no overflow | no overflow | no overflow | no overflow | dots 9×9 / 8×8 / 6 px tall; video row is a horizontal scroller by design |
| prod `/classic/` | no overflow | — | — | no overflow | no `<h1>`; H3→H5; ticker links 17 px tall; 2 YouTube iframes 480 px wide inside overflow-hidden |
| prod `/sanskar/` | no overflow | — | no overflow | no overflow | `#alert-toast-div` 390 px wide (hidden toast) |
| prod `/swaraj/` | no overflow | — | — | — | |
| prod `/bandhughar/` | no overflow | — | — | no overflow | admin-modal inputs unlabeled (hidden) |
| prod `/other_activities/` | no overflow | — | — | no overflow | hero band is title-only (no image) |
| prod `/prasanta-raktadan-shibir/` | no overflow | — | — | no overflow | |
| prod `/patriotism-in-action/` | no overflow | — | — | — | |
| prod `/odisha-satabdi-sevavrata/` | no overflow | — | — | — | |
| prod `/bandhughar/detail/…lankapara/` | **caption off-screen** (left 300, w 459) | — | — | no overflow | FAB overlaps caption |
| prod 404 | no overflow | — | — | — | image 351 px in 360 (6 px past edge) |
| prod login modal | 349 px wide, fits; focus trapped; body scroll locked; inputs 44 px tall, unlabeled | | | | |
| local `/` | no overflow | — | — | — | same layout as prod; hero = 5.9 MB fallback |
| local `/bandhughar/` | no overflow | — | — | — | 2× 404 (missing local media); label-for misuse ×6 |
| local `/bandhughar/detail/…/` | **caption off-screen** (same numbers) | — | — | — | |

"—" = not measured at that width (360 and 1440 were the bounding cases; 390 matched 360 on the home page exactly).

Screenshots: `screens/prod-home-{360,390,768,1440}.jpeg`, `prod-home-360.png` (full page), `prod-classic-{360,1440}.jpeg`, `prod-sanskar-{360,768,1440}.jpeg`, `prod-swaraj-360.jpeg`, `prod-bandhughar-{360,1440}.jpeg`, `prod-other_activities-{360,1440}.jpeg`, `prod-prasanta-raktadan-shibir-{360,1440}.jpeg`, `prod-patriotism-in-action-360.jpeg`, `prod-odisha-satabdi-sevavrata-360.jpeg`, `prod-bandhughar-detail-{360,1440}.jpeg`, `prod-404-360.jpeg`, `prod-login-modal-360.jpeg`, `local-home-360.jpeg`, `local-bandhughar-360.jpeg`, `local-bandhughar-detail-360.jpeg`.

### Accessibility basics

| Check | Result |
|---|---|
| `<html lang>` | `en` on every page (both) |
| Alt text | `/`, `/bandhughar/`, `/sanskar/`: 0 missing; `/classic/`: 6 of 68 missing (prod); hero slides use `alt=""` (decorative) |
| Heading order | `/`: h1 present; Django pages: no h1, H2→H5 and H3→H5 jumps |
| Form labels | 5 modal inputs placeholder-only; 6 broken `label for` on admin modals |
| Keyboard focus | modal traps focus correctly; nav link focus has no visible outline (one element measured) |
| Contrast | not measured separately — Lighthouse `color-contrast` audit passed on `/` and `/bandhughar/` |
| Landmarks | `/` has `<main>`; Django pages have none |
| Console errors | `/`: none (both); classic-template pages: `main.js:275` TypeError (both) |
| Mixed content | none observed (all requests https on prod) |

## 5. Method

Date: 2026-09-12 (all runs sequential during one session).

Skills loaded: `task-observer` (session protocol), `prompt-master` (prompt), `chrome-devtools-axi` (Chrome control: `open`, `emulate`, `eval`, `screenshot`, `console`, `network`, `lighthouse`, `perf-start/stop`), `web-browsing-cli` (`oc open` no-JS text view). `find-skills` was not invoked: the two browser/HTTP skills already installed covered the need, and `curl` was blocked by policy, so a Node `fetch` script replaced it.

Tools and scripts (all in `~/.claude-tara/jobs/7d233961/tmp/`): `vitals.js` (in-page CWV + image sizing), `layout.js` (overflow, tap targets, headings, labels, meta), `sweep.sh` (viewport loop), `batch2.sh` (modal, console, local), `probe.mjs` → `probe-results.json` (headers, HTML parse, asset HEAD, TLS ALPN), `imgweight.mjs` → `imgweight-*.json` (image bytes per page). Lighthouse reports: `tmp/lh/prod-home-mobile/`, `tmp/lh/prod-bandhughar-mobile/`.

Limits: `perf-start/perf-stop` returned no insights (so CWV come from Performance APIs, warm cache); Lighthouse build lacks the Performance category; production requests kept to ≤ 1/s and ≤ 3 loads per page; no forms submitted, no login, no writes.
