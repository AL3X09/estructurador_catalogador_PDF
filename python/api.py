from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import shutil
from typing import List, Optional
from pdf_knowledge.extractor import PDFExtractor

app = FastAPI(title="Catalogador de Conocimiento PDF API")

# Permitir peticiones desde el frontend de Tauri
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """
    Endpoint de salud para que Tauri verifique si el sidecar está listo.
    """
    return {"status": "ok"}


class ExtractRequest(BaseModel):
    pdf_path: str

@app.post("/extract")
def extract_pdf(request: ExtractRequest):
    """
    Recibe la ruta de un PDF, lo procesa y devuelve el Markdown y el catálogo.
    """
    if not os.path.exists(request.pdf_path):
        raise HTTPException(status_code=404, detail="Archivo PDF no encontrado")

    try:
        extractor = PDFExtractor(request.pdf_path)
        result = extractor.extract_and_catalog()

        # Leer el contenido de Markdown generado
        with open(result["markdown_path"], "r", encoding="utf-8") as f:
            markdown_content = f.read()

        return {
            "catalog": result["catalog"],
            "markdown": markdown_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el PDF: {str(e)}")

@app.get("/catalog")
def list_catalog():
    """
    Lista todos los documentos procesados y su metadata.
    """
    base_dir = "knowledge_base"
    if not os.path.exists(base_dir):
        return {"documents": []}

    documents = []
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path):
            catalog_path = os.path.join(item_path, "catalog.json")
            if os.path.exists(catalog_path):
                with open(catalog_path, "r", encoding="utf-8") as f:
                    import json
                    documents.append(json.load(f))

    return {"documents": documents}

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=47821, reload=False)
