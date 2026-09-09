from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import pdfs

app = FastAPI(
    title="Catalogador de Conocimiento PDF API",
    description="API para procesar PDFs y generar catálogos Markdown/JSON",
    version="1.0.0"
)

# Configurar CORS para permitir el frontend de Vite en desarrollo
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar los routers
app.include_router(pdfs.router)

from fastapi.staticfiles import StaticFiles
import os

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")
os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
app.mount("/knowledge_base", StaticFiles(directory=KNOWLEDGE_BASE_DIR), name="knowledge_base")
