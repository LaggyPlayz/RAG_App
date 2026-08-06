from app.services.ingestion.pdf_loader import LoadedPage

try:
    import docx
except ImportError:
    docx = None


class DOCXLoader:
    """Extracts text from Word (.docx) documents."""

    def load(self, file_path: str) -> list[LoadedPage]:
        if docx is None:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return [LoadedPage(page_number=1, text=f.read())]

        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n\n".join(paragraphs)

        return [LoadedPage(page_number=1, text=full_text)]
