"""Document Processing Module

Handles file uploads, text extraction, and document chunking for RAG systems.
Supports multiple file formats (txt, pdf, docx).
"""

import os
import tempfile
from typing import List, Optional
import streamlit as st

from src.common.logger import get_logger
from src.common.custom_exception import CustomException


class DocumentProcessor:
    """Processes uploaded documents and extracts text content."""
    
    SUPPORTED_FORMATS = {'.txt', '.pdf', '.docx'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    CHUNK_SIZE = 1000  # Characters per chunk
    CHUNK_OVERLAP = 200  # Overlap between chunks
    
    def __init__(self):
        """Initialize the document processor."""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("DocumentProcessor initialized")
    
    def validate_file(self, uploaded_file) -> bool:
        """Validate uploaded file format and size.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            bool: True if file is valid
            
        Raises:
            CustomException: If file validation fails
        """
        if not uploaded_file:
            raise CustomException("No file provided")
        
        file_name = uploaded_file.name
        file_ext = os.path.splitext(file_name)[1].lower()
        
        if file_ext not in self.SUPPORTED_FORMATS:
            raise CustomException(
                f"Unsupported file format: {file_ext}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        file_size = uploaded_file.size
        if file_size > self.MAX_FILE_SIZE:
            raise CustomException(
                f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds "
                f"maximum allowed size ({self.MAX_FILE_SIZE / 1024 / 1024:.2f} MB)"
            )
        
        self.logger.info(f"File validation successful: {file_name} ({file_size} bytes)")
        return True
    
    def extract_text_from_txt(self, file_content: bytes) -> str:
        """Extract text from .txt file.
        
        Args:
            file_content: Raw file bytes
            
        Returns:
            str: Extracted text
        """
        try:
            text = file_content.decode('utf-8')
            self.logger.info(f"Extracted {len(text)} characters from TXT file")
            return text
        except UnicodeDecodeError:
            raise CustomException("Unable to decode TXT file. Ensure it's UTF-8 encoded.")
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from .pdf file.
        
        Args:
            file_path: Path to temporary PDF file
            
        Returns:
            str: Extracted text
        """
        try:
            import PyPDF2
            
            text = ""
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
            
            self.logger.info(f"Extracted {len(text)} characters from PDF file")
            return text
        
        except ImportError:
            raise CustomException(
                "PyPDF2 not installed. Install it with: pip install PyPDF2"
            )
        except Exception as e:
            raise CustomException(f"Failed to extract text from PDF: {str(e)}", e)
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from .docx file.
        
        Args:
            file_path: Path to temporary DOCX file
            
        Returns:
            str: Extracted text
        """
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            self.logger.info(f"Extracted {len(text)} characters from DOCX file")
            return text
        
        except ImportError:
            raise CustomException(
                "python-docx not installed. Install it with: pip install python-docx"
            )
        except Exception as e:
            raise CustomException(f"Failed to extract text from DOCX: {str(e)}", e)
    
    def process_file(self, uploaded_file) -> str:
        """Process uploaded file and extract text.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            str: Extracted text from document
            
        Raises:
            CustomException: If processing fails
        """
        try:
            # Validate file
            self.validate_file(uploaded_file)
            
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            text = ""
            
            # Handle .txt files
            if file_ext == '.txt':
                text = self.extract_text_from_txt(uploaded_file.read())
            
            # Handle .pdf files
            elif file_ext == '.pdf':
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                try:
                    text = self.extract_text_from_pdf(tmp_path)
                finally:
                    os.unlink(tmp_path)
            
            # Handle .docx files
            elif file_ext == '.docx':
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                try:
                    text = self.extract_text_from_docx(tmp_path)
                finally:
                    os.unlink(tmp_path)
            
            return text
        
        except CustomException:
            raise
        except Exception as e:
            error_msg = f"Failed to process document: {str(e)}"
            self.logger.error(error_msg)
            raise CustomException(error_msg, e)
    
    def chunk_text(self, text: str, chunk_size: Optional[int] = None,
                   chunk_overlap: Optional[int] = None) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk (default: self.CHUNK_SIZE)
            chunk_overlap: Overlap between chunks (default: self.CHUNK_OVERLAP)
            
        Returns:
            List[str]: List of text chunks
        """
        chunk_size = chunk_size or self.CHUNK_SIZE
        chunk_overlap = chunk_overlap or self.CHUNK_OVERLAP
        
        chunks = []
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunk = text[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        
        self.logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
