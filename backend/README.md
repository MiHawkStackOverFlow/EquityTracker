# 📦 EquityTracker – Backend (FastAPI + Docker + AWS)

This is the backend service for **EquityTracker**, a personal finance and stock watchlist web app. It is built with **FastAPI**, containerized using **Docker**, and deployed on **AWS EC2** using a secure **CI/CD pipeline** powered by GitHub Actions.

---

## 🚀 Features

* FastAPI web framework with `/` root endpoint
* Dockerized for consistent cloud deployments
* EC2-hosted for real-world backend exposure
* GitHub Actions pipeline auto-deploys on `master` push

---

## 🛠 Tech Stack

| Layer      | Tech Used           |
| ---------- | ------------------- |
| Language   | Python 3.10         |
| Framework  | FastAPI             |
| Hosting    | AWS EC2 (Free Tier) |
| Container  | Docker              |
| CI/CD      | GitHub Actions      |
| Web Server | Uvicorn (ASGI)      |

---

## ⚙️ Local Development Setup

```bash
# Clone repo and go to backend folder
cd EquityTracker/backend

# (Optional) Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🐳 Docker Instructions

```bash
# From backend folder
cd EquityTracker/backend

# Build Docker image
docker build -t equitytracker-backend .

# Run container
docker run -d -p 8000:8000 --name equitytracker-container equitytracker-backend
```

Test at: `http://localhost:8000/`

---

## 🔐 GitHub Actions CI/CD (Auto-Deploy to EC2)

This project auto-deploys backend to AWS EC2 using:

* `.github/workflows/deploy.yml`
* GitHub Secrets: `EC2_HOST`, `EC2_USER`, `EC2_KEY`, `FINNHUB_API_KEY`, `DATABASE_URL`

Every `master` push triggers remote `git pull`, `docker build`, and `run` on EC2.

---

## 📁 Folder Structure

```
backend/
├── app/
│   └── main.py
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── README.md (this file)
```

---

## 🧠 Credits

This backend was architected with cloud-native design and DevOps best practices in mind to demonstrate:

* Cloud readiness
* Containerization
* Automated infrastructure via GitHub

---

## 🔗 Project Board

See `EquityTracker Dev Board` in GitHub Projects for ongoing task tracking.

---

## 🗃️ PostgreSQL + Watchlist Schema Setup

I integrated **PostgreSQL** using Docker, and added a **Watchlist** table with migration tracking via **Alembic**.

## ▶️ Local DB (Dockerized PostgreSQL bash)

docker run --name equitytracker-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=equitytracker_db -p 5432:5432 -v equitytracker_pgdata:/var/lib/postgresql/data -d postgres:15


## 🔌 DB Connectivity

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=equitytracker_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

## 🧱 Alembic – Migrations

### Create migration (auto-detect Watchlist model)
alembic revision --autogenerate -m "create_watchlist_table"

### Apply migration to DB
alembic upgrade head

### Migrations are stored in:
backend/alembic/versions/


