import fitz
import statistics
from typing import List, Dict, Any

class Extractor:
    """
    Clase encargada de extraer texto de un archivo PDF usando PyMuPDF,
    identificando jerarquías de encabezados basándose en los tamaños de fuente.
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    def extract_blocks_with_fonts(self) -> List[Dict[str, Any]]:
        """
        Extrae los bloques de texto de todas las páginas, calculando el tamaño
        de fuente predominante para cada bloque.

        Returns:
            List[Dict[str, Any]]: Una lista de diccionarios con la información de cada bloque,
            incluyendo texto, página, coordenadas (bbox) y tamaño de fuente principal.
        """
        blocks_info = []
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            # Extraer diccionario detallado (incluye fuentes y posiciones)
            page_dict = page.get_text("dict")

            for block in page_dict.get("blocks", []):
                # Solo procesar bloques de texto (type 0)
                if block.get("type") == 0:
                    text_lines = []
                    font_sizes = []

                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text_lines.append(span.get("text", "").strip())
                            if span.get("text", "").strip():
                                font_sizes.append(span.get("size", 0))

                    full_text = " ".join(text_lines).strip()
                    if full_text:
                        # Asignar el tamaño de fuente máximo encontrado en el bloque para jerarquizarlo
                        main_size = max(font_sizes) if font_sizes else 0
                        blocks_info.append({
                            "page": page_num + 1,
                            "bbox": block.get("bbox"),  # (x0, y0, x1, y1)
                            "text": full_text,
                            "font_size": main_size,
                            "type": "text"
                        })
        return blocks_info

    def get_font_size_thresholds(self, blocks: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calcula los umbrales de tamaño de fuente para determinar los niveles de encabezado (#, ##, ###).
        Calcula la mediana y agrupa los tamaños mayores.

        Args:
            blocks (List[Dict[str, Any]]): Los bloques extraídos con tamaños de fuente.

        Returns:
            Dict[str, float]: Diccionario con el tamaño mediano y los umbrales para h1, h2, h3.
        """
        sizes = [b["font_size"] for b in blocks if b["font_size"] > 0]
        if not sizes:
             return {"median": 12.0, "h1": 99.0, "h2": 99.0, "h3": 99.0}

        median_size = statistics.median(sizes)

        # Obtener tamaños únicos mayores a la mediana
        larger_sizes = sorted(list(set([s for s in sizes if s > median_size * 1.1])), reverse=True)

        thresholds = {"median": median_size}

        # Asignar niveles de encabezados según los tamaños mayores disponibles
        if len(larger_sizes) >= 1:
            thresholds["h1"] = larger_sizes[0]
        else:
            thresholds["h1"] = median_size * 1.5

        if len(larger_sizes) >= 2:
            thresholds["h2"] = larger_sizes[1]
        else:
            thresholds["h2"] = median_size * 1.3

        if len(larger_sizes) >= 3:
            thresholds["h3"] = larger_sizes[2]
        else:
            thresholds["h3"] = median_size * 1.15

        return thresholds

    def identify_repetitive_noise(self, blocks: List[Dict[str, Any]]) -> set:
        """
        Identifica ruido repetitivo (headers/footers) detectando líneas
        que se repiten en más del 50% de las páginas.

        Args:
            blocks (List[Dict[str, Any]]): Todos los bloques de texto extraídos.

        Returns:
            set: Un conjunto de textos identificados como ruido repetitivo.
        """
        num_pages = len(self.doc)
        if num_pages <= 2:
            return set()

        text_counts: Dict[str, set] = {}
        for block in blocks:
            # Solo consideramos textos cortos como posibles headers/footers
            text = block["text"]
            if len(text) < 100:
                if text not in text_counts:
                    text_counts[text] = set()
                text_counts[text].add(block["page"])

        noise_texts = set()
        for text, pages in text_counts.items():
            if len(pages) > (num_pages * 0.5):
                noise_texts.add(text)

        return noise_texts

    def process_and_merge(self) -> Dict[str, Any]:
        """
        Procesa el PDF extrayendo texto y tablas, fusionándolos por posición (coordenada Y),
        eliminando ruido repetitivo, y generando el contenido Markdown final.

        Returns:
            Dict[str, Any]: Diccionario con el contenido Markdown, número de páginas y número de tablas.
        """
        text_blocks = self.extract_blocks_with_fonts()
        table_blocks = self.extract_tables()

        thresholds = self.get_font_size_thresholds(text_blocks)
        noise_texts = self.identify_repetitive_noise(text_blocks)

        # Combinar todos los bloques y agrupar por página
        all_blocks = text_blocks + table_blocks
        pages_content = {}

        for block in all_blocks:
            page = block["page"]
            if page not in pages_content:
                pages_content[page] = []
            pages_content[page].append(block)

        markdown_lines = []

        for page in sorted(pages_content.keys()):
            page_blocks = pages_content[page]
            # Ordenar elementos de la página por la coordenada y0 (top)
            page_blocks.sort(key=lambda x: x["bbox"][1])

            for block in page_blocks:
                if block["type"] == "table":
                    markdown_lines.append(block["text"])
                    markdown_lines.append("")
                else:
                    text = block["text"]
                    if text in noise_texts:
                        continue

                    font_size = block["font_size"]

                    # Asignar nivel de encabezado según los umbrales
                    if font_size >= thresholds.get("h1", 99.0):
                        markdown_lines.append(f"# {text}")
                    elif font_size >= thresholds.get("h2", 99.0):
                        markdown_lines.append(f"## {text}")
                    elif font_size >= thresholds.get("h3", 99.0):
                        markdown_lines.append(f"### {text}")
                    else:
                        markdown_lines.append(text)

                    markdown_lines.append("") # Línea en blanco después de cada bloque

        return {
            "markdown": "\n".join(markdown_lines),
            "num_pages": len(self.doc),
            "num_tables": len(table_blocks)
        }

    def extract_tables(self) -> List[Dict[str, Any]]:
        """
        Extrae las tablas del PDF usando pdfplumber y las convierte a formato Markdown.

        Returns:
            List[Dict[str, Any]]: Una lista con diccionarios de tablas,
            incluyendo contenido markdown, página y su coordenada vertical inicial.
        """
        import pdfplumber
        tables_info = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.find_tables()
                for table in tables:
                    table_data = table.extract()
                    if not table_data:
                        continue

                    # Convertir los datos a formato Markdown
                    markdown_table = ""
                    for i, row in enumerate(table_data):
                        # Reemplazar None o saltos de línea por espacios
                        clean_row = [str(cell).replace('\n', ' ') if cell else "" for cell in row]
                        markdown_table += "| " + " | ".join(clean_row) + " |\n"

                        # Añadir separador de cabecera después de la primera fila
                        if i == 0:
                            markdown_table += "|" + "|".join(["---"] * len(clean_row)) + "|\n"

                    tables_info.append({
                        "page": page_num + 1,
                        "bbox": table.bbox,  # (x0, top, x1, bottom) - top equivale a y0
                        "text": markdown_table.strip(),
                        "type": "table"
                    })

        return tables_info

    def close(self):
        """Cierra el documento PDF."""
        self.doc.close()
