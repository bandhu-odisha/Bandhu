Prerequisites

Ensure the following are installed before starting:

1. Python 3.6+
2.Docker Desktop

🚀 Getting Started

1. Clone the Repository
git clone https://github.com/bandhu-odisha/Bandhu
cd Bandhu

2. Create & Activate Virtual Environment
python -m venv venv
.\venv\Scripts\Activate.ps1

3. Install Dependencies
pip install -r requirements.txt

4. Start Docker Desktop

Wait until the 🐳 whale icon is steady.

Verify Docker: docker ps

🗄️ Database Setup

5. Start MySQL Container
docker-compose up -d

6. Import Database Dump

Place bandhu_odisha_new.sql.gz on your Desktop

Run: .\scripts\import-db.ps1

⚠️ If PowerShell blocks the script:

Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

Re-run the import command afterward.

⚙️ Environment Configuration

7. Configure .env File
copy .env.example .env

Edit .env and set the following (use absolute paths):

SECRET_KEY=your-secret-key
STATIC_ROOT=absolute/path/to/static
MEDIA_ROOT=absolute/path/to/media

🖼️ Media Files

Steps to Download Media Files from cPanel

1. Log in to cPanel
2. Open File Manager
3. Navigate to the project’s media/ directory
4. Select the entire media folder
5. Click Compress
6. Choose ZIP Archive
7. Download the generated media.zip file to your local system


Extract Media Files Locally 

Place media.zip in the project root and run: Expand-Archive -Path "media.zip" -DestinationPath "." -Force


✅ After extraction, ensure the structure is:

Bandhu/
 ├── media/
 ├── static/
 ├── manage.py

▶️ Running the Application

8. Apply Migrations
python manage.py migrate

9. Start Development Server
python manage.py runserver

Open in browser:
👉 http://127.0.0.1:8000/