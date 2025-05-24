## 📘 DEVOPS\_NOTES.md – EC2 + RDS Deployment Summary for EquityTracker

**Project:** EquityTracker – Backend (FastAPI + Docker + RDS + GitHub Actions)

---

### ✅ 1. AWS RDS Setup (PostgreSQL)

* Created RDS instance: `equitytracker-db`
* Engine: PostgreSQL 15.x
* Enabled Public Access
* Security group rule: Inbound port **5432** open to EC2 and local IP
* Verified with:

  ```bash
  psql -h <RDS_ENDPOINT> -U postgres -d equitytracker_db
  ```

---

### ✅ 2. FastAPI App Update for RDS

* Used `DATABASE_URL` environment variable:

  ```env
  DATABASE_URL=postgresql+asyncpg://<USER>:<PASSWORD>@<RDS_ENDPOINT>:5432/equitytracker_db
  ```
* Updated `db.py`:

  ```python
  from sqlalchemy.ext.asyncio import create_async_engine
  import os
  DATABASE_URL = os.environ.get("DATABASE_URL")
  engine = create_async_engine(DATABASE_URL, echo=True)
  ```

---

### ✅ 3. GitHub Actions CI/CD Secret Injection

* Updated `.github/workflows/deploy.yml`:

  ```yaml
  docker run -d -p 8000:8000 \
    -e FINNHUB_API_KEY=${{ secrets.FINNHUB_API_KEY }} \
    -e DATABASE_URL=${{ secrets.DATABASE_URL }} \
    --name equitytracker-container equitytracker-backend
  ```
* Secrets stored:

  * `EC2_KEY`, `EC2_USER`, `EC2_HOST`
  * `FINNHUB_API_KEY`, `DATABASE_URL`

---

### ✅ 4. Docker Build & Containerization

* Cleared stale containers:

  ```bash
  docker stop equitytracker-container
  docker rm equitytracker-container
  ```
* Built & ran manually:

  ```bash
  docker build -t equitytracker-backend .
  docker run -d -p 8000:8000 \
    -e FINNHUB_API_KEY=... \
    -e DATABASE_URL=... \
    --name equitytracker-container equitytracker-backend
  ```

---

### ✅ 5. Alembic Migrations on RDS

* Created `db_sync.py` with SQLAlchemy sync engine
* Modified `alembic/env.py`:

  ```python
  from app.db_sync import Base
  from sqlalchemy import create_engine
  url = os.environ.get("DATABASE_URL")
  connectable = create_engine(url, poolclass=pool.NullPool)
  ```
* Installed tools:

  ```bash
  sudo apt install python3.10-venv
  pip install python-dotenv psycopg2-binary alembic
  ```
* Ran migrations:

  ```bash
  alembic upgrade head
  ```

---

### ✅ 6. Validation & Testing

* Swagger UI: `http://<EC2_PUBLIC_IP>:8000/docs`
* Inserted & queried Watchlist entries via:

  * Swagger `/watchlist`
  * `psql` CLI

---

### 🔐 Final GitHub Secrets Used

| Key               | Description                     |
| ----------------- | ------------------------------- |
| `EC2_HOST`        | Public IP of EC2 instance       |
| `EC2_USER`        | EC2 login username (ubuntu)     |
| `EC2_KEY`         | Private SSH key                 |
| `FINNHUB_API_KEY` | API key for live stock data     |
| `DATABASE_URL`    | RDS URL string (asyncpg format) |

---

### 📌 Outcome

* ✅ Backend live on EC2, connected to Amazon RDS
* ✅ Watchlist table and CRUD verified
* ✅ GitHub Actions auto-deploy functional
* ✅ Clean separation of `.env` vs production secrets
* ✅ Docker-based isolation & reproducibility

---
