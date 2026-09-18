# Bandhu

A non-profit organization based in Odisha, working for the upliftment of society.

Website for [Bandhu Odisha](https://www.bandhuodisha.in/) — Django backend, React landing page.

> **Contributors:** keep this README up to date whenever setup or deploy steps change.

---

## 1. Dev, run, test, debug locally

### Setup (first time)

```bat
git clone https://github.com/bandhu-odisha/Bandhu.git
cd Bandhu

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` — set at least `SECRET_KEY`, `STATIC_ROOT`, and `MEDIA_ROOT` to absolute paths on your machine (e.g. `C:\Projects\Bandhu\media`).

```bat
python manage.py migrate
python manage.py create_admin_user
python manage.py import_local_media
```

Local admin login: `admin@bandhu.demo` / `admin123`

Use `DB_ENGINE=sqlite` in `.env` if you don't have MySQL. For production-like data, import a DB dump and set `DB_ENGINE=mysql`.

### Media files (images, uploads)

Production media is **not** in git. To run the site with real photos and files locally:

1. Ask a maintainer for **cPanel login credentials** (provided separately).
2. Log in to cPanel → **File Manager**.
3. Open the site’s **`media`** folder on the server.
4. Download it as a **zip**, then extract the contents into your local `MEDIA_ROOT` folder (the path set in `.env`, e.g. `C:\Projects\Bandhu\media`).
5. Restart `runserver` and hard-refresh the browser.

`python manage.py import_local_media` only copies a few bundled placeholder images — it does **not** replace a full production media download from cPanel.

### Run

```bat
venv\Scripts\activate
python manage.py runserver
```

Site: **http://127.0.0.1:8000/**

If you change the React landing page (`frontend/`):

```bat
cd frontend
npm install
npm run build
cd ..
```

### Test & debug loop

1. Edit code and save.
2. Refresh the browser (hard-refresh after CSS/JS: `Ctrl+Shift+R`).
3. Watch the `runserver` terminal — errors and tracebacks appear there.
4. Repeat.

| Change | Extra step |
|--------|------------|
| Models | `python manage.py makemigrations && python manage.py migrate` |
| Landing page | `npm run build` in `frontend/` |

### Run the test suite

Regression tests live in a `tests/` package inside every app (`accounts/tests/`, `bandhuapp/tests/`, `applications/<app>/tests/`). They use Django's built-in runner and an in-memory SQLite database, so no MySQL or extra packages are needed — the same `.env` you use for `runserver` works (`DB_ENGINE=sqlite`).

> **Your virtualenv must hold the pinned versions.** Django 2.2 requires Python 3.5–3.8. On a newer Python, `pip install -r requirements.txt` silently resolves to a much newer Django, and this project does not run there at all — it uses `force_text`, which Django 4.0 removed. If `python -c "import django; print(django.get_version())"` does not print `2.2.13`, rebuild the venv on Python 3.8 before running the suite.

> **Apple Silicon Macs (M1 and later):** `pip install -r requirements.txt` fails there. Five pins are older than arm64 macOS and have no wheel for it, so pip tries to compile them and the build breaks: `numpy==1.17.4`, `cffi==1.14.0`, `cryptography==2.9.2`, `Pillow==6.2.1`, `mysqlclient==2.0.1`. Don't edit `requirements.txt` (CI and production are Linux, where the pins install fine). Install everything else pinned, then leave out or upgrade those five:
> - `numpy` — nothing in the code imports it; skip it.
> - `mysqlclient` — not needed locally with `DB_ENGINE=sqlite`; skip it.
> - `cffi`, `cryptography`, `Pillow` — install newer versions. A working local venv has `cffi 1.17.1`, `cryptography 47.0.0`, `Pillow 9.5.0`.
>
> ```bash
> grep -viE '^(numpy|mysqlclient|cffi|cryptography|Pillow)==' requirements.txt > /tmp/req-local.txt
> pip install -r /tmp/req-local.txt cffi cryptography "Pillow<10"
> ```
> Afterwards run `python manage.py check` and the test suite. An install that finishes cleanly can still break at import time.

```bash
python manage.py test                       # whole suite
python manage.py test accounts              # one app
python manage.py test bandhuapp.tests.test_landing   # one module
```

The suite never touches the network: SendGrid, YouTube and the production media host are mocked. Uploads go to a temporary `MEDIA_ROOT`. Tests that document a known bug are marked `@unittest.expectedFailure` with the reason in their docstring; flip them to normal tests when the bug is fixed.

Shared fixtures (`make_user`, `make_admin`, `make_profile`, `image_upload`, `TempMediaMixin`) live in `bandhuapp/tests/support.py`; the initiative-program contract tests shared by Prasanta Raktadan Shibir, Patriotism in Action and Odisha Satabdi Sevavrata live in `bandhuapp/tests/initiative_program_support.py`.

GitHub Actions runs the same suite on every push and pull request (`.github/workflows/tests.yml`, Python 3.8 + the pinned `requirements.txt`).

Optional coverage report (install `coverage` into your venv only; it is not a project dependency):

```bash
pip install coverage
coverage run manage.py test && coverage report -m   # omit rules are in .coveragerc
```

---

## 2. Dev loop on the admin page

Content can be edited in two places. Use the same login for both.

**Create / reset admin user:**

```bash
python manage.py create_admin_user --reset-password
```

### Django admin — `/admin/`

For structured data: people, designations, publications, site settings, initiative entries.

1. Go to http://127.0.0.1:8000/admin/
2. Log in (`admin@bandhu.demo` / `admin123` locally).
3. Edit and save a record.
4. Open the public page and confirm the change.

### On-page admin — log in, then browse the site

After logging in at `/accounts/login/`, section pages show extra controls for admin users:

- Upload and approve photos
- Add activities, events, meetings
- See **Draft** badges on unpublished entries
- Add initiative program entries inline

Example pages: `/anandakendra/`, `/bandhughar/`, `/prasanta-raktadan-shibir/`

### Admin dev loop

```
runserver running
  → log in (/admin/ or /accounts/login/)
  → edit content
  → refresh the public page
  → check runserver terminal for errors
  → repeat
```

Unpublished entries stay visible to admins only until marked published.

---

## 3. Deploy to production

Production: **https://www.bandhuodisha.in/**

Before deploy: test locally, commit any new migrations, run `npm run build` if the landing page changed. Never commit `.env`.

On the cPanel:
* Go to "Setup Python App" under the Software category.
* Click on the edit (pencil) icon.
* Copy the command to enter the virtual environment.
* Go back to the cPanel main page and open "Terminal" under the Advanced category at the bottom.
* Paste and run the virtual environment command copied earlier.
* Now, follow the steps below:
  ```bash
  # Pull the latest changes
  git pull origin master

  # If some packages were added, removed or modified
  # pip install -r requirements.txt

  # Run migrations (make sure the `python manage.py makemigrations`
  # command was run locally, and migration files were pushed)
  python manage.py migrate

  # Copy any new static files to the public_html/static folder
  # (only needs to be done if there are any frontend changes)
  python manage.py collectstatic --noinput

  # Fill in any blank Video.duration values (YouTube fetch no longer runs
  # on the request path — see DONE/planning/2026-09-12-home-load-time-improvement/spec.md).
  # Saving a Video in /admin/ now fetches its duration automatically, so this
  # is a one-time backfill for videos added before that hook existed. Run it
  # once after this deploy; no cron needed afterward.
  python manage.py backfill_video_durations

  # Pre-generate the WebP thumbnails the home page serves, so the first real
  # visitor doesn't pay generation cost. Run once after this deploy, and again
  # after a bulk media import.
  python manage.py warm_landing_thumbnails
  ```
* Lastly, go back to the "Setup Python App" and restart the application. 

Verify the live site and `/admin/` after deploy. Production uses MySQL and `DEBUG=False`; env vars live on the server only.

SSH access, server paths, and restart commands are maintained by the project maintainers.

---

## Other documentation

How to access production data, database table designs, and model-level docs are maintained separately by the development team. For media, use cPanel as above; for a database dump, ask a maintainer.
