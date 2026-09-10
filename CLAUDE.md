# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is
Website for Bandhu Odisha (non-profit). Django 2.2 backend + React 18/Vite/Tailwind landing page. Deployed on cPanel via Passenger (`passenger_wsgi.py` → `bandhu.wsgi`). README.md has full setup/deploy steps; keep it updated when those change.

## Commands
```bash
source venv/bin/activate                      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                          # set SECRET_KEY, STATIC_ROOT, MEDIA_ROOT (absolute), DB_ENGINE=sqlite
python manage.py migrate
python manage.py create_admin_user            # admin@bandhu.demo / admin123; --reset-password to reset
python manage.py import_local_media           # placeholder images only; real media comes from cPanel zip
python manage.py runserver                    # http://127.0.0.1:8000/

# Models changed
python manage.py makemigrations && python manage.py migrate

# Landing page (React) changed — build output is COMMITTED, rebuild and commit it
cd frontend && npm install && npm run build   # writes ../static/frontend/assets/index.{js,css}
```
```bash
python manage.py test                          # regression suite (sqlite in-memory, no network); CI runs it via .github/workflows/tests.yml
python manage.py test applications.sevavrata   # one app; tests live in <app>/tests/ packages
coverage run manage.py test && coverage report # optional; `pip install coverage` locally only, omit rules in .coveragerc
```
Test helpers: `bandhuapp/tests/support.py` (users, profiles, uploads, `TempMediaMixin`); `bandhuapp/tests/initiative_program_support.py` is the shared contract every initiative-program clone app runs. `@unittest.expectedFailure` tests document known bugs — read the docstring before "fixing" the test. **Never delete `applications/__init__.py`** — without it `applications/` is a namespace package, the runner silently discovers only the `accounts`/`bandhuapp` tests (285 instead of 725) and still reports success, and `manage.py test applications.<app>` dies with a `TypeError`. No linter config. Deploy = `git pull`, `pip install`, `migrate`, `collectstatic --noinput`, restart (see README §3).

**Check the test count, not just the pass.** A full run is `Ran 725 tests ... OK (expected failures=10)`. The runner reports on the tests it *discovered*, so a lower number is a discovery failure that still prints `OK` — treat any count other than 725 as a broken build until explained (a deliberate add/remove is the only valid explanation; bump the number here when that happens). Cross-check against `grep -rh "def test_" --include="*.py" accounts bandhuapp applications | wc -l` (647 methods on disk; runtime is higher because the clone apps each re-run the shared initiative contract).

**If output ever buries the summary**, split the streams — the progress dots and the `Ran N tests` line go to stderr, so anything an app writes to stdout drowns it in `tail`:
```bash
python manage.py test 2>err.log >/dev/null; tail -20 err.log
```
This is diagnostic only, not standing procedure: app code must not write to stdout. Request-path failures use `logger.exception(...)` on a module logger (`accounts/forms.py`, `accounts/views.py`, `bandhuapp/views.py`) — never `print()`. Tests that deliberately trigger those handlers wrap the call in `with self.assertLogs('<module>', level='ERROR')`, which both asserts the failure is logged and keeps the traceback out of the run output; without it the record propagates to Python's last-resort handler and clutters stderr.

## Gotchas
- `.gitignore` ignores `*.html`. Existing templates are tracked; a **new** template needs `git add -f`.
- `db.sqlite3`, `media/`, `.env` are ignored. `DB_ENGINE` defaults to `mysql` in `bandhu/settings.py`; set `sqlite` locally.
- Static assets are referenced with manual cache-busting `?v=NNN` in templates (e.g. `templates/landing_react.html`); bump the number when the file changes.
- Root `css/`, `css1/`, `js/`, `img/` are live static dirs (mapped with prefixes in `STATICFILES_DIRS`), not legacy.
- **Django serves static/media only when `DEBUG=True`.** The `else:` branch in `bandhu/urls.py` is commented as serving them with `DEBUG=False`, but it is dead code — `django.conf.urls.static.static()` returns `[]` whenever `DEBUG` is false. In production the web server (Apache/LiteSpeed on cPanel) serves `/media/` and `/static/` off disk as a *different* OS user than the Passenger app, so app-written files without world-read permission 403. Hence `FILE_UPLOAD_PERMISSIONS = 0o644` / `FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755` in `bandhu/settings.py`; see `DONE/planning/2026-09-10-media-upload-permissions/spec.md`.
- Pinned old deps (Django 2.2, Pillow 6, mysqlclient 2.0) — don't upgrade casually.
- `scripts/` = one-off migration repair scripts, not tooling.

## Architecture
**Project layout**
- `bandhu/` — settings (env via `python-decouple` from `.env`), root `urls.py`, wsgi.
- `accounts/` — custom `User` (`AUTH_USER_MODEL=accounts.User`), signup/login modal, email tokens, password reset, social auth (`social_django`).
- `bandhuapp/` — core app: landing page, people/staff/designations, pillar home pages, annual reports, notices, and **all shared initiative machinery** (below).
- `applications/<initiative>/` — one Django app per initiative, each mounted at its own URL prefix in `bandhu/urls.py` (`bandhughar/`→`ashram`, `other_activities/`→`charitywork`, `prasanta-raktadan-shibir/`, `patriotism-in-action/`, `odisha-satabdi-sevavrata/`, etc.). `madhmukti` and `sanskarbarga` are URL/view-only shells (empty models). Each has a `seed_<app>_content` management command.

**Landing page (React)**
`/` → `bandhuapp.views.index_react` → `templates/landing_react.html`, which injects server data via `{{ landing_data|json_script:"landing-data" }}` and loads `static/frontend/assets/index.{js,css}`. `frontend/src/App.jsx` reads that JSON. Same data at `/api/landing/`. Legacy Jinja landing survives at `/classic/`. `frontend/vite.config.js` pins `base: '/static/frontend/'`, `outDir: ../static/frontend`, fixed asset filenames so Django can hard-code paths.

**Initiative programs (the unified pattern)**
`prasantaraktadan`, `patriotism`, `sevavrata` are clones of `ashram` (Bandhughar) with identical model sets (Ashram, Activity, Event, Meeting, Attendee, Photo, report/invitation files, HomePage). They share logic through `bandhuapp/initiative_program_year.py`: a `PROGRAMS` registry keyed by app label holding display copy + URL names, view factories (`make_create_activity`, `make_add_to_gallery`, `make_upload_report_file`, …), context builders (`build_index_context`, `build_year_detail_context`), and publish logic (`entry_has_public_content`, `maybe_publish_entry`, `reconcile_publish_states`, `get_visible_entries`). Templates live in `templates/initiative_program/`. Related helpers: `bandhuapp/initiative_home_models.py` (hero caption mixin), `initiative_*_admin.py`, `initiative_program_seed.py`, `bandhughar_clone_seed.py`. Adding a new program = new clone app + `PROGRAMS` entry, not new views.

**Pillar homes**
Abstract `PillarHomePageBase` in `bandhuapp/models.py` → `SanskarHomePage`, `SwarajHomePage`, `SwabalambanHomePage`; views `pillar_sanskar`/`pillar_swaraj`; nav visibility from context processor `bandhuapp.processors.initiative_nav_visibility`.

**On-page admin**
Logged-in admins get inline controls on public pages. Pattern: `{% if user|is_admin %}` (filter in `bandhuapp/templatetags/permissions.py`) — no raw `is_staff` checks. Draft vs published is an `is_published` flag reconciled in code (`reconcile_publish_states`), shown as "Draft" badges to admins only. Django admin at `/admin/` handles structured data; on-page admin handles photos/activities/events.
