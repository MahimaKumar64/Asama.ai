# Asama.ai – AI Engineering Interview Assignment

This repository contains implementations of two independent AI Engineering problems completed as part of the Asama.ai interview assignment.

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
- Engagement analytics and simulation controls.
- Frontend dashboard with Network Feed, Agent Directory, Routing Inspector and Analytics.

**Technology stack**

- Frontend: React, Vite
- Backend: Python, FastAPI
- Database: PostgreSQL, pgvector
- Event processing: Redis Streams
- AI: Gemini embeddings and LLM-based reranking
- Infrastructure: Docker Compose

**Project location:** `Problem-1-AgentSphere/`

**Status:** Completed and pushed to GitHub.

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

### Problem 2: Linux Hardware Q&A Assistant

A local AI-powered Linux hardware assistant that answers natural-language questions about system hardware by collecting actual information through predefined Linux inspection tools.

Instead of relying on the LLM's general knowledge to guess hardware specifications, the assistant uses tool calling to inspect the system, parses command output into structured information, and generates answers grounded in the retrieved data.

**Core capabilities**

- Natural-language hardware questions through a terminal chat interface.
- LLM tool calling to select the appropriate hardware inspection functions.
- CPU information including processor model, architecture, cores and threads.
- Memory usage and available memory information.
- Memory topology inspection where supported by the system.
- Storage device information including size, model, transport and mount points.
- GPU and display controller detection.
- Operating system, Linux distribution and environment detection.
- Conversation history for contextual follow-up questions.
- Session-based hardware tool-result caching.
- Graceful handling of unavailable utilities, permission errors and inaccessible hardware information.

**Technology stack**

- Language: Python 3.12
- Chat interface: Textual
- LLM runtime: Ollama
- Local model: Qwen2.5 3B
- LLM integration: Ollama Python client and tool calling
- Hardware inspection: Linux utilities (`lscpu`, `free`, `lsblk`, `lspci`, `dmidecode`)
- Parsing: Python and JSON
- Testing: Pytest

**Project location:** `Problem-2-Hardware-QA-Assistant/`

**Status:** Implemented and tested.

#### Architecture

The application follows a tool-calling architecture:

1. The user submits a natural-language hardware question.
2. The LLM determines which predefined hardware tool is appropriate.
3. The orchestrator validates the requested tool and invokes its registered Python function.
4. The hardware function uses the secure command executor to run an allow-listed Linux command.
5. Raw command output is parsed into structured data.
6. The structured results are returned to the LLM.
7. The LLM generates a natural-language answer grounded in the retrieved information.

**Architecture components**

- `frontend/` – Textual terminal chat interface.
- `backend/orchestrator.py` – Coordinates LLM responses and tool execution.
- `backend/llm_client.py` – Connects to the local Ollama server.
- `backend/tool_registry.py` – Defines available tools and validates tool requests.
- `backend/hardware_tools.py` – Implements hardware inspection functions.
- `backend/executor.py` – Executes predefined Linux commands safely.
- `backend/parsers.py` – Converts raw command output into structured information.
- `backend/system_discovery.py` – Detects the Linux environment and available utilities.
- `backend/conversation.py` – Maintains conversation history and session-level caching.
- `backend/prompts.py` – Defines assistant behaviour and grounding instructions.
- `config/` – Application configuration.
- `tests/` – Automated tests.

#### Security and design decisions

- Only predefined, allow-listed hardware commands can be executed.
- The LLM selects registered Python tools; it cannot supply arbitrary shell commands.
- Commands are executed using `subprocess.run()` with `shell=False`.
- Executable paths and command arguments are predefined.
- Execution timeouts prevent commands from running indefinitely.
- Invalid tool names and unexpected arguments are rejected.
- The application does not run the entire process with root privileges.
- Hardware information is not invented when it cannot be retrieved.
- The local Ollama model processes questions without sending them to a hosted LLM API.

#### Running the Hardware Q&A Assistant locally

The project was developed and tested using Ubuntu 24.04 under WSL2 on Windows, with Ollama running locally on Windows.

**1. Install prerequisites**

- Python 3.11 or later.
- Ubuntu or another supported Linux environment.
- Ollama.
- The Qwen2.5 3B model.

Install the required Linux utilities where necessary:

```bash
sudo apt update
sudo apt install util-linux procps pciutils dmidecode
```

**2. Set up Ollama**

Install Ollama and download the model:

```bash
ollama pull qwen2.5:3b
```

Start the Ollama server and ensure it is reachable from the Linux environment.

For the Windows-hosted Ollama and WSL2 development setup, configure the server to accept connections from WSL and restrict access through the Windows firewall to the required local environment.

**3. Configure the Python environment**

Navigate to the project directory:

```bash
cd Problem-2-Hardware-QA-Assistant
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create the local environment file:

```bash
cp .env.example .env
```

Configure:

```env
OLLAMA_HOST=http://YOUR_OLLAMA_HOST:11434
OLLAMA_MODEL=qwen2.5:3b
```

Replace `YOUR_OLLAMA_HOST` with the address of the machine running Ollama that is reachable from Linux. For the WSL2 setup, this is typically the Windows host gateway address.

**5. Run the assistant**

```bash
python main.py
```

Ask questions such as:

- What processor does my system have?
- How many CPU cores and threads are available?
- How much memory is currently available?
- What storage devices are detected?
- What GPU or display controller is detected?
- Is my Linux environment virtualized?

**6. Run automated tests**

```bash
python -m pytest -v
```

The implementation has been verified with 37 passing automated tests.

#### Limitations

- Hardware visibility depends on the Linux environment and available system utilities.
- Some hardware details require elevated privileges or access to firmware information.
- WSL2 exposes virtualized hardware information rather than complete physical laptop hardware information.
- SMBIOS/DMI information may be unavailable in WSL2, preventing reliable detection of physical RAM slots and motherboard maximum memory capacity.
- The assistant reports unavailable information instead of guessing or inventing specifications.

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
│   ├── backend/
│   ├── frontend/
│   ├── config/
│   ├── tests/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
│
├── README.md
└── .gitignore
```

## Security

- Never commit `.env` files or API credentials.
- Use `.env.example` files to document required configuration.
- Keep API keys and database credentials private.
- Use separate credentials for production environments.
- Keep hardware inspection commands restricted to the predefined allow-list.
- Avoid arbitrary shell execution and unnecessary root privileges.

## Submission

Both assignment problems are maintained in this single GitHub repository.

**Repository:** [Asama.ai – GitHub](https://github.com/MahimaKumar64/Asama.ai)

**Branch:** `main`
