# Spec — Jan 2015 special Ankurayan (approach D)

Status: BUILT 2026-11-06 — M1–M4, R1, R2, T1 done; reviews r1 opus+fable APPROVED, r2 opus APPROVED, end fable APPROVED; suite Ran 782 OK (expected failures=10); V2 regression diff empty (34 pages); live check passed. Remaining: DS1 data entry by the user after deploy.
Previous: correction 2026-11-06 (r1 review) — R1 fallback skips labelled rows; 0018 orders slug op first. Correction 2026-11-06 — added R2 (seed clean-up deleted unsynced rows, which would remove a hand-added special); M1–M4, R1 unchanged. Reconstructed 2026-11-06 against HEAD cddb7dc (first pass).

## Original request
"The site has exactly one Ankurayan entry per year … A 2015 entry already exists (Dec 17–20, 2015). A special Jan 2015 Ankurayan must also show." User asked for 5 approaches with break risk, via /lateral, shown in Lavish. Full record with every question and option: `rough-idea.md`.

## Questions I asked
- **Q1a — which approach?** Options A (section inside Dec 2015), B (hand-made chip), C (second row, slug is the ID), D (C plus display label), E (full rework). Recommended: A if small, D if it needs its own page (evidence: facts F1–F6 below). Answer: "approach D". PROVIDED. ANSWERED → items M1–M4, T1.
- **Q1b — also add the year-strip chip (B)?** Options: yes / no (form note: only matters with A). Recommended: yes only with A (evidence: C/D/E rows each get a chip from ankurayan.html:144 loop). Answer: "add year-strip chip (B): yes". PROVIDED. ANSWERED → M3 (each row already gets a chip; with D it shows the label).
- **Q2a — how should the old 2015 chip read?** Options: "Dec 2015" + "Jan 2015" / "2015" + "Jan 2015" (old chip unchanged). Recommended: "Dec 2015" + "Jan 2015" (evidence: mock capture `scratch/mock/strip-desktop-dec.png`; label is data, needs no extra code). Answer: "chip labels = "Dec 2015" + "Jan 2015"". PROVIDED. ANSWERED → DS1 + M3.
- **Q3 — no regression.** Decision: what the build must prove about existing pages. Open answer. Recommended: rendered-HTML diff of every existing Ankurayan page plus full suite (evidence: detector proven silent/firing on baseline, V2). Answer: "Confirm there will be no regression to the existing website". PROVIDED. ANSWERED → V2 (rendered-page diff), R1 (seed command), Acceptance.

## Confirm these changes
Already established in this conversation (mock page `.lavish/ankurayan-jan2015-mock.html`, answer Q2b "decision = build approach D", plus "build using /dev-workflow"), so not re-asked:
- Q2b go-ahead: build approach D as shown in the mock. Evidence: user answer "decision = build approach D".
- M1/M4: /admin/ Ankurayan form shows a new optional "Label" field after Year; the admin list shows a Label column. Evidence: approved plan D text "admin prepopulates slug from year+label".
- M1: /admin/ object names read "Ankurayan <label or year>" and "Invitation letter — Ankurayan <label or year>"; identical to today for unlabelled rows. Evidence: models.py:32, :167.
- M1/M4: saving a second row with an existing slug is refused (admin form error) instead of creating a duplicate that 500s both pages. Evidence: F2.
- M4: on a new row the slug pre-fills from year + label (e.g. `2015-jan-2015`, editable); existing rows' slugs never change (F3b). Admin list sorts by year then start date. Evidence: admin.py:16, prepopulate.js.
- M2: within one year, the later-starting entry lists first (Dec 2015 before Jan 2015), as in the mock; other years keep today's order. Evidence: views.py:23, :73; mock `scratch/mock/strip-desktop-dec.png`.
- M3: a row with a label shows the label (also in the chip's screen-reader `aria-label`) (e.g. "Jan 2015") in the year chip, tab title, hero heading, h1 and invitation-letter text. Rows without a label render exactly as today (V2). Evidence: mock screenshots.

## My reading of the request
The chip the user asked for (Q1b "yes") is the normal year-strip chip every row already gets; with D it reads the label. No hand-made link. The on-page "New Ankurayan" button stays one-row-per-year; specials are added in /admin/. Creating the Jan 2015 row and typing "Dec 2015" on the existing row are data entry the user does after deploy (DS1), not code.

## Objectives and Outcome ledger
| Objective | Metric that shows it met | Record | Writer |
|---|---|---|---|
| O1 Two rows in one year, each with its own page and label | New tests pass: both detail pages 200 with their own label; index lists both in order | Test log of the suite | dev-workflow run (once); GitHub Actions `tests` workflow on every push (recurring) |
| O2 No change to existing pages | Rendered HTML of /ankurayan/ + 15 detail pages × anonymous/admin identical before vs after with no labels set | `scratch/regress-diff.txt` (empty) | dev-workflow run (once) |
| O3 Safe deploy on MySQL | Duplicate-slug query returns 0 rows before `migrate` | Deploy note in the build's final report | User at deploy |
Artifacts added: 1 model field, 1 migration, 1 test module. No new scripts or jobs.

## Verification summary
| ID | Claim | Status | Citation |
|---|---|---|---|
| F1 | `year` is unique; `slug` is not | CONFIRMED | applications/ankurayan/models.py:11, :25 |
| F2 | Detail/upload views resolve by slug with get_object_or_404 → two equal slugs = 500 | CONFIRMED | views.py:56, :108, :129, :148, :167 |
| F3 | Admin prepopulates slug from year | CONFIRMED | admin.py:16 |
| F3b | Prepopulate JS only fills an empty slug, so editing an existing row's label never changes its URL | CONFIRMED | venv/.../admin/static/admin/js/prepopulate.js `if (!prepopulatedField.val())` |
| F4 | On-page create refuses an existing year; test locks it | CONFIRMED | views.py:43; tests/test_views.py:145 `test_duplicate_year_rejected` |
| F5 | Lists sort by `-year` only | CONFIRMED | views.py:23, :73 |
| F6 | Year is the visible label at 6 template sites + 2 `__str__` | CONFIRMED (grep) | ankurayan_detail.html:8, :34, :1406, :1605, :2055; ankurayan.html:144; models.py:32, :167 |
| F7 | `year == 2021` checks need an int year | CONFIRMED | ankurayan_detail.html:1522, :1528 |
| F8 | Sitemap orders and reverses by slug | CONFIRMED | bandhuapp/sitemaps.py `order_by('slug')`, `kwargs={'slug': entry.slug}` |
| F9 | Local DB: 15 rows, 0 duplicate slugs | CONFIRMED (query run 2026-11-06) | Count/annotate query output `[] 15` |
| F10 | `seed_ankurayan_content` looks rows up by year → crashes (MultipleObjectsReturned) once two 2015 rows exist | CONFIRMED | management/commands/seed_ankurayan_content.py:422 |
| F11 | `notice_links` looks up slug `ankurayan-{year}` — unaffected | CONFIRMED | bandhuapp/notice_links.py:41-45 |
| F12 | Baseline suite: Ran 762, OK (expected failures=10) | CONFIRMED | /tmp/ankurayan-baseline-tests.log |
| F13 | MySQL migration can be tested locally | CONTRADICTED | `mysql not found`; mysqlclient not importable in venv; Docker daemon not running (probe 2026-11-06) |

## Priority order
1. O2 no regression (user's explicit requirement; existing pages are what visitors use today): M2 ordering, M3 blank-label fallback, R1, V2.
2. O3 safe deploy: M1 migration + pre-deploy query.
3. O1 the new capability: M1–M4, T1.
Policy assumed: the user adds the Jan 2015 row and the "Dec 2015" label in /admin/ after deploy.

## M — Model, migration, views, templates, admin

**M1 Model + migration.** Today: models.py:11 `year = IntegerField(unique=True)` and models.py:25 `slug = SlugField()` (F1) — a second 2015 row is refused by the DB, and nothing stops two equal slugs (F2 → 500). CONFIRMED.
Change: `year = models.IntegerField()`; `slug = models.SlugField(unique=True)`; add `label = models.CharField(max_length=40, blank=True, default='', help_text='Shown instead of the year, e.g. "Jan 2015". Leave blank to show the year.')`; add `@property display_label` → `self.label or str(self.year)`; `Ankurayan.__str__` → `f'Ankurayan {self.display_label}'`; `AnkurayanInvitationLetter.__str__` → `f'Invitation letter — Ankurayan {self.ankurayan.display_label}'`. Migration `0018` via `makemigrations ankurayan`, with the slug AlterField ordered first so that on MySQL (non-transactional DDL) a duplicate-slug failure leaves the table unchanged and the migration re-runnable.
Test that fails today: creating two rows with year 2015 and slugs `2015`/`2015-jan` raises IntegrityError today; a duplicate slug saves today and must raise after.
existing path checked: `grep -rn "display_label\|label =" applications/ankurayan/models.py` → no such field/property; `InitiativeHomePageMixin` (bandhuapp/initiative_home_models.py) supplies hero captions only.

**M2 Ordering.** Today: `order_by('-year')` at views.py:23 and :73 — two 2015 rows come back in undefined order. CONFIRMED.
Change: `order_by('-year', '-start_date')` at both sites (Dec 2015 before Jan 2015, as in the mock). Years are unique for existing rows, so their order is unchanged.
Test that fails today: index with Dec (start 2015-12-17) and Jan (start 2015-01-10) rows lists Dec before Jan regardless of insert order (insert Jan last and first).
existing path checked: no Meta.ordering on Ankurayan (models.py:28-29 holds only verbose_name_plural).

**M3 Template labels.** Today: ankurayan_detail.html:8, :34, :1406, :1605, :2055 and ankurayan.html:144 print `year` (F6). CONFIRMED.
Change: `ankurayan.year` → `ankurayan.display_label` at ankurayan_detail.html:8, :34, :1406, :1605, :2055; `ankur.year` → `ankur.display_label` in both the text and `aria-label` at ankurayan.html:144. Leave :1522/:1528 on `year` (F7). With a blank label, `display_label` renders the same digits, so output is byte-identical (V2).
Test that fails today: detail page of a row labelled "Jan 2015" contains `<h1 class="bold-txt page-showcase-title">Ankurayan Jan 2015</h1>` and `content: "Ankurayan Jan 2015"`; index contains a chip reading `Jan 2015`.
existing path checked: grep in F6 lists every `year }}` render in the app's templates; no shared include renders the year.

**M4 Admin.** Today: fieldset `('year', 'title', 'theme', 'slug', 'start_date', 'end_date')`, `prepopulated_fields = {'slug': ('year',)}`, `list_display = ('theme', 'year', 'start_date', 'end_date')`, `ordering = ('year',)` (admin.py:16-21). CONFIRMED.
Change: fieldset `('year', 'label', 'title', 'theme', 'slug', 'start_date', 'end_date')`; `prepopulated_fields = {'slug': ('year', 'label')}` (new rows only, F3b); `list_display = ('theme', 'year', 'label', 'start_date', 'end_date')`; `ordering = ('year', 'start_date')`. A clashing slug becomes a form error (unique field), not a 500.
Test that fails today: admin add form POST with year 2015 and slug `2015` while a `2015` row exists returns the form with a slug error and no new row.
existing path checked: admin.py:14-25 is the only ModelAdmin for Ankurayan.

**M5 On-page create view — no change.** Today: views.py:43 refuses an existing year, so the on-page button cannot make a special; that is the wanted behaviour. CONFIRMED. Keeping it keeps the on-page button one-row-per-year, and `test_duplicate_year_rejected` (tests/test_views.py:145) stays green unchanged. Specials go through /admin/ (My reading).
existing path checked: views.py:28-52 `create_ankurayan`.

## R — Commands

**R1 Seed command lookup.** Today: `Ankurayan.objects.get_or_create(year=year, defaults=defaults)` (seed_ankurayan_content.py:422) raises MultipleObjectsReturned once a second row with that year exists. CONFIRMED.
Change: pick the row whose slug is `str(year)` first; if none, use the year's only *unlabelled* row when exactly one exists (today's behaviour; a labelled special is never re-slugged, matching R2's definition); otherwise create with `year=year, **defaults`. Behaviour for one-row-per-year data is unchanged.
Test that fails today: run the command's lookup helper with rows `2015` and `2015-jan` (year 2015) → returns the `2015` row, no exception.
existing path checked: grep F10 — the only `year`-keyed get/get_or_create on Ankurayan outside tests.

**R2 Seed clean-up keeps specials.** Today: seed_ankurayan_content.py:472 `Ankurayan.objects.exclude(id__in=kept_ids).delete()` deletes every row the seed did not sync, so a hand-added `2015-jan` row would be deleted on the next seed run. CONFIRMED (found by the r1 builder; line read 2026-11-06).
Change: delete only unlabelled unsynced rows: `Ankurayan.objects.exclude(id__in=kept_ids).filter(label='').delete()`. Every row that exists today has a blank label after M1's migration, so the clean-up is unchanged for today's data.
Test that fails today: seed clean-up with a kept `2015` row, an unsynced labelled `2015-jan` row and an unsynced unlabelled row → the labelled row survives, the unlabelled one is deleted.
existing path checked: :472 is the only `Ankurayan.objects…delete()` in the command (grep `.delete()`).

## T — Tests

**T1 New test module** `applications/ankurayan/tests/test_same_year_entries.py`: covers R2 (labelled row survives clean-up), M1 (unique slug IntegrityError; two 2015 rows coexist), M2 (order), M3 (labels on detail + index chip; blank-label row still renders `Ankurayan 2015`), M4 (admin slug clash), R1 (lookup). Today: NOT FOUND (new capability) — `grep -rln "2015-jan" applications/ankurayan/tests` → none.
existing path checked: tests/test_views.py, test_models_admin.py hold no same-year cases.

## V — Verification
- V1 Suite: `venv/bin/python manage.py test 2>scratch/test.log >/dev/null; rc=$?; tail -5 scratch/test.log` → `Ran 762+N` (N = new test methods) `OK (expected failures=10)`. Writes no live state (in-memory sqlite).
- V2 No regression: `venv/bin/python manage.py migrate ankurayan` on the local db.sqlite3 (writes local DB; back up first: `cp db.sqlite3 /tmp/ankurayan-regress/db.sqlite3.bak`), no labels set, then `venv/bin/python DONE/planning/2026-11-06-ankurayan-jan-2015-special/scratch/snap.py /tmp/ankurayan-regress/after` and `diff -r /tmp/ankurayan-regress/before /tmp/ankurayan-regress/after > scratch/regress-diff.txt` → empty. Baseline captured at cddb7dc. Detector proven: silent on two baseline runs, fires on a one-word change.
- V3 `venv/bin/python manage.py makemigrations --check --dry-run` → "No changes detected".
- V4 Live: on a copy of the local DB only, add a Jan 2015 row (slug `2015-jan`) and label the 2015 row "Dec 2015"; chrome-devtools-axi shows both chips on /ankurayan/ and both detail URLs load. Restore the DB backup afterwards.

## Completeness sweep
Specified: `label` field (M1), migration 0018 (M1), test module (T1), `scratch/regress-diff.txt` (V2). Referenced-only: none. Nonexistent: none (label's producer is the admin form, M4).

## Requirement trace
| User's words | Item | Match |
|---|---|---|
| "approach D" (Q1a) | M1–M4 | verbatim |
| "add year-strip chip (B): yes" | M3 (chip text from label) | verbatim (chip exists per row; no hand-made link) |
| "Dec 2015" + "Jan 2015" (Q2a) | DS1 (data, user) + M3 | verbatim |
| "build approach D" (Q2b) | M3 labels match mock captures | verbatim |
| "Confirm there will be no regression to the existing website" | V2, R1, R2, M2, M3 fallback | verbatim |

## Data step (user, after deploy)
DS1: in /admin/ → Ankurayan → 2015: set Label "Dec 2015". Add Ankurayan: Year 2015, Label "Jan 2015", slug `2015-jan` (edit the pre-filled `2015-jan-2015` if a shorter URL is wanted), title, theme, dates, hero image.

## Deferred
- MySQL migration run before production. NO EVIDENCE: no local MySQL (F13 probe). Mitigation: pre-deploy `SELECT slug, COUNT(*) FROM ankurayan_ankurayan GROUP BY slug HAVING COUNT(*)>1;` must return no rows. Reopen when: Docker daemon is running locally (then run migrate against `mysql:5.7`/`8` with PyMySQL in a scratch venv).
- On-page "New Ankurayan" form gets a Label input. Reopen when: human call — the user wants to add specials without /admin/.
- On-page create also refusing a slug clash (views.py:47-48 checks year only; an admin row whose slug equals another year's string would make `create()` raise IntegrityError). End-pass review, Minor. Reopen when: an admin row's slug is a bare year different from its own year.
- Seed test `SeedCommandTests` does not assert `--offline` skips detail fetches (r2 review, low). Reopen when: the seed command's `--offline` handling changes.
- Other models' `__str__` (Participant, Guest, Activity, Photo) still show the bare year in /admin/ lists. Reopen when: human call — admins find two "2015 - …" entries confusing.

## Summary of the pass
Framing: evidence harvested from the code, local DB (15 rows, 0 dup slugs) and baseline suite (762 OK); mandate-first item is "no regression" (user Q3); operating policy: data entered by the user in /admin/ after deploy. Assumptions 14 (F1–F13 + F3b): CONFIRMED F1–F12, F3b; CONTRADICTED F13; NOT FOUND none. Citations re-resolved by grep this session, 0 stale. Strategist: N/A (no trading logic). grill-me: none live — Q1–Q3 answered earlier in this conversation. Completeness: Referenced-only 0, Nonexistent 0. Blockers: none; readiness: buildable. Plan text change from the approved plan: the create view keeps its year check (M5) instead of switching to a slug check — no visible change, keeps one-row-per-year on that button.

Item status table:
| ID | Status | file:line |
|---|---|---|
| M1 | CONFIRMED | models.py:11, :25 |
| M2 | CONFIRMED | views.py:23, :73 |
| M3 | CONFIRMED | ankurayan_detail.html:8; ankurayan.html:144 |
| M4 | CONFIRMED | admin.py:16 |
| M5 | CONFIRMED | views.py:43 |
| R1 | CONFIRMED | seed_ankurayan_content.py:422 |
| R2 | CONFIRMED | seed_ankurayan_content.py:472 |
| T1 | NOT FOUND (new capability) | grep "2015-jan" tests → none |

Question decision table:
| Q | Decisions | n |
|---|---|---|
| Q1a | which approach | 1 |
| Q1b | add the chip | 1 |
| Q2a | old chip text | 1 |
| Q3 | no-regression requirement | 1 |

Counts: 1) 0 · 2) 0 · 3) 0 · 4) 0 · 5) 0 · 6) 0 · 7) 0. Fresh-reader pass: 14 found (M1, M3, M5 openings; 5 unlisted visible changes; Q1b, Q3 missing recommendation/evidence; Q2 bundled; Q-ID mismatch with rough-idea; O3 record), 14 fixed.

Steps run / steps skipped (reason): 0 run, 0b run, 1 run, 2 run, 3 run (counts measured; no numeric thresholds), 4 skipped (N/A: no trading rule, threshold or strategy logic), 5 run (all gaps resolved from conversation answers Q1–Q3), 6 run, 7 run, 8 run.
