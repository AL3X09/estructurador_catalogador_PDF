# Backend del Catalogador de Conocimiento PDF

Este directorio contiene toda la lógica y API para el procesamiento de archivos PDF de la aplicación.

## Estructura

- `requirements.txt`: Dependencias de Python (`fastapi`, `uvicorn`, `PyMuPDF`, `pdfplumber`, `python-multipart`, `anthropic`).
- `app/main.py`: Archivo de entrada de FastAPI y configuración de CORS.
- `app/extractor.py`: Lógica principal para la extracción de texto, análisis de tamaños de fuente, extracción de tablas, fusión posicional y reducción de ruido repetitivo.
- `app/catalog.py`: Lógica para generar el archivo `catalog.json`, incluye la integración con Anthropic para resúmenes si `ANTHROPIC_API_KEY` está configurada en el entorno.
- `app/routers/pdfs.py`: Definición de los endpoints expuestos (`/health`, `/pdfs/extract`, `/pdfs`).
- `/knowledge_base/`: Carpeta (creada dinámicamente) donde se almacenan los archivos `.md` y `.json` procesados y desde la cual FastAPI sirve los archivos estáticos.

## Pruebas
Puedes probar rápidamente los endpoints accediendo a la documentación interactiva provista automáticamente por FastAPI en el navegador, normalmente en /docs.
