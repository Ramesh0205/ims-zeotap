# 🚨 Incident Management System (IMS)
### Zeotap Infrastructure / SRE Intern Assignment
**Author:** Ramesh Mandala  
**GitHub:** [YOUR_GITHUB_LINK_HERE]

---

## 🏗️ Architecture Diagram

```
                        ┌─────────────────────────────────────────────────────┐
                        │                  IMS ARCHITECTURE                    │
                        └─────────────────────────────────────────────────────┘

  Signal Sources                  Backend Engine                   Storage Layer
  ─────────────     ──────────────────────────────────────────    ─────────────
  APIs            →  Rate Limiter (500 req/s)                  →  MongoDB
  MCP Hosts       →  In-Memory Buffer (Queue 50k)              →  (Raw Signals / Audit Log)
  Caches          →  Signal Processor (Async Worker)           →
  Queues          →  Debounce Logic (10s window)               →  PostgreSQL
  RDBMS           →  Strategy Pattern (Alert Priority)         →  (Work Items / RCA)
  NoSQL           →  State Machine (Incident Lifecycle)        →
                  →  Metrics Reporter (every 5s)               →  Redis
                                                                →  (Hot Cache / Dashboard)
  Frontend
  ─────────
  React Dashboard → REST API → FastAPI Backend
  - Live Feed (auto-refresh 5s)
  - Incident Detail + Raw Signals
  - RCA Form
  - Status Transitions
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Raw Signal Store | MongoDB 7 (NoSQL audit log) |
| Source of Truth | PostgreSQL 15 (Work Items, RCA) |
| Hot Cache | Redis 7 (Dashboard state) |
| Frontend | React 18 |
| Containerization | Docker + Docker Compose |

---

## 🚀 Setup & Run (One Command)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/ims-zeotap.git
cd ims-zeotap

# 2. Start everything
docker-compose up --build

# 3. Open Dashboard
http://localhost:3000

# 4. API Docs
http://localhost:8000/docs

# 5. Health Check
http://localhost:8000/health
```

---

## 🧪 Simulate Failures

```bash
# Install httpx
pip3 install httpx

# Run simulation (RDBMS outage + Cache failure + MCP failure)
python3 scripts/mock_failure.py
```

---

## 📐 Design Patterns Used

### 1. Strategy Pattern — Alert Priority
Different components get different alert priorities automatically:
- RDBMS → P0 CRITICAL
- API / MCP / QUEUE → P1 HIGH  
- CACHE / NOSQL → P2 WARNING

### 2. State Pattern — Incident Lifecycle
```
OPEN → INVESTIGATING → RESOLVED → CLOSED
```
- Cannot skip states
- Cannot CLOSE without RCA (enforced at API level)
- MTTR calculated automatically on RESOLVED

---

## 🛡️ How Backpressure is Handled

The system uses a **3-layer backpressure strategy:**

1. **Rate Limiter** — Rejects requests above 500/sec with HTTP 429
2. **In-Memory Queue** — asyncio.Queue(maxsize=50000) absorbs burst traffic up to 10,000 signals/sec without crashing even if databases are slow
3. **Async Worker** — Background task drains the queue independently from the API, so the ingestion API never blocks on DB writes

If the queue fills up, the oldest signal is dropped (configurable) and a warning is logged.

---

## 🔒 Security (Bonus)
- CORS configured for controlled origins in production
- Rate limiting prevents DDoS on ingestion API
- Environment variables for all secrets (never hardcoded)
- Input validation via Pydantic schemas

## 📊 Observability
- `/health` endpoint checks all 3 databases
- Throughput metrics printed to console every 5 seconds
- All signal ingestion logged with timestamps

## ✅ RCA Enforcement
- System rejects CLOSED transition if RCA is missing
- RCA requires: start time, end time, category, fix applied (min 10 chars), prevention steps (min 10 chars)
- MTTR auto-calculated from first signal to resolution

---

## 🧪 Run Unit Tests

```bash
cd backend
pip3 install -r requirements.txt
pytest tests/ -v
```
