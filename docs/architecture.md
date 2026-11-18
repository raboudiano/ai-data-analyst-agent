# Architecture — Phase 1

## Current foundation
- Next.js frontend serves the user interface.
- FastAPI exposes the backend API.
- Qdrant runs as a persistent vector database service.
- Gemini credentials are configured through environment variables (not committed).

## Planned request flow
1. Browser sends a request to FastAPI.
2. FastAPI validates input and routes the request.
3. LangGraph coordinates retrieval and analysis tasks.
4. RAG retrieves relevant document chunks from Qdrant.
5. Approved tools perform bounded Pandas/SQL operations.
6. The response returns answer text, chart specifications, and citations.

## Trust boundaries
- Uploaded files are untrusted.
- LLM output is data, not executable authority.
- SQL tools will be read-only and restricted to approved tables.
- Python analysis will use predefined operations rather than unrestricted `exec`.
- Secrets remain server-side.
