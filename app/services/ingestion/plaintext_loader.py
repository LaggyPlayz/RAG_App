from app.services.ingestion.pdf_loader import LoadedPage


class PlainTextLoader:
    """Extracts text from UTF-8 plain text (.txt, .md, .json, .html) files."""

    def load(self, file_path: str) -> list[LoadedPage]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return [LoadedPage(page_number=1, text=text)]
