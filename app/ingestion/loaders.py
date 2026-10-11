from pypdf import PdfReader
from docx import Document

def extract_pdf_text(file_path: str) -> list[dict]:

    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        pages.append(
            {
                "page_number": page_number,
                "text": text,
            }
        )

    return pages


def extract_txt_text(file_path: str) -> list[dict]:

    with open(file_path, "r", encoding="utf-8") as file:

        text = file.read()

    return [
        {
            "page_number": 1,
            "text": text,
        }
    ]

def extract_docx_text(file_path: str) -> list[dict]:

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    text = "\n".join(paragraphs)

    return [
        {
            "page_number": 1,
            "text": text,
        }
    ]