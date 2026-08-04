import csv
from app.services.ingestion.pdf_loader import LoadedPage


class CSVLoader:
    """Extracts text from CSV files formatted as readable row strings."""

    def load(self, file_path: str) -> list[LoadedPage]:
        rows_text = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header:
                header_str = " | ".join(header)
                rows_text.append(f"Header: {header_str}")

            for idx, row in enumerate(reader, start=1):
                row_str = " | ".join(row)
                rows_text.append(f"Row {idx}: {row_str}")

        full_text = "\n".join(rows_text)
        return [LoadedPage(page_number=1, text=full_text)]
