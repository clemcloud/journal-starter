# ☁️ Journal API — Cloud Deployment on AWS

<div align="center">

![AWS](https://img.shields.io/badge/AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![EC2](https://img.shields.io/badge/EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu_20.04-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Amazon Bedrock](https://img.shields.io/badge/Amazon_Bedrock-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)

This document covers the full cloud deployment of the Journal API onto AWS — from network design to a live HTTPS endpoint powered by Amazon Bedrock.

**Live API:** [https://journal-starter.duckdns.org/docs](https://journal-starter.duckdns.org/docs)  
**Author:** Umoru Clement — Cloud Engineer  
**GitHub:** [@clemcloud](https://github.com/clemcloud)  
**LinkedIn:** [clementcloud](https://www.linkedin.com/in/clementcloud)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Step 1 — Network Design](#step-1--network-design)
- [Step 2 — VPC and Security Groups](#step-2--vpc-and-security-groups)
- [Step 3 — Database Server Setup](#step-3--database-server-setup)
- [Step 4 — API Server Setup](#step-4--api-server-setup)
- [Step 5 — Exposing the API over HTTPS](#step-5--exposing-the-api-over-https)
- [Step 6 — AI Integration with Amazon Bedrock](#step-6--ai-integration-with-amazon-bedrock)
- [API Endpoints](#api-endpoints)
- [Challenges Faced](#challenges-faced)
- [What I Learned](#what-i-learned)
- [Key Engineering Decisions](#key-engineering-decisions)
- [What's Next](#whats-next)

---

## 🔍 Overview

The Journal API was deployed to AWS using two EC2 instances running Ubuntu 20.04 LTS — one in a public subnet serving the FastAPI application behind Nginx, and one in a private subnet running PostgreSQL. Traffic is encrypted end-to-end via a TLS certificate from Let's Encrypt, the domain is managed through DuckDNS, and AI analysis is powered by Amazon Bedrock using the Nova Lite model.

The deployment follows a classic two-tier architecture — API layer in a public subnet, database layer in a private subnet — with strict firewall rules controlling traffic at every layer.

### Deployment Summary:

| Component | Technology | Details |
|-----------|-----------|---------|
| **API Server** | EC2 t3.micro | Ubuntu 20.04 LTS, Public Subnet |
| **Database Server** | EC2 t3.micro | Ubuntu 20.04 LTS, Private Subnet |
| **Web Server** | Nginx | Reverse proxy + TLS termination |
| **TLS Certificate** | Let's Encrypt + Certbot | Auto-renewed |
| **Domain** | DuckDNS | Free subdomain |
| **AI Model** | Amazon Bedrock | Nova Lite |
| **Process Manager** | systemd | Keeps API running |

---

## 🏗️ Architecture

The architecture was designed in **Lucidchart** before any AWS resource was provisioned. Every subnet, security group, and traffic flow was mapped out first.

> 📸 _[Add Architecture Diagram screenshot here]_

### Traffic Flow:

```
Internet
    │
    ▼  Port 443 (HTTPS)
  Nginx — Reverse Proxy
    │
    ▼  Port 8000
  FastAPI Application
    │
    ▼  Port 5432
  PostgreSQL — Private Subnet
```

### Network Layout:

```
┌──────────────────────────────────────────────────────────────┐
│                         AWS VPC                              │
│                      (10.0.0.0/16)                           │
│                                                              │
│  ┌───────────────────────┐    ┌───────────────────────────┐  │
│  │    Public Subnet      │    │     Private Subnet        │  │
│  │    10.0.1.0/24        │    │     10.0.2.0/24           │  │
│  │                       │    │                           │  │
│  │  ┌─────────────────┐  │    │  ┌─────────────────────┐  │  │
│  │  │  API EC2        │  │    │  │  DB EC2             │  │  │
│  │  │  t3.micro       │  │    │  │  t3.micro           │  │  │
│  │  │  Ubuntu 24.04   │  │    │  │  Ubuntu 24.04       │  │  │
│  │  │  FastAPI+Nginx  │  │    │  │  PostgreSQL         │  │  │
│  │  │  Public IP ✅   │  │    │  │  No Public IP ✅    │  │  │
│  │  └─────────────────┘  │    │  └─────────────────────┘  │  │
│  └───────────────────────┘    └───────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## Step 1 — Network Design

Before touching the AWS console the full architecture was designed in Lucidchart covering:

- VPC CIDR range: `10.0.0.0/16`
- Public subnet for the API: `10.0.1.0/24`
- Private subnet for the database: `10.0.2.0/24`
- Firewall rules for each subnet including SSH access for management
- Full traffic flow: Internet → port 443 → port 8000 → port 5432
- SSH access to the private database VM via the public API VM as a jump box
- The private subnet uses the NAT gateway to access the internet using a public ip . It is placed in the public subnet to enable its reach into the internet via the internet gateway.

The database VM has no public IP — the only way to reach it is through the API server. This was a deliberate design decision to keep the database completely isolated from the internet.

![cloud infrastructure image](./images/cloud.png)
## Step 2 — VPC and Security Groups

Two EC2 instances were provisioned — one in each subnet. Security groups act as virtual firewalls controlling exactly what traffic can reach each server.

### API Server Security Group (Public Subnet):

| Type | Protocol | Port | Source |
|------|----------|------|--------|
| SSH | TCP | 22 | Your IP only |
| HTTP | TCP | 80 | 0.0.0.0/0 |
| HTTPS | TCP | 443 | 0.0.0.0/0 |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 |

### Database Server Security Group (Private Subnet):

| Type | Protocol | Port | Source |
|------|----------|------|--------|
| SSH | TCP | 22 | Public Subnet only (10.0.1.0/24) |
| PostgreSQL | TCP | 5432 | Public Subnet only (10.0.1.0/24) |

The database is only reachable from the API subnet — not from the internet. This is enforced at the security group level.



## Step 3 — Database Server Setup

A t3.micro EC2 instance running Ubuntu 24.04 LTS was provisioned in the private subnet. Since it has no public IP, initial setup was done via SSH through the API server as a jump box.

### Install PostgreSQL:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
```

### Start and enable PostgreSQL:

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Create the database and a dedicated user:

```bash
sudo -u postgres psql
```

Inside the PostgreSQL shell:

```sql
CREATE DATABASE journal_starter;
CREATE USER journal_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE journal_starter TO journal_user;
\q
```

### Run the schema migration:

```bash
sudo -u postgres psql -d journal_starter -f database_setup.sql
```

### Grant permissions on schema and tables:

```sql
GRANT ALL ON SCHEMA public TO journal_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO journal_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO journal_user;
```

### Configure PostgreSQL for remote access:

Edit `postgresql.conf` to allow connections from outside localhost:

```bash
sudo nano /etc/postgresql/16/main/postgresql.conf
```

Find and update:

```
listen_addresses = '*'
```

Edit `pg_hba.conf` to allow connections from the API subnet:

```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

Add this line:

```
host    journal_starter    journal_user    10.0.1.0/24    md5
```

### Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```
![Postgres image](./images/postgres1.jpeg)


![Postgres image](./images/postgres2.jpeg)

![Postgres image](./images/postgres3.jpeg)
## Step 4 — API Server Setup

A t3.micro EC2 instance running Ubuntu 24.04 LTS was provisioned in the public subnet with a public IP. The Journal API runs as a background systemd service — meaning it starts automatically on boot and restarts if it crashes.

### Install dependencies:

```bash
sudo apt update
sudo apt install git python3 python3-pip -y
```

### Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

### Clone the repository:

```bash
git clone https://github.com/clemcloud/journal-starter.git
cd journal-starter
uv sync
```

### Configure environment variables:

```bash
nano .env
```

```env
DATABASE_URL=postgresql://journal_user:your_secure_password@db-private-ip:5432/career_journal
OPENAI_API_KEY=your_bedrock_key
OPENAI_BASE_URL=your_bedrock_endpoint
OPENAI_MODEL=amazon.nova-lite-v1:0
```

### Run as a systemd background service:

```bash
sudo nano /etc/systemd/system/journal.service
```

```ini
[Unit]
Description=Journal API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/journal-starter
Environment="PYTHONPATH=/home/ubuntu/journal-starter"
Environment="PATH=/home/ubuntu/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
ExecStart=/home/ubuntu/.cargo/bin/uv run uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable journal
sudo systemctl start journal
```

### Smoke test:

```bash
curl http://localhost:8000/entries
```

![instances](./images/instances.jpeg)

## Step 5 — Exposing the API over HTTPS

With the API running on port 8000, the next step was to put Nginx in front of it as a reverse proxy and secure everything with a TLS certificate from Let's Encrypt via a DuckDNS domain.

### Install Nginx:

```bash
sudo apt update
sudo apt install nginx -y
```

### Start and enable Nginx:

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

Verify by visiting `http://EC2_PUBLIC_IP` — you should see the Nginx welcome page.

### Configure Nginx as a reverse proxy:

```bash
sudo nano /etc/nginx/sites-available/default
```

Replace the contents with:

```nginx
server {
    server_name journal-starter.duckdns.org;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

The default file controls the domain name, ports, and proxy behavior — it tells Nginx to forward all incoming requests to the FastAPI app running on port 8000.

### Test Nginx syntax and restart:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### Set up DuckDNS domain:

1. Go to [duckdns.org](https://www.duckdns.org) and log in
2. Create a subdomain — `journal-starter.duckdns.org`
3. Update the IP to your EC2 public IP
4. Your domain is now pointing to your server

![ducks-domain](./images/duckdns.png)

### Install Certbot and generate a TLS certificate:

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx
```
![certbot](./images/certbot.jpeg)

![Tls handshake](./images/tls.jpeg)

Certbot automatically detects your Nginx config, generates a certificate from Let's Encrypt, and updates the Nginx config to serve HTTPS traffic — all in one command.

### Verify HTTPS is working:

```bash
curl -v https://journal-starter.duckdns.org/entries
```

### Access the API from the browser:

```
https://journal-starter.duckdns.org/docs
```

![nginx image](./images/nginx.jpeg)

![curl-request](./images/duckjournal.jpeg)


## Step 6 — AI Integration with Amazon Bedrock

The AI analysis endpoint was migrated from GitHub Models to **Amazon Bedrock** using the **Amazon Nova Lite** model. Because the Journal API uses the OpenAI SDK interface, the migration only required updating the environment variables — no code changes needed.

### Enable Model Access:

1. Go to **AWS Console → Amazon Bedrock → Model Access**
2. Request access to **Amazon Nova Lite**
3. Wait for approval — request early as this can take time

### Update environment variables on the API server:

```bash
nano .env
```

```env
OPENAI_BASE_URL=https://bedrock-runtime.your-region.amazonaws.com
OPENAI_API_KEY=your_aws_key
OPENAI_MODEL=amazon.nova-lite-v1:0
```

### Restart the service:

```bash
sudo systemctl restart journal
```

### Test the AI analysis endpoint:

```bash
curl -X POST https://journal-starter.duckdns.org/entries/{entry_id}/analyze
```

> 📸 _[Add Amazon Bedrock screenshot here]_

---

## 🔌 API Endpoints

All endpoints are live at `https://journal-starter.duckdns.org`

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| `POST` | `/entries` | Create a new journal entry | 201 |
| `GET` | `/entries` | Get all journal entries | 200 |
| `GET` | `/entries/{entry_id}` | Get a single entry by ID | 200 / 404 |
| `PATCH` | `/entries/{entry_id}` | Partially update an entry | 200 / 404 |
| `DELETE` | `/entries/{entry_id}` | Delete a single entry | 200 / 404 |
| `DELETE` | `/entries` | Delete all entries | 200 |
| `POST` | `/entries/{entry_id}/analyze` | AI analysis of an entry | 200 / 404 |

### POST /entries

```bash
curl -X POST https://journal-starter.duckdns.org/entries \
  -H "Content-Type: application/json" \
  -d '{
    "work": "Deploying journal to aws",
    "struggle": "Bedrock integration",
    "intention": "Better deployment"
  }'
```

![proof it works](./images/proof.jpeg)
### GET /entries

```bash
curl https://journal-starter.duckdns.org/entries
```

![all entries](./images/allentries.jpeg)


### GET /entries/{entry_id}

```bash
curl https://journal-starter.duckdns.org/entries/{entry_id}
```

![all entries](./images/getentry.jpeg)

### PATCH /entries/{entry_id}

```bash
curl -X PATCH https://journal-starter.duckdns.org/entries/{entry_id} \
  -H "Content-Type: application/json" \
  -d '{"work": "Deployed Journal API to AWS successfully"}'
```

![update-entry](./images/updatentry.jpeg)

### DELETE /entries/{entry_id}

```bash
curl -X DELETE https://journal-starter.duckdns.org/entries/{entry_id}
```
![delete-entry](./images/deletentry.png)
### POST /entries/{entry_id}/analyze

```bash
curl -X POST https://journal-starter.duckdns.org/entries/{entry_id}/analyze
```

> 📸 _[Add POST /analyze screenshot here]_

---

## 🧱 Challenges Faced

Every deployment has friction — here are the real challenges encountered and how they were solved:

---

### Challenge 1 — PostgreSQL Not Accepting Remote Connections

**Problem:** The API server could not connect to PostgreSQL on the database server even though the security group allowed port 5432.

**Root Cause:** PostgreSQL by default only listens on `localhost` — it ignores all external connection attempts regardless of firewall rules.

**Solution:** Two config files needed to be updated:
- `postgresql.conf` — changed `listen_addresses` from `localhost` to `*`
- `pg_hba.conf` — added an entry to allow connections from the API subnet (`10.0.1.0/24`)

**Lesson:** Network-level access (security groups) and application-level access (PostgreSQL config) are two separate layers — both must be configured correctly.

---

### Challenge 2 — Permission Denied After Schema Migration

**Problem:** After running `database_setup.sql` as the `postgres` superuser, the dedicated `journal_user` could not read or write to the tables.

**Root Cause:** In PostgreSQL, creating a database and granting privileges on it does not automatically grant access to tables created by a different user. The schema and table permissions must be granted separately.

**Solution:** Explicitly granted permissions on the schema and all tables:

```sql
GRANT ALL ON SCHEMA public TO journal_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO journal_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO journal_user;
```

**Lesson:** PostgreSQL has a layered permission model — database → schema → tables → sequences. All layers need to be considered.

---

### Challenge 3 — Nginx Redirect Causing Verifier Failure

**Problem:** The automated verifier checking `GET /entries` was failing even though the endpoint was working in the browser.

**Root Cause:** FastAPI redirects `/entries/` (with trailing slash) to `/entries` (without) with a 307 redirect. The verifier does not follow redirects and expects a direct 200 OK.

**Solution:** Used `/entries` without a trailing slash in all curl commands and verified the Nginx config was not adding any redirects.

**Lesson:** Always test with curl `-v` to see the exact status codes and headers — browser behavior hides redirects that automated tools will catch.

---

### Challenge 4 — API Not Surviving Server Restart

**Problem:** After restarting the EC2 instance, the API was no longer running and had to be started manually.

**Root Cause:** The API was being run directly in the terminal — not as a managed service.

**Solution:** Configured the API as a **systemd service** with `Restart=always` so it starts automatically on boot and restarts on failure.

**Lesson:** In production, applications must be managed by a process supervisor — never run them directly in a terminal session.

---

### Challenge 5 — Amazon Bedrock Model Access Delay

**Problem:** The Bedrock API returned access denied errors immediately after requesting model access.

**Root Cause:** Amazon Bedrock model access is not instant — it requires manual approval which can take time.

**Solution:** Requested access early in the deployment process and tested with GitHub Models in the meantime.

**Lesson:** Always check if your cloud AI service requires approval before building around it — plan for approval delays.

---

## 📚 What I Learned

This deployment was not just about following steps — it surfaced real engineering concepts that only become clear when you're working with live infrastructure:

---

### Networking Goes Deeper Than Expected

Designing the VPC before touching the console forced me to think through every connection — which servers need to talk to each other, on which ports, and from which direction. The difference between public and private subnets is not just a label — it changes everything about how traffic flows and how secure your infrastructure is.

---

### Security is Layered — Not a Single Switch

I quickly learned that security groups alone are not enough. PostgreSQL has its own access control system (`pg_hba.conf`), and the application has its own permission model. Security at the network level, the database level, and the application level are three separate things that all need to be configured correctly. Missing any one layer breaks the system.

---

### Designing Before Building Saves Time

Spending time on the architecture diagram in Lucidchart before provisioning any resources meant I never had to backtrack and redesign the network. Every resource was placed correctly the first time because the plan was already clear.

---

### systemd is Essential for Production

Running an application directly in a terminal is fine for local development — it has no place in production. Configuring the API as a systemd service taught me how Linux manages long-running processes, how to set environment variables securely, and how to ensure services survive reboots and failures automatically.

---

### TLS is Not Optional

Seeing `https://` in the browser after configuring Certbot was genuinely satisfying — but more importantly it showed me how quickly a certificate can be provisioned with the right tools. Let's Encrypt and Certbot make TLS accessible. There is no reason to serve production traffic over plain HTTP.

---

### Cloud AI Services Have Their Own Complexity

Migrating from GitHub Models to Amazon Bedrock showed me that the interface (OpenAI SDK) can stay the same even when the underlying provider changes — the abstraction is the value. It also showed me that managed AI services have their own access control, approval processes, and configuration requirements that need to be planned for.

---

## 🎯 Key Engineering Decisions

These are the deliberate decisions made during this deployment and why:

| Decision | Reason |
|----------|--------|
| **Private subnet for PostgreSQL** | Database should never be directly reachable from the internet |
| **No public IP on DB server** | Eliminates an entire attack surface — only reachable via jump box |
| **systemd for process management** | Ensures the API survives reboots and crashes without manual intervention |
| **Nginx as reverse proxy** | Separates TLS termination from the application — cleaner architecture |
| **DuckDNS for domain** | Free, fast, and sufficient for a demo — no need for a paid domain |
| **Let's Encrypt for TLS** | Free, trusted, auto-renewing certificates — no reason not to use it |
| **Amazon Bedrock over GitHub Models** | Cloud-native AI on the same platform as the infrastructure |
| **Dedicated database user** | Never use the superuser for application connections — least privilege |

---

## 🔜 What's Next

This deployment is Phase 2 of the Journal API project. The next phases are:

- **Phase 3 — Production DevOps** — Dockerfile, Kubernetes manifests, GitHub Actions automated deployments, Prometheus and Grafana observability
- **Phase 4 — Security** — JWT authentication, rate limiting, security scanning, secrets management

→ Back to [main README](../README.md)

---

## 👨‍💻 Author

**Umoru Clement — Cloud Engineer**

- GitHub: [@clemcloud](https://github.com/clemcloud)
- LinkedIn: [clementcloud](https://www.linkedin.com/in/clementcloud)

---

<div align="center">

⭐ **If you found this project helpful, please give it a star!** ⭐

</div>