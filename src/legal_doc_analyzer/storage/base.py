from typing import Dict, Any, Optional
from pydantic import BaseModel

class BaseChunk(BaseModel):
    """Base class for document chunks."""
    content: str
    metadata: Dict[str, Any]

class SearchResult(BaseModel):
    """Class for search results."""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]