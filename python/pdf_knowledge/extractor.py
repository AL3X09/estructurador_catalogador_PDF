import fitz # PyMuPDF
import pdfplumber
import os
import json
import statistics

class PDFExtractor:
    """
    Clase para extraer contenido de PDFs, estructurarlo en Markdown y generar un catálogo.
    """

    def __init__(self, pdf_path: str):
        """
        Inicializa el extractor con la ruta del PDF.
        """
        self.pdf_path = pdf_path

    def _extract_text_blocks(self) -> list:
        """
        Extrae bloques de texto y determina los encabezados basados en el tamaño de la fuente.
        """
        doc = fitz.open(self.pdf_path)
        blocks_by_page = []
        all_sizes = []

        # Primera pasada: recolectar bloques y tamaños de fuente
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            page_blocks = []

            for b in blocks:
                if b["type"] == 0:  # Bloque de texto
                    for l in b["lines"]:
                        for s in l["spans"]:
                            text = s["text"].strip()
                            if text:
                                size = s["size"]
                                all_sizes.append(size)
                                # (y0, texto, tamaño, es_tabla)
                                page_blocks.append({"y0": s["bbox"][1], "text": text, "size": size, "type": "text"})
            blocks_by_page.append(page_blocks)

        # Calcular el tamaño mediano para heurística de encabezados
        if not all_sizes:
            return blocks_by_page

        median_size = statistics.median(all_sizes)

        # Segunda pasada: asignar niveles de encabezado
        for page_blocks in blocks_by_page:
            for block in page_blocks:
                if block["size"] > median_size * 1.5:
                    block["level"] = 1
                elif block["size"] > median_size * 1.3:
                    block["level"] = 2
                elif block["size"] > median_size * 1.1:
                    block["level"] = 3
                else:
                    block["level"] = 0 # Texto normal

        return blocks_by_page

    def _extract_tables(self) -> list:
        """
        Extrae tablas de cada página usando pdfplumber y las convierte a Markdown.
        """
        tables_by_page = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = []
                tables = page.find_tables()
                for table in tables:
                    extracted_table = table.extract()
                    if extracted_table:
                        # Convertir a Markdown
                        md_table = []
                        for i, row in enumerate(extracted_table):
                            # Limpiar Nones
                            clean_row = [str(cell).replace('\n', ' ') if cell is not None else "" for cell in row]
                            md_table.append("| " + " | ".join(clean_row) + " |")
                            if i == 0:
                                # Fila separadora del header
                                md_table.append("|" + "|".join(["---"] * len(clean_row)) + "|")

                        bbox = table.bbox # (x0, top, x1, bottom)
                        page_tables.append({"y0": bbox[1], "text": "\n".join(md_table), "type": "table"})
                tables_by_page.append(page_tables)
        return tables_by_page

    def extract_and_catalog(self) -> dict:
        """
        Método principal que fusiona textos y tablas, elimina repeticiones,
        genera el Markdown y el catálogo.
        """
        text_blocks_by_page = self._extract_text_blocks()
        tables_by_page = self._extract_tables()

        merged_pages = []
        num_pages = len(text_blocks_by_page)
        total_tables = 0

        for i in range(num_pages):
            texts = text_blocks_by_page[i]
            tables = tables_by_page[i] if i < len(tables_by_page) else []
            total_tables += len(tables)

            # Fusión por posición vertical (y0)
            combined = texts + tables
            combined.sort(key=lambda x: x["y0"])
            merged_pages.append(combined)

        # Detección de ruido repetitivo (headers/footers)
        # Una heurística simple: si la primera o última línea se repite en >50% de las páginas, la eliminamos.
        # Mejorado para manejar también números de página (ignorando dígitos)
        first_lines = {}
        last_lines = {}

        for page in merged_pages:
            text_only = [b for b in page if b["type"] == "text"]
            if text_only:
                first = text_only[0]["text"]
                last = text_only[-1]["text"]
                # Normalizamos ignorando números para detectar numeración de páginas
                first_norm = ''.join([i for i in first if not i.isdigit()]).strip()
                last_norm = ''.join([i for i in last if not i.isdigit()]).strip()

                if first_norm:
                    first_lines[first_norm] = first_lines.get(first_norm, 0) + 1
                if last_norm:
                    last_lines[last_norm] = last_lines.get(last_norm, 0) + 1

        noise_threshold = num_pages * 0.5
        noise_texts = set()
        for t, count in first_lines.items():
            if count > noise_threshold:
                noise_texts.add(t)
        for t, count in last_lines.items():
            if count > noise_threshold:
                noise_texts.add(t)

        # Construir Markdown y extraer metadata para el catálogo
        markdown_lines = []
        heading_tree = []
        word_count = 0
        title = "Documento sin título"

        for page in merged_pages:
            for block in page:
                if block["type"] == "text":
                    text_norm = ''.join([i for i in block["text"] if not i.isdigit()]).strip()
                    if text_norm in noise_texts:
                        continue # Saltar ruido

                if block["type"] == "table":
                    markdown_lines.append("\n" + block["text"] + "\n")
                    # Contar palabras aproximadas en la tabla
                    word_count += len(block["text"].split())
                else:
                    level = block.get("level", 0)
                    text = block["text"]
                    if level > 0:
                        prefix = "#" * level
                        markdown_lines.append(f"\n{prefix} {text}\n")
                        heading_tree.append({"level": level, "text": text})
                        if title == "Documento sin título" and level == 1:
                            title = text # Inferir título del primer H1
                    else:
                        markdown_lines.append(text)
                    word_count += len(text.split())

        final_markdown = "\n".join(markdown_lines)

        catalog = {
            "title": title,
            "pages": num_pages,
            "headings": heading_tree,
            "tables_count": total_tables,
            "word_count": word_count,
            "summary": ""
        }

        # Opcional: Generar resumen con Anthropic si la key está presente
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=100,
                    messages=[
                        {"role": "user", "content": f"Resume el siguiente documento en 1-2 líneas:\n\n{final_markdown[:3000]}"}
                    ]
                )
                catalog["summary"] = response.content[0].text
            except Exception as e:
                pass # Ignorar fallos de la API

        # Guardar en disco
        base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        output_dir = os.path.join("knowledge_base", base_name)
        os.makedirs(output_dir, exist_ok=True)

        md_path = os.path.join(output_dir, "document.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(final_markdown)

        json_path = os.path.join(output_dir, "catalog.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)

        return {"markdown_path": md_path, "catalog": catalog}

if __name__ == "__main__":
    pass
