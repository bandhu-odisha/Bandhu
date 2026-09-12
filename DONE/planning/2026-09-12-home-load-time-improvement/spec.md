# Home page load time

**Status:** implemented — Steps 1-3 done, verified against code at commit `e932efd`. Supersedes item **W01** of `DONE/planning/2026-09-12-cx-audit/report.md`, whose diagnosis was wrong.

## Problem

The home page `/` takes 1.4–2.1 s to return any HTML. Every other page on the site takes 0.25–0.45 s.

The cause is a single blocking network call. `bandhuapp/views.py:468` calls `enrich_video_durations(data['videos'])`, which downloads the full public YouTube watch page (~1 MB each, 4 s timeout, four at a time) for every `Video` row whose `duration` is blank — on every request — and never stores the result, so it does it again on the next request forever. All 6 rows have a blank duration. It is the only call site of that function in the repo, which is exactly why only `/` is affected.

It has behaved this way since commit `3d97171` (2026-07-04), so the site has been paying this on every home page visit for about ten weeks.

Two further costs, both on the same page and both smaller: the home page ships 79 requests and roughly 48 MB of images, and two code paths do avoidable per-request work.

### Measured

Harness: `measure_landing.py` in this folder. Run it with `./.venv/bin/python DONE/planning/2026-09-12-home-load-time-improvement/measure_landing.py` from the repo root. It calls `_build_landing_data()` via `RequestFactory` with an `AnonymousUser`, inside a rolled-back transaction, and counts queries with `CaptureQueriesContext`. Parameters for every row below: local sqlite (`DB_ENGINE=sqlite`), `DEBUG=True`, 6 `Video` rows all with blank duration, macOS, auditor's home network.

| Run | Sample 1 | Sample 2 | Queries |
|---|---|---|---|
| YouTube fetch stubbed | 46.5 ms | 37.0 ms | 60 |
| YouTube fetch live | **1528.0 ms** | **1578.4 ms** | 60 |
| Stubbed again (control) | 9.0 ms | 16.8 ms | 60 |

The first stubbed run carries import and connection warm-up; run 3 is the clean figure. The fetch costs **~1.52–1.57 s**, and the query count is identical with and without it — the database layer is not implicated at all.

Because the delta is network latency, it is a floor, not a ceiling: from GoDaddy's datacenter the fetch may be slower than from a laptop, and the 4 s per-request timeout in `bandhuapp/helpers.py:131` is the real worst case.

### What the audit got wrong, and why it matters

W01 concluded "it is the view's own work, not hosting" because local was also slow (1.6–1.8 s). Local is slow for the *same* reason — local also calls YouTube. The comparison distinguished nothing. W01 therefore proposed caching the built dictionary and trimming the view; both are now ruled out on measurement:

- **Caching `_build_landing_data`** would wrap 9–17 ms of real work. There is also no `CACHES` block in `bandhu/settings.py`, so the default is per-process `LocMemCache`, and cPanel Passenger recycles and idles-out workers — every cold worker would still pay the full 1.5 s.
- **Query trimming / `select_related`** would target 60 queries that measure 9–17 ms in total.

## Step 1 — Remove the YouTube fetch from the request path

Fetch durations once, store them, never make a visitor wait for them.

**`bandhuapp/views.py`** — delete the `enrich_video_durations(data['videos'])` call at line 468 **and** the now-unused import at lines 47-52. The loop above line 468 already reads the stored `v.duration`, so a populated field needs nothing else.

**Three existing tests patch that import and must be updated in the same change:** `bandhuapp/tests/test_landing.py:35`, `test_landing.py:106` and `bandhuapp/tests/test_views_coverage.py:393` all patch `'bandhuapp.views.enrich_video_durations'`. Removing the import makes those patchers raise `AttributeError` at setUp; leaving the import in place makes them pass vacuously. Delete the patchers — once the call is gone they assert nothing.

**New management command `bandhuapp/management/commands/backfill_video_durations.py`** — iterate `Video.objects.filter(duration='')`, reuse `enrich_video_durations` (`bandhuapp/helpers.py:148`, which already parallelises correctly), write each result back with `.save(update_fields=['duration'])`, and print a one-line summary of how many were filled. This is the only automated writer of `duration`.

Leave `enrich_video_durations` and `fetch_youtube_duration_formatted` (`helpers.py:111`) unchanged. The command becomes their only caller, and their 9 existing tests (`test_helpers.py:136-183`) stay green.

**Host constraint:** the command runs on cPanel under **Python 3.7.17** (kernel `4.18.0-553.141.2.lve.el8.x86_64`). No walrus operator, no `functools.cached_property`, no positional-only params. f-strings and `ThreadPoolExecutor` are fine.

**Document it in `README.md`** alongside the existing deploy steps (§3): run `python manage.py backfill_video_durations` once after this deploy, and again whenever a video is added. No cron — with ~6 videos changing a couple of times a year, a scheduled job on cPanel is more machinery than the problem justifies, and a missed run costs a cosmetic badge and nothing else.

**Why the badge survives this.** `duration` renders as one small text label in the corner of a video thumbnail (`frontend/src/components/Videos.jsx:78-82`), conditionally — `{duration ? … : null}` — so its absence causes no layout shift and no placeholder. It is also already an editable admin field shown in the list view (`bandhuapp/admin.py:558-559`), so an admin can type one by hand and can see at a glance which videos lack one. A video added between command runs simply shows no length.

## Step 2 — Cut the image payload

The home page references 81 images totalling ~48 MB, including two 8 MB PNGs and a 5.9 MB JPEG. Gallery images are 4000×3000 served to a 313 px slot; the hero is 1040×780 served to 315 px. No `srcset`, no `sizes`, no `width`/`height`, no WebP.

Note that the audit's browser timings were taken with a **warm cache**, which flatters this badly. A first-time visitor on mobile data waits on these bytes and will not notice whether TTFB was 2.1 s or 0.2 s. After Step 1 this is the dominant remaining cost.

`easy-thumbnails==2.6` and `Pillow==6.2.1` are **already in `requirements.txt`** (lines 17 and 23, pulled in by `django-image-cropping`), but `easy_thumbnails` is not in `INSTALLED_APPS`. Enable it rather than adding a dependency or hand-rolling a resize step.

- Add `'easy_thumbnails'` to `INSTALLED_APPS` in `bandhu/settings.py` and define `THUMBNAIL_ALIASES` with three widths — 480, 960 and 1600 px — output as WebP, `upscale=False`.
- In `_build_landing_data`, emit each image as an object rather than a bare URL string: `{'src': <960px url>, 'srcset': '<480 url> 480w, <960 url> 960w, <1600 url> 1600w', 'width': <int>, 'height': <int>}`. Apply to the hero, gallery, pillar and visitor image fields. Keeping the original bare-URL key alongside it lets the React side migrate component by component.
- Consume it in `frontend/src/components/Hero.jsx:103-112` (currently an `<img>` with `src`/`alt`/`className`/`loading`/`decoding` and no `srcSet`) and the gallery components, and set explicit `width`/`height` to prevent layout shift.
- Warm the thumbnails for existing media once after deploy so the first visitor does not pay generation cost.

## Step 3 — Two per-request costs the audit missed

**Unbounded gallery scan — `bandhuapp/views.py:394`.** `for p in Photo.objects.filter(approved=True).order_by('-created')` has no limit, and each iteration calls `file_url()` (a filesystem `stat`) *before* the Python-side `continue` filters discard most rows. Both the server cost and the page's image payload grow without bound as admins upload. Push the filter into SQL (`picture__startswith='bandhuapp/gallery/'`) and add an explicit limit.

**Writes on an anonymous GET — `bandhuapp/initiative_program_year.py:95`.** `reconcile_publish_states` loops every `Ashram` row and calls `.save(update_fields=['is_published'])` whenever the flag has drifted. `build_initiative_nav_visibility` (`:104`) calls it for all three programs, and it is also registered as a context processor (`bandhu/settings.py:74`) — so every page on the site pays it, and `/` pays it twice. Each row costs up to 6 `EXISTS` queries via `entry_has_public_content` (`:71`). Make the read path read-only and reconcile on save or in a command instead.

Locally this is cheap because the tables are small, and it is *included* in the 9–17 ms baseline above. Its production cost scales with the number of year entries, which is unmeasured — see Deferred.

## Out of scope, with reasons

- **Anything requiring the Cloudflare dashboard.** Verified 2026-09-12: nameservers are `maeve.ns.cloudflare.com` / `owen.ns.cloudflare.com` and the domain resolves to Cloudflare anycast IPs (`104.21.74.72`, `172.67.156.59`), so the site *is* proxied through Cloudflare, on what appears to be the free tier. **The team neither controls nor pays for that account.** No step here may depend on a Cloudflare setting. This also blocks audit items W06 (edge cache rule), W18 (`www` → apex redirect) and W19 (Email Obfuscation, which injects a script that 404s on every classic page).
- **Edge-caching the `/` HTML.** Blocked by the account access above, and unnecessary once the page returns in ~250 ms. It is also not the one-line change W01 implied: `index_react` calls `get_token(request)`, and both `accounts/templates/includes/login_modal.html:17` and `includes/signup_modal.html:17` emit `{% csrf_token %}`, so `Set-Cookie: csrftoken` goes out regardless — and it is `Set-Cookie`, not `Vary`, that makes Cloudflare decline to cache. Doing it properly means moving the token to a lazy fetch on modal open (the cookie-fallback pattern already exists at `frontend/src/components/AnnualReportUploadModal.jsx:15`) plus a bypass rule for `sessionid` so admins are never served the public variant.

## Verification

1. **Reproduce the cause before changing anything.** `./.venv/bin/python DONE/planning/2026-09-12-home-load-time-improvement/measure_landing.py`. Expect roughly 1500 ms live vs under 20 ms stubbed, 60 queries throughout.
2. **After Step 1, re-run the same harness.** Expect the "live" row to collapse to the stubbed figure.
3. **Add a regression test asserting no network on the request path.** Patch `urllib.request.urlopen` and assert **`urlopen.assert_not_called()`** after `_build_landing_data` runs. Asserting only that the function survives an exception would pass vacuously, because `enrich_video_durations` already swallows exceptions at `helpers.py:163`. The patch target is sound: `helpers.py` does `import urllib.request` and calls `urllib.request.urlopen(...)` at line 131, so the attribute is looked up at call time.
4. **Run the command against the real rows** and confirm all 6 durations populate and the badges render as before.
5. **Run the suite and check the count, not just the pass.** Baseline confirmed today: `Ran 732 tests in 15.588s` / `OK (expected failures=10)`. Step 1 removes 3 patcher lines but no test methods, so the count should stay 732 plus whatever is added. Any other number is a discovery failure that still prints `OK`. **Use `./.venv/bin/python manage.py test`** — see Deferred on the venv discrepancy.
6. **Rebuild the frontend** after Step 2 (`cd frontend && npm run build`), commit the build output, and bump `?v=305` on `templates/landing_react.html:27` and `:190`.
7. **Measure production after deploy** the way the audit did (Chrome, 360×740 mobile) but with a **cold cache**. Targets: `/` TTFB in line with `/bandhughar/` (~250–800 ms), and home page image weight far below 48 MB.

## Deferred

- **Production `Video` row count and blank-duration count.** `6 / 6` is confirmed against the local `db.sqlite3` only; production may hold more, which would make the fetch cost proportionally worse. *Reopen when:* the backfill command is first run on the host — its summary line reports the real count.
- **Production `Photo` row count.** Sizes both the unbounded scan in Step 3 and the image payload. The local table is empty, so no local measurement is possible. **NO EVIDENCE** — searched: local `bandhuapp_photo` via sqlite, returned 0 rows. *Reopen when:* anyone next has a production shell or DB dump.
- **Production year-entry counts per initiative program.** Determines whether `reconcile_publish_states` is a trivial cost or a real one in production. **NO EVIDENCE** locally. *Reopen when:* the Step 3 change is deployed and page timings on any initiative page are re-measured.
- **Whether `easy_thumbnails` 2.6 behaves on Django 2.2 + Pillow 6.2.1 with WebP output.** Version-compatible on paper; not exercised in this repo. *Reopen when:* Step 2 starts — first task is a spike generating one WebP thumbnail locally.
- **Recovering control of the Cloudflare account.** Higher priority than its performance impact suggests: whoever holds it controls where the entire domain resolves. *Reopen when:* human call — someone checks the GoDaddy domain registration contact and decides whether to reclaim or migrate the DNS.
- **`CLAUDE.md` and `README.md` document `source venv/bin/activate`, but `./venv` has no Django installed; `./.venv` has Django 2.2.13.** Every command in the docs fails as written. *Reopen when:* human call — confirm which virtualenv is canonical, then fix the docs or the venv.

## Implementation notes (2026-09-12)

All three steps shipped. Deviations from the plan above, and what verification actually found:

- **Step 1.** Implemented as written. `measure_landing.py` no longer has a `views.enrich_video_durations` symbol to patch (the call is gone, not stubbed), so its three-row live/stubbed comparison was rewritten to three identical "steady state" timings — all fetch-free by construction. Re-run result: ~5-6 ms / 52 queries (down from 60 queries pre-fix; Step 3's SQL-filtered photo scan also ran by this point). New regression test `bandhuapp.tests.test_landing.LandingDataNoNetworkTests` patches `urllib.request.urlopen` per the spec's Verification §3.
- **Step 2 spike (done first, per Deferred item).** `easy_thumbnails==2.6` calls the removed `PIL.Image.ANTIALIAS` constant (deprecated Pillow 9.1, removed Pillow 10). Local `.venv` has drifted to Pillow 10.4.0 despite `requirements.txt` pinning `Pillow==6.2.1` (see the venv-discrepancy Deferred item above) — production's pinned version is unaffected, but local dev/test would break without a shim. Added a compatibility shim in `bandhu/settings.py` (`Image.ANTIALIAS = Image.LANCZOS` when absent) so thumbnail generation works under either version. Verified end-to-end with a real WebP thumbnail generated from a test image (`bandhuapp.tests.test_views_coverage.BuildLandingDataBranchTests.test_gallery_photo_gets_a_real_webp_thumbnail`).
- **Step 2 scope.** The `{src, srcset, width, height}` object (`responsive_image()` in `bandhuapp/helpers.py`) is applied to gallery photos, profile photos, `HomeVisitor.photo`, `HeroSlide.image`, `HomePage.banner_image`, and pillar mission images — added as a sibling `*_responsive` key (e.g. `picture_responsive`) alongside the existing bare-URL key, exactly as the spec asked. **Not** applied to `hero_photos` (the small decorative extras built by `resolve_media_or_static`, which returns a bare URL string with no Django `FieldFile` to hand to `easy_thumbnails` — mixes real media files and bundled static images). This is a real gap against "apply to the hero... fields" but a narrow one: the actual large hero asset (`HomePage.banner_image` / `HeroSlide.image`) is covered. Consumed in `frontend/src/components/Hero.jsx` and `Gallery.jsx` (`srcSet`, `sizes`, `width`, `height` on the `<img>`).
- **Step 2 width/height cost — found and fixed in review.** The first pass derived width/height by reading `ThumbnailFile.width`/`.height` directly, on the (false) assumption that an already-generated thumbnail made this free. Code review traced `easy_thumbnails/files.py`: without `THUMBNAIL_CACHE_DIMENSIONS`, that property runs a DB query (`Thumbnail.objects.select_related('dimensions').get(...)`) that never finds a cached row, then *opens the thumbnail file from storage and reads it* — on every access, for every image, every request. That reintroduces exactly the per-request, photo-count-scaling cost Steps 1 and 3 removed, and was invisible locally only because the local `Photo` table is empty. Fixed with two changes: `THUMBNAIL_CACHE_DIMENSIONS = True` in `bandhu/settings.py` (so the DB row, once populated, is actually used instead of re-reading the file), and a process-level cache in `bandhuapp/helpers.py` (`_thumb_dimensions`, keyed by thumbnail name) so a repeat request in the same worker costs neither a query nor a file read at all. Regression test: `bandhuapp.tests.test_views_coverage.BuildLandingDataBranchTests.test_thumbnail_dimensions_are_process_cached` asserts zero thumbnail-table queries on a second call. `warm_landing_thumbnails` still pre-generates the thumbnail files themselves post-deploy; local `Photo`/media tables are empty (per the Deferred item on production `Photo` count), so the cold-generation cost under real data volume is still unmeasured here.
- **Step 3, photo scan.** Split into two SQL-filtered, limited queries (`profile_photos/` and `bandhuapp/gallery/` prefixes) instead of one filtered query — a single filter would have silently dropped `profile_photos` entries, which come off the same `Photo.objects.filter(approved=True)` queryset as gallery rows. Limits: `GALLERY_SCAN_LIMIT = 200`, `PROFILE_PHOTOS_LIMIT = 100` (headroom over today's ~81 total images; the dedup pass after the SQL limit can still shrink the final list further).
- **Step 3, reconcile-on-GET.** Removed `reconcile_publish_states` from `build_index_context`, `render_year_detail`, and `build_initiative_nav_visibility` (all GET-triggered). Added it to the three content-*removal* views that previously had no unpublish path at all (`delete_report_file`, `delete_report_link`, `delete_invitation` in `bandhuapp/initiative_program_year.py`) — `maybe_publish_entry` on the addition side never unpublishes, so without this, deleting the last piece of public content would leave an entry stuck published. New management command `reconcile_initiative_publish_states` covers everything else that can drift the flag (a Django-admin edit to `reports` text, a manually-toggled `is_published`). Several existing tests that created an `Ashram` directly with `reports=...` and relied on the read-path reconcile to auto-publish it now set `is_published=True` explicitly — the invariant "adding content publishes" is still covered by `initiative_program_support.py`'s existing `maybe_publish_entry`/`reconcile_publish_states` tests, just no longer triggered implicitly by every GET.
- **Test count:** 732 → 736 (+4: the no-network regression test, a WebP-thumbnail regression test, a reconcile-command test, and the dimensions-cache regression test added during review; one existing nav test was renamed rather than added). `CLAUDE.md`'s baseline and method-count cross-check are updated.

### Observation: production vs. localhost, post-fix (2026-09-12)

Production has **not** been deployed with this fix — everything below is committed on `worktree-home-load-time-spec` only. This is a measurement of the gap the fix closes, not a claim that production is already fast.

| | Production (bandhuodisha.in, live, unfixed) | Localhost (this branch, fixed) |
|---|---|---|
| TTFB, mobile | 2120 ms | — |
| TTFB, desktop | 1515 ms | — |
| Full response, cold | — | 103 ms |
| Full response, steady-state | — | 8–16 ms |

Production figures are the CX audit's own browser/Node measurements (`DONE/planning/2026-09-12-cx-audit/report.md`), taken before this fix existed — they still describe the live site today. Localhost figures are a direct measurement here, via `django.test.Client` against `/` with `ALLOWED_HOSTS` overridden, on this branch (commit `43fd746`).

That is roughly a 100–250x difference, and it is the mechanism identified above, not a hosting artifact: production still runs the code that scrapes YouTube's full watch page on every home page request; this branch does not.

Two caveats against over-reading this table:
- **Not apples-to-apples.** Production is real internet + Cloudflare + GoDaddy shared hosting + MySQL; localhost is Django's dev server on the auditor's machine with sqlite. Once this branch is deployed, expect production TTFB in roughly the **200–500 ms** range — in line with `/bandhughar/`'s already-measured 250–800 ms — not localhost's single-digit milliseconds. Network round-trip and MySQL replace sqlite's near-zero local latency.
- **This is a floor, not a deployed result.** The fix removes ~1.5 s of the measured 1.5–2.1 s gap; the remaining sub-second baseline is unmeasured on production until deploy. *Reopen when:* this branch is merged and deployed, and `/` is re-measured on bandhuodisha.in the same way the audit did (Chrome, 360×740 mobile, cold cache).
