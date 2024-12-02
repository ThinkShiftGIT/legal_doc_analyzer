from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
import logging
import os
from pathlib import Path

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from ..processors.pdf_processor import PDFProcessor
from ..processors.audio_processor import AudioProcessor
from ..processors.video_processor import VideoProcessor
from ..storage.vector_store import ChromaStore
from .models import SearchQuery, SearchResponse, AnalysisResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize components
pdf_processor = PDFProcessor()
audio_processor = AudioProcessor()
video_processor = VideoProcessor()
vector_store = ChromaStore()

# Initialize Mistral client
mistral_client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document."""
    try:
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        file_path = uploads_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process based on file type
        file_extension = file.filename.lower().split('.')[-1]
        
        if file_extension in ['pdf']:
            chunks = pdf_processor.process(str(file_path))
        elif file_extension in ['mp3', 'wav']:
            chunks = audio_processor.process(str(file_path))
        elif file_extension in ['mp4', 'avi']:
            chunks = video_processor.process(str(file_path))
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}"
            )
        
        # Store chunks in vector store
        vector_store.add_documents(chunks)
        
        return {"message": "Document processed successfully"}
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up uploaded file
        if 'file_path' in locals():
            file_path.unlink(missing_ok=True)

@router.post("/search", response_model=SearchResponse)
async def search_documents(query: SearchQuery):
    """Search for relevant documents."""
    try:
        docs = vector_store.similarity_search(query.query)
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        return SearchResponse(results=results)
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_document(query: str):
    """Analyze documents using Mistral AI."""
    try:
        # Get relevant documents from vector store
        docs = vector_store.similarity_search(query)
        
        # Prepare context from documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Prepare the prompt
        system_prompt = "You are a legal document analysis assistant. Use the following context to answer the question."
        user_prompt = f"Context:\n{context}\n\nQuestion: {query}"
        
        # Get response from Mistral
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt)
        ]
        
        response = mistral_client.chat(
            model="mistral-tiny",
            messages=messages
        )
        
        # Extract sources
        sources = []
        for doc in docs:
            sources.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return AnalysisResponse(
            answer=response.choices[0].message.content,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error analyzing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))