# 📘 DEVOPS\_NOTES.md – EquityTracker Backend DevOps Setup

This document summarizes all DevOps work completed for the EquityTracker backend project.
It includes setup steps, commands, tools used, and explanations to help with revision, collaboration, and recruiter transparency.

---

## ✅ 1. EC2 Server Setup (AWS Free Tier)

**Actions:**

* Created a t2.micro EC2 instance in **Canada (Central)** region
* Selected Ubuntu Server 22.04 LTS
* Created SSH key pair: `equitytracker-key.pem`
* Opened ports in Security Group:

  * TCP 22 (SSH)
  * TCP 8000 (FastAPI dev server)

**Commands Used (on local machine):**

```bash
ssh -i equitytracker-key.pem ubuntu@<EC2_PUBLIC_IP>
```

**On EC2:**

```bash
sudo apt update
sudo apt install docker.io git python3-pip -y
```

---

## ✅ 2. FastAPI Backend Manual Deployment

**Created minimal FastAPI app:**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "EquityTracker backend running on EC2!"}
```

**Run server manually:**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Tested in browser:**

```
http://<EC2_PUBLIC_IP>:8000/
```

---

## ✅ 3. Dockerize Backend App

**Dockerfile created in `/backend` folder:**

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**.dockerignore created to exclude unnecessary files:**

```dockerignore
__pycache__/
*.pyc
*.log
*.env
*.pem
.dockerignore
Dockerfile
.vscode/
.git/
tests/
```

**requirements.txt:**

```txt
fastapi==0.110.0
uvicorn==0.29.0
```

**Build and Run Docker container:**

```bash
docker build -t equitytracker-backend .
docker run -d -p 8000:8000 --name equitytracker-container equitytracker-backend
```

---

## ✅ 4. GitHub Secrets Setup

**Created the following secrets in GitHub → Settings → Secrets → Actions:**

* `EC2_HOST` → public IP of EC2 instance
* `EC2_USER` → `ubuntu`
* `EC2_KEY` → contents of `equitytracker-key.pem`

---

## ✅ 5. GitHub Actions CI/CD Deployment

**Workflow file: `.github/workflows/deploy.yml`**

```yaml
name: Deploy Backend to EC2

on:
  push:
    branches:
      - master

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Setup SSH Key
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.EC2_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa

      - name: Add EC2 to known hosts
        run: ssh-keyscan -H ${{ secrets.EC2_HOST }} >> ~/.ssh/known_hosts

      - name: Deploy to EC2
        run: |
          ssh -i ~/.ssh/id_rsa ${{ secrets.EC2_USER }}@${{ secrets.EC2_HOST }} << 'EOF'
            cd EquityTracker/backend
            git pull origin master
            docker stop equitytracker-container || true
            docker rm equitytracker-container || true
            docker build -t equitytracker-backend .
            docker run -d -p 8000:8000 --name equitytracker-container equitytracker-backend
          EOF
```

**✅ CI/CD test successful** → Every `master` push redeploys backend to EC2.

---
