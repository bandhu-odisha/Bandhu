# Bandhu

A non-profit organization based in Odisha, working for the upliftment of society.

## Local Development Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm (for the frontend)
- Git

### 1. Clone the repo

```bash
git clone https://github.com/<your-org>/Bandhu.git
cd Bandhu
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
# On Windows: venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=dev-secret-key-change-me
DEBUG=True
ALLOWED_HOSTS=["localhost", "127.0.0.1"]
DB_ENGINE=sqlite
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=dev@example.com
EMAIL_HOST_PASSWORD=dev-password
EMAIL_PORT=587
EMAIL_USE_SSL=False
SENDER_EMAIL=dev@example.com
ADMINS_EMAIL=["admin@example.com"]
SENDGRID_API_KEY=dev-sendgrid-key
SOCIAL_AUTH_FACEBOOK_KEY=dummy
SOCIAL_AUTH_FACEBOOK_SECRET=dummy
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=dummy
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=dummy
SOCIAL_AUTH_TWITTER_KEY=dummy
SOCIAL_AUTH_TWITTER_SECRET=dummy
SOCIAL_AUTH_GITHUB_KEY=dummy
SOCIAL_AUTH_GITHUB_SECRET=dummy
STATIC_ROOT=/tmp/bandhu_static
STATIC_URL=/static/
MEDIA_ROOT=/tmp/bandhu_media
MEDIA_URL=/media/
```

Setting `DB_ENGINE=sqlite` uses SQLite so you don't need MySQL installed locally.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/

### 7. (Optional) Create an admin user

```bash
python manage.py createsuperuser
```

Admin panel: http://127.0.0.1:8000/admin/

### 8. (Optional) Frontend — Tailwind/React

The `frontend/` directory has a Vite + React + Tailwind CSS setup:

```bash
cd frontend
npm install
npm run dev
```

This runs a Vite dev server that hot-reloads frontend components.

## Troubleshooting

### `ModuleNotFoundError: No module named 'sendgrid'` (or similar)

You likely ran `pip install -r requirements.txt` which installs outdated packages. Use the command in Step 3 instead.

### `ImportError: cannot import name 'force_text'`

`force_text` was removed in Django 4.0. In any file that imports it, replace:
```python
from django.utils.encoding import force_bytes, force_text
```
with:
```python
from django.utils.encoding import force_bytes, force_str as force_text
```

### `ImportError: cannot import name 'six' from 'django.utils'`

`django.utils.six` was removed in Django 3.0. Replace `six.text_type(...)` calls with `str(...)`.

### `ImproperlyConfigured: Cannot import '<appname>'`

Each app under `applications/` must have `name = 'applications.<appname>'` in its `apps.py`, not just `'<appname>'`.

### `DEFAULT_AUTO_FIELD` warnings

These are harmless. To silence them, add to `bandhu/settings.py`:
```python
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
```
