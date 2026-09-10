# Catalogador de Conocimiento PDF

El **Catalogador de Conocimiento PDF** es una aplicación web pura diseñada para convertir archivos PDF en Markdown estructurado y generar un catálogo de metadatos asociado. Su objetivo principal es facilitar la preparación de documentos como fuente de conocimiento para agentes de IA, evitando el consumo de tokens innecesarios mediante la limpieza de ruido repetitivo (headers/footers) y la generación de un árbol jerárquico del contenido.

## Características

- **Extracción Inteligente:** Analiza PDFs utilizando `PyMuPDF` y reconstruye la jerarquía del documento basándose en tamaños de fuente (detectando `# H1`, `## H2`, `### H3`).
- **Tablas en Markdown:** Convierte tablas en los PDFs a formato nativo Markdown `| col | col |` utilizando `pdfplumber`.
- **Fusión Contextual:** Combina texto y tablas basándose en sus coordenadas espaciales `Y`, conservando el flujo de lectura natural del documento original.
- **Reducción de Ruido:** Filtra automáticamente elementos repetitivos en las cabeceras y pies de página.
- **Catálogo (Metadatos y Resumen):** Genera un `catalog.json` por documento con información clave (conteo de palabras por sección, cantidad de tablas y páginas, árbol de navegación), integrando resúmenes de secciones a través de la API de Anthropic (si está configurada).

## Arquitectura

El sistema está dividido estrictamente en un Frontend (Vue 3) y un Backend (Python / FastAPI) independientes.

```text
       [ Usuario (Navegador) ]
                  |
         +-----------------+
         | Frontend (Vue)  | <--- Puerto 5173 (Dev)
         +-----------------+
             |        |
          (POST)    (GET)  (Peticiones HTTP vía Axios)
             |        |
         +-----------------+
         | Backend (FastAPI)| <--- Puerto 8000 (Dev)
         +-----------------+
           /       |       \
          /        |        \
  [PyMuPDF] [pdfplumber]  [Anthropic API]
         |         |         |
         +---------+---------+
                   |
        [ /knowledge_base/ ] (Almacenamiento de Markdown/JSON generados)
```

## Requisitos Previos

- **Node.js (18+ recomendado)** y el gestor de paquetes de Node para el Frontend.
- **Python 3.11+** para el Backend.

## Instrucciones de Instalación y Ejecución

### 1. Backend

El backend se encarga de todo el procesamiento intensivo de PDF y de servir la API REST y los archivos generados.

Ve a la carpeta del backend, instala con pip y usa uvicorn para iniciar (ejemplo: uvicorn app.main:app --reload).
El backend estará disponible en el puerto 8000.

### 2. Frontend

El frontend consume la API del backend. Asegúrate de tener el backend corriendo.
Ve a la carpeta frontend, instala dependencias con el comando habitual de npm e inicia el servidor de desarrollo (por ejemplo, npm run seguido de dev).

---

## Decisiones Técnicas
- El frontend utiliza `Vue 3` con la Composition API (`<script setup>`) y empaquetado con Vite.
- Se utilizó `axios` para las peticiones HTTP y `marked` para una pre-visualización ligera del markdown, sin frameworks de UI pesados adicionales. El estilo fue implementado con CSS nativo simple.
- El backend procesa PDFs con `fitz` (PyMuPDF) para extraer tamaño de fuente, agrupando tamaños mayores a la mediana del documento como H1/H2/H3.
- Todo el código backend y frontend ha sido documentado en español.
