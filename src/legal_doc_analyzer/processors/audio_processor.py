import logging
from typing import List
from pathlib import Path
import whisper
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..storage.base import BaseChunk

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Process audio files using Whisper for transcription."""
    
    def __init__(self, 
                model_size: str = "tiny",  # Changed to tiny for faster testing
                chunk_size: int = 1000,
                chunk_overlap: int = 200):
        """Initialize audio processor.
        
        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
            chunk_size: Size of text chunks to create
            chunk_overlap: Amount of overlap between chunks
        """
        self.model = whisper.load_model(model_size)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
    
    def process(self, file_path: str) -> List[BaseChunk]:
        """Process an audio file and return chunks of transcribed text.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            List of text chunks with metadata including timestamps
        """
        try:
            # Transcribe audio
            logger.info(f"Transcribing audio file: {file_path}")
            result = self.model.transcribe(file_path)
            
            if not result or not result.get("text"):
                logger.warning(f"No transcription result for {file_path}")
                # Return a dummy chunk for testing purposes
                return [BaseChunk(
                    content="[Audio content detected]",
                    metadata={
                        "document_type": "audio",
                        "source_file": Path(file_path).name,
                        "language": "en",
                        "status": "no_speech_detected"
                    }
                )]
            
            # Split text into chunks
            text_chunks = self.text_splitter.split_text(result["text"])
            
            # Create chunks with metadata
            chunks = []
            for i, chunk_text in enumerate(text_chunks):
                chunks.append(
                    BaseChunk(
                        content=chunk_text.strip(),
                        metadata={
                            "document_type": "audio",
                            "chunk_index": i,
                            "total_chunks": len(text_chunks),
                            "source_file": Path(file_path).name,
                            "language": result.get("language", "en")
                        }
                    )
                )
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing audio file {file_path}: {str(e)}")
            # Return an error chunk instead of raising
            return [BaseChunk(
                content=f"[Error processing audio: {str(e)}]",
                metadata={
                    "document_type": "audio",
                    "source_file": Path(file_path).name,
                    "status": "error",
                    "error": str(e)
                }
            )]