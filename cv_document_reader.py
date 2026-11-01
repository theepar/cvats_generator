from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
import re


MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TEXT_LENGTH = 100_000
MAX_PDF_PAGES = 20


@dataclass
class DocumentText:
    text: str
    file_type: str
    warnings: list[str] = field(default_factory=list)


def read_document(content: bytes, filename: str) -> DocumentText:
    if not content:
        raise ValueError("File kosong.")
    if len(content) > MAX_FILE_BYTES:
        raise ValueError("Ukuran file melebihi batas 8 MB.")

    extension = Path(filename).suffix.lower()
    warnings = []

    if extension in (".md", ".txt"):
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise ValueError("File teks harus menggunakan encoding UTF-8.") from error
    elif extension == ".pdf":
        from pypdf import PdfReader
        try:
            reader = PdfReader(BytesIO(content), strict=False)
            if reader.is_encrypted:
                raise ValueError("PDF dilindungi kata sandi. Unggah PDF yang tidak terenkripsi.")
            if len(reader.pages) > MAX_PDF_PAGES:
                raise ValueError(f"PDF melebihi batas {MAX_PDF_PAGES} halaman.")
            pages = []
            empty_pages = 0
            for page in reader.pages:
                page_text = page.extract_text(extraction_mode="layout") or ""
                if not page_text.strip():
                    empty_pages += 1
                pages.append(page_text)
            text = "\n\n".join(pages)
            if empty_pages:
                warnings.append(f"{empty_pages} halaman PDF tidak memiliki teks yang terbaca. PDF hasil scan memerlukan OCR.")
        except ValueError:
            raise
        except Exception as error:
            raise ValueError("PDF gagal dibaca. Pastikan file PDF tidak rusak dan berisi teks yang bisa dipilih.") from error
    elif extension == ".docx":
        from docx import Document
        try:
            document = Document(BytesIO(content))
            lines = []
            for block in document.iter_inner_content():
                if hasattr(block, "rows"):
                    for row in block.rows:
                        cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                        if cells:
                            lines.append(" | ".join(cells))
                else:
                    value = block.text.strip()
                    if not value:
                        lines.append("")
                        continue
                    style = (block.style.name if block.style else "").lower()
                    if "heading" in style and re.search(r"\d", style):
                        level = int(re.search(r"\d", style).group())
                        value = f"{'##' if level == 1 else '###'} {value}"
                    lines.append(value)
            text = "\n".join(lines)
        except Exception as error:
            raise ValueError("Dokumen Word gagal dibaca. Gunakan file .docx yang valid.") from error
    else:
        raise ValueError("Format belum didukung. Gunakan .md, .txt, .pdf, atau .docx.")

    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError("Isi dokumen terlalu panjang (maksimum 100.000 karakter).")
    if not text.strip():
        raise ValueError("Tidak ditemukan teks yang dapat dibaca. Untuk PDF scan, gunakan OCR sebelum mengunggah.")
    return DocumentText(text=text, file_type=extension.lstrip("."), warnings=warnings)
