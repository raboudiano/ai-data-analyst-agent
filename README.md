# AI Data Analyst Agent

An advanced AI Engineering project for analyzing CSV/Excel datasets and answering questions over supporting PDF documentation.

## Phase 1 status
- FastAPI backend scaffold
- Next.js + TypeScript frontend scaffold
- Qdrant service in Docker Compose
- Environment template
- Health endpoint and starter test

## Prerequisites
- Python 3.11+
- Node.js 20+
- npm
- Docker Desktop (recommended for Qdrant)

## 1. Backend setup (Git Bash)

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend:
- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

If using PowerShell instead of Git Bash, activate with:
`..\.venv\Scripts\Activate.ps1`

## 2. Start Qdrant

From the repository root:

```bash
docker compose up -d qdrant
docker compose ps
```

Qdrant:
- HTTP API: http://localhost:6333
- Dashboard: http://localhost:6333/dashboard

## 3. Frontend setup

Open another terminal:

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Frontend: http://localhost:3000

## 4. Verify

```bash
# Backend health
curl http://127.0.0.1:8000/health

# Run backend tests
cd backend
pytest
```

## 5. Git initialization

From the repository root:

```bash
git init
git add .
git commit -m "chore: initialize AI Data Analyst Agent project"
```

Use small, meaningful commits as features are implemented. Do not commit `.env`, API keys, virtual environments, `node_modules`, or generated datasets.

## Initial team split (3 students)
1. Backend and data processing: API, file validation, Pandas/SQL tools.
2. AI engineering: RAG, Qdrant, Gemini, LangGraph and MCP.
3. Frontend and evaluation: Next.js UI, charts, benchmark dashboard.

Agree on API contracts before parallel implementation. Each member should work on a feature branch and open pull requests.

## Planned phases
1. Project foundation (current)
2. CSV/Excel/PDF ingestion and metadata
3. RAG and citations with Qdrant
4. Gemini + LangGraph agent, Python/SQL tools and MCP
5. Next.js chat and analytics dashboard
6. Retrieval and generation benchmarks
7. Integration, tests, report and demonstration

## Important engineering notes
- Never execute arbitrary model-generated Python or SQL directly. Implement constrained tools, validation, timeouts and read-only database access.
- Keep API keys in environment variables and out of Git.
- Treat uploaded files as untrusted input.
- Record benchmark datasets, expected answers, metrics and model/configuration versions.
