import json
import os
import re
from typing import Dict, Any, List

def generate_summary_with_anthropic(text: str) -> str:
    """
    Usa la API de Anthropic para generar un resumen de 1-2 líneas del texto proporcionado.
    Si la clave de API 'ANTHROPIC_API_KEY' no está presente, retorna una cadena vacía.

    Args:
        text (str): El texto que se va a resumir.

    Returns:
        str: El resumen generado o una cadena vacía si no hay clave API o en caso de error.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return ""

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            temperature=0.5,
            system="Eres un asistente que resume textos en español. Debes proporcionar un resumen conciso de 1 a 2 líneas como máximo.",
            messages=[
                {"role": "user", "content": f"Resume el siguiente texto:\n\n{text}"}
            ]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Error al generar resumen con Anthropic: {e}")
        return ""

def create_catalog(pdf_name: str, markdown_content: str, num_pages: int, num_tables: int) -> Dict[str, Any]:
    """
    Genera el catálogo de metadatos de un documento a partir de su contenido Markdown.
    Incluye título, árbol de encabezados, conteo de palabras (total y por sección) y un resumen.

    Args:
        pdf_name (str): Nombre del archivo PDF.
        markdown_content (str): Contenido procesado en formato Markdown.
        num_pages (int): Número total de páginas del PDF original.
        num_tables (int): Número total de tablas detectadas.

    Returns:
        Dict[str, Any]: Diccionario con los metadatos catalogados.
    """
    lines = markdown_content.split('\n')

    title = pdf_name
    headings: List[Dict[str, Any]] = []

    # Expresión regular para detectar encabezados (ej: # Título, ## Subtítulo)
    header_pattern = re.compile(r'^(#{1,6})\s+(.*)')

    current_section = {"level": 0, "text": "Inicio", "content": ""}
    sections = [current_section]

    # Analizamos el contenido Markdown línea por línea
    for line in lines:
        match = header_pattern.match(line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()

            # Inferir el título del primer H1 si aún no se ha establecido
            if level == 1 and title == pdf_name:
                title = text

            # Añadir al árbol de encabezados
            headings.append({"level": level, "text": text})

            # Crear nueva sección para conteo de palabras y resumen
            current_section = {"level": level, "text": text, "content": ""}
            sections.append(current_section)
        else:
            current_section["content"] += line + "\n"

    total_words = 0
    section_stats = []

    # Procesar las secciones recolectadas
    for sec in sections:
        words = len(sec["content"].split())
        total_words += words

        stat = {
            "title": sec["text"],
            "level": sec["level"],
            "word_count": words,
            "summary": ""
        }

        # Generar resumen sólo para secciones principales (ej. nivel 1 o 2) con contenido sustancial
        if sec["level"] in (1, 2) and words > 50:
            # Tomamos un fragmento representativo si es muy largo
            text_to_summarize = sec["content"][:2000]
            stat["summary"] = generate_summary_with_anthropic(text_to_summarize)

        if words > 0 or stat["summary"]:
             section_stats.append(stat)

    catalog = {
        "title": title,
        "filename": pdf_name,
        "num_pages": num_pages,
        "num_tables": num_tables,
        "total_words": total_words,
        "heading_tree": headings,
        "sections": section_stats
    }

    return catalog

def save_catalog(catalog: Dict[str, Any], output_dir: str):
    """
    Guarda el diccionario del catálogo en un archivo JSON en el directorio de salida especificado.

    Args:
        catalog (Dict[str, Any]): Datos del catálogo a guardar.
        output_dir (str): Ruta de la carpeta donde se guardará el archivo 'catalog.json'.
    """
    os.makedirs(output_dir, exist_ok=True)
    catalog_path = os.path.join(output_dir, "catalog.json")

    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
