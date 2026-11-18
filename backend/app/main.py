from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.uploads import router as uploads_router
from app.config import settings

app = FastAPI(title=settings.app_name,
              description="AI data analysis with document ingestion, RAG, tools, MCP and LangGraph.",
              version="0.2.0")
origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(uploads_router)

@app.get("/", tags=["system"])
def root():
    return {"name": settings.app_name, "status": "running", "docs": "/docs"}

@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": "backend"}
