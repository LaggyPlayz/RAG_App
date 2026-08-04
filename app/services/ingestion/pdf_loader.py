from dataclasses import dataclass

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


@dataclass
class LoadedPage:
    page_number: int
    text: str


class PDFLoader:
    """Extracts text page-by-page from PDF files."""

    def load(self, file_path: str) -> list[LoadedPage]:
        pages: list[LoadedPage] = []
        if PyPDF2 is None:
            # Fallback plain text read if PyPDF2 missing
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                pages.append(LoadedPage(page_number=1, text=f.read()))
            return pages

        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for idx, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                pages.append(LoadedPage(page_number=idx, text=text.strip()))

        return pages
