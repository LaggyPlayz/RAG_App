import os

from app.services.ingestion.csv_loader import CSVLoader
from app.services.ingestion.docx_loader import DOCXLoader
from app.services.ingestion.excel_loader import ExcelLoader
from app.services.ingestion.pdf_loader import PDFLoader
from app.services.ingestion.plaintext_loader import PlainTextLoader
from app.utils.exceptions import UnsupportedFileTypeError


class LoaderFactory:
    """Factory selecting document parser by file extension."""

    @staticmethod
    def get_loader(file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return PDFLoader()
        elif ext in (".docx", ".doc"):
            return DOCXLoader()
        elif ext == ".csv":
            return CSVLoader()
        elif ext in (".xlsx", ".xls"):
            return ExcelLoader()
        elif ext in (".txt", ".md", ".json", ".html", ".htm"):
            return PlainTextLoader()
        else:
            raise UnsupportedFileTypeError(f"Unsupported file extension: '{ext}'")
