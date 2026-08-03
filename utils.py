import fitz  # PyMuPDF
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract clean text content from uploaded PDF document bytes using PyMuPDF (fitz)."""
    text_content = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text and text.strip():
                text_content.append(text.strip())
    return "\n\n".join(text_content)

def chunk_document_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """Split text into logical chunks using LangChain RecursiveCharacterTextSplitter."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_text(text)

class MockVectorStore:
    """Fallback vector store manager using ChromaDB or lightweight semantic index."""
    def __init__(self):
        self.documents = []

    def add_profile(self, candidate_name: str, raw_text: str, metadata: Dict[str, Any]):
        chunks = chunk_document_text(raw_text)
        for idx, chunk in enumerate(chunks):
            self.documents.append({
                "id": f"{candidate_name}_{idx}",
                "candidate_name": candidate_name,
                "text": chunk,
                "metadata": metadata
            })

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_words = set(query.lower().split())
        results = []
        for doc in self.documents:
            doc_words = set(doc["text"].lower().split())
            intersection = query_words.intersection(doc_words)
            score = len(intersection) / max(len(query_words), 1)
            results.append({
                "doc": doc,
                "score": round(score, 2)
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

# Global store instance
store_instance = MockVectorStore()
