

import os
import tiktoken
from PyPDF2 import PdfReader
from docx import Document

class DocumentProcessor:
    def __init__(self, max_tokens=3000):
        self.max_tokens = max_tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def process_file(self, file_path):
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == ".pdf":
            return self._process_pdf(file_path)
        elif file_extension == ".docx":
            return self._process_docx(file_path)
        elif file_extension == ".txt":
            return self._process_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def _process_pdf(self, file_path):
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        
        cleaned_text = self._clean_text(text)
        truncated_text, token_count = self._truncate_text(cleaned_text)
        
        metadata = {
            "type": "pdf",
            "size": os.path.getsize(file_path),
            "token_count": token_count,
        }
        return truncated_text, metadata

    def _process_docx(self, file_path):
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        
        cleaned_text = self._clean_text(text)
        truncated_text, token_count = self._truncate_text(cleaned_text)
        
        metadata = {
            "type": "docx",
            "size": os.path.getsize(file_path),
            "token_count": token_count,
        }
        return truncated_text, metadata

    def _process_txt(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        cleaned_text = self._clean_text(text)
        truncated_text, token_count = self._truncate_text(cleaned_text)
        
        metadata = {
            "type": "txt",
            "size": os.path.getsize(file_path),
            "token_count": token_count,
        }
        return truncated_text, metadata

    def _clean_text(self, text):
        # Basic cleaning: remove extra whitespace
        return " ".join(text.split())

    def _truncate_text(self, text):
        tokens = self.tokenizer.encode(text)
        if len(tokens) > self.max_tokens:
            truncated_tokens = tokens[:self.max_tokens]
            truncated_text = self.tokenizer.decode(truncated_tokens)
            return truncated_text, len(truncated_tokens)
        return text, len(tokens)

