import os
import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from ..extractor import Extractor
from ..catalog import create_catalog, save_catalog

router = APIRouter()

# Directorio base para guardar los conocimientos extraídos
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "knowledge_base")

@router.get("/health")
def health_check():
    """
    Endpoint para verificar que el backend está corriendo.
    """
    return {"status": "ok", "message": "Backend funcionando correctamente"}

@router.post("/pdfs/extract")
async def extract_pdf(file: UploadFile = File(...)):
    """
    Recibe un archivo PDF, extrae su texto y tablas, fusiona los elementos
    y genera un documento Markdown y un catálogo JSON.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    pdf_name = os.path.splitext(file.filename)[0]
    output_dir = os.path.join(KNOWLEDGE_BASE_DIR, pdf_name)
    os.makedirs(output_dir, exist_ok=True)

    # Guardar temporalmente el archivo subido
    temp_pdf_path = os.path.join(output_dir, "temp.pdf")
    with open(temp_pdf_path, "wb") as f:
        f.write(await file.read())

    try:
        extractor = Extractor(temp_pdf_path)
        extraction_result = extractor.process_and_merge()
        extractor.close()

        markdown_content = extraction_result["markdown"]
        num_pages = extraction_result["num_pages"]
        num_tables = extraction_result["num_tables"]

        # Guardar Markdown
        markdown_path = os.path.join(output_dir, "document.md")
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Generar y guardar catálogo
        catalog_data = create_catalog(pdf_name, markdown_content, num_pages, num_tables)
        save_catalog(catalog_data, output_dir)

        # Eliminar archivo temporal
        os.remove(temp_pdf_path)

        return JSONResponse(content={
            "message": "PDF procesado exitosamente",
            "catalog": catalog_data,
            "markdown_path": markdown_path
        })

    except Exception as e:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        raise HTTPException(status_code=500, detail=f"Error procesando el PDF: {str(e)}")

@router.get("/pdfs")
def list_pdfs():
    """
    Lista todos los documentos procesados junto con su metadata (catálogo).
    """
    documents = []
    if os.path.exists(KNOWLEDGE_BASE_DIR):
        for item in os.listdir(KNOWLEDGE_BASE_DIR):
            item_path = os.path.join(KNOWLEDGE_BASE_DIR, item)
            if os.path.isdir(item_path):
                catalog_path = os.path.join(item_path, "catalog.json")
                if os.path.exists(catalog_path):
                    with open(catalog_path, "r", encoding="utf-8") as f:
                        catalog_data = json.load(f)
                        catalog_data["id"] = item
                        documents.append(catalog_data)

    return {"documents": documents}
