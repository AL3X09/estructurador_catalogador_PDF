# Catalogador de Conocimiento PDF

Una aplicación de escritorio para Windows desarrollada con Tauri y Python que convierte PDFs en Markdown estructurado y extrae metadata de los documentos.

## Arquitectura

- **Frontend**: Interfaz simple en HTML/CSS/JS (vanilla) para cargar documentos, ver el catálogo y previsualizar los resultados en Markdown.
- **Backend / Lógica (Sidecar)**: Desarrollado en Python, expone una API local mediante FastAPI.
  - La extracción de texto jerárquica usa PyMuPDF.
  - La extracción de tablas usa pdfplumber.
  - Tauri se encarga de ejecutar el binario (generado con PyInstaller) durante el ciclo de vida de la aplicación.
  - El backend escucha peticiones HTTP locales.

## Requisitos para desarrollo

- Node.js (18+)
- Rust (rustup / cargo)
- Python 3.11+

## Desarrollo Local

Para correr el proyecto en modo desarrollo, se ejecuta la aplicación de Tauri y se levanta el entorno de Python al mismo tiempo, sin necesidad de compilar el sidecar previamente.

1. Instalar dependencias de frontend:
   npm install

2. Preparar entorno virtual y dependencias de Python (ej. en bash/Linux/Mac):
   python3 -m venv venv_dev
   source venv_dev/bin/activate
   pip install -r python/requirements.txt

3. Levantar la aplicación Tauri en modo dev:
   npm run tauri dev
   (El script src-tauri/src/lib.rs iniciará el backend de FastAPI de forma automática.)

## Compilación de Producción para Windows

1. Compilar el backend de Python en un ejecutable usando PyInstaller mediante el script provisto:
   .\scripts\build_sidecar.ps1
   Este script creará el binario en src-tauri/bin/pdf-sidecar-x86_64-pc-windows-msvc.exe.

2. Compilar el instalador de Tauri (MSI o NSIS):
   npm run tauri build

3. El instalador final estará disponible en src-tauri/target/release/bundle/msi/.

## Variables de Entorno

- ANTHROPIC_API_KEY: (Opcional) Usada por el sidecar de Python para generar pequeños resúmenes de las secciones usando un LLM de Anthropic. Si no se provee, los resúmenes quedarán vacíos.
