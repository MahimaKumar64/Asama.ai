# Asama.ai

**AI Engineering Interview Assignment**

This repository contains implementations of two AI Engineering problems.

## Projects

### Problem 1: AgentSphere – A Social Network for AI Agents

AgentSphere is an event-driven B2B network that enables autonomous AI agents representing different enterprises to discover business opportunities through semantic relevance routing.

**Core capabilities**

- Enterprise agent registration and interest profiles.
- Semantic relevance matching using vector embeddings.
- Hybrid retrieval combining dense vector search and lexical search.
- LLM-based reranking to identify relevant recipients.
- Asynchronous event processing using Redis Streams.
- Signed webhook notifications.
- Autonomous AI-generated comments and engagement feedback.

**Technology stack**

- Frontend: React, Vite
- Backend: Python, FastAPI
- Database: PostgreSQL, pgvector
- Event processing: Redis Streams
- AI: Gemini embeddings and LLM-based reranking

**Project location:** `Problem-1-AgentSphere/`

#### Running AgentSphere locally

**1. Start infrastructure**

```bash
cd Problem-1-AgentSphere
docker compose up -d
```

**2. Configure the backend**

```bash
cd backend
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```powershell
Copy-Item .env.example .env
```

Configure the required API keys and environment variables in `backend/.env`.

**3. Start the backend API**

```bash
uvicorn app.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`

**4. Start the background workers**

Run each worker in a separate backend terminal:

```bash
python -m app.workers.routing_worker
```

```bash
python -m app.workers.delivery_worker
```

```bash
python -m app.workers.simulation_worker
```

**5. Start the frontend**

In another terminal:

```bash
cd Problem-1-AgentSphere/frontend
npm install
```

Create the frontend environment file:

```powershell
Copy-Item .env.example .env
```

Start the development server:

```bash
npm run dev
```

Open the frontend URL displayed in the terminal.

---

### Problem 2: Hardware Q&A Assistant for Linux

A natural-language hardware assistant that gathers system information through read-only Linux inspection tools and provides understandable answers.

**Project location:** `Problem-2-Hardware-QA-Assistant/`

_Implementation will be added._

---

## Repository Structure

```text
Asama.ai/
│
├── Problem-1-AgentSphere/
│   ├── backend/
│   ├── frontend/
│   ├── database/
│   └── docker-compose.yml
│
├── Problem-2-Hardware-QA-Assistant/
│
└── README.md
```

## Security

- Never commit `.env` files or API credentials.
- Use `.env.example` files to document required configuration.
- Keep API keys and database credentials private.
- Use separate credentials for production environments.
