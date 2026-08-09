# Secure deployment guide

## 1. Backend
Set environment variables:
APP_SECRET=<long random secret>
ADMIN_USER=<your admin username>
ADMIN_PASSWORD=<strong unique password>
DB_PATH=data.db
UPLOAD_DIR=uploads

Run:
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

## 2. Frontend
Open frontend/index.html. Before use, set the API URL in browser localStorage:
localStorage.setItem('MM_API','https://YOUR-BACKEND-DOMAIN')
Then refresh.

## 3. Important production notes
- Do not use the demo/default secret or password.
- Put the API behind HTTPS.
- Restrict CORS to the real frontend domain.
- Use persistent storage for the database and uploaded images on the hosting provider.
- Add email notification provider if desired.
- For high-security production, add password hashing, rate limiting, CSRF strategy where applicable, file-type/size validation, audit logging and backups.
