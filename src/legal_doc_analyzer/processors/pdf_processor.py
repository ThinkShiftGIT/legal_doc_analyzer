import logging
from typing import List
from pathlib import Path
import pypdf

from ..storage.base import BaseChunk

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Process PDF documents."""
    
    def __init__(self, 
                chunk_size: int = 1000,
                chunk_overlap: int = 200):
        """Initialize PDF processor.
        
        Args:
            chunk_size: The size of text chunks to create
            chunk_overlap: The amount of overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # If not at the end, try to break at a newline or space
            if end < text_len:
                last_newline = chunk.rfind('\n')
                last_space = chunk.rfind(' ')
                break_point = max(last_newline, last_space)
                if break_point != -1:
                    end = start + break_point
                    chunk = text[start:end]
            
            chunks.append(chunk)
            start = end - self.chunk_overlap
        
        return chunks
    
    def process(self, file_path: str) -> List[BaseChunk]:
        """Process a PDF file and return chunks of text.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of text chunks with metadata
        """
        try:
            chunks = []
            
            # Open and read PDF
            with open(file_path, 'rb') as file:
                pdf = pypdf.PdfReader(file)
                
                # Process each page
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if not text.strip():
                        continue
                        
                    # Split page content into chunks
                    text_chunks = self._split_text(text)
                    
                    # Create chunks with metadata
                    for j, chunk_text in enumerate(text_chunks):
                        chunks.append(
                            BaseChunk(
                                content=chunk_text,
                                metadata={
                                    "document_type": "pdf",
                                    "page_number": i + 1,
                                    "chunk_index": j,
                                    "source_file": Path(file_path).name,
                                    "language": self._detect_language(chunk_text)
                                }
                            )
                        )
            
            logger.info(f"Successfully processed PDF {file_path} into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise
    
    def _detect_language(self, text: str) -> str:
        """Detect the language of the text (simplified version)."""
        # For now, we'll assume English. In production, use a proper language detection library
        return "en"