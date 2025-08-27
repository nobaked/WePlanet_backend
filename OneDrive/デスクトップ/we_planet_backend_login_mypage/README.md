# We Planet Backend (FastAPI, Azure MySQL)

## Quick Start

```bash
cd backend
python -m venv .venv
# Windows:
. .venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt

# 1) Create .env from example and fill Azure MySQL info & CORS
# Windows:
copy .env.example .env
# macOS/Linux:
# cp .env.example .env

# 2) Put DigiCertGlobalRootCA.crt.pem into backend/certs and set DB_SSL_CA path in .env

# 3) Run API
uvicorn app.main:app --reload --port 8000

# 4) Check
# GET http://localhost:8000/health
```

## Alembic

```bash
cd backend
alembic revision -m "init"
alembic upgrade head
```
