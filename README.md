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

On the server:

```bash
cd /path/to/Bandhu
git pull origin master
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
# restart the app server (command depends on hosting)
```

Verify the live site and `/admin/` after deploy. Production uses MySQL and `DEBUG=False`; env vars live on the server only.

SSH access, server paths, and restart commands are maintained by the project maintainers.

---

## Other documentation

How to access production data, database table designs, and model-level docs are maintained separately by the development team. For media, use cPanel as above; for a database dump, ask a maintainer.
