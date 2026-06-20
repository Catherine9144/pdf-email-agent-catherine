import PyPDF2
from typing import Optional

def extract_pdf_text(file_path: str, max_pages: Optional[int] = None) -> str:
    """
    从PDF文件中提取文本。
    Args:
        file_path: PDF文件路径
        max_pages: 最多读取页数，None表示全部
    Returns:
        提取的文本字符串
    """
    text = []
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        pages = reader.pages[:max_pages] if max_pages else reader.pages
        for page in pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)
