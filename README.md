# RepoMind AI

AI-powered GitHub repository analysis. Paste a URL, get complete documentation, architecture diagrams, complexity analysis, recruiter content, interview prep, and a RAG chat interface.

## Features

| Feature | Description |
|---|---|
| Architecture Analysis | Languages, frameworks, DBs, auth, patterns |
| Auto Documentation | Summary, README, API docs, setup guide |
| Mermaid Diagrams | Component, dataflow, API flow, DB schema |
| Complexity Analyzer | Scores, hotspots, strengths, suggestions |
| Recruiter Mode | Resume bullets, STAR answers, elevator pitch |
| Interview Prep | Beginner/intermediate/advanced Q&A |
| Onboarding Guide | 3-day developer learning path |
| Repo Comparison | Side-by-side analysis of two repos |
| RAG Chat | Ask anything about the codebase |

## Quickstart

```bash
# 1. Copy and fill in your API key
cp backend/.env.example backend/.env
# Edit OPENAI_API_KEY in backend/.env

# 2. Start everything
docker-compose up --build

# Frontend: http://localhost:5173
# API docs: http://localhost:8000/docs
```

## Development (no Docker)

```bash
# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| OPENAI_API_KEY | ✅ | Your OpenAI API key |
| DATABASE_URL | | SQLite path (default: ./data/repomind.db) |
| LLM_MODEL | | OpenAI model (default: gpt-4o) |
| REPO_CLONE_DIR | | Clone directory (default: ./data/repos) |
| FAISS_INDEX_DIR | | FAISS index directory (default: ./data/faiss) |

## Stack

- **Frontend**: React 18, Vite, Tailwind CSS, React Query, Mermaid.js
- **Backend**: FastAPI, SQLAlchemy (async), SQLite
- **AI**: LangChain, FAISS, OpenAI GPT-4o + Embeddings
- **Deployment**: Docker, Vercel (FE), Render (BE)
