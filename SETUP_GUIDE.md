Bandhu Project – Complete Local Setup Guide

This guide explains how to set up the Bandhu Django project from scratch on Windows or macOS.

📋 Prerequisites Checklist
Make sure you have the following installed:

✅ Python 3.9+
✅ MySQL Server 8.4+ (running)
✅ pip & virtualenv
✅ Git
✅ Terminal / Command Prompt access

🧭 Step-by-Step Setup

1️⃣ Clone the Repository

Windows & macOS
git clone https://github.com/bandhu-odisha/Bandhu
cd Bandhu

2️⃣ Create & Activate Virtual Environment

Windows
python -m venv venv
venv\Scripts\activate

You should see (venv) in your prompt.

macOS
python3 -m venv venv
source venv/bin/activate


You should see (venv) in your prompt.

3️⃣ Install MySQL Server

Windows
Download: https://dev.mysql.com/downloads/installer/
Choose Developer Default or Full
Set root password
Keep MySQL running as a Windows service
Verify: mysql --version
If not recognized, add MySQL to PATH:
C:\Program Files\MySQL\MySQL Server 8.4\bin


macOS
Option A: Homebrew (Recommended)
brew install mysql
brew services start mysql

Option B: Official MySQL Installer
Download macOS DMG from MySQL website
Add to PATH:
echo 'export PATH="/usr/local/mysql/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile

4️⃣ Install MySQL Client Dependencies (macOS Only)

❌ Skip this step on Windows

brew install mysql-client pkg-config

Add environment variables:

echo 'export PATH="/opt/homebrew/opt/mysql-client/bin:$PATH"' >> ~/.zprofile
echo 'export LDFLAGS="-L/opt/homebrew/opt/mysql-client/lib"' >> ~/.zprofile
echo 'export CPPFLAGS="-I/opt/homebrew/opt/mysql-client/include"' >> ~/.zprofile
echo 'export PKG_CONFIG_PATH="/opt/homebrew/opt/mysql-client/lib/pkgconfig"' >> ~/.zprofile
source ~/.zprofile

5️⃣ Create Database & User

Both Windows & macOS

CREATE DATABASE bandhu_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'bandhu_user'@'localhost'
  IDENTIFIED BY 'your_password';

GRANT ALL PRIVILEGES ON bandhu_db.* TO 'bandhu_user'@'localhost';
FLUSH PRIVILEGES;

EXIT;

6️⃣ Install Python Dependencies

Windows & macOS

python -m pip install --upgrade pip wheel
pip install mysqlclient
pip install -r requirements.txt

Verify: python -c "import django; print(django.get_version())"
Expected: 2.2.13

| Package      | Version                        |
| ------------ | ------------------------------ |
| Django       | 2.2.13                         |
| numpy        | ≥ 1.19 (tested with **2.0.2**) |
| mysqlclient  | ≥ 2.2.7                        |
| Pillow       | ≥ 8.0 (tested with **11.3.0**) |
| cryptography | ≥ 3.4.8 (tested with **46.x**) |
| cffi         | ≥ 1.15                         |

✅ These versions avoid compilation errors on macOS ARM (M1/M2/M3/M4).

Verify: python -c "import django; print(django.get_version())"
Expected: 2.2.13

7️⃣ Configure Environment Variables (.env)

Generate Django SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"

Sample .env (Same for Windows & macOS)
SECRET_KEY=your-generated-key
DEBUG=True
ALLOWED_HOSTS=['localhost', '127.0.0.1']

DB_NAME=bandhu_db
DB_USER=bandhu_user
DB_PASS=your_password
DB_HOST=localhost

EMAIL_USE_SSL=True
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=test@example.com
EMAIL_HOST_PASSWORD=test
EMAIL_PORT=465
SENDER_EMAIL=test@example.com
ADMINS_EMAIL=['admin@example.com']

SOCIAL_AUTH_FACEBOOK_KEY=
SOCIAL_AUTH_FACEBOOK_SECRET=
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=
SENDGRID_API_KEY=

STATIC_URL=/static/
MEDIA_URL=/media/
STATIC_ROOT=/absolute/path/to/staticfiles
MEDIA_ROOT=/absolute/path/to/media


⚠️ Replace paths with your actual local project path

8️⃣ Run Database Migrations
python manage.py migrate

9️⃣ Create Superuser (Recommended)
python manage.py createsuperuser

Required to access Django Admin.

🔟 Import Production Data (IMPORTANT)

⚠️ Without data, most pages will be empty

Option A: SQL Dump (Preferred)
mysql -u bandhu_user -p bandhu_db < bandhu_dump.sql

Option B: Django Fixtures
python manage.py loaddata production_data.json

Option C: Media Files

Copy production media/ folder into your local MEDIA_ROOT

1️⃣1️⃣ Verify Setup

python manage.py check
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Database connected!')"

1️⃣2️⃣ Start Development Server
python manage.py runserver

🌐 Open:

Homepage: http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/

🔁 Daily Development Workflow

cd Bandhu
source venv/bin/activate   # macOS
venv\Scripts\activate      # Windows
python manage.py runserver

✅ Setup Complete 🎉

You’re now ready to develop locally on Bandhu 🚀