import os
from typing import List, Dict
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def parse_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def parse_html(file_path: str) -> str:
    """Extracts text from an HTML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        return soup.get_text(separator='\n')

def parse_text(file_path: str) -> str:
    """Extracts text from a text-based file (MD, TXT, JSON)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def load_documents(file_paths: List[str]) -> List[Document]:
    """Loads and parses a list of files into LangChain Documents."""
    documents = []
    for path in file_paths:
        ext = os.path.splitext(path)[1].lower()
        content = ""
        try:
            if ext == '.pdf':
                content = parse_pdf(path)
            elif ext == '.html':
                content = parse_html(path)
            elif ext in ['.md', '.txt', '.json']:
                content = parse_text(path)
            else:
                print(f"Unsupported file type: {path}")
                continue
            
            if content:
                documents.append(Document(page_content=content, metadata={"source": os.path.basename(path)}))
        except Exception as e:
            print(f"Error parsing {path}: {e}")
            
    return documents

def chunk_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """Splits documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)
